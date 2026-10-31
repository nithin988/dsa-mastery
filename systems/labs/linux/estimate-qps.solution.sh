#!/bin/bash
# Solution for the estimate-qps lab.
avg=$(( 40000000 * 25 / 86400 ))
peak=$(( avg * 3 ))
tb=$(( 40000000 * 25 * 150 * 365 / 1000000000000 ))
printf 'avg_qps=%s\npeak_qps=%s\nstorage_tb_per_year=%s\n' "$avg" "$peak" "$tb" > "$HOME/sys-lab/answers-estimate.txt"
cat "$HOME/sys-lab/answers-estimate.txt"
