"""Systems Mastery S27: design warm-ups (deep version: URL shortener, IDs, key-value store, pastebin, rate limiter, presenting)."""
from sys_warm2_a import LESSONS_A
from sys_warm2_b import LESSONS_B, TAIL
from sys_design_warmups import MODULE as OLD

MODULE = dict(
    id="dw",
    deep=True,
    title="Design warm-ups: five classic problems, worked end to end",
    lead="Five classic problems, each answered the way a strong candidate would: requirements, numbers, API, data, architecture, deep dive, failure and trade-offs, with the key mechanism run for real. You will measure the capacity and collisions of a URL shortener, generate and decode Snowflake IDs and see what random keys do to a B-tree, build and crash a key-value store, deduplicate and expire a pastebin, and watch a naive rate limiter over-admit while an atomic Redis script holds the line. The last lesson is about presenting all of this in 45 minutes.",
    time="9 to 11 hours",
    why=[
        "These five problems are the vocabulary of system design interviews. Each one is small enough to finish in 45 minutes and rich enough to show whether you reason from requirements and numbers or recite diagrams.",
        "Each hides one real mechanism: collisions and the birthday paradox, clocks and index locality, write-ahead logs and recovery, content addressing and expiry, atomic updates under concurrency. Running them makes the mechanism something you have seen, not something you remember.",
        "Presentation is half the score. The same knowledge produces very different outcomes depending on structure, pacing, numbers and how you handle trade-offs and challenges.",
    ],
    outcomes=[
        "Design a URL shortener with estimates, a collision-free code scheme, caching, redirects and asynchronous analytics.",
        "Design a Snowflake-style ID generator, handle clocks and machine ids, and explain index locality of random versus ordered keys.",
        "Design a key-value store: WAL, memtable, sorted files, tombstones, compaction, recovery, partitioning and replication.",
        "Design a pastebin with metadata and blob separation, content addressing, expiry sweeps and caching.",
        "Design a distributed rate limiter with atomic Redis scripts, hot-key handling and failure behaviour.",
        "Pace and structure a 45-minute design interview and state trade-offs clearly.",
    ],
    before=[
        "The estimation module (S15), caching (S17), scaling data (S19) and APIs (S23) help. Python 3, SQLite, curl and Redis run the experiments.",
        "Install the real tools: `sudo apt install redis-server python3 curl` (the Docker lab image has them). You do **not** need root: Redis runs privately on a high port and stops itself; everything else is plain Python.",
        "Run each lesson's commands in order; the rate limiter lesson builds its own small Redis client. Timings depend on your machine; the shapes match.",
    ],
    env=["The scratch folder is `~/warm` (created by the first command)."],
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
