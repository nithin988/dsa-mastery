#!/bin/bash
# Lab: replay a request log through two rate limiters. Only creates ~/sys-lab/rl.
set -e
L="$HOME/sys-lab"
rm -rf "$L/rl" "$L/check-rate-limiter.sh" "$L/answers-rl.txt"
mkdir -p "$L/rl"
echo "0 0 0 0 0 0 1 1 2 2 3 8 8 8 9 9 9 9 9 9 12 12" | tr ' ' '\n' > "$L/rl/requests.txt"
cat > "$L/rl/README.txt" <<'EOS'
requests.txt has one request time per line (whole seconds, in order).

Limiter A, token bucket: capacity 5 tokens, starts full, refills 1 token per second (never above 5).
  A request at time t first adds (t - previous request time) tokens, then needs 1 token to be allowed.
Limiter B, fixed window: windows are [0,10), [10,20), ...; at most 4 requests allowed per window.

Questions:
1. How many requests does limiter A allow?
2. How many requests does limiter B allow?
EOS
a=$(awk 'BEGIN{tok=5; last=0; ok=0} {t=$1; tok+=(t-last); if(tok>5)tok=5; last=t; if(tok>=1){tok--; ok++}} END{print ok}' "$L/rl/requests.txt")
b=$(awk 'BEGIN{ok=0} {w=int($1/10); if(c[w]<4){c[w]++; ok++}} END{print ok}' "$L/rl/requests.txt")
echo "$a $b" > "$L/rl/.expected"

cat > "$L/check-rate-limiter.sh" <<'EOF'
#!/bin/bash
L="$HOME/sys-lab"
A="$L/answers-rl.txt"
read -r ea eb < "$L/rl/.expected"
ok=1
get() { [ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2-; }
[ "$(get token_bucket_allowed)" = "$ea" ] && echo "PASS: token_bucket_allowed" || { echo "FAIL: token_bucket_allowed= replay the log: add elapsed seconds as tokens (max 5), spend one per allowed request"; ok=0; }
[ "$(get fixed_window_allowed)" = "$eb" ] && echo "PASS: fixed_window_allowed" || { echo "FAIL: fixed_window_allowed= at most 4 per ten-second window"; ok=0; }
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-rate-limiter.sh"
echo "Lab ready. See ~/sys-lab/rl/README.txt"
