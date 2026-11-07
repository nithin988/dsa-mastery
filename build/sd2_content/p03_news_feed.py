"""Problem 3: Design a news feed."""
import sd2kit as k
from sd2 import scen, figure_of

STRIP = k.strip([
    {"title": "Ask the shop", "kind": "warn",
     "scene": lambda cx, cy, w: k.person(cx - 60, cy - 20, 1.1) + k.flow(cx - 36, cy - 20, cx + 20, cy - 20, "warn", "200 lists") + k.database(cx + 56, cy - 20, None, "warn") + k.note(cx, cy + 40, "read everyone you follow", "warn"),
     "caption": "ShopKart adds a Follow button. Opening the feed means fetching every followed shop's posts and sorting them, every time."},
    {"title": "Ready in advance", "kind": "ok",
     "scene": lambda cx, cy, w: k.person(cx - 60, cy - 20, 1.1) + k.flow(cx - 36, cy - 20, cx + 20, cy - 20, "ok", "1 list") + k.cache(cx + 56, cy - 20, None, "ok") + k.note(cx, cy + 40, "a feed built per person", "ok"),
     "caption": "Instead, each new post is copied into every follower's own list. Reading is one cheap lookup."},
    {"title": "The huge account", "kind": "bad",
     "scene": lambda cx, cy, w: k.crowd(cx, cy - 56, 5, 26, .66, "bad") + k.alert(cx, cy + 10, None) + k.badge(cx, cy + 56, "800,000 copies", "bad"),
     "caption": "One account with 800,000 followers posts once and triggers 800,000 writes. That is the celebrity problem."},
], "From a slow feed to a celebrity post", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


DESIGN = k.figure(720, 190, [
    k.person(50, 70, 1.1), k.flow(76, 70, 120, 70, "acc", "post"),
    k.server(160, 70, "post service"), k.flow(190, 70, 250, 70, "acc"),
    k.database(285, 70, "posts", "acc"), k.flow(160, 100, 160, 130, "acc"),
    k.queue(160, 150, "fan-out queue", "", None, 3), k.flow(206, 150, 290, 150, "acc", "batches"),
    k.server(330, 150, "workers", "acc"), k.flow(360, 150, 430, 120, "acc", "push id"),
    k.cache(470, 100, "feed lists", "ok"), k.flow(498, 100, 560, 70, "ok", "1 read"),
    k.person(600, 66, 1.1), k.flow(560, 130, 520, 110, "warn", "celebrity: skip", dash=True),
    k.note(630, 150, "celebrity posts are merged", "warn"), k.note(630, 168, "in at read time", "warn"),
], "News feed design", None)

DATA = dict(
    time="30 minutes",
    seen_at="Often reported for social and messaging companies",
    tagline="The feed question is really one decision: do the work when someone posts, or when someone reads? Strong answers measure both and handle the account everyone follows.",
    story=dict(
        title="The Follow button",
        paras=[
            "ShopKart adds a Follow button so customers can see new products from their favourite sellers. The first version is honest and simple: when you open your feed, the app looks up everyone you follow, fetches their latest posts and sorts them by time. It works in testing.",
            "Then a popular seller reaches 800,000 followers and a customer follows 200 accounts. Opening the feed now means reading 200 lists and merging them, thousands of times a second. The team flips the idea around: build each person's feed ahead of time. That fixes reading, and creates a new problem the first time the huge seller posts.",
        ],
        strip=STRIP),
    requirements=["Functional: publish a post; show a feed of posts from the accounts you follow, newest or ranked first, with pages. Non-functional: opening the feed is fast (tens of milliseconds); a new post appears within seconds; the feed survives accounts with millions of followers; it is fine if a feed is a few seconds stale."],
    numbers=[
        ("Assumptions", "300 million users, 200 million active a day, 500 million posts a day, 200 followers on average, 20 feed opens per active user per day. Treat them as the interviewer's numbers to confirm."),
        ("Posts", "500 million / 86,400 seconds is about **5,800 writes per second** (peak around 15,000)."),
        ("Feed reads", "200 million x 20 / 86,400 is about **46,000 reads per second** (peak around 150,000). Reads outnumber posts about 8 to 1."),
        ("Fan-out on write", "500 million posts x 200 followers is **100 billion list insertions a day**, about 1.2 million per second. This is the number that forces a decision."),
        ("Feed storage", "Keep about 800 post ids per user at 8 bytes: **6.4 KB each**. For 200 million active users that is about 1.3 TB in memory with replication."),
    ],
    numbers_try=[("fd", 0, 0, 0, "Write amplification on a skewed follower graph")],
    design_figure=DESIGN,
    design=[
        ("Publish: store once, then spread", "The post service saves the post and puts an event on a queue. Workers read the event, look up the author's followers and add the post id to each follower's feed list. The author never waits for the spreading.",
         _small([k.person(50, 48, 1), k.flow(76, 48, 130, 48, "acc", "post"), k.server(160, 48, "post svc"), k.flow(190, 48, 245, 48, "acc"), k.queue(300, 48, "event", "", None, 3), k.flow(346, 48, 410, 48, "acc"), k.server(440, 48, "workers"), k.flow(470, 48, 530, 48, "ok", "LPUSH"), k.cache(570, 48, "feeds", "ok")], "Publish and fan-out")),
        ("Read: one list, then fill in the details", "Opening the feed fetches one short list of ids from the feed cache, then loads each post and author from caches. Reading never touches the follow graph, which is why it is fast.",
         _small([k.person(50, 48, 1), k.flow(76, 48, 140, 48, "acc", "open feed"), k.cache(170, 48, "feed list", "ok"), k.flow(200, 48, 300, 48, "ok", "20 ids"), k.server(330, 48, "hydrate"), k.flow(360, 48, 440, 48, "acc"), k.database(480, 48, "posts"), k.note(580, 52, "cursor for next page", "acc")], "Feed read")),
        ("Celebrities are pulled, not pushed", "Above a follower threshold, a post is not copied anywhere. When a follower opens the feed, the app also fetches the latest posts of the few big accounts they follow and merges them in. A post costs a few extra reads instead of millions of writes.",
         _small([k.person(50, 48, 1), k.flow(76, 48, 130, 48, "acc"), k.cache(160, 48, "own list", "ok"), k.flow(186, 48, 250, 48, "ok", "merge"), k.badge(330, 48, "by time or score", "acc"), k.flow(390, 48, 450, 48, "warn", "+ big accounts", dash=True), k.database(500, 48, "celebrity posts", "warn")], "Hybrid read")),
        ("Ranking comes last", "Take a few hundred candidate posts, score each with signals like recency and past interaction, and return the top page. Keep the scorer separate so the feed still works if it is slow: fall back to newest first.",
         _small([k.badge(80, 48, "300 candidates", "acc"), k.flow(150, 48, 220, 48, "acc", "score"), k.server(250, 48, "ranker"), k.flow(280, 48, 360, 48, "acc"), k.badge(420, 48, "top 20", "ok"), k.flow(465, 48, 540, 48, "warn", "slow?", dash=True), k.badge(590, 48, "newest first", "warn")], "Ranking with a fallback")),
    ],
    hard_title="The hard part: the account everyone follows",
    hard_paras=[
        "Pushing every post is cheap for most accounts and ruinous for a few. The measured experiment above shows the shape: most accounts have a handful of followers and a few have hundreds of thousands. A hybrid rule sends posts from small accounts to followers' lists and pulls the big ones at read time.",
        "The threshold is a tuning knob, not a law. Set it by measuring write cost against extra read cost, and say so. Also skip inactive users when pushing: a person who has not opened the app in a month does not need a fresh list.",
    ],
    **{"try": [("fd", 0, 0, 2, "Real Redis: the cost of one post, and one feed read")]},
    scale=[
        ("A celebrity posts", "Do not fan out. Pull at read time, or push in low priority batches to active followers only.", ""),
        ("Fan-out workers fall behind", "The queue grows and new posts show up late. Alert on the age of the oldest event and add workers; feeds are stale, not wrong.", "bad"),
        ("A feed cache node dies", "Rebuild a user's list on demand from the follow graph and recent posts. Slower for that user once, then cached again.", "ok"),
        ("Deleted or private posts", "Feed lists hold ids only, so check each post when hydrating and drop the ones that are gone or hidden.", ""),
        ("A new follow or unfollow", "Backfill a few recent posts from the new account into the follower's list, and remove an unfollowed account's posts lazily on read.", ""),
    ],
    scenario=scen("fd", 0),
    who="A staple social feed question: reported by candidates, not official.",
    real=[
        dict(company="Twitter", text="A 2012 QCon talk by Raffi Krikorian, then Twitter's head of platform engineering, describes the timeline architecture in terms of a write path that fans tweets out into per-user timelines and a read path that serves them.", url="https://www.infoq.com/presentations/Twitter-Timeline-Scalability", source="InfoQ: Timelines at Scale (video)"),
    ],
    recap=dict(
        points=["Decide first: work on write (fan-out on write) or work on read (fan-out on read).",
                "Numbers: about 46,000 feed reads a second but 100 billion list writes a day if you push everything.",
                "Push builds a ready list per user, so reading is one lookup.",
                "Huge accounts break pure push: one post means hundreds of thousands of writes.",
                "Hybrid: push for ordinary accounts, pull the big ones at read time.",
                "Feed lists hold ids only; hydrate from caches and check deleted posts then."],
        quick=[("Why not compute the feed at read time for everyone?", "A reader following 200 accounts would trigger 200 list fetches and a merge on every open, which is too much for 46,000 reads a second."),
               ("What is the celebrity problem?", "Pushing one post to every follower of a huge account causes hundreds of thousands of writes at once, so those accounts are pulled at read time."),
               ("What does a feed list store?", "Only post ids, capped at a few hundred, so memory stays small and posts are loaded from caches on read.")]),
    deeper=[("News feed, full lesson", "S28_feeds_chat_notifications.html#l1"), ("Queues and async work", "S20_queues_streams_async.html#l1"), ("Caching and CDNs", "S17_caching_and_cdns.html#l1")],
)
