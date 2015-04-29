import sys
import string
import logging
import unicycle

def success(result):
    stdout, stderr, rc = result
    if "wrong" in stderr:
        return False
    return True

def choose(counts):
    avg = sum([c[1] for c in counts]) / float(len(counts))
    devs = [(c[0], abs(c[1]-avg)) for c in counts]
    devs.sort(key=lambda x:x[1], reverse=True)
    for cand in devs[:5]:
        yield cand

cycle = "baleful_cycle.py"
logging.basicConfig(level=logging.INFO)
alphabet = set(string.printable) - set(string.whitespace)
binary = sys.argv[1]
print unicycle.solvers.brute_force(
    binary, 
    [], 
    cycle, 
    "", 
    choose, 
    success, 
    alphabet,
    pad=30)
