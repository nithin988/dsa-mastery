"""Toolkit chapter 3: The log has the answer (grep, awk, sort | uniq, finding one customer in a million log lines)."""
import sd2kit as k
from sd2 import iv

# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "3:20 a.m.", "kind": "warn",
     "scene": lambda cx, cy, w: k.person(cx - 50, cy - 8, 1.1, "warn") + k.phone(cx + 40, cy, "support", "warn") + k.flow(cx + 14, cy - 4, cx - 22, cy - 4, "warn") + k.badge(cx, cy + 58, "failed 3 times", "warn"),
     "caption": "Amara in support: one customer says checkout failed three times around 3 a.m. Ten minutes."},
    {"title": "3:24 a.m.", "kind": "bad",
     "scene": lambda cx, cy, w: k.database(cx, cy - 8, "app.log", "bad") + k.badge(cx, cy + 56, "1,200,000 lines", "bad"),
     "caption": "The log has about 1.2 million lines. The editor freezes. Scrolling is hopeless."},
    {"title": "3:29 a.m.", "kind": "ok",
     "scene": lambda cx, cy, w: k.person(cx - 50, cy - 8, 1.1, "ok") + k.badge(cx + 36, cy - 14, "12 lines", "ok") + k.badge(cx + 36, cy + 16, "host db1", "ok") + k.flow(cx - 24, cy - 8, cx - 6, cy - 12, "ok"),
     "caption": "Twelve lines, one database host. A real fault, not the customer's card."},
], "ShopKart's log hunt, three moments", "Story numbers, not measurements: the point is how few lines matter out of how many exist.")

