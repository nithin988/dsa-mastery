"""S28 feeds, chat and notifications: part B (lesson 3: presence and notifications) and the module tail."""
import sysviz as v

PRES_VIZ = v.figure(
    720, 214,
    [v.box(10, 70, 130, 56, "Client", "ink", "heartbeat every 5 s"),
     v.arrow(140, 98, 190, 98), v.box(190, 70, 170, 56, "Presence store", "ok", "key with a 15 s expiry"),
     v.arrow(360, 98, 410, 98), v.box(410, 70, 150, 56, "Watchers", "acc", "friends who are online"),
     v.box(590, 40, 120, 56, "Crash?", "bad", "heartbeats stop"),
     v.box(590, 110, 120, 56, "Expiry", "warn", "offline after 15 s"),
     v.text(360, 168, "Presence is soft state: refreshed by heartbeats, forgotten by timeouts, never the source of truth.", "dg-s"),
     v.text(360, 194, "Tell only people who are looking: fan-out on presence changes is the expensive part.", "dg-s")],
    "Presence with heartbeats and expiry", "A user is online if a heartbeat arrived recently: no explicit logout needed")

LESSONS_B = [
    dict(
        title="Presence and notifications: soft state, heartbeats and not annoying people",
        tier="core",
        situation="The green dot next to a friend's name seems trivial, but a billion users each with hundreds of contacts turns it into a fan-out problem. Notifications have the opposite problem: it is easy to send too many. Both are about doing less, cleverly.",
        learn=["Presence with heartbeats and expiring keys", "Why presence fan-out is the real cost and how to limit it", "Notification pipelines: priority, deduplication, collapsing and quiet hours", "Push channels and their limits"],
        model=[
            "**Presence** is **soft state**: it is recomputed continuously and is wrong or missing without harm. Clients send a **heartbeat** every few seconds; the server stores `online:{user}` with a **short expiry** (for example 15 seconds) in a fast store, so a crashed phone simply stops refreshing and goes offline when the key expires: no explicit logout and no cleanup job. The expensive part is **telling others**: if every status change is broadcast to every contact, a user with 500 contacts flapping online and offline generates enormous traffic. Reduce it by notifying **only people who are currently watching** (subscribed to that user, for example with a chat open), **batching and throttling** updates, using **pull** on demand for big contact lists, and treating presence as approximate (\"last seen recently\").",
            "**Notifications** (push, email, SMS, in-app) are produced by events and delivered through a pipeline: **rules** decide whether and how to notify, a **preference store** respects user settings and **quiet hours**, a **deduplicator** and **collapser** merge repeated events (\"Asha and 999 others liked your photo\" instead of 1,000 pushes), **priority queues** keep password resets ahead of marketing, **rate limits** cap per-user volume, and provider adapters deliver through APNs, FCM, email or SMS gateways, each with its own limits, retries and failure modes. Push messages are **hints**, not the data (the app fetches the content), delivery is **best effort**, and tokens go stale (handle invalid-token responses by removing them). Measure delivery, open and unsubscribe rates: the cost of over-notifying is users who turn everything off.",
        ],
        analogy="A receptionist's board of who is in the office: staff tap a tag every few minutes, tags that are not refreshed are wiped, and the receptionist only phones a colleague when someone they asked about arrives, not every time anyone walks past. Notification rules are the same receptionist deciding whether a message is worth interrupting someone.",
        visual=[PRES_VIZ],
        sim=None,
        walk=[
            ("The client sends heartbeats", "Every few seconds while the app is in use."),
            ("The server stores a key with a short expiry", "Each heartbeat refreshes it; a missing heartbeat lets it lapse."),
            ("Changes are sent only to watchers", "Subscribers to that user get a presence update; others pull when they look."),
            ("Events become notifications through rules", "Preferences, quiet hours, deduplication and collapsing."),
            ("Deliver through provider adapters", "With priorities, retries, rate limits and cleanup of dead tokens."),
        ],
        groups=[
            dict(title="Presence that expires by itself, and notifications that collapse", cmds=[
                dict(volatile=True, c=r'''. ~/feed/rig.sh; redisup
q() { redis-cli -p 6398 "$@"; }
echo "--- three users send heartbeats (SET with a 3 second expiry):"
for u in ana ben cho; do q set online:$u 1 ex 3 >/dev/null; done
echo "online now: $(q --scan --pattern 'online:*' | sort | paste -sd' ')"
sleep 1.5; q set online:ana 1 ex 3 >/dev/null; echo "at 1.5 s ana sends another heartbeat (her key is refreshed); ben and cho do not"
sleep 2; echo "at 3.5 s online: $(q --scan --pattern 'online:*' | sort | paste -sd' ')   <- ben and cho expired by themselves (their phones went quiet)"
echo "ttl of ana's key: $(q ttl online:ana) s"
sleep 2; echo "at 5.5 s online: $(q --scan --pattern 'online:*' | sort | paste -sd' ' | sed 's/^$/nobody/')"
redisdown''',
                     e="Presence in four commands. A heartbeat is a `SET` with an expiry; a user who stops sending heartbeats (closed app, dead battery, lost network) **disappears when the key expires**, with no logout event and no cleanup job. Ana keeps refreshing her key and stays online; Ben and Cho lapse by themselves. The same pattern is used for locks, sessions and leases: let the absence of a signal mean \"gone\". The accuracy is bounded by the expiry (a crash looks online for up to a few seconds), which is a deliberate trade-off.",
                     annot=[("online now: online:ana online:ben online:cho", "all three heartbeats are present"),
                            ("at 3.5 s online: online:ana ...", "Ben and Cho expired without anyone doing anything"),
                            ("ttl of ana's key: 1 s (a refreshed key counts down again)", "each heartbeat resets the expiry"),
                            ("at 5.5 s online: nobody", "everyone eventually lapses when heartbeats stop")]),
                dict(c=r'''python3 - <<'EOF'
# A notification pipeline in miniature: 1,000 likes on one photo, a few other events, quiet hours and a per-user limit.
from collections import defaultdict
events = [('like', 'ana', 'photo1', 'user%d' % i, 9) for i in range(1000)]            # 1,000 likes between 09:00 and 09:10
events += [('comment', 'ana', 'photo1', 'ben', 9), ('password_reset', 'ana', None, 'system', 3), ('marketing', 'ana', None, 'system', 3), ('mention', 'ana', 'post9', 'cho', 3)]
QUIET = range(0, 7)                                                                  # no pushes between 00:00 and 07:00 unless urgent
URGENT = {'password_reset'}
def pipeline(events, collapse=True, limit=5):
    sent, held, collapsed = [], [], 0
    likes = [e for e in events if e[0] == 'like']
    rest = [e for e in events if e[0] != 'like']
    out = []
    if collapse and likes: out.append(('like', 'ana', 'photo1', '%s and %d others' % (likes[0][3], len(likes) - 1), likes[0][4])); collapsed = len(likes) - 1
    else: out += likes
    out += rest
    per_hour = defaultdict(int)
    for kind, user, obj, actor, hour in out:
        if hour in QUIET and kind not in URGENT: held.append((kind, actor)); continue         # deferred to the morning digest
        if per_hour[hour] >= limit and kind not in URGENT: held.append((kind, actor)); continue   # per-user rate limit
        per_hour[hour] += 1; sent.append((kind, actor, hour))
    return sent, held, collapsed
for collapse in (False, True):
    sent, held, c = pipeline(events, collapse=collapse)
    print('collapsing %-5s: %4d pushes sent, %4d held back (rate limit / quiet hours)%s' % (collapse, len(sent), len(held), ('; %d likes merged into one' % c) if c else ''))
sent, held, _ = pipeline(events, True)
print('sent:', [(k, a) for k, a, h in sent])
print('held for the morning digest or limits:', held)
EOF''',
                     e="Why notification systems are mostly about restraint. Without collapsing, 1,000 likes become 1,000 pushes (limited only by the per-user cap, and the user is buried); with **collapsing**, they become one message (\"user0 and 999 others liked your photo\"). The pipeline also holds back marketing and routine events during **quiet hours** while letting the **urgent** password reset through, and a **per-user rate limit** caps what remains. Every rule is a product decision as well as an engineering one: the metric that matters is not messages sent but messages that were useful.",
                     annot=[("collapsing False: ~5 pushes sent, ~1,000 held back", "uncollapsed, the limit just discards almost everything arbitrarily"),
                            ("collapsing True: 3 pushes sent ... 999 likes merged into one", "one meaningful message instead of a thousand"),
                            ("sent: [('like', ...), ('comment', 'ben'), ... ('password_reset', 'system')]", "the urgent reset is delivered even during quiet hours"),
                            ("held ...: marketing and mention at 03:00", "non-urgent notifications wait for the morning digest")]),
            ]),
        ],
        scenario=dict(
            title="\"Design a notification system for an app with 500 million users: push, email and SMS.\"",
            ask="A pipeline design question. They want ingestion, rules, preferences, prioritisation, delivery and failure handling with numbers.",
            clarify=[("Types of notifications, volume, latency targets, providers, user preferences and regulations (unsubscribe, SMS consent)?", "Assume 10 billion notifications a day, transactional ones within seconds, marketing within minutes, strict unsubscribe handling.")],
            think=[("Estimate.", "10B/day is about 115,000 per second on average, 500,000 at peak. Provider calls dominate cost (SMS especially); push and email are cheap per message."),
                   ("Ingestion.", "Services publish events (order shipped, like received) to a queue; a notification service consumes them; templates and localisation applied later."),
                   ("Rules and preferences.", "Per-user channel preferences, quiet hours, frequency caps, consent and unsubscribe flags in a fast store; rules decide whether, when and through which channel."),
                   ("Deduplicate and collapse.", "A key per (user, type, object) with a window; merge repeated events into digests; idempotency keys so retries do not double-send."),
                   ("Prioritise.", "Separate queues and worker pools per priority (security and transactional above social above marketing); marketing is rate limited and scheduled; backpressure so marketing never delays a password reset."),
                   ("Deliver.", "Provider adapters (APNs, FCM, email, SMS gateways) with retries, backoff, per-provider rate limits, circuit breakers and failover to a second provider; remove invalid tokens; record delivery receipts."),
                   ("Track and learn.", "Delivery, open and unsubscribe metrics; per-user volume caps; experiments on timing and content; audit trail for compliance."),
                   ("Failure.", "Provider outage: fail over or delay with retries; queue backlog alerts by priority; dead-letter queue; never lose transactional notifications, never double-send them.")],
            answer=["\"Ten billion notifications a day is about 115,000 per second on average and perhaps 500,000 at peak, so the pipeline is queue-based. Services publish events; a notification service consumes them, looks up the user's preferences, quiet hours, frequency caps and consent in a fast store, and decides whether, when and through which channel to notify. It deduplicates and collapses repeated events into digests and uses idempotency keys so retries never double-send.",
                    "Work is split into priority queues with separate worker pools, so security and transactional messages are never delayed by marketing, which is rate limited and scheduled. Provider adapters for push, email and SMS handle retries with backoff, per-provider rate limits, circuit breakers and failover to a second provider, remove invalid tokens and record delivery receipts. I would track delivery, open and unsubscribe rates, alert on backlog by priority, keep a dead-letter queue and an audit trail for compliance, and make sure transactional notifications are never lost and never sent twice.\""],
            follow=[("How do you prevent notification fatigue?", "Collapsing, frequency caps, quiet hours, relevance scoring and easy per-type opt-outs; measure unsubscribes and treat them as an error budget."),
                    ("What if the push provider is down?", "Retry with backoff, fail over to another channel for critical messages (SMS or email), and queue the rest; monitor provider health with a circuit breaker."),
                    ("How do you handle time zones?", "Store the user's time zone and quiet hours; schedule marketing in local time with jitter to avoid spikes.")],
            slips=["One queue for all priorities.", "No deduplication or idempotency.", "Treating push delivery as guaranteed."],
        ),
        quick=[
            ("How does heartbeat presence detect a crashed client?", "Its key expires when the heartbeats stop; no logout is needed."),
            ("What is the expensive part of presence?", "Notifying watchers of every change: limit it to subscribers and throttle."),
            ("What does collapsing do?", "Merges many similar events into one notification."),
        ],
        traps=[
            "Broadcasting every presence change to every contact.",
            "Sharing queues between marketing and security notifications.",
            "Never removing invalid push tokens: sends keep failing and costing money.",
        ],
    ),
]

