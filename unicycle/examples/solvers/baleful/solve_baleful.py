import os
import collections
import command
import sys
import logging
import pin
import string
import solvers

def success(result):
    stdout, stderr, rc = result
    if "wrong" in stderr:
        return False
    return True

def choose(counts):
    avg = sum([c[1] for c in counts]) / float(len(counts))
    devs = [(c[0], abs(c[1]-avg)) for c in counts]
    devs.sort(key=lambda x:x[1], reverse=True)
    print devs
    for cand in devs[:5]:
        yield cand

cycle = "baleful_cycle.py"
alphabet = set(string.printable) - set(string.whitespace)
binary = sys.argv[1]
solvers.brute_force(
    binary, 
    [], 
    cycle, 
    "", 
    choose, 
    success, 
    alphabet)
