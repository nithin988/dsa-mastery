#!/bin/bash
# Lab: how many keys move when a node is added, with modulo hashing versus a consistent-hash ring. Only creates ~/sys-lab/shard.
set -e
L="$HOME/sys-lab"
rm -rf "$L/shard" "$L/check-shard-moves.sh" "$L/answers-shard.txt"
mkdir -p "$L/shard"
for i in $(seq -w 1 200); do echo "key$i"; done > "$L/shard/keys.txt"
cat > "$L/shard/ring.py" <<'EOS'
"""A tiny consistent-hash ring. Usage: python3 ring.py  (prints how many of the keys change owner when node n4 is added)."""
import bisect, hashlib, os

def h(s):
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)

def build(nodes, vnodes=50):
    ring = sorted((h("%s#%d" % (n, i)), n) for n in nodes for i in range(vnodes))
    return [p for p, _ in ring], [n for _, n in ring]

def owner(ring, key):
    pos, names = ring
    i = bisect.bisect_left(pos, h(key)) % len(pos)
    return names[i]

if __name__ == "__main__":
    keys = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys.txt")).read().split()
    before = build(["n0", "n1", "n2", "n3"])
    after = build(["n0", "n1", "n2", "n3", "n4"])
    moved = sum(1 for k in keys if owner(before, k) != owner(after, k))
    print("ring: %d of %d keys moved" % (moved, len(keys)))
EOS
cat > "$L/shard/README.txt" <<'EOS'
keys.txt has 200 keys. Option A (modulo): node = md5(key) mod N, using the first 8 hex digits of md5(key) as a number:
    python3 -c "import hashlib; print(int(hashlib.md5(b'key001').hexdigest()[:8],16) % 4)"
Option B: the consistent-hash ring in ring.py (4 nodes, then 5 nodes).
Questions:
1. With option A, how many of the 200 keys get a different node when N goes from 4 to 5?
2. With option B, how many keys move when the 5th node is added? (run: python3 ring.py)
EOS
export L
python3 - <<'EOF'
import hashlib, os, sys
L = os.environ["L"]
sys.path.insert(0, L + "/shard")
import ring
keys = open(L + "/shard/keys.txt").read().split()
h = lambda k: int(hashlib.md5(k.encode()).hexdigest()[:8], 16)
a = sum(1 for k in keys if h(k) % 4 != h(k) % 5)
b0, b1 = ring.build(["n0","n1","n2","n3"]), ring.build(["n0","n1","n2","n3","n4"])
b = sum(1 for k in keys if ring.owner(b0, k) != ring.owner(b1, k))
open(L + "/shard/.expected", "w").write("%d %d\n" % (a, b))
EOF

cat > "$L/check-shard-moves.sh" <<'EOF'
#!/bin/bash
L="$HOME/sys-lab"
A="$L/answers-shard.txt"
read -r ea eb < "$L/shard/.expected"
ok=1
get() { [ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2-; }
[ "$(get mod_moved)" = "$ea" ] && echo "PASS: mod_moved" || { echo "FAIL: mod_moved= is how many keys change node with md5-mod hashing from 4 to 5 nodes"; ok=0; }
[ "$(get ring_moved)" = "$eb" ] && echo "PASS: ring_moved" || { echo "FAIL: ring_moved= is the number printed by: python3 ~/sys-lab/shard/ring.py"; ok=0; }
[ $ok = 1 ] && { echo "All tasks done. Notice the difference between the two numbers."; exit 0; } || exit 1
EOF
chmod +x "$L/check-shard-moves.sh"
echo "Lab ready. See ~/sys-lab/shard/README.txt"
