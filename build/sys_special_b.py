"""S21 search, blob and specialised stores: part B (lesson 4: geospatial) and the module tail."""
import sysviz as v

GEO_VIZ = v.figure(
    720, 236,
    [v.box(10, 20, 330, 150, "Geohash: a string per grid cell", "acc", ""),
     v.text(175, 52, "u4pruyd  (about 150 m cell)", "dg-s"), v.text(175, 78, "u4pruy   (about 1 km)", "dg-s"), v.text(175, 104, "u4pru    (about 5 km)", "dg-s"), v.text(175, 130, "shared prefix = nearby (mostly)", "dg-s"),
     v.box(380, 20, 330, 150, "The boundary problem", "bad", ""),
     v.text(545, 52, "two points 10 m apart can sit in", "dg-s"), v.text(545, 78, "different cells with different prefixes", "dg-s"), v.text(545, 104, "so search the cell AND its 8 neighbours", "dg-s"), v.text(545, 130, "then filter by true distance", "dg-s"),
     v.text(360, 206, "Quadtrees, S2 and H3 cells solve the same problem with different shapes and adaptive sizes.", "dg-s")],
    "Geospatial indexing with geohash", "Turn two-dimensional proximity into a one-dimensional index that databases already handle")

LESSONS_B = [
    dict(
        title="Geospatial: finding what is near a point (geohash, grids and quadtrees)",
        tier="hot",
        situation="\"Find the 10 nearest drivers\" cannot be answered by computing the distance to every driver. A database index on latitude and on longitude separately does not help either: nearness is two-dimensional. Spatial indexes turn proximity into something an ordinary index can search.",
        learn=["Why separate lat and lon indexes fail", "Geohash and grid cells: a string prefix per area", "The boundary problem and searching neighbour cells", "Quadtrees, S2 and H3, and a choice for moving objects"],
        model=[
            "To find points **near** a location you need a **spatial index**. Computing the distance to every point is O(n); two separate B-tree indexes (latitude, longitude) each select a **band** across the whole world, and intersecting two huge bands is no better. The standard trick is to **divide the world into cells** and index points by cell: a **geohash** interleaves the bits of latitude and longitude into a base-32 string where each extra character is a smaller cell (about 5 km, 1 km, 150 m, ...) and **nearby points usually share a prefix**, so a plain string index with a `LIKE 'u4pr%'` or an equality on the cell answers \"which points are in this cell\". Other cell systems: fixed **grids**, **quadtrees** (recursively split a cell into four when it holds too many points, adapting to density), Google **S2** and Uber **H3** (cells on a sphere with uniform neighbours).",
            "The catch is the **boundary problem**: two points a few metres apart can fall in **different cells** (even different prefixes). So a proximity search queries the **cell containing the point and its eight neighbours**, then **filters by the true distance** (haversine) and sorts. Choose the cell size to match the radius you search. For **moving objects** (drivers) the index changes constantly: keep positions in an **in-memory** structure (Redis geo commands use a geohash-encoded sorted set), update on each location ping, and expire stale entries; for **static places** (restaurants) a database index (PostGIS, or a geohash column) is enough. At large scale, **shard by cell** so that nearby queries touch few shards, and watch hot cells (a stadium after a game).",
        ],
        analogy="A city divided into postcodes: to find shops near you, you look at your postcode and the neighbouring ones rather than every shop in the country. The trap is the street that runs along a postcode boundary: a shop across the road has a different postcode, so you must also look next door.",
        visual=[GEO_VIZ],
        sim=None,
        walk=[
            ("Choose a cell size from the search radius", "A search radius of about 1 km suggests cells of about 1 km."),
            ("Index points by their cell", "Compute the cell key on write; store or update it."),
            ("Query the cell and its neighbours", "Nine cells cover the boundary cases."),
            ("Filter by true distance and rank", "Haversine distance, then sort and limit."),
            ("Scale and keep moving objects fresh", "In-memory index with expiry; shard by cell; handle hot cells."),
        ],
        groups=[
            dict(title="A geohash index you can test against brute force", cmds=[
                dict(volatile=True, c=r'''mkdir -p ~/spec && cd ~/spec && python3 - <<'EOF'
import math, random, time
from collections import defaultdict
B32 = '0123456789bcdefghjkmnpqrstuvwxyz'
def encode(lat, lon, precision):
    lat_r, lon_r, bits, even, h, ch = [-90.0, 90.0], [-180.0, 180.0], 0, True, '', 0
    while len(h) < precision:
        rng, val = (lon_r, lon) if even else (lat_r, lat)
        mid = (rng[0] + rng[1]) / 2
        if val >= mid: ch = (ch << 1) | 1; rng[0] = mid
        else: ch <<= 1; rng[1] = mid
        even = not even; bits += 1
        if bits == 5: h += B32[ch]; bits = 0; ch = 0
    return h
def decode_center(h):
    lat_r, lon_r, even = [-90.0, 90.0], [-180.0, 180.0], True
    for c in h:
        v = B32.index(c)
        for b in range(4, -1, -1):
            rng = lon_r if even else lat_r; mid = (rng[0] + rng[1]) / 2
            if (v >> b) & 1: rng[0] = mid
            else: rng[1] = mid
            even = not even
    return (lat_r[0] + lat_r[1]) / 2, (lon_r[0] + lon_r[1]) / 2, (lat_r[1] - lat_r[0]), (lon_r[1] - lon_r[0])
def haversine(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1])); d = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(d))
print('known value: encode(57.64911, 10.40744, 11) = %s   (the Wikipedia example is u4pruydqqvj)' % encode(57.64911, 10.40744, 11))
print('precision  cell height x width at this latitude')
for p in (4, 5, 6, 7):
    lat, lon, dh, dw = decode_center(encode(37.77, -122.42, p)); print('   %d       %6.2f km x %6.2f km' % (p, dh * 111.2, dw * 111.2 * math.cos(math.radians(lat))))
rng = random.Random(2)
pts = [(37.70 + rng.random() * 0.15, -122.52 + rng.random() * 0.20) for _ in range(100000)]       # 100,000 drivers over a city
P = 6
cells = defaultdict(list)
for i, p in enumerate(pts): cells[encode(p[0], p[1], P)].append(i)
def neighbours(h):
    lat, lon, dh, dw = decode_center(h)
    return {encode(lat + a * dh, lon + b * dw, P) for a in (-1, 0, 1) for b in (-1, 0, 1)}
def near_index(q, radius_km, cell_set):
    cand = [i for c in cell_set for i in cells.get(c, ())]
    return sorted((i for i in cand if haversine(q, pts[i]) <= radius_km), key=lambda i: haversine(q, pts[i]))
def near_scan(q, radius_km): return sorted((i for i in range(len(pts)) if haversine(q, pts[i]) <= radius_km), key=lambda i: haversine(q, pts[i]))
q = (37.7749, -122.4194); R = 0.5
t = time.perf_counter(); truth = near_scan(q, R); scan_ms = (time.perf_counter() - t) * 1000
t = time.perf_counter(); same = near_index(q, R, {encode(q[0], q[1], P)}); one_ms = (time.perf_counter() - t) * 1000
t = time.perf_counter(); nine = near_index(q, R, neighbours(encode(q[0], q[1], P))); nine_ms = (time.perf_counter() - t) * 1000
print()
print('drivers within %.1f km of the rider: brute force finds %d in %.1f ms' % (R, len(truth), scan_ms))
print('  index, own cell only:           finds %d in %.2f ms   <- misses %d nearby drivers across the cell boundary' % (len(same), one_ms, len(truth) - len(same)))
print('  index, cell + 8 neighbours:     finds %d in %.2f ms   same answer as brute force: %s' % (len(nine), nine_ms, nine == truth))
print('  candidates examined: %d instead of %d' % (sum(len(cells.get(c, ())) for c in neighbours(encode(q[0], q[1], P))), len(pts)))
EOF''',
                     e="A geohash index built from scratch and checked against the truth. The encoder reproduces the well-known reference value, and the table shows how each extra character shrinks the cell (about a kilometre at six characters). With 100,000 drivers, brute force computes 100,000 distances; the index looks only at the rider's cell and its eight neighbours (a few hundred candidates), then filters by exact distance. The experiment also shows the **boundary problem**: searching only the rider's own cell **misses** drivers who are close but just across a cell edge, while the nine-cell search returns **exactly** the brute-force answer. (Timings depend on the machine; the candidate counts and the correctness comparison do not.)",
                     annot=[("known value: encode(57.64911, 10.40744, 11) = u4pruydqqvj", "matches the reference geohash: the encoder is correct"),
                            ("6   0.61 km x 0.97 km", "six characters is a cell of about a kilometre"),
                            ("brute force finds 290 in ~180 ms", "computes 100,000 distances"),
                            ("index, own cell only: finds 128 ... misses 162 nearby drivers across the cell boundary", "the boundary problem: close points in different cells"),
                            ("index, cell + 8 neighbours: finds 290 ... same answer as brute force: True; candidates examined: 1789 instead of 100000", "nine cells plus a distance filter are exact and examine under 2 percent of the points")]),
                dict(volatile=True, c=r'''. /dev/null; mkdir -p ~/spec && cd ~/spec
redis-server --port 6397 --bind 127.0.0.1 --save "" --appendonly no --daemonize yes --dir ~/spec >/dev/null; sleep 0.5
R="redis-cli -p 6397"
echo "--- Redis stores drivers in a geohash-encoded sorted set:"
$R geoadd drivers -122.4194 37.7749 d1 -122.4089 37.7833 d2 -122.4312 37.7694 d3 -122.2711 37.8044 d4 -122.4783 37.8199 d5 >/dev/null
echo "drivers: $($R zcard drivers)"
echo "--- the 3 nearest drivers within 3 km of the rider at (-122.4170, 37.7760):"
$R geosearch drivers fromlonlat -122.4170 37.7760 byradius 3 km asc count 3 withdist | paste -sd' ' | sed 's/ d/\nd/g' | sed 's/^/   /'
echo "--- a driver moves: one command updates the index (this is the hot path for moving objects):"
$R geoadd drivers -122.4180 37.7765 d4 >/dev/null
$R geosearch drivers fromlonlat -122.4170 37.7760 byradius 3 km asc count 3 withdist | paste -sd' ' | sed 's/ d/\nd/g' | sed 's/^/   /'
echo "--- the stored score is the 52-bit geohash integer: $($R zscore drivers d1)"
$R shutdown nosave >/dev/null 2>&1; true''',
                     e="The same idea as a database feature. Redis stores drivers as a sorted set whose **score is a geohash integer**, so `GEOSEARCH` can find members within a radius by scanning a few score ranges (the cell and its neighbours) and filtering by exact distance, returning them sorted with distances. A driver that moves is a single `GEOADD` on the same key: this is why in-memory geo indexes are the usual choice for moving objects, while static places go in PostGIS or a database index.",
                     annot=[("drivers: 5", "five members in the geo set"),
                            ("d1 0.2440 / d2 1.0801 / d3 1.4481", "the nearest three within three kilometres, with distances in km, sorted"),
                            ("after the move: d4 0.1041 is now the nearest", "one GEOADD updated the position: cheap to keep fresh"),
                            ("the stored score is the 52-bit geohash integer: 1367859919124626", "the sorted-set score encodes the location as a geohash")]),
            ]),
        ],
        scenario=dict(
            title="\"Design the matching of riders to the nearest drivers for a ride-hailing service.\"",
            ask="The geospatial design question (and the first half of the Uber problem). They want the index, the update path, the search, scale and failure.",
            clarify=[("How many drivers and riders, location update frequency, and what does \"nearest\" mean (distance, ETA, availability)?", "Assume 1 million active drivers updating every 4 seconds, 100,000 ride requests a minute at peak; ETA matters more than straight-line distance.")],
            think=[("Estimate.", "1M drivers / 4 s = 250,000 location updates per second: the write load dominates; 100,000 requests/min is about 1,700 searches per second. Position data is small and short-lived (latest position only)."),
                   ("Index.", "In-memory geospatial index keyed by cell (geohash, S2 or H3); each driver belongs to one cell at a time; an update moves the driver between cell sets when the cell changes, otherwise just updates the position; entries expire if pings stop."),
                   ("Sharding.", "Partition by cell (or region) so queries touch few shards; use a consistent hash of the cell id, with replication for availability; handle hot cells by splitting finer."),
                   ("Search.", "For a rider, query the cell and its neighbours (increasing rings until enough candidates), filter by availability and distance, then rank by estimated arrival time using a routing service for the top N, not for everybody."),
                   ("Matching and consistency.", "Offer the ride to the best driver with a lock/lease so two riders are not matched to one driver; handle timeouts and decline by moving to the next candidate."),
                   ("Pipeline.", "Location updates go through a message queue to the geo service; trips, payments and history are in durable stores; the geo index is rebuildable from the stream."),
                   ("Failure.", "If a geo shard dies its drivers reappear on the next ping (a few seconds): the index is soft state; degrade to a larger search radius; protect with rate limits and backpressure on updates.")],
            answer=["\"The load is mostly writes: a million drivers pinging every four seconds is about 250,000 location updates per second, while ride requests are around 1,700 searches per second. I would keep the latest position of each driver in an in-memory geospatial index keyed by cell, using geohash, S2 or H3 cells sized to the search radius. An update only changes the cell membership when the driver crosses a cell boundary, and entries expire if pings stop, so the index is soft state that rebuilds itself within seconds after a failure.",
                    "The index is sharded by cell so a query touches few shards, with finer splitting for hot cells. To match a rider I query their cell and its neighbours, expanding rings until there are enough candidates, filter by availability and distance, and rank the best few by ETA from a routing service rather than computing ETA for every driver. The offer uses a lease on the driver so two riders are not matched to the same one, falling back to the next candidate on a decline or timeout. Updates flow through a queue, and trips and payments live in durable stores.\""],
            follow=[("Geohash, quadtree, S2 or H3?", "Geohash is simple and works with any sorted index; quadtrees adapt to density; S2 and H3 give uniform cell neighbours on a sphere (H3 hexagons make ring searches simple); the choice matters less than getting the boundary and update path right."),
                    ("How do you avoid matching one driver to two riders?", "A short lease or atomic compare-and-set on the driver's state (available to offered) so only one offer can exist at a time."),
                    ("How do you handle a stadium emptying?", "A hot cell: split into finer cells dynamically, shard it separately, and batch updates; apply backpressure on the pings.")],
            slips=["Computing distances to all drivers.", "Ignoring the cell boundary problem.", "Treating the location index as a durable store instead of soft state."],
        ),
        quick=[
            ("Why are separate latitude and longitude indexes poor for nearby search?", "Each selects a band across the whole world; nearness needs a two-dimensional structure such as cells."),
            ("What is the boundary problem and its fix?", "Close points can fall in different cells; search the cell plus its neighbours, then filter by true distance."),
            ("Why keep moving objects in memory?", "Position updates are very frequent and short-lived; an in-memory index with expiry handles them cheaply."),
        ],
        traps=[
            "Searching only the single matching cell.",
            "Ranking by straight-line distance when travel time is what matters.",
            "Persisting every location ping synchronously: the write rate is the bottleneck.",
        ],
    ),
]

