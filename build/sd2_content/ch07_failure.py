"""Chapter 7: When things fail (partial failure, idempotency, clocks, quorums and CAP, Raft, retries, breakers, 2PC vs sagas)."""
import sd2kit as k
from sd2 import scen

# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "A normal payment", "kind": "",
     "scene": lambda cx, cy, w: k.person(cx, cy - 46, 1.2) + k.scaled(k.server(cx - 52, cy + 22, "ShopKart") + k.cloud(cx + 56, cy + 18, "card network") + k.flow(cx - 22, cy + 18, cx + 22, cy + 18, "ok") + k.badge(cx, cy + 82, "paid once", "ok"), cx, cy + 22, .85),
     "caption": "The shop asks the card network to charge 50. The charge works and the reply comes back."},
    {"title": "A slow network", "kind": "bad",
     "scene": lambda cx, cy, w: k.person(cx, cy - 46, 1.2, "bad") + k.scaled(k.server(cx - 52, cy + 22, "ShopKart", "warn") + k.cloud(cx + 56, cy + 18, "card network", "ok") + k.flow(cx - 22, cy + 18, cx + 22, cy + 18, "ok") + k.badge(cx, cy + 82, "reply lost: timeout", "bad"), cx, cy + 22, .85),
     "caption": "The card was charged, but the reply was lost. The shop only sees a timeout, so it tries again."},
    {"title": "With a key", "kind": "ok",
     "scene": lambda cx, cy, w: k.person(cx, cy - 46, 1.2, "ok") + k.scaled(k.server(cx - 52, cy + 22, "ShopKart", "ok") + k.cloud(cx + 56, cy + 18, "card network", "ok") + k.flow(cx - 22, cy + 18, cx + 22, cy + 18, "ok") + k.badge(cx, cy + 82, "charged once", "ok"), cx, cy + 22, .85),
     "caption": "The retry carries the same key, so the network says \"already done\" and charges nothing more."},
], "ShopKart payments, three moments", "The same payment on a good day, on a bad network, and with an idempotency key.")

