"""S26 designing for reliability: part A (rig, lessons 1 to 3: availability math, redundancy and degradation, safe deployments)."""
import sysviz as v

RIG = r'''mkdir -p ~/rel && cd ~/rel && cat > backend.py <<'EOF'
# A tiny versioned backend: python3 backend.py NAME PORT ERROR_PERCENT   (fails with 500 for ERROR_PERCENT of requests)
import random, sys, http.server, socketserver
name, port, err = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
rng = random.Random(port)
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        bad = rng.random() * 100 < err
        body = ('%s %s\n' % (name, 'ERROR' if bad else 'ok')).encode()
        self.send_response(500 if bad else 200); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, *a): pass
socketserver.ThreadingTCPServer.allow_reuse_address = True
socketserver.ThreadingTCPServer(('127.0.0.1', port), H).serve_forever()
EOF
cat > rig.sh <<'EOF'
# Backends on 9301.. and nginx on 8310, all private and local. Sockets, logs and nginx files live in ~/rel.
export RL=$HOME/rel PG=$(ls -d /usr/lib/postgresql/*/bin | head -1); export PATH=$PG:$PATH
start_backend() { (cd $RL && setsid python3 backend.py "$1" "$2" "${3:-0}" </dev/null >/dev/null 2>&1 & disown) 2>/dev/null; sleep 0.5; }
stop_all() { pkill -f "python3 backend.py" >/dev/null 2>&1; [ -f $RL/ngx/nginx.pid ] && kill $(cat $RL/ngx/nginx.pid) 2>/dev/null; sleep 0.4; true; }
mkngx() { mkdir -p $RL/ngx && cat > $RL/ngx/n.conf <<CONF
worker_processes 1; daemon on; pid $RL/ngx/nginx.pid; error_log $RL/ngx/error.log;
events { worker_connections 256; }
http { access_log off; client_body_temp_path $RL/ngx/cb; proxy_temp_path $RL/ngx/px; fastcgi_temp_path $RL/ngx/fc; uwsgi_temp_path $RL/ngx/uw; scgi_temp_path $RL/ngx/sc;
$1
}
CONF
}
ngx() { nginx -c $RL/ngx/n.conf -p $RL/ngx/ 2>&1 | grep -v "^$"; sleep 0.5; }
pgup()  { [ -d $RL/pg ] || initdb -D $RL/pg -A trust -U learner >/dev/null
          pg_ctl -D $RL/pg -o "-p 5581 -k $RL -c listen_addresses='' -c fsync=off" -l $RL/pg.log -w start >/dev/null
          createdb -h $RL -p 5581 -U learner app 2>/dev/null || true; }
pgdown(){ pg_ctl -D $RL/pg -m fast stop >/dev/null 2>&1; }
pq()    { psql -X -q -h $RL -p 5581 -U learner -d app "$@"; }
EOF
. ./rig.sh; echo "rig ready in $RL: backend.py and rig.sh (start_backend, stop_all, mkngx, ngx, pgup, pgdown, pq)"'''

NINES_VIZ = v.figure(
    720, 236,
    [v.box(10, 20, 340, 150, "Downtime allowed per year", "acc", ""),
     v.text(180, 54, "99%      3.65 days", "dg-s"), v.text(180, 80, "99.9%    8.8 hours", "dg-s"), v.text(180, 106, "99.99%   52.6 minutes", "dg-s"), v.text(180, 132, "99.999%  5.3 minutes", "dg-s"),
     v.box(380, 20, 330, 150, "What each extra nine costs", "warn", ""),
     v.text(545, 54, "redundant components in every layer", "dg-s"), v.text(545, 80, "multiple zones, then regions", "dg-s"), v.text(545, 106, "automation: no human in the failover path", "dg-s"), v.text(545, 132, "far more engineering and money per nine", "dg-s"),
     v.text(360, 206, "Pick the number from what an outage costs the business, then design to it. Do not promise more nines than your dependencies have.", "dg-s")],
    "The nines", "Each extra nine cuts the allowed downtime by ten and raises the cost far more")

DEPLOY_VIZ = v.figure(
    720, 232,
    [v.box(10, 20, 220, 60, "Rolling", "acc", "replace servers one by one"),
     v.box(250, 20, 220, 60, "Blue-green", "acc", "two full environments, switch the router"),
     v.box(490, 20, 220, 60, "Canary", "ok", "a small share of real traffic first"),
     v.text(120, 100, "simple; mixed versions during rollout", "dg-s"), v.text(360, 100, "instant switch-back; double capacity", "dg-s"), v.text(600, 100, "limits blast radius; needs metrics", "dg-s"),
     v.box(120, 124, 480, 56, "Feature flags separate deploy from release", "warn", "code ships dark; turn it on for 1 percent, then more, and off in seconds"),
     v.text(360, 214, "Whatever the method: small changes, automated checks, a fast rollback, and a watched metric that decides.", "dg-s")],
    "Safe deployment strategies", "How the change reaches users matters as much as what the change is")

