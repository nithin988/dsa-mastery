"""S26 designing for reliability: part B (lessons 4 and 5: observability, disaster recovery and overload) and the module tail."""
import sysviz as v

OBS_VIZ = v.figure(
    720, 236,
    [v.box(10, 20, 220, 90, "Metrics", "acc", ""),
     v.text(120, 56, "numbers over time", "dg-s"), v.text(120, 80, "cheap, alerting, trends", "dg-s"),
     v.box(250, 20, 220, 90, "Logs", "acc", ""),
     v.text(360, 56, "what happened, in detail", "dg-s"), v.text(360, 80, "structured, with a request id", "dg-s"),
     v.box(490, 20, 220, 90, "Traces", "acc", ""),
     v.text(600, 56, "one request across services", "dg-s"), v.text(600, 80, "where did the time go", "dg-s"),
     v.box(120, 134, 480, 52, "Start from the symptom (a metric), narrow with traces, explain with logs", "ok", "alert, then dashboard, then trace, then log line"),
     v.text(360, 218, "RED for services (rate, errors, duration); USE for resources (utilisation, saturation, errors).", "dg-s")],
    "The three pillars of observability", "Metrics tell you that something is wrong, traces where, logs why")

OVERLOAD_VIZ = v.figure(
    720, 214,
    [v.box(10, 20, 330, 120, "Without load shedding", "bad", ""),
     v.text(175, 56, "work piles up, latency grows", "dg-s"), v.text(175, 82, "clients time out and retry", "dg-s"), v.text(175, 108, "the server works on answers nobody waits for", "dg-s"),
     v.box(380, 20, 330, 120, "With load shedding", "ok", ""),
     v.text(545, 56, "reject early when the queue is long", "dg-s"), v.text(545, 82, "the accepted requests finish quickly", "dg-s"), v.text(545, 108, "goodput stays at the server's capacity", "dg-s"),
     v.text(360, 176, "Saying \"no\" quickly to some requests is how you keep saying \"yes\" to the rest.", "dg-s"),
     v.text(360, 200, "Metastable failure: a retry storm keeps the system down even after the original trigger is gone.", "dg-s")],
    "Overload and load shedding", "Past capacity, accepting everything lowers the number of requests actually served")

