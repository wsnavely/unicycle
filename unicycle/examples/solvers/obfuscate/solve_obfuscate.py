import sys
import string
import logging
import unicycle

def success(result):
    stdout, stderr, rc = result
    if "Incorrect" in stdout:
        return False
    return True

def choose(counts):
    counts.sort(key=lambda x:x[1], reverse=True)
    for cand in counts[:5]:
        yield cand

logging.basicConfig(level=logging.INFO)
cycle = "obfuscate_cycle.py"
alphabet = set(string.printable) - set(string.whitespace)
binary = sys.argv[1]

print "Answer:", unicycle.brute_force(
    binary, 
    [], 
    cycle, 
    "", 
    choose, 
    success, 
    alphabet)
