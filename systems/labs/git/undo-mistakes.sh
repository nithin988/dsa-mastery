#!/bin/bash
# Lab: undo three common mistakes without losing the right things. Only touches ~/sys-lab.
set -e
export GIT_PAGER=cat GIT_AUTHOR_NAME="Practice Learner" GIT_AUTHOR_EMAIL="learner@example.com" GIT_COMMITTER_NAME="Practice Learner" GIT_COMMITTER_EMAIL="learner@example.com"
export GIT_AUTHOR_DATE="2026-01-15T10:00:00+0000" GIT_COMMITTER_DATE="2026-01-15T10:00:00+0000"
L="$HOME/sys-lab"
R="$L/undo"
rm -rf "$R" "$L/check-undo-mistakes.sh"
mkdir -p "$R"
cd "$R"
git init -q -b main
git config user.name "Practice Learner"; git config user.email "learner@example.com"
printf 'print("app v1")\n' > app.py
git add app.py && git commit -q -m "Add app"
printf 'Buy milk\n' > notes.txt
git add notes.txt && git commit -q -m "Add notse"
git rev-parse HEAD~1 > "$L/.undo-first"
printf 'print("BROKEN")\n' >> app.py
printf 'API_KEY=do-not-commit\n' > secret.env
git add secret.env

cat > "$L/check-undo-mistakes.sh" <<'EOF'
#!/bin/bash
R="$HOME/sys-lab/undo"
cd "$R" 2>/dev/null || { echo "FAIL: repository missing"; exit 1; }
ok=1
pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; ok=0; }
[ "$(cat app.py)" = 'print("app v1")' ] && pass "the broken edit to app.py is discarded" || fail "app.py must be back to the committed version"
[ -f secret.env ] && pass "secret.env still exists in the folder" || fail "secret.env must not be deleted, only unstaged"
if git ls-files --error-unmatch secret.env >/dev/null 2>&1; then fail "secret.env must not be tracked or staged"; else pass "secret.env is not tracked or staged"; fi
if git show --name-only --format= HEAD | grep -q secret.env; then fail "secret.env was committed: that is the trap"; else pass "secret.env is not in the last commit"; fi
[ "$(git log -1 --format=%s)" = "Add notes" ] && pass "the last commit message is fixed" || fail "the last commit message must be: Add notes"
[ "$(git rev-list --count HEAD)" = "2" ] && pass "still exactly two commits (amended, not added)" || fail "there must still be exactly 2 commits"
[ "$(git rev-parse HEAD~1)" = "$(cat "$HOME/sys-lab/.undo-first")" ] && pass "the first commit is untouched" || fail "the first commit must be unchanged"
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-undo-mistakes.sh"
echo "Lab ready. Run git status in ~/sys-lab/undo and fix three things."
