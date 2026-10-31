#!/bin/bash
# Solution for the disk-detective lab.
cd "$HOME/sys-lab/disk"
bigdir=$(du -sk */ | sort -rn | head -1 | awk '{print $2}' | tr -d '/')
bigfile=$(find . -type f -printf '%s %f\n' | sort -rn | head -1 | awk '{print $2}')
over=$(find . -type f -size +100k | wc -l)
printf 'bigdir=%s\nbigfile=%s\nover100k=%s\n' "$bigdir" "$bigfile" "$over" > "$HOME/sys-lab/answers-disk.txt"
cat "$HOME/sys-lab/answers-disk.txt"
