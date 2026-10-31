"""S27 design warm-ups: part B (lessons 4 to 6: pastebin, rate limiter service, presenting in 45 minutes) and the module tail."""
import sysviz as v
from sys_warm2_a import RIG_REDIS

PASTE_VIZ = v.figure(
    720, 236,
    [v.box(10, 80, 100, 56, "Client", "ink"),
     v.arrow(110, 95, 160, 60), v.arrow(110, 120, 160, 160),
     v.box(160, 30, 140, 56, "POST /pastes", "warn", "hash the content"),
     v.box(160, 134, 140, 56, "GET /p/{id}", "warn", "cache, then store"),
     v.arrow(300, 58, 350, 58), v.arrow(300, 162, 350, 162),
     v.box(350, 30, 170, 56, "Metadata (SQL)", "acc", "id, owner, expiry, size, hash"),
     v.box(350, 134, 170, 56, "Cache (Redis)", "acc", "hot pastes"),
     v.arrow(520, 58, 560, 100), v.arrow(520, 162, 560, 120),
     v.box(560, 80, 150, 56, "Blob store", "ok", "content-addressed objects"),
     v.text(360, 218, "Small rows in a database, big bytes in an object store, hot reads in a cache, expiry as a background sweep.", "dg-s")],
    "Pastebin: metadata, blobs and a cache", "Separate what is small and queried from what is large and immutable")

PLAN_VIZ = v.figure(
    720, 226,
    [v.box(10, 30, 110, 56, "0-5 min", "acc", "requirements"),
     v.box(130, 30, 110, 56, "5-10 min", "acc", "estimates"),
     v.box(250, 30, 110, 56, "10-15 min", "acc", "API + data"),
     v.box(370, 30, 160, 56, "15-30 min", "ok", "architecture, then flows"),
     v.box(540, 30, 170, 56, "30-40 min", "ok", "deep dives and failures"),
     v.box(10, 110, 700, 56, "40-45 min: trade-offs, what you would do next, bottlenecks, monitoring, questions", "warn", "summarise decisions and what you would revisit with more time"),
     v.text(360, 200, "Drive the interview: say the plan, check in at each stage, and spend most of your time where the problem is hard.", "dg-s")],
    "A 45 minute design interview", "A time budget that leaves room for depth and for the interviewer's questions")

