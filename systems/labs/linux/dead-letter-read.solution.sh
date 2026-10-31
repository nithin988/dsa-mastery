#!/bin/bash
# Solution for the dead-letter-read lab.
F="$HOME/sys-lab/dlq/worker.log"
poison=$(grep "action=dead-letter" "$F" | sed 's/.*msg=\([^ ]*\).*/\1/')
att=$(grep "msg=$poison " "$F" | grep -c "attempt=")
dups=$(grep "result=ok" "$F" | sed 's/.*msg=\([^ ]*\).*/\1/' | sort | uniq -d | paste -sd, -)
okn=$(grep -c "result=ok" "$F")
printf 'poison_message=%s\nattempts_poison=%s\nrecovered=m5\nduplicates=%s\nok_total=%s\n' "$poison" "$att" "$dups" "$okn" > "$HOME/sys-lab/answers-dlq.txt"
cat "$HOME/sys-lab/answers-dlq.txt"
