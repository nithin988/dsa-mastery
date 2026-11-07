"""Toolkit chapter 2: Find your way around (navigating, finding, permissions, pipes, a full disk)."""
import sd2kit as k
from sd2 import iv

# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "2:07 a.m.", "kind": "bad",
     "scene": lambda cx, cy, w: k.phone(cx - 46, cy, "pager", "bad") + k.database(cx + 44, cy - 4, "disk", "bad") + k.badge(cx + 44, cy + 56, "100% used", "bad"),
     "caption": "Checkout fails. The log says No space left on device. CPU and memory are fine."},
    {"title": "2:09 a.m.", "kind": "warn",
     "scene": lambda cx, cy, w: k.person(cx - 50, cy - 8, 1.1, "warn") + k.server(cx + 40, cy, "server", "warn") + k.flow(cx - 24, cy, cx + 8, cy, "warn") + k.badge(cx + 40, cy + 62, "$ _", "warn"),
     "caption": "You are logged in. A blinking cursor. Where are you, and where is the space going?"},
    {"title": "2:19 a.m.", "kind": "ok",
     "scene": lambda cx, cy, w: k.person(cx - 50, cy - 8, 1.1, "ok") + k.database(cx + 44, cy - 4, "disk", "ok") + k.flow(cx - 24, cy - 4, cx + 14, cy - 4, "ok") + k.badge(cx + 44, cy + 56, "62% used", "ok"),
     "caption": "One forgotten file, found in five commands, and the checkout works again."},
], "ShopKart's full disk, three moments", "The same server: nothing was wrong with the code. The disk simply filled up.")

