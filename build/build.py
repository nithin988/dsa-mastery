"""Build every topic page and the landing page.

Usage (from the repo root):  python build/build.py
"""
import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from lib import render_topic, CSS, ICONS, icon, FAVICON, SITE_URL, rail, rail_button  # noqa: E402
from lib_sys import render_module, walk_cmds  # noqa: E402
import sitepages  # noqa: E402
import syscatalog  # noqa: E402
import importlib  # noqa: E402
import arrays  # noqa: E402
import foundations  # noqa: E402
import strings  # noqa: E402
import linked_list  # noqa: E402
import stack_queue  # noqa: E402
import sorting_intervals  # noqa: E402
import recursion_backtracking  # noqa: E402
import bit_math  # noqa: E402
import trees  # noqa: E402
import heaps  # noqa: E402
import graphs  # noqa: E402
import graphs_advanced  # noqa: E402
import tries  # noqa: E402
import greedy  # noqa: E402
import dp1  # noqa: E402
import dp2  # noqa: E402
import adv_ds  # noqa: E402
import design  # noqa: E402
import playbook  # noqa: E402

PLANNER_CORE = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "planner_core.js"), encoding="utf-8").read()
PLANNER_JS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "planner.js"), encoding="utf-8").read()
RAIL_JS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "rail.js"), encoding="utf-8").read()
HOME_JS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "home.js"), encoding="utf-8").read()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (file, title, blurb, topic module or None)
CATALOG = [
    ("01_complexity_foundations", "Complexity and Problem-Solving Method", "Big-O, constraints to complexity, brute force to optimal, interview method", foundations.TOPIC),
    ("02_arrays", "Arrays, Hashing and Searching", "Two pointers, sliding window, prefix sum, Kadane, hashing, binary search, quick select", arrays.TOPIC),
    ("03_strings", "Strings", "Counting, palindromes, windows, KMP, stack parsing, in-place edits", strings.TOPIC),
    ("04_linked_list", "Linked Lists", "Dummy node, reversal, fast/slow, merge, runner gap, LRU design", linked_list.TOPIC),
    ("05_stack_queue", "Stacks, Queues and Deques", "Monotonic stack and deque, BFS, expression evaluation, greedy stack, circular buffers", stack_queue.TOPIC),
    ("06_sorting_intervals", "Sorting and Intervals", "Merge/quick sort, comparators, bucket sort, merge/insert intervals, sweep line, greedy scheduling, cyclic sort", sorting_intervals.TOPIC),
    ("07_recursion_backtracking", "Recursion and Backtracking", "Recursion, subsets, combinations, permutations, duplicates, grid search, N-Queens, pruning", recursion_backtracking.TOPIC),
    ("08_bit_math", "Bit Manipulation and Math", "Bit tricks, XOR, bitmasks, fast power, GCD and primes, digits, formulas", bit_math.TOPIC),
    ("09_trees", "Binary Trees and BST", "Recursion on trees, DFS/BFS, path problems, BST, LCA, construction, tree DP, iterative traversals", trees.TOPIC),
    ("10_heap_priority_queue", "Heaps and Priority Queues", "Heap mechanics, top-K, two heaps, k-way merge, greedy, lazy deletion, Dijkstra", heaps.TOPIC),
    ("11_trie", "Tries", "Trie basics, prefix queries, wildcards, Word Search II, augmented nodes, XOR trie, streams", tries.TOPIC),
    ("12_graphs_traversal", "Graph Traversal", "Representation, DFS, BFS, grids, multi-source BFS, cycles, bipartite, state graphs", graphs.TOPIC),
    ("13_graphs_advanced", "Advanced Graphs", "Topological sort, union-find, Dijkstra, Bellman-Ford, MST, bridges, SCC, Eulerian paths", graphs_advanced.TOPIC),
    ("14_greedy", "Greedy", "Exchange argument, jump games, running balance, stock, two-pass, characters, digits, ratios", greedy.TOPIC),
    ("15_dp_1d_2d", "Dynamic Programming I", "State and transition, take-or-skip, coin change, LIS, grids, string prefixes, matrix DP, state machines, rolling arrays", dp1.TOPIC),
    ("16_dp_advanced", "Dynamic Programming II", "0/1 and multi-dimensional knapsack, LCS, edit distance, palindromic and interval DP, bitmask DP, digit DP, monotonic-deque speed-ups", dp2.TOPIC),
    ("17_advanced_ds", "Advanced Data Structures", "Fenwick tree, segment trees with lazy propagation, sparse table, counting with ranks, binary lifting and LCA, ordered sets, offline queries", adv_ds.TOPIC),
    ("18_design_problems", "Design Problems", "LRU and LFU caches, O(1) random sets, iterators, rate limiters, time-based stores, feeds and leaderboards, frequency stacks, text editors", design.TOPIC),
    ("19_interview_playbook", "Interview Playbook", "The six-step framework, constraints to complexity, pattern selection, tested code templates, edge-case checklist, company-style preparation, 12-week plan", playbook.TOPIC),
]


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


