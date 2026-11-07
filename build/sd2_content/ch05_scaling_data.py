"""Chapter 5: When one database is not enough (replication, failover, partitioning, sharding, NoSQL)."""
import sd2kit as k
from sd2 import scen

# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "Year 1", "kind": "",
     "scene": lambda cx, cy, w: k.crowd(cx, cy - 52, 2, 34, .85) + k.scaled(k.database(cx, cy + 22, "one database", "ok") + k.badge(cx, cy + 74, "disk 12% full", "ok"), cx, cy + 22, .95),
     "caption": "One database holds every order and answers every question. There is plenty of room."},
    {"title": "Year 3, Black Friday", "kind": "bad",
     "scene": lambda cx, cy, w: k.crowd(cx, cy - 52, 5, 24, .72, "bad") + k.scaled(k.database(cx, cy + 22, "one database", "bad") + k.badge(cx, cy + 74, "disk 94% full", "bad"), cx, cy + 22, .95),
     "caption": "Orders doubled twice. Even with the cache, every write queues behind one machine."},
    {"title": "Many machines", "kind": "ok",
     "scene": lambda cx, cy, w: k.crowd(cx, cy - 52, 5, 24, .72, "ok") + k.scaled(k.database(cx - 66, cy + 22, "shard A", "ok") + k.database(cx, cy + 22, "shard B", "ok") + k.database(cx + 66, cy + 22, "shard C", "ok") + k.badge(cx, cy + 74, "each holds a slice", "ok"), cx, cy + 22, .78),
     "caption": "The data is split into slices, and each slice has a spare copy. No machine holds it all."},
], "ShopKart's database, three moments", "The same shop in year 1, at the breaking point, and after the data was split up.")

