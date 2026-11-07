"""S21 search, blob and specialised stores: part A (rig, lessons 1 to 3: inverted index and full-text search, object storage, time-series)."""
import sysviz as v

INDEX_VIZ = v.figure(
    720, 240,
    [v.box(10, 20, 300, 130, "Documents", "ink", ""),
     v.text(160, 52, "1: red running shoes", "dg-s"), v.text(160, 78, "2: blue running shorts", "dg-s"), v.text(160, 104, "3: red shorts", "dg-s"),
     v.arrow(310, 85, 370, 85),
     v.box(370, 20, 340, 130, "Inverted index: term to documents", "ok", ""),
     v.text(540, 50, "red     -> 1, 3", "dg-s"), v.text(540, 72, "running -> 1, 2", "dg-s"), v.text(540, 94, "shoes   -> 1", "dg-s"), v.text(540, 116, "shorts  -> 2, 3", "dg-s"), v.text(540, 138, "blue    -> 2", "dg-s"),
     v.text(360, 186, "Query: red AND shorts. Look up two short lists and intersect them: document 3.", "dg-s"),
     v.text(360, 212, "Ranking (TF-IDF, BM25) then orders the matches by how well and how rarely the terms occur.", "dg-s")],
    "The inverted index", "Search engines store the list of documents for each word, not the words of each document")

OBJ_VIZ = v.figure(
    720, 230,
    [v.box(10, 80, 100, 56, "Client", "ink"),
     v.arrow(110, 95, 160, 55), v.arrow(110, 120, 160, 160),
     v.box(160, 28, 190, 56, "Metadata service", "warn", "bucket, key, size, hash, parts"),
     v.box(160, 134, 190, 56, "Data nodes", "ok", "chunks, replicated or erasure coded"),
     v.arrow(350, 56, 400, 56), v.arrow(350, 162, 400, 162),
     v.box(400, 28, 150, 56, "Index (sharded)", "acc", "key to chunk locations"),
     v.box(400, 134, 150, 56, "Failure domains", "acc", "zones, racks, disks"),
     v.box(580, 80, 130, 56, "Durability", "ok", "eleven nines through copies"),
     v.text(360, 216, "Object stores trade features (no in-place edit, no rename) for scale, durability and low cost per byte.", "dg-s")],
    "How object storage works", "Metadata and data are separate; durability comes from copies across failure domains")

