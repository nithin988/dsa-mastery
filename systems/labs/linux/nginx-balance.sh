#!/bin/bash
# Lab: repair a broken nginx load balancer. Starts three practice backends (ports 9101 to 9103). Needs nginx and python3. Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
D="$L/nginxlab"
[ -f "$D/nginx.pid" ] && kill "$(cat "$D/nginx.pid")" 2>/dev/null || true
pkill -f 'nginxlab/backend.py' 2>/dev/null || true
rm -rf "$D" "$L/check-nginx-balance.sh" "$L/answers-nginx.txt"
mkdir -p "$D/t"
cat > "$D/backend.py" <<'EOS'
import sys, http.server, socketserver
name, port = sys.argv[1], int(sys.argv[2])
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        data = ("served by %s\n" % name).encode()
        self.send_response(200); self.send_header('Content-Length', str(len(data))); self.end_headers(); self.wfile.write(data)
    def log_message(self, *a): pass
class S(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True; allow_reuse_address = True
S(('127.0.0.1', port), H).serve_forever()
EOS
cat > "$D/common.conf" <<EOS
access_log off;
client_body_temp_path $D/t/b; proxy_temp_path $D/t/p; fastcgi_temp_path $D/t/f; uwsgi_temp_path $D/t/u; scgi_temp_path $D/t/s;
EOS
cat > "$D/balancer.conf" <<EOS
worker_processes 1; pid $D/nginx.pid; error_log $D/error.log;
events { worker_connections 256; }
http {
  include $D/common.conf;
  upstream app {
    server 127.0.0.1:9101;
    server 127.0.0.1:9102
  }
  server {
    listen 127.0.0.1:8190;
    location / { proxy_pass http://apps; }
  }
}
EOS
for spec in A:9101 B:9102 C:9103; do
  nohup python3 "$D/backend.py" "${spec%:*}" "${spec#*:}" > /dev/null 2>&1 &
done
sleep 1
cat > "$L/check-nginx-balance.sh" <<'EOF'
#!/bin/bash
D="$HOME/sys-lab/nginxlab"
ok=1
if nginx -t -c "$D/balancer.conf" -p "$D/" >/dev/null 2>&1; then echo "PASS: nginx -t accepts the configuration"; else echo "FAIL: nginx -t still reports errors (run: nginx -t -c $D/balancer.conf -p $D/)"; ok=0; fi
if [ -f "$D/nginx.pid" ] && kill -0 "$(cat "$D/nginx.pid")" 2>/dev/null; then echo "PASS: nginx is running"; else echo "FAIL: nginx is not running: nginx -c $D/balancer.conf -p $D/"; ok=0; fi
counts=$(for i in $(seq 1 9); do curl -s -m 3 http://127.0.0.1:8190/; done | sort | uniq -c | awk '{printf "%s ", $1}')
if [ "$counts" = "3 3 3 " ]; then echo "PASS: nine requests were spread 3/3/3 over three servers"; else echo "FAIL: nine requests gave the spread '$counts' (expected 3 3 3: all three backends must be in the upstream)"; ok=0; fi
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-nginx-balance.sh"
echo "Lab ready. Config: $D/balancer.conf   Test: nginx -t -c $D/balancer.conf -p $D/"
