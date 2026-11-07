"""Chapter 6: Do not make people wait (queues, delivery guarantees, outbox, logs, retries, dead letters, back-pressure)."""
import sd2kit as k
from sd2 import scen

# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "Signup today", "kind": "",
     "scene": lambda cx, cy, w: k.person(cx, cy - 46, 1.2) + k.scaled(k.server(cx - 56, cy + 22, "web") + k.cloud(cx + 56, cy + 18, "email, photos") + k.flow(cx - 26, cy + 22, cx + 22, cy + 22, "warn") + k.badge(cx, cy + 82, "4 seconds", "warn"), cx, cy + 22, .85),
     "caption": "The customer waits while the server sends an email and resizes a photo. It takes four seconds."},
    {"title": "Launch spike", "kind": "bad",
     "scene": lambda cx, cy, w: k.crowd(cx, cy - 52, 5, 24, .72, "bad") + k.scaled(k.server(cx - 56, cy + 22, "web", "bad") + k.cloud(cx + 56, cy + 18, "email, photos", "warn") + k.flow(cx - 26, cy + 22, cx + 22, cy + 22, "bad") + k.badge(cx, cy + 82, "all workers busy", "bad"), cx, cy + 22, .85),
     "caption": "200 signups arrive in one second. All 20 workers are stuck waiting. New visitors get errors."},
    {"title": "With a queue", "kind": "ok",
     "scene": lambda cx, cy, w: k.crowd(cx, cy - 52, 5, 24, .72, "ok") + k.scaled(k.server(cx - 66, cy + 22, "web", "ok") + k.queue(cx, cy + 22, "queue", "ok", None, 3) + k.server(cx + 66, cy + 22, "worker", "ok") + k.flow(cx - 40, cy + 22, cx - 50, cy + 22, "ok"), cx, cy + 22, .62),
     "caption": "The server saves the signup, drops a job in the queue and answers at once. Workers catch up."},
], "ShopKart signup, three moments", "The same signup before the spike, during it, and after the slow work moved behind a queue.")