TAIL = dict(
    cases=[],
    cheat=[
        ["feed push", "copy the post id to every follower's capped list: fast reads, write amplification"],
        ["feed pull", "merge followees' posts at read time: cheap writes, slow reads"],
        ["hybrid feed", "push for ordinary authors, pull for celebrities, merge at read"],
        ["feed storage", "ids only, capped lists in memory; bodies from a cache; cursor pagination"],
        ["inactive users", "do not fan out to them; build the feed lazily on return"],
        ["chat order", "server-assigned per-conversation sequence numbers"],
        ["idempotent send", "client message id unique per conversation"],
        ["offline sync", "sync after the last sequence per conversation: no special queue"],
        ["push vs delivery", "push is an optimisation; the stored message is the delivery"],
        ["real-time channel", "WebSocket (both ways), SSE (server to client), long poll (fallback)"],
        ["gateway tier", "holds millions of idle connections; user-to-gateway map in a fast store"],
        ["receipts", "delivered up to N and read up to N: small messages"],
        ["presence", "heartbeat + expiring key; soft state; notify watchers only"],
        ["notification pipeline", "rules, preferences, quiet hours, dedupe, collapse, priority queues, adapters"],
        ["transactional vs marketing", "separate queues and pools; marketing never delays security"],
        ["end-to-end encryption", "server relays ciphertext: metadata-based spam controls"],
    ],
    interview_intro="Social and messaging designs are judged on where you place the cost (write or read), how you order and recover state, and how you restrain volume. Practise each scenario aloud against the clock; the written answers are models, not scripts.",
    interview=[
        dict(q="Design Twitter's home timeline.",
             a=["Estimate posts, reads and fan-out volume; push to followers' capped id lists for ordinary authors, pull celebrities at read time (hybrid).", "Posts stored once, feed lists hold ids, bodies from caches; cursor pagination; ranking on candidates; inactive users skipped.", "Fan-out queue lag, cache loss rebuild, deletes filtered at read time; trade-offs: write amplification versus read latency."],
             follow=["User following a celebrity and 500 others?", "Deletes and edits?"], mistakes=["Pure push without celebrities.", "Whole posts in feeds."],
             angle="Reported by candidates as one of the most common design questions at large companies; not official."),
        dict(q="Design WhatsApp: one-to-one and group chat with offline delivery and receipts.",
             a=["Gateways holding WebSockets separate from stateless chat servers; user-to-gateway map; per-conversation sequence assigned by the owning shard; durable store before ack; idempotent sends by client id.", "Offline: mobile push as a wake-up, sync after last sequence on reconnect; groups push or pull; receipts as small messages.", "Failure: reconnect and sync, replicated shards; end-to-end encryption means ciphertext only."],
             follow=["Routing to the right gateway?", "Multiple devices?"], mistakes=["Client timestamps for order.", "A special offline queue."]),
        dict(q="Design a notification system: push, email and SMS at 10 billion a day.",
             a=["Event queue, notification service with preferences, quiet hours, caps and consent; deduplication and collapsing; idempotency keys.", "Priority queues and pools; provider adapters with retries, rate limits, circuit breakers and failover; token cleanup; receipts.", "Metrics on delivery, opens and unsubscribes; transactional never lost or double-sent."],
             follow=["Notification fatigue?", "Provider outage?"], mistakes=["One queue for all priorities.", "No dedupe."],
             angle="Amazon-style: expect follow-ups on exactly-once behaviour and provider failure; reported by candidates, not official."),
        dict(q="Design presence (online status) for a messaging app.",
             a=["Heartbeats and expiring keys in a fast store; soft state; no explicit logout.", "Fan-out is the cost: notify subscribed watchers only, throttle and batch, pull for large contact lists; approximate 'last seen'.", "Accuracy bounded by the expiry; multi-device presence is the union."],
             follow=["How do you scale to billions?", "What if the store loses data?"], mistakes=["Broadcasting every change to every contact."]),
    ],
    selftest=[
        ("What is fan-out on write?", "Copying a post into every follower's feed at post time."),
        ("What is the celebrity problem and its fix?", "Millions of writes for one post; pull celebrity posts at read time (hybrid)."),
        ("What do feed lists store?", "Capped lists of post ids."),
        ("How does a chat client recover missed messages?", "Sync after the last sequence number it holds."),
        ("What makes a send idempotent?", "A client message id unique per conversation."),
        ("Why not use client timestamps for ordering?", "Client clocks disagree: the server must assign the order."),
        ("WebSocket versus SSE?", "WebSocket is bidirectional; SSE is server-to-client over plain HTTP."),
        ("How does heartbeat presence work?", "A key with a short expiry refreshed by heartbeats lapses when they stop."),
        ("What is expensive about presence?", "Notifying all watchers of each change."),
        ("What does notification collapsing do?", "Merges many events into one message."),
        ("Why separate priority queues for notifications?", "So marketing cannot delay security or transactional messages."),
    ],
    recall=[
        ["hybrid feed", "push ordinary, pull celebrities"],
        ["feed list", "capped ids"],
        ["chat order", "server sequence per conversation"],
        ["send", "idempotent by client id"],
        ["offline", "sync after last seq"],
        ["gateway", "idle connections"],
        ["presence", "heartbeat + expiry"],
        ["notifications", "collapse, cap, prioritise"],
    ],
    sources=[
        dict(title="Twitter's Timelines at Scale (InfoQ talk summary)", url="https://www.infoq.com/presentations/Twitter-Timeline-Scalability/", use="Fan-out on write and the hybrid for celebrities as described by Twitter engineers", license="Copyright InfoQ and the speaker; read or watch online", how="Link only"),
        dict(title="WhatsApp architecture: Erlang Factory talks and engineering posts", url="https://engineering.fb.com/", use="Engineering write-ups from the WhatsApp and Meta messaging teams", license="Copyright Meta; read online", how="Link only"),
        dict(title="MDN: Server-sent events and the WebSocket API", url="https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events", use="The two real-time mechanisms used in the chat lesson", license="CC BY-SA; read online", how="Link only"),
        dict(title="Redis documentation: key expiry (EXPIRE, SET EX)", url="https://redis.io/docs/latest/commands/expire/", use="Expiring keys for presence", license="Copyright Redis; read online", how="Link only"),
        dict(title="Apple Push Notification service and Firebase Cloud Messaging documentation", url="https://firebase.google.com/docs/cloud-messaging", use="Provider limits, tokens and delivery semantics for push", license="Copyright Google; read online", how="Link only"),
    ],
    plan=[
        "**Hours 1 to 3:** the feed: change the follower distribution and the threshold and recompute the write amplification; then the fanout-cost lab.",
        "**Hours 4 to 6:** chat: add a read-receipt table to the toy store; kill and resync a client.",
        "**Hours 7 to 8:** presence and notifications: change the expiry and the heartbeat interval; add a digest to the pipeline.",
        "**Hours 9 to 10:** say each interview scenario aloud for two minutes, timed, and compare with the written answer.",
    ],
)
