"""Systems Mastery S29: media, autocomplete and booking (reference module behind the video, autocomplete, and booking and payments pages)."""
import sysviz as v

PG = r'''export EX=$HOME/ex PGB=$(ls -d /usr/lib/postgresql/*/bin | head -1); export PATH=$PGB:$PATH
mkdir -p $EX; [ -d $EX/pg ] || initdb -D $EX/pg -A trust -U learner >/dev/null
pg_ctl -D $EX/pg -o "-p 5591 -k $EX -c listen_addresses='' -c fsync=off" -l $EX/pg.log -w start >/dev/null
createdb -h $EX -p 5591 -U learner app 2>/dev/null || true
pq() { psql -X -q -h $EX -p 5591 -U learner -d app "$@"; }'''

LESSONS = [
    dict(
        title="Video streaming: segments, bitrate ladders and adaptive playback",
        tier="hot",
        situation="Millions of people press play on phones, laptops and televisions, on fast Wi-Fi and on a train. One file cannot serve them all. Video is cut into short segments in several qualities, and the player chooses a quality for each segment based on what it measures.",
        learn=["Segments and playlists", "The bitrate ladder", "Adaptive bitrate selection and rebuffering"],
        model=[
            "A video is **encoded once into several renditions** (a **bitrate ladder**, for example 235 kbps, 750 kbps, 1.75 Mbps and 4.3 Mbps), and each rendition is cut into **short segments** (2 to 10 seconds). A **manifest** (an HLS or DASH playlist) lists the renditions and their segment URLs. Segments are plain files served over HTTP from a **CDN**, so the whole delivery system is just caching. The **player** downloads segment after segment, measures how fast each download was and its **buffer** level, and **adapts**: it picks a higher rendition when the network is fast and the buffer is healthy, and a lower one when it risks running dry, because an empty buffer means a stall (**rebuffering**), which viewers hate more than lower quality.",
            "On the server side the hard work is **ingest and transcoding** (a pipeline of parallel jobs per segment and rendition, driven by a queue), **storage** (an object store, cold tiers for rarely watched titles) and **delivery** (CDN edges, popular titles pre-positioned near viewers, origin shielding). **Live** streaming uses the same segments produced continuously, so end-to-end delay is a few segments. Costs are dominated by **bandwidth**, which is why CDN hit ratio and efficient codecs matter.",
        ],
        analogy="Delivering a long novel to readers by post: you print it in several editions (small print, large print, audio), tear it into chapters, and the reader's assistant orders the next chapter in whichever edition the current postal service can deliver before they finish reading.",
        sim=None,
        walk=[
            ("Encode into a ladder of renditions", "Several qualities of the same video."),
            ("Cut each into short segments and list them in a manifest", "A playlist of URLs."),
            ("Serve segments from a CDN", "Ordinary cacheable HTTP files."),
            ("The player measures and adapts", "Throughput and buffer decide the next segment's quality."),
            ("Avoid stalls above all", "Drop quality before the buffer empties."),
        ],
        groups=[
            dict(title="A manifest, and adaptive playback against a fixed quality", cmds=[
                dict(c=r'''python3 - <<'EOF'
LADDER = [('240p', 235), ('480p', 750), ('720p', 1750), ('1080p', 4300)]       # name, kilobits per second
SEG = 4                                                                          # seconds per segment
print('#EXTM3U   (a master playlist: one line per rendition)')
for name, kbps in LADDER: print('#EXT-X-STREAM-INF:BANDWIDTH=%d,RESOLUTION=%s\n%s/index.m3u8' % (kbps * 1000, {'240p': '426x240', '480p': '854x480', '720p': '1280x720', '1080p': '1920x1080'}[name], name))
print()
print('#EXTM3U   (a media playlist for 720p: the first 4 of the segments)')
print('#EXT-X-TARGETDURATION:%d' % SEG)
for i in range(4): print('#EXTINF:%d.0,\nseg%04d.ts' % (SEG, i))
print()
dur = 2 * 3600
print('a 2-hour film at each quality (one rendition):')
for name, kbps in LADDER: print('  %-6s %5d kbps  %6.2f GB   %d segments of %d s' % (name, kbps, kbps * 1000 / 8 * dur / 1e9, dur // SEG, SEG))
print('the whole ladder costs %.1f GB per title before replication: storage is cheap compared with delivery bandwidth.' % (sum(k for _, k in LADDER) * 1000 / 8 * dur / 1e9))
EOF''',
                     e="What the player and the CDN actually see. The **master playlist** advertises each rendition with its bandwidth and resolution; the **media playlist** lists segment files, four seconds each. A two-hour film is 1,800 small files per rendition, served as ordinary static files, which is why a CDN can cache and deliver them. The ladder multiplies storage by about two and a half (all four renditions together), a small price compared with the bandwidth cost of delivery.",
                     annot=[("#EXT-X-STREAM-INF:BANDWIDTH=235000,RESOLUTION=426x240", "one rendition advertised with its bitrate and size"),
                            ("#EXTINF:4.0, seg0000.ts", "a four-second segment file: the unit of download and of adaptation"),
                            ("1080p 4300 kbps ... 1800 segments of 4 s", "a two-hour film is a few thousand small cacheable files per rendition")]),
                dict(c=r'''python3 - <<'EOF'
import random
rng = random.Random(11)
LADDER = [235, 750, 1750, 4300]                       # kbps
SEG = 4                                                # seconds of video per segment
# a bandwidth trace: a phone moving between good Wi-Fi, a tunnel, and 4G (kbps), changing every segment time
bw = []
for phase, (lo, hi, n) in enumerate(((5000, 8000, 20), (300, 900, 10), (1500, 3500, 20), (200, 600, 8), (3000, 6000, 12))):
    bw += [rng.uniform(lo, hi) for _ in range(n)]
def play(chooser):
    buffer, t, stalls, stall_time, rates, last_tp = 8.0, 0.0, 0, 0.0, [], bw[0]
    for i, tp in enumerate(bw):
        rate = chooser(last_tp, buffer)
        download = rate * SEG / tp                                   # seconds to download this segment at the current bandwidth
        if download > buffer:                                        # the buffer runs dry while downloading: a stall
            stalls += 1; stall_time += download - buffer; buffer = 0.0
        else: buffer -= download
        buffer = min(buffer + SEG, 30.0); last_tp = tp; rates.append(rate)
    return stalls, stall_time, sum(rates) / len(rates)
fixed_high = lambda tp, buf: 4300
fixed_low = lambda tp, buf: 235
def adaptive(tp, buf):
    safe = tp * (0.6 if buf < 10 else 0.85)                          # be cautious when the buffer is low
    return max([r for r in LADDER if r <= safe] or [LADDER[0]])
print('70 segments of 4 s (%d s of video) over a bandwidth trace with a tunnel in it:' % (70 * SEG))
print('%-26s %7s %12s %15s' % ('strategy', 'stalls', 'stalled for', 'average quality'))
for name, f in (('always 1080p (4300 kbps)', fixed_high), ('always 240p (235 kbps)', fixed_low), ('adaptive', adaptive)):
    s, st, avg = play(f); print('%-26s %7d %10.1f s %11.0f kbps' % (name, s, st, avg))
EOF''',
                     e="Adaptive bitrate on a bumpy network. The viewer moves through good Wi-Fi, a tunnel and a weak 4G area. **Always playing the best quality** stalls repeatedly whenever the bandwidth drops below the video's bitrate. **Always playing the lowest quality** never stalls but looks poor throughout. The **adaptive** player measures the last download and its buffer, chooses the highest rendition it can finish in time (more cautiously when the buffer is low), and gets close to the best of both: very few or no stalls with a much better average quality than the lowest setting. Real players (and Netflix's research on this) use more refined buffer-based algorithms, but the trade-off is the same.",
                     annot=[("always 1080p (4300 kbps): 43 stalls, 766 s stalled", "ignores the network: runs dry whenever bandwidth drops, and the stalls pile up"),
                            ("always 240p (235 kbps): 0 stalls, average 235 kbps", "safe but poor quality for the whole film"),
                            ("adaptive: 2 stalls (18.6 s), average 2192 kbps", "chooses quality per segment from throughput and buffer: about nine times the quality of 240p, with a tiny fraction of the stalls")]),
            ]),
        ],
        scenario=dict(
            title="\"Design YouTube or Netflix: upload, process and stream video to millions of viewers.\"",
            ask="A staple design question. They want the upload and processing pipeline, storage, delivery through a CDN and adaptive playback, with numbers.",
            clarify=[("Video on demand or live? Upload volume, viewers, regions, device types, and are downloads allowed offline?", "Assume video on demand: 500 hours uploaded per minute, a billion hours watched per day, global audience, all devices.")],
            think=[("Estimate.", "500 hours a minute is 30,000 hours of source video per hour. A billion hours watched a day at an average 3 Mbps is about 1.4 exabytes a day of delivery: bandwidth dominates every other cost."),
                   ("Upload path.", "Resumable multipart upload straight to an object store (presigned URLs); an event creates a processing job in a queue."),
                   ("Processing pipeline.", "Split the source into chunks, transcode chunks in parallel into the bitrate ladder and several codecs, package segments and manifests (HLS and DASH), generate thumbnails, run safety checks; a workflow engine tracks the DAG; retries and idempotent tasks."),
                   ("Storage.", "Segments and manifests in an object store; metadata (title, owner, status, renditions) in a database; hot titles on faster tiers, rarely watched on cold storage."),
                   ("Delivery.", "CDN edges serve segments (cache hit ratio is the cost lever); popular and new titles pushed to edges ahead of demand; origin shielding; ISP-embedded caches for the biggest services."),
                   ("Playback.", "The player fetches the manifest and adapts per segment; start-up time matters (first segment small and low quality); DRM for licensed content; analytics for quality of experience."),
                   ("Scale and failure.", "Processing is asynchronous and can lag without affecting playback of existing titles; multi-region origins; a CDN outage falls back to other CDNs; hot new releases need pre-warming."),
                   ("Trade-offs.", "Storage and encode cost versus quality options; segment length (latency versus overhead); codec efficiency versus device support.")],
            answer=["\"Bandwidth is the dominant cost: a billion hours a day at a few megabits is on the order of an exabyte a day, so everything serves the CDN. Uploads go straight to an object store with resumable multipart upload and presigned URLs, and an event queues a processing job. The pipeline splits the source into chunks, transcodes them in parallel into a ladder of renditions and codecs, packages short segments and HLS or DASH manifests, generates thumbnails and runs safety checks, orchestrated as a workflow with retries and idempotent tasks.",
                    "Segments sit in an object store with metadata in a database. Viewers fetch the manifest and the player picks a rendition per segment from measured throughput and buffer, dropping quality before the buffer runs dry. CDN edges serve the segments, with popular titles pre-positioned and origin shielding to protect the store. Processing can lag without affecting playback of existing titles, and a CDN failure falls back to another. The trade-offs are encode and storage cost against quality options, segment length against latency, and codec efficiency against device support.\""],
            follow=[("Why short segments rather than one big file?", "Adaptation per segment, fast start, seeking, cacheable small objects and resumable delivery."),
                    ("How do you start playback quickly?", "Start with a low rendition and a small first segment, prefetch, keep manifests small and served from the edge."),
                    ("How would live streaming differ?", "Segments are produced continuously by a packager, the manifest is updated, end-to-end delay is a few segments, and a CDN with low-latency modes distributes them.")],
            slips=["Serving one big file from the application servers.", "No transcoding or bitrate ladder.", "Ignoring that bandwidth, not compute, is the main cost."],
        ),
        quick=[
            ("What is a bitrate ladder?", "The set of renditions of one video at different bitrates and resolutions."),
            ("What does an adaptive player choose each segment?", "The highest rendition it can download in time given measured throughput and buffer."),
            ("What is the main cost of streaming?", "Delivery bandwidth: so CDN hit ratio and codec efficiency matter."),
        ],
        traps=[
            "Optimising for peak quality and ignoring stalls: viewers prefer lower quality to buffering.",
            "Transcoding on upload in the request path: it must be asynchronous.",
            "One CDN with no fallback.",
        ],
    ),
    dict(
        title="Autocomplete: a trie with precomputed top suggestions",
        tier="hot",
        situation="As you type three letters into a search box, ten plausible completions appear in under 100 milliseconds. Scanning every past query on every keystroke would be far too slow; the trick is to do the work in advance.",
        learn=["Prefix search with a trie", "Storing the top suggestions at each node", "Updating suggestions from a query log", "Serving at very low latency"],
        model=[
            "Autocomplete answers \"what are the most popular queries that start with this prefix?\" for every keystroke. A **trie** (prefix tree) stores queries character by character so that all queries sharing a prefix share a path; to answer a prefix, walk down to its node. The key optimisation is to **precompute and store the top K suggestions (by popularity) at every node**, so a lookup is just a walk down the prefix and a read, independent of how many queries start with it. A **builder** job periodically aggregates the **query log** into counts (with recency weighting) and rebuilds the trie offline; the serving tier loads each new version atomically and serves it from **memory**.",
            "Because the answers only need to be roughly current, the system separates **offline aggregation** (batch or streaming counts over the query log) from **online serving** (a read-only, in-memory structure, sharded by prefix range and replicated, cached at the edge). The client helps: it **debounces** keystrokes, caches previous prefixes and cancels stale requests. Add **personalisation**, **filtering** of unsafe or removed suggestions, **typo tolerance** and trending detection as refinements. Everything is about latency: a few milliseconds of server time, with the network the dominant cost.",
        ],
        analogy="A phone book where, at the top of every letter-combination page, someone has already written the five most-called numbers. You never have to read the page; you read the header.",
        sim=None,
        walk=[
            ("Log every query", "With counts and timestamps."),
            ("Aggregate offline", "Counts per query, recent behaviour weighted more."),
            ("Build the trie with top-K at every node", "Precomputed so reads do no ranking."),
            ("Load the new version atomically", "Serve it from memory, replicated and sharded."),
            ("Keep the client light", "Debounce, cache, cancel stale requests."),
        ],
        groups=[
            dict(title="Scanning versus a trie with stored suggestions", cmds=[
                dict(volatile=True, c=r'''python3 - <<'EOF'
import random, time
rng = random.Random(6)
syll = ['ca', 'mer', 'ra', 'cam', 'pus', 'cat', 'ch', 'cap', 'tain', 'ca', 'lo', 'ri', 'es', 'sho', 'pe', 'ph', 'one', 'lap', 'top', 'pri', 'ce']
queries = {}
for _ in range(60000):                                           # a query log: 60,000 distinct queries with a skewed popularity
    q = ''.join(rng.choice(syll) for _ in range(rng.randint(2, 4)))
    queries[q] = queries.get(q, 0) + int(1000 / (1 + rng.random() * 400)) + 1
K = 5
class Node:
    __slots__ = ('kids', 'top')
    def __init__(self): self.kids, self.top = {}, []
root = Node()
t0 = time.perf_counter()
for q, c in queries.items():
    n = root
    for ch in q:
        n = n.kids.setdefault(ch, Node())
        n.top.append((c, q))
        if len(n.top) > 4 * K: n.top.sort(reverse=True); del n.top[K:]          # keep only the best few at each node
def finish(n):
    n.top.sort(reverse=True); del n.top[K:]
    for kid in n.kids.values(): finish(kid)
finish(root)
build_ms = (time.perf_counter() - t0) * 1000
def suggest_trie(prefix):
    n = root
    for ch in prefix:
        n = n.kids.get(ch)
        if n is None: return []
    return [q for c, q in n.top]
def suggest_scan(prefix): return [q for c, q in sorted(((c, q) for q, c in queries.items() if q.startswith(prefix)), reverse=True)[:K]]
print('built a trie over %d queries in %.0f ms (done offline, not per request)' % (len(queries), build_ms))
for p in ('ca', 'cam', 'camp'):
    print('prefix %-5r top %d: %s' % (p, K, suggest_trie(p)))
print('same answers as scanning the whole log: %s' % all(suggest_trie(p) == suggest_scan(p) for p in ('c', 'ca', 'cam', 'camp', 'ph', 'lap')))
N = 2000
t = time.perf_counter()
for _ in range(N): suggest_scan('cam')
scan = (time.perf_counter() - t) / N * 1000
t = time.perf_counter()
for _ in range(N): suggest_trie('cam')
trie = (time.perf_counter() - t) / N * 1000
print('per keystroke: scanning the log %.2f ms, trie lookup %.4f ms (%.0f times faster)' % (scan, trie, scan / trie))
EOF''',
                     e="Why the work is done in advance. The trie is built once from the query log, keeping only the **top five queries at every node**. A keystroke is then a walk down two or three characters and a read of a short list: no scanning, no sorting. The experiment checks that the answers are **identical** to scanning the entire log, and measures the gap: the trie lookup takes microseconds against milliseconds for the scan, and the gap grows with the size of the log. In production the build runs as a periodic batch job over the aggregated log and the result is swapped into memory atomically.",
                     annot=[("built a trie over 26214 queries in ~290 ms (done offline, not per request)", "the expensive work happens in the builder, not per keystroke"),
                            ("prefix 'cam' top 5: ['cammer', 'camca', ...]", "the best five completions are stored at the node: a lookup is just a read"),
                            ("same answers as scanning the whole log: True", "precomputation changes the cost, not the answer"),
                            ("per keystroke: scanning the log 1.09 ms, trie lookup 0.0003 ms (thousands of times faster)", "the lookup cost no longer depends on the size of the log")]),
            ]),
        ],
        scenario=dict(
            title="\"Design search autocomplete (typeahead) for a search box with 100 million daily users.\"",
            ask="A classic that tests data structure choice, the offline/online split and latency thinking.",
            clarify=[("How many suggestions, how fresh must they be, personalised or global, languages, and the latency budget?", "Assume top 5, refreshed hourly (trending faster), global with light personalisation, under 100 ms end to end.")],
            think=[("Estimate.", "100M users x 10 searches x about 5 keystrokes is about 5 billion suggestion requests a day: roughly 60,000 per second, peak 200,000. Each must be answered from memory in a few milliseconds."),
                   ("Data structure.", "A trie with the top K (about 5 to 10) suggestions precomputed at every node; or a prefix-to-suggestions hash table for prefixes up to a length. Memory: tens of millions of popular queries fit on a few machines."),
                   ("Offline pipeline.", "Log queries to a stream; aggregate counts per query with recency decay in batch (hourly) and streaming (for trending); filter unsafe or removed queries; build a new trie version; publish it as an immutable snapshot."),
                   ("Serving.", "A stateless suggestion service loads the snapshot into memory, sharded by prefix range if needed, with replicas; atomic swap on a new version; edge cache for the shortest prefixes."),
                   ("Client behaviour.", "Debounce (send after a short pause), cache responses by prefix, cancel in-flight requests when the next key arrives, send only after the first character or two."),
                   ("Refinements.", "Personalisation by blending global top K with the user's recent searches; typo tolerance (edit distance, phonetic matching); localisation; real-time trending."),
                   ("Failure and trade-offs.", "If the builder fails, serve the last snapshot; freshness versus build cost; memory versus K and prefix depth; privacy and safety filtering.")],
            answer=["\"That is about five billion requests a day, roughly 60,000 a second and 200,000 at peak, each needing an answer in a few milliseconds, so it must be served from memory. I would use a trie with the top five suggestions precomputed at every node, so a keystroke is a walk down the prefix and a read, independent of the number of queries.",
                    "The expensive work is offline: queries are logged to a stream, counts are aggregated with recency decay in hourly batches plus a streaming path for trending, unsafe or removed queries are filtered, and a new trie snapshot is built and swapped in atomically on stateless suggestion servers, sharded by prefix range and replicated, with an edge cache for short prefixes. The client debounces keystrokes, caches by prefix and cancels stale requests. If the builder fails we keep serving the last snapshot. I would add light personalisation and typo tolerance on top.\""],
            follow=[("Trie or hash table of prefixes?", "A hash table from prefix to top K is simpler and fast but uses more memory for long prefixes; a trie shares prefixes; either way the top K is precomputed."),
                    ("How do you handle trending queries?", "A streaming aggregation over a short window boosts rising queries and merges them with the batch top K."),
                    ("How would you shard the trie?", "By prefix range (a-f, g-m, ...), balanced by traffic rather than letters, with the first characters cached at the edge.")],
            slips=["Computing rankings per keystroke.", "No offline pipeline.", "Ignoring client-side debouncing."],
        ),
        quick=[
            ("What is stored at each trie node for autocomplete?", "The top K suggestions for that prefix, precomputed."),
            ("Where does the expensive work happen?", "Offline, when aggregating the query log and building the trie."),
            ("What does the client do to cut load?", "Debounces keystrokes, caches by prefix and cancels stale requests."),
        ],
        traps=[
            "Ranking on every request.",
            "Rebuilding the trie in place while serving: swap an immutable snapshot atomically.",
            "Suggestions that include removed or unsafe queries because filtering happens only in the UI.",
        ],
    ),
    dict(
        title="Booking and payments: never sell the same seat twice, never charge twice",
        tier="hot",
        situation="Two people click \"buy\" on the last concert ticket in the same millisecond. A phone loses signal after paying and the app retries. Booking and payment systems exist to make the second sale impossible and the second charge harmless.",
        learn=["Oversell: the race and its fixes in a real database", "Holds that expire", "A double-entry ledger that always balances", "Idempotent payment requests"],
        model=[
            "**Overselling** is a read-modify-write race: both buyers read \"one seat left\" and both sell it. Prevent it **in the database**, not in the application: a **conditional update** (`update ... set sold = true where seat = 7 and sold = false`, then check the rows changed), a **unique constraint** on `(event, seat)` so the second insert fails, or a **row lock** (`select ... for update`) in a short transaction. For checkout, use a **hold with an expiry**: reserve the seat for ten minutes while the buyer pays, and release it automatically if they do not; the hold itself uses the same atomic mechanism.",
            "For money, record **every movement as a pair of entries in a double-entry ledger**: a debit and an equal credit in the same transaction, so the sum of all entries is always **zero** and any discrepancy is detectable. Never store only a balance you overwrite. Make payment requests **idempotent** with a client-generated key stored with the result, so a retry after a lost response returns the stored result instead of charging again, and **reconcile** regularly against the payment provider's records. Orchestrate the steps (hold, charge, confirm) as a **saga** with compensations (release the hold, refund) because there is no transaction across your database and the provider.",
        ],
        analogy="A box office with a numbered ticket drawer: a ticket can only be taken from the drawer once, held tickets are set aside with a timer, and every cash movement is written in the ledger twice (out of one account, into another) so the books always add up to zero.",
        sim=None,
        walk=[
            ("Make the sale atomic", "A conditional update, a unique constraint or a row lock decides the winner."),
            ("Hold the seat while the buyer pays", "A reservation with an expiry that releases automatically."),
            ("Charge with an idempotency key", "A retry returns the stored result."),
            ("Record money as balanced ledger entries", "Debit and credit together; the sum is zero."),
            ("Reconcile and compensate", "Compare with the provider; refund or release when a step fails."),
        ],
        groups=[
            dict(title="Overselling in a real database, then a ledger that balances", cmds=[
                dict(volatile=True, c=PG + r'''
pq -c "create table seats(id int primary key, sold_to text); insert into seats values (7, null)"
buyer() { local who=$1; local free; free=$(pq -At -c "select count(*) from seats where id = 7 and sold_to is null"); sleep 0.3; [ "$free" = 1 ] && pq -c "update seats set sold_to = '$who' where id = 7"; }
echo "--- naive: check that the seat is free, then update (two buyers at the same moment):"
buyer alice & buyer bob & wait
echo "sold to: $(pq -At -c 'select sold_to from seats where id = 7')   (both thought it was free: the last write won, and BOTH were told they got it)"
pq -c "update seats set sold_to = null"
echo "--- conditional update: the database decides, atomically:"
buy() { r=$(pq -At -c "update seats set sold_to = '$1' where id = 7 and sold_to is null returning id"); sleep 0.1; [ -n "$r" ] && echo "$1: GOT THE SEAT" || echo "$1: sorry, sold out"; }
buy alice & buy bob & wait
echo "sold to: $(pq -At -c 'select sold_to from seats where id = 7')"
pg_ctl -D $EX/pg -m fast stop >/dev/null 2>&1''',
                     e="The race, then the fix, with real concurrent clients. In the **naive** version both buyers check that the seat is free, both see it free, and both update: **both** are told they succeeded and only the last write remains, an oversold seat. The **conditional update** puts the decision inside one atomic database statement: the first update changes one row, and the second finds `sold_to` already set and changes **zero rows**, so exactly one buyer is told sold out. Always make the *check* and the *change* a single operation.",
                     annot=[("sold to: bob (or alice): both thought it was free", "the check and the update were separate steps: both buyers were told yes"),
                            ("alice: GOT THE SEAT / bob: sorry, sold out", "the conditional update changed one row for the winner and none for the loser"),
                            ("sold to: alice", "exactly one buyer holds the seat")]),
                dict(volatile=True, c=PG + r'''
pq <<'EOF'
create table accounts(id text primary key);
insert into accounts values ('customer:ana'), ('merchant:shop'), ('fees');
create table ledger(id bigserial primary key, txn text not null, account text not null references accounts, amount_cents bigint not null);
create table payments(idem_key text primary key, txn text not null, amount_cents bigint not null);
create function pay(k text, cust text, amt bigint) returns text language plpgsql as $$
declare t text;
begin
  select txn into t from payments where idem_key = k;
  if t is not null then return 'replayed ' || t; end if;                       -- a retry: return the stored result, charge nothing
  t := 'txn-' || k;
  insert into payments values (k, t, amt);
  insert into ledger(txn, account, amount_cents) values (t, cust, -amt), (t, 'merchant:shop', amt - amt / 50), (t, 'fees', amt / 50);   -- debit = credits
  return 'charged ' || t;
end $$;
EOF
echo "--- the first request, then the client retries three times (the response was lost):"
for i in 1 2 3 4; do echo "attempt $i: $(pq -At -c "select pay('order-81', 'customer:ana', 4999)")"; done
echo "--- the ledger (every movement appears as balanced entries):"
pq -c "select account, amount_cents from ledger order by id"
echo "sum of ALL entries (must be zero): $(pq -At -c 'select sum(amount_cents) from ledger')"
echo "payments recorded for this order: $(pq -At -c 'select count(*) from payments')   money taken from ana: $(pq -At -c "select -sum(amount_cents) from ledger where account = 'customer:ana'") cents"
pg_ctl -D $EX/pg -m fast stop >/dev/null 2>&1''',
                     e="A payment as a ledger transaction, retried four times. The idempotency key `order-81` is stored with the result, so attempts two to four return `replayed txn-order-81` and **charge nothing**: Ana is debited once. Each payment writes **balanced entries**: Ana's debit equals the merchant's credit plus the fee, in one transaction, so the **sum of every entry in the ledger is exactly zero**. That invariant is what auditors and reconciliation jobs check: any non-zero total means money appeared or vanished. (A real system also passes the idempotency key to the payment provider and reconciles against their settlement files.)",
                     annot=[("attempt 1: charged txn-order-81 / attempts 2 to 4: replayed txn-order-81", "the stored key makes retries harmless"),
                            ("customer:ana -4999 / merchant:shop 4900 / fees 99", "a debit and its matching credits"),
                            ("sum of ALL entries (must be zero): 0", "the double-entry invariant: money is moved, never created"),
                            ("payments recorded for this order: 1   money taken from ana: 4999 cents", "one charge despite four requests")]),
            ]),
        ],
        scenario=dict(
            title="\"Design a ticket booking system like Ticketmaster. How do you avoid double booking and handle payment failures?\"",
            ask="The booking and payments capstone. They want atomic seat allocation, holds, payment orchestration and failure handling.",
            clarify=[("Peak demand (a famous concert), seat maps or general admission, hold time, payment providers, refunds?", "Assume 50,000 seats on sale at once with 1 million waiting, seat maps, 10 minute holds, an external payment provider.")],
            think=[("Estimate and shape.", "A flash sale: a million people, 50,000 seats. The catalogue reads are cacheable; the writes concentrate on a few hot rows (seats). Protect the booking path with a queue or waiting room."),
                   ("Atomic seat allocation.", "Seats table with a unique constraint or a conditional update (`where status = 'available'`), in a short transaction; the database is the arbiter. Never check in the application and update separately."),
                   ("Holds.", "Moving a seat to `held` with an expiry (hold_until) in the same atomic update; a sweeper or the next reader releases expired holds; the buyer has ten minutes to pay."),
                   ("Waiting room.", "Admit users to the booking flow at a controlled rate through a queue, so the database sees a steady load rather than a million simultaneous requests."),
                   ("Payment.", "An idempotency key per attempt; call the provider; on success mark the seat sold and write ledger entries in one transaction; on failure or timeout the hold expires or is released. A saga handles the steps and compensations (refund if the seat cannot be confirmed)."),
                   ("Unknown outcomes.", "A timeout from the provider is unknown: record a pending payment and reconcile via the provider's status API or webhooks before releasing or confirming."),
                   ("Consistency and scale.", "Shard by event so each hot event lives on one shard with strong consistency; read replicas and caches for browsing; accept slightly stale availability counts but never stale decisions on purchase."),
                   ("Operations.", "Idempotent webhooks, reconciliation jobs, ledger invariants (sum zero), alerts on stuck holds and pending payments.")],
            answer=["\"The browsing side is cacheable, but the booking side concentrates a million people on a few thousand rows, so I put a waiting room in front that admits users at a controlled rate. Seat allocation is decided by the database: a conditional update from available to held with an expiry, or a unique constraint, in one short transaction, never a check in the application followed by a separate update. A hold lasts ten minutes and expires automatically.",
                    "Payment uses an idempotency key per attempt. On success one transaction marks the seat sold and writes balanced ledger entries; on failure the hold expires or is released. A timeout from the provider is an unknown outcome, so I record the payment as pending and reconcile through the provider's status API or webhooks before confirming or releasing, with refunds as compensations in a saga. I shard by event so each hot event has one strongly consistent home, use caches and replicas for browsing, and monitor stuck holds, pending payments and the ledger invariant that all entries sum to zero.\""],
            follow=[("Pessimistic lock or conditional update?", "A conditional update is simpler and holds no lock while the user decides; a row lock works for short critical sections but must never span the payment call."),
                    ("What if the payment succeeds after the hold expired?", "Check the seat inside the confirmation transaction: if it was sold to someone else, refund automatically (a compensation), and tell the buyer."),
                    ("How do you stop bots?", "Waiting room with proof of work or verified accounts, per-user and per-IP limits, purchase caps, and risk scoring.")],
            slips=["Checking availability in the application and updating separately.", "Holding a database lock while waiting for payment.", "Treating a payment timeout as a failure."],
        ),
        quick=[
            ("How do you prevent overselling?", "Make check and change one atomic database operation: a conditional update, unique constraint or row lock."),
            ("What invariant does a double-entry ledger give?", "Every transaction's entries sum to zero, so the total of all entries is always zero."),
            ("What should you do with a payment timeout?", "Treat it as unknown: record it pending and reconcile with the provider before acting."),
        ],
        traps=[
            "Locks held across a slow external call.",
            "Storing only a mutable balance with no ledger: errors cannot be traced.",
            "Releasing a hold on a payment timeout: the charge may have succeeded.",
        ],
    ),
]

