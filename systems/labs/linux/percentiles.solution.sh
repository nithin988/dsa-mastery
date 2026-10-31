#!/bin/bash
# Solution for the percentiles lab (shell tools, independent of the setup's Python).
F="$HOME/sys-lab/lat/latencies.txt"
p() { sort -n "$F" | sed -n "${1}p"; }
mean=$(awk '{s+=$1} END{printf "%d", s/NR + 0.5}' "$F")
printf 'p50=%s\np95=%s\np99=%s\nmean=%s\n' "$(p 500)" "$(p 950)" "$(p 990)" "$mean" > "$HOME/sys-lab/answers-lat.txt"
cat "$HOME/sys-lab/answers-lat.txt"
