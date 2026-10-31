"""S20 queues, streams and async work: part A (rig, lessons 1 to 3)."""
import sysviz as v

RIG = r'''mkdir -p ~/q && cd ~/q && cat > rc.py <<'EOF'
# A minimal Redis client (the Redis wire protocol is simple text), so the experiments need nothing but python3.
import socket
class R:
    def __init__(self, port=6394):
        self.s = socket.create_connection(('127.0.0.1', port)); self.f = self.s.makefile('rb')
    def cmd(self, *a):
        out = b'*%d\r\n' % len(a)
        for x in a:
            x = str(x).encode(); out += b'$%d\r\n%s\r\n' % (len(x), x)
        self.s.sendall(out); return self._read()
    def _read(self):
        line = self.f.readline().rstrip(b'\r\n'); t, val = line[:1], line[1:]
        if t == b'+': return val.decode()
        if t == b'-': raise Exception(val.decode())
        if t == b':': return int(val)
        if t == b'$':
            n = int(val)
            return None if n < 0 else self.f.read(n + 2)[:-2].decode()
        if t == b'*': return [self._read() for _ in range(int(val))]
EOF
cat > rig.sh <<'EOF'
# Redis on port 6394 (queues and streams) and PostgreSQL on port 5561 (outbox and job table), both private and local.
export Q=$HOME/q PG=$(ls -d /usr/lib/postgresql/*/bin | head -1); export PATH=$PG:$PATH
qup()   { redis-server --port 6394 --bind 127.0.0.1 --save "" --appendonly no --daemonize yes --dir $Q --logfile $Q/redis.log >/dev/null; sleep 0.5; }
qcli()  { redis-cli -p 6394 "$@"; }
qdown() { redis-cli -p 6394 shutdown nosave 2>/dev/null; sleep 0.3; true; }
pgup()  { [ -d $Q/pg ] || initdb -D $Q/pg -A trust -U learner >/dev/null
          pg_ctl -D $Q/pg -o "-p 5561 -k $Q -c listen_addresses='' -c fsync=off" -l $Q/pg.log -w start >/dev/null
          createdb -h $Q -p 5561 -U learner app 2>/dev/null || true; }
pgdown(){ pg_ctl -D $Q/pg -m fast stop >/dev/null 2>&1; }
pq()    { psql -X -q -h $Q -p 5561 -U learner -d app "$@"; }
EOF
. ./rig.sh; echo "rig ready in $Q: rc.py (tiny Redis client) and rig.sh (qup, qcli, qdown, pgup, pgdown, pq)"'''

ASYNC_SEQ = v.seq(
    ["Client", "API", "Queue", "Worker"],
    [("a->b", 0, 1, "POST /signup"),
     ("a->b", 1, 2, "enqueue: send welcome email"),
     ("a->b", 1, 0, "202 Accepted (in milliseconds)", "reply"),
     ("a->b", 2, 3, "deliver job when a worker is free"),
     ("a->b", 3, 3, "send the email (slow, may fail)"),
     ("a->b", 3, 2, "ack: done, remove from the queue", "reply"),
     ("note", 0, 3, "if the worker crashes before the ack, the queue gives the job to another worker")],
    "Asynchronous work through a queue", "The user waits only for the enqueue; the slow work happens later, safely retried")

DELIVERY_VIZ = v.figure(
    720, 226,
    [v.box(10, 20, 210, 56, "At most once", "bad", "take the job, then work: a crash loses it"),
     v.box(255, 20, 210, 56, "At least once", "warn", "work, then ack: a crash causes a retry (duplicates)"),
     v.box(500, 20, 210, 56, "Exactly once (effect)", "ok", "at least once plus idempotent handling"),
     v.text(115, 108, "fast, simple, may lose work", "dg-s"), v.text(360, 108, "the usual default: never lose, may repeat", "dg-s"),
     v.text(605, 108, "what you can actually achieve", "dg-s"),
     v.box(120, 134, 480, 52, "No system gives true exactly-once delivery over a network", "ink", "you make the handler safe to repeat instead"),
     v.text(360, 214, "Design every consumer as if each message could arrive twice.", "dg-s")],
    "Delivery guarantees", "Three promises a queue can make, and the one you build yourself")

