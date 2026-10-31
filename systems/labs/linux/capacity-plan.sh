#!/bin/bash
# Lab: turn an estimate into a fleet size and a storage plan. Only creates ~/sys-lab/capacity (a scenario file).
set -e
L="$HOME/sys-lab"
rm -rf "$L/capacity" "$L/check-capacity-plan.sh" "$L/answers-capacity.txt"
mkdir -p "$L/capacity"
cat > "$L/capacity/scenario.txt" <<'EOS'
Photo service scenario
----------------------
Reads per day:                      500,000,000
Peak traffic is 4 times the average.
One application server can serve:   2,000 requests per second at full load.
Keep servers at 60% of full load at peak (headroom for failures and spikes).
Total photo storage:                1,200 TB
One storage node holds:             8 TB
Every photo is stored 3 times (replication).
1 day = 86,400 seconds.

Questions
1. Peak reads per second (average x 4, whole number).
2. Application servers needed (round UP to a whole server).
3. Storage nodes needed including replication (round UP).
EOS

cat > "$L/check-capacity-plan.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-capacity.txt"
ok=1
get() { [ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2- | tr -d ', '; }
near() { awk -v g="$1" -v w="$2" 'BEGIN{ if (g=="") exit 1; d=(g-w)/w; if (d<0) d=-d; exit !(d<=0.05) }'; }
near "$(get peak_qps)" 23148 && echo "PASS: peak_qps" || { echo "FAIL: peak_qps= is 500,000,000 / 86,400 x 4"; ok=0; }
[ "$(get servers)" = "20" ] && echo "PASS: servers" || { echo "FAIL: servers= is peak QPS divided by (2,000 x 0.6), rounded up"; ok=0; }
[ "$(get storage_nodes)" = "450" ] && echo "PASS: storage_nodes" || { echo "FAIL: storage_nodes= is 1,200 TB x 3 copies / 8 TB per node, rounded up"; ok=0; }
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-capacity-plan.sh"
echo "Lab ready. Read ~/sys-lab/capacity/scenario.txt and answer the three questions."
