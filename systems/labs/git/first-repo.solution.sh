#!/bin/bash
# Solution for the first-repo lab.
set -e
export GIT_PAGER=cat
cd "$HOME/sys-lab"
git init -q -b main firstrepo
cd firstrepo
git config user.name "Practice Learner"; git config user.email "learner@example.com"
echo "# My project" > README.md
git add README.md && git commit -q -m "Add README"
echo 'print("hello")' > app.py
git add app.py && git commit -q -m "Add app"
echo "*.log" > .gitignore
echo "debug output" > debug.log
git add .gitignore && git commit -q -m "Ignore logs"
git log --oneline
git status --short
