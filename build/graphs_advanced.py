"""Content for topic 13: Advanced graphs."""

P = []

# ---------------------------------------------------------------- 1
P.append(dict(
    title="Topological sort: Kahn's algorithm and DFS", tier="hot", sim="kahn", oneline="repeatedly take a vertex with no unmet prerequisites",
    why="Ordering tasks with dependencies, and detecting impossible ones", signature="LC 210 / 2115",
    when="Items depend on each other (a DAG) and you need a valid order, the order's existence, or the longest dependency chain.",
    detect="\"course schedule II\" · \"build order\" · \"alien dictionary\" · \"find all possible recipes\" · \"parallel courses\" · \"sort with dependencies\".",
    intuition="Getting dressed: socks before shoes, shirt before jacket. Any item with **nothing left to wait for** can be done now. Do one, cross it off, and some other items may become free. Repeat. If you run out of free items while some remain, they are waiting on each other in a circle: no valid order exists. The count of unmet prerequisites of a vertex is its **in-degree**.",
    brute="Trying all n! orderings is hopeless. Kahn's algorithm finds an order in O(V + E) by always taking a vertex whose in-degree has dropped to 0.",
    idea="Compute `indeg[v]`. Queue all vertices with `indeg == 0`. Pop `u`, append to the order, and for each edge `u → v` decrement `indeg[v]`; when it hits 0, enqueue `v`. If the order has fewer than `V` vertices there is a cycle. The DFS alternative outputs vertices in **reverse finishing order**.",
    steps=["Build `adj` and `indeg`.", "Queue every vertex with `indeg == 0`.", "Pop `u`; add it to `order`; decrement each successor's `indeg`; enqueue those that reach 0.", "`order.size() == V` ⇒ valid order; otherwise a cycle exists."],
    trace_title="edges `5→2, 5→0, 4→0, 4→1, 2→3, 3→1`",
    trace="""in-degrees: 0:2 1:2 2:1 3:1 4:0 5:0     queue [4,5]
pop 4 -> 0:1 1:1
pop 5 -> 2:0 0:0        queue [2,0]
pop 2 -> 3:0            queue [0,3]
pop 0                   queue [3]
pop 3 -> 1:0 ; pop 1
order 4 5 2 0 3 1""",
    code=[("Kahn's algorithm (BFS)",
           """List<List<Integer>> g = new ArrayList<>();
int[] indeg = new int[n];
for (int i = 0; i < n; i++) g.add(new ArrayList<>());
for (int[] e : edges) { g.get(e[0]).add(e[1]); indeg[e[1]]++; }          // e[0] must come before e[1]
Queue<Integer> q = new ArrayDeque<>();
for (int i = 0; i < n; i++) if (indeg[i] == 0) q.add(i);
List<Integer> order = new ArrayList<>();
while (!q.isEmpty()) {
    int u = q.poll();
    order.add(u);
    for (int v : g.get(u)) if (--indeg[v] == 0) q.add(v);
}
return order.size() == n ? order : new ArrayList<>();                     // empty = cycle""",
           """from collections import deque
g = [[] for _ in range(n)]
indeg = [0] * n
for a, b in edges:                                   # a must come before b
    g[a].append(b)
    indeg[b] += 1
q = deque(i for i in range(n) if indeg[i] == 0)
order = []
while q:
    u = q.popleft()
    order.append(u)
    for v in g[u]:
        indeg[v] -= 1
        if indeg[v] == 0:
            q.append(v)
return order if len(order) == n else []              # empty = cycle"""),
          ("DFS version: reverse post-order",
           """int[] state = new int[n];                              // 0 white, 1 grey, 2 black
Deque<Integer> stack = new ArrayDeque<>();
boolean dfs(int u) {
    state[u] = 1;
    for (int v : g.get(u)) {
        if (state[v] == 1) return false;                   // cycle
        if (state[v] == 0 && !dfs(v)) return false;
    }
    state[u] = 2;
    stack.push(u);                                         // pushed AFTER all its successors
    return true;
}
// for each white u: if (!dfs(u)) return cycle; order = stack from top to bottom""",
           """state = [0] * n
post = []
def dfs(u):
    state[u] = 1
    for v in g[u]:
        if state[v] == 1 or (state[v] == 0 and not dfs(v)):
            return False                                  # cycle
    state[u] = 2
    post.append(u)                                        # after all its successors
    return True
ok = all(state[u] != 0 or dfs(u) for u in range(n))
order = post[::-1] if ok else []""")],
    complexity="O(V + E) time, O(V + E) space.",
    traps=["Edge direction: `a → b` means a before b. In Course Schedule `[a, b]` means **b before a**; reverse accordingly.", "Always compare `order.size()` with `V` to detect cycles.",
           "Use a queue for BFS order and a min-heap instead of a queue when the **lexicographically smallest** order is needed.", "The topological order is generally not unique."],
    variants=["Longest path in a DAG / parallel courses: process in topological order with `dp[v] = max(dp[u] + 1)`.", "Alien dictionary: derive edges from adjacent words, then topologically sort letters.", "Find all possible recipes: ingredients are indegree-0 sources."],
    notuse="Graphs with cycles (use SCC condensation first) or when only reachability is needed.",
    problems=[
        (207, "Course Schedule", "M", "course-schedule", "Can all courses be taken? Kahn: processed count == n", "O(V + E) / O(V + E)"),
        (210, "Course Schedule II", "M", "course-schedule-ii", "Return Kahn's order if it contains all courses", "O(V + E) / O(V + E)"),
        (2115, "Find All Possible Recipes from Given Supplies", "M", "find-all-possible-recipes-from-given-supplies", "Recipes depend on ingredients: Kahn from supplies", "O(V + E) / O(V + E)"),
        (851, "Loud and Rich", "M", "loud-and-rich", "DFS/Kahn over the 'richer than' graph keeping the quietest", "O(V + E) / O(V + E)"),
        (1857, "Largest Color Value in a Directed Graph", "H", "largest-color-value-in-a-directed-graph", "DP over topological order: count per colour", "O(26(V + E)) / O(26V)"),
        (1203, "Sort Items by Groups Respecting Dependencies", "H", "sort-items-by-groups-respecting-dependencies", "Two-level topological sort: groups, then items", "O(V + E) / O(V + E)"),
    ]))

