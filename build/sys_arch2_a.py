"""S24 architecture patterns: part A (rig, lessons 1 and 2: monolith versus services, strangler migration)."""
import sysviz as v

RIG = r'''mkdir -p ~/arch && cd ~/arch && cat > backend.py <<'EOF'
# A tiny backend: python3 backend.py NAME PORT   (answers every request with its NAME)
import sys, http.server, socketserver
name, port = sys.argv[1], int(sys.argv[2])
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = ('%s %s\n' % (name, self.path)).encode()
        self.send_response(200); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, *a): pass
socketserver.ThreadingTCPServer.allow_reuse_address = True
socketserver.ThreadingTCPServer(('127.0.0.1', port), H).serve_forever()
EOF
cat > rig.sh <<'EOF'
# Backends on 9201 (legacy monolith) and 9202 (new orders service); nginx on 8210; PostgreSQL on 5571 (socket in ~/arch).
export AR=$HOME/arch PG=$(ls -d /usr/lib/postgresql/*/bin | head -1); export PATH=$PG:$PATH
backends() { for spec in "legacy 9201" "new-orders 9202"; do set -- $spec; (cd $AR && setsid python3 backend.py $1 $2 </dev/null >/dev/null 2>&1 & disown) 2>/dev/null; done; sleep 0.8; }
stop_all() { pkill -f "python3 backend.py" >/dev/null 2>&1; [ -f $AR/ngx/nginx.pid ] && kill $(cat $AR/ngx/nginx.pid) 2>/dev/null; sleep 0.4; true; }
mkngx() {   # mkngx "<contents of the http block's servers and maps>"
  mkdir -p $AR/ngx && cat > $AR/ngx/n.conf <<CONF
worker_processes 1; daemon on; pid $AR/ngx/nginx.pid; error_log $AR/ngx/error.log;
events { worker_connections 256; }
http { access_log off; client_body_temp_path $AR/ngx/cb; proxy_temp_path $AR/ngx/px; fastcgi_temp_path $AR/ngx/fc; uwsgi_temp_path $AR/ngx/uw; scgi_temp_path $AR/ngx/sc;
$1
}
CONF
}
ngx() { nginx -c $AR/ngx/n.conf -p $AR/ngx/ 2>&1 | grep -v "^$"; sleep 0.5; }
pgup()  { [ -d $AR/pg ] || initdb -D $AR/pg -A trust -U learner >/dev/null
          pg_ctl -D $AR/pg -o "-p 5571 -k $AR -c listen_addresses='' -c fsync=off" -l $AR/pg.log -w start >/dev/null
          createdb -h $AR -p 5571 -U learner app 2>/dev/null || true; }
pgdown(){ pg_ctl -D $AR/pg -m fast stop >/dev/null 2>&1; }
pq()    { psql -X -q -h $AR -p 5571 -U learner -d app "$@"; }
EOF
. ./rig.sh; echo "rig ready in $AR: backend.py and rig.sh (backends, mkngx, ngx, stop_all, pgup, pgdown, pq)"'''

MONO_VIZ = v.figure(
    720, 244,
    [v.box(10, 24, 300, 150, "Modular monolith", "ok", ""),
     v.text(160, 56, "one deployable, clear modules inside", "dg-s"), v.text(160, 82, "calls are function calls: microseconds", "dg-s"), v.text(160, 108, "one database transaction", "dg-s"), v.text(160, 134, "one thing to run and debug", "dg-s"),
     v.box(410, 24, 300, 150, "Microservices", "acc", ""),
     v.text(560, 56, "many deployables, owned by teams", "dg-s"), v.text(560, 82, "calls are network calls: milliseconds, can fail", "dg-s"), v.text(560, 108, "data split: no shared transaction", "dg-s"), v.text(560, 134, "needs tracing, discovery, deployment tooling", "dg-s"),
     v.text(360, 204, "Split when team size, deployment independence or scaling differences justify the tax: not before.", "dg-s"),
     v.text(360, 228, "A \"distributed monolith\" has all the costs of services and none of the independence.", "dg-s")],
    "Monolith or services", "Services buy independence and cost operational complexity; many teams start with a modular monolith")

