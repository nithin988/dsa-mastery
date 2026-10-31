#!/bin/bash
# Solution for the queue-backlog-math lab.
cap=$(( 10 * 4 * 2 ))          # 10 workers x 4 threads / 0.5 s
need=$(( (180 + 7) / 8 ))      # capacity per worker is 8 jobs per second; need 1.5 x 120 = 180
newcap=$(( need * 8 ))
drain=$(( (9000 + (newcap - 120) - 1) / (newcap - 120) ))
printf 'capacity_per_second=%s\ngrowing=yes\ngrowth_per_second=%s\nworkers_needed=%s\ndrain_seconds=%s\n' "$cap" "$(( 120 - cap ))" "$need" "$drain" > "$HOME/sys-lab/answers-qmath.txt"
cat "$HOME/sys-lab/answers-qmath.txt"
