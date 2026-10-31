#!/bin/bash
# Solution for the deleted-log lab.
pid=$(pgrep -f 'olf-holder' | head -1)
ls -l /proc/$pid/fd | grep deleted
fd=$(ls -l /proc/$pid/fd | grep deleted | awk '{print $9}' | head -1)
: > /proc/$pid/fd/$fd
printf 'pid=%s\nfd=%s\n' "$pid" "$fd" > "$HOME/sys-lab/answers-olf.txt"
cat "$HOME/sys-lab/answers-olf.txt"