IDEA_FIG = k.figure(720, 250, [
    k.server(80, 76, "du -a /data", "", "sizes, all files"),
    k.flow(112, 76, 236, 76, "acc", "pipe"),
    k.server(268, 76, "sort -rn", "", "biggest first"),
    k.flow(300, 76, 424, 76, "acc", "pipe"),
    k.server(456, 76, "head -3", "", "keep three"),
    k.flow(488, 76, 590, 76, "ok", "screen"),
    k.badge(640, 76, "top 3 files", "ok"),
    k.note(360, 176, "Every command has three streams: 0 input, 1 output, 2 errors. A pipe joins 1 to 0.", "acc"),
    k.note(360, 204, "Errors (stream 2) skip the pipe and go to your screen, so they never hide.", ""),
    k.note(360, 236, "Small tools, joined, beat one giant tool you have to learn.", ""),
], "A pipeline: three small commands find the biggest files", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


HOW = [
    ("Know where you are: paths",
     "Everything on Linux lives in one tree that starts at `/`. `pwd` prints where you are, `ls` shows what is here and `cd` moves. A path that starts with `/` is **absolute** (a full address); one that does not is **relative** (from here).",
     _small([k.badge(60, 40, "/", ""), k.flow(80, 40, 140, 40, "acc"), k.badge(170, 40, "home", ""), k.flow(194, 40, 250, 40, "acc"), k.badge(285, 40, "learner", ""), k.flow(320, 40, 378, 40, "acc"),
             k.badge(418, 40, "workshop", "acc"), k.note(320, 86, "pwd prints the whole address: /home/learner/workshop", "acc"),
             k.note(320, 108, "cd .. goes up one level; cd with no argument goes home", "")], "A path through the folder tree", h=122)),
    ("Find things: by name, by content",
     "`find` looks for **files** by name, size or age. `grep` looks for **lines** inside files. Use find when you know what the file is called, and grep when you only remember something it says.",
     _small([k.badge(80, 34, "find", "acc"), k.flow(112, 34, 220, 34, "acc"), k.note(420, 38, "files by name, size or age: ./logs/app.log", "acc"),
             k.badge(80, 80, "grep", "warn"), k.flow(112, 80, 220, 80, "warn"), k.note(420, 84, "lines by content: ERROR disk almost full", "warn")], "find and grep", h=112)),
    ("Join commands with pipes and redirects",
     "Output normally goes to your screen. `>` sends it to a file instead, `2>` sends only the errors, and `|` feeds one command's output into the next. Careful: `sort f > f` empties `f` first, because the shell opens (and wipes) the file before `sort` reads it.",
     _small([k.server(60, 46, "command"), k.flow(92, 30, 230, 30, "ok"), k.badge(310, 30, "screen or > file", "ok"), k.flow(92, 62, 230, 62, "bad"), k.badge(314, 62, "screen or 2> file", "bad"),
             k.note(540, 34, "stdout: results", "ok"), k.note(540, 66, "stderr: problems", "bad"),
             k.note(320, 112, "sort -r f > f leaves f at 0 bytes: the shell empties it first", "warn")], "Streams, redirects and pipes", h=128)),
    ("Permissions: who may do what",
     "`ls -l` shows ten characters such as `-rwxr-xr-x`. After the type come three triples: the **owner**, the **group** and **everyone else**, each with read (r), write (w) and execute (x). `chmod` changes them, and `Permission denied` means your triple lacks a letter.",
     _small([k.badge(110, 34, "owner: rwx", "ok"), k.badge(300, 34, "group: r-x", "warn"), k.badge(490, 34, "others: r-x", "warn"),
             k.note(320, 80, "chmod 755 = 7 (rwx), 5 (r-x), 5 (r-x). 4 is read, 2 is write, 1 is run", "acc"),
             k.note(320, 104, "Permission denied means your triple lacks the letter, not that the file is gone", "")], "Permission triples", h=122)),
]

DATA = dict(
    time="20 minutes",
    tagline="Get around a Linux server with confidence: where am I, what is here, which file is huge, who may touch it, and how to join small commands into a real answer.",
    story=dict(
        title="2:07 a.m., No space left on device",
        paras=[
            "Your pager goes off at 2:07 a.m. Checkout is failing. Customers press Pay, wait, and get an error. The log shows one line, again and again: `No space left on device`. Memory is fine and the CPU is nearly idle. The server simply cannot write one more byte.",
            "You log in over SSH and see a black screen and a blinking cursor. Where are you? What is on this machine? Which of the thousand folders is the problem? Dev, awake in another time zone, types \"just delete the logs\" in chat. You are not sure which logs, or whether you are allowed to.",
            "This chapter is the map you needed. You ask where you are, look around, find the biggest thing, check who owns it and join small commands with pipes. By 2:19 you know which single file filled the disk, and, more importantly, why deleting it the obvious way would not have helped.",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: small tools, joined together",
        one="The **shell** is a program that reads what you type and starts other programs for you. Linux gives you many small tools that each do one job, and **pipes** join them: the output of one becomes the input of the next.",
        figure=IDEA_FIG,
        paras=["You do not need to memorise hundreds of commands. About fifteen cover most work: `pwd`, `ls`, `cd`, `cat`, `head`, `tail`, `find`, `grep`, `sort`, `du`, `chmod`, and the symbols `|`, `>` and `2>`. The skill is combining them, and asking the system for help with `--help` or `man` when you forget a flag."]),
    how=HOW,
    try_intro=["Four experiments. First: look around a folder tree. Then: find what is eating the space. Then: the twist that fools many engineers, a deleted file that still fills the disk. Finally: what Permission denied looks like."],
    **{"try": [
        ("sh", 0, 1, 13, "Look at a whole folder tree at once",
         {"annot": [("workshop/logs:", "Each folder is listed under its own name followed by a colon."),
                    ("access.log", "A log file inside `logs`. The `-R` option means recursive: go into every folder below."),
                    ("README.txt", "A file sitting directly in `workshop`, listed before the folders it contains.")]}),
        ("pb", 1, 0, 2, "Which file is eating the disk? du, sort and head",
         {"annot": [("15428\tdisk", "The whole folder `disk`, in 1 KB blocks: about 15 MB."),
                    ("15360\tdisk/big", "One file, `big`, accounts for almost all of it (15360 KB is 15 MB)."),
                    ("0\tdisk/f999", "One of thousands of empty files in that folder. Many files can still add up to nothing in size.")]}),
        ("dt", 1, 0, 2, "The twist: a deleted file that still takes space",
         {"annot": [("(deleted)", "The file name is gone from the folder, but a running process still holds the file open, so the kernel keeps it and its space."),
                    ("bash 4w 0", "`lsof +L1` finds it: the command (bash), descriptor 4 opened for writing (`w`), and a link count of 0, meaning no name left.")]}),
        ("sh", 4, 1, 1, "Permission denied: the missing x",
         {"annot": [("Permission denied", "The file exists, but after `chmod -x` nobody has the execute permission, so the kernel refuses to run it. `chmod 755` would give it back.")]}),
    ]},
    breaks=[
        ("Running rm without looking", "`rm` has no recycle bin, and a typo or a space in the wrong place deletes the wrong thing. Fix: run `ls` or `find ... -print` with the same pattern first, then change the command to delete.", "bad"),
        ("Deleting a file a program still holds", "You remove a big log, but the program writing to it still has it open, so `df` shows no space freed. Fix: restart the program, or empty the file in place instead of deleting it. `lsof +L1` shows these deleted-but-open files.", "bad"),
        ("Full of files, not bytes", "A disk can run out of **inodes** (the records that track each file) while bytes remain, for instance with millions of tiny files. Fix: check `df -i` as well as `df -h`, and clean up the folder that holds the swarm.", ""),
        ("chmod 777 to make it work", "Giving everyone every permission hides the real problem and lets any user change or run the file. Fix: find which user needs which letter and grant exactly that.", "bad"),
        ("Redirecting onto your input", "`sort file > file` or `command > file` where the command reads that same file leaves it empty, because the shell wipes it first. Fix: write to a new file, then move it into place.", ""),
        ("Wrong directory", "A relative path works from wherever you are, so the same command can touch a different folder than you think. Fix: run `pwd` before anything destructive, and prefer absolute paths in scripts.", ""),
    ],
    real=[
        dict(company="The Open Group (POSIX)", text="The shell command language standard describes pipelines, redirection and exit status. It is the common ground that `sh`-style shells follow, which is why these habits carry from one Linux or Unix machine to another.", url="https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html", source="POSIX.1-2017: Shell Command Language"),
        dict(company="Linux man-pages", text="The `unlink` page describes what happens when you delete the last name of a file that a process still has open: the file stays in existence until the last descriptor is closed. This is why deleting a log can leave the disk full.", url="https://man7.org/linux/man-pages/man2/unlink.2.html", source="Linux man-pages: unlink(2)"),
        dict(company="The Open Group (POSIX)", text="The `chmod` specification describes the symbolic form (such as `u+x,g-w`) and the octal form (such as `755`) for changing permissions.", url="https://pubs.opengroup.org/onlinepubs/9699919799/utilities/chmod.html", source="POSIX.1-2017: chmod"),
    ],
    real_title="Where this is documented",
    real_tag="Primary sources",
    real_note="Primary documentation. Read the linked page for the exact wording.",
    interview=[dict(scenario=iv("sh", 3), who="A classic operations question: reported by candidates, not official."),
               dict(scenario=iv("sh", 5), who="A common Linux basics question: reported by candidates, not official."),
               dict(scenario=iv("sh", 2), who="A favourite 'gotcha' about redirection: reported by candidates, not official.")],
    interview_sub="Say your answer aloud first, then compare with the model answer. These are the shapes of question candidates report, not official lists from any company.",
    recap=dict(
        points=["`pwd`, `ls` and `cd` answer where you are and what is here; absolute paths start with `/`.",
                "`find` locates files by name, size or age, and `grep` locates lines by content.",
                "A pipe joins one command's output to the next one's input, and `>` and `2>` send output and errors to files.",
                "`du -a | sort -rn | head` is the standard way to find what fills a disk.",
                "`Permission denied` means your owner, group or other triple lacks r, w or x.",
                "A deleted file that a process still holds open keeps its space until that process lets go."],
        quick=[("How do you find the biggest files under a folder?", "`du -a folder | sort -rn | head`: list sizes, put the biggest first, keep the top few."),
               ("What does `chmod 755 file` mean?", "Owner can read, write and run (7); group and others can read and run (5)."),
               ("You deleted a huge log but `df` still shows 100%. Why?", "A process still has the file open, so the kernel keeps its space. Restart the process or truncate the file in place; `lsof +L1` shows it.")]),
    deeper=[("Where am I? Paths", "S02_linux_shell.html#l1"), ("Reading, creating and removing files", "S02_linux_shell.html#l2"), ("Finding things", "S02_linux_shell.html#l3"), ("Pipes and redirection", "S02_linux_shell.html#l4"),
            ("Permissions and users", "S02_linux_shell.html#l5"), ("Variables, exit codes and jobs", "S02_linux_shell.html#l6"), ("Files, inodes and links", "S04_linux_internals.html#l4"),
            ("Playbook: No space left on device", "S12_troubleshooting_playbooks.html#l2")],
)
