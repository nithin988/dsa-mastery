#!/bin/bash
# Solution for the idempotent-pay lab (independent implementation in Python).
python3 - <<'EOF'
import os
naive = safe = dup = 0
seen = set()
for line in open(os.path.expanduser("~/sys-lab/pay/payments.log")):
    if line.startswith("#") or not line.strip():
        continue
    key, amt = line.split()
    naive += int(amt)
    if key in seen:
        dup += 1
    else:
        seen.add(key)
        safe += int(amt)
open(os.path.expanduser("~/sys-lab/answers-pay.txt"), "w").write("naive_total=%d\nsafe_total=%d\nduplicates=%d\n" % (naive, safe, dup))
print(open(os.path.expanduser("~/sys-lab/answers-pay.txt")).read())
EOF
