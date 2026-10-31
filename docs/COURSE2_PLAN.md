# Course 2 plan: Systems Mastery (Linux, Git, troubleshooting, system design, interviews)

Status: **M0 and M1 built and live** (hub, left rail, S02 to S06: Linux and Git, 15 verified labs). M2 onwards not started. Written 2026-10-31 after research. Companion to the DSA course (19 topics, live).

## 1. What we are building and for whom

A second course on the same site, built the same way as DSA: one topic at a time, tested, pushed after each. A learner who finishes it should be able to:

1. Work fluently in a Linux shell and in Git, including getting out of trouble.
2. Debug and troubleshoot a misbehaving system with a method, not a command dump.
3. Run a system day to day: monitoring, incidents, postmortems.
4. Design large systems in an interview (and at work) with numbers, trade-offs and failure modes.
5. Handle the interview formats of large companies (Amazon, Google and similar) for three roles: software engineer, SRE / systems engineer, DevOps / cloud.

The research showed these are really **three different interview loops**, so the course is built as shared foundations plus role paths:

| Role | What the loop tests (per public sources) | Course path |
|---|---|---|
| SDE (Amazon, Google, others) | Open-ended system design (about 45 min), trade-offs, clear communication. Amazon also probes how you would operate the system and judges against its Leadership Principles. Google asks for scope first and expects distributed-systems basics even at L4. | Tracks 1 (light), 3, 4, 5 |
| SRE / systems engineer (Google style) | Linux and UNIX internals, networking, troubleshooting, coding, and **NALSD** (non-abstract large system design: design with real numbers). | Tracks 1, 2, 3, 5 |
| DevOps / cloud | Linux, Git, containers, CI/CD, incident response, reliability. | Tracks 1, 2, plus module S08 and S13 |

## 2. Research findings (and how much to trust them)

Verified from primary pages on 2026-10-30:

- **Google SRE book and SRE Workbook:** free to read at sre.google, licensed **CC BY-NC-ND 4.0**. Relevant chapters: Effective Troubleshooting, Emergency Response, Managing Incidents, Postmortem Culture, Monitoring, SLOs, Load Balancing, Handling Overload, Cascading Failures, Distributed Consensus, Data Integrity. The Workbook has a chapter "Introducing Non-Abstract Large System Design".
- **Amazon Builders' Library:** free to read, no open licence; AWS terms forbid copying or derivatives without authorisation. The article list is JavaScript-rendered, so titles must be read in a browser.
- **Pro Git** (git-scm.com/book): free, **CC BY-NC-SA 3.0**. Chapters include Git Branching (with rebasing), Git Tools, Git Internals.
- **Learn Git Branching:** interactive, MIT licensed. **Oh My Git:** open-source game, licence not stated on the page.
- **MIT Missing Semester (2026):** free, **CC BY-NC-SA**. Lectures include shell, command-line environment, debugging and profiling, version control and Git.
- **The Linux Command Line** (Shotts): free PDF, **CC BY-NC-ND 3.0**. **Linux Journey:** free, no licence stated. **OverTheWire Bandit:** beginner wargame.
- **SadServers:** real troubleshooting scenarios; free tier is limited, the full set is paid (about 125 scenarios on Pro).
- **Brendan Gregg:** the USE Method Linux checklist and the Linux performance tools map (images CC BY-SA 4.0; the site text has no stated licence).
- **System Design Primer:** **CC BY 4.0** (adaptation allowed with attribution). Covers performance vs scalability, CAP, load balancers, caches, databases, async, plus 8 worked designs.
- **MIT 6.5840 Distributed Systems (Spring 2026):** lecture notes, papers and labs public; labs must not be published.
- **Google 2015 article "Hiring Site Reliability Engineers"** (USENIX ;login:) exists; the page was verified but its body text could not be read in this session.
- Well-Architected frameworks (AWS, Google Cloud) both list six pillars.

Not verified, so treated as unconfirmed:

- Interview details from prep blogs (rounds, levels, "Googleyness" rubric). Interview-prep sites are commercial; sources disagree (for example one reported 2022 L5 loop had no design round). The course will label such statements "reported by candidates, not official" and point to the company's own pages.
- The exact 10 commands of "Linux Performance Analysis in 60,000 Milliseconds" (the Netflix page blocked fetching). They must be checked against the source before we teach them.
- Licences for Linux Journey, Oh My Git, the latency-numbers gist, and High Scalability content.

