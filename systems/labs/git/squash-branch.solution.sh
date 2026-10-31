#!/bin/bash
# Solution for the squash-branch lab (the non-interactive equivalent of squashing in git rebase -i).
cd "$HOME/sys-lab/squash"
export GIT_PAGER=cat GIT_AUTHOR_NAME="Practice Learner" GIT_AUTHOR_EMAIL="learner@example.com" GIT_COMMITTER_NAME="Practice Learner" GIT_COMMITTER_EMAIL="learner@example.com"
git switch -q feature
git reset -q --soft main
git commit -q -m "Add search feature"
git log --oneline
