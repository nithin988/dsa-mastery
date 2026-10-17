"""Content for topic 16: Dynamic programming II (knapsack, sequences, intervals, bitmasks, digits)."""

P = []

# ---------------------------------------------------------------- 1
P.append(dict(
    title="0/1 knapsack and subset sum", tier="hot", sim="knap01", oneline="each item is taken once: update the table from high to low",
    why="The parent of a whole family: partition, target sum, bounded budgets", signature="LC 416 / 494",
    when="You choose a subset of items, each at most once, subject to a capacity or a target sum.",
    detect="\"partition equal subset sum\" · \"target sum with + and −\" · \"last stone weight II\" · \"can we reach exactly this total\" · \"maximise value within weight W\".",
    intuition="Go through the items one at a time and keep a table of every total you can reach using the items seen so far. For a new item `x` each reachable total `s − x` creates a new reachable total `s`. If you update the table from **small totals to large**, the item can feed itself and gets used twice (that is the unbounded knapsack). Updating from **large to small** guarantees every update reads values from *before* this item, so each item is used at most once.",
    brute="Trying all 2ⁿ subsets is exponential. The table has `target + 1` cells and each item touches each cell once: O(n · target).",
    idea="`dp[s]` = can (or in how many ways) some chosen items sum to `s`. For each item `x`: `for s = target down to x: dp[s] |= dp[s − x]` (or `+=` to count, `max(dp[s], dp[s − w] + v)` for values). Many problems reduce to a target: partition → `sum / 2`; target sum with signs → `(sum + target) / 2`.",
    steps=["Reduce the problem to \"choose a subset with total T\".", "`dp[0] = true` (empty subset).", "For every item, loop `s` from `T` **down** to the item's weight.", "Answer `dp[T]` (or the best value)."],
    trace_title="`[1, 5, 11, 5]`, target 11",
    trace="""dp: only 0 reachable
item 1  -> 1
item 5  -> 5, 6
item 11 -> 11, 12 ...      (target 11 reached)
item 5  -> 10, 15, 16 ...  (also 5 + 5 + 1 = 11)""",
    code=[("partition equal subset sum and target sum",
           """boolean canPartition(int[] nums) {
    int sum = 0;
    for (int x : nums) sum += x;
    if (sum % 2 != 0) return false;
    int target = sum / 2;
    boolean[] dp = new boolean[target + 1];
    dp[0] = true;
    for (int x : nums)
        for (int s = target; s >= x; s--) dp[s] |= dp[s - x];           // downwards: each item used once
    return dp[target];
}

int findTargetSumWays(int[] nums, int target) {                           // assign + or - to every number
    int sum = 0;
    for (int x : nums) sum += x;
    if (Math.abs(target) > sum || (sum + target) % 2 != 0) return 0;      // positives P: 2P = sum + target
    int goal = (sum + target) / 2;
    int[] dp = new int[goal + 1];
    dp[0] = 1;
    for (int x : nums)
        for (int s = goal; s >= x; s--) dp[s] += dp[s - x];
    return dp[goal];
}""",
           """def can_partition(nums):
    total = sum(nums)
    if total % 2:
        return False
    target = total // 2
    dp = [True] + [False] * target
    for x in nums:
        for s in range(target, x - 1, -1):                                # downwards: each item used once
            dp[s] = dp[s] or dp[s - x]
    return dp[target]

def find_target_sum_ways(nums, target):                                   # assign + or - to every number
    total = sum(nums)
    if abs(target) > total or (total + target) % 2:
        return 0                                                          # positives P: 2P = total + target
    goal = (total + target) // 2
    dp = [1] + [0] * goal
    for x in nums:
        for s in range(goal, x - 1, -1):
            dp[s] += dp[s - x]
    return dp[goal]"""),
          ("classic 0/1 knapsack with weights and values",
           """int knapsack(int[] w, int[] v, int cap) {
    int[] dp = new int[cap + 1];                                          // dp[c] = best value with capacity c
    for (int i = 0; i < w.length; i++)
        for (int c = cap; c >= w[i]; c--) dp[c] = Math.max(dp[c], dp[c - w[i]] + v[i]);
    return dp[cap];
}""",
           """def knapsack(w, v, cap):
    dp = [0] * (cap + 1)                                                  # dp[c] = best value with capacity c
    for wi, vi in zip(w, v):
        for c in range(cap, wi - 1, -1):
            dp[c] = max(dp[c], dp[c - wi] + vi)
    return dp[cap]""")],
    complexity="O(n · target) time, O(target) space (pseudo-polynomial: depends on the numeric value of the target).",
    traps=["Loop capacity **downwards** for 0/1, **upwards** for unbounded; swapping them is the classic bug.", "Reduce \"+/− signs\" problems to subset sum with `(sum + target) / 2`, and check parity and range first.",
           "Counting versions initialise `dp[0] = 1`; feasibility versions use booleans; value versions start from 0.", "A negative or huge target makes the table impractical: say so."],
    variants=["Last stone weight II: partition the stones into two groups with minimal difference (subset sum up to `sum / 2`).", "Number of dice rolls with a target sum: bounded choice per item (1..k).", "Bitset speed-up: represent `dp` as a bitset and shift (`dp |= dp << x`)."],
    notuse="Items may be reused (unbounded: coin change, topic 15) or the values are huge and fractional (greedy / other methods).",
    problems=[
        (416, "Partition Equal Subset Sum", "M", "partition-equal-subset-sum", "Subset sum to half of the total", "O(n·sum) / O(sum)"),
        (494, "Target Sum", "M", "target-sum", "Count subsets with sum (total + target) / 2", "O(n·sum) / O(sum)"),
        (1049, "Last Stone Weight II", "M", "last-stone-weight-ii", "Best subset sum ≤ total / 2; answer total − 2·best", "O(n·sum) / O(sum)"),
        (1155, "Number of Dice Rolls With Target Sum", "M", "number-of-dice-rolls-with-target-sum", "dp[dice][sum] over faces 1..k", "O(d·t·k) / O(t)"),
    ]))

