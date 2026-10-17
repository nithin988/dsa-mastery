"""Content for topic 01: Complexity and problem-solving method."""

P = []

# ---------------------------------------------------------------- 1
P.append(dict(
    title="Reading Big-O: growth rates", tier="hot", sim="pairs", oneline="count how the work grows when n doubles",
    why="Every answer in an interview ends with a complexity", signature="LC 1 (brute vs hash)",
    when="You must state, compare or improve the running time of any solution.",
    detect="\"What is the time complexity?\" · \"can you do better?\" · two solutions to compare · input size n given in the constraints.",
    intuition="Big-O answers one question: **when the input doubles, how much slower does the code get?** O(1) does not care, O(log n) adds one step, O(n) doubles, O(n²) quadruples, O(2ⁿ) squares. We drop constants and lower terms because for large n the fastest-growing term decides everything.",
    brute="A single loop is O(n). A loop inside a loop is usually O(n²). A loop that halves its range each step is O(log n). Counting loop levels is the fastest way to estimate.",
    idea="Count the number of basic operations as a function of `n`, keep the dominant term, drop constants. Sequential blocks **add** (take the max), nested blocks **multiply**.",
    steps=["Identify what `n` is (array length, string length, number of nodes). With two inputs use two variables, e.g. O(n·m).", "Count how many times the innermost statement runs.", "Sequential steps add: O(n) + O(n²) = O(n²). Nested steps multiply.", "Drop constants and lower-order terms: 3n² + 5n + 2 → O(n²).", "Decide the case you are quoting: worst, average or amortised."],
    trace_title="how the work grows (operations)",
    trace="""n          log n   n      n log n    n^2          2^n
10         3       10     33         100          1,024
1,000      10      1e3    1e4        1e6          astronomical
1,000,000  20      1e6    2e7        1e12 (hours) impossible

Order: O(1) < O(log n) < O(n) < O(n log n) < O(n^2) < O(n^3) < O(2^n) < O(n!)""",
    code=[("the five shapes you will meet most",
           """// O(1): constant
int first(int[] a) { return a[0]; }

// O(log n): range halves each step
int steps(int n) { int c = 0; while (n > 1) { n /= 2; c++; } return c; }

// O(n): one pass
int sum(int[] a) { int s = 0; for (int x : a) s += x; return s; }

// O(n log n): n times a halving loop (e.g. merge sort)
void nLogN(int n) {
    for (int i = 0; i < n; i++) for (int j = 1; j < n; j *= 2) { /* work */ }
}

// O(n^2): all pairs
void allPairs(int n) {
    for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) { /* work */ }
}""",
           """# O(1): constant
def first(a): return a[0]

# O(log n): range halves each step
def steps(n):
    c = 0
    while n > 1:
        n //= 2
        c += 1
    return c

# O(n): one pass
def total(a): return sum(a)

# O(n log n): n times a halving loop (e.g. merge sort)
for i in range(n):
    j = 1
    while j < n:
        j *= 2            # work

# O(n^2): all pairs
for i in range(n):
    for j in range(i + 1, n):
        pass              # work""")],
    complexity="This page is about the notation itself: see the table above for how fast each class grows.",
    traps=["Nested loops are not always O(n²): `for i... for j in range(i, i+3)` is O(n). Count the real iterations.",
           "Two different inputs need two variables (O(n·m)), not O(n²).",
           "O(n) time with a hidden O(n) inner call (string slice, `list.index`, `s.contains`) is really O(n²).",
           "Big-O is an upper bound on growth, not an exact count. O(n) code is also \"O(n²)\", but always quote the tightest bound."],
    variants=["Big-Omega (lower bound) and Big-Theta (tight bound): interviews almost always mean tight Big-O.", "Best, average and worst case: quicksort is O(n log n) average and O(n²) worst."],
    notuse="Big-O hides constants. For small n or equal Big-O, constant factors, cache behaviour and library speed decide; say so when it matters.",
    problems=[
        (1, "Two Sum", "E", "two-sum", "Brute force O(n²) pairs → hash map O(n): the classic complexity drop", "O(n) / O(n)"),
        (217, "Contains Duplicate", "E", "contains-duplicate", "Nested loop O(n²) vs sort O(n log n) vs set O(n)", "O(n) / O(n)"),
        (69, "Sqrt(x)", "E", "sqrtx", "Linear scan O(√x) vs binary search O(log x)", "O(log x) / O(1)"),
        (704, "Binary Search", "E", "binary-search", "Why halving gives O(log n)", "O(log n) / O(1)"),
        (49, "Group Anagrams", "M", "group-anagrams", "Cost of the key: sorting O(k log k) vs counting O(k)", "O(N·K log K) / O(N·K)"),
        (238, "Product of Array Except Self", "M", "product-of-array-except-self", "Brute O(n²) → prefix and suffix products O(n)", "O(n) / O(1) extra"),
    ]))

