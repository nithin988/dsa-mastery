"""Content for topic 19: the interview playbook (process, constraints, pattern selection, templates, checklists, plan)."""

P = []

# ---------------------------------------------------------------- 1
P.append(dict(
    title="The six-step interview framework", tier="hot", sim="framework", oneline="clarify, examples, brute force, optimise, code, test: always in this order",
    why="Most failed interviews fail on process, not on knowledge", signature="LC 1 / 121 / 20",
    when="Every coding interview, every practice problem: the order of your steps matters as much as the answer.",
    detect="You are tempted to start typing immediately, you are unsure what the problem asks, or you finish coding with no time left to test.",
    intuition="An interview is a **collaboration under time pressure**, and the interviewer scores how you think. A fixed routine protects you when you are nervous: you always know the next move. Clarifying prevents solving the wrong problem; examples reveal edge cases; a brute-force baseline proves you understand and gives a fallback; naming the bottleneck makes the optimisation look principled rather than lucky; coding with narration shows your style; testing catches bugs before the interviewer does.",
    idea="Run the same six steps on every problem: **(1) Clarify** inputs, limits and edge cases, and restate the task. **(2) Examples**: one normal, one edge, one tricky. **(3) Brute force** with its complexity. **(4) Optimise**: find the bottleneck, name the pattern and its complexity before coding. **(5) Code** cleanly while explaining. **(6) Test** by dry-running your own example and one edge case, then state the final complexity.",
    steps=["Clarify: types, ranges, duplicates, empty input, may I modify the input, what to return on failure.", "Examples: normal, edge (empty / single / duplicates), tricky (negatives, overflow).", "Brute force first: say it, give its complexity, then improve.", "Optimise: name the bottleneck, then the pattern, then the new complexity; wait for a nod before coding.", "Code in small named functions; narrate invariants; no silent minutes.", "Test by hand on your examples; fix calmly; state time and space complexity."],
    trace_title="a 45-minute clock",
    trace="""0-5   clarify and examples
5-10  brute force and chosen approach (agree before coding)
10-30 code with narration
30-40 dry-run tests, fix bugs
40-45 complexity, follow-up questions""",
    code=[],
    complexity="Cost: a few minutes of discipline per problem; saves far more in rewrites and wrong turns.",
    traps=["Coding before you can state the approach in two sentences.", "Going silent: say what you are thinking, even when stuck, and ask for a hint after about 5 minutes.",
           "Skipping the dry run: untested code is the most common reason for a no-hire after a correct idea.", "Arguing with a hint: treat it as information, not criticism."],
    variants=["Whiteboard or plain editor: write signatures and helper function names first; no auto-complete will save you.", "System-design-flavoured coding (design a class): start from the API and complexity requirements (topic 18).", "Pair-programming style rounds: ask how they like to work and think aloud more.", "Follow-ups (\"what if the data does not fit in memory?\"): answer with the trade-off, not just a technique name."],
    notuse="Never skip it. On very easy problems the steps are fast, but the order stays the same.",
    problems=[
        (1, "Two Sum", "E", "two-sum", "Practise the six steps out loud: brute force O(n²), then a hash map in O(n)", "O(n) / O(n)"),
        (121, "Best Time to Buy and Sell Stock", "E", "best-time-to-buy-and-sell-stock", "Brute force pairs, then a running minimum", "O(n) / O(1)"),
        (20, "Valid Parentheses", "E", "valid-parentheses", "Clarify the bracket types and empty string; stack solution", "O(n) / O(n)"),
        (49, "Group Anagrams", "M", "group-anagrams", "Clarify case and alphabet; sorted-key or count-key hash map", "O(n·k log k) / O(n·k)"),
        (56, "Merge Intervals", "M", "merge-intervals", "Examples with touching and nested intervals; sort + sweep", "O(n log n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 2
P.append(dict(
    title="Constraints to complexity to technique", tier="hot", sim="budget", oneline="read the input size first; it tells you which complexity is intended",
    why="The fastest way to rule out wrong approaches before writing code", signature="LC 15 / 287 / 560",
    when="At the start of every problem, right after reading the statement: look at the limits on n.",
    detect="You are choosing between a simple and a clever solution, or your solution times out on the largest tests.",
    intuition="A judge (and a real machine) can do roughly 10⁸ simple operations per second in a compiled language and about 10⁷ in Python. If `n` is 10⁵, an O(n²) algorithm needs 10¹⁰ operations: far too slow. So the limit on `n` tells you the intended complexity class, and each class has a few techniques that naturally reach it. Work backwards from the constraints instead of hoping your first idea fits.",
    idea="Map the input size to a target: `n ≤ 10` → O(n!); `n ≤ 20` → O(2ⁿ); `n ≤ 100` → O(n³); `n ≤ 1 000` → O(n²); `n ≤ 10⁵` → O(n log n); `n ≤ 10⁶` → O(n); larger → O(log n) or O(1). Then ask which technique removes a factor of n from your current idea: hashing, sorting, two pointers, prefix sums, binary search, a heap, a monotonic stack.",
    steps=["Read the constraints before thinking about algorithms.", "Estimate operations: plug n into your candidate's complexity; compare with about 10⁸.", "If too slow, find the repeated work and remove it with the right structure.", "State the final complexity and memory to the interviewer."],
    trace_title="three-sum with n = 3000",
    trace="""brute force triple loop   n^3 = 2.7 * 10^10  -> too slow
sort + two pointers       n^2 = 9 * 10^6      -> fine
state: O(n^2) time, O(1) extra space""",
    code=[],
    complexity="Cost: ten seconds per problem; prevents wasted time on hopeless approaches.",
    traps=["Ignoring constants and hidden costs (string concatenation in a loop, `list.pop(0)`, sorting inside a loop).", "Forgetting memory: an `n × n` table with n = 10⁴ is 400 MB.",
           "Python is about ten times slower per operation: prefer built-ins and aim lower.", "Amortised complexity is real: nested loops over a pointer that only moves forward are still O(n)."],
    variants=["Constraints on values rather than count (values ≤ 10⁵ allow counting arrays or DP over values).", "Query-heavy problems (q up to 10⁵): need O(log n) or O(1) per query, so precompute (topic 17).", "Pseudo-polynomial DP: complexity depends on a numeric value, not just n (topic 16).", "Space limits: rolling arrays and in-place tricks."],
    notuse="When constraints are missing, ask for them. Do not guess silently.",
    problems=[
        (15, "3Sum", "M", "3sum", "n up to 3000: sort + two pointers beats the cubic loop", "O(n²) / O(1)"),
        (167, "Two Sum II - Input Array Is Sorted", "M", "two-sum-ii-input-array-is-sorted", "Sorted input removes the need for a hash map", "O(n) / O(1)"),
        (238, "Product of Array Except Self", "M", "product-of-array-except-self", "Prefix and suffix products instead of division", "O(n) / O(1)"),
        (287, "Find the Duplicate Number", "M", "find-the-duplicate-number", "Constraints forbid modifying or extra space: cycle detection", "O(n) / O(1)"),
        (560, "Subarray Sum Equals K", "M", "subarray-sum-equals-k", "n up to 2·10⁴ and negatives: prefix sums + hash map", "O(n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 3
P.append(dict(
    title="Recognising the pattern from the statement", tier="hot", sim="selector", oneline="underline clues, translate each into a property, then name the pattern",
    why="Knowing patterns is not enough; you must connect them to the wording", signature="LC 3 / 200 / 322",
    when="You read a new problem and do not know where to start.",
    detect="Different problems feel unrelated even though they share a pattern; or you jump to a favourite technique that does not fit.",
    intuition="Problem statements contain **signal words**. \"Longest substring\" says contiguous plus optimising a length: sliding window. \"Number of ways\" says count: DP (or combinatorics), not greedy. \"Minimum steps in a grid\" says unweighted shortest path: BFS. \"Prerequisites\" says directed dependencies: topological sort. Underline the clues, translate each into a property, and the pattern usually names itself; the table below the chapters collects the most useful clues.",
    idea="Four moves: **(1)** underline the clues; **(2)** translate each clue into a property (contiguous, sorted, choose-or-skip, shortest, all combinations, dependencies); **(3)** name the pattern from the properties; **(4)** validate it against the constraints (previous chapter). If two patterns fit, prefer the simpler one that is fast enough, and say why you rejected the other.",
    steps=["Underline words about the goal (min, max, count, all, exists) and the structure (array, tree, graph, grid, string).", "Translate each into a property: contiguous, sorted, overlapping subproblems, shortest, dependencies.", "Name the pattern and the topic it belongs to.", "Check the complexity against the constraints, then explain the choice aloud."],
    trace_title="\"Minimum steps from start to exit of a grid\"",
    trace="""minimum steps  -> shortest path, every move costs 1
grid           -> cells are nodes, 4 neighbours are edges
start to exit  -> single source, single target
=> BFS on the grid (topic 12)""",
    code=[],
    complexity="Cost: one minute of deliberate reading; repays itself on every problem.",
    traps=["Anchoring on the first pattern you think of: confirm it with the constraints.", "Confusing look-alikes: shortest path (BFS) vs cheapest path (Dijkstra); subsequence (DP) vs subarray (window); count (DP) vs enumerate (backtracking).",
           "Greedy without a proof: test a counterexample before committing.", "Ignoring the output type: \"return one answer\" vs \"return all answers\" changes DP into backtracking."],
    variants=["Hybrid problems: BFS + bitmask state, binary search + greedy check, DP + monotonic deque.", "Hidden graphs: words with one-letter differences, states of a puzzle.", "Hidden binary search: \"minimise the maximum\", \"smallest capacity such that…\".", "Hidden prefix sums: subarray sums, ranges with differences."],
    notuse="When a pattern does not obviously fit, fall back to the brute force and look for the bottleneck instead of forcing a pattern.",
    problems=[
        (3, "Longest Substring Without Repeating Characters", "M", "longest-substring-without-repeating-characters", "Contiguous + validity of a window: sliding window", "O(n) / O(k)"),
        (200, "Number of Islands", "M", "number-of-islands", "Grid + connected regions: DFS / BFS / union-find", "O(m·n) / O(m·n)"),
        (322, "Coin Change", "M", "coin-change", "Minimum count with reusable coins: DP over amounts", "O(n·amount) / O(amount)"),
        (207, "Course Schedule", "M", "course-schedule", "Prerequisites: cycle detection / topological sort", "O(V+E) / O(V+E)"),
        (621, "Task Scheduler", "M", "task-scheduler", "Cooldown with counts: greedy on the most frequent task", "O(n) / O(1)"),
        (347, "Top K Frequent Elements", "M", "top-k-frequent-elements", "Top K by count: hash map + heap or buckets", "O(n log k) / O(n)"),
    ]))

# ---------------------------------------------------------------- 4
P.append(dict(
    title="Templates you should write from memory, I: arrays and search", tier="hot", sim=None, oneline="binary search, sliding window, monotonic stack, prefix sums with a map",
    why="Four skeletons cover a large share of array and string questions", signature="LC 704 / 904 / 739",
    when="The problem is about arrays or strings and one of the clues from the selector appears: sorted, window, next greater, subarray sum.",
    detect="Sorted input or a monotone yes / no question → binary search. \"Longest / shortest valid contiguous piece\" → sliding window. \"Next greater / smaller\" → monotonic stack. \"Subarray with sum k\" → prefix sums with a map.",
    intuition="Interviews reward **fluency**: you should be able to write these skeletons without thinking about indices, so your attention goes to what is different about the problem. Each template below is the smallest correct version; the details that vary between problems are marked by comments.",
    idea="**Binary search:** keep `[lo, hi)` with the invariant that the answer lies in it; the predicate decides which half to drop. **Sliding window:** expand `right`, shrink `left` while the window is invalid, record the best. **Monotonic stack:** keep indices in monotone order; pop while the new value breaks the order. **Prefix sum + map:** the count of subarrays with sum `k` ending here is the number of earlier prefixes equal to `prefix − k`.",
    steps=["Pick the template from the clue.", "Write the skeleton, then fill in the problem-specific condition.", "Check the invariant (what is true at the start of each loop iteration).", "Test empty input, one element, and the largest value."],
    trace_title="`firstTrue` on `[3, 7, 12, 20]`: smallest x with x² ≥ 100",
    trace="""lo=0 hi=3
mid=1: 7^2 = 49 < 100 -> lo = 2
mid=2: 12^2 = 144 >= 100 -> hi = 2
lo == hi -> answer index 2 (value 12)""",
    code=[("binary search: lower bound and search on the answer",
           """int lowerBound(int[] a, int x) {                                  // first index with a[i] >= x (a.length if none)
    int lo = 0, hi = a.length;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (a[mid] < x) lo = mid + 1; else hi = mid;
    }
    return lo;
}
int firstTrue(int lo, int hi, java.util.function.IntPredicate ok) {   // smallest x in [lo, hi] with ok(x); ok is false...false true...true
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (ok.test(mid)) hi = mid; else lo = mid + 1;
    }
    return lo;
}""",
           """def lower_bound(a, x):                                            # first index with a[i] >= x (len(a) if none)
    lo, hi = 0, len(a)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo

def first_true(lo, hi, ok):                                       # smallest x in [lo, hi] with ok(x); ok is false...false true...true
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if ok(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo"""),
          ("sliding window: longest substring with at most k distinct characters",
           """int longestAtMostKDistinct(String s, int k) {
    Map<Character, Integer> count = new HashMap<>();
    int best = 0, left = 0;
    for (int right = 0; right < s.length(); right++) {
        count.merge(s.charAt(right), 1, Integer::sum);                  // expand
        while (count.size() > k) {                                      // shrink while the window is invalid
            char c = s.charAt(left++);
            if (count.merge(c, -1, Integer::sum) == 0) count.remove(c);
        }
        best = Math.max(best, right - left + 1);
    }
    return best;
}""",
           """def longest_at_most_k_distinct(s, k):
    count = {}
    best = left = 0
    for right, ch in enumerate(s):
        count[ch] = count.get(ch, 0) + 1                                # expand
        while len(count) > k:                                           # shrink while the window is invalid
            c = s[left]
            left += 1
            count[c] -= 1
            if count[c] == 0:
                del count[c]
        best = max(best, right - left + 1)
    return best"""),
          ("monotonic stack: next greater element to the right",
           """int[] nextGreater(int[] a) {
    int[] res = new int[a.length];
    Arrays.fill(res, -1);
    Deque<Integer> stack = new ArrayDeque<>();                          // indices, values decreasing
    for (int i = 0; i < a.length; i++) {
        while (!stack.isEmpty() && a[stack.peek()] < a[i]) res[stack.pop()] = a[i];
        stack.push(i);
    }
    return res;
}""",
           """def next_greater(a):
    res = [-1] * len(a)
    stack = []                                                          # indices, values decreasing
    for i, x in enumerate(a):
        while stack and a[stack[-1]] < x:
            res[stack.pop()] = x
        stack.append(i)
    return res"""),
          ("prefix sums with a hash map: number of subarrays with sum k",
           """int subarraySum(int[] nums, int k) {
    Map<Integer, Integer> seen = new HashMap<>();
    seen.put(0, 1);                                                     // the empty prefix
    int prefix = 0, count = 0;
    for (int x : nums) {
        prefix += x;
        count += seen.getOrDefault(prefix - k, 0);                      // earlier prefixes that leave a sum of k
        seen.merge(prefix, 1, Integer::sum);
    }
    return count;
}""",
           """def subarray_sum(nums, k):
    seen = {0: 1}                                                       # the empty prefix
    prefix = count = 0
    for x in nums:
        prefix += x
        count += seen.get(prefix - k, 0)                                # earlier prefixes that leave a sum of k
        seen[prefix] = seen.get(prefix, 0) + 1
    return count""")],
    complexity="Binary search O(log n); the other three are O(n) time with O(k) / O(n) memory.",
    traps=["`lo + (hi − lo) / 2` avoids integer overflow.", "Pick one binary search convention (`[lo, hi)` here) and stick to it; mixing conventions causes infinite loops.",
           "Window problems with negatives usually do **not** work with a sliding window: use prefix sums.", "Seed the prefix map with `{0: 1}`."],
    variants=["Binary search on the answer (capacity, speed, days): `firstTrue` with a greedy feasibility check.", "Window with exactly k: `atMost(k) − atMost(k − 1)`.", "Monotonic deque for window maximum (topic 05).", "Two pointers on a sorted array (topic 02)."],
    notuse="When the data is unsorted and the predicate is not monotone (binary search fails), or when elements can be negative and the condition is on the sum (no sliding window).",
    problems=[
        (704, "Binary Search", "E", "binary-search", "The plain template", "O(log n) / O(1)"),
        (34, "Find First and Last Position of Element in Sorted Array", "M", "find-first-and-last-position-of-element-in-sorted-array", "Two lower bounds: x and x + 1", "O(log n) / O(1)"),
        (875, "Koko Eating Bananas", "M", "koko-eating-bananas", "firstTrue over speeds with a greedy hour count", "O(n log m) / O(1)"),
        (904, "Fruit Into Baskets", "M", "fruit-into-baskets", "Longest window with at most 2 distinct values", "O(n) / O(1)"),
        (739, "Daily Temperatures", "M", "daily-temperatures", "Next greater element with a monotonic stack", "O(n) / O(n)"),
        (560, "Subarray Sum Equals K", "M", "subarray-sum-equals-k", "Prefix sums + hash map", "O(n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 5
P.append(dict(
    title="Templates you should write from memory, II: graphs and grids", tier="hot", sim=None, oneline="BFS, DFS, union-find, Dijkstra and topological sort skeletons",
    why="Graph questions are the second biggest block of interview problems", signature="LC 1091 / 200 / 743",
    when="The problem has cells in a grid, dependencies, connections, or shortest paths.",
    detect="\"Minimum steps\" in a grid → BFS. \"Number of regions / components\" → DFS or union-find. \"Cheapest path\" with weights → Dijkstra. \"Order with prerequisites\" → topological sort.",
    intuition="Five skeletons solve nearly every graph question: BFS gives shortest paths when every edge costs 1, DFS explores a whole region, union-find answers connectivity under merges, Dijkstra handles non-negative weights, and Kahn's algorithm orders a DAG. Write them once with a clear `visited` rule (mark when you **push**, not when you pop, to avoid duplicates) and reuse them.",
    idea="**BFS:** queue by levels; mark a cell visited when queued. **DFS:** recursion with a visited mark or in-place sinking. **Union-find:** parent array with path compression and union by size. **Dijkstra:** min-heap of `(distance, node)`; skip stale entries. **Kahn:** compute in-degrees, queue the zeros, remove them one by one; if fewer than `n` nodes come out there is a cycle.",
    steps=["Model the problem as a graph: what are the nodes and the edges?", "Pick the template: unweighted shortest → BFS; weighted → Dijkstra; regions → DFS / union-find; order → Kahn.", "Mark nodes visited when you enqueue them.", "Return the right sentinel (−1 / infinity / empty) when the target is unreachable."],
    trace_title="BFS on a 3 × 3 grid (0 open, 1 wall)",
    trace="""0 0 0
1 1 0
0 0 0
level 0: (0,0)   level 1: (0,1)   level 2: (0,2)
level 3: (1,2)   level 4: (2,2) = goal -> 4 steps""",
    code=[("BFS shortest path in a grid (4 directions, 0 = open, 1 = wall)",
           """int shortestPath(int[][] grid) {
    int n = grid.length, m = grid[0].length;
    if (grid[0][0] == 1 || grid[n - 1][m - 1] == 1) return -1;
    boolean[][] seen = new boolean[n][m];
    Deque<int[]> queue = new ArrayDeque<>();
    queue.add(new int[]{0, 0});
    seen[0][0] = true;                                                  // mark when queued
    int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
    for (int steps = 0; !queue.isEmpty(); steps++) {
        for (int size = queue.size(); size > 0; size--) {               // one BFS level
            int[] cur = queue.poll();
            if (cur[0] == n - 1 && cur[1] == m - 1) return steps;
            for (int[] d : dirs) {
                int r = cur[0] + d[0], c = cur[1] + d[1];
                if (r >= 0 && r < n && c >= 0 && c < m && grid[r][c] == 0 && !seen[r][c]) {
                    seen[r][c] = true;
                    queue.add(new int[]{r, c});
                }
            }
        }
    }
    return -1;
}""",
           """from collections import deque

def shortest_path(grid):
    n, m = len(grid), len(grid[0])
    if grid[0][0] == 1 or grid[n - 1][m - 1] == 1:
        return -1
    seen = [[False] * m for _ in range(n)]
    queue = deque([(0, 0)])
    seen[0][0] = True                                                   # mark when queued
    steps = 0
    while queue:
        for _ in range(len(queue)):                                     # one BFS level
            r, c = queue.popleft()
            if (r, c) == (n - 1, m - 1):
                return steps
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < m and grid[nr][nc] == 0 and not seen[nr][nc]:
                    seen[nr][nc] = True
                    queue.append((nr, nc))
        steps += 1
    return -1"""),
          ("DFS: count connected regions (islands) by sinking visited land",
           """int countIslands(int[][] g) {
    int count = 0;
    for (int r = 0; r < g.length; r++)
        for (int c = 0; c < g[0].length; c++)
            if (g[r][c] == 1) { count++; sink(g, r, c); }
    return count;
}
private void sink(int[][] g, int r, int c) {
    if (r < 0 || c < 0 || r >= g.length || c >= g[0].length || g[r][c] != 1) return;
    g[r][c] = 0;                                                        // mark visited by changing the grid
    sink(g, r + 1, c); sink(g, r - 1, c); sink(g, r, c + 1); sink(g, r, c - 1);
}""",
           """def count_islands(g):
    n, m = len(g), len(g[0])

    def sink(r, c):
        if r < 0 or c < 0 or r >= n or c >= m or g[r][c] != 1:
            return
        g[r][c] = 0                                                     # mark visited by changing the grid
        sink(r + 1, c); sink(r - 1, c); sink(r, c + 1); sink(r, c - 1)

    count = 0
    for r in range(n):
        for c in range(m):
            if g[r][c] == 1:
                count += 1
                sink(r, c)
    return count"""),
          ("union-find (path compression, union by size)",
           """class UnionFind {
    private final int[] parent, size;
    int components;
    UnionFind(int n) {
        parent = new int[n];
        size = new int[n];
        components = n;
        for (int i = 0; i < n; i++) { parent[i] = i; size[i] = 1; }
    }
    int find(int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }   // path halving
        return x;
    }
    boolean union(int a, int b) {
        int ra = find(a), rb = find(b);
        if (ra == rb) return false;                                     // already connected
        if (size[ra] < size[rb]) { int t = ra; ra = rb; rb = t; }
        parent[rb] = ra;
        size[ra] += size[rb];
        components--;
        return true;
    }
}""",
           """class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.components = n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]                # path halving
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                                                # already connected
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        self.components -= 1
        return True"""),
          ("Dijkstra: shortest distances from a source (non-negative weights)",
           """int[] dijkstra(int n, int[][] edges, int src) {                   // edges are directed {u, v, w}
    List<int[]>[] adj = new List[n];
    for (int i = 0; i < n; i++) adj[i] = new ArrayList<>();
    for (int[] e : edges) adj[e[0]].add(new int[]{e[1], e[2]});
    int[] dist = new int[n];
    Arrays.fill(dist, Integer.MAX_VALUE);
    dist[src] = 0;
    PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);   // {distance, node}
    pq.add(new int[]{0, src});
    while (!pq.isEmpty()) {
        int[] top = pq.poll();
        int d = top[0], u = top[1];
        if (d > dist[u]) continue;                                      // stale entry
        for (int[] nb : adj[u])
            if (d + nb[1] < dist[nb[0]]) {
                dist[nb[0]] = d + nb[1];
                pq.add(new int[]{dist[nb[0]], nb[0]});
            }
    }
    return dist;
}""",
           """import heapq

def dijkstra(n, edges, src):                                            # edges are directed (u, v, w)
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
    INF = float('inf')
    dist = [INF] * n
    dist[src] = 0
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue                                                    # stale entry
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(pq, (dist[v], v))
    return dist"""),
          ("topological sort with Kahn's algorithm (empty result = cycle)",
           """int[] topoOrder(int n, int[][] edges) {                          // edge {u, v} means u before v
    List<Integer>[] adj = new List[n];
    for (int i = 0; i < n; i++) adj[i] = new ArrayList<>();
    int[] indeg = new int[n];
    for (int[] e : edges) { adj[e[0]].add(e[1]); indeg[e[1]]++; }
    Deque<Integer> queue = new ArrayDeque<>();
    for (int i = 0; i < n; i++) if (indeg[i] == 0) queue.add(i);
    int[] order = new int[n];
    int k = 0;
    while (!queue.isEmpty()) {
        int u = queue.poll();
        order[k++] = u;
        for (int v : adj[u]) if (--indeg[v] == 0) queue.add(v);
    }
    return k == n ? order : new int[0];                                 // fewer than n nodes: there is a cycle
}""",
           """from collections import deque

def topo_order(n, edges):                                               # edge (u, v) means u before v
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    queue = deque(i for i in range(n) if indeg[i] == 0)
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)
    return order if len(order) == n else []                             # fewer than n nodes: there is a cycle""")],
    complexity="BFS / DFS O(V + E) (O(rows · cols) for grids); union-find ≈ O(α(n)) per operation; Dijkstra O((V + E) log V); Kahn O(V + E).",
    traps=["Mark a node visited when you **enqueue** it in BFS; marking on dequeue allows duplicates and blows up the queue.", "Dijkstra fails with negative edges (use Bellman-Ford) and needs the stale-entry check.",
           "Recursive DFS can overflow the stack on a 10⁵-cell line: use an explicit stack when depth can be huge.", "A cycle in the dependency graph means no topological order: say so explicitly."],
    variants=["Multi-source BFS (rotting oranges, walls and gates): start with all sources in the queue.", "0-1 BFS with a deque for weights 0 and 1.", "Bidirectional BFS for word ladder.", "Union-find with weights or with rollback."],
    notuse="Weighted shortest paths with negative edges (Bellman-Ford), all-pairs on small graphs (Floyd-Warshall), or no graph structure at all.",
    problems=[
        (1091, "Shortest Path in Binary Matrix", "M", "shortest-path-in-binary-matrix", "BFS on 8 directions", "O(n²) / O(n²)"),
        (200, "Number of Islands", "M", "number-of-islands", "DFS or union-find on regions", "O(m·n) / O(m·n)"),
        (547, "Number of Provinces", "M", "number-of-provinces", "Union-find on an adjacency matrix", "O(n²) / O(n)"),
        (207, "Course Schedule", "M", "course-schedule", "Kahn: can all courses be taken?", "O(V+E) / O(V+E)"),
        (210, "Course Schedule II", "M", "course-schedule-ii", "Kahn: return the order", "O(V+E) / O(V+E)"),
        (743, "Network Delay Time", "M", "network-delay-time", "Dijkstra; answer is the largest distance", "O(E log V) / O(V+E)"),
    ]))

# ---------------------------------------------------------------- 6
P.append(dict(
    title="Templates you should write from memory, III: recursion and DP", tier="hot", sim=None, oneline="backtracking, memoisation, bottom-up tables and tree DFS that returns data",
    why="The last big block: enumeration, optimisation and trees", signature="LC 78 / 322 / 543",
    when="You must list all answers (backtracking), find the best or count the ways (DP), or compute something about a tree.",
    detect="\"All subsets / permutations / combinations\" → backtracking. \"Minimum / maximum / number of ways\" with overlapping choices → DP. \"Height / diameter / path sum of a tree\" → DFS that returns information.",
    intuition="**Backtracking** builds an answer one choice at a time: choose, recurse, undo. **DP** is recursion plus memory: if the same subproblem repeats, store it (top-down) or fill a table in dependency order (bottom-up). **Tree DFS** works best when each call returns one useful number (a height) and updates a global answer on the way.",
    idea="Backtracking skeleton: `path` and a `start` index; record when the condition is met; loop over choices: add, recurse, remove. DP: define the state, write the recurrence, set the base case, then memoise or tabulate. Tree: `dfs(node)` returns what the parent needs (height) while the best-so-far (diameter) is updated in a variable.",
    steps=["Backtracking: choose, explore, un-choose; copy `path` when recording.", "DP: state → recurrence → base cases → order (or memo).", "Tree DFS: decide what the function returns and what it records.", "Check the size: backtracking is exponential, DP is states × transitions."],
    trace_title="subsets of `[1, 2, 3]`",
    trace="""[] -> record
[1] -> record, [1,2] -> record, [1,2,3] -> record
[1,3] -> record
[2] -> record, [2,3] -> record
[3] -> record          8 subsets""",
    code=[("backtracking: subsets and permutations",
           """List<List<Integer>> subsets(int[] nums) {
    List<List<Integer>> res = new ArrayList<>();
    collect(nums, 0, new ArrayList<>(), res);
    return res;
}
private void collect(int[] nums, int start, List<Integer> path, List<List<Integer>> res) {
    res.add(new ArrayList<>(path));                                     // record a copy
    for (int i = start; i < nums.length; i++) {
        path.add(nums[i]);                                              // choose
        collect(nums, i + 1, path, res);                                // explore
        path.remove(path.size() - 1);                                   // un-choose
    }
}
List<List<Integer>> permutations(int[] nums) {
    List<List<Integer>> res = new ArrayList<>();
    permute(nums, new boolean[nums.length], new ArrayList<>(), res);
    return res;
}
private void permute(int[] nums, boolean[] used, List<Integer> path, List<List<Integer>> res) {
    if (path.size() == nums.length) { res.add(new ArrayList<>(path)); return; }
    for (int i = 0; i < nums.length; i++) {
        if (used[i]) continue;
        used[i] = true;
        path.add(nums[i]);
        permute(nums, used, path, res);
        path.remove(path.size() - 1);
        used[i] = false;
    }
}""",
           """def subsets(nums):
    res = []

    def collect(start, path):
        res.append(path[:])                                             # record a copy
        for i in range(start, len(nums)):
            path.append(nums[i])                                        # choose
            collect(i + 1, path)                                        # explore
            path.pop()                                                  # un-choose

    collect(0, [])
    return res

def permutations(nums):
    res, used = [], [False] * len(nums)

    def permute(path):
        if len(path) == len(nums):
            res.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            permute(path)
            path.pop()
            used[i] = False

    permute([])
    return res"""),
          ("DP: top-down with memo and bottom-up table (coin change)",
           """int minCoinsTopDown(int[] coins, int amount) {
    int[] memo = new int[amount + 1];
    Arrays.fill(memo, -2);                                              // -2 = not computed, -1 = impossible
    return solve(coins, amount, memo);
}
private int solve(int[] coins, int rem, int[] memo) {
    if (rem == 0) return 0;
    if (rem < 0) return -1;
    if (memo[rem] != -2) return memo[rem];
    int best = Integer.MAX_VALUE;
    for (int c : coins) {
        int sub = solve(coins, rem - c, memo);
        if (sub >= 0) best = Math.min(best, sub + 1);
    }
    return memo[rem] = best == Integer.MAX_VALUE ? -1 : best;
}
int coinChange(int[] coins, int amount) {                               // bottom-up: same recurrence, filled in order
    int[] dp = new int[amount + 1];
    Arrays.fill(dp, amount + 1);
    dp[0] = 0;
    for (int a = 1; a <= amount; a++)
        for (int c : coins)
            if (c <= a) dp[a] = Math.min(dp[a], dp[a - c] + 1);
    return dp[amount] > amount ? -1 : dp[amount];
}""",
           """from functools import lru_cache

def min_coins_top_down(coins, amount):
    @lru_cache(None)
    def solve(rem):
        if rem == 0:
            return 0
        if rem < 0:
            return -1
        best = float('inf')
        for c in coins:
            sub = solve(rem - c)
            if sub >= 0:
                best = min(best, sub + 1)
        return -1 if best == float('inf') else best

    return solve(amount)

def coin_change(coins, amount):                                         # bottom-up: same recurrence, filled in order
    dp = [0] + [amount + 1] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return -1 if dp[amount] > amount else dp[amount]"""),
          ("tree DFS that returns a value and updates a global answer (diameter)",
           """int best = 0;
int diameter(TreeNode root) {
    best = 0;
    height(root);
    return best;
}
private int height(TreeNode node) {
    if (node == null) return 0;
    int left = height(node.left), right = height(node.right);
    best = Math.max(best, left + right);                                // longest path through this node
    return 1 + Math.max(left, right);                                   // what the parent needs
}""",
           """def diameter(root):
    best = 0

    def height(node):
        nonlocal best
        if node is None:
            return 0
        left, right = height(node.left), height(node.right)
        best = max(best, left + right)                                  # longest path through this node
        return 1 + max(left, right)                                     # what the parent needs

    height(root)
    return best""")],
    complexity="Subsets O(n · 2ⁿ), permutations O(n · n!); DP O(states × transitions); tree DFS O(n).",
    traps=["Record a **copy** of `path` (`new ArrayList<>(path)` / `path[:]`), not the list you keep mutating.", "Un-choose exactly what you chose, in the reverse order.",
           "Memo tables need a sentinel that cannot be a real answer (use −2 for \"not computed\" when −1 means \"impossible\").", "Duplicates in the input need sorting plus a skip rule (topic 07)."],
    variants=["Combination sum, N-Queens, word search, palindrome partitioning (topic 07).", "Knapsack, LIS, LCS, edit distance (topics 15 and 16).", "Tree DP: house robber III, max path sum (topic 09).", "Memoised DFS on a grid (longest increasing path)."],
    notuse="A greedy proof exists (then DP is overkill), or the input is too large for exponential search and no overlapping subproblems exist.",
    problems=[
        (78, "Subsets", "M", "subsets", "Choose / explore / un-choose; record at every node", "O(n·2ⁿ) / O(n)"),
        (46, "Permutations", "M", "permutations", "Used array, record at full length", "O(n·n!) / O(n)"),
        (62, "Unique Paths", "M", "unique-paths", "dp[r][c] = dp[r−1][c] + dp[r][c−1]", "O(m·n) / O(n)"),
        (322, "Coin Change", "M", "coin-change", "Top-down memo or bottom-up table", "O(n·amount) / O(amount)"),
        (543, "Diameter of Binary Tree", "E", "diameter-of-binary-tree", "Return height, update diameter on the way up", "O(n) / O(h)"),
        (139, "Word Break", "M", "word-break", "dp[i]: can the prefix of length i be split into words", "O(n²) / O(n)"),
    ]))

# ---------------------------------------------------------------- 7
P.append(dict(
    title="Edge cases, testing and debugging checklist", tier="hot", sim=None, oneline="run the same checklist on every solution before you say done",
    why="Silly bugs, not wrong ideas, decide many rounds", signature="LC 8 / 7 / 33",
    when="Right before you say \"I'm done\", and whenever your output is wrong.",
    detect="Your code works on the sample but fails on hidden tests: empty input, one element, duplicates, negatives, overflow, or off-by-one at the boundary.",
    intuition="Bugs cluster in the same places. A fixed checklist turns testing from \"try some inputs\" into a systematic sweep of those places. Run it silently on every solution and say the interesting items aloud: that shows the interviewer you think like an engineer.",
    idea="Check: **size** (empty, one element, two elements), **values** (all equal, duplicates, negatives, zero, minimum and maximum), **order** (sorted, reverse sorted), **boundaries** (first and last index, `<` vs `≤`), **overflow** (sums and products in `int`), **mutation** (did I change the input? should I copy?), **shared state** (a variable reused across calls), **termination** (can any loop run forever?).",
    steps=["Dry-run your own example line by line, writing the variable values.", "Run the checklist: size, values, order, boundaries, overflow.", "When wrong, find the first line where reality differs from your expectation (print or trace).", "Fix the cause, not the symptom, then re-run all examples."],
    trace_title="debugging a failing case",
    trace="""expected [0,1]   got [1,1]  on  nums=[3,3], target=6
look at the first divergence: map stored before the lookup -> element paired with itself
fix: look up target - x BEFORE inserting x""",
    code=[],
    complexity="Cost: two to five minutes; saves failing on hidden tests.",
    traps=["Testing only the provided example: it is usually the easy case.", "Changing code randomly until it passes: trace instead.",
           "Forgetting integer overflow: use `long` for sums and `Math.floorMod` for modulo with negatives.", "Off-by-one at array ends: write the loop bounds as a sentence (\"i runs over every index that has a next element\")."],
    variants=["String edge cases: empty, single character, all the same, unicode / case, leading and trailing spaces.", "Tree edge cases: null root, single node, skewed chain, duplicates.", "Graph edge cases: disconnected, self-loops, parallel edges, cycles.", "Number edge cases: 0, 1, negatives, `Integer.MIN_VALUE`, `Long` limits."],
    notuse="Never skip it; scale it to the problem size.",
    problems=[
        (8, "String to Integer (atoi)", "M", "string-to-integer-atoi", "Whitespace, sign, overflow clamp, non-digit stop", "O(n) / O(1)"),
        (7, "Reverse Integer", "M", "reverse-integer", "Overflow check before the multiply", "O(log x) / O(1)"),
        (33, "Search in Rotated Sorted Array", "M", "search-in-rotated-sorted-array", "Boundary conditions with ≤ and the rotated half", "O(log n) / O(1)"),
        (54, "Spiral Matrix", "M", "spiral-matrix", "Four shrinking boundaries; single row or column", "O(m·n) / O(1)"),
        (189, "Rotate Array", "M", "rotate-array", "k larger than n, in-place reversal trick", "O(n) / O(1)"),
        (238, "Product of Array Except Self", "M", "product-of-array-except-self", "Zeros and the no-division constraint", "O(n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 8
P.append(dict(
    title="Company-style preparation and the core problem list", tier="sec", sim=None, oneline="match your emphasis to the company, but never skip the fundamentals",
    why="Turns 'everything' into a focused plan for your target interviews", signature="LC 146 / 42 / 76",
    when="You have a target company (or several) and limited weeks left.",
    detect="You have studied the topics but do not know what to prioritise, or you keep solving random problems without a plan.",
    intuition="No company publishes its question bank, and what is reported online is anecdotal and changes over time. What **is** reliable: product companies test the same core skills (arrays and strings, hash maps, trees, graphs, DP, design) with different weights and styles. So prepare the fundamentals for everyone, then use public interview write-ups and recent candidate reports for your target company to adjust the **weights**, not to skip topics.",
    idea="Build the core first (this repo's topics 01-15), then add depth by role: add hard graphs, DP and advanced structures (topics 13, 16, 17) for roles known for harder rounds; add design problems (topic 18) for roles with object-oriented or API rounds; add behavioural preparation everywhere. General tendencies reported by candidates, **not official and not guaranteed**, include: large e-commerce companies lean on arrays, strings, trees, graphs, heaps and design with a strong behavioural component; search and infrastructure companies lean on graphs, DP and harder optimisation with careful complexity analysis; social-media companies lean on arrays, strings, trees and graphs with a fast pace and two problems per round; enterprise software companies lean on lists, trees, strings and classic design questions.",
    steps=["Finish the core topics and the pattern templates before specialising.", "Read recent public interview write-ups for your target company and note the topics and style (speed, hints, follow-ups).", "Solve the core list below, then add problems tagged for your target company on a practice site.", "Do timed mock interviews with a friend: 2 problems in 45 minutes, speaking aloud.", "Prepare behavioural stories (impact, conflict, failure, leadership) using the STAR structure."],
    trace_title="a balanced weekly rhythm",
    trace="""Mon-Thu  2 new problems/day from the current topic
Fri      review: redo two problems from earlier weeks without notes
Sat      one timed mock (45 min, 2 problems) + review
Sun      rest, or read solutions to problems you could not solve""",
    code=[],
    complexity="Cost: a few hours of research at the start; makes every later hour more productive.",
    traps=["Treating anecdotal \"most frequent\" lists as fact: use them to weight your study, not to drop topics.", "Memorising solutions instead of patterns: a small change in the statement breaks memorised answers.",
           "Only solving problems you already like: schedule the weak topics first.", "Neglecting communication and behavioural preparation: they decide close calls."],
    variants=["Short on time (4 weeks): core list + templates + two mocks per week.", "Senior roles: add system design and deeper trade-off discussions.", "New-grad roles: emphasise fundamentals, clean code and testing.", "Online assessments: practise speed and edge cases on a timer with hidden tests."],
    notuse="Do not use company-specific lists as a substitute for understanding the patterns.",
    problems=[
        (146, "LRU Cache", "M", "lru-cache", "Hash map + linked list (topic 18)", "O(1) per op / O(c)"),
        (42, "Trapping Rain Water", "H", "trapping-rain-water", "Two pointers or monotonic stack", "O(n) / O(1)"),
        (76, "Minimum Window Substring", "H", "minimum-window-substring", "Sliding window with counts", "O(n) / O(k)"),
        (139, "Word Break", "M", "word-break", "DP over prefixes", "O(n²) / O(n)"),
        (236, "Lowest Common Ancestor of a Binary Tree", "M", "lowest-common-ancestor-of-a-binary-tree", "Recursion on subtrees", "O(n) / O(h)"),
        (297, "Serialize and Deserialize Binary Tree", "H", "serialize-and-deserialize-binary-tree", "Preorder with null markers", "O(n) / O(n)"),
        (215, "Kth Largest Element in an Array", "M", "kth-largest-element-in-an-array", "Heap or quickselect", "O(n) avg / O(1)"),
        (295, "Find Median from Data Stream", "H", "find-median-from-data-stream", "Two heaps", "O(log n) / O(n)"),
        (124, "Binary Tree Maximum Path Sum", "H", "binary-tree-maximum-path-sum", "Tree DFS returning the best downward path", "O(n) / O(h)"),
        (128, "Longest Consecutive Sequence", "M", "longest-consecutive-sequence", "Hash set; start only at sequence beginnings", "O(n) / O(n)"),
        (53, "Maximum Subarray", "M", "maximum-subarray", "Kadane's algorithm", "O(n) / O(1)"),
        (79, "Word Search", "M", "word-search", "Grid backtracking with in-place marks", "O(m·n·4^L) / O(L)"),
    ]))

TOPIC = dict(
    id="play", file="19_interview_playbook.html", title="Interview Playbook — Process, Pattern Selection, Templates and a 12-Week Plan",
    unit="Chapter", units_heading="The chapters",
    lead="Knowing the topics is half of the job; the other half is the process: how you clarify, choose an approach, write code, test it and talk through it. This playbook ties the whole course together: the six-step interview framework, reading constraints, recognising patterns from the wording, twelve code templates to write from memory (all tested), an edge-case checklist, how to adapt to a target company, and a 12-week plan across all topics.",
    mindset="Interviews test **process under pressure** as much as knowledge. Make the process automatic (the same six steps every time), make the common skeletons automatic (templates), and make the checking automatic (checklist). Then your attention is free for the part that is new in each problem.",
    qintro="Run these questions at the start of every problem:",
    questions=["**What exactly is asked, and what are the limits?** (clarify; read the constraints)", "**What is the simplest correct solution and its cost?** (brute force baseline)", "**What property of the input does the wording reveal?** (contiguous, sorted, shortest, count, all answers, dependencies)",
               "**Which template or topic matches, and does its complexity fit the constraints?**", "**What are the edge cases?** (empty, one element, duplicates, negatives, overflow)"],
    cues=[
        ["sorted array, or a yes / no question that flips once", "Binary search (templates, topic 02)"],
        ["longest / shortest valid contiguous piece", "Sliding window (topics 02, 03)"],
        ["subarray sum equals k, range sums", "Prefix sums + hash map (topic 02)"],
        ["next greater / smaller, histogram, temperatures", "Monotonic stack (topic 05)"],
        ["pairs in a sorted array, palindromes", "Two pointers (topics 02, 03)"],
        ["intervals, meeting rooms, merge", "Sort + sweep, heap (topic 06)"],
        ["linked list cycle, middle, reverse", "Fast / slow pointers (topic 04)"],
        ["all subsets / permutations / combinations", "Backtracking (topic 07)"],
        ["bits, powers of two, single number", "Bit manipulation (topic 08)"],
        ["tree traversal, height, path sum, LCA", "Tree DFS / BFS (topic 09)"],
        ["top K, k-th largest, running median, merge k lists", "Heaps (topic 10)"],
        ["prefix search, autocomplete, word dictionary", "Trie (topic 11)"],
        ["grid, islands, shortest steps, connectivity", "BFS / DFS / union-find (topic 12)"],
        ["prerequisites, ordering, weighted shortest path, MST", "Topological sort, Dijkstra, Kruskal (topic 13)"],
        ["maximise with a locally best choice, intervals, jump game", "Greedy (topic 14)"],
        ["count ways, minimum cost, choose or skip, grids", "DP I (topic 15)"],
        ["two strings, subset sum, ranges, small n with sets", "DP II (topic 16)"],
        ["range query with updates, k-th ancestor, nearest key", "Advanced data structures (topic 17)"],
        ["design a class / cache / feed / iterator", "Design problems (topic 18)"],
        ["n ≤ 20", "Bitmask, subsets, meet in the middle (topics 07, 16)"],
        ["n ≤ 10⁵ and queries", "O(n log n) preprocessing + O(log n) queries (topic 17)"],
    ],
    choose=[
        ["No idea where to start", "Brute force first, then find the bottleneck (chapters 1 and 3)"],
        ["Solution too slow", "Compare n with the budget table, remove a factor of n (chapter 2)"],
        ["Array / string problem", "Templates I (chapter 4)"],
        ["Graph / grid problem", "Templates II (chapter 5)"],
        ["Enumerate, optimise or tree problem", "Templates III (chapter 6)"],
        ["Wrong answer on hidden tests", "Edge-case checklist (chapter 7)"],
        ["Preparing for a specific company", "Core list + weighting (chapter 8)"],
    ],
    rule="**the same six steps, the same few templates, the same checklist.** Spend your creativity on the new part of each problem, not on re-deriving the routine.",
    selftest=[
        ("What are the six steps of the interview framework?", "Clarify, examples, brute force, optimise (name the bottleneck and pattern), code, test. Always in that order, speaking aloud."),
        ("How many simple operations can you rely on per second, and what does that imply for n = 10⁵?", "About 10⁸ in Java / C++ and 10⁷ in Python, so n = 10⁵ allows O(n log n) but not O(n²) (10¹⁰)."),
        ("The statement says \"minimum number of steps in a grid\". What pattern do you name, and why?", "BFS: unweighted shortest path where every move costs 1, with cells as nodes and neighbours as edges."),
        ("Why mark a cell visited when it is enqueued in BFS rather than when it is dequeued?", "Marking on dequeue lets the same cell be queued several times, which wastes time and memory and can blow up the queue."),
        ("What goes wrong if you record `path` itself in backtracking?", "You store a reference to a list you keep mutating, so every recorded answer ends up identical (empty); record a copy."),
        ("Why does a sliding window fail on arrays with negative numbers when the condition is a sum?", "Expanding or shrinking no longer changes the sum monotonically, so you cannot decide which end to move; use prefix sums and a hash map."),
        ("How should you use company-specific question lists?", "As a way to weight your study, not a substitute for the fundamentals: they are anecdotal and change, while the underlying patterns are stable."),
        ("What do you do when you are stuck for five minutes in an interview?", "Say what you have tried, restate the constraints, test a small example by hand, and ask for a hint; silence is worse than an honest question."),
    ],
    plan=[
        "**Week 1:** topics 01 and 02 (complexity, arrays): templates for binary search, windows, prefix sums; start the six-step routine.",
        "**Week 2:** topics 03 and 04 (strings, linked lists); first timed mock (2 easy / medium problems).",
        "**Week 3:** topics 05 and 06 (stacks and queues, sorting and intervals).",
        "**Week 4:** topics 07 and 08 (recursion and backtracking, bits and math); redo the hardest problems from weeks 1-3.",
        "**Week 5:** topic 09 (trees): traversals, BST, LCA, path sums; mock interview.",
        "**Week 6:** topics 10 and 11 (heaps, tries).",
        "**Week 7:** topic 12 (graph traversal and grids), then topic 13 (advanced graphs: Dijkstra, union-find, topological sort).",
        "**Week 8:** topic 14 (greedy) and topic 15 (DP I); mock interview focused on DP.",
        "**Week 9:** topic 16 (DP II): knapsack, strings, intervals, bitmasks.",
        "**Week 10:** topic 17 (advanced data structures) and topic 18 (design problems).",
        "**Week 11:** mixed practice: the core list (chapter 8), two timed mocks, review every problem you got wrong.",
        "**Week 12:** polish: behavioural stories, edge-case checklist drills, final mocks, light review; rest the day before.",
    ],
    patterns=P,
)
