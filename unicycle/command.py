"""A simple module for running shell commands."""

import subprocess
import logging
import unicycle

class Command(object):
    """This class provides an easy to use wrapper around Popen.

    Attributes:
        cmd: The command to run
        args: A list of arguments to the command
        cwd: The working directory
        stdout: The stdout of the command, after running.
        stderr: The stderr of the command, after running.
        returncode: The exit code of the command, after running.
    """

    def __init__(
            self,
            cmd,
            args,
            cwd=None):
        """Construct a new command."""

        self.cmd = cmd
        self.args = args
        self.cwd = cwd
        self.stdout = None
        self.stderr = None
        self.returncode = None

    def __str__(self):
        """Get a string representation of a command."""

        pkg = [self.cmd] + self.args
        return "CMD: " + (" ".join(pkg))

    def run(self, stdin=None):
        """Run a command."""
        pkg = [self.cmd] + self.args
        logging.debug(str(self))
        process = subprocess.Popen(
            pkg,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.cwd,
            env=None)
        self.stdout, self.stderr = process.communicate(input=stdin)
        self.returncode = process.returncode