# ---------------------------------------------------------------- 2
P.append(dict(
    title="Union-Find (disjoint set union)", tier="hot", sim="dsu", oneline="each set is a tree; the root is its name",
    why="Near-constant-time \"are these connected?\" under merging", signature="LC 547 / 990",
    when="Elements are repeatedly merged into groups and you ask whether two elements are in the same group.",
    detect="\"connected components as edges arrive\" · \"are x and y connected\" · \"equations x == y\" · \"swap indices\" · \"most stones removed\" · \"number of provinces\".",
    intuition="Each group has a leader. To find the leader of someone, follow \"who is your boss?\" up to the top (the root). To merge two groups, make one leader report to the other. Two refinements make it nearly instant: attach the **smaller** group under the larger (**union by size**) so chains stay short, and after finding a leader point everyone on the path **directly at it** (**path compression**).",
    brute="Recomputing connectivity with a BFS after every new edge costs O(V + E) each. Union-find answers each query in effectively O(1) (inverse Ackermann).",
    idea="`parent[i] = i` initially. `find(x)`: climb to the root, compressing the path. `union(a, b)`: find both roots; if equal return false (already connected); else attach the smaller tree under the larger and add sizes. Components = `n − successful unions`.",
    steps=["`parent[i] = i`, `size[i] = 1`.", "`find(x)`: while `parent[x] != x`: `parent[x] = parent[parent[x]]`, `x = parent[x]`.", "`union(a, b)`: `ra = find(a)`, `rb = find(b)`; if `ra == rb` return false; attach smaller to larger.", "Count components by decrementing on each successful union."],
    trace_title="6 elements",
    trace="""union(0,1): 1 -> 0
union(2,3): 3 -> 2
union(1,3): roots 0 and 2, same size: 2 -> 0
find(3): 3 -> 2 -> 0 ; compress: 3 -> 0
union(4,5): 5 -> 4
sets {0,1,2,3} {4,5}  components = 6 - 4 = 2""",
    code=[("union-find with path compression and union by size",
           """class DSU {
    int[] parent, size; int components;
    DSU(int n) {
        parent = new int[n]; size = new int[n]; components = n;
        for (int i = 0; i < n; i++) { parent[i] = i; size[i] = 1; }
    }
    int find(int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }   // path halving
        return x;
    }
    boolean union(int a, int b) {
        int ra = find(a), rb = find(b);
        if (ra == rb) return false;                         // already in the same set
        if (size[ra] < size[rb]) { int t = ra; ra = rb; rb = t; }
        parent[rb] = ra; size[ra] += size[rb]; components--;
        return true;
    }
}""",
           """class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.components = n
    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]     # path halving
            x = self.parent[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                                      # already in the same set
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        self.components -= 1
        return True"""),
          ("satisfiability of equations: union the '==' pairs, then check '!='",
           """DSU d = new DSU(26);
for (String e : eq) if (e.charAt(1) == '=') d.union(e.charAt(0) - 'a', e.charAt(3) - 'a');
for (String e : eq) if (e.charAt(1) == '!' && d.find(e.charAt(0) - 'a') == d.find(e.charAt(3) - 'a')) return false;
return true;""",
           """d = DSU(26)
for e in eq:
    if e[1] == '=':
        d.union(ord(e[0]) - 97, ord(e[3]) - 97)
for e in eq:
    if e[1] == '!' and d.find(ord(e[0]) - 97) == d.find(ord(e[3]) - 97):
        return False
return True""")],
    complexity="O(α(n)) ≈ O(1) per operation, O(n) space.",
    traps=["Always union the **roots** (`find(a)`, `find(b)`), not the elements themselves.", "Without union by size / rank and compression, a chain makes `find` O(n).",
           "`union` returning a boolean is how you detect cycles and count merges.", "Map arbitrary keys (strings, coordinates) to integer ids first."],
    variants=["Weighted union-find for ratios (Evaluate Division).", "Rollback union-find for offline dynamic connectivity.", "Union-find on grid cells (`r * C + c`) for islands as land is added."],
    notuse="Edge **deletions** (union-find cannot split sets) or when you also need paths between nodes (BFS/DFS).",
    problems=[
        (547, "Number of Provinces", "M", "number-of-provinces", "Union each connected pair; components remain", "O(n²·α) / O(n)"),
        (990, "Satisfiability of Equality Equations", "M", "satisfiability-of-equality-equations", "Union '==' pairs, then verify '!=' pairs", "O(n·α) / O(1)"),
        (1202, "Smallest String With Swaps", "M", "smallest-string-with-swaps", "Union swappable indices; sort letters within each set", "O(n log n) / O(n)"),
        (947, "Most Stones Removed with Same Row or Column", "M", "most-stones-removed-with-same-row-or-column", "Union rows with columns; answer = stones − components", "O(n·α) / O(n)"),
    ]))

