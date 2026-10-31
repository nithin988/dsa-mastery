#!/bin/bash
# Solution for the zombie-hunt lab.
ps -eo pid,ppid,stat,comm | awk '$3 ~ /^Z/'
ppid=$(ps -eo ppid=,stat= | awk '$2 ~ /^Z/{print $1; exit}')
printf 'parent_pid=%s\n' "$ppid" > "$HOME/sys-lab/answers-zombie.txt"
kill -TERM "$ppid"
sleep 1
cat "$HOME/sys-lab/answers-zombie.txt"