PHASES = [
    ("Foundations", 1, 3),
    ("Core structures", 4, 6),
    ("Recursion and trees", 7, 9),
    ("Heaps, tries and graphs", 10, 13),
    ("Greedy and dynamic programming", 14, 16),
    ("Advanced and interview", 17, 19),
]


def phase_of(num):
    for name, lo, hi in PHASES:
        if lo <= num <= hi:
            return name
    return ""


def distinct_problems(topic):
    return len({lc for p in topic["patterns"] for (lc, *_r) in p["problems"]})


def catalog_json():
    rows = []
    for f, title, _b, topic in CATALOG:
        if not topic:
            continue
        num = f.split("_")[0]
        rows.append({"id": topic["id"], "file": f, "num": num, "title": title, "phase": phase_of(int(num)), "total": distinct_problems(topic)})
    return json.dumps(rows, separators=(",", ":"))


def planner_data():
    """Compact topic data for the study planner (titles, patterns, problem ladders)."""
    rows = []
    for f, title, _b, topic in CATALOG:
        if not topic:
            continue
        num = f.split("_")[0]
        rows.append({
            "id": topic["id"], "file": f, "num": num, "title": title, "phase": phase_of(int(num)),
            "unit": topic.get("unit", "Pattern"),
            "patterns": [
                {"n": i + 1, "title": p["title"], "tier": p["tier"], "hasCode": bool(p["code"]),
                 "problems": [[lc, name, d, slug] for (lc, name, d, slug, _l, _c) in p["problems"]]}
                for i, p in enumerate(topic["patterns"])
            ],
        })
    return rows


def plan_html():
    desc = "Build a realistic DSA study plan from your time, level and the topics you choose, and chat with a plan coach to adjust it."
    icons_json = json.dumps(ICONS, separators=(",", ":"))
    chips = ["I have 8 weeks, 2 hours a day, and I am a beginner", "My interviews are in 4 weeks, make it fast", "Only graphs and dynamic programming", "I fell behind, restart from today", "Why did you trim topics?"]
    chip_html = "".join(f"<button type=\"button\">{html.escape(c)}</button>" for c in chips)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Study planner | DSA Mastery</title>