# ---------------------------------------------------------------- 3
P.append(dict(
    title="Dijkstra: weighted shortest paths", tier="hot", sim="dijkstra2", oneline="finalise the nearest unfinished vertex, then relax its edges",
    why="The standard answer to \"cheapest path\" with non-negative weights", signature="LC 743 / 1976",
    when="Edges have non-negative costs and you need the cheapest path from a source, or counts of cheapest paths.",
    detect="\"network delay time\" · \"cheapest path\" · \"number of ways to arrive at destination\" · \"minimum obstacle removal\" · \"restricted paths\".",
    intuition="Water spilling from the source along pipes of different lengths: it reaches the nearest junctions first. The next junction to be \"reached for good\" is the one with the smallest tentative distance, because any other route to it would have to pass through a junction that is farther away already (and weights cannot be negative). After finalising a vertex, check whether going through it shortens its neighbours (**relaxation**).",
    brute="Bellman-Ford relaxes every edge V times: O(V·E). With a priority queue ordering vertices by tentative distance, Dijkstra needs O((V + E) log V).",
    idea="`dist[src] = 0`; heap of `(dist, vertex)`. Pop the smallest; skip if stale (`d > dist[u]`); for each edge `(u, v, w)`: if `d + w < dist[v]` update and push. To **count** shortest paths keep `ways[v]`: add `ways[u]` when equal, reset to `ways[u]` when strictly better.",
    steps=["Initialise all distances to ∞, source 0, heap with `(0, src)`.", "Pop `(d, u)`; ignore it if `d > dist[u]`.", "Relax each outgoing edge; push improved neighbours.", "Stop when the heap is empty (or the target is popped)."],
    trace_title="edges A-B 4, A-C 1, C-B 2, B-D 1, C-D 5, D-E 3",
    trace="""A=0
finalise A: B=4, C=1
finalise C: B=3 (4 -> 3), D=6
finalise B: D=4 (6 -> 4)
finalise D: E=7
shortest tree: A-C, C-B, B-D, D-E""",
    code=[("Dijkstra with a path-count and 0-1 BFS variant",
           """long[] dist = new long[n]; Arrays.fill(dist, Long.MAX_VALUE); dist[src] = 0;
long[] ways = new long[n]; ways[src] = 1;
PriorityQueue<long[]> pq = new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0]));
pq.add(new long[]{0, src});
while (!pq.isEmpty()) {
    long[] cur = pq.poll(); long d = cur[0]; int u = (int) cur[1];
    if (d > dist[u]) continue;
    for (int[] e : g[u]) {                                  // e = {v, w}
        long nd = d + e[1];
        if (nd < dist[e[0]]) { dist[e[0]] = nd; ways[e[0]] = ways[u]; pq.add(new long[]{nd, e[0]}); }
        else if (nd == dist[e[0]]) ways[e[0]] = (ways[e[0]] + ways[u]) % MOD;      // another shortest path
    }
}""",
           """import heapq
INF = float('inf')
dist = [INF] * n; dist[src] = 0
ways = [0] * n; ways[src] = 1
heap = [(0, src)]
while heap:
    d, u = heapq.heappop(heap)
    if d > dist[u]:
        continue
    for v, w in g[u]:
        nd = d + w
        if nd < dist[v]:
            dist[v], ways[v] = nd, ways[u]
            heapq.heappush(heap, (nd, v))
        elif nd == dist[v]:
            ways[v] = (ways[v] + ways[u]) % MOD                      # another shortest path"""),
          ("0-1 BFS: edge weights are only 0 or 1 (deque instead of a heap)",
           """Deque<int[]> dq = new ArrayDeque<>();
int[] dist = new int[n]; Arrays.fill(dist, Integer.MAX_VALUE); dist[src] = 0;
dq.addFirst(new int[]{src, 0});
while (!dq.isEmpty()) {
    int[] cur = dq.pollFirst(); int u = cur[0];
    if (cur[1] > dist[u]) continue;
    for (int[] e : g[u]) {                                  // e = {v, w}, w is 0 or 1
        if (dist[u] + e[1] < dist[e[0]]) {
            dist[e[0]] = dist[u] + e[1];
            if (e[1] == 0) dq.addFirst(new int[]{e[0], dist[e[0]]});   // free move: front
            else dq.addLast(new int[]{e[0], dist[e[0]]});             // cost 1: back
        }
    }
}""",
           """from collections import deque
dist = [float('inf')] * n; dist[src] = 0
dq = deque([src])
while dq:
    u = dq.popleft()
    for v, w in g[u]:                                       # w is 0 or 1
        if dist[u] + w < dist[v]:
            dist[v] = dist[u] + w
            if w == 0:
                dq.appendleft(v)                            # free move: front
            else:
                dq.append(v)                                # cost 1: back""")],
    complexity="O((V + E) log V) with a binary heap; 0-1 BFS is O(V + E).",
    traps=["Negative edge weights break the proof: use Bellman-Ford.", "Skip stale heap entries (`d > dist[u]`).",
           "Use `long` for distances and for path counts under a modulus.", "Counting paths: handle the `==` case **and** reset on strictly better."],
    variants=["Minimum obstacle removal / min cost of changing arrows: grid with 0/1 edge costs → 0-1 BFS.", "Restricted paths: Dijkstra from the target, then DP over decreasing distance.", "Dijkstra with state (position, fuel / stops) when the cost depends on more than the vertex."],
    notuse="Unweighted graphs (BFS), negative weights (Bellman-Ford), all-pairs (Floyd-Warshall).",
    problems=[
        (743, "Network Delay Time", "M", "network-delay-time", "Dijkstra from k; answer is the largest distance", "O(E log V) / O(V + E)"),
        (1976, "Number of Ways to Arrive at Destination", "M", "number-of-ways-to-arrive-at-destination", "Dijkstra plus a path counter modulo 10⁹+7", "O(E log V) / O(V + E)"),
        (1786, "Number of Restricted Paths from First to Last Node", "M", "number-of-restricted-paths-from-first-to-last-node", "Dijkstra from n, then DP over strictly decreasing distance", "O(E log V) / O(V + E)"),
        (2290, "Minimum Obstacle Removal to Reach Corner", "H", "minimum-obstacle-removal-to-reach-corner", "0-1 BFS: obstacle cells cost 1", "O(m·n) / O(m·n)"),
        (1368, "Minimum Cost to Make at Least One Valid Path in a Grid", "H", "minimum-cost-to-make-at-least-one-valid-path-in-a-grid", "0-1 BFS: following the arrow costs 0, changing costs 1", "O(m·n) / O(m·n)"),
    ]))