**Content policy that follows from the licences:** we **write every explanation ourselves**, and link out to the sources above instead of copying. We never reproduce CC BY-NC-ND/NC-SA text (SRE book, Pro Git, TLCL, Missing Semester) or Amazon Builders' Library text. System Design Primer ideas may be adapted with attribution but we still write our own. For the latency-numbers table we state approximate figures, credit Jeff Dean and Peter Norvig, and say they are about 2012 era. Real outage case studies are summarised in our words with a link to the company's own public postmortem.

## 3. Curriculum: 5 tracks, 29 modules

Sizes: S = smaller than a DSA topic, M = similar, L = larger.

**Track 1: Engineering foundations**
| # | Module | Size |
|---|---|---|
| S01 | How a computer runs programs: processes, threads, memory, files, system calls (the mental model behind everything else) | M |
| S02 | Linux shell fluency: navigation, files, permissions, pipes, redirection, job control | M |
| S03 | Linux text processing and scripting: grep, sed, awk, find, xargs, cut/sort/uniq, bash scripts | M |
| S04 | Linux system internals: process states, signals, memory, filesystems and inodes, users, systemd, journald, cron, /proc | L |
| S05 | Git fundamentals: the snapshot model, staging, branches, merging, remotes, pull requests | M |
| S06 | Git in teams and recovery: rebase, interactive rebase, cherry-pick, reflog, bisect, stash, reset modes, conflicts, workflows (trunk-based vs feature branches) | L |
| S07 | Networking for engineers: TCP/IP, DNS, HTTP/1.1/2/3, TLS, and "what happens when you type a URL" | L |
| S08 | Containers and cloud basics: namespaces and cgroups, Docker, Kubernetes concepts, CI/CD | M |

**Track 2: Debugging and troubleshooting**
| # | Module | Size |
|---|---|---|
| S09 | The debugging method: hypothesis, minimal repro, bisecting, reading logs and stack traces | S |
| S10 | Linux performance triage: the USE method, a first-60-seconds checklist, CPU, memory, disk and network scenarios | L |
| S11 | Deep tools: strace, lsof, ss, tcpdump, perf, core dumps, gdb basics | M |
| S12 | Playbooks: DNS failures, TLS errors, timeouts, port in use, disk full or out of inodes, OOM kills, zombies, too many open files, Kubernetes CrashLoopBackOff | L |
| S13 | Reliability practice: SLIs, SLOs, error budgets, golden signals, alerting, on-call, incident command, blameless postmortems | M |
| S14 | Case files: well-known public outages, what failed, how it was found, the lesson | M |

**Track 3: System design core**
| # | Module | Size |
|---|---|---|
| S15 | The design method: requirements, estimation math, latency numbers, a repeatable framework, how to communicate | M |
| S16 | Scaling blocks: load balancing, caching, CDN, reverse proxy, queues | L |
| S17 | Data: SQL vs NoSQL, indexes, replication, sharding, consistent hashing, transactions and isolation | L |
| S18 | Distributed systems essentials: CAP and PACELC, consistency models, consensus (Raft idea), clocks, retries with backoff and jitter, idempotency, timeouts, circuit breakers | L |
| S19 | Architecture and API patterns: monolith vs microservices, event-driven, CQRS, sagas, REST/gRPC, rate limiting, authentication | M |
| S20 | Designing for reliability and operations: availability math, redundancy, multi-region, disaster recovery, load shedding, safe deployments, observability | M |

**Track 4: Design problems (full walkthroughs)**
| # | Module | Size |
|---|---|---|
| S21 | Warm-ups: URL shortener, pastebin, rate limiter, unique ID generator, key-value store | L |
| S22 | Feeds, chat and notifications | L |
| S23 | Media and storage: video streaming, file sync, search autocomplete, web crawler | L |
| S24 | Location, money, inventory: ride hailing and proximity, payments ledger, ticket booking, metrics monitoring, ad click aggregation | L |
| S25 | *Optional:* low-level (object-oriented) design | M |
| S26 | *Optional:* AI/ML systems design (retrieval, model serving). Sources report such questions are growing; treat as advanced | M |

