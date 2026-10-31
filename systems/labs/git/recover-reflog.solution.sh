#!/bin/bash
# Solution for the recover-reflog lab.
cd "$HOME/sys-lab/lostwork"
export GIT_PAGER=cat
git reflog | head -n 4
git reset -q --hard "HEAD@{1}"
git log --oneline
