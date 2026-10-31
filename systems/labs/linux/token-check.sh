#!/bin/bash
# Lab: inspect three signed tokens and decide which are valid. Only creates ~/sys-lab/tokens. Needs python3.
set -e
L="$HOME/sys-lab"
rm -rf "$L/tokens" "$L/check-token-check.sh" "$L/answers-token.txt"
mkdir -p "$L/tokens"
export L
python3 - <<'EOF'
import base64, hashlib, hmac, json, os
L = os.environ["L"] + "/tokens"
secret = b"lab-secret-not-for-real-use"
b64 = lambda b: base64.urlsafe_b64encode(b).rstrip(b"=").decode()
def sign(h, p):
    return b64(hmac.new(secret, (h + "." + p).encode(), hashlib.sha256).digest())
hdr = b64(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
def make(claims):
    p = b64(json.dumps(claims, separators=(",", ":")).encode())
    return hdr, p, sign(hdr, p)
h, p, s = make({"sub": "asha", "role": "user", "exp": 4102444800})
open(L + "/t1.txt", "w").write("%s.%s.%s\n" % (h, p, s))
h2, p2, s2 = make({"sub": "ben", "role": "user", "exp": 4102444800})
forged = b64(json.dumps({"sub": "ben", "role": "admin", "exp": 4102444800}, separators=(",", ":")).encode())
open(L + "/t2.txt", "w").write("%s.%s.%s\n" % (h2, forged, s2))
h3, p3, s3 = make({"sub": "chen", "role": "user", "exp": 1000})
open(L + "/t3.txt", "w").write("%s.%s.%s\n" % (h3, p3, s3))
EOF
cat > "$L/tokens/README.txt" <<'EOS'
Each file holds one token:  header.payload.signature  (three base64url parts joined by dots, as in a JWT).
Signature = base64url( HMAC-SHA256( secret, header + "." + payload ) ) with padding "=" removed.
The server secret is:  lab-secret-not-for-real-use      (real secrets are never shared like this)
A token is VALID if its signature matches AND its "exp" (expiry, seconds since 1970) is in the future.

Questions:
1. Which tokens are valid?  (list the file names without .txt, comma-separated, e.g. t1,t3)
2. Which token's payload CLAIMS role=admin (valid or not)?
EOS
cat > "$L/check-token-check.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-token.txt"
ok=1
get() { [ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2- | tr -d ' '; }
[ "$(get valid)" = "t1" ] && echo "PASS: valid" || { echo "FAIL: valid= lists tokens with a correct signature and a future exp (check both for every token)"; ok=0; }
[ "$(get claims_admin)" = "t2" ] && echo "PASS: claims_admin" || { echo "FAIL: claims_admin= is the token whose decoded payload says role admin"; ok=0; }
[ $ok = 1 ] && { echo "All tasks done. Note: a forged payload fails verification because the signature no longer matches."; exit 0; } || exit 1
EOF
chmod +x "$L/check-token-check.sh"
echo "Lab ready. See ~/sys-lab/tokens/README.txt"
