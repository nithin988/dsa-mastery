#!/bin/bash
# Solution for the redis-first-aid lab.
R="redis-cli -p 6392"
total=$($R dbsize | awk '{print $1}')
sessions=$($R --scan --pattern 'session:*' | wc -l)
nottl=0; best=""; bestsize=0
while read -r k; do
  [ "$($R ttl "$k")" = "-1" ] && nottl=$((nottl + 1))
  m=$($R memory usage "$k")
  if [ "$m" -gt "$bestsize" ]; then bestsize=$m; best=$k; fi
done < <($R --scan)
printf 'total_keys=%s\nsession_keys=%s\nno_ttl_keys=%s\nbiggest_key=%s\n' "$total" "$sessions" "$nottl" "$best" > "$HOME/sys-lab/answers-redis.txt"
cat "$HOME/sys-lab/answers-redis.txt"
