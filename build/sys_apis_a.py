"""S23 APIs and contracts: part A (rig, lessons 1 to 3: HTTP semantics, pagination and evolution, rate limiting)."""
import sysviz as v

RIG = r'''mkdir -p ~/api && cd ~/api && cat > server.py <<'EOF'
# A small teaching API (standard library only). Run: python3 server.py   (port 8301)
import base64, json, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
ITEMS = [{'id': i, 'name': 'item-%04d' % i, 'price': 100 + i % 50} for i in range(1, 1001)]
ORDERS, KEYS, LOCK = {}, {}, threading.Lock()
BUCKET = {'tokens': 5.0, 'last': time.time()}
def bucket_take():
    with LOCK:
        now = time.time(); BUCKET['tokens'] = min(5.0, BUCKET['tokens'] + (now - BUCKET['last']) * 5); BUCKET['last'] = now
        if BUCKET['tokens'] >= 1: BUCKET['tokens'] -= 1; return True
        return False
class H(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    def log_message(self, *a): pass
    def send(self, code, body=None, headers=()):
        data = b'' if body is None else json.dumps(body).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(data)))
        for k, val in headers: self.send_header(k, val)
        self.end_headers(); self.wfile.write(data)
    def qs(self):
        path, _, q = self.path.partition('?'); return path, dict(p.split('=', 1) for p in q.split('&') if p)
    def body(self):
        n = int(self.headers.get('Content-Length', 0)); return json.loads(self.rfile.read(n) or b'{}')
    def do_GET(self):
        path, q = self.qs()
        if path.startswith('/items/'):
            i = int(path.split('/')[2])
            if not 1 <= i <= len(ITEMS): return self.send(404, {'error': 'no such item'})
            tag = '"v%d"' % (ITEMS[i - 1]['price'])
            if self.headers.get('If-None-Match') == tag: return self.send(304, None, [('ETag', tag)])
            return self.send(200, ITEMS[i - 1], [('ETag', tag), ('Cache-Control', 'max-age=60')])
        if path == '/items':
            limit = min(int(q.get('limit', 5)), 100)
            if 'after' in q:                                          # keyset: continue after the last id the client saw
                last = int(base64.urlsafe_b64decode(q['after']).decode()); page = [x for x in ITEMS if x['id'] > last][:limit]
            else:                                                     # offset
                off = int(q.get('offset', 0)); page = ITEMS[off:off + limit]
            nxt = base64.urlsafe_b64encode(str(page[-1]['id']).encode()).decode() if len(page) == limit else None
            return self.send(200, {'items': page, 'next': nxt})
        if path == '/limited':
            if bucket_take(): return self.send(200, {'ok': True})
            return self.send(429, {'error': 'slow down'}, [('Retry-After', '1')])
        if path == '/v1/user/1':
            return self.send(200, {'id': 1, 'name': 'Asha Rao'}, [('Deprecation', 'true'), ('Sunset', 'Wed, 31 Dec 2026 00:00:00 GMT'), ('Link', '</v2/user/1>; rel="successor-version"')])
        if path == '/v2/user/1':
            return self.send(200, {'id': 1, 'first_name': 'Asha', 'last_name': 'Rao'})
        if path.startswith('/orders/'):
            o = ORDERS.get(int(path.split('/')[2]))
            return self.send(200, o) if o else self.send(404, {'error': 'no such order'})
        self.send(404, {'error': 'not found'})
    def do_POST(self):
        if self.path != '/orders': return self.send(404, {'error': 'not found'})
        key, b = self.headers.get('Idempotency-Key'), self.body()
        with LOCK:
            if key and key in KEYS: return self.send(200, ORDERS[KEYS[key]], [('Idempotent-Replayed', 'true')])
            oid = len(ORDERS) + 1; ORDERS[oid] = {'id': oid, 'item': b.get('item'), 'qty': b.get('qty', 1)}
            if key: KEYS[key] = oid
        self.send(201, ORDERS[oid], [('Location', '/orders/%d' % oid)])
    def do_PUT(self):
        oid = int(self.path.split('/')[2]); b = self.body()
        with LOCK: new = oid not in ORDERS; ORDERS[oid] = {'id': oid, 'item': b.get('item'), 'qty': b.get('qty', 1)}
        self.send(201 if new else 200, ORDERS[oid])
    def do_DELETE(self):
        oid = int(self.path.split('/')[2])
        with LOCK: gone = ORDERS.pop(oid, None)
        self.send(204 if gone else 404, None)
ThreadingHTTPServer.allow_reuse_address = True
ThreadingHTTPServer(('127.0.0.1', 8301), H).serve_forever()
EOF
cat > rig.sh <<'EOF'
export A=$HOME/api B=http://127.0.0.1:8301
apiup()   { (cd $A && setsid python3 server.py </dev/null >/dev/null 2>&1 & disown) 2>/dev/null; for i in 1 2 3 4 5 6 7 8 9 10; do curl -s -o /dev/null $B/items/1 && break; sleep 0.3; done; }
apidown() { pkill -f "python3 server.py" >/dev/null 2>&1; sleep 0.3; true; }
EOF
. ./rig.sh; echo "rig ready in $A: server.py (a small teaching API on port 8301) and rig.sh (apiup, apidown)"'''