**Track 5: Interview and career**
| # | Module | Size |
|---|---|---|
| S27 | Behavioural: Amazon Leadership Principles, Google-style structured behavioural questions, STAR stories, communication | M |
| S28 | Role playbooks: SDE vs SRE vs DevOps loops, NALSD practice, troubleshooting-scenario drills | M |
| S29 | Mock interviews, drills and 12-week plans (connected to the planner) | S |

## 4. How every module teaches (the "clear and pro" format)

Each page follows one blueprint so learners always know where they are:

1. **Why it matters**: one real situation (a 3 a.m. page, a failed deploy, an interview question).
2. **Mental model in plain words**, with an everyday analogy, before any jargon.
3. **See it move**: step-by-step animation on the existing stepper engine, with new drawing types we will add: sequence diagrams (TCP handshake, DNS lookup, request through a load balancer), a hash ring (consistent hashing), Git commit graphs (branch, merge, rebase, reset), process and memory views, and architecture box diagrams generated from a small text description so styling stays uniform.
4. **Commands and concepts, line by line**: every command shown with real sample output and an explanation of each flag and each interesting line of output.
5. **Try it yourself (labs)**: scripts that build a deliberately broken situation (a repo with a conflict and a lost commit, a full disk, a runaway process, a port already in use) and a "check" script that tells you whether you fixed it. Git labs run anywhere Git runs; Linux labs run in a throwaway Docker container so nothing touches the learner's machine.
6. **Troubleshooting playbook**: symptom, likely causes ranked, the command to test each, what the output means, the fix, and how to prevent it.
7. **Real-life case** (short): what happened, the root cause, what we learn.
8. **Interview corner**: 5 to 10 real questions with the shape of a strong answer, the follow-ups interviewers use, and common mistakes. Amazon-style angle ("how would you operate this?") and Google-style angle ("show the numbers") called out where they differ.
9. **Cheat sheet** (printable), **self-test**, and **one-line recall** table.
10. **Further reading**: the best free source for each sub-topic, with its licence noted.

Design walkthroughs (Track 4) use a fixed 9-step shape: requirements, back-of-envelope numbers (math shown, assumptions labelled), API, data model, first diagram, deep dives, bottlenecks and failures, trade-offs and alternatives, and "what a senior engineer adds".

### Worked sample A: S10 Linux performance triage (how one page would run)

Scenario: "the server is slow". Animation walks a 60-second checklist (load average, kernel messages, memory, CPU per core, disk, network) and shows how to read each output. Playbooks: high load but idle CPU (waiting on disk), one core pegged, out of memory with the OOM killer, swapping, disk saturated, network errors. Lab: a container with three planted problems to find. Interview corner: "A service's latency doubled, what do you do?", "Load average is 40 on 8 cores, is that bad?", "What is the difference between load and CPU usage?". (The exact checklist commands will be checked against the Netflix/Gregg source before we write it.)

### Worked sample B: S21 URL shortener (how a design page would run)

Requirements and scale assumptions stated; estimation shown (writes per second, reads per second, storage per year, cache size); API; ID generation options compared (hash, counter, pre-generated ranges) with collision and ordering trade-offs; data model; diagram; deep dives (caching hot links, analytics without slowing redirects, abuse); failure modes (cache down, region down); what changes at 10x and 100x; the Amazon follow-up ("how do you deploy and monitor this?") and the Google follow-up ("show me the numbers for one datacenter").

## 5. Quality bar and verification (extends what DSA has)

- **Commands tested for real:** every shell snippet is executed in a Linux container (Docker is installed on this machine; its engine must be started for builds) and output is captured, so sample output on the pages is real, not invented. Git lab scripts are executed and their "check" scripts verified both ways (fails before the fix, passes after).
- **Numbers tested:** estimation math is computed by code in the build, so the page cannot disagree with its own arithmetic.
- **Links checked:** every external link is requested and its status recorded; licences are noted in a sources table.
- **Animations stepped** to their end state in the browser, as with DSA.
- **Claims labelled:** official, widely documented, or reported-by-candidates. No invented statistics about companies.
- **Review pass:** each module is re-read against its primary sources before push.

## 6. Site and product changes needed

