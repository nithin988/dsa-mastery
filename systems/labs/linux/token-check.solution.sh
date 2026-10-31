#!/bin/bash
# Solution for the token-check lab.
python3 - <<'EOF'
import base64, hashlib, hmac, json, os, time
D = os.path.expanduser("~/sys-lab/tokens/")
secret = b"lab-secret-not-for-real-use"
pad = lambda s: s + "=" * (-len(s) % 4)
valid, admin = [], ""
for name in ("t1", "t2", "t3"):
    h, p, s = open(D + name + ".txt").read().strip().split(".")
    claims = json.loads(base64.urlsafe_b64decode(pad(p)))
    good = hmac.compare_digest(base64.urlsafe_b64encode(hmac.new(secret, (h + "." + p).encode(), hashlib.sha256).digest()).rstrip(b"=").decode(), s)
    if good and claims["exp"] > time.time():
        valid.append(name)
    if claims.get("role") == "admin":
        admin = name
open(os.path.expanduser("~/sys-lab/answers-token.txt"), "w").write("valid=%s\nclaims_admin=%s\n" % (",".join(valid), admin))
print(open(os.path.expanduser("~/sys-lab/answers-token.txt")).read())
EOF
