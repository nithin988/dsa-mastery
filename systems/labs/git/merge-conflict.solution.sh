#!/bin/bash
# Solution for the merge-conflict lab.
cd "$HOME/sys-lab/conflict"
export GIT_PAGER=cat GIT_EDITOR=true
git merge feature || true
printf 'Hello\nWelcome from main\nWelcome from feature\n' > greeting.txt
git add greeting.txt
git commit -q --no-edit
git log --oneline --graph
