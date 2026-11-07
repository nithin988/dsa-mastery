"""Chapter 9: Debug like a detective (the debugging method)."""
import sd2kit as k
from sd2 import iv

# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "Three people, five theories", "kind": "bad",
     "scene": lambda cx, cy, w: k.crowd(cx, cy - 34, 3, 44, .95, "bad") + k.alert(cx, cy + 40, None),
     "caption": "Checkout is failing. Everyone blames something different."},
    {"title": "One method", "kind": "warn",
     "scene": lambda cx, cy, w: k.person(cx - 62, cy - 4, 1.1, "warn") + k.flow(cx - 36, cy - 4, cx - 6, cy - 4, "warn") + k.badge(cx + 44, cy - 4, "grep ERROR", "warn"),
     "caption": "Stop guessing. Read the evidence, make one guess that can be proven wrong, then test it."},
    {"title": "Found in minutes", "kind": "ok",
     "scene": lambda cx, cy, w: k.person(cx - 62, cy - 4, 1.1, "ok") + k.flow(cx - 36, cy - 4, cx - 12, cy - 4, "ok") + k.badge(cx + 40, cy - 4, "NZ missing", "ok"),
     "caption": "The log named the cause all along: a price table with no entry for New Zealand."},
], "ShopKart's checkout failure, three moments", "The same incident: from a room full of theories to one line in a log.")

