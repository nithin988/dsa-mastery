#!/bin/bash
# Solution for the full-disk lab.
R="$HOME/sys-lab/fd"
big=$(find "$R" -type f -printf '%s %p\n' | sort -rn | head -1 | cut -d' ' -f2-)
dir=$(find "$R" -type f -printf '%h\n' | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')
printf 'biggest_file=%s\nmost_files_dir=%s\n' "$big" "$dir" > "$HOME/sys-lab/answers-disk.txt"
cat "$HOME/sys-lab/answers-disk.txt"
