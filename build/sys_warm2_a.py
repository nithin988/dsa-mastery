"""S27 design warm-ups: part A (lessons 1 to 3: URL shortener, unique IDs, key-value store)."""
import sysviz as v

SHORT_VIZ = v.figure(
    720, 250,
    [v.box(10, 80, 100, 56, "Client", "ink"),
     v.arrow(110, 95, 160, 60), v.arrow(110, 120, 160, 160),
     v.box(160, 30, 150, 56, "POST /urls", "warn", "create a short code"),
     v.box(160, 134, 150, 56, "GET /abc123", "warn", "redirect (read path)"),
     v.arrow(310, 58, 360, 58), v.arrow(310, 162, 360, 162),
     v.box(360, 30, 130, 56, "ID generator", "acc", "counter / range"),
     v.arrow(425, 86, 425, 110), v.box(360, 110, 130, 56, "Key-value store", "ok", "code to long URL"),
     v.box(530, 134, 180, 56, "Cache (Redis)", "acc", "hot codes: 90%+ of reads"),
     v.arrow(490, 162, 530, 162),
     v.text(360, 226, "Reads outnumber writes 100 to 1: the read path is a cache, the write path is an ID and a row.", "dg-s")],
    "URL shortener: the whole system on one page", "A short write path, a very hot read path, and a code space that must not collide")

KV_VIZ = v.figure(
    720, 236,
    [v.box(10, 20, 150, 52, "put(k, v)", "ink", ""),
     v.arrow(160, 46, 200, 46), v.box(200, 20, 150, 52, "1. append to the WAL", "warn", "on disk, sequential"),
     v.arrow(350, 46, 390, 46), v.box(390, 20, 150, 52, "2. update the memtable", "acc", "sorted, in memory"),
     v.arrow(540, 46, 580, 46), v.box(580, 20, 130, 52, "3. acknowledge", "ok", ""),
     v.box(200, 110, 150, 52, "Crash?", "bad", "memory is lost"),
     v.arrow(275, 110, 275, 90),
     v.box(390, 110, 320, 52, "Recovery: replay the WAL into a new memtable", "ok", "every acknowledged write is back"),
     v.text(360, 200, "A full memtable is flushed as an immutable sorted file; reads check memtable, then files newest to oldest.", "dg-s"),
     v.text(360, 222, "Across machines: partition keys by consistent hashing and replicate each key to N nodes.", "dg-s")],
    "A single-node key-value store", "Write-ahead log for durability, memtable for speed, sorted files for scale")

RIG_REDIS = r'''mkdir -p ~/warm && cd ~/warm && cat > rc.py <<'EOF'
# A minimal Redis client (the Redis wire protocol is simple text), so the experiments need nothing but python3.
import socket
class R:
    def __init__(self, port=6396):
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
export W=$HOME/warm
redisup()   { redis-server --port 6396 --bind 127.0.0.1 --save "" --appendonly no --daemonize yes --dir $W --logfile $W/redis.log >/dev/null; sleep 0.5; }
redisdown() { redis-cli -p 6396 shutdown nosave 2>/dev/null; sleep 0.3; true; }
EOF
. ./rig.sh; echo "rig ready in $W: rc.py (tiny Redis client) and rig.sh (redisup, redisdown)"'''