# ---------------------------------------------------------------- 2
P.append(dict(
    title="Multi-dimensional knapsack", tier="sec", sim="ones", oneline="two (or more) budgets: add a dimension to the table",
    why="Knapsack with several constraints at once", signature="LC 474 / 879",
    when="Every item consumes more than one resource (zeros and ones, people and profit), and you must stay within all budgets.",
    detect="\"ones and zeroes\" · \"profitable schemes\" · \"painting the walls\" · \"at most m of X and n of Y\" · \"tallest billboard\".",
    intuition="With one budget the table is a row of totals. With two budgets you need a **grid**: one axis per resource. Each item still has the 0/1 choice, so each cell is updated from the cell at (budget − item cost), and you sweep **both** axes from high to low so an item cannot be used twice in one pass.",
    brute="All subsets: 2ⁿ. A grid of `(m + 1) × (n + 1)` cells updated once per item is O(len · m · n).",
    idea="`dp[i][j]` = best value using at most `i` of resource A and `j` of resource B. For an item with cost `(a, b)` and value `v`: `for i = m down to a: for j = n down to b: dp[i][j] = max(dp[i][j], dp[i − a][j − b] + v)`. For \"at least profit P\" problems cap the profit axis at `P`.",
    steps=["Define one axis per constrained resource.", "Initialise the grid (0 for \"at most\" problems, `dp[0][0] = 1` for counting).", "For every item, update both axes downwards.", "Read the answer from the corner cell (or sum the right column)."],
    trace_title="strings `10 0001 111001 1 0`, at most 5 zeros and 3 ones",
    trace="""\"10\"     costs (1 zero, 1 one)
\"0001\"   costs (3, 1)
\"111001\" costs (2, 4) -> too many ones, skip
\"1\"      costs (0, 1)
\"0\"      costs (1, 0)
best subset: 10, 0001, 1, 0  -> 4""",
    code=[("ones and zeroes",
           """int findMaxForm(String[] strs, int m, int n) {
    int[][] dp = new int[m + 1][n + 1];
    for (String s : strs) {
        int zeros = 0, ones = 0;
        for (char c : s.toCharArray()) { if (c == '0') zeros++; else ones++; }
        for (int i = m; i >= zeros; i--)                        // both loops downwards: 0/1 choice
            for (int j = n; j >= ones; j--)
                dp[i][j] = Math.max(dp[i][j], dp[i - zeros][j - ones] + 1);
    }
    return dp[m][n];
}""",
           """def find_max_form(strs, m, n):
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for s in strs:
        zeros, ones = s.count('0'), s.count('1')
        for i in range(m, zeros - 1, -1):                       # both loops downwards: 0/1 choice
            for j in range(n, ones - 1, -1):
                dp[i][j] = max(dp[i][j], dp[i - zeros][j - ones] + 1)
    return dp[m][n]"""),
          ("profitable schemes (count ways; profit axis capped at the minimum)",
           """int profitableSchemes(int n, int minProfit, int[] group, int[] profit) {
    final int MOD = 1_000_000_007;
    int[][] dp = new int[n + 1][minProfit + 1];                  // dp[people][min(profit, minProfit)]
    dp[0][0] = 1;
    for (int k = 0; k < group.length; k++) {
        int g = group[k], p = profit[k];
        for (int i = n; i >= g; i--)
            for (int j = 0; j <= minProfit; j++) {
                int nj = Math.min(minProfit, j + p);               // profit beyond the minimum is all the same
                dp[i][nj] = (dp[i][nj] + dp[i - g][j]) % MOD;
            }
    }
    int total = 0;
    for (int i = 0; i <= n; i++) total = (total + dp[i][minProfit]) % MOD;
    return total;
}""",
           """def profitable_schemes(n, min_profit, group, profit):
    MOD = 10**9 + 7
    dp = [[0] * (min_profit + 1) for _ in range(n + 1)]          # dp[people][min(profit, min_profit)]
    dp[0][0] = 1
    for g, p in zip(group, profit):
        for i in range(n, g - 1, -1):
            for j in range(min_profit + 1):
                nj = min(min_profit, j + p)                        # profit beyond the minimum is all the same
                dp[i][nj] = (dp[i][nj] + dp[i - g][j]) % MOD
    return sum(dp[i][min_profit] for i in range(n + 1)) % MOD""")],
    complexity="O(items · m · n) time, O(m · n) space.",
    traps=["Both axes must be updated **downwards** so one item is not applied twice.", "Items that exceed a budget on their own must be skipped (the loops do this automatically with the lower bounds).",
           "For \"at least P\" requirements cap the axis at `P` (any larger profit is equivalent).", "Counting problems need the modulus after every addition."],
    variants=["Three or more resources: add more dimensions (watch the memory).", "Painting the walls: capacity is time, with free painting as a bonus dimension.", "Tallest billboard: DP on the difference between two supports."],
    notuse="A single capacity (use the 1D table) or constraints that interact in non-additive ways.",
    problems=[
        (474, "Ones and Zeroes", "M", "ones-and-zeroes", "2D knapsack: zeros and ones are the two capacities", "O(L·m·n) / O(m·n)"),
        (879, "Profitable Schemes", "H", "profitable-schemes", "dp[people][profit capped at the minimum]", "O(k·n·P) / O(n·P)"),
        (2742, "Painting the Walls", "H", "painting-the-walls", "Knapsack where free painter time counts as a bonus", "O(n²) / O(n)"),
        (956, "Tallest Billboard", "H", "tallest-billboard", "dp[difference of the two supports] = tallest shared height", "O(n·S) / O(S)"),
    ]))

# ---------------------------------------------------------------- 3
P.append(dict(
    title="Longest common subsequence", tier="hot", sim="lcs", oneline="a table of prefix pairs: match → diagonal, mismatch → best neighbour",
    why="The template for every \"two strings / two sequences\" DP", signature="LC 1143 / 1035",
    when="Two sequences are compared and you ask about their common structure: LCS, deletions to make them equal, interleavings, subsequence counts.",
    detect="\"longest common subsequence\" · \"delete operation for two strings\" · \"uncrossed lines\" · \"shortest common supersequence\" · \"distinct subsequences\" · \"interleaving string\".",
    intuition="Compare the **last** letters of the two prefixes. If they are equal, they can both be the last letter of a common subsequence, so the answer is 1 plus the answer for both prefixes shortened by one. If they differ, at least one of them is unused: drop either the last letter of the first or the last letter of the second and take the better result. Every cell depends only on three neighbours, so the table fills row by row.",
    brute="Trying every subsequence of one string against the other is exponential. The table has `(m + 1) × (n + 1)` cells with O(1) work each.",
    idea="`dp[i][j]` = LCS of `a[0..i)` and `b[0..j)`. If `a[i−1] == b[j−1]`: `dp[i−1][j−1] + 1`; else `max(dp[i−1][j], dp[i][j−1])`. Zero first row and column. Rebuild the string by walking back from the corner.",
    steps=["Allocate `(m + 1) × (n + 1)` zeros.", "For each cell compare the two characters.", "Equal → diagonal + 1; else max(up, left).", "Answer is the bottom-right cell; walk back to recover the sequence."],
    trace_title="`\"abcde\"` and `\"ace\"`",
    trace="""      ''  a  c  e
 ''    0  0  0  0
 a     0  1  1  1
 b     0  1  1  1
 c     0  1  2  2
 d     0  1  2  2
 e     0  1  2  3      LCS = "ace" (3)""",
    code=[("LCS length and the sequence itself",
           """int lcs(String a, String b) {
    int m = a.length(), n = b.length();
    int[][] dp = new int[m + 1][n + 1];
    for (int i = 1; i <= m; i++)
        for (int j = 1; j <= n; j++)
            dp[i][j] = a.charAt(i - 1) == b.charAt(j - 1)
                     ? dp[i - 1][j - 1] + 1
                     : Math.max(dp[i - 1][j], dp[i][j - 1]);
    return dp[m][n];
}
String lcsString(String a, String b) {
    int m = a.length(), n = b.length();
    int[][] dp = new int[m + 1][n + 1];
    for (int i = 1; i <= m; i++)
        for (int j = 1; j <= n; j++)
            dp[i][j] = a.charAt(i - 1) == b.charAt(j - 1) ? dp[i - 1][j - 1] + 1 : Math.max(dp[i - 1][j], dp[i][j - 1]);
    StringBuilder sb = new StringBuilder();
    for (int i = m, j = n; i > 0 && j > 0; ) {                      // walk back from the corner
        if (a.charAt(i - 1) == b.charAt(j - 1)) { sb.append(a.charAt(i - 1)); i--; j--; }
        else if (dp[i - 1][j] >= dp[i][j - 1]) i--;
        else j--;
    }
    return sb.reverse().toString();
}""",
           """def lcs(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]

def lcs_string(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = dp[i - 1][j - 1] + 1 if a[i - 1] == b[j - 1] else max(dp[i - 1][j], dp[i][j - 1])
    out, i, j = [], m, n
    while i > 0 and j > 0:                                            # walk back from the corner
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1]); i -= 1; j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return ''.join(reversed(out))"""),
          ("distinct subsequences (how many times does t occur in s as a subsequence?)",
           """int numDistinct(String s, String t) {
    long[] dp = new long[t.length() + 1];                          // dp[j] = ways to form t[0..j) from the part of s seen so far
    dp[0] = 1;
    for (int i = 0; i < s.length(); i++)
        for (int j = t.length(); j >= 1; j--)                      // downwards: each letter of s used once
            if (s.charAt(i) == t.charAt(j - 1)) dp[j] += dp[j - 1];
    return (int) dp[t.length()];
}""",
           """def num_distinct(s, t):
    dp = [1] + [0] * len(t)                                        # dp[j] = ways to form t[:j] from the part of s seen so far
    for ch in s:
        for j in range(len(t), 0, -1):                             # downwards: each letter of s used once
            if ch == t[j - 1]:
                dp[j] += dp[j - 1]
    return dp[len(t)]""")],
    complexity="O(m · n) time; O(m · n) space (O(min(m, n)) for the length alone with two rows).",
    traps=["Index the table with prefix lengths (`dp[i][j]`, characters `a[i − 1]`, `b[j − 1]`) to avoid off-by-one errors.", "Rebuild the sequence from the **full** table; a rolling array cannot reconstruct it.",
           "Subsequence is not substring: letters need not be adjacent (use the sliding-window / suffix methods for substrings).", "Counting versions can overflow `int`; use `long` or a modulus."],
    variants=["Delete operation for two strings: `m + n − 2 · LCS`.", "Shortest common supersequence: `m + n − LCS`, built by merging along the LCS table.", "Longest common substring: reset to 0 on mismatch and take the maximum cell.", "Interleaving string: `dp[i][j]` = can `s3[0..i+j)` be formed from `s1[0..i)` and `s2[0..j)`."],
    notuse="More than two sequences (the table grows exponentially) or substrings (different recurrence).",
    problems=[
        (1143, "Longest Common Subsequence", "M", "longest-common-subsequence", "Match → diagonal + 1, else max(up, left)", "O(m·n) / O(m·n)"),
        (583, "Delete Operation for Two Strings", "M", "delete-operation-for-two-strings", "m + n − 2 · LCS", "O(m·n) / O(n)"),
        (1035, "Uncrossed Lines", "M", "uncrossed-lines", "Exactly the LCS of the two arrays", "O(m·n) / O(n)"),
        (718, "Maximum Length of Repeated Subarray", "M", "maximum-length-of-repeated-subarray", "Longest common substring: reset to 0 on mismatch", "O(m·n) / O(n)"),
        (97, "Interleaving String", "M", "interleaving-string", "dp[i][j]: first i of s1 and first j of s2 interleave to s3[0..i+j)", "O(m·n) / O(n)"),
        (115, "Distinct Subsequences", "H", "distinct-subsequences", "dp[j] += dp[j−1] on a letter match, loop j downwards", "O(m·n) / O(n)"),
        (1092, "Shortest Common Supersequence", "H", "shortest-common-supersequence", "Build the LCS table, then merge the strings along it", "O(m·n) / O(m·n)"),
    ]))