IDEA_FIG = k.figure(720, 226, [
    k.server(60, 70, "Shop app"),
    k.flow(90, 58, 232, 58, "acc", "charge 50"),
    k.flow(232, 82, 90, 82, "bad", "reply lost", dash=True),
    k.server(266, 70, "Payment API"),
    k.alert(410, 66, "timeout"),
    k.note(590, 12, "Same silence, three causes", "acc"),
    k.badge(590, 38, "request never arrived", "warn"),
    k.badge(590, 70, "charged, reply lost", "bad"),
    k.badge(590, 102, "still working, just slow", "warn"),
    k.badge(360, 156, "Fix: send an idempotency key, so a retry is recognised", "ok"),
    k.note(360, 196, "The server remembers the key and returns the first result instead of charging again.", ""),
], "A timeout means I do not know", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


HOW = [
    ("Make every retry safe, and polite",
     "A timeout does not mean the request failed. So give each request an **idempotency key**, a unique id the server remembers, so a repeat returns the first result. Then retry with a growing wait and a little random jitter, and stop retrying a service that is clearly down (a **circuit breaker**).",
     _small([k.server(40, 40, "app"), k.flow(70, 34, 190, 34, "acc", "pay, key K1"), k.flow(190, 58, 70, 58, "bad", "reply lost", dash=True), k.server(220, 44, "payments"),
             k.badge(470, 30, "first try: charge 50", "warn"), k.badge(500, 62, "retry with K1: no new charge", "ok"),
             k.note(320, 108, "The key and the result are stored for a day or so.", "")], "An idempotency key on a retry", h=122)),
    ("Order by cause, not by clock",
     "Clocks on different machines disagree by milliseconds or more. If you keep \"the write with the later timestamp\", a machine with a fast clock can make an older write win. Use **logical clocks** (counters that follow cause and effect) or version vectors, which also show when two writes truly conflicted.",
     _small([k.server(60, 40, "node A", "warn", "clock 5 s fast"), k.badge(210, 40, "X at 100, stamped 105", "bad"), k.server(360, 40, "node B", "", "clock right"), k.badge(510, 40, "Y at 102, stamped 102", "ok"),
             k.note(320, 112, "Last write wins by timestamp keeps X. The older write won.", "bad")], "A fast clock wins wrongly", h=124)),
    ("Agree by majority",
     "If data lives on N copies, a write that reaches W copies and a read that asks R copies always overlap when W plus R is bigger than N, so the read sees the newest write. When the network splits, you must choose: **refuse** some requests to stay correct (CP), or **answer** from both sides and merge later (AP). To pick one leader, systems like **Raft** need votes from a majority, so two leaders can never both win.",
     _small([k.database(60, 44, "n1", "ok"), k.database(140, 44, "n2", "ok"), k.database(220, 44, "n3", "ok"), k.database(300, 44, "n4", "bad"), k.database(380, 44, "n5", "bad"),
             k.badge(540, 44, "3 of 5: still a majority", "ok"),
             k.note(320, 108, "Two leaders would need the same node to vote twice.", "")], "A majority of five nodes", h=120)),
    ("Undo with a saga, instead of locking everyone",
     "A job that touches two services cannot use one database transaction. **Two-phase commit** asks everyone to prepare, then commit, but if the coordinator dies in between, the rows stay locked (blocked). A **saga** runs the steps one by one and, if one fails, runs an **undo step** (a compensation) for each earlier step.",
     _small([k.badge(90, 30, "book flight", "ok"), k.flow(140, 30, 200, 30, "ok"), k.badge(250, 30, "book hotel", "ok"), k.flow(298, 30, 360, 30, "bad"), k.badge(410, 30, "charge card", "bad"),
             k.badge(570, 30, "no locks held", "ok"), k.flow(380, 42, 296, 72, "warn"), k.badge(250, 80, "release room", "warn"), k.flow(204, 80, 140, 80, "warn"), k.badge(90, 80, "release seat", "warn"),
             k.badge(570, 80, "2PC can block", "bad"), k.note(320, 118, "Saga: every step has an undo. 2PC: locks held until the coordinator decides.", "")], "A saga undoing steps", h=132)),
]

DATA = dict(
    time="20 minutes",
    tagline="The network can lose a reply, clocks disagree, and machines die half way through a job. This chapter is about designing so that none of that hurts the customer.",
    story=dict(
        title="Tuesday afternoon, 40 double charges",
        paras=[
            "ShopKart now has queues, replicas and a cache, and most things work. Then a mobile network provider has a slow afternoon. Support starts getting emails: \"You charged my card twice.\" By evening there are 40 of them, each for the same order, each for 50.",
            "The cause is a single line of reasonable code. The shop calls the card network to charge the customer and waits 10 seconds. On a slow afternoon the card network **did** charge the card, but the reply got lost on the way back. The shop sees only a timeout, assumes failure, and tries again. The second request charges the card a second time.",
            "The shop could not know. A timeout means \"I do not know what happened\", and that is the heart of distributed systems: parts of a system fail separately, and the others cannot tell a failure from slowness. The rest of this chapter is the toolkit for living with that.",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: a timeout means I do not know",
        one="In a distributed system, **partial failure** is normal: one part can fail while the rest keeps going, and you often cannot tell a dead machine from a slow one. So you design every step to be safe to **repeat**, and every decision to survive a missing answer.",
        figure=IDEA_FIG,
        paras=[
            "Four ideas cover most of what goes wrong. **Repeat safely** (idempotency). **Never trust clocks** to order events. **Agree by majority**, so a split network cannot make two answers. And **do not hold locks across machines**: use steps that can be undone. The experiments below show each one in a few lines of code."]),
    how=HOW,
    try_intro=["Six experiments. First: the double charge, and the one-line fix. Then: why a fast clock loses a write, how many copies you must ask, and how a Raft cluster elects leaders until it loses its majority. Then: a retry storm against a down service, and a saga that undoes its steps."],
    **{"try": [("dd", 0, 0, 0, "The double charge, and the fix"),
               ("dd", 1, 0, 0, "A fast clock wins the wrong write"),
               ("dd", 2, 0, 0, "How many copies must you ask?"),
               ("dd", 3, 0, 0, "Electing leaders until the majority is gone"),
               ("dd", 4, 0, 0, "A retry storm, backoff and a breaker"),
               ("dd", 5, 0, 1, "A saga that undoes its steps")]},
    breaks=[
        ("Retry storms", "A service slows down, every client retries at once, and the extra load keeps it down. Fix: wait longer after each failure, add random jitter, cap the attempts, and let a circuit breaker stop calls to a service that is clearly failing.", "bad"),
        ("Clock skew", "Two machines disagree on the time, so \"latest\" is wrong, and an older write overwrites a newer one. Fix: order by version numbers or logical clocks, and treat wall clock time as a hint.", ""),
        ("Two leaders", "A network split lets two nodes both believe they lead, and each accepts writes. Fix: leadership requires a majority vote and a term number, and old leaders are fenced off.", "bad"),
        ("AP overdraft", "On a split network, an always-available bank account lets both sides pay out, and the cash is gone before the sides merge. Fix: for money use a CP choice (refuse without a quorum), and use AP only where a merge can repair things.", ""),
        ("Blocked 2PC", "The coordinator crashes after the prepare phase, and every bank is stuck holding locks, in doubt. Fix: avoid two-phase commit across services; use a saga with undo steps, and keep step handlers idempotent.", "bad"),
        ("Key reuse mistakes", "An idempotency key that is generated fresh on every retry protects nothing, and one that is shared by different orders blocks real payments. Fix: create the key once per intended action and reuse it on every retry of that action.", ""),
    ],
    real=[
        dict(company="Stripe", text="The Stripe API documentation describes **idempotency keys**: send the same key with a retry, and the API returns the saved result of the first request instead of performing the action again.", url="https://docs.stripe.com/api/idempotent_requests", source="Stripe API reference: idempotent requests"),
        dict(company="Raft", text="The Raft paper by Diego Ongaro and John Ousterhout describes a consensus algorithm designed to be easier to understand than Paxos, in which a leader is elected by a majority of the cluster.", url="https://raft.github.io/raft.pdf", source="In Search of an Understandable Consensus Algorithm (USENIX ATC 2014)"),
        dict(company="Amazon", text="The Amazon Builders' Library has written about timeouts, retries, and backoff with jitter, including why retries can make an overload worse and why they should be limited.", url="https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/", source="Amazon Builders' Library: Timeouts, retries and backoff with jitter"),
    ],
    interview=[dict(scenario=scen("dd", 0), who="A very common payments prompt: reported by candidates at large tech companies, not official."),
               dict(scenario=scen("dd", 2), who="A classic distributed systems question: reported by candidates, not official."),
               dict(scenario=scen("dd", 5), who="A frequent follow-up on cross-service consistency: reported by candidates, not official.")],
    interview_sub="Say your answer aloud first, then compare with the model answer. These are the shapes of question candidates report, not official company lists.",
    recap=dict(
        points=["A timeout means \"I do not know\": the work may or may not have happened.",
                "Idempotency keys make retries safe: the server returns the first result for a repeated key.",
                "Retry with growing waits, jitter and a cap, and use a circuit breaker so you stop hammering a failing service.",
                "Wall clocks lie: order events with counters or version vectors, not timestamps.",
                "With N copies, W plus R greater than N makes reads see the latest write; a split network forces a CP or AP choice.",
                "Raft elects one leader by majority; across services prefer a saga with undo steps to two-phase commit."],
        quick=[("The payment call times out. What do you do?", "Retry with the same idempotency key, so a repeated request cannot charge twice."),
               ("Why not order events by timestamp across servers?", "Clocks disagree, so an older write can look newer. Use logical clocks or version vectors."),
               ("Why prefer a saga to two-phase commit?", "2PC holds locks and can block if the coordinator dies; a saga runs steps one by one and undoes them if a later step fails.")]),
    deeper=[("Partial failure and idempotency", "S22_distributed_systems.html#l1"), ("Time and ordering", "S22_distributed_systems.html#l2"), ("Quorums and CAP", "S22_distributed_systems.html#l3"), ("Consensus and Raft", "S22_distributed_systems.html#l4"), ("Retries and circuit breakers", "S22_distributed_systems.html#l5"), ("Two-phase commit and sagas", "S22_distributed_systems.html#l6")],
)