HTTP_VIZ = v.figure(
    720, 236,
    [v.box(10, 20, 330, 190, "Verbs and what they promise", "acc", ""),
     v.text(175, 56, "GET     safe, idempotent, cacheable", "dg-s"),
     v.text(175, 84, "PUT     replace: idempotent", "dg-s"),
     v.text(175, 112, "DELETE  idempotent (repeat: same end state)", "dg-s"),
     v.text(175, 140, "POST    create or act: NOT idempotent", "dg-s"),
     v.text(175, 168, "PATCH   partial update: depends", "dg-s"),
     v.box(380, 20, 330, 190, "Status codes that mean something", "ok", ""),
     v.text(545, 56, "200 OK / 201 Created + Location / 204 No Content", "dg-s"),
     v.text(545, 84, "304 Not Modified (cache is still good)", "dg-s"),
     v.text(545, 112, "400 bad input / 401 who are you / 403 not allowed", "dg-s"),
     v.text(545, 140, "404 not found / 409 conflict / 429 slow down", "dg-s"),
     v.text(545, 168, "500 our bug / 503 overloaded, try later", "dg-s")],
    "HTTP semantics for APIs", "The verb and the status code are part of the contract: clients, caches and retries rely on them")

BUCKET_VIZ = v.figure(
    720, 214,
    [v.box(10, 20, 200, 52, "Fixed window", "warn", "count per minute; resets at :00"),
     v.box(260, 20, 200, 52, "Sliding window", "acc", "count over the last 60 s"),
     v.box(510, 20, 200, 52, "Token bucket", "ok", "refills at a steady rate; bursts allowed"),
     v.text(110, 96, "simple; allows 2x at the boundary", "dg-s"), v.text(360, 96, "smooth; needs more memory", "dg-s"), v.text(610, 96, "the usual choice: burst + average", "dg-s"),
     v.box(120, 122, 480, 52, "Return 429 Too Many Requests with Retry-After", "ink", "and tell the client the limit, what remains and when it resets"),
     v.text(360, 200, "Limit per client (key or user) first; a global limit protects the system, per-client limits keep it fair.", "dg-s")],
    "Rate limiting algorithms", "Three ways to decide \"too many\", and the response that makes clients behave")

