#!/bin/bash
# Lab: find the first bad commit with git bisect. Only touches ~/sys-lab.
set -e
export GIT_PAGER=cat GIT_AUTHOR_NAME="Practice Learner" GIT_AUTHOR_EMAIL="learner@example.com" GIT_COMMITTER_NAME="Practice Learner" GIT_COMMITTER_EMAIL="learner@example.com"
L="$HOME/sys-lab"
R="$L/bisect"
rm -rf "$R" "$L/check-find-the-bug.sh" "$L/answers-bug.txt"
mkdir -p "$R"
cd "$R"
git init -q -b main
git config user.name "Practice Learner"; git config user.email "learner@example.com"
cat > test.sh <<'EOS'
#!/bin/bash
# exits 0 when the pricing file is healthy, 1 when it is broken
if grep -q 'rounding=B' price.txt; then echo "FAIL: wrong rounding"; exit 1; fi
echo "ok"
EOS
chmod +x test.sh
printf 'price=10\nrounding=A\n' > price.txt
git add test.sh price.txt
GIT_AUTHOR_DATE="2026-01-15T00:00:00+0000" GIT_COMMITTER_DATE="2026-01-15T00:00:00+0000" git commit -q -m "Initial pricing"
for n in $(seq 2 16); do
  p=$((10 + n))
  if [ "$n" -eq 11 ]; then
    printf 'price=%s\nrounding=B\n' "$p" > price.txt; msg="Switch pricing to new rounding"
  elif [ "$n" -gt 11 ]; then
    printf 'price=%s\nrounding=B\n' "$p" > price.txt; msg="Update price to $p"
  else
    printf 'price=%s\nrounding=A\n' "$p" > price.txt; msg="Update price to $p"
  fi
  h=$(printf '%02d' "$n")
  GIT_AUTHOR_DATE="2026-01-15T${h}:00:00+0000" GIT_COMMITTER_DATE="2026-01-15T${h}:00:00+0000" git commit -q -am "$msg"
done

cat > "$L/check-find-the-bug.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-bug.txt"
[ -f "$A" ] || { echo "FAIL: write your answer to ~/sys-lab/answers-bug.txt as first_bad=<commit message>"; exit 1; }
got=$(grep '^first_bad=' "$A" | head -1 | cut -d= -f2-)
if [ "$got" = "Switch pricing to new rounding" ]; then echo "PASS: you found the first bad commit"; echo "All tasks done."; exit 0; fi
echo "FAIL: first_bad is '$got'. Use git bisect and give the exact commit message of the FIRST commit where ./test.sh fails."; exit 1
EOF
chmod +x "$L/check-find-the-bug.sh"
echo "Lab ready. ~/sys-lab/bisect has 16 commits; ./test.sh passes at the first and fails at the last."
