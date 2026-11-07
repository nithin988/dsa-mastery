"""Chapter 11: When the usual tools are not enough (strace, lsof, tcpdump, core dumps)."""
import sd2kit as k
from sd2 import iv, figure_of

# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "3:12 a.m.", "kind": "",
     "scene": lambda cx, cy, w: k.person(cx - 70, cy - 10, 1.0) + k.scaled(k.server(cx + 10, cy, "order-sync", "ok") + k.badge(cx + 10, cy + 58, "CPU 1%", "ok"), cx + 10, cy, .95),
     "caption": "Pager: customers pay, then see a spinner. Dashboards are all green. The worker is alive."},
    {"title": "The silence", "kind": "bad",
     "scene": lambda cx, cy, w: k.scaled(k.server(cx - 56, cy, "order-sync", "warn") + k.flow(cx - 24, cy, cx + 14, cy, "bad", dash=True) + k.queue(cx + 64, cy, "orders waiting", "bad", None, 4) + k.badge(cx + 64, cy + 54, "1,400 and rising", "bad"), cx, cy, .82),
     "caption": "No new log line since 2:31. Not busy, not crashed. It is waiting for something that never comes."},
    {"title": "Look inside", "kind": "ok",
     "scene": lambda cx, cy, w: k.scaled(k.server(cx - 62, cy, "order-sync", "ok") + k.flow(cx - 30, cy, cx + 24, cy, "ok") + k.cloud(cx + 62, cy - 4, "gateway", "bad") + k.badge(cx - 8, cy + 58, "stuck in read()", "warn"), cx, cy, .82),
     "caption": "strace and lsof name the call and the peer: a payment gateway connection with no timeout."},
], "ShopKart's silent worker, three moments", "A process can be stuck without using CPU or writing a log line.")

