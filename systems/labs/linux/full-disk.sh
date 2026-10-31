#!/bin/bash
# Lab: "No space left on device" triage: biggest file, and the directory that eats inodes. Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
rm -rf "$L/fd" "$L/check-full-disk.sh" "$L/answers-disk.txt"
mkdir -p "$L/fd/var/log/app" "$L/fd/var/cache/thumbs" "$L/fd/var/lib/db" "$L/fd/tmp/sessions" "$L/fd/home/alice/videos"
dd if=/dev/zero of="$L/fd/var/log/app/debug.log" bs=1M count=24 status=none
dd if=/dev/zero of="$L/fd/var/lib/db/data.bin" bs=1M count=11 status=none
dd if=/dev/zero of="$L/fd/home/alice/videos/holiday.mp4" bs=1M count=19 status=none
for i in $(seq 1 1800); do : > "$L/fd/var/cache/thumbs/t$i.jpg"; done
for i in $(seq 1 120);  do : > "$L/fd/tmp/sessions/s$i"; done

cat > "$L/check-full-disk.sh" <<'EOF'
#!/bin/bash
L="$HOME/sys-lab"
A="$L/answers-disk.txt"
ok=1
get() { [ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2-; }
[ "$(get biggest_file)" = "$L/fd/var/log/app/debug.log" ] && echo "PASS: biggest_file" || { echo "FAIL: biggest_file= should be the full path of the largest file under ~/sys-lab/fd"; ok=0; }
[ "$(get most_files_dir)" = "$L/fd/var/cache/thumbs" ] && echo "PASS: most_files_dir" || { echo "FAIL: most_files_dir= should be the full path of the directory containing the most files (the inode eater)"; ok=0; }
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-full-disk.sh"
echo "Lab ready. Explore ~/sys-lab/fd as if it were a full server disk."
