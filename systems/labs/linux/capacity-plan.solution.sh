#!/bin/bash
# Solution for the capacity-plan lab.
peak=$(( 500000000 * 4 / 86400 ))
servers=$(( (peak + 1199) / 1200 ))   # peak / (2000 * 0.6), rounded up
nodes=$(( (1200 * 3 + 7) / 8 ))
printf 'peak_qps=%s\nservers=%s\nstorage_nodes=%s\n' "$peak" "$servers" "$nodes" > "$HOME/sys-lab/answers-capacity.txt"
cat "$HOME/sys-lab/answers-capacity.txt"
