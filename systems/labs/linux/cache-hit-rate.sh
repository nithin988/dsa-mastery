#!/bin/bash
# Lab: simulate an LRU cache over a request log and measure the hit count for two cache sizes. Only creates ~/sys-lab/cache.
set -e
L="$HOME/sys-lab"
rm -rf "$L/cache" "$L/check-cache-hit-rate.sh" "$L/answers-cache.txt"
mkdir -p "$L/cache"
echo "A B C A B D A E B A C F A B G A B C A D A B E A C B A F D A" | tr ' ' '\n' > "$L/cache/requests.txt"
cat > "$L/cache/README.txt" <<'EOS'
requests.txt has one cache key per line, in the order they were requested.
An LRU cache of size N keeps the N most recently USED keys. A request is a HIT if the key is
already in the cache, otherwise a MISS (the key is then loaded, evicting the least recently used key if full).
Questions: how many hits with a cache of size 3? with a cache of size 5?
EOS
lru() { awk -v cap="$1" '{k=$1; t++; if (k in last) {hits++} else { if (n>=cap) { mt=1e9; for (x in last) if (last[x]<mt) {mt=last[x]; m=x}; delete last[m]; n-- } n++ } last[k]=t} END{print hits+0}' "$L/cache/requests.txt"; }
echo "$(lru 3) $(lru 5)" > "$L/cache/.expected"

cat > "$L/check-cache-hit-rate.sh" <<'EOF'
#!/bin/bash
L="$HOME/sys-lab"
A="$L/answers-cache.txt"
read -r e3 e5 < "$L/cache/.expected"
ok=1
get() { [ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2-; }
[ "$(get hits_size3)" = "$e3" ] && echo "PASS: hits_size3" || { echo "FAIL: hits_size3= is the number of hits for an LRU cache of size 3 (replay requests.txt by hand or with a script)"; ok=0; }
[ "$(get hits_size5)" = "$e5" ] && echo "PASS: hits_size5" || { echo "FAIL: hits_size5= is the number of hits for an LRU cache of size 5"; ok=0; }
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-cache-hit-rate.sh"
echo "Lab ready. See ~/sys-lab/cache/README.txt and requests.txt"