# ---------------------------------------------------------------- 4
P.append(dict(
    title="Bellman-Ford and Floyd-Warshall", tier="hot", sim="bellman", oneline="relax every edge repeatedly; or try every intermediate vertex",
    why="Negative weights, edge-count limits and all-pairs distances", signature="LC 787 / 1334",
    when="Weights may be negative, the path may use at most K edges, or you need distances between every pair of vertices.",
    detect="\"cheapest flights within K stops\" · \"negative cycle\" · \"city with the smallest number of neighbours within a threshold\" · \"all pairs shortest paths\" · \"transitive closure\".",
    intuition="Bellman-Ford: a shortest path uses at most V − 1 edges, so after round `i` every shortest path with at most `i` edges is correct. Just keep relaxing all edges V − 1 times. Floyd-Warshall: ask for each pair (i, j) whether going **through** vertex k is cheaper; try k = 0, 1, 2, ... and the table ends up holding all shortest distances (dynamic programming over which intermediate vertices are allowed).",
    brute="Running Dijkstra from every vertex is O(V·E log V) and fails with negative edges. Floyd-Warshall is O(V³) but trivially simple for small V (≤ 400).",
    idea="Bellman-Ford: repeat V − 1 times: for each edge `(u, v, w)`: `dist[v] = min(dist[v], dist[u] + w)` (use a **copy** of the previous round to limit the path to K edges). A V-th round that still improves something proves a negative cycle. Floyd-Warshall: `for k: for i: for j: d[i][j] = min(d[i][j], d[i][k] + d[k][j])`.",
    steps=["Bellman-Ford: `dist[src] = 0`, everything else ∞.", "Loop `V − 1` times (or `K + 1` for at most K stops): relax all edges.", "Check one more round: any improvement means a negative cycle.", "Floyd-Warshall: initialise `d` from edges, `d[i][i] = 0`; triple loop with `k` outermost."],
    trace_title="CLRS example (5 vertices, negative edges)",
    trace="""round 1: a=6 b=7  then a->d: d=2, b->c: c=4, c->a: a=2 ...
round 2: d=-2 ...
round 3-4: no change (converged)
final: s=0 a=2 b=7 c=4 d=-2""",
    code=[("Bellman-Ford limited to K stops (cheapest flights)",
           """int[] dist = new int[n]; Arrays.fill(dist, Integer.MAX_VALUE); dist[src] = 0;
for (int i = 0; i <= k; i++) {                         // at most k + 1 edges
    int[] next = dist.clone();                          // use the PREVIOUS round only
    for (int[] f : flights) {                           // {from, to, price}
        if (dist[f[0]] != Integer.MAX_VALUE && dist[f[0]] + f[2] < next[f[1]])
            next[f[1]] = dist[f[0]] + f[2];
    }
    dist = next;
}
return dist[dst] == Integer.MAX_VALUE ? -1 : dist[dst];""",
           """INF = float('inf')
dist = [INF] * n
dist[src] = 0
for _ in range(k + 1):                                  # at most k + 1 edges
    nxt = dist[:]                                       # use the PREVIOUS round only
    for u, v, w in flights:
        if dist[u] + w < nxt[v]:
            nxt[v] = dist[u] + w
    dist = nxt
return -1 if dist[dst] == INF else dist[dst]"""),
          ("Floyd-Warshall (all pairs)",
           """int INF = 1_000_000_000;
int[][] d = new int[n][n];
for (int[] row : d) Arrays.fill(row, INF);
for (int i = 0; i < n; i++) d[i][i] = 0;
for (int[] e : edges) { d[e[0]][e[1]] = Math.min(d[e[0]][e[1]], e[2]); d[e[1]][e[0]] = Math.min(d[e[1]][e[0]], e[2]); }
for (int k = 0; k < n; k++)                              // k = allowed intermediate vertex: OUTERMOST loop
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            if (d[i][k] + d[k][j] < d[i][j]) d[i][j] = d[i][k] + d[k][j];""",
           """INF = float('inf')
d = [[INF] * n for _ in range(n)]
for i in range(n):
    d[i][i] = 0
for u, v, w in edges:
    d[u][v] = min(d[u][v], w)
    d[v][u] = min(d[v][u], w)                            # undirected
for k in range(n):                                       # k = allowed intermediate vertex: OUTERMOST loop
    for i in range(n):
        for j in range(n):
            if d[i][k] + d[k][j] < d[i][j]:
                d[i][j] = d[i][k] + d[k][j]""")],
    complexity="Bellman-Ford O(V·E) time, O(V) space. Floyd-Warshall O(V³) time, O(V²) space.",
    traps=["For \"at most K stops\" copy the distance array each round, otherwise a single round can chain several edges.", "Floyd-Warshall needs `k` as the **outermost** loop.",
           "Use a sentinel that does not overflow when added (`INF = 10⁹` with `int`, or check for INF).", "Dijkstra with a plain `visited` array fails for the K-stops variant; the state needs the stop count."],
    variants=["Detect a negative cycle: a relaxation in round V.", "SPFA: queue-based Bellman-Ford, faster in practice.", "Transitive closure: Floyd-Warshall with booleans (`reach[i][j] |= reach[i][k] && reach[k][j]`)."],
    notuse="Large graphs with non-negative weights (Dijkstra) or unweighted graphs (BFS).",
    problems=[
        (787, "Cheapest Flights Within K Stops", "M", "cheapest-flights-within-k-stops", "Bellman-Ford for K + 1 rounds using the previous round's copy", "O(K·E) / O(V)"),
        (1334, "Find the City With the Smallest Number of Neighbors at a Threshold Distance", "M", "find-the-city-with-the-smallest-number-of-neighbors-at-a-threshold-distance", "Floyd-Warshall, count cities within the threshold", "O(V³) / O(V²)"),
        (1462, "Course Schedule IV", "M", "course-schedule-iv", "Boolean Floyd-Warshall for prerequisite reachability", "O(V³) / O(V²)"),
        (1514, "Path with Maximum Probability", "M", "path-with-maximum-probability", "Bellman-Ford or Dijkstra with multiplication", "O(V·E) / O(V)"),
    ]))

# ---------------------------------------------------------------- 5
P.append(dict(
    title="Minimum spanning tree: Kruskal and Prim", tier="hot", sim="kruskal", oneline="cheapest edges first, skipping any that close a cycle",
    why="Connect everything as cheaply as possible", signature="LC 1584 / 1489",
    when="You must connect all vertices with minimum total edge weight (networks, cables, roads).",
    detect="\"min cost to connect all points\" · \"minimum spanning tree\" · \"connect cities / pipes\" · \"critical and pseudo-critical edges\" · \"remove edges but keep connectivity\".",
    intuition="Laying cable between towns with a fixed budget: always build the cheapest link that does not just duplicate a connection you already have. If two towns are already connected (directly or through others), another cable between them is wasted money: skip it. That is Kruskal's rule, and union-find tells you instantly whether two towns are already connected. A spanning tree of V vertices has exactly V − 1 edges.",
    brute="Trying all subsets of edges is exponential. The greedy choice (cheapest safe edge) is provably optimal for MST (the cut property) and costs O(E log E).",
    idea="Kruskal: sort edges by weight; for each edge `union(u, v)`; if it succeeded add the weight; stop at `V − 1` edges. Prim: grow one tree from a start vertex; repeatedly add the cheapest edge leaving the tree using a min-heap.",
    steps=["Sort edges ascending by weight.", "DSU over the vertices.", "For each edge: if `union` merges two different sets → keep it, add its weight.", "If fewer than `V − 1` edges were kept, the graph is disconnected."],
    trace_title="edges AB1 BC2 AC3 CD4 BD5 DE6 CE7",
    trace="""AB 1  accept      BC 2  accept
AC 3  skip (A and C already connected)
CD 4  accept      BD 5  skip (cycle)
DE 6  accept      CE 7  skip
MST = AB BC CD DE, weight 1+2+4+6 = 13""",
    code=[("Kruskal with union-find",
           """Arrays.sort(edges, (a, b) -> a[2] - b[2]);                // {u, v, w}
DSU dsu = new DSU(n);
int total = 0, used = 0;
for (int[] e : edges) {
    if (dsu.union(e[0], e[1])) { total += e[2]; used++; }   // joins two different components
    if (used == n - 1) break;
}
return used == n - 1 ? total : -1;                          // -1: graph not connected""",
           """edges.sort(key=lambda e: e[2])                              # (u, v, w)
dsu = DSU(n)
total = used = 0
for u, v, w in edges:
    if dsu.union(u, v):                                       # joins two different components
        total += w
        used += 1
        if used == n - 1:
            break
return total if used == n - 1 else -1                         # -1: graph not connected"""),
          ("Prim's algorithm with a min-heap (min cost to connect all points)",
           """int n = pts.length, total = 0, taken = 0;
boolean[] in = new boolean[n];
PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);       // {cost, point}
pq.add(new int[]{0, 0});
while (taken < n) {
    int[] cur = pq.poll();
    if (in[cur[1]]) continue;
    in[cur[1]] = true; total += cur[0]; taken++;
    for (int j = 0; j < n; j++)
        if (!in[j]) pq.add(new int[]{Math.abs(pts[cur[1]][0] - pts[j][0]) + Math.abs(pts[cur[1]][1] - pts[j][1]), j});
}
return total;""",
           """import heapq
n = len(pts)
in_tree = [False] * n
heap = [(0, 0)]                                                # (cost to attach, point)
total = taken = 0
while taken < n:
    cost, u = heapq.heappop(heap)
    if in_tree[u]:
        continue
    in_tree[u] = True
    total += cost
    taken += 1
    for v in range(n):
        if not in_tree[v]:
            heapq.heappush(heap, (abs(pts[u][0] - pts[v][0]) + abs(pts[u][1] - pts[v][1]), v))
return total""")],
    complexity="Kruskal O(E log E). Prim with a heap O(E log V); for dense geometric graphs an O(V²) Prim without a heap is simplest.",
    traps=["MST requires an **undirected** connected graph; for directed graphs use arborescence algorithms.", "Check `used == V − 1` to detect a disconnected graph.",
           "Equal weights make the MST non-unique; critical / pseudo-critical edge problems analyse that.", "Do not confuse MST (total weight) with shortest paths (distance from a source)."],
    variants=["Maximum spanning tree: sort descending.", "Minimum bottleneck path: the MST path between two vertices.", "Second-best MST, or remove max edges while keeping the graph traversable (two DSUs for two travellers)."],
    notuse="Shortest paths from a source (Dijkstra) or directed graphs.",
    problems=[
        (1584, "Min Cost to Connect All Points", "M", "min-cost-to-connect-all-points", "Kruskal over all Manhattan edges, or Prim O(n²)", "O(n² log n) / O(n²)"),
        (1579, "Remove Max Number of Edges to Keep Graph Fully Traversable", "H", "remove-max-number-of-edges-to-keep-graph-fully-traversable", "Two DSUs (Alice, Bob); take shared edges first", "O(E·α) / O(V)"),
        (1697, "Checking Existence of Edge Length Limited Paths", "H", "checking-existence-of-edge-length-limited-paths", "Offline: sort edges and queries, union edges below each limit", "O((E + Q) log) / O(V + Q)"),
        (1489, "Find Critical and Pseudo-Critical Edges in Minimum Spanning Tree", "H", "find-critical-and-pseudo-critical-edges-in-minimum-spanning-tree", "Recompute the MST without / with each edge", "O(E²·α) / O(V)"),
    ]))

