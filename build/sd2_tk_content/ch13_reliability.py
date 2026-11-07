"""Chapter 13: Measure, alert, respond (SLIs, SLOs, error budgets, burn-rate alerts, incidents, postmortems)."""
import sd2kit as k
from sd2 import scen, iv

# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "3:04 a.m.", "kind": "warn",
     "scene": lambda cx, cy, w: k.scaled(k.person(cx - 62, cy - 4, 1.0, "warn") + k.alert(cx + 8, cy - 4, None, "warn") + k.badge(cx + 8, cy + 38, "CPU 83%", "warn"), cx, cy, .95),
     "caption": "Pager: CPU above 80% on web-3. Users are fine. It is the nightly report, the third time this week."},
    {"title": "2:10 p.m. Tuesday", "kind": "bad",
     "scene": lambda cx, cy, w: k.crowd(cx - 50, cy - 20, 3, 26, .75, "bad") + k.scaled(k.server(cx + 42, cy, "checkout", "bad") + k.badge(cx + 42, cy + 56, "8% fail", "bad"), cx + 42, cy, .85),
     "caption": "A payment provider slows down. 8% of requests fail for three hours. No alert fires. A customer emails."},
    {"title": "With an SLO", "kind": "ok",
     "scene": lambda cx, cy, w: k.gauge(cx - 56, cy + 10, 56, "budget used", "warn") + k.scaled(k.badge(cx + 56, cy - 16, "2 pages", "bad") + k.badge(cx + 56, cy + 18, "1 ticket", "warn"), cx + 56, cy, .95),
     "caption": "One number and one budget. In a month: 2 pages and 1 ticket for real incidents, not 237 for CPU."},
], "ShopKart's alerts, three moments", "The same month, with alerts on causes and then with alerts on user pain.")


def _seg(x1, x2, kind):
    return f'<rect class="sd-sh {kind}" x="{x1}" y="48" width="{x2 - x1}" height="34" rx="6"/>'


