#!/bin/bash
# Solution for the http-detective lab.
loc=$(curl -s -I http://127.0.0.1:8089/old | tr -d '\r' | awk -F': ' 'tolower($1)=="location"{print $2}')
tok=$(curl -s -I -L http://127.0.0.1:8089/old | tr -d '\r' | awk -F': ' 'tolower($1)=="x-token"{print $2}' | tail -1)
adm=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8089/admin)
printf 'location=%s\ntoken=%s\nadmin_status=%s\n' "$loc" "$tok" "$adm" > "$HOME/sys-lab/answers-http.txt"
cat "$HOME/sys-lab/answers-http.txt"
