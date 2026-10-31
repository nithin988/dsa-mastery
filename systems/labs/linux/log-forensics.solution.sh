#!/bin/bash
# Solution for the log-forensics lab.
cd "$HOME/sys-lab/forensics"
errors=$(grep -c ' ERROR ' app.log)
topmsg=$(awk '$3=="ERROR"{print $4}' app.log | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')
warnms=$(awk '$3=="WARN"{s+=$5} END{print s}' app.log)
printf 'errors=%s\ntopmsg=%s\nwarnms=%s\n' "$errors" "$topmsg" "$warnms" > "$HOME/sys-lab/answers-forensics.txt"
cat "$HOME/sys-lab/answers-forensics.txt"
