"""Chapter 6 (toolkit): When the team grows and things go wrong. Reflog, revert versus reset, bisect."""
import sd2kit as k
from sd2 import iv

# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "Friday 4:50 p.m.", "kind": "",
     "scene": lambda cx, cy, w: k.person(cx - 60, cy - 10, 1.1) + k.server(cx + 36, cy - 6, "release", "ok") + k.flow(cx - 34, cy - 6, cx + 4, cy - 6, "ok") + k.badge(cx, cy + 62, "Dana ships", "ok"),
     "caption": "Dana deploys the week's work. It looks routine and everyone starts to leave."},
    {"title": "5:20 p.m.", "kind": "bad",
     "scene": lambda cx, cy, w: k.phone(cx - 44, cy - 4, "pager", "bad") + k.alert(cx + 40, cy - 8, None) + k.badge(cx, cy + 70, "totals off by a cent", "bad"),
     "caption": "Customers are charged the wrong total. Ravi tries a quick fix and two good commits disappear."},
    {"title": "Monday 9 a.m.", "kind": "ok",
     "scene": lambda cx, cy, w: k.person(cx - 62, cy - 6, 1.1, "ok") + k.database(cx + 30, cy - 4, "history", "ok") + k.flow(cx - 38, cy - 6, cx + 2, cy - 4, "ok") + k.badge(cx, cy + 62, "found in 4 tests", "ok"),
     "caption": "The bad commit was found by bisect and reverted. The lost work came back from the reflog."},
], "ShopKart's pricing release, one weekend", "A bad release, a panicked fix, and a calm recovery.")

