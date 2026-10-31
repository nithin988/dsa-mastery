#!/bin/bash
# Solution for the hung-job lab.
L="$HOME/sys-lab/hang"
strace -f -o /tmp/hang-trace.txt "$L/job" &
spid=$!
sleep 1
grep -c input.fifo /tmp/hang-trace.txt >/dev/null && grep input.fifo /tmp/hang-trace.txt | tail -1
echo "go" > "$L/input.fifo"
wait $spid
printf 'blocked_on=%s\n' "$L/input.fifo" > "$HOME/sys-lab/answers-hang.txt"
cat "$L/done.txt"
