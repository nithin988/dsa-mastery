"""Systems Mastery S13: reliability practice (SLIs, SLOs, error budgets, burn-rate alerts, incident metrics), deterministic simulations."""

LESSONS = [
    dict(
        title="SLIs, SLOs and error budgets: deciding how reliable is reliable enough",
        tier="hot",
        situation="Product wants \"100% uptime\". Engineering knows that is impossible and that chasing the last fraction costs more than it is worth. A service level objective turns an argument into a number, and the error budget tells you how much failure you may spend.",
        learn=["SLI: what you measure", "SLO: the target", "Error budget: what you may spend", "What a budget means in minutes and in requests"],
        model=[
            "A **service level indicator (SLI)** is a measurement of what users experience, usually a ratio: good requests divided by all requests (a request is good if it succeeded and was fast enough). A **service level objective (SLO)** is the target for that ratio over a window, for example 99.9 percent of requests good over 30 days. The **error budget** is what the SLO allows to go wrong: 0.1 percent of requests, or about 43 minutes of full outage in 30 days. While there is budget left you can ship changes and take risks; when it is spent you slow down and fix reliability. This replaces \"never fail\" with a shared, measurable rule. An **SLA** is a contract with customers (often with penalties) and should be looser than the internal SLO.",
            "Choose SLIs from the **user's** point of view (successful, fast responses at the edge), not from machine metrics (CPU), and choose the SLO from what users tolerate and what you can afford: every extra nine costs roughly ten times more. Measure over a **rolling window** and look at **burn rate** (how fast the budget is being consumed relative to the allowed pace), which is the subject of the next lesson.",
        ],
        analogy="A monthly data allowance on a phone plan: you may use it, you can see how much is left, and when it runs low you change your behaviour. Zero use would waste the plan; running out has consequences.",
        sim=None,
        walk=[
            ("Pick what users feel", "Good responses: successful and fast enough, measured at the edge."),
            ("Set the target", "For example 99.9 percent over 30 days, from user tolerance and cost."),
            ("Compute the budget", "0.1 percent of requests, about 43 minutes of full downtime."),
            ("Track consumption", "How much has been spent, and how fast."),
            ("Act on the budget", "Ship while it lasts, stabilise when it is gone."),
        ],
        groups=[
            dict(title="What a target allows, and what an incident costs", cmds=[
                dict(c=r'''python3 - <<'EOF'
WINDOW_MIN = 30 * 24 * 60
print('SLO       error budget          full outage allowed in 30 days')
for slo in (99.0, 99.5, 99.9, 99.95, 99.99):
    budget = 100 - slo
    mins = WINDOW_MIN * budget / 100
    print('%-8s %-20s %s' % (str(slo) + '%', '%.2f%% of requests' % budget, ('%.0f minutes' % mins) if mins >= 10 else ('%.1f minutes' % mins)))
print()
requests = 3_000_000 * 30                                    # 3 million requests a day
slo = 99.9
budget_requests = requests * (100 - slo) / 100
print('a service with 3 million requests a day and a %.1f%% SLO may fail %d requests in 30 days' % (slo, budget_requests))
incidents = [('bad release, 40 minutes at 60% errors', 3_000_000 / 1440 * 40 * 0.60), ('database failover, 6 minutes at 100% errors', 3_000_000 / 1440 * 6), ('slow dependency, 3 hours at 8% errors', 3_000_000 / 1440 * 180 * 0.08)]
spent = 0
for name, lost in incidents:
    spent += lost
    print('  %-46s lost %6d requests -> budget used so far: %4.0f%%' % (name, lost, 100 * spent / budget_requests))
print('after three incidents the budget is %s' % ('SPENT: freeze risky releases and fix reliability' if spent > budget_requests else 'still available (%.0f%% left)' % (100 - 100 * spent / budget_requests)))
EOF''',
                     e="The arithmetic that makes an SLO usable. 99.9 percent over 30 days leaves about **43 minutes** of full outage; 99.99 percent leaves **under 4**. Counting in requests is fairer for a service whose traffic varies: at three million requests a day, the budget is 90,000 failed requests a month. The incident list shows how quickly a budget disappears: a bad release at 60 percent errors for 40 minutes costs more than half of it, and with a failover and a slow dependency on top, the budget is gone. At that point the agreed rule applies: slow down risky changes and invest in reliability.",
                     annot=[("99.9% 0.10% of requests 43 minutes", "three nines allows about 43 minutes of full outage per 30 days"),
                            ("99.99% 0.01% ... 4.3 minutes", "four nines leaves little room for anything"),
                            ("may fail 90000 requests in 30 days", "the same budget counted in requests"),
                            ("bad release ... lost 50000 requests -> budget used so far: 56%", "an incident's cost is a share of the budget, not just a story"),
                            ("after three incidents the budget is SPENT", "the rule bites: freeze risky releases, fix reliability")]),
            ]),
        ],
        scenario=dict(
            title="\"What is an SLO and how do you use an error budget to make decisions?\"",
            ask="A core SRE interview question. They want definitions tied to decisions.",
            clarify=[("Is this a user-facing service? What do users notice most: errors, latency or freshness?", "Choose the SLI from what users feel.")],
            think=[("Define the terms.", "SLI measures good over total; SLO is the target over a window; the error budget is one minus the SLO; an SLA is a customer contract, looser than the SLO."),
                   ("Choose SLIs.", "Availability (successful responses), latency (fast enough, as a percentile threshold), possibly correctness and freshness, measured at the edge."),
                   ("Choose the target.", "From user tolerance and cost; avoid 100 percent; set it just above what users notice."),
                   ("Use the budget.", "While budget remains, release freely and run experiments; when it is spent, freeze risky changes and prioritise reliability work; the policy is agreed in advance by product and engineering."),
                   ("Alert on burn rate.", "Page when the budget is being consumed too fast to last the window."),
                   ("Review.", "Look at budget consumption in reviews; tune SLOs with data.")],
            answer=["\"An SLI measures what users experience as a ratio, say successful and fast requests over all requests. An SLO is the target for it over a window, for example 99.9 percent over 30 days, and the error budget is what that allows to fail: 0.1 percent, about 43 minutes of full outage a month. An SLA is the looser customer contract.",
                    "I use the budget to decide: while there is budget we ship and experiment; when it is spent we freeze risky changes and put the effort into reliability. That rule is agreed in advance by product and engineering, so it is a shared policy and not an argument each time. I alert on how fast the budget is burning rather than on raw errors.\""],
            follow=[("Why not aim for 100 percent?", "It is impossible, and each extra nine costs much more while users stop noticing; it would also freeze all change."),
                    ("Which latency measure do you use?", "A percentile threshold such as the share of requests faster than 300 ms; averages hide the tail."),
                    ("What if the SLO is always met with lots of budget left?", "Either the SLO is too loose, or you can ship faster and take more risk.")],
            slips=["Choosing CPU or memory as an SLI.", "Setting 100 percent.", "Having an SLO nobody uses to make decisions."],
        ),
        quick=[("What is an error budget?", "One minus the SLO: the amount of failure you may spend in the window."), ("How many minutes of full outage does 99.9% allow in 30 days?", "About 43."), ("Why measure SLIs at the user edge?", "Machine metrics can look healthy while users suffer.")],
        traps=["An SLO of 100 percent.", "SLIs that measure machines, not users.", "No agreed policy for what to do when the budget is spent."],
    ),
    dict(
        title="Alerts that matter: burn rate, noise and the incident clock",
        tier="hot",
        situation="The pager goes off 40 times a week and 38 of them need no action, so the two that matter are slow to get attention. Good alerting pages rarely, only for things users feel, and tells you how urgent each one is.",
        learn=["Why cause-based alerts create noise", "Burn-rate alerts over two windows", "Measuring incidents: detect, respond, resolve"],
        model=[
            "An alert should mean: a human must act now. Alerts on **causes** (CPU above 80 percent) fire constantly and often mean nothing to users. Alerts on **symptoms** (users are seeing errors or slowness) fire when it matters. **Burn-rate alerting** ties alerts to the SLO: the burn rate is how many times faster than \"sustainable\" the budget is being consumed (a rate of 1 would use exactly the whole budget by the end of the window). A fast burn (for example 14 times the allowed rate over an hour) means the budget will be gone in about two days: **page now**. A slow burn (about 3 to 6 times over several hours) means a **ticket**. Checking **two windows** (a long one to prove it is real and a short one to prove it is still happening) removes blips and stale alerts.",
            "Measure how incidents go: **time to detect**, **time to acknowledge**, **time to mitigate** (stop the pain) and **time to resolve** (fix the cause). Mitigate first (roll back, fail over, shed load), then investigate. Keep a **timeline**, assign an **incident commander** for large incidents, communicate on a schedule, and finish with a **blameless postmortem** that records what happened, why the system allowed it and the follow-up actions with owners. Alert quality is itself measured: pages per week, share needing action, and incidents found by customers before by monitoring.",
        ],
        analogy="A smoke alarm that goes off when you make toast gets its battery removed. A good one rings only for real smoke, louder when the fire is spreading faster, and tells the fire brigade when it started.",
        sim=None,
        walk=[
            ("Alert on user-visible symptoms", "Error rate and latency against the SLO."),
            ("Compute the burn rate", "Actual error ratio divided by the allowed error ratio."),
            ("Use two windows", "A long window to be sure, a short one to be current."),
            ("Page for fast burns, ticket for slow ones", "Urgency follows how soon the budget runs out."),
            ("Time and review every incident", "Detect, mitigate, resolve, then a blameless postmortem."),
        ],
        groups=[
            dict(title="Noisy alerts versus burn-rate alerts, and an incident's clock", cmds=[
                dict(c=r'''python3 - <<'EOF'
import random
rng = random.Random(21)
SLO_ERR = 0.001                                           # 99.9% SLO: 0.1% of requests may fail
minutes = 30 * 24 * 60
# per-minute error ratio: tiny blips on most minutes, three real incidents
err = [max(0.0, rng.gauss(0.0004, 0.0004)) for _ in range(minutes)]
for start, length, level in ((5000, 25, 0.12), (21000, 8, 0.6), (33000, 180, 0.008)):
    for m in range(start, start + length): err[m] = level
cpu = []
for _ in range(minutes // 10): cpu += [rng.random() < 0.06] * 10   # "CPU above 80%" in about 6% of 10-minute blocks, mostly harmlessly
def naive_alerts():
    fired, quiet = 0, True
    for m in range(minutes):
        if cpu[m] and quiet: fired += 1; quiet = False
        if not cpu[m]: quiet = True
    return fired
def burn(m, window):
    lo = max(0, m - window + 1); return (sum(err[lo:m + 1]) / (m - lo + 1)) / SLO_ERR
def burn_alerts():
    pages, tickets, active_p, active_t, hits, last_page = 0, 0, False, False, [], -10**9
    for m in range(minutes):
        fast = burn(m, 60) >= 14 and burn(m, 5) >= 14           # fast burn: both windows over 14x
        slow = burn(m, 360) >= 3 and burn(m, 30) >= 3           # slow burn: both windows over 3x
        if fast and not active_p: pages += 1; hits.append((m, 'PAGE')); active_p = True
        if fast: last_page = m
        if not fast: active_p = False
        if slow and m - last_page > 360 and not active_t: tickets += 1; hits.append((m, 'ticket')); active_t = True
        if not slow: active_t = False
    return pages, tickets, hits
p, t, hits = burn_alerts()
print('30 days, 3 real incidents (a 25 min spike, an 8 min outage, a 3 hour slow leak)')
print('alert on "CPU above 80%%": %d pages, almost none about a real user problem' % naive_alerts())
print('burn-rate alerts: %d pages and %d tickets' % (p, t))
for m, kind in hits: print('   minute %5d (day %.1f): %s' % (m, m / 1440, kind))
print()
tl = {'incident began': 0, 'alert fired': 4, 'acknowledged': 9, 'mitigated (rolled back)': 31, 'resolved (root cause fixed)': 180}
prev = 0
print('an incident timeline (minutes after the start):')
for k, v in tl.items(): print('   %4d  %s' % (v, k))
print('time to detect %d min, to acknowledge %d min, to mitigate %d min, to resolve %d min' % (tl['alert fired'], tl['acknowledged'] - tl['alert fired'], tl['mitigated (rolled back)'], tl['resolved (root cause fixed)']))
EOF''',
                     e="Why symptom and burn-rate alerts beat cause alerts. A threshold on CPU fires **237 times** in the month, while the three **real incidents** are a tiny part of what wakes anyone. The burn-rate rules fire **only for the three incidents**: the 25-minute spike and the 8-minute outage **page** within minutes (budget burning at a dangerous multiple on both a long and a short window), and the three-hour slow leak, which never burns fast enough to page, is caught by the slower rule as a **ticket** about two hours in. The incident timeline then shows the numbers worth reporting after the event: how long to detect, acknowledge, mitigate and resolve, and why **mitigating first** (a rollback in 31 minutes) matters more than the 180 minutes it took to fully fix the cause.",
                     annot=[("alert on \"CPU above 80%\": 237 pages", "cause-based alerts fire constantly and mostly do not matter"),
                            ("burn-rate alerts: 2 pages and 1 tickets", "only the three real incidents produce alerts: two pages, one ticket"),
                            ("time to detect 4 min, to acknowledge 5 min, to mitigate 31 min, to resolve 180 min", "the metrics to review: mitigate first, then resolve the cause")]),
            ]),
        ],
        scenario=dict(
            title="\"Our on-call gets paged 40 times a week and ignores most of it. How do you fix alerting?\"",
            ask="An operations maturity question. They want symptom-based alerts, burn rates, runbooks and a way to measure improvement.",
            clarify=[("What do the pages look like, which ones need action, and what are the SLOs?", "Count pages and the share that needed a human.")],
            think=[("Audit the pages.", "For each alert in the last month: did it need action? Was it a symptom users feel? Delete or downgrade the ones that did not."),
                   ("Alert on symptoms.", "Page on SLO burn (error rate and latency at the edge), not on causes like CPU; keep cause metrics on dashboards for diagnosis."),
                   ("Use burn rates with two windows.", "Fast burn pages, slow burn tickets, so urgency matches the time the budget has left."),
                   ("Make every page actionable.", "Each alert links to a dashboard and a runbook with first checks and mitigations."),
                   ("Reduce toil.", "Automate recurring fixes; group duplicates; silence during known maintenance."),
                   ("Measure.", "Pages per on-call shift, share actionable, time to acknowledge and mitigate, and incidents first reported by customers.")],
            answer=["\"I would start by auditing a month of pages: which ones needed a human, and which reflected something users felt. Alerts on causes like CPU get deleted or turned into dashboards. I would page on SLO burn instead: error rate and latency at the edge, using burn rates over two windows, so a fast burn pages and a slow burn opens a ticket.",
                    "Every page must be actionable with a link to a runbook and dashboards, recurring fixes get automated, and duplicates are grouped. I would track pages per shift, the share that were actionable, time to acknowledge and mitigate, and how many incidents customers noticed before we did, and review those numbers each month.\""],
            follow=[("What is a burn rate?", "The error ratio divided by the allowed error ratio: 1 would use exactly the whole budget over the window; 14 means it is gone in about two days."),
                    ("Why two windows?", "The long window proves the problem is real; the short one proves it is still happening, so alerts stop soon after recovery."),
                    ("What goes in a blameless postmortem?", "A timeline, impact, root causes in the system and process, what worked, and follow-up actions with owners and dates: no blaming individuals.")],
            slips=["Alerting on every possible cause.", "Pages with no runbook.", "Postmortems that name a person and have no follow-ups."],
        ),
        quick=[("What is the difference between a page and a ticket?", "A page needs action now (fast burn); a ticket can wait (slow burn)."), ("Why mitigate before finding the root cause?", "To stop user pain first; the investigation can continue safely afterwards."), ("What should a postmortem avoid?", "Blaming individuals: it should find system and process causes.")],
        traps=["Pages for things nobody can act on.", "No distinction between urgent and slow problems.", "Postmortems without owned follow-up actions."],
    ),
]

