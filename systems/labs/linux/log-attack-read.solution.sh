#!/bin/bash
# Solution for the log-attack-read lab.
D="$HOME/sys-lab/attacklog"
ip=$(awk '$4=="FAIL"{n[$2]++} END{for(i in n) print n[i], i}' "$D/auth.log" | sort -rn | head -1 | awk '{print $2}')
fails=$(awk -v ip="$ip" '$2==ip && $4=="OK"{exit} $2==ip && $4=="FAIL"{c++} END{print c+0}' "$D/auth.log")
user=$(awk -v ip="$ip" '$2==ip && $4=="OK"{print $3; exit}' "$D/auth.log")
sqli=$(grep -ciE "' or |union select" "$D/web.log")
printf 'attacker_ip=%s\nfailed_before_success=%s\ncompromised_user=%s\nsqli_requests=%s\nnext_step=reset\n' "$ip" "$fails" "$user" "$sqli" > "$HOME/sys-lab/answers-attack.txt"
cat "$HOME/sys-lab/answers-attack.txt"
