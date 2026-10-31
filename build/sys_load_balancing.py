"""Systems Mastery S16: load balancers, proxies and gateways (deep version, real nginx and HAProxy)."""
import sysviz as v

RIG = r'''mkdir -p ~/lb/t && cd ~/lb && cat > backend.py <<'EOF'
# A tiny backend: python3 backend.py NAME PORT [DELAY_SECONDS]
import sys, json, time, http.server, socketserver
name, port = sys.argv[1], int(sys.argv[2])
delay = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        time.sleep(delay)
        if self.path.startswith('/headers'):
            body = json.dumps({'backend': name, 'peer': self.client_address[0],
                               'x_forwarded_for': self.headers.get('X-Forwarded-For'),
                               'x_forwarded_proto': self.headers.get('X-Forwarded-Proto'),
                               'host': self.headers.get('Host')})
        elif self.path.startswith('/big'):
            body = ('served by %s ' % name) * 100
        else:
            body = 'served by %s' % name
        data = (body + '\n').encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers(); self.wfile.write(data)
    def log_message(self, *a): pass
class S(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True; allow_reuse_address = True
S(('127.0.0.1', port), H).serve_forever()
EOF
cat > common.conf <<'EOF'
access_log off;
client_body_temp_path __LB__/t/b; proxy_temp_path __LB__/t/p; fastcgi_temp_path __LB__/t/f; uwsgi_temp_path __LB__/t/u; scgi_temp_path __LB__/t/s;
EOF
sed -i "s#__LB__#$HOME/lb#g" common.conf
cat > rig.sh <<'EOF'
export LB=$HOME/lb
mkconf() { sed "s#__LB__#$LB#g" > "$LB/$1"; }
backends() { for spec in A:9001:0 B:9002:0 C:9003:${1:-0}; do IFS=: read n p d <<<"$spec"; (python3 $LB/backend.py $n $p $d >/dev/null 2>&1 &); done; sleep 1; }
ngx() { nginx -c $LB/$1 -p $LB/ 2>&1; sleep 1; }
stop_all() { [ -f $LB/nginx.pid ] && kill $(cat $LB/nginx.pid) 2>/dev/null; pkill -f "$LB/backend.py" 2>/dev/null; pkill -f "haproxy -f" 2>/dev/null; sleep 0.5; true; }
EOF
. ./rig.sh; echo "rig ready in $LB: backend.py, common.conf, rig.sh"'''

PATH_VIZ = v.figure(
    720, 214,
    [v.box(10, 80, 80, 50, "Clients", "ink"),
     v.arrow(90, 105, 115, 105), v.box(115, 80, 90, 50, "DNS", "acc", "name to address"),
     v.arrow(205, 105, 230, 105), v.box(230, 70, 120, 70, "Load balancer", "acc", "one address, many servers"),
     v.arrow(350, 95, 385, 50), v.arrow(350, 105, 385, 105), v.arrow(350, 115, 385, 160),
     v.box(385, 25, 100, 44, "Server A", "ok"), v.box(385, 83, 100, 44, "Server B", "ok"), v.box(385, 140, 100, 44, "Server C", "ok"),
     v.arrow(485, 105, 520, 105), v.box(520, 80, 110, 50, "Shared data", "warn", "database, cache"),
     v.text(360, 204, "The balancer is the only thing clients know about; servers can come and go behind it.", "dg-s")],
    "Where a load balancer sits", "One front door, many identical servers behind it")

HEALTH_SEQ = v.seq(
    ["Client", "Load balancer", "Server A", "Server B"],
    [("a->b", 1, 2, "health check: GET /health"),
     ("a->b", 2, 1, "200 OK", "reply"),
     ("a->b", 1, 3, "health check: GET /health"),
     ("a->b", 3, 1, "(no answer: the server died)", "bad"),
     ("note", 1, 3, "2 failed checks in a row: B is marked DOWN"),
     ("a->b", 0, 1, "request"),
     ("a->b", 1, 2, "forward to A only"),
     ("a->b", 2, 0, "response (client never noticed B)", "reply")],
    "Health checks keep clients away from dead servers", "The balancer notices failure within seconds and routes around it")

HA_VIZ = v.figure(
    720, 214,
    [v.box(10, 80, 90, 50, "Clients", "ink"),
     v.arrow(100, 105, 135, 105), v.box(135, 80, 130, 50, "Virtual IP", "warn", "the address clients use"),
     v.arrow(265, 95, 300, 55), v.arrow(265, 115, 300, 155),
     v.box(300, 28, 140, 52, "LB 1 (active)", "ok", "holds the virtual IP"), v.box(300, 130, 140, 52, "LB 2 (standby)", "acc", "watches LB 1"),
     v.arrow(440, 54, 475, 95), v.arrow(440, 156, 475, 115),
     v.box(475, 80, 120, 50, "App servers", "ok", "health checked"),
     v.text(360, 204, "If LB 1 stops answering, LB 2 takes over the virtual IP within seconds; clients keep the same address.", "dg-s")],
    "Making the balancer itself highly available", "Two balancers share one address, so the front door is not a single point of failure")

