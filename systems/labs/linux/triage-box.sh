#!/bin/bash
# Lab: one box, three different hogs (CPU, memory, disk). Starts two practice processes (cpuburn, memhog). Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
T="$L/triage"
pkill -x cpuburn 2>/dev/null || true
pkill -x memhog 2>/dev/null || true
rm -rf "$T" "$L/check-triage-box.sh" "$L/answers-triage.txt"
mkdir -p "$T/bin" "$T/spool" "$T/cache" "$T/logs" "$T/uploads"
cp "$(command -v yes)" "$T/bin/cpuburn"
cp "$(command -v bash)" "$T/bin/memhog"
dd if=/dev/zero of="$T/spool/queue.dat" bs=1M count=60 status=none
dd if=/dev/zero of="$T/cache/c.dat" bs=1M count=8 status=none
dd if=/dev/zero of="$T/logs/app.log" bs=1M count=3 status=none
dd if=/dev/zero of="$T/uploads/u.dat" bs=1M count=5 status=none
nohup "$T/bin/cpuburn" > /dev/null 2>&1 &
nohup "$T/bin/memhog" -c 'x=$(head -c 120000000 /dev/zero | tr "\0" a); sleep 100000; true' > /dev/null 2>&1 &
sleep 3

cat > "$L/check-triage-box.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-triage.txt"
ok=1
get() { [ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2-; }
[ "$(get cpu)" = "cpuburn" ] && echo "PASS: cpu" || { echo "FAIL: cpu= should be the process using the most CPU"; ok=0; }
[ "$(get mem)" = "memhog" ] && echo "PASS: mem" || { echo "FAIL: mem= should be the process using the most memory (RSS), not the most CPU"; ok=0; }
[ "$(get disk)" = "spool" ] && echo "PASS: disk" || { echo "FAIL: disk= should be the name of the biggest directory under ~/sys-lab/triage"; ok=0; }
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-triage-box.sh"
echo "Lab ready. Two practice processes are running and ~/sys-lab/triage has some data. Triage it."
