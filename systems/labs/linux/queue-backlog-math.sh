#!/bin/bash
# Lab: size queue consumers from saved metrics. No services needed. Only creates ~/sys-lab/qmath.
set -e
L="$HOME/sys-lab"
rm -rf "$L/qmath" "$L/check-queue-backlog-math.sh" "$L/answers-qmath.txt"
mkdir -p "$L/qmath"
cat > "$L/qmath/metrics.txt" <<'EOF'
Queue "image-resize", measured over the last 10 minutes:
  arrival rate:            120 jobs per second (sustained)
  processing time per job: 0.5 seconds (one job at a time per worker thread)
  threads per worker:      4
  current workers:         10
  current queue depth:     9000 jobs
  oldest message age:      75 seconds
EOF
cat > "$L/qmath/README.txt" <<'EOF'
metrics.txt describes one queue. A worker thread handles one job at a time.

Questions (write key=value lines into ~/sys-lab/answers-qmath.txt):
1. capacity_per_second:  the jobs per second the current workers can process (workers x threads / seconds per job)
2. growing:              yes or no: is the queue growing right now? (arrival rate versus capacity)
3. growth_per_second:    how many jobs per second the depth changes by (arrival minus capacity; use a negative number if shrinking)
4. workers_needed:       the smallest whole number of workers (4 threads each) that makes capacity at least 1.5 times the arrival rate
5. drain_seconds:        with that many workers, how many whole seconds to clear the current 9000-job backlog
                         (backlog divided by capacity minus arrival rate; round up)
EOF
cat > "$L/check-queue-backlog-math.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-qmath.txt"
ok=1
chk() { got=$([ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2- | tr -d ' '); if [ "$got" = "$2" ]; then echo "PASS: $1"; else echo "FAIL: $1 ($3)"; ok=0; fi; }
chk capacity_per_second 80 "10 workers x 4 threads / 0.5 s = 80"
chk growing yes "120 arrive per second, only 80 can be processed"
chk growth_per_second 40 "120 - 80"
chk workers_needed 23 "need capacity >= 180 per second: workers x 8 >= 180, so 22.5 rounds up to 23"
chk drain_seconds 141 "23 workers give capacity 184; the surplus over 120 arrivals is 64 per second; 9000 / 64 = 140.6, round up to 141"
[ $ok = 1 ] && { echo "All tasks done. Capacity must exceed the arrival rate with headroom; the backlog drains only at the surplus."; exit 0; } || exit 1
EOF
chmod +x "$L/check-queue-backlog-math.sh"
echo "Lab ready. Read ~/sys-lab/qmath/README.txt"