IDEA_FIG = k.figure(720, 240, [
    k.badge(80, 50, "1 Observe", "acc"), k.flow(124, 50, 196, 50, "acc"),
    k.badge(250, 50, "2 Hypothesise", "warn"), k.flow(308, 50, 372, 50, "acc"),
    k.badge(430, 50, "3 Predict", "warn"), k.flow(474, 50, 548, 50, "acc"),
    k.badge(600, 50, "4 Test", "ok"),
    k.note(80, 90, "what exactly happens?", ""), k.note(80, 106, "read the error, the log", ""),
    k.note(250, 90, "one guess, written down", ""), k.note(250, 106, "that can be proven wrong", ""),
    k.note(430, 90, "if true, I will see X", ""), k.note(430, 106, "if false, I will see Y", ""),
    k.note(600, 90, "run the cheapest check", ""), k.note(600, 106, "compare with prediction", ""),
    '<path class="sd-a warn dash" d="M600,128 V160 H80 V68" fill="none" marker-end="url(#dga)"/>',
    k.note(340, 154, "Wrong, or half right? You now have new facts. Loop again.", "warn"),
    k.note(360, 206, "Each loop is one cheap test. Ten quick loops beat one long argument.", ""),
], "The debugging loop: observe, hypothesise, predict, test", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


def _squares():
    out = ""
    for i in range(16):
        out += f'<rect class="sd-job{" on" if i == 10 else ""}" x="{40 + i * 34}" y="20" width="26" height="26" rx="4"/>'
    return out


HOW = [
    ("Observe before you guess",
     "Say exactly what happens, to whom, and since when. Read the error message in full and find the first error in the log, because the newest line is usually a side effect.",
     _small([k.server(60, 40, None), k.flow(90, 40, 190, 40, "bad", "error"), k.badge(272, 40, "KeyError: 'NZ'", "bad"), k.flow(342, 40, 420, 40, "acc"),
             k.badge(512, 40, "pricing.py line 41", "warn"), k.note(320, 100, "the message names what and where: read it before theorising", "")], "Reading the evidence")),
    ("Make a guess that can be proven wrong",
     "A hypothesis is one specific theory, such as \"the price table has no entry for New Zealand\". Add a **prediction**: if that is true, an Australian order should still work. A guess that nothing could disprove is not a test.",
     _small([k.person(60, 50, 1.0), k.badge(260, 30, "Guess: NZ is missing from the price table", "warn"), k.badge(260, 72, "Then: other countries still work", "ok"),
             k.note(520, 34, "can be proven wrong", "acc"), k.note(520, 76, "so it is a real test", "acc")], "A hypothesis and its prediction", h=100)),
    ("Narrow it down by halving",
     "If you cannot see the cause, cut the problem in half and test one half. Good or bad tells you where the fault is not. Sixteen items take four tests, and a million take about twenty.",
     _small([_squares(), k.note(159, 74, "lines 1 to 8: ok", "ok"), k.note(431, 74, "lines 9 to 16: FAIL", "bad"),
             k.note(320, 104, "the same trick finds a bad commit, a bad config line or a bad server", "")], "Halving", h=116)),
    ("Compare working with broken",
     "When something works in one place and not in another, stop reasoning and **diff** them: environment variables, versions, config files, the commit before and after. The difference is the shortlist of suspects.",
     _small([k.server(100, 40, "works", "ok"), k.server(540, 40, "broken", "bad"), k.flow(135, 36, 255, 36, "acc"), k.flow(505, 36, 385, 36, "acc"),
             k.note(320, 32, "diff", "acc"), k.note(320, 84, "LANG, MODE, PATH, version: what is different?", "")], "Diffing two environments")),
]

DATA = dict(
    time="20 minutes",
    tagline="Why guessing is the slowest way to fix a bug, and the simple loop that finds the cause of almost anything: observe, guess, predict, test.",
    story=dict(
        title="09:07, the morning after launch",
        paras=[
            "The night before, ShopKart started shipping to New Zealand. At 09:07 you are about to hand over your first night shift when support pings: some customers cannot check out. The log shows three failed checkouts in three minutes, one of them slow (2,310 ms) just before it died.",
            "Three people gather around one screen and five theories appear. Sam from support blames the payment provider. Maya, who wrote the release, says it cannot be her code. Someone says the database looks slow, someone else says the CDN, and a fifth person says it is the customers' browsers. Each theory is plausible. Nobody has checked any of them.",
            "You ask for one thing: **stop, and read the log around the first error**. A few lines up from the failure is a traceback ending in `KeyError: 'NZ'`. The new pricing code has no entry for New Zealand. Four of the five theories were wrong, and it took forty minutes of arguing to find out what one search would have shown in forty seconds.",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: a loop, not a hunch",
        one="**Debugging** is a loop of four moves: observe the evidence, form one hypothesis, predict what you would see if it is true, then test it. Each pass either finds the cause or removes a suspect.",
        figure=IDEA_FIG,
        paras=["It works because it replaces opinions with cheap experiments. Good debuggers are not cleverer; they change **one thing at a time**, write down what they tried, and trust evidence over memory. The Google SRE book describes troubleshooting in exactly these terms, as the hypothetico-deductive method: hypothesise a cause, test it, repeat."]),
    how=HOW,
    try_intro=["Four small experiments, each a few lines you can paste into any Linux shell. First, read a log around the first error. Then test a hypothesis with a trace. Then halve a problem, and finally diff a working setup against a broken one."],
    **{"try": [
        ("db", 1, 0, 1, "Read the log around the first error", {"annot": [
            ("09:07:02 WARN  slow /checkout 2310ms", "A warning just before the failure: the slow request is the first sign of trouble."),
            ("09:07:03 ERROR failed /checkout", "The first error. This is the one to understand; later ones repeat it."),
            ("Traceback (most recent call last):", "Python is about to print the chain of calls that led to the crash."),
            ("File \"pricing.py\", line 41, in compute_total", "The place in your code where it went wrong: file, line and function."),
            ("KeyError: 'NZ'", "What went wrong: the code looked up a key, 'NZ', that is not in the table. Read a trace from the bottom up."),
        ]}),
        ("db", 0, 0, 2, "Test a hypothesis with a trace", {"annot": [
            ("+ n=4", "The shell shows each command after it has expanded variables. First, n is set to 4."),
            ("+ echo 'average: 0'", "The sum was computed before this line printed: total was never set, so it counted as 0 and 0 divided by 4 is 0. The prediction (total is empty) was confirmed."),
            ("average: 0", "The program's own output: a silent wrong answer, which is worse than a crash."),
        ]}),
        ("db", 2, 0, 2, "Halve the problem", {"annot": [
            ("FAIL", "Lines 9 to 12 of a 16 line file contain the bad line. An earlier test of lines 1 to 8 said ok, so the search space just halved twice and is now four lines."),
        ]}),
        ("db", 3, 0, 0, "Diff working against broken", {"annot": [
            ("2,3c2,3", "Lines 2 and 3 changed. Everything else (such as PATH) is identical, so it can be ruled out."),
            ("< LANG=C", "The left side, the working setup: locale C."),
            ("> LANG=en_US.UTF-8", "The right side, the broken setup: a different locale."),
            ("< MODE=prod", "Left: running in production mode."),
            ("> MODE=test", "Right: running in test mode. Two suspects instead of hundreds."),
        ]}),
    ]},
    breaks=[
        ("Changing five things at once", "The problem goes away and you do not know which change fixed it, or whether you broke something else. Fix: change one thing, test, and undo it if it did nothing.", "bad"),
        ("Fixing the symptom", "You restart the server, the errors stop, and everyone goes home. The cause is still there and returns at the next peak. Fix: keep the evidence (logs, a trace) and find why before declaring it done.", ""),
        ("Reading the last line, not the first", "The newest error is often a knock-on effect of an earlier one. In the recorded log, three errors repeat the same failure, and the traceback sits after the first. Fix: find the first error and read around it.", ""),
        ("Only testing your favourite theory", "You look for evidence that supports your guess and ignore the rest. Fix: write the prediction first, and add what would prove you wrong.", "bad"),
        ("Dismissing the flaky one", "A job that fails 3 times in 12 runs is not bad luck, it is a bug with a rate. Fix: loop until it fails, keep that run's output, and study that exact run.", ""),
        ("Waiting on a hang", "A command that never returns gives no error to read. Fix: wrap it in `timeout`, which stops it and returns exit status 124, so a hang becomes a clear signal.", ""),
    ],
    real=[
        dict(company="Google SRE", text="The chapter on effective troubleshooting describes troubleshooting as an application of the **hypothetico-deductive method**: form possible causes from what you observe, then test them by comparing the system with the hypothesis or by making a controlled change.", url="https://sre.google/sre-book/effective-troubleshooting/", source="Google SRE book: Effective Troubleshooting"),
        dict(company="Git", text="The `git bisect` documentation describes using a **binary search** over history: start from a known good and a known bad commit, test the middle, and repeat until the first bad commit is found. It is the halving idea from this chapter, automated.", url="https://git-scm.com/docs/git-bisect", source="git documentation: git-bisect"),
    ],
    real_note="Both notes summarise the linked official documentation; read the source for the full detail.",
    interview=[dict(scenario=iv("db", 0), who="A very common troubleshooting prompt: reported by candidates at many companies, not official."),
               dict(scenario=iv("db", 5), who="A frequent on call question: reported by candidates, not official."),
               dict(scenario=iv("db", 2), who="A popular follow-up about flaky tests: reported by candidates, not official.")],
    interview_sub="Say your answer aloud first, then compare with the model answer. These are the shapes of question candidates report, not official lists.",
    recap=dict(
        points=["Stop guessing: observe first, and say exactly what happens, to whom and since when.",
                "Find the first error in the log and read the lines around it; read a stack trace from the bottom up.",
                "A good hypothesis is specific and comes with a prediction that could prove it wrong.",
                "Halve the problem: sixteen items take four tests, and the same trick finds bad commits and bad config.",
                "When it works here and not there, diff the two environments instead of arguing about them.",
                "Change one thing at a time, keep notes, and wrap anything that might hang in a timeout."],
        quick=[("What are the four moves of the debugging loop?", "Observe, hypothesise, predict, test. If the test disagrees with the prediction, you have new facts and loop again."),
               ("Why read a stack trace from the bottom?", "The last line says what was raised, and the lines above it say which code raised it and how it got there."),
               ("How many tests does it take to find one bad line in 16?", "Four, by testing half at a time: 16 to 8 to 4 to 2 to 1.")]),
    deeper=[("The loop", "S09_debugging_method.html#l1"), ("Reading errors and traces", "S09_debugging_method.html#l2"), ("Shrink by halving", "S09_debugging_method.html#l3"), ("Working versus broken", "S09_debugging_method.html#l4"), ("Flaky failures and hangs", "S09_debugging_method.html#l5")],
)
