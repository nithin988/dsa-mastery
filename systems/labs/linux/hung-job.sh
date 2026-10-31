#!/bin/bash
# Lab: a job hangs and prints nothing. Use strace to see what it waits for. Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
rm -rf "$L/hang" "$L/check-hung-job.sh" "$L/answers-hang.txt"
mkdir -p "$L/hang"
mkfifo "$L/hang/input.fifo"
cat > "$L/hang/job" <<'EOS'
#!/bin/bash
# job: waits for an instruction, then records it. It prints nothing while it waits.
d="$(cd "$(dirname "$0")" && pwd)"
read -r line < "$d/input.fifo"
echo "finished: $line" > "$d/done.txt"
EOS
chmod +x "$L/hang/job"

cat > "$L/check-hung-job.sh" <<'EOF'
#!/bin/bash
L="$HOME/sys-lab"
A="$L/answers-hang.txt"
ok=1
got=""
[ -f "$A" ] && got=$(grep '^blocked_on=' "$A" | head -1 | cut -d= -f2-)
if [ "$got" = "$L/hang/input.fifo" ]; then echo "PASS: you identified what the job waits on"; else echo "FAIL: write blocked_on=<full path> into ~/sys-lab/answers-hang.txt (use the last line of the strace output)"; ok=0; fi
if [ -f "$L/hang/done.txt" ] && grep -q '^finished: .' "$L/hang/done.txt"; then echo "PASS: you unblocked the job and it finished"; else echo "FAIL: the job has not finished (done.txt missing). Give it what it waits for."; ok=0; fi
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-hung-job.sh"
echo "Lab ready. Run ~/sys-lab/hang/job : it prints nothing and never ends. Why?"
