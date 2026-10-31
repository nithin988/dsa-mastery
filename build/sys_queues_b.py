"""S20 queues, streams and async work: part B (lessons 4 to 6)."""
import sysviz as v

LOG_VIZ = v.figure(
    720, 236,
    [v.box(10, 80, 100, 56, "Producers", "ink"),
     v.arrow(110, 108, 150, 108),
     v.box(150, 20, 330, 190, "The log (append only, retained)", "acc", ""),
     v.box(165, 56, 60, 36, "0", "ink"), v.box(230, 56, 60, 36, "1", "ink"), v.box(295, 56, 60, 36, "2", "ink"), v.box(360, 56, 60, 36, "3", "ink"), v.box(425, 56, 45, 36, "4", "ink"),
     v.text(315, 120, "each message has an offset; nothing is deleted when it is read", "dg-s"),
     v.arrow(480, 80, 520, 50), v.arrow(480, 140, 520, 160),
     v.box(520, 20, 190, 56, "Group A (billing)", "ok", "its own position: offset 3"),
     v.box(520, 130, 190, 56, "Group B (analytics)", "ok", "its own position: offset 1"),
     v.text(360, 226, "A queue deletes what is consumed; a log keeps it, and every consumer group tracks its own position.", "dg-s")],
    "A log (stream), the Kafka model", "Messages are kept and numbered; consumers remember where they are, so they can replay and be added later")

PART_ORDER_VIZ = v.figure(
    720, 214,
    [v.box(10, 70, 120, 56, "Events", "ink", "account A, B, C ..."),
     v.arrow(130, 98, 180, 98), v.box(180, 70, 140, 56, "hash(account)", "warn", "chooses a partition"),
     v.arrow(320, 86, 380, 40), v.arrow(320, 98, 380, 98), v.arrow(320, 110, 380, 156),
     v.box(380, 14, 170, 48, "Partition 0: A, D", "ok", ""), v.box(380, 74, 170, 48, "Partition 1: B, E", "ok", ""), v.box(380, 134, 170, 48, "Partition 2: C, F", "ok", ""),
     v.arrow(550, 38, 590, 38), v.arrow(550, 98, 590, 98), v.arrow(550, 158, 590, 158),
     v.box(590, 14, 120, 48, "Consumer 1", "acc", ""), v.box(590, 74, 120, 48, "Consumer 2", "acc", ""), v.box(590, 134, 120, 48, "Consumer 3", "acc", ""),
     v.text(360, 204, "Order is guaranteed only inside a partition: choose the key so related events share one.", "dg-s")],
    "Partitions, keys and ordering", "More partitions mean more parallel consumers; the key keeps related messages in order")

