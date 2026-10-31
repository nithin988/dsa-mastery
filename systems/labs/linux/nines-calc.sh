#!/bin/bash
# Lab: availability arithmetic. Only creates ~/sys-lab/nines (a scenario file).
set -e
L="$HOME/sys-lab"
rm -rf "$L/nines" "$L/check-nines-calc.sh" "$L/answers-nines.txt"
mkdir -p "$L/nines"
cat > "$L/nines/scenario.txt" <<'EOS'
Availability arithmetic
-----------------------
Use a 30-day month = 43,200 minutes.

1. A service promises 99.95% availability. How many minutes of downtime per month does that allow?
   -> write  allowed_minutes=<number>   (one decimal is fine)

2. A request must pass through two services in SERIES. Each is 99.9% available.
   What is the availability of the whole request, in percent?
   -> write  series_percent=<number>    (two decimals)

3. Two identical servers run in PARALLEL (the service is up if at least one is up), each 99% available,
   failing independently. What is the availability of the pair, in percent?
   -> write  parallel_percent=<number>  (two decimals)

4. Backups run every 6 hours and the disaster can strike at any moment.
   What is the WORST-CASE data loss in hours (the RPO you actually get)?
   -> write  worst_case_loss_hours=<number>

Hints: series = multiply availabilities; parallel = 1 - (failure probability of each, multiplied).
EOS
cat > "$L/check-nines-calc.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-nines.txt"
ok=1
get() { [ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2- | tr -d ' %'; }
close() { awk -v g="$1" -v w="$2" -v t="$3" 'BEGIN{ if (g=="") exit 1; d=g-w; if (d<0) d=-d; exit !(d<=t) }'; }
close "$(get allowed_minutes)" 21.6 0.3 && echo "PASS: allowed_minutes" || { echo "FAIL: allowed_minutes= is 0.05% of 43,200 minutes"; ok=0; }
close "$(get series_percent)" 99.80 0.011 && echo "PASS: series_percent" || { echo "FAIL: series_percent= is 0.999 x 0.999 as a percentage"; ok=0; }
close "$(get parallel_percent)" 99.99 0.011 && echo "PASS: parallel_percent" || { echo "FAIL: parallel_percent= is 1 - (0.01 x 0.01) as a percentage"; ok=0; }
close "$(get worst_case_loss_hours)" 6 0.01 && echo "PASS: worst_case_loss_hours" || { echo "FAIL: worst_case_loss_hours= is the whole backup interval"; ok=0; }
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-nines-calc.sh"
echo "Lab ready. Read ~/sys-lab/nines/scenario.txt"