IDEA_FIG = k.figure(720, 262, [
    k.note(360, 22, "One month of error budget for a 99.9% SLO (3 million requests a day)", "acc"),
    _seg(60, 396, "acc"), _seg(396, 474, "warn"), _seg(474, 678, "bad"),
    '<line class="sd-a bad dash" x1="660" y1="38" x2="660" y2="94"/>',
    k.note(228, 110, "bad release 56%", "acc"), k.note(435, 110, "failover +13%", "warn"), k.note(576, 110, "slow dependency +34%", "bad"),
    k.note(690, 132, "100% = 89999 failed requests", "bad", "end"),
    k.note(360, 166, "103% spent after three incidents: the budget is gone", "bad"),
    k.note(360, 192, "SLI: good requests divided by all requests, measured at the edge", ""),
    k.note(360, 214, "SLO: the target, 99.9% over 30 days", ""),
    k.note(360, 236, "Error budget: 100% minus the SLO, 0.1%, about 43 minutes of full outage", ""),
], "An error budget being spent by three incidents", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


HOW = [
    ("Measure what users feel (the SLI)",
     "A **service level indicator (SLI)** is the share of requests that were good: they succeeded and were fast enough. Measure it where the user is, at the edge, not on a machine: CPU can be at five percent while every payment fails.",
     _small([k.crowd(56, 40, 2, 26, .8), k.flow(96, 40, 190, 40, "acc"), k.server(226, 40, "edge"), k.flow(256, 40, 330, 40, "acc"), k.badge(440, 40, "good / all requests", "ok"), k.note(440, 84, "measured at the edge, not on a machine", "")], "The SLI is a ratio users can feel", h=100)),
    ("Set the target and spend the budget (the SLO)",
     "A **service level objective (SLO)** is the target for that share over a window, such as 99.9 percent over 30 days. What it allows to fail is the **error budget**: 0.1 percent, about 43 minutes of full outage. While there is budget you ship; when it is gone you fix reliability.",
     _small([k.badge(80, 40, "SLO 99.9%", "acc"), k.flow(138, 40, 200, 40, "acc"), k.badge(262, 40, "budget 0.1%", "warn"), k.flow(324, 40, 386, 40, "acc"), k.badge(464, 40, "about 43 minutes", "ok"),
             k.note(320, 84, "ship while budget remains, stop and fix when it is spent", "")], "From target to budget", h=100)),
    ("Alert on burn rate, over two windows",
     "The **burn rate** is how many times faster than the allowed pace the budget is being used. A fast burn pages someone and a slow burn opens a ticket. Checking a long window and a short window together proves the problem is real and still happening.",
     _small([k.badge(150, 32, "fast: 14x, 60 min and 5 min", "bad"), k.flow(266, 32, 330, 32, "bad"), k.badge(400, 32, "PAGE now", "bad"),
             k.badge(150, 72, "slow: 3x, 6 hours and 30 min", "warn"), k.flow(266, 72, 330, 72, "warn"), k.badge(400, 72, "ticket", "warn"), k.note(560, 56, "the thresholds used below", "")], "Fast burn pages, slow burn opens a ticket", h=100)),
    ("Run the incident, then write the postmortem",
     "Time every incident: detect, acknowledge, mitigate, resolve. **Mitigate first** (roll back or fail over), then find the cause. Afterwards write a **blameless postmortem**: what happened, why the system allowed it, and follow up actions with owners.",
     _small([k.badge(60, 36, "0 began", ""), k.badge(190, 36, "4 alert", "bad"), k.badge(320, 36, "9 acknowledged", "warn"), k.badge(466, 36, "31 mitigated", "ok"), k.badge(588, 36, "180 resolved", "ok"),
             k.note(320, 84, "minutes after the start", "")], "An incident timeline", h=100)),
]

DATA = dict(
    time="15 minutes",
    tagline="Turn \"is it reliable?\" into a number, spend it on purpose, and page a human only for what users feel.",
    story=dict(
        title="3:04 a.m., the wrong alarm",
        paras=[
            "The pager says `CPU above 80% on web-3`. Mira, on call, checks: it is the nightly report job and users are fine. She acknowledges it and goes back to bed. It is the third time this week. Over a month that alert pages 237 times, and almost none of them are about a real user problem.",
            "On Tuesday at 2:10 p.m. a payment provider slows down. For three hours 8 percent of ShopKart's requests fail. No alert fires, because CPU is fine. The first sign is a customer email. When the founder asks \"how reliable are we?\", nobody can answer with a number.",
            "You do four things. Choose a number users would accept: 99.9 percent of requests good over 30 days. Work out the budget that allows. Alert on how fast the budget is burning instead of on CPU. And time every incident, then write what happened without blaming anyone. The same month would have produced 2 pages and 1 ticket.",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: reliability is a budget you spend on purpose",
        one="Perfect reliability is impossible and expensive. An **SLO** sets the target, the **error budget** is how much failure that target allows, and **burn rate** tells you how fast you are spending it.",
        figure=IDEA_FIG,
        paras=["This replaces arguments with a shared rule. While there is budget, the team ships and takes risks. When it is spent, risky releases stop until reliability is fixed. Alerts follow the same logic: page when the budget will be gone soon, ticket when it is slipping slowly, and stay quiet about causes that users cannot feel."]),
    how=HOW,
    try_intro=["Two real recordings from a simulation with fixed numbers. First: what each target allows, and how three incidents spend a budget. Then: a month of CPU alerts against burn-rate alerts, and the clock of one incident. The simulated traffic is an assumption: three million requests a day."],
    **{"try": [
        ("rp", 0, 0, 0, "What a target allows, and what three incidents cost", {"annot": [
            ("99.9%    0.10% of requests    43 minutes", "three nines allows about 43 minutes of full outage in 30 days"),
            ("99.99%   0.01% of requests    4.3 minutes", "four nines leaves almost no room"),
            ("may fail 89999 requests in 30 days", "the same budget counted in requests, for 3 million requests a day"),
            ("bad release, 40 minutes at 60% errors", "one bad release alone uses 56 percent of the month"),
            ("slow dependency, 3 hours at 8% errors", "this one pushes the total to 103 percent"),
            ("the budget is SPENT", "the agreed rule applies: freeze risky releases and fix reliability")]}),
        ("rp", 1, 0, 0, "Noisy alerts, burn-rate alerts and an incident clock", {"annot": [
            ('alert on "CPU above 80%": 237 pages', "cause alerts fire all month and almost none matter to users"),
            ("burn-rate alerts: 2 pages and 1 tickets", "only the three real incidents alert: two pages, one ticket"),
            ("(day 23.0): ticket", "the three hour slow leak never burns fast enough to page, so the slow rule opens a ticket"),
            ("alert fired", "minute 4: how long detection took"),
            ("mitigated (rolled back)", "minute 31: the pain stops here, long before the cause is fixed"),
            ("to resolve 180 min", "the root cause fix takes longest, which is why mitigating first matters")]}),
    ]},
    breaks=[
        ("An SLO of 100 percent", "It is impossible, it freezes all change, and users stop noticing after the first few nines. Fix: set the target just above what users notice and use the budget to decide.", "bad"),
        ("SLIs that measure machines", "CPU and memory can look healthy while users fail, and the reverse. Fix: measure good requests at the edge: success and speed as the user sees them.", ""),
        ("Alerts on causes", "A page for every CPU spike teaches people to ignore the pager, so the real alert is late. Fix: page on SLO burn and keep cause metrics on dashboards for diagnosis.", "bad"),
        ("No policy for a spent budget", "If nobody agreed what happens when the budget is gone, it is only a chart. Fix: agree in advance with product and engineering: slow risky releases and fund reliability work.", ""),
        ("Blaming a person", "A postmortem that names a culprit teaches people to hide mistakes. Fix: write what happened, why the system allowed it, and what changes, assuming everyone acted sensibly with what they knew.", "bad"),
        ("Alerts nobody can act on", "A page with no dashboard and no runbook wastes the first ten minutes. Fix: every page links to a dashboard and a runbook, and unactionable pages are deleted.", ""),
    ],
    real=[
        dict(company="Google SRE book", text="The chapter on service level objectives describes SLIs, SLOs and SLAs and explains how to choose indicators that reflect what users care about.", url="https://sre.google/sre-book/service-level-objectives/", source="Site Reliability Engineering: Service Level Objectives"),
        dict(company="Google SRE workbook", text="The chapter on alerting on SLOs defines burn rate as how fast the service consumes the error budget relative to the SLO, and describes a multiwindow, multi-burn-rate alerting approach. The thresholds in this chapter's simulation are an illustration in that style, not a quotation.", url="https://sre.google/workbook/alerting-on-slos/", source="The Site Reliability Workbook: Alerting on SLOs"),
        dict(company="Google SRE book", text="The postmortem chapter describes blameless postmortems as a tenet of SRE culture, written to find contributing causes without blaming individuals or teams.", url="https://sre.google/sre-book/postmortem-culture/", source="Site Reliability Engineering: Postmortem Culture"),
    ],
    interview=[dict(scenario=scen("rp", 0), who="A core SRE question: reported by candidates, not official."),
               dict(scenario=scen("rp", 1), who="An operations maturity question: reported by candidates, not official."),
               dict(scenario=iv("pb", 5), who="An incident handling question: reported by candidates, not official.")],
    interview_sub="Say your answer aloud first, then compare with the model answer. These are the shapes of question candidates report, not official lists.",
    recap=dict(
        points=["An SLI is good requests divided by all requests, measured where users are.",
                "An SLO is the target over a window; the error budget is one minus the SLO.",
                "99.9 percent over 30 days leaves about 43 minutes of full outage.",
                "Page on burn rate over two windows, ticket for slow burns, not on causes like CPU.",
                "Time every incident (detect, acknowledge, mitigate, resolve) and mitigate first.",
                "Write blameless postmortems with owned follow up actions."],
        quick=[("What is an error budget?", "One minus the SLO: how much failure you may spend in the window."),
               ("Why alert on burn rate instead of CPU?", "Burn rate tracks what users feel and how soon the budget runs out; CPU alerts fire often and rarely matter."),
               ("What does mitigate first mean?", "Stop the pain with a rollback or failover before hunting the cause, which is why mitigation can take 31 minutes and the full fix 180.")]),
    deeper=[("SLIs, SLOs and error budgets", "S13_reliability_practice.html#l1"), ("Alerts that matter", "S13_reliability_practice.html#l2")],
)
