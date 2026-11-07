"""Chapter 10: The server is slow (performance triage and the USE method)."""
import sd2kit as k
from sd2 import iv

# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "02:07, everything is slow", "kind": "bad",
     "scene": lambda cx, cy, w: k.phone(cx - 56, cy, "pager", "bad") + k.server(cx + 46, cy, "web", "warn") + k.badge(cx + 46, cy + 62, "9 s pages", "bad"),
     "caption": "The pager says checkout takes nine seconds. The dashboard says every server is up."},
    {"title": "Four suspects", "kind": "warn",
     "scene": lambda cx, cy, w: k.gauge(cx - 52, cy, 90, "CPU", "bad") + k.gauge(cx + 52, cy, 30, "memory", "ok"),
     "caption": "CPU, memory, disk or network. You do not guess: you ask the same three questions of each."},
    {"title": "02:31, found", "kind": "ok",
     "scene": lambda cx, cy, w: k.person(cx - 52, cy - 6, 1.1, "ok") + k.server(cx + 46, cy, "web", "ok") + k.flow(cx - 26, cy - 6, cx + 12, cy - 2, "ok"),
     "caption": "A night job was hogging every core. You stop it, watch the numbers fall, and write it down."},
], "ShopKart's slow night, three moments", "The same incident: from a vague pager alert to one named process.")

_cols = [(90, "CPU", "vmstat, mpstat"), (270, "Memory", "free -m, vmstat"), (450, "Disk", "df, iostat"), (630, "Network", "ip -s link, ss -s")]
_parts = []
for _x, _name, _tools in _cols:
    _parts += [k.badge(_x, 36, _name, "acc"),
               k.note(_x, 76, "U: how busy is it?", ""), k.note(_x, 96, "S: what is waiting?", ""), k.note(_x, 116, "E: any errors?", ""),
               k.note(_x, 148, _tools, "acc")]
_parts += [k.note(360, 190, "U utilisation, S saturation, E errors: three questions for every resource.", ""),
           k.note(360, 214, "Whichever resource answers badly is your bottleneck.", "warn")]
