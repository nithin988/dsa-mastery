"""S18 relational databases: part B (lessons 4 to 6)."""
import sysviz as v

WAL_SEQ = v.seq(
    ["Client", "PostgreSQL", "WAL (log)", "Data files"],
    [("a->b", 0, 1, "UPDATE ...; COMMIT"),
     ("a->b", 1, 2, "append the change to the log"),
     ("a->b", 1, 2, "flush the log to disk (fsync)"),
     ("a->b", 1, 0, "COMMIT acknowledged: durable", "reply"),
     ("note", 0, 3, "the data pages are written to the data files later, in the background"),
     ("a->b", 2, 3, "after a crash: replay the log onto the data files", "bad")],
    "Write-ahead logging", "The commit is safe once the log is on disk; the data files can catch up later")

REPL_VIZ = v.figure(
    720, 214,
    [v.box(10, 70, 100, 56, "App servers", "ink"),
     v.arrow(110, 98, 150, 98), v.box(150, 70, 110, 56, "Pooler", "warn", "reuses connections"),
     v.arrow(260, 90, 310, 60), v.arrow(260, 106, 310, 138),
     v.box(310, 30, 170, 56, "Primary", "ok", "all writes, some reads"),
     v.box(310, 110, 170, 56, "Read replica", "acc", "reads only, may lag"),
     v.arrow(395, 86, 395, 110),
     v.text(560, 62, "writes go to the primary", "dg-s"), v.text(560, 142, "reads can spread to replicas", "dg-s"),
     v.text(360, 198, "The next module shows replication, sharding and when to leave a single database.", "dg-s")],
    "Where a single database ends", "A pooler protects the database; replicas add read capacity; sharding splits the data")