# ---------------------------------------------------------------- 6
P.append(dict(
    title="Union-Find applications: cycles, merging and grouping", tier="sec", sim="redundant", oneline="union(u, v) returning false means the edge closes a cycle",
    why="Turns many \"are they already connected?\" puzzles into a few lines", signature="LC 684 / 721 / 399",
    when="You add relationships one by one and need to detect redundancy, merge records, or answer queries about equivalence.",
    detect="\"redundant connection\" · \"accounts merge\" · \"evaluate division\" · \"largest component size by common factor\" · \"making a large island\" · \"number of islands II\".",
    intuition="Adding edges to a forest never forms a cycle as long as each new edge joins **two different** trees. The first edge whose endpoints already share a root is the one that closes a cycle. The same \"already connected?\" question detects duplicates in merging problems: if two accounts share an email, union them; the final roots are the merged accounts.",
    brute="Running a DFS after each added edge to look for a cycle is O(V·(V + E)). With union-find each edge is processed in near-constant time.",
    idea="Create a DSU over ids (map emails, strings or coordinates to integers first). Union related items; the first failing union is the redundant edge. Afterwards group elements by `find(x)` to read off the merged sets. Weighted DSU stores a ratio to the root for equations like `a / b = 2`.",
    steps=["Assign integer ids to the items.", "For each relation: `union(a, b)`; if it returns false, record the edge as redundant.", "To output groups: bucket every item by `find(item)`.", "Weighted DSU: store `weight[x] = x / parent[x]` and multiply along the path."],
    trace_title="edges 1-2, 2-3, 3-4, 1-4, 1-5",
    trace="""1-2 union ok   2-3 union ok   3-4 union ok
1-4 : find(1) == find(4)  -> same set, REDUNDANT
answer [1,4]""",
    code=[("redundant connection (undirected)",
           """DSU dsu = new DSU(edges.length + 1);
for (int[] e : edges)
    if (!dsu.union(e[0], e[1])) return e;          // endpoints were already connected
return new int[0];""",
           """dsu = DSU(len(edges) + 1)
for u, v in edges:
    if not dsu.union(u, v):
        return [u, v]                              # endpoints were already connected"""),
          ("accounts merge (group emails by root)",
           """Map<String, Integer> id = new HashMap<>(); Map<String, String> owner = new HashMap<>();
DSU dsu = new DSU(accounts.size());
for (int i = 0; i < accounts.size(); i++)
    for (String mail : accounts.get(i).subList(1, accounts.get(i).size())) {
        owner.put(mail, accounts.get(i).get(0));
        if (id.containsKey(mail)) dsu.union(i, id.get(mail)); else id.put(mail, i);
    }
Map<Integer, TreeSet<String>> groups = new HashMap<>();
for (String mail : id.keySet()) groups.computeIfAbsent(dsu.find(id.get(mail)), k -> new TreeSet<>()).add(mail);""",
           """from collections import defaultdict
dsu = DSU(len(accounts))
owner, first_seen = {}, {}
for i, acc in enumerate(accounts):
    for mail in acc[1:]:
        owner[mail] = acc[0]
        if mail in first_seen:
            dsu.union(i, first_seen[mail])                    # shared email: same person
        else:
            first_seen[mail] = i
groups = defaultdict(list)
for mail, i in first_seen.items():
    groups[dsu.find(i)].append(mail)
res = [[owner[g[0]]] + sorted(g) for g in groups.values()]""")],
    complexity="O((n + m) α(n)) for n items and m relations.",
    traps=["Redundant Connection II (directed): consider vertices with two parents as well as cycles.", "Always union by **root**; mapping strings to ids first is easy to forget.",
           "Merging accounts: names can repeat for different people; merge by shared emails only.", "Evaluate division: queries on unknown variables return −1.0."],
    variants=["Largest component size by common factor: union numbers with their prime factors.", "Number of islands II: add land cells one at a time, union with land neighbours.", "Evaluate division: weighted DSU, or a graph search over ratios."],
    notuse="Deletions or \"remove an edge\" operations without offline reversal.",
    problems=[
        (684, "Redundant Connection", "M", "redundant-connection", "First edge whose endpoints already share a root", "O(n·α) / O(n)"),
        (721, "Accounts Merge", "M", "accounts-merge", "Union accounts sharing an email; group by root", "O(n·α + n log n) / O(n)"),
        (399, "Evaluate Division", "M", "evaluate-division", "Weighted union-find (or DFS over ratios)", "O((n + q)·α) / O(n)"),
        (685, "Redundant Connection II", "H", "redundant-connection-ii", "Handle a vertex with two parents plus a cycle", "O(n·α) / O(n)"),
        (952, "Largest Component Size by Common Factor", "H", "largest-component-size-by-common-factor", "Union each number with its prime factors", "O(n√max) / O(max)"),
    ]))