LESSONS_A = [
    dict(
        title="API design basics: resources, verbs and status codes",
        tier="hot",
        situation="Two teams build clients against your API. One retries a failed POST and creates two orders; another caches a response that should never have been cached; a third cannot tell \"not found\" from \"not allowed\". An API is a contract, and the details of HTTP are most of the contract.",
        learn=["Resources and URLs", "Verbs and their guarantees: safe and idempotent", "Status codes that clients can act on", "Calling a real API with curl"],
        model=[
            "A REST-style API models **resources** (nouns): `/orders`, `/orders/42`, `/users/7/orders`. The **verb** says what you do and carries guarantees that clients, caches and retry logic depend on. **GET** is **safe** (no side effects) and cacheable. **PUT** replaces a resource and **DELETE** removes one: both are **idempotent** (doing them twice leaves the same state). **POST** creates a resource or triggers an action and is **not idempotent**: a repeat creates another. **PATCH** applies a partial change.",
            "**Status codes** are how the server tells the client what to do next: `200` OK, `201 Created` (with a `Location` header), `204 No Content`, `304 Not Modified`; the **4xx** codes mean the client should change something (`400` invalid input, `401` unauthenticated, `403` not allowed, `404` not found, `409` conflict, `429` too many requests); the **5xx** codes mean the server failed (`500` bug, `503` temporarily overloaded). Clients retry 5xx and 429 (with backoff) and never retry 4xx blindly. Use them precisely and return a consistent **error body** (a code, a human message, a request id).",
        ],
        analogy="A restaurant menu with rules: asking to see the menu changes nothing (GET); replacing your order with a new one is the same no matter how often you say it (PUT); placing a new order twice gives you two meals (POST). The waiter's replies (\"coming up\", \"sold out\", \"not for you\") are the status codes.",
        visual=[HTTP_VIZ],
        sim=None,
        walk=[
            ("Name the resources", "Nouns in plural, nested only when the child cannot exist alone."),
            ("Pick the verb by its guarantee", "Reads are GET; replace is PUT; create or act is POST; remove is DELETE."),
            ("Return the status that tells the client what to do", "201 with Location after a create; 404 for missing; 409 for a conflict; 429 for rate limits."),
            ("Make errors consistent", "One JSON shape for every error, with a stable machine-readable code."),
            ("Document and test the contract", "The API description (OpenAPI) is the contract; tests and generated clients keep it honest."),
        ],
        groups=[
            dict(title="Build the rig, then call a real API", cmds=[
                dict(c=RIG,
                     e="Creates the rig used by the whole module: a small teaching API written with only the Python standard library (items, orders with idempotency keys, a rate-limited endpoint, two versions of a user endpoint, ETags) and two helpers to start and stop it on port 8301. Every later lesson calls it with `curl`."),
                dict(volatile=True, c=r'''. ~/api/rig.sh; apiup
echo "--- GET a resource that exists:";   curl -si $B/items/7 | grep -E "^(HTTP|ETag|Cache-Control)|^\{" | tr -d '\r'
echo "--- GET one that does not:";        curl -si $B/items/99999 | grep -E "^HTTP|^\{" | tr -d '\r'
echo "--- POST creates (not idempotent): twice gives two orders"
curl -si -X POST $B/orders -d '{"item": 7, "qty": 1}' | grep -E "^(HTTP|Location)" | tr -d '\r'
curl -si -X POST $B/orders -d '{"item": 7, "qty": 1}' | grep -E "^(HTTP|Location)" | tr -d '\r'
echo "--- PUT replaces (idempotent): same request twice, same end state"
curl -si -X PUT $B/orders/50 -d '{"item": 9, "qty": 2}' | grep -E "^(HTTP|\{)" | tr -d '\r'
curl -si -X PUT $B/orders/50 -d '{"item": 9, "qty": 2}' | grep -E "^(HTTP|\{)" | tr -d '\r'
echo "--- DELETE twice: the end state is the same (gone); the second reports 404"
curl -s -o /dev/null -w "first: %{http_code}\n" -X DELETE $B/orders/50; curl -s -o /dev/null -w "second: %{http_code}\n" -X DELETE $B/orders/50
apidown''',
                     e="The verbs, one by one, against a real server. `GET` returns the resource with an `ETag` and `Cache-Control`; a missing one is `404`. **POST twice creates two different orders** (`/orders/1` and `/orders/2`): the reason retrying a POST is dangerous. **PUT twice** leaves the same order: first `201 Created`, then `200 OK`, same content. **DELETE twice** ends in the same state (gone); the second reports `404` because there is nothing left, which is fine for the client since the goal was reached.",
                     annot=[("HTTP/1.1 200 OK / ETag: \"v107\" / Cache-Control: max-age=60", "a cacheable read with a validator for later revalidation"),
                            ("HTTP/1.1 404 Not Found / {\"error\": \"no such item\"}", "a precise status plus a consistent error body"),
                            ("POST: 201 Created, Location: /orders/1 then Location: /orders/2", "each POST created a new order: not idempotent"),
                            ("PUT: 201 then 200, the same body", "idempotent: the second PUT changed nothing"),
                            ("DELETE first: 204, second: 404", "same end state; the second reports that nothing was there")]),
            ]),
        ],
        scenario=dict(
            title="\"Design a REST API for a booking system. Which verbs and status codes, and how do you make retries safe?\"",
            ask="The standard API design prompt. They want resources, verbs, codes, error handling and the retry story in one coherent answer.",
            clarify=[("Who are the clients (mobile, partners, internal) and how do they retry?", "Mobile clients on poor networks retry a lot; partners need stability and versioning.")],
            think=[("Name the resources.", "`/bookings`, `/bookings/{id}`, `/rooms/{id}/availability`, `/users/{id}/bookings`. Actions that are not CRUD get their own sub-resource: `POST /bookings/{id}/cancellation`."),
                   ("Assign verbs by guarantee.", "GET availability and bookings; POST /bookings to create; PUT or PATCH to change dates; DELETE or a cancellation resource to cancel."),
                   ("Choose status codes.", "201 with Location on create; 200 on reads; 204 on delete; 400 invalid dates; 401/403 auth; 404 missing; 409 when the room is already booked; 422 for valid syntax but unacceptable data; 429 on rate limits; 503 when overloaded."),
                   ("Make POST retry-safe.", "An `Idempotency-Key` header: the server stores the key and the created booking and returns the same response for a repeat (`200` with a replay header, or the original `201`)."),
                   ("Error format.", "One shape: `{code, message, details, request_id}`; stable codes for clients, messages for humans."),
                   ("Concurrency control.", "ETag or a `version` field with `If-Match` on updates so two editors cannot silently overwrite each other (412 Precondition Failed)."),
                   ("Say what else a contract needs.", "Pagination, filtering, versioning, rate limits, auth, and an OpenAPI description with generated clients and contract tests.")],
            answer=["\"I would model resources: bookings, rooms with availability, and a user's bookings. Reads are GET; creating a booking is POST to the collection, returning 201 with a Location header; changes are PUT or PATCH; cancellation is DELETE or a cancellation sub-resource. I would use specific status codes: 400 or 422 for bad input, 404 for missing, 409 when the room is already taken, 429 for rate limiting and 503 when overloaded, with one consistent error body containing a stable code, a message and a request id.",
                    "POST is not idempotent, so I would require an Idempotency-Key header on creates: the server stores the key with the booking and returns the stored response for a repeat, which makes client retries safe. For updates I would use ETags with If-Match so two editors cannot silently overwrite each other. Then pagination, versioning, rate limits and auth, and an OpenAPI description with contract tests so clients and server stay in step.\""],
            follow=[("PUT or PATCH for updates?", "PUT replaces the whole resource (idempotent, simple semantics); PATCH sends only changes (smaller, but define merge semantics carefully)."),
                    ("What does 409 versus 422 mean?", "409 Conflict: the request conflicts with the current state (room taken). 422 Unprocessable: the request is well-formed but its content is invalid."),
                    ("How do you model an action like cancel?", "As a resource you create (`POST /bookings/{id}/cancellation`) or a state change, so it has an id, a status and an audit trail.")],
            slips=["Verbs in URLs (/createBooking) with everything as POST.", "200 for everything with the error inside the body.", "No story for retries."],
        ),
        quick=[
            ("Which verbs are idempotent?", "GET, PUT and DELETE (and HEAD, OPTIONS); POST is not."),
            ("What does 201 Created come with?", "A Location header pointing to the new resource."),
            ("Which statuses may a client safely retry?", "5xx and 429 with backoff (for idempotent requests); not 4xx without changing the request."),
        ],
        traps=[
            "Returning 200 with an error message in the body: clients, caches and monitoring all misread it.",
            "Using GET for operations with side effects: crawlers and prefetchers will trigger them.",
            "Retry logic that retries 400s: it can never succeed.",
        ],
    ),
    dict(
        title="Pagination, filtering and evolving an API without breaking clients",
        tier="hot",
        situation="`GET /items` returned 50 rows in testing and now returns 4 million. A client asks for page 90,000 and the database groans. Meanwhile a field is renamed and every mobile app in the world breaks. Pagination and versioning are where API designs succeed or fail over years.",
        learn=["Offset versus keyset (cursor) pagination, measured", "Stable pagination while data changes", "Additive, backward-compatible changes", "Versioning and deprecation done politely"],
        model=[
            "**Offset pagination** (`?offset=900000&limit=50`) is simple but the database must walk past all the skipped rows, so deep pages are slow, and if rows are inserted or deleted between requests, items are **skipped or repeated**. **Keyset (cursor) pagination** (`?after=<last id seen>&limit=50`, answered by `where id > :last order by id limit 50`) seeks straight to the right place, stays fast at any depth, and is stable under inserts. The cursor is an **opaque token** the client simply passes back; the response says whether there is a `next` page. The trade-off: no jumping to \"page 7,531\". Always set a maximum page size.",
            "APIs live for years, so **evolve without breaking**. **Additive changes** (new optional fields, new endpoints) are safe if clients **ignore unknown fields**; removing or renaming fields, changing types or semantics is breaking. When you must break, **version** (in the path `/v2/...`, a header, or media type) and run versions side by side with **deprecation signals**: a `Deprecation` and `Sunset` header, a `Link` to the successor, documentation, usage monitoring per version and a published date. Never remove a version while real clients still call it. Prefer the **tolerant reader** principle on the client side, and **contract tests** on the server side.",
        ],
        analogy="A library catalogue that says \"continue after book 904,311\" instead of \"skip the first 900,000 books\": the librarian goes straight there and the numbering does not shift when new books arrive. Renaming a shelf label means leaving the old label up with a sign pointing to the new one until everyone has moved.",
        sim=None,
        walk=[
            ("Return a bounded page and a cursor", "At most N items and an opaque `next` token (or none at the end)."),
            ("Seek, do not skip", "The cursor encodes the last key; the query uses `where key > cursor`."),
            ("Add fields, never repurpose them", "Clients ignore unknown fields, so additions are safe."),
            ("Introduce v2 beside v1", "Both run; v1 starts returning Deprecation and Sunset headers."),
            ("Watch the traffic, then retire", "Remove v1 only after usage reaches zero (or the published date, after outreach)."),
        ],
        groups=[
            dict(title="Offset versus keyset on a million rows, and a polite deprecation", cmds=[
                dict(volatile=True, c=r'''python3 - <<'EOF'
import sqlite3, time
db = sqlite3.connect(':memory:')
db.execute('create table items(id integer primary key, name text)')
db.executemany('insert into items values (?, ?)', ((i, 'item-%d' % i) for i in range(1, 1000001)))
def timeit(sql, args):
    t = time.perf_counter(); rows = db.execute(sql, args).fetchall(); return (time.perf_counter() - t) * 1000, rows
print('page of 50 rows from a table of 1,000,000 (SQLite, real queries)')
for depth in (0, 100000, 500000, 900000):
    off_ms, a = timeit('select id from items order by id limit 50 offset ?', (depth,))
    key_ms, b = timeit('select id from items where id > ? order by id limit 50', (depth,))
    print('  page starting at row %7d:  offset %7.2f ms    keyset %5.2f ms   same rows: %s' % (depth, off_ms, key_ms, a == b))
EOF''',
                     e="Why deep offsets are expensive, measured. The database must walk and discard every skipped row for `offset`, so the time grows with the depth: the page at row 900,000 costs about 25 times more than the first page, and several hundred times more than the keyset query at the same depth. The keyset query seeks straight to `id > last` and costs about the same (tiny) amount at every depth, while returning **exactly the same rows**. SQLite is very fast, so the absolute times are small; against a networked database with larger rows the gap is far larger. The growth against a flat line is the lesson.",
                     annot=[("page starting at row 0: offset 0.21 ms, keyset 0.05 ms", "almost no difference at the start"),
                            ("page starting at row 900000: offset 5.27 ms, keyset 0.01 ms", "the offset query reads and throws away 900,000 rows; the keyset query jumps to the right place (about 500 times faster here)"),
                            ("same rows: True", "the two methods return the same data; only the cost differs")]),
                dict(volatile=True, c=r'''. ~/api/rig.sh; apiup
echo "--- keyset pagination through the API: pass the opaque cursor back"
r=$(curl -s "$B/items?limit=3"); echo "$r" | python3 -c "import sys,json; d=json.load(sys.stdin); print('page 1 ids', [i['id'] for i in d['items']], 'next =', d['next'])"
c=$(echo "$r" | python3 -c "import sys,json; print(json.load(sys.stdin)['next'])")
curl -s "$B/items?limit=3&after=$c" | python3 -c "import sys,json; d=json.load(sys.stdin); print('page 2 ids', [i['id'] for i in d['items']], 'next =', d['next'])"
echo "--- an old version, deprecated politely:"
curl -si $B/v1/user/1 | grep -E "^(HTTP|Deprecation|Sunset|Link)|^\{" | tr -d '\r'
echo "--- the new version changed the shape (a breaking change, so it got a new version):"
curl -s $B/v2/user/1; echo
apidown''',
                     e="Cursor pagination and deprecation through the real API. The first page returns three items and an **opaque `next` cursor** (really the last id, base64-encoded: clients must not parse it); passing it back returns the following three. Version 1 still works but now announces its own retirement with `Deprecation`, a `Sunset` date and a `Link` header to its successor, so clients (and their monitoring) can see the change coming. Version 2 splits `name` into `first_name` and `last_name`: a **breaking** change, which is exactly why it got a new version instead of changing v1.",
                     annot=[("page 1 ids [1, 2, 3] next = Mw==", "an opaque cursor: the last id, encoded"),
                            ("page 2 ids [4, 5, 6]", "continues exactly after the last item seen"),
                            ("Deprecation: true / Sunset: ... / Link: </v2/user/1>; rel=\"successor-version\"", "machine-readable notice: this version will be retired and here is its replacement"),
                            ("{\"id\": 1, \"first_name\": \"Asha\", \"last_name\": \"Rao\"}", "the renamed fields live only in v2")]),
            ]),
        ],
        scenario=dict(
            title="\"We need to rename a field in a public API used by thousands of apps. How do you do it?\"",
            ask="An API evolution question. They want a plan that never breaks a live client, with timing and monitoring.",
            clarify=[("Who are the clients and can we force upgrades?", "Mobile apps live for years; partners need notice; internal clients can be coordinated.")],
            think=[("Do not break v1.", "Renaming or removing a field is a breaking change: apps that read the old name stop working."),
                   ("Prefer the additive path first.", "Add the new field alongside the old one in the same version; document the old as deprecated. Clients migrate at their own pace."),
                   ("Use a new version only when needed.", "For shape changes that cannot coexist, release v2 beside v1; both run on the same backend through adapters."),
                   ("Signal and communicate.", "Deprecation and Sunset headers, release notes, changelog, emails to registered developers, dashboard showing who still uses v1."),
                   ("Measure usage per version and per client.", "Remove only when traffic is gone or the published date passes and the largest clients have confirmed."),
                   ("Keep tests.", "Contract tests for both versions run in CI; clients are tolerant readers that ignore unknown fields.")],
            answer=["\"First I would avoid a breaking change at all: add the new field next to the old one, mark the old one deprecated in the docs, and let clients migrate when they can. If the shape really has to change, I would release v2 alongside v1 and keep both running on one backend through thin adapters.",
                    "I would announce it properly: Deprecation and Sunset headers on v1, a link to the successor, a changelog and direct emails to registered developers. I would measure traffic per version and per client, and only retire v1 when usage is gone or the published date passes after the biggest clients confirm. Contract tests for both versions run in CI, and our clients are tolerant readers that ignore unknown fields so additive changes never break them.\""],
            follow=[("Where do you put the version: URL, header or media type?", "URL is the most visible and easiest to route and cache; headers or media types are cleaner but harder to use and debug. Pick one and be consistent."),
                    ("What is a tolerant reader?", "A client that ignores fields it does not know and does not depend on field order, so additive server changes are safe."),
                    ("How do you handle mobile apps that never update?", "Support old versions much longer, track the share of traffic, and use a forced-update mechanism only as a last resort.")],
            slips=["Renaming a field in place.", "Retiring a version without measuring usage.", "No communication plan."],
        ),
        quick=[
            ("Why is keyset pagination faster than offset for deep pages?", "It seeks directly to the position instead of reading and discarding all skipped rows."),
            ("Is adding a new optional field to a response a breaking change?", "No, if clients ignore unknown fields."),
            ("What do Deprecation and Sunset headers do?", "Announce that an endpoint is deprecated and when it will be removed."),
        ],
        traps=[
            "Unbounded page sizes: one request can take the service down.",
            "Letting clients parse your cursor: you can never change it afterwards.",
            "Retiring an old version because \"nobody uses it\" without measuring.",
        ],
    ),
    dict(
        title="Rate limiting and quotas: fair, fast and explainable",
        tier="hot",
        situation="One client's runaway script sends 5,000 requests a second and everyone else's calls start failing. A good rate limiter protects the service, keeps usage fair, and tells well-behaved clients exactly how to behave.",
        learn=["Fixed window, sliding window and token bucket", "Where to enforce limits and by what key", "429, Retry-After and rate-limit headers", "Distributed rate limiting"],
        model=[
            "A **rate limiter** decides whether a request is allowed. **Fixed window**: count requests per calendar minute and reject over the limit: simple, but a client can send the full limit at the end of one window and again at the start of the next (a **2x burst at the boundary**). **Sliding window** counts over the last 60 seconds precisely (a log of timestamps) or approximately (a weighted blend of two windows): smooth but needs more memory. **Token bucket**: a bucket holds up to B tokens and refills at R per second; each request takes a token: it allows **bursts up to B** while enforcing an **average of R**; it is the most common choice. **Leaky bucket** smooths output to a constant rate.",
            "Decide the **key** to limit by (API key, user id, IP address, tenant) and the **tier** (free versus paid), and enforce at the **edge** (gateway or load balancer) so excess load never reaches your servers, plus a **global** limit that protects the system. When rejecting, return **`429 Too Many Requests`** with **`Retry-After`** and headers that say the limit, what remains and when it resets, so well-behaved clients slow down instead of hammering. In a fleet of servers the counters must be **shared** (usually Redis with atomic operations or a Lua script), or approximated per node; accept small inaccuracy for speed, and decide what happens if the limiter store is down (usually **fail open** with an alert).",
        ],
        analogy="A nightclub door: a fixed window is \"fifty people allowed in each hour on the hour\", so fifty can pour in at 10:59 and fifty more at 11:00. A token bucket is a jar of tickets refilled at a steady rate: a group can use the saved tickets at once, but over a long time the average is capped.",
        visual=[BUCKET_VIZ],
        sim=None,
        walk=[
            ("Pick the identity and the limit", "Per API key: 100 requests per second sustained, bursts of 200."),
            ("Check before doing the work", "At the gateway: take a token or reject immediately: rejection must be cheaper than service."),
            ("Reject politely", "429 with `Retry-After` and the remaining quota."),
            ("Share the counters across servers", "A central store (Redis) with atomic increments, or per-node approximations."),
            ("Monitor and tune", "Watch 429 rates per client, and let customers see their usage."),
        ],
        groups=[
            dict(title="The boundary burst, and a real 429", cmds=[
                dict(c=r'''python3 - <<'EOF'
# A client sends the maximum it can: every 0.05 s for 3 seconds. Limit: 10 requests per second.
def fixed_window(times, limit=10, window=1.0):
    count, cur, ok = 0, None, []
    for t in times:
        w = int(t // window)
        if w != cur: cur, count = w, 0
        if count < limit: count += 1; ok.append(t)
    return ok
def sliding_log(times, limit=10, window=1.0):
    log, ok = [], []
    for t in times:
        log = [x for x in log if x > t - window]
        if len(log) < limit: log.append(t); ok.append(t)
    return ok
def token_bucket(times, rate=10.0, burst=10.0):
    tokens, last, ok = burst, 0.0, []
    for t in times:
        tokens = min(burst, tokens + (t - last) * rate); last = t
        if tokens >= 1: tokens -= 1; ok.append(t)
    return ok
times = [0.7 + i * 0.02 for i in range(150)]                   # starts at 0.7 s: close to a window boundary
def worst_second(ok):                                           # the most requests accepted in ANY 1-second span
    return max(sum(1 for y in ok if x <= y < x + 1.0) for x in ok)
for name, f in (('fixed window', fixed_window), ('sliding window log', sliding_log), ('token bucket (burst 10)', token_bucket)):
    ok = f(times)
    print('%-26s accepted %3d of %d in 3 s,   most accepted in any one second: %2d  (limit is 10)' % (name, len(ok), len(times), worst_second(ok)))
EOF''',
                     e="Three limiters, the same greedy client, the same limit of 10 per second. The **fixed window** accepts 10 in the last part of one window and another 10 right after the boundary: in some one-second span it lets through **nearly twice the limit** (the worst second shows 19 or 20). The **sliding window log** never exceeds 10 in any second. The **token bucket** allows a burst equal to its capacity plus the refill in the same second (19 here, by design) and then settles at the refill rate, so over longer periods its average is about the limit. Choose by what you can afford: the fixed window is cheapest and rough; the others are fairer.",
                     annot=[("fixed window ... most accepted in any one second: ~20 (limit is 10)", "the boundary problem: two full windows back to back"),
                            ("sliding window log ... most accepted in any one second: 10", "exact: never above the limit in any one-second span"),
                            ("token bucket ... accepted 39 of 150 in 3 s, worst second 19", "a full bucket of 10 plus the refill: bursts are allowed by design, then it settles at about 10 per second")]),
                dict(volatile=True, c=r'''. ~/api/rig.sh; apiup
echo "--- 12 quick calls to a limited endpoint (burst 5, refill 5 per second):"
for i in $(seq 1 12); do curl -s -o /dev/null -w "%{http_code} " $B/limited; done; echo
echo "--- what a rejected response looks like:"
curl -si $B/limited | grep -E "^(HTTP|Retry-After)|^\{" | tr -d '\r'
echo "--- a well-behaved client waits Retry-After seconds, then succeeds:"
sleep 1; curl -s -o /dev/null -w "%{http_code}\n" $B/limited
apidown''',
                     e="A token bucket in front of a real endpoint. The first five calls drain the bucket (`200`), the following calls are refused with `429` (a call made after a pause would find a refilled token). The rejected response carries `Retry-After: 1` so a client knows how long to wait; after waiting, the next call succeeds. This is the behaviour clients should implement: **respect `Retry-After`**, back off, and never retry in a tight loop.",
                     annot=[("200 200 200 200 200 429 429 ...", "the burst capacity of 5 is used up; later requests are refused until tokens refill"),
                            ("HTTP/1.1 429 Too Many Requests / Retry-After: 1", "tells the client exactly how long to wait"),
                            ("200 after the wait", "a well-behaved client recovers immediately")]),
            ]),
        ],
        scenario=dict(
            title="\"Design a rate limiter for a public API used by thousands of customers on a fleet of servers.\"",
            ask="A staple design question. They want algorithm, placement, key, distributed counting, failure behaviour and client experience.",
            clarify=[("What are we protecting: backend capacity, fairness, cost? Are there paid tiers? What happens at the limit: reject or queue?", "Fairness and protection suggest per-customer limits with a global ceiling; rejecting with 429 is standard.")],
            think=[("Choose the algorithm.", "Token bucket per key: allows bursts and enforces an average; cheap (two numbers per key)."),
                   ("Choose the key and tiers.", "API key or tenant, with limits per plan; separate limits per endpoint class (writes stricter than reads); a global limit as a safety net."),
                   ("Choose where to enforce.", "At the edge or gateway before application servers; a cheap early rejection."),
                   ("Distribute the counters.", "A shared Redis with an atomic script (read, refill, take, write in one step) per key; or local buckets with a share of the limit per node and periodic reconciliation for lower latency. Accept small inaccuracies."),
                   ("Handle failure.", "If Redis is unavailable, fail open with a conservative local limit and an alert (an outage of the limiter should not become an outage of the API), unless the endpoint is abuse-critical."),
                   ("Client experience.", "429 with Retry-After and `X-RateLimit-Limit/Remaining/Reset` headers; documented limits; usage dashboard; SDKs that back off."),
                   ("Operate it.", "Per-customer 429 rate, top consumers, limit-change workflow, and abuse detection beyond simple counting.")],
            answer=["\"I would use a token bucket per customer, because it allows short bursts while enforcing an average rate, and it needs only two numbers per key. Limits depend on the plan and the endpoint class, with a global limit as a safety net, enforced at the gateway so excess traffic never reaches the application servers.",
                    "Across a fleet the counters live in a shared Redis, updated with one atomic script that refills and takes a token, or in local buckets with a share of the limit per node for lower latency, accepting a little inaccuracy. If Redis is down I fail open with a conservative local limit and an alert. Rejected calls get 429 with Retry-After and rate-limit headers, the limits are documented and customers see their usage. I would monitor 429s per customer and the top consumers.\""],
            follow=[("Why a Lua script in Redis?", "It makes read, refill, take and write one atomic operation, so concurrent requests from different servers cannot over-admit."),
                    ("Per IP or per user?", "Per authenticated identity when you have one; IP limits are a coarse backstop (shared NATs, proxies), useful for unauthenticated traffic."),
                    ("How do you prevent a retry storm when everyone gets 429?", "Retry-After and jittered backoff in clients, plus server-side load shedding; limits that reset smoothly rather than all at once.")],
            slips=["A fixed window described as precise.", "Per-server counters with no sharing.", "No story for what happens when the limiter itself fails."],
        ),
        quick=[
            ("What is the weakness of a fixed-window limiter?", "A client can send the full limit at the end of one window and again at the start of the next: up to twice the limit in a short span."),
            ("What does a token bucket allow that a strict per-second counter does not?", "Short bursts up to the bucket size while keeping the average rate."),
            ("What should a 429 response include?", "A `Retry-After` (and ideally limit, remaining and reset information)."),
        ],
        traps=[
            "Limiting only by IP: many users behind one address are punished together.",
            "A limiter that fails closed when its store is down: it turns a small outage into a big one.",
            "Not telling clients the limits: they cannot behave well.",
        ],
    ),
]
