#!/bin/bash
# Lab: find the one bad line in a 16-line config by halving. Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
rm -rf "$L/cfg" "$L/check-config-bisect.sh" "$L/answers-cfg.txt"
mkdir -p "$L/cfg"
bad=$(( ( $(printf '%s' "sys-lab-cfg" | cksum | cut -d' ' -f1) % 12 ) + 3 ))
for i in $(seq 1 16); do
  if [ "$i" -eq "$bad" ]; then echo "setting_$i = 12O"; else echo "setting_$i = $((i * 10))"; fi
done > "$L/cfg/app.conf"
cat > "$L/cfg/app" <<'EOS'
#!/bin/bash
# app: reads a config file (default: app.conf next to this script). Every value must be a whole number.
f="${1:-$(dirname "$0")/app.conf}"
while IFS= read -r line; do
  [ -z "$line" ] && continue
  v="${line#*= }"
  case "$v" in ''|*[!0-9]*) echo "app: invalid configuration" >&2; exit 1;; esac
done < "$f"
echo "app: started with $(grep -c . "$f") settings"
EOS
chmod +x "$L/cfg/app"
echo "$bad" > "$L/cfg/.expected"

cat > "$L/check-config-bisect.sh" <<'EOF'
#!/bin/bash
L="$HOME/sys-lab"
A="$L/answers-cfg.txt"
want=$(cat "$L/cfg/.expected")
got=""
[ -f "$A" ] && got=$(grep '^bad_line=' "$A" | head -1 | cut -d= -f2-)
if [ "$got" = "$want" ]; then echo "PASS: you found the bad line"; echo "All tasks done."; exit 0; fi
echo "FAIL: write bad_line=<line number> into ~/sys-lab/answers-cfg.txt (first run ~/sys-lab/cfg/app, then halve the file)"; exit 1
EOF
chmod +x "$L/check-config-bisect.sh"
echo "Lab ready. Run ~/sys-lab/cfg/app : it fails. Which line of ~/sys-lab/cfg/app.conf is bad?"