# ---------------------------------------------------------------- 4
P.append(dict(
    title="Edit distance and string matching DP", tier="hot", sim="edit", oneline="three moves, three neighbours: replace, delete, insert",
    why="The best-known 2D string DP, with several interview variants", signature="LC 72 / 44 / 10",
    when="You transform one string into another with allowed operations, or match a string against a pattern with wildcards.",
    detect="\"edit distance\" · \"wildcard matching\" · \"regular expression matching\" · \"minimum operations to convert\" · \"scramble string\".",
    intuition="Look at the last letters again. If they match, nothing is needed: carry over the cost of the shorter prefixes. If they differ, you have three ways to fix the end of the first string, and each corresponds to a neighbouring cell: **replace** (diagonal), **delete** from the first string (cell above), **insert** into the first string (cell to the left). Take the cheapest and add 1. For wildcards, `*` may match nothing (look left) or consume one more letter of `s` (look up).",
    brute="Trying all sequences of edits is exponential. The `(m + 1) × (n + 1)` table does constant work per cell.",
    idea="Edit distance: `dp[i][0] = i`, `dp[0][j] = j`; `dp[i][j] = dp[i−1][j−1]` if letters match, else `1 + min(dp[i−1][j−1], dp[i−1][j], dp[i][j−1])`. Wildcard matching: `dp[i][j]` = does `s[0..i)` match `p[0..j)`; `*` → `dp[i][j−1] || dp[i−1][j]`; `?` or equal letter → `dp[i−1][j−1]`.",
    steps=["Initialise the first row and column with the cost of building / deleting everything.", "For each cell compare `a[i − 1]` and `b[j − 1]`.", "Equal → copy the diagonal; different → 1 + min of three neighbours.", "Answer: bottom-right cell."],
    trace_title="`horse` → `ros`",
    trace="""      ''  r  o  s
 ''    0  1  2  3
 h     1  1  2  3
 o     2  2  1  2
 r     3  2  2  2
 s     4  3  3  2
 e     5  4  4  3      edit distance 3""",
    code=[("edit distance",
           """int minDistance(String a, String b) {
    int m = a.length(), n = b.length();
    int[][] dp = new int[m + 1][n + 1];
    for (int i = 0; i <= m; i++) dp[i][0] = i;                  // delete everything
    for (int j = 0; j <= n; j++) dp[0][j] = j;                  // insert everything
    for (int i = 1; i <= m; i++)
        for (int j = 1; j <= n; j++)
            dp[i][j] = a.charAt(i - 1) == b.charAt(j - 1)
                     ? dp[i - 1][j - 1]
                     : 1 + Math.min(dp[i - 1][j - 1], Math.min(dp[i - 1][j], dp[i][j - 1]));
    return dp[m][n];
}""",
           """def min_distance(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i                                            # delete everything
    for j in range(n + 1):
        dp[0][j] = j                                            # insert everything
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j - 1], dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]"""),
          ("wildcard matching ('?' = any one letter, '*' = any sequence)",
           """boolean isMatch(String s, String p) {
    int m = s.length(), n = p.length();
    boolean[][] dp = new boolean[m + 1][n + 1];
    dp[0][0] = true;
    for (int j = 1; j <= n; j++) dp[0][j] = p.charAt(j - 1) == '*' && dp[0][j - 1];   // leading stars match the empty string
    for (int i = 1; i <= m; i++)
        for (int j = 1; j <= n; j++) {
            char c = p.charAt(j - 1);
            if (c == '*') dp[i][j] = dp[i][j - 1] || dp[i - 1][j];            // star matches nothing, or one more letter
            else if (c == '?' || c == s.charAt(i - 1)) dp[i][j] = dp[i - 1][j - 1];
        }
    return dp[m][n];
}""",
           """def is_match(s, p):
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for j in range(1, n + 1):
        dp[0][j] = p[j - 1] == '*' and dp[0][j - 1]                      # leading stars match the empty string
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            c = p[j - 1]
            if c == '*':
                dp[i][j] = dp[i][j - 1] or dp[i - 1][j]                  # star matches nothing, or one more letter
            elif c == '?' or c == s[i - 1]:
                dp[i][j] = dp[i - 1][j - 1]
    return dp[m][n]""")],
    complexity="O(m · n) time and space (a rolling row gives O(n) space for the value).",
    traps=["Initialise the first row **and** column: they are the cost of building or deleting the whole string.", "Wildcard first row: a pattern of only `*` matches the empty string.",
           "Regular expression matching (`.` and `*` meaning \"zero or more of the previous\") has a different `*` rule: `dp[i][j−2]` or (`dp[i−1][j]` if the previous pattern letter matches).", "Be clear which string is being edited (insert / delete are not symmetric in the table but give the same cost)."],
    variants=["Regular expression matching: star applies to the previous element.", "Scramble string: 3D DP over (i, j, length).", "Minimum ASCII delete sum: LCS-like table with character weights."],
    notuse="Only the common subsequence matters (LCS) or the strings are huge (use banded / bit-parallel algorithms).",
    problems=[
        (72, "Edit Distance", "M", "edit-distance", "1 + min(replace, delete, insert) on a mismatch", "O(m·n) / O(n)"),
        (44, "Wildcard Matching", "H", "wildcard-matching", "'*' → left or up; '?' → diagonal", "O(m·n) / O(n)"),
        (10, "Regular Expression Matching", "H", "regular-expression-matching", "Star applies to the previous pattern letter", "O(m·n) / O(m·n)"),
        (87, "Scramble String", "H", "scramble-string", "3D dp over two start indices and a length", "O(n⁴) / O(n³)"),
    ]))