OUTBOX_SEQ = v.seq(
    ["App", "Database", "Relay", "Broker"],
    [("a->b", 0, 1, "BEGIN; insert order; insert outbox row; COMMIT"),
     ("note", 0, 3, "one transaction: the order and the event are saved together or not at all"),
     ("a->b", 2, 1, "poll: unsent outbox rows"),
     ("a->b", 1, 2, "event rows", "reply"),
     ("a->b", 2, 3, "publish the event"),
     ("a->b", 2, 1, "mark the row as sent"),
     ("note", 0, 3, "crash between publish and mark: the event is published again: consumers must tolerate duplicates")],
    "The transactional outbox", "Write the event in the same transaction as the data, and let a relay publish it")

LESSONS_A = [
    dict(
        title="Why queues: decoupling, spikes and slow work",
        tier="hot",
        situation="Sign-up sends a welcome email, resizes an avatar and notifies three services. It takes 4 seconds, fails when the email provider hiccups, and falls over on launch day. Almost every large system moves such work behind a queue.",
        learn=["What a queue is and what it decouples", "How a queue absorbs a traffic spike", "Producers, consumers and workers", "Real queues running: a Redis list as a job queue"],
        model=[
            "A **message queue** sits between a **producer** (which creates jobs or events) and one or more **consumers/workers** (which process them). The producer **enqueues and returns immediately**; the work happens later, at the consumer's pace. That decouples three things: **time** (the work need not happen while the user waits), **rate** (a burst of arrivals is absorbed by the queue instead of overwhelming the workers) and **failure** (if a worker or a downstream service is down, jobs wait and are retried instead of failing the user's request).",
            "The price: the system becomes **asynchronous**. The user gets \"accepted\", not \"done\"; results arrive later or must be polled; ordering, duplicates and retries now matter; and you must **monitor the queue** (depth and age of the oldest message) because a growing queue is the first sign the workers cannot keep up. A queue **smooths** bursts but cannot fix a system whose average arrival rate exceeds its processing rate: the backlog just grows until something gives.",
        ],
        analogy="A restaurant ticket rail: waiters (producers) hang order tickets and walk away; cooks (consumers) take tickets when they are free. A rush of orders makes the rail longer, not the waiters wait at the stove, and if a cook leaves the next one takes the ticket. If orders always arrive faster than the cooks can cook, the rail just keeps growing.",
        visual=[ASYNC_SEQ],
        sim=None,
        walk=[
            ("Accept the request and enqueue", "The API validates, stores a job description in the queue and replies `202 Accepted` within milliseconds."),
            ("The queue holds the job durably", "It stays until a consumer takes it and acknowledges completion."),
            ("Workers pull at their own pace", "Add workers to go faster; remove them to save money; a slow worker does not slow the producer."),
            ("Failures are retried", "A job that fails (or whose worker dies) is delivered again, usually after a delay."),
            ("Watch depth and age", "Queue depth and oldest-message age tell you whether consumers keep up."),
        ],
        groups=[
            dict(title="Build the rig, then watch a queue absorb a spike", cmds=[
                dict(c=RIG,
                     e="Creates the rig used by the whole module: a tiny Redis client written in a few lines, and helpers that start a private **Redis** (port 6394, for queues and streams) and a private **PostgreSQL** (port 5561, for the outbox and a job table), both as your user with no network. Nothing outside `~/q` is touched."),
                dict(volatile=True, c=r'''. ~/q/rig.sh; qup; cd ~/q; cat > spike.py <<'EOF'
import sys, threading, time
sys.path.insert(0, '.')
from rc import R
r = R(); r.cmd('DEL', 'jobs')
done = [0]
def worker():                                   # one worker: 20 ms per job = 50 jobs per second
    w = R()
    while True:
        j = w.cmd('BRPOP', 'jobs', 1)
        if not j: return                       # BRPOP timed out: the queue stayed empty
        time.sleep(0.02); done[0] += 1
t = threading.Thread(target=worker); t.start()
t0 = time.time()
for i in range(200): r.cmd('LPUSH', 'jobs', 'job-%d' % i)     # a burst: 200 jobs arrive almost at once
print('burst of 200 jobs enqueued in %.0f ms (the producers were never slowed down)' % ((time.time() - t0) * 1000))
for sec in (0, 1, 2, 3, 4, 5):
    print('after %d s: queue depth %3d, completed %3d' % (sec, r.cmd('LLEN', 'jobs'), done[0]))
    time.sleep(1)
t.join()
EOF
python3 spike.py; qdown''',
                     e="A queue absorbing a burst. 200 jobs arrive almost at once, but the single worker handles only about 50 a second. The producer is **not slowed**: enqueueing 200 jobs takes a few milliseconds. The **queue depth** is the visible backlog: it starts near 200 and drains linearly over about 4 seconds. If the burst were a sustained rate above 50 jobs per second, the depth would only ever grow, which is why you alert on depth and on the age of the oldest message.",
                     annot=[("burst of 200 jobs enqueued in ~N ms", "producers are decoupled from how slowly the work is done"),
                            ("after 0 s: queue depth ~200 ... after 4 s: ~0", "the backlog drains at the worker's rate: about 50 jobs per second"),
                            ("completed ~N", "the worker's progress at each sample: the queue turned a spike into a steady stream")]),
                dict(volatile=True, c=r'''. ~/q/rig.sh; qup; cd ~/q
python3 - <<'EOF'
import sys, time
sys.path.insert(0, '.')
from rc import R
r = R()
def send_email(to): time.sleep(0.2)                              # a slow, flaky external call: 200 ms
t = time.time(); send_email('a@example.com'); sync_ms = (time.time() - t) * 1000
t = time.time(); r.cmd('LPUSH', 'emails', '{"to": "a@example.com"}'); async_ms = (time.time() - t) * 1000
print('synchronous signup waits for the email:   %6.1f ms' % sync_ms)
print('asynchronous signup only enqueues:        %6.1f ms' % async_ms)
print('job waiting in the queue:', r.cmd('LRANGE', 'emails', 0, -1))
EOF
qdown''',
                     e="What the user feels. With the email sent inside the request, the signup is as slow as the slowest dependency and fails if it fails. With a queue the request only pays for the enqueue (a fraction of a millisecond) and the job waits safely for a worker. The cost is that the email may arrive a moment later and failures happen out of sight: you now own retries and monitoring.",
                     annot=[("synchronous signup waits for the email: ~200 ms", "the user waits for the external call"),
                            ("asynchronous signup only enqueues: ~0.1 ms", "about a thousand times faster for the user"),
                            ("job waiting in the queue: ['{\"to\": \"a@example.com\"}']", "the work is stored and waiting for a worker")]),
            ]),
        ],
        scenario=dict(
            title="\"When would you put a queue in front of a service? What problems does it create?\"",
            ask="A foundation question that leads into delivery guarantees. A good answer gives benefits, costs and when not to use one.",
            clarify=[("What work is on the request path, and does the user need the result immediately?", "If the user needs the answer to continue, a queue cannot hide the latency: it only fits work that can finish later.")],
            think=[("Name the three things it decouples.", "Time (work later), rate (absorb spikes), failure (retry while a dependency is down). Also lets you scale producers and consumers independently."),
                   ("Say when it fits.", "Sending emails, resizing images, calling flaky third parties, billing runs, fan-out to many services, any work the user does not need to wait for."),
                   ("Say when it does not.", "When the caller needs the result now, or the extra moving part and latency are not worth it for light, reliable work."),
                   ("List the costs.", "Asynchrony (the user sees accepted, not done), duplicates and ordering, a new component to run and monitor, visibility problems (where is my job?), and the possibility of an unbounded backlog."),
                   ("Say what to monitor.", "Queue depth, age of the oldest message, processing rate versus arrival rate, retry and dead-letter counts."),
                   ("Mention the limit.", "A queue smooths bursts. If the average arrival rate exceeds the processing rate, the backlog grows without bound: scale consumers or shed load.")],
            answer=["\"A queue decouples producer and consumer in time, rate and failure. The request just enqueues and returns, a burst piles up in the queue instead of overwhelming the workers, and if a worker or a downstream service is down the job waits and is retried instead of failing the user. It lets me scale producers and consumers independently.",
                    "It fits work the user does not need to wait for: emails, image processing, calls to flaky third parties, billing, fan-out. It does not fit when the caller needs the result right now. The costs are asynchrony, duplicates and ordering concerns, another component to operate, and less visibility. I would monitor depth, the age of the oldest message and the retry and dead-letter counts, and remember that a queue only smooths bursts: if the average arrival rate exceeds the processing rate the backlog grows forever, so I would scale consumers or shed load.\""],
            follow=[("How do you tell the user the work finished?", "Return a job id and let them poll a status endpoint, or push a notification (webhook, websocket, email) when it completes."),
                    ("How do you size the consumers?", "Consumers needed = arrival rate x time per job / concurrency per consumer, with headroom (the last lesson has the calculator)."),
                    ("What is a queue depth alert good for?", "Depth rising steadily means consumers are slower than producers; age of the oldest message shows the user-visible delay.")],
            slips=["Saying a queue \"makes it faster\": it makes the request faster by moving the work.", "Forgetting duplicates and retries.", "No monitoring of depth and age."],
        ),
        quick=[
            ("What three things does a queue decouple?", "Time, rate and failure between producer and consumer."),
            ("What does a rising queue depth tell you?", "Consumers are slower than producers: the backlog is growing."),
            ("Can a queue fix a system whose average load exceeds its capacity?", "No: it only smooths bursts; the backlog would grow without limit."),
        ],
        traps=[
            "Putting a queue on a path where the user needs the result: you added latency and complexity for nothing.",
            "No alert on queue age: the backlog grows silently until users complain.",
            "Assuming the queue makes the work reliable by itself: retries, duplicates and poison messages are yours to design.",
        ],
    ),
    dict(
        title="Delivery guarantees: at most once, at least once and the myth of exactly once",
        tier="hot",
        situation="A worker takes a payment job, charges the card, and crashes before telling the queue it finished. What should the queue do? Lose the job, or give it to another worker and charge twice? Every queue has to pick, and your handler has to survive the choice.",
        learn=["At-most-once and at-least-once, and what each risks", "Acknowledgements and visibility timeouts", "Why exactly-once delivery is not available, and what to do instead", "Idempotent consumers"],
        model=[
            "**At most once**: the queue hands over the message and forgets it. If the consumer crashes mid-work, the message is **lost**; there are never duplicates. **At least once**: the queue keeps the message until the consumer **acknowledges** it; if no ack arrives (a crash, a timeout) it redelivers: nothing is lost, but the same message can be processed **more than once**. This is the common default. With a **visibility timeout**, a taken message is hidden for a while; if not acked in time it reappears for another consumer.",
            "**Exactly once** delivery over an unreliable network is not achievable by a queue alone: after a crash the broker cannot know whether the work was done. What you can build is **exactly-once effect**: at-least-once delivery plus an **idempotent** handler, one whose repetition has no extra effect. Typical techniques: an **idempotency key** (a unique message id recorded when the work is done; a duplicate sees the record and skips), operations that are naturally idempotent (`set status = 'paid'` instead of `balance = balance - 10`), or a database unique constraint on the effect. Design every consumer as if each message could arrive twice.",
        ],
        analogy="A courier who needs a signature: if the recipient never signs, the courier brings the parcel again (at least once). Sometimes the recipient did receive it and just forgot to sign, so they get two parcels, unless the recipient checks the order number and returns the duplicate (idempotency).",
        visual=[DELIVERY_VIZ],
        sim=None,
        walk=[
            ("The consumer takes a message", "The queue moves it to an \"in progress\" state; it is not deleted yet."),
            ("The consumer does the work", "Charges the card, sends the email, updates the record."),
            ("The consumer acknowledges", "Only now does the queue delete the message."),
            ("If the consumer dies first", "No ack arrives; after the visibility timeout the message returns to the queue and another consumer takes it."),
            ("The duplicate must be harmless", "The second worker checks an idempotency key (or uses an idempotent operation) and does not repeat the side effect."),
        ],
        groups=[
            dict(title="Lose it, duplicate it, or make it safe", cmds=[
                dict(volatile=True, c=r'''. ~/q/rig.sh; qup; cd ~/q; cat > guarantees.py <<'EOF'
import sys
sys.path.insert(0, '.')
from rc import R
r = R()
effects = []                                    # the side effects that actually happened (for example, cards charged)
def run(label, take, finish, crash_when, idempotent=False):
    r.cmd('FLUSHALL'); effects.clear()
    for i in range(1, 6): r.cmd('RPUSH', 'jobs', 'job%d' % i)
    crashed = False
    while True:
        job = take()
        if job is None: break
        if idempotent and r.cmd('SET', 'done:' + job, '1', 'NX') is None: finish(job); continue   # already done: skip
        if job == 'job3' and not crashed:       # the worker dies while handling job3
            crashed = True
            if crash_when == 'after work': effects.append(job)        # ...after the side effect, before it could acknowledge
            if r.cmd('LLEN', 'processing'):     # at-least-once: after the visibility timeout the job comes back
                r.cmd('LMOVE', 'processing', 'jobs', 'LEFT', 'RIGHT')
            continue
        effects.append(job)                     # do the work
        finish(job)
    lost = sorted({'job%d' % i for i in range(1, 6)} - set(effects))
    dup = sorted({j for j in effects if effects.count(j) > 1})
    print('%-34s lost: %-6s duplicated effects: %s' % (label, lost or 'none', dup or 'none'))
# at most once: remove the job from the queue BEFORE working on it
def take_amo(): return r.cmd('LPOP', 'jobs')
run('at most once (crash before the work)', take_amo, lambda j: None, 'before work')
# at least once: move to a processing list, work, then acknowledge by removing it
def take_alo(): return r.cmd('LMOVE', 'jobs', 'processing', 'LEFT', 'RIGHT')
def ack(j): r.cmd('LREM', 'processing', 1, j)
run('at least once (crash after the work)', take_alo, ack, 'after work')
run('at least once + idempotent handler', take_alo, ack, 'after work', idempotent=True)
EOF
python3 guarantees.py; qdown''',
                     e="The three behaviours, each with the crash that hurts it most. **At most once**: the job was removed from the queue before the work, so when the worker dies mid-job the job is simply gone: `job3` is lost. **At least once**: the job stays in a processing list until acknowledged, so after the crash it is redelivered; but this worker had already done the work before dying, so `job3`'s effect happens twice. **At least once with an idempotent handler** (a `SET NX` marker per job) redelivers it and the duplicate is skipped, so every job takes effect exactly once. In real code the marker and the effect must be written in one transaction.",
                     annot=[("at most once (crash before the work) ... lost: ['job3']", "the job was taken from the queue before the crash: it is never redelivered and its effect never happens"),
                            ("at least once ... duplicated effects: ['job3']", "nothing lost, but the retried job repeated its side effect"),
                            ("at least once + idempotent handler ... lost: none, duplicated effects: none", "retry plus a duplicate check gives exactly-once effect")]),
            ]),
        ],
        scenario=dict(
            title="\"Can a message queue guarantee exactly-once delivery? How do you process payments safely from a queue?\"",
            ask="A classic trap. The strong answer says no, explains why, and shows how to get the effect anyway.",
            clarify=[("What is the side effect, and can it be repeated safely?", "Charging a card is not safe to repeat; setting a status to paid is.")],
            think=[("Answer the literal question.", "No. After a crash or timeout the broker cannot know whether the consumer finished, so it must choose between possibly losing the message (at most once) and possibly repeating it (at least once)."),
                   ("Pick at least once for payments.", "Losing a payment job is usually worse than repeating one, provided repeating is safe."),
                   ("Make repeating safe.", "Give every payment request a unique idempotency key. The handler records the key and the result in the same database transaction as the effect (or a unique constraint on the key). A duplicate delivery finds the key and returns the stored result."),
                   ("Cover the outside world.", "When calling a payment provider, pass the idempotency key to them too, so a retry does not charge twice."),
                   ("Handle poison and ordering.", "Limit retries with backoff and a dead-letter queue; do not let one bad message block the queue."),
                   ("Say what the broker may call exactly once.", "Some brokers advertise exactly-once within their own transactions (read, process, write back to the same system): useful, but it does not cover external side effects.")],
            answer=["\"No, not as a delivery guarantee: when a consumer crashes or times out the broker cannot know whether the work was done, so it must either risk losing the message or risk delivering it again. For payments I choose at least once, because losing a payment is worse, and make repeating it safe.",
                    "Every payment request carries a unique idempotency key. The handler stores the key and the outcome in the same database transaction as the effect, or relies on a unique constraint, so a duplicate delivery finds the key and returns the stored result instead of charging again. When I call the payment provider I pass the same key so their side is idempotent too. I add retries with backoff and a dead-letter queue so one poison message cannot block the rest. Some brokers offer exactly-once inside their own transactions, which helps for read-process-write within one system but does not cover external side effects.\""],
            follow=[("What is a visibility timeout and how do you choose it?", "How long a taken message stays hidden before being redelivered; longer than the normal processing time, shorter than the delay you can tolerate after a crash."),
                    ("What if the idempotency record is written but the effect fails?", "Write them in the same transaction so they succeed or fail together; for external effects, record intent first and reconcile."),
                    ("Why not just use a distributed transaction?", "Two-phase commit across a queue and an external service is rarely available and blocks on failure; idempotency is simpler and more robust.")],
            slips=["Claiming the queue gives exactly-once.", "Choosing at-most-once for money.", "An idempotency key stored in a different place or time from the effect."],
        ),
        quick=[
            ("What does at-least-once delivery risk?", "The same message may be processed more than once."),
            ("What does at-most-once delivery risk?", "A message can be lost if the consumer crashes after taking it."),
            ("How do you get exactly-once effect?", "At-least-once delivery plus an idempotent handler (an idempotency key or an idempotent operation)."),
        ],
        traps=[
            "Acking before the work is done: that is at-most-once with extra steps.",
            "Recording the idempotency key in a different transaction from the effect: a crash between them gives a duplicate or a loss.",
            "A visibility timeout shorter than the processing time: the job is delivered to two workers while the first is still running.",
        ],
    ),
    dict(
        title="Reliable events from a database: the outbox pattern and SQL job queues",
        tier="hot",
        situation="An order is saved to the database and an \"order placed\" event must reach other services. If the process crashes between the commit and the publish, the order exists and nobody ever hears of it. Two writes to two systems cannot be made atomic, so the pattern is to make it one write.",
        learn=["The dual-write problem", "The transactional outbox and the relay", "A job queue inside PostgreSQL with `FOR UPDATE SKIP LOCKED`", "When a database table is enough of a queue"],
        model=[
            "**Dual write**: save to the database, then publish to a broker. If you crash in between (or the broker is down), the data and the event disagree forever. Doing it in the other order has the mirror problem (an event for something that never committed). There is no way to make a database commit and a broker publish one atomic step.",
            "The **transactional outbox** removes the second write from the critical path: in **one database transaction**, write the business row **and** an event row in an `outbox` table. A separate **relay** process reads unsent outbox rows, publishes them, then marks them sent. Now the event exists if and only if the order does. The relay gives **at-least-once** publishing (a crash between publish and mark re-sends), so consumers must be idempotent. Alternatives to polling include change-data-capture from the database log. A related idea: a plain table can be a **job queue** using `select ... for update skip locked`, which lets many workers claim different rows without blocking each other: perfect when you already run a database and the volume is moderate, and the job can be created in the same transaction as the data.",
        ],
        analogy="Instead of saving the order and then phoning the warehouse (and hoping you do not get interrupted), you write the order and a note \"phone the warehouse\" in the same ledger entry. An assistant goes through the ledger, makes the calls, and ticks the notes off.",
        visual=[OUTBOX_SEQ],
        sim=None,
        walk=[
            ("Write both in one transaction", "Insert the order and the outbox event; commit. Either both exist or neither."),
            ("A relay finds unsent events", "It polls `select ... where sent = false order by id` (or follows the database log)."),
            ("Publish, then mark sent", "If it crashes between the two steps, the event is published again."),
            ("Consumers deduplicate", "Each event has a unique id; consumers skip ids they have processed."),
            ("Use SKIP LOCKED for SQL job queues", "Many workers can safely claim different rows at the same time."),
        ],
        groups=[
            dict(title="The lost event, the outbox, and SKIP LOCKED", cmds=[
                dict(volatile=True, c=r'''. ~/q/rig.sh; qup; pgup
pq -c "create table orders(id serial primary key, item text); create table outbox(id serial primary key, payload text, sent boolean default false)"
echo "--- naive dual write: commit the order, then publish; the process dies in between"
pq -c "insert into orders(item) values ('book')"
echo "(crash here: the publish never runs)"
echo "orders: $(pq -At -c 'select count(*) from orders')   events published: $(qcli llen events)"
echo "--- outbox: order and event in ONE transaction"
pq -c "begin; insert into orders(item) values ('pen'); insert into outbox(payload) values ('order_placed:pen'); commit;"
relay() { pq -At -c "select id || ' ' || payload from outbox where not sent order by id" | while read id payload; do qcli rpush events "$payload" </dev/null >/dev/null; [ "$1" = crash ] && { echo "(relay crashes after publishing $payload, before marking it)"; return; }; pq -c "update outbox set sent = true where id = $id"; done; }
relay crash
echo "events published so far: $(qcli llen events)   unsent outbox rows: $(pq -At -c 'select count(*) from outbox where not sent')"
echo "--- the relay restarts and publishes again:"
relay
echo "events in the broker: $(qcli lrange events 0 -1 | paste -sd' ')   (the same event twice: consumers must deduplicate)"
echo "unsent outbox rows: $(pq -At -c 'select count(*) from outbox where not sent')"
qdown; pgdown''',
                     e="The dual-write bug and its fix, step by step. In the naive version the order is saved and the process dies before publishing: **one order, zero events**, and nothing will ever repair it. With the outbox the event row is committed in the same transaction as the order, so it cannot be lost. The relay publishes it; when it is made to crash after publishing but before marking the row, the event is published **a second time** after the restart. That is the price of the pattern: at-least-once publishing, so consumers must treat the event id as an idempotency key.",
                     annot=[("orders: 1   events published: 0", "the commit succeeded and the event is lost: the two systems now disagree"),
                            ("relay crashes after publishing ..., before marking it", "the simulated failure window of the relay"),
                            ("events published so far: 1   unsent outbox rows: 1", "published but not marked: the row will be sent again"),
                            ("order_placed:pen order_placed:pen", "the event arrived twice: at-least-once, so consumers must deduplicate by event id")]),
                dict(volatile=True, c=r'''. ~/q/rig.sh; pgup
pq -c "create table jobs(id serial primary key, status text default 'new', worker text); insert into jobs(status) select 'new' from generate_series(1, 30)"
claim() { pq -At -c "with c as (select id from jobs where status = 'new' order by id limit 5 for update skip locked) update jobs set status = 'taken', worker = '$1' from c where jobs.id = c.id returning jobs.id" | sort -n | paste -sd' '; }
echo "--- three workers claim 5 jobs each, at the same time:"
for w in A B C; do ( echo "worker $w took: $(claim $w)" ) & done; wait
echo "jobs taken: $(pq -At -c "select count(*) from jobs where status = 'taken'")   distinct ids: $(pq -At -c "select count(distinct id) from jobs where status = 'taken'")   still new: $(pq -At -c "select count(*) from jobs where status = 'new'")"
pgdown''',
                     e="A job queue in a plain table. Three workers each ask for five unclaimed rows at the same moment. `for update skip locked` makes each worker **skip rows another worker has locked** instead of waiting for them, so the three claims never overlap: 15 distinct jobs taken, 15 still waiting. Without `skip locked` the workers would queue up behind each other's locks; without `for update` two workers could claim the same row. For moderate volumes this is a perfectly good queue, and the job can be inserted in the **same transaction** as the business data, which gives you the outbox guarantee for free.",
                     annot=[("worker A/B/C took: five ids each, all different", "skip locked gave each worker its own rows without blocking"),
                            ("jobs taken: 15   distinct ids: 15   still new: 15", "no row was claimed twice: no duplicates, no waiting")]),
            ]),
        ],
        scenario=dict(
            title="\"When an order is placed we must update the database and notify other services. How do you make sure we never lose the notification?\"",
            ask="The dual-write question. The expected answer is the outbox pattern, with its cost and its alternatives.",
            clarify=[("Is it acceptable for consumers to see an event twice? In order?", "Duplicates are almost always acceptable if consumers are idempotent; strict global order is rare and expensive.")],
            think=[("State the problem.", "Writing to the database and a broker are two separate operations; any crash or broker outage between them leaves them inconsistent."),
                   ("Reject the naive fixes.", "Publish first, then commit: an event for an order that may never exist. Commit then publish with a retry in memory: lost on crash. Distributed transaction: rarely available and fragile."),
                   ("Describe the outbox.", "Insert the order and an outbox row in one local transaction. A relay (poller or CDC) publishes unsent rows and marks them sent. The event exists if and only if the order does."),
                   ("State what it guarantees and costs.", "At-least-once publishing, so duplicates: consumers deduplicate by event id. Slight delay from polling (or CDC latency). The outbox table needs cleanup. Ordering per aggregate is preserved if the relay publishes in id order and partitions by aggregate id."),
                   ("Mention alternatives.", "CDC (Debezium reading the database log) instead of polling; event sourcing where the log is the source of truth; for small systems, a SKIP LOCKED jobs table as the queue itself."),
                   ("Say how to operate it.", "Monitor unsent row count and age; partition or purge old rows; make the relay horizontally safe with SKIP LOCKED.")],
            answer=["\"The problem is a dual write: the database commit and the broker publish cannot be one atomic step, so a crash between them leaves the order saved and the event lost. I would use the transactional outbox: in one local transaction I insert the order and an outbox row describing the event. A separate relay, either a poller or change data capture on the database log, publishes the unsent rows and marks them sent. The event exists exactly when the order does.",
                    "The trade-off is that publishing is at least once, because the relay can crash between publishing and marking, so consumers deduplicate on the event id. There is a small delay and the table needs cleanup. I keep per-order ordering by publishing in id order and partitioning by order id, and I monitor the number and age of unsent rows. For small systems I might even use a SKIP LOCKED jobs table as the queue itself.\""],
            follow=[("Polling or change data capture?", "Polling is simple and good for moderate volume; CDC reads the database log, has lower latency and no extra load on tables, but adds infrastructure."),
                    ("How do you keep events for one order in order?", "Publish outbox rows in id order, and partition by the order id so one consumer handles each order's events sequentially."),
                    ("What is the inbox pattern?", "The consumer-side mirror: record each processed event id in the same transaction as its effect, so duplicates are ignored.")],
            slips=["Publishing before committing.", "Forgetting that the outbox gives at-least-once and duplicates.", "Never cleaning up or monitoring the outbox table."],
        ),
        quick=[
            ("What is the dual-write problem?", "Updating a database and publishing an event are two operations that cannot be made atomic, so a crash can leave them inconsistent."),
            ("What does the outbox pattern guarantee?", "The event is saved if and only if the data is (same transaction); publishing is at least once."),
            ("What does `skip locked` do in a job queue?", "Lets many workers claim different rows at once without waiting on each other's locks."),
        ],
        traps=[
            "Publish-then-commit or commit-then-publish with no outbox: both can disagree after a crash.",
            "An outbox table that is never cleaned: it grows without bound and slows the relay.",
            "Using `select ... for update` without `skip locked` for a work queue: workers serialise behind one another.",
        ],
    ),
]
