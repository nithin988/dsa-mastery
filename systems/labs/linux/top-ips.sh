#!/bin/bash
# Lab: top clients in a web log, using only a pipeline. Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
D="$L/weblogs"
rm -rf "$D" "$L/top3.txt" "$L/check-top-ips.sh"
mkdir -p "$D"
: > "$D/web.log"
for i in $(seq 1 50); do
  echo "10.0.0.1 GET /a" >> "$D/web.log"
  [ $((i % 5)) -lt 3 ] && echo "10.0.0.2 GET /b" >> "$D/web.log"
  [ $((i % 5)) -lt 2 ] && echo "10.0.0.3 POST /c" >> "$D/web.log"
  [ $((i % 5)) -eq 0 ] && echo "10.0.0.4 GET /a" >> "$D/web.log"
  [ $((i % 10)) -eq 0 ] && echo "10.0.0.5 GET /d" >> "$D/web.log"
done

cat > "$L/check-top-ips.sh" <<'EOF'
#!/bin/bash
F="$HOME/sys-lab/top3.txt"
[ -f "$F" ] || { echo "FAIL: ~/sys-lab/top3.txt does not exist"; exit 1; }
got=$(awk '{print $1" "$2}' "$F")
want=$(printf '50 10.0.0.1\n30 10.0.0.2\n20 10.0.0.3')
if [ "$got" = "$want" ]; then echo "PASS: top 3 clients are correct"; echo "All tasks done."; exit 0; fi
echo "FAIL: expected the top 3 as 'count ip', most requests first. Your file:"; cat "$F"; exit 1
EOF
chmod +x "$L/check-top-ips.sh"
echo "Lab ready. The log is ~/sys-lab/weblogs/web.log"
