"""Toolkit chapter 1: Why did my program do that? (processes, system calls, memory, file descriptors, exit codes)."""
import sd2kit as k
from sd2 import iv

# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "On her laptop", "kind": "ok",
     "scene": lambda cx, cy, w: k.person(cx - 50, cy - 8, 1.1, "ok") + k.server(cx + 40, cy, "laptop", "ok") + k.flow(cx - 24, cy, cx + 8, cy, "ok") + k.badge(cx + 40, cy + 62, "exit code 0", "ok"),
     "caption": "The export script writes a full file of orders every time. Nothing to see."},
    {"title": "On the server, 12:40 a.m.", "kind": "bad",
     "scene": lambda cx, cy, w: k.phone(cx - 46, cy, "pager", "bad") + k.alert(cx + 40, cy - 4, None) + k.badge(cx + 40, cy + 48, "file: 0 bytes", "bad"),
     "caption": "Same script, same command. Finance gets an empty file and the job says it succeeded."},
    {"title": "At 12:58 a.m.", "kind": "ok",
     "scene": lambda cx, cy, w: k.person(cx - 50, cy - 8, 1.1, "ok") + k.server(cx + 40, cy, "server", "warn") + k.flow(cx - 24, cy, cx + 8, cy, "warn") + k.badge(cx + 40, cy + 62, "ENOENT", "warn"),
     "caption": "You ask the machine what the program asked the kernel. One file was not found, and nobody checked."},
], "ShopKart's nightly export, three moments", "The same program on two machines: the difference was never the code, it was what the program asked for.")