IDEA_FIG = k.figure(720, 260, [
    k.cloud(120, 52, None, "warn"), k._lbl(120, 94, "Already shared", None),
    k.person(360, 52, 1.25), k._lbl(360, 96, "Only on my machine", None),
    k.clock(600, 48, None), k._lbl(600, 90, "Lost something?", None),
    k.note(120, 128, "git revert <commit>", "ok"), k.note(120, 150, "adds a new commit", ""), k.note(120, 172, "history stays intact", "ok"),
    k.note(360, 128, "git reset", "warn"), k.note(360, 150, "moves the branch back", ""), k.note(360, 172, "soft, mixed or hard", "warn"),
    k.note(600, 128, "git reflog", "acc"), k.note(600, 150, "find where HEAD was", ""), k.note(600, 172, "git reset --hard HEAD@{1}", "acc"),
    k.badge(360, 214, "Shared history: add a commit. Private history: you may rewrite it.", "ok"),
], "Which undo to reach for", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


HOW = [
    ("Stop the bleeding: revert, do not rewrite",
     "`git revert <commit>` makes a **new commit that undoes** an old one. History keeps both, so everyone who already pulled the bad commit stays in step. It is the safe first move once something is shared.",
     _small([k.badge(60, 40, "A", "ok"), k.flow(82, 40, 144, 40, "ok"), k.badge(180, 40, "B bad", "bad"), k.flow(216, 40, 298, 40, "ok"), k.badge(320, 40, "C", "ok"), k.flow(342, 40, 400, 40, "ok"), k.badge(440, 40, "revert B", "ok"), k.note(570, 44, "history kept", "ok")], "Revert adds a commit", h=84)),
    ("Find the guilty commit: bisect",
     "`git bisect` does a **binary search** through history. You mark one commit good and one bad, and Git checks out the middle for you to test. Each answer halves the candidates, so sixteen commits need only about four tests, and a test script can run them all.",
     _small([k.badge(60, 40, "1 good", "ok"), k.flow(112, 40, 258, 40, "acc"), k.badge(320, 40, "test the middle", "warn"), k.flow(530, 40, 384, 40, "acc"), k.badge(580, 40, "16 bad", "bad"), k.note(320, 84, "16, 8, 4, 2, 1 candidates left", "ok")], "Bisect halves the candidates", h=100)),
    ("Undo on your own machine: reset has three strengths",
     "`git reset` moves your branch back. `--soft` keeps your changes staged, `--mixed` keeps them in your files, and `--hard` throws them away. Use reset only on commits you have **not** shared, because it rewrites history.",
     _small([k.badge(100, 34, "--soft: keep staged", "ok"), k.badge(320, 34, "--mixed: keep files", "warn"), k.badge(540, 34, "--hard: lose changes", "bad"), k.note(100, 78, "commit undone, work staged", "ok"), k.note(320, 78, "work back in the folder", "warn"), k.note(540, 78, "work gone from folder", "bad")], "Soft, mixed and hard reset", h=100)),
    ("Get lost work back: the reflog",
     "The **reflog** is your local diary of every place `HEAD` has been, even after a `reset --hard` or a deleted branch. Find the commit you want, then point your branch back at it. It only lives on your machine, and old entries expire.",
     _small([k.clock(50, 38, "diary"), k.badge(200, 28, "HEAD@{0}: reset", "bad"), k.badge(200, 62, "HEAD@{1}: commit", "ok"), k.flow(270, 62, 382, 62, "ok", "go back"), k.badge(480, 62, "reset --hard HEAD@{1}", "ok")], "The reflog as a diary", h=100)),
]

DATA = dict(
    time="25 minutes",
    tagline="When a bad commit reaches production you need three skills: undo it safely, find which commit caused it, and recover work you thought you had lost.",
    story=dict(
        title="Friday afternoon: the bad commit",
        paras=[
            "At 4:50 on Friday, Dana deploys the week's work. At 5:20 the pager goes off: some customers are charged totals a cent too high. ShopKart's pricing repository has sixteen commits since launch, and one of them changed how prices are rounded. Nobody knows which.",
            "Ravi, who is not a Git person, wants it gone now. He runs `git reset --hard` three commits back and force-pushes. The bad change disappears, but so do two good commits that Mei pushed that morning. Mei's laptop is on a train home, and nobody can tell what was lost.",
            "A calm team does three things in order. **Revert** the bad change safely, **bisect** to find the guilty commit in a few tests, and use the **reflog** to bring back the commits that were lost. Each is one command, and this chapter shows all three.",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: shared history is added to, private history can be rewritten",
        one="Once commits are **shared**, undo by **adding** a commit (`revert`). While commits are **private**, you may move the branch (`reset`). If you lose work either way, the **reflog** remembers.",
        figure=IDEA_FIG,
        paras=["Almost every Git disaster is the wrong undo for the situation: rewriting history that others already have, or deleting work that was never committed. Choose by one question: has anyone else seen these commits?"]),
    how=HOW,
    try_intro=["Four experiments from real repositories. A revert that keeps history, the reflog that remembers a `reset --hard`, the recovery from it, and bisect finding the bad commit among sixteen."],
    **{"try": [
        ("gr", 2, 1, 0, "Undo a commit without rewriting history", {
            "annot": [("Revert \"v2 once more\"", "The new commit that undoes the old one. Its message names what it reverted."),
                      ("d0378b7 v2 once more", "The original commit is still in the history. Nothing was erased, so teammates who pulled it stay in step."),
                      ("v1", "The file contents are back to the earlier value.")],
            "e": "The log shows three commits: the first version, the change, and the revert on top. The file is back to `v1`, but the history tells the whole truth. This is what you want on a shared branch."}),
        ("gr", 3, 0, 2, "What does the reflog remember?", {
            "annot": [("0228e1f HEAD@{0}: reset: moving to HEAD~2", "The most recent move: the `reset --hard` that dropped two commits."),
                      ("19e18a1 HEAD@{1}: commit: Add export", "Where HEAD was one step ago, before the reset. The lost commit is still here."),
                      ("ac69ac0 HEAD@{4}: commit (initial): Init project", "The first entry: the diary goes all the way back.")],
            "e": "A `git reset --hard HEAD~2` has just removed two commits from the log. `git reflog` shows the diary of where HEAD has been, and the commit that looks lost is still listed with its hash."}),
        ("gr", 3, 0, 3, "Bring the lost commits back", {
            "annot": [("19e18a1 Add export", "The commit that looked lost is the tip of the branch again."),
                      ("07101c7 Add search", "The commit before it came back with it, because the history chains through parents.")],
            "e": "One command, `git reset --hard HEAD@{1}`, points the branch at where it was before the mistake. All four commits are back. This is the cure for the Friday reset, as long as the work had been committed."}),
        ("gr", 4, 1, 1, "Find the bad commit with bisect", {
            "annot": [("running './test.sh'", "Git runs your test on the commit it checked out, and the pass or fail decides which half to try next."),
                      ("FAIL: wrong rounding", "A failing test marks that commit as bad."),
                      ("ae3de3f04ada2707d934b30f863380c90eb85998 is the first bad commit", "The answer: found after four test runs among sixteen commits."),
                      ("Switch pricing to new rounding", "The commit message points at the cause.")],
            "e": "The script exits 1 when the price rounding is wrong and 0 when it is right. `git bisect run` tests the middle commit, then the middle of the remaining half, and so on until one commit is left. Four tests found the cause in a history of sixteen."}),
    ]},
    breaks=[
        ("Reset or force-push on shared history", "You remove a bad commit locally and force-push, and teammates' commits disappear or their branches break. Fix: use `git revert` on shared branches, and force-push only your own branch, with `--force-with-lease`.", "bad"),
        ("`reset --hard` with uncommitted work", "Commits can be rescued from the reflog, but edits that were never committed or staged cannot. Fix: commit or `git stash` before any hard reset.", "bad"),
        ("The reflog is local and it expires", "It lives only in your clone, so it cannot rescue work from a teammate's laptop. Old entries are removed by garbage collection after a configurable time. Fix: recover quickly, and push work to a branch.", ""),
        ("Bisect with a flaky test", "If the test passes sometimes and fails sometimes, bisect points at the wrong commit. Fix: make the test deterministic first, or run it several times per step.", ""),
        ("Reverting a merge commit", "A merge has two parents, so Git needs to know which side to keep (`git revert -m 1 <merge>`). Reverting a merge also makes it harder to re-merge that branch later. Fix: read the docs before you do it.", ""),
        ("Conflicts during revert or rebase", "An undo can clash with later changes to the same lines. Fix: resolve the conflict like any merge, `git add`, and continue, or `--abort` to start again.", ""),
    ],
    real=[
        dict(company="Git documentation", text="The git-bisect page describes finding the commit that introduced a bug by binary search, and `git bisect run` to automate the test.", url="https://git-scm.com/docs/git-bisect", source="git-bisect documentation"),
        dict(company="Git documentation", text="The git-revert page describes creating new commits that undo the changes of earlier commits, rather than rewriting history.", url="https://git-scm.com/docs/git-revert", source="git-revert documentation"),
        dict(company="Pro Git book", text="The data recovery section describes using the reflog to find commits that are no longer on any branch.", url="https://git-scm.com/book/en/v2/Git-Internals-Maintenance-and-Data-Recovery", source="Pro Git: Maintenance and Data Recovery"),
    ],
    real_title="Where this is written down",
    real_tag="Primary docs",
    real_note="These are the official Git documentation pages. Read the source for exact behaviour and options.",
    interview=[dict(scenario=iv("gr", 2), who="A very common Git recovery question: reported by candidates, not official."),
               dict(scenario=iv("gr", 3), who="A frequent debugging question: reported by candidates, not official."),
               dict(scenario=iv("gr", 1), who="A frequent question comparing undo commands: reported by candidates, not official.")],
    interview_sub="Say your answer aloud first, then compare with the model answer. These are the shapes of question candidates report, not official lists.",
    recap=dict(
        points=["On a shared branch, undo with `git revert`: it adds a commit and keeps history.",
                "`git reset` rewrites your private history: soft keeps changes staged, mixed keeps files, hard throws changes away.",
                "`git bisect` finds the first bad commit by binary search; a test script makes it automatic.",
                "The reflog is a local diary of where HEAD has been: `git reset --hard HEAD@{1}` goes back one move.",
                "Committed work is recoverable; uncommitted work lost to `reset --hard` is not.",
                "Before any history rewrite ask: has anyone else seen these commits?"],
        quick=[("Revert or reset for a bad commit that is already on main?", "Revert. It adds a new commit that undoes the change without rewriting shared history."),
               ("How many tests does bisect need for 200 commits?", "About eight, because each test halves the candidates (200, 100, 50, 25, 13, 7, 4, 2, 1)."),
               ("You ran `git reset --hard HEAD~3` by mistake. What now?", "Run `git reflog`, find the commit from before the reset, and `git reset --hard` to it. This works only for committed work.")]),
    deeper=[("Merge, rebase and cherry-pick", "S06_git_teams_recovery.html#l1"), ("Fixup and interactive rebase", "S06_git_teams_recovery.html#l2"), ("Restore, reset and revert", "S06_git_teams_recovery.html#l3"), ("The reflog", "S06_git_teams_recovery.html#l4"),
            ("Bisect", "S06_git_teams_recovery.html#l5"), ("Stash, tags, worktrees", "S06_git_teams_recovery.html#l6"), ("Conflicts and workflows", "S06_git_teams_recovery.html#l7")],
)
