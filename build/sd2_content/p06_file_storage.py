"""Problem 6: Design file storage and sync."""
import sd2kit as k
from sd2 import scen, figure_of

STRIP = k.strip([
    {"title": "One edit", "kind": "warn",
     "scene": lambda cx, cy, w: k.phone(cx - 40, cy - 6, None, "warn") + k.badge(cx + 34, cy - 4, "deck.pptx 1 GB", "warn"),
     "caption": "Ana fixes one typo in a 1 GB presentation. The simple sync tool uploads all 1 GB again."},
    {"title": "Two devices", "kind": "bad",
     "scene": lambda cx, cy, w: k.phone(cx - 44, cy - 6, "laptop", "bad") + k.phone(cx + 44, cy - 6, "phone", "bad") + k.alert(cx, cy - 2, None, "bad"),
     "caption": "She also edited it on her phone on the train. Which copy wins? Someone loses work."},
    {"title": "Pieces and versions", "kind": "ok",
     "scene": lambda cx, cy, w: k.badge(cx - 50, cy - 20, "chunk A", "ok") + k.badge(cx + 50, cy - 20, "chunk B", "ok") + k.badge(cx - 50, cy + 12, "chunk C", "ok") + k.badge(cx + 50, cy + 12, "chunk C2", "warn"),
     "caption": "Cut files into chunks and name each by its hash. Only the changed chunk travels, and both versions are kept."},
], "From whole files to chunks", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


DESIGN = k.figure(720, 260, [
    k.phone(60, 60, "device", "acc"), k.flow(90, 60, 170, 60, "acc", "1 chunks + hashes"),
    k.server(206, 60, "sync API", "acc"), k.flow(236, 60, 316, 60, "acc", "2 which are new?"),
    k.database(356, 60, "metadata", "acc", "file to chunk list"),
    k.flow(206, 98, 206, 160, "ok", "3 upload new chunks"),
    k.cloud(206, 186, "block store", "ok", "erasure coded"),
    k.queue(560, 60, "change log", "acc"), k.flow(390, 60, 512, 60, "acc", "4 append"),
    k.phone(560, 190, "other device", "ok"), k.flow(560, 100, 560, 160, "ok", "5 notify and pull"),
    k.note(400, 246, "Metadata is small and strongly consistent. Blocks are large, immutable and cheap.", ""),
], "File storage and sync design", None)

DATA = dict(
    time="30 minutes",
    seen_at="A common storage design question",
    tagline="Two stores in one: a tiny database that must never be wrong, and a giant blob store that must never lose a byte.",
    story=dict(
        title="The one typo that cost a gigabyte",
        paras=[
            "ShopKart's designers share large product catalogues, some of them a gigabyte. The team first builds sync the obvious way: when a file changes, upload the new file. A designer fixes a typo on the train, and her phone spends the whole commute uploading one gigabyte over a poor connection. Worse, a colleague edited the same file the same hour, and one of the two edits vanishes.",
            "So the question is a real one. How do you build something like Dropbox or Google Drive, where only the changed part travels, a dropped connection resumes, many devices stay in step, and nothing is ever lost?",
        ],
        strip=STRIP),
    requirements=["Functional: upload, download, edit files from several devices; devices sync automatically; share files; keep version history. Non-functional: never lose data (durability above all), upload only what changed, resume after a dropped connection, and show a consistent view of each folder."],
    numbers=[
        ("Users and storage (assumption)", "100 million users with 2 GB each on average is **200 PB** of logical data. These inputs are assumptions chosen for the arithmetic."),
        ("Replication versus erasure coding", "Three full copies would need 600 PB. A 10+4 erasure code uses 1.4 times the space: **280 PB**. The recorded experiment shows the idea with 4+1 fragments at 1.25 times, and rebuilds a lost fragment."),
        ("Change rate (assumption)", "If each user changes files twice a day, that is 200 million syncs a day, about **2,300 per second**. Most are small edits, so chunk level sync saves most of the bytes."),
        ("Chunk size (assumption)", "At 4 MB chunks, a 1 GB file is 256 chunks. A one typo edit changes 1 chunk, so about 4 MB travels instead of 1 GB."),
        ("Metadata versus data", "Metadata (names, folders, chunk lists) is tiny, a few hundred bytes per file, but every operation touches it. Data is huge and touched rarely. Keep them in different systems."),
    ],
    numbers_try=[("sp", 1, 0, 0, "Chunks, hashes and erasure coding, measured")],
    design_figure=DESIGN,
    design=[
        ("Cut files into chunks and name them by hash", "The client splits the file into chunks and computes a hash (a short fingerprint) of each one. The chunk's hash is its name, so identical chunks have identical names. Upload then asks: which of these names do you not have yet?",
         _small([k.badge(80, 30, "chunk 1  h:9f2", "acc"), k.badge(80, 58, "chunk 2  h:41c", "acc"), k.badge(80, 86, "chunk 3  h:7ab", "acc"), k.flow(160, 58, 250, 58, "acc", "ask"), k.server(286, 54, "sync API", "acc"), k.flow(316, 54, 400, 54, "ok", "need h:41c"), k.badge(480, 54, "upload 1 of 3", "ok")], "Chunks by hash", h=116)),
        ("Upload with a resume point", "The client uploads chunks in parts. If the link drops, it asks the server how many bytes arrived and continues from there. A final commit call swaps the file's chunk list in one atomic step, so nobody sees half a file.",
         _small([k.phone(60, 48, None, "acc"), k.flow(88, 48, 190, 48, "acc", "parts"), k.cloud(230, 46, "block store", "ok"), k.flow(264, 48, 380, 48, "warn", "drop", dash=True), k.badge(450, 30, "have 2,000,000 B", "warn"), k.badge(450, 62, "resume from there", "ok")], "Resumable upload")),
        ("Metadata keeps the order of events", "The metadata database stores each file's current chunk list and a version number. Every change also gets a place in a per-user change log. This log is what other devices read to learn what happened.",
         _small([k.server(70, 48, "sync API", "acc"), k.flow(100, 48, 190, 48, "acc", "commit"), k.database(230, 46, "metadata", "acc"), k.flow(260, 48, 350, 48, "acc", "append"), k.queue(400, 48, "change log", "acc"), k.note(540, 52, "ordered per user", "")], "Metadata and change log")),
        ("Other devices pull the changes", "A device keeps a long poll or a push channel open. When the log has news, it fetches the changed file entries, then downloads only the chunks it does not already have. If two edits clash, keep both and mark one as a conflicted copy.",
         _small([k.queue(70, 48, "change log", "acc"), k.flow(116, 48, 210, 48, "ok", "news"), k.phone(250, 48, "device B", "ok"), k.flow(278, 48, 380, 48, "ok", "new chunks"), k.cloud(430, 46, "block store", "ok"), k.note(560, 52, "clash: keep both", "warn")], "Pull changes")),
    ],
    hard_title="The hard part: never lose data, and keep devices consistent",
    hard_paras=[
        "Durability comes from the blocks. Erasure coding splits a chunk into fragments plus parity pieces spread over disks and zones. Any few can fail and the chunk is rebuilt. A background scrubber reads blocks and checks the hashes, because disks rot quietly. Deduplication falls out for free: a chunk with a known hash is never stored twice (be careful across users, since it can reveal that someone else already has a file).",
        "Consistency comes from the metadata. The chunk list and the change log must be strongly consistent, so keep them in a sharded relational database or a consensus based store, shard by user, and commit each change in one transaction. The classic mistake is to put file bytes and file records in the same system: one needs cheap scale, the other needs strict correctness.",
    ],
    **{"try": [("sp", 1, 0, 1, "Resume after a drop, then a ranged read"), ("dw", 3, 0, 0, "Content addressing saves space, measured")]},
    scale=[
        ("Hot shared folder", "Thousands of people edit one shared folder, and one metadata shard takes all the writes. Batch change log appends and cache read views; as a last resort split by sub folder.", ""),
        ("A zone or disk dies", "Erasure coding across zones rebuilds lost fragments. Budget repair bandwidth so rebuilding does not starve normal traffic.", "ok"),
        ("A bug uploads garbage", "Hashes are verified on upload and again on read. Versioning means a bad write can be rolled back to the previous chunk list.", ""),
        ("Orphan chunks", "Deleted files leave unreferenced chunks. A garbage collector counts references, waits a safe delay, then deletes.", ""),
        ("Privacy and deduplication", "Cross user deduplication can leak whether a file exists. Dedupe inside an account, or require proof the client holds the file before linking it.", "bad"),
    ],
    scenario=scen("sp", 1),
    who="A common storage question: reported by candidates, not official.",
    real=[
        dict(company="Dropbox", text="Dropbox describes **Magic Pocket**, the storage system it built in house to hold file data as immutable blocks, with the file and folder records kept separately.", url="https://dropbox.tech/infrastructure/inside-the-magic-pocket", source="Dropbox Tech: Inside the Magic Pocket"),
    ],
    recap=dict(
        points=["Two systems: small strongly consistent metadata, huge immutable blocks.",
                "Cut files into chunks named by hash: only new chunks are uploaded (1 of 10 in the recorded run).",
                "Resumable upload: ask how many bytes arrived, then continue from there.",
                "Erasure coding gives durability at 1.4 times the space (10+4) instead of 3 times.",
                "A per user change log tells other devices what to pull.",
                "Conflicts keep both copies; deleted chunks are removed by a careful garbage collector."],
        quick=[("Why name chunks by their hash?", "Identical content has an identical name, so duplicates are never stored or uploaded twice and corruption is easy to detect."),
               ("Why not three full copies?", "That costs 3 times the space; erasure coding such as 10+4 survives more failures for 1.4 times."),
               ("How does a second device learn about a change?", "It reads the per user change log, then downloads only the chunks it lacks.")]),
    deeper=[("Object storage and blobs", "S21_search_blob_special_stores.html#l2"), ("Pastebin and content addressing", "S27_design_warmups.html#l4"), ("Replication and quorums", "S22_distributed_systems.html#l3")],
)