LESSONS_B = [
    dict(
        title="Observability: metrics, logs and traces that answer \"what is wrong?\"",
        tier="hot",
        situation="Users report that checkout is slow. The average latency graph looks fine. Forty services are involved. Where do you look first, and what should have been recorded so that the answer takes minutes instead of hours?",
        learn=["Counters, gauges and histograms (and why the average lies)", "Percentiles from histogram buckets", "Structured logs and request ids across services", "RED and USE, and alerting on symptoms"],
        model=[
            "**Metrics** are numbers sampled over time: **counters** (requests served: only go up; you look at their **rate**), **gauges** (queue depth, memory: go up and down) and **histograms** (latency distribution in buckets). The **average** latency hides the pain: 99 requests at 20 ms and one at 2 seconds average 40 ms while one user in a hundred waits two seconds. Track **percentiles** (p50, p95, **p99**), computed from histogram buckets, since tail latency is what users and upstream timeouts experience, and in a chain of services the tail compounds. **Logs** record events in detail; make them **structured** (JSON with fields) and include a **request id** (and user or tenant id) so one request can be followed across services. **Traces** record the timeline of a request across services as nested **spans**, showing where the time went.",
            "A usable method: **RED** for services (**R**ate, **E**rrors, **D**uration) and **USE** for resources (**U**tilisation, **S**aturation, **E**rrors). **Alert on symptoms** that users feel (error rate and latency at the edge, measured against an SLO), not on every internal cause (CPU at 80 percent): causes are for dashboards, symptoms are for pages. Keep **high-cardinality** labels (user id) out of metrics (they explode storage) and in logs and traces. Add **deploy markers** and **version labels** so changes line up with graphs. A system you cannot observe, you cannot operate.",
        ],
        analogy="A car dashboard: the speedometer and warning lights (metrics) tell you something is wrong, the diagnostic computer (traces) says which system, and the service history and sensor logs (logs) say why. Average speed over a trip would never tell you about the five seconds the brakes failed.",
        visual=[OBS_VIZ],
        sim=None,
        walk=[
            ("Expose metrics from every service", "Request counter, error counter, latency histogram, saturation gauges."),
            ("Scrape and compute rates and percentiles", "Rates from counter differences, p99 from histogram buckets."),
            ("Log structured events with a request id", "One id travels with the request through every service."),
            ("Trace the slow request", "Find the span that dominates the time."),
            ("Alert on symptoms, page rarely", "Error rate and latency at the edge against the SLO."),
        ],
        groups=[
            dict(title="Metrics from a real service, percentiles, and following a request across services", cmds=[
                dict(volatile=True, c=r'''mkdir -p ~/rel && cd ~/rel && python3 - <<'EOF'
import http.client, random, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
rng = random.Random(9)
BUCKETS = [0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, float('inf')]
m = {'requests': 0, 'errors': 0, 'sum': 0.0, 'buckets': [0] * len(BUCKETS)}; lock = threading.Lock()
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path == '/metrics':                                           # the exposition format: plain text, one sample per line
            with lock:
                lines = ['http_requests_total %d' % m['requests'], 'http_errors_total %d' % m['errors'], 'http_request_duration_seconds_sum %.3f' % m['sum']]
                cum = 0
                for b, c in zip(BUCKETS, m['buckets']): cum += c; lines.append('http_request_duration_seconds_bucket{le="%s"} %d' % ('+Inf' if b == float('inf') else b, cum))
            body = ('\n'.join(lines) + '\n').encode()
        else:
            d = rng.choice([0.005] * 90 + [0.02] * 7 + [0.3] * 2 + [1.5])      # latency: mostly fast, a slow tail
            time.sleep(d)
            with lock:
                m['requests'] += 1; m['sum'] += d; m['errors'] += 1 if rng.random() < 0.02 else 0
                for i, b in enumerate(BUCKETS):
                    if d <= b: m['buckets'][i] += 1; break
            body = b'ok\n'
        self.send_response(200); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
srv = ThreadingHTTPServer(('127.0.0.1', 8320), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
def hit(n):
    c = http.client.HTTPConnection('127.0.0.1', 8320)
    for _ in range(n): c.request('GET', '/'); c.getresponse().read()
def scrape():
    c = http.client.HTTPConnection('127.0.0.1', 8320); c.request('GET', '/metrics'); return c.getresponse().read().decode()
t0 = time.time(); a = scrape()
ts = [threading.Thread(target=hit, args=(120,)) for _ in range(8)]; [t.start() for t in ts]; [t.join() for t in ts]
t1 = time.time(); b = scrape()
print('--- what a scrape looks like (one sample per line):'); print('\n'.join(b.splitlines()[:6] + ['...']))
def val(txt, name): return float([l for l in txt.splitlines() if l.startswith(name + ' ')][0].split()[1])
reqs = val(b, 'http_requests_total') - val(a, 'http_requests_total'); errs = val(b, 'http_errors_total') - val(a, 'http_errors_total')
print('--- computed from two scrapes %.1f s apart:' % (t1 - t0))
print('rate: %.0f requests/s   error ratio: %.1f%%   average latency: %.0f ms' % (reqs / (t1 - t0), 100 * errs / reqs, 1000 * (val(b, 'http_request_duration_seconds_sum') - val(a, 'http_request_duration_seconds_sum')) / reqs))
bk = [(float('inf') if '+Inf' in l else float(l.split('"')[1]), float(l.split()[1])) for l in b.splitlines() if 'bucket' in l]
total = bk[-1][1]
def pct(p):
    target = p / 100 * total
    for le, c in bk:
        if c >= target: return le
for p in (50, 95, 99): print('p%d latency: at most %s s' % (p, pct(p)))
print('the average (%.0f ms) is far below what the slowest 1%% of users experience (p99).' % (1000 * (val(b, 'http_request_duration_seconds_sum') - val(a, 'http_request_duration_seconds_sum')) / reqs))
srv.shutdown()
EOF''',
                     e="A real service exposing metrics in the standard text format, scraped twice. A **counter** only goes up, so its **rate** is the difference between scrapes divided by the time; the **histogram** buckets give the latency distribution, from which p50, p95 and p99 are read (the bucket whose cumulative count reaches that share of requests). The point is the last line: the **average** latency is a few tens of milliseconds, while the slowest 1 percent of requests take a second or more. An alert or an SLO on the average would never see the users who are suffering. (Real systems use a metrics library and a time-series database; the data model is exactly this.)",
                     annot=[("http_requests_total ... http_request_duration_seconds_bucket{le=\"0.01\"} ...", "the exposition format: counters and cumulative histogram buckets"),
                            ("rate: ~129 requests/s   error ratio: 2.3%   average latency: 35 ms", "rate and error ratio computed from counter differences"),
                            ("p50 latency: at most 0.01 s / p95: at most 0.025 s / p99: at most 1.0 or 2.5 s", "percentiles from buckets: the tail is far worse than the median"),
                            ("the average (35 ms) is far below ... p99", "averages hide the tail that users and timeouts feel")]),
                dict(volatile=True, c=r'''cd ~/rel && python3 - <<'EOF'
# Two services, a request id passed between them, and structured JSON logs. Then: reconstruct one slow request from the logs.
import http.client, json, threading, time, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
LOG = []
def log(service, rid, **kw): LOG.append(dict(t=round(time.time(), 3), service=service, request_id=rid, **kw))
class Inventory(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        rid = self.headers.get('X-Request-Id'); t = time.time()
        time.sleep(0.6 if 'slow' in self.path else 0.02)
        log('inventory', rid, msg='stock checked', path=self.path, ms=round((time.time() - t) * 1000))
        self.send_response(200); self.send_header('Content-Length', '2'); self.end_headers(); self.wfile.write(b'ok')
class Api(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        rid = self.headers.get('X-Request-Id') or str(uuid.uuid4())[:8]; t = time.time()
        c = http.client.HTTPConnection('127.0.0.1', 8322); c.request('GET', self.path, headers={'X-Request-Id': rid}); c.getresponse().read()   # the id travels downstream
        log('api', rid, msg='request served', path=self.path, ms=round((time.time() - t) * 1000))
        self.send_response(200); self.send_header('Content-Length', '2'); self.end_headers(); self.wfile.write(b'ok')
for port, h in ((8321, Api), (8322, Inventory)): threading.Thread(target=ThreadingHTTPServer(('127.0.0.1', port), h).serve_forever, daemon=True).start()
def call(path, rid):
    c = http.client.HTTPConnection('127.0.0.1', 8321); c.request('GET', path, headers={'X-Request-Id': rid}); c.getresponse().read()
for i, p in enumerate(['/cart', '/cart', '/slow/cart', '/cart']): call(p, 'req-%d' % (i + 1))
print('--- the structured log lines (JSON), from both services:')
for e in LOG[:4]: print(json.dumps(e))
print('...')
slow = [e for e in LOG if e['service'] == 'api' and e['ms'] > 300][0]
print('--- an alert says p99 is high. Find the slow request: ', slow['request_id'], 'took', slow['ms'], 'ms at the API')
print('--- follow that request id across services:')
for e in sorted((e for e in LOG if e['request_id'] == slow['request_id']), key=lambda e: e['t']): print('   %-10s %-14s %4d ms' % (e['service'], e['msg'], e['ms']))
print('the inventory service accounts for nearly all of it: look there.')
EOF''',
                     e="Following one request through two services. The request id is generated at the edge and passed in a header to every downstream call, and every service writes **structured JSON** log lines that include it. When an alert says latency is high, you pick a slow request from the API's log and **filter by its id** to see the whole story: the API took about 600 ms and the inventory service accounts for nearly all of it. That is distributed tracing in its simplest form; real tracers (OpenTelemetry) also record the parent-child timeline of spans automatically and sample requests to control cost.",
                     annot=[("{\"t\": ..., \"service\": \"inventory\", \"request_id\": \"req-1\", \"msg\": \"stock checked\", \"ms\": 2x}", "structured fields instead of free text: easy to filter and aggregate"),
                            ("the slow request: req-3 took ~620 ms at the API", "found from the alert by looking at slow entries"),
                            ("api request served ~620 ms / inventory stock checked ~600 ms", "following the id shows where the time went")]),
            ]),
        ],
        scenario=dict(
            title="\"Checkout is slow for some users but the average latency dashboard looks fine. How do you investigate, and what would you build so it is quick next time?\"",
            ask="A classic observability question. They want percentiles, drill-down method and the instrumentation to support it.",
            clarify=[("Slow for which users, endpoints, regions or versions? Since when? Did anything change?", "Slice the data: tail problems usually correlate with something (a region, a version, a tenant, a dependency).")],
            think=[("Stop looking at the average.", "Look at p95 and p99 latency (from histograms) at the edge, per endpoint, per region and per version; compare with the SLO."),
                   ("Narrow with the right tool.", "Dashboards (RED) to find which endpoint and when; traces for slow requests to find the slow span; logs filtered by request id for the why; deploy markers to correlate with changes."),
                   ("Check the usual suspects.", "A slow dependency (database query, downstream service), saturation (connection pool, CPU throttling, GC), retries amplifying load, a cold cache, one unhealthy instance (compare per-instance latency)."),
                   ("Fix and verify.", "Roll back or fix; watch the percentile recover; add an alert on the symptom."),
                   ("Build for next time.", "RED metrics with histograms in every service; structured logs with request ids; tracing with sampling that keeps slow and error traces; per-version and per-instance labels; SLO-based alerts on user-visible latency; runbooks linking alerts to dashboards."),
                   ("Avoid common traps.", "High-cardinality labels in metrics, alert fatigue from cause-based alerts, logs without ids, dashboards no one looks at.")],
            answer=["\"I would stop looking at the average, which hides tail problems, and look at p95 and p99 latency from histograms at the edge, sliced by endpoint, region and version, against the SLO. A deploy marker may line it up with a change. Then I drill down: traces for a few slow requests show which span dominates, and the logs filtered by that request id explain why. The usual suspects are a slow dependency or query, saturation such as a connection pool, retries amplifying load, a cold cache, or one unhealthy instance.",
                    "Next time should be quick, so I would make sure every service exposes RED metrics with latency histograms, writes structured logs with a request id that propagates through every call, and is traced with sampling that keeps slow and failed requests. Alerts would be on user-visible symptoms against the SLO rather than on every internal cause, with each alert linking to a dashboard and a runbook, and I would keep high-cardinality labels out of metrics.\""],
            follow=[("Why percentiles from histograms rather than averages?", "The average hides the tail; histograms record the distribution so any percentile can be computed, and they can be summed across instances (averages of percentiles cannot)."),
                    ("What is a good alert?", "One that fires on a user-visible symptom (error rate or latency against the SLO, with burn-rate windows), is actionable, links to a runbook, and rarely fires falsely."),
                    ("What is high cardinality and why is it a problem in metrics?", "Labels with very many distinct values (user ids): each combination is a separate time series, exploding storage and cost; keep such data in logs and traces.")],
            slips=["Using the average.", "Alerting on CPU instead of symptoms.", "No request id, so logs cannot be correlated."],
        ),
        quick=[
            ("Why is the average latency misleading?", "A slow tail hides in it: one user in a hundred can wait seconds while the average looks fine."),
            ("What do RED and USE stand for?", "RED: rate, errors, duration (services). USE: utilisation, saturation, errors (resources)."),
            ("Why put a request id in every log line?", "So one request can be followed across services and logs."),
        ],
        traps=[
            "Averaging percentiles from different instances: it is mathematically meaningless; aggregate histograms instead.",
            "Putting a user id as a metric label: millions of time series.",
            "Alerting on every cause: the pager becomes noise and the real symptom is missed.",
        ],
    ),
    dict(
        title="Disaster recovery and overload: restoring from nothing, and surviving too much",
        tier="hot",
        situation="Someone drops the production table. A region goes dark. Or the opposite problem: you are doing fine until traffic doubles, and the system's own retries finish it off. These are the two ends of reliability: recover from loss, and survive excess.",
        learn=["RPO and RTO, and what they cost", "A backup you have restored is the only backup", "Failover patterns: backup and restore, warm standby, active-active", "Load shedding and metastable failure"],
        model=[
            "**Disaster recovery** is defined by two numbers: **RPO** (recovery point objective: how much recent data you can afford to lose) and **RTO** (recovery time objective: how long you can be down). Backups give an RPO of the time since the last backup and an RTO of the **restore time**, which is usually much longer than people assume; **continuous archiving / replication** shrinks the RPO to seconds; a **warm standby** or **active-active** second site shrinks the RTO to minutes or seconds, at a cost in money and complexity. The rule: **a backup that has not been restored is a hope, not a backup**: test restores regularly, time them, keep copies in another failure domain and account, protect them from the same credentials that can delete production, and keep some **immutable** or offline.",
            "**Overload** is the other failure. A server has a capacity; beyond it, an unprotected system does **not** serve capacity requests per second, it serves **fewer**: queues grow, latency exceeds client timeouts, clients retry, and the server spends its effort on answers nobody is waiting for (**congestion collapse**). A **metastable failure** is when this retry load keeps the system down even after the original trigger has gone. The cure is **load shedding** (reject excess requests early and cheaply, with `503` or `429` and a `Retry-After`), **bounded queues**, **timeouts propagated downstream**, **client-side backoff and retry budgets**, **prioritising** important traffic, and **autoscaling** with headroom (it takes minutes, so it does not replace shedding). Rehearse both with game days and load tests.",
        ],
        analogy="Disaster recovery is the fire drill and the offsite copy of the ledger: you only know it works if you have run it. Overload is a restaurant on a rush night: a host who turns some people away at the door keeps the kitchen serving fast; a host who seats everyone makes every meal arrive cold.",
        visual=[OVERLOAD_VIZ],
        sim=None,
        walk=[
            ("Set RPO and RTO with the business", "What data loss and what downtime are acceptable, and what does each cost?"),
            ("Back up to another failure domain", "Different account, different region, some copies immutable."),
            ("Restore on a schedule and time it", "The measured restore time is your real RTO."),
            ("Protect the front door", "Bounded queues, shedding with 503 and Retry-After, priorities."),
            ("Rehearse both", "Disaster drills and overload tests before the real thing."),
        ],
        groups=[
            dict(title="Restore a dropped database, detect a bad backup, and watch overload collapse", cmds=[
                dict(volatile=True, c=r'''. ~/rel/rig.sh; pgup
pq -c "create table orders(id serial primary key, customer int, total numeric(10,2), note text)"
pq -c "insert into orders(customer, total, note) select (random()*10000)::int, round((random()*500)::numeric, 2), repeat('x', 100) from generate_series(1, 300000)"
echo "rows before the disaster: $(pq -At -c 'select count(*) from orders')"
t0=$(date +%s%N); pg_dump -h $RL -p 5581 -U learner -Fc app > $RL/app.dump; t1=$(date +%s%N)
echo "backup: $(( (t1-t0)/1000000 )) ms, file $(stat -c %s $RL/app.dump) bytes"
echo "--- DISASTER: someone runs DROP TABLE in production"
pq -c "drop table orders"
echo "tables left: $(pq -At -c "select count(*) from information_schema.tables where table_schema='public'")"
t0=$(date +%s%N); pg_restore -h $RL -p 5581 -U learner -d app $RL/app.dump; t1=$(date +%s%N)
echo "restore: $(( (t1-t0)/1000000 )) ms -> rows after restore: $(pq -At -c 'select count(*) from orders')   (this is your real RTO; a bigger database takes proportionally longer)"
echo "--- a backup that was never tested: truncated in transit"
head -c 300000 $RL/app.dump > $RL/bad.dump
createdb -h $RL -p 5581 -U learner scratch
pg_restore -h $RL -p 5581 -U learner -d scratch $RL/bad.dump 2>&1 | head -2
echo "(you only find out when you try to restore; so restore every backup, or a sample, automatically)"
pgdown''',
                     e="A disaster drill in miniature. A table of 300,000 rows is backed up with `pg_dump`, then **dropped**. The restore brings back every row, and the measured time is the **real RTO** for this data size (it grows with the data: a terabyte takes hours, which is why large systems use replicas and point-in-time recovery instead of dump files). The last test shows the second lesson: a truncated backup file is useless, and `pg_restore` only reveals that when you try. A backup job that reports success proves nothing about the restore, so **automate restore tests** and alert on their failure. (Real systems also archive the write-ahead log to restore to any second before the mistake: that is point-in-time recovery, which gives an RPO of seconds.)",
                     annot=[("rows before the disaster: 300000", "the data we must be able to get back"),
                            ("backup: ~N ms, file ~N MB", "the backup cost: small here, large for real databases"),
                            ("tables left: 0", "the disaster: the table is gone"),
                            ("restore: ~N ms -> rows after restore: 300000", "everything recovered; the time is the real RTO"),
                            ("pg_restore: error: could not read from input file: end of file", "the damaged file listed fine but failed when restored: only a real restore proves a backup")]),
                dict(c=r'''python3 - <<'EOF'
# Overload in virtual time: a server can finish 100 requests per second. Clients give up after 1 second and RETRY once.
# "goodput" = requests answered before the client gave up.
def simulate(offered_rate, shed, seconds=30, capacity=100, timeout=1.0, max_queue=50):
    queue = []                                    # arrival times of waiting requests (FIFO)
    good = bad = shed_count = 0
    carry = 0.0; served_budget = 0.0
    for tick in range(seconds * 100):            # 10 ms ticks
        now = tick / 100
        arrivals = offered_rate / 100
        n = int(arrivals + carry); carry = arrivals + carry - n
        for _ in range(n):
            if shed and len(queue) >= max_queue: shed_count += 1; continue        # reject early: cheap
            queue.append(now)
        served_budget += capacity / 100
        while served_budget >= 1 and queue:
            served_budget -= 1; arrived = queue.pop(0)                             # the server works on the oldest request first
            if now - arrived <= timeout: good += 1
            else: bad += 1                                                         # finished too late: the client already left; work wasted
    return good / seconds, bad / seconds, shed_count / seconds
print('capacity: 100 requests/s.  client timeout: 1 s.')
print('offered   WITHOUT shedding              WITH shedding (queue limit 50)')
print('load/s    useful/s  wasted/s            useful/s  wasted/s  rejected/s')
for rate in (50, 90, 100, 150, 300):
    g1, b1, _ = simulate(rate, False); g2, b2, r2 = simulate(rate, True)
    print('%6d    %7.0f  %7.0f             %7.0f  %7.0f  %9.0f' % (rate, g1, b1, g2, b2, r2))
EOF''',
                     e="Congestion collapse in numbers. Up to the server's capacity (100 per second) both versions serve everything. Beyond it, the **unprotected** server keeps accepting requests, its queue grows without limit, every request waits longer than the client's one-second timeout, and the server spends all its effort on answers nobody is waiting for: **useful throughput falls towards zero** while the machine is 100 percent busy. The server with a **bounded queue** rejects the excess immediately and keeps delivering about its full capacity of useful answers, whatever the offered load. Rejecting some requests quickly is what allows the rest to succeed.",
                     annot=[("load 50 and 90: both versions serve everything", "below capacity, shedding makes no difference"),
                            ("load 150 WITHOUT shedding: useful 10/s, wasted 90/s", "the queue's delay passes the client timeout: the server finishes requests too late to matter"),
                            ("load 300 WITHOUT shedding: useful 5/s, wasted 95/s", "congestion collapse: busy but useless"),
                            ("load 300 WITH shedding: useful 100/s, rejected 198/s", "capacity is spent on requests that can still succeed")]),
            ]),
        ],
        scenario=dict(
            title="\"Design disaster recovery for a payments database, and explain what happens when traffic doubles unexpectedly.\"",
            ask="A two-part reliability question: recovery from loss and survival under overload. They want numbers and mechanisms.",
            clarify=[("What are the RPO and RTO the business requires, and what is the data volume?", "Payments usually need RPO near zero and an RTO of minutes; that dictates synchronous replication and a hot standby.")],
            think=[("Define RPO and RTO.", "Payments: RPO of seconds or zero, RTO of minutes. Backups alone (RPO hours, RTO hours) are not enough."),
                   ("Choose the architecture.", "Synchronous replica in another zone (zero loss for a zone failure), asynchronous replica in another region (seconds of loss, survives a region), automated failover with fencing, continuous WAL archiving for point-in-time recovery."),
                   ("Backups.", "Regular base backups plus archived WAL to another account and region, some immutable or offline copies, encryption with keys held separately; protect against the compromised-credentials and operator-error scenarios."),
                   ("Test it.", "Automated restore tests with checksums and row counts, timed; quarterly failover and region-evacuation drills; measure the real RPO and RTO and report them."),
                   ("Overload part.", "Autoscaling takes minutes and databases do not scale instantly; so protect with rate limits per client, bounded queues and load shedding at the edge (503/429 with Retry-After), priority for critical operations (payments over reporting), timeouts and deadlines propagated, client backoff with retry budgets, and a degraded mode that disables expensive optional features."),
                   ("Avoid metastable failure.", "Do not let retries amplify: cap retries, circuit breakers; after an incident, ramp traffic back gradually."),
                   ("Operations.", "Runbooks, dashboards for saturation and queue depth, capacity reviews, load tests at 2x peak, game days.")],
            answer=["\"First the objectives: for payments I would want an RPO of seconds or zero and an RTO of minutes, which backups alone cannot give. So: a synchronous replica in another zone, an asynchronous replica in another region, automated failover with fencing, and continuous archiving of the write-ahead log for point-in-time recovery, plus base backups copied to another account and region with some immutable copies and separate encryption keys. And I would restore them automatically and time it, and rehearse failover and region evacuation regularly, because the measured RTO is the only one that counts.",
                    "When traffic doubles unexpectedly, autoscaling takes minutes and a database cannot scale instantly, so the system must protect itself: rate limits per client, bounded queues, and load shedding at the edge with 503 and Retry-After, priority for payments over reporting, timeouts and deadlines propagated downstream, client backoff with retry budgets and circuit breakers so retries do not create a metastable failure, and a degraded mode that switches off expensive optional features. I would load test at twice the peak and hold game days.\""],
            follow=[("What is point-in-time recovery?", "Restoring a base backup and replaying archived write-ahead log up to a chosen moment (such as just before a bad command), giving an RPO of seconds."),
                    ("Why is your restore time longer than you think?", "Restore must copy the data, rebuild indexes, replay logs and verify, often sequentially and over a network: measure it with production-sized data."),
                    ("What is metastable failure?", "A state where a feedback loop (typically retries) keeps the system overloaded after the original trigger is gone, so it stays down until load is reduced.")],
            slips=["Backups never restored.", "Autoscaling as the only answer to overload.", "Backups stored with the same credentials as production."],
        ),
        quick=[
            ("What do RPO and RTO mean?", "RPO: how much data you can lose; RTO: how long you can be down."),
            ("Why test restores?", "A backup that has never been restored may be unusable, and the restore time is your real RTO."),
            ("What does load shedding do?", "Rejects excess requests early so the accepted ones finish quickly and useful throughput stays at capacity."),
        ],
        traps=[
            "Backup jobs that report success but whose files are corrupt or incomplete.",
            "Backups in the same account and region as production: one mistake or one outage takes both.",
            "Unbounded queues and unlimited retries: the system collapses under the load it was supposed to absorb.",
        ],
    ),
]