# ---------------------------------------------------------------- 7
P.append(dict(
    title="Bridges and articulation points (Tarjan low-link)", tier="sec", sim="bridges", oneline="low-link: how far up the tree can a subtree climb with one back edge?",
    why="Finds the fragile points of a network in a single DFS", signature="LC 1192",
    when="You need edges (bridges) or vertices (articulation points) whose removal disconnects an undirected graph.",
    detect="\"critical connections in a network\" · \"single point of failure\" · \"articulation point\" · \"minimum days to disconnect\".",
    intuition="In the DFS tree, a subtree hangs below an edge. If some vertex in that subtree has a **back edge** to the parent's side (an ancestor), the subtree is also connected the other way round, so cutting the tree edge does not disconnect it. If the subtree can climb no higher than its own top vertex, the tree edge is the only link: a **bridge**. `low[v]` is the smallest discovery time that the subtree of `v` can reach with at most one back edge.",
    brute="Remove each edge and test connectivity: O(E·(V + E)). Tarjan's low-link DFS finds all bridges in O(V + E).",
    idea="DFS with `disc[u]` (discovery time) and `low[u]`. For each neighbour `v ≠ parent`: if visited, `low[u] = min(low[u], disc[v])` (back edge); else recurse and set `low[u] = min(low[u], low[v])`. Tree edge `(u, v)` is a **bridge** iff `low[v] > disc[u]`. Articulation point `u`: `low[v] ≥ disc[u]` for some child `v` (non-root), or the root has ≥ 2 DFS children.",
    steps=["`disc`, `low` arrays, `timer`.", "Enter `u`: `disc[u] = low[u] = ++timer`.", "Skip the parent; visited neighbour → update `low` with `disc`; unvisited → recurse then update `low` with the child's `low`.", "After the child: `low[v] > disc[u]` ⇒ bridge."],
    trace_title="edges 0-1, 1-2, 2-0, 1-3, 3-4",
    trace="""0: d0 l0  ->  1: d1  ->  2: d2, back edge to 0 => l2 = 0
back at 1: l1 = 0
1 -> 3: d3 -> 4: d4 ; l4 = 4 > d3 : bridge 3-4
back at 1: l3 = 3 > d1 : bridge 1-3
bridges: 1-3, 3-4""",
    code=[("critical connections (bridges)",
           """int timer = 0; int[] disc, low; List<List<Integer>> res = new ArrayList<>();
void dfs(int u, int parent) {
    disc[u] = low[u] = ++timer;
    for (int v : g.get(u)) {
        if (v == parent) continue;
        if (disc[v] != 0) low[u] = Math.min(low[u], disc[v]);                 // back edge
        else {
            dfs(v, u);
            low[u] = Math.min(low[u], low[v]);
            if (low[v] > disc[u]) res.add(Arrays.asList(u, v));               // subtree cannot climb above u
        }
    }
}""",
           """import sys
sys.setrecursionlimit(10**6)
disc, low, timer, res = [0] * n, [0] * n, [0], []
def dfs(u, parent):
    timer[0] += 1
    disc[u] = low[u] = timer[0]
    for v in g[u]:
        if v == parent:
            continue
        if disc[v]:
            low[u] = min(low[u], disc[v])                       # back edge
        else:
            dfs(v, u)
            low[u] = min(low[u], low[v])
            if low[v] > disc[u]:
                res.append([u, v])                              # subtree cannot climb above u"""),
          ("articulation points",
           """void dfs(int u, int parent) {
    disc[u] = low[u] = ++timer; int children = 0;
    for (int v : g.get(u)) {
        if (v == parent) continue;
        if (disc[v] != 0) low[u] = Math.min(low[u], disc[v]);
        else {
            children++;
            dfs(v, u);
            low[u] = Math.min(low[u], low[v]);
            if (parent != -1 && low[v] >= disc[u]) isCut[u] = true;           // non-root rule
        }
    }
    if (parent == -1 && children >= 2) isCut[u] = true;                       // root rule
}""",
           """def dfs(u, parent):
    timer[0] += 1
    disc[u] = low[u] = timer[0]
    children = 0
    for v in g[u]:
        if v == parent:
            continue
        if disc[v]:
            low[u] = min(low[u], disc[v])
        else:
            children += 1
            dfs(v, u)
            low[u] = min(low[u], low[v])
            if parent != -1 and low[v] >= disc[u]:
                is_cut[u] = True                                  # non-root rule
    if parent == -1 and children >= 2:
        is_cut[u] = True                                          # root rule""")],
    complexity="O(V + E) time, O(V) recursion depth.",
    traps=["Skip only the **parent** edge (use edge ids when there are parallel edges).", "Bridge test uses `>` (strict); articulation test uses `≥`.",
           "The DFS root is an articulation point only if it has two or more DFS children.", "Deep recursion: raise the recursion limit in Python or write the DFS iteratively."],
    variants=["Number of days to disconnect a grid island: answer is 0, 1 or 2 (check articulation points).", "2-edge-connected components: remove bridges and label components.", "Block-cut tree for biconnected components."],
    notuse="Directed graphs (use strongly connected components) or when only connectivity under random failures is needed.",
    problems=[
        (2685, "Count the Number of Complete Components", "M", "count-the-number-of-complete-components", "Components where every vertex has degree size − 1", "O(V + E) / O(V)"),
        (1568, "Minimum Number of Days to Disconnect Island", "H", "minimum-number-of-days-to-disconnect-island", "0 if disconnected, 1 if an articulation point exists, else 2", "O((mn)²) / O(mn)"),
        (1192, "Critical Connections in a Network", "H", "critical-connections-in-a-network", "Tarjan bridges with disc / low arrays", "O(V + E) / O(V + E)"),
    ]))

