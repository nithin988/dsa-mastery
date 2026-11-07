"""Chapter 4 (toolkit): What is the machine doing? Processes, memory, disk, permissions and services."""
import sd2kit as k
from sd2 import iv

# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "2:51 a.m.", "kind": "bad",
     "scene": lambda cx, cy, w: k.phone(cx - 44, cy - 4, "pager", "bad") + k.alert(cx + 40, cy - 8, None) + k.badge(cx, cy + 70, "checkout errors 38%", "bad"),
     "caption": "The pager says checkout is failing. The server answers ping and says it has been up for 41 days."},
    {"title": "3:04 a.m.", "kind": "warn",
     "scene": lambda cx, cy, w: k.person(cx - 62, cy - 6, 1.1, "warn") + k.server(cx + 20, cy - 6, "web-1", "warn") + k.flow(cx - 38, cy - 6, cx - 12, cy - 6, "warn") + k.badge(cx + 20, cy + 62, "disk 100%", "bad"),
     "caption": "Up is not healthy. A process was killed, the disk is full and a file cannot be written."},
    {"title": "3:40 a.m.", "kind": "ok",
     "scene": lambda cx, cy, w: k.person(cx - 62, cy - 6, 1.1, "ok") + k.server(cx + 20, cy - 6, "web-1", "ok") + k.flow(cx - 38, cy - 6, cx - 12, cy - 6, "ok") + k.badge(cx + 20, cy + 62, "5 checks pass", "ok"),
     "caption": "You ran five checks in order, fixed each cause, and wrote them down for the next person."},
], "ShopKart's web server, one night", "The same machine at three moments: up the whole time, healthy only at the end.")