IDEA_FIG = k.figure(720, 270, [
    k.server(60, 66, "Shell", "", "PID 228"),
    k.flow(94, 66, 176, 66, "acc", "1. starts"),
    '<rect class="sd-sh acc" x="180" y="22" width="250" height="150" rx="12"/>',
    k.note(305, 44, "Your process (PID 234)", "acc"),
    k.badge(305, 78, "private memory", "acc"),
    k.badge(305, 108, "open files 0, 1, 2", "acc"),
    k.badge(305, 138, "exit code when it ends", "warn"),
    k.flow(434, 100, 520, 100, "acc", "2. asks"),
    '<rect class="sd-sh" x="524" y="22" width="170" height="150" rx="12"/>',
    k.note(609, 44, "Kernel", ""),
    k.note(609, 80, "files and disks", "acc"),
    k.note(609, 106, "network", "acc"),
    k.note(609, 132, "memory and CPU", "acc"),
    '<path class="sd-a warn" d="M305,172 V204 H60 V138" fill="none" marker-end="url(#dga)"/>',
    k.note(360, 226, "3. when it ends, the exit code goes back to the shell: 0 means success", "warn"),
    k.note(360, 254, "A process can only do real work by asking the kernel. Watch those requests and nothing stays a mystery.", ""),
], "A process asks the kernel for everything and reports an exit code when it ends", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


HOW = [
    ("The shell starts a process: fork, then exec",
     "To run a command, the shell first makes a copy of itself (**fork**). The copy then swaps itself for the program you asked for (**exec**). The new **process** gets its own number, the **PID**.",
     _small([k.server(60, 40, "shell", "", "PID 228"), k.flow(92, 40, 200, 40, "acc", "1. fork"), k.server(232, 40, "child", "warn", "PID 234"),
             k.flow(264, 40, 372, 40, "acc", "2. exec"), k.server(404, 40, "ls", "ok", "PID 234"), k.note(540, 44, "same PID, new program", "ok")], "Fork and exec", h=112)),
    ("Every process gets its own private memory",
     "A process thinks it owns all the memory. In truth the kernel gives each process its own **address space**, a private map to real memory, so two processes can use the same address without ever touching each other's data.",
     _small([k.server(60, 30, "Process A"), k.flow(92, 30, 168, 30, "acc"), k.badge(260, 30, "address 4000 (A's own)", "acc"), k.flow(352, 30, 526, 60, "acc"),
             k.server(60, 118, "Process B"), k.flow(92, 118, 168, 118, "warn"), k.badge(260, 118, "address 4000 (B's own)", "warn"), k.flow(352, 118, 526, 88, "warn"),
             k.cache(560, 74, "RAM", "", "real memory"), k.note(320, 178, "Same address, different real memory. The kernel keeps the maps apart.", "")], "Private address spaces", h=190)),
    ("A program asks the kernel for everything",
     "Programs cannot touch disks or networks directly. They make **system calls**, such as `open`, `read` and `write`, and the **kernel** does the work. When a program opens a file, the kernel answers with a small number called a **file descriptor**.",
     _small([k.server(60, 40, "program"), k.flow(92, 40, 230, 40, "acc", "open(orders.csv)"), '<rect class="sd-sh" x="234" y="16" width="100" height="48" rx="10"/>', k.note(284, 45, "kernel", ""),
             k.flow(334, 40, 440, 40, "ok", "returns 3"), k.badge(520, 40, "fd 3 is your file", "ok"),
             k.note(320, 94, "If the file is missing, the kernel answers -1 ENOENT: no such file", "bad"),
             k.note(320, 118, "fd 0 is input, 1 is output, 2 is errors: opened for every process", "ok")], "A system call and a file descriptor", h=132)),
    ("When it ends, it leaves an exit code",
     "Every process finishes with a number. **0 means success** and anything from 1 to 255 means failure. The parent reads it (`$?` in the shell), but only if someone asks. A script that never checks will carry on as if all is well.",
     _small([k.server(60, 50, "program"), k.flow(92, 44, 164, 30, "ok"), k.badge(240, 30, "exit 0: it worked", "ok"), k.flow(92, 56, 164, 78, "bad"), k.badge(256, 78, "exit 1 to 255: it failed", "bad"),
             k.flow(330, 34, 404, 48, "ok"), k.flow(352, 78, 404, 58, "bad"), k.server(432, 52, "caller"), k.note(556, 56, "reads it with $?", "acc"),
             k.note(320, 112, "cron and CI only notice failure if your script passes the code on", "warn")], "Exit codes", h=126)),
]

DATA = dict(
    time="20 minutes",
    tagline="Why the same program can behave differently on two machines, and how to see what a program is really doing: processes, system calls, memory, open files and exit codes.",
    story=dict(
        title="12:40 a.m., the export that was empty",
        paras=[
            "It is your second week at ShopKart. Finance needs a file of the day's orders every night. Your colleague Priya wrote a small script, `export_orders.sh`, and it works perfectly on her laptop. She set it up on the server before going home and said, \"It just runs.\"",
            "At 12:40 a.m. she messages from bed: the file that reached finance is empty, 0 bytes, yet the job reports success. On her laptop the same script writes thousands of rows. On the server it prints nothing at all. Nobody can say why one program behaves in two ways.",
            "You could guess for hours. Instead you ask a better question: what did the program actually ask the machine to do? By 12:58 you have the answer. It looked for one file, did not find it, and carried on, because nobody checked the number it left behind when it failed.",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: a program is a conversation with the kernel",
        one="A **process** is a program that is running. It has its own memory and a list of open files, it asks the **kernel** (the core of the operating system) for everything else through **system calls**, and when it ends it leaves an **exit code**.",
        figure=IDEA_FIG,
        paras=["This is the model behind every Linux tool in the rest of the course. Pipes connect the open files of two processes. Permissions are checked by the kernel on each system call. Containers are processes with a restricted view of the machine. Once you can see the conversation, \"it works on my machine\" becomes a question you can answer."]),
    how=HOW,
    try_intro=["Four short experiments, all ordinary commands you can type yourself. First: who starts whom. Then: what a failure looks like as a number. Then: the exact call that failed. Finally: the three files every process starts with."],
    **{"try": [
        ("hc", 0, 0, 0, "Who started this program? Parent and child",
         {"annot": [("child PID: 234, parent PID: 228", "The command ran as a new process, number 234. Its parent, 228, is the shell you typed it into."),
                    ("this shell is PID 228", "The same number again: the child really is a child of this shell.")]}),
        ("hc", 0, 0, 2, "How a program says it failed: the exit code",
         {"annot": [("exit status: 3", "The command ended with code 3. The shell keeps the last code in `$?`. Zero would have meant success; anything else means something went wrong.")]}),
        ("hc", 1, 0, 1, "The exact call that failed: a missing file",
         {"annot": [("openat(AT_FDCWD, \"nothere.txt\", O_RDONLY) = -1 ENOENT", "The program asked the kernel to open `nothere.txt`. The kernel answered -1 with the reason ENOENT, which means no such file."),
                    ("cat: nothere.txt: No such file or directory", "The program turns that answer into a message for you."),
                    ("+++ exited with 1 +++", "And it leaves exit code 1 behind. A script that ignores this number is how an empty export reaches finance.")]}),
        ("hc", 3, 0, 0, "Every process starts with three open files",
         {"annot": [("fd 0 ->", "Descriptor 0 is standard input: where the program reads from."),
                    ("fd 1 ->", "Descriptor 1 is standard output: where it prints."),
                    ("fd 2 ->", "Descriptor 2 is standard error: where it reports problems. Here 1 and 2 point to the same place (the same pipe number), but they are separate descriptors.")]}),
    ]},
    breaks=[
        ("Ignoring the exit code", "A script keeps going after a command fails, so a failed step is hidden behind a later step that succeeds. Fix: turn on `set -e` (stop on error) or check `$?`, and make the script itself exit with a non-zero code on failure.", "bad"),
        ("The working directory is different", "A relative path like `orders.csv` means \"in the folder I was started from\". A scheduled job often starts somewhere else, and the file is not there. Fix: use absolute paths or `cd` to a known folder first.", ""),
        ("A different environment", "The shell passes **environment variables** (such as `PATH`) to each process. A server, cron or a container has different ones from your laptop, so a command is not found or behaves differently. Fix: set what you need inside the script and print it when debugging.", ""),
        ("Out of memory", "A process asks for more memory than the machine has, and the kernel's **OOM killer** ends it, usually with exit code 137 (128 plus signal 9). Fix: find what grew, and set a memory limit and an alert before it happens.", "bad"),
        ("Too many open files", "Each process may hold only so many file descriptors, and sockets count too. On the lab machine the limit is 10240; many systems default to 1024 (an assumption, check yours with `ulimit -n`). Fix: close files you no longer need and raise the limit deliberately.", ""),
        ("Zombies", "When a process ends, its exit code waits to be collected by its parent. If the parent never does, the finished process lingers as a **zombie**. Fix: make the parent wait for its children, or restart the parent.", ""),
    ],
    real=[
        dict(company="Linux man-pages", text="The page for `execve` describes how a program is run: the program being executed by the calling process is replaced with a new one. That is the \"exec\" half of how a shell starts every command.", url="https://man7.org/linux/man-pages/man2/execve.2.html", source="Linux man-pages: execve(2)"),
        dict(company="Linux man-pages", text="The `wait` page describes how a parent collects the exit status of a child, and notes that a child that has finished but has not been waited for stays as a zombie.", url="https://man7.org/linux/man-pages/man2/wait.2.html", source="Linux man-pages: wait(2)"),
        dict(company="Linux man-pages", text="The `syscalls` page lists the system calls that the Linux kernel provides, which is the complete menu of what a program can ask the kernel to do.", url="https://man7.org/linux/man-pages/man2/syscalls.2.html", source="Linux man-pages: syscalls(2)"),
    ],
    real_title="Where this is documented",
    real_tag="Primary sources",
    real_note="Primary documentation. Read the linked page for the exact wording.",
    interview=[dict(scenario=iv("hc", 0), who="A very common Linux and systems prompt: reported by candidates, not official."),
               dict(scenario=iv("hc", 1), who="Often asked as a follow-up to the question above: reported by candidates, not official."),
               dict(scenario=iv("hc", 4), who="A frequent question for operations and SRE roles: reported by candidates, not official.")],
    interview_sub="Say your answer aloud first, then compare with the model answer. These are the shapes of question candidates report, not official lists from any company.",
    recap=dict(
        points=["A process is a running program: its own memory, its own open files, an exit code at the end.",
                "The shell starts a command by fork (copy itself) then exec (become the new program).",
                "Programs never touch hardware: they make system calls and the kernel answers.",
                "Every process starts with three open files: 0 input, 1 output, 2 errors.",
                "Exit code 0 is success and anything else is failure; a script must check it or pass it on.",
                "When behaviour differs between machines, compare the environment, the working directory and the exact failing call."],
        quick=[("What is the difference between a program and a process?", "A program is a file on disk. A process is that program running, with its own memory, open files and PID."),
               ("What does exit code 0 mean, and how do you read it in the shell?", "It means success. Any other number means failure. The shell stores the last code in `$?`."),
               ("What does `ENOENT` in an strace line tell you?", "The kernel could not find the file or folder the program asked for: 'no such file or directory'.")]),
    deeper=[("What happens when you press Enter", "S01_how_computers_run_programs.html#l1"), ("System calls", "S01_how_computers_run_programs.html#l2"), ("Memory and address spaces", "S01_how_computers_run_programs.html#l3"),
            ("Files and file descriptors", "S01_how_computers_run_programs.html#l4"), ("Threads, CPUs and scheduling", "S01_how_computers_run_programs.html#l5"),
            ("Processes and exit codes (Linux internals)", "S04_linux_internals.html#l1")],
)