# ---------------------------------------------------------------- 8
P.append(dict(
    title="Strongly connected components (Kosaraju / Tarjan)", tier="sec", sim="scc", oneline="groups of vertices that all reach each other",
    why="Collapses a directed graph with cycles into a DAG you can order or run DP on", signature="LC 802 / 2360",
    when="A directed graph has cycles and you need its mutually reachable groups, or the structure that remains after contracting them.",
    detect="\"strongly connected\" · \"longest cycle in a graph\" · \"maximum employees invited\" · \"eventual safe nodes\" · 2-SAT style dependencies.",
    intuition="In a directed graph, two vertices are in the same **strongly connected component** (SCC) if each can reach the other. Contract every SCC into one node and all cycles disappear: the result is a DAG. Kosaraju's trick: vertices that finish **last** in a DFS lie in a **source** SCC; running a DFS from them in the **reversed** graph cannot escape their own SCC, so each reversed DFS tree is exactly one SCC.",
    brute="Testing mutual reachability for every pair is O(V·(V + E)). Kosaraju or Tarjan find all SCCs in O(V + E).",
    idea="Kosaraju: (1) DFS the graph, push vertices on a stack when they **finish**. (2) Build the reversed graph. (3) Pop vertices from the stack; DFS in the reversed graph from each unvisited one; the visited set is one SCC.",
    steps=["Pass 1: DFS over all vertices, record finishing order.", "Reverse all edges.", "Pass 2: for vertices in decreasing finishing time, DFS on the reversed graph; each DFS collects one SCC.", "Optional: build the condensation DAG (edges between SCC ids)."],
    trace_title="edges 0→1, 1→2, 2→0, 2→3, 3→4, 4→5, 5→3",
    trace="""pass 1 finish order: 5 4 3 2 1 0
pass 2 (reversed graph) from 0: reaches 2, 1   -> SCC {0,1,2}
from 3: reaches 5, 4                            -> SCC {3,4,5}""",
    code=[("Kosaraju's algorithm",
           """boolean[] seen = new boolean[n];
Deque<Integer> order = new ArrayDeque<>();
void dfs1(int u) { seen[u] = true; for (int v : g[u]) if (!seen[v]) dfs1(v); order.push(u); }   // push AFTER children
for (int u = 0; u < n; u++) if (!seen[u]) dfs1(u);

List<List<Integer>> rev = reversedGraph(g);
Arrays.fill(seen, false);
int sccCount = 0;
int[] comp = new int[n];
void dfs2(int u, int id) { seen[u] = true; comp[u] = id; for (int v : rev.get(u)) if (!seen[v]) dfs2(v, id); }
while (!order.isEmpty()) { int u = order.pop(); if (!seen[u]) dfs2(u, sccCount++); }    // latest finisher first""",
           """import sys
sys.setrecursionlimit(10**6)
seen, order = [False] * n, []
def dfs1(u):
    seen[u] = True
    for v in g[u]:
        if not seen[v]:
            dfs1(v)
    order.append(u)                                    # after its descendants
for u in range(n):
    if not seen[u]:
        dfs1(u)

rev = [[] for _ in range(n)]
for u in range(n):
    for v in g[u]:
        rev[v].append(u)
comp, count = [-1] * n, 0
def dfs2(u, c):
    comp[u] = c
    for v in rev[u]:
        if comp[v] == -1:
            dfs2(v, c)
for u in reversed(order):                              # latest finisher first
    if comp[u] == -1:
        dfs2(u, count)
        count += 1""")],
    complexity="O(V + E) time, O(V + E) space (reversed graph and component ids).",
    traps=["The second pass must use the **reversed** graph and the **reverse finishing order**.", "Tarjan's version needs the low-link on the DFS stack; do not mix its `low` with the bridge version.",
           "Self-loops and parallel edges do not change SCCs.", "For functional graphs (each node has one outgoing edge) cycles are easier to find by walking and colouring."],
    variants=["Condensation DAG: contract SCCs, then topological order / DP (longest path, counting).", "Longest cycle in a functional graph: record visit times while walking.", "2-SAT: variable and its negation in the same SCC ⇒ unsatisfiable."],
    notuse="Undirected graphs (connected components suffice) or when you only need to know if a cycle exists (DFS colours).",
    problems=[
        (802, "Find Eventual Safe States", "M", "find-eventual-safe-states", "Safe nodes cannot reach any cycle: reverse graph + Kahn or DFS colours", "O(V + E) / O(V + E)"),
        (2360, "Longest Cycle in a Graph", "H", "longest-cycle-in-a-graph", "Each node has ≤ 1 out-edge: walk, record visit index to size cycles", "O(V) / O(V)"),
        (2127, "Maximum Employees to Be Invited to a Meeting", "H", "maximum-employees-to-be-invited-to-a-meeting", "Cycles in a functional graph, plus chains hanging off 2-cycles", "O(V) / O(V)"),
    ]))

# ---------------------------------------------------------------- 9
P.append(dict(
    title="Eulerian paths: Hierholzer's algorithm", tier="sec", sim="euler", oneline="walk until stuck, then splice the detours in reverse",
    why="\"Use every edge exactly once\" is a distinct problem from \"visit every vertex\"", signature="LC 332 / 2097",
    when="You must traverse every edge exactly once (an itinerary, a de Bruijn sequence, arranging pairs).",
    detect="\"reconstruct itinerary\" · \"valid arrangement of pairs\" · \"cracking the safe\" · \"use all tickets exactly once\" · \"Eulerian path / circuit\".",
    intuition="Imagine walking along one-way roads and spraying a mark on each road you use. Keep walking along unused roads until you are stuck: the place where you are stuck must be the **end** of the whole trip. Write that place at the end of your route, step back one vertex, and if it still has unused roads, follow them as a detour. Because routes are assembled backwards, reversing the list at the end gives the full trip.",
    brute="Trying all orderings of edges is factorial. Hierholzer uses each edge once: O(E) (or O(E log E) when neighbours must be visited in sorted order).",
    idea="`dfs(u)`: while `u` has an unused outgoing edge `u → v`: remove that edge and `dfs(v)`. Then append `u` to `route`. Finally reverse `route`. A **directed Eulerian path** exists iff in/out degrees balance (one vertex with out − in = 1, one with in − out = 1, others equal) and the edges are connected.",
    steps=["Build adjacency lists (sorted for the lexicographically smallest itinerary).", "Start at the start vertex (the one with out − in = 1, or any vertex for a circuit).", "`dfs(u)`: consume edges while any remain; recurse along each.", "Append `u` after its edges are exhausted; reverse the route."],
    trace_title="edges A→B, B→C, C→A, A→D",
    trace="""dfs(A): A->B  dfs(B): B->C  dfs(C): C->A  dfs(A): A->D  dfs(D): stuck, append D
back in A: no more edges, append A ; C append ; B append ; A append
route (built backwards): D A C B A  -> reversed: A B C A D""",
    code=[("reconstruct itinerary (lexicographically smallest Eulerian path)",
           """Map<String, PriorityQueue<String>> g = new HashMap<>();
for (List<String> t : tickets) g.computeIfAbsent(t.get(0), k -> new PriorityQueue<>()).add(t.get(1));
LinkedList<String> route = new LinkedList<>();
void dfs(String u) {
    PriorityQueue<String> pq = g.get(u);
    while (pq != null && !pq.isEmpty()) dfs(pq.poll());     // consume each edge once, smallest destination first
    route.addFirst(u);                                      // add AFTER the edges are exhausted
}
// dfs("JFK"); return route;""",
           """from collections import defaultdict
g = defaultdict(list)
for a, b in sorted(tickets, reverse=True):                 # reversed so pop() yields the smallest destination
    g[a].append(b)
route = []
def dfs(u):
    while g[u]:
        dfs(g[u].pop())                                    # consume each edge once
    route.append(u)                                        # add AFTER the edges are exhausted
dfs("JFK")
return route[::-1]""")],
    complexity="O(E log E) with sorted neighbours (heap), O(E) otherwise; O(E) space.",
    traps=["Append the vertex **after** its edges are consumed, then reverse; appending on arrival gives the wrong order.", "A greedy walk without the backtracking-splice gets stuck early on dead-end branches.",
           "Check the degree conditions if the problem does not guarantee a valid path.", "Do not confuse with a **Hamiltonian** path (every vertex once), which is NP-hard."],
    variants=["Valid arrangement of pairs: find the start vertex (out − in = 1), then Hierholzer.", "Cracking the safe: Eulerian circuit in the de Bruijn graph.", "Undirected Eulerian path: all degrees even (circuit) or exactly two odd (path)."],
    notuse="When vertices (not edges) must be visited exactly once.",
    problems=[
        (332, "Reconstruct Itinerary", "H", "reconstruct-itinerary", "Hierholzer with sorted destinations", "O(E log E) / O(E)"),
        (2097, "Valid Arrangement of Pairs", "H", "valid-arrangement-of-pairs", "Find the start by degree balance, then Hierholzer", "O(E) / O(E)"),
        (753, "Cracking the Safe", "H", "cracking-the-safe", "Eulerian circuit on the de Bruijn graph", "O(k^n) / O(k^n)"),
    ]))

