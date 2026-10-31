#!/bin/bash
# Solution for the shard-key-choice lab.
F="$HOME/sys-lab/shardkey/requests.csv"
share() { awk -F, -v c="$1" 'NR>1{n[$c%4]++; t++} END{m=0; for(k in n) if(n[k]>m) m=n[k]; print int(100*m/t)}' "$F"; }
best=order_id; [ "$(share 3)" -lt "$(share 1)" ] && best=user_id
printf 'tenant_busiest_share=%s\nuser_busiest_share=%s\norder_busiest_share=%s\nbest_key=%s\n' "$(share 2)" "$(share 3)" "$(share 1)" "$best" > "$HOME/sys-lab/answers-shardkey.txt"
cat "$HOME/sys-lab/answers-shardkey.txt"
