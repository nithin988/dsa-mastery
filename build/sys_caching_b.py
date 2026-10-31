"""S17 caching: part B (lessons 4 to 7)."""
import sysviz as v

STAMPEDE_SEQ = v.seq(
    ["Requests", "Cache", "Database"],
    [("note", 0, 2, "a popular entry expires at 12:00:00"),
     ("a->b", 0, 1, "GET product:1 (x 1,000 at once)"),
     ("a->b", 1, 0, "miss, miss, miss...", "bad"),
     ("a->b", 0, 2, "1,000 identical queries hit the database together"),
     ("a->b", 2, 0, "slow or crashing: the thundering herd", "bad"),
     ("note", 0, 2, "fix: one request rebuilds, the others wait or get the old value")],
    "A cache stampede", "When a hot key expires, every caller misses at the same moment")

HTTP_SEQ = v.seq(
    ["Browser", "CDN edge", "Origin"],
    [("a->b", 0, 1, "GET /app.js"),
     ("a->b", 1, 2, "edge miss: GET /app.js"),
     ("a->b", 2, 1, "200, Cache-Control: max-age=3600, ETag: v7", "reply"),
     ("a->b", 1, 0, "200 (edge keeps a copy for an hour)", "reply"),
     ("note", 0, 2, "next user near this edge: answered by the edge, origin untouched"),
     ("a->b", 0, 1, "GET /app.js  If-None-Match: v7  (after expiry)"),
     ("a->b", 1, 2, "revalidate: If-None-Match: v7"),
     ("a->b", 2, 1, "304 Not Modified (no body)", "reply"),
     ("a->b", 1, 0, "304: keep using your copy", "reply")],
    "HTTP caching with a CDN", "Fresh copies are served locally; stale copies are revalidated cheaply")

