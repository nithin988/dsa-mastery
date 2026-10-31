#!/bin/bash
# Lab: turn numeric IDs into short base62 codes and size the code space. Only creates ~/sys-lab/short.
set -e
L="$HOME/sys-lab"
rm -rf "$L/short" "$L/check-short-code.sh" "$L/answers-short.txt"
mkdir -p "$L/short"
printf '%s\n' 125 62 3844 1000000 2147483647 > "$L/short/ids.txt"
cat > "$L/short/README.txt" <<'EOS'
A URL shortener turns a unique number into a short code using base62.
Alphabet (in this order, value 0 first):  0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
So value 0 is '0', value 10 is 'a', value 35 is 'z', value 36 is 'A', value 61 is 'Z', value 62 is '10'.
(Like decimal, but with 62 symbols; no leading zeros.)

ids.txt has five numbers, one per line.
Questions:
1. codes: the base62 code of each id in order, joined with commas (no spaces), e.g.  codes=a,b,c,d,e
2. max_ids_7: how many different codes exist with exactly 7 characters allowed to be any of the 62 symbols
   (i.e. 62 to the power 7, ignoring leading-zero rules).
EOS
python3 - <<'EOF'
import os
A = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
def enc(n):
    if n == 0: return "0"
    s = ""
    while n:
        n, r = divmod(n, 62); s = A[r] + s
    return s
L = os.path.expanduser("~/sys-lab/short")
ids = [int(x) for x in open(L + "/ids.txt").read().split()]
open(L + "/.expected", "w").write(",".join(enc(i) for i in ids) + " " + str(62 ** 7) + "\n")
EOF
cat > "$L/check-short-code.sh" <<'EOF'
#!/bin/bash
L="$HOME/sys-lab"
A="$L/answers-short.txt"
read -r ec em < "$L/short/.expected"
ok=1
get() { [ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2- | tr -d ' '; }
[ "$(get codes)" = "$ec" ] && echo "PASS: codes" || { echo "FAIL: codes= is the base62 code of each id, comma-separated, using the alphabet in README.txt"; ok=0; }
[ "$(get max_ids_7)" = "$em" ] && echo "PASS: max_ids_7" || { echo "FAIL: max_ids_7= is 62 to the power 7"; ok=0; }
[ $ok = 1 ] && { echo "All tasks done. 7 characters give trillions of links."; exit 0; } || exit 1
EOF
chmod +x "$L/check-short-code.sh"
echo "Lab ready. See ~/sys-lab/short/README.txt"