MODULE = dict(
    id="lb",
    deep=True,
    title="Load balancers, proxies and gateways",
    lead="Every service that runs on more than one server has a front door: something that accepts the clients' requests and decides which server handles each one. This module opens that door. You will run real nginx and HAProxy in front of real backends, watch the algorithms spread (and fail to spread) traffic, kill servers and see the balancer route around them, terminate TLS, route by path, rate limit, cache, and then learn how to answer the interview questions with reasoning, not slogans.",
    time="9 to 11 hours",
    why=[
        "One server handles 500 requests per second. Traffic is about to grow tenfold. You cannot buy a server ten times faster, but you can run ten servers, and then you immediately need something that gives clients **one address**, spreads requests sensibly, stops sending traffic to a server that has died, and lets you deploy without downtime. That something is the load balancer.",
        "It is also the place where many production problems hide: an uneven spread that overloads one server, a health check that sends traffic to a broken node, a deploy that drops requests, a client IP that has vanished behind a proxy. Engineers who understand the balancer from the inside diagnose these in minutes.",
        "In interviews a load balancer appears in almost every design. The weak answer says \"add a load balancer\". The strong answer says which algorithm and why, how failures are detected, where TLS ends, how the balancer itself stays up, and what it costs.",
    ],
    outcomes=[
        "Explain what a load balancer does and where it sits, and the difference between DNS, layer 4 and layer 7 balancing.",
        "Compare round robin, weighted, least connections and consistent hashing, and show the effect of each on real traffic.",
        "Configure nginx and HAProxy as reverse proxies and read their behaviour from real output.",
        "Explain health checks (passive and active), failure detection time, retries and zero-downtime deploys, and demonstrate them.",
        "Terminate TLS at the proxy, pass client identity through headers, and route by path.",
        "Use proxies for rate limiting, compression and caching, and explain what an API gateway adds.",
        "Make the balancer itself highly available and spread traffic across regions.",
        "Answer load-balancing interview questions with a clear approach and numbers.",
    ],
    before=[
        "The networking module (S07): you should know what TCP, TLS and HTTP do. Python 3 runs the small backends; `curl` sends requests.",
        "Install the real tools: `sudo apt install nginx haproxy curl python3` (the Docker lab image has them). You do **not** need root to run them: every demo runs as an ordinary user on high ports and stops itself.",
        "Every experiment starts from a small practice rig that you create once (the first command of the first lesson) and reuse. Counts and timings that depend on your machine are marked; the shapes will match.",
    ],
    env=["The rig lives in `~/lb`. Every later command begins with `. ~/lb/rig.sh` to load its helper functions, and ends by stopping what it started."],
    lessons=[
        dict(
            title="Why a front door: one address, many servers",
            tier="hot",
            situation="Your site now runs on three identical servers. Customers type one name. Something must receive every request and hand it to one of the three, and keep working when one of them is switched off.",
            learn=["What a load balancer is and what it must do", "Three places to balance: DNS, layer 4, layer 7", "Your first real balancer, running"],
            model=[
                "A **load balancer** is a program (or a device, or a cloud service) that accepts connections on one address and forwards each request to one of several backend servers. It exists for three reasons: **capacity** (spread work so no server is overloaded), **availability** (stop sending traffic to a server that is down) and **flexibility** (add, remove or replace servers without clients noticing). It only works if the servers are interchangeable: any of them can answer any request, which is why web servers are kept **stateless** and shared data lives in a database or cache behind them.",
                "You can balance at three levels. **DNS balancing** returns several addresses for one name; it is simple and global but slow to change (caches) and it cannot see server health. **Layer 4** balancing forwards TCP connections by address and port without reading the data: very fast, protocol-agnostic. **Layer 7** balancing reads the HTTP request itself, so it can route by path or header, terminate TLS, cache and rewrite, at the cost of more work per request. Real systems often stack them: DNS to pick a region, a layer 4 balancer to spread connections, layer 7 proxies to route requests.",
            ],
            analogy="A restaurant host: guests see one entrance and one person; the host seats them at whichever waiter is free, skips a waiter who has gone home, and lets the kitchen add tables without telling the guests.",
            visual=[PATH_VIZ],
            sim="lbalgo",
            walk=[
                ("The client asks DNS for the site's address", "The name resolves to the **balancer's** address (or a set of balancer addresses), never to an individual backend. Clients cannot tell how many servers exist."),
                ("The connection reaches the balancer", "It accepts the TCP connection. A layer 7 balancer also finishes the TLS handshake here (TLS termination) and reads the HTTP request."),
                ("The balancer picks a backend", "Using its algorithm (round robin, least connections, hash...) and its knowledge of which servers are healthy, it chooses one."),
                ("It forwards the request, usually on a connection it already has open", "Proxies keep pools of connections to their backends, so the client's request does not pay a new TCP handshake to the server."),
                ("The response travels back through the balancer", "The client sees one answer from one address. The balancer may compress it, cache it, or log it on the way."),
                ("Failure and change happen behind the scenes", "A server crashes, a new one starts, a deploy replaces everything: the balancer's list of backends changes, the clients' experience does not."),
            ],
            groups=[
                dict(title="Build the practice rig and a first balancer", cmds=[
                    dict(c=RIG,
                         e="This creates the rig used by the whole module: a tiny backend program (`backend.py`) that answers with its own name, a shared nginx settings file, and helper functions in `rig.sh`. Nothing is installed or changed outside `~/lb`."),
                    dict(c=r'''. ~/lb/rig.sh; backends; for p in 9001 9002 9003; do printf "port $p -> "; curl -s http://127.0.0.1:$p/; done; stop_all''',
                         e="Three separate servers, each on its own port, each saying who it is. Without a balancer a client would have to know all three addresses and choose one itself.",
                         annot=[("port 9001 -> served by A", "backend A, on its own port"),
                                ("port 9002 -> served by B", "backend B"),
                                ("port 9003 -> served by C", "backend C: three interchangeable servers, three different addresses")]),
                    dict(volatile=True, c=r'''. ~/lb/rig.sh; mkconf rr.conf <<'EOF'
worker_processes 1; pid __LB__/nginx.pid; error_log __LB__/error.log;
events { worker_connections 256; }
http {
  include __LB__/common.conf;
  upstream app { server 127.0.0.1:9001; server 127.0.0.1:9002; server 127.0.0.1:9003; }
  server { listen 127.0.0.1:8180; location / { proxy_pass http://app; } }
}
EOF
nginx -t -c $LB/rr.conf -p $LB/ 2>&1 | sed 's#/home/[a-z]*#~#'; backends; ngx rr.conf; echo "--- nine requests, in order:"; for i in $(seq 1 9); do curl -s http://127.0.0.1:8180/; done | tr '\n' ' '; echo; echo "--- counts:"; for i in $(seq 1 9); do curl -s http://127.0.0.1:8180/; done | sort | uniq -c; stop_all''',
                         e="A real nginx reverse proxy in front of the three backends. `upstream app { ... }` lists the servers and `proxy_pass http://app` sends every request to that group. `nginx -t` checks the configuration before it is used (always do this). The clients talk to one address, port 8180, and the requests rotate over the three servers in order: **round robin**, nginx's default.",
                         annot=[("syntax is ok / test is successful", "`nginx -t` parsed the configuration: always run it before starting or reloading"),
                                ("served by A served by B served by C ...", "round robin: A, B, C, A, B, C... each request goes to the next server in the list"),
                                ("3 served by A", "over nine requests each server got exactly three: perfectly even, as long as every request costs about the same")]),
                ]),
            ],
            scenario=dict(
                title="\"You have three web servers behind one address. Describe how requests get distributed and what happens when one dies.\"",
                ask="A basic but revealing question. They want to hear the components, the decision, the failure behaviour and the cost, not just \"add a load balancer\".",
                clarify=[("Is the application stateless?", "If sessions live in each server's memory, any server cannot answer any request, and the balancer must keep a user on the same server (sticky sessions) or the state must move to a shared store."),
                         ("HTTP traffic, or something else (a database, a game server)?", "HTTP suggests a layer 7 proxy; arbitrary TCP suggests layer 4."),
                         ("Do we need to survive a whole data centre failing?", "That adds DNS or global balancing across regions on top of the local balancer.")],
                think=[("Say what the balancer is and why we want it.", "One address for clients, capacity by spreading load, availability by routing around failures, flexibility by changing servers behind it."),
                       ("Choose the layer.", "For a web application a layer 7 reverse proxy (nginx, HAProxy, a cloud application load balancer) gives TLS termination, path routing and header handling. For raw TCP or maximum throughput, layer 4."),
                       ("Choose the algorithm and justify it.", "Round robin when requests cost about the same; least connections when they vary; hashing when a user or key should stick to a server (cache locality). Start simple."),
                       ("Describe failure detection.", "Health checks: active ones probe each server every second or so and mark it down after a few failures; passive ones notice failed requests. The balancer stops sending to a down server and retries idempotent requests on another."),
                       ("Remove the single point of failure.", "The balancer is now critical, so run at least two behind a shared address (virtual IP) or use a managed service that is redundant for you."),
                       ("Close with deployment and operations.", "Remove a server from rotation (drain) before updating it, so in-flight requests finish; add capacity by adding servers; watch per-server error rates and latency.")],
                answer=["\"Clients connect to one address that belongs to a load balancer. I would use a layer 7 reverse proxy because this is HTTP: it terminates TLS, can route by path, and forwards each request to one of the three servers using round robin to start, or least connections if request times vary a lot. The servers must be stateless, with sessions and data in shared storage, so any server can serve any request.",
                        "The balancer health-checks the servers, for example every second, and marks one down after two or three failures; from then on traffic only goes to the healthy ones, and idempotent requests that fail on a dying server are retried on another. That means one server dying costs a few seconds of reduced capacity and, at worst, a handful of failed requests, not an outage.",
                        "The balancer itself must not be a single point of failure, so I would run two sharing a virtual IP or use a managed load balancer, and for deploys I would drain a server before updating it. I would monitor per-backend error rate and latency to spot an uneven or unhealthy server early.\""],
                follow=[("What if the three servers have different capacities?", "Use weighted balancing (give the big server a larger weight) or least connections, which adapts on its own."),
                        ("Why not just use DNS with three addresses?", "DNS cannot see health, clients and resolvers cache the answer for the TTL (so a dead server keeps receiving traffic), and the spread is crude. DNS is good for picking a region, not for fine-grained balancing."),
                        ("Does the load balancer add latency?", "Yes, a little: an extra hop and some processing, typically well under a millisecond inside a data centre. It usually saves time overall through connection reuse and by avoiding overloaded servers.")],
                slips=["Saying \"a load balancer\" without a layer, an algorithm or a failure story.", "Forgetting that the balancer is itself a single point of failure.", "Ignoring statelessness: sticky sessions hide a design problem."],
            ),
            quick=[
                ("Name the three reasons to put a load balancer in front of servers.", "Capacity (spread load), availability (route around failures) and flexibility (change servers without clients noticing)."),
                ("What is the difference between layer 4 and layer 7 balancing?", "Layer 4 forwards TCP connections by address and port without reading the data; layer 7 reads the HTTP request and can route by path or header, terminate TLS and cache."),
                ("Why must backends be interchangeable?", "So any server can answer any request; this is why state is kept in shared stores rather than in a server's memory."),
            ],
            traps=[
                "Putting a balancer in front of servers that keep user state in memory: requests for the same user then hit servers that do not know them.",
                "Forgetting that the balancer itself needs redundancy.",
                "Running `nginx -s reload` or starting with a config you have not checked with `nginx -t`.",
            ],
        ),
        dict(
            title="Algorithms: how the next server is chosen",
            tier="hot",
            situation="Round robin sounds fair. But what if one server is slow, or bigger than the others, or if the same user must reach the same server? The algorithm decides whether the load is truly balanced.",
            learn=["Round robin and weighted round robin", "Least connections and why slow servers need it", "Hashing for stickiness, and consistent hashing", "What you measure to know it works"],
            model=[
                "**Round robin** rotates through the servers: simple and fair when requests cost about the same and the servers are equal. **Weighted** round robin gives bigger servers a larger share. **Least connections** sends each request to the server with the fewest requests in progress: it adapts automatically when some requests are slow or some servers are slower, because slow servers accumulate open requests and so receive fewer new ones. **Hashing** (by client IP, a header or a cookie) maps the same key to the same server, which keeps caches warm and sessions together. Plain `hash mod N` reshuffles almost every key when N changes; **consistent hashing** places servers on a ring so that only about 1/N of the keys move when a server is added or removed.",
                "The test of an algorithm is not how it looks but what it does under **uneven load**. With equal, quick requests all of these look the same. Add one slow backend or a mix of heavy and light requests, and round robin keeps feeding the slow server its share while least connections steers around it.",
            ],
            analogy="Supermarket queues: round robin is sending each new customer to the next till in turn; least connections is joining the shortest queue; hashing is always going to the till your surname points at, so the same person always meets the same cashier.",
            sim=None,
            walk=[
                ("Round robin", "Keep a pointer into the list; each request advances it by one. No state, no measurement. Even only if requests are alike."),
                ("Weighted", "Servers with weight 3 receive three requests for every one that a weight 1 server receives. Use it when capacities differ, or to send a small share to a new version."),
                ("Least connections", "Track how many requests each server is working on right now and pick the smallest. Needs a counter per server; adapts to slowness without any configuration."),
                ("Hash by key", "Compute a hash of (client IP | user ID | URL) and map it to a server. The same key always lands on the same server while the server set is unchanged."),
                ("Consistent hashing", "Place each server at many points on a circle. A key goes to the next server clockwise. Adding or removing a server only affects the keys on the arc next to it."),
            ],
            groups=[
                dict(title="See each algorithm on real traffic", cmds=[
                    dict(volatile=True, c=r'''. ~/lb/rig.sh; mkconf w.conf <<'EOF'
worker_processes 1; pid __LB__/nginx.pid; error_log __LB__/error.log;
events { worker_connections 256; }
http {
  include __LB__/common.conf;
  upstream app { server 127.0.0.1:9001 weight=3; server 127.0.0.1:9002; server 127.0.0.1:9003; }
  server { listen 127.0.0.1:8180; location / { proxy_pass http://app; } }
}
EOF
backends; ngx w.conf; for i in $(seq 1 10); do curl -s http://127.0.0.1:8180/; done | sort | uniq -c; stop_all''',
                         e="**Weighted** round robin: server A has `weight=3`, B and C the default 1. Over ten requests A answers six and B and C two each (3:1:1). In real life you would give a server with twice the CPU twice the weight, or give a canary version a small weight.",
                         annot=[("6 served by A", "weight 3 out of a total weight of 5 = 60% of the requests"),
                                ("2 served by B / 2 served by C", "weight 1 out of 5 = 20% each")]),
                    dict(volatile=True, c=r'''. ~/lb/rig.sh; for algo in "" "least_conn;"; do
mkconf alg.conf <<EOF
worker_processes 1; pid __LB__/nginx.pid; error_log __LB__/error.log;
events { worker_connections 1024; }
http {
  include __LB__/common.conf;
  upstream app { $algo server 127.0.0.1:9001; server 127.0.0.1:9002; server 127.0.0.1:9003; }
  server { listen 127.0.0.1:8180; location / { proxy_pass http://app; } }
}
EOF
backends 0.5; ngx alg.conf; echo "=== ${algo:-round robin (default)} : 60 requests, 12 at a time, backend C is slow (0.5 s)"; seq 1 60 | xargs -P 12 -I{} curl -s http://127.0.0.1:8180/ | sort | uniq -c; stop_all; done''',
                         e="The experiment that shows why the algorithm matters. Backend C is deliberately slow (0.5 s per request); the others answer instantly. Sixty requests arrive, twelve at a time. **Round robin** blindly gives C a third of them. **Least connections** notices that C always has requests stuck in progress and sends it far fewer, so the fast servers do most of the work and the whole batch finishes sooner.",
                         annot=[("round robin: 20 / 20 / 20", "an even split by count, even though C is slow: every third request has to wait half a second"),
                                ("least_conn: 27 / 30 / 3", "backend C received only 3 of 60 requests: slow servers keep connections open longer, so the counter for C stays high and new requests go to A and B instead"),
                                ("(exact numbers vary run to run)", "the shape is the lesson: rr is even by count, least_conn is even by **load**")]),
                    dict(volatile=True, c=r'''. ~/lb/rig.sh; users="ann bob cho dev eli fay gus hal ivy jon kim lee"
mkconf h3.conf <<'EOF'
worker_processes 1; pid __LB__/nginx.pid; error_log __LB__/error.log;
events { worker_connections 256; }
http {
  include __LB__/common.conf;
  upstream app { hash $http_x_user consistent; server 127.0.0.1:9001; server 127.0.0.1:9002; server 127.0.0.1:9003; }
  server { listen 127.0.0.1:8180; location / { proxy_pass http://app; } }
}
EOF
mkconf h2.conf <<'EOF'
worker_processes 1; pid __LB__/nginx.pid; error_log __LB__/error.log;
events { worker_connections 256; }
http {
  include __LB__/common.conf;
  upstream app { hash $http_x_user consistent; server 127.0.0.1:9001; server 127.0.0.1:9003; }
  server { listen 127.0.0.1:8180; location / { proxy_pass http://app; } }
}
EOF
backends; map() { for u in $users; do printf "$u %s\n" "$(curl -s -H "X-User: $u" http://127.0.0.1:8180/ | awk '{print $3}')"; done; }
ngx h3.conf; map > before.txt; map > again.txt; kill $(cat $LB/nginx.pid); sleep 1
ngx h2.conf; map > after.txt; stop_all
echo "same user, same server on a second pass: $(diff before.txt again.txt >/dev/null && echo yes || echo NO)"
paste before.txt after.txt | awk '{print $1, $2, "->", $4, ($2==$4 ? "" : "  MOVED")}' | column -t
echo "users on B before: $(grep -c ' B' before.txt); users that moved: $(paste before.txt after.txt | awk '$2!=$4' | wc -l)"''',
                         e="**Consistent hashing** with real nginx: `hash $http_x_user consistent` maps the `X-User` header to a server. Twelve users are mapped with three servers, mapped again to prove the choice is stable, then server B is removed and they are mapped again. Only the users that lived on B move (to A or C); everyone else keeps the server they had, so caches on A and C stay valid. With plain `hash mod N` most users would have moved.",
                         annot=[("same user, same server on a second pass: yes", "hashing gives stickiness without any shared state or cookie"),
                                ("ann  A  ->  A", "a user whose server survived keeps it (no MOVED marker)"),
                                ("cho  B  ->  A  MOVED", "a user that was on the removed server B is reassigned to a remaining one (A or C)"),
                                ("users on B before: 5; users that moved: 5", "the number that moved equals the number that were on B: nobody else was disturbed")]),
                ]),
            ],
            scenario=dict(
                title="\"Round robin, least connections or consistent hashing: how do you choose?\"",
                ask="They give you three scenarios: stateless API with uniform requests, an image-resizing service with very uneven request times, and a cache cluster keyed by user. Which algorithm for each, and why?",
                clarify=[("How much do request costs vary?", "That is the whole question for round robin versus least connections."),
                         ("Do we need the same key to reach the same server?", "Caches and session affinity are the reasons to hash."),
                         ("How often do servers join and leave?", "Frequent changes make consistent hashing worth its complexity.")],
                think=[("Start with the simplest that fits.", "Uniform, stateless requests: round robin (or weighted if servers differ). Simple and predictable."),
                       ("Look for variance.", "The image resizer has requests from 20 ms to 5 s: round robin will pile heavy ones onto unlucky servers; least connections spreads by actual load. Mention you would verify with per-server latency percentiles."),
                       ("Look for locality.", "A cache cluster keyed by user wants the same user on the same node so hits are possible: hash by user ID."),
                       ("Show you know the catch of hashing.", "With plain modulo, changing N moves almost every key and empties the caches; consistent hashing with virtual nodes limits movement to about 1/N and spreads load evenly."),
                       ("Mention hot keys.", "Hashing can overload one server if one key (a celebrity user) is hot: cache that key at the edge, split it, or fall back to load-aware balancing."),
                       ("Say how you would know it works.", "Per-server request rate, connections and latency; the spread should be even in load, not just in count.")],
                answer=["\"For the stateless API with uniform requests I would use round robin, weighted if the servers differ in size: it is simple and the load is even. For the image resizer, where request times vary enormously, round robin would give some servers a run of heavy jobs, so I would use least connections, which adapts to how busy each server really is. For the cache cluster keyed by user, I want the same user to hit the same node, so I would hash on the user ID.",
                        "The catch with simple hashing is that when a node is added or removed, hash mod N remaps almost every key and the caches go cold, so I would use consistent hashing with virtual nodes, which moves only about one over N of the keys and keeps the load even. A hot key can still overload one node, so I would watch per-node load and cache or replicate very hot keys.",
                        "In all cases I would confirm with per-server request counts, connections and latency percentiles, because even by count is not the same as even by load.\""],
                follow=[("What are virtual nodes?", "Each physical server appears at many positions on the ring (for example 100). This evens out the share each server gets and, when a server leaves, spreads its keys across all the others instead of dumping them on one neighbour."),
                        ("How would you drain a server using these algorithms?", "Set its weight to zero or mark it down so no new requests arrive, wait for in-flight requests to finish, then stop it."),
                        ("What is power of two choices?", "Pick two servers at random and send the request to the one with fewer connections. It gets most of the benefit of least connections with far less coordination, which matters in large distributed balancers.")],
                slips=["Choosing hashing for \"fairness\": it gives stickiness, not even load.", "Describing round robin as perfectly balanced without mentioning uneven request cost."],
            ),
            quick=[
                ("Why does least connections cope with a slow backend and round robin does not?", "A slow backend keeps its requests open longer, so its connection count stays high and it receives fewer new requests; round robin keeps giving it an equal share."),
                ("What does consistent hashing improve over `hash mod N`?", "When a server is added or removed only about 1/N of the keys move, instead of nearly all of them."),
                ("What would you use to send 5 percent of traffic to a new version?", "Weighted balancing: give the new server a small weight."),
            ],
            traps=[
                "Equal by count is not equal by load: measure CPU, concurrency and latency per server.",
                "Hashing by client IP behind a proxy or NAT: thousands of users share one address and land on one server.",
                "Sticky sessions hide state stored in a server; a server restart then logs users out.",
            ],
        ),
        dict(
            title="Health checks, failures and zero-downtime deploys",
            tier="hot",
            situation="A server crashes at 03:00. Does the balancer keep sending it a third of the traffic, or notice and route around it? And when you deploy, can you replace servers without a single failed request?",
            learn=["Passive and active health checks", "How fast failure is detected, and what clients see meanwhile", "Retries and their danger", "Draining and zero-downtime reloads"],
            model=[
                "Balancers detect failure in two ways. **Passive** checks watch real traffic: if a request to a server fails or times out, count it, and after a few failures stop using that server for a while (nginx `max_fails` and `fail_timeout`). **Active** checks send their own probe (a request to `/health`) every second or so and mark a server **DOWN** after several failures in a row and **UP** again after several successes (HAProxy `check inter 1s fall 2 rise 3`). Detection is never instant: between the failure and the detection some requests go to the dead server. Good balancers **retry** such requests on another server, which is safe only for **idempotent** requests (GET, not a payment POST).",
                "A health check must test what matters: a probe that only checks that the port is open will keep a server in rotation when its application is deadlocked or its database is unreachable. And a check that is too sensitive makes servers flap in and out. For deploys, **drain** the server first: stop sending it new requests, let in-flight ones finish, then update it. A proxy reload should switch configuration without dropping connections.",
            ],
            analogy="A host who sees a waiter drop their tray stops seating guests in that section (passive); a host who walks the floor every minute asking \"all fine?\" (active) finds problems before guests do. Before a waiter goes on break, the host stops seating them and lets them finish current tables (draining).",
            visual=[HEALTH_SEQ],
            walk=[
                ("Probe: the balancer checks each server on a timer", "Every `inter` milliseconds it sends a small request to each backend and records success or failure."),
                ("Fail: consecutive failures cross the threshold", "After `fall` failures in a row the server is marked DOWN. The delay is about `fall x inter`, so a 1 s interval and fall 3 means up to ~3 seconds of exposure."),
                ("Route around: traffic only goes to UP servers", "Requests in flight to the dead server fail or time out; the balancer may retry idempotent ones elsewhere."),
                ("Recover: successes bring it back", "After `rise` successful probes the server rejoins. The rise threshold stops a flapping server from re-entering too eagerly."),
                ("Deploy: drain, update, return", "Mark the server out of rotation, wait for connections to finish, update it, wait for it to pass health checks, then restore it, one server at a time."),
            ],
            groups=[
                dict(title="Kill a server and watch the balancer cope", cmds=[
                    dict(volatile=True, c=r'''. ~/lb/rig.sh; mkconf pass.conf <<'EOF'
worker_processes 1; pid __LB__/nginx.pid; error_log __LB__/error.log;
events { worker_connections 256; }
http {
  include __LB__/common.conf;
  upstream app { server 127.0.0.1:9001 max_fails=1 fail_timeout=10s; server 127.0.0.1:9002 max_fails=1 fail_timeout=10s; server 127.0.0.1:9003 max_fails=1 fail_timeout=10s; }
  server { listen 127.0.0.1:8180; location / { proxy_pass http://app; proxy_next_upstream error timeout; } }
}
EOF
backends; ngx pass.conf; echo "--- all healthy:"; for i in $(seq 1 9); do curl -s http://127.0.0.1:8180/; done | sort | uniq -c
pkill -f "$LB/backend.py B 9002"; sleep 0.5
echo "--- server B killed. HTTP status of 9 requests:"; for i in $(seq 1 9); do curl -s -o /dev/null -w '%{http_code} ' http://127.0.0.1:8180/; done; echo
echo "--- who served them:"; for i in $(seq 1 9); do curl -s http://127.0.0.1:8180/; done | sort | uniq -c
echo "--- what nginx logged:"; grep -m1 -o 'connect() failed.*upstream' error.log | sed 's/, client.*//' ; stop_all''',
                         e="**Passive** failure handling in real nginx. With all three healthy the load is even. Then server B is killed. nginx finds out the hard way, when a request to B fails (`connection refused`); with `max_fails=1` it stops using B for `fail_timeout` (10 s) and, thanks to `proxy_next_upstream error timeout`, **retries that very request on another server**, so clients still see 200. After that B is skipped entirely and A and C share the traffic.",
                         annot=[("--- server B killed. ... 200 200 200 ...", "every request still returned 200: the failed attempt to B was retried invisibly on another server"),
                                ("5 served by A / 4 served by C (no B)", "after the first failure B is out of rotation; A and C split the load"),
                                ("connect() failed (111: Connection refused) while connecting to upstream", "the evidence in the error log: nginx tried B, was refused, marked it failed and moved on")]),
                    dict(volatile=True, c=r'''. ~/lb/rig.sh; mkconf ha.cfg <<'EOF'
global
  maxconn 256
defaults
  mode http
  timeout connect 1s
  timeout client 5s
  timeout server 5s
frontend web
  bind 127.0.0.1:8280
  default_backend app
backend app
  balance roundrobin
  option httpchk GET /
  server A 127.0.0.1:9001 check inter 300ms fall 2 rise 2
  server B 127.0.0.1:9002 check inter 300ms fall 2 rise 2
  server C 127.0.0.1:9003 check inter 300ms fall 2 rise 2
listen stats
  bind 127.0.0.1:8404
  stats enable
  stats uri /stats
EOF
status() { curl -s 'http://127.0.0.1:8404/stats;csv' | awk -F, '$1=="app" && $2 ~ /^[ABC]$/ {printf "%s=%s ", $2, $18} END{print ""}'; }
backends; haproxy -f $LB/ha.cfg -D -p $LB/ha.pid 2>/dev/null; sleep 1.5
echo "healthy:        $(status)"
pkill -f "$LB/backend.py B 9002"; sleep 1.2
echo "B stopped:      $(status)"
echo "requests now:   $(for i in $(seq 1 6); do curl -s http://127.0.0.1:8280/; done | sort | uniq -c | tr '\n' ';')"
(python3 $LB/backend.py B 9002 >/dev/null 2>&1 &); sleep 1.5
echo "B restarted:    $(status)"
kill $(cat $LB/ha.pid) 2>/dev/null; stop_all''',
                         e="**Active** health checks with real HAProxy. HAProxy probes every server every 300 ms (`check inter 300ms`), marks one DOWN after 2 failures (`fall 2`) and UP after 2 successes (`rise 2`), and publishes the state on its stats page, read here as CSV. Within about a second of B being stopped it is DOWN and requests flow only to A and C. When B returns it passes two probes and rejoins automatically. The status column is the 18th field of the stats CSV.",
                         annot=[("healthy: A=UP B=UP C=UP", "all servers pass their checks"),
                                ("B stopped: ... B=DOWN ...", "about `fall x inter` (here 0.6 s) after the failure the balancer marks B DOWN: that is the detection delay"),
                                ("requests now: A and C only", "while B is DOWN no request is sent to it, so clients see no errors"),
                                ("B restarted: ... B=UP ...", "after `rise` successful probes B is added back automatically")]),
                    dict(volatile=True, c=r'''. ~/lb/rig.sh; mkconf r1.conf <<'EOF'
worker_processes 1; pid __LB__/nginx.pid; error_log __LB__/error.log;
events { worker_connections 256; }
http {
  include __LB__/common.conf;
  upstream app { server 127.0.0.1:9001; server 127.0.0.1:9002; server 127.0.0.1:9003; }
  server { listen 127.0.0.1:8180; location / { proxy_pass http://app; } }
}
EOF
sed 's/server 127.0.0.1:9002;/server 127.0.0.1:9002 down;/' $LB/r1.conf > $LB/r2.conf
backends; ngx r1.conf
( for i in $(seq 1 120); do curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8180/; sleep 0.02; done > codes.txt ) &
sleep 1; cp $LB/r2.conf $LB/r1.conf; nginx -t -c $LB/r1.conf -p $LB/ 2>&1 | tail -1 | sed 's#/home/[a-z]*#~#'; kill -HUP $(cat $LB/nginx.pid); wait
echo "requests sent during the reload: $(wc -l < codes.txt), failed: $(grep -vc '^200$' codes.txt)"
echo "after reload, who answers: $(for i in $(seq 1 6); do curl -s http://127.0.0.1:8180/; done | sort | uniq -c | tr '\n' ';')"; stop_all''',
                         e="**A zero-downtime change.** While 120 requests are flowing, the configuration is changed to take server B out of rotation (`down`) and nginx is told to reload (`kill -HUP`). New worker processes start with the new configuration; the old workers finish their in-flight requests and exit. Result: no request failed, and from then on only A and C answer. This is how you drain a server before updating it.",
                         annot=[("test is successful", "always validate the new configuration before reloading"),
                                ("requests sent during the reload: 120, failed: 0", "the reload dropped nothing: old workers finished their requests while new ones took over"),
                                ("after reload, who answers: A and C", "B is out of rotation: safe to stop and update it")]),
                ]),
            ],
            scenario=dict(
                title="\"How do you deploy a new version of a service behind a load balancer with zero downtime?\"",
                ask="Walk through a rolling deployment, including what could go wrong at each step.",
                clarify=[("How many servers, and is there headroom to take one out?", "Rolling deploys reduce capacity by one server at a time; with three servers that is a third, which must be affordable."),
                         ("Do requests last long (uploads, websockets)?", "Long-lived connections need a longer drain time or a way to move clients."),
                         ("Is the new version backward compatible with the database and with the old version running alongside?", "During a rolling deploy both versions serve traffic at once.")],
                think=[("State the principle.", "Never stop a server that is still receiving traffic: take it out of rotation first, let it finish, change it, verify it, put it back."),
                       ("Step through it.", "1) Mark server 1 as draining: no new requests. 2) Wait until its active connections reach zero or a timeout (for example 30 s). 3) Stop it, deploy the new version, start it. 4) Wait for the health check to pass (and ideally a warm-up request). 5) Return it to rotation. 6) Watch error rate and latency for that server compared with the old ones. 7) Repeat for the next server."),
                       ("Name what can go wrong.", "Capacity dip if too many are out at once; a new version that passes the health check but misbehaves (so use a canary: one server or 1-5 percent of traffic first, with automatic rollback on error rate); incompatible database changes (use expand and contract migrations); cache warm-up making the first requests slow."),
                       ("Mention alternatives.", "Blue-green: a full second environment, switch the balancer to it, instant rollback by switching back. Canary releases through weighted balancing."),
                       ("Mention the proxy's own configuration changes.", "Reload rather than restart (graceful), and validate with `nginx -t` first.")],
                answer=["\"I would do a rolling deployment, one server at a time. First I take server one out of rotation so it gets no new requests, then wait for its in-flight requests to finish, up to a timeout. Then I deploy and start the new version, wait until the health check passes, and put it back. I watch that server's error rate and latency against the others before moving on to the next. The principle is never to stop a server that is still receiving traffic.",
                        "What can go wrong is a dip in capacity if I take out too many at once, a new version that passes the health check but is actually broken, and database changes that are not compatible with the old version, which is still running alongside during the rollout. So I make migrations backward compatible, start with a canary on a small share of traffic with automatic rollback if the error rate rises, and keep headroom.",
                        "Blue-green deployment is an alternative: stand up a complete new environment and switch the balancer over, which gives instant rollback at the cost of double capacity for a while.\""],
                follow=[("What is connection draining?", "Telling the balancer to stop assigning new requests to a server while letting existing connections complete, usually with a timeout after which remaining connections are closed."),
                        ("How do you roll back?", "Rolling: redeploy the previous version the same way, so keep the old artifact. Blue-green: point the balancer back at the old environment. Both depend on the database changes being compatible with both versions."),
                        ("A health check passes but users see errors. Why?", "The check is too shallow (it tests that the port answers, not that the application can reach its dependencies), or the problem only shows under real traffic. Use deeper checks and judge canaries by real error rates.")],
                slips=["Restarting servers in place with no draining.", "Deploying to all servers at once.", "Not mentioning database compatibility during the overlap."],
            ),
            quick=[
                ("What is the difference between a passive and an active health check?", "Passive checks count failures of real requests; active checks send their own probes on a timer."),
                ("What is connection draining for?", "To stop sending new requests to a server but let in-flight ones finish, so a deploy does not drop requests."),
                ("Why are retries safe only for idempotent requests?", "A retried request may already have been processed by the failed server; repeating a GET is harmless, repeating a payment is not."),
            ],
            traps=[
                "A health check that only tests the port: the application can be dead while the port still answers.",
                "Marking servers down on a single failed probe: they flap in and out under load. Require several failures (`fall`) and several successes (`rise`).",
                "Retrying non-idempotent requests automatically: double charges and duplicated orders.",
            ],
        ),
        dict(
            title="Layer 4 versus layer 7, and terminating TLS",
            tier="hot",
            situation="Some traffic is HTTP and could be routed by path; some is raw TCP (databases, game servers); and all of it may need TLS. Where should the balancer look at the traffic, and where should encryption end?",
            learn=["What a layer 4 balancer can and cannot do", "What a layer 7 proxy adds", "TLS termination and passing the client's identity"],
            model=[
                "A **layer 4** balancer sees only addresses, ports and bytes: it picks a backend when the TCP connection opens and then shuffles bytes in both directions without understanding them. It is fast, works for any protocol, and cannot route by URL or read headers. A **layer 7** proxy terminates the client's connection, reads the HTTP request, and opens (or reuses) its own connection to the backend. That lets it route by **path or host**, add or rewrite **headers**, **terminate TLS**, compress, cache, rate limit and authenticate, for more CPU per request.",
                "**TLS termination** means the proxy does the TLS handshake and decryption, then talks plain HTTP (or re-encrypts) to the backends: certificates live in one place and backends stay simple. Because backends then see the proxy as the client, the proxy adds **`X-Forwarded-For`** (the real client address) and **`X-Forwarded-Proto`** (whether the original connection was HTTPS) so applications can still know who called and how. Only trust those headers when they come from your own proxy, since clients can forge them.",
            ],
            analogy="Layer 4 is a mail room that forwards sealed envelopes by the address on the outside; layer 7 is a receptionist who opens the letter, reads it and sends it to the right department, and may add a note saying who it came from.",
            sim=None,
            walk=[
                ("A client opens a TCP connection to the proxy", "For layer 4 the balancer picks a backend now and joins the two connections: the backend does the TLS and HTTP itself and sees the balancer's address as the peer."),
                ("Layer 7: TLS is finished at the proxy", "The proxy presents the certificate, decrypts, and reads the plain HTTP request."),
                ("The proxy decides by what it reads", "Path (`/api` to one pool, `/` to another), host name, headers, cookies. This is content-based routing."),
                ("It adds identity headers and forwards", "`X-Forwarded-For: <client ip>` and `X-Forwarded-Proto: https`, so the backend can still log the real client and build correct links."),
                ("The response returns the same way", "The proxy re-encrypts it for the client."),
            ],
            groups=[
                dict(title="Route by path, terminate TLS, and compare with layer 4", cmds=[
                    dict(volatile=True, c=r'''. ~/lb/rig.sh; mkconf l7.conf <<'EOF'
worker_processes 1; pid __LB__/nginx.pid; error_log __LB__/error.log;
events { worker_connections 256; }
http {
  include __LB__/common.conf;
  upstream api { server 127.0.0.1:9001; server 127.0.0.1:9002; }
  upstream web { server 127.0.0.1:9003; }
  server {
    listen 127.0.0.1:8180;
    location /api/ { proxy_pass http://api; }
    location /     { proxy_pass http://web; }
  }
}
EOF
backends; ngx l7.conf
echo "GET /api/orders x4 -> $(for i in 1 2 3 4; do curl -s http://127.0.0.1:8180/api/orders; done | sort | uniq -c | tr '\n' ';')"
echo "GET /index.html x4 -> $(for i in 1 2 3 4; do curl -s http://127.0.0.1:8180/index.html; done | sort | uniq -c | tr '\n' ';')"; stop_all''',
                         e="**Layer 7 routing** with real nginx. The proxy reads the request path: anything under `/api/` goes to the pool of servers A and B, everything else to server C. A layer 4 balancer could never do this, because it never reads the path. This is how one public address can front many different services (an API gateway does the same, with more features).",
                         annot=[("GET /api/orders x4 -> 2 served by A; 2 served by B", "the `/api/` location forwards to the `api` pool, which round-robins A and B"),
                                ("GET /index.html x4 -> 4 served by C", "any other path goes to the `web` pool (only C)")]),
                    dict(volatile=True, c=r'''. ~/lb/rig.sh; openssl req -x509 -newkey rsa:2048 -nodes -keyout lb.key -out lb.crt -days 1 -subj '/CN=localhost' 2>/dev/null
mkconf tls.conf <<'EOF'
worker_processes 1; pid __LB__/nginx.pid; error_log __LB__/error.log;
events { worker_connections 256; }
http {
  include __LB__/common.conf;
  upstream app { server 127.0.0.1:9001; }
  server {
    listen 127.0.0.1:8443 ssl;
    ssl_certificate __LB__/lb.crt; ssl_certificate_key __LB__/lb.key;
    location / {
      proxy_pass http://app;
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-For $remote_addr;
      proxy_set_header X-Forwarded-Proto $scheme;
    }
  }
}
EOF
backends; ngx tls.conf
echo "client -> proxy (HTTPS):  $(curl -sk -o /dev/null -w 'TLS %{ssl_verify_result}, HTTP %{http_code}, version %{http_version}' https://127.0.0.1:8443/)"
echo "what the backend sees:"; curl -sk https://127.0.0.1:8443/headers
echo "connecting to the backend directly (no proxy): $(curl -s http://127.0.0.1:9001/headers)"; stop_all''',
                         e="**TLS termination** with real nginx. The client speaks HTTPS to the proxy (the certificate here is self-signed, so verification is skipped with `-k`). The proxy decrypts, and talks plain HTTP to backend A. Look at what A received: the peer address is the proxy (`127.0.0.1`), but the headers the proxy added say the original request was `https` and give the client address. Without those headers, the application could not tell that the user came over HTTPS or who they were.",
                         annot=[("TLS 18, HTTP 200, version 1.1", "the client's connection to the proxy is encrypted (18 = our self-signed certificate was not trusted, which `-k` ignored); the HTTP request worked"),
                                ("\"peer\": \"127.0.0.1\"", "the backend's TCP peer is the proxy, not the user"),
                                ("\"x_forwarded_proto\": \"https\"", "added by the proxy: the user's connection was HTTPS even though the backend saw plain HTTP"),
                                ("\"x_forwarded_for\": \"127.0.0.1\"", "added by the proxy: the real client address (on this machine the client is also local)"),
                                ("directly: x_forwarded_proto null", "without the proxy those headers do not exist: they are the proxy's testimony, which is why a backend must only trust them from its own proxy")]),
                    dict(volatile=True, c=r'''. ~/lb/rig.sh; mkconf l4.cfg <<'EOF'
global
  maxconn 256
defaults
  timeout connect 1s
  timeout client 5s
  timeout server 5s
frontend tcpfront
  mode tcp
  bind 127.0.0.1:8380
  default_backend tcpapp
backend tcpapp
  mode tcp
  balance roundrobin
  server A 127.0.0.1:9001
  server B 127.0.0.1:9002
EOF
backends; haproxy -f $LB/l4.cfg -D -p $LB/ha.pid 2>/dev/null; sleep 1
echo "through a LAYER 4 balancer, 4 requests: $(for i in 1 2 3 4; do curl -s http://127.0.0.1:8380/; done | sort | uniq -c | tr '\n' ';')"
echo "what the backend sees: $(curl -s http://127.0.0.1:8380/headers)"; kill $(cat $LB/ha.pid); stop_all''',
                         e="The same idea at **layer 4**: HAProxy in `mode tcp` just joins connections, spreading them over A and B without ever reading the HTTP inside. It works, and it is fast, but notice what is missing in the backend's view: no `x_forwarded_for`, no `x_forwarded_proto`. The balancer cannot add a header to data it does not parse. (Layer 4 balancers usually pass the client address through other means, such as the PROXY protocol, or by keeping the original source address.)",
                         annot=[("through a LAYER 4 balancer ... A and B", "connections are spread over the backends exactly like before"),
                                ("\"x_forwarded_for\": null", "a layer 4 balancer does not understand HTTP, so it cannot add HTTP headers"),
                                ("\"peer\": \"127.0.0.1\"", "the backend only sees the balancer as the peer unless the PROXY protocol or similar is used")]),
                ]),
            ],
            scenario=dict(
                title="\"What is the difference between a layer 4 and a layer 7 load balancer, and which would you choose?\"",
                ask="A standard question. A good answer is a decision, not two definitions.",
                clarify=[("What protocol is the traffic?", "HTTP and gRPC suit layer 7. Databases, MQTT, game traffic or anything non-HTTP suits layer 4."),
                         ("Do we need routing by path or host, header manipulation, or TLS termination?", "Any of these requires layer 7."),
                         ("What is the throughput and latency requirement?", "At extreme throughput layer 4 is cheaper per connection.")],
                think=[("Define each by what it sees.", "Layer 4: addresses, ports and bytes; picks a backend per connection. Layer 7: parses HTTP; picks a backend per request."),
                       ("Compare capabilities.", "Layer 7 gives content routing, TLS termination, header rewriting, caching, compression, rate limiting and per-request retries and metrics. Layer 4 gives speed, simplicity, protocol independence, and passes TLS through untouched (end-to-end encryption)."),
                       ("Compare cost.", "Layer 7 costs more CPU and adds a little latency because it terminates and re-creates connections. Layer 4 is lighter."),
                       ("Choose by requirement.", "A web application with path routing and TLS termination: layer 7. A TCP service or very high connection rate: layer 4. Large systems use both: a layer 4 fleet at the edge spreading connections across layer 7 proxies."),
                       ("Mention the identity problem.", "With layer 7 you get the client address in `X-Forwarded-For`; with layer 4 you need the PROXY protocol or direct server return.")],
                answer=["\"A layer 4 balancer works on TCP connections: it sees addresses and ports, picks a backend when the connection opens and forwards bytes without understanding them. It is fast, protocol-independent, and can pass TLS straight through. A layer 7 balancer is an HTTP proxy: it terminates the connection, reads each request, and can route by path, host or header, terminate TLS, rewrite headers, compress, cache and rate limit, at the price of more CPU and a bit more latency.",
                        "For a typical web application I would choose layer 7, because I want path-based routing and TLS termination in one place. For a non-HTTP protocol or a very high connection rate I would choose layer 4. At large scale you often see both: layer 4 spreading connections over a fleet of layer 7 proxies. With layer 7 the backend gets the real client IP from X-Forwarded-For, which it should trust only from the proxy; with layer 4 I would use something like the PROXY protocol.\""],
                follow=[("Where should TLS terminate?", "Usually at the layer 7 proxy or CDN edge so certificates are managed in one place and backends stay simple. Re-encrypt to the backends (or use mutual TLS) when the internal network is not trusted or compliance requires encryption everywhere."),
                        ("What is direct server return?", "A layer 4 technique where backends reply straight to the client instead of through the balancer, so the balancer only handles the small request direction. It needs special network setup."),
                        ("How would you load balance gRPC?", "gRPC uses long-lived HTTP/2 connections with many requests multiplexed on them, so a layer 4 balancer would pin all requests of a client to one backend. Use a layer 7 balancer that understands HTTP/2 (per-request balancing) or client-side balancing.")],
                slips=["Defining the layers by number only, with no examples.", "Forgetting that TLS termination needs the proxy to hold the private key.", "Trusting X-Forwarded-For from the open internet."],
            ),
            quick=[
                ("What can a layer 7 balancer do that a layer 4 balancer cannot?", "Route by path or host, read and rewrite headers, terminate TLS, cache and rate limit, because it understands HTTP."),
                ("Why does the backend need X-Forwarded-For?", "The TCP peer it sees is the proxy, so the proxy reports the real client address in that header."),
                ("Why is a layer 4 balancer a poor fit for gRPC?", "gRPC multiplexes many requests on one long-lived connection, so per-connection balancing sends them all to one backend."),
            ],
            traps=[
                "Trusting `X-Forwarded-For` or `X-Forwarded-Proto` from anywhere except your own proxy.",
                "Terminating TLS at the proxy and then forgetting that traffic behind it is unencrypted on the internal network.",
                "Balancing long-lived HTTP/2 or WebSocket connections with a per-connection algorithm and ending up with a few overloaded backends.",
            ],
        ),
        dict(
            title="What a proxy does besides balancing: rate limits, compression, caching, gateways",
            tier="hot",
            situation="Because every request already passes through the proxy, it is the natural place to do work you do not want in every application: stop abusive clients, shrink responses, answer repeated requests from memory, check credentials.",
            learn=["Rate limiting at the edge", "Compression and caching in a reverse proxy", "What an API gateway adds"],
            model=[
                "A reverse proxy sees all traffic, so cross-cutting features belong there. **Rate limiting** rejects clients that exceed a rate (HTTP **429 Too Many Requests**), protecting backends from overload and abuse; nginx implements a leaky-bucket with `limit_req` (a steady rate plus an allowed **burst**). **Compression** (gzip, brotli) shrinks text responses several times, saving bandwidth and time. **Caching** (`proxy_cache`) stores backend responses and answers repeats from memory or disk, so a popular page is generated once and served thousands of times; the proxy reports `HIT` or `MISS`. An **API gateway** is a layer 7 proxy specialised for APIs: it adds authentication, per-client quotas, request validation, routing to many services, request IDs, and metrics at one choke point.",
            ],
            analogy="The front desk of an office does more than point people to rooms: it checks IDs, turns away someone who keeps coming back every few seconds, hands out copies of the brochure from a stack instead of asking the printing department each time.",
            sim=None,
            walk=[
                ("Identify the client", "By IP, API key, user ID or token. The key you choose decides who shares a quota."),
                ("Apply policy before the backend", "Check the rate limit, authenticate, validate. Rejected requests cost the backend nothing."),
                ("Try the cache", "If the response is cached and fresh, answer immediately; otherwise forward and store the result for next time."),
                ("Shape the response", "Compress it, add security headers, strip internal ones."),
                ("Record it", "Log the request ID, status and timing: the proxy is the best place for uniform access logs and metrics."),
            ],
            groups=[
                dict(title="Rate limit, compress and cache with real nginx", cmds=[
                    dict(volatile=True, c=r'''. ~/lb/rig.sh; mkconf rl.conf <<'EOF'
worker_processes 1; pid __LB__/nginx.pid; error_log __LB__/error.log;
events { worker_connections 256; }
http {
  include __LB__/common.conf;
  limit_req_zone $binary_remote_addr zone=perip:1m rate=5r/s;
  upstream app { server 127.0.0.1:9001; }
  server {
    listen 127.0.0.1:8180;
    location / { limit_req zone=perip burst=5 nodelay; limit_req_status 429; proxy_pass http://app; }
  }
}
EOF
backends; ngx rl.conf
echo "20 requests as fast as possible:"; for i in $(seq 1 20); do curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8180/; done | sort | uniq -c
sleep 2; echo "after waiting 2 seconds, one more request: $(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8180/)"; stop_all''',
                         e="**Rate limiting** with real nginx: each client IP may make 5 requests per second (`rate=5r/s`), with a burst allowance of 5 extra. Twenty requests in a blink: the first six get through (the allowed rate plus the burst), the rest are rejected immediately with **429**. After a pause the bucket has refilled and requests succeed again. This protects backends without any code in them.",
                         annot=[("6 200", "the burst allowance (5) plus the first request: allowed instantly"),
                                ("14 429", "the rest exceeded the rate and were rejected before reaching the backend"),
                                ("after waiting ... 200", "tokens refill over time: the limit is a rate, not a ban")]),
                    dict(volatile=True, c=r'''. ~/lb/rig.sh; mkconf cache.conf <<'EOF'
worker_processes 1; pid __LB__/nginx.pid; error_log __LB__/error.log;
events { worker_connections 256; }
http {
  include __LB__/common.conf;
  proxy_cache_path __LB__/cache levels=1:2 keys_zone=pages:1m max_size=10m inactive=1m;
  gzip on; gzip_types text/plain; gzip_min_length 200;
  upstream app { server 127.0.0.1:9001; }
  server {
    listen 127.0.0.1:8180;
    location / {
      proxy_cache pages; proxy_cache_valid 200 10s;
      add_header X-Cache-Status $upstream_cache_status;
      proxy_pass http://app;
    }
  }
}
EOF
backends; ngx cache.conf
for i in 1 2 3; do printf "request $i: "; curl -s -D - -o /dev/null http://127.0.0.1:8180/ | grep -i x-cache-status | tr -d '\r'; done
echo "uncompressed size: $(curl -s http://127.0.0.1:8180/big | wc -c) bytes; with gzip: $(curl -s -H 'Accept-Encoding: gzip' http://127.0.0.1:8180/big | wc -c) bytes"
echo "header: $(curl -s -D - -o /dev/null -H 'Accept-Encoding: gzip' http://127.0.0.1:8180/big | grep -i content-encoding | tr -d '\r')"; stop_all''',
                         e="**Caching and compression** in a reverse proxy. The first request is a `MISS` (the proxy had to ask the backend), the next two are `HIT`s served from the proxy's cache without touching the backend at all (valid for 10 seconds). Separately, a 1,201-byte text response is shrunk to 47 bytes when the client advertises `Accept-Encoding: gzip`: smaller transfers, faster pages.",
                         annot=[("request 1: X-Cache-Status: MISS", "not in the cache: the proxy forwarded it to the backend and stored the answer"),
                                ("request 2, 3: X-Cache-Status: HIT", "answered from the proxy: the backend did no work"),
                                ("uncompressed size: 1201 bytes; with gzip: 47 bytes", "this text is extremely repetitive so it shrinks 25 times; typical HTML and JSON shrink by 3 to 10 times"),
                                ("Content-Encoding: gzip", "the proxy told the client how the body is encoded, and the client decompresses it")]),
                ]),
            ],
            scenario=dict(
                title="\"What does an API gateway do, and how is it different from a load balancer?\"",
                ask="Many candidates blur the two. Draw the line, then say when you would add a gateway.",
                clarify=[("How many services sit behind it, and who are the clients (browsers, mobile apps, partners)?", "Many services and external clients are the main reasons to add a gateway.")],
                think=[("Start from the load balancer.", "It spreads traffic across identical instances of one service and keeps unhealthy ones out of rotation."),
                       ("Describe the gateway as a smarter, API-aware front door.", "It is a layer 7 proxy in front of many different services: routing by path or host to the right service, authentication and authorisation, rate limits and quotas per client, request and response transformation, API keys, logging and metrics, sometimes caching."),
                       ("Show where they overlap and combine.", "A gateway usually load balances to the instances of each service (or sits in front of per-service load balancers). In practice products (nginx, Envoy, Kong, cloud API gateways) do both."),
                       ("Name the costs.", "An extra hop and a critical shared component: it must be highly available and must not become a bottleneck or a place where business logic accumulates."),
                       ("Give the decision rule.", "One service, many identical instances: a load balancer is enough. Many services behind one public API, with shared concerns (auth, limits): add a gateway.")],
                answer=["\"A load balancer spreads requests across identical instances of one service and removes unhealthy ones. An API gateway is a layer 7 front door for many services: it routes by path or host to the right service, handles authentication, rate limits and quotas per client, can transform requests, and gives you one place for logging and metrics. In practice the gateway also load balances across instances of each service, so the two features live in the same proxy.",
                        "I would add a gateway when there are many services behind one public API and common concerns I do not want to implement in each of them. The costs are an extra hop and a critical component that has to be highly available, and the discipline to keep business logic out of it.\""],
                follow=[("What is a BFF (backend for frontend)?", "A gateway-like service tailored to one client type (mobile, web) that aggregates calls to several backends and shapes the responses for that client."),
                        ("Where do you put authentication?", "At the gateway for coarse checks (is the token valid, which client is this), with services still enforcing fine-grained authorisation for their own data."),
                        ("How do you rate limit across several gateway instances?", "Share the counters in a fast store (for example Redis) or give each instance a share of the quota and accept some inaccuracy.")],
                slips=["Saying a gateway and a load balancer are the same thing.", "Putting business logic in the gateway."],
            ),
            quick=[
                ("What HTTP status does a rate limiter return, and what header helps the client?", "429 Too Many Requests, with a Retry-After header."),
                ("What does X-Cache-Status: HIT tell you?", "The proxy answered from its cache and the backend did no work."),
                ("What does an API gateway add beyond load balancing?", "Per-API routing, authentication, per-client rate limits, transformation, and a single place for logging and metrics."),
            ],
            traps=[
                "Rate limiting by IP behind shared NAT: thousands of users share one address and are blocked together; limit by API key or user as well.",
                "Caching personalised responses in a shared cache: one user sees another's data. Cache only what is the same for everyone, or vary the cache key.",
                "Letting the gateway grow into a place for business logic: it becomes a bottleneck that everyone must change.",
            ],
        ),
        dict(
            title="Making the balancer itself reliable, and spreading across regions",
            tier="hot",
            situation="You made the servers redundant, but every request still goes through one balancer. If it dies, everything is down. And what about a whole data centre failing, or users on another continent?",
            learn=["Redundant balancers and a shared address", "DNS and global load balancing", "Where the single points of failure hide"],
            model=[
                "A single balancer is a **single point of failure**, so balancers come in groups. Two common ways: an **active-passive pair** that share a **virtual IP**: the active one holds the address and the standby watches it (with a protocol such as VRRP, implemented by keepalived); if the active one stops answering, the standby takes the address within seconds and clients keep using the same IP. Or **many active balancers** behind **DNS round robin** (several A records) or **anycast** routing, where the same IP is announced from several places and the network delivers each client to the nearest one. Cloud load balancers hide all of this: they are redundant across zones for you.",
                "To survive the loss of a region and to serve users nearby, add **global load balancing**: DNS that answers with the address of the closest or healthiest region (GeoDNS, latency-based routing, health-checked failover), or anycast. DNS-based failover is bounded by the **TTL** (clients and resolvers keep the old answer) and by clients that ignore it, so critical failover keeps the TTL short and combines DNS with application-level retries.",
            ],
            analogy="A building with two front doors and a receptionist who is always replaced by a colleague if they step out: visitors keep using the same street address.",
            visual=[HA_VIZ],
            walk=[
                ("Give clients a stable address", "A virtual IP (or a DNS name resolving to several balancers) that does not belong to one machine."),
                ("Elect or assign who serves it", "In an active-passive pair the master holds the virtual IP and announces it; the backup listens for those announcements."),
                ("Detect failure", "If the backup stops hearing the master (a few missed announcements, typically 1 to 3 seconds), it assumes the address."),
                ("Keep configuration and state in sync", "Both balancers need the same backend list and settings; connection state may or may not be shared, so existing connections can break at failover."),
                ("Add regions on top", "Global balancing sends users to a healthy region; each region has its own redundant balancers and servers."),
            ],
            groups=[
                dict(title="DNS balancing, as it exists on the real internet", cmds=[
                    dict(volatile=True, c=r'''for i in 1 2 3; do printf "query $i: "; dig +short example.com A | sort | tr '\n' ' '; echo; done; echo "TTL of the answer: $(dig +noall +answer example.com A | awk 'NR==1{print $2}') seconds"''',
                         e="A real site returning **several addresses** for one name: clients pick one, so traffic is spread across the machines behind them (and the set may be reordered or rotated between queries). This is DNS round robin. It is simple and works across data centres, but note the weakness: DNS knows nothing about server health and clients cache the answer for the TTL, so a dead address keeps receiving some traffic until caches expire or the client tries the next address.",
                         annot=[("query 1: 104.20.23.154 172.66.147.243", "two addresses for one name: the client may use either"),
                                ("query 2, query 3: same set, possibly reordered", "resolvers rotate the order, which spreads new clients across the addresses"),
                                ("TTL of the answer: N seconds", "how long resolvers may reuse this answer: this bounds how quickly DNS can move traffic away from a failed address")]),
                    dict(c=r'''cat <<'EOF'
vrrp_instance VI_1 {
    state MASTER            # the standby uses: state BACKUP
    interface eth0
    virtual_router_id 51
    priority 150            # the standby uses a lower number, e.g. 100
    advert_int 1            # announce every second
    virtual_ipaddress { 203.0.113.10 }
}
EOF''', run=False, o="vrrp_instance VI_1 {\n    state MASTER            # the standby uses: state BACKUP\n    interface eth0\n    virtual_router_id 51\n    priority 150            # the standby uses a lower number, e.g. 100\n    advert_int 1            # announce every second\n    virtual_ipaddress { 203.0.113.10 }\n}",
                         e="What an active-passive pair looks like in keepalived, the common tool for a virtual IP on Linux. The master announces every second; if the standby hears nothing for about three announcements it takes over `203.0.113.10`. Shown as a configuration to read, not run: it needs two machines on one network and root privileges.",
                         annot=[("state MASTER / BACKUP", "who starts as the owner of the address"),
                                ("priority 150", "the higher priority wins the election; the standby has a lower one"),
                                ("advert_int 1", "announcement interval: with a missed-announcement limit this sets the failover time"),
                                ("virtual_ipaddress", "the address clients use: it moves between machines")]),
                ]),
            ],
            scenario=dict(
                title="\"How would you design the load balancing for a global service that must survive a data-centre failure?\"",
                ask="A bigger question that tests whether you can layer the pieces: DNS, regional balancers, health checks and failover behaviour.",
                clarify=[("Where are the users, and what latency matters?", "Users on several continents mean serving from nearby regions."),
                         ("Is the data replicated across regions, and is it strongly consistent?", "Failover is only possible if the data a region needs is there; consistency choices follow the distributed systems module."),
                         ("What recovery time do we need?", "Seconds need active-active and short TTLs; minutes can allow DNS failover.")],
                think=[("Layer the problem.", "Global (which region?), regional (which balancer?), local (which server?). Each level has its own mechanism and failure handling."),
                       ("Global level.", "GeoDNS or latency-based DNS returns the address of the nearest healthy region, with health checks removing a failed region and a short TTL (such as 30 to 60 s). Anycast is an alternative that avoids DNS caching."),
                       ("Regional level.", "In each region a pair or fleet of balancers across availability zones (or a managed cloud balancer), each health-checking its servers."),
                       ("Failure behaviour.", "Region fails: health checks stop answering for it, DNS drops it, clients move to the next region within about a TTL; clients and gateways retry on connection errors to cover the gap."),
                       ("Name the hard parts.", "Capacity: the surviving regions must absorb the extra load (plan N+1 across regions). Data: replication lag and conflicts. Testing: run game days to prove the failover works."),
                       ("Mention costs.", "Active-active is expensive and complex; many services use active-passive for the data layer and active-active only for stateless tiers.")],
                answer=["\"I would layer it. At the global level, a health-checked DNS service with latency-based routing returns the address of the nearest healthy region and uses a short TTL, so when a region fails it is dropped within a minute or so; anycast is an alternative. Inside each region, redundant load balancers across availability zones, or a managed one, distribute to servers that they health-check, and the balancers have no single point of failure because they share a virtual IP or sit behind several addresses.",
                        "When a region fails, its health checks fail, DNS stops returning it, and clients move to another region; clients and gateways retry on connection errors to cover the TTL window. The hard parts are capacity, because the remaining regions must be able to carry the extra traffic, and data, because the user's data must be available there, which brings in replication lag and consistency. I would rehearse the failover regularly, since an untested failover tends to fail.\""],
                follow=[("DNS TTLs are often ignored. How do you cope?", "Combine DNS with client-side retries across several addresses, keep an anycast or global load balancer layer in front for critical traffic, and design clients to try the next address on failure."),
                        ("What is the difference between anycast and GeoDNS?", "GeoDNS answers DNS queries with different addresses by location; anycast announces the same address from many places and the network routes each client to the nearest one, with no DNS TTL involved."),
                        ("How many balancers are enough?", "At least two in different failure domains, sized so that losing one still leaves enough capacity.")],
                slips=["Saying \"multi-region\" without the data story.", "Relying on DNS TTLs for instant failover.", "Forgetting capacity on the surviving regions."],
            ),
            quick=[
                ("How does an active-passive pair of balancers keep one address?", "They share a virtual IP: the master announces and holds it, and the standby takes it over when the announcements stop."),
                ("Why is DNS failover slower than local health-check failover?", "Resolvers and clients cache answers for the TTL, and some ignore it."),
                ("Name two places where a single point of failure can hide in a balanced design.", "The balancer itself, and shared dependencies such as the database or DNS provider."),
            ],
            traps=[
                "A pair of balancers on the same rack, switch or power feed: they fail together. Spread them across failure domains.",
                "Configuration drift between balancers: the standby takes over with an out-of-date backend list.",
                "A failover plan never rehearsed: practise it.",
            ],
        ),
    ],
    labs=[
        dict(kind="linux", script="nginx-balance", dir="nginxlab", title="Fix a broken balancer",
             goal=["Find and repair the mistakes in an nginx load balancer configuration until requests spread evenly over three servers."],
             story=["A colleague wrote an nginx configuration to balance three backends, but it does not work: nginx will not start. When it does start it sends everything to one server. Fix it using the real tools: `nginx -t` and `curl`."],
             tasks=["Read `~/sys-lab/nginxlab/balancer.conf` and run `nginx -t -c ~/sys-lab/nginxlab/balancer.conf -p ~/sys-lab/nginxlab/` to see the first error.", "Fix every problem (there are three) until the test passes.", "Start nginx with that file and check that nine requests to `http://127.0.0.1:8190/` give three answers from each backend.", "Run the check script."],
             check="Run the check script.", check_cmd="bash ~/sys-lab/check-nginx-balance.sh",
             hints=["`nginx -t` reports the line number of the first error: fix one, test again.", "An `upstream` block lists one `server` line per backend; the backends listen on 127.0.0.1 ports 9101, 9102 and 9103.", "`proxy_pass` must name the upstream group exactly (`http://app`), and the `listen` port must be 8190."],
             solution=["Run `nginx -t ...`: the first error is a missing semicolon after a `server` line: add it.", "Add the missing third `server 127.0.0.1:9103;` line to the upstream block, and correct the `proxy_pass` name to the upstream (`http://app`).", "Start with `nginx -c ~/sys-lab/nginxlab/balancer.conf -p ~/sys-lab/nginxlab/` and run `for i in $(seq 1 9); do curl -s http://127.0.0.1:8190/; done | sort | uniq -c`."],
             cleanup=["kill $(cat ~/sys-lab/nginxlab/nginx.pid) 2>/dev/null; pkill -f 'nginxlab/backend.py'; true"]),
        dict(kind="linux", script="lb-stats-read", dir="stats", title="Read the balancer's statistics",
             goal=["Read saved HAProxy statistics and diagnose which server is unhealthy, which is overloaded and why."],
             story=["The on-call engineer pastes the balancer's statistics from a bad afternoon. Before anyone touches production you must read them: which server is DOWN, which got most of the traffic and whether the weights explain it."],
             tasks=["Read `stats.csv` (columns are explained in `README.txt`).", "Find the server that is DOWN and the one with the most total sessions.", "Compute the share of traffic that went to the busiest server, its weight, and the total connection errors.", "Write the `key=value` lines into `~/sys-lab/answers-stats.txt`."],
             check="Run the check script.", check_cmd="bash ~/sys-lab/check-lb-stats-read.sh",
             hints=["`status` is the column that says UP or DOWN.", "`stot` is the total number of sessions handled.", "Share = busiest server's stot divided by the sum of the three servers' stot."],
             solution=["The DOWN server is `web3`.", "The busiest is `web1` (stot 6000 of 10000 sessions, weight 3).", "`down=web3`, `busiest=web1`, `share_percent=60`, `weight_busiest=3`, `conn_errors=12`."]),
    ],
    cases=[],
    cheat=[
        ["why balance", "capacity, availability, flexibility: one address, many interchangeable servers"],
        ["layer 4 / layer 7", "connections by address and port / requests by path, host, header; TLS termination, caching"],
        ["round robin", "rotate; even only for equal, uniform requests"],
        ["weighted", "weight 3 gets three requests for every one a weight 1 server gets"],
        ["least connections", "fewest requests in progress: adapts to slow servers"],
        ["hash / consistent hash", "same key, same server; consistent hashing moves only ~1/N keys when servers change"],
        ["passive health check", "count failed real requests (nginx max_fails, fail_timeout)"],
        ["active health check", "probe on a timer: fall N to mark DOWN, rise N to mark UP (HAProxy)"],
        ["detection delay", "about fall x interval: that is how long clients can hit a dead server"],
        ["retry rule", "retry only idempotent requests; never blind-retry a payment"],
        ["drain", "stop new requests, let in-flight finish, then update; nginx -s reload is graceful"],
        ["nginx -t", "validate a configuration before starting or reloading"],
        ["X-Forwarded-For / -Proto", "real client address and original scheme, added by the proxy; trust only from your own proxy"],
        ["429", "rate limited; limit_req zone rate burst in nginx"],
        ["X-Cache-Status", "HIT or MISS from the proxy cache"],
        ["gateway", "layer 7 proxy for APIs: routing, auth, per-client limits, one place for metrics"],
        ["HA balancer", "virtual IP with an active and a standby (keepalived), or several behind DNS or anycast"],
        ["global balancing", "GeoDNS or latency routing with health checks and a short TTL; plan capacity N+1 across regions"],
    ],
    interview_intro="Load balancing answers are judged on decisions and failure behaviour. For each question say the algorithm or layer, why it fits, how failure is detected, and what it costs. The worked scenarios in each lesson are the models to practise with.",
    interview=[
        dict(q="Design the load balancing for a web service with three app servers.",
             a=["One address in front, a layer 7 reverse proxy (TLS termination, path routing); servers stateless with shared session and data stores.", "Algorithm: round robin or least connections depending on request variance; weights if servers differ.", "Health checks (active and passive) with a few seconds detection time; retry only idempotent requests.", "Make the balancer redundant (virtual IP pair or managed service); drain servers during deploys; monitor per-backend errors and latency."],
             follow=["What if one server is slower?", "What if sessions are in memory?"], mistakes=["Saying \"add a load balancer\" and stopping.", "Forgetting balancer redundancy."],
             angle="Reported by candidates as a recurring sub-question inside almost every large design at big tech companies; not official."),
        dict(q="Compare round robin, least connections and consistent hashing.",
             a=["Round robin: simple and even for uniform requests. Least connections: adapts to uneven request cost or slow servers by sending to the least busy. Hashing: same key to the same server for cache or session locality.", "Plain `hash mod N` remaps almost everything when N changes; consistent hashing (with virtual nodes) moves about 1/N of keys.", "Choose by request variance, locality needs and how often servers change; verify with per-server load, not just counts."],
             follow=["What is a hot key problem?", "What is power of two choices?"], mistakes=["Treating even request counts as even load."]),
        dict(q="What is the difference between layer 4 and layer 7 load balancing?",
             a=["Layer 4 balances TCP connections by address and port without reading data: fast, protocol-agnostic. Layer 7 parses HTTP: routes by path, host or header, terminates TLS, rewrites headers, caches, rate limits.", "Layer 7 costs more CPU. Large systems combine them: layer 4 spreading connections across layer 7 proxies.", "gRPC and long-lived HTTP/2 need request-level balancing, so layer 7."],
             follow=["Where does TLS terminate and why?", "How does the backend learn the client IP?"], mistakes=["Giving only the layer numbers."]),
        dict(q="How do you deploy with zero downtime behind a load balancer?",
             a=["Roll one server at a time: remove it from rotation (drain), wait for in-flight requests, deploy, wait for health checks, return it, compare its metrics with the others.", "Canary first (a small share of traffic) with automatic rollback; blue-green for instant switch-back.", "Backward-compatible database changes, because both versions run side by side; keep spare capacity."],
             follow=["How do you roll back?", "What if a health check passes but users see errors?"], mistakes=["Restarting servers in place without draining."]),
        dict(q="How would you make the load balancer itself highly available?",
             a=["At least two balancers in different failure domains behind a virtual IP (active-passive with VRRP/keepalived) or several active ones behind DNS or anycast; or a managed cloud load balancer.", "Keep configuration identical; accept that some in-flight connections may break at failover.", "For regions: GeoDNS or latency routing with health checks and a short TTL, retries in clients, and spare capacity in the other regions."],
             follow=["How fast is failover and what bounds it?", "What happens to existing connections?"], mistakes=["Ignoring the balancer as a single point of failure."],
             angle="Amazon-style: expect \"what happens when it fails at 3 a.m. and who gets paged?\" as a follow-up; reported by candidates, not official."),
        dict(q="What does an API gateway do, and how is it different from a load balancer?",
             a=["A layer 7 front door for many services: routing by path or host, authentication, per-client rate limits and quotas, request transformation, central logging and metrics.", "It also load balances to service instances; the products overlap.", "Costs: an extra hop, a critical shared component, risk of business logic creeping in."],
             follow=["What is a BFF?", "Where does authentication belong?"], mistakes=["Calling them the same thing."]),
        dict(q="Users in Europe and Asia complain about latency. How do load balancing and DNS help?",
             a=["Serve from regions near users: GeoDNS or latency-based routing to the nearest healthy region, or anycast; a CDN for static content.", "Each region has its own balancers and servers; data placement and replication decide what can be served locally.", "Short TTLs and health checks for failover; plan spare capacity for regional failure."],
             follow=["What is the data story?"], mistakes=["Forgetting that data must be near the users too."],
             angle="Google-style: candidates commonly report follow-ups about consistency across regions; reported by candidates, not official."),
    ],
    selftest=[
        ("Name three reasons to use a load balancer.", "Capacity, availability and flexibility."),
        ("How many requests would a weight-3 server get compared with a weight-1 server?", "Three times as many."),
        ("Which algorithm adapts to a slow backend, and why?", "Least connections: the slow server keeps connections open so it gets fewer new ones."),
        ("What does consistent hashing improve over hash mod N?", "Only about 1/N of keys move when servers change."),
        ("What is the detection delay of an active health check with inter 1s and fall 3?", "About 3 seconds."),
        ("Why retry only idempotent requests?", "The failed attempt may have succeeded; repeating a non-idempotent request could duplicate its effect."),
        ("What is connection draining?", "Stop sending new requests to a server and let in-flight ones finish before stopping it."),
        ("What headers carry the client's identity through a reverse proxy?", "X-Forwarded-For and X-Forwarded-Proto."),
        ("What status code does rate limiting return?", "429 Too Many Requests."),
        ("What does an API gateway add beyond a balancer?", "Routing by API, authentication, per-client limits and central logging and metrics."),
        ("Why is DNS failover slower than health-check failover?", "Caches keep the old answer for the TTL, and some clients ignore it."),
        ("How is an active-passive balancer pair given one address?", "A virtual IP that the standby takes over when the master's announcements stop."),
    ],
    recall=[
        ["balancer", "one address, many interchangeable servers"],
        ["L4 vs L7", "bytes by connection vs requests by content"],
        ["least connections", "adapts to slow servers"],
        ["consistent hashing", "only ~1/N of keys move"],
        ["fall / rise", "probes to mark DOWN / UP"],
        ["drain", "stop new, finish old, then update"],
        ["X-Forwarded-For", "the client behind the proxy"],
        ["429", "rate limited"],
        ["virtual IP", "an address that moves between balancers"],
        ["GeoDNS", "nearest healthy region, bounded by TTL"],
    ],
    sources=[
        dict(title="nginx documentation: HTTP load balancing", url="https://nginx.org/en/docs/http/load_balancing.html", use="Algorithms, health checks and weights as used in the experiments", license="Copyright nginx; read online", how="Link only"),
        dict(title="HAProxy configuration manual", url="https://docs.haproxy.org/", use="Every setting used here: check, fall, rise, mode tcp, stats", license="Copyright HAProxy Technologies; read online", how="Link only"),
        dict(title="Consistent hashing and random trees (Karger et al.)", url="https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf", use="The original consistent hashing paper", license="Copyright the authors; read online", how="Link only"),
        dict(title="AWS: Elastic Load Balancing, how it works", url="https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/how-elastic-load-balancing-works.html", use="A real managed balancer: zones, nodes, health checks, cross-zone balancing", license="Copyright Amazon; read online", how="Link only"),
        dict(title="The Power of Two Random Choices (Mitzenmacher)", url="https://www.eecs.harvard.edu/~michaelm/postscripts/handbook2001.pdf", use="Why picking the better of two random servers works so well", license="Copyright the author; read online", how="Link only"),
    ],
    plan=[
        "**Hours 1 to 2:** the first lesson: build the rig, run the first balancer, then re-run it with a fourth backend of your own.",
        "**Hours 3 to 4:** algorithms: rerun the slow-backend experiment with different delays and request counts and explain every difference.",
        "**Hours 5 to 6:** health checks and deploys; then the nginx-balance lab.",
        "**Hours 7 to 8:** layer 4 versus 7 and TLS termination; add a third path to the routing example.",
        "**Hour 9:** proxy features, and the lb-stats-read lab.",
        "**Hours 10 and 11:** high availability and global balancing; then say each interview scenario aloud for two minutes, timed, and compare with the written answer.",
    ],
)
