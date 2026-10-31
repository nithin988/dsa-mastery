"""Systems Mastery S21: design warm-ups (URL shortener, pastebin, rate limiter, ID generator, key-value store)."""
import sysviz as v

SHORT_VIZ = v.figure(
    720, 190,
    [v.box(10, 60, 90, 50, "Client", "ink"),
     v.arrow(100, 85, 125, 85), v.box(125, 60, 100, 50, "Load balancer", "acc"),
     v.arrow(225, 85, 250, 85), v.box(250, 60, 110, 50, "App servers", "acc", "stateless"),
     v.arrow(360, 85, 385, 50), v.box(385, 25, 100, 50, "Cache", "warn", "hot codes"),
     v.arrow(360, 85, 385, 125), v.box(385, 100, 100, 50, "Database", "ok", "code to URL"),
     v.arrow(485, 125, 510, 125), v.box(510, 100, 110, 50, "ID generator", "acc", "unique numbers"),
     v.text(360, 176, "Reads (redirects) dominate: cache them. Writes are rare: get a unique id, encode it, store it.", "dg-s")],
    "A URL shortener", "The smallest design that meets the numbers")

MODULE = dict(
    id="dw",
    title="Design warm-ups",
    lead="Five small systems that appear in interviews again and again: a URL shortener, a pastebin, a distributed rate limiter, a unique ID generator and a key-value store. Each is worked through the method from the design module: requirements, numbers, API and data, a simple design, one deep dive with a runnable prototype, and the trade-offs.",
    time="7 to 8 hours",
    why=[
        "These are the \"first system design questions\" at many companies. They are small enough to finish in 45 minutes and rich enough to reveal how you think: do you ask about scale, do you do the arithmetic, do you spot the hard part (unique IDs, expiry, shared counters)?",
        "They are also real: every company runs a short-link service, a rate limiter, an ID generator and a key-value store somewhere. Understanding the small versions makes the big ones readable.",
    ],
    outcomes=[
        "Design a URL shortener with numbers: read and write rates, storage, code length and collisions.",
        "Design a pastebin and explain expiry, storage choices and abuse limits.",
        "Explain why per-server counters break a distributed rate limiter and how to fix it.",
        "Explain how Snowflake-style IDs are built and what can go wrong.",
        "Explain how an append-only log gives a simple key-value store durability, recovery and compaction.",
        "Present any of them in a clear 45-minute structure.",
    ],
    before=[
        "The design method (S15), scaling blocks (S16), data storage (S17) and distributed systems (S18) are used throughout; each idea is repeated briefly.",
        "Prototypes are small `python3` programs. They are deliberately simple: the point is to see the idea work, not to build production code.",
    ],
    env=["Scratch folder: `mkdir -p ~/warm && cd ~/warm`."],
    lessons=[
        dict(
            title="Design a URL shortener",
            tier="hot",
            situation="\"Design a service like bit.ly: give it a long URL, get a short link; opening the short link redirects.\"",
            learn=["Requirements and numbers", "Base62 codes and collisions", "Read path, write path and caching"],
            model=[
                "**Requirements:** create a short link, redirect fast, links may expire, high availability; analytics optional. **Numbers:** say 100 million new links a month and reads 100 times writes: about 39 writes per second, 3,900 reads per second, peak around 12,000, and about 3 TB over five years at 500 bytes per record. That is modest: a cache plus a database with replicas covers it. **Design:** the redirect is the hot path, so cache hot codes in memory. For the **code**, take a unique number (from an ID generator) and encode it in **base62** (0-9, a-z, A-Z): 7 characters give 62^7, about 3.5 trillion codes, and no collisions because every number is used once. The alternative, hashing the URL and truncating, risks **collisions** you must detect and retry.",
            ],
            analogy="A cloakroom: you hand over something long and awkward and get a small numbered ticket; showing the ticket gets the item back quickly.",
            visual=SHORT_VIZ,
            sim="shorten",
            groups=[
                dict(title="The numbers, and why not just hash", cmds=[
                    dict(c="mkdir -p ~/warm && cd ~/warm && python3 -c \"new=100e6/(30*86400)\nprint('writes/s: %.0f' % new)\nprint('reads/s (100x):  %.0f, peak x3: %.0f' % (new*100, new*300))\nprint('storage, 5 years at 500 B: %.1f TB' % (100e6*12*5*500/1e12))\nprint('7-char base62 codes: %.2e' % 62**7)\"", e="The arithmetic from the design method: tens of writes and a few thousand reads per second, a few terabytes in five years, and a code space (about 3.5 trillion) far larger than needed."),
                    dict(c="cd ~/warm && cat > hash.py <<'EOF'\nimport hashlib\nA = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'\ndef b62(n):\n    s = ''\n    while n:\n        n, r = divmod(n, 62); s = A[r] + s\n    return s or '0'\nurls = ['https://example.com/page/%d' % i for i in range(200000)]\nfor k in (4, 5, 6):\n    codes = {b62(int(hashlib.md5(u.encode()).hexdigest(), 16))[:k] for u in urls}\n    print('hash truncated to %d chars: %d collisions among 200,000 urls' % (k, len(urls) - len(codes)))\nEOF\npython3 hash.py", e="Truncating a hash to a short code causes collisions (two URLs getting the same code), roughly n squared over twice the space. At 4 characters thousands collide among just 200,000 links; even at 6 characters some do. A counter encoded in base62 never collides, which is why most designs use an ID generator.", parts=[("md5(...)", "hash of the URL"), ("[:k]", "keep only the first k characters of the code")]),
                ]),
            ],
            quick=[
                ("How many 7-character base62 codes exist?", "62 to the power 7, about 3.5 trillion."),
                ("Why prefer an ID counter over truncating a hash?", "Every number is unique, so there are no collisions to detect and retry."),
            ],
            traps=[
                "Predictable sequential codes let anyone enumerate every link; add a per-code random component or shuffle the number if links must be private.",
                "A 301 redirect is cached by browsers and hides clicks from your analytics; use 302 if you count visits.",
                "Forgetting expiry, abuse (phishing, spam) and custom aliases when the interviewer asks about extensions.",
            ],
        ),
        dict(
            title="Design a pastebin",
            tier="hot",
            situation="\"Design a service where users paste text and share a link; pastes can expire.\"",
            learn=["Size estimate and what goes where", "Expiry (TTL) and cleanup", "Limits and abuse"],
            model=[
                "**Requirements:** create a paste, read by link, optional expiry, size limit (say 10 MB), high availability. **Numbers:** 1 million pastes a day at an average 10 KB is 10 GB a day, about 3.6 TB a year: too much for a database row store but ideal for **object storage**. **Design:** keep **metadata** (id, owner, created, expires, object key) in a database and the **content** in object storage; serve reads through a CDN and cache. For the id reuse the URL-shortener idea. **Expiry**: store `expires_at`, **ignore expired rows on read** (so users never see them even before cleanup) and delete them in a background job. Rate-limit creation and scan for abuse.",
            ],
            analogy="A noticeboard where each note is pinned with an expiry date: the board is tidied up in the background, but nobody should read an out-of-date note in the meantime.",
            groups=[
                dict(title="Expiry with a real database", cmds=[
                    dict(c="cd ~/warm && cat > paste.py <<'EOF'\nimport sqlite3\nc = sqlite3.connect(':memory:')\nc.execute('CREATE TABLE pastes(id TEXT PRIMARY KEY, expires_at INTEGER)')\nc.execute('CREATE INDEX idx_exp ON pastes(expires_at)')\nc.executemany('INSERT INTO pastes VALUES (?,?)', [('a1', 500), ('b2', 900), ('c3', 1500), ('d4', 2500), ('e5', 99999999)])\nnow = 1000\nlive = c.execute('SELECT id FROM pastes WHERE expires_at > ? ORDER BY id', (now,)).fetchall()\nprint('readable at t=%d:' % now, [r[0] for r in live])\ngone = c.execute('DELETE FROM pastes WHERE expires_at <= ?', (now,)).rowcount\nprint('background cleanup removed', gone, 'expired pastes')\nprint('remaining:', c.execute('SELECT count(*) FROM pastes').fetchone()[0])\nprint('plan:', c.execute('EXPLAIN QUERY PLAN DELETE FROM pastes WHERE expires_at <= 1000').fetchall()[0][3])\nEOF\npython3 paste.py", e="Reads filter on `expires_at > now`, so an expired paste is invisible immediately even if the cleanup job has not run. The cleanup deletes in the background, and an index on `expires_at` keeps both the query and the cleanup from scanning the whole table (the plan shows it searching the index).", parts=[("expires_at > ?", "never show expired content, even before cleanup"), ("idx_exp", "index so cleanup does not scan every row")]),
                ]),
            ],
            quick=[
                ("Where should paste content and paste metadata live?", "Content in object storage (cheap, huge); metadata (id, owner, expiry, object key) in a database."),
                ("Why filter on expiry at read time as well as cleaning up?", "Cleanup runs periodically, so reads must ignore expired rows or users could see content past its expiry."),
            ],
            traps=[
                "Storing multi-megabyte blobs in database rows: it bloats backups and slows queries.",
                "No size limit or rate limit: a pastebin is a free file host for abuse.",
            ],
        ),
        dict(
            title="Design a distributed rate limiter",
            tier="hot",
            situation="\"Limit each API key to 100 requests per minute, across 20 API servers.\"",
            learn=["Why per-server counters fail", "A shared atomic counter", "Failure choices: fail open or closed"],
            model=[
                "**Requirements:** limit per key, low added latency, works across many servers, tolerates the limiter failing. **Why it is hard:** if each of N servers keeps its own counter, a client that spreads requests over them gets **N times the limit**. **Fix:** keep the count in a **shared fast store** (Redis-style) using an **atomic increment with expiry** (`INCR key`, set a TTL on first use), or give each server a share of the quota and rebalance. Algorithm choices: fixed window (simple), sliding window or token bucket (smoother). Decide the **failure mode**: if the store is down, **fail open** (let traffic through, risking overload) or **fail closed** (reject, risking an outage); most public APIs fail open. Return **429** with `Retry-After` and rate-limit headers.",
            ],
            analogy="Ten ticket offices each allowed to sell 100 tickets for one concert: the venue sells 1,000 unless they share one counter.",
            groups=[
                dict(title="Local counters versus a shared counter", cmds=[
                    dict(c="cd ~/warm && cat > rl.py <<'EOF'\nimport itertools\nLIMIT, SERVERS, REQUESTS = 100, 3, 300\n# A client spreads 300 requests over 3 servers in round-robin order.\nlocal = [0] * SERVERS\nallowed_local = 0\nfor i in range(REQUESTS):\n    s = i % SERVERS\n    if local[s] < LIMIT:\n        local[s] += 1; allowed_local += 1\nprint('per-server counters: %d of %d allowed (limit was %d!)' % (allowed_local, REQUESTS, LIMIT))\nshared = 0\nallowed_shared = 0\nfor i in range(REQUESTS):\n    shared += 1                  # in production: one atomic INCR in a shared store\n    if shared <= LIMIT:\n        allowed_shared += 1\nprint('shared counter:      %d of %d allowed' % (allowed_shared, REQUESTS))\nEOF\npython3 rl.py", e="Three servers each enforcing 100 per minute together let the client through 300 times, three times the intended limit. One shared counter enforces exactly 100. In production the shared counter is an atomic increment in a fast store, which also makes the limiter another dependency to keep available."),
                ]),
            ],
            quick=[
                ("Why do per-server counters fail?", "A client spreading requests across N servers gets N times the intended limit."),
                ("Fail open or fail closed when the limiter store is down?", "Most APIs fail open (allow traffic) to avoid an outage, accepting the risk of overload; the choice should be deliberate."),
            ],
            traps=[
                "A non-atomic read-then-write on the counter lets concurrent requests slip through; use an atomic increment.",
                "Putting the limiter in the critical path without a timeout: a slow limiter store becomes your outage.",
            ],
        ),
        dict(
            title="Design a unique ID generator",
            tier="hot",
            situation="\"Generate globally unique 64-bit IDs, roughly sortable by time, at 100,000 per second, from many machines, with no central bottleneck.\"",
            learn=["Why auto-increment and UUID are not enough", "Snowflake-style IDs", "Clock problems"],
            model=[
                "A database **auto-increment** is a single bottleneck and a single point of failure. A random **UUID** needs no coordination but is 128 bits and unordered, which hurts index locality. A **Snowflake-style** ID packs a **timestamp** (41 bits, milliseconds since a custom epoch), a **machine ID** (10 bits) and a **sequence** (12 bits) into 64 bits: machines generate IDs independently, IDs sort by creation time, and each machine can make 4,096 per millisecond. Risks: duplicate machine IDs, and **clocks moving backwards** (the generator must wait or refuse). Alternatives include ticket servers and UUID version 7 (time-ordered).",
            ],
            analogy="Numbered raffle tickets printed at several desks: each desk has its own colour (machine) and counter, and the time stamped on each ticket keeps them in order.",
            sim="snowbits",
            groups=[
                dict(title="Build and decode Snowflake IDs", cmds=[
                    dict(c="cd ~/warm && cat > snow.py <<'EOF'\nclass Gen:\n    def __init__(self, machine):\n        self.m, self.last, self.seq = machine, -1, 0\n    def next(self, now_ms):\n        if now_ms < self.last:\n            raise RuntimeError('clock moved backwards: refuse to issue ids')\n        if now_ms == self.last:\n            self.seq = (self.seq + 1) & 4095\n        else:\n            self.seq = 0\n        self.last = now_ms\n        return (now_ms << 22) | (self.m << 12) | self.seq\ndecode = lambda i: (i >> 22, (i >> 12) & 1023, i & 4095)\ng = Gen(7)\nids = [g.next(1000), g.next(1000), g.next(1000), g.next(1001)]\nfor i in ids:\n    print(i, 'ms=%d machine=%d seq=%d' % decode(i))\nprint('sorted by time:', ids == sorted(ids))\nprint('max per machine per second:', 4096 * 1000)\ntry:\n    g.next(999)\nexcept RuntimeError as e:\n    print('error:', e)\nEOF\npython3 snow.py", e="Three IDs in the same millisecond differ only in the sequence number; the next millisecond resets it. The IDs are already in numeric (and time) order, and a generator can issue 4,096,000 per second. When the clock steps backwards the generator refuses instead of risking a duplicate.", parts=[("<< 22", "shift the timestamp above the machine and sequence bits"), ("& 4095", "keep the low 12 bits: the sequence")]),
                ]),
            ],
            quick=[
                ("What are the fields of a Snowflake-style ID?", "A 41-bit timestamp, a 10-bit machine ID and a 12-bit sequence number (plus an unused sign bit)."),
                ("What is the main danger of time-based IDs?", "Clocks moving backwards or two machines sharing an ID could create duplicates; generators must detect and refuse."),
            ],
            traps=[
                "Assigning machine IDs by hand: two machines with the same ID produce duplicates; use a coordination service or leases.",
                "Using such IDs as a security token: they are guessable and reveal the creation time and the machine.",
            ],
        ),
        dict(
            title="Design a key-value store",
            tier="hot",
            situation="\"Design a store with put(key, value) and get(key) that survives crashes.\" (Single node first, distribution second.)",
            learn=["An append-only log and a memory index", "Crash recovery by replay", "Compaction, then how it scales out"],
            model=[
                "A simple durable store keeps an in-memory **hash index** and an **append-only log** on disk: every `put` and `delete` is appended to the log (the fastest disk operation), then applied to memory; reads are hash lookups. After a **crash** the log is **replayed** to rebuild memory, so acknowledged writes are not lost. The log grows with old versions and deletes, so **compaction** rewrites it keeping only the latest value of each key. Real systems extend this (sorted files, LSM trees, bloom filters). To **scale out**, partition keys with consistent hashing, replicate each partition (leader-follower or quorum), and decide the consistency level, which is exactly the storage and distributed-systems modules combined.",
            ],
            analogy="A ship's logbook: you only ever write at the end, and after losing your notes you can reconstruct the present by reading the log from the beginning.",
            sim="kvlsm",
            groups=[
                dict(title="Put, crash, recover, compact", cmds=[
                    dict(c="cd ~/warm && cat > kv.py <<'EOF'\nimport os, json\nclass KV:\n    def __init__(self, path):\n        self.path, self.mem = path, {}\n        if os.path.exists(path):\n            for line in open(path):\n                op, k, *v = json.loads(line)\n                if op == 'put': self.mem[k] = v[0]\n                else: self.mem.pop(k, None)\n    def _log(self, rec):\n        with open(self.path, 'a') as f:\n            f.write(json.dumps(rec) + '\\n'); f.flush(); os.fsync(f.fileno())\n    def put(self, k, v): self._log(['put', k, v]); self.mem[k] = v\n    def delete(self, k): self._log(['del', k]); self.mem.pop(k, None)\n    def get(self, k): return self.mem.get(k)\n    def compact(self):\n        tmp = self.path + '.tmp'\n        with open(tmp, 'w') as f:\n            for k, v in self.mem.items(): f.write(json.dumps(['put', k, v]) + '\\n')\n        os.replace(tmp, self.path)\nif os.path.exists('kv.log'): os.remove('kv.log')\ns = KV('kv.log')\nfor i in range(1000): s.put('counter', i)\ns.put('user:7', 'Asha'); s.put('tmp', 'x'); s.delete('tmp')\nprint('log lines before compaction:', sum(1 for _ in open('kv.log')))\ns2 = KV('kv.log')          # simulated crash and restart: rebuild from the log\nprint('after restart: counter =', s2.get('counter'), ', user:7 =', s2.get('user:7'), ', tmp =', s2.get('tmp'))\ns2.compact()\nprint('log lines after compaction: ', sum(1 for _ in open('kv.log')))\nprint('data still correct:', KV('kv.log').get('counter'), KV('kv.log').get('user:7'))\nEOF\npython3 kv.py", e="1,000 overwrites of one key plus a few others leave a 1,003-line log. A new instance rebuilds the exact state by replaying it (a simulated crash recovery). Compaction rewrites the log with only the latest value of each live key (two lines here) and the data is unchanged.", parts=[("os.fsync", "force the log to disk before acknowledging the write"), ("os.replace", "atomically swap the compacted file in")]),
                ]),
            ],
            quick=[
                ("How does an append-only log give crash safety?", "Every change is written to the log (and synced) before it is acknowledged; after a crash the log is replayed to rebuild the in-memory state."),
                ("What does compaction do?", "Rewrites the log keeping only the newest value of each live key, so old versions and deletes stop taking space."),
            ],
            traps=[
                "Acknowledging a write before it is flushed to disk: a crash then loses data the client believes is safe.",
                "Replay time grows with the log; compact and snapshot periodically so restarts stay fast.",
            ],
        ),
        dict(
            title="Presenting a design in 45 minutes",
            tier="hot",
            situation="You know the pieces. How do you turn them into a clear, confident answer under time pressure?",
            learn=["A time budget", "What to say at each step", "Handling follow-ups"],
            model=[
                "A reliable shape for any of these problems: **5 minutes** clarifying requirements and stating assumptions; **5** on numbers; **10** on API, data model and the high-level diagram; **15** on one or two deep dives (for the URL shortener: code generation and the cache; for the rate limiter: the shared counter; for the ID generator: clocks); **10** on trade-offs, failures and extensions. Think aloud, label each step, draw as you go, and **ask before assuming**. When challenged, treat it as new information: restate the concern, say how it changes the numbers or the design, and adapt. End by summarising the design in three sentences and naming its biggest risk.",
            ],
            analogy="Telling a story with a beginning (the problem), a middle (the design) and an end (the risks), so the listener never gets lost.",
            quick=[
                ("What goes in the first five minutes?", "Clarifying questions, functional and non-functional requirements, and explicit assumptions."),
                ("How do you end a design discussion well?", "Summarise the design in a few sentences and name its biggest risk and what you would do next."),
            ],
            traps=[
                "Going deep on one component for 30 minutes and never showing the whole system.",
                "Stating a design without the numbers that justify it.",
            ],
        ),
    ],
    labs=[
        dict(kind="linux", script="short-code", dir="short", title="Make short codes",
             goal=["Encode numeric IDs in base62 and size the code space."],
             story=["The shortener team gives you five database IDs. Produce the short codes users will see, and tell them how many 7-character codes exist."],
             tasks=["Read `README.txt` for the alphabet and rules.", "Convert each id in `ids.txt` to base62 (a short script is easiest).", "Compute 62 to the power 7.", "Write `codes=` (comma-separated, in order) and `max_ids_7=` into `~/sys-lab/answers-short.txt`."],
             check="Run the check script.", check_cmd="bash ~/sys-lab/check-short-code.sh",
             hints=["Repeatedly divide by 62; the remainders (reversed) are the digits.", "Use the alphabet string from the README to map each remainder to a symbol.", "In Python: `62**7`."],
             solution=["For each id: `while n: n, r = divmod(n, 62); s = alphabet[r] + s`.", "62**7 = 3,521,614,606,208.", "Write both lines to the answers file."]),
        dict(kind="linux", script="snowflake-id", dir="snow", title="Decode Snowflake IDs",
             goal=["Take a time-based ID apart into its timestamp, machine and sequence."],
             story=["An incident report quotes three IDs. To find which machine produced the third one and when, you need to decode it."],
             tasks=["Read `README.txt` for the bit layout.", "For the third id compute the timestamp (`id >> 22`), machine (`(id >> 12) & 1023`) and sequence (`id & 4095`).", "Write `ms=`, `machine=` and `seq=` into `~/sys-lab/answers-snow.txt`."],
             check="Run the check script.", check_cmd="bash ~/sys-lab/check-snowflake-id.sh",
             hints=["Bash does bit arithmetic: `echo $(( id >> 22 ))`.", "`sed -n '3p' ids.txt` prints the third line.", "The mask 1023 keeps 10 bits; 4095 keeps 12 bits."],
             solution=["`id=$(sed -n 3p ids.txt)`.", "`echo $(( id >> 22 ))`, `echo $(( (id >> 12) & 1023 ))`, `echo $(( id & 4095 ))`.", "Write the three lines to the answers file."]),
    ],
    cases=[],
    cheat=[
        ["1M requests/day", "about 12 per second; 1B/day about 12,000 per second"],
        ["base62", "0-9a-zA-Z; 7 chars give 62^7 = 3.5 trillion codes"],
        ["hash truncation", "collisions: n squared / (2 x space)"],
        ["301 vs 302", "browser-cached (hides clicks) vs not cached (counts visits)"],
        ["object storage + metadata DB", "big blobs in one, small records in the other"],
        ["TTL", "filter on read and clean up in the background, index expires_at"],
        ["per-server limiter", "N servers give N times the limit"],
        ["shared limiter", "atomic increment with expiry in a fast store; decide fail open or closed"],
        ["Snowflake id", "41 bits time, 10 bits machine, 12 bits sequence"],
        ["clock backwards", "refuse or wait; never issue ids"],
        ["append-only log", "durable, fast; replay to recover"],
        ["compaction", "keep only the newest value of each key"],
        ["45 minutes", "5 requirements, 5 numbers, 10 design, 15 deep dive, 10 trade-offs"],
    ],
    interview_intro="These five are warm-ups, so interviewers expect a complete, well-structured answer in 45 minutes. Show the numbers and name the hard part.",
    interview=[
        dict(q="Design a URL shortener.",
             a=["Requirements: create and resolve short links, redirect fast, expiry, high availability. Numbers: e.g. 100M links a month, 100:1 reads, so about 40 writes and 4,000 reads per second, a few TB in five years.", "API: POST /links returns a short code, GET /{code} redirects (302 if you count clicks). Data: code, long URL, created, expiry, owner.", "Code generation: a unique number from an ID generator, base62 encoded (7 chars is 3.5 trillion). Avoid truncated hashes (collisions). Cache hot codes; replicate the database.", "Extensions: analytics, custom aliases, abuse detection, deleting expired links."],
             follow=["How do you avoid sequential, guessable codes?", "How would you handle a link going viral?", "301 or 302?"], mistakes=["Skipping the numbers.", "Ignoring collisions or expiry."],
             angle="Reported by candidates as one of the most common first design questions at large tech companies; not official."),
        dict(q="How do you generate unique IDs across many machines?",
             a=["Options: database auto-increment (bottleneck), UUID (no coordination but large and unordered), ticket server, and Snowflake-style IDs.", "Snowflake: 41-bit timestamp, 10-bit machine ID, 12-bit sequence in 64 bits: independent generation, time-sortable, 4,096 per ms per machine.", "Failure modes: duplicate machine IDs, backwards clocks, sequence overflow (wait for the next millisecond)."],
             follow=["What if a machine's clock jumps back?", "How would you assign machine IDs?"], mistakes=["Relying on random numbers for uniqueness without discussing collisions."]),
        dict(q="Design a distributed rate limiter.",
             a=["Per key limits with a token bucket or sliding window; return 429 with Retry-After.", "Shared state: atomic increment with TTL in a fast store, or per-server quota shares; local counters alone give N times the limit.", "Failure mode (open or closed), hot keys, clock handling, and where it runs (gateway or client library)."],
             follow=["What if the shared store is down?", "How do you limit globally across regions?"], mistakes=["Per-server counters.", "Non-atomic read-then-write."],
             angle="Google-style: candidates commonly report follow-ups on accuracy versus latency and on multi-region limits; reported by candidates, not official."),
        dict(q="Design a pastebin.",
             a=["Requirements, then numbers: 1M pastes a day at 10 KB is 10 GB a day, so use object storage for content and a database for metadata.", "IDs like the URL shortener; reads via CDN and cache; expiry with `expires_at` filtered on read and cleaned in the background.", "Limits: maximum size, creation rate limits, content scanning for abuse."],
             follow=["How do you support private pastes?", "How do you delete expired data cheaply?"], mistakes=["Storing blobs in the database."]),
        dict(q="Design a key-value store. How does it survive a crash?",
             a=["Single node: in-memory hash index plus an append-only log, fsync before acknowledging; replay the log on restart; compact periodically.", "Scale out: partition with consistent hashing, replicate each partition, choose quorum settings (W, R) for consistency.", "Mention LSM trees, bloom filters and memory limits as how real stores extend the idea."],
             follow=["What happens when one replica is down?", "How would you do range queries?"], mistakes=["Acknowledging writes before they are durable."],
             angle="Amazon-style: expect follow-ups modelled on the Dynamo ideas (quorums, consistent hashing, hinted handoff) and on failure handling; reported by candidates, not official."),
        dict(q="You have 45 minutes for a design question. How do you structure them?",
             a=["About 5 minutes of requirements and assumptions, 5 of numbers, 10 for API, data and a high-level diagram, 15 for one or two deep dives, 10 for trade-offs, failures and extensions.", "Think aloud, draw as you go, and summarise at the end including the main risk."],
             follow=["What do you do when you are stuck?"], mistakes=["No numbers.", "All the time on one box."]),
    ],
    selftest=[
        ("How many writes per second is 100 million new links a month?", "About 39."),
        ("How many codes can 7 base62 characters represent?", "62^7, about 3.5 trillion."),
        ("Why not truncate a hash to make short codes?", "Collisions: two URLs can share a code, so you must detect and retry."),
        ("Where do paste contents belong?", "In object storage, with metadata in a database."),
        ("Why do per-server counters break a distributed rate limiter?", "Each server counts separately, so the real limit becomes N times larger."),
        ("What bits make up a Snowflake id?", "41 bits timestamp, 10 bits machine, 12 bits sequence."),
        ("What does an append-only log give a key-value store?", "Fast durable writes and recovery by replaying the log."),
        ("What does compaction remove?", "Old versions of keys and delete markers."),
    ],
    recall=[
        ["base62", "7 chars = 3.5 trillion codes"],
        ["302", "redirect that is not cached: counts clicks"],
        ["metadata + blob", "database plus object storage"],
        ["shared counter", "atomic INCR with TTL"],
        ["fail open", "allow traffic when the limiter is down"],
        ["Snowflake", "time, machine, sequence"],
        ["WAL / log", "write first, replay on restart"],
        ["45 minutes", "5, 5, 10, 15, 10"],
    ],
    sources=[
        dict(title="System Design Primer: design a URL shortener (Pastebin)", url="https://github.com/donnemartin/system-design-primer", use="Worked designs for pastebin and others with diagrams", license="CC BY 4.0", how="Recommended; our text and prototypes are original"),
        dict(title="Twitter Snowflake announcement", url="https://blog.x.com/engineering/en_us/a/2010/announcing-snowflake", use="The origin of Snowflake IDs", license="Copyright the author; read online", how="Link only"),
        dict(title="Redis: INCR pattern for rate limiting", url="https://redis.io/docs/latest/commands/incr/", use="Atomic counters and the rate limiter pattern", license="Documentation under CC BY-SA 4.0", how="Link only"),
        dict(title="Designing Data-Intensive Applications (Martin Kleppmann)", url="https://dataintensive.net/", use="Chapter 3: logs, hash indexes and LSM trees", license="Commercial book; not copied", how="Recommended reading"),
    ],
    plan=[
        "**Hour 1:** URL shortener: redo the estimate with your own numbers; run the collision experiment.",
        "**Hour 2:** pastebin; add a size limit and a per-user quota to the sketch.",
        "**Hour 3:** rate limiter; then Lab 1.",
        "**Hour 4:** ID generator; then Lab 2.",
        "**Hours 5 and 6:** key-value store; extend the prototype with a snapshot file.",
        "**Hours 7 and 8:** deliver each design aloud against a 45-minute timer, then the self-test.",
    ],
)
