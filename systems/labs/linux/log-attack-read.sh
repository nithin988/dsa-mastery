#!/bin/bash
# Lab: read authentication and web logs and find the attack. No services needed. Only creates ~/sys-lab/attacklog.
set -e
L="$HOME/sys-lab"
rm -rf "$L/attacklog" "$L/check-log-attack-read.sh" "$L/answers-attack.txt"
mkdir -p "$L/attacklog"
cat > "$L/attacklog/auth.log" <<'EOF'
10:00:01 203.0.113.9   admin  FAIL
10:00:02 203.0.113.9   admin  FAIL
10:00:03 203.0.113.9   root   FAIL
10:00:04 198.51.100.4  asha   OK
10:00:05 203.0.113.9   ben    FAIL
10:00:06 192.0.2.77    chen   FAIL
10:00:07 203.0.113.9   ben    FAIL
10:00:08 203.0.113.9   ben    OK
10:00:09 198.51.100.4  asha   OK
10:00:10 203.0.113.9   ben    OK
EOF
cat > "$L/attacklog/web.log" <<'EOF'
10:01:01 198.51.100.4  GET /items?id=5
10:01:03 203.0.113.9   GET /items?id=5' OR '1'='1
10:01:04 203.0.113.9   GET /search?q=x' UNION SELECT name,password_hash FROM users--
10:01:05 192.0.2.77    GET /items?id=7
10:01:09 203.0.113.9   GET /admin/export?table=users
10:01:11 198.51.100.4  GET /search?q=boots
EOF
cat > "$L/attacklog/README.txt" <<'EOF'
auth.log: time, source address, user, result (FAIL or OK).   web.log: time, source address, request.

Questions (write key=value lines into ~/sys-lab/answers-attack.txt):
1. attacker_ip:           the address with the most failed logins
2. failed_before_success: how many failed logins that address made before its first successful login
3. compromised_user:      the account that address logged into successfully
4. sqli_requests:         how many requests in web.log contain a SQL injection pattern (' OR or UNION SELECT, any case)
5. next_step:             what you do FIRST for the compromised account: reset or ignore
EOF
cat > "$L/check-log-attack-read.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-attack.txt"
ok=1
chk() { got=$([ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2- | tr -d ' '); if [ "$got" = "$2" ]; then echo "PASS: $1"; else echo "FAIL: $1 ($3)"; ok=0; fi; }
chk attacker_ip 203.0.113.9 "count FAIL lines per address"
chk failed_before_success 5 "admin x2, root, ben x2 before the first OK from that address"
chk compromised_user ben "the first OK from the attacking address"
chk sqli_requests 2 "one OR pattern and one UNION SELECT"
chk next_step reset "revoke sessions and force a password reset (and look for what the account did)"
[ $ok = 1 ] && { echo "All tasks done. Many failures from one address followed by a success is a compromised account: act on it first, then block, then investigate."; exit 0; } || exit 1
EOF
chmod +x "$L/check-log-attack-read.sh"
echo "Lab ready. Read ~/sys-lab/attacklog/README.txt"
