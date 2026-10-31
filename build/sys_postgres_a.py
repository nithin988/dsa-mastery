"""S18 relational databases: part A (rig, lessons 1 to 3)."""
import sysviz as v

RIG = r'''mkdir -p ~/pg && cd ~/pg && cat > rig.sh <<'EOF'
# Helpers for a private PostgreSQL that runs as you, on a socket in ~/pg, port 5545.
export PG=$(ls -d /usr/lib/postgresql/*/bin | head -1); export PATH=$PG:$PATH
export P=$HOME/pg PGHOST=$HOME/pg PGPORT=5545 PGUSER=learner PGDATABASE=shop
pgup() { [ -d $P/data ] || initdb -D $P/data -A trust -U learner >/dev/null
         pg_ctl -D $P/data -o "-p 5545 -k $P -c listen_addresses='' -c fsync=off $*" -l $P/log -w start >/dev/null
         createdb shop 2>/dev/null || true; }
pgdown() { pg_ctl -D $P/data -m fast stop >/dev/null 2>&1; }
q() { psql -X -q "$@"; }
EOF
. ./rig.sh; echo "rig ready in $P: rig.sh gives pgup, pgdown and q (psql)"'''

SEED = r'''. ~/pg/rig.sh; pgup
q <<'EOF'
select setseed(0.42) as s \gset
create table customers(id int primary key, name text not null, country text not null);
insert into customers select g, 'customer ' || g, (array['IN','US','DE','BR','JP'])[1 + g % 5] from generate_series(1, 20000) g;
create table orders(id bigserial primary key, customer_id int not null references customers(id),
                    status text not null, amount numeric(10,2) not null, created_at timestamptz not null);
insert into orders(customer_id, status, amount, created_at)
  select 1 + (random()*19999)::int, (array['new','paid','shipped','done'])[1 + (random()*3)::int],
         round((random()*500)::numeric, 2), now() - (random()*365 || ' days')::interval
  from generate_series(1, 500000);
analyze;
EOF
q -At -c "select 'customers', count(*) from customers union all select 'orders', count(*) from orders"
q -At -c "select 'orders table size: ' || pg_size_pretty(pg_table_size('orders'))"
pgdown'''

TABLE_VIZ = v.figure(
    720, 232,
    [v.box(10, 20, 150, 150, "customers", "acc", "id (primary key), name, country"),
     v.box(280, 20, 180, 150, "orders", "ok", "id (primary key), customer_id, status, amount, created_at"),
     v.arrow(280, 95, 160, 95),
     v.text(220, 84, "customer_id refers to id", "dg-s"),
     v.box(560, 40, 150, 56, "Constraint", "warn", "a foreign key refuses orders for customers that do not exist"),
     v.box(560, 110, 150, 56, "Index", "acc", "the primary key is indexed, so lookups by id are fast"),
     v.text(360, 206, "Tables hold rows; keys tie them together; the database enforces the rules so every application sees consistent data.", "dg-s")],
    "Tables, keys and constraints", "The relational model: data in tables, relationships by keys, rules enforced by the database")

BTREE_VIZ = v.figure(
    720, 250,
    [v.box(285, 14, 150, 44, "Root page", "acc", "ranges of keys"),
     v.arrow(330, 58, 150, 100), v.arrow(360, 58, 360, 100), v.arrow(390, 58, 570, 100),
     v.box(70, 100, 160, 44, "Branch 1 to 5000", "acc", "points to leaf pages"),
     v.box(280, 100, 160, 44, "Branch 5001 to 10000", "acc", "points to leaf pages"),
     v.box(490, 100, 160, 44, "Branch 10001 to 20000", "acc", "points to leaf pages"),
     v.arrow(360, 144, 360, 180),
     v.box(220, 180, 280, 44, "Leaf page: key 7342 -> row location", "ok", "the table row is fetched with one more read"),
     v.text(360, 244, "Three or four page reads find one row among millions. A full scan reads every page.", "dg-s")],
    "A B-tree index", "Each level narrows the search; the depth grows very slowly with the number of rows")

TXN_SEQ = v.seq(
    ["Session A", "Database", "Session B"],
    [("a->b", 0, 1, "BEGIN; read balance = 100"),
     ("a->b", 2, 1, "BEGIN; read balance = 100"),
     ("a->b", 0, 1, "write balance = 70 (100 - 30)"),
     ("a->b", 2, 1, "write balance = 50 (100 - 50)", "bad"),
     ("note", 0, 2, "both read the old value: A's update is overwritten (a lost update)"),
     ("note", 0, 2, "fix: let the database do the arithmetic, or lock the row while you work")],
    "A lost update", "Two read-modify-write cycles interleave and one change disappears")