LESSONS_B = [
    dict(
        title="Design a pastebin: blobs, metadata, deduplication and expiry",
        tier="core",
        situation="\"Design Pastebin\" looks trivial until the follow-ups: how big can a paste be, how do you stop abuse, how do you expire millions of pastes without scanning the table, and how do identical pastes share storage?",
        learn=["Separating metadata from blob storage", "Content-addressed storage and deduplication", "Expiry as a background sweep (and lazy deletion)", "A cache for the few pastes that are read all the time"],
        model=[
            "Split the data by what it is: **metadata** (id, owner, created, expires, size, content hash, visibility) is small, structured and queried: a database row. The **content** is large, immutable and read by key: it belongs in an **object store** (S3-like) or a blob table, not in the database row where it bloats pages and backups. **Content-addressed storage** names each blob by the **hash of its content**: identical pastes (very common: logs, templates, copied snippets) are stored **once**, many metadata rows point to the same blob, and integrity is checkable. The read path is a **cache** (hot pastes are read thousands of times) in front of the metadata and blob lookups.",
            "**Expiry** is a real design point: scanning the whole table for expired rows is expensive. Do **lazy deletion** (a read of an expired paste returns 404 and removes it) plus a background **sweep** that deletes expired metadata in batches using an **index on `expires_at`**, and delete a blob only when **no metadata row references it** (reference counting or a periodic mark-and-sweep). Add **limits and abuse controls**: maximum size, rate limits per user and IP, content scanning for malware and secrets, unguessable ids for private pastes (the id is the capability), and a takedown mechanism. State the numbers: for example 1 million new pastes a day at 10 KB is 10 GB a day, 3.6 TB a year; reads at 10 to 1 are about 120 per second: modest.",
        ],
        analogy="A left-luggage office with a catalogue card for each ticket (metadata) and the actual bags on shelves (blobs). If two customers deposit identical suitcases, one suitcase can serve both tickets. Expired tickets are tidied away by a night shift, and a bag is only removed when no ticket points to it.",
        visual=[PASTE_VIZ],
        sim=None,
        walk=[
            ("Receive the paste and enforce limits", "Size cap, rate limit, optional scanning."),
            ("Hash the content", "The hash is the blob's address and the dedupe key."),
            ("Store the blob once, the metadata always", "If the hash exists, only a metadata row is added."),
            ("Serve reads through a cache", "Hot pastes from memory; misses read metadata then the blob."),
            ("Expire in the background", "Index on expiry, batch deletes, blob removed when unreferenced."),
        ],
        groups=[
            dict(title="Deduplication, expiry and caching, measured", cmds=[
                dict(volatile=True, c=r'''mkdir -p ~/warm && cd ~/warm && python3 - <<'EOF'
import hashlib, os, random, shutil, sqlite3, time
from collections import OrderedDict
rng = random.Random(4)
shutil.rmtree('blobs', ignore_errors=True); os.makedirs('blobs')
db = sqlite3.connect(':memory:')
db.execute('create table pastes(id integer primary key, hash text, size int, expires_at int)')
db.execute('create index pastes_exp on pastes(expires_at)')                    # makes the expiry sweep cheap
templates = ['error log line %d: connection refused\n' % i * 40 for i in range(300)]       # 300 distinct popular contents (logs, templates)
def new_content(i): return rng.choice(templates) if rng.random() < 0.45 else 'unique paste number %d: %s\n' % (i, 'x' * rng.randint(200, 3000))
now = 1_000_000; stored_bytes = logical_bytes = 0
for i in range(5000):
    data = new_content(i).encode(); h = hashlib.sha256(data).hexdigest(); logical_bytes += len(data)
    path = 'blobs/' + h[:2] + '_' + h[2:]
    if not os.path.exists(path): open(path, 'wb').write(data); stored_bytes += len(data)                 # store the blob only once
    db.execute('insert into pastes(hash, size, expires_at) values (?, ?, ?)', (h, len(data), now + rng.choice([60, 600, 3600, 86400])))
print('5000 pastes: %.1f MB submitted, %.1f MB actually stored (%.0f%% saved by content addressing)' % (logical_bytes / 1e6, stored_bytes / 1e6, 100 * (1 - stored_bytes / logical_bytes)))
# expiry sweep 10 minutes later: delete expired metadata in one indexed range delete, then blobs nobody references
later = now + 601
t = time.perf_counter(); n = db.execute('delete from pastes where expires_at < ?', (later,)).rowcount; el = (time.perf_counter() - t) * 1000
refs = {r[0] for r in db.execute('select distinct hash from pastes')}
removed = 0
for f in os.listdir('blobs'):
    h = f.replace('_', '')
    if h not in refs: os.remove('blobs/' + f); removed += 1
print('sweep: %d expired pastes deleted in %.1f ms (using the expiry index); %d orphan blobs removed, %d blobs kept (still referenced)' % (n, el, removed, len(os.listdir('blobs'))))
# a cache in front of reads: popularity is very skewed
ids = list(range(1, 3001)); weights = [1 / (i + 1) for i in range(len(ids))]
reqs = rng.choices(ids, weights, k=100000)
def hit_ratio(cap):
    c, hits = OrderedDict(), 0
    for k in reqs:
        if k in c: hits += 1; c.move_to_end(k)
        else:
            if len(c) >= cap: c.popitem(last=False)
            c[k] = 1
    return 100 * hits / len(reqs)
print('read cache: holding the hottest 5%% of pastes gives a %.0f%% hit ratio; 20%% gives %.0f%%' % (hit_ratio(150), hit_ratio(600)))
EOF''',
                     e="Three mechanisms in one run. **Content addressing** stores each distinct blob once: because almost half the pastes in this data set repeat popular contents, a large share of the bytes is never written twice. The **expiry sweep** deletes thousands of expired metadata rows in one indexed range delete (an index on `expires_at` is what avoids a full scan) and then removes only blobs that no remaining paste references. And a **cache** holding a small fraction of the pastes serves most reads, because popularity is heavily skewed. Together they answer the usual follow-ups: how do you save storage, how do you expire at scale, and how do you serve reads cheaply.",
                     annot=[("5000 pastes: 8.0 MB submitted, 4.9 MB actually stored (38% saved)", "duplicates share one blob"),
                            ("sweep: 2535 expired pastes deleted in 0.8 ms ... 1397 orphan blobs removed, 1655 blobs kept (still referenced)", "batch expiry through an index; blobs are removed only when nothing references them"),
                            ("read cache: hottest 5% of pastes gives a 53% hit ratio; 20% gives 73%", "skewed popularity makes a small cache effective")]),
            ]),
        ],
        scenario=dict(
            title="\"Design Pastebin. 1 million new pastes a day, expiry, and keep storage costs down.\"",
            ask="A warm-up that probes storage design, expiry and abuse handling more than scale.",
            clarify=[("Maximum paste size, retention options, private pastes, custom URLs, syntax highlighting, accounts?", "Assume: up to 10 MB, expiry from 10 minutes to never, unlisted pastes, anonymous allowed.")],
            think=[("Estimate.", "1M/day is about 12 writes per second; at 10 KB average that is 10 GB a day, about 3.6 TB a year (before deduplication and expiry). Reads at 10:1: about 120 per second. Small."),
                   ("API.", "`POST /pastes {content, expires_in, visibility}` returns `{id, url}`; `GET /p/{id}` returns the content; `DELETE /pastes/{id}` for owners."),
                   ("Data model.", "Metadata table (id, owner, hash, size, created, expires_at, visibility) in SQL or a key-value store; blobs in an object store keyed by content hash; ids are random 8-10 character base62 strings (unguessable for unlisted pastes)."),
                   ("Write path.", "Validate size, rate limit, hash content, store blob if new, insert metadata, return the id. Large pastes upload directly to the object store with a pre-signed URL."),
                   ("Read path.", "Cache by id (content is immutable, so the cache never needs invalidation except on delete or expiry); on a miss read metadata, check expiry, fetch the blob; serve through a CDN for popular public pastes."),
                   ("Expiry.", "Lazy check on read; background sweep using an index on expires_at; delete blobs when unreferenced; keep deletes in small batches to avoid load spikes."),
                   ("Abuse and safety.", "Per-IP and per-account rate limits, size limits, malware and secret scanning, abuse reports and takedown, no execution of content, content-type sniffing off."),
                   ("Cost.", "Object storage with lifecycle rules (cold tier for old pastes), deduplication, compression; capacity is cheap, requests and egress are the costs.")],
            answer=["\"At a million pastes a day that is about 12 writes per second and, at ten to one, about 120 reads per second, with roughly 10 gigabytes a day of content: a small system. I would split metadata from content: a table with the id, owner, content hash, size, expiry and visibility, and the bytes in an object store addressed by the hash of the content, so identical pastes are stored once. Ids are random base62 strings, which also make unlisted pastes unguessable.",
                    "Writes validate size, rate limit, hash, store the blob if new and insert the row; large uploads go straight to object storage with a pre-signed URL. Reads go through a cache and optionally a CDN: content is immutable, so caching needs no invalidation except on deletion or expiry. Expiry is lazy on read plus a background sweep over an index on the expiry time, deleting a blob only when nothing references it. I would add rate limits, size caps, scanning for malware and secrets, and a takedown path, and use storage lifecycle rules to move old pastes to a cold tier.\""],
            follow=[("How do you expire millions of pastes without scanning the table?", "An index on expires_at lets the sweep read only expired rows in batches; also lazy expiry on read; or partition the table by expiry date and drop whole partitions."),
                    ("Why is the id a capability for unlisted pastes?", "Anyone with the link can read it, so the id must be long and random; do not use sequential ids."),
                    ("How would you add editing or versions?", "A new immutable blob per version with a version list in metadata: content addressing already supports it, and the cache stays valid.")],
            slips=["Storing large content in the database row.", "A full table scan for expiry.", "Sequential ids for private pastes."],
        ),
        quick=[
            ("What is content-addressed storage?", "Storing each blob under the hash of its content, so identical content is stored once."),
            ("How do you expire many records cheaply?", "Index the expiry time and delete in batches (or drop time partitions), plus lazy deletion on read."),
            ("Why separate metadata from blobs?", "Small, queried rows suit a database; large immutable bytes suit an object store; mixing them bloats pages and backups."),
        ],
        traps=[
            "Deleting a blob when one paste expires although other pastes share it.",
            "Sequential ids on private content.",
            "No size and rate limits: the service becomes a free file host for abuse.",
        ],
    ),
    dict(
        title="Design a distributed rate limiter: atomic token buckets in Redis",
        tier="hot",
        situation="An API runs on forty servers. A customer is limited to 100 requests per second in total, not per server. The counters must be shared, and \"read the count, then write the new count\" will over-admit as soon as two servers do it at once. This is a concurrency problem as much as an algorithm.",
        learn=["Why check-then-update races", "A token bucket as a Lua script in Redis (atomic)", "Choosing keys, limits and failure behaviour", "Local approximation versus central accuracy"],
        model=[
            "A shared limiter keeps a counter per customer in a fast central store (Redis). The naive implementation, **GET the tokens, decide, SET the new value**, has a **race**: two servers read the same value, both admit, both write: the limit is exceeded under concurrency, exactly when it matters. The fix is to make the read-modify-write **atomic**: a **Lua script** executed by Redis runs without interleaving, so it can read the bucket, refill it by the elapsed time, take a token and write it back as one operation; or use atomic commands (`INCR` with expiry for fixed windows). A token bucket needs only two numbers per key (tokens and last refill time), so memory is tiny and the script is fast (tens of microseconds).",
            "Design decisions: the **key** (API key, user, IP, plus endpoint class), the **limits and tiers**, the **response** (`429` with `Retry-After` and `X-RateLimit-*` headers), where to **enforce** (gateway, before the work), and **failure behaviour** when Redis is down (usually **fail open** with a conservative local limit, because a limiter outage should not become an API outage; **fail closed** only for abuse-critical endpoints). For very high rates, avoid one hot key and one round trip per request with **local token buckets** that borrow batches of tokens from the central one (accuracy traded for latency), or **shard the limit** across servers. Expire idle keys so memory does not grow.",
        ],
        analogy="A single till with a single cashier: if two shop assistants each check the float in the drawer and both hand out the last note, the drawer is overdrawn. The fix is one person who checks and hands out in one motion, which is what the Lua script is.",
        sim=None,
        walk=[
            ("Choose the key and the limit", "Per customer and endpoint class, with a burst and a refill rate."),
            ("Run the check as one atomic script", "Refill by elapsed time, take a token if available, store, return allowed or retry-after."),
            ("Answer fast and clearly", "200 or 429 with Retry-After; never queue unbounded."),
            ("Decide what happens if the store is down", "Fail open with a local fallback, and alert."),
            ("Scale the hot path", "Local buckets that borrow tokens in batches for very high rates."),
        ],
        groups=[
            dict(title="A race you can see, and an atomic script that fixes it (real Redis)", cmds=[
                dict(c=RIG_REDIS,
                     e="Creates a minimal Redis client and helpers to start and stop a private Redis on port 6396. The same few lines of Python were used in the caching and queues modules: Redis speaks a simple text protocol, so no library is needed."),
                dict(volatile=True, c=r'''. ~/warm/rig.sh; redisup; cd ~/warm; cat > limiter.py <<'EOF'
import sys, threading, time
sys.path.insert(0, '.')
from rc import R
LIMIT = 10
NAIVE_SLEEP = 0.002                                   # a little work between the check and the update widens the race (real code has network and logic in between)
LUA = """
local tokens = tonumber(redis.call('HGET', KEYS[1], 't'))
local last = tonumber(redis.call('HGET', KEYS[1], 'ts'))
local cap, rate, now = tonumber(ARGV[1]), tonumber(ARGV[2]), tonumber(ARGV[3])
if tokens == nil then tokens = cap; last = now end
tokens = math.min(cap, tokens + (now - last) * rate)
local allowed = 0
if tokens >= 1 then tokens = tokens - 1; allowed = 1 end
redis.call('HSET', KEYS[1], 't', tokens, 'ts', now)
redis.call('PEXPIRE', KEYS[1], 60000)
return allowed
"""
def naive(r):
    t = r.cmd('GET', 'naive')
    if t is not None and int(t) > 0:
        time.sleep(NAIVE_SLEEP); r.cmd('SET', 'naive', int(t) - 1); return 1                 # read, decide, then write: NOT atomic
    return 0
def atomic(r):
    return r.cmd('EVAL', LUA, 1, 'bucket', LIMIT, 0, 1000)                                    # refill rate 0: only the initial 10 tokens exist
def run(fn, threads=30, calls=2):
    allowed = [0]; lock = threading.Lock()
    def work():
        r = R()
        for _ in range(calls):
            a = fn(r)
            with lock: allowed[0] += a
    ts = [threading.Thread(target=work) for _ in range(threads)]; [t.start() for t in ts]; [t.join() for t in ts]
    return allowed[0]
r = R(); r.cmd('FLUSHALL'); r.cmd('SET', 'naive', LIMIT)
print('limit: %d requests. 30 concurrent clients each try twice (60 attempts).' % LIMIT)
print('naive GET, decide, SET:        %2d requests admitted' % run(naive))
print('atomic Lua token bucket:       %2d requests admitted' % run(atomic))
EOF
python3 limiter.py; redisdown''',
                     e="The race, made visible. Thirty clients hit a limit of **ten** at the same instant. The **naive** limiter reads the counter, decides, and writes it back as three separate steps, so many clients read the same value and are all admitted: far more than ten get through (the exact number varies run to run, which is the nature of a race). The **Lua script** executes inside Redis as one uninterrupted operation, so the check and the update cannot interleave: **exactly ten** are admitted, however many clients arrive. Shared state needs atomic updates, not just shared storage.",
                     annot=[("limit: 10 requests. 30 concurrent clients each try twice (60 attempts).", "the setup: 60 attempts against a limit of 10"),
                            ("naive GET, decide, SET: 60 requests admitted (in this run every attempt; the exact number varies)", "the race: clients all saw the same remaining count and were all admitted"),
                            ("atomic Lua token bucket: 10 requests admitted", "the script ran atomically: the limit held exactly")]),
            ]),
        ],
        scenario=dict(
            title="\"Design a rate limiter that works across a fleet of API servers and handles 1 million requests per second.\"",
            ask="The distributed version of the rate limiter question: the algorithm is easy, the distribution and the failure modes are the point.",
            clarify=[("What do we limit by, how accurate must it be, and what happens at the limit: reject, queue or degrade?", "Assume per API key and endpoint class, small inaccuracy acceptable, reject with 429.")],
            think=[("Algorithm.", "Token bucket: bursts allowed, average enforced; two numbers per key."),
                   ("Centralised counters.", "A Redis cluster sharded by key; one atomic Lua script per check (refill, take, write); about 100,000 checks per second per Redis node, so 1 million per second needs ten or more shards, and consistent hashing by key."),
                   ("Reduce the central load.", "Local token buckets in each gateway that borrow a batch of tokens (for example 10 at a time) from the central bucket: far fewer round trips; the inaccuracy is bounded by the batch size times the number of gateways."),
                   ("Hot keys.", "One huge customer is one hot key: split their limit into sub-buckets per gateway or shard the bucket (divide the limit by N and spread)."),
                   ("Failure.", "Redis down or slow: fail open with a conservative local limit, alert; time-box the Redis call (a few milliseconds) so the limiter never adds more latency than a rejection would save."),
                   ("API behaviour.", "429 with Retry-After and X-RateLimit headers; limits visible to customers; tiers; allow-lists; separate limits for expensive endpoints."),
                   ("Operate.", "Metrics: allowed and rejected per key, limiter latency, Redis memory; configuration hot-reloadable; test with load and failure injection.")],
            answer=["\"I would use a token bucket per customer and endpoint class: it allows bursts and enforces an average, and needs only two numbers per key. The counters live in a sharded Redis, and every check is one Lua script that refills, takes a token and writes back atomically, because a read-then-write check races under concurrency and over-admits. A Redis node handles on the order of a hundred thousand such checks a second, so a million per second needs a dozen shards by consistent hashing of the key.",
                    "To cut the central load, each gateway keeps a local bucket that borrows a small batch of tokens from the central one, trading a bounded inaccuracy for far fewer round trips, and a hot customer's bucket is split across sub-buckets. If Redis is slow or down I fail open with a conservative local limit and an alert, with a few millisecond timeout so the limiter never costs more than it saves. Rejected calls get 429 with Retry-After and rate-limit headers, and I monitor allowed and rejected counts per key and limiter latency.\""],
            follow=[("Why a Lua script and not a transaction with WATCH?", "The script is simpler, faster and cannot be interleaved; optimistic transactions with WATCH retry under contention, which is exactly when many clients hit one hot key."),
                    ("Fixed window, sliding window or token bucket?", "Fixed window is cheapest but allows 2x bursts at the boundary; sliding window is accurate but costs more memory; token bucket gives bursts plus an average and is the usual choice."),
                    ("How accurate is the local-bucket approach?", "Error is bounded by the batch size times the number of gateways; choose the batch so the worst case overshoot is acceptable.")],
            slips=["Describing GET then SET as if it were safe.", "A single Redis key as a global bottleneck at a million requests per second.", "Failing closed when the limiter store is unavailable."],
        ),
        quick=[
            ("Why does GET-then-SET over-admit under concurrency?", "Several clients read the same value before any writes it back, so all are admitted."),
            ("How does a Lua script in Redis help?", "It runs atomically, so refill, take and write cannot interleave with other clients."),
            ("What should happen when the limiter's store is down?", "Usually fail open with a conservative local limit and an alert."),
        ],
        traps=[
            "Per-server counters with no sharing: the real limit is N times higher.",
            "One hot key for the busiest customer: use sub-buckets.",
            "A slow Redis call on the request path with no timeout.",
        ],
    ),
    dict(
        title="Presenting a design in 45 minutes: structure, time and what interviewers look for",
        tier="hot",
        situation="You know the building blocks. In the interview you have 45 minutes, a blank whiteboard and a vague prompt. Candidates with the same knowledge get very different results depending on how they structure and drive the conversation.",
        learn=["A time budget that works", "How to open: requirements and estimates", "How to move from boxes to depth", "Common failure patterns and how to avoid them"],
        model=[
            "A design interview evaluates **how you think**: clarifying an ambiguous problem, choosing what matters, estimating, designing at the right level, reasoning about trade-offs and failure, and communicating while collaborating. A reliable structure: **requirements** (functional and non-functional, scope, scale), **estimates** (QPS, storage, bandwidth), **API and data model**, **high-level design** (the main flows end to end), then **deep dives** on the one or two hardest parts, **failure handling and scaling**, and a **summary of trade-offs**. Say the plan out loud at the start and check in at each stage; the interviewer will steer you towards what they care about.",
            "What distinguishes strong answers: **numbers** that justify choices (\"4,000 reads per second, so one cache tier is enough\"); **trade-offs stated explicitly** (\"counters are collision-free but guessable; I would scramble them\"); **depth where it is hard** (not equal time on every box); **failure thinking** (what happens when this node, this queue, this region dies); and **adaptability** (a new requirement changes the design and you can say how). Common failures: jumping to a solution before clarifying, **naming technologies without reasons** (\"use Kafka\"), drawing a diagram and stopping, ignoring the numbers, spending 30 minutes on one component, never considering failure, and being defensive about challenges. Treat the interviewer as a colleague: ask, propose, check, adjust.",
        ],
        analogy="A guided tour: say the route at the start, point out the highlights rather than every room, linger where the interesting exhibit is, and pause for the visitor's questions rather than reciting a script.",
        visual=[PLAN_VIZ],
        sim=None,
        walk=[
            ("Clarify the problem (5 minutes)", "Functional scope, users, scale, what is out of scope; write it down."),
            ("Estimate (5 minutes)", "Requests per second, storage, bandwidth: enough to choose a shape."),
            ("API and data model (5 minutes)", "The few endpoints and entities that matter."),
            ("High-level design (15 minutes)", "Draw the main flows; name the components and why each exists."),
            ("Deep dives and failure (10 minutes)", "The hardest part, bottlenecks, failure modes, scaling."),
            ("Wrap up (5 minutes)", "Summarise decisions and trade-offs; what you would improve; monitoring."),
        ],
        groups=[
            dict(title="A time plan and a numbers drill", cmds=[
                dict(c=r'''python3 - <<'EOF'
plan = [('Clarify requirements and scope', 5), ('Estimates (QPS, storage, bandwidth)', 5), ('API and data model', 5),
        ('High-level design, end-to-end flows', 15), ('Deep dives: the hard parts, bottlenecks, failures', 10), ('Wrap-up: trade-offs, next steps, monitoring', 5)]
t = 0
print('minute  stage')
for name, m in plan:
    print('%2d-%2d   %s  (%d min)' % (t, t + m, name, m)); t += m
print('total %d minutes. Rule of thumb: if you are at minute 20 and still on estimates, say so and move on.' % t)
print()
print('Numbers worth knowing by heart (orders of magnitude):')
rows = [('1 million requests per day', '12 requests/s'), ('100 million requests per day', '1,200 requests/s'), ('1 billion requests per day', '12,000 requests/s'),
        ('1 KB x 1 million items', '1 GB'), ('1 KB x 1 billion items', '1 TB'), ('seconds in a day', '86,400 (about 10^5)'), ('seconds in a year', '31.5 million (about 3 x 10^7)'),
        ('read from memory', '~100 ns'), ('SSD random read', '~100 microseconds'), ('round trip in one data centre', '~0.5 ms'), ('round trip across an ocean', '~150 ms')]
for a, b in rows: print('  %-32s %s' % (a, b))
EOF''',
                     e="A concrete time budget and the numbers to keep in your head. The budget gives half the time to the high-level design and the deep dives, because that is where the evaluation happens; estimates take five minutes, not twenty. The reference table lets you turn \"100 million requests a day\" into \"about 1,200 per second\" in your head, which is usually the number that decides whether you need one server, a cache or a sharded database. Practise saying the numbers out loud with the conclusion attached.",
                     annot=[("0- 5   Clarify requirements and scope (5 min)", "ambiguity is deliberate: ask first"),
                            ("20-30   Deep dives ... (10 min)", "spend the depth where the problem is hard"),
                            ("100 million requests per day = 1,200 requests/s", "the conversion you will use in every estimate"),
                            ("round trip across an ocean ~150 ms", "latency numbers explain why caches, CDNs and regions exist")]),
            ]),
        ],
        scenario=dict(
            title="\"You get 'Design a news feed' with 45 minutes. How do you spend them, and what will the interviewer be looking for?\"",
            ask="A meta question, often asked implicitly. The answer is a plan plus judgement about where to go deep.",
            clarify=[("Does the interviewer have a preference for depth areas? Is there a particular scale or constraint?", "Ask in the first minutes; adapt the deep dives to what they care about.")],
            think=[("Open with the plan.", "\"I will spend about five minutes on requirements, five on estimates, then API and data, then the high-level design, and use the rest for the hardest parts and failure.\""),
                   ("Requirements.", "Feed content (posts from people you follow), read versus write volumes, freshness expectations, ranking, media, followers per user, global or regional."),
                   ("Estimates.", "Users, posts per day, follows, feed reads per second, fan-out cost; conclude which part is hard (the fan-out for celebrities)."),
                   ("Design.", "Post service, graph store, feed generation (fan-out on write versus read, hybrid), feed cache, ranking, media via CDN."),
                   ("Deep dive.", "The celebrity problem and hybrid fan-out; or ranking freshness; choose with the interviewer."),
                   ("Failure and scale.", "Queue backlogs, cache loss, regional failover, hot keys, abuse."),
                   ("Wrap up.", "Trade-offs (write amplification versus read latency, freshness versus cost), what you would measure, what you would do with more time.")],
            answer=["\"I would start by saying how I will use the time: about five minutes on requirements and scope, five on estimates, a few on the API and data model, then fifteen on the high-level design and the rest on the hardest part and on failures, finishing with trade-offs. Then I would clarify the problem: whose posts appear, how many followers, how fresh the feed must be, whether it is ranked, and what scale we have.",
                    "From the estimates I would find the hard part, probably the fan-out for users with millions of followers, and say so. I would draw the post and graph services, feed generation with a hybrid of fan-out on write for ordinary users and on read for celebrities, a feed cache, ranking and the CDN for media. I would go deep where the interviewer shows interest or where the problem is hardest, discuss what happens when queues back up or a cache is lost, and finish with the trade-offs and what I would measure and improve with more time.\""],
            follow=[("What if I run out of time?", "Say what you would cover next, and make sure the end-to-end flow exists before the deep dives; a complete simple design beats a half-finished sophisticated one."),
                    ("What if the interviewer disagrees with your choice?", "Treat it as information: ask what constraint they have in mind, compare the options on that constraint and adapt; do not defend by default."),
                    ("How do you handle a topic you do not know?", "Say what you do know, reason from first principles about requirements and trade-offs, and be explicit about assumptions: honesty plus reasoning scores well.")],
            slips=["Jumping straight into boxes without requirements or numbers.", "Naming technologies without reasons.", "Never mentioning failures or trade-offs."],
        ),
        quick=[
            ("Roughly how many requests per second is 100 million requests per day?", "About 1,200 per second."),
            ("Where should most of your time go in a 45-minute design interview?", "The high-level design and the deep dives on the hardest parts, with failures and trade-offs."),
            ("What is a common sign of a weak answer?", "Naming technologies without reasons, or never discussing failure and trade-offs."),
        ],
        traps=[
            "Spending half the interview on estimates or on one component.",
            "A diagram with no flows: it never shows how a request actually moves.",
            "Defending a choice instead of exploring the interviewer's constraint.",
        ],
    ),
]

