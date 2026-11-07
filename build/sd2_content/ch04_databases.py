"""Chapter 4: Where the data lives (relational databases: indexes, transactions, the log)."""
import sd2kit as k
from sd2 import scen

# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "Monday: slow page", "kind": "warn",
     "scene": lambda cx, cy, w: k.person(cx - 56, cy - 4, 1.1, "warn") + k.flow(cx - 36, cy - 4, cx + 6, cy - 4, "warn") + k.database(cx + 46, cy - 4, None, "warn") + k.badge(cx, cy + 50, "My orders: 8 seconds", "warn"),
     "caption": "The \"my orders\" page reads every order ShopKart has ever taken, to find one customer's few."},
    {"title": "Tuesday: two buyers", "kind": "bad",
     "scene": lambda cx, cy, w: k.person(cx - 56, cy - 34, 1.0, "bad") + k.person(cx - 56, cy + 22, 1.0, "bad") + k.flow(cx - 36, cy - 34, cx + 10, cy - 8, "bad") + k.flow(cx - 36, cy + 22, cx + 10, cy + 6, "bad")
     + k.database(cx + 46, cy - 2, None, "bad") + k.badge(cx + 46, cy + 50, "1 left, 2 sold", "bad"),
     "caption": "The last pair of trainers: two customers press Buy in the same second. Both are told yes."},
    {"title": "Friday: lost orders", "kind": "bad",
     "scene": lambda cx, cy, w: k.server(cx - 48, cy - 2, None, "bad") + k.alert(cx + 40, cy - 2, None) + k.badge(cx, cy + 50, "3 paid orders gone", "bad"),
     "caption": "A power cut restarts the server. Three orders that customers had paid for are not there."},
], "ShopKart's three bad days with data", "Three different failures, one cause: the shop treated its data like a pile of files.")

