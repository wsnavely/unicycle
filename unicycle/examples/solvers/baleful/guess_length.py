import sys
import unicycle

cmd = sys.argv[1]
cycle = "baleful_cycle.py"
results = []

for count in xrange(1,40):
    guess = "x" * count
    stdout, stderr, rc = unicycle.ride(cycle, cmd, [], stdin=(guess + "\n"))
    lines = stderr.split("\n")
    ic = int(lines[-1])
    results.append((count,ic))

results.sort(key=lambda x:x[1], reverse=True)
print results[:5]
