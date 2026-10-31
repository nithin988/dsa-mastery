#!/bin/bash
# Solution for the lb-distribution lab.
cd "$HOME/sys-lab/lb"
declare -a c=(0 0 0)
moved=0
while read -r u; do
  x=$(printf '%s' "$u" | cksum | cut -d' ' -f1)
  a=$((x % 3)); b=$((x % 2))
  c[$a]=$(( ${c[$a]} + 1 ))
  if [ "$a" -ne "$b" ]; then moved=$((moved + 1)); fi
done < users.txt
printf 'server0=%s\nserver1=%s\nserver2=%s\nmoved=%s\n' "${c[0]}" "${c[1]}" "${c[2]}" "$moved" > "$HOME/sys-lab/answers-lb.txt"
cat "$HOME/sys-lab/answers-lb.txt"
