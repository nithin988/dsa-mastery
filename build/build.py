"""Build every topic page and the landing page.

Usage (from the repo root):  python build/build.py
"""
import html
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from lib import render_topic, CSS  # noqa: E402
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
    ("11_trie", "Tries", "Prefix search, word dictionary, XOR trie", None),
    ("12_graphs_traversal", "Graph Traversal", "Representation, DFS, BFS, grids, multi-source BFS, cycles, bipartite, state graphs", graphs.TOPIC),
    ("13_graphs_advanced", "Advanced Graphs", "Topological sort, union-find, Dijkstra, Bellman-Ford, MST, bridges, SCC, Eulerian paths", graphs_advanced.TOPIC),
    ("14_greedy", "Greedy", "Exchange argument, intervals, scheduling", None),
    ("15_dp_1d_2d", "Dynamic Programming I", "1D/2D DP, coin change, LIS, state definition", None),
    ("16_dp_advanced", "Dynamic Programming II", "Knapsack, LCS/edit distance, bitmask, tree DP", None),
    ("17_advanced_ds", "Advanced Data Structures", "Segment tree, Fenwick tree, sparse table", None),
    ("18_design_problems", "Design Problems", "LRU/LFU, iterators, time-based stores", None),
    ("19_interview_playbook", "Interview Playbook", "Pattern selector, communication, 12-week plan", None),
]


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def index_html():
    cards = []
    for f, title, blurb, topic in CATALOG:
        num = f.split("_")[0]
        if topic:
            n = sum(len(p["problems"]) for p in topic["patterns"])
            meta = f"{len(topic['patterns'])} {topic.get('unit', 'Pattern').lower()}s · {n} problems"
            actions = (
                f'<a class="btn pri" href="topics/{f}.html">Open</a>'
                f'<a class="btn" href="topics/{f}.html" download="{f}.html">⬇ Download</a>'
            )
            cls = "card live"
        else:
            meta = "Coming soon"
            actions = '<span class="soon">Planned</span>'
            cls = "card"
        cards.append(
            f'<div class="{cls}"><div class="num">{num}</div><h3>{html.escape(title)}</h3>'
            f'<p>{html.escape(blurb)}</p><div class="meta">{meta}</div><div class="act">{actions}</div></div>'
        )
    extra = """
.hero{padding:34px 0 8px}.hero h1{font-size:32px;margin:0 0 8px;border:0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px;margin:18px 0}
.card{border:1px solid var(--line);border-radius:12px;padding:14px;background:var(--surf);display:flex;flex-direction:column;opacity:.65}
.card.live{opacity:1;border-color:var(--acc)}
.card h3{margin:2px 0 4px}.card p{margin:0 0 8px;color:var(--mut);font-size:13.5px;flex:1}
.num{font:700 12px Consolas,monospace;color:var(--acc)}.meta{font-size:12px;color:var(--mut);margin-bottom:8px}
.act{display:flex;gap:6px}.btn{font-size:13px;padding:5px 11px;border:1px solid var(--line);border-radius:7px;text-decoration:none;color:var(--fg);background:var(--bg)}
.btn.pri{background:var(--acc);color:#fff;border-color:var(--acc)}.soon{font-size:12px;color:var(--mut)}
"""
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DSA Mastery</title><style>{CSS}{extra}</style></head>
<body><main style="max-width:1000px;margin:0 auto;padding:24px 16px 80px">
<div class="hero"><h1>DSA Mastery</h1>
<p class="lead">Pattern-based revision sheets to build real problem-solving skill for product-company interviews. Each topic has the intuition, a step-through animation, code in Java and Python, complexity, common traps and a ladder of LeetCode problems. Every page works offline: use <strong>Download</strong> to keep a copy.</p></div>
<div class="grid">{''.join(cards)}</div>
<p class="muted">Topics are added one at a time. See <a href="https://github.com/nithin988/dsa-mastery/blob/main/ROADMAP.md">ROADMAP.md</a> for the plan.</p>
</main></body></html>
"""


def main():
    built = [(f, t, topic) for f, t, _b, topic in CATALOG if topic]
    for k, (f, t, topic) in enumerate(built):
        topic["prev"] = (built[k - 1][0], built[k - 1][1]) if k else None
        topic["next"] = (built[k + 1][0], built[k + 1][1]) if k + 1 < len(built) else None
    for f, _t, _b, topic in CATALOG:
        if topic:
            write(os.path.join(ROOT, "topics", f + ".html"), render_topic(topic))
            print("built", f)
    write(os.path.join(ROOT, "index.html"), index_html())
    print("built index.html")


if __name__ == "__main__":
    main()
