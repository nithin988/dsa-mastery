#!/bin/bash
# Lab: read a saved API traffic capture and find the contract bugs. No services needed. Only creates ~/sys-lab/apiread.
set -e
L="$HOME/sys-lab"
rm -rf "$L/apiread" "$L/check-api-contract-read.sh" "$L/answers-api.txt"
mkdir -p "$L/apiread"
cat > "$L/apiread/traffic.txt" <<'EOF'
10:00:01 app-17  POST /orders {"item":7,"qty":1}   -> 201 Created, Location: /orders/41
10:00:03 app-17  POST /orders {"item":7,"qty":1}   -> 201 Created, Location: /orders/42
10:00:05 app-22  GET  /orders/999                  -> 200 OK {"error":"no such order"}
10:00:06 app-31  GET  /search?q=shoes              -> 429 Too Many Requests, Retry-After: 2
10:00:06 app-31  GET  /search?q=shoes              -> 429 Too Many Requests, Retry-After: 2
10:00:06 app-31  GET  /search?q=shoes              -> 429 Too Many Requests, Retry-After: 2
10:00:08 app-31  GET  /search?q=shoes              -> 200 OK
10:00:09 app-40  GET  /search?q=boots              -> 429 Too Many Requests, Retry-After: 2
10:00:11 app-40  GET  /search?q=boots              -> 200 OK
EOF
cat > "$L/apiread/README.txt" <<'EOF'
traffic.txt is a capture of API calls: time, client, request, response.

Questions (write key=value lines into ~/sys-lab/answers-api.txt):
1. duplicate_orders:   the two order numbers created by one retried request, comma separated, lower first
2. missing_header:     the request header that would have made the retry safe
3. wrong_status_path:  the path of the request that reported an error with the wrong status code
4. right_status:       the status code that response should have used
5. ignoring_client:    the client that kept calling immediately instead of honouring Retry-After
EOF
cat > "$L/check-api-contract-read.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-api.txt"
ok=1
chk() { got=$([ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2- | tr -d ' '); if [ "$got" = "$2" ]; then echo "PASS: $1"; else echo "FAIL: $1 ($3)"; ok=0; fi; }
chk duplicate_orders 41,42 "two identical POSTs, two Locations"
chk missing_header Idempotency-Key "the header that makes a POST retry return the stored result"
chk wrong_status_path /orders/999 "an error returned with status 200"
chk right_status 404 "a missing resource is 404"
chk ignoring_client app-31 "three requests in the same second after Retry-After: 2"
[ $ok = 1 ] && { echo "All tasks done. Missing idempotency keys duplicate orders; error bodies with 200 hide failures; Retry-After exists to be honoured."; exit 0; } || exit 1
EOF
chmod +x "$L/check-api-contract-read.sh"
echo "Lab ready. Read ~/sys-lab/apiread/README.txt"
