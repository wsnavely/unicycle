import subprocess

class Command(object):
    def __init__(
            self, 
            cmd, 
            args, 
            cwd=None):
        self.cmd = cmd
        self.args = args
        self.cwd = cwd
        self.stdout = None
        self.stderr = None
        self.returncode = None

    def __str__(self):
        pkg = [self.cmd] + self.args
        return "CMD: " + (" ".join(pkg))

    def run(self, stdin=None):
        pkg = [self.cmd] + self.args
        process = subprocess.Popen(
            pkg, 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            cwd=self.cwd, 
            env=None)
        self.stdout, self.stderr = process.communicate(input=stdin)
        self.returncode = process.returncode
