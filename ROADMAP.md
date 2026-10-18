# DSA Mastery Roadmap

Goal: a person who finishes this series can recognise the pattern behind a new problem, derive the solution, state its complexity, and clear product-company interviews.

Each topic is one self-contained HTML file (`topics/NN_name.html`) with a built-in **Download** button, so it works offline and can be shared on its own.

## Phases and topics

| # | File | Topic | Patterns covered | Status |
|---|------|-------|------------------|--------|
| 01 | `01_complexity_foundations` | Complexity and problem-solving method | Big-O, constraints to complexity, amortised cost, space and recursion stack, recurrences, brute force to optimal, interview method, edge cases, hidden library costs | **done** (9 concepts, 54 problems) |
| 02 | `02_arrays` | Arrays, hashing, searching | Two pointers, sliding window (fixed/variable), prefix sum, Kadane, hashing, Dutch flag, binary search (basic, on answer, rotated), quick select/merge sort, specialised tricks | **done** (11 patterns, 77 problems) |
| 03 | `03_strings` | Strings | Frequency counting, two pointers, expand around centre, sliding window, KMP / Z / rolling hash, stack parsing, in-place edits, character arithmetic | **done** (8 patterns, 53 problems) |
| 04 | `04_linked_list` | Linked lists | Dummy node, reversal, fast/slow (Floyd), merge and sort, runner gap, split-reverse-merge, two chains and carry, LRU design | **done** (8 patterns, 36 problems) |
| 05 | `05_stack_queue` | Stacks, queues, deques | Stack bookkeeping, monotonic stack (next greater, ranges), two-stack queue, BFS, monotonic deque, expression evaluation, greedy stack, circular buffers | **done** (9 patterns, 47 problems) |
| 06 | `06_sorting_intervals` | Sorting and intervals | Merge/quick sort, custom comparators, counting and bucket sort, merge and insert intervals, sweep line, greedy scheduling, sort + two pointers, cyclic sort | **done** (9 patterns, 49 problems) |
| 07 | `07_recursion_backtracking` | Recursion and backtracking | Recursion basics, subsets, combinations, permutations, duplicate handling, string partitions, grid search, N-Queens / Sudoku, pruning and memoisation | **done** (9 patterns, 40 problems) |
| 08 | `08_bit_math` | Bit manipulation and math | Bit idioms, XOR cancellation, counting set bits, bitmask subsets, arithmetic with bits, fast power and modular arithmetic, GCD and sieve, digit manipulation, formula-based math | **done** (9 patterns, 51 problems) |
| 09 | `09_trees` | Binary trees and BST | Recursive thinking, DFS traversals and paths, BFS levels, record-vs-return path problems, BST operations, LCA, construct and serialise, tree DP, iterative traversals | **done** (9 patterns, 58 problems) |
| 10 | `10_heap_priority_queue` | Heaps | Heap mechanics, top-K, two heaps (median), k-way merge, greedy with a heap, lazy deletion, heap sort and comparators, Dijkstra, frequency heaps | **done** (9 patterns, 43 problems) |
| 11 | `11_trie` | Tries | Trie basics, prefix counts and autocomplete, wildcards, trie + backtracking, augmented nodes, XOR trie, compressed tries and alternatives, word break, streams | **done** (9 patterns, 32 problems) |
| 12 | `12_graphs_traversal` | Graph traversal | Representation, DFS and components, BFS shortest paths, grids and islands, multi-source BFS, cycle detection, bipartite check, implicit state graphs, border-first search | **done** (9 patterns, 43 problems) |
| 13 | `13_graphs_advanced` | Advanced graphs | Topological sort, union-find, Dijkstra and 0-1 BFS, Bellman-Ford / Floyd-Warshall, MST, union-find applications, bridges, SCC, Eulerian paths | **done** (9 patterns, 37 problems) |
| 14 | `14_greedy` | Greedy | Exchange argument and counterexamples, jump games, running balance with resets, stock trading, two-pass greedy, characters and digits, range tracking, ratio greedy | **done** (9 patterns, 38 problems) |
| 15 | `15_dp_1d_2d` | Dynamic programming I | State/transition method, take-or-skip, coin change, LIS, grid paths, string-prefix DP, matrix DP (largest square), state machines, rolling arrays and reconstruction | **done** (9 patterns, 46 problems) |
| 16 | `16_dp_advanced` | Dynamic programming II | 0/1 and multi-dimensional knapsack, LCS, edit distance, palindromic DP, interval DP, bitmask DP, digit DP, monotonic-deque speed-ups | **done** (9 patterns, 47 problems) |
| 17 | `17_advanced_ds` | Advanced data structures | Fenwick tree, segment tree, lazy propagation, sparse table, Fenwick over ranks, binary lifting and LCA, ordered sets, offline queries | **done** (8 patterns, 31 problems) |
| 18 | `18_design_problems` | Design-style problems | LRU / LFU, O(1) random sets, iterators, rate limiters, time-based stores, feeds and leaderboards, frequency stacks, text editors | **done** (8 patterns, 31 problems) |
| 19 | `19_interview_playbook` | Interview playbook | Pattern selector across all topics, communication script, edge-case checklist, company-wise lists, 12-week plan | planned |

