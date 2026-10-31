#!/bin/bash
# Solution for the short-code lab (written independently, with a lookup of digits).
python3 - <<'EOF'
import os, string
digits = string.digits + string.ascii_lowercase + string.ascii_uppercase
def to62(n):
    out = []
    while True:
        out.append(digits[n % 62]); n //= 62
        if n == 0: break
    return "".join(reversed(out))
ids = [int(x) for x in open(os.path.expanduser("~/sys-lab/short/ids.txt")).read().split()]
with open(os.path.expanduser("~/sys-lab/answers-short.txt"), "w") as f:
    f.write("codes=%s\nmax_ids_7=%d\n" % (",".join(to62(i) for i in ids), 62 ** 7))
print(open(os.path.expanduser("~/sys-lab/answers-short.txt")).read())
EOF
