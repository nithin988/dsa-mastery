#!/bin/bash
# Lab: find where the disk space went. Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
D="$L/disk"
rm -rf "$D" "$L/answers-disk.txt" "$L/check-disk-detective.sh"
mkdir -p "$D"/cache "$D"/media "$D"/logs "$D"/docs
for i in 1 2 3 4 5; do head -c 102400 /dev/zero > "$D/cache/c$i.bin"; done
head -c 3145728 /dev/zero > "$D/media/movie.bin"
head -c 204800 /dev/zero > "$D/media/song1.bin"
head -c 204800 /dev/zero > "$D/media/song2.bin"
for i in 1 2 3 4 5 6 7 8 9 10; do head -c 51200 /dev/zero > "$D/logs/l$i.log"; done
for i in $(seq 1 20); do head -c 1024 /dev/zero > "$D/docs/d$i.txt"; done

cat > "$L/check-disk-detective.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-disk.txt"
[ -f "$A" ] || { echo "FAIL: write your answers to ~/sys-lab/answers-disk.txt"; exit 1; }
ok=1
get() { grep "^$1=" "$A" | head -1 | cut -d= -f2-; }
chk() { if [ "$(get "$1")" = "$2" ]; then echo "PASS: $1"; else echo "FAIL: $1 (got '$(get "$1")')"; ok=0; fi; }
chk bigdir media
chk bigfile movie.bin
chk over100k 3
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-disk-detective.sh"
echo "Lab ready. The practice tree is ~/sys-lab/disk"
