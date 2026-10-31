#!/bin/bash
# Solution for the triage-box lab.
T="$HOME/sys-lab/triage"
cpu=$(ps -eo pcpu,comm --sort=-pcpu | awk '$2=="cpuburn"||$2=="memhog"{print $2; exit}')
mem=$(ps -eo rss,comm --sort=-rss | awk '$2=="cpuburn"||$2=="memhog"{print $2; exit}')
disk=$(du -s "$T"/*/ | sort -rn | head -1 | awk '{print $2}' | xargs basename)
printf 'cpu=%s\nmem=%s\ndisk=%s\n' "$cpu" "$mem" "$disk" > "$HOME/sys-lab/answers-triage.txt"
cat "$HOME/sys-lab/answers-triage.txt"
