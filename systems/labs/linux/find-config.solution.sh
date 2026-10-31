#!/bin/bash
# Solution for the find-config lab.
cd "$HOME/sys-lab/mess"
conf=$(find . -name app.conf)
big=$(find . -name '*.log' -size +1k | wc -l)
port=$(grep '^port=' "$conf" | cut -d= -f2)
printf 'conf=%s\nbigfiles=%s\nport=%s\n' "$conf" "$big" "$port" > "$HOME/sys-lab/answers.txt"
cat "$HOME/sys-lab/answers.txt"
