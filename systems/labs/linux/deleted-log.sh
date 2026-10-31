#!/bin/bash
# Lab: a deleted file still fills the disk because a process holds it open. Starts one practice process. Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
pkill -f 'olf-holder' 2>/dev/null || true
rm -rf "$L/olf" "$L/check-deleted-log.sh" "$L/answers-olf.txt"
mkdir -p "$L/olf"
F="$L/olf/big.log"
nohup bash -c ': olf-holder; exec 5>"'"$F"'"; rm -f "'"$F"'"; head -c 30000000 /dev/zero >&5; sleep 100000; true' > /dev/null 2>&1 &
sleep 2

cat > "$L/check-deleted-log.sh" <<'EOF'
#!/bin/bash
L="$HOME/sys-lab"
A="$L/answers-olf.txt"
pid=$(pgrep -f 'olf-holder' | head -1)
[ -n "$pid" ] || { echo "FAIL: the practice process is not running; run the setup script again"; exit 1; }
ok=1
get() { [ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2-; }
[ "$(get pid)" = "$pid" ] && echo "PASS: pid" || { echo "FAIL: pid= should be the process that holds the deleted file open"; ok=0; }
[ "$(get fd)" = "5" ] && echo "PASS: fd" || { echo "FAIL: fd= should be the descriptor number of the deleted file"; ok=0; }
size=$(stat -L -c %s /proc/$pid/fd/5 2>/dev/null)
[ "$size" = "0" ] && echo "PASS: space released and the process is still running" || { echo "FAIL: the deleted file still uses space (size=$size). Truncate it through /proc without killing the process."; ok=0; }
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-deleted-log.sh"
echo "Lab ready. Someone deleted a big log, but the disk space did not come back. Find out why."
