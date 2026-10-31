#!/bin/bash
# Lab: "Address already in use". Find what holds a port and start the real app on it.
# Starts one practice process (a squatter on 127.0.0.1:8088). Only touches ~/sys-lab. Needs python3.
set -e
L="$HOME/sys-lab"
pkill -f 'sys-lab/net/squatter.py' 2>/dev/null || true
pkill -f 'sys-lab/net/webapp.py' 2>/dev/null || true
rm -rf "$L/net" "$L/check-port-detective.sh" "$L/answers-port.txt"
mkdir -p "$L/net"

cat > "$L/net/squatter.py" <<'EOS'
import http.server, socketserver
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"squatter\n")
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
socketserver.TCPServer(("127.0.0.1", 8088), H).serve_forever()
EOS

cat > "$L/net/webapp.py" <<'EOS'
# The real application: answers /ping with "pong" on 127.0.0.1:8088.
import http.server, socketserver
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"pong\n" if self.path == "/ping" else b"not found\n"
        self.send_response(200 if self.path == "/ping" else 404); self.end_headers(); self.wfile.write(body)
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
try:
    srv = socketserver.TCPServer(("127.0.0.1", 8088), H)
except OSError as e:
    raise SystemExit("webapp: cannot listen on 8088: %s" % e)
srv.serve_forever()
EOS

nohup python3 "$L/net/squatter.py" > /dev/null 2>&1 &
sleep 1

cat > "$L/check-port-detective.sh" <<'EOF'
#!/bin/bash
L="$HOME/sys-lab"
ok=1
if pgrep -f 'sys-lab/net/squatter.py' >/dev/null; then echo "FAIL: the squatter still holds port 8088"; ok=0; else echo "PASS: the squatter is stopped"; fi
body=$(curl -s -m 3 http://127.0.0.1:8088/ping)
if [ "$body" = "pong" ]; then echo "PASS: the real app answers /ping with pong"; else echo "FAIL: http://127.0.0.1:8088/ping did not answer pong (got: '$body'). Start it: python3 ~/sys-lab/net/webapp.py &"; ok=0; fi
if pgrep -f 'sys-lab/net/webapp.py' >/dev/null; then echo "PASS: webapp.py is running"; else echo "FAIL: webapp.py is not running"; ok=0; fi
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-port-detective.sh"
echo "Lab ready. Try: python3 ~/sys-lab/net/webapp.py   (it will fail: the port is taken)"