TAIL = dict(
    cases=[],
    cheat=[
        ["estimate first", "writes/s, reads/s, storage, bandwidth: the numbers choose the shape"],
        ["URL shortener codes", "base62; 7 chars = 3.5 trillion; counters (ranges) have no collisions, hashes collide (birthday)"],
        ["301 vs 302", "cached permanent (no analytics) vs temporary (counted, editable)"],
        ["analytics", "asynchronous through a queue, never on the redirect path"],
        ["Snowflake", "41 bits time, 10 machine, 12 sequence: unique, time-ordered, 64-bit"],
        ["clock backwards", "wait or refuse; never keep issuing IDs"],
        ["UUID v4 vs ordered IDs", "random keys scatter B-tree inserts; time-ordered append"],
        ["KV store write path", "WAL, memtable, ack; flush to sorted files; tombstones; compaction"],
        ["KV recovery", "replay the WAL: every acknowledged write returns"],
        ["KV distribution", "consistent hashing + N replicas + quorums + repair"],
        ["pastebin", "metadata in SQL, bytes in an object store, content-addressed, cache, expiry sweep"],
        ["expiry", "lazy on read + indexed batch sweep; delete a blob when unreferenced"],
        ["rate limiter race", "GET/SET over-admits; use an atomic Lua script or atomic commands"],
        ["limiter failure", "fail open with a local fallback, alert"],
        ["limiter scale", "shard keys; local buckets borrowing token batches; sub-buckets for hot keys"],
        ["45-minute plan", "5 requirements, 5 estimates, 5 API/data, 15 design, 10 deep dive, 5 wrap-up"],
        ["numbers", "100M/day = 1,200/s; 1KB x 1B = 1TB; cross-ocean RTT 150 ms"],
        ["state trade-offs", "every choice: what it buys, what it costs, when you would change it"],
    ],
    interview_intro="Warm-up designs are judged on structure and numbers: clarify, estimate, choose with reasons, go deep where it is hard, and name failures and trade-offs. Practise each scenario aloud against the clock; the written answers are models, not scripts.",
    interview=[
        dict(q="Design a URL shortener.",
             a=["Requirements and estimates: 100M new URLs a month is ~40 writes/s, ~4,000 reads/s, ~3 TB over five years.", "7 base62 characters from a counter with leased ranges (no collisions) versus hashes (birthday collisions, retry); key-value store sharded by code; Redis cache; 302 and async click analytics.", "Failure: replicated store, leased ranges survive the ID service outage; abuse checks, rate limits, expiry."],
             follow=["Guessable codes?", "301 or 302?"], mistakes=["No numbers.", "Hashing without collision handling.", "Synchronous analytics."],
             angle="Reported by candidates as the most common first design question at large companies; not official."),
        dict(q="Design a unique ID generator for 100,000 IDs per second.",
             a=["Clarify unique versus sortable versus sequential; reject auto-increment (single writer) and UUID v4 (random, 128 bits, bad locality).", "Snowflake: 41-bit time, 10-bit machine id, 12-bit sequence: 4,096 per ms per machine; machine ids leased; clock handling (wait or refuse); sequence overflow waits.", "Roughly ordered only across machines: use per-entity sequences for strict order."],
             follow=["Duplicate machine ids?", "Gap-free numbers?"], mistakes=["Using timestamps as a strict global order."]),
        dict(q="Design a key-value store.",
             a=["Single node: WAL, memtable, flush to sorted files, tombstones, compaction, Bloom filters, recovery by log replay.", "Distributed: consistent hashing with virtual nodes, N=3 replicas across zones, tunable quorums, version vectors, read repair, hinted handoff, gossip, Merkle repair.", "Trade-offs: AP by default, no multi-key transactions, ranges need ordered partitioning."],
             follow=["How does it survive a crash?", "Why tombstones?"], mistakes=["Skipping durability.", "Hash mod N with no rebalancing plan."],
             angle="Amazon-style: expect follow-ups on Dynamo concepts such as hinted handoff and quorums; reported by candidates, not official."),
        dict(q="Design Pastebin with a million new pastes a day.",
             a=["~12 writes/s, ~120 reads/s, ~10 GB/day: small.", "Metadata in a database, content in an object store addressed by hash (dedupe), random ids, cache, optional CDN.", "Expiry: lazy plus indexed batch sweep; delete blobs when unreferenced; limits, scanning, takedown; lifecycle to cold storage."],
             follow=["Expiring millions of pastes?", "Versions?"], mistakes=["Blobs in database rows.", "Full scans for expiry."]),
        dict(q="Design a distributed rate limiter for a fleet doing a million requests per second.",
             a=["Token bucket per key; atomic Lua script in sharded Redis (GET/SET races); consistent hashing of keys.", "Local buckets borrowing token batches, sub-buckets for hot keys; fail open with local fallback and a timeout.", "429 with Retry-After and headers; metrics per key; tiers."],
             follow=["Why Lua rather than WATCH?", "How accurate is local borrowing?"], mistakes=["Check-then-update races.", "Single hot key."],
             angle="Google-style: candidates commonly report follow-ups on accuracy versus latency; reported by candidates, not official."),
        dict(q="How do you structure and pace a 45-minute design interview?",
             a=["State the plan: requirements, estimates, API and data, high-level design, deep dives and failure, wrap-up.", "Numbers that justify choices, trade-offs stated, depth where it is hard, failure thinking, adaptability.", "Avoid: jumping to solutions, technologies without reasons, equal time on every box, ignoring failures, being defensive."],
             follow=["What if you run out of time?", "What if the interviewer disagrees?"], mistakes=["No requirements or numbers."]),
    ],
    selftest=[
        ("How many base62 characters give about 3.5 trillion codes?", "Seven."),
        ("Why do hashed short codes collide early?", "The birthday paradox: collisions appear around the square root of the space."),
        ("301 versus 302 for a shortener?", "301 is cached permanently (no analytics, fixed target); 302 is temporary (counted, editable)."),
        ("What are the parts of a Snowflake ID?", "41-bit timestamp, 10-bit machine id, 12-bit sequence."),
        ("What must a generator do if the clock goes backwards?", "Wait or refuse to issue IDs."),
        ("Why are random UUIDs poor primary keys?", "They scatter inserts across the B-tree."),
        ("Why write to the WAL before the memtable?", "So acknowledged writes survive a crash."),
        ("What is a tombstone?", "A marker for a delete in an immutable-file store, removed later by compaction."),
        ("What is content-addressed storage?", "Blobs named by the hash of their content: identical content is stored once."),
        ("How do you expire many records cheaply?", "Index the expiry time, batch deletes, and expire lazily on read."),
        ("Why does GET-then-SET over-admit?", "Concurrent clients read the same value before any writes it back."),
        ("What is the usual limiter failure mode?", "Fail open with a local fallback and an alert."),
        ("How long is 100 million requests per day per second?", "About 1,200 requests per second."),
    ],
    recall=[
        ["base62 x7", "3.5 trillion"],
        ["counter vs hash", "no collisions vs birthday"],
        ["302", "counted and editable"],
        ["Snowflake", "41/10/12 bits"],
        ["clock back", "refuse"],
        ["WAL", "log first, replay on crash"],
        ["tombstone", "delete marker"],
        ["content address", "hash is the name"],
        ["Lua", "atomic check and update"],
        ["fail open", "limiter outage is not an API outage"],
        ["100M/day", "1,200/s"],
    ],
    sources=[
        dict(title="System design primer (GitHub, donnemartin)", url="https://github.com/donnemartin/system-design-primer", use="Worked examples for URL shortener, pastebin and others to compare approaches", license="CC BY 4.0; read online", how="Link only"),
        dict(title="Twitter Snowflake (announcement and design)", url="https://github.com/twitter-archive/snowflake", use="The original 64-bit ID layout", license="Apache 2.0; read online", how="Link only"),
        dict(title="RFC 9562: UUIDs (including UUID version 7)", url="https://www.rfc-editor.org/rfc/rfc9562", use="Time-ordered UUIDs", license="IETF; read online", how="Link only"),
        dict(title="LevelDB implementation notes", url="https://github.com/google/leveldb/blob/main/doc/impl.md", use="Write-ahead log, memtable, sorted files and compaction in a real LSM store", license="BSD licence; read online", how="Link only"),
        dict(title="Redis documentation: EVAL and scripting", url="https://redis.io/docs/latest/develop/interact/programmability/eval-intro/", use="Atomic Lua scripts used in the limiter", license="Copyright Redis; read online", how="Link only"),
        dict(title="Stripe: Scaling your API with rate limiters", url="https://stripe.com/blog/rate-limiters", use="Token buckets and load shedding in production", license="Copyright Stripe; read online", how="Link only"),
    ],
    plan=[
        "**Hours 1 to 2:** URL shortener: change the volumes and recompute the numbers; implement the range-leasing in a few lines; then the short-code lab.",
        "**Hours 3 to 4:** IDs: change the bit widths and check the capacity; then the snowflake-id lab.",
        "**Hours 5 to 6:** key-value store: add a Bloom filter to the toy store and count skipped file reads; kill and recover again.",
        "**Hours 7 to 8:** pastebin: change the duplicate rate and the expiry mix and re-measure.",
        "**Hour 9:** rate limiter: add a refill rate and verify the admitted count over time.",
        "**Hours 10 and 11:** presenting: time yourself giving each scenario answer in 5 minutes aloud, then in 45 as a full design.",
    ],
)
