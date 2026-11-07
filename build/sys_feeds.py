"""Systems Mastery S28: feeds, chat and notifications (reference module behind the news feed, chat and notification pages)."""
from sys_feeds_a import LESSONS_A
from sys_feeds_b import LESSONS_B, TAIL

MODULE = dict(
    id="fd",
    deep=True,
    title="Feeds, chat and notifications",
    lead="Three of the most common product designs, with their key mechanisms run for real: fan-out cost on a skewed follower graph and on real Redis, a chat store with server-assigned sequence numbers, idempotent sends and offline sync, server-sent events pushing messages over one open connection, presence that expires by itself, and a notification pipeline that collapses a thousand likes into one message.",
    time="7 to 9 hours",
    why=[
        "Feeds, messaging and notifications are where scale meets product: the data is simple, the volume is enormous and the user experience (fresh, ordered, not annoying) is the whole point.",
        "Each hides one decisive trade-off: where to pay for fan-out, who owns ordering, and how to restrain volume. Running them makes the trade-off concrete.",
        "They are among the most commonly reported questions in system design interviews.",
    ],
    outcomes=[
        "Design a news feed with fan-out on write, on read and the hybrid, with numbers.",
        "Design a chat system with per-conversation ordering, idempotent sends, offline sync and real-time push.",
        "Design presence and a notification pipeline with deduplication, collapsing and priorities.",
    ],
    before=["The caching (S17), queues (S20) and scaling data (S19) modules help. Python 3, Redis and curl run the experiments."],
    env=["The scratch folder is `~/feed` (created by the first command that needs it)."],
    lessons=LESSONS_A + LESSONS_B,
    labs=[],
    cases=[],
    cheat=TAIL["cheat"],
    interview_intro=TAIL["interview_intro"],
    interview=TAIL["interview"],
    selftest=TAIL["selftest"],
    recall=TAIL["recall"],
    sources=TAIL["sources"],
    plan=TAIL["plan"],
)