IDEA_FIG = k.figure(720, 236, [
    k.person(50, 80, 1.2), k.note(50, 120, "Customer"),
    k.flow(80, 80, 120, 80, "acc"),
    k.server(150, 78, "Web server"),
    k.flow(180, 78, 262, 78, "acc", "1. add a job"),
    k.queue(310, 78, "Queue", "", "jobs wait here", 3),
    k.flow(356, 78, 440, 78, "ok", "3. take one"),
    k.server(480, 78, "Worker"),
    k.flow(510, 78, 586, 78, "ok", "slow work"),
    k.cloud(620, 76, "Email, photos"),
    '<path class="sd-a ok" d="M150,48 V22 H50 V58" fill="none" marker-end="url(#dga)"/>',
    k.note(100, 14, "2. reply at once: welcome!", "ok"),
    k.badge(150, 168, "customer waits ~25 ms", "ok"),
    k.badge(310, 168, "queue absorbs the spike", "acc"),
    k.badge(500, 168, "workers go at their own pace", "warn"),
    k.note(360, 214, "The queue is a buffer between a fast front door and slow work.", ""),
], "A queue between the fast request and the slow work", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


HOW = [
    ("Put slow work behind a queue",
     "Do only what the customer must wait for (save the signup), then put a **job** describing the rest into a **queue**: a line of messages waiting to be handled. A separate **worker** program takes jobs off the line and does the slow work.",
     _small([k.server(60, 44, "web"), k.flow(90, 44, 190, 44, "acc", "save, then enqueue"), k.queue(236, 44, "queue", "", None, 3),
             k.flow(282, 44, 372, 44, "ok", "worker takes one"), k.server(410, 44, "worker"), k.note(560, 48, "email, resize photo", "ok"),
             k.note(320, 104, "The customer is already looking at the next page.", "")], "A web server queueing a job", h=116)),
    ("Expect every message to arrive at least once",
     "Networks fail, so a queue must choose: **at most once** (can lose a job) or **at least once** (can deliver a job twice). Real systems choose at least once, and make the handler **idempotent**, meaning that doing it twice has the same effect as doing it once. That is what \"exactly once\" really means in practice.",
     _small([k.badge(110, 38, "at most once: can lose", "bad"), k.badge(360, 38, "at least once: can repeat", "warn"), k.badge(560, 38, "+ idempotent: safe", "ok"),
             k.note(320, 92, "At least once plus a handler that ignores repeats gives safe, effectively once.", "")], "Delivery guarantees", h=108)),
    ("Never lose the event: use an outbox",
     "Saving an order and then publishing an event are two steps, and a crash between them loses the event. The **outbox pattern** writes the order and the event into the same database transaction, and a small **relay** program publishes unsent events afterwards. It may publish one twice, so consumers must ignore repeats.",
     _small([k.database(60, 44, "order + outbox"), k.flow(112, 44, 262, 44, "acc", "relay reads unsent"), k.server(290, 44, "relay"),
             k.flow(320, 44, 438, 44, "acc", "publish, then mark"), k.queue(490, 44, "broker", "", None, 2),
             k.note(320, 112, "If the relay dies mid-way it publishes again. Consumers deduplicate.", "warn")], "The outbox pattern", h=124)),
    ("Retry gently, park the poison, push back",
     "A failed job is retried after a wait that grows each time (**backoff**). A job that keeps failing, such as a malformed message, moves to a **dead-letter queue** so it stops blocking everyone, and a person looks at it later. If jobs arrive faster than workers can finish, a **bounded** queue says \"not now\" (**back-pressure**) instead of growing without end.",
     _small([k.queue(60, 44, "queue", "", None, 3), k.flow(106, 44, 200, 44, "warn", "fail, wait, retry"), k.server(236, 44, "worker", "warn"),
             k.flow(266, 44, 360, 44, "bad", "failed 4 times"), k.queue(406, 44, "dead letters", "bad", None, 1), k.badge(556, 44, "queue full: say no", "warn"),
             k.note(320, 104, "Retries are spaced out and capped. Dead letters get a human.", "")], "Retries, dead letters and back-pressure", h=116)),
]

DATA = dict(
    time="18 minutes",
    tagline="How to stop making customers wait for slow work: put it behind a queue, and then learn the rules that keep a queue honest (repeats, lost events, retries and overflow).",
    story=dict(
        title="Launch day, 11:00 a.m.",
        paras=[
            "ShopKart's marketing team sends the big launch email at 11:00. Signup has always worked the same way: save the account (0.3 seconds), send a welcome email through a mail provider (1.5 seconds), then resize the profile photo into three sizes (2.2 seconds). Total: four seconds, with the customer staring at a spinner.",
            "Four seconds was fine at ten signups an hour. But the web tier has 20 workers, and each one is stuck for four seconds per signup, so the shop can finish only **5 signups a second** (20 workers divided by 4 seconds). Marketing's email brings 200 signups in the first second. Within moments every worker is busy, browsing visitors cannot get a free one, and the whole site returns errors.",
            "The customer never needed the email or the resized photo **before** seeing the next page. Only the saved account is urgent. The fix is to write down the slow work as a list of jobs and let someone else do it a few seconds later.",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: write the job down, do it later",
        one="A **queue** is a line of messages between the part that asks for work and the part that does it, so the fast side never waits for the slow side.",
        figure=IDEA_FIG,
        paras=[
            "A queue does three jobs. It makes the customer's wait short, it **absorbs a spike** (the line gets long for a minute and then shrinks), and it **separates** the two sides, so a slow or broken email provider no longer breaks signup. The price is that work now happens later, can happen twice, and needs watching.",
            "A plain queue deletes a message once it is handled. A **log** (the Kafka model) keeps messages in order and lets each team read at its own pace. Each team is a **consumer group** with its own bookmark, so billing and analytics can both read every order, and a new team can **replay** history from the start. Inside a group, the work is shared out between the consumers."],
    ),
    how=HOW,
    try_intro=["Five experiments on a real queue (Redis) and a real database. First: a burst of 200 jobs and how the queue drains. Then: what a crash does to each delivery guarantee, the lost event and its fix, how a bad message is retried and parked, and what a full queue does."],
    **{"try": [("qs", 0, 0, 1, "A spike of 200 jobs, absorbed"),
               ("qs", 1, 0, 0, "Lose it, repeat it, or make it safe"),
               ("qs", 2, 0, 0, "The lost event, and the outbox"),
               ("qs", 4, 0, 1, "A bad message: retry, then dead letter"),
               ("qs", 4, 0, 2, "A full queue: back-pressure")]},
    breaks=[
        ("Duplicate work", "A worker finishes the job but crashes before it confirms, so the queue hands the job out again, and the customer gets two emails or two charges. Fix: make handlers idempotent, for example by recording the job id before acting.", "bad"),
        ("Lost events", "The database save succeeds, the publish fails, and nothing downstream hears about the order. Fix: the outbox pattern, so the event is saved with the order.", "bad"),
        ("Poison messages", "One malformed job fails forever and is retried forever, blocking the line behind it. Fix: cap the retries, then move it to a dead-letter queue and alert someone.", ""),
        ("Retry storms", "A struggling email provider makes every job fail, and instant retries multiply the traffic. Fix: backoff with random jitter, a retry cap, and a circuit breaker (chapter 7).", ""),
        ("Unbounded queues", "A queue that grows without limit hides the problem, and a new job ends up waiting minutes. Fix: bound the queue, add workers or shed load, and alert on queue depth and age.", "bad"),
        ("Out of order", "Two workers handle events for the same account at once, so an update is applied before the create. Fix: route by key (the account id) so one account's events go to one worker in order.", ""),
    ],
    real=[
        dict(company="Amazon", text="The documentation for Amazon SQS standard queues describes **at-least-once delivery**: a message is delivered at least once, and occasionally more than once, so applications should be designed to cope with duplicates.", url="https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues.html", source="Amazon SQS Developer Guide: standard queues"),
        dict(company="Apache Kafka", text="The Kafka documentation describes topics split into **partitions**, with **consumer groups** where each partition is read by one consumer of the group. Messages in a partition keep their order and stay available to be read again.", url="https://kafka.apache.org/documentation/", source="Apache Kafka documentation"),
    ],
    interview=[dict(scenario=scen("qs", 0), who="A common prompt about queues: reported by candidates at large tech companies, not official."),
               dict(scenario=scen("qs", 1), who="A frequent probing question on delivery guarantees: reported by candidates, not official."),
               dict(scenario=scen("qs", 4), who="A frequent notification service deep dive: reported by candidates, not official.")],
    interview_sub="Say your answer aloud first, then compare with the model answer. These are the shapes of question candidates report, not official company lists.",
    recap=dict(
        points=["Do only the urgent work before replying; queue the rest as jobs for workers.",
                "A queue absorbs spikes and separates fast code from slow or unreliable code.",
                "Choose at least once delivery and make handlers idempotent: that is practical exactly once.",
                "Save the event with the order (outbox) so a crash cannot lose it.",
                "Use a log with consumer groups when many teams read the same events and may replay them.",
                "Cap retries with backoff, send poison messages to a dead-letter queue, and bound the queue."],
        quick=[("Why can a queue deliver a job twice?", "A worker can finish and crash before confirming, so the queue gives the job to someone else. Handlers must be idempotent."),
               ("What problem does the outbox pattern solve?", "Saving the data and publishing the event are two steps; the outbox saves the event in the same transaction so a crash cannot lose it."),
               ("What is a dead-letter queue for?", "To park a job that keeps failing so it stops blocking the line, until a person can look at it.")]),
    deeper=[("Why queues", "S20_queues_streams_async.html#l1"), ("Delivery guarantees", "S20_queues_streams_async.html#l2"), ("The outbox pattern", "S20_queues_streams_async.html#l3"), ("Logs and consumer groups", "S20_queues_streams_async.html#l4"), ("Retries, dead letters, back-pressure", "S20_queues_streams_async.html#l5"), ("Choosing and sizing", "S20_queues_streams_async.html#l6")],
)
