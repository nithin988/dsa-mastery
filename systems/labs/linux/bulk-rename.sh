#!/bin/bash
# Lab: rename many files safely with a loop. Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
P="$L/photos"
rm -rf "$P" "$L/check-bulk-rename.sh"
mkdir -p "$P"
for n in 001 002 003 004 005; do printf 'photo\n' > "$P/IMG_$n.jpeg"; done
printf 'photo\n' > "$P/my vacation.jpeg"
printf 'keep\n' > "$P/notes.txt"

cat > "$L/check-bulk-rename.sh" <<'EOF'
#!/bin/bash
P="$HOME/sys-lab/photos"
ok=1
left=$(ls "$P" | grep -c '\.jpeg$')
[ "$left" = "0" ] && echo "PASS: no .jpeg files are left" || { echo "FAIL: $left .jpeg files are left"; ok=0; }
for n in IMG_001 IMG_002 IMG_003 IMG_004 IMG_005 "my vacation"; do
  [ -f "$P/$n.jpg" ] || { echo "FAIL: missing '$n.jpg'"; ok=0; }
done
[ $ok = 1 ] && echo "PASS: all six renamed, including the name with a space"
[ -f "$P/notes.txt" ] && echo "PASS: notes.txt untouched" || { echo "FAIL: notes.txt was changed"; ok=0; }
count=$(ls "$P" | wc -l)
[ "$count" = "7" ] && echo "PASS: no files lost or duplicated" || { echo "FAIL: expected 7 files, found $count"; ok=0; }
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-bulk-rename.sh"
echo "Lab ready. Work in ~/sys-lab/photos"