# ---------------------------------------------------------------- 5
P.append(dict(
    title="Palindromic subsequences and substrings", tier="hot", sim="lps", oneline="dp[i][j] over an interval; match the ends, or drop one",
    why="The first DP on intervals of a single string", signature="LC 516 / 647 / 132",
    when="You ask about palindromes inside a string: longest palindromic subsequence, count of palindromic substrings, minimum cuts or insertions.",
    detect="\"longest palindromic subsequence\" · \"palindromic substrings\" · \"minimum insertion steps to make a palindrome\" · \"palindrome partitioning II\" · \"count different palindromic subsequences\".",
    intuition="A palindrome is defined from the outside in: if the first and last letters of `s[i..j]` match, the answer wraps around the answer for the inside `s[i+1..j−1]`; if they do not, one of the ends is useless, so the answer is the better of dropping either one. The state is an **interval**, and an interval depends on shorter intervals, so fill the table by **increasing length** (or `i` downwards, `j` upwards).",
    brute="Trying all subsequences is exponential. The `n × n` table does O(1) per interval: O(n²).",
    idea="LPS: `dp[i][i] = 1`; `dp[i][j] = dp[i+1][j−1] + 2` if `s[i] == s[j]`, else `max(dp[i+1][j], dp[i][j−1])`. Palindromic substring test: `pal[i][j] = s[i] == s[j] && (j − i < 2 || pal[i+1][j−1])`. Minimum cuts: `cuts[j] = min(cuts[i−1] + 1)` over `i` with `pal[i][j]`.",
    steps=["Base case: every single letter is a palindrome (diagonal = 1).", "Iterate `i` from `n − 1` down to 0 and `j` from `i + 1` up to `n − 1`.", "Ends equal → wrap the inside (+2); otherwise max of the two shorter intervals.", "Answer `dp[0][n − 1]`; insertions needed = `n − LPS`."],
    trace_title="`\"bbbab\"`",
    trace="""dp[0][4] looks at s[0]='b' and s[4]='b': equal -> dp[1][3] + 2
dp[1][3] = \"bba\": ends 'b','a' differ -> max(dp[2][3], dp[1][2]) = 2
dp[0][4] = 2 + 2 = 4   (\"bbbb\")""",
    code=[("longest palindromic subsequence and palindromic substrings",
           """int longestPalindromeSubseq(String s) {
    int n = s.length();
    int[][] dp = new int[n][n];
    for (int i = n - 1; i >= 0; i--) {
        dp[i][i] = 1;
        for (int j = i + 1; j < n; j++)
            dp[i][j] = s.charAt(i) == s.charAt(j)
                     ? dp[i + 1][j - 1] + 2                           // dp[i+1][j-1] is 0 when j = i + 1
                     : Math.max(dp[i + 1][j], dp[i][j - 1]);
    }
    return dp[0][n - 1];
}
int countSubstrings(String s) {
    int n = s.length(), count = 0;
    boolean[][] pal = new boolean[n][n];
    for (int i = n - 1; i >= 0; i--)
        for (int j = i; j < n; j++) {
            pal[i][j] = s.charAt(i) == s.charAt(j) && (j - i < 2 || pal[i + 1][j - 1]);
            if (pal[i][j]) count++;
        }
    return count;
}""",
           """def longest_palindrome_subseq(s):
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        dp[i][i] = 1
        for j in range(i + 1, n):
            if s[i] == s[j]:
                dp[i][j] = (dp[i + 1][j - 1] if j - 1 >= i + 1 else 0) + 2     # inside is empty when j = i + 1
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
    return dp[0][n - 1]

def count_substrings(s):
    n, count = len(s), 0
    pal = [[False] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            pal[i][j] = s[i] == s[j] and (j - i < 2 or pal[i + 1][j - 1])
            count += pal[i][j]
    return count"""),
          ("palindrome partitioning II (minimum cuts)",
           """int minCut(String s) {
    int n = s.length();
    boolean[][] pal = new boolean[n][n];
    int[] cuts = new int[n];                                        // cuts[j] = fewest cuts for s[0..j]
    for (int j = 0; j < n; j++) {
        cuts[j] = j;                                                // worst case: cut before every letter
        for (int i = 0; i <= j; i++) {
            if (s.charAt(i) == s.charAt(j) && (j - i < 2 || pal[i + 1][j - 1])) {
                pal[i][j] = true;
                cuts[j] = (i == 0) ? 0 : Math.min(cuts[j], cuts[i - 1] + 1);
            }
        }
    }
    return cuts[n - 1];
}""",
           """def min_cut(s):
    n = len(s)
    pal = [[False] * n for _ in range(n)]
    cuts = [0] * n                                                  # cuts[j] = fewest cuts for s[:j + 1]
    for j in range(n):
        cuts[j] = j                                                 # worst case: cut before every letter
        for i in range(j + 1):
            if s[i] == s[j] and (j - i < 2 or pal[i + 1][j - 1]):
                pal[i][j] = True
                cuts[j] = 0 if i == 0 else min(cuts[j], cuts[i - 1] + 1)
    return cuts[n - 1]""")],
    complexity="O(n²) time and space.",
    traps=["Subsequence (letters may be skipped) vs substring (contiguous): the recurrences differ.", "For length-2 intervals the inside is empty: handle `j == i + 1` explicitly (`dp[i+1][j−1]` is out of order).",
           "Iterate so that `dp[i+1][·]` is computed before `dp[i][·]` (outer `i` descending).", "Minimum insertions to make a palindrome = `n − LPS(s)`."],
    variants=["Longest palindromic substring: expand around the centre in O(n²) with O(1) space (strings topic).", "Count different palindromic subsequences: inclusion–exclusion on the same state.", "Manacher's algorithm: all palindromic substrings in O(n)."],
    notuse="You only need the longest palindromic **substring** (centre expansion is simpler).",
    problems=[
        (647, "Palindromic Substrings", "M", "palindromic-substrings", "pal[i][j] from the inside; count the trues", "O(n²) / O(n²)"),
        (516, "Longest Palindromic Subsequence", "M", "longest-palindromic-subsequence", "Match ends → inside + 2, else best of dropping one end", "O(n²) / O(n²)"),
        (1312, "Minimum Insertion Steps to Make a String Palindrome", "H", "minimum-insertion-steps-to-make-a-string-palindrome", "n − longest palindromic subsequence", "O(n²) / O(n²)"),
        (132, "Palindrome Partitioning II", "H", "palindrome-partitioning-ii", "pal table + cuts[j] = min(cuts[i − 1] + 1)", "O(n²) / O(n²)"),
        (730, "Count Different Palindromic Subsequences", "H", "count-different-palindromic-subsequences", "Interval dp with inclusion–exclusion on the end letters", "O(n²) / O(n²)"),
    ]))