IDEA_FIG = k.figure(720, 244, [
    k.server(72, 56, None), k._lbl(72, 96, "Processes", None),
    k.cache(216, 56, None), k._lbl(216, 96, "Memory", None),
    k.database(360, 56, None), k._lbl(360, 96, "Disk", None),
    k.person(504, 56, 1.25), k._lbl(504, 96, "Permissions", None),
    k.balancer(648, 56, None), k._lbl(648, 96, "Services", None),
    k.note(72, 126, "ps, top, kill", "acc"), k.note(72, 146, "who is running?", ""),
    k.note(216, 126, "free, dmesg", "acc"), k.note(216, 146, "who is using RAM?", ""),
    k.note(360, 126, "df, du, lsof", "acc"), k.note(360, 146, "is there room?", ""),
    k.note(504, 126, "ls -l, id, chmod", "acc"), k.note(504, 146, "who may write?", ""),
    k.note(648, 126, "systemctl", "acc"), k.note(648, 146, "does it restart?", ""),
    k.badge(72, 182, "wrong ones", "bad"), k.badge(216, 182, "none available", "bad"), k.badge(360, 182, "full", "bad"), k.badge(504, 182, "denied", "bad"), k.badge(648, 182, "stays dead", "bad"),
    k.note(360, 226, "Up is not healthy: a healthy machine passes all five checks.", "ok"),
], "Five checks that tell you what a Linux machine is really doing", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


HOW = [
    ("Processes: who is running, and how to stop one politely",
     "A **process** is a running program. You can ask it to stop with a **signal**: `kill` sends SIGTERM (number 15), which a program can catch to save its work and exit. `kill -9` sends SIGKILL, which cannot be caught, so there is no clean up.",
     _small([k.person(50, 38, .95), k.flow(76, 38, 190, 38, "acc", "SIGTERM: please stop"), k.server(226, 38, "app"), k.flow(254, 38, 360, 38, "ok", "cleans up"), k.badge(430, 38, "exit code 0", "ok"),
             k.note(140, 98, "kill -9: no chance to clean up", "bad"), k.badge(430, 94, "exit code 137", "bad")], "SIGTERM versus SIGKILL", h=112)),
    ("Memory: read available, not free",
     "Linux fills spare memory with a **file cache** to speed up disk reads, so the `free` column looks small on a healthy machine. Look at **available**: memory that programs could still get. If it truly runs out, the kernel's **OOM killer** (out of memory) picks a process and sends it SIGKILL.",
     _small([k.badge(70, 38, "used", "warn"), k.badge(150, 38, "cache", "acc"), k.badge(230, 38, "free", "ok"), k.note(190, 78, "available = free + cache that can be given back", "ok"),
             k.flow(300, 38, 408, 38, "bad", "if it runs out"), k.alert(440, 38, None), k.note(548, 42, "OOM killer sends SIGKILL", "bad")], "Used, cache, free and available memory", h=100)),
    ("Disk: space, inodes, and files that are deleted but still open",
     "A disk can be full of **bytes** (`df -h`) or full of **inodes**, the records that name each file (`df -i`). A third trap: if you delete a file that a running process still has open, the space is not freed until that process closes it or restarts. `lsof +L1` lists those files.",
     _small([k.database(56, 40, "disk"), k.flow(90, 44, 136, 44, "acc"), k.badge(190, 28, "space: df -h", "acc"), k.badge(190, 60, "inodes: df -i", "acc"), k.note(430, 32, "deleted but still held open?", "bad"), k.note(430, 56, "lsof +L1 shows who holds it", "bad")], "Three ways a disk fills", h=100)),
    ("Permissions and services: who may do what, and who restarts it",
     "`ls -l` shows three sets of rights, **read, write, execute**, for the owner, the group and everyone else. A program can only do what the user it runs as may do. On modern Linux, **systemd** starts services, runs them as a chosen user, and restarts them if they crash (`Restart=on-failure`).",
     _small([k.badge(80, 32, "-rwxr-x---", "acc"), k.note(80, 66, "owner, group, others", "acc"), k.flow(170, 40, 262, 40, "acc", "runs as user app"), k.server(300, 40, "app.service", "ok"), k.flow(334, 40, 436, 40, "warn", "if it crashes"), k.badge(540, 40, "systemd restarts it", "ok")], "File permissions and a systemd service", h=100)),
]

DATA = dict(
    time="20 minutes",
    tagline="Up is not the same as healthy. Learn the five checks, processes, memory, disk, permissions and services, that tell you what a Linux machine is really doing.",
    story=dict(
        title="Checkout fails, but the server is up",
        paras=[
            "It is 2:51 a.m. on a Tuesday and the pager says checkout errors are at 38 percent. You log in to the web server. It answers ping, the web port is open, and `uptime` says it has been running for 41 days. By every simple test, the machine is fine.",
            "It is not fine. Over the next quarter of an hour you find three things. The checkout process was killed at 2:44 for using too much memory. A log file has grown to 20 GB and the disk is full. And Dana, the developer on call, deleted the log, but the disk is still full.",
            "Nobody on the team could say what the machine was actually doing, only that it was \"up\". A healthy machine passes five checks: the right **processes** are running, there is enough **memory**, there is room on the **disk**, programs are **permitted** to do their job, and **services** restart themselves. This chapter teaches those five, in the order you run them.",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: five checks, in order",
        one="A machine can be **up and still broken**. Health is not one number: it is five small questions, and the answer to each one is a command you can run in seconds.",
        figure=IDEA_FIG,
        paras=["You do not need to memorise hundreds of commands. Ask the five questions in order and write down what you see. Most real incidents turn out to be one of them: a process that died, memory that ran out, a disk that filled, a file nobody may write, or a service that nobody restarts."]),
    how=HOW,
    try_intro=["Four experiments, each recorded from a real Debian Linux machine. First, what a killed process leaves behind. Then how to read the memory numbers, a deleted file that is still using space, and what a permission error looks like."],
    **{"try": [
        ("li", 1, 1, 1, "What does exit code 137 mean?", {
            "annot": [("exit code: 137", "A process killed by `kill -9` reports 137, which is 128 plus the signal number 9.")],
            "e": "The shell starts a `sleep`, kills it with `kill -9` (SIGKILL), and prints its exit code. Exit codes above 128 mean \"stopped by a signal\": subtract 128 to get the signal. The OOM killer uses the same signal, so 137 in a restart loop is a strong hint that memory ran out."}),
        ("pt", 2, 0, 0, "How do I read free -m?", {
            "annot": [("available", "The column to trust: memory that programs could still get, including cache the kernel can give back."),
                      ("3318", "Megabytes available on this small lab machine. Compare it with total (3791), not with the free column."),
                      ("Swap:", "Disk space used as slow overflow memory. A busy swap with little available memory means trouble.")],
            "e": "`free -m` prints memory in megabytes. This lab machine is almost idle, so the numbers are calm. On a busy server `free` shrinks as the cache grows, and that is normal; `available` is the honest number."}),
        ("dt", 1, 0, 2, "A deleted file that still takes space", {
            "annot": [("(deleted)", "The name is gone, but the process still holds the file open, so its space is not freed."),
                      ("bash 4w 0", "Command bash holds file descriptor 4 open for writing, and the file has 0 names left (the link count). `lsof +L1` finds exactly these.")],
            "e": "The command opens a file, writes to it, then deletes it while it is still open. The kernel keeps the data until the last holder lets go. This is why `df` can stay at 100 percent after you delete a huge log."}),
        ("sh", 4, 1, 1, "What a permission error looks like", {
            "annot": [("Permission denied", "The script exists, but the execute bit was removed, so the kernel refuses to run it. The fix is `chmod +x`, not `chmod 777`.")],
            "e": "The command removes the execute right from a script and runs it. Linux answers `Permission denied`. This message is about rights, not about the file being missing, so check `ls -l` and the user the program runs as."}),
    ]},
    breaks=[
        ("Free memory looks tiny", "Linux uses spare memory as a file cache, so `free` is small on a healthy server. Read `available`, and look at swap activity, before you panic.", ""),
        ("The OOM killer", "When memory truly runs out, the kernel kills a process and the service may restart in a loop, exit code 137. Confirm with `dmesg | grep -i \"killed process\"`, then find the cause: a leak, a limit set too high, or too many workers.", "bad"),
        ("Deleted but still open", "You delete a 20 GB log and `df` shows no change, because the process still has it open. Restart or reload the process, or truncate the file instead of deleting it.", "bad"),
        ("Out of inodes", "The disk shows free space but new files fail. Millions of tiny files used every inode (`df -i`). Delete or archive the small files, and stop the thing that creates them.", ""),
        ("Zombie processes", "A zombie has finished but its parent never collected its exit status, so it shows as `Z` or `<defunct>`. You cannot kill a zombie; fix or restart the parent.", ""),
        ("Running everything as root", "It makes errors disappear for a day. Then files owned by root break the next run as a normal user. Run services as their own user with the least rights they need.", "bad"),
    ],
    real=[
        dict(company="Linux man pages", text="The signal(7) manual page describes each signal, which ones can be caught, and states that SIGKILL and SIGSTOP cannot be caught, blocked or ignored.", url="https://man7.org/linux/man-pages/man7/signal.7.html", source="signal(7), Linux manual page"),
        dict(company="Linux man pages", text="The proc_meminfo(5) manual page describes the `MemAvailable` field as an estimate of how much memory is available for starting new applications without swapping.", url="https://man7.org/linux/man-pages/man5/proc_meminfo.5.html", source="proc_meminfo(5), Linux manual page"),
        dict(company="systemd", text="The systemd.service manual describes the `Restart=` setting that tells systemd when to restart a service that exits or crashes.", url="https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html", source="systemd.service(5), freedesktop.org"),
    ],
    real_title="Where this is written down",
    real_tag="Primary docs",
    real_note="These are the manual pages the commands come from. Read the page for the exact behaviour on your system.",
    interview=[dict(scenario=iv("li", 5), who="A frequent Linux question: reported by candidates, not official."),
               dict(scenario=iv("li", 4), who="A frequent question for operations roles: reported by candidates, not official."),
               dict(scenario=iv("li", 6), who="Often asked in container and on-call interviews: reported by candidates, not official.")],
    interview_sub="Say your answer aloud first, then compare with the model answer. These are the shapes of question candidates report, not official lists.",
    recap=dict(
        points=["Up is not healthy: run five checks, processes, memory, disk, permissions and services.",
                "SIGTERM asks a process to stop and can be caught; SIGKILL cannot be caught, and exit code 137 means it was SIGKILLed.",
                "Read `available` in `free`, not `free`: the kernel uses spare memory as cache.",
                "A full disk can mean no space (`df -h`), no inodes (`df -i`), or deleted files still held open (`lsof +L1`).",
                "`Permission denied` is about rights and the running user: read `ls -l`, do not reach for `chmod 777`.",
                "systemd starts, supervises and restarts services; `systemctl status` and `journalctl` tell you why one stopped."],
        quick=[("A process exits with code 137. What happened?", "It received signal 9 (128 plus 9), SIGKILL. A common cause is the OOM killer, so check `dmesg` and memory."),
               ("You deleted a big log but `df` did not change. Why?", "A running process still holds the file open. Restart or reload it, or truncate the file instead of deleting it."),
               ("Why does `free` show almost no free memory on a healthy server?", "The kernel uses spare memory as a file cache and gives it back when needed. Read the available column.")]),
    deeper=[("Processes", "S04_linux_internals.html#l1"), ("Signals", "S04_linux_internals.html#l2"), ("Memory and the OOM killer", "S04_linux_internals.html#l3"), ("Files, inodes and links", "S04_linux_internals.html#l4"),
            ("Users and special bits", "S04_linux_internals.html#l6"), ("Services, logs and jobs", "S04_linux_internals.html#l7"), ("Memory triage", "S10_linux_performance_triage.html#l3"), ("Disk triage", "S10_linux_performance_triage.html#l4")],
)