# ---------------------------------------------------------------- 2
P.append(dict(
    title="Constraints → target complexity", tier="hot", sim=None, oneline="read n, pick the complexity that fits",
    why="Tells you the intended algorithm before you write a line", signature="every problem",
    when="At the start of any problem, to decide which approaches are even allowed.",
    detect="the constraints section: \"1 ≤ n ≤ 10⁵\", \"n ≤ 20\", \"values up to 10⁹\".",
    intuition="A judge machine does roughly **10⁸ simple operations per second**. The constraint on n is a hint from the problem setter about which complexity class they expect. n = 20 is begging for 2ⁿ (subsets); n = 10⁵ rules out n² and wants n log n or n.",
    brute="Do the arithmetic first: if the brute force costs n² and n = 10⁵, that is 10¹⁰ operations (~100 s): too slow. That arithmetic is how you know you must optimise.",
    idea="Match `n` to the largest complexity that stays under about 10⁸ operations, then search for an algorithm in that class.",
    steps=["Read the limit on n (and on the values).", "Compute the operation count for the brute force.", "If it is under ~10⁸, brute force is acceptable; otherwise look one class lower.", "Use the table below to pick the technique family."],
    trace_title="constraint → complexity → typical technique",
    trace="""n <= 10-11        O(n!)           permutations, brute-force backtracking
n <= 20-25        O(2^n)          subsets, bitmask DP, backtracking
n <= 40           O(2^(n/2))      meet in the middle
n <= 100-500      O(n^3)          Floyd-Warshall, triple loops, interval DP
n <= 5,000        O(n^2)          2D DP, all pairs
n <= 1e5 - 2e5    O(n log n)      sorting, heap, binary search, segment tree
n <= 1e6 - 1e7    O(n)            hashing, two pointers, sliding window, prefix sum
n >= 1e9          O(log n)/O(1)   math, binary search on the answer, formula""",
    code=[],
    complexity="Rule of thumb only: ~10⁸ simple operations per second; recursion, hashing and I/O cost more per operation.",
    traps=["The value range matters too: values up to 10⁹ mean products overflow 32-bit, and a counting array of that size will not fit in memory.",
           "Sometimes n is small but the intended answer is exponential, so do not over-optimise a 2ⁿ backtracking with n = 15.",
           "If no constraints are given in an interview, ask. It is a sign of maturity, not weakness."],
    variants=["Multiple limits (n and m, or n and k): evaluate each term, e.g. O(n·k) with k ≤ 100 is fine at n = 10⁵."],
    notuse="This is a heuristic for choosing an approach, never proof that an approach is correct.",
    problems=[
        (46, "Permutations", "M", "permutations", "n ≤ 6 hints at O(n!) backtracking", "O(n·n!) / O(n)"),
        (78, "Subsets", "M", "subsets", "n ≤ 10 hints at 2ⁿ enumeration", "O(n·2ⁿ) / O(n)"),
        (322, "Coin Change", "M", "coin-change", "amount ≤ 10⁴ hints at pseudo-polynomial DP", "O(amount·coins) / O(amount)"),
        (15, "3Sum", "M", "3sum", "n ≤ 3000 allows O(n²)", "O(n²) / O(1)"),
        (215, "Kth Largest Element in an Array", "M", "kth-largest-element-in-an-array", "n ≤ 10⁵ wants O(n log n) or better", "O(n) avg / O(1)"),
        (875, "Koko Eating Bananas", "M", "koko-eating-bananas", "values up to 10⁹ hint at binary search on the answer", "O(n log max) / O(1)"),
    ]))

