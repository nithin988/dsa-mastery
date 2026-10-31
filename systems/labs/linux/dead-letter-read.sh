#!/bin/bash
# Lab: read a saved worker log and find the poison message and the duplicates. No services needed. Only creates ~/sys-lab/dlq.
set -e
L="$HOME/sys-lab"
rm -rf "$L/dlq" "$L/check-dead-letter-read.sh" "$L/answers-dlq.txt"
mkdir -p "$L/dlq"
cat > "$L/dlq/worker.log" <<'EOF'
10:00:01 msg=m1 attempt=1 result=ok
10:00:01 msg=m2 attempt=1 result=ok
10:00:02 msg=m3 attempt=1 result=error "parse error: unexpected token"
10:00:03 msg=m4 attempt=1 result=ok
10:00:04 msg=m3 attempt=2 result=error "parse error: unexpected token"
10:00:05 msg=m5 attempt=1 result=timeout
10:00:06 msg=m6 attempt=1 result=ok
10:00:08 msg=m3 attempt=3 result=error "parse error: unexpected token"
10:00:09 msg=m5 attempt=2 result=ok
10:00:09 msg=m3 action=dead-letter reason="max attempts (3) reached"
10:00:10 msg=m7 attempt=1 result=ok
10:00:11 msg=m2 attempt=1 result=ok
10:00:12 msg=m8 attempt=1 result=ok
10:00:12 msg=m7 attempt=1 result=ok
EOF
cat > "$L/dlq/README.txt" <<'EOF'
worker.log is the log of one consumer reading a queue with at-least-once delivery and a limit of 3 attempts per message.

Questions (write key=value lines into ~/sys-lab/answers-dlq.txt):
1. poison_message:    the message that failed every time and was dead-lettered
2. attempts_poison:   how many attempts it was given before going to the dead-letter queue
3. recovered:         the message that failed once (a timeout) but succeeded on retry
4. duplicates:        the messages that were processed successfully more than once, comma separated, sorted (look for the same msg with result=ok twice)
5. ok_total:          the number of log lines with result=ok (counts duplicates as separate lines)
EOF
cat > "$L/check-dead-letter-read.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-dlq.txt"
ok=1
chk() { got=$([ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2- | tr -d ' '); if [ "$got" = "$2" ]; then echo "PASS: $1"; else echo "FAIL: $1 ($3)"; ok=0; fi; }
chk poison_message m3 "the one with action=dead-letter"
chk attempts_poison 3 "attempt=3 was the last"
chk recovered m5 "timeout on attempt 1, ok on attempt 2"
chk duplicates m2,m7 "each has result=ok on two lines: redelivered and processed again, so handlers must be idempotent"
chk ok_total 9 "count the lines containing result=ok"
[ $ok = 1 ] && { echo "All tasks done. One poison message was isolated after 3 attempts; two messages were processed twice: at-least-once delivery means idempotent handlers."; exit 0; } || exit 1
EOF
chmod +x "$L/check-dead-letter-read.sh"
echo "Lab ready. Read ~/sys-lab/dlq/README.txt"
