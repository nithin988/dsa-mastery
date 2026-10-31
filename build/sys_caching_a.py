"""S17 caching: part A (rig, diagrams, lessons 1 to 3)."""
import sysviz as v

RIG = r'''mkdir -p ~/cache && cd ~/cache && cat > rc.py <<'EOF'
# A minimal Redis client (the Redis wire protocol is simple text), so the experiments need nothing but python3.
import socket
class R:
    def __init__(self, port=6391):
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
def stat(r, name):
    return int([l for l in r.cmd('INFO').split('\r\n') if l.startswith(name + ':')][0].split(':')[1])
EOF
cat > rig.sh <<'EOF'
export C=$HOME/cache
redisup()   { redis-server --port 6391 --bind 127.0.0.1 --save "" --appendonly no --daemonize yes --dir $C --logfile $C/redis.log "$@" >/dev/null; sleep 0.5; }
rcli()      { redis-cli -p 6391 "$@"; }
redisdown() { redis-cli -p 6391 shutdown nosave 2>/dev/null; sleep 0.3; true; }
EOF
. ./rig.sh; echo "rig ready in $C: rc.py (a tiny Redis client) and rig.sh (redisup, rcli, redisdown)"'''

LEVELS_VIZ = v.figure(
    720, 214,
    [v.box(10, 70, 100, 56, "Browser", "acc", "private cache"),
     v.arrow(110, 98, 135, 98), v.box(135, 70, 100, 56, "CDN edge", "acc", "shared, near users"),
     v.arrow(235, 98, 260, 98), v.box(260, 70, 110, 56, "Reverse proxy", "acc", "in front of servers"),
     v.arrow(370, 98, 395, 98), v.box(395, 70, 100, 56, "App cache", "warn", "Redis, memcached"),
     v.arrow(495, 98, 520, 98), v.box(520, 70, 100, 56, "Database", "ok", "buffer pool inside"),
     v.arrow(620, 98, 645, 98), v.box(645, 70, 65, 56, "Disk", "ink"),
     v.text(360, 168, "A request stops at the first level that already has the answer.", "dg-s"),
     v.text(360, 190, "Each level further right is slower, more expensive and shared by fewer or more users.", "dg-s")],
    "The levels of caching", "Every hop to the right costs more time; caches exist to avoid those hops")

ASIDE_SEQ = v.seq(
    ["Client", "App", "Cache", "Database"],
    [("a->b", 0, 1, "GET /user/7"),
     ("a->b", 1, 2, "GET user:7"),
     ("a->b", 2, 1, "miss (nothing stored)", "bad"),
     ("a->b", 1, 3, "SELECT ... WHERE id = 7"),
     ("a->b", 3, 1, "row", "reply"),
     ("a->b", 1, 2, "SET user:7 (expires in 5 min)"),
     ("a->b", 1, 0, "response (slow path: miss)", "reply"),
     ("note", 0, 3, "the next request for user 7 is answered by the cache: no database call"),
     ("a->b", 0, 1, "GET /user/7"),
     ("a->b", 1, 2, "GET user:7"),
     ("a->b", 2, 1, "hit: the stored value", "reply"),
     ("a->b", 1, 0, "response (fast path: hit)", "reply")],
    "Cache-aside: the application manages the cache", "Check the cache first; on a miss read the database and fill the cache")

