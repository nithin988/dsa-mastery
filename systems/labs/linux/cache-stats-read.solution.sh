#!/bin/bash
# Solution for the cache-stats-read lab.
F="$HOME/sys-lab/cstats/info.txt"
awk -F: '
 $1=="keyspace_hits"{h=$2} $1=="keyspace_misses"{m=$2} $1=="used_memory"{u=$2} $1=="maxmemory"{x=$2} $1=="evicted_keys"{e=$2}
 END{ printf "hit_ratio_percent=%d\nmemory_used_percent=%d\nunder_pressure=%s\ndb_load_multiplier=%d\n", 100*h/(h+m), 100*u/x, (e>0 && u/x>0.9) ? "yes" : "no", (h+m)/m }' "$F" > "$HOME/sys-lab/answers-cstats.txt"
cat "$HOME/sys-lab/answers-cstats.txt"
