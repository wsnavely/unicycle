""" Dynamic binary instrumentation with the power of unicycles.

This module allows one easily instrument a binary with
python code.  The metaphor at work here is as follows.
Each binary is like a piece of terrain.  Running the binary
is like riding a unicycle across it.  By painting the wheel
of the unicycle, we can observe the behavior of the execution.

Attributes:
    pin_home (string): The location of the Intel pin software on this system.
"""

import argparse
import os
import shlex
import sys
import unicycle

try:
    import pin
except:
    pass

# Module-level variables
REFS = []
PIN_HOME = None

class Callback(object):
    """
    This class represents a Python function (or  callback) that is
    called when binary instructions are executed.  The conditions
    for triggering the function are twofold: one can specify a range
    (start, end, both inclusive) indicating the values of EIP that
    should trigger the callback; also, one can specify an arbitrary
    predicate, which when true triggers the callback.  The predicate
    takes one argument, the instruction information relayed from
    pin, and should return True or False.
    """
    def __init__(self, start, end, callback, pred):
        """
        Construct a new Callback.
        """
        self.start = start
        self.end = end
        self.callback = callback
        self.predicate = pred

    def filter(self, addr):
        """
        Determine if the given address matches the predicate defined for
        this callback, if one is defined.
        """
        if self.predicate:
            return self.filter(addr)
        return True

    def __str__(self):
        """
        Returns a string representation of a callback.
        """
        return "CALLBACK({0},{1})".format(self.start, self.end)

class Unicycle(object):
    """Associates binary instructions with Python callbacks.

    When we execute a binary, it's as if we are riding a unicycle
    through it.  By painting the wheel of the unicycle, we can
    gather information about the execution.  This class represents
    such a unicycle.

    Attributes:
        callbacks: The list of callbacks associated with this unicycle.
        dismount: A python function called when the binary finishes executing.
    """

    def __init__(self):
        """Construct a new unicycle."""
        self.callbacks = []
        self.dismount = None

    def paint(
            self,
            start,
            end,
            callback,
            pred=None):
        """Specify a set of instructions to instrument with a Python callback.

        Args:
            start: The minimum EIP value to instrument (inclusive)
            end: The maximum EIP value to instrument (inclusive)
            callback: The Python function to call

        Keyword Args:
            pred: An optional filtering predicate. Takes a pin instruction
            address and returns True if the instruction should be instrumented
            with the specified callback, False otherwise.

        Returns:
            None
        """
        self.callbacks.append(Callback(start, end, callback, pred))

    def get_callbacks(self, ins_addr):
        """Generates the callbacks that should be invoked for a given
        instruction.

        Args:
            ins_addr: A pin instruction address.

        Yields:
            The callbacks associated with a given instruction.
        """
        eip = pin.INS_Address(ins_addr)
        for cbk in self.callbacks:
            if eip >= cbk.start and eip <= cbk.end and cbk.filter(ins_addr):
                yield cbk

    def instrument_fxn(self, ins_addr):
        """Instruments a given instruction with the appropriate callbacks.

        Args:
            ins_addr: A pin instruction address.

        Returns:
            None
        """
        for cbk in self.get_callbacks(ins_addr):
            pin.INS_InsertCall(pin.IPOINT_BEFORE, ins_addr, cbk.callback)

    def mount(self):
        """Apply the callback configuration specified in this unicycle.

        Returns:
            None
        """
        instrument = (lambda uni: (lambda addr: uni.instrument_fxn(addr)))
        fxn = instrument(self)

        pin.INS_AddInstrumentFunction(fxn)
        if self.dismount:
            pin.AddFiniFunction(self.dismount)
        REFS.append(fxn)

class InstructionCounterUnicycle(Unicycle):
    """A simple unicycle for performing instruction counting."""

    def __init__(self, start=0x0, end=0xFFFFFFFF):
        """Construct a new instruction counting unicycle.

        Keyword Args:
            start: The value of EIP where we start counting
            end: The value of EIP where we stop counting
        """
        def count(info):
            """Count an instruction."""
            self.ins_count += 1
        def report():
            """Report the total instruction count."""
            sys.stderr.write("\n" + str(self.ins_count))

        super(InstructionCounterUnicycle, self).__init__()
        self.ins_count = 0
        self.paint(start, end, count)
        self.dismount = report

def set_pin_home(pindir):
    """Set the location of the Intel pin software on this system.

    Users can either set the PIN_HOME environment variable, or call
    this function, to specify the location of PIN.
    """
    global PIN_HOME
    PIN_HOME = pindir

def get_pin_home():
    """Get the location of the Intel pin software on this system."""
    global PIN_HOME
    if PIN_HOME == None:
        return os.environ.get('PIN_HOME')
    return PIN_HOME

def ride(cycle, cmd, args, stdin=None):
    """Ride a unicycle through a binary.

    The location of pin must be set prior to calling this function,
    either by setting the PIN_HOME environment variable, or calling
    the set_pin_home function.

    Args:
        cycle: The path to the unicycle.
        cmd: The path to the binary.
        args: A list of arguments for the binary.

    Keyword Args:
        stdin: Data to pass to the binary over stdin.

    Returns:
        A 3-tuple (stdout, sterr, rc), conveying, respectively,
        the stdout of the binary, the stderr of the binary, and
        the return code of the binary.
    """
    pindir = get_pin_home()
    if pindir == None:
        msg = "Couldn't find pin! "
        msg += "Set the PIN_HOME environment variable, "
        msg += "or call set_pin_home before calling this function"
        raise ValueError(msg)

    pin_py = os.path.join(pindir, "source", "tools", "Python_Pin")
    pin_exe = os.path.join(pindir, "pin")
    py_bin = os.path.join(pin_py, "obj-ia32", "Python_Pin.so")
    pin_args = ["-t", py_bin, "-m", cycle, "--", cmd] + args
    cmd = unicycle.Command(pin_exe, pin_args)
    cmd.run(stdin=stdin)
    return (cmd.stdout, cmd.stderr, cmd.returncode)

def get_arg_parser():
    """Get the argument parser used when running this module on
    the command line."""
    parser = argparse.ArgumentParser(description="Let's ride a unicycle.")
    parser.add_argument(\
            "-c",\
            "--cmd",\
            required=True,\
            help="The binary to ride through.")

    parser.add_argument(\
            "-a",\
            "--args",\
            default="",\
            help="The arguments to the binary.")

    parser.add_argument(\
            "-i",\
            "--input",\
            default=None,\
            help="The input to the binary.")

    parser.add_argument(\
            "-u",\
            "--unicycle",\
            required=True,\
            help="The unicycle to ride.")

    parser.add_argument(\
            "-p",\
            "--pinhome",\
            default=None,\
            help="Where does Intel pin live?")

    return parser

def main():
    """Called when invoking this module from the command line."""

    getopt = get_arg_parser()
    args = getopt.parse_args()
    if args.pinhome:
        set_pin_home(args.pinhome)

    if get_pin_home() == None:
        msg = "I need pin to run! "
        msg += "Set the PIN_HOME environment variable, "
        msg += "or specify the --pinhome parameter.\n"
        sys.stderr.write(msg)
        getopt.print_help()
        exit(1)

    result = ride(
        args.unicycle,
        args.cmd,
        shlex.split(args.args),
        args.input)
    return result

if __name__ == "__main__":
    print main()
