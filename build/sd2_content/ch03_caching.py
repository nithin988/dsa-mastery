"""Chapter 3: Make it fast (caching and CDNs)."""
import sd2kit as k
from sd2 import scen

# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "Day 1", "kind": "",
     "scene": lambda cx, cy, w: k.crowd(cx, cy - 52, 2, 34, .85) + k.scaled(k.server(cx - 46, cy + 22, "web") + k.database(cx + 46, cy + 22, "database", "ok") + k.flow(cx - 14, cy + 22, cx + 18, cy + 22, "ok"), cx, cy + 22, .9),
     "caption": "Ten visitors an hour. Every page asks the database six questions. Nobody notices."},
    {"title": "Black Friday", "kind": "bad",
     "scene": lambda cx, cy, w: k.crowd(cx, cy - 52, 5, 24, .72, "bad") + k.scaled(k.server(cx - 46, cy + 22, "web", "warn") + k.database(cx + 46, cy + 22, "database", "bad") + k.flow(cx - 14, cy + 22, cx + 18, cy + 22, "bad") + k.badge(cx + 46, cy + 86, "CPU 96%", "bad"), cx, cy + 22, .9),
     "caption": "5,000 visitors a minute ask the same six questions. The database is overwhelmed and the site stops."},
    {"title": "With a cache", "kind": "ok",
     "scene": lambda cx, cy, w: k.crowd(cx, cy - 52, 5, 24, .72, "ok") + k.scaled(k.server(cx - 66, cy + 22, "web", "ok") + k.cache(cx, cy + 22, "cache", "ok") + k.database(cx + 66, cy + 22, "database", "ok") + k.flow(cx - 36, cy + 22, cx - 28, cy + 22, "ok") + k.flow(cx + 28, cy + 22, cx + 38, cy + 22, "warn", dash=True), cx, cy + 22, .78),
     "caption": "95 of every 100 answers come from memory in about a millisecond. The database finally relaxes."},
], "ShopKart's product page, three moments", "The same shop on three days: nothing changed except where the answers come from.")