TAIL = dict(
    cases=[],
    cheat=[
        ["nines", "99.9 = 8.8 h/year, 99.99 = 52 min, 99.999 = 5 min"],
        ["series / parallel", "series: multiply availabilities; parallel: multiply unavailabilities"],
        ["failure domain", "what fails together: rack, zone, region, version; redundancy must span domains"],
        ["N+1", "spare capacity so losing one copy does not overload the rest"],
        ["supervisor", "restarts crashed processes with backoff and alerts on loops"],
        ["graceful degradation", "optional dependencies get timeout, fallback, circuit breaker"],
        ["canary", "small share of real traffic, metric comparison, automatic rollback"],
        ["feature flag", "deploy is not release; percentage rollout and kill switch"],
        ["expand / migrate / contract", "backward-compatible database changes in steps"],
        ["RED / USE", "rate, errors, duration / utilisation, saturation, errors"],
        ["percentiles", "p99 from histograms; the average hides the tail"],
        ["request id", "in every log line and every downstream call"],
        ["alert on symptoms", "user-visible error rate and latency vs the SLO"],
        ["RPO / RTO", "data you can lose / time you can be down"],
        ["restore test", "an untested backup is a hope; time the restore"],
        ["PITR", "base backup + archived WAL: restore to any second"],
        ["load shedding", "bounded queues, reject early with 503/429 + Retry-After"],
        ["congestion collapse", "past capacity, goodput falls; wasted work on timed-out requests"],
        ["metastable failure", "retries keep the system down after the trigger is gone"],
        ["game day", "rehearse failures and overload before they happen"],
    ],
    interview_intro="Reliability answers are judged on arithmetic, failure domains, automation and testing: say the target, the numbers, what fails together, how recovery is automated and how you know it works. The worked scenarios in each lesson are the models to practise with.",
    interview=[
        dict(q="The business wants 99.99% availability for checkout. How do you design for it and what does it cost?",
             a=["99.99% is ~52 minutes a year (4 a month): failover and rollout must be automated.", "Budget the dependencies (you cannot beat the least available required one); remove single points of failure across failure domains with N+1 capacity; multi-region if needed.", "Graceful degradation, safe deployments, tested recovery; state the cost (about double infrastructure plus discipline) and agree an error budget."],
             follow=["What is an error budget?", "When is multi-region worth it?"], mistakes=["Promising nines without listing dependencies.", "Redundancy within one failure domain."],
             angle="Reported by candidates as a common reliability design prompt at large companies; not official."),
        dict(q="A dependency keeps failing and takes the product down with it. How do you make the system resilient?",
             a=["Classify it critical or optional; optional gets a timeout shorter than the page budget, a fallback (stale cache) and a circuit breaker.", "Critical: redundancy across failure domains, health-checked failover, headroom; retries only for idempotent calls with backoff.", "Bulkheads, bounded queues, load shedding; supervisors and health checks; test with fault injection."],
             follow=["Why is slow worse than down?", "What is a bulkhead?"], mistakes=["Retries as the only answer."],
             angle="Amazon-style: expect \"what do you page on and what is the first mitigation?\"; reported by candidates, not official."),
        dict(q="How do you deploy to millions of users with no downtime and the ability to undo mistakes?",
             a=["Small frequent automated changes; progressive delivery with canary percentages and automated comparison and rollback.", "Feature flags to separate deploy from release; expand, migrate, contract for the database.", "Rolling or blue-green with readiness and draining; region by region or cell by cell; deploy markers and post-incident reviews."],
             follow=["What is a cell-based architecture?", "How do you roll back a database change?"], mistakes=["Big-bang releases.", "Destructive migrations with the deploy."]),
        dict(q="Checkout is slow for some users but the average latency looks fine. How do you investigate?",
             a=["Stop using the average: p95 and p99 from histograms at the edge, sliced by endpoint, region and version, with deploy markers.", "Traces to find the slow span, logs filtered by request id for the why; check dependencies, saturation, retries, cold caches and a bad instance.", "Build for next time: RED metrics with histograms, structured logs with request ids, sampled traces keeping slow and error ones, SLO-based symptom alerts with runbooks."],
             follow=["Why histograms rather than averages?", "What is high cardinality?"], mistakes=["Alerting on CPU.", "No request ids."]),
        dict(q="Design disaster recovery for a payments database, and explain what happens when traffic doubles unexpectedly.",
             a=["RPO seconds or zero and RTO minutes: synchronous replica in another zone, asynchronous in another region, automated failover with fencing, WAL archiving for PITR, base backups in another account with immutable copies.", "Automated timed restore tests and failover drills: the measured RTO is the real one.", "Overload: rate limits, bounded queues, load shedding with 503/429 and Retry-After, priorities, deadlines, client backoff and retry budgets, degraded mode; avoid metastable failure; test at 2x peak."],
             follow=["What is PITR?", "What is metastable failure?"], mistakes=["Backups never restored.", "Autoscaling as the only answer."],
             angle="Google-style SRE: candidates commonly report follow-ups on testing restores and on handling retries during overload; reported by candidates, not official."),
    ],
    selftest=[
        ("How much downtime does 99.99% allow per year?", "About 52 minutes."),
        ("What is the availability of two independent 99.9% copies in parallel?", "99.9999%."),
        ("What is a failure domain?", "A set of components that fail together (rack, zone, region, version)."),
        ("What does a supervisor add?", "Automatic restart with backoff and alerts on crash loops."),
        ("What is graceful degradation?", "Keeping the core working with fallbacks when an optional part fails."),
        ("What does a canary limit?", "The blast radius of a bad release."),
        ("What is the difference between deploy and release with flags?", "Deploy puts code on servers; the flag controls who sees it."),
        ("Why is the average latency misleading?", "It hides the slow tail that users and timeouts experience."),
        ("What do RED and USE stand for?", "Rate, errors, duration; utilisation, saturation, errors."),
        ("What do RPO and RTO mean?", "Recovery point objective (data loss) and recovery time objective (downtime)."),
        ("Why test restores?", "Untested backups may be unusable and the restore time is the real RTO."),
        ("What does load shedding do?", "Rejects excess work early to keep useful throughput at capacity."),
        ("What is metastable failure?", "Retries or similar feedback keep the system overloaded after the trigger is gone."),
    ],
    recall=[
        ["99.99%", "52 minutes a year"],
        ["parallel", "multiply unavailabilities"],
        ["failure domain", "what fails together"],
        ["supervisor", "restart with backoff"],
        ["canary", "small share, compare, roll back"],
        ["flag", "deploy is not release"],
        ["p99", "from histogram buckets"],
        ["RED / USE", "services / resources"],
        ["RPO / RTO", "loss / downtime"],
        ["restore test", "time it"],
        ["shedding", "reject early with 503"],
    ],
    sources=[
        dict(title="Site Reliability Engineering (Google): Embracing Risk and Monitoring Distributed Systems", url="https://sre.google/sre-book/embracing-risk/", use="Availability targets, error budgets and monitoring philosophy", license="CC BY-NC-ND; read online", how="Link only"),
        dict(title="Google SRE: Addressing Cascading Failures", url="https://sre.google/sre-book/addressing-cascading-failures/", use="Overload, load shedding and retry amplification", license="CC BY-NC-ND; read online", how="Link only"),
        dict(title="AWS Builders' Library: Using load shedding to avoid overload", url="https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/", use="Practical load shedding from a large operator", license="Copyright Amazon; read online", how="Link only"),
        dict(title="AWS Builders' Library: Timeouts, retries and backoff with jitter", url="https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/", use="Retry design", license="Copyright Amazon; read online", how="Link only"),
        dict(title="PostgreSQL documentation: Backup and Restore", url="https://www.postgresql.org/docs/current/backup.html", use="pg_dump, base backups and point-in-time recovery", license="PostgreSQL licence; read online", how="Link only"),
        dict(title="Prometheus: Metric types and histograms", url="https://prometheus.io/docs/concepts/metric_types/", use="Counters, gauges and histograms used in the observability lesson", license="Apache 2.0; read online", how="Link only"),
        dict(title="OpenTelemetry documentation", url="https://opentelemetry.io/docs/", use="Standard tracing, metrics and logging instrumentation", license="Apache 2.0; read online", how="Link only"),
        dict(title="Metastable Failures in Distributed Systems (HotOS 2021)", url="https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s11-bronson.pdf", use="Why retries can keep a system down after the trigger is gone", license="Copyright the authors; read online", how="Link only"),
    ],
    plan=[
        "**Hours 1 to 2:** nines and domains: build the rig, extend the arithmetic with your own system's components; then the nines-calc lab.",
        "**Hours 3 to 4:** redundancy: change the supervisor's backoff and kill order; add a third optional dependency to the degradation demo.",
        "**Hours 5 to 6:** deployments: change the canary threshold and error rates; explain what each setting would have caught.",
        "**Hours 7 to 8:** observability: change the latency mix and see the percentiles move; then the percentiles lab.",
        "**Hour 9:** disaster recovery: time the restore on a larger table; add a second backup and compare.",
        "**Hours 10 and 11:** overload: change the capacity, timeout and queue limit; then say each interview scenario aloud for two minutes, timed, and compare with the written answer.",
    ],
)
