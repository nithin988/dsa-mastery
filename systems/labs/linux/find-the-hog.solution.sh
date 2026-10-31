#!/bin/bash
# Solution for the find-the-hog lab.
ps -eo pid,pcpu,comm --sort=-pcpu | head -n 4
pid=$(ps -eo pid,pcpu,comm --sort=-pcpu | awk '$3=="spinner"{print $1; exit}')
kill -TERM "$pid"
sleep 1
printf 'hog=spinner\n' > "$HOME/sys-lab/answers-hog.txt"