# ---------------------------------------------------------------- 6
P.append(dict(
    title="Interval DP: choose the last or the split point", tier="hot", sim="balloons", oneline="solve every sub-interval; the best split combines two smaller ones",
    why="The \"hard\" DP family: burst balloons, matrix chain, cutting sticks, stone games", signature="LC 312 / 1547 / 877",
    when="The cost of handling a segment depends on how you split it, and the two sides can be solved independently once the split is fixed.",
    detect="\"burst balloons\" · \"minimum cost to cut a stick\" · \"minimum score triangulation\" · \"strange printer\" · \"stone game / predict the winner\" · \"matrix chain multiplication\".",
    intuition="Forward thinking fails: when you burst a balloon its neighbours change, so the left and right parts stop being independent. **Reverse it:** pick the balloon `k` that is burst **last** inside `(l, r)`. At that moment its neighbours are exactly `l` and `r`, and everything on its left and on its right was burst earlier within independent intervals `(l, k)` and `(k, r)`. So `dp[l][r]` = best over `k` of `dp[l][k] + dp[k][r] + a[l]·a[k]·a[r]`.",
    brute="Trying every burst order is n!. Interval DP has O(n²) intervals, each with O(n) choices of `k`: O(n³).",
    idea="Define `dp[l][r]` for an interval, choose a split / last element `k` strictly inside, combine `dp[l][k]` and `dp[k][r]` with the cost of the final action, and fill by **increasing interval length** so sub-intervals are ready.",
    steps=["Pad the array if the problem needs sentinel neighbours.", "Loop `gap` (interval length) upward, then the left end `l`; set `r = l + gap`.", "For each `k` in `(l, r)`: candidate = `dp[l][k] + dp[k][r] + cost(l, k, r)`.", "Keep the best; answer `dp[0][n − 1]`."],
    trace_title="burst balloons `[3, 1, 5, 8]` (padded 1 3 1 5 8 1)",
    trace="""dp[0][5] = max over last balloon k:
 k=3 (the 5): dp[0][3] + dp[3][5] + 1*5*1 ...
 k=4 (the 8): dp[0][4] + dp[4][5] + 1*8*1 = 159 + 0 + 8 = 167   <- best
answer 167""",
    code=[("burst balloons and minimum cost to cut a stick",
           """int maxCoins(int[] nums) {
    int n = nums.length + 2;
    int[] a = new int[n];
    a[0] = a[n - 1] = 1;
    for (int i = 0; i < nums.length; i++) a[i + 1] = nums[i];
    int[][] dp = new int[n][n];                                   // dp[l][r]: balloons strictly between l and r
    for (int gap = 2; gap < n; gap++)
        for (int l = 0; l + gap < n; l++) {
            int r = l + gap;
            for (int k = l + 1; k < r; k++)                        // k = the LAST balloon to burst in (l, r)
                dp[l][r] = Math.max(dp[l][r], dp[l][k] + dp[k][r] + a[l] * a[k] * a[r]);
        }
    return dp[0][n - 1];
}
int minCost(int n, int[] cuts) {
    int[] c = new int[cuts.length + 2];
    System.arraycopy(cuts, 0, c, 1, cuts.length);
    c[c.length - 1] = n;                                           // positions 0 .. n with every cut in between
    Arrays.sort(c);
    int m = c.length;
    int[][] dp = new int[m][m];
    for (int gap = 2; gap < m; gap++)
        for (int i = 0; i + gap < m; i++) {
            int j = i + gap;
            dp[i][j] = Integer.MAX_VALUE;
            for (int k = i + 1; k < j; k++)                        // k = the FIRST cut made in this stick piece
                dp[i][j] = Math.min(dp[i][j], dp[i][k] + dp[k][j] + c[j] - c[i]);
        }
    return dp[0][m - 1];
}""",
           """def max_coins(nums):
    a = [1] + nums + [1]
    n = len(a)
    dp = [[0] * n for _ in range(n)]                              # dp[l][r]: balloons strictly between l and r
    for gap in range(2, n):
        for l in range(n - gap):
            r = l + gap
            for k in range(l + 1, r):                              # k = the LAST balloon to burst in (l, r)
                dp[l][r] = max(dp[l][r], dp[l][k] + dp[k][r] + a[l] * a[k] * a[r])
    return dp[0][n - 1]

def min_cost(n, cuts):
    c = [0] + sorted(cuts) + [n]                                   # positions 0 .. n with every cut in between
    m = len(c)
    dp = [[0] * m for _ in range(m)]
    for gap in range(2, m):
        for i in range(m - gap):
            j = i + gap
            dp[i][j] = min(dp[i][k] + dp[k][j] for k in range(i + 1, j)) + c[j] - c[i]   # k = the FIRST cut made in this piece
    return dp[0][m - 1]"""),
          ("predict the winner / stone game (interval DP on score difference)",
           """boolean predictTheWinner(int[] a) {
    int n = a.length;
    int[][] dp = new int[n][n];                                    // dp[i][j] = best (my score - opponent score) on a[i..j]
    for (int i = 0; i < n; i++) dp[i][i] = a[i];
    for (int len = 2; len <= n; len++)
        for (int i = 0; i + len - 1 < n; i++) {
            int j = i + len - 1;
            dp[i][j] = Math.max(a[i] - dp[i + 1][j], a[j] - dp[i][j - 1]);   // take an end; the opponent then plays optimally
        }
    return dp[0][n - 1] >= 0;
}""",
           """def predict_the_winner(a):
    n = len(a)
    dp = [[0] * n for _ in range(n)]                               # dp[i][j] = best (my score - opponent score) on a[i..j]
    for i in range(n):
        dp[i][i] = a[i]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = max(a[i] - dp[i + 1][j], a[j] - dp[i][j - 1])   # take an end; the opponent then plays optimally
    return dp[0][n - 1] >= 0""")],
    complexity="O(n³) time, O(n²) space for burst-balloons-style problems; O(n²) for the game DP.",
    traps=["Think **last** (burst balloons) or **first** (cut the stick) action in the interval; that choice makes the two sides independent.", "Fill by interval **length** so shorter intervals are ready.",
           "Pad with sentinels (`1`, or positions `0` and `n`) so the boundary intervals work.", "Game DPs store score **differences**, not the two players' scores separately."],
    variants=["Matrix chain multiplication: `dp[i][j] = min dp[i][k] + dp[k+1][j] + p[i-1]·p[k]·p[j]`.", "Strange printer: interval dp with merging equal end letters.", "Guess number higher or lower II: minimax interval dp (`k + max(dp[l][k−1], dp[k+1][r])`)."],
    notuse="n larger than a few hundred (O(n³) is too slow) or when a greedy / divide-and-conquer structure exists.",
    problems=[
        (877, "Stone Game", "M", "stone-game", "Score-difference interval dp (or the parity argument)", "O(n²) / O(n²)"),
        (486, "Predict the Winner", "M", "predict-the-winner", "dp[i][j] = max(a[i] − dp[i+1][j], a[j] − dp[i][j−1])", "O(n²) / O(n²)"),
        (375, "Guess Number Higher or Lower II", "M", "guess-number-higher-or-lower-ii", "Minimax over the guess k in each interval", "O(n³) / O(n²)"),
        (1039, "Minimum Score Triangulation of Polygon", "M", "minimum-score-triangulation-of-polygon", "Choose the apex k of the triangle on edge (i, j)", "O(n³) / O(n²)"),
        (1547, "Minimum Cost to Cut a Stick", "H", "minimum-cost-to-cut-a-stick", "First cut k splits the piece; cost = piece length", "O(m³) / O(m²)"),
        (312, "Burst Balloons", "H", "burst-balloons", "k = last balloon burst in (l, r)", "O(n³) / O(n²)"),
        (664, "Strange Printer", "H", "strange-printer", "Interval dp merging equal letters at the ends", "O(n³) / O(n²)"),
    ]))

