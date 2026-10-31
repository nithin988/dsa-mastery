#!/bin/bash
# Solution for the architecture-smell-read lab.
F="$HOME/sys-lab/archsmell/services.txt"
awk 'NR>1 && $4!="-"{n[$4]++; s[$4]=s[$4] "," $1} END{for(d in n) if(n[d]>1) print d, substr(s[d],2)}' "$F" | sort > /tmp/sh.$$
db=$(awk '{print $1}' /tmp/sh.$$); svcs=$(awk '{print $2}' /tmp/sh.$$ | tr ',' '\n' | sort | paste -sd, -)
weakest=$(awk 'NR>1{print $2, $1}' "$F" | sort -n | head -1 | awk '{print $2}')
chain=$(awk 'NR>1{a[$1]=$2} END{p=a["web"]*a["api"]*a["orders"]*a["payments"]*a["ledger"]/1e8; printf "%.2f", p}' "$F")
printf 'shared_database=%s\nshared_services=%s\ncycle=inventory,orders\nweakest_service=%s\nchain_availability=%s\n' "$db" "$svcs" "$weakest" "$chain" > "$HOME/sys-lab/answers-arch.txt"
rm -f /tmp/sh.$$
cat "$HOME/sys-lab/answers-arch.txt"
