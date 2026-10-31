"""Systems Mastery S26: designing for reliability and operations (real nginx canaries, supervisors, metrics, PostgreSQL restores)."""
from sys_rel2_a import LESSONS_A
from sys_rel2_b import LESSONS_B, TAIL
from sys_reliability_design import MODULE as OLD

MODULE = dict(
    id="rd",
    deep=True,
    title="Designing for reliability and operations",
    lead="Reliability is designed in, then proven by testing. This module does the arithmetic of the nines and of failure domains, then runs the mechanisms: a supervisor that restarts a crashing service, an nginx pool that hides a dead server, a page that degrades instead of failing, a real canary that rolls itself back, a feature flag with a kill switch, metrics with percentiles from a live service, a request followed across two services by its id, a database dropped and restored (and a bad backup caught), and an overloaded server that collapses without load shedding.",
    time="9 to 11 hours",
    why=[
        "Every system fails; what separates good ones is that the failures are small, short and survivable. That is a design property, built from redundancy across failure domains, safe deployment, observability, tested recovery and protection from overload.",
        "Most outages follow a change or a feedback loop (retries, queues, cascading timeouts). Engineers who understand deployment safety and overload dynamics prevent the largest class of real incidents.",
        "In interviews \"how would you make this highly available?\" is judged on numbers and mechanisms: the target, the dependencies, the failure domains, the recovery automation and how you would know it works.",
    ],
    outcomes=[
        "Convert nines to downtime, compose availability in series and parallel, and reason about failure domains and N+1 capacity.",
        "Design supervision, health-checked failover and graceful degradation, and test the failure paths.",
        "Release safely with canaries, automatic rollback, feature flags and backward-compatible database changes.",
        "Instrument services with metrics, structured logs and request ids, and diagnose a slow request by percentile and trace.",
        "Define RPO and RTO, restore and verify backups, and design DR; explain overload, load shedding and metastable failure.",
        "Answer reliability interview questions with arithmetic, mechanisms and rehearsed recovery.",
    ],
    before=[
        "The load balancing (S16), scaling data (S19), queues (S20) and distributed systems (S22) modules help. Python 3, nginx and PostgreSQL run the experiments.",
        "Install the real tools: `sudo apt install nginx postgresql python3 curl` (the Docker lab image has them). You do **not** need root: everything runs as an ordinary user on high ports and sockets and stops itself.",
        "Run the first lesson's commands in order: the rig is reused by every later lesson. Timings depend on your machine; the shapes match.",
    ],
    env=["The rig lives in `~/rel`. Every command begins with `. ~/rel/rig.sh` and ends by stopping what it started."],
    lessons=LESSONS_A + LESSONS_B,
    labs=OLD["labs"],
    cases=[],
    cheat=TAIL["cheat"],
    interview_intro=TAIL["interview_intro"],
    interview=TAIL["interview"],
    selftest=TAIL["selftest"],
    recall=TAIL["recall"],
    sources=TAIL["sources"],
    plan=TAIL["plan"],
)