TAIL = dict(
    cases=[],
    cheat=[
        ["inverted index", "term -> postings list of documents; query = lookup + intersect"],
        ["analysis", "lower-case, tokenise, stop words, stem: same at index and query time"],
        ["TF-IDF / BM25", "frequent in the document, rare in the corpus: rank higher"],
        ["search is secondary", "derived from the database via events; eventually consistent; rebuildable"],
        ["shard + replicate", "index sharded by document, every query fans out, top results merged"],
        ["object store", "immutable blobs by key; no edit, rename or locks; huge, durable, cheap"],
        ["metadata vs data", "sharded metadata service separate from data nodes"],
        ["replication vs erasure coding", "3x space, simple vs ~1.4x, slower repair"],
        ["presigned URL", "client uploads and downloads directly to the store"],
        ["multipart / resumable", "parts retried individually; HEAD tells the offset; Range for reads"],
        ["time series", "append-mostly, range queries, mostly recent"],
        ["delta-of-delta", "regular timestamps compress to ~1 bit; ~1-2 bytes per point"],
        ["downsampling", "keep min, max, sum, count; tiers by age"],
        ["cardinality", "distinct series: never use user ids as labels"],
        ["geohash", "string prefix per cell; nearby shares prefix"],
        ["boundary problem", "search the cell and its 8 neighbours, then filter by distance"],
        ["moving objects", "in-memory index with expiry (Redis GEO); soft state"],
        ["choosing a store", "search for text, objects for blobs, TSDB for metrics, geo index for proximity"],
    ],
    interview_intro="Specialised-store answers are judged on knowing which structure fits the access pattern, how it is fed and kept consistent with the source of truth, and what its characteristic limits are. The worked scenarios in each lesson are the models to practise with.",
    interview=[
        dict(q="Design search for an e-commerce site with 100 million products.",
             a=["Inverted index in a Lucene-based engine as a secondary store; analysed text fields, keyword fields for facets, numeric fields; shards and replicas, query fan-out and merge.", "Freshness via events (outbox/CDC) to indexers; alias switch for reindexing; BM25 plus popularity signals, tuned with click data.", "Eventually consistent: recheck stock on the page; rebuild from the database; watch deep pagination and wildcard queries."],
             follow=["Why not LIKE or database full text?", "How do you do autocomplete?"], mistakes=["Search index as the source of truth.", "No update pipeline."],
             angle="Reported by candidates as a common search design prompt at large companies; not official."),
        dict(q="Design photo and video storage (Google Photos or S3).",
             a=["Immutable blobs in an object store, metadata in a separate database; presigned URL or multipart uploads, resumable, async processing.", "Durability by erasure coding across zones with tiering; scrubbing; CDN with cached renditions and ranged reads.", "Estimate volume and cost; dedup carefully; soft then hard delete."],
             follow=["Replication or erasure coding?", "How do uploads avoid your servers?"], mistakes=["Blobs in the relational database.", "Bytes through the app tier."]),
        dict(q="Design a metrics monitoring system for 100,000 servers.",
             a=["500,000 points/s; compressed time-series blocks with delta-of-delta; queue between collectors and storage; sharding by series and time; replication.", "Downsampling tiers keeping min, max, sum, count; label cardinality limits.", "Separate alert evaluator, grouped and routed, with a watchdog; monitoring is itself monitored from outside."],
             follow=["Push or pull?", "What if monitoring fails?"], mistakes=["Ignoring cardinality.", "Average-only rollups."]),
        dict(q="Design the nearest-driver matching for a ride-hailing service.",
             a=["Write-heavy: 250,000 location updates/s; in-memory cell index (geohash, S2, H3) with expiry; shard by cell; split hot cells.", "Search the cell and its neighbours in rings, filter by availability, rank the top N by ETA.", "Lease on the driver to avoid double matching; location index is soft state rebuilt from pings; queue for updates."],
             follow=["Geohash or H3?", "How avoid matching one driver twice?"], mistakes=["Distance to all drivers.", "Ignoring cell boundaries."],
             angle="Uber-style problem: candidates commonly report follow-ups on hot cells and ETA versus distance; reported by candidates, not official."),
        dict(q="Explain an inverted index and how ranking works.",
             a=["Map each term to the documents (and positions) containing it; analyse text the same way at index and query time.", "Intersect postings for AND; score with TF-IDF or BM25 so rare terms and repeated terms count.", "Shard and replicate for scale; the index is derived from the source of truth."],
             follow=["What is stemming?", "What is BM25's improvement over TF-IDF?"], mistakes=["Different analysis at index and query time."]),
    ],
    selftest=[
        ("What does an inverted index map?", "Terms to the documents containing them."),
        ("Why does IDF help ranking?", "Rare terms discriminate between documents; common ones do not."),
        ("Should the search index be the source of truth?", "No: it is a derived, eventually consistent secondary index."),
        ("What do object stores not support?", "In-place edits, rename, locks and cross-object transactions."),
        ("Why erasure coding?", "Durability at about 1.4x space instead of 3x, with costlier repair."),
        ("What is a presigned URL?", "A time-limited signed link for direct upload or download to the store."),
        ("Why do timestamps compress in time series?", "Regular intervals make delta-of-delta almost always zero."),
        ("What should a rollup keep besides the average?", "Min, max, sum and count."),
        ("What is cardinality?", "The number of distinct series (label combinations)."),
        ("What is geohash?", "A string encoding a grid cell; nearby points usually share a prefix."),
        ("What is the boundary problem?", "Close points can be in different cells; search neighbours and filter by distance."),
        ("Why keep driver locations in memory?", "They update constantly and are soft state."),
    ],
    recall=[
        ["inverted index", "term to postings"],
        ["BM25", "TF x rarity, length normalised"],
        ["search store", "derived, eventually consistent"],
        ["object store", "immutable blobs, metadata apart"],
        ["erasure coding", "k+m fragments, ~1.4x"],
        ["presigned URL", "direct to the store"],
        ["delta-of-delta", "~1 bit timestamps"],
        ["rollups", "min, max, sum, count"],
        ["cardinality", "no user id labels"],
        ["geohash", "prefix per cell"],
        ["neighbours", "9 cells, then true distance"],
    ],
    sources=[
        dict(title="Elasticsearch guide: How search works (inverted index, analysis)", url="https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis.html", use="Analysis, tokenisation and index structure in a production engine", license="Copyright Elastic; read online", how="Link only"),
        dict(title="SQLite FTS5 extension", url="https://www.sqlite.org/fts5.html", use="The full-text engine used in the experiment, including BM25 ranking", license="Public domain; read online", how="Link only"),
        dict(title="Amazon S3: durability and data protection", url="https://docs.aws.amazon.com/AmazonS3/latest/userguide/DataDurability.html", use="How a large object store describes durability across failure domains", license="Copyright Amazon; read online", how="Link only"),
        dict(title="Gorilla: A Fast, Scalable, In-Memory Time Series Database (Facebook)", url="https://www.vldb.org/pvldb/vol8/p1816-teller.pdf", use="Delta-of-delta timestamps and XOR value compression", license="Copyright the authors; read online", how="Link only"),
        dict(title="Prometheus: Storage and TSDB design", url="https://prometheus.io/docs/prometheus/latest/storage/", use="Blocks, retention and cardinality in a widely used metrics system", license="Apache 2.0; read online", how="Link only"),
        dict(title="Geohash (Wikipedia) and the reference algorithm", url="https://en.wikipedia.org/wiki/Geohash", use="The encoding and the example value used in the lesson", license="CC BY-SA; read online", how="Link only"),
        dict(title="Uber H3: Hexagonal hierarchical spatial index", url="https://h3geo.org/docs/", use="Cell systems with uniform neighbours", license="Apache 2.0; read online", how="Link only"),
        dict(title="Redis documentation: Geospatial commands", url="https://redis.io/docs/latest/commands/geosearch/", use="GEOADD and GEOSEARCH used in the lesson", license="Copyright Redis; read online", how="Link only"),
    ],
    plan=[
        "**Hours 1 to 2:** search: add a phrase query and a stop-word list to the toy index; compare FTS5 ranking for your own queries.",
        "**Hours 3 to 4:** object storage: change the chunk size and the edit position and count shared chunks; then the search-index-read lab.",
        "**Hours 5 to 6:** time series: change the scrape interval and the value pattern and re-measure compression.",
        "**Hours 7 to 8:** geospatial: change the precision and the search radius; find when the neighbour search becomes necessary.",
        "**Hours 9 to 10:** say each interview scenario aloud for two minutes, timed, and compare with the written answer.",
    ],
)
