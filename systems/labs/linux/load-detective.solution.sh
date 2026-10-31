#!/bin/bash
# Solution for the load-detective lab.
C="$HOME/sys-lab/captures"
oom=$(grep -c 'Out of memory' "$C/dmesg.txt")
culprit=$(awk 'NR==2{print $12}' "$C/top.txt")   # top is sorted by memory in this capture
printf 'bottleneck=memory\nculprit=%s\noom_victims=%s\nwhy_disk_busy=swap\n' "$culprit" "$oom" > "$HOME/sys-lab/answers-load.txt"
cat "$HOME/sys-lab/answers-load.txt"