TOPIC = dict(
    id="graphs_advanced", file="13_graphs_advanced.html", title="Advanced Graphs — Pattern Guide",
    lead="After traversals, graphs get interesting: ordering with dependencies, merging groups, cheapest paths with and without negative weights, spanning trees, fragile points and cycles of mutual reachability. This guide covers topological sort, union-find, Dijkstra, Bellman-Ford and Floyd-Warshall, minimum spanning trees, union-find applications, bridges, strongly connected components and Eulerian paths. Each pattern has the intuition, a step-through animation on a drawn graph, Java and Python code, and a ladder of LeetCode problems.",
    mindset="Match the question to the structure: **order with dependencies** → topological sort; **are these connected as things merge** → union-find; **cheapest path** → Dijkstra (non-negative), Bellman-Ford (negative or limited edges), Floyd-Warshall (all pairs); **connect everything cheaply** → spanning tree; **what breaks if I remove this** → bridges and articulation points; **cycles in a directed graph** → strongly connected components; **use every edge once** → Eulerian path.",
    qintro="Ask these questions on every advanced graph problem:",
    questions=["**Directed or undirected? Weighted? Can weights be negative?**", "**Do I need an order, a path, a tree, or groups?**", "**Does the structure change over time (edges added) or is it static?** → union-find for merging only.",
               "**Is it a DAG?** → topological order and DP.", "**Do I need all pairs or a single source?** → Floyd-Warshall vs Dijkstra / Bellman-Ford."],
    cues=[
        ["\"prerequisites\", \"build order\", \"dependencies\"", "**P1** Topological sort"],
        ["\"connected as edges arrive\", \"equations\", \"merge groups\"", "**P2** Union-Find"],
        ["\"cheapest path\", non-negative weights", "**P3** Dijkstra"],
        ["\"negative weights\", \"at most K stops\", \"all pairs\"", "**P4** Bellman-Ford / Floyd-Warshall"],
        ["\"connect all points with minimum cost\"", "**P5** Minimum spanning tree"],
        ["\"redundant connection\", \"accounts merge\", \"evaluate division\"", "**P6** Union-Find applications"],
        ["\"critical connections\", \"articulation point\"", "**P7** Bridges (Tarjan)"],
        ["\"strongly connected\", \"mutually reachable\", cycles in digraphs", "**P8** SCC"],
        ["\"use every edge exactly once\", \"itinerary\"", "**P9** Eulerian path"],
    ],
    choose=[
        ["Valid ordering of dependent tasks", "Kahn / DFS topological sort (P1)"],
        ["Dynamic connectivity under unions", "Union-Find (P2, P6)"],
        ["Cheapest path, weights ≥ 0", "Dijkstra (P3)"],
        ["Negative weights or ≤ K edges", "Bellman-Ford (P4)"],
        ["Distances between all pairs", "Floyd-Warshall (P4)"],
        ["Cheapest way to connect everything", "Kruskal / Prim (P5)"],
        ["Fragile edges or vertices", "Tarjan low-link (P7)"],
        ["Cycles of mutual reachability", "SCC (P8)"],
        ["Traverse every edge once", "Hierholzer (P9)"],
    ],
    rule="**dependencies → topological sort; merging groups → union-find; weighted paths → Dijkstra unless negative / limited edges / all pairs; connect everything → MST; single points of failure → bridges; directed cycles → SCC.**",
    selftest=[
        ("How does Kahn's algorithm detect a cycle?", "If fewer than V vertices are output, the remaining ones always have a pending prerequisite inside the remaining set, so they lie on or behind a cycle."),
        ("What do union by size and path compression each achieve?", "Union by size keeps trees shallow (height O(log n)); path compression flattens the path after each find. Together they give amortised inverse-Ackermann time per operation."),
        ("Why does Dijkstra require non-negative weights?", "It assumes a popped vertex's distance is final; a later negative edge could create a shorter path to an already finalised vertex."),
        ("How does Bellman-Ford limit the path to at most K edges?", "Run only K rounds, and in each round relax using a copy of the previous round's distances so one round adds at most one edge."),
        ("Why is `k` the outermost loop in Floyd-Warshall?", "After processing intermediate vertices 0..k the table is correct for paths using only those intermediates; each stage builds on the previous complete stage."),
        ("State the Kruskal rule and why it works.", "Add the cheapest edge that connects two different components; by the cut property the cheapest edge crossing any cut belongs to some MST, so the greedy choice is safe."),
        ("What does `low[v] > disc[u]` mean for the tree edge (u, v)?", "The subtree of v cannot reach u or any ancestor through a back edge, so removing the edge disconnects v's subtree: it is a bridge."),
        ("Why is the Eulerian route built in reverse in Hierholzer's algorithm?", "A vertex is appended only when all its edges are used; the first vertex stuck is the true end of the trip, and detours are spliced in before it, so the list is the route backwards."),
    ],
    plan=[
        "**Day 1:** topological sort (Kahn first, then the DFS version); course schedule I and II.",
        "**Day 2:** union-find from scratch (path compression + union by size); equations and provinces.",
        "**Day 3:** Dijkstra with a heap on adjacency lists; then count shortest paths and the 0-1 BFS grid variants.",
        "**Day 4:** Bellman-Ford for K stops and Floyd-Warshall for all pairs.",
        "**Day 5:** Kruskal and Prim; union-find applications (redundant connection, accounts merge).",
        "**Day 6:** bridges / articulation points, SCCs and Hierholzer; draw each on paper before coding.",
    ],
    patterns=P,
)