IDEA_FIG = k.figure(720, 266, [
    k.person(60, 80, 1.25), k.note(60, 130, "Customer"),
    k.flow(94, 80, 166, 80, "acc"),
    k.server(200, 78, "Web server"),
    k.flow(234, 78, 316, 78, "acc", "1. ask"),
    k.cache(350, 78, "Cache", "ok", "memory, ~0.1 ms"),
    k.badge(350, 166, "HIT: 95 of 100", "ok"),
    k.flow(384, 78, 484, 78, "warn", "2. miss", dash=True),
    k.database(520, 78, "Database", "", "disk, ~10 ms"),
    k.badge(520, 166, "MISS: 5 of 100", "warn"),
    '<path class="sd-a warn" d="M520,179 V206 H350 V183" fill="none" marker-end="url(#dga)"/>',
    k.note(435, 226, "3. save the answer for next time", "warn"),
    k.note(360, 254, "A hit never touches the database. A miss pays once; then the next hundred visitors get a hit.", ""),
], "Cache-aside: ask the cache first, the database only on a miss", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


HOW = [
    ("Look in the cache first",
     "Every question has a **key**, such as `product:42`. The web server asks the cache for that key before anything else. Memory is about a hundred times faster than disk.",
     _small([k.server(60, 44, None), k.flow(90, 44, 190, 44, "acc", "ask for product:42"), k.cache(226, 44, "cache"), k.flow(254, 44, 360, 44, "ok", "found"),
             k.badge(430, 44, "return it", "ok"), k.note(560, 48, "no database call", "ok")], "Lookup in the cache by key", h=100)),
    ("On a miss, ask the database, then remember the answer",
     "If the key is not there (never asked, expired, or pushed out), read the database **once**, save the answer in the cache, and return it. This is called **cache-aside**, and it is the pattern most real systems use.",
     _small([k.cache(60, 44, "cache", "warn"), k.flow(90, 44, 170, 44, "warn", "miss"), k.database(210, 44, "database"), k.flow(240, 44, 340, 44, "ok", "answer"),
             k.cache(380, 44, "cache", "ok"), k.badge(480, 44, "now stored", "ok"), k.note(580, 48, "next one hits", "ok")], "Cache-aside on a miss", h=104)),
    ("Decide how long to remember",
     "A cached answer can go stale. Give every entry a **time to live (TTL)** as a safety net, and **delete the entry whenever you change the data**, so the next read refills it with the new value. When memory is full, the cache throws away the least recently used entries.",
     _small([k.clock(60, 40, "TTL 5 min"), k.note(150, 44, "expires by itself", "acc", "start"), k.person(330, 40, .95), k.flow(352, 40, 430, 40, "warn", "write"), k.database(480, 40, "database"),
             k.note(320, 104, "after every write: update the database, then DELETE the cache entry", "warn")], "Expiry and invalidation", h=116)),
    ("Protect the database from the crowd",
     "When a very popular entry expires, thousands of requests miss together and all ask the database at once: a **stampede**. Let **one** request rebuild it while the others wait, spread the expiry times with a little random jitter, and cache \"not found\" for missing keys.",
     _small([k.crowd(70, 40, 4, 24, .7, "bad"), k.flow(130, 40, 210, 40, "bad", "1,000 misses"), k.alert(240, 40, None), k.flow(270, 40, 350, 40, "ok"), k.badge(450, 40, "one rebuilds, the rest wait", "ok"), k.note(450, 90, "a lock with an expiry (SET NX)", "ok")], "Stampede protection", h=108)),
]

DATA = dict(
    time="15 minutes",
    tagline="Why a tiny amount of memory in front of the database is the cheapest speed-up in system design, and why it is also the source of the most confusing bugs.",
    story=dict(
        title="Black Friday, 9:02 a.m.",
        paras=[
            "ShopKart is two years old and doing fine. Every product page makes six database queries: the product, its photos, the price, stock, reviews and related items. With a few hundred visitors an hour nobody cares.",
            "Then Black Friday starts. At 9:02 the pager goes off: the site is crawling, then failing. The web servers are bored (CPU 15%). The database is at 96% and its queue is growing. Pages that took 80 milliseconds now take eight seconds, and customers are leaving.",
            "The senior engineer looks at the query log and sees something odd: **the same six queries, over and over, for the same forty popular products**. The database is working very hard to give the same answers it gave a second ago. The fix is not a bigger database. It is a place to remember answers.",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: remember the answer",
        one="A **cache** is a small, fast place that remembers answers you already worked out, so the next person who asks does not make the slow system do the work again.",
        figure=IDEA_FIG,
        paras=["It works because real traffic is **lopsided**: a few items get most of the requests. Remembering only the hottest 5 to 20 percent of items can answer 70 to 90 percent of requests. Caches exist at every level (browser, CDN, web server, Redis, the database's own memory), and a request stops at the first level that has the answer."]),
    how=HOW,
    try_intro=["Three experiments, each a few lines of code you can run and change. First: what does a cache actually save? Then: why stale data appears, and the fix. Then: what a stampede looks like, and how one lock stops it."],
    **{"try": [("cache", 0, 0, 2, "What does a cache actually save?"), ("cache", 1, 0, 0, "Why stale data appears, and the fix"), ("cache", 3, 0, 0, "A stampede, and how one lock stops it")]},
    breaks=[
        ("Stale data", "The database changed and the cache still holds the old answer. Fix: delete the entry on every write, and keep a TTL as a safety net. Never cache what must be exactly current (balances, checkout stock).", ""),
        ("Stampede", "A hot entry expires and a thousand requests rebuild it together. Fix: one request rebuilds under a lock, TTLs get random jitter, the hottest keys refresh ahead of expiry.", "bad"),
        ("Missing keys", "Requests for things that do not exist always miss and always reach the database (a bug or an attack). Fix: cache \"not found\" for a short time, validate input.", ""),
        ("Cold start", "After a restart the cache is empty and the database takes the full load. Fix: warm it before taking traffic, restart nodes gradually, and rate limit as a backstop.", ""),
        ("Too small", "Memory fills, hot entries are evicted, and the hit ratio falls from 95% to 60%: the database load jumps eight-fold. Fix: size from the hot set, watch evictions and hit ratio.", "bad"),
    ],
    real=[
        dict(company="Facebook", text="The paper on scaling memcache describes a **lease** mechanism: when a popular key is invalidated, only one client gets permission to refill it, which prevents a thundering herd and also stops stale values being written back.", url="https://www.usenix.org/conference/nsdi13/technical-sessions/presentation/nishtala", source="Scaling Memcache at Facebook (NSDI 2013)"),
        dict(company="Netflix", text="Netflix has written about **EVCache**, a distributed in-memory cache built on memcached and replicated across zones, used so that most reads never reach the persistent stores.", url="https://netflixtechblog.com/caching-for-a-global-netflix-7bcc457012f1", source="Netflix Tech Blog: Caching for a Global Netflix"),
        dict(company="Everyone", text="Browsers and CDNs apply the same idea to web content: `Cache-Control`, `ETag` and `304 Not Modified` let copies near the user be reused safely.", url="https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching", source="MDN: HTTP caching"),
    ],
    interview=[dict(scenario=scen("cache", 6), who="A common system design prompt: reported by candidates at large tech companies, not official."),
               dict(scenario=scen("cache", 3), who="A frequent follow-up to \"I would add a cache\": reported by candidates, not official."),
               dict(scenario=scen("cache", 1), who="A frequent probing question about consistency: reported by candidates, not official.")],
    interview_sub="Say your answer aloud first, then compare with the model answer. Companies are not published official lists; these are the shapes of question candidates report.",
    recap=dict(
        points=["A cache remembers answers so the slow system does not repeat work; traffic is lopsided, so a small cache helps a lot.",
                "Cache-aside: look in the cache, on a miss read the database and fill the cache.",
                "Staleness is bounded by a TTL and fixed by deleting the entry on every write.",
                "Hit ratio is the number to watch: 95% means the database sees one request in twenty.",
                "The hard problems are stampedes, missing keys, cold starts and eviction thrash: each has a one-line fix.",
                "Never cache what must be exactly current, and always say what happens when the cache fails."],
        quick=[("What does a 95% hit ratio mean for the database?", "It sees 5 requests for every 100: a twenty-fold reduction in load."),
               ("How do you keep a cache from serving stale data?", "Delete the entry whenever the data changes, and give every entry a TTL as a safety net."),
               ("What is a cache stampede and the simplest fix?", "Many requests rebuild an expired hot entry together; let one rebuild under a lock while the others wait.")]),
    deeper=[("Why caching works", "S17_caching_and_cdns.html#l1"), ("Caching patterns", "S17_caching_and_cdns.html#l2"), ("Eviction", "S17_caching_and_cdns.html#l3"), ("Stampedes and hard problems", "S17_caching_and_cdns.html#l4"), ("HTTP caching and CDNs", "S17_caching_and_cdns.html#l6"), ("Sizing a cache", "S17_caching_and_cdns.html#l7")],
)
