"""Chapter 8: Keep it up (reliability and operations)."""
import sd2kit as k
from sd2 import scen

# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "3:00 p.m.", "kind": "warn",
     "scene": lambda cx, cy, w: k.crowd(cx, cy - 52, 4, 26, .75, "warn") + k.scaled(k.server(cx - 40, cy + 22, "checkout v2", "warn") + k.badge(cx + 40, cy + 22, "100%", "warn"), cx, cy + 22, .9),
     "caption": "A new checkout goes to every customer at once. Within minutes, orders start failing."},
    {"title": "3:00 a.m.", "kind": "bad",
     "scene": lambda cx, cy, w: k.scaled(k.server(cx - 46, cy + 22, "web", "ok") + k.database(cx + 46, cy + 22, "database", "bad") + k.flow(cx - 14, cy + 22, cx + 18, cy + 22, "bad"), cx, cy + 22, .9) + k.alert(cx, cy - 52, None),
     "caption": "The only database host dies. The pager wakes one tired engineer. Orders stop for almost an hour."},
    {"title": "Built to survive", "kind": "ok",
     "scene": lambda cx, cy, w: k.scaled(k.balancer(cx - 70, cy + 22, None, "ok") + k.server(cx, cy - 6, None, "ok") + k.server(cx, cy + 52, None, "ok") + k.flow(cx - 44, cy + 14, cx - 32, cy - 2, "ok") + k.flow(cx - 44, cy + 30, cx - 32, cy + 48, "ok") + k.database(cx + 70, cy + 22, None, "ok"), cx, cy + 22, .74),
     "caption": "Two of everything, small rollouts, a spare database. A failure becomes a quiet log line."},
], "ShopKart's two worst days", "A release that hurt everyone, and a machine that died alone: both fixed with design, not luck.")

