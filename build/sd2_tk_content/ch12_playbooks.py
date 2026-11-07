"""Chapter 12: The runbook (playbooks for the recurring incidents)."""
import sd2kit as k
from sd2 import iv, figure_of

# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "Four times", "kind": "bad",
     "scene": lambda cx, cy, w: k.scaled(k.database(cx - 60, cy, "disk full", "bad") + k.alert(cx + 20, cy - 2, None) + k.badge(cx + 20, cy + 40, "x4 in 10 weeks", "bad") + k.person(cx + 76, cy - 8, .9, "warn"), cx, cy, .9),
     "caption": "Each time a different person fixed it a different way. One of them deleted the wrong folder."},
    {"title": "One page", "kind": "",
     "scene": lambda cx, cy, w: k.scaled(k.note(cx - 74, cy - 36, "Symptom: no space left", "acc", "start") + k.note(cx - 74, cy - 12, "1. df -h   2. df -i", "", "start") + k.note(cx - 74, cy + 12, "3. lsof +L1   4. du -a", "", "start") + k.note(cx - 74, cy + 36, "5. fix, then cause", "ok", "start"), cx, cy, .95),
     "caption": "You write the first runbook: the symptom, the checks in order, what each means, the safe fix."},
    {"title": "The fifth time", "kind": "ok",
     "scene": lambda cx, cy, w: k.scaled(k.person(cx - 66, cy - 6, 1.0, "ok") + k.flow(cx - 40, cy - 6, cx + 6, cy - 6, "ok") + k.database(cx + 52, cy, "disk", "ok") + k.badge(cx - 6, cy + 54, "fixed in 9 minutes", "ok"), cx, cy, .9),
     "caption": "Ines, three days into the job, follows the page at 2 a.m. and fixes it without waking anyone."},
], "ShopKart and the disk that kept filling, three moments", "The same incident, before and after someone wrote it down.")


def _row(y, a, b, c, d, kind=""):
    return (f'<rect class="sd-panel {kind}" x="12" y="{y - 17}" width="696" height="34" rx="8"/>'
            + k.note(24, y + 4, a, "acc", "start") + k.note(190, y + 4, b, "", "start") + k.note(380, y + 4, c, "", "start") + k.note(556, y + 4, d, "ok", "start"))


