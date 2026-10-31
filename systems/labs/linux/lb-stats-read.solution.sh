#!/bin/bash
# Solution for the lb-stats-read lab.
F="$HOME/sys-lab/stats/stats.csv"
awk -F, '$1=="web" && $2 ~ /^web[0-9]$/ { tot+=$8; err+=$14; if ($8>max){max=$8; name=$2; w=$19} if ($18=="DOWN") down=$2 }
END { printf "down=%s\nbusiest=%s\nshare_percent=%d\nweight_busiest=%s\nconn_errors=%d\n", down, name, max*100/tot, w, err }' "$F" > "$HOME/sys-lab/answers-stats.txt"
cat "$HOME/sys-lab/answers-stats.txt"