# ---------------------------------------------------------------- 7
P.append(dict(
    title="Bitmask DP: states over subsets", tier="hot", sim="maskdp", oneline="the state is the set of items already used, stored as an integer",
    why="Exponential problems made tractable for n ≤ about 20", signature="LC 1879 / 943 / 847",
    when="You must assign, order or partition up to ~20 items and what you did earlier matters only through **which items are used** (and maybe the last one).",
    detect="\"assign tasks to workers\" · \"travelling salesman\" · \"minimum XOR sum of two arrays\" · \"fair distribution of cookies\" · \"shortest superstring\" · \"can I win (choose numbers)\".",
    intuition="Brute force tries `n!` orders. But two different orders that use the **same set** of items so far and end in the same state are equivalent for everything that comes next. So collapse them: let the DP state be the set of used items as a bitmask (bit `j` = item `j` used), and move from a mask to a bigger mask by adding one unused item. There are only `2ⁿ` masks, each with `n` transitions.",
    brute="`n!` permutations (n = 15 is 10¹²). Bitmask DP: `2ⁿ · n` (n = 15 is 500 000).",
    idea="`dp[mask]` = best cost for the items in `mask`. For the assignment problem the next worker is `popcount(mask)`; transition `dp[mask | 1<<j] = min(dp[mask] + cost[w][j])` for each free `j`. TSP adds the last city: `dp[mask][last]`.",
    steps=["Index the items `0..n−1`; masks run from `0` to `2ⁿ − 1`.", "Initialise `dp[0]` (empty set) and everything else as ∞.", "For each mask, for each unused item `j`, relax `dp[mask | (1 << j)]`.", "Answer `dp[(1 << n) − 1]` (or the best over the last item)."],
    trace_title="costs `[[9,2,7],[6,4,3],[5,8,1]]`",
    trace="""dp[000] = 0
worker 0 picks a task:        dp[001]=9  dp[010]=2  dp[100]=7
worker 1 from mask 010:       dp[011]=6  dp[110]=5
worker 2 from mask 011 / 110: dp[111] = min(...) = 9
workers 0->1, 1->0, 2->2 cost 2 + 6 + 1 = 9""",
    code=[("assignment problem with a bitmask",
           """int minAssignmentCost(int[][] cost) {
    int n = cost.length;
    int[] dp = new int[1 << n];
    Arrays.fill(dp, Integer.MAX_VALUE / 2);
    dp[0] = 0;
    for (int mask = 0; mask < (1 << n); mask++) {
        int worker = Integer.bitCount(mask);                       // workers 0..worker-1 are already assigned
        if (worker >= n) continue;
        for (int j = 0; j < n; j++)
            if ((mask >> j & 1) == 0)                              // task j is free
                dp[mask | 1 << j] = Math.min(dp[mask | 1 << j], dp[mask] + cost[worker][j]);
    }
    return dp[(1 << n) - 1];
}""",
           """def min_assignment_cost(cost):
    n = len(cost)
    INF = float('inf')
    dp = [INF] * (1 << n)
    dp[0] = 0
    for mask in range(1 << n):
        worker = bin(mask).count('1')                               # workers 0..worker-1 are already assigned
        if worker >= n:
            continue
        for j in range(n):
            if not mask >> j & 1:                                   # task j is free
                dp[mask | 1 << j] = min(dp[mask | 1 << j], dp[mask] + cost[worker][j])
    return dp[(1 << n) - 1]"""),
          ("travelling salesman: dp[mask][last city]",
           """int tsp(int[][] d) {                                            // shortest tour starting and ending at city 0
    int n = d.length, INF = Integer.MAX_VALUE / 2;
    int[][] dp = new int[1 << n][n];
    for (int[] row : dp) Arrays.fill(row, INF);
    dp[1][0] = 0;                                                 // only city 0 visited, standing at city 0
    for (int mask = 1; mask < (1 << n); mask++)
        for (int last = 0; last < n; last++) {
            if ((mask >> last & 1) == 0 || dp[mask][last] >= INF) continue;
            for (int next = 0; next < n; next++)
                if ((mask >> next & 1) == 0)
                    dp[mask | 1 << next][next] = Math.min(dp[mask | 1 << next][next], dp[mask][last] + d[last][next]);
        }
    int best = INF;
    for (int last = 1; last < n; last++) best = Math.min(best, dp[(1 << n) - 1][last] + d[last][0]);
    return best;
}""",
           """def tsp(d):                                                         # shortest tour starting and ending at city 0
    n = len(d)
    INF = float('inf')
    dp = [[INF] * n for _ in range(1 << n)]
    dp[1][0] = 0                                                    # only city 0 visited, standing at city 0
    for mask in range(1, 1 << n):
        for last in range(n):
            if not mask >> last & 1 or dp[mask][last] == INF:
                continue
            for nxt in range(n):
                if not mask >> nxt & 1:
                    dp[mask | 1 << nxt][nxt] = min(dp[mask | 1 << nxt][nxt], dp[mask][last] + d[last][nxt])
    return min(dp[(1 << n) - 1][last] + d[last][0] for last in range(1, n))""")],
    complexity="O(2ⁿ · n) time and O(2ⁿ) space for assignment-style problems; O(2ⁿ · n²) time, O(2ⁿ · n) space for TSP.",
    traps=["n must be small (about ≤ 20); otherwise 2ⁿ states do not fit.", "Operator precedence: write `(mask >> j & 1) == 0` and `mask | (1 << j)` with explicit parentheses.",
           "Use `1L << j` when n can exceed 31, and an INF that cannot overflow when you add to it.", "Many problems let you derive the next index from `popcount(mask)`; if not, the state needs the last item too."],
    variants=["Partition into k equal-sum subsets: `dp[mask]` = remainder of the current bucket.", "Can I win: `dp[mask]` = can the current player force a win with these numbers already chosen.", "Shortest path visiting all nodes: BFS over `(node, mask)` states (graphs topic)."],
    notuse="n above ~20, or when a polynomial DP / greedy exists.",
    problems=[
        (2305, "Fair Distribution of Cookies", "M", "fair-distribution-of-cookies", "Assign cookie bags to children; dp over masks (or backtracking with pruning)", "O(3ⁿ) / O(2ⁿ)"),
        (1947, "Maximum Compatibility Score Sum", "M", "maximum-compatibility-score-sum", "Assignment over masks of mentors", "O(2ⁿ·n) / O(2ⁿ)"),
        (464, "Can I Win", "M", "can-i-win", "Memoise on the mask of used numbers", "O(2ⁿ·n) / O(2ⁿ)"),
        (1986, "Minimum Number of Work Sessions to Finish the Tasks", "M", "minimum-number-of-work-sessions-to-finish-the-tasks", "dp[mask] = (sessions, time in the last session)", "O(2ⁿ·n) / O(2ⁿ)"),
        (1879, "Minimum XOR Sum of Two Arrays", "H", "minimum-xor-sum-of-two-arrays", "Assignment-style dp with cost = a[i] XOR b[j]", "O(2ⁿ·n) / O(2ⁿ)"),
        (943, "Find the Shortest Superstring", "H", "find-the-shortest-superstring", "TSP over words with overlap costs", "O(2ⁿ·n²) / O(2ⁿ·n)"),
    ]))

