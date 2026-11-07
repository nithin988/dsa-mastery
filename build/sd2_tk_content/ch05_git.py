"""Chapter 5 (toolkit): Never lose work. Git basics: commits, branches, merging."""
import sd2kit as k
from sd2 import iv

# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "Friday 11:40 p.m.", "kind": "",
     "scene": lambda cx, cy, w: k.person(cx - 66, cy - 18, 1.05) + k.person(cx + 66, cy - 18, 1.05) + k.database(cx, cy + 6, "prices.csv") + k.flow(cx - 48, cy - 8, cx - 28, cy, "acc") + k.flow(cx + 48, cy - 8, cx + 28, cy, "acc"),
     "caption": "Ravi and Dana both open the one shared prices file. Ravi adds 18 promotion prices and saves."},
    {"title": "Saturday 8:05 a.m.", "kind": "bad",
     "scene": lambda cx, cy, w: k.crowd(cx, cy - 52, 4, 26, .8, "bad") + k.database(cx, cy + 26, None, "bad") + k.badge(cx, cy + 74, "18 promos gone", "bad"),
     "caption": "Dana saved a minute later from an older copy. Ravi's work vanished and nobody noticed until customers did."},
    {"title": "With Git", "kind": "ok",
     "scene": lambda cx, cy, w: k.person(cx - 66, cy - 18, 1.0, "ok") + k.person(cx + 66, cy - 18, 1.0, "ok") + k.database(cx, cy + 12, "history", "ok") + k.flow(cx - 48, cy - 8, cx - 26, cy + 4, "ok") + k.flow(cx + 48, cy - 8, cx + 26, cy + 4, "ok"),
     "caption": "Each person has their own copy and a full history. Git joins the two edits, or tells you they clash."},
], "ShopKart's prices file, three moments", "One shared file loses work; a history that records every change does not.")

