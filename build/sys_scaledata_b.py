"""S19 scaling data: part B (lessons 4 to 6: sharding, NoSQL, choosing a store)."""
import sysviz as v

SHARD_VIZ = v.figure(
    720, 236,
    [v.box(10, 80, 110, 56, "Application", "ink"),
     v.arrow(120, 108, 160, 108), v.box(160, 80, 130, 56, "Router", "warn", "shard = hash(key) mod N"),
     v.arrow(290, 96, 340, 40), v.arrow(290, 108, 340, 108), v.arrow(290, 120, 340, 176),
     v.box(340, 14, 150, 52, "Shard 0", "ok", "keys 0, 3, 6 ..."),
     v.box(340, 82, 150, 52, "Shard 1", "ok", "keys 1, 4, 7 ..."),
     v.box(340, 150, 150, 52, "Shard 2", "ok", "keys 2, 5, 8 ..."),
     v.box(540, 60, 170, 94, "What gets harder", "bad", "queries without the key, cross-shard transactions and joins, resharding, hot keys"),
     v.text(360, 222, "Each shard is a separate database holding a slice of the data; the shard key decides everything.", "dg-s")],
    "Sharding", "Writes and data are split across machines by a key; each machine holds only its slice")

LSM_VIZ = v.figure(
    720, 214,
    [v.box(10, 20, 150, 52, "Write", "ink", "append to a log, then memory"),
     v.arrow(160, 46, 200, 46), v.box(200, 20, 150, 52, "Memtable", "acc", "sorted, in memory"),
     v.arrow(350, 46, 390, 46), v.box(390, 20, 150, 52, "Flush", "warn", "when full: write a sorted file"),
     v.arrow(540, 46, 580, 46), v.box(580, 20, 130, 52, "Sorted runs", "ok", "immutable files"),
     v.arrow(645, 72, 645, 120), v.box(520, 120, 190, 52, "Compaction", "warn", "merge runs, drop old versions"),
     v.text(250, 130, "Read: memtable, then newest run to oldest", "dg-s"),
     v.text(360, 198, "Writes are fast and sequential; reads may check several runs until compaction merges them.", "dg-s")],
    "A log-structured merge tree (LSM)", "The design behind Cassandra, RocksDB, HBase and many NoSQL stores")

SHARDLIB = r'''mkdir -p ~/rep && cd ~/rep && cat > shardlib.py <<'EOF'
# Shard routing in a few lines: a stable hash of the key, modulo the number of shards.
import zlib, subprocess, os
R = os.path.expanduser('~/rep')
def shard(key, n=3):
    return zlib.crc32(str(key).encode()) % n
def sql(db, statement, port=5551):
    r = subprocess.run(['psql', '-X', '-At', '-h', R, '-p', str(port), '-U', 'learner', '-d', db, '-c', statement],
                       capture_output=True, text=True)
    return r.stdout.strip()
EOF
echo "shardlib.py written: shard(key, n) and sql(db, statement)"'''