# ---------------------------------------------------------------- 8
P.append(dict(
    title="Digit DP: counting numbers up to N", tier="sec", sim="digit", oneline="shorter numbers are free; equal-length ones walk N while staying tight",
    why="Counts numbers with a digit property in a huge range without enumerating them", signature="LC 902 / 233 / 600",
    when="You count integers in `[0, N]` (N up to 10⁹ or more) that satisfy a rule about their digits.",
    detect="\"numbers at most N given digit set\" · \"count numbers with unique digits\" · \"number of digit one\" · \"non-negative integers without consecutive ones\" · \"count special integers\".",
    intuition="Compare a candidate number to `N` from the left. Any candidate with **fewer digits** than `N` is automatically smaller, so only the digit rule matters. For candidates with the **same length**, walk the digits of `N`: at each position you may choose a digit **smaller** than `N`'s digit (the number is now free; every later position is unconstrained) or **equal** to it (stay \"tight\" and continue). The count of free completions is a simple power or table lookup.",
    brute="Testing every integer up to N is O(N): impossible for N = 10⁹. Digit DP visits only `len(N)` positions with a handful of states.",
    idea="State: `(position, tight, extra)` where `extra` is whatever the rule needs (last digit, mask of used digits, count so far). Pre-count shorter lengths separately. For each position, add the choices below `N[i]` multiplied by the number of free completions, then continue only if `N[i]` itself is allowed.",
    steps=["Write `N` as a string of digits.", "Add the count of all valid numbers shorter than `N`.", "For each position `i`: count allowed digits smaller than `N[i]` × completions of the remaining positions.", "If `N[i]` is not allowed, stop; if all digits were allowed add 1 for `N` itself."],
    trace_title="digits {1, 3, 5}, N = 234",
    trace="""1 digit : 3
2 digits: 3^2 = 9
3 digits: position 0 (digit 2): allowed digits < 2 -> {1}: 1 * 3^2 = 9
          digit 2 not allowed -> stop
total 3 + 9 + 9 = 21""",
    code=[("numbers at most N given a digit set",
           """int atMostNGivenDigitSet(String[] digits, int n) {
    String s = String.valueOf(n);
    int L = s.length(), D = digits.length;
    int res = 0;
    long p = 1;
    for (int len = 1; len < L; len++) { p *= D; res += p; }            // every shorter length: D^len numbers
    for (int i = 0; i < L; i++) {
        boolean tight = false;                                        // can we keep matching N's digit?
        for (String d : digits) {
            if (d.charAt(0) < s.charAt(i)) res += (int) Math.pow(D, L - i - 1);   // smaller digit: rest is free
            else if (d.charAt(0) == s.charAt(i)) tight = true;
        }
        if (!tight) return res;
    }
    return res + 1;                                                   // N itself is buildable
}""",
           """def at_most_n_given_digit_set(digits, n):
    s = str(n)
    L, D = len(s), len(digits)
    res = sum(D ** length for length in range(1, L))                  # every shorter length: D^len numbers
    for i, ch in enumerate(s):
        tight = False                                                 # can we keep matching N's digit?
        for d in digits:
            if d < ch:
                res += D ** (L - i - 1)                               # smaller digit: rest is free
            elif d == ch:
                tight = True
        if not tight:
            return res
    return res + 1                                                    # N itself is buildable"""),
          ("count numbers with unique digits (permutation counting)",
           """int countNumbersWithUniqueDigits(int n) {                          // numbers in [0, 10^n)
    if (n == 0) return 1;
    int res = 10, unique = 9, available = 9;                          // all 1-digit numbers: 10
    for (int len = 2; len <= Math.min(n, 10); len++) {
        unique *= available;                                          // 9 * 9 * 8 * 7 ...: first digit non-zero, then fewer choices
        res += unique;
        available--;
    }
    return res;
}""",
           """def count_numbers_with_unique_digits(n):                           # numbers in [0, 10^n)
    if n == 0:
        return 1
    res, unique, available = 10, 9, 9                                  # all 1-digit numbers: 10
    for length in range(2, min(n, 10) + 1):
        unique *= available                                            # 9 * 9 * 8 * 7 ...: first digit non-zero, then fewer choices
        res += unique
        available -= 1
    return res""")],
    complexity="O(digits · |digit set|) for the walk; general digit DP is O(digits · states · 10).",
    traps=["Count shorter lengths separately; do not forget them.", "The \"tight\" flag must be dropped as soon as you pick a smaller digit.",
           "Leading zeros matter for rules like \"unique digits\" or \"no repeated digit\": track whether the number has started.", "Add 1 for `N` itself only when every digit of `N` was allowed."],
    variants=["Number of digit one: count how often 1 appears at each position by formula.", "Non-negative integers without consecutive ones: Fibonacci-style counts with a tight walk.", "Count special integers / numbers with repeated digits: bitmask of used digits as part of the state."],
    notuse="Small ranges (just enumerate) or rules unrelated to the digits.",
    problems=[
        (357, "Count Numbers with Unique Digits", "M", "count-numbers-with-unique-digits", "Permutation counting per length", "O(n) / O(1)"),
        (788, "Rotated Digits", "M", "rotated-digits", "Per-digit classification (brute force or digit dp)", "O(N log N) / O(1)"),
        (902, "Numbers At Most N Given Digit Set", "H", "numbers-at-most-n-given-digit-set", "Shorter lengths + tight walk over N", "O(L·D) / O(1)"),
        (233, "Number of Digit One", "H", "number-of-digit-one", "Count ones per position with high / current / low parts", "O(log N) / O(1)"),
        (600, "Non-negative Integers without Consecutive Ones", "H", "non-negative-integers-without-consecutive-ones", "Fibonacci counts while walking the bits of N", "O(log N) / O(log N)"),
        (2376, "Count Special Integers", "H", "count-special-integers", "Digit dp with a mask of used digits", "O(L·2¹⁰·10) / O(L·2¹⁰)"),
    ]))

# ---------------------------------------------------------------- 9
P.append(dict(
    title="Speeding up DP: monotonic deque and friends", tier="sec", sim="jump6", oneline="when dp[i] needs a window maximum, keep the window in a deque",
    why="Turns O(n·k) transitions into O(n)", signature="LC 1696 / 1425",
    when="Each state takes a max / min over a **window** of earlier states (`dp[i] = a[i] + max(dp[i−k..i−1])`).",
    detect="\"jump game VI\" · \"constrained subsequence sum\" · \"max value of equation\" · \"jump game V\" · any DP whose transition is a range maximum or minimum.",
    intuition="Computing the max of the last `k` states from scratch costs `k` per cell. But as you move right, the window changes by one element in and one out. A **monotonic deque** keeps the window's candidates in decreasing order: a new value removes every smaller value from the back (they can never be the maximum again) and the front is always the current maximum; indices that slide out of the window are dropped from the front.",
    brute="Naïve window max: O(n · k). The deque makes each index enter and leave once: O(n).",
    idea="Maintain a deque of indices with decreasing `dp`. At index `i`: pop the front while it is older than `i − k`; `dp[i] = a[i] + dp[front]` (or `+ max(0, dp[front])` when starting fresh is allowed); pop the back while `dp[back] ≤ dp[i]`; push `i`.",
    steps=["Initialise `dp[0]` and the deque with index 0.", "Drop indices outside the window from the front.", "Compute `dp[i]` from `dp[front]`.", "Pop weaker indices from the back, then push `i`."],
    trace_title="`a = [1, −1, −2, 4, −7, 3]`, k = 2",
    trace="""dp0 = 1                     deque [0]
dp1 = -1 + dp[0] = 0        deque [0,1]
dp2 = -2 + max(dp0,dp1) = -1
dp3 =  4 + max(dp1,dp2) =  4  deque [3]
dp4 = -7 + max(dp2,dp3) = -3
dp5 =  3 + max(dp3,dp4) =  7  answer""",
    code=[("jump game VI",
           """int maxResult(int[] a, int k) {
    int n = a.length;
    int[] dp = new int[n];
    Deque<Integer> dq = new ArrayDeque<>();                        // indices with decreasing dp
    dp[0] = a[0];
    dq.addLast(0);
    for (int i = 1; i < n; i++) {
        while (dq.peekFirst() < i - k) dq.pollFirst();              // left the window
        dp[i] = a[i] + dp[dq.peekFirst()];                          // best of the last k states
        while (!dq.isEmpty() && dp[dq.peekLast()] <= dp[i]) dq.pollLast();   // weaker states are never needed again
        dq.addLast(i);
    }
    return dp[n - 1];
}""",
           """from collections import deque
def max_result(a, k):
    n = len(a)
    dp = [0] * n
    dp[0] = a[0]
    dq = deque([0])                                                  # indices with decreasing dp
    for i in range(1, n):
        while dq[0] < i - k:
            dq.popleft()                                             # left the window
        dp[i] = a[i] + dp[dq[0]]                                     # best of the last k states
        while dq and dp[dq[-1]] <= dp[i]:
            dq.pop()                                                 # weaker states are never needed again
        dq.append(i)
    return dp[-1]"""),
          ("constrained subsequence sum (may restart: add max(0, best))",
           """int constrainedSubsetSum(int[] a, int k) {
    int n = a.length, best = a[0];
    int[] dp = new int[n];
    Deque<Integer> dq = new ArrayDeque<>();
    for (int i = 0; i < n; i++) {
        while (!dq.isEmpty() && dq.peekFirst() < i - k) dq.pollFirst();
        dp[i] = a[i] + (dq.isEmpty() ? 0 : Math.max(0, dp[dq.peekFirst()]));   // extend a chain, or start a new one
        best = Math.max(best, dp[i]);
        while (!dq.isEmpty() && dp[dq.peekLast()] <= dp[i]) dq.pollLast();
        dq.addLast(i);
    }
    return best;
}""",
           """def constrained_subset_sum(a, k):
    n, best = len(a), a[0]
    dp = [0] * n
    dq = deque()
    for i in range(n):
        while dq and dq[0] < i - k:
            dq.popleft()
        dp[i] = a[i] + (max(0, dp[dq[0]]) if dq else 0)             # extend a chain, or start a new one
        best = max(best, dp[i])
        while dq and dp[dq[-1]] <= dp[i]:
            dq.pop()
        dq.append(i)
    return best""")],
    complexity="O(n) time and O(n) space (O(k) for the deque).",
    traps=["The deque stores **indices** so you can tell when the front leaves the window.", "Pop expired indices from the front **before** reading the maximum.",
           "If you may also start a new chain, use `max(0, best in window)`.", "Other transitions: prefix sums (range sums), Fenwick / segment tree (range max with updates), binary search (LIS), convex hull trick (linear functions)."],
    variants=["Max value of equation: `max(yi + yj + |xi − xj|)` with a deque over `yi − xi`.", "Jump Game V: transitions to a range bounded by the first taller element (stack + DP).", "Shortest subarray with sum at least K: monotonic deque over prefix sums (topic 05)."],
    notuse="Transitions that are not window extremes (arbitrary earlier states): the plain O(n²) DP or another structure applies.",
    problems=[
        (1696, "Jump Game VI", "M", "jump-game-vi", "dp[i] = a[i] + window max, kept by a monotonic deque", "O(n) / O(n)"),
        (1425, "Constrained Subsequence Sum", "H", "constrained-subsequence-sum", "Same deque; allow restarting with max(0, best)", "O(n) / O(n)"),
        (1499, "Max Value of Equation", "H", "max-value-of-equation", "Deque over yi − xi within the distance window", "O(n) / O(n)"),
        (1340, "Jump Game V", "H", "jump-game-v", "dp over indices sorted by value (or monotonic stack)", "O(n·d) / O(n)"),
    ]))

