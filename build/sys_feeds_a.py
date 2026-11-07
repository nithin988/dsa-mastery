"""S28 feeds, chat and notifications: part A (rig, lessons 1 and 2: news feed fan-out, chat)."""
import sysviz as v
from sys_warm2_a import RIG_REDIS as _R

RIG = _R.replace("~/warm", "~/feed").replace("$HOME/warm", "$HOME/feed").replace("6396", "6398").replace("export W=$HOME/feed", "export F=$HOME/feed").replace("$W/", "$F/").replace('. ./rig.sh; echo "rig ready in $W:', '. ./rig.sh; echo "rig ready in $F:')

FANOUT_VIZ = v.figure(
    720, 250,
    [v.box(10, 20, 330, 160, "Fan-out on write (push)", "acc", ""),
     v.text(175, 54, "post -> copy to every follower's feed", "dg-s"), v.text(175, 80, "read = one cached list: very fast", "dg-s"), v.text(175, 106, "cost: writes = followers per post", "dg-s"), v.text(175, 132, "a celebrity post = millions of writes", "dg-s"),
     v.box(380, 20, 330, 160, "Fan-out on read (pull)", "warn", ""),
     v.text(545, 54, "read = fetch posts of everyone you follow", "dg-s"), v.text(545, 80, "write = one row: very cheap", "dg-s"), v.text(545, 106, "cost: reads touch hundreds of lists", "dg-s"), v.text(545, 132, "slow reads, hot authors", "dg-s"),
     v.box(120, 196, 480, 40, "Hybrid: push for ordinary authors, pull for celebrities, merge at read time", "ok", ""),
     v.text(360, 246, "", "dg-s")],
    "Feed generation strategies", "Where you pay: at write time for every follower, or at read time for every followee")

CHAT_SEQ = v.seq(
    ["Alice's phone", "Chat service", "Bob's phone"],
    [("a->b", 0, 1, "send(conv 7, client_id c1, 'hi')"),
     ("a->b", 1, 1, "assign seq 41 in conversation 7, store"),
     ("a->b", 1, 0, "ack(c1, seq 41)", "reply"),
     ("a->b", 1, 2, "push message seq 41 (if online)"),
     ("note", 0, 2, "Bob was offline: the push is lost, nothing else is"),
     ("a->b", 2, 1, "reconnect: sync(conv 7, after seq 38)"),
     ("a->b", 1, 2, "messages 39, 40, 41", "reply"),
     ("a->b", 2, 1, "delivered up to seq 41", "reply")],
    "Chat: sequence numbers make ordering and sync simple", "The server orders messages per conversation; clients resume from the last sequence they have")