- **Course hub:** landing page shows two courses (DSA Mastery, Systems Mastery) with role filters. Existing DSA URLs do not change, so links already shared keep working; new pages live under `systems/`.
- **New page components** in the shared template: mental-model box, lab box, playbook (decision list), case-file box, interview Q&A, sources table, cheat sheet.
- **Planner:** extend to both courses with time estimates per module (reading, labs, drills) and role presets ("SDE in 8 weeks", "SRE in 12 weeks").
- **Later (optional):** a mock-interviewer mode in the coach (bring-your-own Gemini key): it asks a design or troubleshooting question, you answer, and it critiques against a rubric. It would need clear labelling that it is practice feedback.

## 7. Build order (one step at a time, push after each, run verification each time)

| Milestone | Contents | Why this order |
|---|---|---|
| M0 | Course hub, new components, lab runner, diagram renderers, verification harness | Everything else depends on it |
| M1 | S02, S03, S04, S05, S06 (Linux and Git) | Concrete, fully testable, immediately useful; proves the lab format |
| M2 | S01, S07, S09, S10, S11, S12 | Troubleshooting is the differentiator |
| M3 | S15, S16, S17, S18, S19, S20 | Design core, needed before the walkthroughs |
| M4 | S21, S22, S23, S24 | Design walkthroughs |
| M5 | S13, S14, S27, S28, S29 | Reliability, case files, interview playbooks, mocks |
| M6 | S08, S25, S26, mock-interviewer mode | Optional extensions |

## 8. Decisions needed from you (recommended defaults in bold)

1. **Role focus:** build SDE-relevant modules first (M3, M4 early) or Linux, Git and troubleshooting first? Default: **Linux and Git first (M1), as in the table**, because it is testable and what your friends can use immediately.
2. **Scope:** include low-level design (S25) and AI/ML design (S26)? Default: **yes, but last (M6)**.
3. **Labs:** Linux labs need Docker on the learner's machine. Default: **yes, with a plain-text fallback walkthrough for people without Docker**.
4. **Structure and name:** one site with two courses, DSA URLs unchanged, new pages under `systems/`. Default: **keep "DSA Mastery" as a course name and use a neutral umbrella for the site; you pick the umbrella name** (examples: "Mastery", "Interview Mastery").
5. **Company wording:** keep company-specific advice labelled as candidate-reported unless it comes from the company's own pages. Default: **yes**.

## 9. Risks

- **Scope:** 29 modules is large; the milestones let us stop after any milestone with a coherent product.
- **Source drift:** interview formats change; every company claim carries a date and a "reported" label.
- **Licence limits:** several best sources forbid derivatives, which is why we write original explanations and link out.
- **Lab safety:** labs run in disposable containers only; no script touches the learner's own system.
- **Accuracy of troubleshooting advice:** commands differ across distributions and versions; we test on a named distribution and say which.

## 8. Presentation principles (added after reviewing takeUforward and learning-science results)

What takeUforward does that we copy: one clear path with counts per topic (for example 20 modules, 495 problems in three tiers), short lesson pages (a few hundred words, one idea each), a visible progress counter, a planner, notes and revision lists. What the learning research says (worked examples with labelled steps reduce load; examples must sit next to the explanation they illustrate; spaced retrieval beats rereading) shapes the rest.

Our measured starting point: about 7,000 words and 30,000+ px per module, roughly 3 times a takeUforward lesson. Decisions:

1. **Short view by default.** Each command shows its recorded output and one explaining sentence; the rest of the explanation, the part-by-part table, the traps list and the playbooks are folded (`details.more`). The top-bar button "Show all details" opens everything and remembers the choice. Printing opens everything.
2. **Content budget for new modules:** visible prose per lesson of about 300 words, at most 6 commands per lesson, one picture and one animation, everything else folded.
3. **Quick check** (1 to 3 questions with answers hidden) at the end of every lesson (field `quick`), in addition to the module self-test. Back-fill the S02 to S06 lessons.
4. **Hands-on first:** labs stay fully visible; they are the part no other free course offers with automatic checks.
5. **Step-by-step reader (our own design, not a copy of anyone's):** a module is a path of steps (Start here, each lesson, each lab, each wrap-up section). One step is shown at a time (page height drops from about 30,000 px to about 3,500 px); the sidebar and top chips follow along; "Done, next" ticks the lesson and moves on; "All on one page" restores the long view for searching and printing. The URL hash selects the step, so links and the back button work. Implemented in `build/view.js`.
6. **To do:** a "Quick path" filter (Must know lessons and labs only), a streak and "continue where you left off" on the landing page, and a module planner on the Systems landing page like the DSA one.
