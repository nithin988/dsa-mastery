#!/bin/bash
# Lab: write a small, safe backup script. Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
B="$L/backup"
rm -rf "$B" "$L/check-backup-script.sh"
mkdir -p "$B"
cat > "$B/SPEC.txt" <<'EOF'
Write ~/sys-lab/backup/backup.sh with this behaviour:

  backup.sh SOURCE_DIR DEST_DIR

  1. With the wrong number of arguments: print a usage line to stderr and exit with code 1.
  2. If SOURCE_DIR does not exist: print an error to stderr and exit with code 2.
  3. Create DEST_DIR if it does not exist.
  4. Copy every *.txt file from SOURCE_DIR (not subfolders, not other file types) into DEST_DIR.
     File names may contain spaces.
  5. Print "copied N files" (N is the number copied) and exit with code 0.
  6. Start the script with a shebang and use: set -euo pipefail
EOF

cat > "$L/check-backup-script.sh" <<'EOF'
#!/bin/bash
S="$HOME/sys-lab/backup/backup.sh"
[ -f "$S" ] || { echo "FAIL: ~/sys-lab/backup/backup.sh does not exist"; exit 1; }
ok=1
pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; ok=0; }
head -1 "$S" | grep -q '^#!' && pass "has a shebang" || fail "first line must be a shebang (#!/bin/bash)"
grep -q 'set -euo pipefail' "$S" && pass "uses set -euo pipefail" || fail "use set -euo pipefail"
T=$(mktemp -d)
mkdir -p "$T/src/sub"
printf 'a\n' > "$T/src/one.txt"; printf 'b\n' > "$T/src/two.txt"; printf 'c\n' > "$T/src/my notes.txt"
printf 'd\n' > "$T/src/skip.log"; printf 'e\n' > "$T/src/sub/deep.txt"
bash "$S" >/dev/null 2>&1; [ $? -eq 1 ] && pass "no arguments exits 1" || fail "no arguments must exit 1"
bash "$S" "$T/nope" "$T/out" >/dev/null 2>&1; [ $? -eq 2 ] && pass "missing source exits 2" || fail "missing source must exit 2"
out=$(bash "$S" "$T/src" "$T/dest" 2>/dev/null); rc=$?
[ $rc -eq 0 ] && pass "normal run exits 0" || fail "normal run must exit 0 (got $rc)"
[ "$out" = "copied 3 files" ] && pass "prints: copied 3 files" || fail "must print exactly 'copied 3 files' (got '$out')"
[ -f "$T/dest/one.txt" ] && [ -f "$T/dest/two.txt" ] && [ -f "$T/dest/my notes.txt" ] && pass "copied the txt files, including the name with a space" || fail "the three txt files (one with a space in its name) must be in DEST"
[ ! -e "$T/dest/skip.log" ] && [ ! -e "$T/dest/deep.txt" ] && pass "did not copy other types or subfolders" || fail "only top-level *.txt files must be copied"
rm -rf "$T"
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-backup-script.sh"
echo "Lab ready. Read ~/sys-lab/backup/SPEC.txt, then write ~/sys-lab/backup/backup.sh"
