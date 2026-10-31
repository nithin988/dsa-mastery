#!/bin/bash
# Lab: choose a shard key from real traffic numbers. No services needed. Only creates ~/sys-lab/shardkey.
set -e
L="$HOME/sys-lab"
rm -rf "$L/shardkey" "$L/check-shard-key-choice.sh" "$L/answers-shardkey.txt"
mkdir -p "$L/shardkey"
python3 - <<'EOF'
import random, os
rng = random.Random(11)
rows = []
for i in range(6000):
    # a few huge tenants (accounts), many small ones; users inside a tenant; orders have unique ids
    tenant = 1 if rng.random() < 0.45 else rng.randint(2, 200)
    user = rng.randint(1, 5000) if tenant != 1 else rng.randint(1, 5000)
    rows.append((i + 1, tenant, user))
with open(os.path.expanduser("~/sys-lab/shardkey/requests.csv"), "w") as f:
    f.write("order_id,tenant_id,user_id\n")
    for r in rows: f.write("%d,%d,%d\n" % r)
EOF
cat > "$L/shardkey/README.txt" <<'EOF'
requests.csv holds 6000 requests with the order, tenant and user each touched. One tenant (tenant_id 1) is a very large customer.
You plan 4 shards. A request goes to shard (key mod 4) for the key you choose.

Questions (write key=value lines into ~/sys-lab/answers-shardkey.txt):
1. tenant_busiest_share: the percentage of requests (whole number, rounded down) that land on the busiest shard if you shard by tenant_id
2. user_busiest_share:   the same, sharding by user_id
3. order_busiest_share:  the same, sharding by order_id
4. best_key:             which of tenant_id, user_id, order_id gives the most even spread

Hint: for each key, count requests per (key mod 4) with awk or sort and uniq, then take the biggest count divided by 6000.
EOF
cat > "$L/check-shard-key-choice.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-shardkey.txt"
F="$HOME/sys-lab/shardkey/requests.csv"
ok=1
share() { awk -F, -v c="$1" 'NR>1{n[$c%4]++; t++} END{m=0; for(k in n) if(n[k]>m) m=n[k]; print int(100*m/t)}' "$F"; }
chk() { got=$([ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2- | tr -d ' %'); if [ "$got" = "$2" ]; then echo "PASS: $1"; else echo "FAIL: $1 ($3)"; ok=0; fi; }
chk tenant_busiest_share "$(share 2)" "count requests per (tenant_id mod 4); the big tenant lands on one shard"
chk user_busiest_share "$(share 3)" "count requests per (user_id mod 4)"
chk order_busiest_share "$(share 1)" "count requests per (order_id mod 4)"
got=$([ -f "$A" ] && grep "^best_key=" "$A" | head -1 | cut -d= -f2- | tr -d ' ')
case "$got" in tenant_id) c=2;; user_id) c=3;; order_id) c=1;; *) c=0;; esac
min=$(for k in 1 2 3; do share $k; done | sort -n | head -1)
if [ "$c" != 0 ] && [ "$(share $c)" = "$min" ]; then echo "PASS: best_key"; else echo "FAIL: best_key (pick the key whose busiest share is smallest; tenant_id is the skewed one)"; ok=0; fi
[ $ok = 1 ] && { echo "All tasks done. A key with a few huge values (a big tenant) creates a hot shard; a high-cardinality key spreads load but scatters related data."; exit 0; } || exit 1
EOF
chmod +x "$L/check-shard-key-choice.sh"
echo "Lab ready. Read ~/sys-lab/shardkey/README.txt"
