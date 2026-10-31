"""S23 APIs and contracts: part B (lessons 4 and 5: API styles, reliable APIs) and the module tail."""
import sysviz as v

STYLES_VIZ = v.figure(
    720, 244,
    [v.box(10, 20, 220, 150, "REST + JSON", "acc", ""),
     v.text(120, 56, "resources and verbs", "dg-s"), v.text(120, 82, "human readable, cacheable", "dg-s"), v.text(120, 108, "easy for everyone", "dg-s"), v.text(120, 140, "over- or under-fetching", "dg-s"),
     v.box(250, 20, 220, 150, "gRPC (protobuf, HTTP/2)", "ok", ""),
     v.text(360, 56, "typed contract, generated code", "dg-s"), v.text(360, 82, "compact binary, streaming", "dg-s"), v.text(360, 108, "great between services", "dg-s"), v.text(360, 140, "hard from browsers, hard to debug", "dg-s"),
     v.box(490, 20, 220, 150, "GraphQL", "warn", ""),
     v.text(600, 56, "client picks the fields", "dg-s"), v.text(600, 82, "one request, many resources", "dg-s"), v.text(600, 108, "great for varied UIs", "dg-s"), v.text(600, 140, "caching, cost control, N+1", "dg-s"),
     v.text(360, 204, "Public and partner APIs: REST. Internal service calls: gRPC. Many different clients with different needs: GraphQL (often as a BFF).", "dg-s"),
     v.text(360, 228, "Choose by who calls, how often, and who must debug it at 3 a.m.", "dg-s")],
    "API styles compared", "Three common styles and where each earns its place")

WEBHOOK_SEQ = v.seq(
    ["Provider", "Your endpoint"],
    [("a->b", 0, 1, "POST /webhook  X-Signature: HMAC(secret, timestamp.body)"),
     ("note", 0, 1, "you recompute the HMAC with the shared secret and compare in constant time"),
     ("a->b", 1, 0, "200 OK within a few seconds (do the work later)", "reply"),
     ("note", 0, 1, "no 200: the provider retries with backoff, so the same event can arrive again: dedupe by event id"),
     ("a->b", 0, 1, "POST again (retry): same event id", "bad"),
     ("a->b", 1, 0, "200 OK (ignored: already processed)", "reply")],
    "Webhooks done safely", "Verify the signature, answer fast, process asynchronously, and expect duplicates")

