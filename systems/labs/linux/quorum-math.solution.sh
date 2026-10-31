#!/bin/bash
# Solution for the quorum-math lab: apply the two rules.
out="$HOME/sys-lab/answers-quorum.txt"
: > "$out"
while read -r name n w r; do
  if [ $((w + r)) -gt "$n" ]; then fresh=yes; else fresh=no; fi
  echo "$name=$fresh/$((n - w))" >> "$out"
done <<'EOF'
s1 3 2 2
s2 3 1 1
s3 5 3 3
s4 5 2 3
s5 7 4 4
EOF
cat "$out"
