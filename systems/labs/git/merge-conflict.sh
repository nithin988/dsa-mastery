#!/bin/bash
# Lab: resolve a real merge conflict. Only touches ~/sys-lab.
set -e
export GIT_PAGER=cat GIT_AUTHOR_NAME="Practice Learner" GIT_AUTHOR_EMAIL="learner@example.com" GIT_COMMITTER_NAME="Practice Learner" GIT_COMMITTER_EMAIL="learner@example.com"
L="$HOME/sys-lab"
R="$L/conflict"
rm -rf "$R" "$L/check-merge-conflict.sh"
mkdir -p "$R"
cd "$R"
git init -q -b main
git config user.name "Practice Learner"; git config user.email "learner@example.com"
printf 'Hello\nWelcome\n' > greeting.txt
git add greeting.txt && git commit -q -m "Add greeting"
git switch -q -c feature
printf 'Hello\nWelcome from feature\n' > greeting.txt
git commit -q -am "Feature greeting"
git switch -q main
printf 'Hello\nWelcome from main\n' > greeting.txt
git commit -q -am "Main greeting"

cat > "$L/check-merge-conflict.sh" <<'EOF'
#!/bin/bash
R="$HOME/sys-lab/conflict"
cd "$R" 2>/dev/null || { echo "FAIL: repository missing"; exit 1; }
ok=1
pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; ok=0; }
if grep -q '^<<<<<<<\|^=======\|^>>>>>>>' greeting.txt; then fail "greeting.txt still contains conflict markers"; else pass "no conflict markers left"; fi
want=$(printf 'Hello\nWelcome from main\nWelcome from feature')
[ "$(cat greeting.txt)" = "$want" ] && pass "greeting.txt has both welcome lines, main first" || fail "greeting.txt must be: Hello / Welcome from main / Welcome from feature"
[ "$(git rev-list --parents -n 1 HEAD | wc -w)" = "3" ] && pass "HEAD is a merge commit with two parents" || fail "complete the merge: HEAD must be a merge commit"
[ -z "$(git status --porcelain)" ] && pass "working tree is clean" || fail "working tree is not clean (finish with git add and git commit)"
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-merge-conflict.sh"
echo "Lab ready. In ~/sys-lab/conflict run: git merge feature"