<meta name="description" content="{desc}"><meta name="theme-color" content="#0f172a">
<meta property="og:type" content="website"><meta property="og:site_name" content="DSA Mastery"><meta property="og:title" content="Study planner | DSA Mastery">
<meta property="og:description" content="{desc}"><meta property="og:url" content="{SITE_URL}plan.html">
<link rel="icon" href="{FAVICON}">
<style>{CSS}</style></head>
<body class="has-rail">
<a class="skip" href="#content">Skip to content</a>
{rail("plan")}
<header class="bar"><div class="bar-in">{rail_button()}<a class="brand" href="dsa.html" aria-label="DSA Mastery home"><span class="logo" aria-hidden="true">DSA</span><b>DSA <span>Mastery</span></b></a>
<nav class="crumbs" aria-label="Breadcrumb"><a href="dsa.html">DSA topics</a>{icon("right")}<span class="cur">Study planner</span></nav>
<button id="b-theme" class="iconbtn" title="Toggle light / dark" aria-label="Toggle light or dark theme">{icon("theme")}</button></div></header>
<main id="content" class="home planner">
<header class="hero"><div class="eyebrow"><span class="tag">Planner</span>Realistic, not aspirational</div>
<h1>Plan your DSA study</h1>
<p class="lead">Tell it how much time you really have and pick the topics. It builds a day-by-day schedule with spaced reviews and weekly checkpoints, trims what does not fit and says so. Chat with the coach to adjust the plan in plain language.</p></header>
<div class="pl-grid">
<div class="pl-col">
<section class="card" aria-labelledby="h-set"><div class="card-h"><h2 id="h-set">1. Your time</h2></div><div class="card-b" id="settings"></div></section>
<section class="card" aria-labelledby="h-top"><div class="card-h"><h2 id="h-top">2. Topics to cover</h2><span id="topics-sum"></span></div><div class="card-b" id="topics"></div></section>
</div>
<aside class="card chat" aria-label="Plan coach">
<div class="card-h"><h2>Plan coach</h2><span id="coach-mode" class="st">Offline mode</span>
<button id="clear-chat" class="btn iconbtn" title="Clear the chat" aria-label="Clear the chat">{icon("reset")}</button>
<button id="key-toggle" class="btn" aria-expanded="false" aria-controls="key-panel" title="Add a Gemini API key">{icon("key")}<span>Key</span></button></div>
<div id="key-panel" class="key-panel" hidden>
<p class="muted">Optional: add your own free Gemini API key for a natural conversation (get one in <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener">Google AI Studio</a>). The key is stored only in this browser and sent only to Google. Each message includes your plan settings and how many problems you have ticked per topic, nothing else.</p>
<input id="key-input" type="password" autocomplete="off" spellcheck="false" aria-label="Gemini API key" placeholder="Paste your Gemini API key">
<label><input type="checkbox" id="key-remember" checked> Remember on this device</label>
<div class="row"><select id="model-select" aria-label="Gemini model"></select><button type="button" id="key-detect" class="btn">Detect models</button></div>
<div class="row"><button type="button" id="key-save" class="btn pri">Save</button><button type="button" id="key-remove" class="btn" hidden>Remove key</button><span id="key-state" class="muted"></span></div>
<p id="key-msg" class="muted" role="status"></p></div>
<div id="msgs" class="msgs" role="log" aria-live="polite" aria-label="Conversation"></div>
<div id="chips" class="chips2">{chip_html}</div>
<form id="composer" class="composer"><textarea id="ask" rows="1" placeholder="Tell me about your time and goals" aria-label="Message to the plan coach"></textarea><button id="send" class="btn pri" type="submit"></button></form>
</aside></div>
<section aria-labelledby="h-plan"><h2 id="h-plan" class="sec-h">3. Your plan</h2><div id="plan-out" aria-live="polite"></div></section>
</main>
<footer class="site-foot"><span>DSA Mastery: free, open study sheets. Your plan and ticks are saved in this browser only.</span><span><a href="dsa.html">All DSA topics</a> · <a href="https://github.com/nithin988/dsa-mastery" target="_blank" rel="noopener">GitHub</a></span></footer>
<script>window.DSA_DATA={json.dumps(planner_data(), separators=(",", ":"))};</script>
<script>(function(){{var IC={icons_json};
{PLANNER_CORE}
{PLANNER_JS}
{RAIL_JS}
}})();</script>
</body></html>
"""


def dsa_html():
    live = [(f, t, b, topic) for f, t, b, topic in CATALOG if topic]
    n_pat = sum(len(tp["patterns"]) for *_x, tp in live)
    n_sim = sum(1 for *_x, tp in live for p in tp["patterns"] if p.get("sim"))
    n_lc = len({lc for *_x, tp in live for p in tp["patterns"] for (lc, *_r) in p["problems"]})
    phases = []
    for pname, lo, hi in PHASES:
        cards = []
        for f, title, blurb, topic in live:
            num = int(f.split("_")[0])
            if not lo <= num <= hi:
                continue
            n = distinct_problems(topic)
            unit = topic.get("unit", "Pattern").lower()
            sims = sum(1 for p in topic["patterns"] if p.get("sim"))
            cards.append(
                f'<article class="tcard" data-file="{f}" data-num="{num:02d}" data-title="{html.escape(title, quote=True)}" data-blurb="{html.escape(blurb, quote=True)}" data-status="new">'
                f'<div class="tcard-h"><span class="no">{num:02d}</span><h3>{html.escape(title)}</h3><span class="st">Not started</span></div>'
                f'<div class="tcard-b"><p>{html.escape(blurb)}</p>'
                f'<div class="meta"><span>{icon("layers")}{len(topic["patterns"])} {unit}s</span><span>{icon("film")}{sims} animations</span><span>{icon("stairs")}{n} problems</span></div>'
                f'<div><div class="meter" aria-hidden="true"><i></i></div><div class="meta" style="margin-top:6px"><span class="solved">0 / {n} solved</span></div></div>'
                f'<div class="act"><a class="btn pri" href="topics/{f}.html">Open{icon("arr-r")}</a>'
                f'<a class="btn" href="topics/{f}.html" download="{f}.html" title="Save this topic as a standalone HTML file">{icon("down")}Download</a></div></div></article>'
            )
        phases.append(
            f'<section class="phase" aria-labelledby="ph-{lo}"><div class="phase-h"><span class="ph">Phase {len(phases) + 1}</span>'
            f'<h2 id="ph-{lo}">{html.escape(pname)}</h2><span>Topics {lo:02d} to {hi:02d}</span></div><div class="grid">{"".join(cards)}</div></section>'
        )
    first = live[0][0]
    desc = "Free pattern-based DSA study sheets for product-company interviews: intuition, step-by-step animations, Java and Python code, complexity, traps and LeetCode ladders. Works offline."
    icons_json = json.dumps(ICONS, separators=(",", ":"))
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DSA Mastery: pattern-based data structures and algorithms</title>
<meta name="description" content="{desc}"><meta name="theme-color" content="#0f172a">
<meta property="og:type" content="website"><meta property="og:site_name" content="DSA Mastery"><meta property="og:title" content="DSA Mastery">
<meta property="og:description" content="{desc}"><meta property="og:url" content="{SITE_URL}">
<link rel="icon" href="{FAVICON}">
<style>{CSS}</style></head>
<body class="has-rail">
<a class="skip" href="#content">Skip to content</a>
{rail("dsa")}
<header class="bar"><div class="bar-in">{rail_button()}<a class="brand" href="dsa.html" aria-label="DSA Mastery home"><span class="logo" aria-hidden="true">DSA</span><b>DSA <span>Mastery</span></b></a>
<span style="margin-right:auto"></span>
<a class="btn" href="plan.html">{icon("cal")}<span class="t-long">Planner</span></a>
<a class="btn" href="https://github.com/nithin988/dsa-mastery" target="_blank" rel="noopener">{icon("ext")}<span class="t-long">GitHub</span></a>
<button class="btn" data-share>{icon("share")}<span class="t-long">Share</span></button>
<button id="b-theme" class="iconbtn" title="Toggle light / dark" aria-label="Toggle light or dark theme">{icon("theme")}</button></div></header>
<main id="content" class="home">
<section class="home-hero">
<div class="hero"><div class="eyebrow"><span class="tag">Free and open</span>Works offline</div>
<h1>Master data structures and algorithms, one pattern at a time</h1>
<p class="lead">Revision sheets built for product-company interviews. Every topic has the intuition, a step-by-step animation, code in Java and Python, complexity, common traps and a ladder of LeetCode problems from easy to hard.</p>
<div class="cta"><a id="cta-start" class="btn pri lg" href="topics/{first}.html"><span>Start with topic 01</span>{icon("arr-r")}</a>
<a id="cta-continue" class="btn lg" href="#" hidden><span>Continue</span>{icon("arr-r")}</a>
<a class="btn lg" href="plan.html">{icon("cal")}<span>Plan my study</span></a>
<button class="btn lg" data-share>{icon("share")}<span>Share with friends</span></button></div></div>
<div class="kpis"><div class="kpi"><b>{len(live)}</b><span>topics in {len(PHASES)} phases</span></div><div class="kpi"><b>{n_pat}</b><span>patterns and chapters</span></div>
<div class="kpi"><b>{n_sim}</b><span>step-by-step animations</span></div><div class="kpi"><b>{n_lc}</b><span>LeetCode problems</span></div>
<div class="kpi wide"><span>Your progress</span><b id="k-pct">0%</b><div class="meter" id="k-meter" role="progressbar" aria-label="Overall progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><i id="k-bar"></i></div>
<span id="k-txt" style="margin-top:8px">0 problems solved (saved in this browser)</span><span id="k-topics" style="margin-top:2px"></span></div></div>
</section>
<section class="how" aria-label="How it works">
<div><b><span class="no">1</span>Learn the idea</b>Read when to use the pattern and why it works, in plain language.</div>
<div><b><span class="no">2</span>Watch it run</b>Step through an animation until the algorithm feels obvious.</div>
<div><b><span class="no">3</span>Practise</b>Write the skeleton from memory, then climb the problem ladder.</div></section>
<div class="tools"><h2 id="path">Learning path</h2><span class="muted" id="count" aria-live="polite"></span>
<label class="search">{icon("search")}<input id="q" type="search" placeholder="Search topics" aria-label="Search topics"></label>
<span class="filters" role="group" aria-label="Filter by progress"><button data-f="all" aria-pressed="true">All</button><button data-f="new" aria-pressed="false">Not started</button><button data-f="doing" aria-pressed="false">In progress</button><button data-f="done" aria-pressed="false">Done</button></span></div>
{"".join(phases)}
<p class="empty" id="empty" hidden>No topics match your search or filter.</p>
</main>
<footer class="site-foot"><span>DSA Mastery: free, open study sheets. Progress is saved in your browser only. <a href="https://github.com/nithin988/dsa-mastery/blob/main/ROADMAP.md">Roadmap</a></span><span><a href="https://github.com/nithin988/dsa-mastery" target="_blank" rel="noopener">GitHub</a></span></footer>
<script>window.DSA_TOPICS={catalog_json()};</script>
<script>(function(){{var IC={icons_json};
{HOME_JS}
{RAIL_JS}
}})();</script>
</body></html>
"""


def load_systems():
    """Rows for every catalog module; live ones carry their MODULE dict."""
    rows = []
    for num, slug, title, blurb, track, modname in syscatalog.MODULES:
        mod = None
        if modname:
            try:
                mod = importlib.import_module(modname).MODULE
            except ModuleNotFoundError as e:
                if e.name != modname:
                    raise
        rows.append({"num": num, "slug": slug, "title": title, "blurb": blurb, "track": track, "module": mod})
    return rows


def sys_catalog_json(rows):
    out = []
    for r in rows:
        m = r["module"]
        if m:
            out.append({"id": m["id"], "file": r["slug"], "num": r["num"], "title": r["title"], "phase": syscatalog.TRACKS[r["track"] - 1][0],
                        "total": len(m["lessons"]) + len(m.get("labs", [])) + 1})
    return json.dumps(out, separators=(",", ":"))


def build_systems():
    rows = load_systems()
    live = [r for r in rows if r["module"]]
    cat = sys_catalog_json(rows)
    for k, r in enumerate(live):
        m = r["module"]
        m["file"] = r["slug"] + ".html"
        m["num"] = r["num"]
        m["track"] = syscatalog.TRACKS[r["track"] - 1][0]
        m["prev"] = (live[k - 1]["slug"], live[k - 1]["title"]) if k else None
        m["next"] = (live[k + 1]["slug"], live[k + 1]["title"]) if k + 1 < len(live) else None
        m["_catalog"] = cat
        m["_n_total"] = len(rows)
        write(os.path.join(ROOT, "systems", r["slug"] + ".html"), render_module(m))
        print("built", r["slug"])
    stat_rows = []
    for r in rows:
        m = r["module"]
        stat_rows.append({**{k: r[k] for k in ("num", "slug", "title", "blurb", "track", "module")},
                          "lessons": len(m["lessons"]) if m else 0, "labs": len(m.get("labs", [])) if m else 0,
                          "sims": sum(1 for L in m["lessons"] if L.get("sim")) if m else 0})
    stats = {"live": len(live), "total": len(rows), "lessons": sum(x["lessons"] for x in stat_rows), "labs": sum(x["labs"] for x in stat_rows),
             "questions": sum(len(r["module"].get("interview", [])) for r in live)}
    write(os.path.join(ROOT, "systems.html"), sitepages.systems_html(stat_rows, cat, stats))
    print("built systems.html")
    # hub
    dsa_live = [(f, t, b, topic) for f, t, b, topic in CATALOG if topic]
    dsa = {"topics": len(dsa_live), "problems": len({lc for *_x, tp in dsa_live for p in tp["patterns"] for (lc, *_r) in p["problems"]}), "catalog": catalog_json()}
    sysc = {"live": len(live), "total": len(rows), "labs": stats["labs"], "catalog": cat}
    write(os.path.join(ROOT, "index.html"), sitepages.hub_html(dsa, sysc))
    print("built index.html (hub)")


def main():
    built = [(f, t, topic) for f, t, _b, topic in CATALOG if topic]
    for k, (f, t, topic) in enumerate(built):
        topic["prev"] = (built[k - 1][0], built[k - 1][1]) if k else None
        topic["next"] = (built[k + 1][0], built[k + 1][1]) if k + 1 < len(built) else None
    cat = catalog_json()
    for f, _t, _b, topic in CATALOG:
        if topic:
            topic["_catalog"] = cat
            topic["_n_topics"] = len(built)
            topic["_phase"] = phase_of(int(f.split("_")[0]))
            write(os.path.join(ROOT, "topics", f + ".html"), render_topic(topic))
            print("built", f)
    write(os.path.join(ROOT, "dsa.html"), dsa_html())
    print("built dsa.html")
    build_systems()
    write(os.path.join(ROOT, "plan.html"), plan_html())
    print("built plan.html")


if __name__ == "__main__":
    main()