LESSONS_A = [
    dict(
        title="Design a URL shortener: from requirements to numbers to a system",
        tier="hot",
        situation="\"Design a URL shortener\" is the most common first system design question, and the most often answered badly: a box diagram with no numbers. This lesson builds the answer the way you should give it: requirements, estimates, code space, collisions, redirects, scaling and failure.",
        learn=["Requirements, estimates and the read to write ratio", "How many characters a code needs (and what base62 gives)", "Collisions: random codes versus counters, measured", "301 versus 302 and what analytics needs"],
        model=[
            "**Requirements.** Functional: create a short code for a long URL, redirect from the code, optionally custom aliases, expiry and click analytics. Non-functional: redirects must be **fast and highly available** (they sit in every link that is shared), writes can be slower, links must not collide, and codes should not be guessable if URLs are private. **Estimates**: say 100 million new URLs a month is about **40 writes per second**; with a read to write ratio of 100 to 1 that is about **4,000 redirects per second** (peaks 5 to 10 times higher); at 500 bytes per record, five years is about 3 TB: modest. The shape is **read-heavy and key-value**: a cache in front of a simple store covers it.",
            "**The code.** A code of length *n* in base62 (a-z, A-Z, 0-9) has 62ⁿ values: 6 characters give 56.8 billion, 7 give 3.5 trillion. Two ways to choose codes: **random or hashed codes** (hash the URL and truncate) can **collide**: by the birthday paradox, collisions appear much earlier than the size of the space suggests, so you must detect and retry; **counter-based codes** (a unique number from an ID generator, encoded in base62) never collide, are short, but are **sequential and guessable** unless you scramble them (a reversible permutation) and need a distributed counter (hand out **ranges** of numbers to each app server). **301** (permanent) redirects are cached by browsers, which saves load but hides later clicks from your analytics; **302** (temporary) hits you every time and lets you count and change the target. Click analytics should be **asynchronous** (a queue), never on the redirect path.",
        ],
        analogy="A coat-check: you hand in a coat (the long URL) and get a small numbered ticket (the code). The numbers must never be reused while the coat is there, handing out tickets must be quick, and finding a coat from its ticket must be instant, because everyone is waiting at the counter.",
        visual=[SHORT_VIZ],
        sim=None,
        walk=[
            ("Clarify and estimate", "Writes per second, redirects per second, retention, custom aliases, analytics: the numbers drive the design."),
            ("Choose the code space and scheme", "Length from the capacity table; counters (no collisions) or random with retry."),
            ("Define the API and data model", "POST creates, GET redirects; one row per code: code, long URL, created, expiry, owner."),
            ("Make reads fast and available", "A cache in front (hot codes), replicas, a CDN or edge for the redirect itself."),
            ("Handle abuse, analytics and failures", "Rate limits, malware checks, async click counting, what happens when the ID generator is down."),
        ],
        groups=[
            dict(title="Capacity, collisions and redirects, measured", cmds=[
                dict(c=r'''mkdir -p ~/warm && cd ~/warm && python3 - <<'EOF'
import math
ALPHA = 62
print('code length  distinct codes        years of supply at 100 million new URLs a month')
for n in (5, 6, 7, 8):
    codes = ALPHA ** n
    print('%6d       %-20s  %s' % (n, '{:,}'.format(codes), '%.1f' % (codes / 1.2e9) if codes / 1.2e9 < 1e6 else 'practically forever'))
print()
writes = 100e6 / (30 * 86400); reads = writes * 100
print('100 million new URLs a month = %.0f writes/s;  at 100:1 reads = %.0f redirects/s (peak 10x: %.0f/s)' % (writes, reads, reads * 10))
print('storage: 500 bytes x 100M x 12 x 5 years = %.1f TB' % (500 * 100e6 * 12 * 5 / 1e12))
def b62(n):
    chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'; s = ''
    while n: n, r = divmod(n, 62); s = chars[r] + s
    return s or '0'
print('counter values -> codes:  1 -> %s   1,000,000 -> %s   56,800,000,000 -> %s   3,521,614,606,207 -> %s' % (b62(1), b62(10**6), b62(56_800_000_000), b62(62**7 - 1)))
EOF''',
                     e="The numbers an interviewer wants to hear in the first five minutes. At 100 million new URLs a month the system sees only about **40 writes per second** and **4,000 redirects per second** (peaks ten times higher): small by large-system standards, which is why the design is a cache plus a simple store, not a heroic distributed database. **Six** base62 characters give 56.8 billion codes, nearly 50 years of supply at that rate; seven give effectively forever. A counter encoded in base62 yields short codes with no collisions at all.",
                     annot=[("6      56,800,235,584 ... 47.3 years", "six characters already outlast any realistic plan"),
                            ("100 million new URLs a month = 39 writes/s; ... 3858 redirects/s (peak 10x: 38580/s)", "read heavy, and small: one cache tier handles the peak"),
                            ("storage: ... 3.0 TB", "modest: fits on a few nodes even with replication"),
                            ("counter values -> codes: 1 -> 1   1,000,000 -> 4c92   ...", "base62 encoding of a counter: short codes, no collisions")]),
                dict(volatile=True, c=r'''cd ~/warm && python3 - <<'EOF'
import hashlib, random, sqlite3, time
chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
def b62(n, width):
    s = ''
    for _ in range(width): n, r = divmod(n, 62); s += chars[r]
    return s
# 1. truncated hashes: the birthday paradox in action (5-character codes: 916 million possibilities, only 100,000 URLs)
N, W = 100_000, 5
seen, collisions = {}, 0
for i in range(N):
    url = 'https://example.com/page/%d' % i
    code = b62(int(hashlib.sha256(url.encode()).hexdigest(), 16), W)
    if code in seen: collisions += 1
    seen[code] = url
expected = N * N / (2 * 62 ** W)
print('hashing %d URLs into %d-character codes (%s possible): %d collisions (the birthday estimate predicts about %.1f)' % (N, W, '{:,}'.format(62 ** W), collisions, expected))
print('even a tiny fraction of the space in use produces collisions: you must detect and retry, or avoid hashing.')
# 2. a fuller space: 4-character random codes with 300,000 already stored; each insert may need retries
db = sqlite3.connect(':memory:'); db.execute('create table urls(code text primary key, url text)')
rng = random.Random(1); t = time.perf_counter(); retries = 0
for i in range(300_000):
    while True:
        code = ''.join(rng.choice(chars) for _ in range(4))
        try: db.execute('insert into urls values (?, ?)', (code, 'u%d' % i)); break
        except sqlite3.IntegrityError: retries += 1                        # the database enforces uniqueness: retry with a new code
print('inserting 300,000 random 4-character codes (14.8 million possible): %d retries needed (%.1f%% of inserts) in %.1f s' % (retries, 100 * retries / 300_000, time.perf_counter() - t))
# 3. counters never collide
db.execute('create table c(code text primary key)'); n = 0
for i in range(300_000): db.execute('insert into c values (?)', (b62(i + 1, 4),)); n += 1
print('300,000 counter-based 4-character codes: %d inserts, 0 retries, zero collisions by construction' % n)
EOF''',
                     e="Why \"just hash the URL\" is a trap. Hashing 100,000 URLs into five characters (916 million possible codes, so the space is 99.99 percent empty) still produces **a handful of collisions**, as the birthday formula predicts: n²/2m. A fuller code space needs constant retries: the database's `primary key` constraint is the safety net that makes retrying correct, because two requests can never insert the same code. A **counter** encoded in base62 has no collisions at all, which is why most real designs use one (often allocating ranges of numbers to each application server so no central bottleneck exists), scrambling the order if codes must not be guessable.",
                     annot=[("hashing 100000 URLs into 5-character codes (916,132,832 possible): 7 collisions (the birthday estimate predicts about 5.5)", "collisions appear long before the space is full"),
                            ("inserting 300,000 random 4-character codes ...: 3100 retries needed (1.0% of inserts)", "a fuller space means more retries: the unique constraint catches them"),
                            ("300,000 counter-based 4-character codes: ... 0 retries", "counter-based codes cannot collide")]),
                dict(volatile=True, c=r'''cd ~/warm && cat > redirect.py <<'EOF'
import http.server, socketserver
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        kind = 301 if self.path.startswith('/p/') else 302                   # /p/ permanent, otherwise temporary
        self.send_response(kind); self.send_header('Location', 'https://example.org/very/long/target?utm=1')
        if kind == 301: self.send_header('Cache-Control', 'max-age=31536000')
        self.send_header('Content-Length', '0'); self.end_headers()
    do_HEAD = do_GET                                                         # curl -I sends HEAD
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
socketserver.TCPServer(('127.0.0.1', 8330), H).serve_forever()
EOF
(setsid python3 redirect.py </dev/null >/dev/null 2>&1 & disown) 2>/dev/null; sleep 0.6
echo "--- 302 (temporary): every click reaches your server, so you can count it and change the target:"
curl -sI http://127.0.0.1:8330/abc123 | grep -E "^(HTTP|Location|Cache-Control)" | tr -d '\r'
echo "--- 301 (permanent): browsers cache it, so later clicks never reach you (less load, no analytics, target is stuck):"
curl -sI http://127.0.0.1:8330/p/abc123 | grep -E "^(HTTP|Location|Cache-Control)" | tr -d '\r'
pkill -f redirect.py; true''',
                     e="The redirect decision, in two responses. A **302** goes back to the shortener on every click, so every click can be counted and the destination can be changed later. A **301** carries `Cache-Control: max-age=31536000`: browsers and proxies remember it for a year, which removes load from your servers but means later clicks are invisible to your analytics and the link can never be repointed. Choose by the requirement: analytics or editable links need 302; pure, immutable shortening can use 301 (or a short max-age).",
                     annot=[("HTTP/1.0 302 Found / Location: ...", "temporary: every click comes back to you"),
                            ("HTTP/1.0 301 Moved Permanently / Cache-Control: max-age=31536000", "permanent: cached for a year by clients, invisible to your analytics")]),
            ]),
        ],
        scenario=dict(
            title="\"Design a URL shortener like bit.ly. Walk me through it.\"",
            ask="The canonical warm-up. A strong answer has structure and numbers: requirements, estimates, API, data model, architecture, deep dives, failure.",
            clarify=[("Do we need custom aliases, expiry, analytics, private links? What scale?", "Assume: 100 million new URLs a month, 100:1 read to write, 5-year retention, custom aliases optional, click analytics wanted, redirects must be fast."),
                     ("What availability do we need for redirects versus creation?", "Redirects: very high (99.99%); creation can be a little less strict.")],
            think=[("Estimate.", "About 40 writes/s and 4,000 reads/s (peak 40,000/s); 3 TB in five years; the working set of hot links is small and cacheable."),
                   ("API.", "`POST /v1/urls {long_url, alias?, expires_at?}` returns `{short_url}`; `GET /{code}` returns `302 Location`; `GET /v1/urls/{code}/stats`. Authenticate creators, rate limit creation."),
                   ("Choose the code scheme.", "7 base62 characters (3.5 trillion) from a counter: no collisions. Each app server leases a range of numbers (for example 1 million at a time) from a small coordination service so there is no per-request central call; scramble with a reversible permutation if codes must be unguessable. Custom aliases are checked for uniqueness with the primary key constraint."),
                   ("Data model.", "A key-value table: `code (primary key) -> long_url, owner, created_at, expires_at`. A sharded relational or wide-column/key-value store works; partition by code (hash)."),
                   ("Read path.", "Redirect service checks the cache (Redis, LRU) first; on a miss reads the store and fills the cache; 302 response. Cache hit ratio above 95 percent means the store sees a few hundred reads a second. Add a CDN/edge for global latency if needed."),
                   ("Analytics.", "Publish a click event to a queue asynchronously (never block the redirect); a consumer aggregates counts by code and time bucket in an analytics store."),
                   ("Failures and abuse.", "Store replicated across zones; if the ID range service is down, servers continue with their leased range; malware and phishing checks on creation; rate limits; expiry sweeps; takedown process."),
                   ("Say the trade-offs.", "301 versus 302; counters versus hashes; consistency (a new code must be readable immediately: read-your-writes for creators); cost of cache memory.")],
            answer=["\"Let me start with numbers. At 100 million new URLs a month that is about 40 writes per second and, at 100 to 1, about 4,000 redirects per second with peaks ten times that, and roughly 3 terabytes over five years: small, read-heavy and key-value. The API is POST to create a short URL and GET on the code, which returns a 302 so I can count clicks and change targets.",
                    "For codes I use seven base62 characters from a counter: 3.5 trillion values and no collisions, whereas hashing and truncating collides early by the birthday paradox. Each app server leases a range of numbers from a small coordination service so there is no central call per request, and I scramble the order if codes must not be guessable. The data is one key-value row per code, sharded by hash of the code. Redirects check a Redis cache first, with a hit ratio above 95 percent, so the store sees a few hundred reads a second; clicks are published to a queue and aggregated asynchronously so analytics never slows the redirect. Everything is replicated across zones; if the range service is down, servers keep using their leased range. I would add rate limits, abuse checks, expiry and a takedown path.\""],
            follow=[("How would you prevent guessable or enumerable codes?", "Apply a reversible permutation (a block cipher over the counter) before base62-encoding, or use random codes with collision retry; add rate limits on lookups."),
                    ("What happens when the same long URL is submitted twice?", "Either create a new code each time (simple, allows per-user analytics) or deduplicate by hash of the URL per user; state the choice."),
                    ("How do you scale reads to 400,000 per second?", "More cache replicas, consistent hashing across cache nodes, CDN or edge caching of the 302 with a short TTL, and replicas of the store.")],
            slips=["No numbers at all.", "Hashing and truncating without discussing collisions.", "Counting clicks synchronously on the redirect path."],
        ),
        quick=[
            ("How many base62 characters give about 3.5 trillion codes?", "Seven (62^7)."),
            ("Why do truncated hashes collide earlier than expected?", "The birthday paradox: collisions appear when the number of items is about the square root of the space."),
            ("When would you choose 301 over 302?", "When links are immutable and you do not need per-click analytics; 301 is cached by clients."),
        ],
        traps=[
            "Putting analytics writes on the redirect path.",
            "A single ID generator that every request calls: a bottleneck and a single point of failure.",
            "Forgetting that the cache hit ratio, not the database, determines how many reads the store sees.",
        ],
    ),
    dict(
        title="Design a unique ID generator: Snowflake IDs and why index locality matters",
        tier="hot",
        situation="Every row, order and message needs an ID, generated on many machines at once, without a central bottleneck, unique forever, and ideally sortable by time. Auto-increment breaks the moment you shard, and random UUIDs quietly slow your database down.",
        learn=["Why auto-increment fails at scale", "The Snowflake layout: time, machine, sequence", "Clock problems and how generators cope", "UUIDs versus time-ordered IDs, measured in a real B-tree"],
        model=[
            "A database **auto-increment** gives dense, ordered IDs but needs one writer: it does not survive sharding or multi-master. A **UUID v4** is 128 random bits: unique with no coordination, but **random**, and as a primary key it scatters inserts across the B-tree, causing page splits, poor cache locality and larger indexes. A **Snowflake-style** ID packs a **timestamp** (milliseconds since a custom epoch, 41 bits, about 69 years), a **machine id** (10 bits, 1,024 machines) and a **per-millisecond sequence** (12 bits, 4,096 IDs per millisecond per machine) into 64 bits: unique without coordination (each machine owns its id), **roughly time-ordered** (so inserts append to the right edge of the index), compact, and decodable for debugging. ULIDs and UUID v7 apply the same idea to 128-bit formats.",
            "The hard part is **time**. If the clock goes backwards (NTP step, VM pause) the generator may repeat a timestamp and duplicate IDs: the safe behaviour is to **wait or refuse** until the clock catches up, never to continue. Machine ids must be **assigned uniquely** (from a coordination service, or derived from a lease). If more than 4,096 IDs are needed in one millisecond the generator waits for the next one. Alternatives: **ticket servers** or **range allocation** (each server leases a block of numbers: simple, dense, no clocks), and a central **sequence per entity** when strict gap-free ordering is required (which needs a single leader). State what ordering you actually need: unique, sortable by time, or strictly sequential are three different requirements.",
        ],
        analogy="Instead of one clerk numbering every form (a bottleneck), each branch stamps forms with the date and time, its own branch number and a counter for forms in the same moment: any two forms in the world are distinguishable, and sorting by number sorts them roughly by time.",
        sim=None,
        walk=[
            ("Decide what \"unique\" must mean", "Unique only, sortable by time, or strictly sequential?"),
            ("Pack the fields", "Timestamp, machine id, sequence number into 64 bits."),
            ("Give each machine its own id", "From a coordination service or lease: duplicates here break everything."),
            ("Handle the clock", "Wait on a backwards step; wait for the next millisecond when the sequence is exhausted."),
            ("Check what it does to the index", "Time-ordered IDs append; random IDs scatter."),
        ],
        groups=[
            dict(title="A Snowflake generator, and what ID choice does to a B-tree", cmds=[
                dict(c=r'''cd ~/warm && python3 - <<'EOF'
EPOCH = 1_700_000_000_000            # custom epoch in ms
class Snowflake:
    def __init__(self, machine, clock):
        self.machine, self.clock, self.last, self.seq = machine, clock, -1, 0
    def next(self):
        now = self.clock()
        if now < self.last: raise RuntimeError('clock moved backwards by %d ms: refuse to issue IDs' % (self.last - now))
        if now == self.last:
            self.seq = (self.seq + 1) & 0xFFF
            if self.seq == 0:                                              # 4096 IDs used in this millisecond: wait for the next one
                while now <= self.last: now = self.clock() + 1
        else: self.seq = 0
        self.last = now
        return ((now - EPOCH) << 22) | (self.machine << 12) | self.seq
def decode(i): return {'ms_since_epoch': i >> 22, 'machine': (i >> 12) & 0x3FF, 'sequence': i & 0xFFF}
t = [1_700_000_500_000]
clock = lambda: t[0]
gens = [Snowflake(m, clock) for m in (1, 2, 3)]
ids = []
for step in range(4000):                                                   # three machines issue IDs; the clock ticks every 5 requests
    if step % 5 == 0: t[0] += 1
    for g in gens: ids.append(g.next())
print('generated %d IDs on 3 machines: %d unique, strictly increasing within a machine: %s' % (len(ids), len(set(ids)), all(a < b for a, b in zip([i for i in ids[0::3]], [i for i in ids[0::3]][1:]))))
print('example ID %d decodes to %s' % (ids[10], decode(ids[10])))
print('sorted by ID is (nearly) sorted by time: first 3 decoded:', [decode(i)['ms_since_epoch'] for i in sorted(ids)[:3]])
print('capacity: %d IDs per millisecond per machine, %d machines, about %.0f years from the epoch' % (4096, 1024, (1 << 41) / (365.25 * 24 * 3600 * 1000)))
t[0] -= 5
try: gens[0].next()
except RuntimeError as e: print('clock went backwards:', e)
EOF''',
                     e="A complete Snowflake generator in thirty lines. Three machines issue 12,000 IDs with the clock advancing only every few requests, so many IDs share a millisecond: the **sequence** field disambiguates them, the **machine** field separates generators, and all 12,000 are unique with no coordination between machines. Decoding an ID recovers its timestamp, machine and sequence, handy when debugging. The last lines show the essential safety rule: if the clock moves **backwards**, the generator **refuses** to issue IDs rather than risk duplicating one.",
                     annot=[("generated 12000 IDs on 3 machines: 12000 unique", "no collisions without any coordination between machines"),
                            ("example ID 2097156202499 decodes to {'ms_since_epoch': 500001, 'machine': 2, 'sequence': 3}", "the ID carries its own time, machine and sequence"),
                            ("capacity: 4096 IDs per millisecond per machine, 1024 machines, about 70 years", "the layout's limits: 41 + 10 + 12 bits"),
                            ("clock went backwards: refuse to issue IDs", "never continue on a backwards clock: that is how duplicates are born")]),
                dict(volatile=True, c=r'''cd ~/warm && python3 - <<'EOF'
import os, sqlite3, time, uuid
def run(label, keys):
    path = '/tmp/idtest.db'
    if os.path.exists(path): os.remove(path)
    db = sqlite3.connect(path); db.execute('pragma journal_mode=off'); db.execute('pragma synchronous=off'); db.execute('pragma cache_size=-2000')   # a small cache, like a table bigger than memory
    db.execute('create table t(id text primary key, v integer) without rowid')
    t = time.perf_counter()
    db.executemany('insert into t values (?, 1)', ((k,) for k in keys)); db.commit()
    el = time.perf_counter() - t
    pages = db.execute('pragma page_count').fetchone()[0]; size = os.path.getsize(path) / 1e6
    print('%-34s %5.2f s for 300,000 inserts, database file %.1f MB' % (label, el, size))
N = 300_000
ordered = ['%015d' % i for i in range(N)]                                   # time-ordered like Snowflake / UUIDv7 / ULID
randomkeys = [str(uuid.uuid4()) for _ in range(N)]                          # random UUID v4
run('time-ordered IDs (append only):', ordered)
run('random UUID v4 (scattered):', randomkeys)
EOF''',
                     e="Why ID choice is a performance decision. Inserting 300,000 rows into a B-tree whose cache is smaller than the table: **time-ordered keys** always land at the right edge, so the same few pages stay hot and pages fill completely. **Random UUIDs** land everywhere, forcing the database to touch and split pages all over the tree: the inserts are slower, and the file is larger because pages are left half empty. At larger scale (indexes bigger than memory) the gap becomes dramatic, with each insert causing a random disk read. This is the practical reason to prefer Snowflake, ULID or UUID v7 over UUID v4 for primary keys.",
                     annot=[("time-ordered IDs: 0.30 s, file 7.2 MB", "appends: fast and compact"),
                            ("random UUID v4: 0.90 s, file 14.1 MB", "scattered inserts: three times slower and twice the size here")]),
            ]),
        ],
        scenario=dict(
            title="\"Design a unique ID generator for a distributed system that creates 100,000 IDs per second.\"",
            ask="A classic warm-up. They want requirements, options with trade-offs, a chosen design, and clock handling.",
            clarify=[("Must IDs be sortable by time? Strictly sequential? How long (64-bit?) and how many writers?", "Assume: unique, roughly time-ordered, 64-bit, many servers across regions.")],
            think=[("Reject the simple options.", "Database auto-increment: single writer, bottleneck, breaks with sharding. UUID v4: unique and simple, but 128 bits, random, bad index locality, not sortable."),
                   ("Describe the options.", "Ticket servers or range allocation (dense, simple, central dependency but only per block); Snowflake (decentralised, time-ordered, 64-bit); UUID v7/ULID (decentralised, time-ordered, 128-bit)."),
                   ("Choose Snowflake and size it.", "41 bits time, 10 bits machine, 12 bits sequence: 4,096 IDs per ms per machine, 4 million per second per machine. 100,000 per second is trivial: even one machine suffices; run a few for availability."),
                   ("Machine ids.", "Assigned from a coordination service (etcd/ZooKeeper) with a lease, or derived from a config; never two machines with the same id."),
                   ("Clock handling.", "Use a monotonic source for the sequence logic, refuse or wait when the clock steps back, monitor NTP offsets; sequence overflow waits for the next ms."),
                   ("Sortability limits.", "IDs are only roughly time-ordered across machines (clock skew), so do not use them as a strict ordering of events: use a per-entity sequence or a log for that."),
                   ("Failure and operations.", "Generator as a library or a small stateless service with several instances; no persistent state needed except the machine id and the last timestamp; epoch choice documented forever.")],
            answer=["\"First I clarify what unique has to mean: unique only, roughly sortable by time, or strictly sequential. For unique and roughly time-ordered at 100,000 per second I would use Snowflake-style IDs. Auto-increment is a single-writer bottleneck, and UUID v4 is random, which damages index locality and is not sortable.",
                    "A Snowflake ID is 64 bits: 41 bits of milliseconds since a custom epoch, 10 bits of machine id and 12 bits of sequence, so each machine can issue 4,096 IDs per millisecond. 100,000 per second is trivial, so I would run a few generators for availability with machine ids leased from a coordination service. Time is the danger: if the clock goes backwards the generator must wait or refuse, and if the sequence overflows it waits for the next millisecond. IDs are only roughly ordered across machines because of clock skew, so for strict ordering of events I would use a per-entity sequence or a log instead.\""],
            follow=[("Why not just use UUIDs?", "UUID v4 is fine for uniqueness, but 128 random bits make primary-key indexes larger and slower, and they are not sortable; UUID v7 and ULID fix the ordering part."),
                    ("What if two machines get the same machine id?", "They can issue identical IDs in the same millisecond: assignment must be unique and leased, with a check on startup."),
                    ("How would you generate gap-free invoice numbers?", "That is a different requirement: a transactional sequence in one database (or a single leader per series), accepting the throughput limit.")],
            slips=["Using timestamps from machines as a strict global order.", "Not saying what happens when the clock goes backwards.", "Treating \"unique\" and \"sequential\" as the same requirement."],
        ),
        quick=[
            ("What are the three parts of a Snowflake ID?", "Timestamp (41 bits), machine id (10 bits) and per-millisecond sequence (12 bits)."),
            ("Why are random UUIDs bad primary keys?", "Inserts scatter across the B-tree: page splits, poor cache locality and bigger indexes."),
            ("What must a generator do when the clock moves backwards?", "Wait or refuse; never keep issuing IDs."),
        ],
        traps=[
            "Duplicate machine ids: two generators produce the same IDs.",
            "Using ID order as the true order of events across machines.",
            "Forgetting that the epoch and bit layout are forever once IDs are stored.",
        ],
    ),
    dict(
        title="Design a key-value store: write-ahead log, memtable, recovery and partitioning",
        tier="hot",
        situation="\"Design a key-value store\" asks for the core of every database in one question: how data survives a crash, how reads and writes stay fast, and how it spreads across machines. A toy you build and break yourself makes the answer concrete.",
        learn=["The write path: WAL first, then memory", "Crash recovery by log replay, demonstrated", "Flushing, tombstones and compaction", "Partitioning and replicating across nodes"],
        model=[
            "A single-node store durably accepts `put(key, value)` by first **appending to a write-ahead log (WAL)** on disk (sequential, fast), then updating an in-memory sorted structure (the **memtable**), then acknowledging. If the process crashes, memory is lost but the log is not: on restart the store **replays the log** to rebuild the memtable, so every acknowledged write survives. When the memtable is full it is **flushed** to an immutable **sorted file** (SSTable) and the log can be truncated. Reads check the memtable, then the files from newest to oldest (a **Bloom filter** per file avoids most useless lookups). A **delete** writes a **tombstone** (a marker), because old files are immutable; **compaction** merges files in the background, keeping the newest version of each key and dropping tombstones and obsolete values. This is the LSM design used by Cassandra, RocksDB and many others.",
            "To scale beyond one node: **partition** keys across nodes by **consistent hashing** (a ring with virtual nodes, so adding a node moves only about 1/N of the keys), and **replicate** each key to **N nodes** (typically 3, the next nodes on the ring) in different failure domains. Choose the consistency per request with quorums (W + R > N for strong reads), handle a temporarily dead replica with **hinted handoff** and repair divergence with **read repair** and **anti-entropy** (Merkle trees), and detect failures with **gossip**. Clients (or a coordinator node) route each request to the right replicas. Each of these ideas appeared earlier in the course; a good answer assembles them and states the consistency and availability choice.",
        ],
        analogy="A clerk who writes every instruction in a ledger before touching the filing cabinet: if the building loses power mid-task, the ledger tells them exactly what to redo. Periodically the ledger's entries are filed into sorted folders, and a deleted record is marked rather than torn out until the folders are merged.",
        visual=[KV_VIZ],
        sim=None,
        walk=[
            ("Append to the log", "Sequential write: durable once flushed to disk."),
            ("Update the memtable", "A sorted in-memory map for fast reads and ordered flushing."),
            ("Flush to sorted files", "Immutable, so no in-place updates; deletes become tombstones."),
            ("Compact in the background", "Merge files, keep the newest version, drop tombstones."),
            ("Partition and replicate", "Consistent hashing and N replicas across failure domains."),
        ],
        groups=[
            dict(title="A toy store you can crash", cmds=[
                dict(volatile=True, c=r'''cd ~/warm && cat > kv.py <<'EOF'
import json, os, glob
class KV:
    def __init__(self, d, limit=500):
        self.d, self.limit = d, limit; os.makedirs(d, exist_ok=True)
        self.mem = {}; self.segments = sorted(glob.glob(d + '/seg-*.json'))     # immutable sorted files, oldest first
        self.wal = d + '/wal.log'
        if os.path.exists(self.wal):                                            # RECOVERY: replay the log into a fresh memtable
            for line in open(self.wal):
                op = json.loads(line); self.mem[op['k']] = op['v']
        self.log = open(self.wal, 'a')
    def put(self, k, v):
        self.log.write(json.dumps({'k': k, 'v': v}) + '\n'); self.log.flush(); os.fsync(self.log.fileno())   # 1. durable first
        self.mem[k] = v                                                        # 2. then memory
        if len(self.mem) >= self.limit: self.flush()                            # 3. a full memtable becomes a sorted file
    def delete(self, k): self.put(k, None)                                      # a tombstone: None means deleted
    def flush(self):
        name = '%s/seg-%04d.json' % (self.d, len(self.segments))
        json.dump(dict(sorted(self.mem.items())), open(name, 'w')); self.segments.append(name)
        self.mem = {}; self.log.close(); open(self.wal, 'w').close(); self.log = open(self.wal, 'a')
    def get(self, k):
        if k in self.mem: return self.mem[k], 'memtable'
        for seg in reversed(self.segments):                                     # newest to oldest
            data = json.load(open(seg))
            if k in data: return data[k], os.path.basename(seg)
        return None, 'not found'
    def compact(self):
        merged = {}
        for seg in self.segments: merged.update(json.load(open(seg)))          # newer segments overwrite older values
        merged = {k: v for k, v in merged.items() if v is not None}            # tombstones can finally be dropped
        for seg in self.segments: os.remove(seg)
        name = self.d + '/seg-0000.json'; json.dump(dict(sorted(merged.items())), open(name, 'w')); self.segments = [name]
EOF
python3 - <<'EOF'
import sys, shutil; sys.path.insert(0, '.')
from kv import KV
shutil.rmtree('/tmp/kvdemo', ignore_errors=True)
s = KV('/tmp/kvdemo')
for i in range(1250): s.put('user:%04d' % i, 'name-%d' % i)               # fills the memtable twice: two files are flushed
for i in range(0, 1250, 5): s.delete('user:%04d' % i)                      # delete every fifth user (tombstones)
s.put('user:0001', 'updated')                                              # overwrite a key that lives in an older file
print('files on disk:', [f.split('/')[-1] for f in s.segments], '| keys still only in memory:', len(s.mem))
print('get user:0001 ->', s.get('user:0001'), '(newest value wins)')
print('get user:0010 ->', s.get('user:0010'), '(a tombstone hides the old value)')
print('get user:0703 ->', s.get('user:0703'))
print('--- CRASH: the process dies; everything in memory is lost. We start a new instance on the same directory.')
del s
s2 = KV('/tmp/kvdemo')
print('after recovery: memtable rebuilt from the log with %d keys' % len(s2.mem))
ok = all(s2.get('user:%04d' % i)[0] == (None if i % 5 == 0 else ('updated' if i == 1 else 'name-%d' % i)) for i in range(1250))
print('all 1250 keys read back correctly after the crash:', ok)
s2.flush()                                                                 # push the remaining memtable (with its tombstones) into a file first
before = sum(__import__('os').path.getsize(f) for f in s2.segments); nfiles = len(s2.segments)
s2.compact()
print('compaction: %d files -> 1 file; bytes %d -> %d (obsolete values and tombstones dropped); still correct: %s' % (nfiles, before, __import__('os').path.getsize(s2.segments[0]),
      all(s2.get('user:%04d' % i)[0] == (None if i % 5 == 0 else ('updated' if i == 1 else 'name-%d' % i)) for i in range(1250))))
EOF''',
                     e="A key-value store small enough to read and break. **1,250 writes** fill the memtable twice, so two sorted files exist and the rest of the data is only in memory and the log. Reads find the **newest** value (the overwrite of `user:0001`), a **tombstone** hides a deleted key even though an older file still holds it, and ordinary keys come from the file that has them. Then the **crash**: the in-memory state is thrown away and a new instance is started on the same directory; it **replays the write-ahead log** and every key reads back correctly, including the unflushed ones. Finally **compaction** merges the files, drops the tombstones and old versions, and the data is still correct. These are the same mechanisms that real LSM stores implement with files, Bloom filters and background threads.",
                     annot=[("files on disk: ['seg-0000.json', 'seg-0001.json'] | keys still only in memory: 451", "two memtables were flushed; the newest writes and the tombstones live in memory and the log"),
                            ("get user:0001 -> ('updated', 'memtable')", "the newest version wins over the copy in an older file"),
                            ("get user:0010 -> (None, 'memtable')", "the delete is a tombstone write: it hides the key even if an older file still holds a value"),
                            ("after recovery: memtable rebuilt from the log with 451 keys", "the WAL replay restored everything that was acknowledged but not yet flushed"),
                            ("all 1250 keys read back correctly after the crash: True", "durability: no acknowledged write was lost"),
                            ("compaction: 3 files -> 1 file; bytes ... -> ... (obsolete values and tombstones dropped)", "compaction merges the files, drops tombstones and old versions, and reads get simpler")]),
                dict(c=r'''python3 - <<'EOF'
# Placement on a ring with virtual nodes and 3 replicas: which nodes hold a key, and what happens when one node dies?
import bisect, zlib
nodes = ['node-A', 'node-B', 'node-C', 'node-D', 'node-E']
ring = sorted((zlib.crc32(('%s#%d' % (n, v)).encode()), n) for n in nodes for v in range(64))
hashes = [h for h, _ in ring]
def replicas(key, n=3, alive=None):
    i = bisect.bisect(hashes, zlib.crc32(key.encode())); out = []
    for step in range(len(ring)):
        node = ring[(i + step) % len(ring)][1]
        if node not in out and (alive is None or node in alive): out.append(node)
        if len(out) == n: break
    return out
for k in ('user:1', 'user:2', 'cart:77', 'order:9001'): print('%-11s -> replicas %s' % (k, replicas(k)))
dead = 'node-C'; alive = [n for n in nodes if n != dead]
affected = [k for k in ('user:%d' % i for i in range(1000)) if dead in replicas(k)]
print('if %s dies: %d of 1000 keys lose one replica (about 3/5 = 60%%), but every key still has at least %d live replicas' % (dead, len(affected), min(len([n for n in replicas(k) if n in alive]) for k in affected)))
print('with W=2, R=2 of N=3: writes and reads still succeed for every key (2 of 3 replicas alive)')
EOF''',
                     e="Placement and fault tolerance in a dozen lines. Each key's replicas are the first three **distinct nodes** met walking the ring from the key's hash. When one node of five dies, roughly three fifths of the keys lose one of their three replicas (because each node holds about 3/5 of the data in a 5-node ring with 3 copies), but **every key still has two live replicas**, so with W=2 and R=2 reads and writes continue. The missing copies are rebuilt in the background (hinted handoff, repair), which is where the engineering effort of real systems goes.",
                     annot=[("user:1 -> replicas ['node-X', 'node-Y', 'node-Z']", "three distinct nodes chosen from the ring position of the key"),
                            ("if node-C dies: 522 of 1000 keys lose one replica ... at least 2 live replicas", "replication means a single node failure loses no data and (with quorums) no availability"),
                            ("with W=2, R=2 of N=3: writes and reads still succeed", "a majority of replicas is enough")]),
            ]),
        ],
        scenario=dict(
            title="\"Design a distributed key-value store like Dynamo or Redis Cluster.\"",
            ask="A foundational design question. They want single-node durability, partitioning, replication, consistency choices and failure handling.",
            clarify=[("What are the size, throughput and consistency requirements? Is it a cache or a database? Range queries needed?", "Assume: a durable store, 100 TB, 1 million operations/s, tunable consistency, point lookups by key only.")],
            think=[("Single node.", "WAL then memtable; flush to sorted files; Bloom filters; compaction; recovery by log replay. Choose the LSM design for write-heavy loads."),
                   ("Partitioning.", "Consistent hashing with virtual nodes: even spread, a node join or leave moves about 1/N of the data; or fixed hash slots (Redis Cluster) assigned to nodes."),
                   ("Replication.", "N=3 replicas on the next distinct nodes across failure domains (zones); a coordinator for each request."),
                   ("Consistency.", "Tunable quorums: W + R > N for strong reads, lower for speed and availability; version vectors (or last-write-wins where acceptable) for conflicts; read repair."),
                   ("Failure handling.", "Gossip for membership and failure detection; hinted handoff while a replica is down; anti-entropy with Merkle trees to repair; sloppy quorums for availability at the cost of consistency."),
                   ("Operations.", "Rebalancing with throttled streaming; compaction tuning; monitoring of tail latency per node; capacity planning (data size times replication plus headroom)."),
                   ("State the trade-offs.", "Availability versus consistency under partition (AP by default with tunable strong reads); no multi-key transactions; range queries need ordered partitioning (a different design)." )],
            answer=["\"Each node is an LSM store: a write goes to a write-ahead log, then the memtable, and is acknowledged; a full memtable becomes an immutable sorted file; reads check the memtable and then files newest to oldest with Bloom filters; compaction merges files and drops tombstones; recovery replays the log, so no acknowledged write is lost.",
                    "To scale out I partition keys with consistent hashing and virtual nodes, so adding a node moves only about 1/N of the data, and replicate each key to three nodes in different zones. Consistency is tunable per request with quorums: W plus R greater than N for strong reads, less for speed and availability, with version vectors to detect conflicting writes and read repair to heal them. Failures are detected by gossip, hinted handoff covers a short outage and Merkle-tree anti-entropy repairs longer ones. The trade-off is that by default this is an AP design with no multi-key transactions and no range queries; if I need ranges I would partition by key ranges instead.\""],
            follow=[("How does the store survive a node crash?", "The WAL on disk is replayed on restart; the other replicas serve in the meantime; hinted handoff and repair bring the node up to date."),
                    ("Why are deletes tombstones?", "Files are immutable and replicas may not all have seen the delete; the tombstone must propagate and be kept long enough to overtake old values before compaction removes it."),
                    ("How would you support range scans?", "Partition by key range (ordered partitions) rather than hash, accepting hot ranges, or keep a secondary ordered index.")],
            slips=["Skipping the single-node durability story.", "Hash partitioning with `mod N` and no discussion of rebalancing.", "No view on consistency when replicas disagree."],
        ),
        quick=[
            ("Why write to the WAL before the memtable?", "So an acknowledged write survives a crash: memory is lost, the log is replayed."),
            ("What is a tombstone?", "A marker written for a delete because old immutable files cannot be edited; compaction later removes it."),
            ("Why consistent hashing with virtual nodes?", "Even spread and only about 1/N of the keys move when nodes join or leave."),
        ],
        traps=[
            "Acknowledging a write before the log is on disk: a crash loses data you promised was safe.",
            "Removing tombstones before every replica has seen the delete: deleted data comes back.",
            "Replicas in the same rack or zone: one failure takes all copies.",
        ],
    ),
]
