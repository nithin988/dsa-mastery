#!/bin/bash
# Lab: back-of-envelope estimation for a chat app. Only creates ~/sys-lab/estimate (a scenario file). No services are started.
set -e
L="$HOME/sys-lab"
rm -rf "$L/estimate" "$L/check-estimate-qps.sh" "$L/answers-estimate.txt"
mkdir -p "$L/estimate"
cat > "$L/estimate/scenario.txt" <<'EOS'
Chat app scenario
-----------------
Daily active users (DAU):          40,000,000
Messages sent per user per day:    25
Average message size on disk:      150 bytes (text plus metadata)
Peak traffic is 3 times the average.
1 day = 86,400 seconds.  Use 1 TB = 1,000,000,000,000 bytes.

Questions
1. Average messages per second (round to a whole number).
2. Peak messages per second (average x 3, round to a whole number).
3. New storage per year in terabytes (365 days, round to a whole number).
EOS

cat > "$L/check-estimate-qps.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-estimate.txt"
ok=1
get() { [ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2- | tr -d ', '; }
near() { awk -v g="$1" -v w="$2" 'BEGIN{ if (g=="") exit 1; d=(g-w)/w; if (d<0) d=-d; exit !(d<=0.05) }'; }
near "$(get avg_qps)" 11574 && echo "PASS: avg_qps" || { echo "FAIL: avg_qps= should be about 40,000,000 x 25 / 86,400"; ok=0; }
near "$(get peak_qps)" 34722 && echo "PASS: peak_qps" || { echo "FAIL: peak_qps= should be about three times the average"; ok=0; }
near "$(get storage_tb_per_year)" 55 && echo "PASS: storage_tb_per_year" || { echo "FAIL: storage_tb_per_year= is messages per day x 150 bytes x 365, in terabytes"; ok=0; }
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-estimate-qps.sh"
echo "Lab ready. Read ~/sys-lab/estimate/scenario.txt and answer the three questions."