Suggested build order: 02 (upgrade, sets the template) -> 03 -> 04 -> 05 -> 09 -> 12 -> 15 -> remaining.

## Sources to cross-check each topic against

- NeetCode 150 / Blind 75 (pattern grouping and frequency)
- Grind 75 (ordering by difficulty)
- Striver's A2Z sheet and Love Babbar 450 (coverage for Indian product-company interviews)
- Sean Prashad's LeetCode patterns (pattern-to-problem mapping)
- CP-Algorithms and CLRS (correctness and complexity)
- Company-tagged LeetCode lists (frequency)

Frequency tiers are our judgement from these lists, and the pages say so; they are not hard data.

## Page template (what every topic file contains)

The sample `02_arrays.html` is a good base. What we keep, and what we add:

| Section | In sample | Plan |
|---------|-----------|------|
| Mindset + 3 questions to ask | yes | keep |
| Pattern priority index (frequency tiers) | yes | keep, add source list per row |
| Problem-cue selector | yes | keep |
| Per pattern: when / detect / core idea / how it works / trace / skeleton / complexity / traps / when not | yes | keep |
| **Intuition** (a real-world analogy plus "why does this work") | no | add to every pattern |
| **Brute force -> optimised** story | no | add, with the complexity drop shown |
| **Visual step-through** (small animated or step-by-step diagram per pattern) | no | add, so friends can watch the algorithm run |
| **Problem ladder** per pattern: Easy -> Medium -> Hard, each with LC number, link, one-line logic, time/space | partial (names only) | add |
| Code in Java only | Java | Java plus Python tabs (C++ later if wanted) |
| Variants and follow-ups ("what if sorted / streaming / negatives") | no | add |
| Common mistakes seen in interviews | partial (Traps) | keep, expand |
| Self-test (5 quick questions with hidden answers) | no | add |
| Progress checklist (tick problems, saved in the browser) | no | add |
| Working table of contents and anchors | links were broken in the sample | fix |
| Dark/light mode, print styles, mobile layout | print only | add |
| **Download button** (saves the page as a standalone `.html`) | no | add to every page |

Fixes noticed in the sample: the contents list shows raw `[text](#anchor)` because the Markdown links were not converted; the 3-pointer "Dutch flag" and "variable window" traces are vague (`bca...`, `swap/scan`) and should be full step-by-step traces.

## Repo structure

```
dsa-mastery/
  README.md              landing page: topic list, how to study, download links
  ROADMAP.md             this file
  index.html             GitHub Pages landing page (cards for every topic)
  topics/NN_name.html    one self-contained file per topic
  docs/                  template spec, contribution notes
```

Sharing: enable GitHub Pages so friends open `https://nithin988.github.io/dsa-mastery/` and read online; each page has a Download button, and the README links to the raw files as well.

## Definition of done for a topic

1. Every pattern has intuition, trace, skeleton, complexity and traps.
2. Each pattern has a 6-10 problem ladder (Easy to Hard) with LC links and one-line logic.
3. Cross-checked against at least two of the source lists above.
4. Code in Java and Python is run against the example inputs.
5. Opens correctly offline, in dark mode, on mobile, and prints cleanly.