TOPIC = dict(
    id="dp2", file="16_dp_advanced.html", title="Dynamic Programming II — Knapsack, Sequences, Intervals and Bitmasks",
    lead="With the basics of DP in place, this guide covers the families that make DP interviews hard: 0/1 and multi-dimensional knapsack, longest common subsequence, edit distance, palindromic intervals, interval DP with split points, bitmask DP over subsets, digit DP, and the speed-ups (monotonic deque) that turn O(n·k) transitions into O(n). Each pattern has the intuition, a step-through animation that fills the table, Java and Python code, and a ladder of LeetCode problems.",
    mindset="Advanced DP is mostly **choosing the right state shape**: a 1D total (knapsack), a pair of prefixes (two strings), an interval `[l, r]` (palindromes, balloons), a set of used items (bitmask), or a position with a \"tight\" flag (digits). Once the shape is right the recurrence is usually two or three terms. Always ask what must be remembered about the past, and nothing more.",
    qintro="Ask these questions on every hard DP problem:",
    questions=["**What is the smallest description of \"where I am\"?** (total, two prefix lengths, an interval, a mask, a digit position)", "**Is it 0/1 (each item once) or unbounded?** → loop direction.",
               "**Does the answer for a range split into two independent ranges after one choice?** → interval DP.", "**Is n ≤ 20 and the order irrelevant?** → bitmask over subsets.", "**Does the transition take a max over a window?** → monotonic deque."],
    cues=[
        ["choose a subset, each once, target or capacity", "**P1** 0/1 knapsack"],
        ["two budgets at once", "**P2** Multi-dimensional knapsack"],
        ["compare two sequences, common structure", "**P3** LCS"],
        ["transform one string into another, wildcard match", "**P4** Edit distance"],
        ["palindromes inside a string", "**P5** Palindromic DP"],
        ["split point / last action in a range", "**P6** Interval DP"],
        ["assign or order ≤ 20 items", "**P7** Bitmask DP"],
        ["count numbers ≤ N with a digit rule", "**P8** Digit DP"],
        ["dp[i] = a[i] + max over the last k states", "**P9** Monotonic deque optimisation"],
    ],
    choose=[
        ["Subset with a total / capacity", "Knapsack row (P1)"],
        ["Two sequences", "Prefix-pair table (P3, P4)"],
        ["One string, inside-out structure", "Interval table (P5, P6)"],
        ["Few items, any order", "Bitmask (P7)"],
        ["Range of huge integers by digits", "Digit DP (P8)"],
        ["Window-max transition", "Monotonic deque (P9)"],
    ],
    rule="**state shape first, recurrence second.** 0/1 vs unbounded is decided by the loop direction; interval DP fills by length; bitmask DP loops over masks in increasing order.",
    selftest=[
        ("Why does 0/1 knapsack loop the capacity downwards?", "Updating from high to low guarantees every read `dp[s − x]` still holds the value from before this item, so the item is used at most once. Going upwards would reuse the same item (unbounded)."),
        ("In LCS what happens when the last characters match?", "They can both be the end of a common subsequence, so `dp[i][j] = dp[i−1][j−1] + 1`; otherwise at least one is unused and the answer is `max(dp[i−1][j], dp[i][j−1])`."),
        ("What three operations does edit distance consider and which neighbours do they correspond to?", "Replace (diagonal), delete from the first string (above), insert into the first string (left); each costs 1 and the table takes the minimum."),
        ("Why does Burst Balloons choose the LAST balloon to burst?", "At that moment its neighbours are the interval ends, and the two sides were handled earlier and independently; choosing the first would make neighbours change and break independence."),
        ("Why fill interval DP by increasing length?", "Each `dp[l][r]` depends on strictly shorter intervals inside it, so shorter ones must be computed first."),
        ("What is bitmask DP's main limitation?", "The state count is 2ⁿ, so n must be small (about 20). It also needs the order not to matter beyond which items are used."),
        ("In digit DP, what is the \"tight\" flag?", "It records that the prefix chosen so far equals N's prefix, so the next digit is limited by N's digit; once a smaller digit is chosen the rest is unconstrained."),
        ("How does the monotonic deque speed up `dp[i] = a[i] + max(dp[i−k..i−1])`?", "It keeps the window's candidates in decreasing order, so the maximum is at the front and each index enters and leaves once, giving O(n) instead of O(n·k)."),
    ],
    plan=[
        "**Day 1:** 0/1 knapsack and subset sum; write the downwards loop from memory and explain why.",
        "**Day 2:** multi-dimensional knapsack; then LCS (length and reconstruction).",
        "**Day 3:** edit distance and wildcard matching; draw the table for a small case.",
        "**Day 4:** palindromic DP and interval DP (burst balloons, cutting a stick).",
        "**Day 5:** bitmask DP (assignment, TSP) and digit DP.",
        "**Day 6:** monotonic-deque optimisation; then pick one problem per pattern and state its state, transition and base case aloud.",
    ],
    patterns=P,
)