LESSONS_A = [
    dict(
        title="Why caching works, and where caches live",
        tier="hot",
        situation="Your product page takes 400 ms because it runs six database queries. It is requested 5,000 times a second, and 95 percent of those requests ask for the same few thousand products. Computing the same answer thousands of times is the waste a cache removes.",
        learn=["Why caches work at all (locality)", "The levels of caching from browser to disk", "Hit ratio and what it does to average latency", "Your first real cache: Redis"],
        model=[
            "A **cache** is a small, fast store of answers you already computed or fetched, kept close to whoever asks, so that repeating the question does not repeat the work. It works because real access patterns are **skewed**: a small part of the data gets most of the requests (**locality**, the 80/20 effect). Keep that hot part in fast memory and most requests never reach the slow system.",
            "Caches exist at every level: the **browser**, a **CDN edge**, a **reverse proxy**, an **application cache** such as Redis or memcached, the **database's own buffer pool**, and the CPU caches under all of it. A request stops at the first level that has the answer. The key number is the **hit ratio** (hits divided by hits plus misses). Average latency is `hit_ratio x hit_time + (1 - hit_ratio) x miss_time`, so with a 1 ms hit and a 50 ms miss, a 95 percent hit ratio gives about 3.5 ms, but 50 percent gives 25.5 ms. The last few percent of hit ratio are worth a great deal.",
            "A cache is **not free**: it can serve **stale** data, it has a size limit, it has to be filled and kept consistent, and it is one more component that can fail. Every lesson in this module is about getting the benefit while controlling those costs.",
        ],
        analogy="Keeping the books you use every day on your desk instead of walking to the library each time. The desk is small, so you keep only what you use often, and you must remember to replace a book when a new edition comes out.",
        visual=[LEVELS_VIZ, ASIDE_SEQ],
        sim="cachefill",
        walk=[
            ("A request arrives at the application", "It needs some data: a user profile, a product page, the result of an expensive query."),
            ("Look in the cache first", "The application asks the cache for the answer using a **key** (for example `user:7`). A cache lookup is a single in-memory operation: well under a millisecond."),
            ("Hit: return it immediately", "If the key is present and has not expired, that is a **hit**. The slow system is never touched."),
            ("Miss: go to the source and remember the answer", "If the key is absent (never stored, expired or evicted) that is a **miss**: the application reads the database, then stores the result in the cache with an expiry time, then returns it."),
            ("The next requests are hits", "Until the entry expires, changes or is evicted, every repeat is served from memory. The first request pays, the following thousands are free."),
            ("Measure the hit ratio", "Hits and misses are counted by the cache itself. A falling hit ratio is an early warning: the working set grew, TTLs are too short, or someone changed the key format."),
        ],
        groups=[
            dict(title="Build the rig, then a first look at a real cache", cmds=[
                dict(c=RIG,
                     e="Creates the rig used by the whole module: a minimal Redis client written in a few lines (Redis speaks a very simple text protocol, so Python needs no library) and helper functions to start, query and stop a practice Redis on port 6391. Nothing outside `~/cache` is touched."),
                dict(volatile=True, c=r'''. ~/cache/rig.sh; redisup; rcli set greeting hello; rcli get greeting; rcli expire greeting 30; rcli ttl greeting; rcli set counter 0; rcli incr counter; rcli incr counter; rcli type counter; rcli dbsize; redisdown''',
                     e="The first five minutes with a real cache. `SET` stores a value under a key, `GET` reads it, `EXPIRE` gives the key a time to live in seconds and `TTL` shows how much is left. `INCR` atomically adds one to a number (the basis of counters and rate limits). Redis keeps everything in memory, which is why it is fast.",
                     annot=[("OK", "reply to SET: stored"),
                            ("hello", "the value that GET returned"),
                            ("(integer) 1", "EXPIRE replied 1: the key exists and now has a TTL"),
                            ("30", "seconds left before the key disappears by itself"),
                            ("1 then 2", "INCR returned the new value each time: the operation is atomic, safe for many clients at once"),
                            ("string", "the type of the key (Redis also has lists, hashes, sets, sorted sets...)"),
                            ("2", "DBSIZE: the number of keys now stored")]),
                dict(volatile=True, c=r'''. ~/cache/rig.sh; redisup; cd ~/cache; cat > slow.py <<'EOF'
import sys, time
sys.path.insert(0, '.')
from rc import R, stat
r = R()
def slow_lookup(key):
    time.sleep(0.05)                       # pretend this is a database query that takes 50 ms
    return 'value-for-' + key
def cached_lookup(key):
    v = r.cmd('GET', key)
    if v is None:                          # miss: do the slow thing once, remember the answer
        v = slow_lookup(key)
        r.cmd('SET', key, v, 'EX', 60)
    return v
r.cmd('CONFIG', 'RESETSTAT')
t = time.perf_counter()
for _ in range(20): slow_lookup('item:1')
without = (time.perf_counter() - t) * 1000
t = time.perf_counter()
for _ in range(20): cached_lookup('item:1')
with_cache = (time.perf_counter() - t) * 1000
hits, misses = stat(r, 'keyspace_hits'), stat(r, 'keyspace_misses')
print('20 lookups without a cache: %6.0f ms  (%.1f ms each)' % (without, without / 20))
print('20 lookups with a cache:    %6.0f ms  (%.1f ms each)' % (with_cache, with_cache / 20))
print('Redis counted: %d hits, %d miss, hit ratio %d%%' % (hits, misses, 100 * hits / (hits + misses)))
EOF
python3 slow.py; redisdown''',
                     e="The whole idea in one experiment. A pretend database call takes 50 ms. Twenty identical lookups cost a full second without a cache. With a cache, the first lookup is a miss (50 ms, and the answer is stored) and the other nineteen are hits that take a fraction of a millisecond. Redis itself counts hits and misses, which is the number you watch in production.",
                     annot=[("20 lookups without a cache ... 50.x ms each", "every call pays the full price: 20 x 50 ms = about one second"),
                            ("20 lookups with a cache ... about 53 ms", "one miss (50 ms) plus 19 hits at about 0.1 ms each"),
                            ("19 hits, 1 miss, hit ratio 95%", "from Redis's own counters: the hit ratio explains the speed-up, since average = 0.95 x 0.1 ms + 0.05 x 50 ms")]),
            ]),
        ],
        scenario=dict(
            title="\"The product page is slow and the database is at 90 percent CPU. Would you add a cache, and what do you need to know first?\"",
            ask="A realistic starting question. A weak answer says \"yes, add Redis\". A strong one asks what to measure, decides what to cache, and names the costs.",
            clarify=[("What exactly is slow, and what is the read to write ratio?", "A cache pays off for data that is read much more often than it changes."),
                     ("How skewed are the requests? Do a few items get most of the traffic?", "Skew decides the hit ratio you can reach with a small cache."),
                     ("How stale may the data be?", "Seconds of staleness for a product page are usually fine; for an account balance they are not."),
                     ("Is the slowness really in repeated reads? Is it queries, missing indexes, or something else?", "Fix an obvious missing index first; caching a badly written query hides the problem.")],
            think=[("Measure before caching.", "Find the expensive, repeated reads: slow query log, request counts per key or per query. Cache what is both expensive and frequently repeated."),
                   ("Choose the level.", "Static content: CDN and browser. A rendered page that is the same for everyone: reverse proxy or CDN. Computed data and database results: an application cache such as Redis. Pick the level closest to the user that is still correct."),
                   ("Choose the pattern and the expiry.", "Cache-aside with a TTL fits most read-heavy data: simple, tolerant of cache failure. The TTL bounds how stale an answer can get."),
                   ("Estimate the benefit with the formula.", "If the page is 400 ms on a miss and 5 ms on a hit, a 90 percent hit ratio gives about 45 ms average; and the database sees one tenth of the reads. The skew tells you whether 90 percent is realistic."),
                   ("Name the costs and the failure behaviour.", "Staleness, memory, an extra system to run, and cold starts: what happens when the cache is empty or down. The database must survive a cold cache, or the cache must be warmed and protected (later lessons)."),
                   ("Define how you will know it works.", "Track hit ratio, evictions, latency percentiles and database load before and after.")],
            answer=["\"Before adding a cache I would measure: which queries are expensive and repeated, how skewed the traffic is, and how stale the data may be. If product data is read a hundred times for every write and a few products get most of the traffic, a cache is a good fit.",
                    "I would use cache-aside in an application cache like Redis: check the cache by product key, on a miss read the database and store the result with a TTL of a minute or so, which bounds staleness. Where the page is the same for everyone I would also let a CDN or reverse proxy cache it. With a 5 ms hit and a 400 ms miss, a 90 percent hit ratio gives an average around 45 ms and cuts database reads to a tenth.",
                    "The costs are stale data within the TTL, memory, one more component, and what happens on a cold or failed cache, so I would make sure the database can survive a cold start, monitor hit ratio and evictions, and invalidate or shorten the TTL for data that must be fresher.\""],
            follow=[("How do you decide the TTL?", "From how stale the business can tolerate, and how expensive a miss is. Short TTLs mean fresher data but more misses; long TTLs mean the opposite. Often different data gets different TTLs."),
                    ("What if the hit ratio is only 40 percent?", "Find out why: the working set may be larger than the cache, the key may include something unique per request, or the TTL is too short. A low hit ratio can mean the cache costs more than it saves."),
                    ("Where would you not use a cache?", "Data that must always be exactly current, data that is rarely read twice, and as a patch for a missing index or an inefficient query.")],
            slips=["Adding a cache without measuring what is repeated and expensive.", "Ignoring staleness and the cold-start problem.", "Caching something with a unique key per request: the hit ratio is zero."],
        ),
        quick=[
            ("What does a cache rely on to be effective?", "Skewed access patterns (locality): a small hot set gets most of the requests."),
            ("With a 1 ms hit, 50 ms miss and a 90 percent hit ratio, what is the average latency?", "About 5.9 ms (0.9 x 1 + 0.1 x 50)."),
            ("Name three levels where caching happens.", "Browser, CDN edge, reverse proxy, application cache (Redis or memcached), the database's buffer pool."),
        ],
        traps=[
            "Caching to hide a slow query that an index would fix.",
            "Treating the cache as a source of truth: it can be emptied or lost at any time.",
            "Forgetting that a cold or failed cache sends the full load straight to the database.",
        ],
    ),
    dict(
        title="Caching patterns: cache-aside, write-through, write-behind and friends",
        tier="hot",
        situation="Reads are cached. Now someone updates the product price. How does the cache find out? Different patterns answer that question differently, and each trades speed, simplicity and consistency.",
        learn=["Cache-aside, read-through, write-through, write-behind and refresh-ahead", "How staleness arises and the invalidation rule that fixes most of it", "Race conditions between a cache and a database"],
        model=[
            "**Cache-aside** (lazy loading): the application reads the cache, on a miss reads the database and fills the cache. The cache is just a store; the application owns the logic. Simple and robust: if the cache dies, the application still works (slowly). **Read-through** is the same idea with the cache layer itself loading from the database on a miss. For writes: **write-through** writes to the cache **and** the database together, so reads after a write see the new value, at the cost of write latency and caching data nobody may read. **Write-behind** (write-back) writes to the cache and saves to the database later in batches: fast writes, but data can be lost if the cache dies before it flushes. **Refresh-ahead** reloads hot entries shortly before they expire to avoid a slow miss.",
            "With cache-aside the classic problem is **staleness**: the database changes and the cache still holds the old value until it expires. The usual cure is **invalidate on write**: after updating the database, **delete** the cache entry, so the next read reloads the fresh value. Deleting is safer than updating the cache, because two concurrent updates could otherwise leave an older value in the cache. Even so, a read that started before the write can store an old value after the delete (a small race), which is why every entry also gets a **TTL** as a safety net.",
        ],
        analogy="Cache-aside is checking the shelf first and fetching from the warehouse when it is bare. Write-through is updating the shelf label and the warehouse record at once. Write-behind is updating the shelf now and doing the paperwork at the end of the day: quicker, but a fire in between loses the paperwork.",
        visual=[],
        sim=None,
        walk=[
            ("Reads with cache-aside", "Get from the cache; if missing, read the database, store the value with a TTL, return it. The cache only ever holds what someone asked for."),
            ("Writes: update the database first", "The database is the source of truth, so it must be updated first and must succeed."),
            ("Then invalidate the cache entry", "Delete the key (do not try to write the new value into the cache). The next read misses, reloads the new value and caches it."),
            ("Or write through", "Update the database and the cache together when you know the data will be read soon and you want reads to be consistent immediately. Both writes must succeed or fail together, or they diverge."),
            ("Or write behind", "Acknowledge the write after storing it in the cache, and persist it asynchronously in batches. Use only where losing the last few writes is acceptable, or the cache itself is durable."),
            ("Always keep a TTL", "Even with invalidation, bugs and races leave stale entries; a TTL guarantees they disappear eventually."),
        ],
        groups=[
            dict(title="See staleness appear, and the fixes", cmds=[
                dict(c=r'''. ~/cache/rig.sh; redisup; cd ~/cache; cat > patterns.py <<'EOF'
import sys
sys.path.insert(0, '.')
from rc import R
r = R(); r.cmd('FLUSHALL')
db = {'user:1': 'Asha (plan v1)'}; db_reads = [0]
def db_read(k):
    db_reads[0] += 1; return db[k]
def get(k):                                          # cache-aside read
    v = r.cmd('GET', k)
    if v is None:
        v = db_read(k); r.cmd('SET', k, v, 'EX', 300)
    return v
print('read 1:', get('user:1'), '   (database reads so far: %d)' % db_reads[0])
print('read 2:', get('user:1'), '   (database reads so far: %d)' % db_reads[0])
db['user:1'] = 'Asha (plan v2)'                      # the database changes; nobody tells the cache
print('after an update, no invalidation: ', get('user:1'), '   <- STALE')
r.cmd('DEL', 'user:1')                               # invalidate on write
print('after delete-on-write:            ', get('user:1'))
db['user:1'] = 'Asha (plan v3)'; r.cmd('SET', 'user:1', 'Asha (plan v3)', 'EX', 300)   # write-through
print('after write-through:              ', get('user:1'), '   (database reads: %d, no extra read needed)' % db_reads[0])
EOF
python3 patterns.py; redisdown''',
                     e="Cache-aside and its staleness problem, in a few lines. The first read is a miss (one database read), the second a hit (no database read). Then the database changes and nobody tells the cache: the next read returns the **old** value. Deleting the key on write fixes it (the next read reloads the new value). Write-through also gives a fresh value without any extra database read, because the cache was updated together with the database.",
                     annot=[("read 1 ... (database reads so far: 1)", "a miss: the value came from the database and was stored"),
                            ("read 2 ... (database reads so far: 1)", "a hit: still one database read in total"),
                            ("after an update, no invalidation: Asha (plan v1)   <- STALE", "the cache still holds the old value for up to the TTL (five minutes here): the central weakness of caching"),
                            ("after delete-on-write: Asha (plan v2)", "deleting the key forced a miss, so the fresh value was loaded and cached"),
                            ("after write-through: Asha (plan v3)", "cache and database were updated together, so the next read is a hit that is already fresh")]),
            ]),
        ],
        scenario=dict(
            title="\"How do you keep a cache and a database consistent?\"",
            ask="One of the most common caching questions. The honest answer is that you cannot make them perfectly consistent for free, so you choose how stale is acceptable and how to bound it.",
            clarify=[("How stale can this data be, and what happens if a user sees an old value?", "A profile picture can be minutes stale; a stock count at checkout cannot."),
                     ("Read to write ratio, and how often is the same key written?", "Rarely-written data suits invalidation; constantly changing data may not suit caching at all."),
                     ("Is there one writer path or many (several services update the same table)?", "Every writer must invalidate, which is easy to forget; a central write path is much safer.")],
            think=[("State the baseline.", "Cache-aside with a TTL and delete-on-write. The database is the source of truth; the cache is a disposable copy."),
                   ("Explain the order of operations.", "Write to the database, then delete the cache key. If you delete first, a concurrent read can reload the old value before the write lands and keep it for a whole TTL."),
                   ("Name the remaining race.", "A reader that missed before the write can still store its old value after your delete. This is rare and bounded by the TTL, which is why you always set one."),
                   ("Offer stronger options and their prices.", "Write-through gives fresh reads but ties writes to cache availability. Versioned keys (`user:7:v12`) avoid races. Event-driven invalidation publishes a change event that all caches consume (CDC), at the cost of infrastructure. For must-be-correct data, skip the cache or read from the primary database."),
                   ("Say what you monitor.", "Hit ratio, and sampled comparisons between cache and database to detect divergence.")],
            answer=["\"I treat the database as the source of truth and the cache as a disposable copy. For reads I use cache-aside with a TTL. For writes I update the database first and then delete the cache key, so the next read reloads the fresh value. The order matters: if I deleted first, a concurrent read could reload the old value and keep it for the whole TTL.",
                    "There is still a small race, where a reader that missed before the write stores its old value after my delete, so every entry has a TTL that bounds staleness. If the business cannot tolerate that for some data, I would use write-through, versioned keys, or event-driven invalidation from a change stream, or I would not cache it and read from the primary instead. And I would monitor the hit ratio and compare samples of cache and database to catch divergence.\""],
            follow=[("Why delete rather than update the cache on a write?", "Two concurrent writers can update the database in one order and the cache in the other, leaving the cache with the older value. Deleting lets the next read load whatever is currently in the database."),
                    ("What is write-behind and when is it acceptable?", "The cache acknowledges the write and the database is updated later in batches. It makes writes fast and cheap but can lose the last writes if the cache fails; it fits counters, metrics or view counts, not orders or payments."),
                    ("What happens if the cache delete fails after the database write?", "The cache keeps a stale value until the TTL. Retry the delete (from a queue if necessary), keep TTLs short for important data, and treat the TTL as the guaranteed bound.")],
            slips=["Updating the cache before the database.", "Saying the cache and database are always consistent.", "No TTL: one missed invalidation then lives forever."],
        ),
        quick=[
            ("What is the rule for keeping a cache-aside cache fresh when data changes?", "Update the database first, then delete the cache entry, and keep a TTL as a safety net."),
            ("Why is write-behind dangerous?", "The cache acknowledges writes before they reach the database, so data can be lost if the cache fails before flushing."),
            ("Why delete the cache key instead of overwriting it on a write?", "Concurrent writers could leave an older value in the cache; deleting forces the next read to load the current database value."),
        ],
        traps=[
            "Invalidating before the database write completes: a concurrent read refills the cache with the old value.",
            "Several services writing the same table, only one of which invalidates the cache.",
            "No TTL on cached entries: any missed invalidation becomes permanent staleness.",
        ],
    ),
    dict(
        title="Memory limits and eviction: what a full cache throws away",
        tier="hot",
        situation="Memory is finite. After a week the cache is full. What does it do when a new key arrives: refuse, or delete something? And which something? The answer decides your hit ratio and, sometimes, your outage.",
        learn=["Expiry versus eviction", "LRU, LFU and random eviction", "What Redis does at its memory limit, with real output", "Sizing a cache"],
        model=[
            "Entries leave a cache for two reasons. **Expiry** removes an entry whose TTL ran out (it is stale by definition). **Eviction** removes a still-valid entry because memory is full. The **eviction policy** chooses the victim. **LRU** (least recently used) throws out what has not been touched for longest, on the bet that recent use predicts future use. **LFU** (least frequently used) throws out what is used least often, which protects steadily popular items from being pushed out by a one-time scan. **Random** is surprisingly acceptable and very cheap. **noeviction** refuses new writes with an error when memory is full: right for a database-like use of Redis, dangerous for a cache.",
            "In Redis, `maxmemory` sets the limit and `maxmemory-policy` the behaviour (`allkeys-lru`, `allkeys-lfu`, `volatile-lru` which only evicts keys that have a TTL, `noeviction`...). Redis approximates LRU by sampling a few keys rather than tracking exact order, which keeps it fast. **Sizing:** a cache needs enough memory for the **hot working set**, not for all the data: with skewed traffic the first few percent of the data buy most of the hit ratio, then returns diminish. Remember per-key overhead: a 100-byte value costs noticeably more than 100 bytes in memory.",
        ],
        analogy="A desk with room for ten books. When an eleventh arrives you put one back: the one you have not touched for longest (LRU), or the one you use least overall (LFU). The rule decides whether a one-off reference book can push out your daily dictionary.",
        sim=None,
        walk=[
            ("Memory reaches the limit", "Redis counts bytes used against `maxmemory`. Below the limit nothing is evicted."),
            ("A new write arrives", "Before storing it, Redis checks whether the new key would exceed the limit."),
            ("The policy picks victims", "`allkeys-lru` samples a handful of keys (default five) and removes the one used least recently, repeating until enough memory is free."),
            ("The write succeeds, a cold key is gone", "Callers see no error; the evicted key will simply miss next time and be reloaded from the database."),
            ("Under `noeviction` the write fails", "Redis answers with an error (`OOM command not allowed`) and keeps all existing data. Applications must handle it."),
            ("Watch `evicted_keys`", "A steadily growing count means the working set does not fit: increase memory, shorten TTLs, or cache less."),
        ],
        groups=[
            dict(title="Fill a real Redis past its limit", cmds=[
                dict(volatile=True, c=r'''. ~/cache/rig.sh; redisup --maxmemory 2mb --maxmemory-policy allkeys-lru; cd ~/cache; cat > evict.py <<'EOF'
import sys
sys.path.insert(0, '.')
from rc import R, stat
r = R(); val = 'x' * 1000
r.cmd('SET', 'hot', 'important')
for i in range(3000):                       # about 3 MB of data into a 2 MB cache
    r.cmd('SET', 'k%d' % i, val)
    if i % 50 == 0: r.cmd('GET', 'hot')     # 'hot' keeps being used
print('policy:             ', r.cmd('CONFIG', 'GET', 'maxmemory-policy')[1])
print('keys written:       3000, keys still stored: %d' % r.cmd('DBSIZE'))
print('evicted by Redis:   %d' % stat(r, 'evicted_keys'))
print('oldest key k0 still there?   %s' % ('yes' if r.cmd('EXISTS', 'k0') else 'no'))
print('newest key k2999 still there? %s' % ('yes' if r.cmd('EXISTS', 'k2999') else 'no'))
print('frequently used "hot" key still there? %s' % ('yes' if r.cmd('EXISTS', 'hot') else 'no'))
EOF
python3 evict.py; redisdown''',
                     e="A 2 MB Redis is fed about 3 MB of data under `allkeys-lru`. Nothing fails: Redis quietly evicts the keys that were used least recently. The oldest key is gone, the newest is there, and the `hot` key, touched regularly throughout, survived because LRU keeps what is being used. The exact numbers vary run to run; the pattern does not.",
                     annot=[("policy: allkeys-lru", "any key may be evicted, least recently used first"),
                            ("keys written: 3000, keys still stored: ~1500", "about half of the keys fit in the memory limit"),
                            ("evicted by Redis: ~1500", "the keys thrown away to make room: the rest of the 3000"),
                            ("oldest key k0 still there? no", "written first and never read again: the first to go"),
                            ("newest key k2999 still there? yes", "recently written, so recently used"),
                            ("\"hot\" key still there? yes", "it was read every 50 writes, so it never became the least recently used")]),
                dict(volatile=True, c=r'''. ~/cache/rig.sh; redisup --maxmemory 2mb --maxmemory-policy noeviction; cd ~/cache; cat > noevict.py <<'EOF'
import sys
sys.path.insert(0, '.')
from rc import R
r = R(); val = 'x' * 1000
for i in range(3000):
    try:
        r.cmd('SET', 'k%d' % i, val)
    except Exception as e:
        print('first write refused at key number %d' % i)
        print('error message:', str(e)[:48] + '...')
        break
print('policy:', r.cmd('CONFIG', 'GET', 'maxmemory-policy')[1], '  keys stored:', r.cmd('DBSIZE'))
try:
    print('reading an existing key still works:', r.cmd('GET', 'k0')[:5] + '...')
except Exception as e:
    print('read failed', e)
EOF
python3 noevict.py; redisdown''',
                     e="The same fill with `noeviction`. Redis protects the data it has and **refuses new writes** with an `OOM` error. Reads keep working. That is correct when Redis is the primary store (you must never lose data silently) and a production incident when it is meant to be a cache: the application starts failing on writes. Always choose the policy deliberately.",
                     annot=[("first write refused at key number ~1500", "the memory limit was reached: from here every new key fails"),
                            ("error message: OOM command not allowed when used memory...", "Redis's refusal: the application must catch it, or requests that tried to cache will fail"),
                            ("reading an existing key still works", "the existing data is protected; only writes are refused")]),
            ]),
        ],
        scenario=dict(
            title="\"Your Redis cache's hit ratio has dropped from 95 percent to 60 percent and evictions are climbing. What do you do?\"",
            ask="A production-flavoured question. They are looking for a method: diagnose the cause from numbers, then choose the fix.",
            clarify=[("What changed around the time it dropped?", "A deploy changing key formats or TTLs, a new feature, a traffic spike, a bigger data set: correlation points at the cause."),
                     ("What do memory, evicted_keys and expired_keys show?", "Rising evictions with memory at the limit means the working set no longer fits.")],
            think=[("Read the numbers first.", "`INFO stats` (hits, misses, evicted_keys, expired_keys) and `INFO memory` (used versus max). Evictions climbing with memory at the limit: capacity. No evictions but many misses: TTLs too short or keys not repeating."),
                   ("Separate the causes.", "(1) Working set grew: more distinct hot keys than fit. (2) A new access pattern, such as a scan or a crawler touching each key once, pushing hot keys out (cache pollution). (3) Key explosion: someone put a unique value (timestamp, request ID) in the key, so nothing is ever reused. (4) TTLs shortened. (5) A restart emptied the cache and it is simply cold."),
                   ("Choose the fix to match.", "Capacity: add memory or shard across nodes, and cache smaller values (compress, store only needed fields). Pollution: use LFU, or bypass the cache for scans. Key explosion: fix the key. TTL: restore. Cold start: warm the cache or protect the database."),
                   ("Check the policy.", "`allkeys-lru` or `allkeys-lfu` for a pure cache; `volatile-*` only if some keys must never be evicted; never `noeviction` for a cache."),
                   ("Protect the database meanwhile.", "A falling hit ratio sends extra load to it: rate limit, queue, or serve stale data if needed.")],
            answer=["\"I would start with the numbers: the hit and miss counters, evictions and memory usage. If evictions are climbing and memory is at its limit, the working set no longer fits, either because the data grew or because something is polluting the cache, such as a job that reads every key once. If there are no evictions but lots of misses, I would suspect a key format change that makes keys unique, or TTLs that were shortened, or a restart that left the cache cold.",
                    "The fix follows the cause: add memory or shard the cache and store smaller values for capacity, switch to an LFU policy or bypass the cache for scans for pollution, fix the key or restore the TTL otherwise, and warm the cache after restarts. In the meantime I would protect the database from the extra load with rate limiting, and I would alert on hit ratio and eviction rate so we find out before users do.\""],
            follow=[("LRU versus LFU: when is each better?", "LRU adapts quickly when popularity shifts but a one-off scan can flush it. LFU protects steadily popular items from scans but adapts slowly to new trends; Redis's LFU decays counters over time to soften that."),
                    ("What is cache pollution?", "Data that is read once and never again (for example a full table export) taking space and pushing out hot entries. Avoid by bypassing the cache for such reads or using admission policies."),
                    ("How would you decide how much memory the cache needs?", "Measure the hit ratio at different sizes (or use access logs to simulate), look for the knee of the curve where more memory gives little more hit ratio, and add headroom for key overhead and growth.")],
            slips=["Using `noeviction` for a cache.", "Adding memory without checking why the hit ratio fell.", "Forgetting per-key memory overhead when sizing."],
        ),
        quick=[
            ("What is the difference between expiry and eviction?", "Expiry removes an entry whose TTL has run out; eviction removes a still-valid entry because memory is full."),
            ("What does `noeviction` do when memory is full?", "It refuses new writes with an error and keeps existing data."),
            ("Why might LFU beat LRU for a cache that sees occasional full scans?", "A scan touches many keys once; LRU would treat them as recent and evict hot keys, while LFU keeps frequently used keys."),
        ],
        traps=[
            "Using `noeviction` (the Redis default) for a cache: writes start failing when memory fills.",
            "Sizing by raw data size: key names, pointers and allocator overhead add roughly 100 bytes or more per key.",
            "Treating any eviction as a problem: some eviction is normal; a rising eviction rate with falling hit ratio is the warning sign.",
        ],
    ),
]
