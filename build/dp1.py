"""Content for topic 15: Dynamic programming I (1D and 2D)."""

P = []

# ---------------------------------------------------------------- 1
P.append(dict(
    title="DP fundamentals: state, transition, base case", tier="hot", sim="fibtree", oneline="solve each distinct subproblem once and reuse the answer",
    why="Every DP problem is built from these four ingredients", signature="LC 70 / 509",
    when="A problem can be split into smaller versions of itself that **overlap**, and the best answer is built from the best answers of the parts.",
    detect="\"number of ways\" · \"minimum / maximum cost\" · \"can it be done?\" · a brute-force recursion that repeats the same arguments · choices at each step that depend on earlier choices.",
    intuition="Imagine writing every intermediate answer on a whiteboard so you never recompute it. Plain recursion forgets what it already solved (the call tree explodes: fib(5) makes 15 calls to solve 6 different problems). DP remembers: either **top-down** (recursion plus a cache, called memoisation) or **bottom-up** (fill a table from the smallest subproblem upward, called tabulation). Two properties must hold: **overlapping subproblems** (the same sub-answers are needed again) and **optimal substructure** (the answer is assembled from sub-answers).",
    brute="Naïve recursion is exponential (about 2ⁿ for Fibonacci). A table with one cell per distinct state costs (number of states) × (cost of one transition): O(n) for Fibonacci.",
    idea="Define: (1) **state** = what uniquely identifies a subproblem (`dp[i]`, `dp[i][j]`); (2) **meaning** of the value stored; (3) **transition** from smaller states; (4) **base cases**; (5) **order** to compute (dependencies first); (6) **answer** cell. If a cell depends only on the last k cells, keep only those (space optimisation).",
    steps=["Write the brute-force recursion and spot repeated arguments.", "Name the state and write what `dp[state]` means in one sentence.", "Write the transition and the base cases.", "Choose top-down (add a cache) or bottom-up (loop in dependency order); then trim the space."],
    trace_title="climbing stairs: ways(n) = ways(n−1) + ways(n−2)",
    trace="""dp[0] = 1 (empty path)   dp[1] = 1
dp[2] = dp[1] + dp[0] = 2
dp[3] = dp[2] + dp[1] = 3
dp[4] = 5   dp[5] = 8
only the last two values are needed -> O(1) space""",
    code=[("one recurrence, four implementations (climbing stairs)",
           """// 1) naive recursion: O(2^n)
int waysNaive(int n) { return n <= 1 ? 1 : waysNaive(n - 1) + waysNaive(n - 2); }

// 2) top-down with memo: O(n) time, O(n) space
int[] memo;
int waysMemo(int n) {
    if (n <= 1) return 1;
    if (memo[n] != 0) return memo[n];
    return memo[n] = waysMemo(n - 1) + waysMemo(n - 2);      // allocate memo = new int[n + 1] first
}

// 3) bottom-up table
int waysTable(int n) {
    int[] dp = new int[n + 1]; dp[0] = 1; if (n >= 1) dp[1] = 1;
    for (int i = 2; i <= n; i++) dp[i] = dp[i - 1] + dp[i - 2];
    return dp[n];
}

// 4) rolling variables: O(1) space
int waysRolling(int n) {
    int a = 1, b = 1;
    for (int i = 2; i <= n; i++) { int c = a + b; a = b; b = c; }
    return b;
}""",
           """# 1) naive recursion: O(2^n)
def ways(n):
    return 1 if n <= 1 else ways(n - 1) + ways(n - 2)

# 2) top-down with memo: O(n) time, O(n) space
from functools import lru_cache
@lru_cache(None)
def ways(n):
    return 1 if n <= 1 else ways(n - 1) + ways(n - 2)

# 3) bottom-up table
dp = [1, 1] + [0] * (n - 1)
for i in range(2, n + 1):
    dp[i] = dp[i - 1] + dp[i - 2]

# 4) rolling variables: O(1) space
a = b = 1
for _ in range(2, n + 1):
    a, b = b, a + b
return b""")],
    complexity="Time = (number of states) × (transition cost). Space = number of states, often reducible to the last row / last k values.",
    traps=["Write the **meaning** of `dp[i]` before coding; most wrong answers come from a vague state.", "Off-by-one in base cases (`dp[0]` is often the empty prefix with value 1 or 0).",
           "Bottom-up loops must visit states in dependency order.", "Memoising with a mutable argument or a huge state space can blow memory: check the number of distinct states."],
    variants=["Memoisation (easier to derive) vs tabulation (no recursion limit, easier to optimise).", "Reconstruction: store the choice to rebuild the actual solution.", "Counting vs optimising vs feasibility DPs share the same skeleton with different operators (+, min / max, OR)."],
    notuse="No overlapping subproblems (use divide and conquer), or a provably safe greedy rule exists (topic 14).",
    problems=[
        (509, "Fibonacci Number", "E", "fibonacci-number", "dp[i] = dp[i−1] + dp[i−2]; keep two variables", "O(n) / O(1)"),
        (70, "Climbing Stairs", "E", "climbing-stairs", "Ways(n) = ways(n−1) + ways(n−2)", "O(n) / O(1)"),
        (1137, "N-th Tribonacci Number", "E", "n-th-tribonacci-number", "Same idea with three previous values", "O(n) / O(1)"),
        (746, "Min Cost Climbing Stairs", "E", "min-cost-climbing-stairs", "dp[i] = cost[i] + min(dp[i−1], dp[i−2])", "O(n) / O(1)"),
        (1025, "Divisor Game", "E", "divisor-game", "dp over n with win / lose states (or parity observation)", "O(n√n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 2
P.append(dict(
    title="Linear DP: take it or skip it (House Robber)", tier="hot", sim="robber", oneline="dp[i] = max(skip i, take i + best before the neighbour)",
    why="The template for most 1D optimisation problems", signature="LC 198 / 213",
    when="You scan a sequence and decide for each item whether to use it, with a rule that forbids some combinations (adjacent items, a cooldown, a distance).",
    detect="\"house robber\" · \"delete and earn\" · \"maximum subarray\" · \"no two adjacent\" · \"questions with brainpower (skip next k)\".",
    intuition="At house `i` you have exactly two choices. **Skip** it: your total is whatever was best for the houses before. **Rob** it: you add its money to the best total that ended **two houses ago** (the neighbour must be untouched). Take the better. Because the choice at `i` only needs answers for smaller prefixes, you can fill a table left to right.",
    brute="Trying all subsets of non-adjacent houses is exponential. The DP considers each house once: O(n).",
    idea="`dp[i]` = best total using houses `0..i`. `dp[i] = max(dp[i−1], dp[i−2] + a[i])`. Base: `dp[0] = a[0]`, `dp[1] = max(a[0], a[1])`. Only two previous values are needed: use two variables.",
    steps=["Define `dp[i]` = best value for the prefix ending at `i`.", "Transition: skip → `dp[i−1]`; take → `a[i] + dp[i−2]`.", "Base cases for the first one or two items.", "Return `dp[n−1]` (or keep `prev1`, `prev2`)."],
    trace_title="`[2,7,9,3,1]`",
    trace="""dp[0] = 2
dp[1] = max(2, 7)            = 7
dp[2] = max(7, 2 + 9)        = 11
dp[3] = max(11, 7 + 3)       = 11
dp[4] = max(11, 11 + 1)      = 12     (rob 2, 9, 1)""",
    code=[("house robber, O(1) space",
           """int prev2 = 0, prev1 = 0;                       // best up to i-2 and i-1
for (int x : a) {
    int cur = Math.max(prev1, prev2 + x);         // skip x, or rob x on top of the best two houses back
    prev2 = prev1;
    prev1 = cur;
}
return prev1;""",
           """prev2 = prev1 = 0                                  # best up to i-2 and i-1
for x in a:
    prev2, prev1 = prev1, max(prev1, prev2 + x)    # skip x, or rob x on top of the best two houses back
return prev1"""),
          ("house robber II: houses in a circle (first and last are adjacent)",
           """int rob(int[] a) {
    int n = a.length;
    if (n == 1) return a[0];
    return Math.max(robRange(a, 0, n - 2), robRange(a, 1, n - 1));      // exclude the last, or exclude the first
}
int robRange(int[] a, int lo, int hi) {
    int p2 = 0, p1 = 0;
    for (int i = lo; i <= hi; i++) { int c = Math.max(p1, p2 + a[i]); p2 = p1; p1 = c; }
    return p1;
}""",
           """def rob(a):
    if len(a) == 1:
        return a[0]
    def rob_range(lo, hi):
        p2 = p1 = 0
        for i in range(lo, hi + 1):
            p2, p1 = p1, max(p1, p2 + a[i])
        return p1
    return max(rob_range(0, len(a) - 2), rob_range(1, len(a) - 1))     # exclude the last, or exclude the first""")],
    complexity="O(n) time, O(1) space.",
    traps=["Do not forget the case `n = 1` (or empty input).", "For the circular version run the linear DP twice on `[0, n−2]` and `[1, n−1]`.",
           "Delete and Earn is House Robber after bucketing by value (`points[v] = v × count`).", "Do not greedily take the largest house: DP considers the whole prefix."],
    variants=["Delete and earn: bucket values, rob with adjacency on the value line.", "Solving questions with brainpower: `dp[i] = max(skip, points + dp[i + brainpower + 1])` from the right.", "Maximum subarray (Kadane) is `dp[i] = max(a[i], dp[i−1] + a[i])`."],
    notuse="When the forbidden pattern depends on more than the last two items (needs a richer state).",
    problems=[
        (198, "House Robber", "M", "house-robber", "dp[i] = max(dp[i−1], dp[i−2] + a[i])", "O(n) / O(1)"),
        (213, "House Robber II", "M", "house-robber-ii", "Linear robber on two ranges (circle)", "O(n) / O(1)"),
        (740, "Delete and Earn", "M", "delete-and-earn", "Bucket by value, then House Robber", "O(n + max) / O(max)"),
        (53, "Maximum Subarray", "M", "maximum-subarray", "dp[i] = max(a[i], dp[i−1] + a[i]) (Kadane)", "O(n) / O(1)"),
        (2140, "Solving Questions With Brainpower", "M", "solving-questions-with-brainpower", "From the right: max(skip, points + dp[i + brain + 1])", "O(n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 3
P.append(dict(
    title="Unbounded choices: coin change", tier="hot", sim="coinchange", oneline="dp[a] = best over each coin c of dp[a − c] plus the coin",
    why="Counting ways and minimum count with reusable items", signature="LC 322 / 518 / 279",
    when="You build a target amount (sum, length, steps) from items you may use any number of times.",
    detect="\"fewest coins\" · \"number of ways to make change\" · \"perfect squares\" · \"combination sum IV\" · \"minimum cost for tickets\".",
    intuition="To make amount `a`, the **last coin** you use must be some coin `c`; before that you made `a − c`. So the best way to make `a` is the best over all coins of (best way to make `a − c`) + 1. Fill the table from 0 upward so every smaller amount is already solved. Greedy fails here (coins 1, 3, 4: greedy 4+1+1, DP 3+3) because the best first coin depends on what remains.",
    brute="Trying all multisets of coins is exponential. The table has `amount + 1` cells and each tries every coin: O(amount × coins).",
    idea="Fewest coins: `dp[0] = 0`, `dp[a] = min(dp[a − c] + 1)` over coins `c ≤ a` (use ∞ for impossible). Number of **combinations**: loop **coins outside**, amounts inside: `dp[a] += dp[a − c]`. Number of **sequences** (order matters): amounts outside, coins inside.",
    steps=["`dp[0]` = base (0 coins / 1 way).", "Initialise other cells to ∞ (min) or 0 (counting).", "Loop amounts (and coins in the right nesting order for counting).", "Answer `dp[amount]`; ∞ means impossible."],
    trace_title="coins `[1,3,4]`, amount 6",
    trace="""dp[0]=0
dp[1]=1  dp[2]=2  dp[3]=min(dp[2]+1, dp[0]+1)=1
dp[4]=1  dp[5]=min(dp[4]+1, dp[2]+1, dp[1]+1)=2
dp[6]=min(dp[5]+1, dp[3]+1, dp[2]+1)=2   (3 + 3)""",
    code=[("minimum coins and number of combinations",
           """// fewest coins
int[] dp = new int[amount + 1];
Arrays.fill(dp, amount + 1);                        // "infinity"
dp[0] = 0;
for (int a = 1; a <= amount; a++)
    for (int c : coins)
        if (c <= a) dp[a] = Math.min(dp[a], dp[a - c] + 1);
int fewest = dp[amount] > amount ? -1 : dp[amount];

// number of COMBINATIONS (order does not matter): coins in the OUTER loop
int[] ways = new int[amount + 1];
ways[0] = 1;
for (int c : coins)
    for (int a = c; a <= amount; a++) ways[a] += ways[a - c];""",
           """# fewest coins
INF = float('inf')
dp = [0] + [INF] * amount
for a in range(1, amount + 1):
    for c in coins:
        if c <= a:
            dp[a] = min(dp[a], dp[a - c] + 1)
fewest = -1 if dp[amount] == INF else dp[amount]

# number of COMBINATIONS (order does not matter): coins in the OUTER loop
ways = [1] + [0] * amount
for c in coins:
    for a in range(c, amount + 1):
        ways[a] += ways[a - c]"""),
          ("perfect squares (the 'coins' are 1, 4, 9, …)",
           """int[] dp = new int[n + 1];
for (int i = 1; i <= n; i++) {
    dp[i] = i;                                          // worst case: all 1s
    for (int s = 1; s * s <= i; s++) dp[i] = Math.min(dp[i], dp[i - s * s] + 1);
}
return dp[n];""",
           """dp = [0] * (n + 1)
for i in range(1, n + 1):
    dp[i] = min(dp[i - s * s] for s in range(1, int(i ** 0.5) + 1)) + 1
return dp[n]""")],
    complexity="O(amount × coins) time, O(amount) space.",
    traps=["Use a sentinel larger than any real answer (`amount + 1`), and convert back to −1.", "Combinations vs permutations: which loop is outer changes the answer.",
           "`dp[a − c]` may be ∞: do not add 1 to an overflowing sentinel (use `amount + 1`, not `Integer.MAX_VALUE`).", "Greedy is wrong for general coin sets (see the greedy topic)."],
    variants=["Combination Sum IV: sequences (amounts outer, coins inner).", "Minimum cost for tickets: DP over days with 1-, 7-, 30-day passes.", "Perfect squares: coins are squares; also solvable with BFS."],
    notuse="Each coin may be used once (that is 0/1 knapsack, topic 16) or the structure is a canonical coin system where greedy is provably optimal.",
    problems=[
        (279, "Perfect Squares", "M", "perfect-squares", "dp[i] = 1 + min over squares s ≤ i of dp[i − s]", "O(n√n) / O(n)"),
        (322, "Coin Change", "M", "coin-change", "dp[a] = min(dp[a − c] + 1)", "O(amount·coins) / O(amount)"),
        (518, "Coin Change II", "M", "coin-change-ii", "Combinations: coins outer, amounts inner", "O(amount·coins) / O(amount)"),
        (377, "Combination Sum IV", "M", "combination-sum-iv", "Sequences: amounts outer, coins inner", "O(target·n) / O(target)"),
        (983, "Minimum Cost For Tickets", "M", "minimum-cost-for-tickets", "dp over travel days with three pass options", "O(days) / O(days)"),
    ]))

# ---------------------------------------------------------------- 4
P.append(dict(
    title="Longest increasing subsequence", tier="hot", sim="lis", oneline="O(n²) with dp[i]; O(n log n) with a tails array and binary search",
    why="The model for \"longest chain\" problems with an ordering rule", signature="LC 300 / 354",
    when="You choose elements in order (not necessarily adjacent) so that each satisfies a relation with the previous one, and want the longest chain.",
    detect="\"longest increasing subsequence\" · \"longest chain of pairs / envelopes / strings\" · \"largest divisible subset\" · \"number of LIS\".",
    intuition="Quadratic DP: the longest increasing subsequence **ending at** `i` is 1 plus the best one ending at some earlier, smaller element. For speed, flip the viewpoint: for every length `k`, remember the **smallest possible last value** of an increasing subsequence of length `k` (`tails[k]`). A smaller tail is always better for extending. The `tails` array is sorted, so a new number replaces the first tail that is ≥ it (binary search) or extends the array.",
    brute="Trying all subsequences is 2ⁿ. `dp[i] = 1 + max dp[j]` over `j < i, a[j] < a[i]` is O(n²). The tails array with binary search gives O(n log n).",
    idea="O(n²): `dp[i] = 1 + max(dp[j])`. O(n log n): for each `x`, `idx = lowerBound(tails, x)`; `tails[idx] = x`; if `idx == size`, size++. The answer is the size. Reduce 2D chains (envelopes) to LIS by sorting one dimension (ties in decreasing order of the other).",
    steps=["Quadratic: initialise `dp[i] = 1`; for each earlier `j` with `a[j] < a[i]` update `dp[i]`.", "Fast version: keep `tails`; binary search the first index with `tails[idx] >= x`.", "Replace or append; the length of `tails` is the LIS length.", "Reconstruct the sequence with predecessor pointers if needed."],
    trace_title="`[10,9,2,5,3,7,101,18]`",
    trace="""10 -> [10]
 9 -> [9]          (replace)
 2 -> [2]
 5 -> [2,5]        (extend)
 3 -> [2,3]        (replace 5)
 7 -> [2,3,7]
101 -> [2,3,7,101]
18 -> [2,3,7,18]    LIS length 4""",
    code=[("O(n log n) LIS with tails and binary search",
           """int[] tails = new int[a.length];
int size = 0;
for (int x : a) {
    int lo = 0, hi = size;                            // first index with tails[idx] >= x
    while (lo < hi) {
        int mid = (lo + hi) >>> 1;
        if (tails[mid] < x) lo = mid + 1; else hi = mid;
    }
    tails[lo] = x;
    if (lo == size) size++;
}
return size;""",
           """from bisect import bisect_left
tails = []
for x in a:
    i = bisect_left(tails, x)                          # first index with tails[i] >= x  (strictly increasing LIS)
    if i == len(tails):
        tails.append(x)
    else:
        tails[i] = x
return len(tails)"""),
          ("O(n²) DP, and longest chain of pairs / strings as the same idea",
           """int[] dp = new int[n];
Arrays.fill(dp, 1);
int best = 1;
for (int i = 1; i < n; i++)
    for (int j = 0; j < i; j++)
        if (a[j] < a[i]) dp[i] = Math.max(dp[i], dp[j] + 1);        // extend the chain that ends at j
for (int v : dp) best = Math.max(best, v);
// pair chain: sort by end, then greedy; or sort by start and use the same dp with "pairs[j][1] < pairs[i][0]\"""",
           """dp = [1] * n
for i in range(1, n):
    for j in range(i):
        if a[j] < a[i]:
            dp[i] = max(dp[i], dp[j] + 1)                 # extend the chain that ends at j
best = max(dp)
# pair chain: sort by end, then greedy; or sort by start and use the same dp with pairs[j][1] < pairs[i][0]""")],
    complexity="O(n²) time / O(n) space for the DP; O(n log n) time / O(n) space with tails.",
    traps=["`tails` is **not** the actual subsequence; only its length is meaningful.", "Strictly increasing → `lowerBound` (first ≥ x); non-decreasing → `upperBound` (first > x).",
           "Russian doll envelopes: sort by width ascending and height **descending** for equal widths, then LIS on heights.", "Number of LIS needs an extra `count[]` array alongside `dp`."],
    variants=["Longest non-decreasing subsequence: use `upperBound`.", "Longest string chain / largest divisible subset: sort, then LIS-style dp with a custom relation.", "Longest bitonic subsequence: LIS from the left and from the right."],
    notuse="When elements must be contiguous (that is a sliding window / Kadane problem).",
    problems=[
        (300, "Longest Increasing Subsequence", "M", "longest-increasing-subsequence", "tails array + binary search", "O(n log n) / O(n)"),
        (646, "Maximum Length of Pair Chain", "M", "maximum-length-of-pair-chain", "Sort by end then greedy (or LIS-style dp)", "O(n log n) / O(1)"),
        (368, "Largest Divisible Subset", "M", "largest-divisible-subset", "Sort; dp[i] = 1 + dp[j] for a[i] % a[j] == 0; rebuild", "O(n²) / O(n)"),
        (1048, "Longest String Chain", "M", "longest-string-chain", "Sort by length; dp over words by deleting one letter", "O(n·L²) / O(n)"),
        (673, "Number of Longest Increasing Subsequence", "M", "number-of-longest-increasing-subsequence", "dp length and count arrays", "O(n²) / O(n)"),
        (354, "Russian Doll Envelopes", "H", "russian-doll-envelopes", "Sort by width asc, height desc; LIS on heights", "O(n log n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 5
P.append(dict(
    title="Grid DP: paths and costs", tier="hot", sim="gridpath", oneline="a cell depends on the cell above and the cell to the left",
    why="The first 2D DP: tables you can see and fill by hand", signature="LC 62 / 64 / 120",
    when="You move through a grid with restricted moves (right / down) and count paths, minimise cost or check feasibility.",
    detect="\"unique paths\" · \"minimum path sum\" · \"triangle\" · \"falling path sum\" · \"dungeon game\" · \"cherry pickup\".",
    intuition="If you may only move right or down, the last step into cell `(i, j)` came either from the cell above or from the cell to the left. So the best cost (or the number of paths) at `(i, j)` is that of the better (or the sum) of those two neighbours, plus the cost of the cell itself. Fill the table row by row so both neighbours are ready. The first row and first column have only one possible predecessor.",
    brute="Exploring every path is exponential (C(m + n, m) paths). The table has m × n cells with O(1) work each.",
    idea="Cost: `dp[i][j] = g[i][j] + min(dp[i−1][j], dp[i][j−1])`. Counting: `dp[i][j] = dp[i−1][j] + dp[i][j−1]`; an obstacle cell is 0. Each row depends only on the previous row, so a single 1D array suffices.",
    steps=["Initialise `dp[0][0]`; fill the first row and column from their single predecessor.", "For the rest use the transition from above and left.", "Obstacles: set the cell to 0 (no paths) before using it.", "The answer is `dp[m−1][n−1]`; to recover the path walk back to the smaller predecessor."],
    trace_title="min path sum, grid `[[1,3,1,2],[1,5,1,3],[4,2,1,1]]`",
    trace="""row0: 1  4  5  7
row1: 2  7  6  9
row2: 6  8  7  8      answer 8
path: (0,0) (0,1) (0,2) (1,2) (2,2) (2,3)""",
    code=[("unique paths and minimum path sum with one row of memory",
           """// number of paths with obstacles (obstacleGrid[i][j] == 1 blocks the cell)
int[] ways = new int[n];
ways[0] = 1;
for (int i = 0; i < m; i++)
    for (int j = 0; j < n; j++) {
        if (g[i][j] == 1) ways[j] = 0;                              // blocked: no path goes through
        else if (j > 0) ways[j] += ways[j - 1];                     // ways[j] already holds "from above"
    }
// minimum path sum
int[] dp = new int[n];
for (int i = 0; i < m; i++)
    for (int j = 0; j < n; j++) {
        if (i == 0 && j == 0) dp[j] = g[0][0];
        else if (i == 0) dp[j] = dp[j - 1] + g[i][j];
        else if (j == 0) dp[j] = dp[j] + g[i][j];
        else dp[j] = g[i][j] + Math.min(dp[j], dp[j - 1]);          // min(from above, from left)
    }""",
           """# number of paths with obstacles
ways = [0] * n
ways[0] = 1
for i in range(m):
    for j in range(n):
        if g[i][j] == 1:
            ways[j] = 0                                             # blocked: no path goes through
        elif j > 0:
            ways[j] += ways[j - 1]                                  # ways[j] already holds "from above"

# minimum path sum
dp = [0] * n
for i in range(m):
    for j in range(n):
        if i == 0 and j == 0:
            dp[j] = g[0][0]
        elif i == 0:
            dp[j] = dp[j - 1] + g[i][j]
        elif j == 0:
            dp[j] += g[i][j]
        else:
            dp[j] = g[i][j] + min(dp[j], dp[j - 1])                 # min(from above, from left)"""),
          ("triangle (bottom-up, in place)",
           """int[] dp = triangle.get(triangle.size() - 1).stream().mapToInt(Integer::intValue).toArray();   // last row
for (int i = triangle.size() - 2; i >= 0; i--)
    for (int j = 0; j <= i; j++)
        dp[j] = triangle.get(i).get(j) + Math.min(dp[j], dp[j + 1]);                                  // the two cells below
return dp[0];""",
           """dp = triangle[-1][:]                                       # start from the last row
for i in range(len(triangle) - 2, -1, -1):
    for j in range(i + 1):
        dp[j] = triangle[i][j] + min(dp[j], dp[j + 1])         # the two cells below
return dp[0]""")],
    complexity="O(m·n) time; O(n) space with a rolling row (O(m·n) if you need the path).",
    traps=["Initialise the first row and column separately (they have only one predecessor).", "With the 1D rolling array, `dp[j]` before the update means \"from above\" and `dp[j−1]` means \"from the left\".",
           "Obstacles on the start or end cell make the answer 0.", "Dungeon Game must be computed **backwards** (minimum health needed), not forwards."],
    variants=["Minimum falling path sum: three predecessors (above-left, above, above-right).", "Dungeon game: dp from the bottom-right with `max(1, …)` health.", "Cherry pickup: two walkers simultaneously (3D state)."],
    notuse="Moves in four directions (that is a graph problem, topic 12) or when cost depends on the whole path.",
    problems=[
        (62, "Unique Paths", "M", "unique-paths", "dp[i][j] = dp[i−1][j] + dp[i][j−1]", "O(m·n) / O(n)"),
        (63, "Unique Paths II", "M", "unique-paths-ii", "Same, with obstacle cells set to 0", "O(m·n) / O(n)"),
        (64, "Minimum Path Sum", "M", "minimum-path-sum", "cost + min(above, left)", "O(m·n) / O(n)"),
        (120, "Triangle", "M", "triangle", "Bottom-up: each cell takes the min of the two below", "O(n²) / O(n)"),
        (931, "Minimum Falling Path Sum", "M", "minimum-falling-path-sum", "Min of three predecessors in the previous row", "O(n²) / O(n)"),
        (174, "Dungeon Game", "H", "dungeon-game", "Backward dp of minimum health required", "O(m·n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 6
P.append(dict(
    title="String DP on prefixes: decode ways", tier="hot", sim="decode", oneline="dp[i] counts the ways for the first i characters, using 1 or 2 characters",
    why="Counting parsings and segmentations over a string", signature="LC 91 / 139",
    when="You count or test the ways to cut a string into valid pieces of small bounded length.",
    detect="\"decode ways\" · \"word break\" · \"count number of texts\" · \"knight dialer\" · \"how many strings can be formed\".",
    intuition="The last piece of a valid decoding is either **one character** or **two characters**. If it is one valid character, the rest is any decoding of the first `i − 1` characters. If it is a valid two-character code (10–26), the rest is a decoding of the first `i − 2`. The total is the sum of the two cases. `dp[0] = 1` represents the empty string (one way: decode nothing).",
    brute="Recursion that tries 1 and 2 characters branches into Fibonacci-like trees of repeated work (2ⁿ). The prefix table solves each length once: O(n).",
    idea="`dp[i] = (s[i−1] != '0' ? dp[i−1] : 0) + (10 ≤ int(s[i−2..i−1]) ≤ 26 ? dp[i−2] : 0)`. For word break: `dp[i] = OR over j < i of dp[j] && dict.contains(s[j..i))`.",
    steps=["`dp[0] = 1`.", "For each `i`: add `dp[i−1]` if the last character is a valid single code.", "Add `dp[i−2]` if the last two characters form a valid pair.", "Answer `dp[n]`."],
    trace_title="`\"226\"`",
    trace="""dp[0] = 1
'2'   valid single           dp[1] = 1
'2'   single: dp[1]=1 ; '22' valid pair: dp[0]=1      dp[2] = 2
'6'   single: dp[2]=2 ; '26' valid pair: dp[1]=1      dp[3] = 3""",
    code=[("decode ways (O(1) space) and word break",
           """int numDecodings(String s) {
    int n = s.length();
    int prev2 = 1, prev1 = s.charAt(0) != '0' ? 1 : 0;           // dp[0], dp[1]
    for (int i = 2; i <= n; i++) {
        int cur = 0;
        if (s.charAt(i - 1) != '0') cur += prev1;                  // last char alone
        int two = Integer.parseInt(s.substring(i - 2, i));
        if (two >= 10 && two <= 26) cur += prev2;                  // last two chars together
        prev2 = prev1; prev1 = cur;
    }
    return prev1;
}
boolean wordBreak(String s, Set<String> dict) {
    boolean[] dp = new boolean[s.length() + 1];
    dp[0] = true;
    for (int i = 1; i <= s.length(); i++)
        for (int j = 0; j < i && !dp[i]; j++)
            if (dp[j] && dict.contains(s.substring(j, i))) dp[i] = true;
    return dp[s.length()];
}""",
           """def num_decodings(s):
    prev2, prev1 = 1, (1 if s[0] != '0' else 0)                  # dp[0], dp[1]
    for i in range(2, len(s) + 1):
        cur = 0
        if s[i - 1] != '0':
            cur += prev1                                          # last char alone
        if 10 <= int(s[i - 2:i]) <= 26:
            cur += prev2                                          # last two chars together
        prev2, prev1 = prev1, cur
    return prev1

def word_break(s, words):
    words = set(words)
    dp = [True] + [False] * len(s)
    for i in range(1, len(s) + 1):
        dp[i] = any(dp[j] and s[j:i] in words for j in range(i))
    return dp[-1]"""),
          ("count number of texts (phone keys with 3 or 4 letters)",
           """final int MOD = 1_000_000_007;
long[] dp = new long[n + 1];
dp[0] = 1;
for (int i = 1; i <= n; i++) {
    int maxRun = (s.charAt(i - 1) == '7' || s.charAt(i - 1) == '9') ? 4 : 3;   // keys 7 and 9 have 4 letters
    for (int k = 1; k <= maxRun && i - k >= 0; k++) {
        if (k > 1 && s.charAt(i - k) != s.charAt(i - 1)) break;                // the run of equal presses ends
        dp[i] = (dp[i] + dp[i - k]) % MOD;
    }
}
return (int) dp[n];""",
           """MOD = 10**9 + 7
n = len(s)
dp = [1] + [0] * n
for i in range(1, n + 1):
    max_run = 4 if s[i - 1] in '79' else 3                        # keys 7 and 9 have 4 letters
    for k in range(1, max_run + 1):
        if i - k < 0 or (k > 1 and s[i - k] != s[i - 1]):
            break                                                 # the run of equal presses ends
        dp[i] = (dp[i] + dp[i - k]) % MOD
return dp[n]""")],
    complexity="O(n) time (O(n·L) for word break with a hash set), O(1)–O(n) space.",
    traps=["A lone `'0'` is invalid; `\"10\"` and `\"20\"` are valid only as pairs.", "Strings starting with `'0'` have 0 ways.",
           "`dp[i]` refers to the first `i` characters, so the character at `s[i − 1]` is the last one.", "Take the modulus after every addition when the problem asks for it."],
    variants=["Decode Ways II with `*` wildcards (more cases per transition).", "Knight dialer: dp over (step, digit) with the knight's neighbour table.", "Count vowels permutation: dp over the last letter."],
    notuse="Pieces of unbounded length without structure (then you need substring checks or tries, topic 11).",
    problems=[
        (91, "Decode Ways", "M", "decode-ways", "dp[i] = single (dp[i−1]) + pair (dp[i−2])", "O(n) / O(1)"),
        (139, "Word Break", "M", "word-break", "dp[i] true if some dp[j] and s[j..i) is a word", "O(n²) / O(n)"),
        (2266, "Count Number of Texts", "M", "count-number-of-texts", "dp over runs of identical key presses (3 or 4 long)", "O(n) / O(n)"),
        (935, "Knight Dialer", "M", "knight-dialer", "dp over (moves left, digit) with neighbour lists", "O(10·n) / O(10)"),
        (639, "Decode Ways II", "H", "decode-ways-ii", "Same recurrence with * multiplicities", "O(n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 7
P.append(dict(
    title="2D DP on a matrix: largest square", tier="hot", sim="square", oneline="a corner's square is limited by its three neighbours",
    why="Teaches 2D states that depend on three neighbours", signature="LC 221 / 1277",
    when="You look for the biggest shape ending at each cell of a 0/1 matrix (square, plus sign, bordered square).",
    detect="\"maximal square\" · \"count square submatrices\" · \"largest plus sign\" · \"largest 1-bordered square\".",
    intuition="Let `dp[i][j]` be the side of the largest all-1 square whose **bottom-right corner** is `(i, j)`. A square of side `k` ending there needs squares of side `k − 1` ending at the cell above, the cell to the left and the cell diagonally above-left. So the side can be at most one more than the **smallest** of those three. This \"corner\" definition also counts all squares: a corner with value `k` is the corner of exactly `k` squares (sides 1..k).",
    brute="Checking every square for all ones is O((mn)·min(m,n)²). The DP does O(1) work per cell.",
    idea="If `g[i][j] == 0` then `dp = 0`; else `dp[i][j] = 1 + min(dp[i−1][j], dp[i][j−1], dp[i−1][j−1])` (with out-of-range neighbours counted as 0). Answer: `max(dp)²` for the maximal square, or `sum(dp)` for the number of squares.",
    steps=["Create `dp` (or work in place if modifying the input is allowed).", "Zero cell → `dp = 0`.", "One cell → 1 + min of above, left, above-left (0 if outside).", "Track the maximum side, or add every `dp` to a total."],
    trace_title="maximal square in a 4×5 matrix",
    trace="""1 0 1 0 0        1 0 1 0 0
1 0 1 1 1   ->   1 0 1 1 1
1 1 1 1 1        1 1 1 2 2     the 2s are corners of 2x2 squares
1 0 0 1 0        1 0 0 1 0     max side 2, area 4""",
    code=[("maximal square and count of square submatrices",
           """int m = g.length, n = g[0].length, side = 0, count = 0;
int[][] dp = new int[m + 1][n + 1];                      // extra row / column of zeros removes boundary cases
for (int i = 1; i <= m; i++)
    for (int j = 1; j <= n; j++) {
        if (g[i - 1][j - 1] == '1') {
            dp[i][j] = 1 + Math.min(dp[i - 1][j], Math.min(dp[i][j - 1], dp[i - 1][j - 1]));
            side = Math.max(side, dp[i][j]);
            count += dp[i][j];                           // a corner of value k is the corner of k squares
        }
    }
int area = side * side;""",
           """m, n = len(g), len(g[0])
dp = [[0] * (n + 1) for _ in range(m + 1)]               # extra row / column of zeros removes boundary cases
side = count = 0
for i in range(1, m + 1):
    for j in range(1, n + 1):
        if g[i - 1][j - 1] == '1':
            dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
            side = max(side, dp[i][j])
            count += dp[i][j]                            # a corner of value k is the corner of k squares
area = side * side"""),
          ("largest plus sign (four directional runs, take the minimum)",
           """int[][] dp = new int[n][n];
for (int[] row : dp) Arrays.fill(row, n);                 // best arm length seen so far, capped by n
for (int[] m : mines) dp[m[0]][m[1]] = 0;
for (int i = 0; i < n; i++) {
    int l = 0, r = 0, u = 0, d = 0;
    for (int j = 0, k = n - 1; j < n; j++, k--) {
        l = dp[i][j] == 0 ? 0 : l + 1; dp[i][j] = Math.min(dp[i][j], l);       // run of ones ending at (i, j) from the left
        r = dp[i][k] == 0 ? 0 : r + 1; dp[i][k] = Math.min(dp[i][k], r);       // ... from the right
        u = dp[j][i] == 0 ? 0 : u + 1; dp[j][i] = Math.min(dp[j][i], u);       // ... from above
        d = dp[k][i] == 0 ? 0 : d + 1; dp[k][i] = Math.min(dp[k][i], d);       // ... from below
    }
}""",
           """dp = [[n] * n for _ in range(n)]                          # best arm length seen so far, capped by n
for x, y in mines:
    dp[x][y] = 0
for i in range(n):
    l = r = u = d = 0
    for j in range(n):
        k = n - 1 - j
        l = l + 1 if dp[i][j] else 0; dp[i][j] = min(dp[i][j], l)       # run of ones from the left
        r = r + 1 if dp[i][k] else 0; dp[i][k] = min(dp[i][k], r)       # ... from the right
        u = u + 1 if dp[j][i] else 0; dp[j][i] = min(dp[j][i], u)       # ... from above
        d = d + 1 if dp[k][i] else 0; dp[k][i] = min(dp[k][i], d)       # ... from below
best = max(max(row) for row in dp)""")],
    complexity="O(m·n) time, O(m·n) space (O(n) with a rolling row plus one saved value).",
    traps=["The **bottom-right corner** definition is what makes the min of three neighbours correct.", "Characters `'1'` vs integers `1`: read the input type.",
           "Report the **area** (`side²`), not the side, for Maximal Square.", "A padded `(m+1) × (n+1)` array avoids special-casing the first row and column."],
    variants=["Count square submatrices: sum of all dp values.", "Maximal rectangle: histogram + stack per row (topic 05), not this DP.", "Largest 1-bordered square: precompute consecutive-ones runs to the right and down."],
    notuse="Rectangles (use the histogram method) or shapes whose size is not limited by neighbours in this way.",
    problems=[
        (221, "Maximal Square", "M", "maximal-square", "dp = 1 + min(above, left, above-left); area = max²", "O(m·n) / O(n)"),
        (1277, "Count Square Submatrices with All Ones", "M", "count-square-submatrices-with-all-ones", "Same dp; add every cell's value", "O(m·n) / O(m·n)"),
        (764, "Largest Plus Sign", "M", "largest-plus-sign", "Four directional run lengths; take the minimum per cell", "O(n²) / O(n²)"),
        (1139, "Largest 1-Bordered Square", "M", "largest-1-bordered-square", "Runs of ones to the right and below; check candidate sizes", "O(n³) / O(n²)"),
    ]))

# ---------------------------------------------------------------- 8
P.append(dict(
    title="State-machine DP: stock with cooldown", tier="hot", sim="cooldown", oneline="a few named states; transitions are the allowed moves between them",
    why="Turns messy rules (cooldown, fee, k transactions) into a clean table", signature="LC 309 / 123 / 188",
    when="Each step you can be in one of a few **modes**, and the rules say which mode can follow which.",
    detect="\"best time to buy and sell with cooldown\" · \"at most k transactions\" · \"wiggle subsequence\" · \"minimum swaps to make sequences increasing\" · any rule like \"after X you must wait\".",
    intuition="Draw the situation as a small diagram: circles are modes (holding a share, just sold, resting), arrows are the legal moves. On each day, the best profit in a mode is the best over the arrows that lead into it, applied to **yesterday's** values. The cooldown rule is nothing more than the absence of an arrow from `sold` directly to `hold`. Only yesterday's values matter, so a few variables replace a table.",
    brute="Recursive search over buy / sell / skip decisions is exponential. Tracking the best profit per mode per day is O(n × modes).",
    idea="`hold`, `sold`, `rest`. Each day, computed from the previous values: `sold = hold + price`; `hold = max(hold, rest − price)`; `rest = max(rest, sold_prev)`. Answer `max(sold, rest)`. For at most `k` transactions keep `buy[j]` and `sell[j]` for each transaction count.",
    steps=["Name the states and what each means.", "Write every legal transition into each state.", "Update all states from the previous day's values (compute with temporaries).", "Answer: the best of the \"not holding\" states at the end."],
    trace_title="prices `[1,2,3,0,2]` with cooldown",
    trace="""day0: hold -1  sold 0  rest 0
day1 (2): sold 1  hold -1  rest 0
day2 (3): sold 2  hold -1  rest 1
day3 (0): sold -1 hold 1   rest 2
day4 (2): sold 3  hold 1   rest 2     answer max(3, 2) = 3""",
    code=[("best time to buy and sell with cooldown",
           """int hold = -prices[0], sold = 0, rest = 0;
for (int i = 1; i < prices.length; i++) {
    int prevSold = sold;
    sold = hold + prices[i];                          // sell today
    hold = Math.max(hold, rest - prices[i]);          // keep holding, or buy today (only from rest!)
    rest = Math.max(rest, prevSold);                  // do nothing, or finish yesterday's cooldown
}
return Math.max(sold, rest);""",
           """hold, sold, rest = -prices[0], 0, 0
for p in prices[1:]:
    prev_sold = sold
    sold = hold + p                                    # sell today
    hold = max(hold, rest - p)                         # keep holding, or buy today (only from rest!)
    rest = max(rest, prev_sold)                        # do nothing, or finish yesterday's cooldown
return max(sold, rest)"""),
          ("at most k transactions",
           """if (k >= prices.length / 2) {                                     // unlimited: sum of rises
    int profit = 0;
    for (int i = 1; i < prices.length; i++) profit += Math.max(0, prices[i] - prices[i - 1]);
    return profit;
}
int[] buy = new int[k + 1], sell = new int[k + 1];
Arrays.fill(buy, Integer.MIN_VALUE / 2);
for (int p : prices)
    for (int j = 1; j <= k; j++) {
        buy[j] = Math.max(buy[j], sell[j - 1] - p);                   // j-th buy, after j-1 completed sells
        sell[j] = Math.max(sell[j], buy[j] + p);                      // j-th sell
    }
return sell[k];""",
           """if k >= len(prices) // 2:                                           # unlimited: sum of rises
    return sum(max(0, prices[i] - prices[i - 1]) for i in range(1, len(prices)))
buy = [float('-inf')] * (k + 1)
sell = [0] * (k + 1)
for p in prices:
    for j in range(1, k + 1):
        buy[j] = max(buy[j], sell[j - 1] - p)                           # j-th buy, after j-1 completed sells
        sell[j] = max(sell[j], buy[j] + p)                              # j-th sell
return sell[k]""")],
    complexity="O(n) time, O(1) space for cooldown; O(n·k) time, O(k) space for k transactions.",
    traps=["Update all states from the **previous** values (use temporaries) or the cooldown leaks.", "Initialise `hold` with `−prices[0]` and the others with 0; unreachable states use −∞.",
           "Count a transaction when you **buy** (or sell) consistently.", "For large `k` fall back to the unlimited greedy to avoid TLE and memory blowups."],
    variants=["Stock with transaction fee: two states (cash, hold) (topic 14).", "Wiggle subsequence: states `up` and `down`.", "Minimum swaps to make sequences increasing: states `swapped` / `not swapped` at each index."],
    notuse="Problems with a single obvious rule that a plain greedy solves.",
    problems=[
        (376, "Wiggle Subsequence", "M", "wiggle-subsequence", "Two states: last move up or down", "O(n) / O(1)"),
        (309, "Best Time to Buy and Sell Stock with Cooldown", "M", "best-time-to-buy-and-sell-stock-with-cooldown", "hold / sold / rest states", "O(n) / O(1)"),
        (123, "Best Time to Buy and Sell Stock III", "H", "best-time-to-buy-and-sell-stock-iii", "k = 2 transactions: four running states", "O(n) / O(1)"),
        (188, "Best Time to Buy and Sell Stock IV", "H", "best-time-to-buy-and-sell-stock-iv", "buy[j] / sell[j] arrays for k transactions", "O(n·k) / O(k)"),
        (801, "Minimum Swaps To Make Sequences Increasing", "H", "minimum-swaps-to-make-sequences-increasing", "Two states per index: swapped or kept", "O(n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 9
P.append(dict(
    title="Space optimisation and reconstructing the answer", tier="hot", sim="rebuild", oneline="keep only the rows you need, or store the choices to rebuild the path",
    why="Two follow-up questions that appear after almost every DP solution", signature="LC 118 / 119 / 322",
    when="The interviewer asks \"can you use less memory?\" or \"can you return the actual solution, not just its value?\".",
    detect="\"return the coins / path / subsequence\" · \"O(1) or O(n) space\" · Pascal's triangle row · rolling-array DPs.",
    intuition="A DP table is a map of answers. If each row only reads the previous row, you can throw old rows away: reuse one array (iterate in the direction that does not overwrite values you still need). But the same table can also say **how** each value was obtained: store the winning choice in a parallel table and walk it from the target back to the start. You usually can't have both: a rolling array forgets the choices.",
    brute="Keeping the full table costs O(states). Rolling arrays reduce 2D DP to O(width) and 1D DP with k look-backs to O(k).",
    idea="Space: write `dp[j]` in place; iterate `j` **backwards** when the update reads smaller indices of the old row (0/1 knapsack, Pascal row), **forwards** when it should read the already updated ones (unbounded). Reconstruction: keep `choice[state]` (which move / predecessor produced the optimum) and follow it back from the answer state.",
    steps=["Identify which previous cells each cell reads.", "If only the previous row / last k values: shrink the table.", "Choose the loop direction so reads see the correct (old or new) values.", "For the actual solution: store `choice[]` / `parent[]`, then backtrack from the target."],
    trace_title="coin change coins `[1,3,4]`, amount 6: reconstruction",
    trace="""dp     = [0, 1, 2, 1, 1, 2, 2]
choice = [-, 1, 1, 3, 4, 1, 3]
6 -> choice 3 -> 3 -> choice 3 -> 0
coins used: [3, 3]""",
    code=[("reconstruct the coins used",
           """int[] dp = new int[amount + 1], choice = new int[amount + 1];
Arrays.fill(dp, Integer.MAX_VALUE); dp[0] = 0;
for (int a = 1; a <= amount; a++)
    for (int c : coins)
        if (c <= a && dp[a - c] != Integer.MAX_VALUE && dp[a - c] + 1 < dp[a]) { dp[a] = dp[a - c] + 1; choice[a] = c; }
List<Integer> used = new ArrayList<>();
for (int a = amount; a > 0 && dp[amount] != Integer.MAX_VALUE; a -= choice[a]) used.add(choice[a]);     // walk back""",
           """INF = float('inf')
dp, choice = [0] + [INF] * amount, [0] * (amount + 1)
for a in range(1, amount + 1):
    for c in coins:
        if c <= a and dp[a - c] + 1 < dp[a]:
            dp[a], choice[a] = dp[a - c] + 1, c
used, a = [], amount
while a > 0 and dp[amount] != INF:
    used.append(choice[a])                                  # walk back from the target
    a -= choice[a]"""),
          ("Pascal's triangle row in O(k) space (update backwards)",
           """List<Integer> row = new ArrayList<>(Collections.nCopies(k + 1, 0));
row.set(0, 1);
for (int i = 1; i <= k; i++)
    for (int j = i; j >= 1; j--)                            // BACKWARDS so row[j - 1] is still the old value
        row.set(j, row.get(j) + row.get(j - 1));""",
           """row = [1] + [0] * k
for i in range(1, k + 1):
    for j in range(i, 0, -1):                               # BACKWARDS so row[j - 1] is still the old value
        row[j] += row[j - 1]""")],
    complexity="Rolling arrays: space O(width). Reconstruction: extra O(states) for the choice table and O(path length) to walk back.",
    traps=["Iterate in the right direction: wrong direction silently uses the new value instead of the old (this is the 0/1 vs unbounded knapsack difference).", "A rolling array cannot reconstruct a path; keep a parent table, or recompute with a second pass.",
           "When reconstructing, verify that `dp[target]` is reachable before walking back.", "Ties: any optimal solution is usually accepted; mention how you break ties."],
    variants=["LIS reconstruction: store the predecessor index of each element.", "Longest common subsequence / edit distance reconstruction: walk the table from the corner (topic 16).", "Hirschberg's algorithm recovers the LCS path in O(n) space."],
    notuse="Do not optimise space before the solution is correct; first write the plain table.",
    problems=[
        (118, "Pascal's Triangle", "E", "pascals-triangle", "Each entry is the sum of the two above", "O(n²) / O(n²)"),
        (119, "Pascal's Triangle II", "E", "pascals-triangle-ii", "One row, update from the right", "O(k²) / O(k)"),
        (1262, "Greatest Sum Divisible by Three", "M", "greatest-sum-divisible-by-three", "dp over remainder 0, 1, 2 (3 rolling states)", "O(n) / O(1)"),
        (1043, "Partition Array for Maximum Sum", "M", "partition-array-for-maximum-sum", "dp[i] = best over the last k group sizes", "O(n·k) / O(n)"),
        (322, "Coin Change", "M", "coin-change", "Add a choice table to recover the coins", "O(amount·coins) / O(amount)"),
    ]))

TOPIC = dict(
    id="dp1", file="15_dp_1d_2d.html", title="Dynamic Programming I — 1D and 2D Patterns",
    lead="Dynamic programming is recursion with a memory. This guide builds the habit step by step: define the state, write the transition, set the base cases, choose the order. Then the first families: take-or-skip (House Robber), unbounded choices (coin change), longest increasing subsequence, grid paths, string prefixes (decode ways), 2D matrix DP (largest square), state machines (stock with cooldown) and the two standard follow-ups: use less memory, and return the actual solution. Each pattern has the intuition, a step-through animation that fills the table, Java and Python code, and a ladder of LeetCode problems.",
    mindset="Every DP is answered by the same sentence: **\"`dp[state]` is the best / count / feasibility of ___ , and it is built from smaller states by ___.\"** If you cannot finish that sentence, the state is wrong. Write the brute-force recursion first, notice the repeated arguments, add a cache, and only then convert it to a loop and trim the space.",
    qintro="Ask these questions on every DP problem:",
    questions=["**What decision is made at each step, and what do I need to remember about the past?** → the state.", "**What does `dp[state]` mean in one sentence?**", "**Which smaller states does it depend on?** → the transition and the loop order.",
               "**What are the base cases?**", "**Is it counting (+), optimising (min / max) or feasibility (OR)?** → the operator."],
    cues=[
        ["a recursion that repeats the same arguments", "**P1** DP fundamentals"],
        ["\"no two adjacent\", take or skip each item", "**P2** Linear DP"],
        ["\"fewest coins\", \"number of ways to reach a sum\", items reusable", "**P3** Unbounded DP"],
        ["\"longest increasing / chain of\"", "**P4** LIS"],
        ["moves right / down, grid costs and counts", "**P5** Grid DP"],
        ["count ways to cut / decode a string", "**P6** String prefix DP"],
        ["largest square / shape ending at each cell", "**P7** Matrix DP"],
        ["cooldown, fee, \"at most k\" transactions, modes", "**P8** State-machine DP"],
        ["\"use less space\" or \"return the solution\"", "**P9** Rolling arrays and reconstruction"],
    ],
    choose=[
        ["Choices interact; a greedy rule is unprovable", "Dynamic programming"],
        ["Decide per item with a forbidden pattern", "Take-or-skip DP (P2)"],
        ["Reusable items, a target total", "Unbounded DP (P3)"],
        ["Ordered chain with a relation", "LIS-style DP (P4)"],
        ["Rectangular table of positions", "Grid / matrix DP (P5, P7)"],
        ["Several modes with transition rules", "State machine (P8)"],
        ["Follow-up: memory or the actual answer", "Rolling arrays / choice table (P9)"],
    ],
    rule="**state → meaning → transition → base case → order → answer.** If a cell only reads the previous row or the last two values, keep only those; if you must output the solution, keep a choice table.",
    selftest=[
        ("What two properties must a problem have for DP to apply?", "Overlapping subproblems (the same sub-answers are needed repeatedly) and optimal substructure (the answer is built from sub-answers)."),
        ("What is the difference between memoisation and tabulation?", "Memoisation is top-down recursion with a cache; tabulation is bottom-up, filling the table in dependency order. Both visit each state once."),
        ("In House Robber, what are the two choices at house i and the resulting recurrence?", "Skip it (dp[i−1]) or rob it (a[i] + dp[i−2]); take the maximum."),
        ("In coin change, why does the loop nesting decide combinations versus permutations?", "With coins in the outer loop each coin is considered in a fixed order, so multisets are counted once; with amounts outer and coins inner every order is counted separately."),
        ("Why is the O(n log n) LIS tails array always sorted?", "tails[k] is the smallest possible tail of an increasing subsequence of length k + 1, and shorter subsequences can always end with a smaller value, so the array is increasing."),
        ("In Maximal Square, why do we take the minimum of three neighbours?", "A square of side k needs squares of side k − 1 ending at the cell above, to the left and diagonally above-left; the smallest of the three limits how far it can grow."),
        ("How do you reconstruct the solution from a DP table?", "Store the choice that produced each optimal value (or recompute it), then walk back from the answer state following those choices to the base case."),
        ("When must a rolling array iterate backwards?", "When the update reads indices from the previous row that the forward sweep would already have overwritten (0/1 knapsack, Pascal's row)."),
    ],
    plan=[
        "**Day 1:** fundamentals: naïve recursion → memo → table → rolling variables for Fibonacci and climbing stairs.",
        "**Day 2:** take-or-skip: House Robber I and II, Delete and Earn, Maximum Subarray.",
        "**Day 3:** coin change (min and ways) and perfect squares; write the loop-order rule on paper.",
        "**Day 4:** LIS O(n²) then O(n log n); one chain problem (pairs or strings).",
        "**Day 5:** grid DP and string-prefix DP (decode ways, word break).",
        "**Day 6:** matrix DP (maximal square), state machines (stock cooldown), then reconstruct the answer for coin change.",
    ],
    patterns=P,
)
