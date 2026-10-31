#!/bin/bash
# Lab: find zombie processes and fix the real problem (their parent). Starts one practice parent (zombifier.py). Needs python3. Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
pkill -f 'sys-lab/zombies/zombifier.py' 2>/dev/null || true
rm -rf "$L/zombies" "$L/check-zombie-hunt.sh" "$L/answers-zombie.txt"
mkdir -p "$L/zombies"
cat > "$L/zombies/zombifier.py" <<'EOS'
# A buggy parent: forks three children that exit at once, and never calls wait().
import os, time
for _ in range(3):
    if os.fork() == 0:
        os._exit(0)
time.sleep(100000)
EOS
nohup python3 "$L/zombies/zombifier.py" > /dev/null 2>&1 &
sleep 1
pgrep -f 'sys-lab/zombies/zombifier.py' | head -1 > "$L/zombies/.parent"

cat > "$L/check-zombie-hunt.sh" <<'EOF'
#!/bin/bash
L="$HOME/sys-lab"
A="$L/answers-zombie.txt"
want=$(cat "$L/zombies/.parent")
ok=1
get() { [ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2-; }
[ "$(get parent_pid)" = "$want" ] && echo "PASS: you identified the parent of the zombies" || { echo "FAIL: parent_pid= should be the PID of the process that created the zombies (PPID of the Z entries)"; ok=0; }
if kill -0 "$want" 2>/dev/null; then echo "FAIL: the buggy parent ($want) is still running; stop it (SIGTERM) so its zombies are reaped"; ok=0; else echo "PASS: the parent is gone"; fi
z=$(ps -eo stat=,ppid= | awk -v p="$want" '$1 ~ /^Z/ && $2==p' | wc -l)
[ "$z" = "0" ] && echo "PASS: no zombies remain" || { echo "FAIL: $z zombie(s) remain"; ok=0; }
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-zombie-hunt.sh"
echo "Lab ready. There are zombie processes. Find who creates them."
