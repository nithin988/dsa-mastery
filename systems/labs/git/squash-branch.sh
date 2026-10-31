#!/bin/bash
# Lab: squash a messy feature branch into one clean commit. Only touches ~/sys-lab.
set -e
export GIT_PAGER=cat GIT_AUTHOR_NAME="Practice Learner" GIT_AUTHOR_EMAIL="learner@example.com" GIT_COMMITTER_NAME="Practice Learner" GIT_COMMITTER_EMAIL="learner@example.com"
export GIT_AUTHOR_DATE="2026-01-15T10:00:00+0000" GIT_COMMITTER_DATE="2026-01-15T10:00:00+0000"
L="$HOME/sys-lab"
R="$L/squash"
rm -rf "$R" "$L/check-squash-branch.sh" "$L/.squash-main"
mkdir -p "$R"
cd "$R"
git init -q -b main
git config user.name "Practice Learner"; git config user.email "learner@example.com"
printf 'def search(items, q):\n    pass\n' > search.py
git add search.py && git commit -q -m "Add search stub"
git rev-parse main > "$L/.squash-main"
git switch -q -c feature
printf 'def search(items, q):\n    return [i for i in items if q in i]\n' > search.py
git commit -q -am "wip"
printf 'def search(items, q):\n    return [i for i in items if q in i]  # case sensitive\n' > search.py
git commit -q -am "fix typo"
printf 'def search(items, q):\n    q = q.lower()\n    return [i for i in items if q in i.lower()]\n' > search.py
git commit -q -am "fix again"
printf 'def search(items, q):\n    q = q.lower()\n    return [i for i in items if q in i.lower()]\n\n# tested by hand\n' > search.py
git commit -q -am "more wip"

cat > "$L/check-squash-branch.sh" <<'EOF'
#!/bin/bash
R="$HOME/sys-lab/squash"
cd "$R" 2>/dev/null || { echo "FAIL: repository missing"; exit 1; }
ok=1
pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; ok=0; }
[ "$(git rev-parse --abbrev-ref HEAD)" = "feature" ] && pass "you are on feature" || fail "finish on the feature branch"
[ "$(git rev-list --count main..feature)" = "1" ] && pass "feature has exactly one commit on top of main" || fail "feature must have exactly 1 commit on top of main (found $(git rev-list --count main..feature))"
[ "$(git log -1 --format=%s feature)" = "Add search feature" ] && pass "the commit message is right" || fail "the commit message must be: Add search feature"
[ "$(git rev-parse main)" = "$(cat "$HOME/sys-lab/.squash-main")" ] && pass "main was not touched" || fail "main must be unchanged"
grep -q 'q.lower()' search.py && grep -q 'tested by hand' search.py && pass "the final code is kept intact" || fail "the final content of search.py must be kept"
[ -z "$(git status --porcelain)" ] && pass "working tree is clean" || fail "working tree is not clean"
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-squash-branch.sh"
echo "Lab ready. ~/sys-lab/squash has a feature branch with four messy commits."