LESSONS_A = [
    dict(
        title="Search: the inverted index, ranking and a real full-text engine",
        tier="hot",
        situation="\"Find every product containing red and shorts\" is a `LIKE '%red%'` that reads every row and cannot rank. Search needs a different data structure, the one behind every search engine: the inverted index.",
        learn=["Why scanning does not scale, and the inverted index", "Tokenising, stemming and stop words", "Ranking: term frequency and rarity (TF-IDF, BM25)", "A real full-text engine (SQLite FTS5) and where Elasticsearch fits"],
        model=[
            "A **database `LIKE` scan** reads every document for every query and cannot rank results. A search engine builds an **inverted index** ahead of time: for each **term** a **postings list** of the documents (and positions) containing it. A multi-word query looks up each term's short list and **intersects** them (for AND) or merges them (for OR): the cost depends on the lists, not the corpus size. Before indexing, text goes through **analysis**: lower-casing, **tokenising** into words, removing **stop words** (the, a), and **stemming** (running to run) so that related forms match. The same analysis must be applied to the query.",
            "Results are **ranked**, not just matched. **TF-IDF** scores a document higher when a query term appears often in it (**term frequency**) and lower when the term is common across the corpus (**inverse document frequency**: rare terms matter more); **BM25** refines this with length normalisation and saturation and is the usual default. At scale an index is **sharded** by document across nodes (every query goes to every shard and the top results are merged) and **replicated**. Search systems (Lucene-based Elasticsearch and OpenSearch, Solr) are usually a **secondary index** fed from the primary database by events or CDC, not the system of record: they are eventually consistent and rebuilt from the source when needed. Add **relevance tuning**, typo tolerance (edit distance), synonyms, faceting and autocomplete as needs arise.",
        ],
        analogy="The index at the back of a book: instead of reading every page for the word \"saffron\", you look it up and get the page numbers. Two words? Look up both lists and keep the pages in common. A word that appears on every page tells you nothing; one that appears on two pages tells you a lot.",
        visual=[INDEX_VIZ],
        sim=None,
        walk=[
            ("Analyse the text", "Lower-case, split into tokens, drop stop words, stem."),
            ("Build the inverted index", "For each term, the list of documents (and positions) that contain it."),
            ("Analyse the query the same way", "Otherwise the terms will not match what was indexed."),
            ("Intersect or merge the postings lists", "AND intersects; OR merges; phrases check positions."),
            ("Rank the matches", "BM25 (or TF-IDF), perhaps combined with popularity, freshness and personalisation."),
        ],
        groups=[
            dict(title="Build an inverted index by hand, then use a real engine", cmds=[
                dict(c=r'''mkdir -p ~/spec && cd ~/spec && python3 - <<'EOF'
import math, re
from collections import defaultdict
docs = {1: 'Red running shoes for trail running', 2: 'Blue running shorts, lightweight', 3: 'Red cotton shorts', 4: 'Leather office shoes, black', 5: 'Running socks for trail and road'}
STOP = {'for', 'and', 'the', 'a'}
def analyse(text):
    out = []
    for w in re.findall(r'[a-z]+', text.lower()):
        if w in STOP: continue
        for suf in ('ing', 's'):                       # a toy stemmer: running -> runn... good enough to show the idea
            if w.endswith(suf) and len(w) > len(suf) + 2: w = w[:-len(suf)]; break
        out.append(w)
    return out
index = defaultdict(lambda: defaultdict(int))          # term -> {doc id: term frequency}
for i, text in docs.items():
    for t in analyse(text): index[t][i] += 1
print('inverted index (term -> {document: count}):')
for t in sorted(index): print('  %-10s %s' % (t, dict(index[t])))
def search(query):
    terms = analyse(query)
    postings = [set(index[t]) for t in terms]
    hits = set.intersection(*postings) if postings else set()
    N = len(docs)
    def score(i): return sum(index[t][i] * math.log(1 + N / len(index[t])) for t in terms)       # TF x IDF
    return sorted(((round(score(i), 2), i, docs[i]) for i in hits), reverse=True)
for q in ('red shorts', 'running shoes', 'trail'):
    print('\nquery %r analysed to %s' % (q, analyse(q)))
    for s, i, d in search(q): print('   score %.2f  doc %d: %s' % (s, i, d))
EOF''',
                     e="A search engine in forty lines. Each document is analysed and added to the **inverted index**: for each stemmed term, which documents contain it and how often. A query is analysed the same way, the short postings lists are **intersected** (documents containing every term) and the survivors are **scored** by term frequency weighted by how **rare** the term is across the collection, so a match on a rare word beats a match on a common one. Nothing scans the documents at query time: the work depends on the lists, which is why this scales to billions of documents once the index is sharded.",
                     annot=[("runn {1: 2, 2: 1, 5: 1}", "a postings list: the toy stemmer turns running into runn, and the list shows which documents contain it and how often"),
                            ("query 'red shorts' analysed to ['red', 'short']", "the same analysis as at indexing: plural removed"),
                            ("score ... doc 3: Red cotton shorts", "the only document containing both terms is the only result"),
                            ("query 'trail': docs 5 and 1 tie at 1.25", "equal counts of the same term score equally; a document repeating the term more often would rank higher")]),
                dict(volatile=True, c=r'''cd ~/spec && python3 - <<'EOF'
import sqlite3, time, random
db = sqlite3.connect(':memory:')
print('SQLite', sqlite3.sqlite_version, '- FTS5 available:', 'ENABLE_FTS5' in ' '.join(r[0] for r in db.execute('pragma compile_options')))
db.execute("create virtual table docs using fts5(title, body, tokenize='porter')")      # an inverted index with stemming, built in
words = 'cotton leather running trail office light heavy waterproof breathable winter summer lace strap zip hood sole grip'.split()
rng = random.Random(1)
rows = [(' '.join(rng.sample(words, 2)) + ' shoes', ' '.join(rng.choice(words) for _ in range(30))) for _ in range(100000)]
db.executemany('insert into docs values (?, ?)', rows)
db.execute("insert into docs values ('Marathon racing flats', 'ultra light carbon plate saffron racing')")
db.commit()
t = time.perf_counter(); n = db.execute("select count(*) from docs where body like '%saffron%'").fetchone()[0]; like_ms = (time.perf_counter() - t) * 1000
t = time.perf_counter(); r = db.execute("select title, bm25(docs) from docs where docs match 'saffron' order by bm25(docs)").fetchall(); fts_ms = (time.perf_counter() - t) * 1000
print('LIKE scan over 100,001 documents:   found %d in %7.1f ms' % (n, like_ms))
print('full-text index (FTS5 MATCH):       found %d in %7.3f ms   -> %s' % (len(r), fts_ms, r[0][0]))
db.executemany('insert into docs values (?, ?)', [('Saffron dye kit', 'saffron saffron saffron saffron'), ('Cooking set', 'a pinch of saffron for the rice and a pot'), ('Spice rack', 'cumin pepper salt saffron paprika cardamom')])
print('ranked query "saffron" (BM25, lower score = better in FTS5): documents that use the word more, and are shorter, rank first:')
for title, score in db.execute("select title, round(bm25(docs), 2) from docs where docs match 'saffron' order by bm25(docs)"): print('   %-34s bm25 %s' % (title, score))
print('stemming at work: a query for "run" also matches "running":', db.execute("select count(*) from docs where docs match 'run'").fetchone()[0], 'documents')
EOF''',
                     e="The same idea in a real engine you already have. SQLite's FTS5 builds an inverted index and ranks with **BM25**. The needle (`saffron`, present in one document of 100,001) is found by the `LIKE` scan only after reading everything, while the index answers in a fraction of a millisecond; the gap grows with the corpus. Multi-term queries return ranked results, and the Porter stemmer makes `run` match `running`. Elasticsearch, OpenSearch and Solr are distributed, feature-rich versions of exactly this structure (built on Lucene).",
                     annot=[("FTS5 available: True", "the full-text extension ships with SQLite here"),
                            ("LIKE scan over 100,001 documents: found 1 in tens of ms", "reads every row: cost grows with the corpus"),
                            ("full-text index (FTS5 MATCH): found 1 in under a millisecond", "a postings list lookup: tens to hundreds of times faster here, and the gap grows with the corpus"),
                            ("stemming at work: a query for \"run\" also matches \"running\": 85767 documents", "analysis at index and query time makes related word forms match"),
                            ("ranked query \"saffron\": Saffron dye kit first", "the document that repeats the rare term most ranks first (FTS5 returns negative scores: smaller is better)")]),
            ]),
        ],
        scenario=dict(
            title="\"Design search for an e-commerce site with 100 million products. How do you keep it fresh and relevant?\"",
            ask="The standard search design question. They want the index structure, the pipeline from the database, scaling, relevance and failure behaviour.",
            clarify=[("Query rate, update rate, latency target, and what matters in ranking (text match, popularity, price, personalisation)?", "Assume 5,000 queries/s, 1 million product updates/day, 100 ms p99, relevance from text plus popularity.")],
            think=[("Do not search the database.", "LIKE scans do not scale or rank; build a search index (inverted index) in a Lucene-based engine as a secondary store; the product database stays the source of truth."),
                   ("Index design.", "Documents with analysed text fields (title, description, brand), keyword fields (category, brand) for filtering and facets, numeric fields (price, rating, sales rank); analyser chain with stemming and synonyms; autocomplete via edge n-grams or a completion index."),
                   ("Scale.", "100M documents at about 2 KB is 200 GB of source, an index of similar size: shard into 20 to 50 shards of a few GB to 30 GB; replicate each shard 2 to 3 times for availability and query throughput; every query fans out to all shards and merges the top results."),
                   ("Freshness.", "Product changes publish events (outbox/CDC) to a queue; indexers update the search index within seconds; periodic full reindexing into a new index with an alias switch for schema changes."),
                   ("Relevance.", "BM25 text score combined with signals (sales, rating, stock, margin, personalisation) via a learned or hand-tuned function; query understanding (spell correction, synonyms); measure with click-through and conversion; A/B tests."),
                   ("Reliability and consistency.", "The index is eventually consistent: a product just made unavailable may still appear: re-check stock on the product page; if the cluster is degraded, serve cached or simplified results; rebuild from the database if lost."),
                   ("Costs and limits.", "Deep pagination is expensive (use search-after cursors), wildcard-leading queries are slow, mapping explosions from dynamic fields, hot shards.")],
            answer=["\"I would not search the database: a LIKE scan neither scales nor ranks. I would build an inverted index in a Lucene-based engine such as Elasticsearch or OpenSearch as a secondary store, with the product database remaining the source of truth. Documents have analysed text fields with stemming and synonyms, keyword fields for filters and facets, and numeric fields like price and rating. With a hundred million products that is a couple of hundred gigabytes, so I would use a few dozen shards, each replicated two or three times, with every query fanning out to all shards and merging the top results.",
                    "Freshness comes from publishing product changes as events through an outbox or change data capture to indexers that update the index within seconds; schema changes go into a new index with an alias switch. Ranking combines BM25 with signals such as sales, rating and stock, tuned with click-through and A/B tests. The index is eventually consistent, so availability is rechecked on the product page, and if it is lost I rebuild from the database. I would watch deep pagination, expensive wildcard queries and hot shards.\""],
            follow=[("Why not use the database's full-text search?", "Fine for small data and simple needs (PostgreSQL full-text, SQLite FTS5); at large scale, with facets, relevance tuning and distributed scaling, a dedicated engine is better."),
                    ("How do you do autocomplete?", "A prefix index (edge n-grams or a completion trie), ranked by popularity, served from memory with very low latency; see the autocomplete design problem."),
                    ("What is eventual consistency here and how do you hide it?", "The index lags the database by seconds; hide it by rechecking authoritative data (stock, price) when rendering and by routing a user's own edits through read-your-writes paths.")],
            slips=["\"Use Elasticsearch\" with no explanation of the index.", "Treating the search index as the system of record.", "Ignoring how updates reach the index."],
        ),
        quick=[
            ("What does an inverted index map?", "Each term to the list of documents (and positions) containing it."),
            ("Why does TF-IDF weight rare terms more?", "A term that is common across documents says little about relevance; a rare term discriminates."),
            ("Should the search index be your source of truth?", "No: it is a derived, eventually consistent secondary index rebuilt from the primary store."),
        ],
        traps=[
            "Different analysis at index time and query time: terms never match.",
            "Deep pagination with large offsets: every shard must produce and sort all the skipped results.",
            "Reindexing in place with no alias switch: users see a half-built index.",
        ],
    ),
    dict(
        title="Object storage and blobs: how photos and videos are stored at scale",
        tier="hot",
        situation="Users upload billions of photos and videos. They are large, immutable, read often and must never be lost. Putting them in a relational database is expensive and slow; the standard answer is an object store such as S3, and an interviewer will ask how one works inside.",
        learn=["Objects, buckets and keys, and what object stores deliberately do not offer", "Metadata separate from data", "Durability: replication versus erasure coding", "Large uploads: multipart and resumable, and presigned URLs"],
        model=[
            "An **object store** keeps **immutable blobs** addressed by a **key** inside a **bucket**, via a simple HTTP API (put, get, delete, list by prefix). It deliberately lacks what file systems and databases have: no in-place edits (write a new version), no rename (copy and delete), no locks, no transactions across objects. In exchange it offers **enormous scale, high durability** (S3 quotes eleven nines), **low cost per byte**, and **simple, cacheable HTTP access**. Metadata (key, size, hash, content type, version, which chunks and where) lives in a **sharded metadata/index service**, separate from the **data nodes** holding the bytes; separating them lets each scale independently.",
            "**Durability** comes from storing each object across **failure domains** (disks, racks, zones). **Replication** keeps full copies (simple, fast reads, 3x the space). **Erasure coding** splits an object into *k* data fragments plus *m* parity fragments so that any *k* of the *k + m* rebuild it (for example 10 + 4 survives any 4 lost fragments at 1.4x the space): far cheaper at scale, more compute and slower repair. Background **scrubbing** checks hashes and repairs silent corruption. For large files use **multipart upload** (parts uploaded in parallel and retried individually, then stitched) and **presigned URLs** (time-limited signed links so clients upload and download **directly** to and from the store, bypassing your servers); serve popular objects through a **CDN**.",
        ],
        analogy="A huge warehouse with a card index. You hand in a package and get a code; the index records which aisle and shelf, and the warehouse keeps spare copies (or a recoverable split of each package) in different buildings, so a fire in one building loses nothing.",
        visual=[OBJ_VIZ],
        sim=None,
        walk=[
            ("Client asks the API for an upload", "The service authenticates, creates the metadata record and returns a presigned URL (or multipart upload id)."),
            ("Client uploads directly to the store", "Large files in parts, each retried on failure; your servers never carry the bytes."),
            ("The store spreads the data", "Chunks are placed in different failure domains, replicated or erasure coded."),
            ("Metadata is committed last", "The object becomes visible only when all parts are verified (hash) and complete."),
            ("Reads go through caches", "A CDN or cache serves popular objects; cold ones come from the store."),
        ],
        groups=[
            dict(title="Chunks, hashes, erasure coding and resumable transfers", cmds=[
                dict(c=r'''mkdir -p ~/spec && cd ~/spec && python3 - <<'EOF'
import hashlib, os, random
rng = random.Random(8)
# Two "files" that differ by one small edit in the middle; store them as fixed-size chunks addressed by hash.
base = bytes(rng.getrandbits(8) for _ in range(40 * 1024))                       # a 40 KB file
edited = base[:20000] + b'EDIT' + base[20004:]                                   # the same file with 4 bytes changed
def chunks(data, size=4096): return [data[i:i + size] for i in range(0, len(data), size)]
store = {}
def put(data):
    keys = []
    for c in chunks(data):
        h = hashlib.sha256(c).hexdigest(); store.setdefault(h, c); keys.append(h)    # identical chunks are stored once
    return keys
v1 = put(base); v2 = put(edited)
print('file v1: %d chunks; file v2: %d chunks; distinct chunks actually stored: %d (instead of %d)' % (len(v1), len(v2), len(store), len(v1) + len(v2)))
print('uploading v2 after v1 needs only the chunks the store does not already have: %d of %d' % (len(set(v2) - set(v1)), len(v2)))
# Erasure coding with a single XOR parity fragment (the simplest case of the idea): any ONE of k+1 fragments can be lost.
k = 4; frags = [base[i * 10240:(i + 1) * 10240] for i in range(k)]
parity = bytes(a ^ b ^ c ^ d for a, b, c, d in zip(*frags))
print()
print('erasure coding (4 data fragments + 1 XOR parity = 1.25x the space):')
lost = 2; survivors = [f for i, f in enumerate(frags) if i != lost]
rebuilt = bytes(a ^ b ^ c ^ p for a, b, c, p in zip(*survivors, parity))
print('  fragment %d is lost (a failed disk); rebuilt from the other fragments and the parity: identical to the original = %s' % (lost, rebuilt == frags[lost]))
print('  replication would need 3x the space for the same single-failure protection; real systems use Reed-Solomon codes such as 10+4 (1.4x, any 4 losses).')
EOF''',
                     e="Two storage ideas in one experiment. **Chunking with hashes**: a 40 KB file and a copy with four changed bytes share every chunk but one, so storing the second version costs one chunk (and uploading it only needs the chunks the store lacks). This is the basis of deduplication and delta uploads in cloud storage. **Erasure coding**, in its simplest form: four data fragments plus one XOR parity fragment; when one fragment is lost the others and the parity reconstruct it exactly, for 1.25 times the space instead of the 3 times that replication would need for the same single-failure protection. Production systems use Reed-Solomon codes that survive several simultaneous losses.",
                     annot=[("file v1: 10 chunks; file v2: 10 chunks; distinct chunks actually stored: 11 (instead of 20)", "the edit changed one chunk: nearly everything is shared"),
                            ("uploading v2 after v1 needs only ... 1 of 10", "delta upload: send only the new chunk"),
                            ("fragment 2 is lost ...; rebuilt ... identical to the original = True", "parity rebuilds a lost fragment: durability without full copies")]),
                dict(volatile=True, c=r'''cd ~/spec && cat > blobserver.py <<'EOF'
# A tiny blob server with resumable uploads: PUT with a Content-Range appends a part; HEAD tells the client how much has arrived.
import http.server, os, socketserver
os.makedirs('/tmp/blobs', exist_ok=True)
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def path_(self): return '/tmp/blobs/' + self.path.strip('/').replace('/', '_')
    def do_HEAD(self):
        p = self.path_(); size = os.path.getsize(p) if os.path.exists(p) else 0
        self.send_response(200); self.send_header('X-Received-Bytes', str(size)); self.send_header('Content-Length', '0'); self.end_headers()
    def do_PUT(self):
        n = int(self.headers['Content-Length']); start = int(self.headers.get('Content-Range', 'bytes 0-').split()[1].split('-')[0])
        p = self.path_(); have = os.path.getsize(p) if os.path.exists(p) else 0
        if start != have:                                                          # the client must continue exactly where the server stopped
            self.send_response(409); self.send_header('X-Received-Bytes', str(have)); self.send_header('Content-Length', '0'); self.end_headers(); return
        open(p, 'ab').write(self.rfile.read(n)); self.send_response(200); self.send_header('Content-Length', '0'); self.end_headers()
    def do_GET(self):
        p = self.path_(); rng = self.headers.get('Range'); data = open(p, 'rb').read()
        if rng: a, b = rng.split('=')[1].split('-'); data = data[int(a):int(b) + 1]; self.send_response(206)
        else: self.send_response(200)
        self.send_header('Content-Length', str(len(data))); self.end_headers(); self.wfile.write(data)
socketserver.TCPServer.allow_reuse_address = True
socketserver.TCPServer(('127.0.0.1', 8340), H).serve_forever()
EOF
rm -rf /tmp/blobs; (setsid python3 blobserver.py </dev/null >/dev/null 2>&1 & disown) 2>/dev/null; sleep 0.7
head -c 3000000 /dev/urandom > big.bin; sum=$(sha256sum big.bin | cut -c1-16)
echo "file: 3,000,000 bytes, sha256 starts $sum"
echo "--- upload in 1 MB parts; the connection 'drops' after the second part:"
curl -s -o /dev/null -X PUT -H "Content-Range: bytes 0-" --data-binary @<(head -c 1000000 big.bin) http://127.0.0.1:8340/videos/big.bin
curl -s -o /dev/null -X PUT -H "Content-Range: bytes 1000000-" --data-binary @<(tail -c +1000001 big.bin | head -c 1000000) http://127.0.0.1:8340/videos/big.bin
echo "--- the client reconnects and asks how much arrived (HEAD):"
got=$(curl -sI http://127.0.0.1:8340/videos/big.bin | grep -i x-received | tr -d '\r' | awk '{print $2}'); echo "server has $got bytes"
echo "--- it resumes from that offset, sending only the rest:"
curl -s -o /dev/null -X PUT -H "Content-Range: bytes $got-" --data-binary @<(tail -c +$((got+1)) big.bin) http://127.0.0.1:8340/videos/big.bin
echo "stored object sha256 starts $(sha256sum /tmp/blobs/videos_big.bin | cut -c1-16)   (matches the original: $([ "$sum" = "$(sha256sum /tmp/blobs/videos_big.bin | cut -c1-16)" ] && echo yes || echo NO))"
echo "--- a ranged download (video seeking): bytes 1,000,000 to 1,000,009 only:"
curl -s -H "Range: bytes=1000000-1000009" http://127.0.0.1:8340/videos/big.bin | wc -c | sed 's/^/received bytes: /'
pkill -f blobserver.py; true''',
                     e="Resumable uploads and ranged reads with real HTTP. The file goes up in parts; after the connection \"drops\" the client asks the server how many bytes it has (`HEAD`), then sends **only the remainder** starting at that offset: no need to start over a multi-gigabyte upload, and the final checksum proves the object is intact. A **`Range` request** fetches just ten bytes from the middle, which is how video players seek and how downloads resume. Real object stores add parallel parts, a part list to assemble, a final commit and signed URLs, but the protocol idea is exactly this.",
                     annot=[("server has 2000000 bytes", "the server knows exactly how far the upload got"),
                            ("stored object sha256 starts ... (matches the original: yes)", "the resumed upload produced an identical object"),
                            ("received bytes: 10", "a ranged GET returns only the requested slice: seeking and resumable downloads")]),
            ]),
        ],
        scenario=dict(
            title="\"Design a photo and video storage service like Google Photos or S3. How are files stored, kept durable and served?\"",
            ask="A storage design question. They want upload paths, metadata, durability, cost and serving.",
            clarify=[("Object sizes, total volume, read to write ratio, durability and availability targets?", "Assume 2 billion photos a day... scaled down: 500 million uploads a day averaging 3 MB (1.5 PB/day), videos larger; eleven nines durability, 99.99% availability.")],
            think=[("Estimate.", "500M uploads/day is about 5,800 per second and 1.5 PB/day: about 550 PB a year before replication. Reads outnumber writes 10:1 and follow a steep popularity curve (recent and popular items dominate)."),
                   ("Upload path.", "Client asks the API (auth, quota) and receives a presigned URL or multipart upload id; uploads parts directly to the object store, resumable; a completion call verifies size and hash and makes the object visible; processing (thumbnails, transcoding, virus scan) is asynchronous through a queue."),
                   ("Storage.", "Object store with metadata service (sharded database of key to chunk locations) separate from data nodes; erasure coding (for example 10+4) across zones for durable, cheap storage; hot tier on SSD/replicas for recent objects, cold tier for old; lifecycle rules."),
                   ("Dedup and integrity.", "Content hashes for integrity and optional deduplication (careful with privacy implications); scrubbing and repair jobs; checksums verified on read."),
                   ("Read path.", "CDN in front; thumbnails and renditions generated once and cached; ranged reads for video; presigned or signed cookie access for private content."),
                   ("Metadata and search.", "A separate database for albums, owners, EXIF, face and label indexes; the blob key is just one field."),
                   ("Failure and cost.", "Zone failures survived by erasure coding across zones; repair bandwidth budgeted; the dominant cost is storage and egress: tiering, compression, CDN hit ratio.")],
            answer=["\"Photos are large immutable blobs, so I would use an object store and keep metadata in a separate database. At 500 million uploads a day that is about 6,000 uploads a second and 1.5 petabytes a day, so cost and durability dominate. Clients get a presigned URL or a multipart upload id from the API after auth and quota checks and upload parts directly to the store, resumable; a completion call verifies size and hash and makes the object visible. Thumbnails, transcoding and scanning run asynchronously from a queue.",
                    "The store separates a sharded metadata service from the data nodes and places data across zones with erasure coding such as ten plus four for durability at about 1.4 times the space, with SSD for recent objects and a cold tier for old ones through lifecycle rules, and scrubbing to repair silent corruption. Reads go through a CDN with cached renditions and ranged requests for video. Albums, owners and labels live in a separate database. The costs are storage and egress, so tiering, compression and CDN hit ratio are the levers.\""],
            follow=[("Replication or erasure coding?", "Replication for hot, small or latency-sensitive data (simple, fast repair); erasure coding for large, cold data where space dominates, accepting slower reads on failure and costlier repair."),
                    ("How do you avoid sending large uploads through your servers?", "Presigned URLs (or signed upload policies) let clients write directly to the store; your API only authorises and records metadata."),
                    ("How do you handle deletion and privacy?", "Soft delete in metadata, then asynchronous hard deletion with a grace period; reference counting if deduplicated; verify deletion across replicas and backups.")],
            slips=["Storing photos in the relational database.", "Routing all bytes through the application servers.", "No story for durability beyond \"we have backups\"."],
        ),
        quick=[
            ("What do object stores deliberately not support?", "In-place edits, rename, locks and cross-object transactions."),
            ("Why erasure coding instead of 3 copies?", "It gives similar durability for far less space (for example 1.4x instead of 3x), at the cost of more compute and slower repair."),
            ("What is a presigned URL for?", "A time-limited signed link letting a client upload or download directly to the store, bypassing your servers."),
        ],
        traps=[
            "Carrying large uploads through the application tier: it becomes the bandwidth bottleneck.",
            "Making an object visible before all parts are verified: readers see partial files.",
            "Treating replication as backup: a replicated delete or corruption replicates too.",
        ],
    ),
    dict(
        title="Time-series data: ingest, compression and downsampling",
        tier="core",
        situation="A fleet of 100,000 servers reports 50 metrics every 10 seconds. That is 500,000 points per second, forever, written in time order and queried by time range and aggregation. A general-purpose database struggles; a time-series store is built for exactly this shape.",
        learn=["The workload shape of time-series data", "Why timestamps and values compress so well (delta-of-delta)", "Downsampling and retention tiers", "Cardinality: the real limit of a metrics system"],
        model=[
            "Time-series data is **append-mostly** (points arrive in time order and are almost never updated), queried as **ranges** and **aggregations** (average over the last hour, per host), and mostly **recent** (old data is queried at coarser resolution). Stores such as Prometheus, InfluxDB and TimescaleDB, or wide-column stores partitioned by series and time, exploit this: data is grouped by **series** (a metric plus its label set) and time block, written to an in-memory buffer and a log, and flushed to **immutable compressed blocks**. Timestamps arrive at regular intervals, so **delta-of-delta encoding** stores mostly zeros; floating-point values that change slowly compress with **XOR encoding** (the Gorilla technique): real systems reach 1 to 2 bytes per point, from 16 raw.",
            "Keep storage bounded with **retention and downsampling**: raw 10-second points for 2 weeks, 1-minute averages for 3 months, 1-hour averages for years, computed by background jobs (and keeping min, max, count, sum so percentiles and rates remain approximately computable). The scaling limit is usually **cardinality** (the number of distinct series): each unique label combination (for example adding a user id label) creates a new series with its own index entry and memory, so high-cardinality labels can overwhelm the system long before the point rate does. Design alerts and dashboards around aggregated queries, shard by series hash and time, and treat raw data as perishable.",
        ],
        analogy="A seismograph's paper roll: it only ever grows at one end, you read it by time window, last week is looked at in detail and last year only as a summary, and a pen per sensor (series) is what limits how many sensors you can run.",
        sim=None,
        walk=[
            ("Write to an in-memory head block and a log", "Points are appended in time order; the log protects against a crash."),
            ("Flush immutable compressed blocks", "Delta-of-delta timestamps and XOR-compressed values: bytes per point drop sharply."),
            ("Query by series and time range", "An index maps label sets to series; blocks outside the range are skipped."),
            ("Downsample and expire", "Roll up older data to coarser resolutions; delete raw data by retention."),
            ("Watch the cardinality", "Reject or limit labels with unbounded values."),
        ],
        groups=[
            dict(title="Delta-of-delta compression and downsampling, measured", cmds=[
                dict(c=r'''python3 - <<'EOF'
import random, struct, zlib
rng = random.Random(3)
n = 3600 * 6                                            # six hours of one metric at one point per second... sampled every 10 s would be 2,160; use 21,600 points
ts = [1_700_000_000 + i * 10 + (1 if rng.random() < 0.02 else 0) for i in range(n)]       # every 10 s, with a rare 1 s jitter
vals = [round(40 + 10 * (1 if (i // 500) % 2 else 0) + rng.random(), 1) for i in range(n)]  # a slowly varying CPU percentage
raw = b''.join(struct.pack('<qd', t, v) for t, v in zip(ts, vals))
print('%d points; raw encoding (8-byte timestamp + 8-byte float): %d bytes = %.1f bytes/point' % (n, len(raw), len(raw) / n))
# delta of delta on the timestamps
deltas = [ts[0]] + [b - a for a, b in zip(ts, ts[1:])]
dod = [deltas[0], deltas[1]] + [b - a for a, b in zip(deltas[1:], deltas[2:])]
zeros = sum(1 for x in dod[2:] if x == 0)
print('timestamps: delta-of-delta is zero for %.1f%% of points (they cost ~1 bit each in a real encoder)' % (100 * zeros / (n - 2)))
# values: store the integer tenths and compress deltas
ints = [int(round(v * 10)) for v in vals]; vd = [ints[0]] + [b - a for a, b in zip(ints, ints[1:])]
packed = struct.pack('<%dq' % n, *dod) + struct.pack('<%dh' % n, *[max(-32768, min(32767, x)) for x in vd])
print('timestamps + values as deltas, then a general compressor (zlib): %d bytes = %.2f bytes/point (%.0fx smaller than raw)' % (len(zlib.compress(packed, 9)), len(zlib.compress(packed, 9)) / n, len(raw) / len(zlib.compress(packed, 9))))
print()
print('retention tiers for 500,000 points/s of raw data (16 bytes raw, ~1.5 bytes compressed):')
per_day = 500_000 * 86400
print('  raw for 14 days:               %7.0f TB uncompressed, %5.1f TB compressed' % (per_day * 14 * 16 / 1e12, per_day * 14 * 1.5 / 1e12))
print('  1-minute averages for 90 days: %7.1f TB compressed (6x fewer points per series than 10 s raw)' % (per_day / 6 / 6 * 90 * 1.5 / 1e12 / 1))
print('  1-hour averages for 5 years:   %7.2f TB compressed' % (per_day / 360 / 6 * 365 * 5 * 1.5 / 1e12))
EOF''',
                     e="Why time-series stores are small. A regular scrape interval makes the **delta of the delta** of the timestamps almost always zero, which costs about one bit per point in a real encoder; slowly changing values compress as small deltas. Even this crude version (deltas plus a general-purpose compressor) shrinks 16 bytes per point to a small fraction, and production encoders get to 1 to 2 bytes. The retention arithmetic at the bottom shows why downsampling is essential at fleet scale: keeping raw data for two weeks costs tens of terabytes, while hourly averages for five years cost a tiny fraction of that.",
                     annot=[("21600 points; raw encoding ...: 16.0 bytes/point", "the naive layout"),
                            ("timestamps: delta-of-delta is zero for 93.6% of points", "regular intervals: almost no information per timestamp (the occasional 1 s jitter breaks the pattern)"),
                            ("... as deltas, then zlib: 16486 bytes = 0.76 bytes/point (21x smaller than raw)", "compression exploits the regularity and slow change (this synthetic data is very regular; real data compresses to about 1 to 2 bytes)"),
                            ("raw for 14 days: 10 TB uncompressed, 0.9 TB compressed; 1-hour averages for 5 years: 0.05 TB", "downsampling and retention bound the storage")]),
                dict(c=r'''python3 - <<'EOF'
import statistics
# Downsample 6 hours of 10-second points to 1-minute rollups, keeping min / max / sum / count so more questions can still be answered.
import random
rng = random.Random(5)
points = [(i * 10, 40 + rng.random() * 5 + (30 if 9000 <= i * 10 < 9010 else 0)) for i in range(2160)]       # a brief spike: one 10-second sample at t=9000 s
rolled = {}
for t, v in points:
    b = t // 60
    r = rolled.setdefault(b, {'min': v, 'max': v, 'sum': 0.0, 'count': 0})
    r['min'] = min(r['min'], v); r['max'] = max(r['max'], v); r['sum'] += v; r['count'] += 1
print('raw points: %d   1-minute rollups: %d' % (len(points), len(rolled)))
spike_minute = 9000 // 60
r = rolled[spike_minute]
print('the spike minute, rolled up with avg only:  avg %.1f   <- the spike is diluted' % (r['sum'] / r['count']))
print('the spike minute, rolled up with max kept:  max %.1f   <- the spike is still visible (and alertable)' % r['max'])
print('a normal minute:                            avg %.1f   max %.1f' % (rolled[10]['sum'] / rolled[10]['count'], rolled[10]['max']))
print()
print('cardinality: how many series does one metric create?')
for labels, n in (('host (100,000)', 100_000), ('host x endpoint (20)', 2_000_000), ('host x endpoint x status (5)', 10_000_000), ('... x user_id (1,000,000)', 10_000_000_000_000)):
    print('  http_requests_total{%-30s -> %s series%s' % (labels + '}', '{:,}'.format(n), '   <- unusable' if n > 1e9 else ''))
EOF''',
                     e="Two traps of rollups and labels. A one-minute **average** dilutes a ten-second spike to almost nothing, so a good rollup keeps **min, max, sum and count** as well, so spikes remain visible and alertable, and averages and rates can be recomputed correctly for any window. The cardinality table is the other real limit: every distinct label combination is a separate series with its own memory and index, so adding `endpoint` and `status` multiplies by tens, and adding a high-cardinality label such as a user id multiplies by millions and takes the system down. Per-user detail belongs in logs and traces, not in metric labels.",
                     annot=[("the spike minute, rolled up with avg only: avg ~47", "the average dilutes a 30-point, 10-second spike"),
                            ("the spike minute, rolled up with max kept: max ~73", "keeping the max preserves what alerts need"),
                            ("http_requests_total{... x user_id ...} -> 10,000,000,000,000 series <- unusable", "unbounded labels, not point rate, are what kill metrics systems")]),
            ]),
        ],
        scenario=dict(
            title="\"Design a metrics monitoring system for 100,000 servers.\"",
            ask="A time-series design question that also tests alerting and cost thinking.",
            clarify=[("How many metrics per server, scrape interval, retention, query patterns and alerting latency?", "Assume 50 metrics per server every 10 seconds, 2 weeks of raw data, 1 year rolled up, alert within 30 seconds.")],
            think=[("Estimate.", "100,000 x 50 / 10 s = 500,000 points per second; 43 billion per day; at 1.5 bytes compressed about 65 GB a day: 900 GB for two weeks raw. The series count is 5 million (before extra labels)."),
                   ("Ingest.", "Agents on hosts expose or push metrics; collectors scrape or receive and batch; a queue (Kafka) decouples collection from storage for bursts; writers append to an in-memory head block with a WAL and flush compressed blocks."),
                   ("Storage.", "A time-series database partitioned by series hash and time block, replicated 2 to 3 times; compression (delta-of-delta, XOR); retention tiers via background downsampling that keeps min, max, sum and count."),
                   ("Query.", "A label index maps selectors to series; time-range pruning; pre-aggregated rollups for dashboards; caching of dashboard queries; limits on query cost (series count, range)."),
                   ("Alerting.", "A separate evaluator runs rules every 15 to 30 seconds against recent data in memory; alert state in a durable store; deduplication, grouping, silencing and routing to on-call; alerts on symptoms against SLOs; the alerting path must be more reliable than what it watches (a watchdog alert proves it works)."),
                   ("Scaling and cardinality.", "Shard by series hash; cap label cardinality per metric; reject high-cardinality labels at ingest; hierarchical or federated collection per region or cluster."),
                   ("Failure.", "Collector loss: buffering and retries; a storage node loss: replicas; a region loss: per-region monitoring that is itself monitored from outside; accept gaps rather than block hosts.")],
            answer=["\"Fifty metrics from a hundred thousand servers every ten seconds is about 500,000 points per second, 43 billion a day, but compressed at about a byte and a half each that is roughly 65 gigabytes a day, so two weeks of raw data is under a terabyte: very manageable. Collectors scrape or receive metrics and put them on a queue so bursts do not hurt storage; writers append to an in-memory block with a write-ahead log and flush compressed immutable blocks using delta-of-delta timestamps and XOR-encoded values; storage is sharded by series and time and replicated.",
                    "Background jobs downsample to one-minute and one-hour rollups keeping min, max, sum and count, with retention tiers. Queries use a label index and time-range pruning with cached dashboards and cost limits. A separate evaluator runs alert rules every fifteen to thirty seconds against recent data, groups and routes alerts, and is watched by a watchdog alert. The real limit is series cardinality, so I cap label cardinality and keep per-user detail out of metrics. If collectors or a node fail, buffering and replicas cover it, and each region's monitoring is itself monitored from outside.\""],
            follow=[("Push or pull collection?", "Pull (scrape) makes targets simple and detects dead targets by failure to scrape; push suits short-lived jobs and firewalled networks; large systems use both."),
                    ("How do you alert without false alarms?", "Alert on user-visible symptoms against an SLO with burn-rate windows, require the condition to persist, group related alerts and route by ownership."),
                    ("What happens when the monitoring system itself fails?", "Monitor it independently (a separate system or provider), use a heartbeat/watchdog alert that must always fire, and keep alerting capacity simple and over-provisioned.")],
            slips=["Ignoring cardinality.", "Averages-only rollups.", "Alerting that depends on the system being monitored."],
        ),
        quick=[
            ("Why do timestamps compress well in time series?", "Regular intervals make the delta of the delta almost always zero."),
            ("What should a rollup keep besides the average?", "Min, max, sum and count, so spikes and exact aggregates remain available."),
            ("What is cardinality in a metrics system?", "The number of distinct series (label combinations); unbounded labels can overwhelm the system."),
        ],
        traps=[
            "A user id (or request id) as a metric label.",
            "Downsampling to averages only: spikes disappear from history.",
            "Alerting and dashboards served by the same system that is failing.",
        ],
    ),
]