LESSONS_B = [
    dict(
        title="The hard problems: stampedes, penetration, hot keys, cold starts",
        tier="hot",
        situation="The cache works well for weeks. Then a popular key expires and the database collapses; or someone asks for a million product IDs that do not exist; or one celebrity key melts a single cache node. Caches fail in specific, predictable ways.",
        learn=["Cache stampede (thundering herd) and its fixes", "Cache penetration and negative caching", "Hot keys and cold starts"],
        model=[
            "**Stampede (thundering herd):** a very popular entry expires; for the next few hundred milliseconds every request misses and every request recomputes the same expensive answer, so the database receives a thousand identical queries at once. Fixes: let **one** request rebuild while the others **wait** or serve the **old value** (a lock with `SET key NX PX`, or request coalescing), add **jitter** to TTLs so keys do not all expire together, and **refresh ahead** of expiry for hot keys.",
            "**Penetration:** requests for keys that do not exist anywhere (typos, scanners, attackers) always miss the cache and always hit the database. Fix with **negative caching** (store \"not found\" for a short time) and, for floods, a **Bloom filter** or input validation in front. **Hot keys:** one key receives so much traffic that the single cache node holding it is overloaded even though the cluster is idle; replicate the hot key, add a short-lived local cache in each app server, or split it into several keys. **Cold start:** an empty cache (after a restart or deploy) sends full load to the database; warm it, restart nodes gradually, and protect the database with limits.",
        ],
        analogy="A bakery whose popular loaf sells out at exactly 8:00: a hundred customers ask at once and the baker is overwhelmed. Better to have one person start the new batch while the others wait or take yesterday's loaf, and to stagger the sell-by times.",
        visual=[STAMPEDE_SEQ],
        sim=None,
        walk=[
            ("A hot entry expires", "All servers see the miss within the same few milliseconds because they were all hitting the same key."),
            ("Each one recomputes", "Without coordination, every request runs the expensive query: the database load jumps by the number of waiting requests."),
            ("Coordinate with a lock", "The first request sets a lock key with `SET key NX PX`; Redis guarantees only one caller wins. The winner rebuilds the entry and releases the lock."),
            ("The others wait briefly or serve stale", "They poll the cache for a few tens of milliseconds, or return the previous value kept alongside (stale-while-revalidate)."),
            ("Negative caching for the absent", "If the database also has nothing, store a short-lived \"none\" marker so repeated lookups stop reaching the database."),
            ("Spread the load in time", "Add random jitter to TTLs (for example 300 plus or minus 30 seconds) so entries written together do not expire together."),
        ],
        groups=[
            dict(title="Reproduce a stampede and fix it", cmds=[
                dict(volatile=True, c=r'''. ~/cache/rig.sh; redisup; cd ~/cache; cat > stampede.py <<'EOF'
import sys, threading, time
sys.path.insert(0, '.')
from rc import R
calls = [0]; guard = threading.Lock()
def expensive():
    with guard: calls[0] += 1
    time.sleep(0.3)                                  # an expensive query: 300 ms
    return 'page'
def naive(r):
    if r.cmd('GET', 'page') is None:
        r.cmd('SET', 'page', expensive(), 'EX', 60)
def guarded(r):
    if r.cmd('GET', 'page') is not None: return
    if r.cmd('SET', 'page:lock', '1', 'NX', 'PX', 5000):         # only ONE caller wins the lock
        r.cmd('SET', 'page', expensive(), 'EX', 60); r.cmd('DEL', 'page:lock')
    else:                                                        # everybody else waits for the winner
        for _ in range(100):
            time.sleep(0.02)
            if r.cmd('GET', 'page') is not None: return
def run(fn):
    R().cmd('FLUSHALL'); calls[0] = 0
    ts = [threading.Thread(target=fn, args=(R(),)) for _ in range(40)]
    t = time.perf_counter(); [x.start() for x in ts]; [x.join() for x in ts]
    return calls[0], (time.perf_counter() - t) * 1000
for name, fn in (('no protection', naive), ('with a lock', guarded)):
    n, ms = run(fn)
    print('%-14s 40 simultaneous requests -> %2d expensive database calls, finished in %4.0f ms' % (name, n, ms))
EOF
python3 stampede.py; redisdown''',
                     e="Forty requests ask for the same expired key at once. Without protection, nearly all of them miss and each runs the 300 ms query: forty database calls for one answer. With the lock, one caller wins `SET ... NX` and rebuilds the entry while the other thirty-nine poll the cache and return as soon as it appears: **one** database call. Same latency for users, one fortieth of the load for the database.",
                     annot=[("no protection ... ~40 expensive database calls", "every request missed and recomputed: the stampede (the exact count depends on timing, but it is close to the number of requests)"),
                            ("with a lock ... 1 expensive database call", "`SET page:lock 1 NX PX 5000` succeeds for exactly one caller; the lock expires after 5 s even if that caller crashes"),
                            ("finished in ~330 ms", "the waiters complete just after the winner's 300 ms rebuild: users wait about the same, the database does 1/40th of the work")]),
                dict(c=r'''. ~/cache/rig.sh; redisup; cd ~/cache; cat > penetration.py <<'EOF'
import sys
sys.path.insert(0, '.')
from rc import R
r = R()
def lookup(key, negative_caching, counter):
    v = r.cmd('GET', key)
    if v is not None:
        return None if v == 'NONE' else v
    counter[0] += 1                          # a real database query: the row does not exist
    if negative_caching:
        r.cmd('SET', key, 'NONE', 'EX', 60)  # remember "not found" for a minute
    return None
for neg in (False, True):
    r.cmd('FLUSHALL'); db_queries = [0]
    for _ in range(10000): lookup('user:999999', neg, db_queries)
    print('negative caching %-5s: 10,000 lookups of a missing id -> %5d database queries' % (neg, db_queries[0]))
EOF
python3 penetration.py; redisdown''',
                     e="Cache penetration: 10,000 requests for an ID that does not exist. A plain cache-aside never stores anything for it, so every one of the 10,000 requests reaches the database. Storing a short-lived \"not found\" marker (negative caching) turns that into a single database query. Keep the negative TTL short, so a record that is created a moment later becomes visible soon.",
                     annot=[("negative caching False: ... 10000 database queries", "a missing key is never cached, so every lookup falls through to the database"),
                            ("negative caching True: ... 1 database queries", "after the first miss a `NONE` marker is cached for 60 s and the other 9,999 lookups are answered by the cache")]),
            ]),
        ],
        scenario=dict(
            title="\"What is a cache stampede, and how would you prevent it?\"",
            ask="A favourite follow-up after you say \"I would add a cache\". It tests whether you have thought about what happens at the moment a cache entry disappears.",
            clarify=[("Which keys are hot, and how expensive is a rebuild?", "A stampede matters for hot keys with expensive rebuilds; a cheap query barely notices.")],
            think=[("Describe the failure precisely.", "A hot key expires or is evicted. Many concurrent requests miss, and each independently recomputes the value from the database. The database sees a burst of identical expensive queries exactly when load is highest, and can slow or fail, which makes the rebuild even slower and more requests pile up."),
                   ("Give the family of fixes.", "(1) Single flight: only one request rebuilds; others wait or reuse. (2) Serve stale while revalidating: keep the old value a little longer and refresh in the background. (3) Jittered TTLs so entries do not expire together. (4) Refresh ahead for the hottest keys. (5) Never let a cache expire on its own for the very hottest data: update it from the writer."),
                   ("Explain the lock approach concretely.", "`SET lock NX PX 5000` gives the lock to exactly one caller and expires by itself if that caller dies; the winner recomputes, stores the value and deletes the lock; losers poll the cache briefly or return stale data."),
                   ("Mention the related problems.", "Cold start after a restart is a stampede on every key; penetration (missing keys) bypasses the cache entirely; hot keys overload one node."),
                   ("Say how you would test it.", "Load test with an expiring key and watch database queries per second: it should not spike.")],
            answer=["\"A stampede is what happens when a very popular cache entry expires or is evicted: many concurrent requests all miss at once and each recomputes the same value from the database, so the database gets a burst of identical expensive queries just when traffic is highest, and may slow down or fail.",
                    "To prevent it I would make only one request rebuild the entry. In Redis that is a lock with SET NX and an expiry: the winner recomputes and refills the cache, and the others briefly wait for the cache to be filled or serve the previous value. I would also add random jitter to TTLs so entries do not all expire together, and refresh the very hottest keys before they expire. After a restart the whole cache is cold, which is a stampede on every key, so I would warm it or bring nodes back gradually. And I would load test an expiring hot key to see the database stays flat.\""],
            follow=[("What is stale-while-revalidate?", "Serving the old value past its expiry while a background request fetches a new one: users never wait for a rebuild, at the cost of slightly older data."),
                    ("What if the lock holder crashes?", "The lock has an expiry (PX), so after that time another request can take it; choose it longer than a normal rebuild and shorter than your tolerance for a stall."),
                    ("How does a Bloom filter help penetration?", "It answers \"definitely not present\" cheaply for IDs that cannot exist, so invalid lookups are rejected before they reach the cache or the database; it may say \"maybe present\" wrongly but never the reverse.")],
            slips=["Only describing the problem without a concrete fix.", "A lock without an expiry: one crash blocks the key forever.", "Forgetting cold starts and missing keys, which are cousins of the same problem."],
        ),
        quick=[
            ("What does `SET key value NX PX 5000` do and why is it useful?", "It sets the key only if it does not exist, with a 5 second expiry: exactly one caller wins, so it works as a self-expiring lock."),
            ("What is negative caching?", "Caching the fact that something does not exist, for a short time, so repeated lookups of missing keys stop hitting the database."),
            ("Why add jitter to TTLs?", "So entries created together do not all expire together, which would send a burst of misses to the database."),
        ],
        traps=[
            "A lock without an expiry: if the holder crashes the key is stuck.",
            "A long negative-cache TTL: a record created a moment later stays invisible.",
            "Fixing stampedes only for one key: after a restart every key is a stampede, so protect the database as a whole.",
        ],
    ),
    dict(
        title="Redis, memcached and distributed caches",
        tier="hot",
        situation="One cache server holds a few gigabytes and handles maybe a hundred thousand operations a second. Your data and traffic are bigger. What is the difference between Redis and memcached, and how do you spread a cache over many machines?",
        learn=["What Redis offers beyond a key-value map", "Memcached: the simplest possible cache", "Persistence and replication in Redis", "Distributing a cache: client-side sharding and consistent hashing"],
        model=[
            "**memcached** is a plain, very fast, multi-threaded in-memory key-value cache: strings with a TTL, LRU eviction, no persistence, no data structures. **Redis** is an in-memory **data structure server**: strings, **lists**, **hashes**, **sets**, **sorted sets** (leaderboards), counters, streams, pub/sub, atomic operations and scripts, optional **persistence** (RDB snapshots and an append-only file) and **replication**. The extra power is why Redis is also used for queues, rate limiters, sessions and leaderboards, and why it needs more care: with persistence and rich types it can be a database, with the responsibilities of one. Redis executes commands on one thread, so each command is atomic.",
            "To go beyond one machine you **shard**: split the keys over several nodes. The simplest way is **client-side sharding**: the client hashes the key and picks a node; with **consistent hashing** adding or removing a node moves only about 1/N of the keys instead of almost all (as shown in the load balancing module). **Redis Cluster** does this server-side with 16,384 hash slots spread across nodes, plus replicas for failover. Replication gives read capacity and survival of a node loss, but replicas can lag, so a read from a replica may be slightly stale. Treat a cache node's death as normal: the cluster loses that share of the data and the database absorbs the misses.",
        ],
        analogy="memcached is a coat-check counter: hand over a coat, get a ticket, nothing more. Redis is a whole cloakroom attendant who also sorts hats, keeps a running tally, and can write the log to a ledger.",
        sim=None,
        walk=[
            ("Pick by what you store", "Plain cached blobs with TTLs and maximum simplicity: memcached or Redis. Anything with structure or atomicity (counters, queues, sorted sets, locks): Redis."),
            ("Persistence is optional, and a trade-off", "RDB takes periodic snapshots (fast restart, may lose the last minutes); AOF logs every write (less loss, more disk work). A pure cache usually needs neither."),
            ("Replicate for survival and read capacity", "A replica copies the primary's data. If the primary dies, a replica is promoted. Replication is asynchronous, so a promoted replica may miss the latest writes."),
            ("Shard for size and write throughput", "Hash each key to a node. Consistent hashing or hash slots limit data movement when nodes join or leave."),
            ("Plan for loss", "When a node dies its keys miss until reloaded; the database must absorb that. Avoid putting everything on a few huge nodes: lose one and a large share of the cache goes cold."),
        ],
        groups=[
            dict(title="Redis structures, memcached's protocol, and persistence", cmds=[
                dict(volatile=True, c=r'''. ~/cache/rig.sh; redisup
echo "--- a list used as a queue"; rcli lpush jobs job1 job2 job3 >/dev/null; rcli lrange jobs 0 -1 | tr '\n' ' '; echo
echo "--- a hash: one object, several fields"; rcli hset user:1 name Asha age 31 >/dev/null; rcli hgetall user:1 | paste -sd' '
echo "--- a sorted set: a leaderboard"; rcli zadd board 120 ann 90 bob 150 cho >/dev/null; rcli zrevrange board 0 2 withscores | paste -sd' '
echo "--- an atomic lock: SETNX"; rcli setnx lock owner1; rcli setnx lock owner2
redisdown''',
                     e="What makes Redis more than a cache. The same server stores a **list** (here used as a queue of jobs, newest first), a **hash** (an object with fields), and a **sorted set** (members ordered by score: a leaderboard that Redis keeps sorted for you). `SETNX` sets a key only if it does not exist: the first caller gets `1`, the second `0`, which is the primitive behind locks.",
                     annot=[("job3 job2 job1", "`LPUSH` adds to the front, so the list reads newest first; `RPOP` would take the oldest: a queue"),
                            ("name Asha age 31", "a hash returns its field names and values: a whole record under one key"),
                            ("cho 150 ann 120 bob 90", "`ZREVRANGE ... WITHSCORES` returns members from highest score to lowest: Redis keeps the order, so a top-N query is trivial"),
                            ("1 then 0", "the first SETNX created the key (1), the second found it existing (0): only one caller can hold the lock")]),
                dict(volatile=True, c=r'''. ~/cache/rig.sh; memcached -p 11311 -U 0 -d -P $C/mc.pid -m 16; sleep 0.5
printf 'set k 0 60 5\r\nhello\r\nget k\r\nget missing\r\nstats\r\nquit\r\n' | nc -q1 127.0.0.1 11311 | tr -d '\r' | grep -E '^(STORED|VALUE|hello|END|STAT (cmd_get|get_hits|get_misses|curr_items|limit_maxbytes))'
kill $(cat $C/mc.pid); sleep 0.3''',
                     e="memcached's whole protocol is plain text. `set k 0 60 5` means: key `k`, flags 0, expire in 60 seconds, 5 bytes of data follow. `get` returns the value or nothing. `stats` shows what you would monitor: gets, hits, misses, items, the memory limit. Two gets were made (one hit, one miss), so the hit ratio here is 50 percent. That is all memcached does, and it does it extremely fast on many threads.",
                     annot=[("STORED", "reply to `set`: the value was accepted"),
                            ("VALUE k 0 5 / hello / END", "the `get` hit: key, flags, length, then the data; END closes the response (a miss returns only END)"),
                            ("STAT cmd_get 2 / get_hits 1 / get_misses 1", "two reads: one hit and one miss: the counters behind a hit ratio"),
                            ("STAT limit_maxbytes 16777216", "the memory limit set with `-m 16` (megabytes): memcached evicts least recently used items beyond it")]),
                dict(volatile=True, c=r'''. ~/cache/rig.sh; redisup; rcli set persist-me 42 >/dev/null; rcli save; ls -l $C/dump.rdb | awk '{print "snapshot file:", $5, "bytes"}'; redisdown
redisup; echo "after a restart, persist-me = $(rcli get persist-me)"; redisdown; rm -f $C/dump.rdb''',
                     e="Redis persistence in action. `SAVE` writes a snapshot (`dump.rdb`) to disk. After the server is stopped and started again in the same directory it loads the snapshot, so the key is still there. A pure cache usually runs without persistence (a restart simply starts cold); a Redis used for sessions, queues or leaderboards usually wants it, and a write-ahead style append-only file for less data loss.",
                     annot=[("OK", "`SAVE` completed: the snapshot is on disk"),
                            ("snapshot file: ~100 bytes", "a tiny file for a tiny data set; real snapshots hold the whole data set"),
                            ("after a restart, persist-me = 42", "the data was reloaded from the snapshot on startup; without persistence it would be empty (a cold cache)")]),
            ]),
        ],
        scenario=dict(
            title="\"Redis or memcached? And how would you design a distributed cache for a service with 50,000 requests per second?\"",
            ask="Two questions in one. First a comparison, then a design with numbers.",
            clarify=[("What will be stored: plain values, or structures and counters? How large, how many keys?", "Sizes and structure decide the product and the node count."),
                     ("What happens if a cache node is lost?", "If the database cannot take the misses, you need replicas and gradual warm-up.")],
            think=[("Compare briefly.", "memcached: simplest, multi-threaded, pure LRU cache, no persistence or types. Redis: data structures, atomic operations, persistence and replication, single-threaded per instance. For a plain read cache either works; Redis is the default choice because of flexibility."),
                   ("Estimate load.", "50,000 requests per second with a 90 percent hit ratio means 45,000 cache reads per second and 5,000 database reads per second. One Redis node can do on the order of 100,000 simple operations a second, so one node is enough for throughput; memory and availability decide the rest."),
                   ("Estimate memory.", "Hot set of 20 million entries at 1 KB with about 100 bytes of overhead is about 22 GB. That fits on a large node but is risky as a single failure domain: shard across several nodes, for example four of 8 GB each with replicas."),
                   ("Place the data.", "Consistent hashing or hash slots (Redis Cluster) over the nodes so that adding capacity moves only a fraction of the keys."),
                   ("Handle failure.", "Each shard has a replica for failover. Losing a shard sends about 1/N of reads to the database: size the database for that, warm the replica, and protect with rate limits."),
                   ("Handle hot keys and stampedes.", "Local in-process caches for the hottest keys, locks for rebuilds, jittered TTLs.")],
            answer=["\"For a plain read cache either would work, but I would choose Redis because it also gives atomic operations, structures and optional persistence and replication; memcached is simpler and multi-threaded and fine if all I need is key-value with LRU.",
                    "With 50,000 requests per second and a 90 percent hit ratio, the cache serves 45,000 reads per second and the database 5,000. One node can handle that throughput, so I size for memory and failure: say 20 million hot entries at about 1 KB plus overhead is roughly 22 GB, so I would shard over four or more nodes using Redis Cluster hash slots or client-side consistent hashing, each with a replica. Losing one shard means about a quarter of reads fall through to the database, so the database must be able to absorb that, or I add more, smaller shards. For hot keys I would add a small local cache in each application server, and protect rebuilds with locks and jittered TTLs.\""],
            follow=[("How does Redis Cluster distribute keys?", "It divides keys into 16,384 hash slots (`CRC16(key) mod 16384`) and assigns ranges of slots to nodes; moving a slot between nodes rebalances the data. Clients learn the map and talk to the right node."),
                    ("Why is Redis fast with one thread?", "Everything is in memory, commands are simple and short, there are no locks to contend for, and an event loop handles many connections; the cost is that one slow command (for example `KEYS *` on a big data set) blocks everyone."),
                    ("Should you use Redis as your primary database?", "It can be, with persistence and replication configured, if the data fits in memory and you accept its durability trade-offs. For a pure cache, treat it as disposable.")],
            slips=["Choosing Redis for everything without saying why.", "Sizing only by throughput and forgetting memory and failure domains.", "Running slow commands like KEYS * in production."],
        ),
        quick=[
            ("Name three things Redis offers that memcached does not.", "Data structures (lists, hashes, sorted sets...), persistence and replication, atomic operations and scripts."),
            ("Why does sharding with consistent hashing help when you add a cache node?", "Only about 1/N of the keys move to the new node; with plain modulo hashing almost every key would change node and the cache would go cold."),
            ("What happens to reads when one of four cache shards dies?", "About a quarter of the keys miss and fall through to the database until they are reloaded or a replica takes over."),
        ],
        traps=[
            "Using `KEYS *` or other O(N) commands in production: Redis is single-threaded, so everything waits.",
            "Persistence settings left at defaults without checking what they actually guarantee.",
            "Treating a replica as always current: asynchronous replication can lag.",
        ],
    ),
    dict(
        title="HTTP caching and CDNs: caching at the edge of the internet",
        tier="hot",
        situation="Your server is in Frankfurt and your users are in Singapore. Every image and script crosses the planet. Meanwhile your server answers the same request for the same logo millions of times. Caching in HTTP and at a CDN solves both.",
        learn=["Cache-Control, ETag, Last-Modified and 304", "Fresh versus stale, and revalidation", "Shared versus private caches, Vary", "Versioned URLs and CDN purging"],
        model=[
            "HTTP has caching built in, controlled by response headers. **Cache-Control: max-age=N** says the response is **fresh** for N seconds: caches serve it without asking. `public` allows shared caches (CDNs, proxies) to keep it, `private` only the browser, `no-store` forbids storing, `no-cache` allows storing but demands **revalidation** each time. When a stored response is stale, the cache **revalidates**: it sends `If-None-Match: <ETag>` (or `If-Modified-Since`), and if nothing changed the origin answers **304 Not Modified** with no body, so only a few bytes travel. `Vary: Accept-Encoding` tells caches that the response differs by that request header, so they must store a variant per value.",
            "A **CDN** is a network of shared cache servers (**edges**) near users. The first request near an edge is a miss and goes to the **origin**; later ones are hits served close to the user, cutting latency and origin load. The hard part is **change**: you cannot recall copies in browsers. The standard answer is **versioned (fingerprinted) URLs**: `app.7f3a9c.js` can be cached for a year with `immutable` because a new build gets a new name; only the HTML page that references it must stay short-lived. For things that must change now, CDNs offer **purge/invalidation** APIs, used sparingly.",
        ],
        analogy="Local branch libraries: a popular book is stocked at every branch (edge), so most readers never travel to the central archive (origin). A new edition gets a new title (versioned URL), so nobody can accidentally keep reading the old one.",
        visual=[HTTP_SEQ],
        sim="cdn",
        walk=[
            ("First request: nothing is cached", "The browser asks the CDN edge; the edge misses and asks the origin; the origin answers with the content and caching headers."),
            ("The response travels back, leaving copies", "The edge stores it (if `public` and allowed) and the browser stores it. Both now know how long it is fresh."),
            ("Fresh: served without asking", "Within `max-age` the browser reuses its copy with no network at all; other users near the same edge are served by the edge without touching the origin."),
            ("Stale: revalidate", "After expiry the cache sends a conditional request with the ETag. If unchanged, a 304 renews the copy for free; if changed, the full new response arrives."),
            ("Change safely with new names", "Deploy `app.8b21d4.js` instead of editing `app.7f3a9c.js`; update the short-lived HTML to point at it. No purge needed."),
            ("Purge only when you must", "For urgent fixes use the CDN's purge API for specific paths or tags; purging everything sends the full load to the origin."),
        ],
        groups=[
            dict(title="Headers and conditional requests, on a local server and a real CDN", cmds=[
                dict(volatile=True, c=r'''. ~/cache/rig.sh; cd ~/cache; cat > httpcache.py <<'EOF'
import http.server, socketserver
VERSION = [1]
class H(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    def reply(self, code, headers, body=b''):
        self.send_response(code)
        for k, v in headers: self.send_header(k, v)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.path == '/app.7f3a9c.js':          # fingerprinted file: safe to cache for a year
            self.reply(200, [('Cache-Control', 'public, max-age=31536000, immutable')], b'console.log(1);' * 20)
        elif self.path == '/price':                 # changing data: short freshness plus validation
            etag = '"v%d"' % VERSION[0]
            if self.headers.get('If-None-Match') == etag:
                self.reply(304, [('ETag', etag), ('Cache-Control', 'public, max-age=5')])
            else:
                self.reply(200, [('ETag', etag), ('Cache-Control', 'public, max-age=5'), ('Vary', 'Accept-Encoding')], b'price: 19.99\n')
        else:
            self.reply(404, [('Cache-Control', 'no-store')], b'not found\n')
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
socketserver.TCPServer(('127.0.0.1', 8101), H).serve_forever()
EOF
(python3 httpcache.py >/dev/null 2>&1 &); sleep 1
echo "--- a fingerprinted static file:"; curl -s -D - -o /dev/null http://127.0.0.1:8101/app.7f3a9c.js | grep -i cache-control | tr -d '\r'
echo "--- changing data, first request:"; curl -s -D - http://127.0.0.1:8101/price | grep -iE '^(HTTP|etag|cache-control|vary|price)' | tr -d '\r'
echo "--- revalidation with the ETag we hold:"; curl -s -o /dev/null -w 'status %{http_code}, body bytes %{size_download}\n' -H 'If-None-Match: "v1"' http://127.0.0.1:8101/price
pkill -f httpcache.py''',
                     e="HTTP caching with the headers you will actually set. A fingerprinted file is marked `public, max-age=31536000, immutable`: any cache may keep it for a year and never needs to ask again (a new build would have a new name). A changing resource is fresh for only 5 seconds and carries an `ETag`; after that a cache asks \"still `v1`?\" with `If-None-Match` and receives a **304 with no body**, renewing its copy for the price of a header exchange. `Vary` tells caches this response depends on the request's `Accept-Encoding`.",
                     annot=[("Cache-Control: public, max-age=31536000, immutable", "one year, shared caches allowed, and never revalidate: right for a file whose name changes when its content changes"),
                            ("ETag: \"v1\"", "the version label of this response: the key for later conditional requests"),
                            ("Cache-Control: public, max-age=5", "fresh for 5 seconds: during that time a cache answers without contacting the origin"),
                            ("Vary: Accept-Encoding", "the stored copy applies only to requests with the same Accept-Encoding: caches keep one variant per value"),
                            ("status 304, body bytes 0", "revalidation succeeded: the origin confirmed the cached copy and sent no body at all")]),
                dict(volatile=True, c=r'''curl -sI https://example.com | tr -d '\r' | grep -iE '^(HTTP|cache-control|age|etag|vary|server|cf-cache-status|content-encoding)' ''',
                     e="The headers of a real site that sits behind a CDN. this site's CDN hides `cache-control` and `etag` from this request (other sites show them); `age` is how many seconds the CDN has held this copy; `cf-cache-status` (the name is CDN-specific) reports whether this response was a `HIT` from an edge or a `MISS`. Run it twice: the `age` and status tell you whether you were served from the edge.",
                     annot=[("HTTP/2 200", "the version negotiated and the status"),
                            ("server: cloudflare", "the CDN edge answered, not the origin"),
                            ("age: N", "seconds this copy has sat in the CDN's cache: proof that it was served from a cache, not generated now"),
                            ("cf-cache-status: HIT", "this CDN's report of an edge cache hit; other CDNs use headers such as `x-cache`")]),
            ]),
        ],
        scenario=dict(
            title="\"How would you design caching for a news website with global readers and breaking news that must update within a minute?\"",
            ask="They want to see you combine CDN, HTTP headers, application caches and invalidation, and handle the \"breaking news\" exception without caching everything for an hour.",
            clarify=[("How many readers, how spread out, and what is the read to write ratio?", "Millions of readers and a few editors means almost everything is cacheable for at least a few seconds."),
                     ("How fast must an edit appear, and is it acceptable for different users to see different versions briefly?", "A minute of staleness is the budget here."),
                     ("Which parts are personalised (login, recommendations)?", "Personalised parts must not be cached in shared caches.")],
            think=[("Split the page by how it changes.", "Static assets (CSS, JS, images): fingerprinted URLs, `max-age` of a year, `immutable`. Article HTML: shared and short-lived. Personalised fragments: loaded separately and not cached publicly (`private` or `no-store`)."),
                   ("Cache the HTML at the CDN with a short freshness.", "`s-maxage=30` (for shared caches) with `stale-while-revalidate` so users are never made to wait for a refresh. Even a 30 s TTL cuts origin traffic by orders of magnitude at high request rates."),
                   ("Use revalidation.", "ETag on articles so a stale copy is renewed with a 304 instead of a full download."),
                   ("Handle breaking news.", "Combine the TTL with explicit purge: when an editor publishes or edits, the publishing system calls the CDN's purge API for that URL (and the section pages that list it), using surrogate keys or tags to purge groups."),
                   ("Protect the origin.", "Origin shielding (a regional tier between the edges and the origin) so a purge or cold edges do not send every edge's request to the origin; request collapsing so simultaneous misses become one fetch."),
                   ("Say what you monitor.", "Edge hit ratio, origin request rate, purge latency, and the age of served content.")],
            answer=["\"I would split the page by how it changes. Static assets get fingerprinted file names and a year of caching as immutable. The article HTML is cached at the CDN for a short time, say thirty seconds with stale-while-revalidate, plus an ETag so revalidation costs a 304. That alone absorbs almost all of the load. Personalised parts, like the logged-in user's name or recommendations, are loaded separately with private or no-store so they never enter a shared cache.",
                    "For breaking news the TTL is not enough, so publishing triggers a purge of that article and the section pages that list it, using tags so one call covers all affected URLs. To keep purges and cold edges from hammering the origin I would use an origin shield tier and request collapsing so concurrent misses become one origin fetch. I would watch edge hit ratio, origin request rate and purge latency.\""],
            follow=[("What is the difference between max-age and s-maxage?", "`max-age` applies to every cache including the browser; `s-maxage` applies only to shared caches such as CDNs and overrides `max-age` for them, so you can keep browsers short and the CDN longer or the reverse."),
                    ("What does `no-cache` mean versus `no-store`?", "`no-cache` lets caches store the response but requires revalidation before each reuse; `no-store` forbids storing it at all (use for sensitive data)."),
                    ("How can a CDN cache an API response that varies by user?", "Do not, unless the cache key includes the identifying value (careful: low hit ratio and privacy risk). Cache the shared parts, or use short-lived signed URLs for per-user content.")],
            slips=["Putting one long TTL on HTML and being unable to ship a fix.", "Caching personalised responses in a shared cache: one user sees another's data.", "Purging the whole CDN as a routine action."],
        ),
        quick=[
            ("What does a 304 response mean?", "Not Modified: the client's cached copy is still valid and no body is sent."),
            ("Why do fingerprinted file names make long caching safe?", "A changed file gets a new name, so nobody can hold an outdated copy under the same URL."),
            ("What is the difference between `no-cache` and `no-store`?", "`no-cache` allows storing but requires revalidation each time; `no-store` forbids storing."),
        ],
        traps=[
            "A long `max-age` on a URL that is not versioned: you cannot update it until every cache expires.",
            "Caching responses that contain personal data in a shared cache (check `Cache-Control: private`).",
            "Forgetting `Vary`: a gzip response served to a client that did not ask for gzip.",
        ],
    ),
    dict(
        title="Sizing, choosing what to cache, and proving it works",
        tier="hot",
        situation="You know the mechanisms. The final skill is applying them to a real system: what to cache, where, how much memory, how to measure, and how to explain the whole plan.",
        learn=["The measured cost of a key in Redis", "How hit ratio grows with cache size (diminishing returns)", "A decision guide: what to cache where", "Measuring the effect"],
        model=[
            "Sizing a cache has three inputs: the **number of hot keys**, the **size of each value** and the **per-key overhead** of the cache. Overhead is real: Redis spends roughly 50 to 100 bytes on bookkeeping for every key on top of the key name and the value, so ten million small keys can cost far more memory than their raw size. The **hit ratio** grows quickly at first and then flattens: with skewed traffic caching the hottest 5 percent of keys may give a 60 percent hit ratio, 20 percent gives 80 percent, and getting from 95 to 99 percent can cost many times more memory than getting from 0 to 95.",
            "Choosing what to cache: **cache what is expensive to compute or fetch, read much more often than it changes, and identical for many requests**. Do not cache data that must always be exactly current, data that is rarely read twice, or unique-per-request results. Prove the effect with numbers: database queries per second, p50 and p99 latency, hit ratio and evictions, before and after. A cache you cannot measure is a guess.",
        ],
        analogy="Stocking a corner shop: you cannot hold every product, so you stock what sells fast and spoils slowly, make room by clearing what nobody buys, and count sales to see whether the shelf space is paying for itself.",
        sim=None,
        walk=[
            ("Find the candidates", "Profile reads: which queries or calls are slow and repeated? Rank by (frequency x cost)."),
            ("Check each against the rules", "Read-heavy? Tolerates the staleness you can bound? Same answer for many requests? If not, skip or cache a shared part only."),
            ("Pick the level and the pattern", "CDN or proxy for shared pages, application cache for computed data, cache-aside with TTL and delete-on-write by default."),
            ("Size it with real overhead", "Hot keys x (value + key name + overhead), plus headroom; measure per-key overhead on your own data."),
            ("Protect the database", "Locks and jitter for stampedes, negative caching for missing keys, rate limits as a backstop, a plan for cold starts."),
            ("Measure and iterate", "Compare database load and latency percentiles before and after; watch hit ratio and evictions continuously."),
        ],
        groups=[
            dict(title="Measure overhead and the shape of the hit-ratio curve", cmds=[
                dict(volatile=True, c=r'''. ~/cache/rig.sh; redisup; cd ~/cache; cat > sizing.py <<'EOF'
import sys
sys.path.insert(0, '.')
from rc import R, stat
r = R()
before = stat(r, 'used_memory')
for i in range(10000):
    r.cmd('SET', 'item:%06d' % i, 'v' * 100)          # 10,000 keys with a 100-byte value
after = stat(r, 'used_memory')
per_key = (after - before) / 10000
print('raw data per key:      %d bytes (11-byte key name + 100-byte value)' % 111)
print('Redis memory per key:  %.0f bytes' % per_key)
print('overhead:              %.0f bytes per key (%.0f%% on top of the data)' % (per_key - 111, 100 * (per_key - 111) / 111))
print('so 10 million such keys need about %.1f GB, not %.1f GB' % (per_key * 1e7 / 1e9, 111 * 1e7 / 1e9))
EOF
python3 sizing.py; redisdown''',
                     e="Measuring instead of guessing. Ten thousand keys with 100-byte values are stored and Redis's own memory counter is compared before and after. Each key costs noticeably more than its data: the key name, the value and Redis's bookkeeping (pointers, expiry, allocator rounding). For small values the overhead can be larger than the data itself, which changes a capacity plan by a large factor.",
                     annot=[("raw data per key: 111 bytes", "what you might assume each key costs"),
                            ("Redis memory per key: ~193 bytes (varies with version)", "what it really costs, measured with `INFO memory`"),
                            ("overhead: ~82 bytes per key", "the bookkeeping on top of the data: more than 70 percent here, because the value is small"),
                            ("10 million such keys need about 1.9 GB, not 1.1 GB", "the planning consequence: always multiply by the measured per-key cost")]),
                dict(c=r'''python3 - <<'EOF'
import random
from collections import OrderedDict
rng = random.Random(7)
N = 100000                                          # distinct items
weights = [1 / (i + 1) for i in range(N)]           # a few items are very popular, most are rare
reqs = rng.choices(range(N), weights, k=200000)
def hit_ratio(cap):
    c, hits = OrderedDict(), 0
    for k in reqs:
        if k in c:
            hits += 1; c.move_to_end(k)
        else:
            if len(c) >= cap: c.popitem(last=False)
            c[k] = 1
    return hits / len(reqs)
print('cache size as a share of all items -> hit ratio, and average latency (1 ms hit, 50 ms miss)')
for pct in (1, 5, 10, 20, 40):
    h = hit_ratio(N * pct // 100)
    print('  %2d%% of the items -> hit ratio %4.1f%%, average %5.1f ms' % (pct, h * 100, h * 1 + (1 - h) * 50))
EOF''',
                     e="The diminishing-returns curve, measured on skewed traffic with an LRU cache. The first 1 percent of items already answers a large part of the requests, and each doubling of the cache adds less than the one before. This is the reason to size a cache for the hot working set, and the reason \"just add more memory\" has an expensive tail.",
                     annot=[("1% of the items -> hit ratio ~51%", "a tiny cache already answers half of the requests because a few items dominate"),
                            ("5% -> 66%, 10% -> 73%, 20% -> 78%", "each step buys less than the last: the curve flattens"),
                            ("40% of the items -> hit ratio 81%, average ~10 ms", "forty times the memory of the 1 percent cache lifts the hit ratio by only 30 points and the average from 25 ms to 10 ms: diminishing returns")]),
            ]),
        ],
        playbook=dict(title="What to cache where", intro=["A decision table: find the kind of data, read the level and settings."], rows=[
            ["Static files (images, JS, CSS)", "CDN and browser; fingerprinted URLs", "Identical for everyone, changes only on deploy", "`Cache-Control: public, max-age=31536000, immutable`"],
            ["Article or catalogue pages, same for all", "CDN or reverse proxy; short TTL; revalidate", "Read-heavy, small staleness is fine", "`s-maxage=30`, ETag, `stale-while-revalidate`, purge on edit"],
            ["Database query results, computed data", "Application cache (Redis)", "Expensive, repeated, same for many callers", "Cache-aside, TTL, delete on write, lock for rebuilds"],
            ["User session, per-user state", "Redis with persistence or a session store", "Read on every request, must survive restarts", "Short TTL refreshed on use; replicate"],
            ["Counters, rate limits, leaderboards", "Redis atomic operations and sorted sets", "Needs atomicity, not just caching", "INCR with expiry, sorted sets"],
            ["Account balances, inventory at checkout", "Do not cache (read the primary)", "Must be exactly current", "Cache only derived or display data"],
        ]),
        scenario=dict(
            title="\"Walk me through adding caching to a slow product page, end to end.\"",
            ask="The capstone question for this module. They want a structured plan that uses what you know: measure, choose levels, patterns, sizing, failure handling, verification.",
            clarify=[("What is the traffic, the page's content mix, and how fresh must prices and stock be?", "Prices tolerate a minute; stock at checkout must be exact.")],
            think=[("Measure first.", "Profile the page: which queries are slow, how many times each runs, and what fraction of requests ask for the same products (skew)."),
                   ("Split by volatility.", "Product description and images: change rarely, cacheable for hours, CDN. Price: changes sometimes, tolerates a minute, cache with short TTL and invalidate on change. Stock level at checkout: not cached. Personalisation: separate, private."),
                   ("Choose levels.", "CDN for images and the shared part of the HTML; Redis for the assembled product data and expensive queries; database untouched except on a miss."),
                   ("Pick patterns and settings.", "Cache-aside with TTLs by data type, delete on write, jittered TTLs, a lock for rebuilds of the hottest products, negative caching for unknown IDs."),
                   ("Size it.", "Hot set of products times value size times measured overhead, plus headroom, sharded with replicas; use the hit-ratio curve to choose a target such as 90 percent rather than 99."),
                   ("Plan for failure and cold start.", "If Redis is down the page must still work (slower): timeouts on cache calls, fall back to the database with a rate limit. Warm the cache before a big sale."),
                   ("Verify with numbers.", "Before and after: database queries per second, page p50 and p99, hit ratio, evictions; run a load test including an expiry event.")],
            answer=["\"I would start by measuring: which queries make the page slow, how often each runs, and how skewed the traffic is across products. Then I split the page by how it changes. Images and descriptions are static enough for the CDN with fingerprinted URLs. The assembled product data goes in Redis with cache-aside, a TTL by data type, and delete-on-write so edits show up quickly. Price tolerates a minute of staleness, stock at checkout is read from the database and never cached, and personalisation is loaded separately and kept private.",
                    "To protect the database I would add jitter to TTLs, a lock so only one request rebuilds a hot product, and negative caching for unknown IDs. I would size Redis from the hot set times the measured per-key memory with headroom, sharded with replicas, aiming for something like a 90 percent hit ratio since the curve flattens after that. If Redis fails, the page must still work, with timeouts on cache calls and a rate-limited fallback to the database. I would verify with before and after numbers: database queries per second, p50 and p99 latency, hit ratio and evictions, including a load test through a key expiry.\""],
            follow=[("How do you know the cache is not serving wrong prices?", "Bound staleness with TTL and delete-on-write, sample cache against the database in a background check and alert on divergence, and make price changes publish an invalidation event."),
                    ("The page is still slow on a cache hit. Why?", "The time may not be in the data fetch: rendering, serialisation, large payloads, many sequential cache calls (batch them with MGET or pipelining), or other services. Profile before adding more caching."),
                    ("How would you prepare for a flash sale?", "Pre-warm the cache for sale items, raise TTLs for the duration, add replicas, rehearse a cold-cache scenario with the database protected by rate limits, and watch hit ratio and eviction live.")],
            slips=["Starting with Redis before measuring anything.", "Caching stock or balances that must be exact.", "Not saying what happens when the cache fails."],
        ),
        quick=[
            ("Why does a Redis key cost more memory than its data?", "Each key carries bookkeeping (pointers, expiry, allocator rounding), commonly 50 to 100 bytes or more on top of the key and value."),
            ("What does the hit-ratio curve tell you about sizing?", "Returns diminish: the hottest few percent of items give most of the hits; getting the last few percent costs disproportionately more memory."),
            ("Name two kinds of data you should not cache.", "Data that must always be exactly current (balances, checkout stock) and results that are unique per request."),
        ],
        traps=[
            "Sizing from raw data size: measure the real per-key memory.",
            "Chasing the last few percent of hit ratio with expensive memory.",
            "Declaring success without before and after measurements of database load and latency percentiles.",
        ],
    ),
]
