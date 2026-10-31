#!/bin/bash
# Solution for the undo-mistakes lab (order matters: unstage secret.env BEFORE amending).
cd "$HOME/sys-lab/undo"
export GIT_PAGER=cat
git restore --staged secret.env
git restore app.py
git commit -q --amend -m "Add notes"
git status --short
git log --oneline