IDEA_FIG = k.figure(720, 232, _parts, "The USE method: utilisation, saturation and errors for CPU, memory, disk and network", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


HOW = [
    ("Compare load with the number of cores",
     "The **load average** counts tasks that are running or waiting for a CPU. Count the cores first (`nproc`): load near the core count is full, and load far above it means work is queueing.",
     _small([k.badge(110, 36, "load average 31", "bad"), k.flow(170, 36, 250, 36, "warn", "vs"), k.badge(330, 36, "8 cores", "acc"), k.flow(380, 36, 460, 36, "bad"),
             k.badge(540, 36, "work is queueing", "bad"), k.note(320, 88, "story numbers: the same load on 32 cores would be fine", "")], "Load against cores")),
    ("Ask USE of every resource",
     "For each of CPU, memory, disk and network ask: how **busy** is it (utilisation), how much is **waiting** for it (saturation), and is it logging **errors**? The one that answers badly is the bottleneck.",
     _small([k.gauge(100, 50, 97, "CPU", "bad"), k.gauge(260, 50, 40, "memory", "ok"), k.gauge(420, 50, 12, "disk", "ok"), k.gauge(580, 50, 5, "network", "ok")], "Four resources, one bad", h=116)),
    ("Read memory the right way",
     "Linux uses spare memory to cache files, so a small `free` number is normal. Read **available** (what programs could use without swapping) and watch whether the machine is **swapping**, which is the real warning sign.",
     _small([k.badge(130, 36, "free 3055: unused", "warn"), k.badge(380, 36, "available 3318: usable", "ok"), k.note(580, 40, "MB, idle machine", ""),
             k.note(320, 88, "look at available and at swap activity, not at free", "")], "Free versus available")),
    ("Find who, fix it, measure again",
     "List processes sorted by CPU, memory or disk to name the heaviest one. Then fix or stop it and measure again, because a number that does not fall means you fixed the wrong thing.",
     _small([k.badge(110, 34, "ps --sort=-pcpu", "acc"), k.flow(176, 34, 236, 34, "acc"), k.badge(330, 34, "yes at 99.5% CPU", "bad"), k.flow(400, 34, 460, 34, "ok"), k.badge(545, 34, "re-measure", "ok"),
             k.note(320, 84, "name the heaviest process, fix or stop it, then measure again to prove it", "")], "Name the culprit and verify")),
]

DATA = dict(
    time="20 minutes",
    tagline="What to do when the server is slow and nobody knows why: a short checklist that tells you in a minute whether it is the CPU, memory, disk or network.",
    story=dict(
        title="02:07, everything is slow",
        paras=[
            "It is 02:07 on a Friday and the pager wakes you. Checkout is taking about nine seconds instead of one. You open the dashboard: every instance is green and every health check passes. Everything is up, and everything is slow.",
            "A teammate on the call suggests adding more servers. Another wants to restart the database. Both are guesses. You SSH into one web server and ask only one question: **which resource is the bottleneck?** In the first minute the numbers say the CPU: the run queue is long and every core is busy.",
            "One more command names the process: a nightly export job, started at 02:00, using every core. You stop it, the pages speed up within seconds, and you write down what you saw. The whole investigation took four commands, because you asked the same few questions of each resource instead of guessing. (The numbers in this story are made up; the experiments below are real recordings.)",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: ask the same three questions of every resource",
        one="The **USE method** says: for every resource, check its **utilisation** (how busy it is), its **saturation** (how much work is waiting for it) and its **errors**. A slow server is always short of one of four things: CPU, memory, disk or network.",
        figure=IDEA_FIG,
        paras=["It works because it is a map, not a guess. You walk the four resources in a few minutes, and the one with high utilisation, a queue, or errors is where to dig. Everything else you can rule out, which is just as valuable at 2 a.m."]),
    how=HOW,
    try_intro=["Four experiments you can run on any Linux machine. The recordings were taken on a quiet test machine, so most numbers look healthy: that is useful too, because you learn what normal looks like before you need to recognise abnormal."],
    **{"try": [
        ("pt", 0, 0, 0, "Cores, then load", {"annot": [
            ("8", "The first line is the number of cores: this machine has eight."),
            ("0.36 0.11 0.03", "Load averages over the last 1, 5 and 15 minutes. All far below 8 cores, so nothing is queueing."),
            ("1/195", "One task running right now out of 195 in total."),
        ]}),
        ("pt", 1, 0, 0, "Create CPU load and find the culprit", {"annot": [
            ("PID %CPU COMMAND", "Processes sorted by CPU share, biggest first."),
            ("1360 99.5 yes", "The burner we started: one core fully used. In real life, the first line is your culprit."),
            ("1255  5.6 sleep", "A tiny, short lived process. Far below the top, so ignore it."),
        ]}),
        ("pt", 2, 0, 0, "Read memory: available, not free", {"annot": [
            ("3791", "Total memory in MB."),
            ("473", "Used by programs."),
            ("3055", "Free: completely unused. This number alone says little."),
            ("396", "Buffers and cache: files kept in memory, handed back instantly when a program needs space."),
            ("3318", "Available: what programs could really use. This is the number to read."),
            ("Swap:", "The swap row. Used is 0 here; swap in use and growing is the warning sign."),
        ]}),
        ("pt", 5, 0, 0, "The first 60 seconds in one go", {"annot": [
            ("up 1 min", "How long the machine has been running: a very recent reboot would be a clue."),
            ("load average: 0.46, 0.14, 0.04", "Load again, still low."),
            ("0  0 99  0  0  0", "CPU split from vmstat: user, system, idle, waiting for disk, stolen. 99 percent idle."),
            ("3129564", "Free memory in KiB (about 3 GB), matching the memory table."),
            ("Mem:", "A quick memory check at the end, so you see CPU, run queue, swap and memory together."),
        ]}),
    ]},
    breaks=[
        ("Reading free instead of available", "A server shows little free memory and someone panics, but Linux fills spare memory with cache on purpose. Fix: read `available`, and check whether swap is in use and growing.", ""),
        ("Load average without core count", "A load of 8 is a crisis on 1 core and idle on 32. Fix: always compare with `nproc`, and use pressure numbers (`/proc/pressure`) to see real stalls.", "bad"),
        ("One core stuck, the rest idle", "The average CPU looks fine at 12 percent, but a single thread is at 100 percent and everything waits on it. Fix: look per core with `mpstat -P ALL`.", ""),
        ("Disk full by inodes or deleted files", "`df -h` shows space free, yet writes fail because the inodes ran out, or a deleted file is still held open. Fix: check `df -i` too, and `lsof` for deleted files.", ""),
        ("Fixing the loudest, not the bottleneck", "You tune the busiest looking thing, but the real bottleneck was elsewhere. Fix: walk all four resources before you act, and re-measure after every change.", "bad"),
        ("Everything idle, users still slow", "The machine is quiet, so the delay is outside it: a slow database, a DNS lookup, a remote API. Fix: time each hop of the request and look at the dependencies.", ""),
    ],
    real=[
        dict(company="Brendan Gregg", text="The USE method page describes the checklist this chapter teaches: for every resource, check utilisation, saturation and errors.", url="https://www.brendangregg.com/usemethod.html", source="Brendan Gregg: The USE Method"),
        dict(company="Netflix", text="A Netflix engineering post describes a ten command checklist for the first 60 seconds on a slow Linux server, including `uptime`, `vmstat`, `mpstat`, `iostat` and `free -m`.", url="https://netflixtechblog.com/linux-performance-analysis-in-60-000-milliseconds-accc10403c55", source="Netflix Tech Blog: Linux Performance Analysis in 60,000 Milliseconds"),
        dict(company="Linux kernel", text="The kernel documentation for pressure stall information describes how Linux reports the share of time tasks are stalled waiting for CPU, memory or I/O, exposed under `/proc/pressure/`.", url="https://docs.kernel.org/accounting/psi.html", source="Linux kernel documentation: PSI"),
    ],
    real_note="These notes summarise the linked documentation and posts; read the source for the full detail.",
    interview=[dict(scenario=iv("pt", 0), who="A very common Linux troubleshooting prompt: reported by candidates, not official."),
               dict(scenario=iv("pt", 2), who="A frequent probing question about memory: reported by candidates, not official."),
               dict(scenario=iv("pt", 5), who="A good senior level follow-up: reported by candidates, not official.")],
    interview_sub="Say your answer aloud first, then compare with the model answer. These are the shapes of question candidates report, not official lists.",
    recap=dict(
        points=["Everything up and everything slow means: find the bottleneck resource, do not guess.",
                "USE: for each resource check utilisation, saturation and errors.",
                "Compare the load average with the core count; load far above cores means queueing.",
                "Read available memory and swap activity, never just free.",
                "Name the heaviest process with ps sorted by CPU or memory, then fix it.",
                "Re-measure after every change, and write down what you saw for the runbook."],
        quick=[("What does USE stand for?", "Utilisation, saturation, errors: how busy a resource is, how much is waiting, and whether it reports errors."),
               ("A server has load 20 on 4 cores. Is that bad?", "Yes: five times more runnable work than cores means tasks are queueing. Check which process and whether it is CPU or disk waiting."),
               ("Why is low free memory often fine?", "Linux uses spare memory as file cache and gives it back on demand. Read available instead, and watch swap.")]),
    deeper=[("The USE method", "S10_linux_performance_triage.html#l1"), ("CPU", "S10_linux_performance_triage.html#l2"), ("Memory", "S10_linux_performance_triage.html#l3"), ("Disk", "S10_linux_performance_triage.html#l4"), ("Network", "S10_linux_performance_triage.html#l5"), ("The first 60 seconds", "S10_linux_performance_triage.html#l6")],
)
