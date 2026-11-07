"""Systems Mastery S21: search, blob storage and specialised stores (inverted index, object storage, time series, geospatial)."""
from sys_special_a import LESSONS_A
from sys_special_b import LESSONS_B, TAIL

MODULE = dict(
    id="sp",
    deep=True,
    title="Search, blob storage and specialised stores",
    lead="A relational database is not the right tool for every kind of data. This module builds and measures the structures behind four specialised stores: an inverted index with ranking (and the real SQLite full-text engine), content-addressed chunks, erasure coding and resumable uploads for object storage, delta-of-delta compression and rollups for time series, and a geohash index checked against brute force for proximity search. Each is the answer to \"why not just put it in PostgreSQL?\".",
    time="8 to 10 hours",
    why=[
        "Full-text search, large files, metrics and \"near me\" queries are four of the most common reasons a system grows beyond a single relational database. Each has a data structure that makes it fast and a failure mode that bites when it is misused.",
        "These stores are usually secondary systems fed from a source of truth. Knowing how they are kept in step, what is eventually consistent, and how to rebuild them, is as important as knowing how they work inside.",
        "In interviews they appear as full problems (design search, design photo storage, design monitoring, design ride matching) and as components inside larger designs. Strong answers name the structure, the numbers and the trade-offs.",
    ],
    outcomes=[
        "Explain and build an inverted index with analysis and TF-IDF ranking; use a real full-text engine and design search with a pipeline from the primary database.",
        "Explain object storage: metadata separate from data, chunking and hashing, replication versus erasure coding, presigned URLs, multipart and resumable transfers.",
        "Explain time-series storage: delta-of-delta compression, downsampling with min, max, sum and count, retention tiers, and cardinality limits.",
        "Explain geospatial indexing with geohash cells, the boundary problem and neighbour search; design nearest-driver matching.",
        "Answer search, storage, monitoring and geospatial interview questions with numbers and trade-offs.",
    ],
    before=[
        "The databases (S18), scaling data (S19) and queues (S20) modules help: search indexes and rollups are fed by events. Python 3, curl and Redis run the experiments; SQLite's full-text extension is part of Python's sqlite3.",
        "Install the real tools: `sudo apt install redis-server python3 curl` (the Docker lab image has them). You do **not** need root: servers run privately on high ports and stop themselves.",
        "Run each lesson's commands in order. Timings depend on your machine; the shapes, counts and comparisons match.",
    ],
    env=["The scratch folder is `~/spec` (created by the first command of each lesson)."],
    lessons=LESSONS_A + LESSONS_B,
    labs=[
        dict(kind="linux", script="search-index-read", dir="searchlab", title="Answer search queries from the postings lists",
             goal=["Work out postings lists, an AND query, term frequency and term rarity from a small document set, the way an inverted index does."],
             story=["Before trusting a search engine's ranking you should be able to reproduce it on paper. Six product titles, four questions."],
             tasks=["Read `docs.txt` and `README.txt` in `~/sys-lab/searchlab`.", "List the documents containing `shoes`, and those containing both `red` and `shorts`.", "Find the document where `running` occurs most often and the rarest of four terms.", "Write `key=value` lines into `~/sys-lab/answers-search.txt`."],
             check="Run the check script.", check_cmd="bash ~/sys-lab/check-search-index-read.sh",
             hints=["`grep -w shoes docs.txt | cut -d: -f1` gives the postings list for one term.", "An AND query is the intersection of two lists: `comm -12` on sorted lists does it.", "The rarest term has the shortest postings list: count the lines for each."],
             solution=["shoes appears in documents 1 and 4.", "red is in 1, 3, 6 and shorts in 2, 3, 6: the intersection is 3 and 6.", "Document 1 contains running twice; shoes (2 documents) is the rarest of the four terms."]),
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