LESSONS_B = [
    dict(
        title="Logs and streams: the Kafka model, run on Redis Streams",
        tier="hot",
        situation="A queue hands each message to one worker and then forgets it. But the billing service, the analytics pipeline and the search indexer all need every order event, and next month a fourth system will need the history. For that you need a log.",
        learn=["Queue versus log: what is deleted and what is kept", "Offsets and consumer groups", "Replay: reading history again", "Acknowledgement and the pending list"],
        model=[
            "A **log** (or **stream**) is an **append-only, ordered** sequence of messages, each with an **offset** or id. Reading does **not** remove a message: retention (time or size) does. Each **consumer group** keeps its own position, so billing, analytics and search each receive **every** message independently, at their own speed; **within** one group the messages are shared among its consumers, so adding consumers scales one job. A new consumer, or a bug fix, can **replay** history from any offset. This is the model of Apache Kafka, Redis Streams, Kinesis and Pulsar.",
            "A **classic queue** (RabbitMQ, SQS) is the opposite trade: messages are **deleted** when acknowledged, routing and per-message features (delays, priorities, dead-letter queues) are rich, but history is gone and each message goes to one consumer. Use a **queue for work distribution** (do this job once), and a **log for events** (many independent consumers, replay, audit, rebuilding derived data). In a log, the consumer **commits its position** (or acknowledges entries); if it dies, a replacement resumes from the last committed position, which gives at-least-once processing: again, make handlers idempotent.",
        ],
        analogy="A queue is a to-do tray: take a slip, do it, throw it away. A log is a bound ledger on a shelf: everyone who needs it keeps a bookmark in their own copy of the reading, new people can start from page one, and nothing is torn out when it is read.",
        visual=[LOG_VIZ],
        sim=None,
        walk=[
            ("Producers append", "Each event gets the next id; the order of the log is the order of arrival."),
            ("Consumer groups read independently", "Each group has a cursor: billing may be at offset 900 while analytics is at 400."),
            ("Within a group, consumers share the work", "Each message goes to one consumer of the group; add consumers to go faster."),
            ("Acknowledge when done", "The group records how far it got; unacknowledged messages show up in the pending list and can be claimed by another consumer."),
            ("Replay at will", "Reset a group's position, or read a range, to rebuild a view or recover from a bug."),
        ],
        groups=[
            dict(title="A real stream: groups, pending entries and replay", cmds=[
                dict(volatile=True, c=r'''. ~/q/rig.sh; qup
for i in 1 2 3 4 5 6; do qcli xadd orders $i-0 order o$i amount $((i*10)) >/dev/null; done
echo "--- the stream keeps what was written:   length = $(qcli xlen orders)"
qcli xgroup create orders billing 0 >/dev/null; qcli xgroup create orders analytics 0 >/dev/null
echo "--- group billing, consumer c1 reads 2, consumer c2 reads 2 (each message goes to one consumer of the group):"
echo "c1:" $(qcli xreadgroup group billing c1 count 2 streams orders '>' | paste -sd' ')
echo "c2:" $(qcli xreadgroup group billing c2 count 2 streams orders '>' | paste -sd' ')
echo "--- group analytics reads everything, independently of billing:"
echo "analytics got $(qcli xreadgroup group analytics a1 count 10 streams orders '>' | grep -c '^o[0-9]') orders"
echo "--- billing acknowledges c1's two messages; c2's are still pending:"
qcli xack orders billing 1-0 2-0 >/dev/null
qcli xpending orders billing | paste -sd' '
echo "--- c2 'crashes'; c1 claims its pending messages (idle > 0 ms) and finishes them:"
echo "c1 now owns: $(qcli xautoclaim orders billing c1 0 0-0 count 10 | sed -n '2,$p' | grep -E '^[0-9]+-0$' | paste -sd' ')"
echo "--- replay: the log still has everything, read it again from the start:"
qcli xrange orders - + count 3 | grep -E "^[0-9]+-0" | paste -sd' '
qdown''',
                     e="The log model, step by step on a real Redis stream. Six events are appended and **stay** after being read. Group `billing` splits them between two consumers; group `analytics` reads **all six** on its own, unaffected by billing. Messages that were delivered but not acknowledged sit in the **pending list** with their owner: that is how a crashed consumer's work is found. Another consumer **claims** them and carries on. Because nothing was deleted, anyone can **replay** from the start. (Explicit ids `1-0`, `2-0`... are used only to make the output predictable; normally Redis assigns time-based ids.)",
                     annot=[("length = 6", "all six events are retained after being written"),
                            ("c1: ... c2: ...", "within the billing group each message went to exactly one consumer"),
                            ("analytics got 6 orders", "a different group sees every message independently"),
                            ("pending: 2 (ids 3-0 and 4-0) owned by c2", "delivered, not acknowledged: the pending list is what recovery uses"),
                            ("c1 now owns: 3-0 4-0", "another consumer can take over a dead one's unacknowledged work"),
                            ("1-0 2-0 3-0 (replay)", "the history is still there: a new consumer or a bug fix can read it again")]),
            ]),
        ],
        scenario=dict(
            title="\"Kafka versus RabbitMQ or SQS: when would you pick each?\"",
            ask="A comparison question. They want the underlying model, not product loyalty.",
            clarify=[("Is each message a job to be done once, or an event many systems care about? How long must history be kept?", "Jobs favour queues; events with several consumers or replay favour logs.")],
            think=[("State the two models.", "Queue: messages are removed once acknowledged; broker does routing, delays, priorities, dead-letter. Log: messages are retained in order per partition; consumers track offsets; many groups read independently."),
                   ("Pick by need.", "Distribute work among interchangeable workers with retries and dead-lettering: queue. Many services consume the same events, need replay, audit or to rebuild state, very high throughput: log."),
                   ("Compare what each costs.", "Log: ordering only within a partition, consumers must manage offsets and idempotency, retention storage, partition count chosen up front. Queue: no replay, per-message routing is flexible, simpler for work distribution; ordering is weaker once there are several consumers."),
                   ("Mention scale.", "Logs scale by partitions (ordered shards) and consumer groups; throughput of hundreds of thousands to millions of messages per second per cluster is normal."),
                   ("Say hybrids are common.", "Events flow into a log for the system of record, and downstream workers use queues for job distribution."),
                   ("Say what you would measure.", "Consumer lag per group (log end offset minus committed offset) is the key health metric.")],
            answer=["\"They are different models. A queue like RabbitMQ or SQS removes a message when it is acknowledged, has flexible routing, delays and dead-letter queues, and gives each message to one consumer: it is the right tool for distributing jobs to workers. A log like Kafka keeps messages in order within a partition for a retention period, and each consumer group tracks its own offset, so many services can read the same events independently and I can replay history to rebuild a view or fix a bug.",
                    "So for background jobs I would pick a queue; for events that billing, analytics and search all consume, or where I need replay and audit, a log. The costs of a log are that ordering is only per partition, I choose the partition count and key up front, and consumers must handle offsets and be idempotent. I would monitor consumer lag per group. Often both appear in one system.\""],
            follow=[("What is consumer lag?", "How far a group is behind the end of the log (end offset minus the group's committed offset): rising lag means the group cannot keep up."),
                    ("How does a log scale beyond one machine?", "It is split into partitions spread over brokers; each partition is an ordered log, replicated; consumers in a group split the partitions."),
                    ("What happens if two consumers in a group read the same partition?", "They do not: a partition is assigned to one consumer of a group at a time, which is what preserves order.")],
            slips=["Treating them as interchangeable.", "Forgetting that ordering is per partition only.", "Not mentioning consumer lag."],
        ),
        quick=[
            ("What does a log keep that a queue deletes?", "The messages themselves: they stay until retention removes them, so they can be replayed."),
            ("What is a consumer group?", "A set of consumers that share a stream's messages; each group tracks its own position and sees every message."),
            ("What is the pending list?", "Messages delivered to a consumer but not yet acknowledged: used to recover from a crashed consumer."),
        ],
        traps=[
            "Using one consumer group for two different purposes: they steal each other's messages.",
            "Forgetting retention: an unbounded stream fills memory or disk.",
            "Assuming a log gives global order: only order within a partition is guaranteed.",
        ],
    ),
    dict(
        title="Ordering, retries, dead letters and back-pressure",
        tier="hot",
        situation="Account 7 gets \"deposit 100\" then \"withdraw 80\". Two workers handle them in parallel and the withdrawal runs first. A malformed message fails forever and blocks the line. A slow database makes the queue grow without limit until the machine runs out of memory.",
        learn=["Ordering by key with partitions", "Retries with exponential backoff and jitter", "Dead-letter queues for poison messages", "Back-pressure: bounded queues and shedding load"],
        model=[
            "**Ordering**: with several parallel consumers, global order is lost. The standard solution is **partition by key**: hash the key (the account id, the conversation id) to pick a partition, and let exactly one consumer read each partition, so all events for one key are processed **in order** while different keys run in parallel. More partitions allow more parallelism but never reorder within a key. Choose the key as the unit that needs ordering, and beware hot keys (one account with huge traffic).",
            "**Retries**: transient failures (timeouts, a brief outage) deserve a retry, after a delay that **grows exponentially with jitter** so retries do not synchronise into a storm. Failures that will never succeed (a malformed payload: a **poison message**) must not be retried forever: after a limit move the message to a **dead-letter queue** (DLQ), alert, and let humans or tools inspect and replay it. **Back-pressure**: if producers are faster than consumers, an unbounded queue only postpones the failure, using memory and adding delay (a backlog of N jobs at S per second means a wait of N/S seconds). Use a **bounded** queue and decide the policy: slow the producer (block), reject with \"busy\" (load shedding, HTTP 429/503), drop the least valuable work, or scale consumers.",
        ],
        analogy="Check-in desks at an airport: each family (key) goes to one desk so their bags stay together. A passenger with the wrong passport (poison message) is sent aside to a special desk instead of blocking the line. If the queue stretches out of the door, you either open more desks or tell people to come back later.",
        visual=[PART_ORDER_VIZ],
        sim=None,
        walk=[
            ("Choose the ordering key", "The smallest thing whose events must stay in order: an account, an order, a conversation."),
            ("Route by hash of the key", "Same key, same partition, same consumer: ordered; different keys: parallel."),
            ("Retry transient failures with backoff", "Wait 1 s, 2 s, 4 s ... with random jitter; cap the attempts."),
            ("Dead-letter poison messages", "After the last attempt move the message aside with the error, and alert on the DLQ size."),
            ("Bound the queue and choose a policy", "When full: block producers, shed load, or drop; always alert on depth and age."),
        ],
        groups=[
            dict(title="Order by key, retry, dead-letter, and back-pressure", cmds=[
                dict(volatile=True, c=r'''python3 - <<'EOF'
import queue, random, threading, time
rng = random.Random(3)
events = [(acct, seq) for seq in range(1, 31) for acct in range(1, 5)]      # 4 accounts, each with events numbered 1..30 in order
def run(route, label):
    qs = [queue.Queue() for _ in range(4)] if route else [queue.Queue()] * 4   # no key: ONE shared queue, any worker takes any event
    for e in events: qs[route(e) if route else 0].put(e)
    seen = {a: [] for a in range(1, 5)}; lock = threading.Lock()
    def worker(q):
        while True:
            try: acct, seq = q.get_nowait()
            except queue.Empty: return
            time.sleep(rng.random() * 0.003)                          # processing takes a variable time
            with lock: seen[acct].append(seq)
    ts = [threading.Thread(target=worker, args=(q,)) for q in qs]
    [t.start() for t in ts]; [t.join() for t in ts]
    bad = sum(1 for a in seen for x, y in zip(seen[a], seen[a][1:]) if y < x)
    print('%-34s events processed out of order: %d' % (label, bad))
run(None, 'any worker, any event (no key):')
run(lambda e: e[0] % 4, 'partitioned by account:')
EOF''',
                     e="Why partition by key. The same 120 events (four accounts, each numbered 1 to 30) are processed by four parallel workers with random processing times. When any worker takes any event, **events for the same account overtake each other**: many are processed out of order. When events are routed by account to one fixed worker, each account's events stay in order **by construction** while the four accounts still run in parallel. This is what Kafka partitions and message keys do.",
                     annot=[("any worker, any event: out of order: 15 in the recording (varies per run)", "parallelism without a key scrambles per-account order"),
                            ("partitioned by account: out of order: 0", "same key, same partition, same worker: order preserved, still parallel across accounts")]),
                dict(volatile=True, c=r'''python3 - <<'EOF'
import random, time
rng = random.Random(1)
dlq, log = [], []
def handle(msg, attempt):
    if msg.get('bad'): raise ValueError('malformed payload')               # a poison message: will never succeed
    if msg['id'] == 'm2' and attempt == 1: raise TimeoutError('downstream timed out')   # transient: works on retry
def process(msg, max_attempts=4, base=0.05):
    for attempt in range(1, max_attempts + 1):
        try:
            handle(msg, attempt); log.append('%s attempt %d: ok' % (msg['id'], attempt)); return
        except Exception as e:
            log.append('%s attempt %d: %s' % (msg['id'], attempt, e))
            if attempt == max_attempts:
                dlq.append((msg['id'], str(e))); log.append('%s -> dead-letter queue' % msg['id']); return
            delay = base * 2 ** (attempt - 1) * (0.5 + rng.random())      # exponential backoff with jitter
            log.append('   waiting %.0f ms before retry' % (delay * 1000)); time.sleep(delay)
for m in ({'id': 'm1'}, {'id': 'm2'}, {'id': 'm3', 'bad': True}, {'id': 'm4'}): process(m)
print('\n'.join(log)); print('dead-letter queue now holds:', dlq)
EOF''',
                     e="Retries done properly. `m2` fails once with a transient timeout, waits (a delay that **doubles with random jitter**) and succeeds on the second attempt. `m3` is a **poison message**: it fails every time, so after the attempt limit it is moved to the **dead-letter queue** with its error, instead of blocking the others or retrying forever. `m4` is processed normally afterwards. The DLQ must be monitored: a growing DLQ is a bug report, and its messages can be fixed and replayed.",
                     annot=[("m2 attempt 1: downstream timed out ... m2 attempt 2: ok", "a transient failure recovered by a retry after a backoff"),
                            ("waiting N ms before retry (growing: ~50, ~100, ~200 ms with jitter)", "exponential backoff with jitter so retries do not hammer a struggling service in lockstep"),
                            ("m3 -> dead-letter queue", "a message that can never succeed is parked after the attempt limit, with its error"),
                            ("dead-letter queue now holds: [('m3', 'malformed payload')]", "operators can inspect, fix and replay it")]),
                dict(volatile=True, c=r'''python3 - <<'EOF'
import queue, threading, time
def scenario(maxsize, label):
    q = queue.Queue(maxsize=maxsize); stats = {'done': 0, 'rejected': 0, 'peak': 0}
    stop = threading.Event()
    def worker():
        while not stop.is_set():
            try: q.get(timeout=0.1)
            except queue.Empty: continue
            time.sleep(0.02); stats['done'] += 1                          # service rate: 50 per second
    t = threading.Thread(target=worker); t.start()
    start = time.time()
    while time.time() - start < 3:                                        # arrival rate: 100 per second for 3 seconds
        try: q.put_nowait(1)
        except queue.Full: stats['rejected'] += 1
        stats['peak'] = max(stats['peak'], q.qsize()); time.sleep(0.01)
    wait = q.qsize() * 0.02
    stop.set(); t.join()
    print('%-22s peak depth %3d, rejected %3d, a new job would now wait about %.1f s' % (label, stats['peak'], stats['rejected'], wait))
scenario(0, 'unbounded queue:')
scenario(20, 'bounded queue (20):')
EOF''',
                     e="Back-pressure, measured. Jobs arrive at about 100 per second but are processed at 50 per second. The **unbounded** queue accepts everything, so its depth keeps growing (about 50 more jobs every second) and a newly arrived job would wait many seconds: latency grows and memory fills while every job is still \"accepted\". The **bounded** queue holds at most 20, so the excess is **rejected immediately** (the caller gets a clear `busy` and can retry later or degrade), and the wait for accepted jobs stays under half a second. Rejecting early is usually kinder than accepting work you cannot finish.",
                     annot=[("unbounded queue: peak depth ~145, rejected 0, wait ~3 s", "everything accepted, delay grows with the backlog (depth / service rate)"),
                            ("bounded queue (20): peak depth 20, rejected ~120, wait ~0.4 s", "excess load is shed at the door, accepted work stays fast")]),
            ]),
        ],
        scenario=dict(
            title="\"Design a notification service that sends 10 million emails a day with retries. What can go wrong in the queue?\"",
            ask="They want a pipeline with the failure modes named: ordering, retries, poison messages, back-pressure, third-party limits.",
            clarify=[("Peak rate, delivery deadline, and are there per-user ordering needs?", "10 million a day is about 115 per second on average, perhaps 1,000 per second at peak. Order matters only per user, if at all."),
                     ("What does the email provider limit?", "Third parties rate-limit: the consumer must respect their limits.")],
            think=[("Size the flow.", "10M / 86,400 s is about 115 per second average; peak maybe 10x. With 100 ms per send and 50 concurrent senders, capacity is 500 per second: scale for peak, or let the queue smooth it."),
                   ("Pipeline.", "API receives requests and writes an outbox row or enqueues; a queue per priority (password resets before newsletters); workers call the provider; results update a status table."),
                   ("Ordering.", "Not global; per recipient if needed: partition by user id."),
                   ("Retries and idempotency.", "Retry transient errors with exponential backoff and jitter; an idempotency key per notification (and pass it to the provider) so a retry never double-sends; at-least-once delivery with deduplication."),
                   ("Poison and DLQ.", "Invalid addresses or payloads go to a dead-letter queue after a few attempts, with an alert and a tool to inspect and replay."),
                   ("Back-pressure and limits.", "Bounded queues, a rate limiter toward the provider (token bucket), and a priority scheme so a newsletter cannot delay a password reset; shed or defer low-priority work first."),
                   ("Monitoring.", "Queue depth and oldest age per priority, send rate, error rate by cause, DLQ size, end-to-end delivery latency.")],
            answer=["\"Ten million a day is about 115 sends per second on average and maybe ten times that at peak, which a queue plus a pool of workers handles easily. The API writes the notification and an event in one transaction (an outbox) or enqueues it, with a queue per priority so password resets are never stuck behind newsletters. Workers call the email provider and record the result.",
                    "Failures: transient errors are retried with exponential backoff and jitter; every notification has an idempotency key, also passed to the provider, so at-least-once delivery cannot double-send; invalid messages go to a dead-letter queue after a few attempts, with an alert. Ordering is only needed per recipient, so I would partition by user id. I would bound the queues and rate limit toward the provider, shedding low-priority work first under pressure. I would monitor depth and oldest age per priority, error rates by cause, DLQ size and end-to-end latency.\""],
            follow=[("How do you handle the provider being down for an hour?", "Retries back off; the queue grows (bounded, with alerts); fail over to a second provider if available; low-priority messages wait, high-priority ones switch route."),
                    ("How do you prevent a newsletter from delaying password resets?", "Separate queues and consumer pools per priority (or weighted consumption), and rate limit the bulk queue."),
                    ("How would you track that a notification was delivered?", "A status row per notification updated by the worker and by provider webhooks (delivered, bounced), with timestamps for latency metrics.")],
            slips=["One queue for everything.", "Retrying forever without a dead-letter queue.", "No idempotency: retries double-send."],
        ),
        quick=[
            ("How do you keep events for one account in order while processing in parallel?", "Partition by account id so one consumer handles each account's events sequentially."),
            ("Why add jitter to retry delays?", "So many failed clients do not retry at the same instant and overload the recovering service."),
            ("What is a dead-letter queue for?", "Parking messages that keep failing so they stop blocking the queue and can be inspected and replayed."),
        ],
        traps=[
            "Retrying a poison message forever: it burns capacity and blocks the queue.",
            "An unbounded queue that hides overload until memory or delay becomes the outage.",
            "Choosing a skewed ordering key: one hot key serialises most of the traffic.",
        ],
    ),
    dict(
        title="Choosing and sizing: queue, log, pub/sub or database table",
        tier="hot",
        situation="You are asked to move work off the request path and \"add Kafka\". Is that right? How many consumers do you need? What do you do when a consumer is slow? This lesson makes those choices repeatable.",
        learn=["A decision table for work queues, logs, pub/sub and tables", "Sizing consumers with simple arithmetic (Little's law)", "Async API design: status, webhooks, idempotency", "What to monitor"],
        model=[
            "Start from the need: **distribute jobs** (queue or a SKIP LOCKED table), **broadcast events to many independent consumers with replay** (log), **fan out ephemeral notifications to current subscribers** (pub/sub: Redis pub/sub, SNS: not stored, a subscriber that is down misses it), **enforce a strict workflow** (a workflow engine). Prefer the simplest thing that works: a table in the database you already run is enough for modest volume and gives transactional enqueue; add a broker when volume, fan-out or replay demands it.",
            "**Sizing**: by **Little's law**, the number of jobs in the system equals arrival rate times time in system. Consumers needed = arrival rate x processing time / concurrency per consumer, then add headroom (target 50 to 70 percent utilisation) and size for the peak, or accept that the queue absorbs it for a bounded time. The **async API** pattern: return `202 Accepted` with a job id and a status URL (or a webhook callback), accept an **idempotency key** so client retries do not create duplicates, and define how long results are kept. Monitor **depth, age of the oldest message, consumer lag, retry rate, DLQ size** and end-to-end latency.",
        ],
        analogy="A post office chooses between a letterbox (a work queue: one letter, one handler), a public noticeboard (pub/sub: whoever is there reads it, and it is not kept) and an archive of every document with reading rooms (a log).",
        sim=None,
        walk=[
            ("Say what the consumer needs", "One worker per job, many independent readers, replay, or just a notification?"),
            ("Start simple", "A jobs table or a managed queue before a streaming platform."),
            ("Compute capacity", "Arrival rate x seconds per job / concurrency, then headroom for peak."),
            ("Design the API for async", "202, job id, status endpoint or webhook, idempotency key."),
            ("Add the guard rails", "Bounded queues, retries with backoff, dead-letter, per-priority queues, alerts on age and lag."),
        ],
        groups=[
            dict(title="A consumer sizing calculator", cmds=[
                dict(c=r'''python3 - <<'EOF'
import math
def size(name, per_sec, secs_per_job, threads, peak_x=1, target_util=0.6):
    peak = per_sec * peak_x
    needed_threads = peak * secs_per_job / target_util            # Little's law: jobs in flight = rate x time; add headroom
    workers = math.ceil(needed_threads / threads)
    print('%s' % name)
    print('  average %.0f jobs/s, peak %.0f jobs/s, %.2f s per job' % (per_sec, peak, secs_per_job))
    print('  jobs in flight at peak: %.0f; at %d%% utilisation that is %.0f threads -> %d workers of %d threads' % (peak * secs_per_job, target_util * 100, needed_threads, workers, threads))
size('Emails: 10 million a day', 10e6 / 86400, 0.1, 25, peak_x=10)
size('Image resize: 40 uploads a second', 40, 1.5, 4, peak_x=3)
size('Payments webhook: 300 a second, 40 ms each', 300, 0.04, 8, peak_x=2)
EOF''',
                     e="The same rule of thumb applied three ways. **Jobs in flight = arrival rate x time per job**, so slow jobs need many threads even at a modest rate (image resizing), while fast jobs at a high rate need very few (webhooks). Dividing by the target utilisation leaves headroom for bursts and failures. This is the arithmetic behind a sentence like \"about 20 workers, scaling to 40 for peak\", and the numbers are easy to defend because every term is stated.",
                     annot=[("Emails: ... peak 1157 jobs/s ... 116 jobs in flight at peak ... 193 threads -> 8 workers of 25 threads", "ten times the average rate at the peak, 100 ms per send"),
                            ("Image resize: ... 180 jobs in flight at peak ... 300 threads -> 75 workers of 4 threads", "slow jobs mean many threads even at a modest request rate"),
                            ("Payments webhook: ... 24 jobs in flight ... 40 threads -> 5 workers of 8 threads", "fast jobs need little capacity")]),
            ]),
        ],
        playbook=dict(title="Which mechanism for which job", intro=["A decision table: start from what the consumer needs."], rows=[
            ["Background jobs for interchangeable workers (emails, resizing)", "Work queue (SQS, RabbitMQ, Redis list) or a jobs table with SKIP LOCKED", "One consumer per job, retries, dead-letter, delays", "Idempotent handlers; monitor depth and age"],
            ["The same events needed by many services; replay and audit", "Log / stream (Kafka, Kinesis, Redis Streams)", "Retention, offsets per group, partition ordering", "Choose key and partition count; monitor consumer lag"],
            ["Notify currently connected subscribers, loss is acceptable", "Pub/sub (Redis pub/sub, SNS to push)", "Fire and forget; no storage", "A subscriber that is down misses the message"],
            ["Publish an event reliably after a database change", "Outbox table + relay (or CDC) into a queue or log", "Event exists if and only if the data does", "At least once: dedupe in consumers"],
            ["A long multi-step process with compensations", "Workflow engine or saga with a queue per step", "Durable state per step, retries, timeouts", "Idempotent steps; clear compensation"],
            ["Low volume, you already run a database", "A table in that database", "Transactional enqueue, no new system", "Move to a broker when volume demands"],
        ]),
        scenario=dict(
            title="\"Your checkout takes 6 seconds because it calls five services in sequence. How do you redesign it with queues?\"",
            ask="A synthesis question: what stays synchronous, what moves behind a queue, and how the user learns the result.",
            clarify=[("Which calls must finish before we can tell the customer success?", "Typically: validate cart, take payment authorisation, reserve stock. Others (email, analytics, loyalty points, warehouse notification) can happen later.")],
            think=[("Split the work.", "Synchronous (the user needs the answer): validate, authorise payment, reserve stock. Asynchronous: confirmation email, analytics, loyalty points, invoice PDF, warehouse and shipping notifications."),
                   ("Make the handoff reliable.", "Write the order and an outbox event in one transaction; a relay publishes `order_placed` to a log; each downstream service has its own consumer group and processes at its own pace."),
                   ("Idempotency.", "Each consumer deduplicates by event id; the checkout API accepts an idempotency key so a double-click or client retry does not create two orders."),
                   ("Failure handling.", "Retries with backoff per consumer, dead-letter queues, and alerts; a failing email service never fails a checkout."),
                   ("User experience.", "Return the order number immediately; the confirmation page shows status; emails and shipping updates arrive later."),
                   ("Operations.", "Consumer lag per downstream service, DLQ sizes, end-to-end time from order to email, and a runbook to replay events.")],
            answer=["\"I would split the checkout into what the customer must wait for and what they do not. Validating the cart, authorising the payment and reserving stock stay synchronous, because the answer depends on them. Everything else, the confirmation email, analytics, loyalty points, invoices and warehouse notifications, moves behind an event.",
                    "I would write the order and an outbox row in one transaction, and a relay would publish an order_placed event to a log, so no event is lost and each downstream service has its own consumer group working at its own speed. Each consumer is idempotent on the event id, the checkout API takes an idempotency key so a double click does not create two orders, and failures are retried with backoff and then dead-lettered with an alert, so a broken email service can never fail a checkout. The customer gets an order number at once. I would monitor consumer lag per service, dead-letter sizes and the time from order to email.\""],
            follow=[("What if payment authorisation succeeds but stock reservation fails?", "Compensate: void or refund the authorisation (a saga step), and tell the customer; make the compensation idempotent."),
                    ("How do you keep the five services from going out of sync?", "Events are the source of truth for downstream state; consumers are idempotent and replayable; reconciliation jobs compare and repair."),
                    ("When would you keep a call synchronous even though it is slow?", "When the user's next step depends on the result, or when the failure must be reported immediately (payment authorisation).")],
            slips=["Moving payment confirmation behind a queue and telling the user it succeeded.", "No outbox: events lost on crash.", "No idempotency key: double orders."],
        ),
        quick=[
            ("How many consumer threads do you need?", "Arrival rate x seconds per job, divided by the target utilisation (headroom), sized for the peak."),
            ("What is the difference between a queue and pub/sub?", "A queue stores messages until a worker takes them; basic pub/sub does not store, so absent subscribers miss messages."),
            ("What does an async API return?", "`202 Accepted` with a job id and a way to check the status (or a webhook), and accepts an idempotency key."),
        ],
        traps=[
            "Adding a heavyweight streaming platform for a few jobs a minute.",
            "Sizing for the average rate: the peak is what fills queues.",
            "Telling the user an operation succeeded before its outcome is known.",
        ],
    ),
]