IDEA_FIG = k.figure(720, 292, [
    k.note(10, 14, "Copies (replication): the same data on more machines", "acc", "start"),
    k.server(60, 62, "App"),
    k.flow(90, 56, 196, 56, "acc", "writes"),
    k.database(230, 56, "Primary", "ok"),
    k.flow(260, 56, 366, 56, "warn", "copies changes", dash=True),
    k.database(400, 56, "Replica 1"),
    k.database(540, 56, "Replica 2"),
    '<path class="sd-a warn dash" d="M230,30 V22 H540 V30" fill="none" marker-end="url(#dga)"/>',
    k.note(360, 124, "Reads can go to any copy. More readers and a spare if one dies, but a copy can be behind.", "", "middle"),
    k.note(10, 150, "Slices (sharding): different data on different machines", "acc", "start"),
    k.balancer(90, 218, "Router"),
    k.flow(116, 218, 266, 218, "acc", "id 1 to 3"),
    '<path class="sd-a acc" d="M90,194 V176 H430 V194" fill="none" marker-end="url(#dga)"/>',
    '<path class="sd-a acc" d="M90,194 V164 H590 V194" fill="none" marker-end="url(#dga)"/>',
    k.database(300, 218, "Shard A"), k.database(430, 218, "Shard B"), k.database(590, 218, "Shard C"),
    k.note(360, 284, "More writers and more room, but a question that spans slices gets harder.", ""),
], "Replication copies the data, sharding splits it", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


HOW = [
    ("Copy the data to replicas",
     "A **replica** is a second database that receives every change from the **primary** and applies it. Send writes to the primary and spread reads across the replicas. Copying takes a moment, so a replica can be **behind** (this gap is called replication lag).",
     _small([k.database(60, 44, "primary", "ok"), k.flow(90, 44, 250, 44, "warn", "copy of each change", dash=True), k.database(284, 44, "replica"),
             k.flow(470, 44, 316, 44, "acc", "read"), k.person(500, 44, .95), k.badge(580, 44, "2 s behind", "warn"),
             k.note(320, 112, "Writes go to the primary only. Reads can go to either.", "")], "A primary copying to a replica", h=126)),
    ("Plan for the primary to die",
     "If the primary dies, **promote** a replica to take its place. This is called **failover**. The danger is the old primary waking up and accepting writes too: two machines both think they are in charge, called **split brain**. So you must shut the old one out (fence it).",
     _small([k.database(60, 44, "old primary", "bad"), k.flow(90, 44, 190, 44, "warn", "promote"), k.database(226, 44, "replica", "ok"),
             k.database(420, 44, "old one wakes", "warn"), k.flow(452, 44, 508, 44, "bad"), k.alert(540, 44, "split brain"),
             k.note(320, 112, "Fence the old primary so it can never accept a write again.", "bad")], "Failover and split brain", h=124)),
    ("Split a big table, then split the database",
     "**Partitioning** cuts one huge table into pieces (for example one per month) inside one database. Old months can be dropped almost instantly. **Sharding** goes further and puts different pieces on different machines, chosen by a **shard key** such as the user id.",
     _small([k.database(60, 44, "events table"), k.flow(90, 44, 190, 44, "acc", "by month"),
             k.badge(240, 44, "Jan", "acc"), k.badge(292, 44, "Feb", "acc"), k.badge(344, 44, "Mar", "acc"),
             k.flow(378, 44, 458, 44, "acc", "by user id"), k.database(500, 44, "shard A"), k.database(590, 44, "shard B"),
             k.note(320, 108, "Partitions: one machine. Shards: many machines.", "")], "Partitioning versus sharding", h=120)),
    ("Choose the key, and expect to grow",
     "A good shard key spreads **load** and **data** evenly and keeps what you ask together on one shard. When you add a shard, a plain \"key mod number of shards\" moves most of the data, while **consistent hashing** moves only what the new shard must own.",
     _small([k.database(50, 44, "3 shards"), k.flow(78, 44, 150, 44, "acc", "add a 4th"),
             k.badge(250, 44, "mod N: 75% move", "bad"), k.badge(470, 44, "consistent hashing: 27% move", "ok"),
             k.note(320, 104, "The ideal is 25%: only the keys the new shard now owns.", "")], "Resharding cost", h=116)),
]

DATA = dict(
    time="18 minutes",
    tagline="What to do when one database machine is too small, too busy or too risky: make copies for reads and safety, make slices for writes and size, and know what each costs you.",
    story=dict(
        title="Black Friday, year three",
        paras=[
            "ShopKart has grown. The cache from chapter 3 keeps product pages fast, and the indexes and transactions from chapter 4 keep orders correct. But orders have doubled two years in a row. The order database is one machine, and it is now 94% full.",
            "On Black Friday the cache cannot help, because every order is a **write**, and a cache only helps reads. Writes queue behind a single disk. Checkout slows to a crawl. The team adds a read copy to take the browsing load, and the next morning support has a new problem: customers save a new address, reload the page and see the old one.",
            "Both problems have the same root. **One machine is doing everything**: holding all the data, taking all the writes, and being the only copy. The way out is to spread the data over many machines, and each way of doing it brings a new problem to manage.",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: copies for safety and reads, slices for writes and size",
        one="You can spread a database in two ways. **Replication** keeps the *same* data on several machines. **Sharding** puts *different* data on different machines. Most real systems use both.",
        figure=IDEA_FIG,
        paras=[
            "Copies help with reads and survival but do nothing for write volume, because every copy must still apply every write. Slices help with writes and total size, but they make questions across slices harder.",
            "There is also a third option: pick a database built to spread out from day one. Many **NoSQL** stores (key-value, document and wide-column stores) are. They fit when you look things up by a key, need huge write volume, and can live without joins and multi-row transactions. They are a trade, not an upgrade. If PostgreSQL can still carry you, it usually should.",
        ]),
    how=HOW,
    try_intro=["Four experiments on a real PostgreSQL primary and replica, and real routing code. First: how stale can a replica be? Then: what split brain looks like. Then: why plain modulo makes growing painful, and what a bad shard key does."],
    **{"try": [("sd", 0, 0, 2, "How stale can a replica be?"),
               ("sd", 1, 0, 1, "Failover and a split brain"),
               ("sd", 3, 0, 2, "Adding a shard: modulo against consistent hashing"),
               ("sd", 3, 0, 3, "A hot shard from a bad key")]},
    breaks=[
        ("Reading your own write", "A user saves, then reads from a replica that has not caught up, and sees old data. Fix: for a few seconds after a write, read that user's data from the primary, or read from a replica only once it has reached the write.", "bad"),
        ("Split brain", "After a failover the old primary comes back and two nodes accept writes, so the data forks. Fix: fence the old primary, and let only a majority vote decide who leads (chapter 7).", "bad"),
        ("Hot shard", "One key gets most of the traffic (one huge customer, one celebrity), so one shard is busy while the others sit idle. Fix: choose a key that spreads load, or split the big key across several shards.", ""),
        ("Queries across shards", "A join or a report that spans shards must ask all of them and combine the answers, and a transaction across two shards is hard. Fix: choose the key so most queries touch one shard, and keep cross-shard work rare.", ""),
        ("Resharding pain", "Adding a shard to a plain \"key mod N\" layout moves about three quarters of the data. Fix: consistent hashing or many small virtual shards that you move one at a time.", ""),
        ("NoSQL by fashion", "Choosing a document or key-value store only because it \"scales\" and then needing joins, reports and transactions. Fix: start from the access patterns, and keep the relational database until you can name what it cannot do.", ""),
    ],
    real=[
        dict(company="Amazon", text="The Dynamo paper describes a key-value store that spreads keys over nodes with **consistent hashing**, keeps several copies of each key, and uses quorum reads and writes, accepting that copies can briefly disagree in exchange for staying available.", url="https://www.allthingsdistributed.com/2007/10/amazons_dynamo.html", source="Dynamo: Amazon's Highly Available Key-value Store (SOSP 2007)"),
        dict(company="Vitess", text="The Vitess project describes itself as a database clustering system for horizontally scaling MySQL, and it handles the routing and resharding work that teams otherwise build by hand.", url="https://vitess.io/docs/", source="Vitess documentation"),
    ],
    interview=[dict(scenario=scen("sd", 0), who="A common database scaling prompt: reported by candidates at large tech companies, not official."),
               dict(scenario=scen("sd", 1), who="A frequent probe after \"I would add a replica\": reported by candidates, not official."),
               dict(scenario=scen("sd", 3), who="A frequent follow-up when writes are the bottleneck: reported by candidates, not official.")],
    interview_sub="Say your answer aloud first, then compare with the model answer. These are the shapes of question candidates report, not official company lists.",
    recap=dict(
        points=["Replication keeps the same data on more machines: more reads and a spare, but copies can lag.",
                "Read your own writes from the primary, or the user sees old data.",
                "Failover promotes a replica; fence the old primary or you get split brain.",
                "Partitioning splits a table inside one database; sharding splits the data across machines by a shard key.",
                "A good shard key spreads load and keeps common queries on one shard; consistent hashing makes growing cheap.",
                "Choose NoSQL for access patterns you can name (lookup by key, huge writes), not for fashion."],
        quick=[("A user saves, reloads and sees old data after you added replicas. Why?", "The replica is behind the primary (replication lag). Read that user's data from the primary for a short time after they write."),
               ("What is split brain and how do you prevent it?", "Two nodes both accept writes as primary. Fence the old primary and require a majority vote for leadership."),
               ("Why not shard by key mod N?", "Adding a shard moves most of the keys (75% in the experiment). Consistent hashing moves only about a quarter.")]),
    deeper=[("Replication and lag", "S19_scaling_data.html#l1"), ("Failover and split brain", "S19_scaling_data.html#l2"), ("Partitioning", "S19_scaling_data.html#l3"), ("Sharding", "S19_scaling_data.html#l4"), ("NoSQL stores", "S19_scaling_data.html#l5"), ("Choosing and sizing", "S19_scaling_data.html#l6")],
)
