#!/bin/bash
# Solution for the snowflake-id lab (shell arithmetic).
id=$(sed -n '3p' "$HOME/sys-lab/snow/ids.txt")
printf 'ms=%s\nmachine=%s\nseq=%s\n' "$(( id >> 22 ))" "$(( (id >> 12) & 1023 ))" "$(( id & 4095 ))" > "$HOME/sys-lab/answers-snow.txt"
cat "$HOME/sys-lab/answers-snow.txt"
