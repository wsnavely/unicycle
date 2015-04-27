import os
import collections
import command
import sys
import logging
import pin
import string
import unicycle

def brute_force(cmd, guess):
    print "Guess:", guess
    counts = []
    for ch in string.printable:
        if ch in string.whitespace:
            continue 
        (stdout, stderr, rc) = unicycle.ride("examples/obfuscate_unicycle.py", cmd, [], stdin=(guess + ch))
        if "Incorrect!" not in stdout:
            print "Success!", guess
        count = int(stderr)
        counts.append((ch, count))
    counts.sort(key=lambda x:x[1], reverse=True)
    candidates = counts[:5]
    for cand in candidates:
        brute_force(cmd, guess + cand[0])

unicycle.set_pin_home("/home/ubuntu/ctf_research/pin/pin-2.14-67254-gcc.4.4.7-linux")
brute_force(sys.argv[1], "")
