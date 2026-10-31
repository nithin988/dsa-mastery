# System design curriculum: audit and redesign

Written after the first system design modules (S15 to S21) were reviewed and judged **informative but not teaching**: sections felt small, topics read like lists of facts, and interview questions were mentioned, not worked through. This document records what a senior engineer wants a junior to be able to do, what was wrong with the first version, and the redesigned course.

## 1. The goal

A person who finishes the system design part should be able to:

1. Take any vague product request and turn it into requirements, numbers and a first design, in a calm repeatable way.
2. Explain **how each building block really works inside** (not just its name), what problem it solves, what problem it creates, and how it fails.
3. Follow one request through the whole system, and say where time goes and what breaks.
4. Reason about trade-offs with numbers, and defend or change a design when challenged.
5. Solve the classic design problems from scratch and explain the choices out loud.
6. Use real tools (nginx, HAProxy, Redis, PostgreSQL, tcpdump) well enough to check a claim instead of trusting it.

## 2. What research says about learning this

Sources reviewed: the System Design Primer, open-source system design courses, and the published guidance of interview-preparation sites (vendor sites, so used only where several agree).

- **Request flow is the backbone.** Beginners understand a system once they can follow one request from the client to the data and back.
- **Learn the problem, not the product.** For every component, learn the problem it solves *and the problem it creates*. Memorising reference architectures does not transfer.
- **Fundamentals, then patterns, then practice.** Building blocks first, then design problems, then timed practice.
- **Worked examples beat passive reading,** provided the example shows the *reasoning*, not only the answer.
- **Estimation and trade-offs are the skill being graded.** Numbers justify the design; naming the cost of each choice shows seniority.

## 3. Audit of the first version

| Finding | Effect on the learner |
|---|---|
| Each lesson about 300 visible words with one animation | A fact list: the learner cannot rebuild the idea alone |
| Several topics squeezed into one module (load balancing, caching, CDN and queues in one; SQL, NoSQL, replication, sharding and transactions in one) | None of them deep enough to be useful |
| Experiments were Python simulations of ideas | Good for intuition, but not what an engineer meets at work |
| Interview content was a list of questions with outline bullets | The learner sees the question but not how to think towards the answer |
| One lesson per step in the reader, plus seven tiny wrap-up steps | "Next section" for very little content |
| Missing topics: security, search and blob storage, proxies and gateways, real-world architectures, infrastructure systems (cache, queue, scheduler), observability depth | Gaps interviewers do probe |

## 4. The redesigned course (system design part)

**Part A. Think like a designer**
- S15 The design method and estimation
- (Foundations, already built) S01 how programs run, S07 networking (rebuilt in the new style)

**Part B. Building blocks** (each one: why it exists, how it works inside, a flow diagram, real tool experiments with annotated output, failure modes, trade-offs and a decision guide, worked interview scenarios)
- S16 Load balancers, proxies and gateways (real: nginx, HAProxy)
- S17 Caching and CDNs (real: Redis, memcached, HTTP caching)
- S18 Relational databases in depth (real: PostgreSQL: indexes, plans, transactions, isolation)
- S19 Scaling data: replication, sharding and NoSQL (real: replication lag, consistent hashing)
- S20 Queues, streams and asynchronous work
- S21 Search, blob storage and specialised stores
- S22 Distributed systems essentials
- S23 APIs and service communication
- S24 Architecture patterns: monoliths to events
- S25 Security for system design
- S26 Designing for reliability and operations

**Part C. Design problems** (each one worked end to end with the four-step method, numbers, API, data model, diagram, two deep dives, bottlenecks, failure cases and what interviewers push on)
- S27 Warm-ups: URL shortener, pastebin, rate limiter, ID generator, key-value store
- S28 Feeds, chat and notifications
- S29 Media, files and streaming
- S30 Search, crawling and analytics pipelines
- S31 Maps, bookings, commerce and payments
- S32 Infrastructure systems: distributed cache, queue, scheduler, metrics

**Part D. Real systems and interviews**
- S33 How real systems are built (public architecture write-ups, with sources)
- S34 The interview playbook: approach, communication, behavioural, level expectations
- S35 Role playbooks and mock drills

**Extensions (last)**
- S36 AI and ML systems design
- S37 Low-level (object-oriented) design

Around this sit the unchanged Linux, Git and troubleshooting modules (S01 to S14), including the networking, performance and debugging skills that system design rests on.

## 5. The blueprint every lesson must follow

1. **Situation:** a concrete problem a learner can picture.
2. **Mental model and analogy:** plain words first.
3. **The picture:** a flow or sequence diagram of one request (not a decoration).
4. **How it works, step by step:** numbered, each step says what happens and why.
5. **Real tool, real output:** a command run on the real system, with a table that explains every line of the output.
6. **How it fails:** the symptoms, how you notice them, how to fix them.
7. **Trade-offs and choosing:** when to use it, when not, what it costs.
8. **Interview in practice:** a worked scenario: the question, what to clarify and why, the reasoning step by step, a strong spoken answer, follow-ups with answers, common slips.
9. **Quick check and traps.**

Modules also keep: a lab with an automatic check, a cheat sheet, a self-test and a one-line recall list.

## 6. What stays honest

- Output marked real was recorded on real Linux with the real tool; outputs that vary (timings, addresses) are marked as such.
- Company-specific interview details are labelled as reported by candidates, not official.
- Where a tool cannot be run safely here (for example a multi-region cloud failover), the output is labelled illustrative.

## 7. Build order

Rebuild or create in this order, one module at a time, each verified and pushed:
S16, S17, S18, S19, S20 (the building blocks learners ask about most), then S22 (deepen), S23 and S24, S25, S26 (deepen), S21, then Part C (S27 deepened, S28 to S32), then S33 to S35, then S08, S13, S14 (Foundations and Troubleshooting leftovers), then S36 and S37.

Until a new module exists, the older overview module stays live in its slot and is replaced when the deeper modules are ready.
