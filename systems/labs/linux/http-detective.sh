#!/bin/bash
# Lab: read an HTTP conversation with curl. Starts a small practice web server on 127.0.0.1:8089. Only touches ~/sys-lab. Needs python3.
set -e
L="$HOME/sys-lab"
pkill -f 'sys-lab/net2/server.py' 2>/dev/null || true
rm -rf "$L/net2" "$L/check-http-detective.sh" "$L/answers-http.txt"
mkdir -p "$L/net2"

cat > "$L/net2/server.py" <<'EOS'
import http.server, socketserver, hashlib
TOKEN = "T-" + hashlib.sha1(b"sys-lab-http").hexdigest()[:8]
class H(http.server.BaseHTTPRequestHandler):
    def reply(self, head_only):
        def send(code, headers=(), body=b""):
            self.send_response(code)
            for k, v in headers:
                self.send_header(k, v)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if not head_only:
                self.wfile.write(body)
        if self.path == "/old":
            send(301, [("Location", "/moved/here")])
        elif self.path == "/moved/here":
            send(200, [("X-Token", TOKEN)], b"you made it\n")
        elif self.path == "/admin":
            send(403, [], b"forbidden\n")
        else:
            send(404, [], b"nothing here\n")
    def do_GET(self): self.reply(False)
    def do_HEAD(self): self.reply(True)
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
socketserver.TCPServer(("127.0.0.1", 8089), H).serve_forever()
EOS
nohup python3 "$L/net2/server.py" > /dev/null 2>&1 &
sleep 1

cat > "$L/check-http-detective.sh" <<'EOF'
#!/bin/bash
L="$HOME/sys-lab"
A="$L/answers-http.txt"
ok=1
get() { [ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2-; }
tok=$(curl -s -m 3 -I -L http://127.0.0.1:8089/old | tr -d '\r' | awk -F': ' 'tolower($1)=="x-token"{print $2}' | tail -1)
[ -n "$tok" ] || { echo "FAIL: the practice server on port 8089 is not running; run the setup script again"; exit 1; }
[ "$(get location)" = "/moved/here" ] && echo "PASS: location" || { echo "FAIL: location= should be where /old redirects to (the Location header)"; ok=0; }
[ "$(get token)" = "$tok" ] && echo "PASS: token" || { echo "FAIL: token= should be the X-Token header of the final page"; ok=0; }
[ "$(get admin_status)" = "403" ] && echo "PASS: admin_status" || { echo "FAIL: admin_status= should be the status code of /admin"; ok=0; }
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-http-detective.sh"
echo "Lab ready. A web server is listening on http://127.0.0.1:8089"
