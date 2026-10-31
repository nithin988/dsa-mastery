"""Systems Mastery S24: architecture patterns (monolith to services, strangler migration, event sourcing, CQRS, data ownership)."""
from sys_arch2_a import LESSONS_A
from sys_arch2_b import LESSONS_B, TAIL

MODULE = dict(
    id="ar2",
    deep=True,
    title="Architecture patterns: monoliths, services, events and CQRS",
    lead="Architecture is the set of decisions that are expensive to change. This module tests the popular patterns on real systems instead of slogans: the measured cost of a network hop and the arithmetic of chains of services, a strangler migration with real nginx (path routing, percentage rollout, rollback, automatic fallback), event sourcing with replay, snapshots and time travel, a CQRS read model on PostgreSQL with its consistency gap, and the shared-database trap that breaks a service in production.",
    time="9 to 11 hours",
    why=[
        "Architecture fashions come and go (services, events, CQRS), and teams adopt them without counting the costs. The engineers who matter can say what problem a pattern solves, what it makes harder, and how to adopt it in small reversible steps.",
        "Most architecture disasters are boundary mistakes: a distributed monolith, a shared database, a rewrite that never ships. The cures are cheap if applied early (clear modules, one owner per piece of data, a router in front) and expensive later.",
        "In interviews, \"how would you architect this?\" is judged on reasoning from requirements, honest trade-offs and a migration path, not on naming patterns.",
    ],
    outcomes=[
        "Compare a monolith, a modular monolith and microservices, measure a hop's cost and compute the availability of a service chain.",
        "Migrate incrementally with the strangler pattern: path routing, percentage rollout, shadow traffic, fallback and rollback, on a real proxy.",
        "Explain event-driven design and event sourcing: replay, snapshots, time travel, schema evolution, privacy and when not to use it.",
        "Explain CQRS and read models, demonstrate the consistency gap, and rebuild a read model.",
        "Define service boundaries by capability and data ownership, avoid the shared-database trap, and spot a distributed monolith.",
        "Answer architecture interview questions with reasoning, costs and an adoption path.",
    ],
    before=[
        "The databases (S18), queues (S20) and APIs (S23) modules help: the outbox, idempotency and contracts appear again here. Python 3, nginx and PostgreSQL run the experiments.",
        "Install the real tools: `sudo apt install nginx postgresql python3 curl` (the Docker lab image has them). You do **not** need root or the system services: every demo runs private instances as an ordinary user on high ports or sockets and stops them.",
        "Run the first lesson's commands in order; the strangler lesson creates the rig used by the later ones. Timings depend on your machine; the shapes match.",
    ],
    env=["The rig lives in `~/arch` (created by the strangler lesson). Later commands begin with `. ~/arch/rig.sh` and end by stopping what they started."],
    lessons=LESSONS_A + LESSONS_B,
    labs=[
        dict(kind="linux", script="architecture-smell-read", dir="archsmell", title="Find the architecture smells in a service map",
             goal=["Read a dependency list and find the shared database, the circular dependency, the weakest link and the availability of a long call chain."],
             story=["An architecture review is tomorrow. You are given the list of services, their availability, what each calls and which database each uses. Find what a reviewer would flag."],
             tasks=["Read `services.txt` and `README.txt` in `~/sys-lab/archsmell`.", "Find the database used by more than one service and the services using it.", "Find the circular dependency and the service with the lowest availability.", "Compute the availability of the chain web, api, orders, payments, ledger.", "Write `key=value` lines into `~/sys-lab/answers-arch.txt`."],
             check="Run the check script.", check_cmd="bash ~/sys-lab/check-architecture-smell-read.sh",
             hints=["Group services by the database column and look for a database that appears more than once.", "A cycle: A calls B and B calls A.", "Multiply fractions: 0.9995 x 0.999 x 0.999 x 0.999 x 0.9999, then multiply by 100 and round to two decimals."],
             solution=["`ordersdb` is used by orders, payments and inventory.", "orders and inventory call each other.", "search has the lowest availability (99.50); the chain is about 99.64 percent."]),
    ],
    cases=[],
    cheat=TAIL["cheat"],
    interview_intro=TAIL["interview_intro"],
    interview=TAIL["interview"],
    selftest=TAIL["selftest"],
    recall=TAIL["recall"],
    sources=TAIL["sources"],
    plan=TAIL["plan"],
)
