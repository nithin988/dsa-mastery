#!/bin/bash
# Solution for the cache-hit-rate lab (independent implementation in Python).
python3 - <<'EOF'
import os
from collections import OrderedDict
reqs = open(os.path.expanduser("~/sys-lab/cache/requests.txt")).read().split()
def hits(cap):
    c, h = OrderedDict(), 0
    for k in reqs:
        if k in c:
            h += 1
            c.move_to_end(k)
        else:
            if len(c) >= cap:
                c.popitem(last=False)
            c[k] = 1
    return h
open(os.path.expanduser("~/sys-lab/answers-cache.txt"), "w").write("hits_size3=%d\nhits_size5=%d\n" % (hits(3), hits(5)))
print(open(os.path.expanduser("~/sys-lab/answers-cache.txt")).read())
EOF
