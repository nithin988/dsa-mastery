#!/bin/bash
# Solution for the top-ips lab.
cut -d' ' -f1 "$HOME/sys-lab/weblogs/web.log" | sort | uniq -c | sort -rn | head -3 > "$HOME/sys-lab/top3.txt"
cat "$HOME/sys-lab/top3.txt"
