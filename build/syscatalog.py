"""Catalog of the Systems Mastery course: tracks and modules (live or planned).

A module is live when its content module (the name in the last column) exists and defines MODULE.
Order here is the learning order. See docs/COURSE2_PLAN.md.
"""

TRACKS = [
    ("Foundations", "Linux, Git, networking and containers: the toolbox every engineer uses daily."),
    ("Troubleshooting", "Debugging method, performance triage, deep tools, playbooks, reliability practice and real outages."),
    ("System design core", "Estimation, scaling blocks, data, distributed systems, architecture and reliability."),
    ("Design problems", "Full walkthroughs of classic interview designs, with numbers, diagrams and trade-offs."),
    ("Interview and career", "Behavioural interviews, role playbooks and mock drills."),
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
    ("S15", "S15_design_method_estimation", "The design method and estimation", "Requirements, back-of-envelope math, latency numbers and a repeatable framework.", 3, None),
    ("S16", "S16_scaling_building_blocks", "Scaling building blocks", "Load balancing, caching, CDN, reverse proxies and queues.", 3, None),
    ("S17", "S17_data_storage", "Data storage", "SQL and NoSQL, indexes, replication, sharding, consistent hashing, transactions.", 3, None),
    ("S18", "S18_distributed_systems", "Distributed systems essentials", "CAP and PACELC, consistency, consensus, clocks, retries, idempotency.", 3, None),
    ("S19", "S19_architecture_api_patterns", "Architecture and API patterns", "Microservices, events, CQRS, sagas, REST and gRPC, rate limiting, auth.", 3, None),
    ("S20", "S20_designing_for_reliability", "Designing for reliability", "Availability math, multi-region, disaster recovery, safe deployments, observability.", 3, None),
    ("S21", "S21_design_warmups", "Design warm-ups", "URL shortener, pastebin, rate limiter, ID generator, key-value store.", 4, None),
    ("S22", "S22_feeds_chat_notifications", "Feeds, chat and notifications", "News feed, messaging and notification systems.", 4, None),
    ("S23", "S23_media_storage_search", "Media, storage and search", "Video streaming, file sync, autocomplete and web crawling.", 4, None),
    ("S24", "S24_location_money_inventory", "Location, money and inventory", "Ride hailing, payments ledger, ticketing, metrics monitoring, ad click aggregation.", 4, None),
    ("S25", "S25_behavioural_interviews", "Behavioural interviews", "Amazon Leadership Principles, Google-style questions, STAR stories.", 5, None),
    ("S26", "S26_role_playbooks", "Role playbooks", "SDE, SRE and DevOps loops, NALSD practice and troubleshooting drills.", 5, None),
    ("S27", "S27_mock_interviews_plans", "Mock interviews and plans", "Drills, mock rounds and 12-week plans.", 5, None),
    ("S28", "S28_ai_ml_systems_design", "AI and ML systems design", "Retrieval, model serving and the trade-offs behind them (advanced).", 6, None),
    ("S29", "S29_low_level_design", "Low-level design", "Object-oriented design, SOLID, patterns and classic LLD interview problems. The last module of the course.", 6, None),
]