IDEA_FIG = k.figure(720, 250, [
    k.note(360, 22, "Pick the tool by the question, not by habit", "acc"),
    k.clock(90, 70, None), k.badge(90, 122, "strace", "acc"),
    k.note(90, 150, "What is it asking", ""), k.note(90, 166, "the kernel for?", ""),
    k.server(270, 66, None), k.badge(270, 122, "lsof", "acc"),
    k.note(270, 150, "What does it hold", ""), k.note(270, 166, "open? Who has the port?", ""),
    k.cloud(450, 66, None), k.badge(450, 122, "tcpdump", "acc"),
    k.note(450, 150, "Are the packets", ""), k.note(450, 166, "really arriving?", ""),
    k.alert(630, 66, None, "warn"), k.badge(630, 122, "core + gdb", "acc"),
    k.note(630, 150, "Where exactly did", ""), k.note(630, 166, "it crash?", ""),
    k.note(360, 206, "Try the first 60 seconds checklist first. Reach for these when it points at one process.", ""),
    k.note(360, 230, "Each one is read only to start with. Each costs more the longer you leave it running.", "warn"),
], "Four deep tools, four questions", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


HOW = [
    ("strace: what is the process asking the kernel for?",
     "A program cannot touch a file, a socket or a clock by itself: it asks the kernel through a **system call** such as `openat` or `read`. `strace` prints each call and its result, so a hung process shows its last call with no result, and a failing one shows the error code.",
     _small([k.server(60, 44, "process"), k.flow(90, 44, 220, 44, "acc", "openat(...)"), k.flow(220, 60, 90, 60, "bad", "-1 ENOENT"), k.cache(262, 44, "kernel", "acc"),
             k.note(450, 40, "last line, no result = waiting", "warn"), k.note(450, 62, "result -1 = it failed, and why", "bad")], "strace sits between the process and the kernel", h=104)),
    ("lsof: what does it hold open, and who owns the port?",
     "On Linux a file, a socket and a pipe are all **file descriptors**, small numbers each process holds. `lsof` lists them for any process, or tells you which process listens on a port. It also finds a deleted file that a process still holds, which keeps the disk full.",
     _small([k.server(60, 44, "process"), k.flow(90, 38, 200, 20, "acc"), k.flow(90, 44, 200, 44, "acc"), k.flow(90, 50, 200, 70, "warn"),
             k.note(270, 24, "log file", ""), k.note(270, 48, "listening socket :8083", ""), k.note(290, 74, "deleted file, still held", "warn"), k.badge(520, 44, "lsof -p PID", "acc")], "lsof lists what one process holds", h=100)),
    ("tcpdump: are the packets really arriving?",
     "`tcpdump` prints the packets that cross a network interface. Always give it a filter such as `tcp port 8084`. A healthy conversation starts with the handshake flags `S`, `S.`, `.`, then data. A lone `S` repeated means nobody answered.",
     _small([k.phone(50, 40, "client"), k.flow(80, 32, 250, 32, "acc", "S"), k.flow(250, 50, 80, 50, "ok", "S."), k.server(290, 40, "server"),
             k.badge(440, 40, "S, S., . then data", "ok"), k.note(580, 44, "S, S, S = no reply", "bad")], "A packet capture shows the handshake", h=100)),
    ("Core dump and gdb: read a crash after the fact",
     "When a native program crashes it can leave a **core file**, a snapshot of its memory. `gdb` loads the program and the core and prints the **backtrace**: the chain of function calls that led to the crash, with the bad value in the top frame.",
     _small([k.alert(60, 40, "crash", "bad"), k.flow(90, 40, 200, 40, "warn", "core file"), k.database(236, 40, "core", "warn"), k.flow(262, 40, 340, 40, "acc", "gdb bt"),
             k.badge(450, 26, "#0 copy_name dst=0", "bad"), k.badge(450, 54, "#1 parse_line", ""), k.note(582, 44, "caller = cause", "ok")], "A backtrace points at the failing line", h=104)),
]

DATA = dict(
    time="15 minutes",
    tagline="Four tools that look inside one process or one connection when the metrics and the logs have nothing left to say.",
    story=dict(
        title="3:12 a.m., and everything is green",
        paras=[
            "The pager says orders are not being confirmed. Customers pay, then stare at a spinner. Mira, the engineer on call with you, opens every dashboard: CPU 1%, memory fine, disk fine, no errors. The worker process that confirms orders, `order-sync`, is running.",
            "But the queue of orders waiting has grown from nothing to 1,400 in forty minutes, and the worker has not written a log line since 2:31. A busy process shows up as CPU. A crashed one shows up in the logs. This one is neither: it is **waiting** for something that never arrives.",
            "The usual tools have run out, so you look at the process itself. One command shows the single call it is stuck in. Another shows who is on the other end: a connection to the payment gateway, opened with no timeout. A restart drains the queue by 3:34. A timeout in the code, shipped the next morning, makes sure it cannot happen again.",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: ask the process, not the dashboard",
        one="Metrics and logs are what the program chose to tell you. **Deep tools** ask the machine what is really happening: which calls a process makes, what it holds open, what crosses the wire and where it died.",
        figure=IDEA_FIG,
        paras=["These tools work on any language, because every program talks to the machine the same way, through system calls and sockets. Start with the first 60 seconds checklist from the performance chapter. Reach for these only when it points at one process or one connection and still gives no reason."]),
    how=HOW,
    try_intro=["Four real recordings. A hang cannot be recorded safely, so the first one shows the same tool on a call that fails: you will see exactly what a trace line looks like. Then a deleted file that still fills the disk, the packets of one web request, and a crash read from its core file."],
    **{"try": [
        ("dt", 0, 0, 3, "See the exact call that failed", {"annot": [
            ('openat(AT_FDCWD, "nothere", O_RDONLY)', "the system call: open the file `nothere` for reading"),
            ("ENOENT (No such file or directory)", "the kernel's answer: the result is -1 and the reason is ENOENT, so the path does not exist"),
            ("+++ exited with 1 +++", "the process ended with status 1, which the shell sees as failure")]}),
        ("dt", 1, 0, 2, "Find a deleted file that is still using space", {"annot": [
            ("(deleted)", "the name is gone but the process still holds the file, so its blocks are not freed"),
            ("bash 4w 0", "`lsof +L1` finds it: process `bash`, descriptor 4 open for writing, link count 0")]}),
        ("dt", 2, 0, 1, "Read one web request as packets", {"annot": [
            ("Flags [S] Flags [S.] Flags [.]", "the three way handshake: connect, accept, confirm"),
            ("Flags [P.]", "data pushed: the first one is the request, the next is the reply"),
            ]}),
        ("dt", 3, 0, 3, "Read a crash from its core file", {"annot": [
            ("copy_name (dst=0x0", "frame 0, where it crashed: the destination pointer is 0, a null pointer"),
            ("at crash.c:2", "the exact source line that wrote through it"),
            ("in parse_line", "frame 1, the caller that passed the null pointer: the real bug is here"),
            ("in main ()", "the bottom frame: where the program started")]}),
    ]},
    breaks=[
        ("strace slows the process", "The strace manual notes that a traced process runs more slowly than a normal one. On a busy production service that can turn a small problem into an outage. Fix: trace one process briefly, filter with `-e`, or use `strace -c` for a summary.", "bad"),
        ("A capture with no filter", "`tcpdump` on a busy interface prints thousands of lines a second, fills disks and records data you should not keep. Fix: always filter by host and port, limit with `-c`, and keep captures private and short.", "bad"),
        ("Encrypted traffic", "On HTTPS the packets show who talked and when, but not what was said. Fix: use the capture to prove the connection and its timing, and read the content in the application logs or with a test client.", ""),
        ("No permission, or no symbols", "Attaching to another user's process needs root, and a binary built without debug information gives a backtrace of bare addresses. Fix: run as the right user, and keep the symbol files for every release.", ""),
        ("Core dumps fill the disk", "A core file holds the process memory: it can be large and it can contain passwords. Fix: set a size limit, store cores in a protected folder, and clean them out.", ""),
        ("Looking at frame zero only", "The top frame shows where it crashed, but the cause is often a caller that passed a bad value. Fix: read the whole backtrace, and print the arguments of each frame.", ""),
    ],
    real=[
        dict(company="Linux man pages", text="The `strace` manual describes tracing system calls and signals, and includes a note that a traced process runs more slowly than a non-traced one.", url="https://man7.org/linux/man-pages/man1/strace.1.html", source="strace(1), Linux man-pages project"),
        dict(company="tcpdump project", text="The `tcpdump` manual describes the capture filter language (host, port and protocol expressions) used to keep a capture small enough to read.", url="https://www.tcpdump.org/manpages/tcpdump.1.html", source="tcpdump(1), tcpdump.org"),
        dict(company="Linux man pages", text="The `core(5)` page describes when a core dump is produced, how its size is limited with `RLIMIT_CORE`, and how the file name is chosen.", url="https://man7.org/linux/man-pages/man5/core.5.html", source="core(5), Linux man-pages project"),
    ],
    interview=[dict(scenario=iv("dt", 0), who="A common senior systems question: reported by candidates at large tech companies, not official.", ),
               dict(scenario=iv("dt", 1, "A classic Linux operations question: reported by candidates, not official."), who="Reported by candidates as a classic Linux question, not official."),
               dict(scenario=iv("dt", 3, "A question for roles that run native code: reported by candidates, not official."), who="Reported by candidates for roles that run native code, not official.")],
    interview_sub="Say your answer aloud first, then compare with the model answer. These are the shapes of question candidates report, not official lists.",
    recap=dict(
        points=["When metrics and logs are silent, look at the process itself.",
                "`strace` shows the calls a process makes; the last call with no result is what it waits for.",
                "`lsof` shows what a process holds open, who owns a port, and deleted files that still use space.",
                "`tcpdump` with a filter proves whether packets arrive: S, S., then data is healthy.",
                "A core file plus `gdb bt` shows the chain of calls to a crash; read the callers, not only frame 0.",
                "Every deep tool has a cost: trace briefly, filter captures, protect core files."],
        quick=[("A process uses no CPU and does nothing. Which tool first?", "`strace -p PID` (or `strace -f` on a new run): the last call without a result is what it waits for."),
               ("`df` says full but `du` is small. What do you check?", "`lsof +L1` for a deleted file that a process still holds open."),
               ("What does a repeated lone `S` in tcpdump mean?", "The client keeps sending connection requests and nobody replies: the packets are lost or the server is not answering.")]),
    deeper=[("strace", "S11_deep_debugging_tools.html#l1"), ("lsof", "S11_deep_debugging_tools.html#l2"), ("tcpdump", "S11_deep_debugging_tools.html#l3"), ("gdb and core dumps", "S11_deep_debugging_tools.html#l4"), ("Choosing the right tool", "S11_deep_debugging_tools.html#l5")],
)