STRANGLER_VIZ = v.figure(
    720, 226,
    [v.box(10, 80, 100, 56, "Clients", "ink"),
     v.arrow(110, 108, 150, 108), v.box(150, 80, 130, 56, "Routing layer", "warn", "nginx / gateway"),
     v.arrow(280, 96, 340, 52), v.arrow(280, 120, 340, 164),
     v.box(340, 24, 190, 56, "New orders service", "ok", "takes more paths over time"),
     v.box(340, 140, 190, 56, "Legacy monolith", "ink", "shrinks as paths move"),
     v.box(570, 60, 140, 96, "Rollback", "acc", "change one route back; the legacy path is still there"),
     v.text(360, 218, "Move one capability at a time behind a router; the old system stays the fallback until the new one has proved itself.", "dg-s")],
    "The strangler fig migration", "Grow the new system around the old one, route by route, instead of a big-bang rewrite")

LESSONS_A = [
    dict(
        title="Monolith, modular monolith or microservices: the real trade-off",
        tier="hot",
        situation="Someone says \"let's move to microservices\" because that is what big companies do. Eighteen months later there are 30 services, a two-hour deployment ritual, and bugs that need five teams to debug. Or the monolith has become a ball of mud that 60 engineers cannot change safely. Both are real failure modes.",
        learn=["What a network hop costs in time and in reliability", "The availability arithmetic of chains of services", "Modular monolith as a serious option", "When splitting is justified"],
        model=[
            "A **monolith** is deployed as one unit; modules call each other as ordinary functions (microseconds, always succeed or throw), share one database, and can use one transaction. It is simple to build, test, run and debug, and it scales by running more copies. It becomes painful when **many teams** must coordinate every release, when one module needs to scale or deploy at a different rhythm, or when the code has no internal boundaries. **Microservices** split the system into independently deployable services that own their data and talk over the network: teams can ship independently, scale parts separately and choose technology, in exchange for the **distributed-systems tax**: every call is a network call (slower, can time out, needs retries and idempotency), there is no shared transaction (sagas, eventual consistency), and you must run service discovery, deployment, tracing, versioned contracts and on-call for many things.",
            "The **availability** cost is arithmetic: a request that needs five services in series, each 99.9 percent available, is only about **99.5 percent** available (0.999^5): hours of extra downtime a year, unless you add timeouts, fallbacks and redundancy. A **modular monolith** (one deployable, strict internal module boundaries, each module owning its tables) gives most of the design benefits and defers the operational tax; it can later be split along already-clean seams. Split a piece out when there is a concrete reason: independent scaling, a team that needs independent releases, a different reliability or security boundary, or a technology that does not fit. The anti-pattern is the **distributed monolith**: services that must be deployed together, share a database or call each other in long synchronous chains, with all the costs and none of the independence.",
        ],
        analogy="One big kitchen where cooks share every tool and pass dishes by hand (monolith) versus a food court of separate stalls, each with its own cook, till and supplier (microservices). The food court scales and lets stalls change menus independently, but customers now queue at several counters, payment is per stall and a missing ingredient at one stall must be sorted out between stalls.",
        visual=[MONO_VIZ],
        sim=None,
        walk=[
            ("Start with clear modules", "Even in one deployable, give each business area its own module and its own tables, with a small public interface."),
            ("Measure the pain, not the fashion", "Slow releases, merge conflicts between teams, one hot spot needing different scaling: concrete reasons."),
            ("Split along an existing seam", "Pick a module with few dependencies and clear data ownership."),
            ("Pay the tax up front", "Contracts, retries with idempotency, timeouts, tracing, deployment automation and on-call for the new service."),
            ("Re-check the arithmetic", "Count the services in the critical path and the resulting availability and latency."),
        ],
        groups=[
            dict(title="What a hop costs, and what a chain does to availability", cmds=[
                dict(volatile=True, c=r'''python3 - <<'EOF'
import json, threading, time, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
def price(item): return {'item': item, 'price': 100 + item % 50}             # the business logic: a plain function
class H(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    disable_nagle_algorithm = True
    def log_message(self, *a): pass
    def do_GET(self):
        body = json.dumps(price(int(self.path.split('/')[2]))).encode()
        self.send_response(200); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
srv = ThreadingHTTPServer(('127.0.0.1', 8221), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
N = 2000
t = time.perf_counter()
for i in range(N): price(i)
local_us = (time.perf_counter() - t) / N * 1e6
import http.client
conn = http.client.HTTPConnection('127.0.0.1', 8221)                          # a kept-alive connection: the best case for a network call
t = time.perf_counter()
for i in range(N): conn.request('GET', '/price/%d' % i); json.loads(conn.getresponse().read())
http_us = (time.perf_counter() - t) / N * 1e6
print('in-process function call:    %8.1f microseconds' % local_us)
print('HTTP call to localhost:      %8.1f microseconds   (%d times slower, on the SAME machine)' % (http_us, http_us / max(local_us, 0.01)))
print('across a data centre add roughly 500 microseconds to a few milliseconds; across regions tens to hundreds of milliseconds.')
srv.shutdown()
EOF''',
                     e="The tax of a service boundary, measured at its cheapest. The same piece of business logic is called as a function and over HTTP to localhost with a reused connection (no real network at all). The HTTP call is already **thousands of times slower**, and it adds failure modes (timeouts, refused connections, partial failure) that a function call does not have. Across a real network the gap widens. This is not an argument against services; it is the cost you must be getting something for.",
                     annot=[("in-process function call: 0.1 microseconds", "a function call inside a monolith costs almost nothing"),
                            ("HTTP call to localhost: ~290 microseconds (thousands of times slower)", "serialisation, a socket and a thread hop, with no real network yet (your numbers will differ)"),
                            ("across a data centre ... regions", "real distance adds more, and the call can now fail in new ways")]),
                dict(c=r'''python3 - <<'EOF'
# Availability of a request that needs several services in series, each with its own availability.
def chain(avails):
    a = 1.0
    for x in avails: a *= x
    return a
def downtime(a): return (1 - a) * 365 * 24 * 60
print('one service at 99.9%%:             %.3f%% available, %5.0f minutes of downtime a year' % (99.9, downtime(0.999)))
for n in (3, 5, 10, 20):
    a = chain([0.999] * n)
    print('%2d services in series at 99.9%%:  %.3f%% available, %5.0f minutes of downtime a year' % (n, a * 100, downtime(a)))
print()
print('with a fallback so that 2 of the 5 services are optional (the request still succeeds without them):')
a = chain([0.999] * 3); print('   3 required services:           %.3f%% available' % (a * 100))
print('with each required service run as 2 independent copies behind a balancer (each copy 99.9 percent):')
per = 1 - (1 - 0.999) ** 2; a = chain([per] * 5); print('   5 services, each redundant:    %.5f%% available' % (a * 100))
EOF''',
                     e="The arithmetic that should accompany every \"let's split it\" discussion. Availabilities of services in series **multiply**: five 99.9 percent services give 99.5 percent, about two and a half **days** of downtime a year instead of nine hours; twenty give 98 percent. Two ways back: make dependencies **optional** with fallbacks (so fewer are required for a request to succeed), and run **redundant copies** so each hop is far more reliable than a single instance. Without those, every service you add to a request's critical path makes the whole thing worse.",
                     annot=[("5 services in series at 99.9%: 99.501% available, ~2,600 minutes of downtime a year", "0.999^5: several times the downtime of one service"),
                            ("20 services in series: 98.019%", "about a week of downtime a year if nothing else is done"),
                            ("3 required services: 99.700%", "making two of them optional removes them from the product"),
                            ("5 services, each redundant: 99.99950%", "redundancy makes each link much stronger than 99.9%")]),
            ]),
        ],
        scenario=dict(
            title="\"We have a monolith with 60 engineers and slow releases. Should we move to microservices? How would you decide?\"",
            ask="A judgement question that tests whether you reason from problems, not trends, and know the costs.",
            clarify=[("What exactly hurts: release coordination, scaling, reliability, onboarding? Where are the team boundaries?", "Different pains have different cures; not all need services.")],
            think=[("Diagnose first.", "If releases are slow because of test time, flaky pipelines or lack of module boundaries, services will not fix it. Services fix independent deployment and independent scaling and team autonomy."),
                   ("Describe the options.", "Improve the monolith (fast CI, feature flags, trunk-based development); make it modular (module boundaries, owned tables, enforced dependency rules); then extract services where there is a clear reason."),
                   ("State the costs.", "Network calls (latency, failure), no shared transaction (sagas, idempotency), operations (deployment, discovery, tracing, on-call), contract versioning, data duplication, and the availability product of services in series."),
                   ("Choose where to cut.", "Along business capabilities with clean data ownership and low coupling; start with the piece that most needs independent scaling or deployment (or a different security boundary), not the most central one."),
                   ("Plan the migration.", "Strangler pattern behind a router; one service at a time; each extraction needs its own database, contract, monitoring and rollback."),
                   ("Define success.", "Deployment frequency per team, lead time, change failure rate, incident count: measure before and after.")],
            answer=["\"I would start by finding what actually hurts. Slow releases from long test pipelines or tangled code are not fixed by services; independent deployment, independent scaling and team autonomy are. So first I would improve the monolith: fast CI, feature flags, and a modular structure with enforced boundaries and each module owning its tables.",
                    "Then I would extract a service only where there is a concrete reason, along a business seam with clean data ownership, using a strangler approach behind a router, one service at a time, each with its own database, contract, monitoring and rollback. I would count the costs honestly: network latency and failures, no shared transactions so sagas and idempotency, operational overhead, and the availability of services in series. And I would measure deployment frequency, lead time and incidents before and after to see whether it paid off.\""],
            follow=[("What is a distributed monolith?", "Services that cannot be deployed independently, share a database or call each other in long synchronous chains: all the costs, none of the benefits."),
                    ("How small should a service be?", "Aligned to a business capability and a team (the team owns it end to end), not a number of lines; too fine-grained creates chatty calls and coordination."),
                    ("What is the minimum platform you need before microservices?", "Automated build and deploy, centralised logging, metrics and distributed tracing, service discovery or a gateway, and a standard way to handle retries, timeouts and contracts.")],
            slips=["Choosing microservices because large companies use them.", "Ignoring the operational and consistency costs.", "Extracting the most central, most coupled piece first."],
        ),
        quick=[
            ("What does a network call add compared with a function call?", "Latency, serialisation and new failure modes (timeouts, partial failure)."),
            ("What is the availability of 5 services in series, each 99.9%?", "About 99.5% (0.999^5)."),
            ("What is a modular monolith?", "One deployable with strict internal module boundaries, each module owning its data: most design benefits, little operational tax."),
        ],
        traps=[
            "Splitting by technical layer (a \"database service\") instead of business capability.",
            "Services sharing a database: coupled schemas and deployments.",
            "No distributed tracing before the third service: debugging becomes guesswork.",
        ],
    ),
    dict(
        title="The strangler fig: migrating without a big-bang rewrite",
        tier="hot",
        situation="The old system works, badly, and nobody dares touch it. A full rewrite will take two years and ship nothing until the end. The reliable way out is to grow the replacement around the old system, one route at a time, with a router that can send traffic either way.",
        learn=["Routing by path to old and new systems", "Gradual percentage rollout and instant rollback", "Falling back when the new service fails", "What to verify before moving the next route"],
        model=[
            "The **strangler fig pattern** (named after the vine that grows around a tree) replaces a legacy system incrementally: put a **routing layer** (reverse proxy, API gateway) in front of it, build the new implementation of **one capability**, and route that capability's traffic to the new service while everything else still goes to the legacy system. Repeat until the legacy system serves nothing and can be retired. At every step the system works, risk is small, and **rollback is changing one route back**.",
            "Make each step safe: **route by path or header** to the new service; **roll out by percentage** (send 1, then 10, then 50, then 100 percent) while comparing errors and latency; optionally **shadow** traffic (copy real requests to the new service and compare its answers without returning them) to find differences before any user is affected; keep the legacy path as an automatic **fallback** while confidence is built; and migrate the **data** deliberately (dual writes or change-data-capture into the new service's database, then switch the source of truth). Resist moving the next route until the previous one has proved itself on real traffic.",
        ],
        analogy="Renovating a shop while it stays open: build the new checkout counter beside the old one, direct a few customers to it, watch how it goes, then close the old counter. If the new one jams, point customers back at the old one in seconds.",
        visual=[STRANGLER_VIZ],
        sim=None,
        walk=[
            ("Put a router in front", "All traffic goes through it; initially everything is sent to the legacy system."),
            ("Build one capability anew", "A new orders service with its own data, behind the same URLs."),
            ("Route that path to it, a few percent first", "Watch errors and latency against the legacy system."),
            ("Keep the way back", "Rolling back is one routing change, and the legacy path still works."),
            ("Repeat, then retire the old", "Move the next capability; delete the legacy code only when nothing calls it."),
        ],
        groups=[
            dict(title="Real nginx routing between a legacy system and a new service", cmds=[
                dict(c=RIG,
                     e="Creates the rig: a tiny backend that answers with its own name (one instance plays the legacy monolith on port 9201, another the new orders service on 9202), helper functions that write an nginx configuration and start and stop everything as an ordinary user, and PostgreSQL helpers for the later lessons. Nothing outside `~/arch` is touched."),
                dict(volatile=True, c=r'''. ~/arch/rig.sh; backends
mkngx 'upstream legacy { server 127.0.0.1:9201; }
upstream orders_new { server 127.0.0.1:9202; }
server { listen 8210;
  location /orders { proxy_pass http://orders_new; }          # this one capability has been strangled out of the monolith
  location /       { proxy_pass http://legacy; }              # everything else is still served by the legacy system
}'
ngx
for p in /orders/42 /users/7 /catalog/shoes /orders/list; do echo "GET $p -> $(curl -s http://127.0.0.1:8210$p)"; done
stop_all''',
                     e="Path-based strangling with real nginx. Requests under `/orders` are answered by the **new** service; everything else, `/users`, `/catalog`, still reaches the legacy monolith. To clients nothing changed: same host, same URLs. The router is the only component that knows which system serves what, which is what makes migrating one route at a time possible.",
                     annot=[("GET /orders/42 -> new-orders /orders/42", "this route has been migrated to the new service"),
                            ("GET /users/7 -> legacy /users/7", "not yet migrated: the legacy system still serves it"),
                            ("GET /orders/list -> new-orders /orders/list", "the whole `/orders` subtree goes to the new service")]),
                dict(volatile=True, c=r'''. ~/arch/rig.sh; backends
conf() { clause="$1 orders_new;"; [ "$1" = 0% ] && clause=""; mkngx "upstream legacy { server 127.0.0.1:9201; }
upstream orders_new { server 127.0.0.1:9202; }
split_clients \"\$request_id\" \$orders_target { $clause * legacy; }
server { listen 8210;
  location /orders { proxy_pass http://\$orders_target; }
  location /       { proxy_pass http://legacy; }
}"; }
count() { for i in $(seq 1 200); do curl -s http://127.0.0.1:8210/orders/$i | cut -d' ' -f1; done | sort | uniq -c | tr -s ' ' | paste -sd' '; }
for pct in 0% 10% 50% 100%; do conf $pct; if [ -f $AR/ngx/nginx.pid ] && kill -0 $(cat $AR/ngx/nginx.pid) 2>/dev/null; then nginx -c $AR/ngx/n.conf -p $AR/ngx/ -s reload 2>/dev/null; sleep 0.5; else ngx; fi; echo "rollout $pct of /orders to the new service, 200 requests: $(count)"; done
echo "--- rollback: set the share back to 0% and reload (the legacy path never went away)"
conf 0%; nginx -c $AR/ngx/n.conf -p $AR/ngx/ -s reload 2>/dev/null; sleep 0.5; echo "after rollback: $(count)"
stop_all''',
                     e="A gradual rollout with `split_clients`, which hashes each request to a percentage bucket. At 0 percent every `/orders` request still goes to legacy; at 10 percent roughly one in ten reaches the new service (the sample is random, so the counts are close to, not exactly, 20 of 200); at 100 percent all do. Rolling back is one configuration line and a reload, with no deployment, which is the safety net that makes each step low-risk. In real use you compare error rates and latency between the two paths at every step before increasing the share.",
                     annot=[("rollout 0%: 200 legacy", "nothing has moved yet"),
                            ("rollout 10%: 184 legacy, 16 new-orders", "a small slice of live traffic exercises the new service (random sampling: close to 20, not exactly)"),
                            ("rollout 50%: 107 legacy, 93 new-orders", "about half and half: wide enough to compare behaviour under real load"),
                            ("rollout 100%: 200 new-orders", "the capability has moved; the legacy code for it can eventually be removed"),
                            ("after rollback: 200 legacy", "one line and a reload undid the whole migration step")]),
                dict(volatile=True, c=r'''. ~/arch/rig.sh; backends
mkngx 'upstream orders_pool { server 127.0.0.1:9202; server 127.0.0.1:9201 backup; }      # the legacy system is the backup
server { listen 8210; location /orders { proxy_pass http://orders_pool; proxy_next_upstream error timeout http_502 http_503; proxy_connect_timeout 1s; } }'
ngx
echo "new service healthy:  $(curl -s http://127.0.0.1:8210/orders/1)"
pkill -f "backend.py new-orders"; sleep 0.5
echo "new service killed:   $(curl -s http://127.0.0.1:8210/orders/1)   <- served by the legacy backup, the user noticed nothing"
stop_all''',
                     e="Falling back to the old system automatically. The legacy backend is declared as the `backup` server of the new service's pool, so nginx uses it only when the primary fails. When the new service is killed, the next request is served by the legacy system without an error. For read paths this is a powerful way to migrate with confidence; for writes you must be careful that the new and legacy systems do not both accept writes for the same data.",
                     annot=[("new service healthy: new-orders /orders/1", "the primary serves while healthy"),
                            ("new service killed: legacy /orders/1", "the backup took over automatically when the connection failed")]),
            ]),
        ],
        scenario=dict(
            title="\"We need to replace a ten-year-old billing system that every other system depends on. How do you migrate with no downtime?\"",
            ask="A migration question. They want an incremental plan with verification, data migration and rollback, not a big-bang cutover.",
            clarify=[("How many systems depend on it and through what interface? Is there a clear way to intercept the traffic?", "Without an interception point (API, queue, database) the first step is to create one.")],
            think=[("Reject the rewrite.", "A big-bang rewrite ships nothing for a long time, the target keeps moving, and cutover is a single high-risk night."),
                   ("Create an interception point.", "A routing layer or facade in front of the legacy API; if clients use the database directly, introduce an API first."),
                   ("Pick the first slice.", "A low-risk, well-bounded capability (for example invoice rendering or tax lookup) to prove the process."),
                   ("Verify before moving users.", "Shadow traffic: send copies of real requests to the new system and compare its answers with the legacy ones; reconcile differences; then roll out by percentage with automatic fallback."),
                   ("Migrate the data deliberately.", "Backfill the new store, keep it in sync with change data capture or dual writes, compare continuously, then switch the source of truth for that capability and keep the old one read-only for a while."),
                   ("Keep rollback cheap.", "Every step reversible by a routing change until the data authority has moved; plan the point of no return explicitly."),
                   ("Retire the old.", "Remove routes, then code, then data, only after traffic and dependencies are zero.")],
            answer=["\"I would avoid a big-bang rewrite and use the strangler pattern. First I need an interception point: a routing layer or facade in front of the legacy billing API, creating one if clients talk to its database directly. Then I would pick a small, well-bounded first capability and build it in the new system.",
                    "Before moving real users I would shadow production traffic to the new system and compare its answers with the legacy ones, then roll out by percentage with automatic fallback and a one-line rollback. The data moves deliberately: backfill, then keep both in sync with change data capture, compare continuously, and switch the source of truth for that capability only when the numbers agree, keeping the old data read-only for a while. I repeat per capability, decide the point of no return explicitly, and retire routes, code and data only when traffic is zero.\""],
            follow=[("What is shadow traffic?", "Copying real requests to the new system, discarding or comparing its responses, so differences are found without affecting users."),
                    ("How do you keep data in sync during migration?", "Change data capture from the legacy database into the new store (or dual writes through the facade), with continuous reconciliation, then switch which side is authoritative."),
                    ("What if the new system is slower?", "Roll back via the router, profile with real traffic and fix before continuing; the percentage rollout limits the damage while you learn.")],
            slips=["Proposing a big-bang rewrite.", "No way to roll back.", "Migrating data without continuous comparison."],
        ),
        quick=[
            ("What does the routing layer do in the strangler pattern?", "Sends each capability's traffic to the new or the legacy system, and makes rollback a routing change."),
            ("What is shadow traffic for?", "Comparing the new system's answers with the legacy ones on real requests without exposing users."),
            ("When can you remove the legacy code?", "When no traffic or dependency uses that capability any more."),
        ],
        traps=[
            "No router: you cannot move a route or roll one back.",
            "Both systems accepting writes for the same data without a clear authority.",
            "Starting with the most central, most coupled capability.",
        ],
    ),
]