LESSONS_A = [
    dict(
        title="Why a database: tables, SQL and the ACID guarantees",
        tier="hot",
        situation="Your orders live in a pile of files. Two processes write at once and corrupt a file; a crash halfway through a payment loses money; finding \"all paid orders from Germany last week\" means reading everything. A database solves exactly these problems, and almost every system design includes one.",
        learn=["Tables, rows, keys and relationships", "What a transaction is, and what ACID promises", "Your own real PostgreSQL, running in a minute", "Constraints: the database refusing bad data"],
        model=[
            "A **relational database** stores data in **tables** of rows and columns. Each row has a **primary key** that identifies it; a **foreign key** in one table refers to a key in another (an order refers to its customer). You describe **what** you want in **SQL** (`select`, `insert`, `update`, `delete`, `join`) and the database decides **how** to get it, including which indexes to use. The database also enforces **constraints** (not null, unique, foreign key, check), so a bug in one application cannot silently store nonsense.",
            "A **transaction** groups several statements into one unit. **ACID** names what the database promises: **Atomicity** (all of the statements take effect, or none do), **Consistency** (constraints hold before and after), **Isolation** (concurrent transactions do not see each other's half-finished work, to a degree you choose) and **Durability** (once committed, the data survives a crash, because it is written to a log on disk first). Almost every design question about money, bookings or inventory leans on these four words.",
        ],
        analogy="A bank's back office with rules: every transfer is written in a ledger, a transfer is either fully recorded or not at all, two clerks never see each other's half-written entry, and an entry stays even if the lights go out. The database is that office, run by a very fast clerk.",
        visual=[TABLE_VIZ],
        sim=None,
        walk=[
            ("Design tables around things", "Customers and orders are separate tables; each order stores only the customer's `id`, not a copy of the customer."),
            ("Declare the rules", "Primary keys, `not null`, and a foreign key from orders to customers: the database now rejects an order for a customer that does not exist."),
            ("Ask questions in SQL", "A join combines rows from several tables; `group by` aggregates; `where` filters. You never say which loop to run."),
            ("Group changes into a transaction", "`begin; ... commit;` makes several statements succeed or fail together; `rollback` undoes them."),
            ("The database logs before it changes", "Committed work is written to a write-ahead log first, so a crash cannot lose it (the next lessons show this)."),
        ],
        groups=[
            dict(title="Build the rig, load real data, ask questions", cmds=[
                dict(c=RIG,
                     e="Creates the rig used by the whole module: a small file of helper functions that start a **real PostgreSQL** under your own user (its own data directory, a socket in `~/pg`, no network, no root) and stop it again. `fsync=off` is set only to make the practice data load quickly; never use it for data you care about."),
                dict(volatile=True, c=SEED,
                     e="Creates two tables and fills them: 20,000 customers and 500,000 orders with random but reproducible values (`setseed`). `analyze` lets PostgreSQL collect statistics about the data, which its planner uses to choose how to run queries. Everything in the next lessons runs against these tables.",
                     annot=[("customers | 20000", "the customers table has 20,000 rows"),
                            ("orders | 500000", "the orders table has 500,000 rows: big enough that a full scan is noticeable"),
                            ("orders table size: ~30 MB", "the table's storage on disk: this is what a full scan has to read")]),
                dict(volatile=True, c=r'''. ~/pg/rig.sh; pgup
q -c "select c.country, count(*) as orders, round(avg(o.amount), 2) as avg_amount
      from orders o join customers c on c.id = o.customer_id
      where o.status = 'paid' group by c.country order by orders desc"
pgdown''',
                     e="One SQL statement answers a real question: for paid orders, how many came from each country and what was the average amount. `join` matches each order to its customer by the foreign key, `where` keeps the paid ones, `group by` makes one row per country. You described the result; PostgreSQL chose how to compute it (the next lesson shows how).",
                     annot=[("country | orders | avg_amount", "the result is itself a table: one row per country"),
                            ("five rows (IN, US, DE, BR, JP)", "customers were assigned five countries, so five groups appear")]),
            ]),
            dict(title="Atomicity and constraints, for real", cmds=[
                dict(volatile=True, c=r'''. ~/pg/rig.sh; pgup
q -c "create table accounts(id int primary key, owner text, balance int check (balance >= 0)); insert into accounts values (1,'ana',100),(2,'ben',20);"
echo "--- a transfer that fails halfway, inside a transaction:"
q -c "begin; update accounts set balance = balance - 150 where id = 1; update accounts set balance = balance + 150 where id = 2; commit;" 2>&1 | head -3
echo "--- balances afterwards (nothing moved):"
q -At -c "select owner, balance from accounts order by id"
echo "--- a valid transfer:"
q -c "begin; update accounts set balance = balance - 30 where id = 1; update accounts set balance = balance + 30 where id = 2; commit;"
q -At -c "select owner, balance from accounts order by id"
echo "--- an order for a customer that does not exist:"
q -c "insert into orders(customer_id, status, amount, created_at) values (999999, 'new', 10, now())" 2>&1 | head -2
pgdown''',
                     e="Atomicity and constraints in action. The first transfer tries to move 150 from an account that holds 100: the `check (balance >= 0)` constraint rejects the first update, the transaction is aborted, and the second update never takes effect: **no money moved**. The valid transfer commits both updates together. The last statement tries to insert an order for a customer that does not exist, and the foreign key refuses it. The database protected the data even though the application did nothing special.",
                     annot=[("violates check constraint \"accounts_balance_check\"", "the rule `balance >= 0` rejected the withdrawal; the whole transaction is now aborted"),
                            ("ana | 100 / ben | 20", "after the failed transfer nothing changed: all or nothing"),
                            ("ana | 70 / ben | 50", "after the valid transfer both updates took effect together"),
                            ("violates foreign key constraint", "customer 999999 does not exist, so the order is refused")]),
            ]),
        ],
        scenario=dict(
            title="\"Explain ACID with an example. Why does it matter?\"",
            ask="A warm-up that opens many database discussions. They want precise definitions tied to a concrete example, not four memorised words.",
            clarify=[("Is it okay if I use a bank transfer?", "Yes: it is the classic example because partial failure and concurrency both matter.")],
            think=[("Define each letter with the transfer.", "Atomicity: debit and credit both happen or neither. Consistency: constraints (no negative balance, totals preserved) hold after commit. Isolation: another transaction never sees the money gone from one account and not yet in the other. Durability: after the commit is acknowledged, a crash does not undo it."),
                   ("Say how it is implemented, briefly.", "Atomicity and durability come from a write-ahead log: changes are recorded in the log and flushed to disk at commit; recovery replays or undoes. Isolation comes from locks or multi-version concurrency control. Consistency comes from constraints and the application's own rules."),
                   ("Say why it matters for design.", "Without transactions every failure window needs custom repair code. With them, one `commit` is the point of no return. When data is spread across several databases you lose this for free, which is why distributed transactions, sagas and idempotency exist later in the course."),
                   ("Add the honest caveat.", "Isolation has levels: the default in most systems is weaker than \"serializable\", so you must know which anomalies remain (the next lessons demonstrate them).")],
            answer=["\"ACID describes what a transaction guarantees. Take a transfer of 30 from Ana to Ben. Atomicity: the debit and the credit happen together or not at all, so a crash between them cannot lose money. Consistency: the rules, such as no negative balance, hold after the transaction. Isolation: another transaction never sees the money missing from Ana and not yet in Ben. Durability: once the commit is acknowledged, a crash will not undo it, because the change is in the write-ahead log on disk.",
                    "It matters because it moves failure handling into the database: one commit is the point of no return. Two caveats: isolation comes in levels and the common default allows some anomalies, and once data lives in several databases you no longer get this for free, which is where sagas and idempotency come in.\""],
            follow=[("How does a database achieve durability?", "It appends the change to a write-ahead log and flushes the log to disk before acknowledging the commit; data pages are written later and recovered from the log after a crash."),
                    ("Is ACID the same as the consistency in CAP?", "No. ACID consistency means constraints hold; CAP consistency means all replicas agree (linearizability). Same word, different meaning."),
                    ("Do NoSQL databases have transactions?", "Some do (single-document or multi-document), many give atomicity only per record. Check each system rather than assume.")],
            slips=["Reciting the four words without an example.", "Confusing the C in ACID with the C in CAP.", "Claiming transactions work across separate databases automatically."],
        ),
        quick=[
            ("What does atomicity guarantee?", "All statements in the transaction take effect, or none do."),
            ("What is a foreign key for?", "It makes the database refuse a row that refers to a row that does not exist."),
            ("Why does PostgreSQL write to a log before the data files?", "So a committed change can be recovered after a crash: durability."),
        ],
        traps=[
            "Running statements outside a transaction and assuming they are grouped: each runs on its own unless you `begin`.",
            "Turning off fsync or durability settings in production to \"go faster\".",
            "Enforcing rules only in the application: the next application (or script) will bypass them.",
        ],
    ),
    dict(
        title="Indexes and query plans: why one query takes 8 ms and another takes 8 s",
        tier="hot",
        situation="The orders table has half a million rows and \"show this customer's orders\" suddenly takes a visible fraction of a second. At ten times the data it will take seconds. The cure is almost always an index, and the skill is knowing how to see that, choose the right one, and know what it costs.",
        learn=["How a B-tree index finds one row among millions", "Reading EXPLAIN and EXPLAIN ANALYZE", "Composite indexes and column order", "What indexes cost on writes and in space"],
        model=[
            "Without an index the database must read the **whole table** to find matching rows (a **sequential scan**). An **index** is a separate, sorted structure (in PostgreSQL by default a **B-tree**) that maps column values to row locations, so a lookup reads three or four pages instead of all of them. **EXPLAIN** shows the **plan** the planner chose (which scans, joins and sorts); **EXPLAIN ANALYZE** also runs the query and shows the actual rows and time. The planner chooses using **statistics** about the data, so stale statistics (run `analyze`) lead to bad plans.",
            "A **composite index** on `(a, b)` is sorted by `a`, then by `b` within each `a`: it helps filters on `a`, or on `a` and `b`, but **not** on `b` alone, and it can return rows already sorted by `b` for a fixed `a`. Put equality columns first and the range or sort column last. Indexes are not free: every insert, update of an indexed column and delete must also update every index, and indexes take disk space. They help reads at a cost to writes, so index what real queries need, not every column.",
        ],
        analogy="The index at the back of a textbook: finding every mention of a word takes seconds, but whoever writes the book must maintain the index with every edit, and a book with an index for every possible word would be mostly index.",
        visual=[BTREE_VIZ],
        sim=None,
        walk=[
            ("Find the slow query", "Start from a real query (from the slow query log or a profile), not from guesses about which columns to index."),
            ("Ask for the plan", "`EXPLAIN ANALYZE` shows `Seq Scan` (reads everything) or `Index Scan` (uses an index), the rows examined and the time."),
            ("Check the estimates", "If the planner's estimated rows differ wildly from the actual rows, run `ANALYZE` or investigate skew."),
            ("Create the index that matches the query", "Equality columns first, then the range or sort column. `create index ... on orders(customer_id)`."),
            ("Verify, then count the cost", "Re-run EXPLAIN ANALYZE. Then measure insert speed and index size: every index must be maintained."),
        ],
        groups=[
            dict(title="Before and after an index, on real data", cmds=[
                dict(c=r'''. ~/pg/rig.sh; pgup
echo "--- plan for one customer, no index on customer_id:"
q -At -c "explain (analyze, costs off, timing off, summary off) select * from orders where customer_id = 4242"
q -c "create index orders_customer_idx on orders(customer_id)"
echo "--- the same query after creating the index:"
q -At -c "explain (analyze, costs off, timing off, summary off) select * from orders where customer_id = 4242"
pgdown''',
                     e="The same query, before and after. Without an index PostgreSQL reads **all** 500,000 rows and throws away almost all of them (`Rows Removed by Filter`). After `create index`, it uses the index to jump straight to the few matching rows. Nothing about the query changed; only the available access path.",
                     annot=[("Parallel Seq Scan on orders (inside a Gather)", "reads the whole table, here split over three processes (two workers and the leader)"),
                            ("Rows Removed by Filter: 166658 (per process)", "each process read about a third of the table and discarded nearly everything: the work was wasted"),
                            ("Bitmap Index Scan on orders_customer_idx / Bitmap Heap Scan", "after the index: look up matching row locations in the index, then fetch just those table pages"),
                            ("actual rows=25 / Heap Blocks: exact=25", "this customer has 25 orders in 25 table pages: that is all that has to be read now")]),
                dict(volatile=True, c=r'''. ~/pg/rig.sh; pgup
q -c "drop index if exists orders_customer_idx"
echo "--- time without the index:"; q -At -c "explain (analyze, costs off) select * from orders where customer_id = 4242" | grep -E "Execution Time"
q -c "create index orders_customer_idx on orders(customer_id)"
echo "--- time with the index:"; q -At -c "explain (analyze, costs off) select * from orders where customer_id = 4242" | grep -E "Execution Time"
q -At -c "select 'index size: ' || pg_size_pretty(pg_relation_size('orders_customer_idx')) || ', table size: ' || pg_size_pretty(pg_table_size('orders'))"
pgdown''',
                     e="The difference in time, measured. The exact milliseconds depend on your machine; the ratio is what matters: the indexed lookup is typically tens to hundreds of times faster than scanning the table (about 55 times here), and the gap grows with the table. The last line shows the price: the index takes real space (here about an eighth of the table, more for wider columns).",
                     annot=[("Execution Time: 14.985 ms (no index)", "a parallel scan of 500,000 rows"),
                            ("Execution Time: 0.270 ms (with index)", "a few page reads: about 55 times faster"),
                            ("index size: 3776 kB, table size: 30 MB", "an index on one integer column takes about an eighth of the table: indexes cost disk space and memory")]),
            ]),
            dict(title="Composite indexes and the cost on writes", cmds=[
                dict(c=r'''. ~/pg/rig.sh; pgup
q -c "create index orders_status_created_idx on orders(status, created_at)"
echo "--- filter on both columns (equality first, range second): uses the index"
q -At -c "explain (costs off) select id from orders where status = 'paid' and created_at > now() - interval '2 days'"
echo "--- filter on the second column only: the index cannot help much"
q -At -c "explain (costs off) select id from orders where created_at > now() - interval '2 days'"
echo "--- newest 5 paid orders: the index returns them already sorted"
q -At -c "explain (costs off) select id from orders where status = 'paid' order by created_at desc limit 5"
pgdown''',
                     e="Column order matters. The index on `(status, created_at)` is sorted by status, then by date within each status. A filter on status **and** a date range jumps to one status and reads a slice. A filter on **only** the date cannot use that ordering, so PostgreSQL falls back to a different plan. And \"newest five paid orders\" needs no sorting at all: the index already stores paid orders in date order, so the first five entries from the end are the answer.",
                     annot=[("Bitmap Index Scan on orders_status_created_idx (first query)", "both columns are used in Index Cond: status narrows, created_at slices"),
                            ("Parallel Seq Scan (second query)", "created_at alone is not a prefix of the index, so PostgreSQL scans the table instead"),
                            ("Index Scan Backward ... Limit (third query)", "no Sort node: the index delivers rows in order, and `limit 5` stops after five")]),
                dict(volatile=True, c=r'''. ~/pg/rig.sh; pgup
q -c "create table w0(id serial primary key, a int, b int, c int, d int)"
q -c "create table w4(id serial primary key, a int, b int, c int, d int); create index on w4(a); create index on w4(b); create index on w4(c); create index on w4(d);"
t() { s=$(date +%s%N); q -c "$1" >/dev/null; e=$(date +%s%N); echo "$2: $(( (e-s)/1000000 )) ms"; }
t "insert into w0(a,b,c,d) select g, g*7 % 1000, random()*1e6, g % 50 from generate_series(1,200000) g" "200,000 inserts, no extra indexes"
t "insert into w4(a,b,c,d) select g, g*7 % 1000, random()*1e6, g % 50 from generate_series(1,200000) g" "200,000 inserts, four extra indexes"
pgdown''',
                     e="The cost of indexes on writes. The same 200,000 rows are inserted into two identical tables, one with only its primary key and one with four extra indexes. Every insert must also add an entry to every index, so the second load is clearly slower (about 4 times in the recording). This is why you index what real queries need and not every column.",
                     annot=[("no extra indexes: 372 ms", "baseline: only the primary key is maintained"),
                            ("four extra indexes: 1501 ms (about 4 times slower)", "each index is another structure to update on every insert (your numbers will differ)")]),
            ]),
        ],
        scenario=dict(
            title="\"This query is slow. How do you find out why, and what do you do?\"",
            ask="The most common database question in interviews and on call. They want a method, not a guess.",
            clarify=[("How slow, how often, and how big is the table?", "A 2 s query run once a day is different from a 50 ms query run 5,000 times a second."),
                     ("Is it slow always, or only sometimes?", "Always slow suggests a missing index; sometimes slow suggests locks, a bad plan after a statistics change, or load.")],
            think=[("Get the actual query and its plan.", "`EXPLAIN (ANALYZE, BUFFERS)` on the real query with real parameter values. Look for a Seq Scan on a big table, a large gap between estimated and actual rows, a Sort spilling to disk, or nested loops over many rows."),
                   ("Diagnose from the plan.", "Seq Scan with many rows removed means a missing or unusable index. Wrong estimates mean stale statistics (`ANALYZE`) or correlated columns. A Sort over a huge set means an index could deliver the order."),
                   ("Choose the index to fit the query.", "Equality columns first, then range or sort; consider a covering index (`include`) if the query reads few columns; check functions in the WHERE clause (`lower(email)`) need a matching expression index."),
                   ("Weigh the cost.", "Each index slows writes and uses memory. Measure on a copy with production-like data; create indexes without blocking writers (`create index concurrently`)."),
                   ("Verify and monitor.", "Re-run EXPLAIN ANALYZE, compare latency percentiles before and after, and watch that write throughput did not suffer.")],
            answer=["\"First I get the real query with real parameters and run EXPLAIN ANALYZE. I look for a sequential scan on a large table, estimates far from actual rows, or a sort that spills. A Seq Scan with almost all rows removed means a missing or unusable index; bad estimates mean I should refresh statistics.",
                    "I design the index around the query: equality columns first, then the range or sort column, and I check things like a function applied to a column that would stop the index being used. I weigh the write cost and the space, build it concurrently so writers are not blocked, and then re-run the plan and compare latency percentiles before and after. If a single index is not enough I look at the query itself: select fewer columns, paginate with a keyset instead of a big offset, or cache the result.\""],
            follow=[("Why might the planner ignore your index?", "The query uses a function or type cast on the column, the table is small, the condition matches most rows (a scan is cheaper), or statistics are stale."),
                    ("What is a covering index?", "An index that contains every column the query needs (`include (...)`), so PostgreSQL answers from the index alone without visiting the table."),
                    ("What are the downsides of OFFSET pagination?", "The database still reads and discards all skipped rows, so deep pages get slower; keyset pagination (`where id > last_seen order by id limit n`) stays fast.")],
            slips=["Adding an index without looking at the plan.", "Indexing every column \"just in case\".", "Forgetting that a function on a column prevents the plain index from being used."],
        ),
        quick=[
            ("What does a `Seq Scan` mean in a plan?", "The database reads the whole table."),
            ("Does an index on `(a, b)` help a query that filters only on `b`?", "Not as a normal lookup: the index is sorted by `a` first."),
            ("Name two costs of an index.", "Slower writes (every index is updated) and extra disk space and memory."),
        ],
        traps=[
            "Judging a plan on a tiny table: the planner correctly prefers a scan there. Test with realistic data.",
            "A function on the column (`where lower(name) = ...`) silently bypasses a plain index.",
            "Creating an index on a busy table without `concurrently`: it blocks writes while it builds.",
        ],
    ),
    dict(
        title="Transactions and isolation: what concurrent users can see, and break",
        tier="hot",
        situation="Two customers buy the last ticket at the same moment. Two admin screens edit the same balance. A report runs while data changes underneath it. Isolation decides what each transaction is allowed to see, and your code must be written for the level you actually have.",
        learn=["Lost updates, non-repeatable reads and how to prevent them", "Isolation levels: read committed, repeatable read, serializable", "Row locks (`FOR UPDATE`) and deadlocks", "Optimistic versus pessimistic concurrency"],
        model=[
            "When transactions run **concurrently**, a few things can go wrong. A **lost update**: both read a value, both compute from it, the second write overwrites the first. A **non-repeatable read**: you read a row twice in one transaction and get different values because someone committed in between. A **phantom**: a repeated query returns new rows. A **dirty read** (seeing uncommitted data) is not allowed in PostgreSQL. **Isolation levels** choose how much of this is prevented: PostgreSQL's default **read committed** sees newly committed data on every statement; **repeatable read** gives a stable snapshot for the whole transaction; **serializable** behaves as if transactions ran one after another (and may abort some with a serialization failure, which the application must retry).",
            "Prevent lost updates by not doing read-modify-write in the application: let the database compute (`set balance = balance - 30`), or **lock** the row you read (`select ... for update`) so other writers wait, or use **optimistic concurrency** (a version column: `update ... where id = 1 and version = 7`, and retry if zero rows changed). Locks can create **deadlocks** (A waits for B while B waits for A); PostgreSQL detects them and aborts one transaction, so applications must retry, and should take locks in a consistent order.",
        ],
        analogy="Two people editing the same shared document: if each copies it, edits and pastes it back, one person's changes vanish. Locking the document while you edit, or checking nobody changed it since you copied it, are the two ways to stay safe.",
        visual=[TXN_SEQ],
        sim=None,
        walk=[
            ("Two sessions read the same row", "Both see balance 100 at the start; neither knows about the other."),
            ("Each computes in the application", "A computes 70, B computes 50 from the same old value."),
            ("Both write", "The last write wins; the other change is silently lost. No error is raised."),
            ("Fix it in the database", "A single `update ... set balance = balance - 30` is atomic; or take a row lock first with `for update`."),
            ("Choose an isolation level on purpose", "Know that read committed can show you different data on each statement; use repeatable read or serializable when a transaction needs a consistent view, and be ready to retry."),
        ],
        groups=[
            dict(title="Reproduce a lost update, then fix it two ways", cmds=[
                dict(volatile=True, c=r'''. ~/pg/rig.sh; pgup
q -c "create table acct(id int primary key, balance int); insert into acct values (1, 100)"
echo "--- application-style read, think, write (two clients at once):"
( b=$(q -At -c "select balance from acct where id=1"); sleep 0.6; q -c "update acct set balance=$((b-30)) where id=1" ) &
( b=$(q -At -c "select balance from acct where id=1"); sleep 1.0; q -c "update acct set balance=$((b-50)) where id=1" ) &
wait
echo "balance is now: $(q -At -c 'select balance from acct where id=1')   (100 - 30 - 50 should be 20)"
echo "--- the same two withdrawals as single atomic statements:"
q -c "update acct set balance = 100 where id=1"
( q -c "update acct set balance = balance - 30 where id=1" ) & ( q -c "update acct set balance = balance - 50 where id=1" ) & wait
echo "balance is now: $(q -At -c 'select balance from acct where id=1')"
echo "--- read-modify-write protected by a row lock:"
q -c "update acct set balance = 100 where id=1"
w() { q -At -c "begin; select balance from acct where id=1 for update;" -c "select pg_sleep($2)" -c "update acct set balance = balance - $1 where id=1; commit;" >/dev/null; }
w 30 0.6 & sleep 0.1; w 50 0.1 & wait
echo "balance is now: $(q -At -c 'select balance from acct where id=1')"
pgdown''',
                     e="The classic bug, reproduced. Two clients each read 100, wait (as real code does while it computes), then write. The result is **70 or 50, not 20**: one withdrawal vanished and nothing reported an error. Making the update a single atomic statement fixes it (20), and so does locking the row you read with `FOR UPDATE`: the second client waits for the first to finish, then reads the new value and gets 20.",
                     annot=[("balance is now: 50  (100 - 30 - 50 should be 20)", "the last writer overwrote the first: a lost update (you may see 70 instead depending on timing)"),
                            ("balance is now: 20 (atomic statements)", "the database applied both decrements to the current value: correct"),
                            ("balance is now: 20 (row lock)", "the second transaction waited on the lock, then saw the committed value: correct")]),
            ]),
            dict(title="Isolation levels, and a deadlock", cmds=[
                dict(volatile=True, c=r'''. ~/pg/rig.sh; pgup
q -c "create table seen(n int)"
for lvl in "read committed" "repeatable read"; do
  q -c "truncate seen; insert into seen values (1),(2),(3)"
  echo "--- isolation level: $lvl"
  ( q -At -c "begin isolation level $lvl; select 'first count:  ' || count(*) from seen;" -c "select pg_sleep(1.2)" -c "select 'second count: ' || count(*) from seen; commit;" | grep count ) &
  sleep 0.5; q -c "insert into seen values (4)"
  wait
done
pgdown''',
                     e="What a transaction can see. A long transaction counts the rows, a second session inserts a row and commits, and the first counts again. Under **read committed** (PostgreSQL's default) each statement sees the latest committed data, so the count changes inside one transaction (a **non-repeatable read** of the whole result: a phantom). Under **repeatable read** the transaction keeps its snapshot from the start and both counts agree.",
                     annot=[("read committed: first count: 3 / second count: 4", "the second statement saw the other session's committed insert"),
                            ("repeatable read: first count: 3 / second count: 3", "the snapshot taken at the start is used for the whole transaction")]),
                dict(volatile=True, c=r'''. ~/pg/rig.sh; pgup
q -c "create table lk(id int primary key, v int); insert into lk values (1,0),(2,0)"
( q -c "begin; update lk set v=1 where id=1;" -c "select pg_sleep(1)" -c "update lk set v=1 where id=2; commit;" 2>&1 | grep -E "ERROR|DETAIL" | cut -c1-90 ) &
sleep 0.3
( q -c "begin; update lk set v=2 where id=2;" -c "select pg_sleep(1)" -c "update lk set v=2 where id=1; commit;" 2>&1 | grep -E "ERROR|DETAIL" | cut -c1-90 ) &
wait
echo "--- the surviving values (one transaction was rolled back by the database):"
q -At -c "select id, v from lk order by id"
pgdown''',
                     e="A deadlock, on purpose. Transaction 1 locks row 1 then wants row 2; transaction 2 locks row 2 then wants row 1. Neither can ever proceed. PostgreSQL notices after about a second (`deadlock_timeout`), **aborts one transaction** with an error and lets the other finish. The application that gets the error must **retry**. The cure is to always lock rows in the same order.",
                     annot=[("ERROR: deadlock detected", "the database found the cycle and chose a victim"),
                            ("DETAIL: Process ... waits for ShareLock ... blocked by process ...", "who waited for whom"),
                            ("1|2 and 2|2", "both rows hold the surviving transaction's value 2: the aborted transaction's updates were rolled back entirely"),]),
            ]),
        ],
        scenario=dict(
            title="\"Two users try to book the last seat at the same moment. How do you make sure only one succeeds?\"",
            ask="A staple of design interviews (tickets, rooms, inventory). They want you to name the race and give at least two concrete fixes with trade-offs.",
            clarify=[("One database or several? Is the inventory in a single row or many?", "A single primary database makes row locks and constraints enough; sharded or multi-service inventory needs more."),
                     ("What happens on conflict: wait, fail or retry?", "Failing fast with a clear message is usually better for the second buyer than waiting.")],
            think=[("Name the race.", "Both read `seats_left = 1`, both decide to sell, both decrement: oversell. It is a read-modify-write race."),
                   ("Fix 1: atomic conditional update.", "`update seats set left = left - 1 where event = 7 and left > 0`, then check how many rows were updated: zero means sold out. The database serialises the two updates; no explicit lock or retry loop."),
                   ("Fix 2: row lock.", "`begin; select ... for update; check; update; commit;` The second transaction waits, then sees the new value. Simple but holds the lock while your code runs: keep the transaction short."),
                   ("Fix 3: optimistic version check or a unique constraint.", "For individual seats, a unique constraint on `(event, seat)` makes the second insert fail: the database enforces it, so it holds under any concurrency."),
                   ("Handle the edges.", "Retries after serialization failures or deadlocks; a reservation with a short expiry (hold the seat for 10 minutes) with a job to release expired holds; idempotency keys so a retried request does not book twice."),
                   ("Mention scale.", "A hot single row (the last seat of a famous concert) is serialised on its lock: that is correct but limits throughput; queue the requests or shard by event.")],
            answer=["\"The race is read-modify-write: both requests see one seat left and both sell it. I would let the database make the decision atomically. The simplest way is a conditional update, `update seats set left = left - 1 where event_id = 7 and left > 0`, then check the number of rows changed: if it is zero, the seat is gone. For individual seats a unique constraint on event and seat does the same job and cannot be bypassed.",
                    "Alternatively I would take a row lock with SELECT FOR UPDATE in a short transaction. I would keep transactions short, retry on deadlock or serialization errors, hold a seat with an expiry during payment, and use an idempotency key so a retried request does not book twice. For a very hot event all buyers serialise on one row, which is correct but limits throughput, so I would queue requests or partition by event.\""],
            follow=[("What if the inventory is in a different service from the database that records the order?", "You cannot use one transaction. Reserve first (with an expiry), then confirm after payment, and compensate on failure: a saga with idempotent steps (later modules)."),
                    ("Optimistic or pessimistic locking?", "Optimistic works well when conflicts are rare (retry on the rare conflict, no waiting); pessimistic when conflicts are frequent or retries are costly."),
                    ("Why not just use serializable isolation everywhere?", "It is correct but aborts some transactions under contention, which you must retry, and costs throughput; use it where the invariant is complex, not by default.")],
            slips=["Checking availability in the application and then updating separately.", "Holding a row lock during a slow external call such as payment.", "Forgetting what happens on a retry: a double booking."],
        ),
        quick=[
            ("What is a lost update?", "Two transactions read the same value and both write back results based on it; one write overwrites the other."),
            ("How does `update t set n = n - 1` avoid it?", "The database applies it to the current value atomically, so concurrent updates both take effect."),
            ("What should an application do when it gets a deadlock error?", "Retry the transaction; and lock rows in a consistent order to make deadlocks rare."),
        ],
        traps=[
            "Assuming the default isolation level protects read-modify-write cycles: it does not.",
            "Long transactions that hold locks (and old snapshots) while waiting on slow things.",
            "No retry logic for deadlocks and serialization failures: rare errors become user-visible failures.",
        ],
    ),
]