MODULE = dict(
    id="rp",
    deep=True,
    title="Reliability practice: SLOs, alerts and incidents",
    lead="Reliability as a measurable practice: SLIs and SLOs and the error budget as arithmetic you can run, then alerts that page only when users feel pain (burn rates over two windows against a noisy CPU alert), and the clock of an incident with the metrics worth reviewing.",
    time="4 to 5 hours",
    why=["Teams that run systems well agree on a number for reliability and alert on it. Teams that do not drown in noisy pages. These ideas appear in every operations and SRE interview."],
    outcomes=["Define SLI, SLO, SLA and the error budget and compute budgets in minutes and requests.", "Design burn-rate alerts with two windows and explain pages versus tickets.", "Run an incident with a timeline and a blameless postmortem."],
    before=["The designing for reliability module (S26) and the debugging method (S09) help. Python 3 runs the simulations, which are seeded and repeat exactly."],
    env=["Nothing to install beyond Python 3."],
    lessons=LESSONS,
    labs=[],
    cases=[],
    cheat=[["SLI", "a ratio of good events to all events, measured from the user's view"], ["SLO", "the target for an SLI over a window"], ["error budget", "1 - SLO: what you may spend; policy when it is spent"], ["SLA", "a customer contract, looser than the SLO"], ["burn rate", "error ratio divided by allowed error ratio"], ["two windows", "long to be sure, short to be current"], ["page vs ticket", "fast burn pages, slow burn tickets"], ["incident phases", "detect, acknowledge, mitigate, resolve, postmortem"], ["blameless postmortem", "system and process causes, owned follow-ups"]],
    interview_intro="Reference module behind the Systems Mastery chapter on reliability practice.",
    interview=[],
    selftest=[("What is an error budget?", "One minus the SLO.")],
    recall=[["SLO", "target over a window"]],
    sources=[
        dict(title="Google SRE book: Service Level Objectives", url="https://sre.google/sre-book/service-level-objectives/", use="SLIs, SLOs and SLAs", license="CC BY-NC-ND; read online", how="Link only"),
        dict(title="Google SRE workbook: Alerting on SLOs", url="https://sre.google/workbook/alerting-on-slos/", use="Burn-rate alerts with multiple windows", license="CC BY-NC-ND; read online", how="Link only"),
        dict(title="Google SRE book: Postmortem culture", url="https://sre.google/sre-book/postmortem-culture/", use="Blameless postmortems", license="CC BY-NC-ND; read online", how="Link only"),
    ],
    plan=["Run each simulation and change the SLO or the window sizes."],
)