IDEA_FIG = k.figure(720, 270, [
    k.person(50, 120, 1.15), k.note(50, 160, "Shop"),
    k.flow(80, 120, 168, 120, "acc", "SQL"),
    k.database(210, 120, "Database"),
    k.flow(240, 100, 346, 52, "ok"), k.flow(240, 120, 322, 120, "ok"), k.flow(240, 140, 306, 206, "ok"),
    k.badge(380, 50, "Index", "ok"), k.note(414, 54, "find rows without reading the whole table", "", "start"),
    k.badge(380, 120, "Transaction", "ok"), k.note(440, 124, "all or nothing, one buyer at a time", "", "start"),
    k.badge(380, 208, "Write-ahead log", "ok"), k.note(450, 212, "writes survive a crash", "", "start"),
    k.note(360, 254, "A database is a promise: fast to find, safe to share, safe to keep.", ""),
], "The three things a database gives you", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


HOW = [
    ("Keep data in tables and ask with SQL",
     "A relational database stores data as **tables** of rows (orders, customers, stock). You ask questions in **SQL**, and the database decides how to find the answer. It also protects the data with rules, so a bad row is rejected instead of saved.",
     _small([k.database(70, 40, "database", "ok"), k.badge(190, 40, "orders", "acc"), k.badge(280, 40, "customers", "acc"), k.badge(370, 40, "stock", "acc"), k.flow(412, 40, 480, 40, "acc"), k.note(560, 44, "ask with SQL", "acc")], "Tables inside a database", h=98)),
    ("Add an index so it does not read everything",
     "Without an index, finding one customer's orders means reading **every row**. An **index** is a sorted list of customer ids that points to the rows, like the index of a book. The database jumps straight there.",
     _small([k.database(60, 38, None, "bad"), k.flow(90, 38, 190, 38, "bad", "no index"), k.badge(280, 38, "reads every row", "bad"), k.database(60, 90, None, "ok"), k.flow(90, 90, 190, 90, "ok", "index"), k.badge(280, 90, "reads 25 pages", "ok"), k.note(500, 66, "same answer, far less work", "ok")], "A query with and without an index", h=128)),
    ("Let the database referee two buyers",
     "Two buyers each read \"1 left\", then each write \"0 left\": both are told yes. This is a **lost update**. Fix it by letting the database do the subtraction in one statement, or by **locking** the row so the second buyer waits for the first.",
     _small([k.person(50, 28, .85), k.person(50, 76, .85), k.flow(76, 28, 190, 46, "bad"), k.flow(76, 76, 190, 58, "bad"), k.database(230, 52, None, "ok"), k.badge(380, 28, "lock the row", "ok"), k.badge(380, 76, "the other waits", "ok"), k.note(530, 54, "one sale, one refusal", "ok")], "Two buyers and a row lock", h=112)),
    ("Write to a log before you say yes",
     "Before changing the table, the database appends the change to the **write-ahead log** on disk. Only then does it say \"committed\". If the server dies, it replays the log on restart, so every committed order is still there.",
     _small([k.server(50, 44, None, "ok"), k.flow(80, 44, 160, 44, "acc", "1. log it"), k.database(196, 44, "log", "warn"), k.flow(224, 44, 304, 44, "ok", "2. say yes"), k.badge(380, 44, "committed", "ok"),
             k.flow(432, 44, 500, 44, "warn", "3. later", dash=True), k.database(540, 44, "table", "")], "The write-ahead log", h=112)),
]

DATA = dict(
    time="20 minutes",
    tagline="Three bad days, one lesson: a database is not a box of files. Indexes make finding fast, transactions make sharing safe, and the log makes saving permanent.",
    story=dict(
        title="Three bad days in one week",
        paras=[
            "ShopKart has a balancer, four servers and a cache. The pages are fast again, then the data starts to bite. On Monday a customer complains that \"my orders\" takes **8 seconds**. The query asks for one customer's orders, but the database reads every order the shop has ever taken, a few million rows, and throws almost all of them away.",
            "On Tuesday the last pair of limited-edition trainers sells **twice**. Two customers pressed Buy within the same second. Each request read \"stock: 1\", each decided it was fine, and each wrote \"stock: 0\". Both customers got a confirmation email, and one of them will be disappointed.",
            "On Friday there is a power cut and the server restarts. Three orders that customers had **already paid for** are missing: the early version confirmed an order before it was safely on disk. These are three different bugs with one root cause. The next sections show the three tools that fix them.",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: a database makes three promises",
        one="A **relational database** stores data in tables and promises three things: it finds rows fast (**indexes**), it keeps many users from corrupting each other's work (**transactions**), and it never loses what it said it saved (the **write-ahead log**).",
        figure=IDEA_FIG,
        paras=["Together the last two are part of the famous **ACID** guarantees: a transaction is all or nothing (atomic), leaves the data valid (consistent), does not trip over other users (isolated) and survives a crash (durable). PostgreSQL does all of this, and the experiments below use real PostgreSQL."]),
    how=HOW,
    try_intro=["Four experiments on a real PostgreSQL database. First: the query plan before and after an index. Then: a lost update reproduced and fixed. Then: killing the server on purpose to see the log bring the data back. Last: why updates make a table grow."],
    **{"try": [("pg", 1, 0, 0, "The same query before and after an index"),
               ("pg", 2, 0, 0, "A lost update, and two ways to fix it"),
               ("pg", 3, 1, 0, "Kill the server and see committed rows survive"),
               ("pg", 3, 0, 1, "Why a table grows when you update it")]},
    breaks=[
        ("A missing index", "A page that should take milliseconds takes seconds, and gets worse as the table grows. Fix: read the query plan, look for a full table scan, and add an index on the column you filter by.", "bad"),
        ("Too many indexes", "Every index is extra work on every write and extra disk space. In the practice database an index on one integer column took about an eighth of the table's size. Add indexes for the queries you really run.", ""),
        ("Read, think, then write", "Reading a value in your code, changing it, and writing it back lets two users overwrite each other. Fix: one atomic statement, a row lock, or a unique constraint that makes the second attempt fail.", "bad"),
        ("Deadlocks", "Two transactions each hold a lock the other needs, and both wait forever. The database notices and cancels one. Fix: lock rows in the same order everywhere, and keep transactions short.", ""),
        ("Bloat from old versions", "An update writes a new version of the row and keeps the old one for readers who still need it. In the experiment, 100,000 rows grew from 14 MB to 27 MB to 40 MB with no cleanup. Let vacuum run, and watch dead rows.", ""),
        ("Too many connections", "Each connection to the database costs memory, and four servers each opening many connections add up quickly. Fix: use a connection pool so a few connections are shared by many requests.", "bad"),
    ],
    real=[
        dict(company="PostgreSQL", text="The official documentation explains write-ahead logging: changes to data files are written only after the log record describing them has been flushed to permanent storage, which is what lets the database recover after a crash.", url="https://www.postgresql.org/docs/current/wal-intro.html", source="PostgreSQL documentation: Write-Ahead Logging (WAL)"),
        dict(company="PostgreSQL", text="The documentation on MVCC explains how PostgreSQL keeps several versions of a row so that readers do not block writers, which is why old versions pile up until vacuum removes them.", url="https://www.postgresql.org/docs/current/mvcc-intro.html", source="PostgreSQL documentation: Concurrency Control, Introduction"),
        dict(company="Everyone", text="Markus Winand's free guide \"Use The Index, Luke\" teaches how database indexes work and how to design them for real queries, across several database systems.", url="https://use-the-index-luke.com/", source="Use The Index, Luke"),
    ],
    interview=[dict(scenario=scen("pg", 1), who="The most reported database question: reported by candidates, not official."),
               dict(scenario=scen("pg", 2), who="A staple of tickets, hotels and inventory design questions: reported by candidates, not official."),
               dict(scenario=scen("pg", 3), who="A common depth question on durability: reported by candidates, not official.")],
    interview_sub="Say your answer aloud first, then compare with the model answer. These are the shapes of question candidates report, not official lists.",
    recap=dict(
        points=["A database makes three promises: fast lookups, safe sharing and no lost commits.",
                "An index lets a query jump to its rows; without one the database scans the whole table.",
                "Reading, changing and writing back in your code loses updates; do the change inside the database.",
                "Fixes for the last item: one atomic update, a row lock (SELECT FOR UPDATE), or a unique constraint.",
                "The write-ahead log is written first, so committed data survives a crash; it is replayed on restart.",
                "Updates keep old versions until vacuum cleans them: watch table size and dead rows."],
        quick=[("What does an index trade for faster reads?", "Extra disk space and slower writes, because every write must update the index too."),
               ("How do you stop two buyers getting the last item?", "Make the check and the update one atomic step: update stock = stock - 1 where stock > 0, or lock the row first."),
               ("Why does a committed row survive a power cut?", "The change was written to the write-ahead log on disk before the database said committed, and the log is replayed on restart.")]),
    deeper=[("Why a database and ACID", "S18_data_storage.html#l1"), ("Indexes and query plans", "S18_data_storage.html#l2"), ("Transactions and isolation", "S18_data_storage.html#l3"), ("MVCC, the log and vacuum", "S18_data_storage.html#l4"), ("Schema design and the N+1 trap", "S18_data_storage.html#l5"), ("Connections, pooling and locks", "S18_data_storage.html#l6")],
)
