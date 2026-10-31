#!/bin/bash
# Lab: identify a mystery process using only /proc. Starts one practice process (named nightly-job); only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
pkill -f '^nightly-job' 2>/dev/null || true
rm -rf "$L/jobs" "$L/check-proc-detective.sh" "$L/answers-proc.txt"
mkdir -p "$L/jobs/batch"
( cd "$L/jobs/batch" && nohup bash -c 'exec -a nightly-job sleep 3571' > /dev/null 2>&1 & )
sleep 1

cat > "$L/check-proc-detective.sh" <<'EOF'
#!/bin/bash
L="$HOME/sys-lab"
A="$L/answers-proc.txt"
pid=$(pgrep -f '^nightly-job' | head -1)
[ -n "$pid" ] || { echo "FAIL: the practice process nightly-job is not running; run the setup script again"; exit 1; }
ok=1
get() { [ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2-; }
[ "$(get pid)" = "$pid" ] && echo "PASS: pid" || { echo "FAIL: pid is wrong (write pid=<the PID of nightly-job>)"; ok=0; }
real=$(readlink -f /proc/$pid/exe)
[ "$(get exe)" = "$real" ] && echo "PASS: exe" || { echo "FAIL: exe is wrong (the program file that is really running, from /proc/PID/exe)"; ok=0; }
cwd=$(readlink -f /proc/$pid/cwd)
[ "$(get cwd)" = "$cwd" ] && echo "PASS: cwd" || { echo "FAIL: cwd is wrong (its current directory, from /proc/PID/cwd)"; ok=0; }
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-proc-detective.sh"
echo "Lab ready. A process called nightly-job is running. Who is it really?"