LESSONS_B = [
    dict(
        title="Under the hood: MVCC, the write-ahead log and vacuum",
        tier="core",
        situation="You update one row and PostgreSQL's table gets bigger. You kill the database mid-write and your committed data is still there. A long-running report blocks nobody, yet disk usage creeps up. These are the same two mechanisms at work.",
        learn=["MVCC: readers and writers that do not block each other", "Dead rows, bloat and VACUUM", "The write-ahead log and crash recovery", "What fsync and replication have to do with durability"],
        model=[
            "PostgreSQL uses **MVCC** (multi-version concurrency control): an `UPDATE` does not overwrite a row, it writes a **new version** and marks the old one as deleted by this transaction. Each transaction sees the versions that were visible when its snapshot was taken, so **readers do not block writers and writers do not block readers**. The cost: old versions (**dead tuples**) stay in the table until **VACUUM** removes them. A table with heavy updates and no timely vacuum **bloats**: it grows and scans slow down. The most common cause of bloat is a long-running transaction that keeps old versions visible.",
            "**Durability** comes from the **write-ahead log (WAL)**: before a change reaches the data files, a record of it is appended to the log, and at `COMMIT` the log is flushed to disk. If the server crashes, PostgreSQL replays the log on startup (**crash recovery**) and the committed data is back. Replicas work the same way: they receive the stream of WAL records and replay it, which is why a replica may lag the primary. `fsync` is what forces the log to physical disk; turning it off is fast and unsafe against power loss.",
        ],
        analogy="A ledger written in ink: nothing is erased, a correction is a new line and the old line is struck through. Readers consult the ledger as of a date; a clerk periodically copies it to a clean book without the struck lines (vacuum). The ledger is written before the summaries, so the summaries can always be rebuilt.",
        visual=[WAL_SEQ],
        sim=None,
        walk=[
            ("An update writes a new row version", "The old version is still there, marked with the id of the transaction that replaced it."),
            ("Readers keep seeing what they should", "A transaction that started earlier still sees the old version; new transactions see the new one: no blocking."),
            ("Dead versions accumulate", "When no running transaction can see an old version any more, it is garbage, but space is only reused after vacuum."),
            ("VACUUM reclaims space for reuse", "Autovacuum runs in the background; `VACUUM` marks dead space reusable (the file does not usually shrink)."),
            ("The WAL makes commits durable", "The log is flushed at commit; data files are written lazily; recovery replays the log."),
        ],
        groups=[
            dict(title="Watch row versions, bloat and vacuum", cmds=[
                dict(volatile=True, c=r'''. ~/pg/rig.sh; pgup
q -c "create table v(id int primary key, n int); insert into v values (1, 0)"
echo "--- the row's physical location (ctid) and creating transaction (xmin):"
q -At -c "select 'ctid=' || ctid || ' xmin=' || xmin || ' n=' || n from v"
q -c "update v set n = 1 where id = 1"
echo "--- after one UPDATE: a different physical row (a new version was written):"
q -At -c "select 'ctid=' || ctid || ' xmin=' || xmin || ' n=' || n from v"
echo "--- dead versions left behind:"
q -At -c "select 'dead tuples: ' || n_dead_tup from pg_stat_user_tables where relname = 'v'"
pgdown''',
                     e="MVCC made visible. `ctid` is the physical position of the row and `xmin` the transaction that created it. After a single `UPDATE` the **same logical row lives at a different ctid with a different xmin**: PostgreSQL wrote a new version and left the old one in place as a dead tuple (the statistics collector reports it a moment later, so the dead count may show 0 or 1 right after).",
                     annot=[("ctid=(0,1) xmin=N n=0", "the first version: page 0, slot 1"),
                            ("ctid=(0,2) xmin=N+1 n=1", "after the update: a new physical row (slot 2) written by a new transaction"),
                            ("dead tuples: 1", "the old version is still in the table until vacuum (the counter updates asynchronously)")]),
                dict(volatile=True, c=r'''. ~/pg/rig.sh; pgup
q -c "create table bloat(id int primary key, pad text); insert into bloat select g, repeat('x', 100) from generate_series(1, 100000) g"
size() { q -At -c "select pg_size_pretty(pg_table_size('bloat'))"; }
echo "size after loading:        $(size)"
q -c "update bloat set pad = repeat('y', 100)"
echo "size after updating every row once:  $(size)   (old versions kept)"
q -c "update bloat set pad = repeat('z', 100)"
echo "size after a second update: $(size)"
q -c "vacuum bloat"
q -c "update bloat set pad = repeat('w', 100)"
echo "size after VACUUM and a third update: $(size)   (dead space reused)"
q -c "vacuum full bloat"
echo "size after VACUUM FULL:      $(size)   (table rewritten compactly; takes an exclusive lock)"
pgdown''',
                     e="Bloat, measured. Every full-table update writes a new version of every row, so the table roughly doubles after the first update and grows again after the second. After a plain `VACUUM` the dead space becomes reusable, so a third update does **not** grow the file. `VACUUM FULL` rewrites the table to its minimal size but needs an exclusive lock, so it is a maintenance-window tool. The practical lesson: keep autovacuum healthy and avoid long transactions that stop it from cleaning.",
                     annot=[("size after loading: 14 MB", "the starting size for 100,000 rows"),
                            ("after updating every row once: 27 MB", "the old versions are still there next to the new ones"),
                            ("after a second update: 40 MB", "bloat keeps growing without vacuum"),
                            ("after VACUUM and a third update: 40 MB (no growth)", "dead space was reused: vacuum did its job without shrinking the file"),
                            ("after VACUUM FULL: 13 MB", "rewritten compactly; the lock made it a maintenance operation")]),
            ]),
            dict(title="Crash recovery with the write-ahead log", cmds=[
                dict(volatile=True, c=r'''. ~/pg/rig.sh; pgup
q -c "create table survive(n int); insert into survive select generate_series(1, 1000)"
echo "committed rows before the crash: $(q -At -c 'select count(*) from survive')"
echo "WAL position:  $(q -At -c 'select pg_current_wal_lsn()')"
q -c "insert into survive select generate_series(1, 5000)"
echo "WAL position after 5000 more rows: $(q -At -c 'select pg_current_wal_lsn()')  (the log grew)"
echo "--- kill -9 the server (no clean shutdown):"
kill -9 $(head -1 $P/data/postmaster.pid); sleep 1
pgup
echo "--- server log from the restart:"
grep -E "not properly shut down|automatic recovery|redo done|ready to accept" $P/log | tail -4 | cut -c1-110
echo "rows after the restart: $(q -At -c 'select count(*) from survive')"
pgdown''',
                     e="Durability, tested by violence. After rows are committed the server process is killed with `kill -9`: no chance to shut down cleanly. On restart PostgreSQL finds the data files behind the log, **replays the write-ahead log**, and reports that it was not properly shut down and recovered automatically. All 6,000 committed rows are there. (We turned `fsync` off for speed, which is safe against a killed process because the operating system still holds the written data; it would not be safe against power loss, which is why production keeps `fsync` on.)",
                     annot=[("pg_ctl: another server might be running; trying to start server anyway", "pg_ctl saw the stale pid file left by the killed server and started anyway: expected after kill -9"),
                            ("committed rows before the crash: 1000", "the starting data"),
                            ("WAL position grows after the insert", "each change was appended to the log"),
                            ("database system was not properly shut down; automatic recovery in progress", "PostgreSQL noticed the unclean stop and replayed its log"),
                            ("rows after the restart: 6000", "every committed row survived the crash")]),
            ]),
        ],
        scenario=dict(
            title="\"What happens inside PostgreSQL when I update a row and commit? What if the server crashes right after the commit?\"",
            ask="They are testing whether you understand durability beyond the word, and whether you know why databases need maintenance.",
            clarify=[("Is it okay to describe PostgreSQL specifically?", "Yes: the ideas (log first, snapshots) are shared by most systems; mention where they differ.")],
            think=[("Walk the write path.", "The transaction finds the row, writes a new row version (MVCC), appends a log record to the WAL buffer, and at commit flushes the WAL to disk. Only then is the client told the commit succeeded. Data pages stay in memory and are written later by a background process (checkpointing)."),
                   ("Answer the crash question.", "Data files may be stale, but the log has the commit. On restart PostgreSQL replays the log from the last checkpoint, so the committed update is present; uncommitted changes are discarded."),
                   ("Mention what makes it real.", "The guarantee depends on `fsync` being honest all the way down (disk caches, battery-backed controllers, cloud disks) and on `synchronous_commit`."),
                   ("Connect to replication.", "Replicas stream the same WAL. Synchronous replication waits for a replica to confirm before acknowledging commit: durable against losing the primary at the cost of latency; asynchronous is faster but can lose the last commits on failover."),
                   ("Mention the maintenance cost of MVCC.", "Old versions need vacuum; long transactions block cleanup and cause bloat, so monitor transaction age and autovacuum.")],
            answer=["\"The update creates a new version of the row, since PostgreSQL never overwrites in place, and appends a record to the write-ahead log. At commit the log is flushed to disk and only then is the client told it succeeded; the data pages themselves are written later in the background. If the server crashes right after the commit, the data files may be behind but the log has the change, so on restart PostgreSQL replays the log and the committed update is there, while uncommitted work is discarded.",
                    "That durability depends on fsync being honest through the whole storage stack. Replicas work by streaming and replaying the same log; synchronous replication waits for a replica's confirmation before commit returns, so a failover cannot lose it, at the price of latency. The cost of keeping old versions is vacuum: dead rows must be cleaned, and long-running transactions prevent that, so I would monitor transaction age and bloat.\""],
            follow=[("What is a checkpoint?", "A point where all dirty data pages up to a log position are flushed to the data files, so recovery only has to replay the log after it."),
                    ("How can a replica be behind the primary?", "It replays the log asynchronously: network delay or heavy replay can make it lag, so reads from a replica may be stale (read-your-writes needs care)."),
                    ("What is the risk of `synchronous_commit = off`?", "A crash can lose the last few commits (up to a short window) but not corrupt the database: a latency-for-durability trade.")],
            slips=["Saying the data is written to the table first.", "Not mentioning that durability depends on the disk honouring flushes.", "Forgetting the maintenance cost of MVCC."],
        ),
        quick=[
            ("What does MVCC allow that locking readers would not?", "Readers and writers do not block each other: readers use a snapshot of older versions."),
            ("Why does a table grow after updates?", "Updates write new row versions; the old ones remain as dead tuples until vacuum."),
            ("What does recovery replay after a crash?", "The write-ahead log, bringing the data files up to date with every committed change."),
        ],
        traps=[
            "A transaction left open for hours: vacuum cannot clean anything newer than its snapshot, so bloat grows.",
            "Running `VACUUM FULL` on a busy table: it takes an exclusive lock.",
            "Assuming a commit is durable on any cloud disk without checking what the platform guarantees.",
        ],
    ),
    dict(
        title="Schema design in practice: normalisation, denormalisation and the N+1 trap",
        tier="hot",
        situation="You must design the tables for an online store, and interviewers ask: \"normalised or denormalised? why?\" Meanwhile the real-life problem is usually not the schema itself but how the application queries it: a page that runs 200 small queries instead of one.",
        learn=["Normalisation: one fact in one place", "When and how to denormalise deliberately", "Keys, constraints and data types worth getting right", "The N+1 query problem and pagination"],
        model=[
            "**Normalisation** means storing each fact **once**: a customer's name lives in the customers table, and orders point to it. This prevents **update anomalies** (change the name in one place, not 40,000 order rows) and keeps data consistent. The price is **joins** at read time. **Denormalisation** deliberately copies data to avoid joins (a `customer_name` column on orders, a precomputed `order_total`, a counter), trading consistency work (you must keep the copy right) for read speed. Normalise first; denormalise a specific, measured hot read, and decide who keeps the copy correct (a trigger, the application, or a periodic job).",
            "The most common application-level performance bug is **N+1 queries**: one query for a list, then one query per row for its details. With 100 rows that is 101 round trips; each is cheap in the database but expensive in network and connection overhead. Fix it with one **join** or a single `where id in (...)` query. For lists, use **keyset pagination** (`where id > :last order by id limit 20`) rather than `offset`, which re-reads all skipped rows. Choose types carefully: use `timestamptz` for times, `numeric` for money (never floating point), and a surrogate primary key plus a natural unique constraint where one exists.",
        ],
        analogy="A contact list where each person's company address is written once on the company's card and people point to it. Changing the address is one edit. A denormalised list writes the address on every person's card: faster to read one card, but now moving offices means editing hundreds of cards.",
        sim=None,
        walk=[
            ("List the entities and their facts", "Customers, products, orders, order items: one table each, with only the facts that belong to that entity."),
            ("Add keys and constraints", "Primary keys, foreign keys, `not null`, `unique`, `check`: let the database defend the rules."),
            ("Write the real queries", "The pages and reports the system must serve: do they need joins across five tables on a hot path?"),
            ("Measure, then denormalise a specific hot read", "Copy the one column or counter that removes the join, and choose how it is kept correct."),
            ("Avoid N+1 and deep offsets", "One query per page of results, not one per row; keyset pagination for long lists."),
        ],
        groups=[
            dict(title="N+1 measured, and pagination", cmds=[
                dict(volatile=True, c=r'''. ~/pg/rig.sh; pgup
echo "--- N+1: fetch 100 orders, then each order's customer with a separate query"
s=$(date +%s%N)
for id in $(q -At -c "select id from orders order by id limit 100"); do
  q -At -c "select c.name from customers c join orders o on o.customer_id = c.id where o.id = $id" >/dev/null
done
e=$(date +%s%N); echo "101 queries: $(( (e-s)/1000000 )) ms"
echo "--- one join instead"
s=$(date +%s%N)
q -At -c "select o.id, c.name from orders o join customers c on c.id = o.customer_id order by o.id limit 100" >/dev/null
e=$(date +%s%N); echo "1 query:     $(( (e-s)/1000000 )) ms"
pgdown''',
                     e="The N+1 problem, timed. Each separate query is trivial for PostgreSQL, but each also pays a connection and a round trip (here each `psql` call even opens a new connection, which exaggerates the cost; in an application with a connection pool the per-query overhead is smaller but the shape is the same). One join returns the same 100 rows in a single round trip. When you see a page that gets slower as the list grows, count the queries before you touch anything else.",
                     annot=[("101 queries: 706 ms", "one query for the list plus one per row"),
                            ("1 query: 7 ms", "the same data from a single join: about 100 times faster here")]),
                dict(volatile=True, c=r'''. ~/pg/rig.sh; pgup
echo "--- OFFSET pagination, deep page:"
q -At -c "explain (analyze, costs off, summary off, timing off) select id from orders order by id offset 400000 limit 20" | grep -E "Limit|Index|Seq|rows="
echo "--- keyset pagination, same place (id > 400000):"
q -At -c "explain (analyze, costs off, summary off, timing off) select id from orders where id > 400000 order by id limit 20" | grep -E "Limit|Index|Seq|rows="
pgdown''',
                     e="Why deep pages get slow. `offset 400000` makes the database walk **400,020 index entries** and discard 400,000 of them before returning 20 rows. Keyset pagination (`where id > last_seen`) jumps straight to the right place and reads only the 20 rows needed, so the 10th page and the 20,000th page cost the same. The trade-off: you can go next and previous easily but cannot jump to \"page 7,531\".",
                     annot=[("Limit ... actual rows=20 / Index Only Scan ... rows=400020", "with offset the scan underneath produced 400,020 rows to return 20"),
                            ("Index Scan ... actual rows=20 (keyset)", "the keyset version read exactly the rows it returned")]),
            ]),
        ],
        scenario=dict(
            title="\"Design the schema for an online store's orders. Normalised or denormalised?\"",
            ask="A schema design question that also tests whether you think about queries, integrity and growth.",
            clarify=[("What are the main reads and writes, and their rates?", "Browsing orders per customer is a read; placing an order is a write. Reads vastly outnumber writes in most stores."),
                     ("Do prices change, and must an old order keep the price it was bought at?", "Yes in nearly every real store: the order must store the price at purchase time, which is deliberate denormalisation.")],
            think=[("Start normalised.", "customers, products, orders, order_items (order_id, product_id, quantity, unit_price). Each fact once; foreign keys and constraints enforce the relationships."),
                   ("Identify what must be copied.", "`unit_price` and shipping address are copied into the order at purchase time: history must not change when the catalogue changes. That is correct denormalisation: a snapshot, not a duplicate to keep in sync."),
                   ("Add indexes from the queries.", "`orders(customer_id, created_at desc)` for \"my orders\"; `order_items(order_id)`; a unique constraint on any natural key."),
                   ("Denormalise measured hot reads only.", "If the orders list page needs the total and the item count, store `total_amount` on the order, written in the same transaction as the items, rather than summing every time."),
                   ("Plan for growth.", "Money as numeric or integer cents; timestamptz; soft deletes versus archiving; later partitioning orders by date or sharding by customer if one database is not enough.")],
            answer=["\"I would start normalised: customers, products, orders and order items, each fact stored once, with primary keys, foreign keys and constraints so the database defends integrity. Then I would deliberately copy what must not change: the unit price and the shipping address are stored on the order as a snapshot, because an old order must keep what the customer actually paid even if the catalogue changes.",
                    "I would add indexes for the real queries, for example orders by customer and date, and only denormalise measured hot reads, such as storing the order total in the same transaction that writes the items, so the list page does not aggregate every time. Money goes in as numeric or integer cents, times as timestamptz. If the table outgrows one machine I would partition by date or shard by customer, which is the next module.\""],
            follow=[("When is denormalisation a bad idea?", "When the copy must be kept in sync across many writers, or when the saved join is not measurably the bottleneck: you take on consistency work for no gain."),
                    ("How would you store money?", "As integer minor units (cents) or numeric with a fixed scale, never floating point; keep the currency alongside."),
                    ("How do you avoid N+1 in an ORM?", "Use eager loading or an explicit join, and log query counts per request in tests so a regression is caught.")],
            slips=["Denormalising up front without measuring.", "Using floats for money.", "Forgetting that old orders need a price snapshot."],
        ),
        quick=[
            ("What problem does normalisation prevent?", "Update anomalies: the same fact stored in many places can become inconsistent."),
            ("What is an N+1 query problem?", "One query for a list plus one per row for details: many round trips instead of one join."),
            ("Why is keyset pagination faster than offset for deep pages?", "It seeks straight to the position instead of reading and discarding all the skipped rows."),
        ],
        traps=[
            "Denormalising everything for speed, then spending years keeping copies in sync.",
            "Storing money as floating-point numbers.",
            "Counting on `offset` pagination for large tables.",
        ],
    ),
    dict(
        title="Connections, pooling, locks and finding what is wrong",
        tier="hot",
        situation="At peak the application starts failing with \"too many connections\", even though the database CPU is nearly idle. Another day everything hangs because one forgotten transaction holds a lock. Knowing how connections work, and how to ask the database what it is doing, resolves most of these in minutes.",
        learn=["Why a connection is expensive (a process each)", "Connection pooling and its limits", "pg_stat_activity: what is running right now", "Finding who blocks whom, and slow query settings"],
        model=[
            "In PostgreSQL every client connection is served by its **own operating system process**. A connection takes time to open (authentication, process start) and memory to keep, so a database can hold a few hundred connections comfortably, not tens of thousands. Applications that open a new connection per request waste time; applications with thousands of instances each holding a pool exhaust the server. The fix is a **connection pooler** (PgBouncer or a built-in pool): many application connections share a small number of real ones. Size the pool to what the database can actually run in parallel (roughly a few times the CPU cores), not to the number of requests.",
            "The database can describe itself: **`pg_stat_activity`** lists every connection, its state (`active`, `idle`, `idle in transaction`), the query and how long it has run. **`idle in transaction`** is dangerous: a transaction that is open but doing nothing holds locks and an old snapshot. **`pg_blocking_pids()`** shows who is blocking whom. Protect yourself with **`statement_timeout`** (kill runaway queries), **`lock_timeout`** and **`idle_in_transaction_session_timeout`**. Slow queries are found with `log_min_duration_statement` or the `pg_stat_statements` extension.",
        ],
        analogy="A restaurant kitchen has a limited number of cooks (CPU). Hiring a new cook for every customer who walks in is slow and wasteful; a host (the pooler) seats many customers and feeds orders to the few cooks. A customer who sits at the pass and does not leave (an idle transaction) blocks everyone behind them.",
        visual=[REPL_VIZ],
        sim=None,
        walk=[
            ("Each client gets a backend process", "Opening one costs milliseconds and memory; the server has a hard `max_connections` limit."),
            ("A pooler sits in between", "Applications connect to the pooler; it keeps a small set of real connections and hands them out per transaction."),
            ("Look at what is running", "`pg_stat_activity` shows state, duration and the query: the first place to look when something hangs."),
            ("Find the blocker", "`pg_blocking_pids(pid)` and `pg_locks` show which session holds the lock others wait for."),
            ("Put guard rails on", "Timeouts for statements, locks and idle transactions turn silent hangs into clear errors."),
        ],
        groups=[
            dict(title="Connections and the cost of opening them", cmds=[
                dict(volatile=True, c=r'''. ~/pg/rig.sh; pgup
echo "--- connection limits:"
q -At -c "show max_connections"
echo "--- open three idle connections and look at the server's processes:"
for i in 1 2 3; do ( q -c "select pg_sleep(2)" >/dev/null & ) ; done; sleep 0.5
ps -eo comm,args | grep "postgres: learner" | grep -v grep | cut -c1-70
echo "--- what the server says about them:"
q -c "select state, count(*) from pg_stat_activity where datname = 'shop' group by state order by state"
sleep 2; pgdown''',
                     e="The process-per-connection model, visible. Each client connection appears as its own `postgres: learner shop ...` process in `ps`, and `pg_stat_activity` counts them by state. `max_connections` (100 by default) is a hard ceiling: when 100 connections exist, the 101st is refused with `too many connections`, no matter how idle the CPU is.",
                     annot=[("100", "the default connection limit"),
                            ("postgres: learner shop [local] SELECT (three lines)", "one backend process per client connection; the command shown is what each is doing"),
                            ("active | 4", "three sleeping queries plus this one asking: all in state active")]),
                dict(volatile=True, c=r'''. ~/pg/rig.sh; pgup
echo "--- 50 separate connections, one query each:"
s=$(date +%s%N); for i in $(seq 1 50); do q -At -c "select 1" >/dev/null; done; e=$(date +%s%N)
echo "  $(( (e-s)/1000000 )) ms in total"
echo "--- 50 queries on one reused connection:"
s=$(date +%s%N); (for i in $(seq 1 50); do echo "select 1;"; done) | q -At >/dev/null; e=$(date +%s%N)
echo "  $(( (e-s)/1000000 )) ms in total"
pgdown''',
                     e="Why pools exist, measured. Fifty queries over fifty fresh connections spend most of their time starting `psql`, connecting and authenticating; fifty queries over one reused connection are much faster. The gap on your machine will differ, and a real application's connect cost also includes the network and TLS, which makes it worse. A pool pays the connection cost once and then reuses it.",
                     annot=[("50 separate connections: hundreds of ms", "each pays connect and authentication"),
                            ("50 queries on one connection: a few ms to tens of ms", "the same work with the connection cost paid once")]),
            ]),
            dict(title="Find the blocker and put guard rails on", cmds=[
                dict(volatile=True, c=r'''. ~/pg/rig.sh; pgup
q -c "create table cfg(k text primary key, v text); insert into cfg values ('mode','a')"
echo "--- a transaction that is opened and forgotten (idle in transaction):"
( q -c "begin; update cfg set v='b' where k='mode';" -c "select pg_sleep(4)" >/dev/null ) &
sleep 0.5
echo "--- another session tries to update the same row (it will wait):"
( q -c "update cfg set v='c' where k='mode'" >/dev/null ) &
sleep 1
q -c "select pid, state, wait_event_type as waiting_on, pg_blocking_pids(pid) as blocked_by, left(query, 40) as query from pg_stat_activity where datname='shop' and pid <> pg_backend_pid() order by pid"
echo "--- a guard rail: give up after 1 second instead of hanging:"
q -c "set lock_timeout = '1s'; update cfg set v='d' where k='mode'" 2>&1 | head -1
wait; pgdown''',
                     e="The first aid kit for a hang. `pg_stat_activity` lists two sessions: one **blocked** (`wait_event_type` is `Lock`, `blocked_by` shows the other session's process id) and the other the holder, which is `idle in transaction`/running a sleep with its row lock still held. The last command shows a guard rail: with `lock_timeout` the third session fails after a second with a clear error instead of waiting indefinitely.",
                     annot=[("wait_event_type Lock, blocked_by {83628}", "this session waits for a lock held by the listed process"),
                            ("holder: Timeout, blocked_by {} (running pg_sleep)", "the holder is sleeping inside an open transaction and keeps its row lock until it commits: in real life this is the forgotten `idle in transaction` session"),
                            ("ERROR: canceling statement due to lock timeout", "the guard rail turned a silent hang into a fast, visible error")]),
            ]),
        ],
        scenario=dict(
            title="\"Production is slow and the application reports too many connections. What do you do?\"",
            ask="An on-call style question. They want a calm, ordered diagnosis and a lasting fix, not a restart.",
            clarify=[("Is the database CPU high or idle? Are queries slow, or are connections piling up waiting?", "CPU idle with many connections suggests waiting on locks or on slow clients; CPU high suggests expensive queries.")],
            think=[("Look at what the database is doing.", "`select state, wait_event_type, count(*) from pg_stat_activity group by 1,2`: many `idle in transaction` points to application bugs holding transactions open; many waiting on `Lock` means a blocker; many `active` with high CPU means heavy queries."),
                   ("Find the blocker or the heavy queries.", "`pg_blocking_pids` for blockers; longest-running queries by `now() - query_start`; slow query log or pg_stat_statements for the worst offenders."),
                   ("Relieve the immediate pressure carefully.", "Cancel the blocking query or terminate its backend (`pg_cancel_backend`, `pg_terminate_backend`) rather than restarting everything; shed load at the pooler or application."),
                   ("Fix the cause.", "Add a pooler and size pools to the database's capacity; set `idle_in_transaction_session_timeout`, `statement_timeout`, `lock_timeout`; fix the code that holds transactions across slow calls; add the missing index."),
                   ("Prevent the next one.", "Alert on connection count, `idle in transaction` age, lock waits and replication lag; load test connection limits before a launch.")],
            answer=["\"I start by asking the database what it is doing: pg_stat_activity grouped by state and wait event. Many sessions idle in transaction usually means the application holds transactions open; many waiting on locks means a blocker that I find with pg_blocking_pids; many active sessions with high CPU means expensive queries, which I find by duration or in the slow query log.",
                    "To relieve pressure I cancel or terminate the specific blocking backend instead of restarting, and shed load at the pooler. To fix the cause I put a connection pooler in front, size it to what the database can run in parallel, set idle-in-transaction, statement and lock timeouts, and fix the code or index at fault. Then I alert on connection count, idle-in-transaction age and lock waits so the next one pages us before it becomes an outage.\""],
            follow=[("Why not just raise max_connections?", "Each connection is a process with memory and scheduling overhead; more connections often make throughput worse. Pool instead."),
                    ("What is the difference between session and transaction pooling?", "Session pooling holds a real connection for the whole client session; transaction pooling returns it after each transaction, supporting far more clients but not session features like prepared statements or advisory locks."),
                    ("What do you do when a replica lags?", "Check replay load and long queries on the replica, network, and primary write volume; route lag-sensitive reads to the primary; alert on lag in seconds.")],
            slips=["Restarting the database first.", "Raising max_connections as the only fix.", "Having no timeouts, so one stuck session can stall everything."],
        ),
        quick=[
            ("Why is a PostgreSQL connection expensive?", "Each connection is its own process: opening takes time and each uses memory."),
            ("What does `idle in transaction` mean and why is it dangerous?", "A transaction is open but doing nothing; it holds locks and an old snapshot, blocking others and vacuum."),
            ("Which function shows who is blocking a session?", "`pg_blocking_pids(pid)`."),
        ],
        traps=[
            "Raising `max_connections` instead of adding a pooler.",
            "A pool bigger than the database can run in parallel: queueing moves into the database where it is more expensive.",
            "Holding a transaction open across a network call, a file upload or user input.",
        ],
    ),
]
