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

max_val = float(max([res[1] for res in results]))
normalize = [(res[0], res[1]/max_val) for res in results]
for res in normalize:
    idx, val = res
    
    freq = int(val * 30)
    print format(idx, '03d') + ": " + ("*" * freq)