MODULE = dict(
    id="ex",
    deep=True,
    title="Video, autocomplete and booking",
    lead="Three more classic designs with their key mechanisms run for real: adaptive bitrate playback against a fixed quality on a bumpy network, an autocomplete trie with precomputed suggestions checked against a full scan, and booking and payments: an oversold seat in a real database, the atomic fix, and an idempotent double-entry ledger that always balances.",
    time="5 to 7 hours",
    why=["Video, search suggestions and ticket booking appear again and again in system design interviews and in real products. Each has one decisive mechanism, and running it makes the design choice clear."],
    outcomes=["Design adaptive video streaming.", "Design autocomplete with a precomputed trie.", "Design booking and payments with atomic allocation, holds, a ledger and idempotent charges."],
    before=["Python 3 and PostgreSQL run the experiments. The booking experiments start a private PostgreSQL as an ordinary user."],
    env=["Scratch folders are created by the commands."],
    lessons=LESSONS,
    labs=[],
    cases=[],
    cheat=[["bitrate ladder", "renditions at several bitrates; segments served by a CDN"], ["adaptive bitrate", "choose per segment from throughput and buffer; avoid stalls"], ["trie top-K", "precompute the best K suggestions at each node; build offline"], ["oversell fix", "check and change in one atomic database operation"], ["hold", "reservation with an expiry"], ["ledger", "balanced entries: the sum is zero"], ["idempotency key", "retries return the stored result"]],
    interview_intro="Reference module behind three whiteboard pages.",
    interview=[],
    selftest=[("What does an adaptive player choose?", "The highest rendition it can download in time.")],
    recall=[["ABR", "per-segment quality from throughput and buffer"]],
    sources=[
        dict(title="Apple HTTP Live Streaming (HLS) documentation", url="https://developer.apple.com/streaming/", use="Playlists and segments", license="Copyright Apple; read online", how="Link only"),
        dict(title="PostgreSQL documentation: INSERT ON CONFLICT and row locking", url="https://www.postgresql.org/docs/current/sql-insert.html", use="Atomic allocation patterns", license="PostgreSQL licence; read online", how="Link only"),
    ],
    plan=["Run each experiment and change the numbers."],
)