LESSONS_B = [
    dict(
        title="Sharding: splitting the data across machines",
        tier="hot",
        situation="Indexes are right, caches are warm, replicas absorb the reads, and the primary is still at 90 percent CPU on writes with a disk that will be full in four months. One machine cannot hold or write this much. The only remaining move is to split the data across machines.",
        learn=["What sharding is and how a shard key routes data", "Single-key lookups versus queries without the key", "Resharding: why mod N is painful and consistent hashing helps", "Hot shards and what makes a good shard key"],
        model=[
            "**Sharding** (horizontal partitioning across machines) splits a data set into **shards**, each stored on its own database server, chosen by a **shard key**: `shard = hash(key) mod N`, or a lookup table, or a key range. Writes and data now scale with the number of machines. The price is paid everywhere else: a query that includes the shard key goes to **one** shard, but a query that does not must ask **every** shard and merge the answers (**scatter-gather**); a transaction or join that spans shards is no longer a plain database operation; and changing the number of shards moves data.",
            "Choosing the **shard key** is the most important decision: it must appear in your hot queries, have **many distinct values** and spread load **evenly**. Sharding by tenant makes each customer's data local (great for joins within a tenant) but one giant tenant becomes a **hot shard**; sharding by a high-cardinality id spreads load but scatters related rows. **Resharding** with plain `hash mod N` moves almost every key when N changes; **consistent hashing** (a ring with virtual nodes) or a directory of many small logical shards mapped to machines moves only about 1/N of the data. Shard late: it is expensive to build and to undo.",
        ],
        analogy="A library that outgrows its building and splits into branches by the first letter of the author. Looking up a known author goes to one branch. Asking \"every book about sailing\" means phoning all branches. Adding a branch means moving books, and if one author is enormously popular, that branch is overwhelmed.",
        visual=[SHARD_VIZ],
        sim=None,
        walk=[
            ("Pick a shard key", "It appears in the queries that matter, is high-cardinality, and spreads load."),
            ("Route by hash", "The application (or a router) computes `hash(key) mod N` and talks to that shard only."),
            ("Single-key operations stay cheap", "A lookup or write by the key touches one shard, and a transaction inside one shard keeps full ACID."),
            ("Everything else costs more", "No key means ask all shards and merge; cross-shard changes need sagas or two-phase commit."),
            ("Plan for growth", "Use many logical shards mapped onto fewer machines, or consistent hashing, so adding machines moves little data."),
        ],
        groups=[
            dict(title="Real shards, real routing", cmds=[
                dict(c=SHARDLIB,
                     e="A tiny routing library, the core of every sharded system: a **stable hash** of the key (CRC32, not Python's per-run `hash`) modulo the number of shards, plus a helper to run SQL against one database. The three shards in this lesson are three databases on the practice server (in production each would be its own machine; the routing logic is the same)."),
                dict(volatile=True, c=r'''. ~/rep/rig.sh; priup; cd ~/rep
python3 - <<'EOF'
import sys; sys.path.insert(0, '.')
from shardlib import shard, sql
N = 3
for i in range(N):
    sql('postgres', 'create database shard%d' % i)
    sql('shard%d' % i, 'create table users(id int primary key, email text, name text)')
buckets = [[] for _ in range(N)]
for uid in range(1, 3001):
    buckets[shard(uid, N)].append("(%d,'user%d@example.com','user %d')" % (uid, uid, uid))
for i in range(N):
    sql('shard%d' % i, 'insert into users values ' + ','.join(buckets[i]))
for i in range(N):
    print('shard%d holds %s users' % (i, sql('shard%d' % i, 'select count(*) from users')))
print()
print('lookup by id 1234 (the shard key):')
s = shard(1234, N); print('  router computed shard%d, asked 1 shard ->' % s, sql('shard%d' % s, 'select email from users where id = 1234'))
print('lookup by email (NOT the shard key):')
hits = [(i, sql('shard%d' % i, "select id from users where email = 'user1234@example.com'")) for i in range(N)]
print('  had to ask all %d shards ->' % N, [h for h in hits if h[1]], '(scatter-gather)')
EOF
pg_ctl -D $R/primary -m fast stop >/dev/null''',
                     e="Sharding in miniature. 3,000 users are routed to three databases by `crc32(id) mod 3` and the spread is nearly even. A lookup by **id** (the shard key) is computed locally and asks **one** shard. A lookup by **email** cannot be routed: the router has no way to know which shard holds it, so it asks **all three** and keeps the one that answers. At 3 shards that is a nuisance; at 300 it is a serious cost, which is why queries must be designed around the shard key (or a separate index mapping email to id is maintained).",
                     annot=[("shard0 holds ~1000 users (three nearly equal counts)", "a good hash spreads keys evenly"),
                            ("router computed shardN, asked 1 shard", "the key is in the query, so the router knows exactly where to go"),
                            ("had to ask all 3 shards", "without the shard key every shard must be searched: scatter-gather")]),
                dict(volatile=True, c=r'''cd ~/rep; python3 - <<'EOF'
import sys, bisect, zlib
sys.path.insert(0, '.')
from shardlib import shard
KEYS = range(1, 30001)
old = {k: shard(k, 3) for k in KEYS}
new = {k: shard(k, 4) for k in KEYS}
moved = sum(1 for k in KEYS if old[k] != new[k])
print('hash mod N, adding a 4th shard (3 -> 4): %5d of %d keys move (%d%%)' % (moved, len(KEYS), 100 * moved // len(KEYS)))
def ring(nodes, vnodes=100):
    pts = sorted((zlib.crc32(('%s#%d' % (n, v)).encode()), n) for n in nodes for v in range(vnodes))
    return pts, [p[0] for p in pts]
def owner(r, key):
    pts, hs = r
    i = bisect.bisect(hs, zlib.crc32(str(key).encode())) % len(pts)
    return pts[i][1]
r3, r4 = ring(['s0', 's1', 's2']), ring(['s0', 's1', 's2', 's3'])
moved = sum(1 for k in KEYS if owner(r3, k) != owner(r4, k))
print('consistent hashing, same change:         %5d of %d keys move (%d%%)' % (moved, len(KEYS), 100 * moved // len(KEYS)))
print('(the ideal is 1/4 = 25 percent: only the keys the new shard now owns)')
EOF''',
                     e="Why resharding with `mod N` is painful. Going from 3 to 4 shards changes `hash mod N` for most keys, so roughly **three quarters of the data has to move**. A consistent-hashing ring with virtual nodes moves only the keys that the new shard takes over, close to the ideal 25 percent. Real systems use this idea (or many small logical shards assigned to machines) so that adding capacity is a controlled copy, not a data earthquake.",
                     annot=[("hash mod N ... ~75% move", "adding one shard remaps most keys"),
                            ("consistent hashing ... ~25% move", "only keys now owned by the new shard move")]),
                dict(c=r'''python3 - <<'EOF'
import random, collections
rng = random.Random(5)
N = 4
def load(pick_key):
    c = collections.Counter()
    for i in range(100000):
        tenant = 1 if rng.random() < 0.4 else rng.randint(2, 500)     # one tenant sends 40% of all requests
        c[pick_key(i, tenant) % N] += 1
    return c
for name, fn in (('shard by tenant_id', lambda i, t: t), ('shard by request id', lambda i, t: i)):
    c = load(fn)
    print('%-20s' % name, '  '.join('shard%d %2d%%' % (s, c[s] / 1000) for s in range(N)))
EOF''',
                     e="The hot-shard problem, measured. One large tenant produces 40 percent of the traffic. Sharding by `tenant_id` puts all of that tenant on a single shard, which then carries a disproportionate share of the load (and will fill up first). Sharding by a high-cardinality request id spreads the load evenly, but then one tenant's rows are scattered over all shards. The right key depends on which queries matter most; big tenants are usually handled by giving them a dedicated shard.",
                     annot=[("shard by tenant_id: shard1 54%, the others about 15%", "the big tenant makes one shard carry more than half the load"),
                            ("shard by request id: ~25% each", "an even spread, at the price of scattered tenant data")]),
            ]),
        ],
        scenario=dict(
            title="\"Your database cannot handle the write load. Walk me through sharding it.\"",
            ask="A core scaling question. They expect you to exhaust the cheaper options first, then choose a key with reasoning and discuss the pain points.",
            clarify=[("What is the workload: read heavy or write heavy? How big is the data and how fast is it growing?", "Read-heavy problems are solved with replicas and caches; sharding is for write throughput or size beyond one machine."),
                     ("What are the main query patterns?", "The shard key must appear in the hot queries.")],
            think=[("Exhaust cheaper options first.", "Indexes, query fixes, caching, replicas, partitioning, bigger hardware. Sharding adds permanent complexity."),
                   ("Choose the shard key from the queries.", "For a multi-tenant system, `tenant_id` keeps a tenant's joins local; for a social app, `user_id`. Check cardinality and skew: a few giant keys mean hot shards."),
                   ("Choose the routing scheme.", "Hash for even spread; ranges for range scans (but hot ranges); a directory or many logical shards mapped to machines for flexible rebalancing; consistent hashing so adding machines moves about 1/N."),
                   ("Handle what breaks.", "Queries without the key: maintain a secondary index or search service, or accept scatter-gather for rare queries. Cross-shard transactions: avoid by design, or use sagas and idempotency. Global unique ids: Snowflake-style ids. Aggregates: pre-compute."),
                   ("Operations.", "Resharding as a background copy with dual writes or a cut-over, schema changes across all shards, backups per shard, monitoring per shard (hot shard alerts), and replicas for each shard."),
                   ("Fallback for giants.", "A very large tenant gets its own shard.")],
            answer=["\"I would first make sure sharding is necessary: indexes, caching, replicas and partitioning are cheaper, and sharding adds permanent complexity. If one primary still cannot take the writes or hold the data, I would choose the shard key from the queries: it must appear in the hot ones, have many distinct values and spread load. For a multi-tenant product that is usually the tenant id, with big tenants given their own shard to avoid hot spots.",
                    "I would route by hash into many logical shards mapped onto machines, or use consistent hashing, so adding machines moves only about a fraction of the data. Then the costs: queries without the key need a secondary index or scatter-gather, cross-shard transactions should be avoided by design or handled with sagas and idempotency, ids need to be globally unique, and resharding is a background copy with a careful cut-over. Each shard gets its own replicas, backups and monitoring.\""],
            follow=[("What is a directory-based shard mapping?", "A lookup table from key (or key range) to shard that you can change, giving flexibility at the cost of an extra component to keep consistent and fast."),
                    ("How do you do a cross-shard transaction?", "Avoid it by choosing the key so related data is together; otherwise two-phase commit (blocking, rarely used at scale) or a saga with compensations and idempotent steps."),
                    ("How would you migrate from one database to a sharded one live?", "Dual write or change data capture into the shards, backfill, verify counts and checksums, read from shards for a small percentage, then switch writes, keeping the ability to roll back.")],
            slips=["Sharding before using indexes, caches and replicas.", "Choosing a key that no query uses.", "Ignoring cross-shard queries and transactions."],
        ),
        quick=[
            ("What does a shard key decide?", "Which shard a row lives on, and therefore which queries are cheap (those with the key)."),
            ("Why is `hash mod N` bad for adding shards?", "Changing N remaps most keys, so most data moves; consistent hashing moves about 1/N."),
            ("What is a hot shard?", "A shard that receives a disproportionate share of traffic or data, often because of a skewed key like a giant tenant."),
        ],
        traps=[
            "Sharding early: you pay the complexity forever and may choose the wrong key.",
            "A shard key that is low-cardinality or skewed.",
            "Assuming cross-shard queries and joins will \"just work\".",
        ],
    ),
    dict(
        title="NoSQL: key-value, document and log-structured stores",
        tier="hot",
        situation="Someone says \"just use MongoDB\" or \"use Cassandra, it scales\". What do these systems actually change, what do they give up, and which of their ideas could you run in a relational database anyway?",
        learn=["The four families and what each is for", "Key-value: speed and simplicity, and what it cannot query", "Documents: flexible shapes, and indexing inside them", "How a log-structured (LSM) store makes writes fast"],
        model=[
            "\"NoSQL\" is a label for several different designs: **key-value** (Redis, DynamoDB: get and put by key, very fast, no queries by value), **document** (MongoDB, or `jsonb` in PostgreSQL: self-contained JSON documents with flexible shapes and indexes on fields), **wide-column** (Cassandra, HBase: rows grouped by a partition key, sorted within it, built for huge write rates) and **graph** (relationships as first-class data). What they usually trade away: joins, multi-row transactions and ad hoc queries. What they buy: simple horizontal scaling by key, flexible schemas and (often) very high write throughput.",
            "Many scale-out stores use a **log-structured merge tree (LSM)**: writes go to an in-memory sorted table (plus a log for safety) and are flushed to **immutable sorted files**; reads check memory then the files from newest to oldest; **compaction** merges files in the background. Writes are sequential and cheap; reads may touch several files, and compaction costs disk and CPU (write amplification). A relational B-tree updates pages in place instead. Neither is better: LSM favours write-heavy loads, B-trees favour read-heavy ones and range queries with in-place updates.",
        ],
        analogy="A relational database is a well-organised filing cabinet with cross-references. A key-value store is a coat check: ticket in, coat out, nothing else. A document store is a folder per case with whatever papers belong in it. An LSM store is a stack of dated notebooks: you always append to the newest one and periodically merge old notebooks.",
        visual=[LSM_VIZ],
        sim=None,
        walk=[
            ("Start from the access pattern", "Get by key? Flexible nested records? Huge ingest of time-ordered events? Relationships?"),
            ("Key-value for lookups by id", "Sessions, caches, counters, carts: one key, one value, microsecond reads."),
            ("Documents for variable records", "Product catalogues and profiles where each record has a different shape and is read as a whole."),
            ("LSM for write-heavy streams", "Messages, metrics and events: append fast, read by partition key and time."),
            ("Check what you lose", "Joins, constraints, transactions across records, ad hoc queries: where do they go in your design?"),
        ],
        groups=[
            dict(title="Key-value, documents and an LSM tree you can read", cmds=[
                dict(volatile=True, c=r'''redis-server --port 6393 --save "" --appendonly no --daemonize yes --dir $HOME >/dev/null; sleep 0.5
R="redis-cli -p 6393"
$R hset cart:42 item:7 2 item:9 1 >/dev/null; $R expire cart:42 3600 >/dev/null
echo "--- get the cart by its key (the only fast question):"; $R hgetall cart:42 | paste -sd' '
echo "--- ttl is built in: $($R ttl cart:42) seconds"
echo "--- 'find every cart that contains item:9' has no index, so it means scanning every key:"
for i in 1 2 3; do $R hset cart:$((100+i)) item:9 1 >/dev/null; done
$R --scan --pattern 'cart:*' | while read k; do [ "$($R hexists $k item:9)" = 1 ] && echo $k; done | sort | paste -sd' '
$R shutdown nosave >/dev/null 2>&1; true''',
                     e="The key-value bargain. Fetching a cart **by its key** is instant, and expiry is built in. But a question about the **value** (\"which carts contain item 9?\") has no answer except scanning every key, because there is no index on contents. If you need that query you must maintain your own index (for example a set per item) or choose a different store. This is the pattern in every NoSQL decision: very fast on the access pattern you designed for, hard on the ones you did not.",
                     annot=[("item:7 2 item:9 1", "the whole cart came back from one lookup"),
                            ("ttl is built in: ~3600 seconds", "expiry is a first-class feature"),
                            ("cart:101 cart:102 cart:103 cart:42", "the value query required scanning all keys and checking each: no secondary index")]),
                dict(volatile=True, c=r'''. ~/rep/rig.sh; priup
pq <<'EOF'
create table docs(d jsonb);
insert into docs select jsonb_build_object('id', g, 'city', (array['Pune','Berlin','Austin','Osaka','Lima'])[1 + g % 5], 'tags', jsonb_build_array('t' || (g % 7)))
  || case when g % 3 = 0 then jsonb_build_object('premium', true, 'plan', jsonb_build_object('tier', 'gold', 'seats', g % 10)) else '{}'::jsonb end
  from generate_series(1, 100000) g;
analyze docs;
EOF
echo "--- documents of different shapes live in one collection:"
pq -At -c "select d from docs where (d->>'id')::int in (3, 4) order by (d->>'id')::int"
echo "--- find by a field, no index:"
pq -At -c "explain (analyze, costs off, timing off, summary off) select count(*) from docs where d @> '{\"city\":\"Pune\"}'" | grep -E "Scan"
pq -c "create index docs_gin on docs using gin (d jsonb_path_ops)"
echo "--- the same query with a GIN index:"
pq -At -c "explain (analyze, costs off, timing off, summary off) select count(*) from docs where d @> '{\"city\":\"Pune\"}'" | grep -E "Scan"
pg_ctl -D $R/primary -m fast stop >/dev/null''',
                     e="The document model, inside a relational database. Documents of different shapes (some have a `premium` flag and a nested `plan`, others do not) sit in the same table with no schema change. A query on a field without an index scans all 100,000 documents; a **GIN index** on the document lets the same query use an index. This is what makes `jsonb` a good first step before adopting a separate document database: you keep joins, transactions and SQL, and gain flexible shapes.",
                     annot=[("{\"id\": 3, \"city\": ..., \"plan\": {...}, \"premium\": true}", "this document has extra and nested fields"),
                            ("{\"id\": 4, \"city\": ..., \"tags\": [...]}", "this one does not: the shape differs per document"),
                            ("Seq Scan on docs (no index)", "every one of the 100,000 documents is read and tested"),
                            ("Bitmap Index Scan on docs_gin", "the GIN index answers containment queries on any field")]),
                dict(c=r'''python3 - <<'EOF'
# A toy LSM tree: memtable + immutable sorted runs + compaction. Real stores do exactly this, with files and a log.
class LSM:
    def __init__(self, limit=4):
        self.mem, self.runs, self.limit, self.flushes = {}, [], limit, 0
    def put(self, k, v):
        self.mem[k] = v                                      # a write only touches memory (plus a log in real life)
        if len(self.mem) >= self.limit:
            self.runs.insert(0, dict(sorted(self.mem.items())))   # flush: a new immutable sorted run, newest first
            self.mem, self.flushes = {}, self.flushes + 1
    def get(self, k):
        if k in self.mem: return self.mem[k], 0
        for n, run in enumerate(self.runs, 1):               # newest to oldest
            if k in run: return run[k], n
        return None, len(self.runs)
    def compact(self):
        merged = {}
        for run in reversed(self.runs): merged.update(run)   # newer values win; old versions disappear
        self.runs = [dict(sorted(merged.items()))]
db = LSM()
for i in range(20): db.put('key%02d' % (i % 10), 'v%d' % i)  # 20 writes over 10 keys: every key is written twice
print('after 20 writes: %d runs on disk, %d keys in memory' % (len(db.runs), len(db.mem)))
print('read key00 (oldest data): value %s after checking %d place(s)' % db.get('key00'))
print('read key09 (newest data): value %s after checking %d place(s)' % db.get('key09'))
db.compact()
print('after compaction: %d run(s); read key00: value %s after checking %d place(s)' % ((len(db.runs),) + db.get('key00')))
EOF''',
                     e="An LSM tree you can read end to end (about 20 lines of Python). Writes only touch memory until the memtable is full, then it is flushed as a new immutable sorted run: fast and sequential. Reads must look in memory and then in every run from newest to oldest, so **old data can cost several lookups** (read amplification). Compaction merges the runs, keeps the newest value of each key and discards the old versions, so afterwards a read checks one place. Real systems add a write-ahead log, Bloom filters (to skip runs that cannot contain the key) and levelled compaction, but this is the mechanism.",
                     annot=[("after 20 writes: 5 runs on disk, 0 keys in memory", "each full memtable became a sorted run: writes never modified an existing file"),
                            ("read key00 ... after checking N places", "an older key sits in an older run: several runs are consulted"),
                            ("after compaction: 1 run ... checking 1 place", "merged: one lookup, and obsolete values are gone")]),
            ]),
        ],
        scenario=dict(
            title="\"When would you choose a NoSQL database over PostgreSQL? Give me a concrete case.\"",
            ask="A favourite opinion question. A good answer avoids tribal claims and reasons from access patterns, scale and consistency needs.",
            clarify=[("What are the access patterns and the scale? What consistency does the data need?", "These decide everything: money needs transactions, a feed timeline needs cheap writes.")],
            think=[("Start with the default.", "A relational database is the right default: flexible queries, transactions, constraints, mature tooling. Most systems never outgrow a well-tuned primary with replicas and a cache."),
                   ("Name the real reasons to leave.", "A write rate or data size beyond one machine with a natural partition key; a simple access pattern (by key) at huge scale; very flexible or deeply nested records; multi-region active-active writes; a specialised model (graph, time series, search)."),
                   ("Give a concrete example.", "Chat messages: billions per day, always read by conversation and time: a wide-column store partitioned by conversation id with time-sorted rows (an LSM design) fits. Sessions and carts: key-value with TTL. Product catalogue with variable attributes: documents. Orders and payments: relational."),
                   ("State the costs.", "Give up joins and multi-record transactions, design tables per query, handle consistency and denormalisation in the application, and operate a new system."),
                   ("Hybrid is normal.", "Orders in PostgreSQL, sessions in Redis, messages in Cassandra, search in an index, with events keeping them in sync.")],
            answer=["\"My default is a relational database: it gives flexible queries, transactions and constraints, and a tuned primary with replicas and a cache carries most systems a long way. I would choose NoSQL for a specific reason: a write rate or data size beyond one machine with a natural partition key, a simple access pattern at huge scale, very variable records, or a specialised model such as graph or time series.",
                    "For example chat messages: billions a day, always read by conversation in time order, so a wide-column store partitioned by conversation id with time-sorted rows fits, and its log-structured design makes the writes cheap. Sessions and carts suit a key-value store with expiry. But I would keep orders and payments relational, because they need transactions. The cost of NoSQL is losing joins and multi-record transactions and designing storage around each query, so most real systems are hybrids.\""],
            follow=[("Why are writes fast in an LSM store?", "They append to memory and a log, then flush sorted files sequentially, never updating in place; compaction is deferred to the background."),
                    ("What is a Bloom filter doing in an LSM store?", "It tells quickly that a run definitely does not contain a key, so most runs are skipped on reads."),
                    ("Is `jsonb` in PostgreSQL a replacement for a document database?", "For moderate scale, often yes: flexible shapes with indexes and transactions. At very large scale or with built-in sharding needs, a dedicated store may be better.")],
            slips=["Choosing NoSQL because \"it scales\" without naming the access pattern.", "Ignoring the loss of transactions and joins.", "Forgetting that mixing stores is normal."],
        ),
        quick=[
            ("What is the main limit of a key-value store?", "It can only look things up by key; there are no efficient queries by value without your own index."),
            ("Why are LSM writes fast?", "Writes are sequential appends to memory and immutable files; no in-place updates."),
            ("What does compaction do?", "Merges sorted files, keeps the newest value per key and discards old versions."),
        ],
        traps=[
            "Picking NoSQL for \"scale\" at a size one PostgreSQL would handle.",
            "Modelling data without knowing the queries: in NoSQL the queries come first.",
            "Forgetting compaction and tombstone costs when sizing an LSM store.",
        ],
    ),
    dict(
        title="Choosing a data store and sizing it: the decision you defend in an interview",
        tier="hot",
        situation="Every design interview has the moment: \"what database would you use, and how many machines?\" This lesson turns the previous ones into a repeatable way to decide and to size.",
        learn=["A decision table from data shape to store", "Back-of-envelope sizing of storage and nodes", "Consistency choices and what you tell the interviewer", "Combining stores in one design"],
        model=[
            "Decide from **four questions**: (1) What are the **access patterns** (by key, by range, by search, by relationship, analytical)? (2) What **consistency and transactions** does the data need (money, inventory: strong; feeds, counters: eventual is fine)? (3) What is the **scale** (data size, writes per second, reads per second, growth)? (4) What are the **availability and latency** needs (regions, failover)? Default to a relational database unless an answer clearly rules it out, and say why.",
            "Then **size it**: data size = records x record size x replication factor x growth (plus index overhead, often 30 to 100 percent); write capacity = peak writes per second divided by what one node sustains (often a few thousand simple writes per second per node for a relational primary, tens of thousands for an LSM store); read capacity = replicas and caches. The number of shards is the larger of what size and write rate require, plus headroom (target 50 to 60 percent utilisation) and the replication factor on top. The goal is not a precise figure but a defensible one and a clear statement of which assumption dominates.",
        ],
        analogy="Choosing a vehicle: a car for most trips (relational), a freight truck for huge simple loads (wide-column), a courier bike for tiny instant lookups (key-value). You decide from the load, the distance and the road, then count how many you need and add spares.",
        sim=None,
        walk=[
            ("Write down the access patterns", "List the five most important queries and writes with their rates."),
            ("Mark the consistency needs", "Which data must be exact (balances, stock) and which can lag (counts, feeds)."),
            ("Estimate size and rates", "Records x bytes x replicas x growth; peak writes and reads per second."),
            ("Pick the store per data set", "Relational by default; another store only for a named reason."),
            ("Add nodes, replicas and headroom", "Shards from size and writes, replicas from reads and availability, 50 to 60 percent target utilisation."),
        ],
        groups=[
            dict(title="A sizing calculator you can reuse", cmds=[
                dict(c=r'''python3 - <<'EOF'
# Back-of-envelope sizing: how many database nodes does this workload need?
import math
def plan(name, records, bytes_each, growth_years, write_qps, read_qps, node_disk_gb, node_write_qps, node_read_qps, replicas=3):
    raw_gb = records * bytes_each / 1e9
    stored_gb = raw_gb * 1.5 * (1 + growth_years)             # 50% for indexes and overhead, plus growth
    shards_size = math.ceil(stored_gb / (node_disk_gb * 0.6))   # keep disks at 60%
    shards_write = math.ceil(write_qps / (node_write_qps * 0.6))
    shards = max(shards_size, shards_write)
    reads_per_shard = read_qps / shards
    replicas_for_reads = max(1, math.ceil(reads_per_shard / (node_read_qps * 0.6)))
    print('%s' % name)
    print('  data now %.0f GB, planned %.0f GB (indexes + %d years growth)' % (raw_gb, stored_gb, growth_years))
    print('  shards needed: %d by size, %d by writes -> %d shards' % (shards_size, shards_write, shards))
    print('  copies per shard: %d (the larger of %d for availability and %d for reads)' % (max(replicas, replicas_for_reads), replicas, replicas_for_reads))
    print('  total nodes: %d' % (shards * max(replicas, replicas_for_reads)))
plan('Orders: 200M orders of 1 KB, 300 writes/s, 6000 reads/s, relational nodes (2 TB disk, 3000 w/s, 20000 r/s)',
     200e6, 1000, 2, 300, 6000, 2000, 3000, 20000)
plan('Chat messages: 30B messages of 300 B, 120000 writes/s, 150000 reads/s, LSM nodes (4 TB disk, 30000 w/s, 30000 r/s)',
     30e9, 300, 2, 120000, 150000, 4000, 30000, 30000)
EOF''',
                     e="The same arithmetic with two very different workloads. **Orders** are modest: the data fits comfortably on one node, writes are far below one node's limit, so one primary plus replicas is enough, and the reasoning is about availability rather than scale. **Chat messages** are enormous in both size and write rate, so the data and write throughput each require many nodes, which is exactly where a partitioned LSM-style store earns its place. The numbers are assumptions and should be stated as such; what matters is that the decision follows the numbers, not fashion.",
                     annot=[("Orders: shards needed: 1 by size, 1 by writes -> 1 shards", "one primary node is enough for size and writes: no sharding"),
                            ("Orders: total nodes: 3", "three copies for availability: the reasoning is about survival, not scale"),
                            ("Chat: shards needed: 17 by size, 7 by writes -> 17 shards", "the data size (about 40 TB planned) dominates; writes alone would need 7"),
                            ("Chat: total nodes: 51", "17 shards x 3 copies: the replication factor multiplies the hardware")]),
            ]),
        ],
        playbook=dict(title="From data shape to store", intro=["A decision table to check your instinct, not replace your thinking."], rows=[
            ["Money, orders, inventory, anything needing transactions", "Relational (PostgreSQL, MySQL)", "ACID, constraints, joins; scales far with indexes, replicas, cache, then sharding", "Default choice"],
            ["Sessions, carts, caches, counters, rate limits", "Key-value (Redis, DynamoDB)", "Lookup by key, TTL, atomic counters; no queries by value", "Persistence settings matter"],
            ["Catalogues and profiles with variable shape", "Document (MongoDB, jsonb)", "Flexible nested records read as a whole; indexes on fields", "Consider jsonb first"],
            ["Messages, events, metrics, huge ingest by key and time", "Wide-column / LSM (Cassandra, HBase, Bigtable)", "Very high write rate, partitioned by key, time-sorted rows", "Design tables per query; eventual consistency"],
            ["Relationships and traversals (friends of friends)", "Graph (Neo4j, or relational with care)", "Queries follow edges", "Check scale needs honestly"],
            ["Full-text and ranked search", "Search index (Elasticsearch, OpenSearch)", "Inverted index, relevance", "A secondary index, not the system of record"],
            ["Analytics over huge data", "Column store / warehouse (BigQuery, ClickHouse, Redshift)", "Scans of few columns over many rows", "Fed from the primary by pipelines"],
        ]),
        scenario=dict(
            title="\"Design the storage for a chat application with 500 million users. What databases and how many machines?\"",
            ask="The decision-and-sizing question. They want separate stores per data type with reasons, numbers, and a consistency story.",
            clarify=[("How many messages per day, how long are they kept, and what are the read patterns?", "Say it explicitly: for example 40 billion messages a day, retained for years, read as recent history of one conversation.")],
            think=[("Split the data by access pattern.", "Messages: append-heavy, read by conversation in time order. User accounts and relationships: moderate, relational. Presence and typing: ephemeral key-value. Media: blob storage, with only metadata in a database. Search: a separate index."),
                   ("Choose stores.", "Messages: wide-column/LSM store partitioned by conversation id (partition key) with time-ordered rows, so the latest N messages of a chat is one partition read. Accounts: relational with replicas. Presence: Redis. Media: object storage and a CDN."),
                   ("Size the messages.", "40 billion per day is about 460,000 writes per second on average, perhaps 1 million at peak; at 300 bytes that is 12 TB per day, and with 3 replicas and retention of years, petabytes. Nodes: peak writes over about 30,000 per node gives roughly 40 nodes for writes; the data volume dominates and needs thousands of nodes with tiered storage and retention policies."),
                   ("Consistency and ordering.", "Within a conversation, messages must be ordered: assign ids per conversation (or time-based ids) and sort by them; eventual consistency across replicas is acceptable, but a user must see their own message immediately (read your writes)."),
                   ("Failure and hot spots.", "Replication across zones with quorum writes; a hot group chat becomes a hot partition: cap fan-out, split very large conversations into time buckets."),
                   ("Say the assumptions.", "State the assumptions and how the design changes if they are wrong.")],
            answer=["\"I would split by access pattern. Messages are append-heavy and read as the latest page of one conversation, so a wide-column LSM store partitioned by conversation id with time-ordered rows fits: the common read is one partition. Accounts and relationships go in a relational database with replicas, presence in Redis with expiry, media in object storage with a CDN, and search in a separate index fed from events.",
                    "For size: say 40 billion messages a day is about half a million writes a second on average and several hundred terabytes a day of raw data with replication, so message storage is a large partitioned cluster with retention and tiering, while the relational part is small. Ordering is per conversation using time-based ids, replication across zones with quorum writes, and the user always reads their own message. A very hot group conversation becomes a hot partition, so I would bucket by time and limit fan-out. I would state these numbers as assumptions and show how the design changes if they are off.\""],
            follow=[("Why not PostgreSQL for the messages?", "At this write rate and size one primary is far beyond its limits; sharding PostgreSQL yourself is possible but a store built for partitioned append-heavy data does it natively."),
                    ("How do you paginate message history?", "Keyset by message id or time within the conversation partition: `where conv = ? and id < last_seen order by id desc limit 50`."),
                    ("How do you delete data for compliance?", "Design deletion in: time-bucketed partitions expire cheaply; per-user deletion needs a mapping and tombstones, and compaction eventually removes the data.")],
            slips=["Naming one database for everything.", "Giving no numbers, or numbers with no assumptions stated.", "Forgetting ordering and read-your-writes."],
        ),
        quick=[
            ("Which store do you default to and why?", "Relational: transactions, constraints, flexible queries; it scales far with indexes, replicas and caches."),
            ("What drives the number of shards?", "The larger of data size and write rate requirements, with headroom, multiplied by replicas."),
            ("Why might a design use several stores?", "Different data has different access patterns and consistency needs; one store rarely suits all."),
        ],
        traps=[
            "Quoting a database name without saying why.",
            "Sizing without replication, indexes and growth: the real footprint is two to five times the raw data.",
            "Running disks and nodes at 90 percent: no headroom for failures and rebalancing.",
        ],
    ),
]
