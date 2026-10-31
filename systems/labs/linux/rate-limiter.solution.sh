#!/bin/bash
# Solution for the rate-limiter lab (independent implementation in Python).
python3 - <<'EOF'
import os
times = [int(x) for x in open(os.path.expanduser("~/sys-lab/rl/requests.txt")).read().split()]
tokens, last, bucket_ok = 5, 0, 0
for t in times:
    tokens = min(5, tokens + (t - last))
    last = t
    if tokens >= 1:
        tokens -= 1
        bucket_ok += 1
count, window_ok = {}, 0
for t in times:
    w = t // 10
    if count.get(w, 0) < 4:
        count[w] = count.get(w, 0) + 1
        window_ok += 1
open(os.path.expanduser("~/sys-lab/answers-rl.txt"), "w").write("token_bucket_allowed=%d\nfixed_window_allowed=%d\n" % (bucket_ok, window_ok))
print(open(os.path.expanduser("~/sys-lab/answers-rl.txt")).read())
EOF