LESSONS_A = [
    dict(
        title="Design a news feed: fan-out on write, fan-out on read and the celebrity problem",
        tier="hot",
        situation="\"Design the Twitter or Facebook feed\" is the classic scale problem: reads are constant and must be instant, writes fan out to followers, and a handful of accounts have millions of followers. The whole design is one trade-off, where you do the work.",
        learn=["The two basic strategies and their costs", "Measuring write amplification with real numbers", "The celebrity problem and the hybrid", "Feed storage, ranking and pagination"],
        model=[
            "A feed shows recent posts from the people you follow. **Fan-out on write (push)**: when someone posts, copy the post id into the precomputed feed list of **every follower** (a capped list per user, in memory). Reading is then a single cheap lookup, so reads, which are the majority, are fast; the cost is **write amplification**: a post by a user with 1 million followers means 1 million list updates. **Fan-out on read (pull)**: store the post once; when a user opens the feed, fetch the recent posts of everyone they follow and merge them: writes are trivial but every read touches hundreds of lists, which is slow and expensive for a read-heavy product.",
            "Real systems use a **hybrid**: **push for ordinary authors** (cheap, because they have few followers), and **pull for celebrities** (merge their recent posts into the follower's feed at read time). A threshold (for example 100,000 followers) decides. Feed lists hold **post ids** only (a few hundred per user, capped), with the post bodies fetched from a **post cache** and the author/graph data from separate services. **Ranking** (chronological, or scored by affinity, recency and engagement) runs on the candidate list; **pagination** uses cursors (the last post id or score), never offsets. Handle **inactive users** (do not fan out to accounts that have not logged in for months: build their feed lazily on return), **deletes** (remove or filter at read time), and **hot posts** (cache aggressively). The pipeline is asynchronous: a post is acknowledged, then fan-out jobs run from a queue, so a post may take seconds to appear for some followers.",
        ],
        analogy="A newspaper delivered to every subscriber's door each morning (push: expensive for the publisher, instant for the reader) versus going to the newsstand and collecting a copy of every paper you like (pull: no delivery cost, slow for the reader). A hybrid delivers the small papers and has you fetch the one giant national edition yourself.",
        visual=[FANOUT_VIZ],
        sim=None,
        walk=[
            ("A user posts", "The post is stored once and acknowledged; fan-out happens asynchronously."),
            ("Choose push or pull by follower count", "Below the celebrity threshold: push to all followers; above it: skip the fan-out."),
            ("Followers' feed lists are updated", "A capped list of post ids per follower, newest first, in an in-memory store."),
            ("A reader opens the app", "Read the precomputed list, merge in recent posts of followed celebrities, rank, hydrate post bodies."),
            ("Page with a cursor", "Return the next page after the last seen id; never use offsets."),
        ],
        groups=[
            dict(title="Write amplification, measured on a skewed follower distribution and on real Redis", cmds=[
                dict(c=r'''python3 - <<'EOF'
import random
rng = random.Random(7)
USERS = 100_000
# follower counts follow a heavy-tailed distribution: most users have a few followers, a handful have millions
followers = [max(1, int(10 / (rng.random() ** 1.1 + 1e-9)) % 3_000_000) for _ in range(USERS)]
followers.sort(reverse=True)
posts_per_user_per_day = 1.0
total_follow_edges = sum(followers)
print('users: %d   follow edges: %s   median followers: %d   max followers: %s' % (USERS, '{:,}'.format(total_follow_edges), followers[USERS // 2], '{:,}'.format(followers[0])))
print('top 10 accounts hold %.0f%% of all follow edges' % (100 * sum(followers[:10]) / total_follow_edges))
posts = USERS * posts_per_user_per_day
push = sum(f * posts_per_user_per_day for f in followers)
print()
print('pure fan-out on write: %s list writes per day (%.0f writes per post on average, %s for the biggest account)' % ('{:,.0f}'.format(push), push / posts, '{:,}'.format(followers[0])))
for thr in (1_000_000, 100_000, 10_000):
    celebs = [f for f in followers if f >= thr]
    hybrid = sum(f for f in followers if f < thr) * posts_per_user_per_day
    print('hybrid, celebrity threshold %9s followers: %3d celebrity accounts pulled at read time; push writes fall to %s per day (%.0f%% of pure push)' % ('{:,}'.format(thr), len(celebs), '{:,.0f}'.format(hybrid), 100 * hybrid / push))
print()
print('read side (a user following 200 accounts opens the app):')
print('  pull everything:            200 lists fetched and merged per feed read')
print('  push (precomputed list):      1 list fetched')
print('  hybrid:                       1 list + up to ~5 celebrity lists merged')
EOF''',
                     e="The shape of the feed problem, in numbers. Follower counts are heavy-tailed: the median user has a handful, a few accounts have millions, and the top ten accounts hold a large share of all follow edges. **Pure push** therefore spends most of its writes on a handful of celebrity posts. A **hybrid** that pulls celebrities at read time removes most of the write amplification with a tiny change on the read side (a few extra lists to merge), and lowering the threshold trades more read work for fewer writes. This is the quantitative argument for the hybrid that an interviewer expects.",
                     annot=[("median followers: small ... max followers: millions ... top 10 accounts hold N% of all follow edges", "a heavy tail: a few accounts dominate"),
                            ("pure fan-out on write: ... writes per day (X writes per post on average, millions for the biggest account)", "average amplification hides the celebrity spikes"),
                            ("hybrid, celebrity threshold 100,000 ...: N celebrity accounts pulled; push writes fall to a fraction", "excluding a few accounts removes most of the writes"),
                            ("read side: pull 200 lists / push 1 list / hybrid 1 + a few", "the read-side cost of each strategy")]),
                dict(c=RIG,
                     e="Creates a tiny Redis client and helpers to start and stop a private Redis on port 6398 (the same few lines as in earlier modules). The next experiment stores real feed lists in it."),
                dict(volatile=True, c=r'''. ~/feed/rig.sh; redisup; cd ~/feed; cat > fanout.py <<'EOF'
import sys, time
sys.path.insert(0, '.')
from rc import R
r = R(); r.cmd('FLUSHALL')
CAP = 200                                                         # each feed keeps the newest 200 post ids
def fan_out(post_id, n_followers):
    t = time.perf_counter()
    for f in range(n_followers):                                  # in real systems this runs in batches on many workers (pipelined)
        r.cmd('LPUSH', 'feed:%d' % f, post_id); r.cmd('LTRIM', 'feed:%d' % f, 0, CAP - 1)
    return (time.perf_counter() - t) * 1000
for n in (100, 1000, 10000):
    ms = fan_out(n, n)
    print('post by an author with %6d followers: %6d feed updates in %7.0f ms  (%.3f ms per follower)' % (n, n, ms, ms / n))
print('reading one user\'s feed (one LRANGE of 20 post ids):', end=' ')
t = time.perf_counter()
for _ in range(1000): r.cmd('LRANGE', 'feed:5', 0, 19)
print('%.3f ms per read' % ((time.perf_counter() - t)))
print('feed:5 holds %d post ids (capped at %d); newest first: %s' % (r.cmd('LLEN', 'feed:5'), CAP, r.cmd('LRANGE', 'feed:5', 0, 4)))
EOF
python3 fanout.py; redisdown''',
                     e="The two sides of push, on a real in-memory store. Updating a follower's feed is cheap (a push and a trim on a capped list), but it is **one operation per follower**: a post by an author with 10,000 followers needs 10,000 of them, roughly a hundred times the work of a post by an author with 100 followers (real systems batch and pipeline these across many workers, but the count of updates is the same). The read, in contrast, is a **single list lookup of about a tenth of a millisecond**: that asymmetry (very cheap reads, expensive celebrity writes) is exactly what the hybrid design balances.",
                     annot=[("post by an author with 100 followers: 100 feed updates in ~N ms", "an ordinary post is cheap to fan out"),
                            ("post by an author with 10000 followers: 10000 feed updates in ~N ms (about 100x the work)", "write amplification grows linearly with followers"),
                            ("reading one user's feed (one LRANGE of 20 post ids): ~0.1 ms per read", "the read is a single in-memory list lookup"),
                            ("feed:5 holds 200 post ids (capped at 200)", "capped lists bound memory per user")]),
            ]),
        ],
        scenario=dict(
            title="\"Design Twitter's home timeline.\"",
            ask="The canonical feed question. A strong answer has the estimate, the fan-out trade-off with the celebrity fix, storage, ranking and failure handling.",
            clarify=[("Scale (users, posts, follows), freshness expectation, ranked or chronological, media, how many followers can one account have?", "Assume 300 million users, 200 million daily active, 500 million posts a day, average 200 followers, a handful with 50 million, timeline reads 20 times per user per day.")],
            think=[("Estimate.", "Posts: 500M/day is about 5,800/s (peak 15,000/s). Reads: 200M x 20 / 86,400 is about 46,000/s (peak 150,000/s): read-heavy 8:1. Fan-out: 500M posts x 200 average followers = 100 billion feed insertions a day (1.2 million per second) if purely push, with spikes from celebrity posts."),
                   ("Data model.", "Posts table (id, author, text, media refs, time) sharded by id; follow graph (follower, followee) sharded by user; feed cache: per-user capped list of post ids (about 800 ids x 8 bytes = 6.4 KB; for 200M active users about 1.3 TB in memory with replication)."),
                   ("Write path.", "Post service stores the post, publishes an event; fan-out workers (from a queue) push the id to each follower's feed list, in batches by shard, skipping inactive users and celebrity authors."),
                   ("Read path.", "Fetch the user's feed list, fetch the celebrity posts they follow (pull) and merge by time or score, hydrate post bodies and author info from caches, apply ranking and filters, return a page with a cursor."),
                   ("Hybrid threshold.", "About 10,000 to 100,000 followers: tune with measurements; the cost of a celebrity post is moved from millions of writes to a few extra reads per active follower."),
                   ("Ranking and freshness.", "Candidate generation then a scoring model (recency, affinity, engagement); precompute for heavy users; the feed may lag by seconds, which is acceptable."),
                   ("Failure and scale.", "Fan-out queue backlog delays feeds (monitor lag), a lost feed cache is rebuilt from the graph and recent posts (slow path), regional replication of feed caches, handle deletes and blocks at read time."),
                   ("Trade-offs.", "Write amplification versus read latency; memory cost of feeds; staleness; complexity of the hybrid.")],
            answer=["\"Let me estimate. 500 million posts a day is about 6,000 posts per second, and with 200 million daily users reading their timeline 20 times a day, about 46,000 reads per second at an average and 150,000 at peak: read-heavy. If I copied every post to every follower, with 200 followers on average that is 100 billion feed insertions a day, over a million a second, with huge spikes when someone with 50 million followers posts.",
                    "So I use a hybrid. Posts are stored once and published as an event. Fan-out workers push the post id into a capped, in-memory list per follower for ordinary authors, skipping inactive users. For authors above a follower threshold, say 100,000, I skip the fan-out and merge their recent posts into the reader's feed at read time. A read fetches the precomputed list, adds the celebrity posts the user follows, ranks the candidates, hydrates post bodies from a cache and returns a page with a cursor. The feed is eventually consistent by a few seconds; I monitor fan-out queue lag; and if a feed cache is lost I rebuild it from the follow graph and recent posts.\""],
            follow=[("How do you handle a user who follows a celebrity and 500 ordinary accounts?", "The precomputed list contains the 500 ordinary authors' posts; the celebrity's recent posts are fetched separately and merged at read time."),
                    ("What about deleting or editing a post?", "Posts are looked up by id at hydration time, so a delete removes the body and the id is filtered out at read time; edits update the post store, not the feeds."),
                    ("How do you paginate?", "A cursor of the last post id (or score) returned; the next page continues after it; offsets are unstable as new posts arrive.")],
            slips=["Pure push with no mention of celebrities.", "Storing whole posts in each feed instead of ids.", "No numbers for fan-out volume."],
        ),
        quick=[
            ("What is fan-out on write?", "Copying a new post into every follower's feed at post time, so reads are a single cheap lookup."),
            ("What is the celebrity problem?", "A post by an account with millions of followers causes millions of feed writes at once; solved by pulling celebrities' posts at read time."),
            ("What do feed lists store?", "Post ids only, capped, newest first; bodies are fetched from a cache."),
        ],
        traps=[
            "Fanning out to inactive users: wasted writes and memory.",
            "Offset pagination on a feed that is constantly changing.",
            "Storing entire post bodies in every feed: huge duplication and painful deletes and edits.",
        ],
    ),
    dict(
        title="Design a chat system: ordering, delivery, offline sync and real-time push",
        tier="hot",
        situation="\"Design WhatsApp or Slack\" tests whether you can keep a conversation correct when phones go offline mid-message, networks drop, the same message is sent twice and two people type at once. The core idea is small: the server owns the order.",
        learn=["Per-conversation sequence numbers for ordering and sync", "Idempotent sends: client ids and deduplication", "Push versus polling: WebSocket, long poll and server-sent events", "Delivery and read receipts"],
        model=[
            "A chat service's job is to **order, store, deliver and sync** messages. The server assigns each message a **monotonically increasing sequence number within its conversation**; that single order is what everyone sees, regardless of when messages arrive over the network. Each client remembers the **last sequence number it has** per conversation; on reconnect it asks `sync(conversation, after=seq)` and receives exactly what it missed, so **offline delivery needs no special case**: push is only an optimisation for online users. Messages are **stored durably first** (acknowledged to the sender with the assigned sequence number), then pushed.",
            "Because networks are unreliable and clients retry, the send operation must be **idempotent**: the client generates a **client message id**; the server enforces uniqueness on `(conversation, client message id)`, so a retried send returns the original sequence number instead of creating a duplicate. **Real-time push** needs a long-lived connection: **WebSocket** (bidirectional, the standard), **server-sent events** (server to client only, simple, over HTTP) or **long polling** (a fallback). A **connection gateway** tier holds millions of idle connections (lightweight, stateless apart from a user-to-gateway mapping kept in a fast store) and a **chat service** tier does the logic. **Delivery** and **read receipts** are small messages of their own (`delivered up to seq N`). **Group chats** fan out to members (small groups: push to each; huge channels: members pull by sync); **ordering across conversations** is not guaranteed and not needed. For **end-to-end encryption**, the server stores and relays opaque ciphertext and cannot rank, search or filter content.",
        ],
        analogy="A shared notebook per conversation with numbered lines that only the secretary writes. Each person remembers the last line number they read; if someone is away, on return they ask \"what is after line 38?\" and get exactly the missing lines. Handing the secretary the same note twice with the same reference number adds only one line.",
        visual=[CHAT_SEQ],
        sim=None,
        walk=[
            ("The sender sends with a client message id", "Retries are safe: same id, same result."),
            ("The server assigns the next sequence number and stores durably", "Then acknowledges the sender with that number."),
            ("Online recipients get a push", "Through the gateway holding their connection (WebSocket)."),
            ("Offline recipients do nothing special", "On reconnect they sync after their last sequence number."),
            ("Receipts flow back as small messages", "Delivered up to N, read up to N."),
        ],
        groups=[
            dict(title="A chat store with sequence numbers, idempotent sends, offline sync and server-sent events", cmds=[
                dict(c=r'''mkdir -p ~/feed && cd ~/feed && python3 - <<'EOF'
import sqlite3
db = sqlite3.connect(':memory:')
db.execute('create table messages(conv int, seq int, client_id text, sender text, body text, primary key (conv, seq), unique (conv, client_id))')
db.execute('create table counters(conv int primary key, last_seq int)')
def send(conv, client_id, sender, body):
    # idempotent: a retry with the same client_id returns the original sequence number, never a second message
    row = db.execute('select seq from messages where conv = ? and client_id = ?', (conv, client_id)).fetchone()
    if row: return row[0], 'duplicate ignored'
    db.execute('insert into counters values (?, 0) on conflict do nothing', (conv,))
    seq = db.execute('update counters set last_seq = last_seq + 1 where conv = ? returning last_seq', (conv,)).fetchone()[0]     # the server owns the order
    db.execute('insert into messages values (?, ?, ?, ?, ?)', (conv, seq, client_id, sender, body)); return seq, 'stored'
def sync(conv, after): return db.execute('select seq, sender, body from messages where conv = ? and seq > ? order by seq', (conv, after)).fetchall()
print('alice sends hi:             ', send(7, 'a-1', 'alice', 'hi'))
print('bob sends hello (at the same time, arrives second):', send(7, 'b-1', 'bob', 'hello'))
print('alice\'s phone retries the first send (no ack received):', send(7, 'a-1', 'alice', 'hi'))
send(7, 'a-2', 'alice', 'are you there?'); send(7, 'b-2', 'bob', 'yes!'); send(7, 'a-3', 'alice', 'great')
print()
print('bob\'s phone was off after he saw seq 2. It reconnects and asks for everything after seq 2:')
for m in sync(7, 2): print('   ', m)
print('a brand new device joins the conversation and syncs from 0: %d messages, in order' % len(sync(7, 0)))
print('another conversation has its own numbering: conv 8 first message ->', send(8, 'c-1', 'carol', 'hey'))
EOF''',
                     e="The heart of a chat backend in thirty lines. The **server assigns the sequence number per conversation**, so both phones see one order even though messages crossed in the network. Alice's retry (she never got the ack) carries the same **client id** and is recognised: `duplicate ignored`, the original number is returned and no second \"hi\" appears. Bob's phone was offline, and needs **no special handling**: it reconnects and asks for everything after the last sequence number it has, receiving exactly the three missed messages in order. A brand-new device syncs from zero the same way. Each conversation has its own counter, so there is no global ordering bottleneck.",
                     annot=[("alice sends hi: (1, 'stored')", "the server assigned sequence 1 and stored the message"),
                            ("alice's phone retries ...: (1, 'duplicate ignored')", "the client id makes a retried send harmless"),
                            ("bob's phone ... everything after seq 2: (3, ...), (4, ...), (5, ...)", "offline sync is just \"after the last sequence I have\""),
                            ("conv 8 first message -> (1, 'stored')", "sequence numbers are per conversation: no global counter")]),
                dict(volatile=True, c=r'''cd ~/feed && cat > sse.py <<'EOF'
# A tiny server-sent-events endpoint: GET /events streams new messages to the client as they arrive.
import http.server, socketserver, threading, time
subscribers = []
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path.startswith('/send'):                                        # /send?m=text  broadcasts a message to everyone connected
            msg = self.path.split('m=')[1]
            for w in list(subscribers):
                try: w.write(('id: %d\ndata: %s\n\n' % (int(time.time() * 1000) % 100000, msg)).encode()); w.flush()
                except Exception: subscribers.remove(w)
            self.send_response(200); self.send_header('Content-Length', '2'); self.end_headers(); self.wfile.write(b'ok'); return
        self.send_response(200); self.send_header('Content-Type', 'text/event-stream'); self.send_header('Cache-Control', 'no-cache'); self.end_headers()
        self.wfile.write(b': connected\n\n'); self.wfile.flush(); subscribers.append(self.wfile)
        while True: time.sleep(0.2)
socketserver.ThreadingTCPServer.allow_reuse_address = True
socketserver.ThreadingTCPServer(('127.0.0.1', 8350), H).serve_forever()
EOF
(setsid python3 sse.py </dev/null >/dev/null 2>&1 & disown) 2>/dev/null; sleep 0.7
echo "--- a client opens ONE long-lived HTTP connection and waits (the connection stays open):"
( curl -sN -m 2 http://127.0.0.1:8350/events | sed 's/^/   received: /' ) &
sleep 0.5
curl -s "http://127.0.0.1:8350/send?m=hello" >/dev/null; sleep 0.3
curl -s "http://127.0.0.1:8350/send?m=how-are-you" >/dev/null
wait
echo "--- the client got both messages pushed over the same connection, with no polling."
pkill -f sse.py; true''',
                     e="Real-time push with the simplest standard mechanism. The client opens **one long-lived HTTP connection** (`text/event-stream`); the server writes a small event whenever a message arrives, and the client sees it immediately, with no repeated polling. WebSocket does the same in both directions and is the usual choice for chat; server-sent events are simpler when only the server pushes (notifications, live scores) and work through ordinary HTTP infrastructure. A real gateway tier holds hundreds of thousands of such idle connections per machine, which is why it is kept separate from the chat logic, with a fast mapping of user to gateway so a message can be routed to the right connection.",
                     annot=[(": connected", "the stream is open and idle: no polling"),
                            ("received: id: ... / data: hello", "the first message arrived over the open connection as it was sent"),
                            ("received: ... data: how-are-you", "the second message used the same connection")]),
            ]),
        ],
        scenario=dict(
            title="\"Design WhatsApp: one-to-one and group chat for a billion users with offline delivery and read receipts.\"",
            ask="A staple design question. They want ordering, durability, connections, offline sync, groups, receipts and scale.",
            clarify=[("Scale, group size limits, message retention, media, end-to-end encryption, multiple devices per user?", "Assume 1 billion users, 100 billion messages a day, groups up to 1,000, media separate, multi-device, end-to-end encrypted.")],
            think=[("Estimate.", "100B messages/day is about 1.2 million per second average, 3 million at peak. At 100 bytes that is 10 TB/day of text. Connections: 500 million concurrent online users, each an idle long-lived connection: at 100,000 connections per gateway machine that is 5,000 gateway machines."),
                   ("Architecture.", "Connection gateways (WebSocket) hold connections and map user to gateway in a fast store; stateless chat servers handle sends; a message store partitioned by conversation id; a queue for fan-out and push notifications; a media service with object storage for attachments."),
                   ("Ordering and storage.", "Per-conversation sequence assigned by the shard owning the conversation; messages stored durably (a write-optimised wide-column or key-value store partitioned by conversation, time-ordered) before acknowledgement."),
                   ("Idempotency.", "Client message id unique per conversation; retries return the same sequence number."),
                   ("Delivery.", "If the recipient is online, push through their gateway; otherwise store and send a mobile push notification (a wake-up, not the data); on reconnect, sync after the last sequence per conversation; the server can delete messages after delivery to all devices for privacy-focused designs."),
                   ("Groups.", "Group membership service; small groups fan out on write to each member's inbox or push to online members; large groups members sync per conversation; per-user read position as a small message (read up to N)."),
                   ("Receipts and presence.", "Delivered and read receipts are tiny messages flowing back; presence from heartbeats with expiry, throttled for large contact lists."),
                   ("Failure and scale.", "Gateway failure: clients reconnect to another gateway and sync; shard failure: replicas with leader per conversation; hot groups: rate limit; end-to-end encryption: server relays ciphertext, so search and spam filtering move to clients or metadata."),
                   ("Trade-offs.", "Per-conversation ordering only; exactly-once is built from at-least-once plus dedupe; battery and bandwidth costs of connections.")],
            answer=["\"A hundred billion messages a day is about 1.2 million per second on average, and with half a billion concurrent connections I need thousands of gateway machines holding idle WebSockets, with a fast mapping from user to gateway. The gateways are separate from stateless chat servers, which assign each message the next sequence number within its conversation, store it durably in a store partitioned by conversation, acknowledge the sender with that number, and then push to online recipients.",
                    "Ordering is per conversation only, which is all anyone needs, and sends are idempotent through a client message id so retries never duplicate. Offline recipients need no special case: they get a mobile push notification as a wake-up and on reconnect sync after the last sequence number they have. Groups use a membership service and either push to online members or let members pull per conversation; delivered and read receipts are small messages of their own. If a gateway dies clients reconnect elsewhere and sync; shards are replicated with a leader per conversation; the server relays only ciphertext for end-to-end encryption, so spam and abuse controls rely on metadata and client-side checks.\""],
            follow=[("How do you route a message to the right gateway?", "A fast store maps user (and device) id to the gateway holding its connection; the chat service looks it up and forwards, or publishes to a per-gateway channel."),
                    ("How do you keep messages ordered in a group?", "The same per-conversation sequence assigned by the owning shard: every member sees the same order."),
                    ("What happens when a user has three devices?", "Each device tracks its own last-seen sequence per conversation and syncs independently; receipts are per user with the highest read position.")],
            slips=["Using timestamps from clients for ordering.", "A special offline queue instead of simple sync-after-sequence.", "Ignoring idempotency of sends."],
        ),
        quick=[
            ("How do clients recover missed messages?", "They ask the server for everything after the last sequence number they hold in each conversation."),
            ("What makes a send idempotent?", "A client-generated message id, unique per conversation, so a retry returns the original sequence number."),
            ("Why separate gateways from chat servers?", "Holding millions of idle connections is a different workload from message logic, and scales and fails differently."),
        ],
        traps=[
            "Trusting client timestamps to order messages.",
            "Treating the push as the delivery: a lost push must not lose the message.",
            "A global sequence counter: one bottleneck for the whole system.",
        ],
    ),
]
