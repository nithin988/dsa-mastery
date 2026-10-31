#!/bin/bash
# Lab: find the real config file in a messy tree. Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
M="$L/mess"
rm -rf "$M" "$L/answers.txt" "$L/check-find-config.sh"
mkdir -p "$M"/projects/blog/deploy "$M"/projects/blog/src "$M"/projects/shop/deploy "$M"/backups/2025 "$M"/tmp/cache "$M"/logs/old
printf 'port=8080\nmode=production\n' > "$M/projects/blog/deploy/app.conf"
printf 'port=9999\nmode=old\n' > "$M/projects/blog/deploy/app.conf.bak"
printf 'port=7777\n' > "$M/projects/shop/deploy/old_app.conf"
printf 'port=1111\n' > "$M/backups/2025/app.conf.2025"
printf 'print("blog")\n' > "$M/projects/blog/src/main.py"
for n in a b c d e f; do printf 'short log line\n' > "$M/logs/$n.log"; done
for n in big1 big2 big3; do head -c 2048 /dev/zero | tr '\0' 'x' > "$M/logs/old/$n.log"; done
printf 'cache\n' > "$M/tmp/cache/x.tmp"

cat > "$L/check-find-config.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers.txt"
ok=1
[ -f "$A" ] || { echo "FAIL: no answers file at ~/sys-lab/answers.txt"; exit 1; }
conf=$(grep '^conf=' "$A" | head -1 | cut -d= -f2- | sed 's#^\./##')
big=$(grep '^bigfiles=' "$A" | head -1 | cut -d= -f2-)
port=$(grep '^port=' "$A" | head -1 | cut -d= -f2-)
[ "$conf" = "projects/blog/deploy/app.conf" ] && echo "PASS: conf path" || { echo "FAIL: conf path (got '$conf')"; ok=0; }
[ "$big" = "3" ] && echo "PASS: bigfiles" || { echo "FAIL: bigfiles (got '$big')"; ok=0; }
[ "$port" = "8080" ] && echo "PASS: port" || { echo "FAIL: port (got '$port')"; ok=0; }
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-find-config.sh"
echo "Lab ready. Work in ~/sys-lab/mess and write your answers to ~/sys-lab/answers.txt"
cd "$M" 2>/dev/null || true