LESSONS_B = [
    dict(
        title="REST, gRPC and GraphQL: choosing an API style",
        tier="core",
        situation="The mobile team wants one call for the whole home screen, the internal services need fast typed calls, and a partner wants something they can try with curl. One style rarely fits all three.",
        learn=["What each style optimises", "Over-fetching, under-fetching and the N+1 round-trip problem", "Binary versus text payloads, measured", "Where each style belongs in a system"],
        model=[
            "**REST over JSON** is the universal default: resources, verbs, status codes, cacheable, readable, usable from anywhere with `curl`. Its weakness is **chattiness and fit**: a screen that needs a user, their orders and each order's items may require many calls (**under-fetching**, and the **N+1 round-trip** problem), while each response carries fields the screen does not use (**over-fetching**). **GraphQL** lets the client describe exactly the fields and nested resources it wants in **one request**, which suits many different clients (mobile, web, partners), at the cost of harder **caching**, the risk of expensive queries (you need depth and cost limits), and server-side N+1 database queries unless you batch.",
            "**gRPC** uses a typed contract (**protobuf**), generated client and server code, compact **binary** messages over **HTTP/2** with multiplexing and **streaming**. It is excellent for **service-to-service** calls (smaller, faster, strongly typed, with deadlines propagated) and poor for browsers and for casual debugging. A typical large system uses all three: gRPC between internal services, REST for public and partner APIs, and a **backend-for-frontend (BFF)** (often GraphQL) that aggregates calls for each client. Whichever you pick, the contract (OpenAPI, protobuf, GraphQL schema) is the source of truth, with generated clients and contract tests.",
        ],
        analogy="Ordering food: REST is a menu where you order each dish separately and get the whole dish; GraphQL is telling the waiter exactly which parts of which dishes you want in one order; gRPC is the kitchen's internal ticket system: terse, structured, and unreadable to guests.",
        visual=[STYLES_VIZ],
        sim=None,
        walk=[
            ("List the callers", "Browsers, mobile apps, partners, other services: each has different needs."),
            ("Count round trips for the busiest screen", "If it takes many calls, aggregate (BFF or GraphQL) rather than chat."),
            ("Pick the contract language", "OpenAPI for REST, protobuf for gRPC, a schema for GraphQL; generate clients."),
            ("Guard the expensive ones", "Depth and cost limits for GraphQL; deadlines for gRPC; pagination everywhere."),
            ("Standardise errors, auth, tracing across styles", "A request id and consistent errors make mixed systems debuggable."),
        ],
        groups=[
            dict(title="Round trips, fields and bytes", cmds=[
                dict(c=r'''python3 - <<'EOF'
import json, struct
users = {1: {'id': 1, 'name': 'Asha Rao', 'email': 'asha@example.com', 'phone': '+91 98450 00001', 'address': '12 MG Road, Bengaluru', 'plan': 'pro', 'created': '2024-01-15', 'locale': 'en-IN', 'tz': 'Asia/Kolkata', 'marketing': True, 'avatar': 'https://img.example.com/u/1.png', 'notes': 'x' * 40}}
orders = {1: [{'id': 100 + i, 'user': 1, 'total': 10 * i, 'status': 'paid', 'items': [1000 + i, 2000 + i], 'created': '2026-10-%02d' % (i % 28 + 1)} for i in range(20)]}
# The home screen needs: the user's name, and for each of 20 orders: id, total.
print('REST, one resource per call:')
calls = 1 + 1; print('  GET /users/1, GET /users/1/orders  ->  %d round trips (add one per order if details are separate: %d)' % (calls, calls + 20))
rest_bytes = len(json.dumps(users[1])) + len(json.dumps(orders[1]))
print('  bytes received: %d (every field of every object)' % rest_bytes)
gql = {'name': users[1]['name'], 'orders': [{'id': o['id'], 'total': o['total']} for o in orders[1]]}
print('GraphQL-style, one request that names the fields:  1 round trip, %d bytes' % len(json.dumps(gql)))
# a binary encoding for the same 20 orders: id (uint32) + total (uint32), after a short header
packed = struct.pack('<H', len(orders[1])) + b''.join(struct.pack('<II', o['id'], o['total']) for o in orders[1])
print('Binary (protobuf-like, fixed-size ints):  %d bytes for the order list (JSON: %d bytes for the same fields)' % (len(packed), len(json.dumps([{'id': o['id'], 'total': o['total']} for o in orders[1]]))))
EOF''',
                     e="Three ways to serve the same home screen. With REST, the screen makes at least two calls (and 22 if each order's details are separate), and downloads every field of every object although it shows two. A request that names the fields it wants (the GraphQL idea) needs **one** round trip and a fraction of the bytes. A binary encoding with fixed-size integers shrinks the order list further: this is why gRPC is popular between internal services (real protobuf uses variable-length integers and tags, so its size differs a little; the principle is the same). None of the three is better in general: each moves the cost somewhere else.",
                     annot=[("REST ... 2 round trips (add one per order if details are separate: 22)", "chatty: the number of calls grows with the data"),
                            ("bytes received: 2389 (every field of every object)", "over-fetching: the screen shows two fields of each order"),
                            ("GraphQL-style ... 1 round trip, 561 bytes", "the client names the fields: fewer calls and fewer bytes"),
                            ("Binary ... 162 bytes (JSON: 529 for the same fields)", "compact, typed, fast to parse: the appeal of gRPC between services")]),
            ]),
        ],
        scenario=dict(
            title="\"REST, GraphQL or gRPC for our system? We have mobile apps, a web app, partners and about 40 internal services.\"",
            ask="A judgement question. A good answer maps each style to a caller and names the costs, instead of choosing a winner.",
            clarify=[("Who are the clients, how different are their needs, and do we control them?", "Controlled internal clients can use gRPC; external partners need stability and simplicity; varied UIs need flexibility.")],
            think=[("Split by caller.", "Internal service-to-service: gRPC (typed contracts, speed, streaming, deadlines). Public and partner API: REST with OpenAPI (universal, cacheable, debuggable). Mobile and web clients: a BFF that aggregates calls, possibly GraphQL."),
                   ("Say what GraphQL costs.", "Caching is harder (single endpoint, POST), expensive nested queries need depth and cost limits and persisted queries, resolvers can cause N+1 database queries (use batching like DataLoader), and authorisation must be per field."),
                   ("Say what gRPC costs.", "Browsers need gRPC-Web or a gateway, debugging needs tools, load balancing needs L7 awareness (long-lived HTTP/2 connections), and schema evolution rules (never reuse field numbers)."),
                   ("Say what REST costs.", "Chatty for aggregate screens, over-fetching, and many endpoints to maintain; mitigate with sparse fieldsets, embedding and a BFF."),
                   ("Keep one contract discipline.", "OpenAPI/protobuf/schema as the source of truth; generated clients; contract tests; a consistent error model, auth, request ids and tracing across all three."),
                   ("Recommend.", "gRPC inside, REST outside, BFF for the apps; adopt GraphQL only where client diversity justifies its cost.")],
            answer=["\"I would not pick one. Between our internal services I would use gRPC: typed contracts, generated clients, compact binary messages, streaming and deadlines. For partners and the public I would offer REST with an OpenAPI description, because it is universal, cacheable and easy to debug. For the mobile and web apps I would put a backend-for-frontend that aggregates calls, and use GraphQL there only if our clients are diverse enough to justify its costs.",
                    "Those costs are real: GraphQL makes caching harder, needs depth and cost limits and batching to avoid N+1 queries; gRPC needs a gateway for browsers and L7 load balancing; REST is chatty for aggregate screens. Across all three I would keep one discipline: a schema as the source of truth, generated clients, contract tests, and consistent errors, auth, request ids and tracing.\""],
            follow=[("What is the N+1 problem in GraphQL?", "A list resolver triggers one database query per item for a nested field; batching (DataLoader) turns N queries into one."),
                    ("Why is load balancing gRPC tricky?", "It uses a few long-lived HTTP/2 connections with many multiplexed calls, so connection-level balancing sends all calls to one backend; use an L7 balancer or client-side balancing."),
                    ("How do you evolve a protobuf schema safely?", "Add fields with new numbers, never reuse or renumber, never change types: old and new code can then interoperate.")],
            slips=["Naming one style as the winner.", "Ignoring GraphQL's caching and cost issues.", "Exposing gRPC directly to browsers without a plan."],
        ),
        quick=[
            ("What is over-fetching?", "Receiving more fields than the client needs."),
            ("Where does gRPC fit best?", "Service-to-service calls: typed, compact, fast, with streaming and deadlines."),
            ("What is a BFF?", "A backend-for-frontend: a service that aggregates and shapes calls for one kind of client."),
        ],
        traps=[
            "Exposing a GraphQL endpoint with no depth or cost limits: one query can take the service down.",
            "Choosing gRPC for a public API where customers expect curl.",
            "Three styles with three different error models and no shared tracing.",
        ],
    ),
    dict(
        title="Reliable APIs: idempotency keys, async jobs and webhooks",
        tier="hot",
        situation="A mobile client on a train retries an order three times. A report endpoint takes 90 seconds. A partner needs to know when a payment settles. Reliable APIs make retries harmless, long work asynchronous and notifications trustworthy.",
        learn=["Idempotency keys on POST, against a real server", "The 202 Accepted pattern for long work", "Webhooks: signatures, retries and duplicates", "Putting the reliability checklist together"],
        model=[
            "**Idempotency keys**: the client sends a unique `Idempotency-Key` with each creating request; the server stores the key and the response in the same transaction as the effect and returns the **stored response** for a repeat (often with a replay header), rejecting the same key with a different body. This makes network retries safe. **Long-running work** should not hold a connection open: return **`202 Accepted`** with a `Location` for a **job resource**, process in the background (a queue), and let the client **poll** the job (`pending`, `done`, `failed`, with a result URL) or receive a **webhook**.",
            "**Webhooks** are your API calling your customer's server. Treat them as at-least-once: sign every request (an **HMAC** of timestamp and body with a shared secret) so the receiver can verify the sender and reject old replays; expect the receiver to be down, so retry with exponential backoff for a while; include a stable **event id** so receivers can **deduplicate**; and let receivers answer quickly (`2xx`) and process afterwards. Offer a way to **replay** missed events. A reliable API also documents its **timeouts, retry guidance, rate limits and error codes**, and exposes a **request id** in every response for support.",
        ],
        analogy="A pizza order line that records your order number: if you phone twice with the same number, they say \"already making it\" instead of baking two. A long order gets a ticket and a text when ready, and the shop signs the text so you know it is really them.",
        visual=[WEBHOOK_SEQ],
        sim=None,
        walk=[
            ("Client generates a key and sends the request", "One key per intended operation, reused on every retry."),
            ("Server records key, result and effect together", "A repeat returns the stored response: no second effect."),
            ("Long work returns 202 and a job URL", "A queue and worker do the work; the client polls or waits for a webhook."),
            ("Webhooks are signed and retried", "The receiver verifies the HMAC and timestamp, answers fast, and dedupes by event id."),
            ("Everything is observable", "Request ids, per-key logs and replay tools make support possible."),
        ],
        groups=[
            dict(title="Idempotency on the real API, async jobs and signed webhooks", cmds=[
                dict(volatile=True, c=r'''. ~/api/rig.sh; apiup
echo "--- without a key, a retried POST creates two orders:"
curl -s -X POST $B/orders -d '{"item": 7}' | tr -d '\n'; echo; curl -s -X POST $B/orders -d '{"item": 7}' | tr -d '\n'; echo
echo "--- with the same Idempotency-Key, the retry returns the stored result:"
curl -si -X POST $B/orders -H "Idempotency-Key: k-123" -d '{"item": 9}' | grep -E "^(HTTP|Idempotent|Location)|^\{" | tr -d '\r'
curl -si -X POST $B/orders -H "Idempotency-Key: k-123" -d '{"item": 9}' | grep -E "^(HTTP|Idempotent|Location)|^\{" | tr -d '\r'
apidown''',
                     e="The retry problem and its fix on the real server. Without a key, two identical POSTs give orders 1 and 2. With the same `Idempotency-Key`, the first call creates order 3 (`201 Created`, with `Location`), and the retry returns **the same order 3** with an `Idempotent-Replayed: true` header and no new order. The client can retry as often as the network demands. (A real implementation also stores the request fingerprint and rejects the same key with a different body.)",
                     annot=[("{\"id\": 1 ...} then {\"id\": 2 ...}", "no key: each retry created a new order"),
                            ("HTTP/1.1 201 Created / Location: /orders/3", "the first call with the key creates the order"),
                            ("HTTP/1.1 200 OK / Idempotent-Replayed: true / {\"id\": 3 ...}", "the retry got the same order back: no duplicate")]),
                dict(volatile=True, c=r'''python3 - <<'EOF'
# The 202 pattern: POST starts a job and returns at once; the client polls the job resource.
import json, threading, time, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
jobs = {}
def work(jid):
    time.sleep(1.0); jobs[jid] = {'status': 'done', 'result': '/reports/%d.pdf' % jid}      # the slow part (a report)
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def reply(self, code, body, extra=()):
        d = json.dumps(body).encode(); self.send_response(code); self.send_header('Content-Length', str(len(d)))
        for k, v in extra: self.send_header(k, v)
        self.end_headers(); self.wfile.write(d)
    def do_POST(self):
        jid = len(jobs) + 1; jobs[jid] = {'status': 'pending'}; threading.Thread(target=work, args=(jid,)).start()
        self.reply(202, jobs[jid], [('Location', '/jobs/%d' % jid), ('Retry-After', '1')])
    def do_GET(self): self.reply(200, jobs[int(self.path.split('/')[2])])
srv = ThreadingHTTPServer(('127.0.0.1', 8302), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
t0 = time.time()
req = urllib.request.Request('http://127.0.0.1:8302/reports', method='POST'); r = urllib.request.urlopen(req)
print('POST /reports -> %d %s in %.0f ms, Location: %s' % (r.status, r.reason, (time.time() - t0) * 1000, r.headers['Location']))
while True:
    s = json.load(urllib.request.urlopen('http://127.0.0.1:8302' + r.headers['Location']))
    print('  poll after %.1f s: %s' % (time.time() - t0, s))
    if s['status'] == 'done': break
    time.sleep(0.5)
srv.shutdown()
EOF''',
                     e="Long work without a long request. The `POST` returns **`202 Accepted`** in a few milliseconds with a `Location` for the job and a `Retry-After` hint; the work (one second here, ninety in real life) happens in a background thread. The client polls the job resource until it reports `done` with a result link. The connection is never held open, so proxies and mobile networks cannot kill it, and the same job could equally notify a webhook when done.",
                     annot=[("POST /reports -> 202 Accepted in ~17 ms, Location: /jobs/1", "the request returned immediately with a handle to the work"),
                            ("poll after 0.0 s: {'status': 'pending'} ...", "the client asks again until the job finishes"),
                            ("{'status': 'done', 'result': '/reports/1.pdf'}", "the final state links to the result")]),
                dict(c=r'''python3 - <<'EOF'
# Webhook verification: HMAC of "timestamp.body" with a shared secret, constant-time compare, reject old timestamps, dedupe by event id.
import hmac, hashlib, time
SECRET = b'whsec_demo_only'
seen = set()
def sign(body, ts): return hmac.new(SECRET, ('%d.' % ts).encode() + body, hashlib.sha256).hexdigest()
def receive(body, ts, signature, event_id, now):
    if abs(now - ts) > 300: return 'REJECT: timestamp too old (replay)'
    if not hmac.compare_digest(sign(body, ts), signature): return 'REJECT: bad signature (not from the provider, or body altered)'
    if event_id in seen: return '200 OK, duplicate ignored (already processed)'
    seen.add(event_id); return '200 OK, processed'
now = 1_800_000_000; body = b'{"event":"payment.settled","id":"evt_1","amount":4999}'
good = sign(body, now)
print('genuine request:            ', receive(body, now, good, 'evt_1', now))
print('same event delivered again: ', receive(body, now, good, 'evt_1', now + 30))
print('body tampered with:         ', receive(body.replace(b'4999', b'9999'), now, good, 'evt_2', now))
print('forged signature:           ', receive(body, now, 'deadbeef' * 8, 'evt_3', now))
print('captured request replayed 1h later:', receive(body, now, good, 'evt_9', now + 3600))
EOF''',
                     e="The receiving side of a webhook, with the checks that matter. A genuine request verifies and is processed. The provider's **retry** of the same event is recognised by its event id and acknowledged without reprocessing (the 200 stops further retries). A tampered body or a forged signature fails the HMAC comparison (done with a constant-time compare to avoid timing leaks). A captured request replayed an hour later is rejected by the timestamp window. These four checks are the difference between a webhook endpoint anyone can trigger and one you can trust.",
                     annot=[("genuine request: 200 OK, processed", "signature valid, timestamp fresh, new event id"),
                            ("same event delivered again: 200 OK, duplicate ignored", "at-least-once delivery: dedupe by event id and still return 200"),
                            ("body tampered with: REJECT: bad signature", "the HMAC covers the body, so any change is detected"),
                            ("replayed 1h later: REJECT: timestamp too old", "an attacker cannot reuse a captured request outside the window")]),
            ]),
        ],
        scenario=dict(
            title="\"Design the payments API for a platform: creating a charge, asynchronous settlement, and notifying merchants.\"",
            ask="A synthesis question. They want idempotency, status modelling, async processing, webhooks and failure behaviour in one design.",
            clarify=[("How long can settlement take, and how do merchants learn the outcome?", "Card authorisation is quick; settlement takes days: merchants need notifications, not polling for days.")],
            think=[("Create the charge safely.", "`POST /charges` with a required `Idempotency-Key`; the server stores key, request fingerprint and the response with the charge in one transaction; a replay returns the same response; a different body with the same key is `422`."),
                   ("Model state explicitly.", "A charge has a status (`pending`, `authorised`, `captured`, `failed`, `refunded`) with timestamps and an immutable event history; clients read it with `GET /charges/{id}`."),
                   ("Make slow steps asynchronous.", "Authorisation may return `202` with a pending status; a worker talks to the card network via a queue (with the provider's own idempotency key and retries); the outcome updates the charge."),
                   ("Notify with webhooks.", "On each state change emit an event through the outbox; deliver with signed webhooks (HMAC with timestamp), retries with exponential backoff for days, unique event ids, a delivery log and a replay endpoint; merchants answer quickly and dedupe."),
                   ("Support and safety.", "Request ids on every response; per-merchant rate limits; auditing; a dashboard of failed deliveries; versioned events."),
                   ("Concurrency.", "State transitions use compare-and-set (`update ... where status = 'authorised'`) so a capture and a void cannot both win."),
                   ("Say what could go wrong.", "Webhook endpoint down for hours (retries and replay), duplicate events (dedupe), out-of-order events (include a sequence or the full current object so the order does not matter).")],
            answer=["\"Creating a charge is a POST with a required idempotency key. The server stores the key and the response in the same transaction as the charge, so a retry returns the same result and a different body with the same key is rejected. A charge is a state machine, pending, authorised, captured, failed, refunded, with an immutable event history and compare-and-set transitions so a capture and a void cannot both win.",
                    "Slow steps are asynchronous: a worker calls the card network through a queue, using the provider's own idempotency key and retries, and updates the charge. Each state change writes an event through the outbox, and webhooks deliver it to merchants, signed with an HMAC over a timestamp and the body, retried with exponential backoff for days, with unique event ids so merchants can deduplicate, a delivery log and a replay endpoint. Every response carries a request id, and because events can arrive out of order the payload contains the current object or a sequence number.\""],
            follow=[("How do you handle out-of-order webhooks?", "Include a sequence number or version and the full resource state; receivers ignore events older than what they already hold, or fetch the current state from the API."),
                    ("What if the merchant's endpoint is down for a day?", "Keep retrying with backoff for days, surface failures in a dashboard, and provide a replay endpoint to fetch missed events."),
                    ("Why store the request fingerprint with the key?", "To detect a client reusing a key for a different request, which is a bug that must not silently return the wrong response.")],
            slips=["No idempotency on the create call.", "Webhooks without signatures or event ids.", "Assuming webhooks arrive once and in order."],
        ),
        quick=[
            ("What does `202 Accepted` tell the client?", "The request was accepted for processing; the work is not finished; check the job resource or wait for a webhook."),
            ("Why sign webhooks with an HMAC including a timestamp?", "So the receiver can verify the sender and body, and reject replays of old captured requests."),
            ("Why must webhook receivers deduplicate?", "Providers retry on failure, so the same event can arrive more than once."),
        ],
        traps=[
            "Webhook handlers that do all the work before responding: they time out and trigger retries.",
            "Comparing signatures with `==` instead of a constant-time comparison.",
            "Idempotency keys cached with a short TTL: a late retry creates a duplicate.",
        ],
    ),
]

