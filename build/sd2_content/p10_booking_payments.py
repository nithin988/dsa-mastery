"""Problem 10: Design booking and payments."""
import sd2kit as k
from sd2 import scen, figure_of

STRIP = k.strip([
    {"title": "Two buyers, one seat", "kind": "bad",
     "scene": lambda cx, cy, w: k.person(cx - 52, cy - 6, 1, "bad") + k.person(cx + 52, cy - 6, 1, "bad") + k.badge(cx, cy + 36, "seat 14C", "bad"),
     "caption": "Both check and see the seat is free. Both click buy. Both are told they got it."},
    {"title": "The database decides", "kind": "ok",
     "scene": lambda cx, cy, w: k.person(cx - 56, cy - 6, 1, "ok") + k.database(cx + 6, cy - 6, None, "ok") + k.person(cx + 62, cy - 6, 1, "warn") + k.badge(cx, cy + 36, "one wins", "ok"),
     "caption": "One atomic step: take the seat only if it is still free. The second buyer gets a polite no."},
    {"title": "Charged twice?", "kind": "warn",
     "scene": lambda cx, cy, w: k.phone(cx - 44, cy - 6, None, "warn") + k.clock(cx + 44, cy - 6, None, "warn") + k.badge(cx, cy + 40, "reply lost, retry", "warn"),
     "caption": "The payment reply is lost, so the app retries. A key makes the retry harmless."},
], "Never sell twice, never charge twice", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


DESIGN = k.figure(720, 260, [
    k.crowd(60, 48, 3, 22, .7), k.flow(120, 52, 180, 52, "acc", "admit slowly"),
    k.queue(230, 52, "waiting room", "acc"), k.flow(276, 52, 340, 52, "acc"),
    k.server(376, 52, "booking API", "acc"), k.flow(406, 52, 470, 52, "acc", "1 hold seat"),
    k.database(516, 50, "seats", "acc", "status, hold_until"),
    k.flow(376, 86, 376, 150, "ok", "2 pay (key)"),
    k.cloud(376, 176, "payment provider", "ok"),
    k.flow(410, 176, 480, 176, "ok", "3 success"),
    k.database(520, 176, "ledger + order", "ok", "one transaction"),
    k.note(360, 250, "Seats and money are decided by the database. Browsing is cached and may be slightly stale.", ""),
], "Booking and payments design", None)

DATA = dict(
    time="35 minutes",
    seen_at="The usual correctness focused design question",
    tagline="Two promises that are easy to say and hard to keep under load: never sell the same seat twice, never charge the same card twice.",
    story=dict(
        title="Two tickets for seat 14C",
        paras=[
            "ShopKart sells 500 tickets for a launch event. The booking code reads the seat, sees it is free, then marks it sold. At noon, two customers click within the same few milliseconds. Both read free, both write sold, and both receive a confirmation. At the door there is one seat and two angry people.",
            "A week later a different bug shows up. The payment provider is slow, the app times out and retries, and one customer is charged twice. The interviewer's question is the same one the team now has to answer: how do you design ticket booking so neither mistake can happen, even when a million people arrive at once?",
        ],
        strip=STRIP),
    requirements=["Functional: browse events and seat maps, hold seats while paying, pay, receive a ticket, refund. Non-functional: a seat is never sold twice, a customer is never charged twice, holds expire on their own, and the system survives a flash sale. Money correctness is more important than speed."],
    numbers=[
        ("The flash sale", "50,000 seats go on sale while 1 million people wait (the scenario's assumption). That is 20 buyers per seat, all arriving in the first minutes."),
        ("Reads versus writes", "Browsing the event and seat map is cacheable and can be a little stale. Writes concentrate on a few thousand hot rows, the seats. Read load is not the problem; contention is."),
        ("Holds", "A hold lasts 10 minutes. If 50,000 seats are held at once and a buyer needs about 2 minutes to pay, most holds are released early or expire. Holds must clean themselves up."),
        ("Payment calls", "If a tenth of the million reach payment, that is 100,000 payment calls in a few minutes. The provider is slow and sometimes unavailable, so every payment must survive a timeout."),
        ("Ledger arithmetic", "In the recorded run, one 4,999 cent order produces three balanced entries: -4,999, +4,900 and +99. They sum to zero, which is the check that no money appeared or vanished."),
    ],
    numbers_try=[],
    design_figure=DESIGN,
    design=[
        ("Let the database decide the seat", "Do not check in the application and then update. Use one statement: set the seat to held where its status is still available. The database runs it atomically, so exactly one buyer changes the row, and the other sees zero rows changed.",
         _small([k.person(60, 48, 1, "ok"), k.person(60, 96, 1, "warn"), k.flow(88, 48, 190, 60, "ok", "available? take"), k.database(236, 58, "seats", "acc"), k.flow(268, 58, 380, 58, "ok", "1 row changed"), k.badge(450, 40, "alice: got it", "ok"), k.badge(450, 76, "bob: sold out", "warn")], "Conditional update", h=124)),
        ("Hold the seat with an expiry", "The same update also writes hold_until, ten minutes ahead. The buyer now has time to pay. If they leave, the next reader or a sweeper job sees the expired hold and frees the seat. No manual clean up is needed.",
         _small([k.badge(90, 48, "available", "ok"), k.flow(140, 48, 220, 48, "acc", "hold"), k.badge(280, 48, "held until 12:10", "warn"), k.flow(350, 48, 430, 48, "ok", "paid"), k.badge(480, 48, "sold", "ok"), k.note(320, 94, "or: time runs out, back to available", "")], "Seat states")),
        ("Pay with an idempotency key", "Each payment attempt carries a unique key. The first request charges the card. A retry with the same key does not charge again; it replays the first answer. This turns the dangerous unknown timeout into a safe repeat.",
         _small([k.phone(60, 48, "client", "acc"), k.flow(88, 48, 190, 48, "acc", "pay, key K1"), k.server(226, 48, "payments", "acc"), k.flow(256, 48, 360, 48, "ok", "first: charge"), k.badge(430, 30, "txn-81", "ok"), k.badge(430, 64, "retry: replay", "warn")], "Idempotent payment")),
        ("Record money in a balanced ledger", "Confirmation writes the order, marks the seat sold and appends ledger entries in one database transaction. Every movement is a set of entries that sum to zero. Mistakes are fixed by adding reversing entries, never by editing history.",
         _small([k.badge(110, 24, "customer  -4999", "bad"), k.badge(110, 52, "merchant  +4900", "ok"), k.badge(110, 80, "fees  +99", "ok"), k.flow(200, 52, 300, 52, "acc", "sum"), k.badge(360, 52, "0", "ok"), k.note(520, 56, "every order balances", "")], "Ledger", h=116)),
    ],
    hard_title="The hard part: two services, one outcome",
    hard_paras=[
        "Seats live in your database; the card lives in the provider's system. You cannot wrap both in one transaction. Two phase commit would hold locks while waiting on an outside party and can block if the coordinator dies, so it is a poor fit. Use a saga: a chain of local steps (hold seat, charge card, confirm order), each with an undo (release seat, refund). If a step fails, run the undos for the steps already done.",
        "The sharpest case is a payment timeout, because the outcome is unknown: the card may or may not have been charged. Do not release the seat or confirm yet. Record the payment as pending, then settle it from the provider's webhook or status check. A reconciliation job compares your records with the provider's, and alerts on any holds or pending payments that stay stuck.",
    ],
    **{"try": [("ex", 2, 0, 0, "Overselling in a real database, then the conditional update"), ("ex", 2, 0, 1, "Retries replay one charge, and the ledger sums to zero"), ("dd", 5, 0, 1, "A saga that compensates when a step fails")]},
    scale=[
        ("A million people arrive at once", "A waiting room admits users at a steady rate so the database sees a trickle, not a spike. Browsing is served from cache with slightly stale seat counts; the decision itself is never stale.", ""),
        ("Hot event on one shard", "Shard by event so every seat decision for one event lives in one place with strong consistency. Add event level rate limits and keep transactions short.", ""),
        ("Provider times out", "Mark the payment pending and settle it later by webhook or status call. Webhooks must be idempotent too, as providers send them more than once.", "bad"),
        ("Stuck holds", "A hold that never resolves blocks a seat. The sweeper frees expired holds and an alert fires if the count of old pending payments grows.", ""),
        ("Bots and scalpers", "Rate limit per account and per payment method, use challenges in the waiting room, and cap seats per order.", "bad"),
    ],
    scenario=scen("ex", 2),
    who="A commonly reported correctness question: reported by candidates, not official.",
    real=[
        dict(company="Stripe", text="Stripe has written about **idempotency keys**: a client sends a unique key with a request, and the server returns the stored result for a repeated key instead of performing the action twice.", url="https://stripe.com/blog/idempotency", source="Stripe Blog: Designing robust and predictable APIs with idempotency"),
    ],
    recap=dict(
        points=["Let the database decide: one conditional update from available to held, never check then write.",
                "Holds carry an expiry, so abandoned seats free themselves.",
                "A waiting room turns a million arrivals into a steady trickle.",
                "An idempotency key makes payment retries safe: in the recorded run, 4 attempts and 1 charge.",
                "A balanced ledger sums to zero; fix mistakes with reversing entries.",
                "Seat plus payment is a saga with undo steps; a timeout means pending, not failed."],
        quick=[("Why is check then update unsafe?", "Two buyers can both see the seat free before either writes; the conditional update makes the check and the write one atomic step."),
               ("What does an idempotency key do?", "It lets the server recognise a retry and replay the first result instead of charging again."),
               ("Why not two phase commit with the payment provider?", "It holds locks across outside calls and can block on a coordinator failure; a saga with compensations avoids that.")]),
    deeper=[("Booking and payments, full lesson", "S29_media_files_streaming.html#l3"), ("Distributed transactions and sagas", "S22_distributed_systems.html#l6"), ("Partial failure and idempotency", "S22_distributed_systems.html#l1")],
)