IDEA_FIG = k.figure(720, 250, [
    k.database(60, 70, "The log", "", "1.2M lines"),
    k.flow(86, 70, 150, 70, "acc", "grep"),
    k.badge(205, 70, "14,300 lines", "acc"),
    k.flow(258, 70, 330, 70, "acc", "awk"),
    k.badge(380, 70, "one column", "acc"),
    k.flow(426, 70, 500, 70, "acc", "count"),
    k.badge(560, 70, "1 answer", "ok"),
    k.note(360, 150, "grep finds lines, awk picks and adds up columns, sort and uniq count", "acc"),
    k.note(360, 180, "grep and awk read the file as a stream, so a huge log never has to fit in memory.", ""),
    k.note(360, 232, "The line counts belong to the ShopKart story, not to a measurement.", "warn"),
], "A log shrinks to one answer: filter, pick, count", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


HOW = [
    ("Filter first with grep",
     "Each log line is one event. `grep` keeps only the lines that match a word or pattern, so a million lines shrink to the few you care about. Add `-c` to count them, `-n` to see line numbers, `-v` to keep everything except a match.",
     _small([k.note(24, 24, "11:00:02 ERROR disk full (host=web2) 5ms", "bad", "start"), k.note(24, 46, "11:00:30 INFO backup started (host=db2) 20ms", "", "start"),
             k.note(24, 68, "11:15:09 WARN retrying connection (host=web1) 200ms", "", "start"), k.note(24, 90, "11:15:40 ERROR db timeout (host=db1) 3000ms", "bad", "start"),
             k.flow(400, 36, 456, 48, "bad"), k.flow(420, 90, 456, 58, "bad"), k.badge(552, 50, "grep ERROR keeps 2", "bad")], "grep keeps matching lines", h=112)),
    ("Cut lines into columns with awk",
     "`awk` splits every line into columns on spaces: `$1` is the first, `$3` the third. It can test a column, keep the matches, and do sums while it reads. That turns a log into numbers.",
     _small([k.badge(60, 34, "$1 date", ""), k.badge(150, 34, "$2 time", ""), k.badge(250, 34, "$3 level", "bad"), k.badge(370, 34, "$4 $5 message", ""), k.badge(500, 34, "$6 host", ""), k.badge(590, 34, "$7 ms", ""),
             k.note(320, 84, "awk '$3==\"ERROR\" {n++} END {print n}' counts rows where column 3 is ERROR", "acc"),
             k.note(320, 108, "On the lab log it prints 5 errors", "ok")], "awk columns", h=124)),
    ("Count with sort, uniq and sort again",
     "To count how often each value appears, sort the values so equal ones sit together, count the neighbours with `uniq -c`, then sort the counts with `sort -rn` so the biggest is first. It is the most reused three-word recipe in operations.",
     _small([k.badge(70, 34, "db1 web1 db1", ""), k.flow(124, 34, 200, 34, "acc", "sort"), k.badge(260, 34, "db1 db1 web1", ""), k.flow(314, 34, 390, 34, "acc", "uniq -c"),
             k.badge(450, 34, "2 db1, 1 web1", "ok"), k.flow(508, 34, 566, 34, "acc", "rank"),
             k.note(320, 84, "uniq only counts neighbours, so you must sort first", "warn"),
             k.note(320, 108, "The lab log, by host: 4 db1, 2 db2, 4 web1, 4 web2", "ok")], "sort, uniq -c, sort -rn", h=124)),
    ("Save the recipe as a script",
     "When you type the same pipeline twice, put it in a file. A script can take the log name as an argument, print a usage message if you forget, and end with a proper exit code so cron or CI can tell whether it worked.",
     _small([k.server(60, 56, "logsum.sh"), k.flow(92, 50, 164, 28, "warn"), k.badge(262, 26, "no argument: usage, exit 1", "warn"), k.flow(92, 56, 196, 60, "bad"), k.badge(290, 60, "no such file: exit 2", "bad"),
             k.flow(92, 64, 176, 94, "ok"), k.badge(284, 96, "good file: prints the summary", "ok"), k.note(560, 62, "scripts say how they ended", "acc")], "A small log summary script", h=130)),
]

DATA = dict(
    time="20 minutes",
    tagline="How to find one customer, one error or one slow host in a log of millions of lines, using four small tools: grep, awk, sort and uniq.",
    story=dict(
        title="3:20 a.m., one customer in a million lines",
        paras=[
            "ShopKart's server writes every event to one file, `app.log`. By 3 a.m. it holds about 1.2 million lines. At 3:20 Amara from support forwards a message: a customer says checkout failed three times \"around three o'clock\". She wants to know what happened before she replies. She has ten minutes.",
            "You open the file in an editor and it freezes. You try scrolling in `less` and give up after a minute. Nobody can read a million lines, and you do not need to. You need the dozen that mention this customer, and the pattern around them.",
            "Four tools do almost all of this work: `grep` finds lines, `awk` picks columns and adds things up, `sort` and `uniq` count. By 3:29 you know all three failures were \"db timeout\" errors on one database host, `db1`, within a few minutes of each other. Not the customer's card. A real fault, and a clue for the chapters ahead.",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: do not read the log, question it",
        one="A log is a **stream of lines**, one event per line. Instead of reading it, you **filter** it down to the lines that matter, **pick** the columns you need, and **count** what remains. Each step is one small command.",
        figure=IDEA_FIG,
        paras=["Commands on Linux read lines in and write lines out, so they join with pipes (`|`) like pieces of a pipeline. You build the answer in steps and watch the number of lines fall at each one: first the whole log, then only errors, then only one host, then a count. If a step surprises you, run the pipeline up to that step and look."]),
    how=HOW,
    try_intro=["Four experiments on a small sample log, `server.log` (14 lines). First: narrow by time. Then: count by condition with awk. Then: count by host with sort and uniq. Finally: a script that summarises the whole file."],
    **{"try": [
        ("tx", 0, 1, 0, "Narrow to one hour with grep",
         {"annot": [("2026-01-15 11:00:02 ERROR disk full", "The pattern `^2026-01-15 11:` keeps lines that start with that date and hour. The first match is a disk full error on web2."),
                    ("2026-01-15 11:15:40 ERROR db timeout (host=db1) 3000ms", "A database timeout at 11:15:40, on host db1, after waiting 3000 milliseconds.")]}),
        ("tx", 2, 0, 3, "Count rows that match with awk",
         {"annot": [("5 errors", "awk read every line, added one to `n` whenever column 3 was `ERROR`, and printed the total at the end.")]}),
        ("tx", 0, 1, 2, "Which host is in the log most? grep, sort, uniq",
         {"annot": [("4 host=db1", "Four lines mention db1. The number comes from `uniq -c` and the host from `grep -o`, which prints only the matched part of each line."),
                    ("2 host=db2", "Two lines mention db2, and the other hosts show four each. Note this counts every level, not only errors.")]}),
        ("tx", 6, 0, 1, "A reusable summary: levels and errors by host",
         {"annot": [("lines: 14", "The script counts all lines first."),
                    ("6 INFO", "Counts by level, biggest first: six INFO, five ERROR, three WARN."),
                    ("3 host=db1", "Of the five errors, three came from db1: the host to look at first.")]}),
    ]},
    breaks=[
        ("A regular expression that backtracks", "A badly written pattern can try so many ways to match that it uses all the CPU. This is a real outage cause, not a classroom worry. Fix: keep patterns simple, test them on large and odd input, and put time limits on matching.", "bad"),
        ("Counting without sorting", "`uniq -c` only counts lines that are next to each other. On unsorted input it gives several small counts for the same value and a wrong total. Fix: always `sort` before `uniq`.", ""),
        ("xargs splits on spaces", "A file called `my notes.tmp` becomes two names, `my` and `notes.tmp`, and the wrong thing gets processed or deleted. Fix: use `find -print0 | xargs -0`, which separates names with a zero byte instead.", "bad"),
        ("The pattern is too narrow or too wide", "`grep error` misses `ERROR` because matching is case sensitive, and `grep timeout` also matches unrelated lines. Fix: use `-i` for case, anchor with `^` or exact fields, and look at a few matches before trusting a count.", ""),
        ("A pipeline that hides a failure", "In `a | b`, the exit code is that of `b` only. If `a` fails, the script still looks fine: on the lab machine it printed 0 without `pipefail` and 1 with it. Fix: start scripts with `set -euo pipefail`.", "bad"),
        ("The line is in another file", "Logs rotate: yesterday's lines sit in `app.log.1` or a compressed `.gz` file. Fix: search all the rotated files (`zgrep` reads compressed ones) and mind the time zone when matching times.", ""),
    ],
    real=[
        dict(company="Cloudflare", text="Cloudflare's write-up of its 2 July 2019 outage describes a single regular expression in a firewall rule that backtracked enormously and used up the CPU that serves HTTP and HTTPS traffic. It reports that the service was down for 27 minutes.", url="https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/", source="Cloudflare blog: Details of the Cloudflare outage on July 2, 2019"),
        dict(company="The Open Group (POSIX)", text="The `grep` specification describes the basic and extended regular expressions used by `grep` and by many other tools.", url="https://pubs.opengroup.org/onlinepubs/9699919799/utilities/grep.html", source="POSIX.1-2017: grep"),
        dict(company="The Open Group (POSIX)", text="The `awk` specification defines awk as a pattern-action language: a pattern selects lines, and an action does something with them, which is exactly how the counting example above works.", url="https://pubs.opengroup.org/onlinepubs/9699919799/utilities/awk.html", source="POSIX.1-2017: awk"),
    ],
    real_title="Where this is documented",
    real_tag="Primary sources",
    real_note="A public postmortem and primary documentation. Read the linked pages for the exact wording.",
    interview=[dict(scenario=iv("tx", 0), who="A very common Linux and scripting prompt: reported by candidates, not official."),
               dict(scenario=iv("tx", 1), who="Often asked to check you know which tool to reach for: reported by candidates, not official."),
               dict(scenario=iv("tx", 2), who="A frequent question about writing safe scripts: reported by candidates, not official.")],
    interview_sub="Say your answer aloud first, then compare with the model answer. These are the shapes of question candidates report, not official lists from any company.",
    recap=dict(
        points=["A log is one event per line, so filter, pick columns, then count.",
                "`grep` keeps lines that match; `-c` counts, `-n` numbers them, `-v` inverts, `-o` prints only the match.",
                "`awk` splits lines into columns (`$1`, `$3`) and can test, keep and total them while it reads.",
                "`sort | uniq -c | sort -rn` counts values and puts the most common first; always sort before `uniq`.",
                "Build pipelines step by step and check how many lines remain after each step.",
                "Scripts should start with `set -euo pipefail` and exit with a code that says how they ended."],
        quick=[("How do you find the top five most frequent values in a column?", "`awk '{print $N}' file | sort | uniq -c | sort -rn | head -5`."),
               ("Why must you `sort` before `uniq`?", "`uniq` only collapses lines that are next to each other; sorting puts equal lines side by side."),
               ("What does `pipefail` change?", "Without it a pipeline's exit code is that of the last command only; with it, a failure in any step makes the whole pipeline fail.")]),
    deeper=[("grep and regular expressions", "S03_text_processing_scripting.html#l1"), ("sed: edit text as it flows", "S03_text_processing_scripting.html#l2"), ("awk: columns, conditions and totals", "S03_text_processing_scripting.html#l3"),
            ("awk for totals and groups", "S03_text_processing_scripting.html#l4"), ("sort, uniq, cut, tr and xargs", "S03_text_processing_scripting.html#l5"), ("Bash scripts and safety", "S03_text_processing_scripting.html#l6"),
            ("A log summary script", "S03_text_processing_scripting.html#l7")],
)