TAIL = dict(
    cases=[],
    cheat=[
        ["GET / PUT / DELETE", "safe or idempotent: retries and caches can rely on them"],
        ["POST", "create or act: not idempotent, so use an Idempotency-Key"],
        ["201 + Location", "created, here is the new resource"],
        ["400 / 401 / 403 / 404 / 409 / 429", "bad input / who are you / not allowed / missing / conflict / slow down"],
        ["5xx vs 4xx", "retry 5xx and 429 with backoff; fix the request for 4xx"],
        ["error body", "one shape: code, message, details, request id"],
        ["offset pagination", "simple; deep pages slow; rows skipped or repeated on change"],
        ["keyset (cursor)", "where id > last: fast at any depth, stable; opaque next token"],
        ["additive change", "safe if clients ignore unknown fields"],
        ["versioning", "run v1 and v2 side by side; Deprecation, Sunset and Link headers; measure then retire"],
        ["token bucket", "burst up to B, average R: the usual limiter"],
        ["fixed window", "cheap but allows 2x at the boundary"],
        ["429 + Retry-After", "tell clients how long to wait"],
        ["limiter store down", "usually fail open with an alert"],
        ["REST / gRPC / GraphQL", "public and partners / between services / flexible clients through a BFF"],
        ["N+1", "one call or query per item: batch or aggregate"],
        ["Idempotency-Key", "client-generated; stored with the effect; replay returns the stored response"],
        ["202 + job URL", "long work: accept, process in the background, poll or webhook"],
        ["webhook", "HMAC(timestamp.body), constant-time compare, short window, dedupe by event id, answer fast"],
        ["ETag + If-None-Match", "cheap revalidation (304) and optimistic concurrency with If-Match"],
    ],
    interview_intro="API answers are judged on the details that make an interface safe to use for years: precise HTTP semantics, retry safety, bounded responses, compatibility and failure behaviour. The worked scenarios in each lesson are the models to practise with.",
    interview=[
        dict(q="Design a REST API for a booking system: verbs, status codes and safe retries.",
             a=["Resources: bookings, availability, user bookings; verbs by guarantee; 201 with Location, 409 for conflicts, 429, 503.", "Idempotency-Key on POST stored with the effect; ETag and If-Match on updates; one error shape with a request id.", "Pagination, versioning, rate limits, auth and an OpenAPI contract with tests."],
             follow=["PUT or PATCH?", "409 versus 422?"], mistakes=["Verbs in URLs.", "200 for errors.", "No retry story."],
             angle="Reported by candidates as a very common API design prompt at large companies; not official."),
        dict(q="How do you paginate a large collection, and why not use offset?",
             a=["Offset skips by reading and discarding rows, so deep pages are slow, and inserts or deletes cause skipped or repeated items.", "Keyset: opaque cursor encoding the last key, `where key > cursor order by key limit n`, constant cost, stable; set a maximum page size.", "Trade-off: no random page jumps; add a total count only if really needed."],
             follow=["How do you paginate on a non-unique sort key?", "Should the cursor be signed?"], mistakes=["Unbounded page size.", "Letting clients parse cursors."]),
        dict(q="We must rename a field in a public API with thousands of clients. How?",
             a=["Never break v1: add the new field beside the old, deprecate the old.", "If a new shape is unavoidable, release v2 beside v1 through adapters; Deprecation, Sunset and Link headers; changelog and outreach.", "Measure usage per version and client; retire only when usage is gone or the published date passes; contract tests for both."],
             follow=["Where do you put the version?", "What is a tolerant reader?"], mistakes=["Renaming in place.", "Retiring without measuring."]),
        dict(q="Design a rate limiter for a public API on a fleet of servers.",
             a=["Token bucket per API key and plan, per endpoint class, plus a global limit; enforce at the gateway.", "Shared counters in Redis with an atomic script, or local buckets with shares; accept small inaccuracy; fail open with an alert.", "429 with Retry-After and limit headers; documented limits and a usage dashboard; monitor top consumers."],
             follow=["Why a Lua script?", "Per IP or per user?"], mistakes=["Fixed window sold as precise.", "No plan for limiter failure."],
             angle="Amazon and Google-style: commonly reported as a design question with follow-ups on distributed counting; reported by candidates, not official."),
        dict(q="REST, GraphQL or gRPC? We have mobile, web, partners and 40 internal services.",
             a=["Split by caller: gRPC between services, REST with OpenAPI for partners and public, a BFF (possibly GraphQL) for the apps.", "Costs: GraphQL caching, depth and cost limits, N+1 batching; gRPC browsers and L7 balancing; REST chattiness.", "One discipline across all: schema as source of truth, generated clients, contract tests, consistent errors, auth and tracing."],
             follow=["What is N+1 in GraphQL?", "Why is gRPC load balancing tricky?"], mistakes=["Naming one winner."]),
        dict(q="Design the payments API: charge creation, async settlement and merchant notifications.",
             a=["POST /charges with an Idempotency-Key stored with the charge; a state machine with compare-and-set transitions and an immutable event history.", "Slow steps through a queue with the provider's idempotency key; events through the outbox; signed webhooks with backoff for days, event ids, delivery log and replay.", "Handle out-of-order and duplicate events: sequence numbers and full state in the payload; request ids and audit."],
             follow=["Out-of-order webhooks?", "Merchant endpoint down for a day?"], mistakes=["Unsigned webhooks.", "Assuming exactly once and in order."]),
    ],
    selftest=[
        ("Which HTTP verbs are idempotent?", "GET, PUT, DELETE (and HEAD, OPTIONS)."),
        ("What does 201 Created include?", "A Location header for the new resource."),
        ("What should a client do on 429?", "Wait for Retry-After and retry with backoff."),
        ("Why is deep offset pagination slow?", "The database reads and discards all the skipped rows."),
        ("Is adding an optional response field breaking?", "No, if clients ignore unknown fields."),
        ("What headers announce a deprecated endpoint?", "Deprecation, Sunset and a Link to the successor."),
        ("What is the fixed-window weakness?", "Up to twice the limit around a window boundary."),
        ("What does a token bucket allow?", "Bursts up to its size while enforcing an average rate."),
        ("What is over-fetching?", "Receiving fields the client does not use."),
        ("Where is gRPC strongest?", "Service-to-service calls."),
        ("What is an idempotency key?", "A client-generated unique id so a retried request returns the stored result instead of repeating the effect."),
        ("What does 202 Accepted mean?", "Accepted for processing, not complete: use a job URL or webhook."),
        ("What must a webhook receiver verify?", "The HMAC signature (constant-time), a fresh timestamp and the event id for deduplication."),
    ],
    recall=[
        ["idempotent verbs", "GET, PUT, DELETE"],
        ["201", "Created + Location"],
        ["429", "Retry-After"],
        ["keyset", "where id > last"],
        ["additive change", "ignore unknown fields"],
        ["Deprecation / Sunset", "announce retirement"],
        ["token bucket", "burst plus average"],
        ["REST / gRPC / GraphQL", "outside / inside / BFF"],
        ["Idempotency-Key", "retry returns stored result"],
        ["202", "accepted, job URL"],
        ["webhook", "HMAC, timestamp, event id"],
    ],
    sources=[
        dict(title="MDN: HTTP request methods and response status codes", url="https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods", use="Safe and idempotent methods and what each status means", license="CC BY-SA; read online", how="Link only"),
        dict(title="RFC 9110: HTTP Semantics", url="https://www.rfc-editor.org/rfc/rfc9110", use="The authoritative definitions of methods, status codes and conditional requests", license="IETF; read online", how="Link only"),
        dict(title="Stripe API: idempotent requests", url="https://docs.stripe.com/api/idempotent_requests", use="A widely copied idempotency key design", license="Copyright Stripe; read online", how="Link only"),
        dict(title="Stripe: Webhook signatures", url="https://docs.stripe.com/webhooks#verify-events", use="Timestamped HMAC webhook verification as in the lesson", license="Copyright Stripe; read online", how="Link only"),
        dict(title="OpenAPI Specification", url="https://spec.openapis.org/oas/latest.html", use="The contract language for REST APIs", license="Apache 2.0; read online", how="Link only"),
        dict(title="gRPC documentation: core concepts", url="https://grpc.io/docs/what-is-grpc/core-concepts/", use="Protobuf, streaming and deadlines", license="Apache 2.0; read online", how="Link only"),
        dict(title="Google API design guide", url="https://cloud.google.com/apis/design", use="Resource-oriented design, pagination, errors and versioning from a large API producer", license="CC BY 4.0; read online", how="Link only"),
    ],
    plan=[
        "**Hours 1 to 2:** HTTP basics: build the rig, call every verb, then add a `PATCH` endpoint to the server and explain its guarantees.",
        "**Hours 3 to 4:** pagination and evolution: run both timings with different depths; design a v2 of the item resource on paper.",
        "**Hours 5 to 6:** rate limiting: change the limit and the arrival pattern; explain every output.",
        "**Hours 7 to 8:** API styles: count bytes and round trips for another screen of your own choosing.",
        "**Hour 9:** reliability: break the idempotency demo on purpose (omit the key) and fix it again; extend the webhook checks.",
        "**Hours 10 and 11:** say each interview scenario aloud for two minutes, timed, and compare with the written answer.",
    ],
)
