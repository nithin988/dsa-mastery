"""Problem 7: Design ride hailing and nearby search."""
import sd2kit as k
from sd2 import scen, figure_of

STRIP = k.strip([
    {"title": "Check everyone", "kind": "warn",
     "scene": lambda cx, cy, w: k.crowd(cx, cy - 40, 5, 24, .72, "warn") + k.badge(cx, cy + 22, "100,000 drivers", "warn") + k.note(cx, cy + 56, "56.8 ms per search", "warn"),
     "caption": "The first idea: measure the distance to every driver. It works for ten drivers, not for a city."},
    {"title": "The edge of the box", "kind": "bad",
     "scene": lambda cx, cy, w: k.person(cx, cy - 4, 1.1, "bad") + k.badge(cx - 52, cy + 38, "cell A", "bad") + k.badge(cx + 52, cy + 38, "cell B", "bad"),
     "caption": "Cut the map into boxes and look only in the rider's box. Drivers just across the line are missed."},
    {"title": "Box plus neighbours", "kind": "ok",
     "scene": lambda cx, cy, w: k.person(cx, cy - 4, 1.1, "ok") + k.badge(cx, cy + 38, "9 cells", "ok"),
     "caption": "Look in the rider's box and the eight around it. Same answer as checking everyone, far less work."},
], "From brute force to cells", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


DESIGN = k.figure(720, 250, [
    k.phone(60, 50, "driver app", "acc"), k.flow(90, 50, 170, 50, "acc", "ping every 4 s"),
    k.queue(220, 50, "location stream", "acc"), k.flow(266, 50, 346, 50, "acc"),
    k.server(386, 50, "geo service", "acc"), k.flow(416, 50, 496, 50, "acc", "update cell"),
    k.cache(540, 50, "cell index", "acc", "in memory"),
    k.person(60, 170, 1), k.flow(88, 170, 170, 170, "ok", "request"),
    k.server(206, 170, "match service", "ok"), k.flow(236, 170, 346, 170, "ok", "9 cells"),
    k.cache(386, 170, "cell index", "ok"), k.flow(416, 170, 496, 170, "ok", "top N"),
    k.server(540, 170, "ETA service", "ok"),
    k.note(360, 238, "Updates flow along the top. Searches flow along the bottom. Both use the same in memory index.", ""),
], "Ride hailing design", None)

DATA = dict(
    time="30 minutes",
    seen_at="A frequent location based design question",
    tagline="Mostly a write problem in disguise: a million moving points, and a search that must only look in the right few cells.",
    story=dict(
        title="Where is the nearest driver?",
        paras=[
            "ShopKart starts same day delivery in one city with a few hundred couriers on bikes. The first version stores each courier's last position in a database table and, for each order, computes the distance to every courier. With 300 couriers nobody notices. A year later the fleet is 100,000 and the dispatch screen takes a full minute to offer a job.",
            "Two things grew at once. Couriers send their position every few seconds, which is a stream of writes that never stops. And every order needs a search for who is closest. This is the same shape as ride hailing: how do you find the nearest moving things quickly?",
        ],
        strip=STRIP),
    requirements=["Functional: drivers report location; a rider requests a ride; the system finds nearby available drivers, offers the ride, and tracks the trip. Non-functional: a match in a few seconds, the system tolerates losing a server without losing the trip, and one driver is never matched to two riders."],
    numbers=[
        ("Location updates", "1 million active drivers each ping every 4 seconds: 1,000,000 / 4 = **250,000 updates per second**. These writes dominate."),
        ("Searches", "100,000 ride requests per minute at peak is about **1,700 searches per second**. Much less than the updates."),
        ("Data size", "Only the latest position matters: id, latitude, longitude, time, say 50 bytes each. A million drivers is **50 MB**. It fits in the memory of one machine; the trouble is the update rate, not the size."),
        ("Cell size", "In the recorded experiment, geohash precision 6 gives cells about 0.61 km by 0.97 km, and precision 7 about 0.15 km by 0.12 km. Choose a cell about the size of the search radius."),
        ("Why an index", "The recorded brute force search over 100,000 drivers took 56.8 ms and the cell index with neighbours took 2.20 ms, examining 1,789 candidates instead of 100,000."),
    ],
    numbers_try=[("sp", 3, 0, 0, "Geohash cells against brute force, measured")],
    design_figure=DESIGN,
    design=[
        ("Divide the map into cells", "A geohash turns a latitude and longitude into a short string. Nearby places share the same beginning, so a string prefix is a cell. Each driver belongs to exactly one cell at a time. Other systems use S2 or H3 cells for the same idea.",
         _small([k.badge(110, 30, "u4pruyd", "acc"), k.badge(110, 62, "u4pruye", "acc"), k.flow(190, 46, 290, 46, "acc", "same start"), k.badge(380, 46, "u4pruy = cell", "ok"), k.note(540, 50, "neighbours share a prefix", "")], "Geohash cells")),
        ("Keep the index in memory", "Store drivers in a map from cell to set of drivers. An update just rewrites the position, and moves the driver to a new set only when the cell changes. Entries expire if pings stop, so a lost phone disappears by itself.",
         _small([k.phone(60, 48, "driver", "acc"), k.flow(88, 48, 190, 48, "acc", "new position"), k.cache(230, 48, "cell u4pruy", "acc"), k.flow(258, 48, 360, 48, "warn", "crossed line", dash=True), k.cache(400, 48, "cell u4pruz", "warn"), k.note(540, 52, "expires if silent", "")], "Update the index")),
        ("Search the cell and its neighbours", "The rider's own cell is not enough, because a driver 50 metres away may sit across the line. Search the rider's cell plus the eight around it, then widen in rings until you have enough candidates. The recorded run shows the own cell alone missed 162 of 290 nearby drivers.",
         _small([k.person(60, 48, 1), k.flow(88, 48, 180, 48, "ok", "9 cells"), k.cache(220, 48, "index", "ok"), k.flow(246, 48, 340, 48, "ok", "candidates"), k.server(380, 48, "filter", "ok"), k.flow(410, 48, 500, 48, "ok", "top N"), k.badge(560, 48, "290 found", "ok")], "Neighbour search")),
        ("Rank the few, then offer with a lock", "Straight line distance is a guess. Ask a routing service for the arrival time of only the best 10 or so candidates. Offer the ride to the best one with a short lease on that driver, so no other rider can be given the same driver while the offer is open.",
         _small([k.badge(80, 48, "top 10", "ok"), k.flow(120, 48, 200, 48, "ok"), k.server(240, 48, "ETA", "ok"), k.flow(270, 48, 370, 48, "ok", "best one"), k.badge(440, 48, "lease driver 15 s", "acc"), k.flow(500, 48, 560, 48, "acc"), k.phone(590, 48, None, "acc")], "Rank and lease")),
    ],
    hard_title="The hard part: the boundary problem and the update storm",
    hard_paras=[
        "The boundary problem is that cells cut the world into hard lines. Nearness does not respect lines, so you must always search the neighbouring cells as well. The second hard part is the write rate: 250,000 updates per second. Shard the index by cell id so a search touches a few shards and each shard handles a share of the writes. Splitting a crowded cell into smaller cells (an airport, a stadium) handles hotspots.",
        "Because the index holds only the latest position and is rebuilt from the stream, it is soft state. If a shard dies, its drivers reappear on their next ping a few seconds later. That makes the design simple to run: trips and payments live in a durable database, locations live in memory.",
    ],
    **{"try": [("sp", 3, 0, 1, "The same idea in Redis: a geohash sorted set")]},
    scale=[
        ("Hot cell at an airport", "Hundreds of drivers in a small cell. Split the cell into finer ones when it holds too many, and cap how many candidates one search reads.", ""),
        ("A geo shard dies", "Its drivers reappear on the next ping. Search a wider radius for a few seconds and replicate shards for faster recovery.", "ok"),
        ("Update storm", "A network blip makes every phone resend at once. Use the queue as a buffer, drop stale updates (only the newest position matters) and apply backpressure.", ""),
        ("Two riders, one driver", "Take a lease on the driver before offering. Release it on decline or timeout, then move to the next candidate.", "bad"),
        ("Moving across shards", "A driver crossing a shard boundary is written to the new shard and removed from the old. A short double listing is harmless because the lease decides who gets the ride.", ""),
    ],
    scenario=scen("sp", 3),
    who="A frequent location question: reported by candidates, not official.",
    real=[
        dict(company="Uber", text="Uber describes **H3**, its open source hexagonal grid for dividing the world into cells, used for marketplace analysis and for finding things near a point.", url="https://h3geo.org/docs/", source="H3 documentation (open source project created at Uber)"),
    ],
    recap=dict(
        points=["It is write heavy: 250,000 location updates per second against about 1,700 searches.",
                "Keep only the latest position, in memory, keyed by cell. Entries expire if pings stop.",
                "Search the rider's cell and its eight neighbours: 290 found, same as brute force, 2.20 ms against 56.8 ms.",
                "The own cell alone missed 162 nearby drivers: the boundary problem.",
                "Rank only the top few by arrival time, then offer with a lease on the driver.",
                "Locations are soft state rebuilt from the stream; trips and payments are durable."],
        quick=[("What is the boundary problem?", "A nearby driver may sit in the next cell, so searching one cell misses them; search the neighbours too."),
               ("Why is the index in memory and not a database?", "The data is tiny but the update rate is huge, and only the latest position matters."),
               ("How do you stop two riders getting one driver?", "Take a short lease on the driver before making the offer.")]),
    deeper=[("Geospatial: geohash, grids and quadtrees", "S21_search_blob_special_stores.html#l4"), ("Sharding across machines", "S19_scaling_data.html#l4"), ("Retries and timeouts", "S22_distributed_systems.html#l5")],
)
