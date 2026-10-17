"""Content for topic 07: Recursion and backtracking."""

P = []

# ---------------------------------------------------------------- 1
P.append(dict(
    title="Recursion fundamentals: base case, trust and the call stack", tier="hot", sim="callstack", oneline="solve a smaller copy, trust it, combine",
    why="Every tree, graph, DP and backtracking solution is recursion underneath", signature="LC 509 / 50",
    when="A problem is defined in terms of a smaller version of itself.",
    detect="\"n! \" · \"power\" · \"reverse recursively\" · \"is it a power of two\" · any definition with \"the rest of the problem is the same but smaller\".",
    intuition="Russian dolls: to open the biggest doll, open the next smaller one inside it and so on until the tiniest solid doll (the **base case**). You do not need to simulate every doll in your head. Trust that the call on the smaller problem returns the right answer, and just do the small step that combines it with yours.",
    brute="Writing the loop for every depth of nesting is impossible for tree-shaped problems. Recursion lets the language manage the \"to do later\" list for you on the **call stack**.",
    idea="Every recursive function has three parts: a **base case** that stops, a **smaller subproblem** (progress toward the base case), and a **combine** step that builds the answer from the sub-answer.",
    steps=["Write the base case first (smallest input, answer known).", "Express the answer for `n` using the answer for something smaller.", "Make sure every call moves toward the base case.", "Check the depth: each pending call uses stack space, so depth = O(space)."],
    trace_title="`factorial(4)`",
    trace="""f(4) = 4 * f(3)
f(3) = 3 * f(2)
f(2) = 2 * f(1)
f(1) = 1            <- base case, stack is deepest
unwind: f(2)=2, f(3)=6, f(4)=24""",
    code=[("factorial and recursive reverse (base case + smaller problem)",
           """int fact(int n) {
    if (n <= 1) return 1;                 // base case
    return n * fact(n - 1);               // smaller problem, then combine
}

void reverse(char[] s, int l, int r) {
    if (l >= r) return;                   // base case: nothing left to swap
    char t = s[l]; s[l] = s[r]; s[r] = t;
    reverse(s, l + 1, r - 1);             // the middle is a smaller copy of the same problem
}""",
           """def fact(n):
    if n <= 1:                            # base case
        return 1
    return n * fact(n - 1)                # smaller problem, then combine

def reverse(s, l, r):
    if l >= r:                            # base case: nothing left to swap
        return
    s[l], s[r] = s[r], s[l]
    reverse(s, l + 1, r - 1)              # the middle is a smaller copy of the same problem"""),
          ("remember answers: plain recursion → memoisation",
           """int[] memo = new int[n + 1];
int climb(int n) {                         // ways to climb n stairs, 1 or 2 steps at a time
    if (n <= 1) return 1;
    if (memo[n] != 0) return memo[n];      // already solved: reuse
    return memo[n] = climb(n - 1) + climb(n - 2);
}""",
           """from functools import lru_cache
@lru_cache(None)
def climb(n):                              # ways to climb n stairs, 1 or 2 steps at a time
    if n <= 1:
        return 1
    return climb(n - 1) + climb(n - 2)     # each n is computed once""")],
    complexity="Time = (number of calls) × (work per call). Space = recursion depth (plus any memo).",
    traps=["Missing or wrong base case causes infinite recursion and a stack overflow.", "The recursive call must make progress (`n − 1`, `l + 1`); otherwise it loops forever.",
           "Java and Python have no tail-call optimisation: depth of ~10⁴–10⁵ can overflow. Convert to a loop or an explicit stack.", "Overlapping subproblems (Fibonacci) blow up to O(2ⁿ): add memoisation."],
    variants=["Fast power: halve the exponent each call (depth log n).", "Mutual recursion and recursion on trees (topic 09).", "Recursion → iteration: an explicit stack mimics the call stack."],
    notuse="When a simple loop is clearer and the depth could be huge.",
    problems=[
        (509, "Fibonacci Number", "E", "fibonacci-number", "Two recursive calls; memoise to avoid O(2ⁿ)", "O(n) / O(n)"),
        (231, "Power of Two", "E", "power-of-two", "n is a power of two if n/2 is, base case n == 1", "O(log n) / O(log n)"),
        (344, "Reverse String", "E", "reverse-string", "Swap ends, recurse on the middle", "O(n) / O(n)"),
        (50, "Pow(x, n)", "M", "powx-n", "Halve the exponent; square the half result", "O(log n) / O(log n)"),
        (779, "K-th Symbol in Grammar", "M", "k-th-symbol-in-grammar", "Row n is row n−1 followed by its flip: recurse on the parent index", "O(n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 2
P.append(dict(
    title="Subsets: the choose / explore / un-choose template", tier="hot", sim="subsets", oneline="every path in the decision tree is an answer",
    why="The template that every other backtracking problem copies", signature="LC 78",
    when="Generate all subsets, or decide for each element whether it is in or out.",
    detect="\"all subsets / power set\" · \"all possible\" · \"letter case permutations\" · \"partition into k groups\" · \"target sum with +/−\".",
    intuition="Picture a tree of decisions. At the root you have chosen nothing. Each step you add one more element from those not yet considered. Walking down is **choose**, recursing is **explore**, coming back up and removing the element is **un-choose** (backtrack). Because you undo every choice, the same path list is reused for the whole search.",
    brute="Generating subsets with bitmasks works for small n. Backtracking is the same 2ⁿ work but lets you **prune** early (stop going down when a constraint is already broken).",
    idea="`dfs(start, path)`: record `path`; for `i` from `start` to `n − 1`: append `a[i]`, `dfs(i + 1)`, remove `a[i]`. Using `start` ensures each combination is generated in one order only.",
    steps=["Record the current `path` (a copy!).", "For each `i` from `start`: **choose** `a[i]` (append).", "**Explore** `dfs(i + 1, path)`.", "**Un-choose** (remove the last element) and try the next `i`."],
    trace_title="`[1,2,3]`",
    trace="""[]  [1]  [1,2]  [1,2,3]  (back)  [1,3]  (back, back)
[2]  [2,3]  (back, back)  [3]
8 subsets = 2^3""",
    code=[("subsets with the start-index template",
           """List<List<Integer>> res = new ArrayList<>();
void dfs(int[] a, int start, List<Integer> path) {
    res.add(new ArrayList<>(path));                     // copy: path keeps changing
    for (int i = start; i < a.length; i++) {
        path.add(a[i]);                                  // choose
        dfs(a, i + 1, path);                             // explore
        path.remove(path.size() - 1);                    // un-choose
    }
}""",
           """res = []
def dfs(start, path):
    res.append(path[:])                                  # copy: path keeps changing
    for i in range(start, len(a)):
        path.append(a[i])                                # choose
        dfs(i + 1, path)                                 # explore
        path.pop()                                       # un-choose
dfs(0, [])"""),
          ("include / exclude form and bitmask form",
           """List<List<Integer>> res = new ArrayList<>();

// include or exclude each element
void dfs(int[] a, int i, List<Integer> path) {
    if (i == a.length) { res.add(new ArrayList<>(path)); return; }
    dfs(a, i + 1, path);                                 // exclude a[i]
    path.add(a[i]);
    dfs(a, i + 1, path);                                 // include a[i]
    path.remove(path.size() - 1);
}

// bitmask: every integer 0 .. 2^n - 1 is a subset
List<List<Integer>> allSubsets(int[] a) {
    int n = a.length;
    List<List<Integer>> out = new ArrayList<>();
    for (int mask = 0; mask < (1 << n); mask++) {
        List<Integer> s = new ArrayList<>();
        for (int j = 0; j < n; j++) if ((mask >> j & 1) == 1) s.add(a[j]);
        out.add(s);
    }
    return out;
}""",
           """def dfs(i, path):
    if i == len(a):
        res.append(path[:])
        return
    dfs(i + 1, path)                                     # exclude a[i]
    path.append(a[i])
    dfs(i + 1, path)                                     # include a[i]
    path.pop()

# bitmask: every integer 0 .. 2^n - 1 is a subset
for mask in range(1 << len(a)):
    res.append([a[j] for j in range(len(a)) if mask >> j & 1])""")],
    complexity="O(n · 2ⁿ) time (2ⁿ subsets, each copied in O(n)), O(n) recursion depth.",
    traps=["Append a **copy** of `path` (`new ArrayList<>(path)` / `path[:]`), not the list itself.", "Always undo the choice after the recursive call, or paths leak into each other.",
           "Pass `i + 1` (not `start + 1`) so elements are not reused or reordered.", "Pruning belongs before the recursive call (check the constraint, then choose)."],
    variants=["Letter case permutation: two branches only at letters.", "Target sum / partition to k equal subsets: include/exclude with a running sum and pruning.", "Subsets of size k = combinations (next pattern)."],
    notuse="When the number of valid results is exponential but you only need a count or an optimum: use DP instead.",
    problems=[
        (1863, "Sum of All Subset XOR Totals", "E", "sum-of-all-subset-xor-totals", "Include / exclude carrying the running XOR", "O(2ⁿ) / O(n)"),
        (78, "Subsets", "M", "subsets", "Start-index template, record on entry", "O(n·2ⁿ) / O(n)"),
        (784, "Letter Case Permutation", "M", "letter-case-permutation", "Branch lower / upper only at letters", "O(n·2ⁿ) / O(n)"),
        (494, "Target Sum", "M", "target-sum", "Include / exclude with ± and a running total (memo → DP)", "O(2ⁿ) / O(n)"),
        (698, "Partition to K Equal Sum Subsets", "M", "partition-to-k-equal-sum-subsets", "Fill buckets with pruning; skip duplicate states", "O(k·2ⁿ) / O(n)"),
        (473, "Matchsticks to Square", "M", "matchsticks-to-square", "Place each stick into one of 4 sides; sort descending to prune", "O(4ⁿ) / O(n)"),
    ]))

# ---------------------------------------------------------------- 3
P.append(dict(
    title="Combinations and combination sum", tier="hot", sim="combsum", oneline="a start index stops [2,3] and [3,2] being counted twice",
    why="The reusable skeleton for \"pick items summing to a target\"", signature="LC 39 / 77",
    when="Choose k items, or any items whose sum meets a target, where order does not matter.",
    detect="\"combinations of k numbers\" · \"combination sum\" · \"letter combinations of a phone number\" · \"choose items to reach a total\".",
    intuition="Order does not matter for a combination, so impose one: only ever pick items at or after the one you took last. That removes the permutations of the same set without checking anything. Add **pruning**: if the candidate is already larger than what is left, stop (and, in a sorted list, so is everything after it).",
    brute="Generate all subsets and filter by sum: O(2ⁿ) work even when most are hopeless. Pruning cuts whole branches as soon as the remaining target is exceeded.",
    idea="Sort candidates. `dfs(start, remaining, path)`: if `remaining == 0` record; for `i ≥ start`: if `c[i] > remaining` break; choose `c[i]`; recurse with `start = i` (reuse allowed) or `i + 1` (each once); un-choose.",
    steps=["Sort the candidates (enables the early `break`).", "Base case: `remaining == 0` → record a copy.", "Loop `i` from `start`; `break` when `c[i] > remaining`.", "Recurse with `i` (unlimited reuse) or `i + 1` (single use)."],
    trace_title="candidates `[2,3,5]`, target 5",
    trace="""[2]  rem 3 -> [2,2] rem 1 -> 2 > 1 prune
              [2,3] rem 0  FOUND
              5 > 3 prune
[3]  rem 2 -> 3 > 2 prune
[5]  rem 0  FOUND
=> [2,3] [5]""",
    code=[("combination sum (numbers reusable)",
           """void dfs(int[] c, int start, int rem, List<Integer> path) {
    if (rem == 0) { res.add(new ArrayList<>(path)); return; }
    for (int i = start; i < c.length; i++) {
        if (c[i] > rem) break;                           // sorted: everything after is too big too
        path.add(c[i]);
        dfs(c, i, rem - c[i], path);                      // i, not i + 1: the same number may be reused
        path.remove(path.size() - 1);
    }
}
// call: Arrays.sort(c); dfs(c, 0, target, new ArrayList<>());""",
           """def dfs(start, rem, path):
    if rem == 0:
        res.append(path[:])
        return
    for i in range(start, len(c)):
        if c[i] > rem:
            break                                        # sorted: everything after is too big too
        path.append(c[i])
        dfs(i, rem - c[i], path)                         # i, not i + 1: the same number may be reused
        path.pop()
c.sort()
dfs(0, target, [])"""),
          ("combinations C(n, k) with a length-based prune",
           """void dfs(int n, int k, int start, List<Integer> path) {
    if (path.size() == k) { res.add(new ArrayList<>(path)); return; }
    for (int i = start; i <= n - (k - path.size()) + 1; i++) {   // not enough numbers left otherwise
        path.add(i);
        dfs(n, k, i + 1, path);
        path.remove(path.size() - 1);
    }
}""",
           """def dfs(start, path):
    if len(path) == k:
        res.append(path[:])
        return
    for i in range(start, n - (k - len(path)) + 2):              # not enough numbers left otherwise
        path.append(i)
        dfs(i + 1, path)
        path.pop()
dfs(1, [])""")],
    complexity="Worst case O(2ⁿ) or C(n, k) × k; pruning reduces it a lot in practice. Depth O(target / min candidate).",
    traps=["Use `i` for reusable candidates and `i + 1` for single-use ones.", "Without sorting, the `break` prune is wrong (use `continue` instead).",
           "Record a copy of `path`.", "Phone-number letters is the same loop, but over the letters of the current digit instead of a start index."],
    variants=["Combination Sum III: exactly k numbers 1–9 summing to n.", "Combination Sum II: each number once, with duplicates skipped (next pattern).", "Number of ways (not the lists): use DP / unbounded knapsack instead."],
    notuse="When only the **count** of combinations is needed (DP is polynomial) or the target is huge.",
    problems=[
        (77, "Combinations", "M", "combinations", "Pick k numbers from 1..n with a start index", "O(C(n,k)·k) / O(k)"),
        (216, "Combination Sum III", "M", "combination-sum-iii", "k numbers from 1..9 summing to n, each once", "O(C(9,k)) / O(k)"),
        (17, "Letter Combinations of a Phone Number", "M", "letter-combinations-of-a-phone-number", "One letter per digit: depth = number of digits", "O(4ⁿ·n) / O(n)"),
        (39, "Combination Sum", "M", "combination-sum", "Reusable candidates, sorted, prune when too large", "O(2^target) / O(target)"),
    ]))

# ---------------------------------------------------------------- 4
P.append(dict(
    title="Permutations: choose any unused element", tier="hot", sim="perm", oneline="a used[] array turns subsets into orderings",
    why="The other core template: when order matters", signature="LC 46",
    when="Arrange all items in every possible order.",
    detect="\"all permutations\" · \"all arrangements\" · \"next / k-th permutation\" · \"beautiful arrangement\".",
    intuition="Filling n seats one by one: for seat 1 you may pick anyone, for seat 2 anyone who is not already seated, and so on. The `used` array is the list of people already seated. When all seats are filled, record the arrangement; then un-seat the last person and try someone else.",
    brute="Trying all n^n sequences and rejecting repeats is wasteful. Tracking `used` ensures only n! valid sequences are ever generated.",
    idea="`dfs(path)`: if `path.size() == n` record; for each index `i` not used: mark used, append, recurse, remove, unmark. A swap-based variant permutes the array in place.",
    steps=["Base case: path is full → record a copy.", "For each element not used: mark it used and append.", "Recurse for the next position.", "Backtrack: remove it and mark unused."],
    trace_title="`[1,2,3]`",
    trace="""1 -> 12 -> 123 *   1 -> 13 -> 132 *
2 -> 21 -> 213 *   2 -> 23 -> 231 *
3 -> 31 -> 312 *   3 -> 32 -> 321 *
6 permutations = 3!""",
    code=[("permutations with a used array",
           """void dfs(int[] a, boolean[] used, List<Integer> path) {
    if (path.size() == a.length) { res.add(new ArrayList<>(path)); return; }
    for (int i = 0; i < a.length; i++) {
        if (used[i]) continue;
        used[i] = true; path.add(a[i]);                  // choose
        dfs(a, used, path);                              // explore
        path.remove(path.size() - 1); used[i] = false;   // un-choose
    }
}""",
           """def dfs(path):
    if len(path) == len(a):
        res.append(path[:])
        return
    for i in range(len(a)):
        if used[i]:
            continue
        used[i] = True
        path.append(a[i])                                # choose
        dfs(path)                                        # explore
        path.pop()
        used[i] = False                                  # un-choose
used = [False] * len(a)
dfs([])"""),
          ("in-place swap version",
           """void dfs(int[] a, int k) {
    if (k == a.length) { res.add(toList(a)); return; }
    for (int i = k; i < a.length; i++) {
        swap(a, k, i);                                   // place a[i] at position k
        dfs(a, k + 1);
        swap(a, k, i);                                   // undo
    }
}""",
           """def dfs(k):
    if k == len(a):
        res.append(a[:])
        return
    for i in range(k, len(a)):
        a[k], a[i] = a[i], a[k]                          # place a[i] at position k
        dfs(k + 1)
        a[k], a[i] = a[i], a[k]                          # undo
dfs(0)""")],
    complexity="O(n · n!) time, O(n) space for recursion and the used array.",
    traps=["Start the loop at `0` (not `start`): order matters, so any unused element can come next.", "Forgetting to reset `used[i] = false` after the recursive call.",
           "n! grows fast: n = 10 is 3.6 million; n = 12 is 479 million.", "For \"next permutation\" or the k-th permutation do **not** generate all of them: use the factorial number system or the next-permutation algorithm."],
    variants=["Beautiful arrangement: permutations with a divisibility check as pruning.", "Permutation sequence: compute the k-th directly with factorials.", "Permutations with duplicates: sort and skip repeats (next pattern)."],
    notuse="When you need only the k-th or next permutation, or the number of permutations (use math).",
    problems=[
        (46, "Permutations", "M", "permutations", "used[] array: choose any unused element at each position", "O(n·n!) / O(n)"),
        (526, "Beautiful Arrangement", "M", "beautiful-arrangement", "Permutation with a divisibility prune", "O(k) / O(n)"),
        (31, "Next Permutation", "M", "next-permutation", "No search needed: pivot, swap, reverse suffix", "O(n) / O(1)"),
        (60, "Permutation Sequence", "H", "permutation-sequence", "Pick digits using factorials; no enumeration", "O(n²) / O(n)"),
    ]))

# ---------------------------------------------------------------- 5
P.append(dict(
    title="Handling duplicates: sort and skip", tier="hot", sim="dedupe", oneline="never pick the same value twice at the same level",
    why="The usual twist that separates a correct answer from one with repeated results", signature="LC 90 / 47 / 40",
    when="The input has repeated values and the output must not contain duplicate subsets, permutations or combinations.",
    detect="\"Subsets II\" · \"Permutations II\" · \"Combination Sum II\" · \"unique combinations\" · \"no duplicate sets\".",
    intuition="If two cards both show a 2, choosing \"the first 2\" and then \"the second 2\" gives the same hand as the reverse. To avoid that, make equal cards line up (sort) and add a rule: at any one position in the decision tree, you may use a given value **only once as a choice**. The second 2 can still be used deeper in the recursion (after the first 2 was chosen).",
    brute="Generate everything and remove duplicates with a set: correct but wastes time and memory. Skipping at the source never creates the duplicates.",
    idea="Sort the array. In the loop at a given level, `if (i > start && a[i] == a[i − 1]) continue;`. For permutations use `used[]` and skip when `a[i] == a[i − 1] && !used[i − 1]`.",
    steps=["Sort so equal values are adjacent.", "Within one loop level, skip `a[i]` if it equals `a[i − 1]` and `i > start` (the first of the run was already tried at this level).", "Permutations: skip `a[i]` if `a[i − 1]` is equal and **not currently used**.", "Everything else is the normal template."],
    trace_title="subsets of `[1,2,2]`",
    trace="""[] [1] [1,2] [1,2,2]
  at level start=1: i=2 equals i=1 -> skip
[2] [2,2]
  at root: i=2 equals i=1 -> skip
=> [] [1] [1,2] [1,2,2] [2] [2,2]  (6, not 8)""",
    code=[("Subsets II (duplicates in the input)",
           """List<List<Integer>> res = new ArrayList<>();

List<List<Integer>> subsetsWithDup(int[] a) {
    Arrays.sort(a);
    dfs(a, 0, new ArrayList<>());
    return res;
}
void dfs(int[] a, int start, List<Integer> path) {
    res.add(new ArrayList<>(path));
    for (int i = start; i < a.length; i++) {
        if (i > start && a[i] == a[i - 1]) continue;         // same value already tried at this level
        path.add(a[i]);
        dfs(a, i + 1, path);
        path.remove(path.size() - 1);
    }
}""",
           """a.sort()
def dfs(start, path):
    res.append(path[:])
    for i in range(start, len(a)):
        if i > start and a[i] == a[i - 1]:
            continue                                         # same value already tried at this level
        path.append(a[i])
        dfs(i + 1, path)
        path.pop()
dfs(0, [])"""),
          ("Permutations II (duplicates in the input)",
           """List<List<Integer>> res = new ArrayList<>();

List<List<Integer>> permuteUnique(int[] a) {
    Arrays.sort(a);
    dfs(a, new boolean[a.length], new ArrayList<>());
    return res;
}
void dfs(int[] a, boolean[] used, List<Integer> path) {
    if (path.size() == a.length) { res.add(new ArrayList<>(path)); return; }
    for (int i = 0; i < a.length; i++) {
        if (used[i]) continue;
        if (i > 0 && a[i] == a[i - 1] && !used[i - 1]) continue;   // keep equal values in a fixed order
        used[i] = true; path.add(a[i]);
        dfs(a, used, path);
        path.remove(path.size() - 1); used[i] = false;
    }
}""",
           """a.sort()
used = [False] * len(a)
def dfs(path):
    if len(path) == len(a):
        res.append(path[:])
        return
    for i in range(len(a)):
        if used[i]:
            continue
        if i > 0 and a[i] == a[i - 1] and not used[i - 1]:       # keep equal values in a fixed order
            continue
        used[i] = True
        path.append(a[i])
        dfs(path)
        path.pop()
        used[i] = False
dfs([])""")],
    complexity="Same as the base template; the skip removes duplicate subtrees (often a large saving).",
    traps=["You **must** sort first; the skip rule relies on equal values being adjacent.", "`i > start` (not `i > 0`) for subsets and combinations; `i > 0` with the `!used[i − 1]` condition for permutations.",
           "Skipping is per **level**, not global: the second 2 is still allowed deeper in the same path.", "Combination Sum II: skip duplicates **and** recurse with `i + 1` (each element used once)."],
    variants=["Non-decreasing subsequences (no sorting allowed): use a per-level `HashSet` of values already tried.", "Letter tile possibilities: count letters and branch over distinct letters."],
    notuse="If all elements are distinct, none of this is needed.",
    problems=[
        (90, "Subsets II", "M", "subsets-ii", "Sort; skip a[i] == a[i−1] when i > start", "O(n·2ⁿ) / O(n)"),
        (47, "Permutations II", "M", "permutations-ii", "Sort; skip equal value if the previous equal is unused", "O(n·n!) / O(n)"),
        (40, "Combination Sum II", "M", "combination-sum-ii", "Sort; use each once; skip duplicates at a level", "O(2ⁿ) / O(n)"),
        (491, "Non-decreasing Subsequences", "M", "non-decreasing-subsequences", "Cannot sort: per-level set of used values", "O(n·2ⁿ) / O(n)"),
        (1079, "Letter Tile Possibilities", "M", "letter-tile-possibilities", "Count letters; branch over each distinct letter", "O(n!) / O(n)"),
    ]))

# ---------------------------------------------------------------- 6
P.append(dict(
    title="Strings: partitions, cuts and letter choices", tier="hot", sim="partition", oneline="at each start index try every end, keep the valid piece",
    why="Cutting strings into valid parts is a standard backtracking family", signature="LC 131 / 93",
    when="Split a string into pieces that each satisfy a rule, or build a string from per-position choices.",
    detect="\"palindrome partitioning\" · \"restore IP addresses\" · \"word break II\" · \"letter combinations\" · \"concatenated string with unique characters\".",
    intuition="Cutting a loaf into slices where every slice must be acceptable. Stand at the current cut position and try every possible next slice: if the slice is valid, take it and continue from where it ends. If you reach the end of the loaf, the slices so far are an answer.",
    brute="Try every set of cut positions (2ⁿ⁻¹) and check each piece afterwards. Checking each piece **as soon as it is formed** rejects bad cuts early.",
    idea="`dfs(start, path)`: if `start == n` record `path`. For `end` in `start..n−1`: `piece = s[start..end]`; if valid, append, `dfs(end + 1)`, remove.",
    steps=["Base case: `start == n` → record the partition.", "Loop `end` from `start` to `n − 1`.", "If `s[start..end]` is valid (palindrome, number 0–255, dictionary word), choose it.", "Recurse from `end + 1`; then un-choose."],
    trace_title="palindrome partitions of `\"aab\"`",
    trace="""cut "a"   -> "a" -> "b"      record [a, a, b]
          "ab" not a palindrome
cut "aa"  -> "b"             record [aa, b]
cut "aab" not a palindrome""",
    code=[("palindrome partitioning",
           """void dfs(String s, int start, List<String> path) {
    if (start == s.length()) { res.add(new ArrayList<>(path)); return; }
    for (int end = start; end < s.length(); end++) {
        if (!isPal(s, start, end)) continue;                       // prune: bad piece
        path.add(s.substring(start, end + 1));
        dfs(s, end + 1, path);
        path.remove(path.size() - 1);
    }
}
boolean isPal(String s, int l, int r) { while (l < r) if (s.charAt(l++) != s.charAt(r--)) return false; return true; }""",
           """def dfs(start, path):
    if start == len(s):
        res.append(path[:])
        return
    for end in range(start, len(s)):
        piece = s[start:end + 1]
        if piece != piece[::-1]:
            continue                                           # prune: bad piece
        path.append(piece)
        dfs(end + 1, path)
        path.pop()
dfs(0, [])"""),
          ("letter case permutation (branch only at letters)",
           """void dfs(char[] c, int i) {
    if (i == c.length) { res.add(new String(c)); return; }
    dfs(c, i + 1);                                           // keep as is
    if (Character.isLetter(c[i])) {
        c[i] ^= 32;                                          // flip the case
        dfs(c, i + 1);
        c[i] ^= 32;                                          // un-choose
    }
}""",
           """def dfs(i, cur):
    if i == len(s):
        res.append(''.join(cur))
        return
    dfs(i + 1, cur)                                          # keep as is
    if s[i].isalpha():
        cur[i] = cur[i].swapcase()                           # flip the case
        dfs(i + 1, cur)
        cur[i] = cur[i].swapcase()                           # un-choose
dfs(0, list(s))""")],
    complexity="O(n · 2ⁿ) for palindrome partitioning (a DP table can precompute palindromes in O(n²)); IP addresses are bounded by 3⁴ cuts.",
    traps=["Do the validity check **before** recursing; do not generate then filter.", "Cutting at `end + 1`, not `end`.", "Leading zeros in IP octets (`\"01\"` invalid) and the range 0–255.", "Word Break II: memoise on `start` or it times out."],
    variants=["Restore IP addresses: exactly 4 parts, each 1–3 digits and ≤ 255.", "Word Break II: pieces must be dictionary words; memoise the sentences from each index.", "Maximum length concatenation with unique characters: bitmask of used letters."],
    notuse="When only a count or the minimum number of cuts is needed (use DP).",
    problems=[
        (131, "Palindrome Partitioning", "M", "palindrome-partitioning", "Try every end; take only palindromic pieces", "O(n·2ⁿ) / O(n)"),
        (93, "Restore IP Addresses", "M", "restore-ip-addresses", "Four parts of 1–3 digits, value ≤ 255, no leading zero", "O(1) bounded / O(1)"),
        (1239, "Maximum Length of a Concatenated String with Unique Characters", "M", "maximum-length-of-a-concatenated-string-with-unique-characters", "Include / exclude with a letter bitmask", "O(2ⁿ) / O(n)"),
        (140, "Word Break II", "H", "word-break-ii", "Try dictionary prefixes; memoise results per start", "O(2ⁿ) / O(2ⁿ)"),
    ]))

# ---------------------------------------------------------------- 7
P.append(dict(
    title="Grid and path search with visited marking", tier="hot", sim="wordgrid", oneline="mark the cell, explore four ways, unmark on the way back",
    why="Word Search and path-count problems appear in nearly every interview loop", signature="LC 79",
    when="Find a path through a grid or board where cells cannot be reused within one path.",
    detect="\"word search\" · \"path with maximum gold\" · \"unique paths III\" · \"can the word be formed from adjacent cells\".",
    intuition="Exploring a maze with a ball of thread: leave a mark where you have been so you do not walk in circles, and when a corridor dead-ends, walk back **removing the mark** so a different route can still pass through that cell. The un-marking is what makes it backtracking rather than a plain flood fill.",
    brute="Enumerating all paths blindly explodes. Matching the next letter at each step rejects almost every path immediately.",
    idea="For each start cell run `dfs(r, c, k)`: fail on out-of-bounds, a visited cell or a mismatch; mark the cell; try 4 neighbours; unmark; return whether any succeeded.",
    steps=["Try every cell as a start.", "`dfs`: if `k == len(word)` → success.", "Reject if out of bounds or `board[r][c] != word[k]`.", "Mark visited (e.g. set to `#`), recurse in 4 directions, restore the cell, return the result."],
    trace_title="ABCCED in a 3×4 board",
    trace="""A(0,0) -> B(0,1) -> C(0,2)
C: right (0,3)=E not C  dead end
   down  (1,2)=C ok -> E(2,2) -> D(2,1)   word complete
path: (0,0)(0,1)(0,2)(1,2)(2,2)(2,1)""",
    code=[("word search",
           """boolean exist(char[][] b, String w) {
    for (int r = 0; r < b.length; r++)
        for (int c = 0; c < b[0].length; c++)
            if (dfs(b, w, 0, r, c)) return true;
    return false;
}
boolean dfs(char[][] b, String w, int k, int r, int c) {
    if (k == w.length()) return true;
    if (r < 0 || c < 0 || r >= b.length || c >= b[0].length || b[r][c] != w.charAt(k)) return false;
    char t = b[r][c];
    b[r][c] = '#';                                            // mark visited
    boolean ok = dfs(b, w, k + 1, r + 1, c) || dfs(b, w, k + 1, r - 1, c)
              || dfs(b, w, k + 1, r, c + 1) || dfs(b, w, k + 1, r, c - 1);
    b[r][c] = t;                                              // un-mark (backtrack)
    return ok;
}""",
           """def exist(board, word):
    R, C = len(board), len(board[0])
    def dfs(r, c, k):
        if k == len(word):
            return True
        if not (0 <= r < R and 0 <= c < C) or board[r][c] != word[k]:
            return False
        t, board[r][c] = board[r][c], '#'                     # mark visited
        ok = (dfs(r + 1, c, k + 1) or dfs(r - 1, c, k + 1) or
              dfs(r, c + 1, k + 1) or dfs(r, c - 1, k + 1))
        board[r][c] = t                                       # un-mark (backtrack)
        return ok
    return any(dfs(r, c, 0) for r in range(R) for c in range(C))"""),
          ("path with maximum gold (best path, not just existence)",
           """int maxGold(int[][] g) {
    int best = 0;
    for (int r = 0; r < g.length; r++)
        for (int c = 0; c < g[0].length; c++) best = Math.max(best, dfs(g, r, c));
    return best;
}
int dfs(int[][] g, int r, int c) {
    if (r < 0 || c < 0 || r >= g.length || c >= g[0].length || g[r][c] == 0) return 0;
    int gold = g[r][c];
    g[r][c] = 0;                                              // mark
    int next = Math.max(Math.max(dfs(g, r + 1, c), dfs(g, r - 1, c)), Math.max(dfs(g, r, c + 1), dfs(g, r, c - 1)));
    g[r][c] = gold;                                           // un-mark
    return gold + next;
}""",
           """def dfs(r, c):
    if not (0 <= r < m and 0 <= c < n) or g[r][c] == 0:
        return 0
    gold, g[r][c] = g[r][c], 0                                # mark
    nxt = max(dfs(r + 1, c), dfs(r - 1, c), dfs(r, c + 1), dfs(r, c - 1))
    g[r][c] = gold                                            # un-mark
    return gold + nxt
best = max(dfs(r, c) for r in range(m) for c in range(n))""")],
    complexity="O(m · n · 3^L) for word length L (3 choices after the first step), O(L) recursion depth.",
    traps=["Forgetting to restore the cell makes later searches fail.", "Order of checks: bounds **first**, then the cell value.",
           "Use `||` short-circuiting so you stop at the first success.", "For many words (Word Search II) build a trie and prune with it."],
    variants=["Unique Paths III: count paths that visit every empty cell exactly once (track remaining cells).", "Word Search II: trie + same DFS.", "Flood fill and islands are the same DFS **without** un-marking (topic 12)."],
    notuse="When you only need connectivity or shortest paths (BFS / DFS with permanent marks).",
    problems=[
        (79, "Word Search", "M", "word-search", "Match letter by letter; mark and un-mark the cell", "O(m·n·3^L) / O(L)"),
        (1219, "Path with Maximum Gold", "M", "path-with-maximum-gold", "Return gold + best neighbour; un-mark after", "O(m·n·3^k) / O(k)"),
        (980, "Unique Paths III", "H", "unique-paths-iii", "Count paths covering every empty cell once", "O(3^(m·n)) / O(m·n)"),
        (212, "Word Search II", "H", "word-search-ii", "Trie of words + DFS; prune dead trie branches", "O(m·n·3^L) / O(total letters)"),
    ]))

# ---------------------------------------------------------------- 8
P.append(dict(
    title="Constraint search: N-Queens and Sudoku", tier="hot", sim="nqueens", oneline="place, check constraints in O(1), undo when stuck",
    why="The standard \"hard backtracking\" interview problems", signature="LC 51 / 37",
    when="Fill a board so that every row, column or region obeys constraints.",
    detect="\"N-Queens\" · \"Sudoku solver\" · \"place pieces so none attack\" · \"fill the grid\".",
    intuition="Place one thing at a time in a fixed order (row by row). At each step only the options consistent with everything already placed are tried. If a row has **no** legal option, an earlier decision must have been wrong, so undo the previous placement and try its next option. Constant-time conflict checks (boolean arrays for columns and diagonals) keep it fast.",
    brute="Putting n queens anywhere is C(n², n) boards. One queen per row cuts it to nⁿ; rejecting conflicts immediately cuts it to a tiny fraction.",
    idea="`dfs(row)`: if `row == n` record the board; for each column: if no conflict, place, `dfs(row + 1)`, remove. Conflicts: `col`, `row + col` (anti-diagonal) and `row − col` (diagonal) each tracked in a set or boolean array.",
    steps=["Row by row: for each column, test `cols[c]`, `d1[r + c]`, `d2[r − c + n − 1]`.", "If safe: mark the three, place the queen, recurse to the next row.", "On return: unmark and remove.", "At `row == n`: record (or count) the solution."],
    trace_title="4-Queens",
    trace="""row0 c0 -> row1 c2 -> row2 no safe column  undo c2
        row1 c3 -> row2 c1 -> row3 no safe column  undo
undo row0 c0, try c1
row0 c1 -> row1 c3 -> row2 c0 -> row3 c2   SOLUTION (1,3,0,2)""",
    code=[("N-Queens (count solutions) with O(1) conflict checks",
           """int count = 0;
boolean[] cols, d1, d2;                                 // d1[r + c], d2[r - c + n - 1]
void dfs(int r, int n) {
    if (r == n) { count++; return; }
    for (int c = 0; c < n; c++) {
        if (cols[c] || d1[r + c] || d2[r - c + n - 1]) continue;
        cols[c] = d1[r + c] = d2[r - c + n - 1] = true;          // place
        dfs(r + 1, n);
        cols[c] = d1[r + c] = d2[r - c + n - 1] = false;         // remove
    }
}
// init: cols = new boolean[n]; d1 = new boolean[2 * n]; d2 = new boolean[2 * n];""",
           """def total_n_queens(n):
    cols, d1, d2 = set(), set(), set()
    def dfs(r):
        if r == n:
            return 1
        count = 0
        for c in range(n):
            if c in cols or r + c in d1 or r - c in d2:
                continue
            cols.add(c); d1.add(r + c); d2.add(r - c)            # place
            count += dfs(r + 1)
            cols.remove(c); d1.remove(r + c); d2.remove(r - c)   # remove
        return count
    return dfs(0)"""),
          ("Sudoku solver (try digits in the first empty cell)",
           """boolean solve(char[][] b) {
    for (int r = 0; r < 9; r++) for (int c = 0; c < 9; c++) {
        if (b[r][c] != '.') continue;
        for (char d = '1'; d <= '9'; d++) {
            if (!ok(b, r, c, d)) continue;
            b[r][c] = d;
            if (solve(b)) return true;
            b[r][c] = '.';                                       // undo
        }
        return false;                                            // no digit fits: backtrack
    }
    return true;                                                 // no empty cell left
}
boolean ok(char[][] b, int r, int c, char d) {
    for (int i = 0; i < 9; i++)
        if (b[r][i] == d || b[i][c] == d || b[r / 3 * 3 + i / 3][c / 3 * 3 + i % 3] == d) return false;
    return true;
}""",
           """def solve(b):
    for r in range(9):
        for c in range(9):
            if b[r][c] != '.':
                continue
            for d in '123456789':
                if ok(b, r, c, d):
                    b[r][c] = d
                    if solve(b):
                        return True
                    b[r][c] = '.'                                # undo
            return False                                         # no digit fits: backtrack
    return True                                                  # no empty cell left

def ok(b, r, c, d):
    for i in range(9):
        if b[r][i] == d or b[i][c] == d or b[r // 3 * 3 + i // 3][c // 3 * 3 + i % 3] == d:
            return False
    return True""")],
    complexity="N-Queens roughly O(n!) with pruning; Sudoku worst case exponential but fast in practice with constraint checks.",
    traps=["The anti-diagonal index is `row + col`; the diagonal is `row − col` (offset by `n − 1` in an array).", "Undo **all three** marks when backtracking.",
           "For printing boards, build the strings only when a solution is complete.", "Sudoku: choose the empty cell with the fewest candidates first (MRV) for a big speed-up."],
    variants=["N-Queens II: count only.", "Bitmask version of N-Queens with three integers is the fastest.", "Other constraint puzzles (graph colouring, knight's tour) use the same skeleton."],
    notuse="When the constraint structure fits a polynomial algorithm (matching, DP).",
    problems=[
        (52, "N-Queens II", "H", "n-queens-ii", "Count solutions with column and diagonal sets", "O(n!) / O(n)"),
        (51, "N-Queens", "H", "n-queens", "Same search, build the board strings on success", "O(n!) / O(n²)"),
        (37, "Sudoku Solver", "H", "sudoku-solver", "First empty cell, try 1–9 with row/column/box checks", "O(9^empty) / O(1)"),
    ]))

# ---------------------------------------------------------------- 9
P.append(dict(
    title="Pruning and memoisation: generate only valid states", tier="sec", sim="parens", oneline="never build the branches you know will fail",
    why="The difference between a TLE and an accepted backtracking solution", signature="LC 22 / 139",
    when="Most branches of the search tree are invalid, or the same sub-state is reached again and again.",
    detect="\"generate parentheses\" · \"remove invalid parentheses\" · \"word break\" · \"expression add operators\" · \"additive number\".",
    intuition="Instead of writing every possible string and then crossing out the bad ones, never write a letter that can only lead to a bad string. For parentheses: you may open a bracket while some are still unspent, but you may close one only if an open one is waiting. The tree contains only valid prefixes, so nothing is wasted. When the same sub-problem reappears (the same suffix of a string), remember its answer.",
    brute="Generating all 2^(2n) strings and filtering costs exponential time even for tiny answers. Pruned generation visits only the Catalan(n) valid results and their valid prefixes.",
    idea="Carry the state that defines validity (`open`, `close`, current sum, last operand) and check it **before** recursing. If `dfs(state)` can be reached by several paths, cache `state → result` (memoisation); this is the bridge to dynamic programming.",
    steps=["Identify the invariant of a valid prefix (e.g. `close ≤ open ≤ n`).", "Only recurse into choices that keep the invariant.", "Record when the length (or goal) is reached.", "If states repeat, add a memo keyed by the state."],
    trace_title="n = 2 parentheses",
    trace="""(    open 1
((   open 2   (cannot add another '(' : open == n)
(()  close 1
(()) close 2  RECORD
()   close 1 <= open 1
()(  open 2
()() RECORD
=> (()) ()()""",
    code=[("generate parentheses (prune invalid prefixes)",
           """List<String> res = new ArrayList<>();

void dfs(int open, int close, int n, StringBuilder sb) {
    if (sb.length() == 2 * n) { res.add(sb.toString()); return; }
    if (open < n) {                                         // may still open
        sb.append('('); dfs(open + 1, close, n, sb); sb.deleteCharAt(sb.length() - 1);
    }
    if (close < open) {                                     // may close only if something is open
        sb.append(')'); dfs(open, close + 1, n, sb); sb.deleteCharAt(sb.length() - 1);
    }
}""",
           """def generate(n):
    res = []
    def dfs(cur, open_, close):
        if len(cur) == 2 * n:
            res.append(''.join(cur))
            return
        if open_ < n:                                       # may still open
            cur.append('('); dfs(cur, open_ + 1, close); cur.pop()
        if close < open_:                                   # may close only if something is open
            cur.append(')'); dfs(cur, open_, close + 1); cur.pop()
    dfs([], 0, 0)
    return res"""),
          ("word break with memoisation (same suffix reached repeatedly)",
           """Map<Integer, Boolean> memo = new HashMap<>();
boolean dfs(String s, int start, Set<String> dict) {
    if (start == s.length()) return true;
    if (memo.containsKey(start)) return memo.get(start);
    for (int end = start + 1; end <= s.length(); end++)
        if (dict.contains(s.substring(start, end)) && dfs(s, end, dict)) { memo.put(start, true); return true; }
    memo.put(start, false);
    return false;
}""",
           """from functools import lru_cache
words = set(wordDict)
@lru_cache(None)
def dfs(start):
    if start == len(s):
        return True
    return any(s[start:end] in words and dfs(end) for end in range(start + 1, len(s) + 1))
return dfs(0)""")],
    complexity="Generate parentheses: O(4ⁿ / √n) (Catalan growth). Memoised word break: O(n²) states × substring cost.",
    traps=["Check the constraint **before** recursing, not after.", "Memoise only when the result depends solely on the state arguments, not on the current path.",
           "Remove invalid parentheses: BFS by removals or DFS with a count of how many `(` / `)` to remove, skipping duplicates.", "Expression add operators: track the previous operand to handle `*` precedence, and skip numbers with leading zeros."],
    variants=["Remove invalid parentheses: compute the minimum removals first, then prune.", "Additive number: choose the first two numbers, then verify the rest greedily.", "Expression add operators: DFS with value and last term."],
    notuse="When subproblems overlap heavily and you only need a count or boolean: switch to bottom-up DP (topics 15–16).",
    problems=[
        (22, "Generate Parentheses", "M", "generate-parentheses", "Add '(' while open < n, ')' while close < open", "O(4ⁿ/√n) / O(n)"),
        (139, "Word Break", "M", "word-break", "Memoise on the start index (or bottom-up DP)", "O(n²) / O(n)"),
        (306, "Additive Number", "M", "additive-number", "Choose the first two numbers, check the rest", "O(n³) / O(n)"),
        (282, "Expression Add Operators", "H", "expression-add-operators", "Track value and last operand; handle * precedence", "O(4ⁿ) / O(n)"),
        (301, "Remove Invalid Parentheses", "H", "remove-invalid-parentheses", "Minimum removals then DFS, skipping duplicates", "O(2ⁿ) / O(n)"),
    ]))

TOPIC = dict(
    id="backtracking", file="07_recursion_backtracking.html", title="Recursion and Backtracking — Pattern Guide",
    lead="Backtracking is a systematic way to try every possibility while abandoning dead ends early. This guide starts with recursion itself, then covers the choose / explore / un-choose template through subsets, combinations, permutations, duplicates, string partitions, grid search, N-Queens and pruning. Each pattern has the intuition, a step-through animation of the decision tree, Java and Python code, and a ladder of LeetCode problems.",
    mindset="Backtracking is **depth-first search over a tree of decisions**: pick an option, explore everything it leads to, then undo it and pick the next. Three questions define every solution: **what is a choice**, **what makes a partial answer invalid (prune)**, and **when is it complete (record)**. Always append a *copy* of the path and always undo what you did.",
    qintro="Ask these questions before writing the recursion:",
    questions=["**What is one decision?** (pick an element, place a queen, cut the string here)", "**What state do I carry?** (path, start index, used[], remaining, visited)", "**When is the path complete?** (record a copy)",
               "**When can I abandon it early?** (prune before recursing)", "**Does order matter, and can values repeat?** → start index vs used[], sort and skip duplicates."],
    cues=[
        ["a definition in terms of a smaller copy of itself", "**P1** Recursion fundamentals"],
        ["\"all subsets\", \"include or exclude\"", "**P2** Subsets"],
        ["\"combinations\", \"combination sum\", \"choose k\"", "**P3** Combinations"],
        ["\"all permutations / arrangements\"", "**P4** Permutations"],
        ["repeated values but unique results", "**P5** Skip duplicates"],
        ["split a string into valid pieces", "**P6** String partitions"],
        ["\"word search\", path through a grid without reuse", "**P7** Grid backtracking"],
        ["\"N-Queens\", \"Sudoku\", fill a board", "**P8** Constraint search"],
        ["\"generate all valid …\", too many invalid candidates", "**P9** Pruning and memoisation"],
    ],
    choose=[
        ["Order does not matter, choose a subset", "Start-index template (P2, P3)"],
        ["Order matters, use every element", "used[] permutations (P4)"],
        ["Input has repeats, output must not", "Sort + skip (P5)"],
        ["Cut a string into valid pieces", "Try every end (P6)"],
        ["Path through cells without reuse", "Mark / un-mark DFS (P7)"],
        ["Place items under constraints", "O(1) conflict sets (P8)"],
        ["Same sub-state reached repeatedly", "Memoise → DP (P9)"],
    ],
    rule="if you can describe the answer as a **sequence of choices**, write `choose → explore → un-choose`; if the same sub-state repeats and you only need a count or a boolean, switch to **DP**.",
    selftest=[
        ("Why do we append `new ArrayList<>(path)` instead of `path` when recording a result?", "`path` is reused and mutated throughout the search; recording the same object would make every stored result end up empty or equal to the last path."),
        ("What is the difference between the subsets template and the permutations template?", "Subsets use a start index so elements are picked in increasing order (order does not matter). Permutations loop over all indices and use a `used` array because order matters."),
        ("In Combination Sum, why recurse with `i` rather than `i + 1`?", "The same candidate may be reused, so the next level may pick the same index again; `i` (not `start`) also keeps combinations in non-decreasing order."),
        ("How does `if (i > start && a[i] == a[i − 1]) continue;` prevent duplicates?", "At one level it lets only the first element of a run of equal values be chosen, so identical branches are not created; later equal values can still be used deeper."),
        ("Why is un-marking the cell essential in Word Search?", "A cell visited in a failed path must become available again for other paths. Without un-marking, valid words are missed."),
        ("Name the three conflict checks in N-Queens.", "Column, diagonal (`row − col`) and anti-diagonal (`row + col`), each in an O(1) boolean array or set."),
        ("What does pruning change about the time complexity?", "The worst case is usually unchanged, but whole subtrees are skipped, so real running time drops massively (for example only Catalan(n) parenthesis strings are visited)."),
        ("When should backtracking become dynamic programming?", "When you only need a count, a boolean or an optimum and the same sub-state is reached through many paths; cache by state (memoise) or fill a table."),
    ],
    plan=[
        "**Day 1:** recursion basics (factorial, power, reverse); then write the subsets template from memory.",
        "**Day 2:** combinations, combination sum and phone-number letters.",
        "**Day 3:** permutations (both versions), then the duplicate-handling variants.",
        "**Day 4:** string partitions (palindrome partitioning, restore IP) and word search.",
        "**Day 5:** N-Queens; then the pruning problems (generate parentheses, word break with memo).",
        "**Day 6:** redo one problem per pattern without notes; for each, state the choice, the prune and the base case aloud.",
    ],
    patterns=P,
)