IDEA_FIG = k.figure(720, 252, [
    k.person(50, 70, 1.15), k.note(50, 112, "You", ""),
    k.flow(80, 70, 160, 70, "acc", "edit"),
    k.server(200, 68, "Working folder"),
    k.flow(232, 70, 316, 70, "acc", "git add"),
    k.queue(360, 70, "Staging area", "", None, 2),
    k.flow(406, 70, 462, 70, "ok", "git commit"),
    k.database(500, 70, "Local history", "ok"),
    k.flow(530, 70, 604, 70, "acc", "git push"),
    k.cloud(650, 70, "Remote"),
    '<path class="sd-a warn dash" d="M650,116 V176 H200 V124" fill="none" marker-end="url(#dga)"/>',
    k.note(430, 196, "git pull: bring your teammates' work into your folder", "warn"),
    k.note(360, 236, "Every commit is a snapshot of the whole project, saved with a message and an author.", ""),
], "The four places your work lives in Git", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


HOW = [
    ("Save a snapshot: stage, then commit",
     "Edit files in your **working folder**. `git add` chooses what goes into the next snapshot (the **staging area**), and `git commit -m \"message\"` saves it with your name and message. Every commit is a full snapshot you can return to.",
     _small([k.server(60, 40, "edit"), k.flow(90, 40, 190, 40, "acc", "git add"), k.queue(236, 40, "staged", "", None, 2), k.flow(284, 40, 384, 40, "acc", "git commit"), k.database(430, 40, "history", "ok"), k.note(560, 44, "snapshot + message", "ok")], "Stage then commit", h=100)),
    ("Branch: a safe place to try things",
     "A **branch** is just a movable label that points at a commit, so creating one is instant and cheap. Work on `feature` while `main` stays untouched, and nobody else is disturbed.",
     _small([k.badge(60, 30, "A", "ok"), k.flow(80, 30, 150, 30, "ok"), k.badge(170, 30, "B", "ok"), k.flow(190, 30, 260, 30, "ok"), k.badge(280, 30, "C", "ok"), k.note(380, 34, "main moves on", "ok"),
             k.flow(184, 42, 232, 72, "warn"), k.badge(250, 82, "D", "warn"), k.flow(272, 82, 340, 82, "warn"), k.badge(360, 82, "E", "warn"), k.note(500, 86, "feature: a label on E", "warn")], "Two branches from commit B", h=108)),
    ("Merge: bring the work together",
     "`git merge feature` joins the branches. If `main` has not moved, Git just slides the label forward (a **fast-forward**). If both moved, Git makes a **merge commit** with two parents; if both edited the same lines, it stops and asks you to choose.",
     _small([k.badge(80, 30, "C", "ok"), k.badge(80, 78, "E", "warn"), k.flow(104, 36, 236, 52, "ok"), k.flow(104, 74, 236, 58, "warn"), k.badge(260, 54, "M", "ok"),
             k.note(420, 50, "merge commit M has two parents", "ok"), k.note(420, 78, "or fast-forward: just move the label", "")], "Merging two branches", h=108)),
    ("Share: push, fetch and pull",
     "`git push` sends your commits to the **remote** (the shared copy, such as on GitHub). `git fetch` downloads what others pushed without touching your files. `git pull` is fetch plus merge. Fetch first when you want to look before you change anything.",
     _small([k.person(40, 40, .95), k.database(110, 40, "local repo"), k.flow(140, 40, 262, 40, "acc", "push"), k.cloud(300, 40, "remote"), k.flow(450, 40, 340, 40, "ok", "push"), k.database(480, 40, "teammate"), k.person(560, 40, .95),
             k.note(300, 96, "fetch looks, pull looks and merges", "warn")], "Push, fetch and pull", h=108)),
]

DATA = dict(
    time="20 minutes",
    tagline="Git is a history of snapshots that two people can edit together without erasing each other. Learn commits, branches and merging, and why work you committed is very hard to lose.",
    story=dict(
        title="Friday night: the prices that vanished",
        paras=[
            "ShopKart keeps its prices in one file, `prices.csv`, on a shared drive. At 11:40 p.m. on a Friday, Ravi, the co-founder, adds 18 weekend promotion prices and saves. A minute later Dana opens the file she loaded earlier, fixes two typos, and saves too.",
            "Dana's save replaces the whole file with her older copy plus two fixes. Ravi's 18 promotions are gone. Nothing warns anyone. At 8:05 on Saturday morning the first customers see full prices, and by 9:00 there are nine complaints.",
            "The problem is not carelessness. A shared file has **one version**, so the last save wins. You want the opposite: every change recorded, every person working on their own copy, and a tool that joins the edits or tells you honestly when they clash. That tool is **Git**.",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: history instead of overwriting",
        one="**Git** records the project as a chain of snapshots called **commits**. Branches let people work in parallel, and merging joins their work, so a change is never silently replaced.",
        figure=IDEA_FIG,
        paras=["Each commit stores a snapshot, an author, a message, and a link to the commit before it. Because the full history lives on every person's machine and on the remote, one lost file or one bad day rarely costs more than the work you had not yet committed."]),
    how=HOW,
    try_intro=["Four experiments from a real Git repository. First, what a commit really is. Then how branches and merges look in the history, how Git tells you a teammate has pushed, and the one kind of work Git cannot give back."],
    **{"try": [
        ("gb", 0, 1, 3, "What is inside a commit?", {
            "annot": [("tree aaa96ced2d9a1c8e72c56b253a0e2fe78393feb7", "The snapshot: a tree, which is the list of files and folders as they were."),
                      ("author Ada Learner <ada@example.com> 1768492800 +0000", "Who made it and when (the number is a timestamp)."),
                      ("Add hello", "The message you wrote. There is no `parent` line because this was the very first commit.")],
            "e": "`git cat-file -p HEAD` prints the raw commit object. It is small: a pointer to the snapshot, an author, a committer and a message. Later commits add a `parent` line, and that chain of parents is the history."}),
        ("gb", 2, 1, 2, "Two branches, one merge", {
            "annot": [("*   2f90936 Merge fix", "The merge commit: it joins the two lines of work, so it has two parents."),
                      ("| * 97661d6 Add fix", "Work done on the `fix` branch."),
                      ("* | 3205427 Add main change", "Work done on `main` at the same time.")],
            "e": "This is the history after two branches were merged. The graph forks where the branches diverged and joins at the merge commit, and every commit on both sides is still there."}),
        ("gb", 3, 1, 3, "How do I know a teammate pushed?", {
            "annot": [("[behind 1]", "The remote has one commit that your branch does not have yet. `git pull` would bring it in.")],
            "e": "After `git fetch`, `git status -sb` compares your branch with the remote copy. Here the teammate has pushed one commit, so you are one behind. Fetching first lets you see this before anything changes in your folder."}),
        ("gb", 1, 1, 0, "The work Git cannot give back", {
            "annot": [("hello world", "After `git restore`, the file is back to the committed text. The `oops` line that was never committed is gone for good.")],
            "e": "The command adds a line, then throws it away with `git restore`. Git only protects what you have committed (or at least staged). Uncommitted edits that you discard are not in any history, so commit small and often."}),
    ]},
    breaks=[
        ("Uncommitted work is not safe", "Git can recover committed work almost always, but not edits you never committed. Commit in small steps, and use a branch rather than waiting for the perfect moment.", "bad"),
        ("Secrets in history", "Deleting a password file in a later commit does not remove it: `git log -S` still finds it. Treat the password as leaked and change it, then ask your team how to rewrite history.", "bad"),
        ("Push rejected", "Someone pushed before you, so your branch is behind. Fetch, then merge or rebase their commits into yours, resolve any clash, and push again. Do not reach for force.", ""),
        ("Conflicts", "Two people edited the same lines. Git marks both versions in the file with `<<<<<<<` and `>>>>>>>`; you choose the final text, `git add` it and commit.", ""),
        ("Ignoring a file that is already tracked", "Adding a file to `.gitignore` only affects files Git is not tracking yet. For one it already tracks, run `git rm --cached` first.", ""),
        ("Committing everything blindly", "`git add .` can add build output, logs or a `.env` file. Run `git status` and `git diff --staged` before every commit, and keep a `.gitignore`.", ""),
    ],
    real=[
        dict(company="Pro Git book", text="The Pro Git book describes a branch as a lightweight movable pointer to a commit, which is why creating and switching branches is quick.", url="https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell", source="Pro Git: Branches in a Nutshell"),
        dict(company="Pro Git book", text="The Git Objects chapter describes how Git stores content as objects, including the commit and tree objects you saw in the first experiment.", url="https://git-scm.com/book/en/v2/Git-Internals-Git-Objects", source="Pro Git: Git Objects"),
        dict(company="GitHub Docs", text="GitHub's guide describes what to do when a secret reaches a repository, and notes that removing it from history is not the same as making it safe again.", url="https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository", source="GitHub Docs: Removing sensitive data from a repository"),
    ],
    real_title="Where this is written down",
    real_tag="Primary docs",
    real_note="These are the official Git book and GitHub documentation. Read the source for full detail.",
    interview=[dict(scenario=iv("gb", 4), who="A common Git scenario: reported by candidates, not official."),
               dict(scenario=iv("gb", 7), who="A frequent everyday-Git question: reported by candidates, not official."),
               dict(scenario=iv("gb", 3), who="A frequent question about branches and merges: reported by candidates, not official.")],
    interview_sub="Say your answer aloud first, then compare with the model answer. These are the shapes of question candidates report, not official lists.",
    recap=dict(
        points=["A shared file keeps one version and the last save wins; Git keeps a history so changes are not erased.",
                "A commit is a snapshot with an author, a message and a link to its parent.",
                "Stage with `git add`, save with `git commit`, and check with `git status` and `git diff` first.",
                "A branch is a cheap label on a commit: work in parallel, then merge.",
                "Fetch to look, pull to fetch and merge, push to share. Never force when a push is rejected.",
                "Committed work is very hard to lose; uncommitted work and committed secrets are the real dangers."],
        quick=[("What does a fast-forward merge do?", "It moves the branch label forward because the other branch has not moved. There is no merge commit."),
               ("What is the difference between fetch and pull?", "Fetch downloads new commits without changing your files. Pull is fetch followed by a merge."),
               ("Which work can Git not recover?", "Edits you never committed or staged and then discarded. Commit small and often.")]),
    deeper=[("The snapshot model", "S05_git_fundamentals.html#l1"), ("Staging, diffs and fixing mistakes", "S05_git_fundamentals.html#l2"), ("Branches and merging", "S05_git_fundamentals.html#l3"), ("Remotes", "S05_git_fundamentals.html#l4"),
            ("Reading history", "S05_git_fundamentals.html#l5"), ("Good habits and secrets", "S05_git_fundamentals.html#l6")],
)
