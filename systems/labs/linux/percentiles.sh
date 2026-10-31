#!/bin/bash
# Lab: compute p50, p95 and p99 latency from a request log, and see why the average misleads. Creates ~/sys-lab/lat. Needs python3.
set -e
L="$HOME/sys-lab"
rm -rf "$L/lat" "$L/check-percentiles.sh" "$L/answers-lat.txt"
mkdir -p "$L/lat"
export L
python3 - <<'EOF'
import math, os, random
L = os.environ["L"] + "/lat"
rng = random.Random(21)
vals = [int(rng.gauss(80, 15)) for _ in range(940)] + [int(rng.uniform(900, 2500)) for _ in range(60)]
vals = [max(5, v) for v in vals]
rng.shuffle(vals)
open(L + "/latencies.txt", "w").write("\n".join(map(str, vals)) + "\n")
s = sorted(vals)
rank = lambda p: s[math.ceil(p / 100 * len(s)) - 1]
mean = round(sum(vals) / len(vals))
open(L + "/.expected", "w").write("%d %d %d %d\n" % (rank(50), rank(95), rank(99), mean))
EOF
cat > "$L/lat/README.txt" <<'EOS'
latencies.txt has 1,000 request latencies in milliseconds, one per line, in arrival order.
Percentile by nearest rank: sort ascending; pK is the value at position ceil(K/100 * N) (positions start at 1).
  With N=1000: p50 is the 500th value, p95 the 950th, p99 the 990th.
Useful:   sort -n latencies.txt | sed -n '500p'

Questions (whole milliseconds):
1. p50 (the median)   2. p95   3. p99   4. the average (mean), rounded to a whole number
Then ask yourself: which number would your users complain about, and which one would a dashboard of averages show?
EOS
cat > "$L/check-percentiles.sh" <<'EOF'
#!/bin/bash
L="$HOME/sys-lab"
A="$L/answers-lat.txt"
read -r e50 e95 e99 em < "$L/lat/.expected"
ok=1
get() { [ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2-; }
[ "$(get p50)" = "$e50" ] && echo "PASS: p50" || { echo "FAIL: p50= is the 500th value of the sorted list"; ok=0; }
[ "$(get p95)" = "$e95" ] && echo "PASS: p95" || { echo "FAIL: p95= is the 950th value of the sorted list"; ok=0; }
[ "$(get p99)" = "$e99" ] && echo "PASS: p99" || { echo "FAIL: p99= is the 990th value of the sorted list"; ok=0; }
[ "$(get mean)" = "$em" ] && echo "PASS: mean" || { echo "FAIL: mean= is the sum divided by 1000, rounded"; ok=0; }
[ $ok = 1 ] && { echo "All tasks done. Compare the mean with p99: the average hides the slow tail."; exit 0; } || exit 1
EOF
chmod +x "$L/check-percentiles.sh"
echo "Lab ready. See ~/sys-lab/lat/README.txt"