IDEA_FIG = k.figure(720, 300, [
    k.note(24, 24, "SYMPTOM", "", "start"), k.note(190, 24, "CHECK (one command)", "", "start"), k.note(380, 24, "WHAT IT MEANS", "", "start"), k.note(556, 24, "SAFE FIX", "", "start"),
    _row(58, "No space left", "df -h  then  df -i", "full, or out of inodes", "find big, rotate logs"),
    _row(100, "Address in use", "lsof -nP -iTCP:PORT", "an old copy still runs", "stop old, then start"),
    _row(142, "Exit code 137", "kubectl describe pod", "killed for memory", "find leak, set limits"),
    _row(184, "Load is high", "uptime; vmstat 1 3", "CPU, disk or memory?", "go to the perf chapter"),
    k.note(360, 236, "A runbook is a lookup table for a tired person at 3 a.m.", "acc"),
    k.note(360, 262, "Every row has the same four parts. If no row matches, go back to the method:", ""),
    k.note(360, 282, "observe, hypothesise, test.", ""),
], "A runbook: symptom, check, meaning, fix", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


HOW = [
    ("Name the symptom exactly",
     "Write the words the pager, the log or the user actually shows, such as `No space left on device` or `exit status 137`. Someone half asleep will search for those words, so use them as the title.",
     figure_of("pb", 0, 0)),
    ("Give one command per check, in order",
     "Each check is a single command that can be pasted, and the order goes from cheapest and safest to most expensive. For a full disk: space (`df -h`), then inodes (`df -i`), then deleted files still held open (`lsof +L1`), then the biggest directories (`du`).",
     _small([k.badge(70, 40, "1 df -h", "acc"), k.flow(122, 40, 168, 40, "acc"), k.badge(230, 40, "2 df -i", "acc"), k.flow(284, 40, 330, 40, "acc"), k.badge(398, 40, "3 lsof +L1", "acc"), k.flow(462, 40, 508, 40, "acc"),
             k.badge(570, 40, "4 du -a", "acc"), k.note(320, 86, "cheapest and safest first", "ok")], "Checks run from cheap to expensive", h=100)),
    ("Say what each result means, and the safe fix",
     "Every result points to one meaning and one fix: space full means find the big file, inodes full means find the folder of tiny files, a deleted file held open means restart or truncate that process. Mark anything risky, such as `rm`, with a warning and what to check first.",
     _small([k.badge(80, 36, "df -h: 100%", "bad"), k.flow(138, 36, 200, 36, "acc"), k.note(300, 40, "find the big file with du", "ok"),
             k.badge(80, 74, "df -h ok, df -i 100%", "warn"), k.flow(172, 74, 230, 74, "acc"), k.note(380, 78, "folder of tiny files: rotate it", "ok")], "Each result maps to one fix", h=100)),
    ("Say when to stop, and update the page after every incident",
     "A runbook must say when to stop and who to call, for example if the check does not match any row after ten minutes. After every incident add what was missing. Then ask the better question: can the fix be automated, or the cause removed?",
     _small([k.alert(60, 40, "no match", "warn"), k.flow(92, 40, 190, 40, "warn", "10 minutes"), k.person(226, 40, 1.0), k.note(310, 28, "call the owner", "warn", "start"), k.note(310, 50, "then add a new row", "ok", "start"),
             k.badge(540, 40, "automate it", "ok")], "Escalate, then improve the page", h=100)),
]

DATA = dict(
    time="15 minutes",
    tagline="Write the page once, so the fourth time, and every time after, takes minutes and does not depend on who is awake.",
    story=dict(
        title="2:07 a.m., the fourth time",
        paras=[
            "The pager says `No space left on device`. It is 2:07 a.m. and it is the fourth time in ten weeks. The first time, Sam deleted old logs by hand. The second time, Jo restarted the database, which did nothing because a deleted log was still held open. The third time, nobody noticed that one folder held six million tiny files.",
            "This time it takes 41 minutes to fix, and about ninety orders fail while the disk is full. Worse, nobody can say what the right fix is: each person did something different, and one of them nearly deleted the wrong directory. There is no checklist. The knowledge lives in three different heads.",
            "So the next morning, before anything else, you write one page. The symptom, five checks in order, what each result means, the safe fix and when to call the owner. Three weeks later it happens again. Ines, who joined on Monday, opens the page at 2 a.m. and fixes it in nine minutes. Nobody is woken up.",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: a lookup table for a tired person",
        one="A **runbook** (or playbook) is a short page for one recurring problem: the symptom, the checks in order, what each result means, and the safe fix. It turns hard won experience into steps anyone on call can follow.",
        figure=IDEA_FIG,
        paras=["It is not a replacement for thinking: it covers the problems you have already solved. For a new problem you still use the method from the debugging chapter. But about the same few incidents account for most pages, so a runbook for each one saves the most time."]),
    how=HOW,
    try_intro=["Four real recordings, each the check from one runbook row. Where the space went on a full disk, who owns a port that is already in use, what a zombie process looks like, and what exit status 137 really means."],
    **{"try": [
        ("pb", 1, 0, 2, "Disk full: find where the space went", {"annot": [
            ("15428", "the whole folder `disk`, in kilobytes (a `du -a` listing sorted largest first)"),
            ("disk/big", "one file holds almost all of it: 15360 of 15428 kilobytes, about 99.6 percent"),
            ("disk/f999", "the thousands of tiny files take no space at all, which is why `df -i` (inodes) is a separate check")]}),
        ("dt", 1, 0, 0, "Port in use: who is listening?", {"annot": [
            ("python3", "the command name of the process that owns the port"),
            ("IPv4 127.0.0.1:8083", "protocol and address: this process holds port 8083 on the local machine"),
            ("(LISTEN)", "the state: it is waiting for connections, so a second copy cannot bind this port")]}),
        ("pb", 2, 0, 0, "Zombies: a finished child nobody collected", {"annot": [
            ("Z+   python3", "state Z is a zombie: it has exited, but its parent has not read its exit status yet")]}),
        ("pb", 3, 0, 1, "Exit 137: the process was killed", {"annot": [
            ("exit status: 137", "128 plus 9: the process was ended by signal 9, SIGKILL, which in a container is often the out of memory killer")]}),
    ]},
    breaks=[
        ("The page goes stale", "Commands change when the system changes, and an old runbook fails at 3 a.m. Fix: give every page an owner and a date, and test its commands during a calm hour or an incident review.", "bad"),
        ("Too long to use", "A page that reads like an essay will not be read at 3 a.m. Fix: one symptom, numbered steps, one command per step, the meaning in a few words.", ""),
        ("Dangerous steps with no warning", "A tired person will paste `rm -rf` exactly as written. Fix: put the safe checks first, mark every destructive step, and say what to look at before running it.", "bad"),
        ("The runbook hides the cause", "If the fix is always the same, the page is a bandage and the incident will keep coming. Fix: link a ticket for the real cause and track how often each page is used.", ""),
        ("No exit", "Not every incident matches a row, and a page that never says \"stop\" keeps people guessing alone. Fix: say after how long and to whom to escalate.", ""),
    ],
    real=[
        dict(company="Google SRE book", text="The chapter on managing incidents describes running an incident with clear roles (an incident commander and leads for operations, communications and planning), which is the same structure a runbook should name at its escalation step.", url="https://sre.google/sre-book/managing-incidents/", source="Site Reliability Engineering: Managing Incidents"),
        dict(company="Google SRE book", text="The chapter on effective troubleshooting describes the process as a systematic method of forming and testing hypotheses, with triage first, which is the fallback when no runbook row matches.", url="https://sre.google/sre-book/effective-troubleshooting/", source="Site Reliability Engineering: Effective Troubleshooting"),
    ],
    interview=[dict(scenario=iv("pb", 0), who="Reported by candidates as a very common Linux troubleshooting question, not official."),
               dict(scenario=iv("pb", 2), who="Reported by candidates for container and Kubernetes roles, not official."),
               dict(scenario=iv("pb", 5), who="An incident handling question: reported by candidates, not official.")],
    interview_sub="Say your answer aloud first, then compare with the model answer. These are the shapes of question candidates report, not official lists.",
    recap=dict(
        points=["A runbook is a short page per recurring symptom: checks in order, what each means, the safe fix.",
                "Title it with the exact words the pager or log shows.",
                "One pasteable command per check, from cheapest and safest to most expensive.",
                "Disk full: space, then inodes, then deleted files held open, then the biggest files.",
                "Port in use: find the owner with `lsof`, stop the old copy politely before anything else.",
                "Say when to stop and escalate, and update the page after every incident."],
        quick=[("What are the four parts of a runbook row?", "Symptom, check, what it means, safe fix."),
               ("What does exit status 137 mean?", "128 plus 9: the process was killed by SIGKILL, often the out of memory killer."),
               ("Why check inodes as well as space?", "A disk can be full of millions of tiny files and show free space: `df -h` and `df -i` answer different questions.")]),
    deeper=[("Incident flow and playbooks", "S12_troubleshooting_playbooks.html#l1"), ("No space left on device", "S12_troubleshooting_playbooks.html#l2"), ("Zombies and stuck processes", "S12_troubleshooting_playbooks.html#l3"), ("Out of memory and exit 137", "S12_troubleshooting_playbooks.html#l4"), ("DNS failures", "S12_troubleshooting_playbooks.html#l5"), ("Certificates and timeouts", "S12_troubleshooting_playbooks.html#l6"), ("Container crash loops", "S12_troubleshooting_playbooks.html#l7")],
)