IDEA_FIG = k.figure(720, 270, [
    k.person(50, 100, 1.25), k.note(50, 150, "Customers"),
    k.flow(84, 100, 130, 100, "acc"),
    k.balancer(160, 100, "Load balancer", "ok"),
    '<rect class="sd-panel ok" x="250" y="12" width="300" height="108" rx="10"/>',
    '<rect class="sd-panel ok" x="250" y="126" width="300" height="108" rx="10"/>',
    k.note(262, 30, "Zone A", "ok", "start"), k.note(262, 144, "Zone B", "ok", "start"),
    k.server(310, 66, "app 1", "ok"), k.database(450, 66, "database", "ok"),
    k.server(310, 182, "app 2", "ok"), k.database(450, 182, "copy", "ok"),
    k.flow(182, 84, 280, 62, "ok"), k.flow(182, 118, 280, 178, "ok"),
    k.flow(342, 66, 424, 66, "ok"), k.flow(342, 182, 424, 182, "ok"),
    '<path class="sd-a ok dash" d="M500,70 V176" fill="none" marker-end="url(#dga)"/>',
    k.note(630, 126, "copies stay in step", "ok"),
    k.badge(630, 80, "Zone A dies", "bad"), k.badge(630, 176, "Zone B serves", "ok"),
    k.note(360, 258, "No single machine, and no single zone, can take the shop down.", ""),
], "Two copies in two zones behind a load balancer", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


HOW = [
    ("Count the nines, then spread the blast radius",
     "Availability is the share of time you work: 99.9% allows 43.2 minutes of downtime in a 30-day month, 99.99% allows only 4.3. A **failure domain** is the set of things that die together (one machine, one rack, one zone), so keep copies in different domains.",
     _small([k.badge(80, 44, "99.9%", "warn"), k.note(80, 76, "43.2 min a month", "warn"), k.badge(240, 44, "99.99%", "ok"), k.note(240, 76, "4.3 min a month", "ok"),
             k.cloud(400, 40, "zone A", "bad"), k.cloud(540, 40, "zone B", "ok"), k.flow(436, 40, 500, 40, "ok", "survives", dash=True)], "Nines and failure domains", h=104)),
    ("Restart, fail over, degrade",
     "A **supervisor** restarts a crashed process after a short wait that grows each time. A load balancer **fails over** by skipping a dead server and retrying on another. When an optional part such as recommendations is down, **degrade gracefully**: show the page without it.",
     _small([k.server(60, 44, "crashed", "bad"), k.flow(90, 44, 190, 44, "warn", "restart in 1s, 2s..."), k.server(226, 44, "back", "ok"), k.balancer(380, 44, None, "ok"), k.flow(406, 36, 500, 24, "ok"), k.server(530, 24, "b", "ok"),
             k.flow(406, 52, 500, 70, "bad", dash=True), k.badge(560, 76, "skipped", "bad")], "Supervisor and failover", h=118)),
    ("Release to a few, with a switch to undo",
     "A **canary release** sends a small share (say 5%) of traffic to the new version and compares its errors with the old one. If it is worse, roll back automatically. A **feature flag** hides new code behind a switch, so you turn it on for some users and off in seconds without a redeploy.",
     _small([k.balancer(60, 44, None, "acc"), k.flow(86, 36, 190, 24, "ok", "95%"), k.server(226, 24, "stable", "ok"), k.flow(86, 52, 190, 70, "warn", "5%"), k.server(226, 74, "canary", "warn"),
             k.badge(380, 44, "errors 33% vs 1%", "bad"), k.flow(450, 44, 500, 44, "bad"), k.badge(560, 44, "ROLL BACK", "bad")], "Canary and rollback", h=124)),
    ("Measure, so you notice before customers do",
     "**Metrics** are numbers over time (request rate, error ratio, latency percentiles). **Logs** are the events. A **trace** follows one request id across services. Alert on the slowest 1% (p99), not the average, which hides the pain.",
     _small([k.gauge(60, 56, 96, "errors", "bad"), k.badge(190, 44, "avg 35 ms", "ok"), k.badge(190, 76, "p99 2.5 s", "bad"), k.note(190, 104, "the average hides it", "bad"),
             k.server(340, 44, "api", "ok"), k.flow(368, 44, 450, 44, "warn", "req-3, 601 ms"), k.server(490, 44, "inventory", "bad"), k.note(580, 48, "look here", "bad")], "Metrics and tracing", h=120)),
]

DATA = dict(
    time="18 minutes",
    tagline="How to make a system that keeps working while parts of it break, parts of it are being changed, and far too many people show up at once.",
    story=dict(
        title="A bad release at 3 p.m. and a dead server at 3 a.m.",
        paras=[
            "ShopKart has grown up. After the cache from chapter 3 and the retries from chapter 7, the shop is fast and mostly correct. But on a Tuesday at 3 p.m. the team ships a redesigned checkout to **all customers at once**. Twenty minutes later, support is flooded: some payments fail, and nobody can say why.",
            "They roll back by hand and lose about an hour. Three nights later, at 3 a.m., the one machine running the database dies. The pager wakes the only engineer on call. Restoring service takes almost an hour of lost orders, plus the cost of the shop being dark in the middle of a sale.",
            "Neither day was caused by a clever attack or a rare bug. One change reached everyone before anyone knew whether it was safe, and one machine could take down the business. **Reliability is designing so that normal failures and normal mistakes stay small.**",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: assume it will fail, and make failure small",
        one="**Reliability** means the system keeps doing its job even when parts fail. You get it by removing single points of failure, by changing things a little at a time, and by being able to see what is wrong and undo it quickly.",
        figure=IDEA_FIG,
        paras=["Every extra nine costs more. Two independent copies of a 99.9% service give 99.9999% on paper, but only if the copies fail separately: two copies in one zone die together when the zone does, and the real figure falls back to about 99.9%. So the design question is always: what fails together, and what happens next?"]),
    how=HOW,
    try_intro=["Three experiments. First: the arithmetic of the nines, including the trap of copies that fail together. Then: a canary that decides to roll back by itself. Then: what an overloaded service does with and without load shedding."],
    **{"try": [("rd", 0, 0, 1, "The nines, and copies that fail together"), ("rd", 2, 0, 0, "A canary that rolls itself back"), ("rd", 4, 0, 1, "Overload: shed load or collapse")]},
    breaks=[
        ("Counting copies that are not independent", "Two servers behind one load balancer, in one zone, on one power feed, do not multiply availability. Fix: put copies in different failure domains, and list what they share (zone, database, config, deploy).", "bad"),
        ("A weak link in the chain", "Components in a chain multiply: three parts at 99.9% each give 99.7%. In the recorded example a single database at 99.95% was the weakest link, costing 316 minutes a year; a second copy cut that to 53 minutes.", ""),
        ("Ship to everyone at once", "A bug that reaches every user is an outage. Fix: canary at 5%, compare errors with the stable version, roll back automatically, and put risky changes behind a feature flag with a kill switch.", "bad"),
        ("A dependency that drags you down", "An optional service (recommendations) fails and the whole page fails with it. Fix: timeouts, fallbacks, and a stale or empty answer. In the recorded run the critical design served 713 of 1000 pages; the graceful one served all 1000.", ""),
        ("Backups nobody has restored", "A backup that was never tested may be broken and you find out in the disaster. Fix: restore automatically on a schedule, and measure restore time, because that is your real recovery time.", "bad"),
        ("Overload turns into collapse", "When load exceeds capacity, queues grow, clients time out, and the work done is wasted. Fix: reject early with a clear error (load shedding), keep queues short, and let clients back off.", ""),
    ],
    real=[
        dict(company="Google", text="The SRE book describes **error budgets**: pick a reliability target, treat the allowed failure as a budget, and slow down releases when it is spent, so reliability and speed of change are balanced by a number, not an argument.", url="https://sre.google/sre-book/embracing-risk/", source="Google SRE Book: Embracing Risk"),
        dict(company="Netflix", text="Netflix open-sourced **Chaos Monkey**, a tool that deliberately terminates instances in production so teams build services that survive losing a machine.", url="https://github.com/Netflix/chaosmonkey", source="Netflix/chaosmonkey on GitHub"),
    ],
    interview=[dict(scenario=scen("rd", 0), who="A common reliability prompt: reported by candidates at large tech companies, not official."),
               dict(scenario=scen("rd", 2), who="A frequent operations question for senior roles: reported by candidates, not official."),
               dict(scenario=scen("rd", 4), who="A common closing question about disasters and traffic spikes: reported by candidates, not official.")],
    interview_sub="Say your answer aloud first, then compare with the model answer. These are the shapes of question candidates report, not official lists.",
    recap=dict(
        points=["Availability is time: 99.9% is 43.2 minutes a month, 99.99% is 4.3 minutes.",
                "Chains multiply and lower availability; independent copies raise it. Shared failure domains break the maths.",
                "Supervisors restart, load balancers fail over, and optional features degrade instead of failing the page.",
                "Release to 5% first, compare errors, roll back automatically, and keep a flag as a kill switch.",
                "Watch p99 and follow a request id across services; the average hides the pain.",
                "Restore your backups on purpose, and shed load before overload collapses you."],
        quick=[("What does 99.99% allow per month?", "About 4.3 minutes of downtime in a 30-day month."),
               ("Why is a canary better than testing alone?", "It exercises the new version on real traffic at small scale, with an automatic decision to roll back if errors rise."),
               ("What is load shedding?", "Rejecting some requests early so the rest are served well, instead of queueing everything until all of it times out.")]),
    deeper=[("Availability arithmetic and failure domains", "S26_designing_for_reliability.html#l1"), ("Supervisors, failover and degradation", "S26_designing_for_reliability.html#l2"), ("Canaries, rollbacks and flags", "S26_designing_for_reliability.html#l3"), ("Observability", "S26_designing_for_reliability.html#l4"), ("Disaster recovery and overload", "S26_designing_for_reliability.html#l5")],
)
