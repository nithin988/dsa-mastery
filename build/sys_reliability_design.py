"""Systems Mastery S20: designing for reliability."""
import sysviz as v

DOMAINS_VIZ = v.figure(
    720, 214,
    [v.box(10, 14, 220, 56, "Region A", "acc", "a whole geographic area"),
     v.box(250, 14, 220, 56, "Availability zone", "acc", "separate power and network"),
     v.box(490, 14, 220, 56, "Single machine", "acc", "the smallest failure unit"),
     v.text(120, 94, "fire, flood, provider outage,", "dg-s"), v.text(120, 112, "bad regional deploy", "dg-s"),
     v.text(360, 94, "data-centre power or network fault:", "dg-s"), v.text(360, 112, "spread across at least 2 to 3", "dg-s"),
     v.text(600, 94, "crash, disk, kernel panic:", "dg-s"), v.text(600, 112, "run several behind a balancer", "dg-s"),
     v.text(360, 156, "Redundancy only helps if copies fail independently: two servers in one rack share a fate.", "dg-s"),
     v.text(360, 182, "Choose the failure domain you want to survive, then place copies in different ones.", "dg-s")],
    "Failure domains", "Each level of redundancy protects against a bigger kind of failure")

MODULE = dict(
    id="rd",
    title="Designing for reliability",
    lead="Reliable systems are not those that never fail; they are those designed so that failures are expected, contained and survivable. This module covers availability arithmetic (the nines), redundancy and failure domains, disaster recovery (RPO and RTO), safe deployments (canary, blue-green, feature flags), resilience patterns (timeouts, circuit breakers, degradation) and the observability that tells you something is wrong.",
    time="6 to 7 hours",
    why=[
        "A deploy at 14:00 breaks checkout for everyone, and the rollback takes an hour. The same change released to 1 percent of traffic first would have shown a spike in errors within five minutes and rolled itself back, with almost nobody noticing. Reliability is mostly about limiting the blast radius of mistakes.",
        "Reliability questions end most system design interviews: \"what happens if this component dies?\", \"how many nines do you need and what does it cost?\", \"how do you deploy safely?\", \"how would you know it is broken?\" Good answers are specific and numerical.",
    ],
    outcomes=[
        "Compute availability for series and parallel designs and translate nines into downtime.",
        "Choose failure domains and explain what redundancy does and does not protect against.",
        "Explain RPO and RTO and pick a disaster recovery strategy.",
        "Describe canary, blue-green and feature-flag deployments and when each helps.",
        "Use timeouts, circuit breakers, bulkheads and graceful degradation.",
        "Explain the golden signals and why percentiles beat averages.",
    ],
    before=[
        "The distributed systems and scaling modules (S16, S18). Calculations use `python3`, `awk` and `sort`; simulations are seeded so outputs repeat.",
    ],
    env=["Scratch folder: `mkdir -p ~/rel && cd ~/rel`."],
    lessons=[
        dict(
            title="Availability and the nines",
            tier="hot",
            situation="The business wants \"five nines\". What does that actually mean, and what does it cost?",
            learn=["Nines to downtime", "Series versus parallel availability", "Why each extra nine is far more expensive"],
            model=[
                "Availability is the share of time a service works, quoted in **nines**: 99 percent allows 3.65 days of downtime a year, **99.9 percent** about 8.8 hours, **99.99 percent** about 52 minutes and **99.999 percent** about 5 minutes. Components in **series** (every one must work) multiply their availabilities, so the whole is **worse** than each part. Components in **parallel** (any one is enough, failing independently) multiply their **failure** probabilities, so the whole is **better**. Redundancy is how you get nines; each extra nine costs roughly ten times more effort, so pick the target from what the business really needs.",
            ],
            analogy="A chain is as weak as its weakest link (series). Two parachutes are safer than one (parallel), but only if they cannot both fail for the same reason.",
            sim="nines",
            groups=[
                dict(title="The arithmetic", cmds=[
                    dict(c="mkdir -p ~/rel && cd ~/rel && python3 -c \"print('availability   per year      per 30-day month')\nfor n in (2,3,4,5):\n    a=1-10**-n; y=(1-a)*365*24*60; m=(1-a)*30*24*60\n    print('%-13s %-13s %s' % (('%.*f%%' % (max(0,n-2),100*a)), ('%.0f min' % y if y<600 else '%.1f h' % (y/60)), ('%.1f min' % m)))\"", e="Downtime allowed per year and per month for two to five nines. Four nines leaves under an hour a year, which no human can meet by manual fixing alone."),
                    dict(c="python3 -c \"a=0.999\nprint('series, 3 services at 99.9%%:   %.4f%%' % (100*a**3))\nb=0.99\nprint('parallel, 2 servers at 99%%:    %.4f%%' % (100*(1-(1-b)**2)))\nprint('parallel, 3 servers at 99%%:    %.6f%%' % (100*(1-(1-b)**3)))\"", e="Three services in series at 99.9 percent give only 99.70 percent. Two independent servers at 99 percent in parallel reach 99.99 percent, three reach 99.9999 percent. That is the whole case for redundancy, with one condition: independent failures."),
                ]),
            ],
            quick=[
                ("What availability allows about 52 minutes of downtime a year?", "99.99 percent (four nines)."),
                ("What happens to availability when you chain services in series?", "It multiplies, so the whole is lower than any single part."),
            ],
            traps=[
                "Counting redundancy that is not independent: two servers behind one switch, one power feed or one bad config push fail together.",
                "Promising more nines than your dependencies provide: you cannot be more available than the services you rely on.",
            ],
        ),
        dict(
            title="Redundancy, failure domains and multi-region",
            tier="hot",
            situation="\"What if the data centre loses power? What if the whole region is down?\" The answer depends on which failure you decided to survive.",
            learn=["Failure domains: machine, zone, region", "Active-passive versus active-active", "What multi-region costs"],
            model=[
                "A **failure domain** is the set of things that fail together: a machine, a rack, an **availability zone** (separate power and network in one region), a **region**. Redundancy only protects you if the copies are in **different** domains. Running across 2 to 3 zones survives a data-centre fault and is the normal baseline. **Multi-region** survives a whole-region outage but costs a lot: **active-passive** keeps a standby region ready (simpler, failover takes time), **active-active** serves traffic from several regions at once (fast failover, but data must be replicated and conflicts resolved, bringing back the consistency trade-offs of the distributed systems module).",
            ],
            analogy="Keeping your spare key in the same drawer as your keys protects against nothing. Put one at a neighbour's house (another zone) or in another town (another region).",
            visual=DOMAINS_VIZ,
            quick=[
                ("Why spread replicas across availability zones?", "Zones have separate power and networking, so a fault in one does not take down every copy."),
                ("What is the main extra difficulty of active-active multi-region?", "Replicating data between regions and resolving conflicting writes, with the consistency trade-offs that implies."),
            ],
            traps=[
                "Placing \"redundant\" copies in one zone or behind one shared dependency, so a single event takes all of them.",
                "Designing multi-region without ever testing a regional failover: it usually fails the first time it is needed.",
            ],
        ),
        dict(
            title="Disaster recovery: RPO and RTO",
            tier="hot",
            situation="A region is gone. How much data can you lose, and how long can you be down? Those two numbers decide the whole plan.",
            learn=["RPO and RTO", "Backup and restore, pilot light, warm standby, active-active", "Testing restores"],
            model=[
                "**RPO** (recovery point objective) is how much data you can afford to lose, expressed as time: backups every 6 hours mean up to 6 hours lost. **RTO** (recovery time objective) is how long you can afford to be down: detection, decision, restore, start-up. Strategies, from cheap and slow to expensive and fast: **backup and restore**, **pilot light** (a minimal core always running), **warm standby** (a scaled-down live copy) and **active-active**. Whatever you choose, **test the restore**: a backup you have never restored is only a hope, and real RTO is usually much worse than the plan.",
            ],
            analogy="Insurance: the premium (cost) buys a smaller loss (RPO) and a faster return to normal (RTO); no insurance is cheapest until the day you need it.",
            sim="dr",
            groups=[
                dict(title="What a backup schedule really promises", cmds=[
                    dict(c="python3 -c \"print('backup every   worst-case loss   average loss')\nfor h in (24,6,1):\n    print('%2d hours       %2d hours          %.1f hours' % (h, h, h/2))\"", e="With periodic backups, the worst case is the whole interval and, on average, half of it. Cutting the loss to minutes means continuous replication of the changes (the write-ahead log), not more frequent full backups."),
                ]),
            ],
            quick=[
                ("What is RPO?", "How much data loss is acceptable, as a length of time (the gap between the last recoverable point and the disaster)."),
                ("Which DR strategy is fastest to recover but most expensive?", "Active-active, running full capacity in several regions."),
            ],
            traps=[
                "Backups stored in the same account or region as the data they protect.",
                "Never restoring a backup in a drill, so corruption or missing steps are discovered during a real disaster.",
            ],
        ),
        dict(
            title="Safe deployments: canary, blue-green, feature flags",
            tier="hot",
            situation="Most outages are caused by changes. How do you release often without betting the whole site each time?",
            learn=["Canary and progressive rollout", "Blue-green and instant rollback", "Feature flags and kill switches"],
            model=[
                "Limit the **blast radius** of every change. A **canary** release sends a small share of real traffic (1 percent, then 5, 25, 50, 100) to the new version while automatic checks compare its errors and latency with the old one, and rolls back if it is worse. **Blue-green** keeps two full environments and flips traffic between them, so rollback is one switch. **Feature flags** separate **deploying** code from **releasing** it: ship it switched off, enable it gradually, and turn it off instantly with no new deploy. Also: deploy small changes, deploy often, never on Friday evening without a reason, and make rollback boring and rehearsed.",
            ],
            analogy="Testing a new recipe on one table before changing the whole restaurant's menu.",
            sim="canary",
            groups=[
                dict(title="A canary that catches a bad release", cmds=[
                    dict(c="cd ~/rel && cat > canary.py <<'EOF'\nimport random\nrng = random.Random(4)\nbaseline_err, bad_err = 0.01, 0.06   # v1 fails 1% of requests; the broken v2 fails 6%\nfor share in (1, 5, 25, 50, 100):\n    requests = 4000 * share // 5 if share > 1 else 800\n    errors = sum(1 for _ in range(requests) if rng.random() < bad_err)\n    rate = errors / requests\n    verdict = 'ROLL BACK' if rate > 2 * baseline_err else 'ok'\n    print('canary %3d%%: %5d requests, error rate %.1f%% (baseline %.1f%%) -> %s' % (share, requests, rate * 100, baseline_err * 100, verdict))\n    if verdict == 'ROLL BACK':\n        print('  rollout stopped after exposing %d%% of users' % share)\n        break\nEOF\npython3 canary.py", e="The broken version fails 6 percent of requests against a 1 percent baseline. The very first 1 percent step already shows the problem and the rollout stops there, so only about one user in a hundred was affected, compared with everyone if the release had gone out at once. The rule here (more than twice the baseline error rate) is a simple stand-in for real automatic analysis."),
                ]),
            ],
            quick=[
                ("What does a canary release do?", "Sends a small share of real traffic to the new version, compares its health with the old one, and rolls back automatically if it is worse."),
                ("What is the benefit of feature flags?", "You can release gradually and switch a feature off instantly without a new deployment."),
            ],
            traps=[
                "A canary with no automatic checks relies on someone watching a dashboard; define the metrics and thresholds in advance.",
                "Database changes that break the old version: use backwards-compatible migrations so rollback is possible.",
            ],
        ),
        dict(
            title="Resilience patterns: timeouts, circuit breakers, degradation",
            tier="hot",
            situation="One slow dependency can make every thread in your service wait, and then your service looks dead to its callers. Failures spread unless you stop them.",
            learn=["Timeouts and retries", "Circuit breakers and bulkheads", "Graceful degradation and backpressure"],
            model=[
                "Assume every dependency will sometimes be slow or down. Set a **timeout** on every remote call (the default is often far too long) and limit **retries** (with backoff). A **circuit breaker** stops calling a failing dependency: after enough failures it **opens** and calls fail instantly, then **half-opens** to test recovery, protecting your resources and giving the other service room to heal. **Bulkheads** give each dependency its own pool so one cannot exhaust everything. **Graceful degradation** serves a reduced experience (cached data, a default, a clear message) instead of failing. **Backpressure** and load shedding refuse excess work early instead of collapsing under it.",
            ],
            analogy="Ship compartments (bulkheads) stop one leak sinking the ship; a fuse (circuit breaker) cuts the circuit before the wiring burns.",
            sim="breaker",
            groups=[
                dict(title="A breaker opening and recovering", cmds=[
                    dict(c="cd ~/rel && cat > breaker.py <<'EOF'\n# The dependency fails for calls 4 to 9, then recovers. Breaker: open after 3 failures in a row, trial after 2 skipped calls.\ncalls_ok = [True, True, True, False, False, False, False, False, False, True, True, True, True]\nstate, fails, skipped = 'closed', 0, 0\nfor i, ok in enumerate(calls_ok, 1):\n    if state == 'open':\n        skipped += 1\n        if skipped <= 2:\n            print('call %2d: breaker OPEN, failed fast (dependency not called)' % i)\n            continue\n        state = 'half-open'\n    result = 'ok' if ok else 'FAIL'\n    if state == 'half-open':\n        state = 'closed' if ok else 'open'\n        skipped = 0\n        fails = 0 if ok else fails\n        print('call %2d: half-open trial -> %s, breaker now %s' % (i, result, state.upper()))\n        continue\n    fails = 0 if ok else fails + 1\n    if fails >= 3:\n        state, skipped = 'open', 0\n    print('call %2d: %s%s' % (i, result, '  -> breaker OPENS' if state == 'open' else ''))\nEOF\npython3 breaker.py", e="After three straight failures the breaker opens and the next calls fail instantly without touching the sick dependency. A trial call that fails keeps it open; once the dependency recovers, a successful trial closes it again and normal traffic resumes.", parts=[("closed / open / half-open", "pass through, fail fast, test recovery")]),
                ]),
            ],
            quick=[
                ("What does a circuit breaker do when a dependency keeps failing?", "It opens and fails calls immediately, then periodically tests recovery with a trial call."),
                ("What is graceful degradation?", "Serving a reduced but useful response (cache, default, message) when a dependency is down, instead of failing completely."),
            ],
            traps=[
                "No timeout on a remote call: one slow dependency can hold every thread and take your whole service down.",
                "Retries at several layers multiply load on a struggling service; retry in one place with a budget.",
            ],
        ),
        dict(
            title="Observability: the signals that tell you it is broken",
            tier="hot",
            situation="Users complain on social media before your dashboard turns red. By the time you know, it has been an hour.",
            learn=["Metrics, logs and traces", "The four golden signals", "Percentiles instead of averages"],
            model=[
                "**Observability** is being able to ask new questions about a running system from its outputs: **metrics** (numbers over time: cheap, great for alerting), **logs** (detailed events: great for diagnosis) and **traces** (one request followed across services). Watch the four **golden signals**: **latency**, **traffic**, **errors** and **saturation**. Measure latency with **percentiles** (p50, p95, p99), not the average: a few very slow requests barely move the mean but ruin the experience of the users who hit them, and at scale \"1 percent\" is many people. Alert on symptoms users feel (errors, latency), not on every internal cause.",
            ],
            analogy="A hospital monitor: several vital signs on one screen with alarms for dangerous values, and the full chart and scans available when you need to diagnose.",
            groups=[
                dict(title="Averages hide the tail", cmds=[
                    dict(c="cd ~/rel && python3 -c \"import random\nr=random.Random(8)\nv=[max(5,int(r.gauss(80,15))) for _ in range(940)]+[int(r.uniform(900,2500)) for _ in range(60)]\nr.shuffle(v)\nopen('lat.txt','w').write('\\n'.join(map(str,v))+'\\n')\" && sort -n lat.txt | awk '{a[NR]=$1; s+=$1} END{printf \"requests %d\\nmean    %d ms\\np50     %d ms\\np95     %d ms\\np99     %d ms\\n\", NR, s/NR, a[int(NR*0.50)], a[int(NR*0.95)], a[int(NR*0.99)]}'", e="1,000 requests where 6 percent are very slow. The mean (about 170 ms) looks acceptable and the median (80 ms) looks great, yet p95 and p99 show requests taking a second or more. A dashboard of averages would never show what those users feel.", parts=[("sort -n | awk", "sort the latencies, then read the value at each rank"), ("a[int(NR*0.99)]", "the 99th percentile: 99 percent of requests were faster")]),
                ]),
            ],
            quick=[
                ("Name the four golden signals.", "Latency, traffic, errors and saturation."),
                ("Why prefer p99 over the average for latency?", "The average hides a slow tail; p99 shows what the slowest 1 percent of requests experience."),
            ],
            traps=[
                "Alerting on CPU instead of user-visible symptoms creates noisy alerts that people learn to ignore.",
                "Averaging percentiles across servers is meaningless; aggregate the raw histogram buckets instead.",
            ],
        ),
    ],
    labs=[
        dict(kind="linux", script="nines-calc", dir="nines", title="Availability arithmetic",
             goal=["Convert an SLA into minutes of downtime and compute series and parallel availability."],
             story=["A customer contract promises 99.95 percent. Before signing, you need to know how many minutes that allows, how a two-service chain behaves, and what redundancy buys."],
             tasks=["Read `scenario.txt`.", "Compute the four answers (a calculator, `awk` or Python is fine).", "Write the four `key=value` lines into `~/sys-lab/answers-nines.txt`."],
             check="Run the check script.", check_cmd="bash ~/sys-lab/check-nines-calc.sh",
             hints=["Downtime allowed = (1 - availability) x minutes in the month.", "Series: multiply the availabilities.", "Parallel: 1 minus the product of the failure probabilities."],
             solution=["allowed_minutes = 43,200 x 0.0005 = 21.6.", "series_percent = 0.999 x 0.999 = 99.80.", "parallel_percent = 1 - 0.01 x 0.01 = 99.99.", "worst_case_loss_hours = 6."]),
        dict(kind="linux", script="percentiles", dir="lat", title="Percentiles versus the average",
             goal=["Compute p50, p95, p99 and the mean of a latency log with shell tools, and see why the mean misleads."],
             story=["`latencies.txt` holds the response times of 1,000 requests. The dashboard shows the average and says everything is fine, but users are complaining."],
             tasks=["Read `README.txt` for the nearest-rank rule.", "Compute p50, p95, p99 and the rounded mean.", "Write `p50=`, `p95=`, `p99=` and `mean=` into `~/sys-lab/answers-lat.txt`."],
             check="Run the check script.", check_cmd="bash ~/sys-lab/check-percentiles.sh",
             hints=["`sort -n latencies.txt | sed -n '500p'` prints the 500th value.", "p95 is the 950th value and p99 the 990th (N is 1,000).", "`awk '{s+=$1} END{print s/NR}'` gives the mean."],
             solution=["Sort the file numerically and print lines 500, 950 and 990.", "Compute the mean with awk and round it.", "Write the four lines to the answers file."]),
    ],
    cases=[],
    cheat=[
        ["99% / 99.9% / 99.99% / 99.999%", "3.65 days / 8.8 h / 52 min / 5 min downtime per year"],
        ["series", "multiply availabilities: worse than any part"],
        ["parallel (independent)", "1 - product of failure probabilities: better"],
        ["failure domains", "machine, zone, region: copies must be in different ones"],
        ["RPO / RTO", "data you can lose / time you can be down"],
        ["DR strategies", "backup and restore, pilot light, warm standby, active-active"],
        ["canary", "small share first, compare with baseline, auto rollback"],
        ["blue-green", "two environments, flip traffic, instant rollback"],
        ["feature flag", "deploy dark, release gradually, kill switch"],
        ["timeout, retry with backoff", "on every remote call, with limits"],
        ["circuit breaker", "closed, open (fail fast), half-open (trial)"],
        ["bulkhead, degradation, backpressure", "isolate pools, serve less, refuse early"],
        ["golden signals", "latency, traffic, errors, saturation"],
        ["percentiles", "p50, p95, p99: use them, not the average"],
    ],
    interview_intro="For reliability questions, name the failure, the blast radius, the detection and the recovery. Four short sentences beat a long architecture tour.",
    interview=[
        dict(q="What does \"five nines\" mean, and what would it take?",
             a=["99.999 percent availability: about 5 minutes of downtime a year, 26 seconds a month.", "It needs redundancy in independent failure domains, automatic failover, safe deployments and strong observability; manual recovery cannot meet it.", "Each extra nine costs roughly ten times more, and you cannot exceed the availability of your dependencies: choose the target from business need."],
             follow=["How does series versus parallel change the maths?", "What is your error budget at 99.95 percent?"], mistakes=["Promising five nines without measuring dependencies."],
             angle="Amazon-style: candidates commonly report follow-ups asking what you would do when the dependency you rely on is the bottleneck; reported by candidates, not official."),
        dict(q="How do you deploy changes safely to a large service?",
             a=["Small, frequent changes; automated tests and checks in the pipeline.", "Progressive rollout (canary) with automatic comparison of errors and latency and automatic rollback; blue-green for instant switch-back; feature flags to separate deploy from release.", "Backwards-compatible database migrations so rollback is always possible."],
             follow=["How do you roll back a schema change?"], mistakes=["Big-bang releases.", "Rollback that depends on a human noticing."]),
        dict(q="Explain RPO and RTO and how they drive your disaster recovery design.",
             a=["RPO is acceptable data loss in time; RTO is acceptable downtime.", "Small RPO means continuous replication; small RTO means a warm or active standby, automation and rehearsed runbooks.", "Match the cost to the business value and test restores regularly."],
             follow=["What does your backup strategy look like?"], mistakes=["Untested backups."]),
        dict(q="What is a circuit breaker and why do you need one?",
             a=["It stops calls to a failing dependency after a failure threshold: open (fail fast), half-open (trial), closed (normal).", "It protects your threads and queues from piling up behind timeouts and gives the dependency room to recover; pair it with fallbacks."],
             follow=["How does it relate to retries?"], mistakes=["Retrying aggressively into a failing service."],
             angle="Google-style: candidates commonly report this as a follow-up to a design question about a dependency failing; reported by candidates, not official."),
        dict(q="Why use percentiles for latency instead of the average?",
             a=["A few very slow requests barely change the mean but dominate the experience of the users who hit them.", "p95 and p99 show the tail; at scale 1 percent is a lot of people, and in a request that fans out to many backends the slowest backend decides the response time."],
             follow=["Why can't you average p99 across servers?"], mistakes=["Alerting on the mean."]),
        dict(q="Your service is down. How do you find out, and how fast?",
             a=["Detection should come from monitoring (golden signals, synthetic checks), not from customers: alert on user-visible symptoms with clear thresholds.", "On-call receives the page, mitigates first (rollback, failover, flag off), then diagnoses with logs, metrics and traces.", "Afterwards a blameless postmortem with owned actions."],
             follow=["How do you reduce time to detect and time to recover?"], mistakes=["Alerting on causes (CPU) rather than symptoms (errors, latency)."]),
    ],
    selftest=[
        ("How much downtime a year is 99.99% availability?", "About 52 minutes."),
        ("Three 99.9% services in series give what availability?", "About 99.7%."),
        ("What is the availability of two independent 99% servers in parallel?", "99.99%."),
        ("What do RPO and RTO measure?", "Acceptable data loss in time, and acceptable downtime."),
        ("What does a canary deployment do?", "Releases to a small share of traffic first and rolls back automatically if health is worse."),
        ("What states does a circuit breaker have?", "Closed, open and half-open."),
        ("Name the four golden signals.", "Latency, traffic, errors, saturation."),
        ("Why is the mean a poor latency measure?", "It hides the slow tail that a minority of users experience."),
    ],
    recall=[
        ["nines", "99.99% = 52 minutes a year"],
        ["series vs parallel", "multiply availabilities / multiply failures"],
        ["failure domain", "copies must fail independently"],
        ["RPO / RTO", "lost data / lost time"],
        ["canary", "limit the blast radius, roll back automatically"],
        ["circuit breaker", "fail fast, test recovery"],
        ["golden signals", "latency, traffic, errors, saturation"],
        ["p99", "what the slowest 1 percent feel"],
    ],
    sources=[
        dict(title="AWS Well-Architected Framework: Reliability pillar", url="https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html", use="Design principles for reliable workloads, including DR strategies", license="Copyright Amazon; read online", how="Link only"),
        dict(title="Google SRE book: Monitoring Distributed Systems", url="https://sre.google/sre-book/monitoring-distributed-systems/", use="The four golden signals and alerting philosophy", license="CC BY-NC-ND 4.0 (no derivatives)", how="Link only; nothing copied"),
        dict(title="Martin Fowler: Circuit Breaker", url="https://martinfowler.com/bliki/CircuitBreaker.html", use="The pattern explained simply", license="Copyright Martin Fowler; read online", how="Link only"),
        dict(title="Martin Fowler: Feature Toggles", url="https://martinfowler.com/articles/feature-toggles.html", use="Kinds of flags and how to manage them", license="Copyright Martin Fowler; read online", how="Link only"),
    ],
    plan=[
        "**Hour 1:** availability and the nines; compute the availability of a system you know.",
        "**Hour 2:** redundancy, zones and regions; then Lab 1.",
        "**Hour 3:** disaster recovery; write an RPO and RTO for three kinds of product.",
        "**Hour 4:** safe deployments; run the canary simulation with other error rates.",
        "**Hour 5:** resilience patterns; read the breaker output line by line.",
        "**Hours 6 and 7:** observability and Lab 2, then interview answers out loud (failure, blast radius, detection, recovery) and the self-test.",
    ],
)
