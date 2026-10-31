#!/bin/bash
# Lab: apply a payment log twice, with and without idempotency keys. Only creates ~/sys-lab/pay.
set -e
L="$HOME/sys-lab"
rm -rf "$L/pay" "$L/check-idempotent-pay.sh" "$L/answers-pay.txt"
mkdir -p "$L/pay"
cat > "$L/pay/payments.log" <<'EOS'
# idempotency_key amount_in_dollars   (the same key means the client retried the same payment)
k1001 20
k1002 35
k1002 35
k1003 12
k1004 50
k1004 50
k1004 50
k1005 8
k1006 27
k1003 12
k1007 100
k1008 15
k1008 15
EOS
cat > "$L/pay/README.txt" <<'EOS'
payments.log is the list of requests the payment server received (comments start with #).
A naive server charges every line. An idempotent server remembers each key and ignores repeats.
Questions:
1. naive_total: the total charged if every line is processed.
2. safe_total: the total charged when only the first request with each key is processed.
3. duplicates: how many requests were ignored as repeats in the idempotent case.
EOS
awk '!/^#/ && NF==2 {naive+=$2; if (seen[$1]++) dup++; else safe+=$2} END{print naive, safe, dup}' "$L/pay/payments.log" > "$L/pay/.expected"

cat > "$L/check-idempotent-pay.sh" <<'EOF'
#!/bin/bash
L="$HOME/sys-lab"
A="$L/answers-pay.txt"
read -r en es ed < "$L/pay/.expected"
ok=1
get() { [ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2-; }
[ "$(get naive_total)" = "$en" ] && echo "PASS: naive_total" || { echo "FAIL: naive_total= is the sum of every line's amount"; ok=0; }
[ "$(get safe_total)" = "$es" ] && echo "PASS: safe_total" || { echo "FAIL: safe_total= counts only the first line for each key"; ok=0; }
[ "$(get duplicates)" = "$ed" ] && echo "PASS: duplicates" || { echo "FAIL: duplicates= is the number of repeated-key lines"; ok=0; }
[ $ok = 1 ] && { echo "All tasks done. The difference between the totals is money wrongly charged by the naive server."; exit 0; } || exit 1
EOF
chmod +x "$L/check-idempotent-pay.sh"
echo "Lab ready. See ~/sys-lab/pay/README.txt"
