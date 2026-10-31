#!/bin/bash
# Lab: quorum arithmetic for replicated stores. Only creates ~/sys-lab/quorum.
set -e
L="$HOME/sys-lab"
rm -rf "$L/quorum" "$L/check-quorum-math.sh" "$L/answers-quorum.txt"
mkdir -p "$L/quorum"
cat > "$L/quorum/scenarios.txt" <<'EOS'
A replicated store has N copies of every item. A write succeeds when W copies acknowledge it.
A read asks R copies and returns the newest value it sees.

Rule 1: a read is GUARANTEED to see the latest acknowledged write if  W + R > N.
Rule 2: writes keep working while at most  N - W  copies are down.

Scenario  N  W  R
s1        3  2  2
s2        3  1  1
s3        5  3  3
s4        5  2  3
s5        7  4  4

For each scenario write a line in ~/sys-lab/answers-quorum.txt like:
s1=yes/1
meaning: yes (reads are guaranteed fresh) / 1 (copies that may be down for writes to still work).
Use yes or no for the first part.
EOS

cat > "$L/check-quorum-math.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-quorum.txt"
ok=1
chk() { got=$([ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2- | tr -d ' '); if [ "$got" = "$2" ]; then echo "PASS: $1"; else echo "FAIL: $1 (apply the two rules; format yes/1 or no/2)"; ok=0; fi; }
chk s1 yes/1; chk s2 no/2; chk s3 yes/2; chk s4 no/3; chk s5 yes/3
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-quorum-math.sh"
echo "Lab ready. Read ~/sys-lab/quorum/scenarios.txt"
