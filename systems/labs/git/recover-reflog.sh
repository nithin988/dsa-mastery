#!/bin/bash
# Lab: recover commits lost to a hard reset. Only touches ~/sys-lab.
set -e
export GIT_PAGER=cat GIT_AUTHOR_NAME="Practice Learner" GIT_AUTHOR_EMAIL="learner@example.com" GIT_COMMITTER_NAME="Practice Learner" GIT_COMMITTER_EMAIL="learner@example.com"
L="$HOME/sys-lab"
R="$L/lostwork"
rm -rf "$R" "$L/check-recover-reflog.sh" "$L/.lost-tip"
mkdir -p "$R"
cd "$R"
git init -q -b main
git config user.name "Practice Learner"; git config user.email "learner@example.com"
i=0
for msg in "Init project" "Add login" "Add search" "Add export"; do
  i=$((i + 1))
  echo "$msg" >> history.txt
  git add history.txt
  GIT_AUTHOR_DATE="2026-01-15T1$i:00:00+0000" GIT_COMMITTER_DATE="2026-01-15T1$i:00:00+0000" git commit -q -m "$msg"
done
git rev-parse HEAD > "$L/.lost-tip"
git reset -q --hard HEAD~2

cat > "$L/check-recover-reflog.sh" <<'EOF'
#!/bin/bash
R="$HOME/sys-lab/lostwork"
cd "$R" 2>/dev/null || { echo "FAIL: repository missing"; exit 1; }
ok=1
pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; ok=0; }
[ "$(git rev-parse HEAD)" = "$(cat "$HOME/sys-lab/.lost-tip")" ] && pass "main points at the original tip again" || fail "main must point at the commit 'Add export' that was lost"
[ "$(git rev-list --count HEAD)" = "4" ] && pass "all four commits are back" || fail "the history should have 4 commits"
[ "$(git rev-parse --abbrev-ref HEAD)" = "main" ] && pass "you are on main" || fail "restore the work on the branch main"
[ -z "$(git status --porcelain)" ] && pass "working tree is clean" || fail "working tree is not clean"
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-recover-reflog.sh"
echo "Lab ready. Someone ran a hard reset on ~/sys-lab/lostwork and two commits vanished from git log."
