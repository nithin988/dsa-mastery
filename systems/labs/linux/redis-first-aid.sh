#!/bin/bash
# Lab: investigate a live Redis. Starts a practice Redis on port 6392 (no password, local only). Needs redis-server and redis-cli. Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
D="$L/redislab"
redis-cli -p 6392 shutdown nosave 2>/dev/null || true
rm -rf "$D" "$L/check-redis-first-aid.sh" "$L/answers-redis.txt"
mkdir -p "$D"
redis-server --port 6392 --bind 127.0.0.1 --save "" --appendonly no --daemonize yes --dir "$D" --logfile "$D/redis.log" > /dev/null
sleep 1
python3 - <<'EOF'
import socket
s = socket.create_connection(("127.0.0.1", 6392)); f = s.makefile("rb")
def cmd(*a):
    out = b"*%d\r\n" % len(a)
    for x in a:
        x = str(x).encode(); out += b"$%d\r\n%s\r\n" % (len(x), x)
    s.sendall(out); f.readline()
for i in range(50): cmd("set", "session:%d" % i, "user-%d" % i, "EX", 300)
for i in range(30): cmd("set", "cache:page:%d" % i, "x" * 200, "EX", 60)
for i in range(5):  cmd("set", "config:%d" % i, "value")
cmd("set", "report:2026", "r" * 200000)
for i in range(20): cmd("set", "leak:%d" % i, "y" * 1000)
EOF
cat > "$D/README.txt" <<'EOS'
A practice Redis is running on 127.0.0.1 port 6392.   Connect with:  redis-cli -p 6392
Useful commands:  DBSIZE   SCAN 0 MATCH 'session:*' COUNT 1000   TTL key   MEMORY USAGE key   INFO memory
Some keys expire (they have a TTL), some never do. Never-expiring keys are the usual cause of a cache that "leaks" memory.

Questions (write key=value lines into ~/sys-lab/answers-redis.txt):
1. total_keys:        how many keys exist (DBSIZE)
2. session_keys:      how many keys start with "session:"
3. no_ttl_keys:       how many keys have NO expiry (TTL returns -1)
4. biggest_key:       the name of the key that uses the most memory (MEMORY USAGE)
EOS
cat > "$L/check-redis-first-aid.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-redis.txt"
redis-cli -p 6392 ping >/dev/null 2>&1 || { echo "FAIL: the practice Redis is not running; run the setup script again"; exit 1; }
ok=1
chk() { got=$([ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2- | tr -d ' '); if [ "$got" = "$2" ]; then echo "PASS: $1"; else echo "FAIL: $1 ($3)"; ok=0; fi; }
chk total_keys 106 "DBSIZE"
chk session_keys 50 "SCAN 0 MATCH 'session:*' COUNT 1000 (or count them yourself)"
chk no_ttl_keys 26 "keys whose TTL is -1: loop over all keys and run TTL on each"
chk biggest_key report:2026 "MEMORY USAGE on the candidates"
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-redis-first-aid.sh"
echo "Lab ready. Read ~/sys-lab/redislab/README.txt"