# ---------------------------------------------------------------- 3
P.append(dict(
    title="Amortised analysis", tier="sec", sim="amort", oneline="rare expensive steps paid for by many cheap ones",
    why="Explains why dynamic arrays, hash tables and monotonic stacks are fast", signature="LC 232 / 739",
    when="An operation is occasionally expensive but cheap on average over a sequence.",
    detect="\"dynamic array / ArrayList append\" · \"implement a queue with two stacks\" · a `while` loop inside a `for` loop where the inner loop's total work is bounded.",
    intuition="You pay a monthly gym fee, not per visit. A resize that copies n elements looks costly, but it only happens after n cheap appends, so spreading the cost over those appends gives O(1) each. The total work over many operations is what counts.",
    brute="Naïve reading: \"append can cost O(n), so n appends cost O(n²)\". The tight reading: resizes cost 1 + 2 + 4 + … + n < 2n in total, so n appends cost O(n).",
    idea="Total cost of a sequence of m operations divided by m. Use the **aggregate** method (add up total work) or the **potential** idea (cheap steps store credit for the expensive one).",
    steps=["Find the expensive step and how often it can happen.", "Show each element can cause that expensive work only a bounded number of times.", "Total work ≤ constant × (number of elements), so the average per operation is constant."],
    trace_title="doubling a dynamic array (8 appends)",
    trace="""append 1: cap 1              cost 1
append 2: full, copy 1 -> cap 2   cost 1 + 1
append 3: full, copy 2 -> cap 4   cost 1 + 2
append 4:                         cost 1
append 5: full, copy 4 -> cap 8   cost 1 + 4
append 6..8:                      cost 1 each
total = 8 writes + 7 copies = 15  (< 2 per append)""",
    code=[("dynamic array append (amortised O(1))",
           """void add(int x) {
    if (size == data.length)
        data = Arrays.copyOf(data, 2 * data.length);   // rare O(n) copy
    data[size++] = x;                                  // common O(1) write
}""",
           """def add(self, x):
    if self.size == len(self.data):
        self.data.extend([None] * len(self.data))      # rare O(n) copy
    self.data[self.size] = x                           # common O(1) write
    self.size += 1""")],
    complexity="Dynamic array append: O(1) amortised, O(n) worst single call. Hash table insert: O(1) amortised.",
    traps=["Amortised is not average-case: it is a guarantee over any sequence of operations, with no randomness involved.",
           "A single operation can still be slow, which matters for real-time systems.",
           "`while` inside `for` is not automatically O(n²). If the inner loop's pointer only moves forward overall (monotonic stack, sliding window), the total is O(n)."],
    variants=["Queue via two stacks: each element is moved at most once, so pop is O(1) amortised.", "Monotonic stack: each element is pushed and popped at most once."],
    notuse="When you need a hard worst-case bound per operation (use a structure with worst-case guarantees).",
    problems=[
        (232, "Implement Queue using Stacks", "E", "implement-queue-using-stacks", "Move elements stack-to-stack only when the output stack is empty", "O(1) amortised / O(n)"),
        (3, "Longest Substring Without Repeating Characters", "M", "longest-substring-without-repeating-characters", "Inner while looks nested, but l only moves forward: O(n)", "O(n) / O(σ)"),
        (739, "Daily Temperatures", "M", "daily-temperatures", "Monotonic stack: every index pushed and popped once", "O(n) / O(n)"),
        (155, "Min Stack", "M", "min-stack", "O(1) per operation by storing the running minimum", "O(1) / O(n)"),
        (84, "Largest Rectangle in Histogram", "H", "largest-rectangle-in-histogram", "Monotonic stack, amortised O(1) per bar", "O(n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 4
P.append(dict(
    title="Space complexity and the recursion stack", tier="hot", sim=None, oneline="count extra memory, including call-stack depth",
    why="Interviewers always follow \"time?\" with \"and space?\"", signature="LC 509 / 70",
    when="You must state memory use, or you are choosing between recursion and iteration.",
    detect="\"in place\" · \"O(1) extra space\" · deep recursion · memoisation tables.",
    intuition="Time is how long you work; space is how much desk you need. Each recursive call that has not yet returned keeps a **stack frame** on the desk, so a recursion n levels deep uses O(n) space even if it allocates nothing else.",
    brute="Naïve Fibonacci recursion has O(2ⁿ) time. Adding a memo makes it O(n) time and O(n) space. Keeping only the last two values makes it O(n) time and O(1) space.",
    idea="Space = extra memory your algorithm allocates **beyond the input** (auxiliary space), plus recursion depth. Input size is usually not counted unless stated.",
    steps=["Add up data structures you create (arrays, maps, copies).", "Add the maximum depth of the recursion stack.", "Take the dominant term.", "Ask whether the extra memory can be reused or dropped (rolling array, two variables)."],
    trace_title="three ways to compute Fibonacci",
    trace="""naive recursion   time O(2^n)   space O(n)  (stack depth)
memoised          time O(n)     space O(n)  (table + stack)
bottom-up, 2 vars time O(n)     space O(1)""",
    code=[("Fibonacci: time and space trade-offs",
           """int fibNaive(int n) { return n < 2 ? n : fibNaive(n - 1) + fibNaive(n - 2); }   // O(2^n), O(n) stack

int fibMemo(int n, int[] memo) {                                                  // O(n), O(n)
    if (n < 2) return n;
    if (memo[n] != 0) return memo[n];
    return memo[n] = fibMemo(n - 1, memo) + fibMemo(n - 2, memo);
}

int fib(int n) {                                                                  // O(n), O(1)
    int a = 0, b = 1;
    for (int i = 0; i < n; i++) { int t = a + b; a = b; b = t; }
    return a;
}""",
           """def fib_naive(n):                       # O(2^n) time, O(n) stack
    return n if n < 2 else fib_naive(n - 1) + fib_naive(n - 2)

from functools import lru_cache
@lru_cache(None)
def fib_memo(n):                        # O(n) time, O(n) space
    return n if n < 2 else fib_memo(n - 1) + fib_memo(n - 2)

def fib(n):                             # O(n) time, O(1) space
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a""")],
    complexity="Recursion: space = depth of the call stack (n for a linear chain, log n for a balanced halving, tree height for DFS on a tree).",
    traps=["Recursion depth counts as space: DFS on a skewed tree of 10⁵ nodes is O(n) stack and can overflow in Java or hit Python's default limit (about 1000).",
           "Slicing in Python (`a[1:]`) or `substring` in Java copies, adding hidden O(n) space and time per call.",
           "\"In place\" means O(1) extra space, not zero: a few variables are fine."],
    variants=["Rolling array: DP over rows only needs the previous row, O(n·m) → O(m).", "Tail recursion is not optimised in Java or Python: convert to a loop when depth is large."],
    notuse="When memory is plentiful and clarity matters more, a memo table is fine; just state the cost.",
    problems=[
        (509, "Fibonacci Number", "E", "fibonacci-number", "Naive → memo → two variables", "O(n) / O(1)"),
        (70, "Climbing Stairs", "E", "climbing-stairs", "Same recurrence as Fibonacci; rolling variables", "O(n) / O(1)"),
        (136, "Single Number", "E", "single-number", "XOR cancels pairs: O(1) space instead of a set", "O(n) / O(1)"),
        (50, "Pow(x, n)", "M", "powx-n", "Fast exponentiation: depth log n instead of n", "O(log n) / O(log n) or O(1)"),
        (198, "House Robber", "M", "house-robber", "DP needs only the previous two states", "O(n) / O(1)"),
        (62, "Unique Paths", "M", "unique-paths", "2D table shrinks to a single rolling row", "O(mn) / O(n)"),
    ]))

# ---------------------------------------------------------------- 5
P.append(dict(
    title="Recurrences and divide and conquer", tier="sec", sim=None, oneline="write T(n) from the structure, then solve it",
    why="Gives the complexity of every recursive algorithm", signature="LC 912 / 50",
    when="A function calls itself on smaller inputs and you need its running time.",
    detect="\"divide and conquer\" · merge sort / quicksort · binary search · tree recursion · fast power.",
    intuition="Draw the recursion as a tree. Cost per level × number of levels = total. Merge sort: each level does n work and there are log n levels → n log n. Binary search: each level does 1 unit and there are log n levels → log n.",
    brute="Instead of guessing, write the recurrence: `T(n) = a·T(n/b) + f(n)`: `a` sub-problems, each of size n/b, plus f(n) work to split and combine.",
    idea="Compare the work at the root `f(n)` with the work at the leaves `n^(log_b a)`. Whichever dominates decides the answer; if they tie you multiply by log n.",
    steps=["Write `T(n) = a·T(n/b) + O(n^d)`.", "Compute `log_b a`.", "If `d < log_b a` → O(n^(log_b a)) (leaves dominate).", "If `d == log_b a` → O(n^d · log n) (every level equal).", "If `d > log_b a` → O(n^d) (root dominates)."],
    trace_title="recurrence cheat sheet",
    trace="""T(n) = T(n/2) + O(1)      O(log n)     binary search
T(n) = T(n/2) + O(n)      O(n)         quick select (average)
T(n) = 2T(n/2) + O(1)     O(n)         visit every node of a balanced tree
T(n) = 2T(n/2) + O(n)     O(n log n)   merge sort
T(n) = T(n-1) + O(1)      O(n)         linear recursion
T(n) = T(n-1) + O(n)      O(n^2)       quicksort worst case, insertion sort
T(n) = 2T(n-1) + O(1)     O(2^n)       naive Fibonacci, subsets""",
    code=[("fast power: T(n) = T(n/2) + O(1) = O(log n)",
           """double pow(double x, long n) {
    if (n == 0) return 1;
    if (n < 0) return 1 / pow(x, -n);
    double half = pow(x, n / 2);
    return n % 2 == 0 ? half * half : half * half * x;
}""",
           """def power(x, n):
    if n == 0:
        return 1.0
    if n < 0:
        return 1 / power(x, -n)
    half = power(x, n // 2)
    return half * half if n % 2 == 0 else half * half * x""")],
    complexity="Fast power: O(log n) time and O(log n) stack. Merge sort: O(n log n) time, O(n) space.",
    traps=["Computing `pow(x, n/2)` **twice** instead of once turns O(log n) into O(n).", "In Java negate n as `long`: `-Integer.MIN_VALUE` overflows.",
           "Recurrences with unequal splits (T(n−1) + T(1)) are not solved by the master theorem: draw the tree."],
    variants=["Akra–Bazzi / unbalanced splits: sum the levels of the recursion tree instead.", "Divide and conquer on arrays: max subarray, count inversions, closest pair."],
    notuse="If sub-problems overlap heavily, use dynamic programming rather than plain divide and conquer.",
    problems=[
        (50, "Pow(x, n)", "M", "powx-n", "Halve the exponent each step", "O(log n) / O(log n)"),
        (169, "Majority Element", "E", "majority-element", "Divide and conquer version: T(n) = 2T(n/2) + O(n)", "O(n log n) / O(log n)"),
        (912, "Sort an Array", "M", "sort-an-array", "Merge sort: 2T(n/2) + O(n)", "O(n log n) / O(n)"),
        (53, "Maximum Subarray", "M", "maximum-subarray", "Divide and conquer: best in left, right or crossing the middle", "O(n log n) / O(log n)"),
        (240, "Search a 2D Matrix II", "M", "search-a-2d-matrix-ii", "Eliminate a row or column each step", "O(m + n) / O(1)"),
        (4, "Median of Two Sorted Arrays", "H", "median-of-two-sorted-arrays", "Discard half of the smaller array each step", "O(log min(m,n)) / O(1)"),
    ]))

# ---------------------------------------------------------------- 6
P.append(dict(
    title="From brute force to optimal", tier="hot", sim=None, oneline="find the repeated work, then remove it",
    why="The core interview skill: improve a working solution", signature="LC 1 / 121",
    when="You have a correct but slow solution and need a faster one.",
    detect="\"can you optimise it?\" · nested loops · repeated scans · recomputing the same value.",
    intuition="A slow solution is slow because it **repeats work** or **looks at things it can rule out**. Find the bottleneck line, ask \"what do I recompute here?\" and swap in a structure that remembers or orders the data.",
    brute="Always start with the obvious brute force. It proves you understand the problem, gives a correct baseline to test against, and its bottleneck shows where to improve.",
    idea="Name the bottleneck, then apply the toolbox: **sort**, **hash**, **two pointers**, **sliding window**, **prefix sum**, **binary search**, **heap**, **memoise**, **precompute**, **greedy**, **bit trick**.",
    steps=["Write the brute force and its complexity.", "Underline the slowest part (usually a search or a recomputation).", "Ask: can sorting make the search faster? Can a hash map make it O(1)? Can I carry a running value instead of recomputing?", "State the new complexity and what you traded (time ↔ space).", "Check correctness on the edge cases again."],
    trace_title="Two Sum: three levels of the same problem",
    trace="""brute force      two loops over all pairs           O(n^2) time, O(1) space
sort + 2 ptrs    sort, then move l and r inward     O(n log n) time, O(1) space (loses indices)
hash map         remember seen values, look up      O(n) time, O(n) space""",
    code=[("Two Sum, brute force then hash map",
           """// brute force: O(n^2)
for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
        if (a[i] + a[j] == target) return new int[]{i, j};

// hash map: O(n)
Map<Integer, Integer> seen = new HashMap<>();
for (int i = 0; i < n; i++) {
    Integer j = seen.get(target - a[i]);
    if (j != null) return new int[]{j, i};
    seen.put(a[i], i);
}""",
           """# brute force: O(n^2)
for i in range(len(a)):
    for j in range(i + 1, len(a)):
        if a[i] + a[j] == target:
            return [i, j]

# hash map: O(n)
seen = {}
for i, x in enumerate(a):
    if target - x in seen:
        return [seen[target - x], i]
    seen[x] = i""")],
    complexity="Most optimisations trade space for time (hash map) or pay O(n log n) once to unlock faster steps (sort).",
    traps=["Jumping straight to a clever solution without stating the brute force: say it first, even in one sentence.", "Optimising the wrong line: measure which part dominates.",
           "Sorting destroys original indices; if you need them, keep pairs `(value, index)`."],
    variants=["Tool for \"best over all subarrays\": prefix sum, sliding window, Kadane.", "Tool for \"has x been seen\": hash set.", "Tool for \"smallest / largest k\": heap or quick select.", "Tool for \"overlapping sub-problems\": memoisation → DP."],
    notuse="When n is tiny, the brute force is the right answer: do not over-engineer.",
    problems=[
        (1, "Two Sum", "E", "two-sum", "O(n²) pairs → O(n) hash map", "O(n) / O(n)"),
        (217, "Contains Duplicate", "E", "contains-duplicate", "Nested loops → sort → set", "O(n) / O(n)"),
        (242, "Valid Anagram", "E", "valid-anagram", "Sort both strings O(n log n) → count letters O(n)", "O(n) / O(1)"),
        (121, "Best Time to Buy and Sell Stock", "E", "best-time-to-buy-and-sell-stock", "All (buy, sell) pairs → carry the minimum so far", "O(n) / O(1)"),
        (169, "Majority Element", "E", "majority-element", "Count map → sort → Boyer–Moore voting", "O(n) / O(1)"),
        (53, "Maximum Subarray", "M", "maximum-subarray", "All subarrays O(n²) → Kadane O(n)", "O(n) / O(1)"),
        (560, "Subarray Sum Equals K", "M", "subarray-sum-equals-k", "All subarrays → prefix sums + hash map", "O(n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 7
P.append(dict(
    title="A repeatable problem-solving method", tier="hot", sim=None, oneline="clarify, example, brute force, optimise, code, test",
    why="Structure beats inspiration under interview pressure", signature="every interview",
    when="Every problem, especially one you have not seen before.",
    detect="a blank page, an unfamiliar problem, or the urge to start coding immediately.",
    intuition="Interviewers grade **how you think** as much as the final code. A fixed routine keeps you calm, shows structure, and catches misunderstandings before they cost 20 minutes.",
    brute=None,
    idea="Follow the same eight steps every time. Talk through each out loud.",
    steps=["**Restate** the problem in your own words and confirm the input and output.", "**Clarify** constraints: size of n, value ranges, duplicates, negatives, sorted?, empty input, what to return when no answer.",
           "**Examples:** work a small example by hand, then an edge case.", "**Brute force:** describe it and its complexity.", "**Optimise:** find the bottleneck, name the pattern, state the new complexity.",
           "**Code** cleanly with meaningful names, narrating as you go.", "**Test:** dry-run your own example and the edge cases line by line.", "**Complexity:** state time and space, and mention trade-offs or follow-ups."],
    trace_title="a short spoken walk-through (Two Sum)",
    trace="""\"So given an array and a target I return the indices of two numbers adding to it.
 Can there be duplicates or negatives? Exactly one answer? Is the array sorted?\"
\"Example [2,7,11,15], target 9 gives [0,1]. Edge case: [3,3], target 6.\"
\"Brute force checks every pair: O(n^2) time, O(1) space.\"
\"The bottleneck is searching for the partner. A hash map gives O(1) lookup:
 for each x look for target-x, then store x. O(n) time, O(n) space.\"
[code, then dry-run [3,3]] \"Complexity O(n)/O(n); if memory mattered and the array
 were sorted I would use two pointers for O(1) space.\"""",
    code=[],
    complexity="Not applicable: this is a process. Time-box: ~5 min understand, ~10 min approach, ~15 min code, ~5 min test.",
    traps=["Silence: narrate your thinking even when stuck; interviewers can only help if they hear it.", "Coding before agreeing on the approach.",
           "Skipping the dry run: most bugs (off-by-one, empty input) are caught here.", "Not knowing when to stop optimising: if an interviewer says \"good\", move on to testing."],
    variants=["Stuck? Try a smaller input, draw it, solve it by hand, then generalise.", "Still stuck? Ask what pattern family it belongs to: window, pointers, hashing, DP, graph.", "Hint received? Say thanks and build on it; do not pretend you knew."],
    notuse="Never skip it; scale it down for easy problems.",
    problems=[
        (1, "Two Sum", "E", "two-sum", "Practise the full eight-step routine on the simplest problem", "O(n) / O(n)"),
        (20, "Valid Parentheses", "E", "valid-parentheses", "Clarify: other characters? empty string? Then stack", "O(n) / O(n)"),
        (14, "Longest Common Prefix", "E", "longest-common-prefix", "Brute force vs vertical scan vs sorting; compare aloud", "O(S) / O(1)"),
        (125, "Valid Palindrome", "E", "valid-palindrome", "Clarify casing and punctuation before coding", "O(n) / O(1)"),
        (11, "Container With Most Water", "M", "container-with-most-water", "State brute force, then justify moving the shorter wall", "O(n) / O(1)"),
        (3, "Longest Substring Without Repeating Characters", "M", "longest-substring-without-repeating-characters", "Build from brute force to window by explaining each pointer move", "O(n) / O(σ)"),
    ]))

# ---------------------------------------------------------------- 8
P.append(dict(
    title="Edge cases, overflow and dry-running", tier="hot", sim=None, oneline="test the boundaries before the interviewer does",
    why="Off-by-one and overflow bugs fail otherwise-correct solutions", signature="LC 7 / 8",
    when="Before you say \"done\" on any solution.",
    detect="integer arithmetic · array indexing · loops with boundaries · \"return -1 / empty if…\".",
    intuition="Most wrong answers are right algorithms that fail on the boundary: nothing in the input, one thing, everything the same, the biggest number. A thirty-second checklist and a line-by-line dry run catch nearly all of them.",
    brute=None,
    idea="Run the code by hand on small inputs, tracking variables in a table, and always include the checklist cases.",
    steps=["Empty input / `n = 0`.", "Single element, and exactly two elements.", "All elements equal; all distinct.", "Already sorted, reverse sorted.", "Negative numbers, zeros, very large values (overflow).", "Target at the first or last position, or absent.", "Dry-run: write each variable per iteration in a small table."],
    trace_title="dry-run table for Kadane on `[-2, 1, -3]`",
    trace="""i   a[i]   cur          best
0   -2     -2           -2     (start from a[0], not 0)
1    1     max(1,-1)=1   1
2   -3     max(-3,-2)=-2 1
=> 1""",
    code=[("integer overflow in Java (Python ints do not overflow)",
           """int mid = (lo + hi) / 2;            // BUG: lo + hi can overflow int
int mid = lo + (hi - lo) / 2;        // safe

long prod = (long) a * b;            // widen BEFORE multiplying
int safe = Math.addExact(x, y);      // throws instead of wrapping

// reverse integer: check before multiplying by 10
if (rev > Integer.MAX_VALUE / 10 || rev < Integer.MIN_VALUE / 10) return 0;""",
           """# Python ints are arbitrary precision: no overflow,
# but if the problem says 32-bit you must check manually:
if not -2**31 <= result <= 2**31 - 1:
    return 0

mid = lo + (hi - lo) // 2     # same habit; // is floor division
# note: -7 // 2 == -4 in Python but -7 / 2 == -3 in Java""")],
    complexity="Not applicable: a correctness habit.",
    traps=["Java integer division truncates toward zero; Python `//` floors. They differ for negatives.", "`Math.abs(Integer.MIN_VALUE)` is still negative.",
           "Using `<=` vs `<` in loop bounds; check the first and last iteration by hand.", "Mutating a collection while iterating it.", "Returning the wrong value type for \"not found\" (−1 vs empty list vs null)."],
    variants=["Also test the largest allowed n for time and the largest values for overflow.", "Random testing: compare the optimised solution with the brute force on small random inputs."],
    notuse="There is no case where skipping testing is wise.",
    problems=[
        (66, "Plus One", "E", "plus-one", "Carry through trailing 9s; all-9s grows the array", "O(n) / O(1)"),
        (9, "Palindrome Number", "E", "palindrome-number", "Negatives and trailing zeros; reverse half to avoid overflow", "O(log n) / O(1)"),
        (415, "Add Strings", "E", "add-strings", "Different lengths and a final carry", "O(max(m,n)) / O(max(m,n))"),
        (7, "Reverse Integer", "M", "reverse-integer", "Check overflow before multiplying by 10", "O(log n) / O(1)"),
        (8, "String to Integer (atoi)", "M", "string-to-integer-atoi", "Whitespace, sign, non-digit stop, clamp on overflow", "O(n) / O(1)"),
        (69, "Sqrt(x)", "E", "sqrtx", "mid * mid overflows int: use long or divide", "O(log x) / O(1)"),
    ]))

# ---------------------------------------------------------------- 9
P.append(dict(
    title="Hidden costs in Java and Python", tier="hot", sim=None, oneline="know what the library calls really cost",
    why="An innocent-looking call can turn O(n) into O(n²)", signature="LC 14 / 151",
    when="Any time a loop contains a library call: slicing, `contains`, `remove(0)`, `+=` on strings.",
    detect="string building in a loop · `list.remove` / `insert(0, …)` · `x in list` · `substring` inside loops.",
    intuition="Complexity analysis counts the cost of every line, and library calls are lines. `s += c` looks like one step, but strings are immutable, so each `+=` copies the whole string: n of them cost O(n²).",
    brute=None,
    idea="Memorise the cost of the handful of operations you use constantly, and choose the structure whose fast operations match what your loop does.",
    steps=["List the library calls inside your loops.", "Look each one up in the table below.", "Replace expensive ones: `StringBuilder` / `''.join`, `ArrayDeque` / `deque`, `HashSet` / `set`, indexes instead of slices."],
    trace_title="cost cheat sheet",
    trace="""JAVA
String +=  in a loop            O(n^2) total     -> StringBuilder.append  O(1) amortised
s.substring(i, j)               O(j - i)         copies
s.contains / indexOf            O(n*m) worst
ArrayList.add(x)                O(1) amortised   add(0, x) / remove(0): O(n)
LinkedList.get(i)               O(n)             (no random access)
HashMap get/put                 O(1) expected    treeified buckets O(log n) worst
ArrayDeque offer/poll           O(1)             use instead of Stack / LinkedList
PriorityQueue offer/poll        O(log n)         peek O(1), remove(obj) O(n)
Arrays.sort / Collections.sort  O(n log n)

PYTHON
s += c  in a loop               O(n^2) possible  -> ''.join(parts)
a[i:j] slice                    O(j - i)         copies
x in list / list.index          O(n)             x in set / dict: O(1) expected
list.append / pop()             O(1) amortised   insert(0, x) / pop(0): O(n) -> collections.deque
sorted / list.sort              O(n log n)       (Timsort)
heapq.heappush / heappop        O(log n)
len, indexing, dict get/set     O(1)""",
    code=[("building a string in a loop",
           """// O(n^2): copies the string every iteration
String s = "";
for (char c : chars) s += c;

// O(n): one growing buffer
StringBuilder sb = new StringBuilder();
for (char c : chars) sb.append(c);
String s2 = sb.toString();""",
           """# can be O(n^2): may copy each time
s = ""
for c in chars:
    s += c

# O(n): collect then join once
s2 = "".join(chars)""")],
    complexity="Always quote the cost including library calls: a \"loop of n with a substring\" is O(n²), not O(n).",
    traps=["`Stack` in Java is synchronised and legacy: use `ArrayDeque`.", "`list.pop(0)` on a Python list is O(n): use `deque.popleft()`.",
           "`in` on a list inside a loop is O(n²) overall; convert to a set first.", "Passing slices to recursive calls copies each time: pass indices instead."],
    variants=["Immutable vs mutable: strings are immutable in both languages; convert to a char array or list to edit in place.", "Sorting cost depends on comparator cost: sorting n strings of length k is O(n·k log n)."],
    notuse="Micro-optimising when n is small: clarity first, then fix the costly call if the complexity requires it.",
    problems=[
        (14, "Longest Common Prefix", "E", "longest-common-prefix", "Avoid creating substrings in the loop; compare characters by index", "O(S) / O(1)"),
        (67, "Add Binary", "E", "add-binary", "Build with StringBuilder / list and reverse once", "O(max(m,n)) / O(max(m,n))"),
        (28, "Find the Index of the First Occurrence in a String", "E", "find-the-index-of-the-first-occurrence-in-a-string", "Know the cost of naive search O(n·m) before KMP", "O(n·m) naive / O(1)"),
        (443, "String Compression", "M", "string-compression", "In-place write pointer avoids building new strings", "O(n) / O(1)"),
        (151, "Reverse Words in a String", "M", "reverse-words-in-a-string", "Split and join once; avoid repeated concatenation", "O(n) / O(n)"),
        (49, "Group Anagrams", "M", "group-anagrams", "Cost of the grouping key: sort vs count", "O(N·K log K) / O(N·K)"),
    ]))

TOPIC = dict(
    id="foundations", file="01_complexity_foundations.html", title="Complexity and Problem-Solving Method — Foundations",
    unit="Concept", units_heading="The concepts",
    lead="Everything else in this series rests on this page: how to measure a solution, how to read the constraints, how to go from brute force to optimal, and how to run an interview problem from start to finish. Each concept has the intuition, a worked example, code in Java and Python, traps, and practice problems that exercise exactly that skill.",
    mindset="Algorithms are only useful if you can **judge** them. Before any technique, you need three habits: estimate the cost of a solution, use the constraints to decide how fast it must be, and follow a fixed routine so you never freeze on an unfamiliar problem. Nine short concepts cover this.",
    qintro="Ask these questions on every problem, before writing code:",
    questions=["**How big can n get?** → decides the target complexity.", "**What is my brute force and what does it cost?** → gives a baseline and exposes the bottleneck.",
               "**What work is repeated or can be ruled out?** → points to hashing, sorting, a window, a prefix or a heap.", "**What are the edge cases and the value ranges?** → empty input, duplicates, negatives, overflow."],
    cues=[
        ["\"what is the time complexity?\", comparing two solutions", "**C1** Reading Big-O"],
        ["\"1 ≤ n ≤ 10⁵\", \"n ≤ 20\", values up to 10⁹", "**C2** Constraints → complexity"],
        ["a loop inside a loop that is not really n²; ArrayList or hash table cost", "**C3** Amortised analysis"],
        ["\"O(1) extra space\", deep recursion, memo tables", "**C4** Space and the recursion stack"],
        ["a function that calls itself on half the input", "**C5** Recurrences and divide and conquer"],
        ["\"can you do better?\"", "**C6** Brute force to optimal"],
        ["an unfamiliar problem and a blank page", "**C7** Problem-solving method"],
        ["integer arithmetic, boundaries, \"it passes the sample but fails hidden tests\"", "**C8** Edge cases and overflow"],
        ["string building in a loop, `remove(0)`, `x in list`", "**C9** Hidden costs"],
    ],
    choose=[
        ["Decide which algorithm is even allowed", "Constraints → complexity (C2)"],
        ["State how fast your code is", "Big-O (C1), amortised (C3), recurrences (C5)"],
        ["State how much memory it uses", "Space and recursion stack (C4)"],
        ["Improve a working solution", "Brute force to optimal (C6)"],
        ["Run the whole interview", "Method (C7)"],
        ["Make sure it actually works", "Edge cases (C8) and hidden costs (C9)"],
    ],
    rule="before writing any code, compute `n` × brute-force cost. If it is over ~10⁸, you have just been told that the interviewer expects a better pattern.",
    selftest=[
        ("A loop runs `for i in 0..n: for j in i..n`. What is the complexity and why?", "O(n²). The inner loop runs n−i times, so the total is n + (n−1) + … + 1 = n(n+1)/2, which is O(n²)."),
        ("n = 10⁵. Can an O(n²) solution pass? What should you aim for?", "No: n² = 10¹⁰ operations, about 100 seconds at 10⁸ per second. Aim for O(n log n) or O(n)."),
        ("Why is appending to a dynamic array O(1) amortised even though resizing is O(n)?", "Resizes happen at sizes 1, 2, 4, 8, …, so the total copy cost is less than 2n over n appends, an average of under 2 units per append."),
        ("What is the space complexity of a recursive DFS on a path-shaped tree with n nodes?", "O(n): the recursion stack holds n frames at the deepest point."),
        ("Solve T(n) = 2T(n/2) + O(n).", "a = 2, b = 2, d = 1, log_b a = 1 = d, so every level costs the same: O(n log n). This is merge sort."),
        ("Why can `s += c` in a loop be O(n²)?", "Strings are immutable, so each concatenation copies the existing string; the copies total 1 + 2 + … + n."),
        ("What is the first thing to say after reading a new problem?", "Restate it, then clarify constraints, inputs and edge cases before proposing any approach."),
        ("Why can `mid = (lo + hi) / 2` be a bug in Java?", "`lo + hi` can exceed `Integer.MAX_VALUE` and wrap negative. Use `lo + (hi − lo) / 2`."),
    ],
    plan=[
        "**Day 1:** read concepts 1–2 and do the first three problems of each ladder; say the complexity aloud before you code.",
        "**Day 2:** concepts 3–5; derive each recurrence yourself on paper using the tree method.",
        "**Day 3:** concept 6; take five easy problems and write brute force, then the optimised version, noting the complexity drop.",
        "**Day 4:** concepts 7–9; do two problems **out loud** as if in an interview, with the eight-step routine and a dry run.",
        "**Ongoing:** after every problem in the later topics, write one line: constraint → complexity → pattern.",
    ],
    patterns=P,
)
