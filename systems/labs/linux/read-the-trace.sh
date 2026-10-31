#!/bin/bash
# Lab: find the root cause in a noisy log with a buried stack trace. Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
rm -rf "$L/trace" "$L/check-read-the-trace.sh" "$L/answers-trace.txt"
mkdir -p "$L/trace"
{
  for m in 01 02 03 04 05 06; do
    echo "2026-03-02 09:${m}:11 INFO  request ok path=/home ms=$((m * 7))"
    echo "2026-03-02 09:${m}:15 INFO  request ok path=/cart ms=$((m * 9))"
  done
  echo "2026-03-02 09:07:02 WARN  slow request path=/checkout ms=2310"
  echo "2026-03-02 09:07:03 ERROR request failed path=/checkout status=500"
  echo "Traceback (most recent call last):"
  echo "  File \"/srv/shop/app.py\", line 88, in handle_checkout"
  echo "    total = compute_total(cart)"
  echo "  File \"/srv/shop/pricing.py\", line 41, in compute_total"
  echo "    rate = tax_rates[cart.country]"
  echo "KeyError: 'NZ'"
  for m in 08 09; do
    echo "2026-03-02 09:${m}:11 INFO  request ok path=/home ms=$((m * 3))"
    echo "2026-03-02 09:${m}:19 ERROR request failed path=/checkout status=500"
  done
} > "$L/trace/app.log"

cat > "$L/check-read-the-trace.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-trace.txt"
ok=1
get() { [ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2-; }
[ "$(get file)" = "pricing.py" ] && echo "PASS: file" || { echo "FAIL: file= should be the file where the error was raised (the LAST frame of the trace)"; ok=0; }
[ "$(get line)" = "41" ] && echo "PASS: line" || { echo "FAIL: line= is the line number in that file"; ok=0; }
[ "$(get missing_key)" = "NZ" ] && echo "PASS: missing_key" || { echo "FAIL: missing_key= is the value named in the KeyError"; ok=0; }
[ "$(get first_error_time)" = "09:07:03" ] && echo "PASS: first_error_time" || { echo "FAIL: first_error_time= is the time of the FIRST ERROR line (hh:mm:ss)"; ok=0; }
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-read-the-trace.sh"
echo "Lab ready. Read ~/sys-lab/trace/app.log"
