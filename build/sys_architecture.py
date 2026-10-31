"""Systems Mastery S19: architecture and API patterns."""
import sysviz as v

API_VIZ = v.figure(
    720, 214,
    [v.box(10, 14, 220, 56, "REST", "acc", "resources + HTTP verbs, JSON"),
     v.box(250, 14, 220, 56, "gRPC", "acc", "typed calls, binary, streaming"),
     v.box(490, 14, 220, 56, "GraphQL", "acc", "client picks the fields"),
     v.text(120, 96, "public APIs, simple CRUD,", "dg-s"), v.text(120, 114, "cacheable with plain HTTP", "dg-s"),
     v.text(360, 96, "service to service, low latency,", "dg-s"), v.text(360, 114, "strict contracts (protobuf)", "dg-s"),
     v.text(600, 96, "mobile and web clients with", "dg-s"), v.text(600, 114, "varied data needs", "dg-s"),
     v.text(360, 156, "All three sit on the same ideas: a contract, versioning, errors, authentication, pagination.", "dg-s"),
     v.text(360, 182, "Pick the one your clients and your team can use well, then be consistent.", "dg-s")],
    "Three API styles", "Choose by who calls the API and what they need")

MODULE = dict(
    id="ar",
    title="Architecture and API patterns",
    lead="This module covers how services are shaped and how they talk: monolith versus microservices, designing REST APIs (and when gRPC or GraphQL fit), events and CQRS, sagas for multi-service operations, rate limiting, and authentication. Every pattern comes with its price, and you will run small versions of each.",
    time="6 to 7 hours",
    why=[
        "A team splits a working monolith into twelve microservices because it sounds modern. Releases get slower, a checkout now crosses five network calls, and one failing service takes the site down. The pattern was not wrong, the reason was: nobody counted the cost.",
        "Interviewers ask \"monolith or microservices?\", \"how would you design this API?\", \"how do you keep data consistent across services?\", \"how would you rate limit?\" The right answers name the trade-off, not a favourite.",
    ],
    outcomes=[
        "Decide between a monolith and microservices, and state what each costs.",
        "Design a clean REST API: resources, status codes, pagination, versioning and errors.",
        "Explain events, pub/sub, CQRS and event sourcing in plain terms.",
        "Explain sagas and compensation for operations that span services.",
        "Implement and compare token-bucket and fixed-window rate limits.",
        "Explain sessions, signed tokens (JWT), OAuth at a high level, and authentication versus authorisation.",
    ],
    before=[
        "The distributed systems module (S18) helps a lot, because the costs of these patterns are its lessons.",
        "Experiments use `python3` and `curl` on localhost; they are deterministic.",
    ],
    env=["Scratch folder: `mkdir -p ~/arch && cd ~/arch`."],
    lessons=[
        dict(
            title="Monolith or microservices",
            tier="hot",
            situation="The team is growing and releases keep colliding. Someone suggests microservices. Is that the fix?",
            learn=["What each style gives and costs", "When to split", "Why a chain of calls is less reliable than each call"],
            model=[
                "A **monolith** is one deployable application: in-process calls, one database and one transaction, easy to run and debug. **Microservices** split the system into small services, each owning its own data and deployed on its own, reached over the network. Benefits: independent releases and scaling, and team autonomy. Costs: every call can be slow or fail, no shared transaction across services, and a lot of operational work (deployment, monitoring, tracing). A sensible path is a **well-structured monolith first**, then extract a service when a specific team, scaling or release problem justifies the cost.",
            ],
            analogy="One kitchen where every cook can reach every ingredient, versus a food court of separate stalls: stalls are independent, but now you need runners, a payment system between them and a plan for when one stall closes.",
            sim="micro",
            groups=[
                dict(title="The reliability price of splitting", cmds=[
                    dict(c="python3 -c \"for n in (1,3,5,8,12):\n    print('%2d serial calls, each 99.9%% available: whole request %.2f%% available' % (n, 100*0.999**n))\"", e="If one request needs several services in a row and each is 99.9 percent available, the request is only as reliable as all of them together: 12 calls in series drop it to about 98.8 percent, which is hours of extra downtime a year. Fewer hops, timeouts, retries and fallbacks matter more than any single service's quality."),
                ]),
            ],
            quick=[
                ("What is the main reliability cost of splitting into many services?", "Every network call can fail or be slow, and availability multiplies down along a chain of calls."),
                ("When is it reasonable to extract a service?", "When a specific scaling, release-independence or team-ownership problem justifies the added network and operational cost."),
            ],
            traps=[
                "A distributed monolith: services that must be deployed together and share a database give the costs of both styles.",
                "Splitting by technical layer (an \"API service\", a \"DB service\") instead of by business capability.",
            ],
        ),
        dict(
            title="Designing a REST API",
            tier="hot",
            situation="Mobile apps and partners will call your service for years. Mistakes in the API are the hardest to undo.",
            learn=["Resources, verbs and status codes", "Pagination, errors and versioning", "REST versus gRPC versus GraphQL"],
            model=[
                "A **REST** API models **resources** (nouns such as `/v1/items/6`) and uses HTTP verbs: **GET** reads, **POST** creates, **PUT** or **PATCH** updates, **DELETE** removes. Use status codes honestly: **200** OK, **201** Created (with a `Location` header), **400** bad request, **401** not authenticated, **403** forbidden, **404** not found, **429** too many requests, **5xx** server fault. Big lists need **pagination** (limit and offset, or an opaque cursor). Errors should be structured JSON with a machine-readable code. Put a **version** in the path so you can evolve it without breaking clients. **gRPC** uses typed binary contracts and suits service-to-service calls; **GraphQL** lets clients ask for exactly the fields they need.",
            ],
            analogy="A restaurant menu: clear item names, one standard way to order, and a numbered receipt format so every customer understands every response.",
            visual=API_VIZ,
            groups=[
                dict(title="A small API, called with curl", cmds=[
                    dict(c="mkdir -p ~/arch && cd ~/arch && cat > api.py <<'EOF'\nimport http.server, socketserver, json\nfrom urllib.parse import urlparse, parse_qs\nITEMS = [{'id': i, 'name': 'item%d' % i} for i in range(1, 6)]\nclass H(http.server.BaseHTTPRequestHandler):\n    def send(self, code, obj, headers=()):\n        body = json.dumps(obj).encode()\n        self.send_response(code)\n        self.send_header('Content-Type', 'application/json')\n        self.send_header('Content-Length', str(len(body)))\n        for k, v in headers:\n            self.send_header(k, v)\n        self.end_headers(); self.wfile.write(body)\n    def do_GET(self):\n        u = urlparse(self.path); q = parse_qs(u.query)\n        if u.path == '/v1/items':\n            limit = int(q.get('limit', ['2'])[0]); off = int(q.get('offset', ['0'])[0])\n            nxt = off + limit if off + limit < len(ITEMS) else None\n            self.send(200, {'items': ITEMS[off:off + limit], 'next_offset': nxt})\n        elif u.path.startswith('/v1/items/'):\n            i = int(u.path.rsplit('/', 1)[1]); m = [x for x in ITEMS if x['id'] == i]\n            if m: self.send(200, m[0])\n            else: self.send(404, {'error': 'not_found', 'message': 'no item %d' % i})\n        else:\n            self.send(404, {'error': 'not_found'})\n    def do_POST(self):\n        n = int(self.headers.get('Content-Length', 0)); data = json.loads(self.rfile.read(n) or b'{}')\n        item = {'id': len(ITEMS) + 1, 'name': data.get('name', '?')}; ITEMS.append(item)\n        self.send(201, item, [('Location', '/v1/items/%d' % item['id'])])\n    def log_message(self, *a): pass\nsocketserver.TCPServer.allow_reuse_address = True\nsocketserver.TCPServer(('127.0.0.1', 8086), H).serve_forever()\nEOF\n(python3 api.py >/dev/null 2>&1 &); sleep 1; curl -s 'http://127.0.0.1:8086/v1/items?limit=2'; echo", e="A tiny API with versioned paths. `GET /v1/items?limit=2` returns the first page and a `next_offset` the client uses to fetch the next one: pagination keeps responses small and predictable."),
                    dict(c="curl -s 'http://127.0.0.1:8086/v1/items?limit=2&offset=4'; echo; curl -s -w ' -> HTTP %{http_code}\\n' http://127.0.0.1:8086/v1/items/99", e="The last page has `next_offset: null`, so the client knows to stop. A missing resource returns **404** with a structured error body (a code a program can read, plus a human message), not a 200 with an apology."),
                    dict(c="curl -si -X POST -d '{\"name\":\"widget\"}' http://127.0.0.1:8086/v1/items | grep -E '^(HTTP|Location)'; curl -s http://127.0.0.1:8086/v1/items/6; echo", e="Creating a resource returns **201 Created** and a `Location` header with its address, and a GET of that address shows it. Using the right code and header lets generic clients behave correctly.", parts=[("-X POST -d '...'", "send a POST with a JSON body"), ("201 + Location", "created, and where to find it")]),
                    dict(c="pkill -f 'api.py'; echo stopped", e="Stop the practice API."),
                ]),
            ],
            quick=[
                ("Which status code means a resource was created, and which header says where?", "201 Created, with a `Location` header."),
                ("Why paginate a list endpoint?", "To keep responses small and fast and avoid returning millions of rows at once; clients follow a cursor or offset."),
            ],
            traps=[
                "Returning 200 with `{\"error\": ...}` for failures: clients, caches and monitors all misread it.",
                "Changing a field's meaning inside the same version; add new fields or a new version instead.",
                "Offset pagination over data that changes can skip or repeat items; a cursor is safer for large feeds.",
            ],
        ),
        dict(
            title="Events, pub/sub, CQRS and event sourcing",
            tier="hot",
            situation="When an order is placed, five other systems need to know: email, stock, analytics, fraud, loyalty points. Calling all five from the order service ties them together.",
            learn=["Publishing events instead of calling services", "CQRS: separate writes and reads", "Event sourcing and replay"],
            model=[
                "In an **event-driven** design a service publishes an **event** (\"OrderPlaced\") to a broker and any number of subscribers react: the publisher no longer knows or waits for them (**pub/sub**), which decouples teams and absorbs failures through queues. **CQRS** separates the **write** side (commands, validation) from **read** views built for queries. With **event sourcing** the log of events is the source of truth: current state is derived by replaying it, and you can rebuild any view or add a new one later. The price: eventual consistency (a view lags the write), harder debugging and the need to evolve event formats carefully.",
            ],
            analogy="A noticeboard in a office: someone posts \"order placed\"; each department reads it when ready and does its part, without the poster phoning five people.",
            sim="cqrs",
            groups=[
                dict(title="Rebuild state by replaying events", cmds=[
                    dict(c="mkdir -p ~/arch && cd ~/arch && cat > events.py <<'EOF'\nevents = [\n    ('OrderPlaced',  {'order': 1, 'customer': 'asha', 'total': 30}),\n    ('OrderPlaced',  {'order': 2, 'customer': 'ben',  'total': 15}),\n    ('OrderPaid',    {'order': 1}),\n    ('OrderPlaced',  {'order': 3, 'customer': 'asha', 'total': 20}),\n    ('OrderCancelled', {'order': 2}),\n]\n# Read view 1: orders by status. Read view 2: spend per customer. Both built from the same log.\nstatus, spend, owner = {}, {}, {}\nfor kind, e in events:\n    if kind == 'OrderPlaced':\n        status[e['order']] = 'placed'; owner[e['order']] = e['customer']\n        spend[e['customer']] = spend.get(e['customer'], 0) + e['total']\n    elif kind == 'OrderPaid':\n        status[e['order']] = 'paid'\n    elif kind == 'OrderCancelled':\n        status[e['order']] = 'cancelled'\nprint('orders by status:', status)\nprint('spend per customer (placed orders):', spend)\nEOF\npython3 events.py", e="One history of five events produces two different read views. If a new question arrives tomorrow (\"how many orders were cancelled per customer?\") you write a new projection and replay the same log: nothing was thrown away. (In real systems the projection also subtracts cancelled orders; this view deliberately shows only what each event did.)"),
                ]),
            ],
            quick=[
                ("What does publishing an event instead of calling a service change?", "The publisher no longer knows or waits for consumers, so teams are decoupled and failures are absorbed by the queue."),
                ("What is the cost of CQRS read views?", "They update slightly after the write, so reads are eventually consistent."),
            ],
            traps=[
                "Event sourcing everywhere: it adds heavy complexity; use it where history and replay genuinely matter (finance, audit).",
                "Events that carry no version or schema discipline become impossible to change; plan for evolution from day one.",
            ],
        ),
        dict(
            title="Sagas: consistency across services",
            tier="hot",
            situation="Placing an order reserves stock, charges a card and books a shipment in three services with three databases. The shipment fails. What now?",
            learn=["Why a distributed transaction is avoided", "Compensating actions", "Orchestration versus choreography"],
            model=[
                "Across services there is usually no single ACID transaction. A **saga** replaces it with a sequence of **local transactions**, each paired with a **compensating action** that undoes its effect semantically (a refund undoes a charge). If step three fails, the saga runs the compensations for steps two and one in reverse. A saga can be **orchestrated** (a coordinator tells each service what to do and tracks progress) or **choreographed** (each service reacts to the previous service's event). Every step and every compensation must be **idempotent** and retryable, and the system is only **eventually consistent**: intermediate states are visible to others.",
            ],
            analogy="Booking a holiday: flights, hotel, car. If the car is unavailable you cancel the hotel and flights; each booking has a defined way of being undone.",
            sim="saga",
            groups=[
                dict(title="A saga that fails and compensates", cmds=[
                    dict(c="mkdir -p ~/arch && cd ~/arch && cat > saga.py <<'EOF'\nsteps = [\n    ('reserve stock',    lambda: True,  'release stock'),\n    ('charge card',      lambda: True,  'refund card'),\n    ('create shipment',  lambda: False, 'cancel shipment'),\n]\ndone = []\nfor name, action, undo in steps:\n    ok = action()\n    print('%-16s -> %s' % (name, 'ok' if ok else 'FAILED'))\n    if not ok:\n        for prev_name, prev_undo in reversed(done):\n            print('  compensate: %-16s (undo of %s)' % (prev_undo, prev_name))\n        print('order cancelled, system consistent again')\n        break\n    done.append((name, undo))\nEOF\npython3 saga.py", e="The first two steps succeed and commit. The third fails, so the saga runs the compensations in reverse order: refund the card, then release the stock. The business state is consistent again, though other users could briefly have seen the stock as reserved."),
                ]),
            ],
            quick=[
                ("What is a compensating action?", "An operation that semantically undoes an earlier committed step, such as a refund for a charge."),
                ("Orchestration versus choreography?", "Orchestration uses a coordinator that directs the steps; choreography has services react to each other's events."),
            ],
            traps=[
                "Compensations that can fail or are not idempotent leave the order half-undone; make them retryable and monitor stuck sagas.",
                "Some steps cannot be undone (an email sent, a parcel shipped); order the steps so the irreversible ones come last.",
            ],
        ),
        dict(
            title="Rate limiting",
            tier="hot",
            situation="One client sends 5,000 requests per second by mistake, and everyone else's requests start timing out.",
            learn=["Why limit", "Token bucket versus fixed window", "429 and Retry-After"],
            model=[
                "A **rate limiter** protects a service from overload and abuse by capping how many requests a client may make. A **fixed window** counts requests per clock interval (simple, but a client can send a full quota at the end of one window and again at the start of the next, doubling the burst). A **token bucket** holds up to a capacity of tokens that refill at a steady rate; each request spends one, so short bursts are allowed but the long-run rate is bounded. Rejected requests get **HTTP 429 Too Many Requests**, ideally with a `Retry-After` header. In a fleet the counters need shared state (for example a cache) or each node enforces a share.",
            ],
            analogy="A water tank with a tap: the tank (capacity) lets you draw a burst; the refill (rate) limits how much you can draw over time.",
            sim="bucket",
            groups=[
                dict(title="Burst, then steady", cmds=[
                    dict(c="mkdir -p ~/arch && cd ~/arch && cat > bucket.py <<'EOF'\n# A client sends 10 requests every second for 6 seconds. Capacity 5, refill 2 tokens per second.\ncap, rate, tokens = 5, 2, 5.0\nfor second in range(6):\n    tokens = min(cap, tokens + (rate if second else 0))\n    allowed = 0\n    for _ in range(10):\n        if tokens >= 1:\n            tokens -= 1; allowed += 1\n    print('second %d: allowed %2d, rejected %2d' % (second, allowed, 10 - allowed))\n# Fixed window: limit 4 per 10 s window. A client sends 4 just before and 4 just after the boundary.\nprint('fixed window (limit 4 per 10 s): 4 requests at t=9.9 + 4 at t=10.0 = 8 accepted within 0.1 s')\nEOF\npython3 bucket.py", e="The first second allows a burst of 5 (the full bucket), after that only the refill rate of 2 per second gets through while the client keeps asking for 10. The last line shows the fixed-window weakness: two full quotas back to back across the window boundary.", parts=[("cap, rate", "bucket size and refill per second")]),
                ]),
            ],
            quick=[
                ("What status code means \"rate limited\"?", "429 Too Many Requests (with an optional Retry-After header)."),
                ("What weakness does a fixed window have?", "A client can use a full quota at the end of one window and another at the start of the next, doubling the burst."),
            ],
            traps=[
                "Limiting by IP alone punishes everyone behind a shared address and misses attackers with many IPs; limit by API key or user too.",
                "Per-node counters multiply the real limit by the number of nodes; share the counter or divide the quota.",
            ],
        ),
        dict(
            title="Authentication, tokens and authorisation",
            tier="hot",
            situation="Who is calling, and what are they allowed to do? Confusing the two questions causes most security bugs.",
            learn=["Authentication versus authorisation", "Sessions versus signed tokens (JWT)", "OAuth in one paragraph and password hashing"],
            model=[
                "**Authentication** answers \"who are you?\"; **authorisation** answers \"what may you do?\". After login the server can keep a **session** (a random ID stored server-side, sent in a cookie) or issue a **signed token** such as a **JWT**: a header, a payload of claims (user, role, expiry) and a signature made with a secret. Anyone can **read** a JWT (it is only encoded), but nobody can **change** it without the signature failing, so servers can verify tokens without a lookup. **OAuth 2** lets a user grant an application limited access to their data on another service without sharing a password. Store passwords only as **slow salted hashes** (bcrypt, scrypt, Argon2, PBKDF2), never in plain text.",
            ],
            analogy="A concert wristband: security checks your ticket once (authentication), the band says which areas you may enter (authorisation), and a forged band is spotted by its hologram (signature).",
            groups=[
                dict(title="Signed tokens and hashed passwords", cmds=[
                    dict(c="mkdir -p ~/arch && cd ~/arch && cat > tok.py <<'EOF'\nimport base64, hashlib, hmac, json\nb64 = lambda b: base64.urlsafe_b64encode(b).rstrip(b'=').decode()\nsecret = b'demo-secret'\ndef sign(msg):\n    return b64(hmac.new(secret, msg.encode(), hashlib.sha256).digest())\nhead = b64(b'{\"alg\":\"HS256\"}')\nbody = b64(json.dumps({'sub': 'asha', 'role': 'user'}).encode())\ntoken = head + '.' + body + '.' + sign(head + '.' + body)\nprint('token parts:', len(token.split('.')))\ndef check(t):\n    h, p, s = t.split('.')\n    return hmac.compare_digest(sign(h + '.' + p), s)\nprint('genuine token verifies:', check(token))\nforged_body = b64(json.dumps({'sub': 'asha', 'role': 'admin'}).encode())\nforged = head + '.' + forged_body + '.' + token.split('.')[2]\nprint('forged (role=admin) verifies:', check(forged))\nsalt = b'0123456789abcdef'\nh = hashlib.pbkdf2_hmac('sha256', b'correct horse', salt, 200000)\nprint('password check, right:', hashlib.pbkdf2_hmac('sha256', b'correct horse', salt, 200000) == h)\nprint('password check, wrong:', hashlib.pbkdf2_hmac('sha256', b'wrong guess', salt, 200000) == h)\nEOF\npython3 tok.py", e="The token verifies; changing the role in the payload without the secret makes the signature check fail. For passwords we store only the salted hash and compare hashes: the right password matches and a wrong one does not, and the 200,000 iterations make guessing slow.", parts=[("hmac + sha256", "signature that needs the secret to produce"), ("pbkdf2_hmac(..., 200000)", "deliberately slow, salted password hash")]),
                ]),
            ],
            quick=[
                ("Authentication versus authorisation?", "Authentication proves who you are; authorisation decides what you may do."),
                ("Can a client read the contents of a JWT? Can it change them undetected?", "It can read them (they are only encoded), but changing them breaks the signature, so the change is detected."),
            ],
            traps=[
                "Putting secrets in a JWT payload: it is readable by anyone who holds the token.",
                "Long-lived tokens with no way to revoke them; use short expiries plus refresh tokens.",
                "Storing passwords with a fast hash (plain SHA-256) or in plain text.",
            ],
        ),
    ],
    labs=[
        dict(kind="linux", script="rate-limiter", dir="rl", title="Replay a log through two rate limiters",
             goal=["Compare how a token bucket and a fixed window treat the same traffic."],
             story=["`requests.txt` holds the arrival times (in seconds) of 22 requests, including two bursts. The platform team wants to know how many get through under each limiter."],
             tasks=["Read `README.txt` for both rules.", "Replay the log through the token bucket (capacity 5, refill 1 per second) and count allowed requests.", "Replay it through the fixed window (4 per 10 seconds) and count allowed requests.", "Write `token_bucket_allowed=` and `fixed_window_allowed=` into `~/sys-lab/answers-rl.txt`."],
             check="Run the check script.", check_cmd="bash ~/sys-lab/check-rate-limiter.sh",
             hints=["Keep `tokens` and the `last` request time; on each request add `t - last` tokens (cap 5), then spend one if you have at least one.", "For the window use `int(t / 10)` as the window number and count per window.", "A short script (Python or awk) is easier than doing it by hand."],
             solution=["Token bucket: refill by elapsed seconds (max 5), allow if tokens >= 1.", "Fixed window: allow while the window's count is below 4.", "Write both counts to the answers file."]),
        dict(kind="linux", script="token-check", dir="tokens", title="Which tokens are valid?",
             goal=["Decode three signed tokens, verify their signatures and expiry, and spot a forgery."],
             story=["Three tokens arrived at an API. One is genuine, one has been tampered with to claim admin rights, and one has expired. `README.txt` gives the signing rule and the lab secret."],
             tasks=["Split each token into header, payload and signature, and decode the payload (base64url).", "Recompute the HMAC-SHA256 signature with the secret and compare, and check `exp`.", "Write `valid=` (file names without `.txt`) and `claims_admin=` into `~/sys-lab/answers-token.txt`."],
             check="Run the check script.", check_cmd="bash ~/sys-lab/check-token-check.sh",
             hints=["Python: `base64.urlsafe_b64decode(part + '=' * (-len(part) % 4))` decodes a part.", "The signature is `base64url(HMAC-SHA256(secret, header + '.' + payload))` without `=` padding.", "A forged payload with an unchanged signature fails the comparison."],
             solution=["Decode each payload and read `role` and `exp`.", "Recompute the signature: t1 matches and has a future expiry; t2 has role admin but a wrong signature; t3 matches but expired.", "`valid=t1` and `claims_admin=t2`."]),
    ],
    cases=[],
    cheat=[
        ["monolith first", "split when a real scaling, release or team problem justifies the network cost"],
        ["availability of a chain", "multiply: 99.9% x 12 calls is about 98.8%"],
        ["GET / POST / PUT / PATCH / DELETE", "read / create / replace / update / remove"],
        ["200 201 400 401 403 404 429 5xx", "ok / created / bad request / not authenticated / forbidden / not found / rate limited / server fault"],
        ["pagination", "limit+offset or an opaque cursor; always say when it ends"],
        ["/v1/...", "version in the path so you can evolve without breaking clients"],
        ["pub/sub", "publisher does not know or wait for subscribers"],
        ["CQRS", "separate command (write) and query (read view) models"],
        ["event sourcing", "events are the truth; state is a replay"],
        ["saga", "local transactions plus compensating actions in reverse"],
        ["token bucket vs fixed window", "bursts up to capacity then steady rate / simple but boundary double-burst"],
        ["429 + Retry-After", "rate limited, try again later"],
        ["JWT", "readable header and claims, signed: tampering is detected"],
        ["password storage", "salted slow hash (bcrypt, scrypt, Argon2, PBKDF2)"],
    ],
    interview_intro="Architecture answers are judged on whether you name the cost of your choice. End each answer with \"and the price of that is...\".",
    interview=[
        dict(q="Monolith or microservices for a new product? How do you decide?",
             a=["Start with a well-structured monolith: simpler to build, test, deploy and debug, and one transaction spans everything.", "Extract services when a concrete problem appears: independent scaling, team autonomy and release cadence, or fault isolation.", "Name the price: network calls, partial failure, no shared transaction, operational overhead (deployment, tracing, monitoring)."],
             follow=["How would you split an existing monolith?", "What is a distributed monolith?"], mistakes=["Choosing microservices because they are fashionable.", "Splitting by technical layer."],
             angle="Amazon-style: candidates commonly report follow-ups on ownership boundaries and who is on call for each service; reported by candidates, not official."),
        dict(q="Design a REST API for a resource such as orders. What do you pay attention to?",
             a=["Nouns for resources (`/v1/orders/{id}`), verbs via HTTP methods, correct status codes (201 with Location, 404, 409, 429).", "Pagination with a cursor, filtering and sorting, structured error bodies, versioning in the path.", "Idempotency keys for POSTs that must not repeat, authentication, rate limits and clear documentation (OpenAPI)."],
             follow=["How would you version a breaking change?", "PUT versus PATCH?"], mistakes=["Verbs in URLs (`/getOrder`).", "200 for errors."]),
        dict(q="Explain a saga. When do you use it and how does it fail?",
             a=["A sequence of local transactions with compensations, used when an operation spans services and a distributed transaction is not available.", "Orchestrated by a coordinator or choreographed through events.", "Failure handling: compensate in reverse order; steps and compensations must be idempotent and retryable; some actions cannot be undone, so order them last."],
             follow=["What happens if a compensation fails?"], mistakes=["Believing a saga gives ACID isolation."]),
        dict(q="Explain CQRS and event sourcing. What are the trade-offs?",
             a=["CQRS separates the write model from read models tailored to queries; event sourcing stores the sequence of events and derives state by replay.", "Benefits: scalable reads, audit trail, rebuild or add views. Costs: eventual consistency, complexity, event schema evolution."],
             follow=["How do you handle a read right after a write?"], mistakes=["Using it for a simple CRUD app."]),
        dict(q="How would you implement rate limiting for an API used by thousands of clients?",
             a=["Token bucket per API key (and per IP as a backstop), returning 429 with Retry-After.", "Keep counters in a fast shared store (for example Redis) or enforce per-node shares; accept small inaccuracy for speed.", "Decide limits per plan, allow bursts, monitor rejected traffic, and protect the limiter itself from failure (fail open or closed by design)."],
             follow=["Token bucket versus sliding window?", "What if the shared store is down?"], mistakes=["Per-node counters that multiply the limit."],
             angle="Google-style: candidates commonly report this as a design warm-up with follow-ups on scale and hot keys; reported by candidates, not official."),
        dict(q="Sessions versus JWTs: when would you choose each, and what are the risks of JWTs?",
             a=["Sessions: server-side state keyed by a random ID cookie; easy to revoke, needs shared storage when scaled out.", "JWTs: stateless verification by signature, convenient across services; hard to revoke, so use short expiry plus refresh tokens.", "Risks: secrets in the payload (it is readable), weak algorithms or keys, accepting `alg: none`, storing tokens where scripts can steal them."],
             follow=["How do you log a user out everywhere?"], mistakes=["Calling JWTs encrypted."]),
    ],
    selftest=[
        ("What is availability of 12 serial calls that are each 99.9% available?", "About 98.8% (0.999 to the 12th power)."),
        ("Which HTTP status means created, and which header accompanies it?", "201 Created and Location."),
        ("What is a compensating action?", "An operation that semantically undoes an earlier committed saga step."),
        ("What does event sourcing store?", "The sequence of events; current state is derived by replaying them."),
        ("Token bucket versus fixed window in one line?", "Bucket allows bursts up to capacity at a steady refill rate; fixed window counts per clock interval and can double-burst at a boundary."),
        ("What status code signals rate limiting?", "429 Too Many Requests."),
        ("Can anyone read a JWT payload?", "Yes, it is only base64url-encoded; the signature only prevents tampering."),
        ("How should passwords be stored?", "As salted, deliberately slow hashes such as bcrypt, scrypt, Argon2 or PBKDF2."),
    ],
    recall=[
        ["monolith first", "split only for a concrete reason"],
        ["201 + Location", "created, and where"],
        ["429", "rate limited"],
        ["pub/sub", "decouples publisher from subscribers"],
        ["CQRS", "separate write and read models"],
        ["saga", "local steps with compensations"],
        ["token bucket", "burst up to capacity, steady refill rate"],
        ["JWT", "signed claims: readable, tamper-evident"],
    ],
    sources=[
        dict(title="Microsoft Azure Architecture Center: cloud design patterns", url="https://learn.microsoft.com/en-us/azure/architecture/patterns/", use="Saga, CQRS, event sourcing, rate limiting and more, with diagrams", license="Copyright Microsoft; read online", how="Link only"),
        dict(title="Microsoft REST API guidelines", url="https://github.com/microsoft/api-guidelines", use="A thorough real-world API design guide", license="CC BY 4.0", how="Link only"),
        dict(title="OAuth 2.0 simplified (Aaron Parecki)", url="https://aaronparecki.com/oauth-2-simplified/", use="A clear explanation of the OAuth flows", license="Copyright the author; read online", how="Link only"),
        dict(title="JWT introduction (jwt.io)", url="https://jwt.io/introduction", use="What a JWT contains and how it is verified", license="Copyright Auth0; read online", how="Link only"),
        dict(title="OWASP Password Storage Cheat Sheet", url="https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html", use="Current guidance on hashing passwords", license="CC BY-SA 4.0", how="Link only"),
    ],
    plan=[
        "**Hour 1:** monolith versus microservices; compute the availability table for your own system.",
        "**Hour 2:** REST design; run the API and add a PUT or DELETE endpoint yourself.",
        "**Hour 3:** events and CQRS; add a new read view to the events script.",
        "**Hour 4:** sagas; then rate limiting and Lab 1.",
        "**Hour 5:** authentication and tokens; then Lab 2.",
        "**Hours 6 and 7:** interview answers out loud (end each with the price) and the self-test.",
    ],
)