LESSONS_A = [
    dict(
        title="Availability arithmetic and failure domains: what the nines really mean",
        tier="hot",
        situation="The product wants \"five nines\". Engineering says it is a lot of work. What does 99.999 percent allow per year, what does it cost, and why does putting two servers in the same rack not give you double the reliability?",
        learn=["Availability in nines, converted to minutes", "Series and parallel composition", "Failure domains and correlated failures", "Deciding the target from the cost of downtime"],
        model=[
            "**Availability** is the fraction of time a service works. In nines: 99 percent allows 3.7 days of downtime a year, 99.9 percent 8.8 hours, **99.99 percent 52 minutes**, 99.999 percent 5 minutes. Components in **series** (all needed) multiply: three 99.9 percent components give 99.7 percent. Components in **parallel** (any one is enough) multiply their **unavailability**: two independent 99.9 percent copies give 1 − 0.001² = 99.9999 percent. That is the mathematical case for redundancy, and it holds only if the failures are **independent**.",
            "Failures are often **correlated**: two servers in one rack share a power feed; two in one zone share a network; two in one region share a control plane; two deployed with the same bad release share the bug. A **failure domain** is the set of things that fail together, so redundancy must **span domains** (racks, zones, regions) and **versions** (staged rollouts). Add **N+1** (or N+2) capacity so that losing one unit does not overload the rest. The practical process: choose an **availability target** from what an hour of downtime costs, subtract what your **dependencies** can offer (you cannot be more available than the cloud region and the DNS provider you rely on), and spend engineering where the budget of unavailability is being used up.",
        ],
        analogy="Two spare tyres in the same boot do nothing for you if a thief takes the whole boot. Redundancy only protects against the failures that the copies do not share.",
        visual=[NINES_VIZ],
        sim=None,
        walk=[
            ("Set the target from the business", "What does an hour of downtime cost, and what do customers tolerate?"),
            ("List the dependencies and their availability", "The target cannot exceed what the components below it provide."),
            ("Find the failure domains", "Rack, zone, region, vendor, software version: what dies together?"),
            ("Add redundancy across domains", "Copies in different domains, with N+1 capacity."),
            ("Remove humans from the failover path", "Automated detection and failover; humans verify, not perform."),
        ],
        groups=[
            dict(title="Build the rig, then do the arithmetic", cmds=[
                dict(c=RIG,
                     e="Creates the rig used by the whole module: a tiny versioned backend that can be told to fail a given percentage of requests, helpers to write an nginx configuration and start and stop everything as an ordinary user, and PostgreSQL helpers for the disaster-recovery lesson. Nothing outside `~/rel` is touched."),
                dict(c=r'''python3 - <<'EOF'
MIN_YEAR = 365.25 * 24 * 60
def down(a): return (1 - a) * MIN_YEAR
print('target     downtime per year   per 30-day month')
for nines in ('99', '99.5', '99.9', '99.95', '99.99', '99.999'):
    a = float(nines) / 100
    y = down(a); m = (1 - a) * 30 * 24 * 60
    print('%-9s  %-18s  %s' % (nines + '%', ('%.1f minutes' % y) if y < 600 else ('%.1f hours' % (y / 60)) if y < 6000 else '%.1f days' % (y / 1440), ('%.1f minutes' % m)))
print()
print('series (all needed):  3 components at 99.9%% -> %.3f%%' % (100 * 0.999 ** 3))
print('parallel (any works): 2 independent copies at 99.9%% -> %.5f%%   3 copies -> %.7f%%' % (100 * (1 - 0.001 ** 2), 100 * (1 - 0.001 ** 3)))
print()
print('a service built from: load balancer 99.99%%, app tier 2 copies at 99.9%%, database 99.95%% (single), cache optional')
lb, app, db = 0.9999, 1 - 0.001 ** 2, 0.9995
total = lb * app * db
print('  overall: %.4f%%  ->  %.0f minutes of downtime a year   (the single database is the weakest link)' % (total * 100, down(total)))
db2 = 1 - 0.0005 ** 2
total2 = lb * app * db2
print('  with a second database copy:  %.4f%%  ->  %.0f minutes a year' % (total2 * 100, down(total2)))
print()
print('correlated failure: two copies in the SAME zone that fails 0.1%% of the time:')
print('  independent assumption: %.5f%%   real (both die with the zone): %.3f%%' % (100 * (1 - 0.001 ** 2), 100 * 0.999))
EOF''',
                     e="The arithmetic that should precede any \"we need five nines\" conversation. 99.99 percent is **52 minutes** a year, and 99.999 percent barely **5 minutes**, less than one slow deployment. In series availabilities multiply (more components, lower availability); in parallel the **unavailabilities** multiply (two 99.9 percent copies reach 99.9999 percent). The composite example shows the lesson: once the application tier is duplicated, the single database dominates the downtime; adding a second copy removes most of it. The last lines show the catch: two copies in the **same failure domain** do not multiply anything, because they fail together.",
                     annot=[("99.99% ... 52.6 minutes", "four nines allows under an hour of downtime a year"),
                            ("series: 3 components at 99.9% -> 99.700%", "every extra required component lowers the total"),
                            ("parallel: 2 independent copies -> 99.99990%", "redundancy multiplies the small unavailability"),
                            ("overall: 99.9400% -> about 315 minutes ... with a second database copy: 99.9899% -> about 53 minutes", "fixing the weakest link buys nearly an order of magnitude"),
                            ("independent assumption 99.99990% vs real 99.900%", "copies that share a failure domain are one copy for that failure")]),
            ]),
        ],
        scenario=dict(
            title="\"The business wants 99.99% availability for checkout. How do you design for it, and what does it cost?\"",
            ask="An availability design question. They want arithmetic, failure domains, dependencies and honesty about cost.",
            clarify=[("Is 99.99% measured at the user, per month, and what counts as down? What does an hour of downtime cost?", "Measure at the user's edge; define success with an SLI; compare the cost of downtime with the cost of the extra nines.")],
            think=[("Do the arithmetic.", "99.99 percent is about 4 minutes a month, 52 a year: shorter than most deployments and most manual recoveries, so failover and deployment must be automated."),
                   ("Budget the dependencies.", "List every dependency in the request path with its real availability (DNS, CDN, payment provider, database, cloud region). If a required dependency offers 99.9 percent, you cannot promise 99.99 without making it optional or redundant."),
                   ("Remove single points of failure across domains.", "Load balancers, app servers, databases and caches in at least two zones, N+1 capacity; multi-region if the region's own availability is not enough."),
                   ("Make failures cheap.", "Graceful degradation: checkout works without recommendations; fallbacks and cached data; timeouts, retries with backoff and circuit breakers; asynchronous steps through queues."),
                   ("Make changes safe.", "Most outages follow changes: canary releases, feature flags, automatic rollback, small batches, backward-compatible database migrations."),
                   ("Make recovery fast and tested.", "Automated failover, runbooks, game days, tested backups; detection in under a minute."),
                   ("State the cost.", "Roughly doubled infrastructure, more engineering and operational discipline per nine; propose the target the business will pay for and an error budget policy.")],
            answer=["\"First the arithmetic: 99.99 percent is about four minutes of downtime a month, shorter than most deployments or manual recoveries, so failover and rollout must be automated. Then I list every dependency in the checkout path with its real availability, because if a required one offers 99.9 percent I either make it optional with a fallback or add redundancy; I cannot promise more nines than my dependencies have.",
                    "Then I remove single points of failure across failure domains: balancers, app servers, databases and caches in at least two zones with spare capacity, and a second region if the region's own availability is not enough. I make failures cheap with graceful degradation, timeouts, retries with backoff, circuit breakers and queues; make changes safe with canaries, flags and automatic rollback; and make recovery fast and tested with automated failover and game days. And I would state the cost, roughly twice the infrastructure plus engineering discipline, and agree an error budget so the business chooses the target knowingly.\""],
            follow=[("What is an error budget?", "The allowed unreliability implied by the SLO (for example 0.01 percent): spend it on releases and experiments, and slow down when it is exhausted (the reliability practice module covers this)."),
                    ("Why are two servers in one zone not enough?", "They share failure domains (power, network, zone control plane), so the independence assumption in the arithmetic is false."),
                    ("When is multi-region worth it?", "When the cost of regional outages exceeds the cost and complexity of running active-active or fast-failover across regions, or when latency or data residency requires it.")],
            slips=["Promising nines without listing dependencies.", "Redundancy inside one failure domain.", "Manual failover in a four-nines design."],
        ),
        quick=[
            ("How much downtime does 99.99% allow per year?", "About 52 minutes."),
            ("What is the availability of two independent 99.9% copies in parallel?", "99.9999%."),
            ("What is a failure domain?", "The set of components that fail together, such as a rack, zone, region or software version."),
        ],
        traps=[
            "Counting redundant copies as independent when they share a rack, zone or release.",
            "Promising a target higher than the least available required dependency.",
            "Designing the failover but never testing it.",
        ],
    ),
    dict(
        title="Redundancy in practice: supervisors, failover and graceful degradation",
        tier="hot",
        situation="Processes crash. Servers die. A dependency goes slow. The question is not whether, but what happens next: does something restart the process, does traffic move to a healthy copy, and does the user still get a useful, if reduced, page?",
        learn=["Supervisors and automatic restart", "Health-checked failover across copies", "Graceful degradation instead of failure", "Why the failover path must be tested"],
        model=[
            "Reliable systems assume components fail and arrange for **automatic recovery**. A **supervisor** (systemd, a container orchestrator, a process manager) restarts a crashed process, with **backoff** so that a crash loop does not hammer the machine and an alert when it keeps failing. A **load balancer with health checks** stops sending traffic to a failed copy and resumes when it recovers (as in the load balancing module). **Redundant data** needs replication and tested failover (scaling data module).",
            "**Graceful degradation** keeps the core function working when a part fails: the product page loads without recommendations, search falls back to a simpler ranking, checkout accepts the order and queues the email. Design it deliberately: classify dependencies as **critical** (must work) or **optional**, give each optional one a **timeout, fallback value and circuit breaker**, serve **stale cached data** when the source is down, and **shed load** (reject low-priority work) before everything collapses. Then **test the failure paths**: kill instances in production-like environments (chaos testing, game days). A failover that has never run is a hope.",
        ],
        analogy="A hospital with a backup generator that switches on automatically, a duty rota so someone replaces a sick nurse, and a paper form for when the computers fail: the service continues, reduced but safe, and the generator is tested monthly.",
        sim=None,
        walk=[
            ("Detect the failure quickly", "Health checks, heartbeats, error-rate alerts; seconds, not minutes."),
            ("Restart or replace automatically", "A supervisor restarts the process; an orchestrator replaces the instance."),
            ("Route around it", "The balancer or client removes the failed copy from rotation."),
            ("Degrade instead of failing", "Fallbacks and cached data for optional dependencies; shed low-priority load."),
            ("Rehearse", "Kill things on purpose and watch what users see."),
        ],
        groups=[
            dict(title="A supervisor restarting a crashing service, and failover while a server dies", cmds=[
                dict(volatile=True, c=r'''. ~/rel/rig.sh; cd ~/rel
cat > flaky.py <<'EOF'
import os, threading, http.server, socketserver
threading.Timer(1.5, lambda: os._exit(1)).start()                      # the process crashes 1.5 s after every start
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.send_header('Content-Length', '3'); self.end_headers(); self.wfile.write(b'ok\n')
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
socketserver.TCPServer(('127.0.0.1', 9310), H).serve_forever()
EOF
cat > supervisor.sh <<'EOF'
#!/bin/bash
# A tiny supervisor: restart the service when it dies, with exponential backoff (1, 2, 4 ... seconds, capped).
delay=1; n=0
while [ $n -lt 3 ]; do
  python3 flaky.py >/dev/null 2>&1; n=$((n+1))
  echo "supervisor: service exited, restart $n in ${delay}s"; sleep $delay; delay=$((delay*2)); [ $delay -gt 2 ] && delay=2
done
EOF
chmod +x supervisor.sh
./supervisor.sh &
sleep 0.8; echo "request while up:      $(curl -s -m 1 http://127.0.0.1:9310/ || echo failed)"
sleep 1.1; echo "request after crash:   $(curl -s -m 1 http://127.0.0.1:9310/ || echo 'failed (service is down)')"
sleep 1.3; echo "request after restart: $(curl -s -m 1 http://127.0.0.1:9310/ || echo failed)"
wait''',
                     e="Self-healing in thirty lines. The service is built to crash 1.5 seconds after each start. A tiny supervisor restarts it each time it exits, **waiting longer after each failure** (exponential backoff) so that a crash loop cannot saturate the machine. A request while the service is down fails, but after the restart the next one succeeds without a human. Real supervisors (systemd, Kubernetes) add health checks, restart limits and alerts when restarts keep happening: a service that crashes every minute is up but unhealthy.",
                     annot=[("request while up: ok", "the first instance is serving"),
                            ("request after crash: failed (service is down)", "the window between a crash and the restart: the failure users could notice"),
                            ("supervisor: service exited, restart 1 in 1s ... restart 2 in 2s", "restarts with a growing delay: backoff against crash loops"),
                            ("request after restart: ok", "recovered automatically, no human involved")]),
                dict(volatile=True, c=r'''. ~/rel/rig.sh
start_backend a 9301; start_backend b 9302; start_backend c 9303
mkngx 'upstream pool { server 127.0.0.1:9301 max_fails=1 fail_timeout=5s; server 127.0.0.1:9302 max_fails=1 fail_timeout=5s; server 127.0.0.1:9303 max_fails=1 fail_timeout=5s; }
server { listen 8310; location / { proxy_pass http://pool; proxy_next_upstream error timeout http_502 http_503; proxy_connect_timeout 1s; } }'
ngx
run() { for i in $(seq 1 60); do curl -s -m 2 -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8310/; done | sort | uniq -c | tr -s ' ' | paste -sd' '; }
echo "all three healthy:        $(run)"
pkill -f "backend.py b 9302"; sleep 0.3
echo "backend b killed:         $(run)   <- no failed requests: nginx retried on another server"
pkill -f "backend.py c 9303"; sleep 0.3
echo "backends b and c killed:  $(run)"
pkill -f "backend.py a 9301"; sleep 0.3
echo "all three dead:           $(run)"
stop_all''',
                     e="Failover as users experience it. With three healthy backends all 60 requests succeed. When one is **killed**, the next requests that would have gone to it are retried on another server (`proxy_next_upstream`), so there are **no** failed requests, and the dead server stops being tried. With only one left everything still works (at one third of the capacity, which is why N+1 capacity matters). When all three are dead the failure is total and visible as 502s. The shape to remember: redundancy hides failures only while there is spare capacity and a working detection and retry path.",
                     annot=[("all three healthy: 60 x 200", "baseline"),
                            ("backend b killed: 60 x 200", "the balancer retried on another server: the user saw nothing"),
                            ("backends b and c killed: 60 x 200", "one server carries all the load: capacity, not availability, is now the risk"),
                            ("all three dead: 60 x 502", "no redundancy left: total failure")]),
                dict(c=r'''python3 - <<'EOF'
# Graceful degradation: a product page needs the product (critical) and recommendations (optional, sometimes down).
import random
rng = random.Random(2)
cache = {'recs:42': ['sock', 'hat', 'scarf']}                   # stale but useful recommendations kept from earlier
def get_recommendations(pid, healthy):
    if not healthy: raise TimeoutError('recommendation service timed out')
    return ['new-1', 'new-2']
def page_naive(pid, healthy):
    return {'product': pid, 'recs': get_recommendations(pid, healthy)}
def page_degraded(pid, healthy):
    page = {'product': pid}
    try: page['recs'] = get_recommendations(pid, healthy)
    except TimeoutError: page['recs'] = cache.get('recs:%d' % pid, [])        # optional dependency: fall back to stale data, never fail the page
    return page
failing = [rng.random() < 0.3 for _ in range(1000)]                # the recommender is down for 30% of requests
naive_ok = deg_ok = 0
for f in failing:
    try: page_naive(42, not f); naive_ok += 1
    except TimeoutError: pass
    page_degraded(42, not f); deg_ok += 1
print('recommendation service failing for %d of 1000 requests' % sum(failing))
print('page that treats it as critical:  %4d of 1000 pages served' % naive_ok)
print('page that degrades gracefully:    %4d of 1000 pages served (some with stale recommendations)' % deg_ok)
EOF''',
                     e="Why classifying dependencies matters. The recommender is **optional**, but the naive page treats it as critical, so a 30 percent failure rate of a nice-to-have feature becomes a 30 percent failure rate of the whole product page. The degraded version catches the failure, uses stale cached recommendations (or none) and serves **every** page. The user may see slightly older suggestions; they do not see an error. The same pattern applies to personalisation, ads, analytics, reviews and anything that is not the reason the user came.",
                     annot=[("recommendation service failing for 287 of 1000 requests", "the optional dependency is down about 30 percent of the time"),
                            ("page that treats it as critical: 713 of 1000 served", "a nice-to-have feature took the page down with it"),
                            ("page that degrades gracefully: 1000 of 1000 served", "optional dependency, fallback data: the page always works")]),
            ]),
        ],
        scenario=dict(
            title="\"One of our dependencies keeps failing and takes the product down with it. How do you make the system resilient?\"",
            ask="A resilience-design question. They want classification, fallbacks, timeouts and testing, not just \"add retries\".",
            clarify=[("Is the dependency critical to the user's goal? How does it fail: down, slow or wrong?", "Slow is worse than down; wrong data is worse than missing data.")],
            think=[("Classify the dependency.", "Critical (the request cannot succeed without it) or optional (the request can succeed without it, perhaps degraded)."),
                   ("Optional: degrade.", "Timeout shorter than the page's budget, fallback value (stale cache, default, empty), circuit breaker so you stop calling a sick dependency, and a metric that shows how often the fallback is used."),
                   ("Critical: make it redundant.", "Multiple instances across failure domains, health-checked failover, capacity headroom, retries with backoff only for idempotent calls; or queue the work and complete it later."),
                   ("Protect yourself from slowness.", "Timeouts everywhere, bulkheads (separate pools), load shedding, bounded queues."),
                   ("Recover automatically.", "Supervisors, health checks, auto-scaling and replacement, and alerts when the automatic recovery keeps firing."),
                   ("Test it.", "Fault injection: kill and slow the dependency in a test environment and in production at low blast radius; observe user-visible behaviour and fix the surprises."),
                   ("Measure.", "SLI at the user's edge, dependency error and latency, fallback rate, circuit state.")],
            answer=["\"First I classify the dependency: can the request succeed without it? If it is optional, I give it a timeout shorter than the page's budget, a fallback such as stale cached data or a default, and a circuit breaker so we stop hammering it when it is sick, plus a metric for how often the fallback is used. If it is critical, I make it redundant across failure domains with health-checked failover and spare capacity, and use retries with backoff only for idempotent calls, or queue the work to finish later.",
                    "I protect against slowness with timeouts everywhere, separate pools so one slow dependency cannot use all the threads, bounded queues and load shedding. Recovery is automatic through supervisors and health checks, with alerts when it keeps firing. Then I test the failure paths by killing and slowing the dependency on purpose, and measure the user-facing success rate rather than the dependency's own health.\""],
            follow=[("Why is a slow dependency worse than a dead one?", "A dead one fails fast and frees resources; a slow one ties up threads and connections in every caller until they fail too."),
                    ("What is a bulkhead?", "Isolating resources (thread pools, connections) per dependency so one failing dependency cannot exhaust everything."),
                    ("What is chaos engineering?", "Deliberately injecting failures (killed instances, added latency) to verify that the system degrades as designed, starting small and controlled.")],
            slips=["Retries as the only answer.", "Treating every dependency as critical.", "Never exercising the fallbacks."],
        ),
        quick=[
            ("What does a supervisor add to a service?", "Automatic restart on crash, with backoff so crash loops do not overload the machine."),
            ("What is graceful degradation?", "Keeping the core function working when an optional part fails, with fallbacks such as stale data."),
            ("Why must you test failover paths?", "An untested failover usually fails the first time it is needed."),
        ],
        traps=[
            "Restart loops with no backoff and no alert: a service that is \"up\" but crashing every minute.",
            "Fallbacks that are never exercised and silently broken.",
            "Redundancy with no spare capacity: losing one copy overloads the rest.",
        ],
    ),
    dict(
        title="Safe deployments: canaries, rollbacks and feature flags",
        tier="hot",
        situation="Most outages follow a change. A deployment that reaches every user at once turns a mistake into an incident. The goal is to let a bad change hurt as few people as possible for as short a time as possible.",
        learn=["Rolling, blue-green and canary releases", "Deciding automatically whether a canary is healthy", "Feature flags: separating deploy from release", "Backward-compatible database changes"],
        model=[
            "A **rolling** deployment replaces instances a few at a time (simple, but old and new versions run together and rollback means rolling forward again). **Blue-green** runs two full environments and switches the router: switching back is instant, at the cost of double capacity and the need to keep the data compatible. A **canary** sends a **small share of real traffic** (1 percent, then 5, 25, 100) to the new version while comparing its **error rate and latency** with the old one, and **automatically rolls back** when it is worse. Canary plus automation limits the **blast radius** and the **time to detect**.",
            "**Feature flags** separate **deploy** (code on the servers) from **release** (users see it): ship the code switched off, enable it for staff, then 1 percent of users, then everyone, and switch it off in seconds if metrics worsen, without redeploying. Flags need hygiene (remove old ones). **Database changes** must be **backward compatible** with both the old and new code, done in steps (expand: add the new column; migrate: write both; contract: remove the old one later), because during any rollout both versions run against the same data. Keep **changes small** and **frequent**: small changes have small blast radii, are easy to review and easy to revert.",
        ],
        analogy="Introducing a new recipe at a restaurant: serve it to one table, watch the reactions, then more tables, and keep the old kitchen ready. A feature flag is a menu card you can slip in or out without rebuilding the kitchen.",
        visual=[DEPLOY_VIZ],
        sim=None,
        walk=[
            ("Ship the new version beside the old", "Both run; the router decides who sees which."),
            ("Send a small share to the new version", "1 percent of requests, chosen at random or by user."),
            ("Compare error rate and latency by version", "Automatically, over a window long enough to be meaningful."),
            ("Promote or roll back by rule", "If the canary is within tolerance, increase the share; if not, route everything back."),
            ("Keep data compatible", "Expand, migrate, contract: both versions must work with the schema at every step."),
        ],
        groups=[
            dict(title="A real canary with an automatic rollback decision", cmds=[
                dict(volatile=True, c=r'''. ~/rel/rig.sh; cd ~/rel
start_backend stable 9301 0.5; start_backend canary 9302 30        # the new version has a bug: it fails 30% of requests (stable fails 0.5%)
conf() { clause="$1 canary;"; [ "$1" = 0% ] && clause=""; mkngx "upstream stable { server 127.0.0.1:9301; }
upstream canary { server 127.0.0.1:9302; }
split_clients \"\$request_id\" \$target { $clause * stable; }
server { listen 8310; location / { proxy_pass http://\$target; } }"; }
stats() { for i in $(seq 1 400); do curl -s -m 2 http://127.0.0.1:8310/; done | awk '{n[$1]++; if ($2=="ERROR") e[$1]++} END{for (k in n) printf "%s: %d requests, %d errors (%.1f%%)\n", k, n[k], e[k], 100*e[k]/n[k]}' | sort; }
conf 0%; ngx
decide() { stats | tee /tmp/canary.$$ | sed 's/^/   /'; rate=$(awk -F'[(%]' '/^canary/{print $2}' /tmp/canary.$$); if [ -n "$rate" ] && awk "BEGIN{exit !($rate > 5)}"; then echo "   decision: canary error rate ${rate}% is above 5% -> ROLL BACK"; return 1; else echo "   decision: healthy -> promote"; return 0; fi; }
for pct in 5% 25%; do echo "step: send $pct of traffic to the canary"; conf $pct; nginx -c $RL/ngx/n.conf -p $RL/ngx/ -s reload 2>/dev/null; sleep 0.5; if ! decide; then conf 0%; nginx -c $RL/ngx/n.conf -p $RL/ngx/ -s reload 2>/dev/null; sleep 0.5; echo "rolled back: all traffic is on the stable version again:"; stats | sed 's/^/   /'; break; fi; done
stop_all''',
                     e="A canary doing its job. The new version has a bug that fails 30 percent of requests, the stable version about half a percent. At the first step only **5 percent** of traffic reaches the canary, so only about one request in twenty hits an error, and the decision rule (canary error rate above 5 percent) fires within the first measurement window: the traffic is routed **back to the stable version** automatically. Compare this with a big-bang release that would have given 30 percent errors to every user until a human noticed. The rule needs real metrics, a large enough sample and a rollback that is one configuration change.",
                     annot=[("step: send 5% of traffic to the canary", "a small slice of real users exercises the new version"),
                            ("canary: 16 requests, 5 errors (31.2%) / stable: 384 requests, 4 errors (1.0%)", "the comparison shows the new version is much worse (sampled traffic: your numbers will differ)"),
                            ("decision: canary error rate above 5% -> ROLL BACK", "an automatic, metric-based rule"),
                            ("rolled back: stable: 400 requests, 1 errors (0.2%)", "everyone is back on the good version within seconds; only about 5 percent were ever affected")]),
                dict(c=r'''python3 - <<'EOF'
# A feature flag with percentage rollout and a kill switch: deterministic by user id, so a user sees a consistent experience.
import hashlib
flags = {'new-checkout': {'enabled': True, 'percent': 10}}
def on(flag, user):
    f = flags[flag]
    if not f['enabled']: return False
    bucket = int(hashlib.sha256(('%s:%s' % (flag, user)).encode()).hexdigest(), 16) % 100
    return bucket < f['percent']
users = ['user-%d' % i for i in range(1000)]
for pct in (0, 10, 50, 100):
    flags['new-checkout']['percent'] = pct
    print('rollout %3d%%: %4d of 1000 users see the new checkout' % (pct, sum(on('new-checkout', u) for u in users)))
flags['new-checkout']['percent'] = 50
before = {u for u in users if on('new-checkout', u)}
flags['new-checkout']['percent'] = 60
after = {u for u in users if on('new-checkout', u)}
print('raising 50%% -> 60%%: %d users stayed on, %d users were removed from the new version (consistent buckets)' % (len(before & after), len(before - after)))
flags['new-checkout']['enabled'] = False
print('kill switch: %d users see the new checkout (no redeploy needed)' % sum(on('new-checkout', u) for u in users))
EOF''',
                     e="A feature flag is a few lines of code and a config value. Hashing the user id into a bucket gives a **stable** assignment (a user does not flip between old and new on every request) and a percentage that you can raise gradually: raising from 50 to 60 percent adds users without removing anyone already on the new version. The **kill switch** turns the feature off for everyone immediately with no deployment, which is the rollback you want at 3 a.m. Treat flags as technical debt: remove them once a feature is fully released.",
                     annot=[("rollout 10%: 91 of 1000 users see the new checkout", "the percentage bucket works (hash buckets are close to, not exactly, 10 percent)"),
                            ("raising 50% -> 60%: 472 stayed on, 0 removed", "buckets are consistent: increasing the percentage never flips someone back"),
                            ("kill switch: 0 users", "switched off instantly without redeploying")]),
            ]),
        ],
        scenario=dict(
            title="\"How would you deploy changes to a system serving millions of users with no downtime and the ability to undo mistakes?\"",
            ask="The standard release-engineering question. They want strategy, automation, data compatibility and what you watch.",
            clarify=[("How often do we deploy, how fast can we detect bad releases, and does the change touch the database?", "Frequent small releases need automation; database changes need the expand-contract discipline.")],
            think=[("Small, frequent, automated.", "Trunk-based development, CI with tests, one pipeline to production, small changes that are easy to review and revert."),
                   ("Progressive delivery.", "Canary release: 1 percent, 5, 25, 100, with automated comparison of error rate, latency and business metrics against the baseline; automatic rollback on regression; bake time between steps."),
                   ("Separate deploy from release.", "Feature flags to turn features on gradually and off instantly, per user cohort or region."),
                   ("Compatible data changes.", "Expand, migrate, contract: add nullable columns or new tables first, deploy code that writes both, backfill, switch reads, remove the old later; never couple a destructive migration to a deploy."),
                   ("Zero downtime mechanics.", "Rolling or blue-green behind a load balancer with draining and readiness checks; stateless instances; connection draining; preStop hooks."),
                   ("Guard rails.", "Deployment freezes around peak events, change calendars, automatic halt when error budget is burned, cell-based or region-by-region rollout so a bad change cannot hit everywhere at once."),
                   ("Observe and learn.", "Dashboards by version, deploy markers on graphs, post-incident reviews feeding back into the pipeline.")],
            answer=["\"I would make changes small, frequent and automated: trunk-based development, a single pipeline with tests, and progressive delivery. Each release goes to a canary first, 1 percent then 5, 25 and 100, with an automated comparison of error rate, latency and business metrics against the stable version and an automatic rollback when it regresses, with bake time between steps. Risky features ship behind flags so they can be turned on gradually and off instantly without a redeploy.",
                    "Database changes follow expand, migrate, contract so old and new code both work with the schema at every step, and destructive changes never ride along with a deploy. For zero downtime I use rolling or blue-green behind a balancer with readiness checks and connection draining, and I roll out region by region or cell by cell so a bad change cannot hit everyone. Deploy markers on the dashboards and post-incident reviews feed back into the pipeline.\""],
            follow=[("What is a cell-based architecture?", "Dividing the system into independent cells, each serving a slice of customers, so a bad change or failure affects one cell, and rollouts proceed cell by cell."),
                    ("How long should a canary run?", "Long enough to collect a statistically meaningful sample and to cover cyclical behaviour (for example a few minutes at high traffic, longer at low traffic), with automatic checks."),
                    ("How do you roll back a database change?", "You usually do not: design changes to be backward compatible so the code can roll back while the schema stays; keep destructive steps separate and delayed.")],
            slips=["Big-bang releases.", "Rollback that depends on a human noticing.", "Destructive migrations tied to the deploy."],
        ),
        quick=[
            ("What does a canary release limit?", "The blast radius of a bad change: only a small share of users see it before it is checked."),
            ("What is the difference between deploy and release with feature flags?", "Deploy puts code on servers; release (via the flag) lets users see it, independently and reversibly."),
            ("What are the steps of a backward-compatible database change?", "Expand (add new), migrate (write both and backfill), contract (remove old) in separate releases."),
        ],
        traps=[
            "A canary with no automated decision: a human has to notice the graph.",
            "Feature flags that are never removed: combinatorial states and forgotten code.",
            "Running a destructive migration in the same release that needs it.",
        ],
    ),
]
