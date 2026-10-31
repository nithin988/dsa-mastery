#!/bin/bash
# Solution for the find-the-bug lab.
cd "$HOME/sys-lab/bisect"
export GIT_PAGER=cat
git bisect start >/dev/null
git bisect bad >/dev/null
git bisect good "$(git rev-list --max-parents=0 HEAD)" >/dev/null
git bisect run ./test.sh >/dev/null
subject=$(git log -1 --format=%s refs/bisect/bad)
git bisect reset >/dev/null 2>&1
printf 'first_bad=%s\n' "$subject" > "$HOME/sys-lab/answers-bug.txt"
cat "$HOME/sys-lab/answers-bug.txt"
