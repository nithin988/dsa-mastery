"""Content for topic 12: Graph traversal."""

P = []

# ---------------------------------------------------------------- 1
P.append(dict(
    title="Graph basics: modelling and representation", tier="hot", sim="buildgraph", oneline="vertices, edges, and the adjacency list you build first",
    why="Every graph problem starts by turning the input into something you can traverse", signature="LC 1791 / 997",
    when="The problem describes relationships between things: friends, roads, prerequisites, links.",
    detect="\"n nodes and a list of edges\" · \"connected\" · \"path exists\" · \"prerequisites\" · \"network\" · \"town judge\" · grids and word games that hide a graph.",
    intuition="A graph is just a table of who is connected to whom. Choose the table that makes the question you ask most often cheap. \"Who are the neighbours of u?\" is by far the most common, so you keep a list of neighbours for each vertex (**adjacency list**). A matrix answers \"is there an edge u–v?\" in O(1) but wastes O(V²) space on sparse graphs.",
    brute="Scanning the whole edge list to find the neighbours of a vertex costs O(E) each time, O(V·E) for a traversal. An adjacency list makes it O(deg(u)), and a full traversal O(V + E).",
    idea="Build `adj[u]` from the edge list once. Undirected edge → add both directions; directed → one. Weighted → store `(v, w)` pairs. For grids and implicit state spaces, generate neighbours on the fly instead of storing them.",
    steps=["Count vertices `n` (watch 0- vs 1-indexing).", "Create `n` empty lists.", "For each edge `(u, v)`: `adj[u].add(v)`; if undirected also `adj[v].add(u)`.", "Keep a `visited` set/array for traversals; compute in-degree / out-degree if the problem is about counts."],
    trace_title="edges `0-1, 0-2, 1-2, 2-3`",
    trace="""adj[0] = [1, 2]
adj[1] = [0, 2]
adj[2] = [0, 1, 3]
adj[3] = [2]
space O(V + E); neighbours of u in O(deg(u))""",
    code=[("adjacency list from an edge list",
           """List<List<Integer>> g = new ArrayList<>();
for (int i = 0; i < n; i++) g.add(new ArrayList<>());
for (int[] e : edges) {
    g.get(e[0]).add(e[1]);
    g.get(e[1]).add(e[0]);              // omit this line for a directed graph
}
// weighted: g.get(u).add(new int[]{v, w});""",
           """g = [[] for _ in range(n)]
for u, v in edges:
    g[u].append(v)
    g[v].append(u)                      # omit this line for a directed graph
# weighted: g[u].append((v, w))"""),
          ("degrees: find the town judge (trusts nobody, trusted by everyone else)",
           """int[] score = new int[n + 1];
for (int[] t : trust) { score[t[0]]--; score[t[1]]++; }      // out-edge counts -1, in-edge counts +1
for (int i = 1; i <= n; i++) if (score[i] == n - 1) return i;
return -1;""",
           """score = [0] * (n + 1)
for a, b in trust:
    score[a] -= 1                                           # out-edge counts -1
    score[b] += 1                                           # in-edge counts +1
for i in range(1, n + 1):
    if score[i] == n - 1:
        return i
return -1""")],
    complexity="Build: O(V + E) time and space. Matrix: O(V²) space.",
    traps=["Vertices numbered from 1 need an array of size `n + 1`.", "Undirected means **two** adjacency entries per edge; forgetting one makes the graph look directed.",
           "Duplicate edges and self-loops may appear: decide whether they matter.", "A disconnected graph needs the traversal started from **every** unvisited vertex."],
    variants=["Adjacency matrix when `n ≤ 500` and the input is a matrix (number of provinces).", "Edge list for algorithms that sort edges (Kruskal).", "Indegree array for topological sort and for \"vertices that reach all nodes\" (indegree 0)."],
    notuse="If the input is already a grid, do not build a list: compute `(r ± 1, c ± 1)` neighbours directly.",
    problems=[
        (1791, "Find Center of Star Graph", "E", "find-center-of-star-graph", "The center appears in every edge: check the first two edges", "O(1) / O(1)"),
        (997, "Find the Town Judge", "E", "find-the-town-judge", "Net trust score per person; judge has n − 1", "O(n + E) / O(n)"),
        (1557, "Minimum Number of Vertices to Reach All Nodes", "M", "minimum-number-of-vertices-to-reach-all-nodes", "Vertices with in-degree 0", "O(n + E) / O(n)"),
        (1971, "Find if Path Exists in Graph", "E", "find-if-path-exists-in-graph", "Build adjacency list, DFS or BFS from the source", "O(V + E) / O(V + E)"),
        (797, "All Paths From Source to Target", "M", "all-paths-from-source-to-target", "DFS in a DAG, record the path", "O(2ⁿ·n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 2
P.append(dict(
    title="DFS and connected components", tier="hot", sim="dfs", oneline="go as deep as you can, then back up; mark vertices visited",
    why="The most flexible traversal: components, reachability, cloning, paths", signature="LC 547 / 133 / 841",
    when="You must visit everything reachable from a vertex, count groups, or explore one path at a time.",
    detect="\"number of provinces / connected components\" · \"can reach all rooms\" · \"clone a graph\" · \"is there a path\" · \"number of operations to connect the network\".",
    intuition="Exploring a maze with chalk: walk down a corridor, marking each junction you pass; at a dead end (or an already-marked junction) turn back to the most recent junction with an unexplored branch. The chalk marks (the `visited` set) guarantee you never go round in circles. Starting a fresh walk from any unmarked spot counts the separate parts of the maze.",
    brute="Checking every pair of vertices for a path is O(V²·(V + E)). One DFS marks the entire component of its start vertex in O(V + E), and each vertex is processed once overall.",
    idea="`dfs(u)`: mark `u` visited; for each neighbour `v` not visited: `dfs(v)`. For components: loop over all vertices and start a DFS from each unvisited one, counting the starts. Use an explicit stack when the depth may be large.",
    steps=["`visited = {}`.", "For every vertex `u`: if not visited → `components++`, `dfs(u)`.", "`dfs(u)`: mark, then recurse on unvisited neighbours.", "Total work O(V + E): every vertex once, every edge looked at once (twice if undirected)."],
    trace_title="edges `0-1 0-2 1-3 1-4 2-5` and `6-7`",
    trace="""component 1: 0 -> 1 -> 3 (back) -> 4 (back) -> back -> 2 -> 5
component 2: 6 -> 7
components = 2""",
    code=[("DFS: recursive, iterative, and counting components",
           """boolean[] seen = new boolean[n];
void dfs(int u) {
    seen[u] = true;
    for (int v : g.get(u)) if (!seen[v]) dfs(v);
}
int components = 0;
for (int u = 0; u < n; u++) if (!seen[u]) { components++; dfs(u); }

// iterative: avoids stack overflow on long paths
Deque<Integer> st = new ArrayDeque<>();
st.push(start); seen[start] = true;
while (!st.isEmpty()) {
    int u = st.pop();
    for (int v : g.get(u)) if (!seen[v]) { seen[v] = true; st.push(v); }
}""",
           """seen = [False] * n
def dfs(u):
    seen[u] = True
    for v in g[u]:
        if not seen[v]:
            dfs(v)
components = 0
for u in range(n):
    if not seen[u]:
        components += 1
        dfs(u)

# iterative: avoids the recursion limit on long paths
stack = [start]; seen[start] = True
while stack:
    u = stack.pop()
    for v in g[u]:
        if not seen[v]:
            seen[v] = True
            stack.append(v)"""),
          ("clone a graph (map original → copy)",
           """Map<Node, Node> copy = new HashMap<>();
Node clone(Node n) {
    if (n == null) return null;
    if (copy.containsKey(n)) return copy.get(n);              // already cloned: reuse (breaks cycles)
    Node c = new Node(n.val);
    copy.put(n, c);                                           // register BEFORE recursing
    for (Node nb : n.neighbors) c.neighbors.add(clone(nb));
    return c;
}""",
           """copy = {}
def clone(n):
    if not n:
        return None
    if n in copy:
        return copy[n]                                        # already cloned: reuse (breaks cycles)
    c = Node(n.val)
    copy[n] = c                                               # register BEFORE recursing
    c.neighbors = [clone(nb) for nb in n.neighbors]
    return c""")],
    complexity="O(V + E) time, O(V) space (visited set + recursion / stack).",
    traps=["Mark a vertex visited when you **push or enter** it, not when you leave it, or cycles loop forever.", "For undirected graphs do not treat the edge back to the parent as a cycle.",
           "Deep recursion (10⁵ vertices in a path) overflows the stack: use the iterative version.", "Clone Graph: put the new node in the map **before** cloning the neighbours."],
    variants=["Keys and rooms: DFS from room 0, check all rooms visited.", "Number of operations to connect the network: components − 1 cables are needed (and enough spare edges).", "Number of provinces on an adjacency **matrix**: same count with `isConnected[u][v]`."],
    notuse="Shortest paths in unweighted graphs (BFS finds them; DFS does not).",
    problems=[
        (841, "Keys and Rooms", "M", "keys-and-rooms", "DFS from room 0; every room must be visited", "O(V + E) / O(V)"),
        (547, "Number of Provinces", "M", "number-of-provinces", "Count DFS starts over an adjacency matrix", "O(n²) / O(n)"),
        (133, "Clone Graph", "M", "clone-graph", "DFS with a map original → clone", "O(V + E) / O(V)"),
        (1319, "Number of Operations to Make Network Connected", "M", "number-of-operations-to-make-network-connected", "Need E ≥ n − 1; answer = components − 1", "O(V + E) / O(V + E)"),
    ]))

# ---------------------------------------------------------------- 3
P.append(dict(
    title="BFS and shortest paths in unweighted graphs", tier="hot", sim="bfsg", oneline="a queue explores in rings; first arrival = shortest",
    why="Fewest steps / edges / moves is always BFS", signature="LC 1091 / 1306 / 1129",
    when="The answer is a minimum number of edges or moves, or you need all vertices at distance exactly d.",
    detect="\"minimum number of steps / moves / edges\" · \"shortest path in a maze or grid\" · \"nearest exit\" · \"reach in the fewest jumps\".",
    intuition="Ripples in a pond: the water reaches everything at distance 1 before anything at distance 2. A queue reproduces this: vertices at distance d are dequeued before any at distance d + 1. The first time a vertex is discovered it is therefore by a shortest path, so you never have to revisit it.",
    brute="Enumerating all paths with DFS is exponential. BFS reaches each vertex once: O(V + E), and the distance array it fills is exactly the shortest-path lengths.",
    idea="`dist[src] = 0`, enqueue `src`. While the queue is not empty: pop `u`; for each neighbour `v` with `dist[v] == −1`: `dist[v] = dist[u] + 1`, `parent[v] = u`, enqueue `v`. Rebuild a path by following `parent` back from the target.",
    steps=["`dist` filled with −1; `dist[src] = 0`; queue = `[src]`.", "Pop `u`.", "For each unvisited neighbour: set its distance and parent; enqueue it.", "Stop when the target is dequeued (or the queue empties)."],
    trace_title="shortest path 0 → 6",
    trace="""dist: 0=0  1=1 2=1  3=2 4=2  5=3  6=4
parents: 6<-5<-3<-1<-0
path 0 -> 1 -> 3 -> 5 -> 6  (4 edges)""",
    code=[("BFS distances and path reconstruction",
           """int[] dist = new int[n], parent = new int[n];
Arrays.fill(dist, -1); Arrays.fill(parent, -1);
Queue<Integer> q = new ArrayDeque<>();
dist[src] = 0; q.add(src);
while (!q.isEmpty()) {
    int u = q.poll();
    for (int v : g.get(u)) {
        if (dist[v] != -1) continue;                    // already discovered
        dist[v] = dist[u] + 1;
        parent[v] = u;
        q.add(v);                                       // mark when ENQUEUED
    }
}
// path: for (int v = target; v != -1; v = parent[v]) path.add(v); then reverse""",
           """from collections import deque
dist = [-1] * n
parent = [-1] * n
dist[src] = 0
q = deque([src])
while q:
    u = q.popleft()
    for v in g[u]:
        if dist[v] != -1:
            continue                                    # already discovered
        dist[v] = dist[u] + 1
        parent[v] = u
        q.append(v)                                     # mark when ENQUEUED
# path: v = target; while v != -1: path.append(v); v = parent[v]; then reverse"""),
          ("jump game III: BFS over positions",
           """boolean canReach(int[] a, int start) {
    Queue<Integer> q = new ArrayDeque<>(); q.add(start);
    boolean[] seen = new boolean[a.length]; seen[start] = true;
    while (!q.isEmpty()) {
        int i = q.poll();
        if (a[i] == 0) return true;
        for (int j : new int[]{i + a[i], i - a[i]})
            if (j >= 0 && j < a.length && !seen[j]) { seen[j] = true; q.add(j); }
    }
    return false;
}""",
           """def can_reach(a, start):
    q, seen = deque([start]), {start}
    while q:
        i = q.popleft()
        if a[i] == 0:
            return True
        for j in (i + a[i], i - a[i]):
            if 0 <= j < len(a) and j not in seen:
                seen.add(j)
                q.append(j)
    return False""")],
    complexity="O(V + E) time, O(V) space.",
    traps=["Mark vertices visited when you **enqueue** them, not when you dequeue them.", "BFS gives shortest paths only when every edge has the same cost; weighted graphs need Dijkstra.",
           "Stop early when the target is found to save work.", "For levels, process `queue.size()` vertices per round."],
    variants=["Shortest path with alternating edge colours: state = (vertex, last colour).", "Minimum Height Trees: peel leaves layer by layer (BFS from the outside in).", "Bidirectional BFS from both ends for huge branching factors."],
    notuse="Weighted edges (Dijkstra / 0-1 BFS), or when you must list every path (DFS).",
    problems=[
        (1306, "Jump Game III", "M", "jump-game-iii", "BFS over positions i ± a[i]", "O(n) / O(n)"),
        (1926, "Nearest Exit from Entrance in Maze", "M", "nearest-exit-from-entrance-in-maze", "BFS on the grid; first border cell reached", "O(m·n) / O(m·n)"),
        (1091, "Shortest Path in Binary Matrix", "M", "shortest-path-in-binary-matrix", "BFS with 8 directions", "O(n²) / O(n²)"),
        (1129, "Shortest Path with Alternating Colors", "M", "shortest-path-with-alternating-colors", "BFS on (node, last colour) states", "O(V + E) / O(V)"),
        (310, "Minimum Height Trees", "M", "minimum-height-trees", "Repeatedly remove leaves; the last 1–2 vertices are the roots", "O(V) / O(V)"),
    ]))

# ---------------------------------------------------------------- 4
P.append(dict(
    title="Grids as graphs: islands and flood fill", tier="hot", sim="islands", oneline="cells are vertices, the 4 neighbours are the edges",
    why="Matrix traversal questions appear in almost every interview", signature="LC 200 / 695",
    when="A 2D grid where connected cells of the same kind form regions to count, measure or colour.",
    detect="\"number of islands\" · \"max area of island\" · \"flood fill\" · \"island perimeter\" · \"count sub-islands\" · \"making a large island\".",
    intuition="A grid is a graph you do not have to store: the neighbours of `(r, c)` are `(r ± 1, c)` and `(r, c ± 1)`. Scan the cells; each time you find land you have not seen, you have discovered a new island, so flood it (DFS or BFS) to mark all of it and never count it again. \"Sinking\" the land (changing 1 to 0) doubles as the visited marker.",
    brute="Comparing every pair of land cells for connectivity is O((mn)²). A single flood fill per island touches each cell once: O(m·n) overall.",
    idea="`for r, c: if grid[r][c] == 1: count++; dfs(r, c)`. `dfs` returns immediately for out-of-bounds, water or already visited; otherwise it marks the cell and recurses to 4 neighbours. For area, return `1 + sum of the four calls`.",
    steps=["Scan every cell.", "On unvisited land: increment the island count and start a flood fill.", "Flood fill: bounds check, land check, mark visited, recurse in 4 directions.", "Measure by returning sizes; compute perimeter by counting land–water boundaries."],
    trace_title="grid with 3 islands",
    trace="""11000
10011      islands: {(0,0),(0,1),(1,0)}
00010                {(1,3),(1,4),(2,3)}
01000                {(3,1)}   -> 3""",
    code=[("number of islands and max area",
           """int dfs(char[][] g, int r, int c) {
    if (r < 0 || c < 0 || r >= g.length || c >= g[0].length || g[r][c] != '1') return 0;
    g[r][c] = '0';                                          // sink = mark visited
    return 1 + dfs(g, r + 1, c) + dfs(g, r - 1, c) + dfs(g, r, c + 1) + dfs(g, r, c - 1);
}
int count = 0, best = 0;
for (int r = 0; r < g.length; r++)
    for (int c = 0; c < g[0].length; c++)
        if (g[r][c] == '1') { count++; best = Math.max(best, dfs(g, r, c)); }""",
           """def dfs(r, c):
    if not (0 <= r < R and 0 <= c < C) or g[r][c] != '1':
        return 0
    g[r][c] = '0'                                           # sink = mark visited
    return 1 + dfs(r + 1, c) + dfs(r - 1, c) + dfs(r, c + 1) + dfs(r, c - 1)

R, C = len(g), len(g[0])
count = best = 0
for r in range(R):
    for c in range(C):
        if g[r][c] == '1':
            count += 1
            best = max(best, dfs(r, c))"""),
          ("island perimeter (count land–water or border edges)",
           """int per = 0;
for (int r = 0; r < m; r++) for (int c = 0; c < n; c++) {
    if (g[r][c] != 1) continue;
    per += 4;
    if (r > 0 && g[r - 1][c] == 1) per -= 2;             // each shared edge removes 2 from the total
    if (c > 0 && g[r][c - 1] == 1) per -= 2;
}""",
           """per = 0
for r in range(m):
    for c in range(n):
        if g[r][c] != 1:
            continue
        per += 4
        if r > 0 and g[r - 1][c] == 1: per -= 2          # each shared edge removes 2 from the total
        if c > 0 and g[r][c - 1] == 1: per -= 2""")],
    complexity="O(m·n) time, O(m·n) recursion depth in the worst case (use BFS or an explicit stack for huge grids).",
    traps=["Do the bounds check **before** reading `g[r][c]`.", "Mutating the input is fine in interviews but say so; otherwise keep a `visited` array.",
           "Use 4 directions unless the problem says diagonals count.", "A grid of 10⁶ land cells can overflow recursion: prefer BFS or an explicit stack."],
    variants=["Count sub-islands: flood island in grid2 and verify every cell is land in grid1.", "Making a large island: label islands with ids and sizes, then try flipping each water cell.", "Flood fill: same DFS recolouring the connected same-colour region."],
    notuse="Shortest paths on the grid (BFS) or weighted movement (Dijkstra).",
    problems=[
        (463, "Island Perimeter", "E", "island-perimeter", "4 per land cell minus 2 for each shared edge", "O(m·n) / O(1)"),
        (733, "Flood Fill", "E", "flood-fill", "DFS recolouring the connected region", "O(m·n) / O(m·n)"),
        (200, "Number of Islands", "M", "number-of-islands", "Count flood fills", "O(m·n) / O(m·n)"),
        (695, "Max Area of Island", "M", "max-area-of-island", "DFS returns region size; keep the max", "O(m·n) / O(m·n)"),
        (1905, "Count Sub Islands", "M", "count-sub-islands", "Flood grid2 island; every cell must be land in grid1", "O(m·n) / O(m·n)"),
        (827, "Making A Large Island", "H", "making-a-large-island", "Label islands with sizes, try flipping each 0", "O(m·n) / O(m·n)"),
    ]))

# ---------------------------------------------------------------- 5
P.append(dict(
    title="Multi-source BFS: waves from many starting points", tier="hot", sim="multibfs", oneline="put every source in the queue at distance 0",
    why="Replaces \"BFS from every cell\" (too slow) with one pass", signature="LC 542 / 994",
    when="You need each cell's distance to the nearest source, or something spreads from several places at once.",
    detect="\"distance to the nearest 0 / gate / land / water\" · \"rotting oranges\" · \"spread of fire\" · \"map of highest peak\" · \"as far from land as possible\".",
    intuition="Many stones dropped into a pond at the same moment: the ripples spread together, and each point of water is first reached by the stone nearest to it. Instead of running a separate BFS from every cell, begin with **all sources at distance 0 in the same queue**. The wave then advances one step at a time and the first time a cell is reached, that distance is its answer.",
    brute="A BFS from every cell costs O((mn)²). One BFS from all sources costs O(m·n) because each cell enters the queue once.",
    idea="Initialise the queue with every source and set their distance to 0 (or 'visited'). Standard BFS afterwards. Process by levels when you need the number of rounds (minutes).",
    steps=["Scan the grid; enqueue all sources, set their distance 0.", "BFS: pop a cell, for each unvisited neighbour set `dist = dist[cell] + 1`, enqueue.", "Rounds (levels) equal elapsed time for spreading problems.", "Unreached cells keep their sentinel (−1) → impossible case."],
    trace_title="distance to the nearest 0",
    trace="""1 1 1 0         2 2 1 0
1 1 1 1   ->    1 2 2 1
0 1 1 1         0 1 2 2
(level 1 fills the cells next to a zero, level 2 the next ring)""",
    code=[("01 Matrix: distance of every cell to the nearest 0",
           """int m = mat.length, n = mat[0].length;
int[][] dist = new int[m][n];
Queue<int[]> q = new ArrayDeque<>();
for (int r = 0; r < m; r++) for (int c = 0; c < n; c++) {
    if (mat[r][c] == 0) q.add(new int[]{r, c});            // ALL sources first
    else dist[r][c] = -1;
}
int[][] D = {{1,0},{-1,0},{0,1},{0,-1}};
while (!q.isEmpty()) {
    int[] p = q.poll();
    for (int[] d : D) {
        int r = p[0] + d[0], c = p[1] + d[1];
        if (r >= 0 && c >= 0 && r < m && c < n && dist[r][c] == -1) {
            dist[r][c] = dist[p[0]][p[1]] + 1;
            q.add(new int[]{r, c});
        }
    }
}""",
           """from collections import deque
m, n = len(mat), len(mat[0])
dist = [[-1] * n for _ in range(m)]
q = deque()
for r in range(m):
    for c in range(n):
        if mat[r][c] == 0:
            dist[r][c] = 0
            q.append((r, c))                                # ALL sources first
while q:
    r, c = q.popleft()
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < m and 0 <= nc < n and dist[nr][nc] == -1:
            dist[nr][nc] = dist[r][c] + 1
            q.append((nr, nc))"""),
          ("rotting oranges: count the rounds",
           """int fresh = 0, minutes = 0;
Queue<int[]> q = new ArrayDeque<>();
for (int r = 0; r < m; r++) for (int c = 0; c < n; c++) {
    if (g[r][c] == 2) q.add(new int[]{r, c}); else if (g[r][c] == 1) fresh++;
}
while (!q.isEmpty() && fresh > 0) {
    minutes++;
    for (int s = q.size(); s > 0; s--) {                    // one minute = one level
        int[] p = q.poll();
        for (int[] d : D) {
            int r = p[0] + d[0], c = p[1] + d[1];
            if (r >= 0 && c >= 0 && r < m && c < n && g[r][c] == 1) { g[r][c] = 2; fresh--; q.add(new int[]{r, c}); }
        }
    }
}
return fresh == 0 ? minutes : -1;""",
           """fresh, q = 0, deque()
for r in range(m):
    for c in range(n):
        if g[r][c] == 2: q.append((r, c))
        elif g[r][c] == 1: fresh += 1
minutes = 0
while q and fresh:
    minutes += 1
    for _ in range(len(q)):                                 # one minute = one level
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and g[nr][nc] == 1:
                g[nr][nc] = 2
                fresh -= 1
                q.append((nr, nc))
return minutes if fresh == 0 else -1""")],
    complexity="O(m·n) time and space.",
    traps=["Enqueue **all** sources before starting; adding them one at a time and running BFS each defeats the purpose.", "Count rounds (levels), not cells, for time questions.",
           "Detect unreachable cells: leftover fresh oranges or −1 distances.", "Do not count the last level that finds nothing new."],
    variants=["Shortest bridge: DFS to find one island, then multi-source BFS from all its cells to the other island.", "Map of highest peak: BFS from all water cells (height 0) assigning height = distance.", "Walls and gates: BFS from all gates."],
    notuse="A single source and single target (plain BFS), or weighted costs (Dijkstra).",
    problems=[
        (542, "01 Matrix", "M", "01-matrix", "Enqueue every 0, fill distances outward", "O(m·n) / O(m·n)"),
        (994, "Rotting Oranges", "M", "rotting-oranges", "Enqueue rotten ones; count levels", "O(m·n) / O(m·n)"),
        (1162, "As Far from Land as Possible", "M", "as-far-from-land-as-possible", "Multi-source BFS from land; last level distance", "O(n²) / O(n²)"),
        (1765, "Map of Highest Peak", "M", "map-of-highest-peak", "BFS from all water cells; height = distance", "O(m·n) / O(m·n)"),
        (934, "Shortest Bridge", "M", "shortest-bridge", "Flood one island, then BFS outward from all of its cells", "O(n²) / O(n²)"),
    ]))

# ---------------------------------------------------------------- 6
P.append(dict(
    title="Cycle detection with DFS colours", tier="hot", sim="cycle", oneline="an edge to a grey vertex (still on the path) closes a cycle",
    why="Underlies course scheduling, deadlock checks and safe-state problems", signature="LC 207 / 802",
    when="You must know whether a directed graph is acyclic, or find vertices that cannot reach a cycle.",
    detect="\"can you finish all courses\" · \"detect a cycle\" · \"eventual safe states\" · \"deadlock\" · \"circular dependency\".",
    intuition="Walking a path of chalk-marked rooms: **grey** rooms are on the path you are currently walking, **black** rooms are fully explored, **white** rooms are untouched. If an exit from your current room leads to a **grey** room, you have walked in a circle. A **black** room is harmless: everything beyond it was already explored and led nowhere back to you.",
    brute="Checking reachability from every vertex to itself is O(V·(V + E)). One DFS with three states finds a cycle in O(V + E).",
    idea="`state[u]`: 0 white, 1 grey (in the recursion stack), 2 black (done). `dfs(u)`: set grey; for each `v`: if grey → cycle; if white and `dfs(v)` finds a cycle → cycle; then set black. For undirected graphs, ignore the edge back to the parent.",
    steps=["All vertices white.", "Enter `u`: colour grey.", "For each neighbour: grey → return cycle; white → recurse.", "Leaving `u`: colour black."],
    trace_title="`0→1, 1→2, 2→3, 3→1, 0→4`",
    trace="""0 grey -> 1 grey -> 2 grey -> 3 grey
3 -> 1 : 1 is grey  => back edge, cycle 1 -> 2 -> 3 -> 1""",
    code=[("directed cycle detection (course schedule)",
           """int[] state = new int[n];                              // 0 white, 1 grey, 2 black
boolean hasCycle(int u) {
    state[u] = 1;
    for (int v : g.get(u)) {
        if (state[v] == 1) return true;                    // back edge to the current path
        if (state[v] == 0 && hasCycle(v)) return true;
    }
    state[u] = 2;
    return false;
}
boolean canFinish() {
    for (int u = 0; u < n; u++) if (state[u] == 0 && hasCycle(u)) return false;
    return true;
}""",
           """state = [0] * n                                       # 0 white, 1 grey, 2 black
def has_cycle(u):
    state[u] = 1
    for v in g[u]:
        if state[v] == 1:
            return True                                    # back edge to the current path
        if state[v] == 0 and has_cycle(v):
            return True
    state[u] = 2
    return False
can_finish = not any(state[u] == 0 and has_cycle(u) for u in range(n))"""),
          ("undirected cycle detection (ignore the parent edge)",
           """boolean dfs(int u, int parent, boolean[] seen) {
    seen[u] = true;
    for (int v : g.get(u)) {
        if (v == parent) continue;                        // the edge we just came along
        if (seen[v]) return true;                         // reached an earlier vertex another way
        if (dfs(v, u, seen)) return true;
    }
    return false;
}""",
           """def dfs(u, parent):
    seen[u] = True
    for v in g[u]:
        if v == parent:
            continue                                      # the edge we just came along
        if seen[v] or dfs(v, u):
            return True                                   # reached an earlier vertex another way
    return False""")],
    complexity="O(V + E) time, O(V) space.",
    traps=["Directed graphs need three states; a plain `visited` flag reports false cycles on cross / forward edges.", "Undirected graphs: skip the parent (and watch multi-edges between the same pair).",
           "Start a DFS from **every** white vertex (the graph may be disconnected).", "Safe states: a vertex is safe iff every path from it ends in a terminal; vertices on or leading to a cycle are unsafe."],
    variants=["Topological ordering (topic 13): reverse post-order, or Kahn's algorithm with in-degrees (also detects cycles).", "Eventual safe states: DFS colours or reverse graph + Kahn.", "Union-Find detects cycles in undirected graphs as edges are added (topic 13)."],
    notuse="You just need an order of tasks (use Kahn's algorithm and check the order length).",
    problems=[
        (207, "Course Schedule", "M", "course-schedule", "Is the prerequisite graph acyclic? DFS colours", "O(V + E) / O(V + E)"),
        (210, "Course Schedule II", "M", "course-schedule-ii", "Reverse post-order of a DFS (or Kahn) if no cycle", "O(V + E) / O(V + E)"),
        (802, "Find Eventual Safe States", "M", "find-eventual-safe-states", "Black vertices are safe; grey/cycle vertices are not", "O(V + E) / O(V)"),
        (1462, "Course Schedule IV", "M", "course-schedule-iv", "Reachability of prerequisites (DFS / Floyd-Warshall)", "O(V·(V + E)) / O(V²)"),
        (2050, "Parallel Courses III", "H", "parallel-courses-iii", "Longest path in a DAG with DFS memo or Kahn", "O(V + E) / O(V + E)"),
    ]))

# ---------------------------------------------------------------- 7
P.append(dict(
    title="Bipartite check: two-colouring", tier="sec", sim="bipartite", oneline="alternate colours along edges; a clash means an odd cycle",
    why="\"Split into two groups\" problems reduce to it", signature="LC 785 / 886",
    when="You must divide vertices into two sets so that every edge connects different sets (teams, rooms, conflicts).",
    detect="\"is graph bipartite\" · \"possible bipartition\" · \"dislikes\" · \"split into two groups with no conflicts\" · \"assign two colours\".",
    intuition="Painting a map with only two colours so that neighbours always differ. Pick any vertex and paint it red; all its neighbours must be blue; their neighbours red again, and so on. If you ever reach a neighbour that already has the **same** colour as you, no two-colouring exists, and that happens exactly when the graph has a cycle of odd length.",
    brute="Trying all 2ⁿ assignments is exponential. The forced propagation of colours decides in O(V + E).",
    idea="`color[v] = −1` initially. For each uncoloured vertex, colour it 0 and BFS/DFS: for each neighbour, if uncoloured give it the opposite colour; if coloured with the same colour as the current vertex, return false.",
    steps=["Fill `color` with −1.", "For every uncoloured vertex: set colour 0 and traverse.", "Neighbour uncoloured → opposite colour; coloured the same → not bipartite.", "If no conflict in any component → bipartite."],
    trace_title="triangle `0-1-2` plus `2-3`",
    trace="""0 : A
1,2 : B           (neighbours of 0)
dequeue 1: neighbour 2 is B, same as 1  -> conflict
odd cycle 0-1-2  => NOT bipartite""",
    code=[("is graph bipartite (BFS colouring)",
           """int[] color = new int[n];
Arrays.fill(color, -1);
for (int s = 0; s < n; s++) {
    if (color[s] != -1) continue;
    color[s] = 0;
    Queue<Integer> q = new ArrayDeque<>(); q.add(s);
    while (!q.isEmpty()) {
        int u = q.poll();
        for (int v : g.get(u)) {
            if (color[v] == -1) { color[v] = 1 - color[u]; q.add(v); }
            else if (color[v] == color[u]) return false;      // odd cycle
        }
    }
}
return true;""",
           """color = [-1] * n
for s in range(n):
    if color[s] != -1:
        continue
    color[s] = 0
    q = deque([s])
    while q:
        u = q.popleft()
        for v in g[u]:
            if color[v] == -1:
                color[v] = 1 - color[u]
                q.append(v)
            elif color[v] == color[u]:
                return False                                  # odd cycle
return True""")],
    complexity="O(V + E) time, O(V) space.",
    traps=["Check **every component** (the graph may be disconnected).", "Compare colours when the neighbour is already coloured; do not only check `visited`.",
           "Build the graph from the \"dislikes\" pairs in both directions.", "A graph with no edges, or only even cycles / trees, is bipartite."],
    variants=["Possible bipartition: same check on the dislike graph.", "Flower planting with no adjacent equal: greedy colouring with 4 colours (max degree 3).", "Divide nodes into maximum groups: per-component BFS depth after bipartite check."],
    notuse="When you need more than two groups (general graph colouring is NP-hard).",
    problems=[
        (1042, "Flower Planting With No Adjacent", "E", "flower-planting-with-no-adjacent", "Greedy: give each garden the first colour unused by neighbours", "O(V + E) / O(V)"),
        (785, "Is Graph Bipartite?", "M", "is-graph-bipartite", "BFS two-colouring of each component", "O(V + E) / O(V)"),
        (886, "Possible Bipartition", "M", "possible-bipartition", "Build the dislike graph, then 2-colour it", "O(V + E) / O(V + E)"),
        (2493, "Divide Nodes Into the Maximum Number of Groups", "H", "divide-nodes-into-the-maximum-number-of-groups", "Per component: bipartite check + best BFS depth over start nodes", "O(V·(V + E)) / O(V + E)"),
    ]))

# ---------------------------------------------------------------- 8
P.append(dict(
    title="Implicit graphs: BFS over states", tier="hot", sim="wordladder", oneline="states are vertices, legal moves are edges",
    why="Puzzle and transformation questions hide a graph you never write down", signature="LC 127 / 752 / 433",
    when="You have a start state, a goal state and moves, and you need the fewest moves.",
    detect="\"minimum transformations / mutations / turns\" · \"word ladder\" · \"open the lock\" · \"sliding puzzle\" · \"perfect squares\" · \"jumps to reach home\".",
    intuition="Draw every possible configuration as a dot and join two dots if one move turns one into the other. You never have to draw the whole picture: from any state you can generate its neighbours by applying the moves. \"Fewest moves\" is then a shortest path in an unweighted graph, which is BFS.",
    brute="Trying every sequence of moves is exponential. BFS visits each distinct state once, so the cost is the number of reachable states times the cost of generating neighbours.",
    idea="Encode a state (string, tuple, integer). `neighbors(state)` yields states reachable in one move. BFS from the start with a `visited` set, level by level; the level number when you first see the goal is the answer. Skip forbidden states (deadends).",
    steps=["Pick a hashable state representation.", "Write `neighbors(state)` (change one letter, turn a wheel, slide a tile).", "BFS with a visited set (initially including forbidden states).", "Return the number of levels when the goal is dequeued; −1 if the queue empties."],
    trace_title="`hit → cog` with words hot, dot, dog, lot, log, cog",
    trace="""level 1: hit
level 2: hot
level 3: dot lot
level 4: dog log
level 5: cog       => 5 words (4 moves)""",
    code=[("word ladder (BFS, removing words from the dictionary as visited)",
           """Set<String> dict = new HashSet<>(wordList);
if (!dict.contains(end)) return 0;
Queue<String> q = new ArrayDeque<>(); q.add(begin);
int steps = 1;
while (!q.isEmpty()) {
    for (int s = q.size(); s > 0; s--) {
        String w = q.poll();
        if (w.equals(end)) return steps;
        char[] c = w.toCharArray();
        for (int i = 0; i < c.length; i++) {
            char old = c[i];
            for (char ch = 'a'; ch <= 'z'; ch++) {
                c[i] = ch;
                String nw = new String(c);
                if (dict.remove(nw)) q.add(nw);              // remove = mark visited
            }
            c[i] = old;
        }
    }
    steps++;
}
return 0;""",
           """from collections import deque
words = set(wordList)
if end not in words:
    return 0
q, steps = deque([begin]), 1
while q:
    for _ in range(len(q)):
        w = q.popleft()
        if w == end:
            return steps
        for i in range(len(w)):
            for ch in 'abcdefghijklmnopqrstuvwxyz':
                nw = w[:i] + ch + w[i + 1:]
                if nw in words:
                    words.remove(nw)                           # remove = mark visited
                    q.append(nw)
    steps += 1
return 0"""),
          ("open the lock (generic BFS over 4-digit states)",
           """Set<String> seen = new HashSet<>(Arrays.asList(deadends));
if (seen.contains("0000")) return -1;
Queue<String> q = new ArrayDeque<>(); q.add("0000"); seen.add("0000");
int turns = 0;
while (!q.isEmpty()) {
    for (int s = q.size(); s > 0; s--) {
        String cur = q.poll();
        if (cur.equals(target)) return turns;
        for (int i = 0; i < 4; i++)
            for (int d : new int[]{1, 9}) {                    // +1 and -1 (mod 10)
                char[] c = cur.toCharArray();
                c[i] = (char) ('0' + (c[i] - '0' + d) % 10);
                String nxt = new String(c);
                if (seen.add(nxt)) q.add(nxt);
            }
    }
    turns++;
}
return -1;""",
           """seen = set(deadends)
if "0000" in seen:
    return -1
q, turns = deque(["0000"]), 0
seen.add("0000")
while q:
    for _ in range(len(q)):
        cur = q.popleft()
        if cur == target:
            return turns
        for i in range(4):
            for d in (1, 9):                                   # +1 and -1 (mod 10)
                nxt = cur[:i] + str((int(cur[i]) + d) % 10) + cur[i + 1:]
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
    turns += 1
return -1""")],
    complexity="O(states × cost of generating neighbours). Word ladder: O(N · L · 26).",
    traps=["Include forbidden / start states in `visited` from the beginning.", "Word ladder length counts **words**, not moves (off by one); read the statement.",
           "Return 0 / −1 immediately when the goal is unreachable or not in the dictionary.", "Use wildcard buckets (`h*t`) or the letter-swap loop, not an O(N²) pairwise comparison."],
    variants=["Perfect squares: states are remaining sums; edges subtract a square (BFS levels = minimum count).", "Sliding puzzle: state is the board as a string; swap `0` with a neighbour.", "Minimum jumps to reach home: state = (position, last move was back?)."],
    notuse="Moves with different costs (Dijkstra) or when you only need to know whether the goal is reachable (DFS is enough).",
    problems=[
        (433, "Minimum Genetic Mutation", "M", "minimum-genetic-mutation", "BFS over gene strings changing one letter", "O(N·L·4) / O(N)"),
        (752, "Open the Lock", "M", "open-the-lock", "BFS over 10⁴ wheel states, skip deadends", "O(10⁴·8) / O(10⁴)"),
        (279, "Perfect Squares", "M", "perfect-squares", "BFS levels over remainders (or DP)", "O(n√n) / O(n)"),
        (127, "Word Ladder", "H", "word-ladder", "BFS by changing one letter at a time", "O(N·L²) / O(N·L)"),
        (773, "Sliding Puzzle", "H", "sliding-puzzle", "BFS over board strings, swapping the blank", "O(6!) / O(6!)"),
    ]))

# ---------------------------------------------------------------- 9
P.append(dict(
    title="Border-first search: think in reverse", tier="sec", sim="surrounded", oneline="start from what is guaranteed safe and spread inward",
    why="Turns an expensive \"is this region enclosed?\" test into one traversal", signature="LC 130 / 417 / 1020",
    when="A region counts (or not) depending on whether it touches the border or can reach a special edge.",
    detect="\"surrounded regions\" · \"number of enclaves\" · \"closed islands\" · \"Pacific Atlantic water flow\" · \"cells that can reach both oceans\".",
    intuition="To find the ponds that are completely enclosed, do not test every pond. Instead, find the water that is **connected to the outside** (the border) and mark it. Whatever water is left unmarked cannot reach the border, so it is enclosed. Searching from the safe cells inward costs one traversal instead of one per region.",
    brute="Run a search from every cell to see if it reaches the border: O((mn)²). Searching once from all border cells and marking what they reach is O(m·n).",
    idea="Seed a DFS/BFS from every qualifying border cell and mark everything reachable. Then one scan: unmarked cells are the answer (flip them, count them). For two-sided questions (Pacific and Atlantic) run one reverse search per ocean and intersect.",
    steps=["Collect border cells that satisfy the condition (the `O`s, the land).", "DFS/BFS from each, marking reachable cells safe.", "Scan the grid: unmarked qualifying cells are enclosed.", "Flip, count or intersect as the problem asks."],
    trace_title="surrounded regions",
    trace="""X X X X       X X X X
X O O X  ->   X X X X
X X O X       X X X X
X O X X       X O X X   (border-connected O stays)""",
    code=[("surrounded regions: mark border-connected O, flip the rest",
           """void solve(char[][] b) {
    int m = b.length, n = b[0].length;
    for (int r = 0; r < m; r++) { mark(b, r, 0); mark(b, r, n - 1); }       // left and right borders
    for (int c = 0; c < n; c++) { mark(b, 0, c); mark(b, m - 1, c); }       // top and bottom borders
    for (int r = 0; r < m; r++) for (int c = 0; c < n; c++) {
        if (b[r][c] == 'O') b[r][c] = 'X';                                   // enclosed
        else if (b[r][c] == 'S') b[r][c] = 'O';                              // safe: restore
    }
}
void mark(char[][] b, int r, int c) {
    if (r < 0 || c < 0 || r >= b.length || c >= b[0].length || b[r][c] != 'O') return;
    b[r][c] = 'S';
    mark(b, r + 1, c); mark(b, r - 1, c); mark(b, r, c + 1); mark(b, r, c - 1);
}""",
           """def solve(b):
    m, n = len(b), len(b[0])
    def mark(r, c):
        if not (0 <= r < m and 0 <= c < n) or b[r][c] != 'O':
            return
        b[r][c] = 'S'
        mark(r + 1, c); mark(r - 1, c); mark(r, c + 1); mark(r, c - 1)
    for r in range(m):
        mark(r, 0); mark(r, n - 1)                          # left and right borders
    for c in range(n):
        mark(0, c); mark(m - 1, c)                          # top and bottom borders
    for r in range(m):
        for c in range(n):
            if b[r][c] == 'O': b[r][c] = 'X'                # enclosed
            elif b[r][c] == 'S': b[r][c] = 'O'              # safe: restore"""),
          ("Pacific Atlantic: search uphill from each ocean, intersect",
           """boolean[][] pac = new boolean[m][n], atl = new boolean[m][n];
for (int r = 0; r < m; r++) { dfs(h, pac, r, 0); dfs(h, atl, r, n - 1); }
for (int c = 0; c < n; c++) { dfs(h, pac, 0, c); dfs(h, atl, m - 1, c); }
void dfs(int[][] h, boolean[][] seen, int r, int c) {
    seen[r][c] = true;
    for (int[] d : D) {
        int nr = r + d[0], nc = c + d[1];
        if (nr < 0 || nc < 0 || nr >= h.length || nc >= h[0].length || seen[nr][nc]) continue;
        if (h[nr][nc] >= h[r][c]) dfs(h, seen, nr, nc);          // water flows downhill, so we climb in reverse
    }
}
// answer: cells with pac[r][c] && atl[r][c]""",
           """def reach(starts):
    seen, stack = set(starts), list(starts)
    while stack:
        r, c = stack.pop()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and (nr, nc) not in seen and h[nr][nc] >= h[r][c]:
                seen.add((nr, nc))                                # climb uphill in reverse
                stack.append((nr, nc))
    return seen
pac = reach([(r, 0) for r in range(m)] + [(0, c) for c in range(n)])
atl = reach([(r, n - 1) for r in range(m)] + [(m - 1, c) for c in range(n)])
return [list(p) for p in pac & atl]""")],
    complexity="O(m·n) time and space.",
    traps=["Use a temporary marker (like `'S'`) so you can tell safe cells from enclosed ones, then restore.", "Search from **all** border cells, not just corners.",
           "Pacific Atlantic: the reverse search climbs to cells with height **≥** the current one.", "Number of closed islands counts regions with **no** border cell; sink border-connected land first."],
    variants=["Number of Enclaves: sink border land, count the remaining land cells.", "Number of Closed Islands: sink border-connected land, then count islands.", "Reverse reachability also solves \"which nodes can reach X\" on a directed graph (search the reversed edges)."],
    notuse="When regions are small and independent, a per-region check may be simpler.",
    problems=[
        (1020, "Number of Enclaves", "M", "number-of-enclaves", "Sink border-connected land; count what remains", "O(m·n) / O(m·n)"),
        (1254, "Number of Closed Islands", "M", "number-of-closed-islands", "Sink border land, then count islands", "O(m·n) / O(m·n)"),
        (130, "Surrounded Regions", "M", "surrounded-regions", "Mark border-connected O's safe, flip the others", "O(m·n) / O(m·n)"),
        (417, "Pacific Atlantic Water Flow", "M", "pacific-atlantic-water-flow", "Reverse DFS from each ocean; intersect", "O(m·n) / O(m·n)"),
    ]))

TOPIC = dict(
    id="graphs_traversal", file="12_graphs_traversal.html", title="Graph Traversal — Pattern Guide",
    lead="Graphs model almost everything: maps, social networks, grids, puzzles, dependencies. This guide covers representing graphs, DFS and connected components, BFS shortest paths, grids and islands, multi-source BFS, cycle detection, bipartite checking, implicit state graphs and border-first search. Each pattern has the intuition, a step-through animation that draws the graph or grid, Java and Python code, and a ladder of LeetCode problems.",
    mindset="Every graph problem has two decisions: **how to model it** (what is a vertex, what is an edge, is the graph given or implicit?) and **which traversal fits** (DFS to explore, count and detect cycles; BFS for fewest steps and levels). Mark vertices visited the moment you discover them, start from every unvisited vertex when the graph may be disconnected, and remember that grids and puzzles are graphs in disguise.",
    qintro="Ask these questions on every graph problem:",
    questions=["**What are the vertices and the edges?** (cells, words, states, courses)", "**Directed or undirected? Weighted or not?** (weights → Dijkstra, topic 13)",
               "**Do I need fewest steps?** → BFS. **Count, explore, detect a cycle?** → DFS.", "**Can the graph be disconnected?** → loop over all vertices.", "**Is there more than one starting point?** → multi-source BFS."],
    cues=[
        ["\"n nodes and edges\", degrees, \"town judge\"", "**P1** Representation"],
        ["\"connected components\", \"reachable\", \"clone\"", "**P2** DFS"],
        ["\"minimum steps / edges\"", "**P3** BFS shortest path"],
        ["\"islands\", \"flood fill\", regions in a matrix", "**P4** Grid DFS/BFS"],
        ["\"distance to the nearest\", \"spreads from several places\"", "**P5** Multi-source BFS"],
        ["\"prerequisites\", \"circular dependency\"", "**P6** Cycle detection"],
        ["\"split into two groups\", \"dislikes\"", "**P7** Bipartite check"],
        ["\"minimum transformations\", \"lock\", \"puzzle\"", "**P8** BFS over states"],
        ["\"surrounded\", \"enclaves\", \"reach both oceans\"", "**P9** Border-first search"],
    ],
    choose=[
        ["Fewest edges or moves", "BFS (P3, P5, P8)"],
        ["Count components or regions", "DFS / flood fill (P2, P4)"],
        ["Detect a cycle in a directed graph", "DFS colours (P6)"],
        ["Two-group assignment", "BFS colouring (P7)"],
        ["Nearest of many sources", "Multi-source BFS (P5)"],
        ["Enclosed or border-connected regions", "Search from the border (P9)"],
        ["Puzzle with moves", "BFS on states (P8)"],
    ],
    rule="**fewest steps → BFS; everything reachable, components, cycles → DFS; many sources → put them all in the queue first; enclosed → search from the border.** Always keep a visited structure and mark it when you enqueue or enter.",
    selftest=[
        ("Why mark a vertex visited when you enqueue it in BFS?", "Otherwise several neighbours can enqueue the same vertex before it is processed, growing the queue and (with weights or counts) giving wrong results."),
        ("Why does BFS find shortest paths in unweighted graphs?", "It processes vertices in order of distance from the source, so the first time a vertex is reached is by a path with the fewest edges."),
        ("Why does directed cycle detection need three colours?", "A visited vertex may be finished (harmless cross or forward edge) or still on the current path (back edge = cycle). Only the grey state signals a cycle."),
        ("What is the time complexity of DFS or BFS over an adjacency list?", "O(V + E): each vertex is processed once and each edge is examined once (twice if undirected)."),
        ("How does multi-source BFS beat running BFS from each source?", "All sources start in the same queue at distance 0, so each cell is reached by the nearest source in one pass: O(V + E) instead of O(sources × (V + E))."),
        ("When is a graph bipartite?", "Exactly when it contains no odd-length cycle; BFS or DFS two-colouring detects a violation as an edge joining two vertices of the same colour."),
        ("How do you count connected components?", "Loop over all vertices; each time you meet an unvisited one, increment the counter and traverse its whole component."),
        ("Why search from the border in Surrounded Regions?", "The border-connected `O`s are exactly the safe ones; marking them with one traversal leaves the enclosed regions unmarked, avoiding a separate search per region."),
    ],
    plan=[
        "**Day 1:** representation and DFS: build adjacency lists, count components, clone a graph.",
        "**Day 2:** BFS shortest path on graphs and grids; write the template from memory.",
        "**Day 3:** grid problems: islands, max area, flood fill; then multi-source BFS (rotting oranges, 01 matrix).",
        "**Day 4:** cycle detection and course schedule; bipartite checks.",
        "**Day 5:** implicit graphs: word ladder, open the lock, perfect squares.",
        "**Day 6:** border-first problems and a mixed review; for each problem name the vertices, edges and traversal aloud.",
    ],
    patterns=P,
)
