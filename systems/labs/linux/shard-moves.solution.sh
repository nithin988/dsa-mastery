#!/bin/bash
# Solution for the shard-moves lab.
cd "$HOME/sys-lab/shard"
ring=$(python3 ring.py | awk '{print $2}')
mod=$(python3 - <<'EOF'
import hashlib
keys = open("keys.txt").read().split()
h = lambda k: int(hashlib.md5(k.encode()).hexdigest()[:8], 16)
print(sum(1 for k in keys if h(k) % 4 != h(k) % 5))
EOF
)
printf 'mod_moved=%s\nring_moved=%s\n' "$mod" "$ring" > "$HOME/sys-lab/answers-shard.txt"
cat "$HOME/sys-lab/answers-shard.txt"
