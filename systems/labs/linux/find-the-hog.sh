#!/bin/bash
# Lab: find the process that is hogging the CPU and stop it politely, without killing the innocent one.
# Only touches ~/sys-lab and the two practice processes it starts (spinner and lazyworker).
set -e
L="$HOME/sys-lab"
B="$L/bin"
pkill -x spinner 2>/dev/null || true
pkill -x lazyworker 2>/dev/null || true
rm -rf "$B" "$L/check-find-the-hog.sh" "$L/answers-hog.txt"
mkdir -p "$B"
cp "$(command -v yes)" "$B/spinner"
cp "$(command -v sleep)" "$B/lazyworker"
nohup "$B/spinner" > /dev/null 2>&1 &
nohup "$B/lazyworker" 100000 > /dev/null 2>&1 &
sleep 1

cat > "$L/check-find-the-hog.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-hog.txt"
ok=1
if [ -f "$A" ] && [ "$(grep '^hog=' "$A" | head -1 | cut -d= -f2-)" = "spinner" ]; then echo "PASS: you named the CPU hog"; else echo "FAIL: write hog=<process name> into ~/sys-lab/answers-hog.txt"; ok=0; fi
if pgrep -x spinner >/dev/null; then echo "FAIL: the hog is still running"; ok=0; else echo "PASS: the hog is stopped"; fi
if pgrep -x lazyworker >/dev/null; then echo "PASS: the innocent process is still running"; else echo "FAIL: you also killed the innocent process (lazyworker)"; ok=0; fi
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-find-the-hog.sh"
echo "Lab ready: two processes are running. One is burning a CPU."
