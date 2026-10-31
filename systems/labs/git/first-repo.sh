#!/bin/bash
# Lab: make a clean first history. Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
rm -rf "$L/firstrepo" "$L/check-first-repo.sh"
mkdir -p "$L"
cat > "$L/SPEC-first-repo.txt" <<'EOF'
Create a repository in ~/sys-lab/firstrepo on a branch called main, with exactly three commits, oldest first:

  1. message "Add README"   containing only the new file README.md
  2. message "Add app"      containing only the new file app.py
  3. message "Ignore logs"  containing only a .gitignore that ignores *.log

Also create a file debug.log (any content). It must stay untracked and must not show up in git status.
At the end the working tree must be clean.
EOF

cat > "$L/check-first-repo.sh" <<'EOF'
#!/bin/bash
R="$HOME/sys-lab/firstrepo"
ok=1
pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; ok=0; }
[ -d "$R/.git" ] || { echo "FAIL: ~/sys-lab/firstrepo is not a git repository yet"; exit 1; }
cd "$R"
[ "$(git rev-parse --abbrev-ref HEAD 2>/dev/null)" = "main" ] && pass "on branch main" || fail "the branch must be called main"
subjects=$(git log --reverse --format=%s 2>/dev/null | tr '\n' '|')
[ "$subjects" = "Add README|Add app|Ignore logs|" ] && pass "three commits with the right messages, in order" || fail "commit messages must be, oldest first: Add README, Add app, Ignore logs (got: $subjects)"
c1=$(git log --reverse --format=%H | sed -n 1p); c2=$(git log --reverse --format=%H | sed -n 2p); c3=$(git log --reverse --format=%H | sed -n 3p)
[ "$(git show --name-only --format= "$c1" 2>/dev/null)" = "README.md" ] && pass "commit 1 contains only README.md" || fail "commit 1 must contain only README.md"
[ "$(git show --name-only --format= "$c2" 2>/dev/null)" = "app.py" ] && pass "commit 2 contains only app.py" || fail "commit 2 must contain only app.py"
[ "$(git show --name-only --format= "$c3" 2>/dev/null)" = ".gitignore" ] && pass "commit 3 contains only .gitignore" || fail "commit 3 must contain only .gitignore"
grep -qx '\*.log' .gitignore 2>/dev/null && pass ".gitignore ignores *.log" || fail ".gitignore must contain the line *.log"
[ -f debug.log ] && git check-ignore -q debug.log && pass "debug.log exists and is ignored" || fail "create debug.log and make sure it is ignored"
[ -z "$(git status --porcelain)" ] && pass "working tree is clean" || fail "working tree is not clean"
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-first-repo.sh"
echo "Lab ready. Read ~/sys-lab/SPEC-first-repo.txt"
