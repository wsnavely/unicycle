# builtin imports
import argparse
import os
import pin
import shlex
import sys

# package imports
import command

refs = []
pin_home=""

class Callback(object):
    def __init__(self, start, end, callback):
        self.start = start
        self.end = end
        self.callback = callback

    def __str__(self):
        return "({0},{1})".format(self.start, self.end)
 
class Unicycle(object):
    def __init__(self):
        self.callbacks = []
        self.dismount = None

    def paint(self, start, end, callback):
        self.callbacks.append(Callback(start, end, callback))

    def get_callbacks(self, addr):
        for callback in self.callbacks:
            if addr >= callback.start and addr <= callback.end:
                yield callback

    def instrument_fxn(self, ins_addr):
        address = pin.INS_Address(ins_addr)
        for cb in self.get_callbacks(address):
            pin.INS_InsertCall(pin.IPOINT_BEFORE, ins_addr, cb.callback)

    def mount(self):
        instrument = (lambda uni: (lambda addr: uni.instrument_fxn(addr)))
        fxn = instrument(self)
        pin.INS_AddInstrumentFunction(fxn)
        if self.dismount:
            pin.AddFiniFunction(self.dismount)
        refs.append(fxn)

class InstructionCounterUnicycle(Unicycle):
    def __init__(self, start=0x0, end=0xFFFFFFFF):
        def count(info):
            self.ins_count += 1
        def report():
            sys.stderr.write(str(self.ins_count))

        super(InstructionCounterUnicycle, self).__init__()
        self.ins_count = 0
        self.paint(start, end, count)
        self.dismount = report

def set_pin_home(val):
    global pin_home
    pin_home = val

def ride(
        unicycle,
        cmd,
        args,
        pinhome=None,
        stdin=None):
    if pinhome == None:
        pinhome = pin_home

    pin_py = os.path.join(pinhome, "source", "tools", "Python_Pin")
    pin_exe = os.path.join(pinhome, "pin")
    py_bin = os.path.join(pin_py, "obj-ia32", "Python_Pin.so")
    pin_args = ["-t", py_bin, "-m", unicycle, "--", cmd] + args
    cmd = command.Command(pin_exe, pin_args) 
    cmd.run(stdin=stdin)
    return (cmd.stdout, cmd.stderr, cmd.returncode)

def get_arg_parser():
    parser = argparse.ArgumentParser(description="Let's ride a unicycle.")
    parser.add_argument(
            "-c", 
            "--cmd", 
            required=True,
            help="The binary to ride through.")
    parser.add_argument(
            "-a", 
            "--args", 
            default="",
            help="The arguments to the binary.")
    parser.add_argument(
            "-i", 
            "--input", 
            default=None,
            help="The input to the binary.")
    parser.add_argument(
            "-u", 
            "--unicycle", 
            required=True,
            help="The unicycle to ride.")
    parser.add_argument(
            "-p", 
            "--pinhome", 
            default=None,
            help="Where does Intel pin live? " +
                 "You can also set the PIN_HOME environment variable.")
    return parser
 
if __name__ == "__main__":
    getopt = get_arg_parser()
    args = getopt.parse_args()
    if args.pinhome:
        pinhome = args.pinhome
    else:
        pinhome = os.environ.get('PIN_HOME')

    if pinhome == None:
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
        pinhome, 
        args.input)
    print result
