"""Problem 1: Design a URL shortener."""
import sd2kit as k
from sd2 import scen, figure_of

STRIP = k.strip([
    {"title": "The long link", "kind": "warn",
     "scene": lambda cx, cy, w: k.phone(cx, cy - 6, None, "warn") + k.badge(cx, cy + 38, "shop.example.com/p/42?utm=...", "warn"),
     "caption": "A tweet allows 280 characters and a marketing link takes 300. It will not fit."},
    {"title": "The short link", "kind": "ok",
     "scene": lambda cx, cy, w: k.phone(cx, cy - 6, None, "ok") + k.badge(cx, cy + 38, "sho.rt/aZ3k9Q", "ok"),
     "caption": "Seven characters. The service remembers which long link it stands for."},
    {"title": "A million clicks", "kind": "",
     "scene": lambda cx, cy, w: k.crowd(cx, cy - 52, 5, 24, .72) + k.scaled(k.server(cx - 46, cy + 22, "redirect") + k.cache(cx + 46, cy + 22, "cache", "ok") + k.flow(cx - 14, cy + 22, cx + 18, cy + 22, "ok"), cx, cy + 22, .9),
     "caption": "Each click is one lookup. Almost all of them can be answered from memory."},
], "From a long link to a short one", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


DATA = dict(
    time="25 minutes",
    seen_at="The most common first design question",
    tagline="The classic warm-up: small enough to finish in 45 minutes, deep enough to show whether you reason from numbers or just draw boxes.",
    story=dict(
        title="A link that will not fit",
        paras=[
            "A marketing team at ShopKart wants to put a product link in a text message. The link is 300 characters of tracking parameters. The message limit is 160. They ask engineering for something like bit.ly: paste a long link, get a short one, and when anyone opens the short link they land on the long one.",
            "It sounds trivial, and the first version is: a table with two columns, a counter, a redirect. The interesting parts appear when you ask what happens at scale. What if two servers hand out the same code at the same moment? What if one link goes viral and gets a million clicks an hour? What if you need to count the clicks without slowing down the redirect?",
        ],
        strip=STRIP),
    requirements=["Functional: create a short code for a long URL; redirect from the code; optional custom alias and expiry; click statistics. Non-functional: redirects are fast and almost never down (they sit inside links people already shared); codes never collide; creating a link can be a little slower."],
    numbers=[
        ("New links per month", "100 million, about **40 writes per second** (peaks a few times higher)."),
        ("Redirects", "Reads outnumber writes about 100 to 1: **4,000 redirects per second**, peak 40,000. The read path is the hot path."),
        ("Storage", "500 bytes per record, 100 million a month, five years: about **3 TB**. A few machines, not a fleet."),
        ("Code length", "6 characters of base62 give 56.8 billion codes (47 years of supply at this rate); 7 give 3.5 trillion. **7 is plenty.**"),
        ("Cache", "Popular links dominate. Holding the hottest 5 to 20 percent in memory answers most redirects; the database sees a few hundred reads a second."),
    ],
    numbers_try=[("dw", 0, 0, 0, "Capacity, code length and storage")],
    design_figure=figure_of("dw", 0),
    design=[
        ("Create: a short code for a long URL", "The API validates the URL, takes a unique number from an ID generator, turns it into a base62 string (the code) and stores `code -> long URL`. The write path is short and cheap.",
         _small([k.person(60, 48, 1), k.flow(88, 48, 170, 48, "acc", "POST /urls"), k.server(206, 48, "API"), k.flow(236, 48, 320, 48, "acc"), k.badge(380, 48, "id 125 -> code 21", "acc"), k.flow(440, 48, 500, 48, "acc"), k.database(540, 48, "store")], "Create flow")),
        ("Redirect: the hot path", "The redirect service looks in the cache by code. On a hit it returns `302` with the long URL at once. On a miss it reads the store, fills the cache, and returns. Nothing else happens on this path.",
         _small([k.person(60, 48, 1), k.flow(88, 48, 170, 48, "acc", "GET /21"), k.server(206, 48, "redirect"), k.flow(236, 48, 320, 48, "ok"), k.cache(350, 48, "cache", "ok"), k.flow(376, 48, 470, 48, "warn", "miss", dash=True), k.database(510, 48, "store")], "Redirect flow")),
        ("Counters in ranges, so no server is a bottleneck", "Each app server leases a block of numbers (for example a million) from a tiny coordination service and hands them out locally. No call per request, no collisions, and if the coordinator is down servers keep going until their block runs out.",
         _small([k.server(70, 48, "app 1", "acc"), k.server(180, 48, "app 2", "acc"), k.server(290, 48, "app 3", "acc"), k.badge(70, 96, "1 - 1,000,000", "acc"), k.badge(180, 96, "1,000,001 - 2,000,000", "acc"), k.badge(290, 96, "2,000,001 - 3,000,000", "acc"), k.note(490, 52, "ranges leased from one small service", "acc")], "Counter ranges", h=116)),
        ("Click analytics happen later", "The redirect publishes a click event to a queue and returns immediately. A separate consumer aggregates counts by code and day. Analytics can lag by minutes; the redirect cannot.",
         _small([k.server(70, 48, "redirect"), k.flow(100, 48, 190, 48, "ok", "302 first"), k.queue(250, 48, "queue"), k.flow(296, 48, 380, 48, "acc"), k.server(420, 48, "counter"), k.flow(450, 48, 530, 48, "acc"), k.database(570, 48, "stats")], "Asynchronous analytics")),
    ],
    hard_title="The hard part: codes that never collide, and a redirect that stays fast",
    hard_paras=[
        "There are two real decisions. **How to make codes**: hashing the long URL and keeping a few characters sounds simple but collides much earlier than people expect (the birthday paradox), so you must detect and retry. A counter encoded in base62 never collides; scramble it if codes must not be guessable. **How to redirect**: `301` is cached by browsers (less load, but you lose later clicks and cannot change the target); `302` reaches you every time, so you can count and edit. Pick from the requirements, and say which.",
    ],
    **{"try": [("dw", 0, 0, 1, "Hashing collides sooner than you expect; counters never do"), ("dw", 0, 0, 2, "301 or 302: what the browser remembers")]},
    scale=[
        ("Reads at 400,000 per second", "More cache replicas with consistent hashing, a CDN or edge in front for the redirect with a short TTL, read replicas of the store.", ""),
        ("The coordinator is down", "Servers keep using their leased range. Lease generously and alert early; a range of a million lasts hours.", "ok"),
        ("A viral link (hot key)", "One key, huge traffic. Replicate the entry across cache nodes or keep it in each app server's memory for a few seconds.", ""),
        ("Abuse", "Rate limit creation, scan targets for malware and phishing, support takedown, and make private links unguessable.", "bad"),
        ("Consistency", "A creator must be able to open their new link immediately: read your own write from the primary for a few seconds.", ""),
    ],
    scenario=scen("dw", 0),
    who="The most reported cross-company question: reported by candidates, not official.",
    real=[
        dict(company="Instagram", text="Their engineering blog describes generating **64-bit IDs** from a timestamp, a logical shard id and a per-shard sequence, computed inside PostgreSQL: the same recipe as the ranges-and-Snowflake approach above.", url="https://instagram-engineering.com/sharding-ids-at-instagram-1cf5a71e5a5c", source="Instagram Engineering: Sharding and IDs at Instagram"),
        dict(company="Twitter", text="Twitter's open-sourced **Snowflake** generator packs time, machine and sequence into 64 bits so any server can mint unique, roughly time-ordered IDs without coordination.", url="https://github.com/twitter-archive/snowflake", source="twitter-archive/snowflake"),
    ],
    recap=dict(
        points=["Estimate first: ~40 writes/s, ~4,000 reads/s, ~3 TB over five years. It is a small, read-heavy, key-value system.",
                "Codes: 7 base62 characters from a counter with leased ranges. Hashing collides early; counters do not.",
                "Redirect path = cache, then store, then `302`. Nothing else runs on it.",
                "Analytics go through a queue so counting never slows the redirect.",
                "`301` saves load but hides clicks and freezes the target; `302` is the safer default.",
                "Say the failure story: coordinator down, hot link, abuse, new-link consistency."],
        quick=[("How many characters does a 7-character base62 code give?", "62^7, about 3.5 trillion codes."),
               ("Why not just hash the URL?", "Truncated hashes collide long before the space is full (birthday paradox), so you need retry logic; counters avoid it."),
               ("Why publish clicks to a queue instead of counting in the redirect?", "Counting on the redirect path adds latency and a failure mode to the hottest request.")]),
    deeper=[("URL shortener, full lesson", "S27_design_warmups.html#l1"), ("Unique ID generators", "S27_design_warmups.html#l2"), ("Caching and CDNs", "S17_caching_and_cdns.html#l1")],
)
