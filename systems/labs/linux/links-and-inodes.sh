#!/bin/bash
# Lab: hard links, symbolic links and what survives a delete. Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
P="$L/links"
rm -rf "$P" "$L/check-links-and-inodes.sh" "$L/.links-inode"
mkdir -p "$P"
printf 'Q4 numbers\n' > "$P/report.txt"
stat -c %i "$P/report.txt" > "$L/.links-inode"

cat > "$L/check-links-and-inodes.sh" <<'EOF'
#!/bin/bash
P="$HOME/sys-lab/links"
ok=1
want=$(cat "$HOME/sys-lab/.links-inode")
if [ -f "$P/backup.txt" ] && [ "$(stat -c %i "$P/backup.txt")" = "$want" ]; then echo "PASS: backup.txt is a hard link to the original data"; else echo "FAIL: backup.txt must be a HARD link to the original report (same inode)"; ok=0; fi
if [ -L "$P/latest.txt" ] && [ "$(readlink "$P/latest.txt")" = "report.txt" ]; then echo "PASS: latest.txt is a symbolic link to report.txt"; else echo "FAIL: latest.txt must be a SYMBOLIC link to the name report.txt"; ok=0; fi
if [ ! -e "$P/report.txt" ]; then echo "PASS: report.txt (the first name) is deleted"; else echo "FAIL: delete the name report.txt"; ok=0; fi
if [ "$(cat "$P/backup.txt" 2>/dev/null)" = "Q4 numbers" ]; then echo "PASS: the data survived through the hard link"; else echo "FAIL: the data is not readable through backup.txt"; ok=0; fi
if [ -L "$P/latest.txt" ] && [ ! -e "$P/latest.txt" ]; then echo "PASS: latest.txt is now dangling, as expected"; else echo "FAIL: latest.txt should now point to a missing file"; ok=0; fi
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-links-and-inodes.sh"
echo "Lab ready. Work in ~/sys-lab/links"
