"""Catalog of the Systems Mastery course: tracks and modules (live or planned).

A module is live when its content module (the name in the last column) exists and defines MODULE.
Order here is the learning order. See docs/COURSE2_PLAN.md.
"""

TRACKS = [
    ("Foundations", "Linux, Git, networking and containers: the toolbox every engineer uses daily."),
    ("Troubleshooting", "Debugging method, performance triage, deep tools, playbooks, reliability practice and real outages."),
    ("System design: building blocks", "Estimation, then every building block in depth: balancers, caches, databases, queues, search, distributed systems, APIs, security and reliability."),
    ("System design: worked problems", "Classic designs solved end to end: numbers, API, data, diagram, deep dives, trade-offs and what interviewers push on."),
    ("Real systems and interviews", "How real companies built their systems, and how to explain a design under interview conditions."),
    ("Extensions", "Added last: AI and ML systems design, and low-level (object-oriented) design."),
]

# (num, slug, title, blurb, track index (1-based), content module name or None)
MODULES = [
    ("S01", "S01_how_computers_run_programs", "How a computer runs programs", "Processes, threads, memory, files and system calls: the mental model behind everything else.", 1, "sys_how_computers"),
    ("S02", "S02_linux_shell", "Linux shell fluency", "Navigate, find, read, move and secure files; pipes, redirection, permissions and job control.", 1, "sys_linux_shell"),
    ("S03", "S03_text_processing_scripting", "Text processing and scripting", "grep, sed, awk, find, xargs, sort and uniq, then bash scripts that do real work.", 1, "sys_text_scripting"),
    ("S04", "S04_linux_internals", "Linux system internals", "Process states, signals, memory, filesystems and inodes, users, systemd, logs and /proc.", 1, "sys_linux_internals"),
    ("S05", "S05_git_fundamentals", "Git fundamentals", "The snapshot model, staging, branches, merging, remotes and pull requests.", 1, "sys_git_basics"),
    ("S06", "S06_git_teams_recovery", "Git in teams and recovery", "Rebase, interactive rebase, cherry-pick, reflog, bisect, stash, reset modes and conflict handling.", 1, "sys_git_recovery"),
    ("S07", "S07_networking_for_engineers", "Networking for engineers", "TCP/IP, DNS, HTTP, TLS and what really happens when you type a URL.", 1, "sys_networking"),
    ("S08", "S08_containers_cloud_basics", "Containers and cloud basics", "Namespaces and cgroups, Docker, Kubernetes concepts and CI/CD.", 1, None),
    ("S09", "S09_debugging_method", "The debugging method", "Hypotheses, minimal repros, bisecting, reading logs and stack traces.", 2, "sys_debugging"),
    ("S10", "S10_linux_performance_triage", "Linux performance triage", "The USE method and a first-60-seconds checklist for CPU, memory, disk and network.", 2, "sys_perf_triage"),
    ("S11", "S11_deep_debugging_tools", "Deep debugging tools", "strace, lsof, ss, tcpdump, perf, core dumps and gdb basics.", 2, "sys_deep_tools"),
    ("S12", "S12_troubleshooting_playbooks", "Troubleshooting playbooks", "DNS, TLS, timeouts, full disks, OOM kills, zombies and Kubernetes crash loops.", 2, "sys_playbooks"),
    ("S13", "S13_reliability_practice", "Reliability practice", "SLIs, SLOs, error budgets, alerting, on-call, incident command and postmortems.", 2, None),
    ("S14", "S14_case_files_outages", "Case files: real outages", "Well-known public outages: what failed, how it was found, the lesson.", 2, None),
    ("S15", "S15_design_method_estimation", "The design method and estimation", "Requirements, back-of-envelope math, latency numbers and a repeatable framework.", 3, "sys_design_method"),
    ("S16", "S16_load_balancers_proxies", "Load balancers, proxies and gateways", "Real nginx and HAProxy: algorithms, health checks, zero-downtime deploys, layer 4 versus 7, TLS termination, rate limiting, gateways and highly available balancing.", 3, "sys_load_balancing"),
    ("S17", "S17_caching_and_cdns", "Caching, CDNs and queues (overview)", "Overview of caching, CDNs and queues. Being split into deeper modules S17 (caching and CDNs) and S20 (queues, streams and async work).", 3, "sys_scaling_blocks"),
    ("S18", "S18_data_storage", "Data storage (overview)", "Overview of SQL and NoSQL, indexes, replication, sharding and transactions. Being split into deeper modules S18 and S19.", 3, "sys_data_storage"),
    ("S19", "S19_scaling_data", "Scaling data: replication, sharding and NoSQL", "Replication in practice, partitioning, consistent hashing and choosing a store.", 3, None),
    ("S20", "S20_queues_streams_async", "Queues, streams and asynchronous work", "Message queues, logs and streams, delivery guarantees, ordering, back-pressure and the outbox pattern.", 3, None),
    ("S21", "S21_search_blob_special_stores", "Search, blob storage and specialised stores", "Inverted indexes, object storage, time-series and geospatial stores, and when to use each.", 3, None),
    ("S22", "S22_distributed_systems", "Distributed systems essentials", "CAP and PACELC, consistency, consensus, clocks, retries, idempotency.", 3, "sys_distributed"),
    ("S23", "S23_architecture_api_patterns", "APIs and architecture patterns (overview)", "Overview of REST, events, CQRS, sagas, rate limiting and auth. Being split into deeper modules S23, S24 and S25.", 3, "sys_architecture"),
    ("S24", "S24_architecture_patterns", "Architecture patterns: monoliths to events", "Monolith versus microservices, event-driven design, CQRS, sagas, the outbox and migration patterns.", 3, None),
    ("S25", "S25_security_for_design", "Security for system design", "Authentication, authorisation, TLS and mTLS, secrets, common attacks, DDoS and data protection.", 3, None),
    ("S26", "S26_designing_for_reliability", "Designing for reliability and operations", "Availability math, multi-region, disaster recovery, safe deployments, observability.", 3, "sys_reliability_design"),
    ("S27", "S27_design_warmups", "Design warm-ups", "URL shortener, pastebin, rate limiter, ID generator, key-value store.", 4, "sys_design_warmups"),
    ("S28", "S28_feeds_chat_notifications", "Feeds, chat and notifications", "News feed, messaging, presence and notification systems.", 4, None),
    ("S29", "S29_media_files_streaming", "Media, files and streaming", "Video streaming, file sync and image services.", 4, None),
    ("S30", "S30_search_crawl_analytics", "Search, crawling and analytics pipelines", "Autocomplete, web crawler, log and metrics pipelines.", 4, None),
    ("S31", "S31_maps_bookings_payments", "Maps, bookings, commerce and payments", "Ride hailing, ticketing and double-booking, checkout, payments and ledgers.", 4, None),
    ("S32", "S32_infrastructure_systems", "Infrastructure systems", "Distributed cache, message queue, job scheduler and monitoring system.", 4, None),
    ("S33", "S33_real_world_architectures", "How real systems are built", "Public architecture write-ups from well-known companies, with the lessons and sources.", 5, None),
    ("S34", "S34_interview_playbook", "The interview playbook", "Approach, communication, behavioural questions and level expectations.", 5, None),
    ("S35", "S35_role_playbooks_mocks", "Role playbooks and mock drills", "SDE, SRE and DevOps loops, troubleshooting drills, mock rounds and study plans.", 5, None),
    ("S36", "S36_ai_ml_systems_design", "AI and ML systems design", "Retrieval, model serving and the trade-offs behind them (advanced).", 6, None),
    ("S37", "S37_low_level_design", "Low-level design", "Object-oriented design, SOLID, patterns and classic LLD interview problems. The last module of the course.", 6, None),
]
