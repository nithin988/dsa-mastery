"""Problem 9: Design a notification system."""
import sd2kit as k
from sd2 import scen, figure_of

STRIP = k.strip([
    {"title": "1,000 pings", "kind": "bad",
     "scene": lambda cx, cy, w: k.phone(cx, cy - 20, None, "bad") + k.badge(cx - 52, cy - 52, "like", "bad") + k.badge(cx + 52, cy - 36, "like", "bad") + k.badge(cx - 52, cy + 10, "like", "bad") + k.badge(cx + 52, cy + 26, "like", "bad") + k.note(cx, cy + 62, "one photo, a thousand buzzes", "bad"),
     "caption": "A seller's photo goes popular. Every like sends a push, and the phone buzzes for ten minutes."},
    {"title": "Muted for good", "kind": "warn",
     "scene": lambda cx, cy, w: k.phone(cx, cy - 20, None, "warn") + k.badge(cx, cy + 36, "notifications off", "warn") + k.note(cx, cy + 66, "and the password reset?", "warn"),
     "caption": "The seller switches notifications off. Now even the important ones are lost."},
    {"title": "Collapsed and sorted", "kind": "ok",
     "scene": lambda cx, cy, w: k.phone(cx, cy - 20, None, "ok") + k.badge(cx, cy + 36, "user0 and 999 others", "ok") + k.note(cx, cy + 66, "urgent ones first", "ok"),
     "caption": "Likes merge into one line, quiet hours are respected, and security messages always go through."},
], "From noise to a sensible pipeline", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


DESIGN = k.figure(720, 200, [
    k.server(50, 60, "services"), k.flow(80, 60, 130, 60, "acc", "events"),
    k.queue(180, 60, "event queue", "", None, 3), k.flow(226, 60, 280, 60, "acc"),
    k.server(310, 60, "rules", "acc"), k.flow(340, 60, 395, 60, "acc"),
    k.cache(425, 60, "preferences", "ok"), k.flow(310, 90, 310, 130, "acc"),
    k.queue(310, 150, "priority queues", "", None, 2), k.flow(356, 150, 420, 150, "acc"),
    k.server(450, 150, "senders", "acc"), k.flow(480, 150, 540, 150, "acc", "retry"),
    k.cloud(580, 150, "push, email, SMS", "ok"), k.flow(450, 180, 380, 190, "bad", "", dash=True),
    k.badge(335, 192, "dead letters", "bad"),
], "Notification pipeline", None)

DATA = dict(
    time="30 minutes",
    seen_at="Reported for apps with push, email and SMS",
    tagline="Sending a notification is easy. The system is the part that decides whether to send, merges the noise, retries safely and never lets marketing delay a password reset.",
    story=dict(
        title="A photo that went popular",
        paras=[
            "ShopKart sellers want to know when someone likes their photo or buys something, so the team sends a phone push for every event. It is a loop that calls the push provider. It works for a month.",
            "Then one seller's photo takes off. Over ten minutes it collects 1,000 likes, so the phone buzzes 1,000 times and the seller turns notifications off for the whole app. The same week the email provider has an outage, and a backlog of retries delays a password reset by an hour. The loop needed rules, priorities and a way to give up gracefully.",
        ],
        strip=STRIP),
    requirements=["Functional: accept events from many services; decide who gets what on which channel (push, email, SMS); respect preferences, quiet hours and unsubscribe; retry failures; record what was sent. Non-functional: urgent messages arrive in seconds; low priority never blocks high priority; nothing is sent twice; the system survives a provider outage."],
    numbers=[
        ("Assumptions", "500 million users, 10 billion notifications a day, transactional ones within seconds, marketing within minutes. Confirm these."),
        ("Rate", "10 billion / 86,400 seconds is about **115,000 per second** on average, around 500,000 at peak."),
        ("A smaller service", "For 10 million emails a day: about **115 per second** on average, perhaps 1,000 at peak. With 100 ms per send and 50 concurrent senders, capacity is 500 per second, so a queue must smooth the peak."),
        ("Cost", "The provider call dominates cost, especially SMS. Collapsing and caps save money as well as annoyance."),
        ("Presence", "Do not send a push to someone actively in the app. A short lived 'online' key per user answers that question cheaply."),
    ],
    numbers_try=[("fd", 2, 0, 1, "1,000 likes, quiet hours and a per user limit")],
    design_figure=DESIGN,
    design=[
        ("Events go on a queue, never straight to a provider", "Services publish events like 'order shipped' or 'like received'. The notification service reads them from a queue, so a spike waits in line instead of overwhelming the senders.",
         _small([k.server(60, 48, "orders"), k.server(150, 48, "social"), k.flow(180, 48, 260, 48, "acc", "events"), k.queue(320, 48, "queue", "", None, 3), k.flow(366, 48, 440, 48, "acc"), k.server(480, 48, "notifier", "acc"), k.note(580, 52, "spikes wait in line", "acc")], "Event intake")),
        ("Rules decide whether, when and where", "A rules step checks the user's channel choices, quiet hours, frequency cap and consent. Repeated events with the same user, type and object inside a window are merged into one, like '1,000 likes' becoming a single line.",
         _small([k.badge(70, 48, "1,000 likes", "bad"), k.flow(120, 48, 190, 48, "acc"), k.server(230, 48, "rules", "acc"), k.flow(260, 48, 340, 48, "ok", "merge"), k.badge(430, 48, "user0 and 999 others", "ok"), k.note(580, 52, "plus quiet hours", "acc")], "Rules and collapsing")),
        ("Separate lanes for urgent and casual", "Each priority has its own queue and its own workers. A password reset sits in the fast lane, and a newsletter in a slow lane that is rate limited. When the system is busy, the casual lane waits first.",
         _small([k.queue(120, 36, "urgent", "bad", None, 1), k.queue(120, 84, "marketing", "warn", None, 4), k.flow(166, 36, 300, 36, "ok", "many workers"), k.flow(166, 84, 300, 84, "warn", "few workers", dash=True), k.cloud(380, 60, "providers", "acc"), k.note(540, 64, "newsletters never delay resets", "acc")], "Priority lanes", h=124)),
        ("Retry with care, then give up loudly", "A failed send is retried after a growing, jittered delay, with an idempotency key so a retry cannot double send. A message that keeps failing, such as a malformed address, moves to a dead letter queue where a person can inspect it.",
         _small([k.server(60, 48, "sender"), k.flow(90, 48, 180, 48, "warn", "fail, wait"), k.clock(210, 44, None, "warn"), k.flow(236, 48, 320, 48, "warn", "try again"), k.cloud(370, 48, "provider", "acc"), k.flow(400, 48, 490, 48, "bad", "4 failures", dash=True), k.queue(540, 48, "dead letters", "bad", None, 1)], "Retries and dead letters")),
    ],
    hard_title="The hard part: not annoying people, and not falling over",
    hard_paras=[
        "Two things make notifications hard. The first is volume you did not ask for: collapse repeats, cap per user, and hold low priority messages for quiet hours. The second is failure: providers are slow or down, so retries, back pressure and priority lanes keep the important messages moving.",
        "Presence is a small trick worth knowing. A user's 'online' key expires on its own a few seconds after the heartbeats stop, so nobody has to clean up. The experiments below show the retry and dead letter flow, then presence.",
    ],
    **{"try": [("qs", 4, 0, 1, "Retry with backoff, then the dead letter queue"), ("qs", 4, 0, 2, "A bounded queue protects the workers"), ("fd", 2, 0, 0, "Presence that expires by itself")]},
    scale=[
        ("A provider is down", "Open a circuit breaker so workers stop hammering it, switch to a second provider where you have one, and let the queue hold the rest.", ""),
        ("Retry storms", "Without jitter, thousands of retries land at the same moment and knock the provider over again. Add random delay and a cap on attempts.", "bad"),
        ("Duplicate sends", "A worker crashes after sending but before recording it. Use an idempotency key so the retry is recognised and skipped.", ""),
        ("Dead tokens", "Push tokens go stale when people uninstall. Remove tokens the provider rejects so you stop paying to send into the void.", ""),
        ("Compliance", "Honour unsubscribe and SMS consent instantly, and keep an audit trail of what was sent and why.", "ok"),
    ],
    scenario=scen("fd", 2),
    who="A pipeline design question: reported by candidates, not official.",
    real=[
        dict(company="Amazon Web Services", text="The Amazon SQS documentation describes dead letter queues as a place to move messages that could not be processed successfully after a set number of receive attempts, so they can be inspected.", url="https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html", source="AWS docs: SQS dead letter queues"),
        dict(company="Redis", text="The Redis documentation describes setting an expiry on a key so it is deleted automatically, which is the basis of the presence trick used here.", url="https://redis.io/docs/latest/commands/expire/", source="Redis docs: EXPIRE"),
    ],
    recap=dict(
        points=["Put events on a queue, so spikes wait instead of crashing senders.",
                "Rules step: preferences, quiet hours, frequency caps, consent.",
                "Collapse repeats: 1,000 likes become one notification.",
                "Priority lanes so urgent messages never wait behind marketing.",
                "Retry with backoff and jitter, with an idempotency key, then dead letter.",
                "Presence is a key with an expiry, refreshed by heartbeats."],
        quick=[("Why collapse notifications?", "Repeated events annoy people and cost money. In the experiment 999 likes merged into one push."),
               ("What is a dead letter queue?", "A holding place for messages that keep failing, so they stop blocking the queue and a person can inspect them."),
               ("Why add jitter to retry delays?", "So many failed messages do not all retry at the same instant and overload the provider again.")]),
    deeper=[("Presence and notifications, full lesson", "S28_feeds_chat_notifications.html#l3"), ("Retries, dead letters and back pressure", "S20_queues_streams_async.html#l5"), ("Queues and async work", "S20_queues_streams_async.html#l1")],
)
