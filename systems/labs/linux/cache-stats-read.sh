#!/bin/bash
# Lab: diagnose a cache from saved `redis-cli INFO` output. No services needed. Only creates ~/sys-lab/cstats.
set -e
L="$HOME/sys-lab"
rm -rf "$L/cstats" "$L/check-cache-stats-read.sh" "$L/answers-cstats.txt"
mkdir -p "$L/cstats"
cat > "$L/cstats/info.txt" <<'EOS'
# Memory
used_memory:2097120
used_memory_human:2.00M
maxmemory:2097152
maxmemory_human:2.00M
maxmemory_policy:allkeys-lru
# Stats
total_connections_received:1842
total_commands_processed:912500
keyspace_hits:600000
keyspace_misses:300000
expired_keys:41000
evicted_keys:128000
# Keyspace
db0:keys=15200,expires=15200,avg_ttl=48211
EOS
cat > "$L/cstats/README.txt" <<'EOS'
info.txt is the output of `redis-cli INFO` from a production cache, trimmed to the relevant lines.
Definitions:   hit ratio = hits / (hits + misses)    evicted_keys = keys thrown out because memory was full
               expired_keys = keys removed because their TTL ran out

Questions (write key=value lines into ~/sys-lab/answers-cstats.txt):
1. hit_ratio_percent:  the cache hit ratio as a whole percentage
2. memory_used_percent: used_memory as a whole percentage of maxmemory (round down)
3. under_pressure:     yes or no: is the cache evicting keys because it is full? (look at memory and evicted_keys)
4. db_load_multiplier: if the cache were turned off, how many times more reads would the database get?
                       (all reads would go to the database: total reads divided by the reads the database sees today, which are the misses)
EOS
cat > "$L/check-cache-stats-read.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-cstats.txt"
ok=1
chk() { got=$([ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2- | tr -d ' %x'); if [ "$got" = "$2" ]; then echo "PASS: $1"; else echo "FAIL: $1 ($3)"; ok=0; fi; }
chk hit_ratio_percent 66 "600000 / (600000 + 300000) = 66.6%, give 66 (round down)"
chk memory_used_percent 99 "2097120 / 2097152"
chk under_pressure yes "memory is almost full and evicted_keys is large"
chk db_load_multiplier 3 "900000 reads in total vs 300000 misses today"
[ $ok = 1 ] && { echo "All tasks done. A one-third miss rate and 128,000 evictions: this cache is too small for its working set."; exit 0; } || exit 1
EOF
chmod +x "$L/check-cache-stats-read.sh"
echo "Lab ready. Read ~/sys-lab/cstats/README.txt"
