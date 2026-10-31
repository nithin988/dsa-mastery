#!/bin/bash
# Lab: answer three questions about a 240-line log with awk, grep and friends. Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
D="$L/forensics"
rm -rf "$D" "$L/answers-forensics.txt" "$L/check-log-forensics.sh"
mkdir -p "$D"
msgs=(db_timeout db_timeout disk_full upstream_refused)
: > "$D/app.log"
for i in $(seq 1 240); do
  hour=$((10 + i / 60)); min=$((i % 60))
  if [ $((i % 10)) -eq 0 ]; then
    level=ERROR; msg=${msgs[$(( (i / 10) % 4 ))]}; lat=3000
  elif [ $((i % 10)) -eq 3 ] || [ $((i % 10)) -eq 6 ]; then
    level=WARN; msg=slow_query; lat=1500
  else
    level=INFO; msg=request_ok; lat=$((100 + i % 50))
  fi
  printf '2026-01-15 %02d:%02d:00 %s %s %s\n' "$hour" "$min" "$level" "$msg" "$lat" >> "$D/app.log"
done

cat > "$L/check-log-forensics.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-forensics.txt"
[ -f "$A" ] || { echo "FAIL: write your answers to ~/sys-lab/answers-forensics.txt"; exit 1; }
ok=1
get() { grep "^$1=" "$A" | head -1 | cut -d= -f2-; }
chk() { if [ "$(get "$1")" = "$2" ]; then echo "PASS: $1"; else echo "FAIL: $1 (got '$(get "$1")')"; ok=0; fi; }
chk errors 24
chk topmsg db_timeout
chk warnms 72000
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-log-forensics.sh"
echo "Lab ready. The log is ~/sys-lab/forensics/app.log (format: date time LEVEL message latency_ms)"
