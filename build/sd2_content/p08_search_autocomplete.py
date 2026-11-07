"""Problem 8: Design search and autocomplete."""
import sd2kit as k
from sd2 import scen, figure_of

STRIP = k.strip([
    {"title": "Typing is slow", "kind": "warn",
     "scene": lambda cx, cy, w: k.person(cx - 64, cy - 20, 1.1) + k.badge(cx + 20, cy - 36, "camp", "warn") + k.note(cx + 20, cy + 4, "nothing suggested", "warn") + k.note(cx, cy + 56, "customers type full words", "warn"),
     "caption": "ShopKart's search box waits for the full word and a button press. Many customers give up after a typo."},
    {"title": "Suggestions", "kind": "ok",
     "scene": lambda cx, cy, w: k.badge(cx, cy - 46, "cam", "acc") + k.badge(cx, cy - 12, "camera", "ok") + k.badge(cx, cy + 16, "camping stove", "ok") + k.badge(cx, cy + 44, "camp chair", "ok"),
     "caption": "After each key the box shows the five most popular queries that start with what was typed."},
    {"title": "A scan per key", "kind": "bad",
     "scene": lambda cx, cy, w: k.crowd(cx, cy - 56, 5, 26, .66, "bad") + k.database(cx, cy + 6, None, "bad") + k.note(cx, cy + 56, "every key scans the log", "bad"),
     "caption": "The first version scans the whole query log on every keystroke. With thousands of typists the database cannot keep up."},
], "From a plain box to suggestions", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


DESIGN = k.figure(720, 200, [
    k.server(60, 56, "search logs"), k.flow(90, 56, 150, 56, "acc", "daily"),
    k.server(180, 56, "counts", "acc"), k.flow(210, 56, 270, 56, "acc", "build"),
    k.badge(330, 56, "trie snapshot v42", "acc"), k.flow(395, 56, 470, 56, "ok", "publish"),
    k.server(510, 56, "suggest nodes", "ok"), k.note(510, 110, "snapshot loaded in memory", "ok"),
    k.person(60, 150, 1.1), k.flow(86, 150, 170, 150, "ok", "typed: cam"),
    k.cache(210, 150, "edge cache", "ok"), k.flow(238, 150, 440, 150, "ok", "miss: look up prefix"),
    k.flow(510, 120, 510, 128, "ok"), k.badge(560, 150, "top 5 in under 1 ms", "ok"),
], "Autocomplete: offline build, online lookup", None)

DATA = dict(
    time="35 minutes",
    seen_at="Reported for search focused companies",
    tagline="Start with autocomplete, which is a data structure question. Then show how the full search behind it works, because they use two different tools.",
    story=dict(
        title="The search box that waits",
        paras=[
            "ShopKart's search box works like a form: type a whole word, press Enter, wait for results. Support notices the pattern. People type 'camra', get nothing, and leave. A competitor shows suggestions after the first two letters, and customers prefer it.",
            "The team builds suggestions fast: on every keystroke, scan the log of past queries for ones that start with the typed text and sort by popularity. It works for the team of five testing it. On launch day thousands of customers type at once, each typing ten keys a query, and the scan turns into the busiest thing in the system.",
        ],
        strip=STRIP),
    requirements=["Functional: as the user types, show the top five matching popular queries; then, on submit, return ranked product results. Non-functional: suggestions in under 100 ms end to end, ideally a few milliseconds on the server; fresh within about an hour, with trending faster; results can be a little stale; unsafe queries never appear."],
    numbers=[
        ("Assumptions", "100 million daily users, about 10 searches each, about 5 keystrokes per search that trigger a suggestion request. Confirm with the interviewer."),
        ("Suggestion load", "100 million x 10 x 5 is about 5 billion requests a day: roughly **60,000 per second**, peak around 200,000."),
        ("Latency", "Each one must be answered from memory in a few milliseconds, so the lookup cannot touch a database."),
        ("Memory", "Tens of millions of popular queries fit on a few machines when you keep only the top queries and a short list per prefix."),
        ("Full search", "For the search results behind it, assume 5,000 queries per second and 100 million products: a search engine on separate machines, not the product database."),
    ],
    numbers_try=[("ex", 1, 0, 0, "Scanning versus a trie with stored suggestions")],
    design_figure=DESIGN,
    design=[
        ("Count queries offline", "Search events go into a log. A batch job counts how often each query was searched, gives recent searches more weight, and removes unsafe or banned queries. Nothing here runs per keystroke.",
         _small([k.server(60, 48, "search logs"), k.flow(90, 48, 170, 48, "acc", "events"), k.server(200, 48, "counter", "acc"), k.flow(230, 48, 310, 48, "acc", "per query"), k.badge(380, 48, "camera: 9,400", "acc"), k.flow(440, 48, 520, 48, "warn", "filter"), k.badge(580, 48, "safe list", "ok")], "Offline counting")),
        ("A trie that already knows the answer", "A trie is a tree where each step down is one more letter. At every node we store the top five queries below it, worked out ahead of time. Typing 'cam' means walking three steps and reading a ready made list.",
         _small([k.badge(60, 48, "c", "acc"), k.flow(80, 48, 130, 48, "acc"), k.badge(150, 48, "a", "acc"), k.flow(170, 48, 220, 48, "acc"), k.badge(240, 48, "m", "acc"), k.flow(262, 48, 330, 48, "ok", "read list"), k.badge(450, 48, "camera, camp, camping...", "ok")], "Trie with stored suggestions")),
        ("Publish the whole trie as a snapshot", "The builder writes a new immutable trie and the suggestion servers load it into memory, then switch over in one step. If a build fails, servers keep serving the last good snapshot.",
         _small([k.server(70, 48, "builder", "acc"), k.flow(100, 48, 190, 48, "acc", "snapshot v42"), k.server(240, 48, "node 1", "ok"), k.server(340, 48, "node 2", "ok"), k.flow(370, 48, 460, 48, "warn", "build fails?", dash=True), k.badge(540, 48, "keep v41", "warn")], "Snapshot publish")),
        ("The client does half the work", "The page waits for a short pause before asking, cancels the request when the next key arrives, and remembers answers it already got for a prefix. That cuts requests a lot before any server is involved.",
         _small([k.person(50, 48, 1), k.badge(160, 48, "wait 100 ms", "acc"), k.flow(215, 48, 290, 48, "acc", "ask"), k.cache(330, 48, "local cache", "ok"), k.flow(358, 48, 450, 48, "ok", "hit: no call"), k.badge(520, 48, "fewer requests", "ok")], "Client behaviour")),
    ],
    hard_title="The hard part: fresh, fast, and then real search",
    hard_paras=[
        "Autocomplete is fast because the thinking was done earlier. The cost is freshness: the trie reflects the last build. Fix that by blending in a small, fast-updating trending list, and say the trade-off aloud.",
        "Full search is a different tool. An inverted index maps each word to the products that contain it, so a query reads only a few short lists instead of every product. Results are then ranked, commonly with a score called BM25 that rewards rare words and does not let one word repeated many times dominate. The experiments below build both ideas by hand and compare them with a real full text engine.",
    ],
    **{"try": [("sp", 0, 0, 0, "Build an inverted index and rank results by hand"), ("sp", 0, 0, 1, "A real full text index against scanning every row")]},
    scale=[
        ("Memory grows", "Keep only queries above a minimum count and trim the lists. Shard by the first letters of the prefix if one machine cannot hold it.", ""),
        ("Typos", "Add edit distance or phonetic matching as a second step, so 'camra' still suggests 'camera'.", ""),
        ("Unsafe suggestions", "Filter in the builder and also support a quick block list applied at serving time.", "bad"),
        ("The index is stale", "For full search, publish product changes to a queue and update the index within seconds. Rebuild into a new index and switch an alias when the schema changes.", ""),
        ("A shard of the search index is down", "Run each shard with replicas, and return partial results rather than none if a whole shard is missing.", "ok"),
    ],
    scenario=scen("ex", 1),
    who="A classic data structure and design question: reported by candidates, not official.",
    real=[
        dict(company="Elastic", text="A blog post series from Elastic describes BM25, the default text scoring in Elasticsearch, explaining its two main ideas: rare terms matter more, and repeating a term has diminishing returns.", url="https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables", source="Elastic: Practical BM25, Part 2"),
    ],
    recap=dict(
        points=["Autocomplete is about 60,000 requests a second, so every answer comes from memory.",
                "A trie stores the top five suggestions at each node, computed ahead of time.",
                "Build offline from query logs, publish as an immutable snapshot, keep the last good one.",
                "Debounce, cancel and cache on the client to cut requests.",
                "Full search uses an inverted index: word to documents, then ranking such as BM25.",
                "Keep the search index separate from the database and feed it with events."],
        quick=[("Why store top suggestions at every trie node?", "So a lookup is just a walk down the prefix and a read, with no scanning and no sorting."),
               ("What is an inverted index?", "A map from each word to the documents containing it, so a query reads a few lists instead of every document."),
               ("How do you keep suggestions fresh?", "Rebuild the snapshot regularly and blend in a small trending list that updates faster.")]),
    deeper=[("Autocomplete, full lesson", "S29_media_files_streaming.html#l2"), ("Search and the inverted index", "S21_search_blob_special_stores.html#l1")],
)
