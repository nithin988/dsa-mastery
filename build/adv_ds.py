"""Content for topic 17: advanced data structures (Fenwick, segment trees, sparse table, LCA, ordered sets, offline queries)."""

P = []

# ---------------------------------------------------------------- 1
P.append(dict(
    title="Fenwick tree (binary indexed tree)", tier="hot", sim="bit", oneline="prefix sums with point updates, both in O(log n), in ten lines",
    why="The shortest structure that makes updates and range queries both fast", signature="LC 307 / 315",
    when="An array changes by point updates and you also need prefix or range sums (or counts) many times.",
    detect="\"range sum query mutable\" · \"number of elements less than x so far\" · \"count pairs with a condition while sweeping\" · \"queries on a permutation\".",
    intuition="Two simple structures each fail: a plain array updates in O(1) but a query costs O(n); a prefix-sum array queries in O(1) but one update costs O(n). The Fenwick tree stores **partial sums over blocks whose sizes are powers of two**. Cell `i` stores the sum of the last `lowbit(i)` elements ending at `i` (`lowbit(i) = i & −i`). A prefix query adds O(log n) blocks by stripping the lowest set bit; an update touches the O(log n) blocks that contain the position by adding the lowest set bit.",
    brute="Recomputing a prefix each time is O(n) per query; a prefix-sum array makes each update O(n). The Fenwick tree makes both O(log n).",
    idea="1-indexed array `t`. `add(i, v)`: `for (; i <= n; i += i & −i) t[i] += v`. `prefix(i)`: `for (; i > 0; i −= i & −i) s += t[i]`. `range(l, r) = prefix(r) − prefix(l − 1)`. Build in O(n) by pushing each finished cell into its parent `i + lowbit(i)`.",
    steps=["Allocate `t` of size `n + 1` (index 0 is unused).", "To change position `i` by `v`, climb with `i += i & −i`.", "To get the sum of the first `i`, descend with `i −= i & −i`.", "Range sum is the difference of two prefixes."],
    trace_title="`a = [3, 2, −1, 6, 5, 4, −3, 3]`, `prefix(7)`",
    trace="""i = 7 (111): add BIT[7]  = -3   -> sum -3     i -= 1 -> 6
i = 6 (110): add BIT[6]  =  9   -> sum  6     i -= 2 -> 4
i = 4 (100): add BIT[4]  = 10   -> sum 16     i -= 4 -> 0
prefix(7) = 16 = 3 + 2 - 1 + 6 + 5 + 4 - 3""",
    code=[("Fenwick tree with point update and prefix / range sum (0-indexed API)",
           """class FenwickTree {
    private final int n;
    private final long[] t;
    FenwickTree(int n) { this.n = n; t = new long[n + 1]; }
    void add(int i, long delta) {                                  // a[i] += delta
        for (i++; i <= n; i += i & -i) t[i] += delta;              // climb to every block containing i
    }
    long prefix(int i) {                                           // sum of a[0..i]
        long s = 0;
        for (i++; i > 0; i -= i & -i) s += t[i];                   // strip the lowest set bit
        return s;
    }
    long range(int l, int r) { return prefix(r) - (l > 0 ? prefix(l - 1) : 0); }
}""",
           """class FenwickTree:
    def __init__(self, n):
        self.n = n
        self.t = [0] * (n + 1)

    def add(self, i, delta):                                       # a[i] += delta
        i += 1
        while i <= self.n:
            self.t[i] += delta
            i += i & -i                                            # climb to every block containing i

    def prefix(self, i):                                           # sum of a[0..i]
        s, i = 0, i + 1
        while i > 0:
            s += self.t[i]
            i -= i & -i                                            # strip the lowest set bit
        return s

    def range(self, l, r):
        return self.prefix(r) - (self.prefix(l - 1) if l > 0 else 0)"""),
          ("O(n) build and k-th smallest by binary descent (counts in the tree)",
           """long[] buildFenwick(int[] a) {                                  // O(n) instead of n updates
    int n = a.length;
    long[] t = new long[n + 1];
    for (int i = 1; i <= n; i++) {
        t[i] += a[i - 1];
        int parent = i + (i & -i);
        if (parent <= n) t[parent] += t[i];                        // push the finished cell into its parent
    }
    return t;
}
int kthSmallest(long[] t, int n, long k) {                         // smallest index whose prefix count is >= k (1-indexed)
    int pos = 0;
    for (int step = Integer.highestOneBit(n); step > 0; step >>= 1)
        if (pos + step <= n && t[pos + step] < k) { pos += step; k -= t[pos]; }
    return pos + 1;
}""",
           """def build_fenwick(a):                                              # O(n) instead of n updates
    n = len(a)
    t = [0] * (n + 1)
    for i in range(1, n + 1):
        t[i] += a[i - 1]
        parent = i + (i & -i)
        if parent <= n:
            t[parent] += t[i]                                      # push the finished cell into its parent
    return t

def kth_smallest(t, n, k):                                         # smallest index whose prefix count is >= k (1-indexed)
    pos, step = 0, 1 << (n.bit_length() - 1)
    while step:
        if pos + step <= n and t[pos + step] < k:
            pos += step
            k -= t[pos]
        step >>= 1
    return pos + 1""")],
    complexity="O(log n) per update and query, O(n) space, O(n) build.",
    traps=["The tree is **1-indexed** internally (index 0 would loop forever); keep a 0-indexed public API like the code does.", "Use `long` for sums.",
           "A Fenwick tree needs an invertible operation (sum, xor, count) for ranges; for range min / max use a segment tree.", "To \"set\" a value, add the difference `new − old` (keep a copy of the array)."],
    variants=["Range update + point query: store differences in the tree.", "Range update + range query: two Fenwick trees.", "2D Fenwick tree: nested loops over both indices.", "Counting inversions / smaller-after-self: Fenwick over compressed values (P5)."],
    notuse="Range min / max, or non-invertible operations (use a segment tree / sparse table); or a static array with only queries (prefix sums are simpler).",
    problems=[
        (307, "Range Sum Query - Mutable", "M", "range-sum-query-mutable", "Fenwick tree with add(difference) and prefix queries", "O(log n) / O(n)"),
        (1409, "Queries on a Permutation With Key", "M", "queries-on-a-permutation-with-key", "Positions in a Fenwick tree; move an element to the front", "O((n+q) log n) / O(n+q)"),
        (2426, "Number of Pairs Satisfying Inequality", "H", "number-of-pairs-satisfying-inequality", "Rewrite as a[i]−b[i] ≤ a[j]−b[j]+d; count with a Fenwick tree", "O(n log n) / O(n)"),
        (2179, "Count Good Triplets in an Array", "H", "count-good-triplets-in-an-array", "For every middle element count smaller-left × larger-right with a BIT", "O(n log n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 2
P.append(dict(
    title="Segment tree: range queries with updates", tier="hot", sim="seg", oneline="every node stores the answer for its segment; combine two children",
    why="The general tool for any associative range query with point updates", signature="LC 307 / 699 / 2407",
    when="You need range sum / min / max / gcd with point updates, or you must search for the first position satisfying a condition.",
    detect="\"range minimum with updates\" · \"first index with value ≥ x in a range\" · \"falling squares\" · \"LIS with value difference constraint\" · \"online majority element\".",
    intuition="Split the array in half again and again; each tree node stores the answer for its segment, and a parent's answer is the combination of its two children's answers. A query for `[l, r]` visits nodes top-down: a node completely **outside** contributes nothing, a node completely **inside** contributes its stored answer and we stop, and a node that **overlaps partly** recurses into both children. At most two nodes per level are partial, so the query visits O(log n) nodes.",
    brute="A loop over the range costs O(n) per query; with updates a prefix array costs O(n) per update. The tree costs O(log n) for both.",
    idea="Iterative layout: leaves at `n..2n−1`, parent of `i` is `i >> 1`. Build: `t[i] = t[2i] + t[2i+1]`. Update: set the leaf, then recompute ancestors. Query `[l, r]`: shift both ends in; add `t[l++]` when `l` is a right child and `t[--r]` when `r` is a right bound. Replace `+` with `min`, `max`, `gcd` or `xor` for other queries.",
    steps=["Store the elements in the leaves and combine upward.", "Update: change the leaf, walk to the root recomputing each parent.", "Query: collect the O(log n) maximal nodes fully inside the range.", "Combine them with the operation (order matters only for non-commutative operations)."],
    trace_title="sum of `a[2..6]` in `[2, 1, 5, 3, 4, 2, 6, 1]`",
    trace="""root [0,7] partial -> split
[0,3] partial -> [0,1] outside, [2,3] inside: +8
[4,7] partial -> [4,5] inside: +6, [6,7] partial -> [6,6] inside: +6, [7,7] outside
total = 8 + 6 + 6 = 20""",
    code=[("iterative (bottom-up) sum segment tree",
           """class SegmentTree {
    private final int n;
    private final int[] t;
    SegmentTree(int[] a) {
        n = a.length;
        t = new int[2 * n];
        for (int i = 0; i < n; i++) t[n + i] = a[i];                // leaves
        for (int i = n - 1; i > 0; i--) t[i] = t[2 * i] + t[2 * i + 1];
    }
    void update(int i, int v) {                                    // a[i] = v
        for (t[i += n] = v; i > 1; i >>= 1) t[i >> 1] = t[i] + t[i ^ 1];
    }
    int query(int l, int r) {                                      // sum of a[l..r] inclusive
        int s = 0;
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if ((l & 1) == 1) s += t[l++];                         // l is a right child: take it and move right
            if ((r & 1) == 1) s += t[--r];                         // r is exclusive: take the left sibling
        }
        return s;
    }
}""",
           """class SegmentTree:
    def __init__(self, a):
        self.n = len(a)
        self.t = [0] * self.n + list(a)                            # leaves at n .. 2n-1
        for i in range(self.n - 1, 0, -1):
            self.t[i] = self.t[2 * i] + self.t[2 * i + 1]

    def update(self, i, v):                                        # a[i] = v
        i += self.n
        self.t[i] = v
        while i > 1:
            self.t[i >> 1] = self.t[i] + self.t[i ^ 1]
            i >>= 1

    def query(self, l, r):                                         # sum of a[l..r] inclusive
        s = 0
        l, r = l + self.n, r + self.n + 1
        while l < r:
            if l & 1:
                s += self.t[l]
                l += 1                                             # l is a right child: take it and move right
            if r & 1:
                r -= 1
                s += self.t[r]                                     # r is exclusive: take the left sibling
            l >>= 1
            r >>= 1
        return s"""),
          ("recursive max tree with \"first index whose value is at least x\" (tree descent)",
           """class MaxSegmentTree {
    private final int n;
    private final int[] mx;
    MaxSegmentTree(int[] a) {
        n = a.length;
        mx = new int[4 * n];
        build(1, 0, n - 1, a);
    }
    private void build(int o, int l, int r, int[] a) {
        if (l == r) { mx[o] = a[l]; return; }
        int m = (l + r) / 2;
        build(2 * o, l, m, a);
        build(2 * o + 1, m + 1, r, a);
        mx[o] = Math.max(mx[2 * o], mx[2 * o + 1]);
    }
    void update(int pos, int v) { update(1, 0, n - 1, pos, v); }
    private void update(int o, int l, int r, int pos, int v) {
        if (l == r) { mx[o] = v; return; }
        int m = (l + r) / 2;
        if (pos <= m) update(2 * o, l, m, pos, v); else update(2 * o + 1, m + 1, r, pos, v);
        mx[o] = Math.max(mx[2 * o], mx[2 * o + 1]);
    }
    int firstAtLeast(int x) { return mx[1] < x ? -1 : descend(1, 0, n - 1, x); }
    private int descend(int o, int l, int r, int x) {              // go left whenever the left child can satisfy x
        if (l == r) return l;
        int m = (l + r) / 2;
        return mx[2 * o] >= x ? descend(2 * o, l, m, x) : descend(2 * o + 1, m + 1, r, x);
    }
}""",
           """class MaxSegmentTree:
    def __init__(self, a):
        self.n = len(a)
        self.mx = [0] * (4 * self.n)
        self._build(1, 0, self.n - 1, a)

    def _build(self, o, l, r, a):
        if l == r:
            self.mx[o] = a[l]
            return
        m = (l + r) // 2
        self._build(2 * o, l, m, a)
        self._build(2 * o + 1, m + 1, r, a)
        self.mx[o] = max(self.mx[2 * o], self.mx[2 * o + 1])

    def update(self, pos, v, o=1, l=0, r=None):
        r = self.n - 1 if r is None else r
        if l == r:
            self.mx[o] = v
            return
        m = (l + r) // 2
        if pos <= m:
            self.update(pos, v, 2 * o, l, m)
        else:
            self.update(pos, v, 2 * o + 1, m + 1, r)
        self.mx[o] = max(self.mx[2 * o], self.mx[2 * o + 1])

    def first_at_least(self, x):                                   # go left whenever the left child can satisfy x
        if self.mx[1] < x:
            return -1
        o, l, r = 1, 0, self.n - 1
        while l < r:
            m = (l + r) // 2
            if self.mx[2 * o] >= x:
                o, r = 2 * o, m
            else:
                o, l = 2 * o + 1, m + 1
        return l""")],
    complexity="O(n) build, O(log n) per query and update, O(n) space (2n iterative, 4n recursive).",
    traps=["Recursive trees need an array of size **4n**, not 2n, for arbitrary n.", "Be consistent about inclusive or exclusive right ends.",
           "The bottom-up version above is only correct for **commutative** operations when combining left and right pieces carelessly; for min / max / sum it is fine.", "For range updates use lazy propagation (P3)."],
    variants=["Min / max / gcd / xor / count of a value: change the combine function.", "Store `(max, index)` pairs for argmax.", "Dynamic (sparse) segment tree: create children on demand for huge coordinate ranges.", "Merge-sort tree / persistent trees: store more per node."],
    notuse="A static array with only queries (sparse table, prefix sums) or only sums with point updates (Fenwick is shorter).",
    problems=[
        (307, "Range Sum Query - Mutable", "M", "range-sum-query-mutable", "Sum segment tree with point update", "O(log n) / O(n)"),
        (699, "Falling Squares", "H", "falling-squares", "Range max query + range assign over compressed coordinates", "O(n log n) / O(n)"),
        (2407, "Longest Increasing Subsequence II", "H", "longest-increasing-subsequence-ii", "Max tree over values: dp[x] = 1 + max over [x−k, x−1]", "O(n log m) / O(m)"),
        (1157, "Online Majority Element In Subarray", "H", "online-majority-element-in-subarray", "Segment tree of Boyer–Moore candidates + binary search on positions", "O(log n) per query / O(n)"),
    ]))

# ---------------------------------------------------------------- 3
P.append(dict(
    title="Lazy propagation: range updates", tier="sec", sim="lazy", oneline="postpone the update: leave a tag and push it down only when needed",
    why="Range add / range assign together with range queries in O(log n)", signature="LC 732 / 218 / 850",
    when="You apply an update to **every element of a range** and also query ranges (range add + range sum / max).",
    detect="\"add k to every element in [l, r]\" · \"my calendar III (max overlap)\" · \"skyline\" · \"rectangle area union\" · \"flip a range then count\".",
    intuition="A plain segment tree would have to change every leaf of the range, which is O(n). Instead, when an update covers a node **completely**, change that node's stored answer immediately and leave a **lazy tag** (\"everything below still needs +v\"). The children are not touched. Only when a later operation must look **inside** that node, push the tag down to its two children first. Each operation touches O(log n) nodes, and pending work is paid for lazily.",
    brute="Applying an update to each element: O(n) per update. Lazy tags: O(log n) per update and query.",
    idea="Two arrays: `sum[node]` (the answer of the node including its own tags) and `lazy[node]`. `apply(node, len, v)`: `sum += v · len; lazy += v`. `push(node)`: send `lazy` to both children and clear it. Update: if covered → `apply` and stop; else `push`, recurse, `pull` (`sum = left + right`). Query: same descent with `push`. For range **max** with range add you can skip pushing: keep a permanent tag per node (\"mark permanence\").",
    steps=["Fully covered node → update stored value and tag, stop.", "Partially covered node → push its tag to the children first.", "Recurse into the overlapping children.", "Pull: recompute the node from its children."],
    trace_title="`[1, 2, 3, 4]`: add 10 to [0, 1], then sum [1, 2]",
    trace="""add(0..1, +10): root partial -> left [0,1] fully inside: sum 3 -> 23, lazy +10 (stop)
sum(1..2): root partial -> left [0,1] partial: push +10 down (leaves 11, 12)
   leaf 1 = 12 inside, leaf 0 outside; right [2,3] partial -> leaf 2 = 3
total 15""",
    code=[("range add and range sum with lazy tags",
           """class LazySegmentTree {
    private final int n;
    private final long[] sum, lazy;
    LazySegmentTree(int[] a) {
        n = a.length;
        sum = new long[4 * n];
        lazy = new long[4 * n];
        build(1, 0, n - 1, a);
    }
    private void build(int o, int l, int r, int[] a) {
        if (l == r) { sum[o] = a[l]; return; }
        int m = (l + r) / 2;
        build(2 * o, l, m, a);
        build(2 * o + 1, m + 1, r, a);
        sum[o] = sum[2 * o] + sum[2 * o + 1];
    }
    private void apply(int o, int len, long v) { sum[o] += v * len; lazy[o] += v; }
    private void push(int o, int l, int r) {
        if (lazy[o] == 0) return;
        int m = (l + r) / 2;
        apply(2 * o, m - l + 1, lazy[o]);
        apply(2 * o + 1, r - m, lazy[o]);
        lazy[o] = 0;
    }
    void add(int ql, int qr, long v) { add(1, 0, n - 1, ql, qr, v); }
    private void add(int o, int l, int r, int ql, int qr, long v) {
        if (qr < l || r < ql) return;
        if (ql <= l && r <= qr) { apply(o, r - l + 1, v); return; }   // fully covered: tag and stop
        push(o, l, r);
        int m = (l + r) / 2;
        add(2 * o, l, m, ql, qr, v);
        add(2 * o + 1, m + 1, r, ql, qr, v);
        sum[o] = sum[2 * o] + sum[2 * o + 1];                         // pull up
    }
    long query(int ql, int qr) { return query(1, 0, n - 1, ql, qr); }
    private long query(int o, int l, int r, int ql, int qr) {
        if (qr < l || r < ql) return 0;
        if (ql <= l && r <= qr) return sum[o];
        push(o, l, r);
        int m = (l + r) / 2;
        return query(2 * o, l, m, ql, qr) + query(2 * o + 1, m + 1, r, ql, qr);
    }
}""",
           """class LazySegmentTree:
    def __init__(self, a):
        self.n = len(a)
        self.sum = [0] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)
        self._build(1, 0, self.n - 1, a)

    def _build(self, o, l, r, a):
        if l == r:
            self.sum[o] = a[l]
            return
        m = (l + r) // 2
        self._build(2 * o, l, m, a)
        self._build(2 * o + 1, m + 1, r, a)
        self.sum[o] = self.sum[2 * o] + self.sum[2 * o + 1]

    def _apply(self, o, length, v):
        self.sum[o] += v * length
        self.lazy[o] += v

    def _push(self, o, l, r):
        if self.lazy[o]:
            m = (l + r) // 2
            self._apply(2 * o, m - l + 1, self.lazy[o])
            self._apply(2 * o + 1, r - m, self.lazy[o])
            self.lazy[o] = 0

    def add(self, ql, qr, v, o=1, l=0, r=None):
        r = self.n - 1 if r is None else r
        if qr < l or r < ql:
            return
        if ql <= l and r <= qr:                                    # fully covered: tag and stop
            self._apply(o, r - l + 1, v)
            return
        self._push(o, l, r)
        m = (l + r) // 2
        self.add(ql, qr, v, 2 * o, l, m)
        self.add(ql, qr, v, 2 * o + 1, m + 1, r)
        self.sum[o] = self.sum[2 * o] + self.sum[2 * o + 1]        # pull up

    def query(self, ql, qr, o=1, l=0, r=None):
        r = self.n - 1 if r is None else r
        if qr < l or r < ql:
            return 0
        if ql <= l and r <= qr:
            return self.sum[o]
        self._push(o, l, r)
        m = (l + r) // 2
        return self.query(ql, qr, 2 * o, l, m) + self.query(ql, qr, 2 * o + 1, m + 1, r)"""),
          ("range add + global max with permanent tags (no push-down needed)",
           """class AddMaxTree {
    private final int n;
    private final int[] mx, add;
    AddMaxTree(int n) { this.n = n; mx = new int[4 * n]; add = new int[4 * n]; }
    void update(int ql, int qr, int v) { update(1, 0, n - 1, ql, qr, v); }
    private void update(int o, int l, int r, int ql, int qr, int v) {
        if (ql <= l && r <= qr) { mx[o] += v; add[o] += v; return; }   // permanent tag: never pushed down
        int m = (l + r) / 2;
        if (ql <= m) update(2 * o, l, m, ql, qr, v);
        if (qr > m) update(2 * o + 1, m + 1, r, ql, qr, v);
        mx[o] = Math.max(mx[2 * o], mx[2 * o + 1]) + add[o];           // children max plus this node's own tag
    }
    int max() { return mx[1]; }
}""",
           """class AddMaxTree:
    def __init__(self, n):
        self.n = n
        self.mx = [0] * (4 * n)
        self.add_ = [0] * (4 * n)

    def update(self, ql, qr, v, o=1, l=0, r=None):
        r = self.n - 1 if r is None else r
        if ql <= l and r <= qr:                                    # permanent tag: never pushed down
            self.mx[o] += v
            self.add_[o] += v
            return
        m = (l + r) // 2
        if ql <= m:
            self.update(ql, qr, v, 2 * o, l, m)
        if qr > m:
            self.update(ql, qr, v, 2 * o + 1, m + 1, r)
        self.mx[o] = max(self.mx[2 * o], self.mx[2 * o + 1]) + self.add_[o]   # children max plus this node's own tag

    def max(self):
        return self.mx[1]""")],
    complexity="O(n) build, O(log n) per range update / query, O(n) space.",
    traps=["Always **push before recursing** into a partly covered node and **pull after** changing children.", "`sum += v * length`: the tag is per element, so multiply by the segment length.",
           "Use `long`: sums of many range adds overflow `int`.", "Range **assign** needs a separate \"has assignment\" flag, because a tag of 0 is a valid assignment."],
    variants=["Range assign + range sum: tag = (flag, value).", "Range add + range min / max with mark permanence (second snippet).", "Rectangle union area / skyline: sweep line + segment tree over compressed coordinates.", "Flip bits in a range + count ones: tag is a boolean toggled on apply."],
    notuse="Only point updates (plain segment / Fenwick) or offline range updates (a difference array is enough).",
    problems=[
        (732, "My Calendar III", "H", "my-calendar-iii", "Range add +1 on each booking, track the global max (mark permanence)", "O(log N) per booking / O(N)"),
        (218, "The Skyline Problem", "H", "the-skyline-problem", "Sweep line + heap (or lazy tree over compressed x)", "O(n log n) / O(n)"),
        (850, "Rectangle Area II", "H", "rectangle-area-ii", "Sweep over x; a tree over compressed y keeps the covered length", "O(n²) or O(n log n) / O(n)"),
        (2569, "Handling Sum Queries After Update", "H", "handling-sum-queries-after-update", "Range flip + count ones with a toggle tag", "O((n+q) log n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 4
P.append(dict(
    title="Sparse table: O(1) range minimum on static data", tier="sec", sim="sparse", oneline="precompute every power-of-two window; answer with two overlapping windows",
    why="The fastest range min / max / gcd query when the array never changes", signature="LC 239 / 1438 / 2104",
    when="Many range min / max / gcd queries on an array that does **not** change.",
    detect="\"many range minimum queries\" · \"static array\" · \"LCA with Euler tour\" · \"largest value in every window\" · \"gcd of a range\".",
    intuition="Precompute `table[j][i]` = the minimum of the `2^j` elements starting at `i`. Each row is built from the row above in O(1) per cell (`two halves`). To answer `min(l..r)` find the largest power of two `2^k` not above the length; the two windows `[l, l + 2^k)` and `(r − 2^k, r]` cover the whole range. They **overlap**, which is harmless for min, max and gcd (idempotent operations), so the answer is `min(table[k][l], table[k][r − 2^k + 1])` in O(1).",
    brute="Scanning the range is O(n) per query. The table costs O(n log n) once and then O(1) per query.",
    idea="`table[0] = a`. For `j ≥ 1`: `table[j][i] = min(table[j−1][i], table[j−1][i + 2^(j−1)])` for every `i` with `i + 2^j ≤ n`. Precompute `log[len]` (or use `bit_length`). Query: `k = log[r − l + 1]`.",
    steps=["Fill row 0 with the array.", "Build row `j` from row `j − 1`.", "For a query compute `k = floor(log2(length))`.", "Return the better of the two overlapping windows."],
    trace_title="`[5, 2, 4, 7, 6, 3, 1, 8]`, `min(1..6)`",
    trace="""length 6 -> k = 2 (window 4)
table[2][1] = min(2, 4, 7, 6) = 2   (covers 1..4)
table[2][3] = min(7, 6, 3, 1) = 1   (covers 3..6)
answer min(2, 1) = 1""",
    code=[("sparse table for range minimum",
           """class SparseTable {
    private final int[][] t;
    private final int[] log;
    SparseTable(int[] a) {
        int n = a.length;
        log = new int[n + 1];
        for (int i = 2; i <= n; i++) log[i] = log[i / 2] + 1;
        t = new int[log[n] + 1][];
        t[0] = a.clone();
        for (int j = 1; j <= log[n]; j++) {
            t[j] = new int[n - (1 << j) + 1];
            for (int i = 0; i + (1 << j) <= n; i++)
                t[j][i] = Math.min(t[j - 1][i], t[j - 1][i + (1 << (j - 1))]);
        }
    }
    int min(int l, int r) {                                        // inclusive
        int k = log[r - l + 1];
        return Math.min(t[k][l], t[k][r - (1 << k) + 1]);           // two overlapping windows
    }
}""",
           """class SparseTable:
    def __init__(self, a):
        n = len(a)
        self.t = [list(a)]
        j = 1
        while (1 << j) <= n:
            prev = self.t[-1]
            half = 1 << (j - 1)
            self.t.append([min(prev[i], prev[i + half]) for i in range(n - (1 << j) + 1)])
            j += 1

    def min(self, l, r):                                           # inclusive
        k = (r - l + 1).bit_length() - 1
        return min(self.t[k][l], self.t[k][r - (1 << k) + 1])      # two overlapping windows"""),
          ("range gcd (another idempotent operation)",
           """class GcdTable {
    private final int[][] t;
    GcdTable(int[] a) {
        int n = a.length, levels = 32 - Integer.numberOfLeadingZeros(n);
        t = new int[levels][];
        t[0] = a.clone();
        for (int j = 1; j < levels; j++) {
            t[j] = new int[n - (1 << j) + 1];
            for (int i = 0; i + (1 << j) <= n; i++) t[j][i] = gcd(t[j - 1][i], t[j - 1][i + (1 << (j - 1))]);
        }
    }
    private static int gcd(int x, int y) { return y == 0 ? x : gcd(y, x % y); }
    int query(int l, int r) {
        int k = 31 - Integer.numberOfLeadingZeros(r - l + 1);
        return gcd(t[k][l], t[k][r - (1 << k) + 1]);
    }
}""",
           """from math import gcd

class GcdTable:
    def __init__(self, a):
        n = len(a)
        self.t = [list(a)]
        j = 1
        while (1 << j) <= n:
            prev, half = self.t[-1], 1 << (j - 1)
            self.t.append([gcd(prev[i], prev[i + half]) for i in range(n - (1 << j) + 1)])
            j += 1

    def query(self, l, r):
        k = (r - l + 1).bit_length() - 1
        return gcd(self.t[k][l], self.t[k][r - (1 << k) + 1])""")],
    complexity="O(n log n) build and memory, O(1) per query.",
    traps=["Only for **idempotent** operations (min, max, gcd, and, or). Sums would double-count the overlap.", "The array must not change: any update means rebuilding (use a segment tree instead).",
           "Do not call `log2` on floats in a hot loop: precompute `log[]` or use bit tricks.", "Memory is n log n: about 20 million ints for n = 10⁶."],
    variants=["Disjoint sparse table: O(1) queries for non-idempotent operations such as sums or products.", "Store indices (argmin) instead of values.", "Euler tour + sparse table: O(1) LCA (P6).", "Sliding window maximum: a monotonic deque is O(n) with no table."],
    notuse="Updates between queries, or a single pass is enough (monotonic deque, prefix sums).",
    problems=[
        (239, "Sliding Window Maximum", "H", "sliding-window-maximum", "Window max: monotonic deque (O(n)); a sparse table also works", "O(n) / O(k)"),
        (1438, "Longest Continuous Subarray With Absolute Diff Less Than or Equal to Limit", "M", "longest-continuous-subarray-with-absolute-diff-less-than-or-equal-to-limit", "Two deques (max and min) or a sparse table + two pointers", "O(n) / O(n)"),
        (2104, "Sum of Subarray Ranges", "M", "sum-of-subarray-ranges", "Sum of max − sum of min: monotonic stack (or range queries)", "O(n) / O(n)"),
        (1521, "Find a Value of a Mysterious Function Closest to Target", "H", "find-a-value-of-a-mysterious-function-closest-to-target", "Bitwise AND over ranges: sparse table or set of distinct ANDs", "O(n log A) / O(n)"),
    ]))

# ---------------------------------------------------------------- 5
P.append(dict(
    title="Counting while sweeping: Fenwick tree over ranks", tier="hot", sim="inv", oneline="compress values, sweep, and count earlier elements in O(log n)",
    why="Turns O(n²) pair counting (inversions and friends) into O(n log n)", signature="LC 315 / 493 / 327",
    when="You must count, for each element, how many earlier (or later) elements are smaller, larger, or within a range.",
    detect="\"count of smaller numbers after self\" · \"reverse pairs\" · \"count of range sum\" · \"count inversions\" · \"create sorted array through instructions\".",
    intuition="Sweep through the array once. For each element the question is a **prefix count over values**: how many of the elements already seen are smaller than it? Keep a Fenwick tree indexed by **value** (compressed to ranks `1..m` because values may be huge). Query the prefix of ranks below the current value, then insert the current value. Each element costs two O(log n) operations.",
    brute="Comparing every pair is O(n²). Sorting plus a merge step also gives O(n log n) (merge sort count), but the Fenwick sweep generalises to \"range\" questions.",
    idea="Sort the distinct values for coordinate compression (`rank = index + 1`). Sweep (direction depends on whether you count earlier or later elements). `count = prefix(rank − 1)` for strictly smaller, `inserted − prefix(rank)` for strictly larger, then `add(rank, +1)`.",
    steps=["Compress values to ranks `1..m`.", "Iterate the array in the needed direction.", "Query the Fenwick tree for the count you need.", "Insert the current rank into the tree."],
    trace_title="inversions of `[7, 3, 5, 1]`",
    trace="""ranks 4 2 3 1
7: seen 0                 -> 0
3: seen 1, prefix(2) = 0  -> 1 larger
5: seen 2, prefix(3) = 1  -> 1 larger
1: seen 3, prefix(1) = 0  -> 3 larger
total 5""",
    code=[("count of smaller numbers after self",
           """List<Integer> countSmaller(int[] nums) {
    int[] sorted = Arrays.stream(nums).distinct().sorted().toArray();   // coordinate compression
    int n = sorted.length;
    int[] bit = new int[n + 1];
    Integer[] res = new Integer[nums.length];
    for (int i = nums.length - 1; i >= 0; i--) {                         // sweep right to left
        int rank = Arrays.binarySearch(sorted, nums[i]) + 1;             // 1-indexed rank
        int cnt = 0;
        for (int j = rank - 1; j > 0; j -= j & -j) cnt += bit[j];        // strictly smaller values already on the right
        res[i] = cnt;
        for (int j = rank; j <= n; j += j & -j) bit[j]++;
    }
    return Arrays.asList(res);
}""",
           """from bisect import bisect_left

def count_smaller(nums):
    vals = sorted(set(nums))                                             # coordinate compression
    n = len(vals)
    bit = [0] * (n + 1)
    res = [0] * len(nums)
    for i in range(len(nums) - 1, -1, -1):                               # sweep right to left
        rank = bisect_left(vals, nums[i]) + 1                            # 1-indexed rank
        j, cnt = rank - 1, 0
        while j > 0:
            cnt += bit[j]                                                # strictly smaller values already on the right
            j -= j & -j
        res[i] = cnt
        j = rank
        while j <= n:
            bit[j] += 1
            j += j & -j
    return res"""),
          ("reverse pairs: count i < j with nums[i] > 2 · nums[j]",
           """int reversePairs(int[] nums) {
    long[] vals = Arrays.stream(nums).asLongStream().distinct().sorted().toArray();
    int n = vals.length, seen = 0, ans = 0;
    int[] bit = new int[n + 1];
    for (int x : nums) {
        int k = upper(vals, 2L * x);                                    // distinct values <= 2x
        int le = 0;
        for (int j = k; j > 0; j -= j & -j) le += bit[j];
        ans += seen - le;                                                // earlier values strictly greater than 2x
        for (int j = Arrays.binarySearch(vals, (long) x) + 1; j <= n; j += j & -j) bit[j]++;
        seen++;
    }
    return ans;
}
private int upper(long[] a, long x) {                                    // first index with a[i] > x
    int lo = 0, hi = a.length;
    while (lo < hi) { int mid = (lo + hi) >>> 1; if (a[mid] <= x) lo = mid + 1; else hi = mid; }
    return lo;
}""",
           """from bisect import bisect_left, bisect_right

def reverse_pairs(nums):
    vals = sorted(set(nums))
    n = len(vals)
    bit = [0] * (n + 1)
    seen = ans = 0
    for x in nums:
        j = bisect_right(vals, 2 * x)                                    # distinct values <= 2x
        le = 0
        while j > 0:
            le += bit[j]
            j -= j & -j
        ans += seen - le                                                 # earlier values strictly greater than 2x
        j = bisect_left(vals, x) + 1
        while j <= n:
            bit[j] += 1
            j += j & -j
        seen += 1
    return ans""")],
    complexity="O(n log n) time, O(n) space.",
    traps=["Compress **all** values you will query or insert (for reverse pairs the query value is `2x`, not `x`: use binary search on the sorted array rather than a rank map).", "Strictly smaller vs smaller-or-equal changes the prefix bound by one rank.",
           "Duplicates share one rank; `distinct()` / `set()` before sorting.", "Sweep direction decides \"before\" vs \"after\": right-to-left counts elements to the right."],
    variants=["Count of range sum: Fenwick over prefix sums, query a value window.", "Create sorted array through instructions: min(smaller, larger) cost per insert.", "Merge sort counting: split, count cross pairs during merge, O(n log n) without a tree."],
    notuse="n ≤ a few thousand (the O(n²) double loop is fine) or the data is not sweep-ordered (use offline sorting).",
    problems=[
        (315, "Count of Smaller Numbers After Self", "H", "count-of-smaller-numbers-after-self", "Right-to-left sweep; BIT over ranks gives strictly smaller counts", "O(n log n) / O(n)"),
        (493, "Reverse Pairs", "H", "reverse-pairs", "BIT over compressed values; query rank of 2x", "O(n log n) / O(n)"),
        (327, "Count of Range Sum", "H", "count-of-range-sum", "BIT (or merge sort) over prefix sums within [lower, upper]", "O(n log n) / O(n)"),
        (1649, "Create Sorted Array through Instructions", "H", "create-sorted-array-through-instructions", "Cost = min(count smaller, count larger) with a BIT", "O(n log m) / O(m)"),
    ]))

# ---------------------------------------------------------------- 6
P.append(dict(
    title="Binary lifting and lowest common ancestor", tier="hot", sim="lca", oneline="store every 2^j-th ancestor; jump in powers of two",
    why="Ancestor and LCA queries on trees in O(log n) after a one-time table", signature="LC 1483 / 236",
    when="You answer many queries of the form \"k-th ancestor of a node\" or \"lowest common ancestor of u and v\" on a fixed tree.",
    detect="\"kth ancestor of a tree node\" · \"lowest common ancestor\" · \"distance between two nodes\" · \"queries on a tree path\".",
    intuition="Walking up one parent at a time costs O(depth) per query. Precompute `up[j][v]`, the `2^j`-th ancestor of `v` (the parent of the `2^(j−1)`-th ancestor of the `2^(j−1)`-th ancestor). Any jump of `k` steps is the sum of the powers of two in `k`'s binary representation, so it takes O(log n) lookups. For LCA: first lift the deeper node to the same depth, then lift both together from the highest power to the lowest, **skipping jumps that would make them meet**; the parent of the resulting pair is the LCA.",
    brute="Climbing parents one at a time: O(depth) per query, O(n) in a chain. Binary lifting: O(n log n) preprocessing and O(log n) per query.",
    idea="`up[0][v] = parent[v]` (root → −1). `up[j][v] = up[j−1][up[j−1][v]]`. `kth(v, k)`: for each set bit `j` of `k`, `v = up[j][v]`. `lca(u, v)`: equalise depths with `kth`, return if equal, else for `j` from high to low: if `up[j][u] != up[j][v]` jump both; answer `up[0][u]`.",
    steps=["Compute depths and `up[0]` from the parent array.", "Fill `up[j]` from `up[j − 1]`.", "To lift by `k`, follow the set bits of `k`.", "For LCA lift the deeper node, then jump both while their ancestors differ."],
    trace_title="LCA of nodes 7 and 6 in the 9-node tree",
    trace="""depth(7) = 3, depth(6) = 2 -> lift 7 by 1: u = 3
up[1][3] = 0 = up[1][6]    -> equal, skip
up[0][3] = 1 != up[0][6] = 2 -> jump: u = 1, v = 2
LCA = up[0][1] = 0""",
    code=[("binary lifting: k-th ancestor and LCA (parent[i] < i, parent[0] = -1)",
           """class TreeAncestor {
    private final int LOG;
    private final int[][] up;                                      // up[j][v] = 2^j-th ancestor of v, or -1
    private final int[] depth;
    TreeAncestor(int n, int[] parent) {
        LOG = 32 - Integer.numberOfLeadingZeros(Math.max(1, n));
        up = new int[LOG][n];
        depth = new int[n];
        for (int v = 0; v < n; v++) {
            up[0][v] = parent[v];
            depth[v] = parent[v] < 0 ? 0 : depth[parent[v]] + 1;
        }
        for (int j = 1; j < LOG; j++)
            for (int v = 0; v < n; v++) {
                int mid = up[j - 1][v];
                up[j][v] = mid < 0 ? -1 : up[j - 1][mid];
            }
    }
    int getKthAncestor(int node, int k) {
        if (k > depth[node]) return -1;
        for (int j = 0; j < LOG; j++)
            if ((k >> j & 1) == 1) node = up[j][node];             // follow the set bits of k
        return node;
    }
    int lca(int u, int v) {
        if (depth[u] < depth[v]) { int t = u; u = v; v = t; }
        u = getKthAncestor(u, depth[u] - depth[v]);                // lift the deeper node
        if (u == v) return u;
        for (int j = LOG - 1; j >= 0; j--)
            if (up[j][u] != up[j][v]) { u = up[j][u]; v = up[j][v]; }   // jump only if they do not meet
        return up[0][u];
    }
}""",
           """class TreeAncestor:
    def __init__(self, n, parent):                                 # parent[i] < i, parent[0] = -1
        self.LOG = max(1, n).bit_length()
        self.depth = [0] * n
        for v in range(n):
            self.depth[v] = 0 if parent[v] < 0 else self.depth[parent[v]] + 1
        self.up = [list(parent)]                                   # up[j][v] = 2^j-th ancestor of v, or -1
        for j in range(1, self.LOG):
            prev = self.up[-1]
            self.up.append([-1 if prev[v] < 0 else prev[prev[v]] for v in range(n)])

    def get_kth_ancestor(self, node, k):
        if k > self.depth[node]:
            return -1
        for j in range(self.LOG):
            if k >> j & 1:
                node = self.up[j][node]                            # follow the set bits of k
        return node

    def lca(self, u, v):
        if self.depth[u] < self.depth[v]:
            u, v = v, u
        u = self.get_kth_ancestor(u, self.depth[u] - self.depth[v])   # lift the deeper node
        if u == v:
            return u
        for j in range(self.LOG - 1, -1, -1):
            if self.up[j][u] != self.up[j][v]:                     # jump only if they do not meet
                u, v = self.up[j][u], self.up[j][v]
        return self.up[0][u]"""),
          ("LCA of a binary tree by recursion (single query, no preprocessing)",
           """TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
    if (root == null || root == p || root == q) return root;
    TreeNode left = lowestCommonAncestor(root.left, p, q);
    TreeNode right = lowestCommonAncestor(root.right, p, q);
    if (left != null && right != null) return root;                // p and q are on different sides
    return left != null ? left : right;
}""",
           """def lowest_common_ancestor(root, p, q):
    if root is None or root is p or root is q:
        return root
    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)
    if left and right:                                             # p and q are on different sides
        return root
    return left or right""")],
    complexity="O(n log n) preprocessing and memory, O(log n) per query; the single-query recursion is O(n).",
    traps=["The table has `LOG` rows where `2^LOG > n`; jumping past the root must give −1, not crash.", "In the LCA loop jump only when the two ancestors **differ**; the answer is the parent afterwards.",
           "Depths must be computed before lifting; with an arbitrary parent order use a DFS / BFS from the root.", "For a BST the LCA is found by walking down from the root (no table needed)."],
    variants=["Distance between nodes: `depth[u] + depth[v] − 2 · depth[lca]`.", "Path aggregates (max edge weight on the path): store the aggregate with each `up[j][v]`.", "Euler tour + sparse table: O(1) LCA queries.", "Offline LCA (Tarjan) with union-find."],
    notuse="A single LCA query (use the recursion) or a BST (compare values while descending).",
    problems=[
        (235, "Lowest Common Ancestor of a Binary Search Tree", "M", "lowest-common-ancestor-of-a-binary-search-tree", "Walk down: both smaller go left, both larger go right, else split", "O(h) / O(1)"),
        (236, "Lowest Common Ancestor of a Binary Tree", "M", "lowest-common-ancestor-of-a-binary-tree", "Recursion: the node where p and q are found on different sides", "O(n) / O(h)"),
        (1123, "Lowest Common Ancestor of Deepest Leaves", "M", "lowest-common-ancestor-of-deepest-leaves", "Return (depth, node); equal child depths mean the current node", "O(n) / O(h)"),
        (1483, "Kth Ancestor of a Tree Node", "H", "kth-ancestor-of-a-tree-node", "Binary lifting table; jump along the set bits of k", "O(log n) per query / O(n log n)"),
    ]))

# ---------------------------------------------------------------- 7
P.append(dict(
    title="Ordered set / TreeMap: floor and ceiling", tier="hot", sim="treemap", oneline="keep keys sorted so the nearest neighbours are one search away",
    why="The tool for \"closest value\" and interval-booking problems", signature="LC 729 / 220 / 352",
    when="You insert and delete keys and must ask for the nearest smaller or larger key, or check a new interval against its neighbours.",
    detect="\"my calendar\" · \"contains nearby almost duplicate\" · \"data stream as disjoint intervals\" · \"closest value\" · \"stock price fluctuation (current / max / min)\" · \"sliding window median\".",
    intuition="In a sorted collection a new item can only conflict with its **immediate neighbours**: the largest key not above it (**floor**) and the smallest key not below it (**ceiling**). A balanced tree (Java `TreeMap` / `TreeSet`, C++ `std::set`) finds them in O(log n) and also inserts and deletes in O(log n). Python has no built-in tree: use `bisect` on a sorted list (O(log n) search, O(n) insert), the `sortedcontainers` package, or a different idea (buckets) when it fits.",
    brute="Scanning every stored item is O(n) per operation. The ordered structure makes each operation O(log n).",
    idea="Calendar: store `start → end`; for a new `[s, e)` take `floor(s)` (must end ≤ `s`) and `ceiling(s)` (must start ≥ `e`). Near-duplicate: keep a window of the last `k` values; `ceiling(x − t)` must exceed `x + t`. Intervals: on insert, merge with the floor and ceiling neighbours.",
    steps=["Keep the keys sorted (TreeMap / sorted list).", "Binary-search the new key's position.", "Test the floor and ceiling neighbours only.", "Insert (or merge) and delete expired keys."],
    trace_title="My Calendar I with [10,20), [30,40), [50,60)",
    trace="""book [20,30): floor start 10 ends 20 <= 20 ok, ceiling start 30 >= 30 ok -> booked
book [35,45): floor start 30 ends 40 > 35 -> overlap, rejected""",
    code=[("My Calendar I (conflict check against floor and ceiling)",
           """class MyCalendar {
    private final TreeMap<Integer, Integer> booked = new TreeMap<>();      // start -> end
    boolean book(int start, int end) {
        Map.Entry<Integer, Integer> prev = booked.floorEntry(start);        // largest start <= new start
        Map.Entry<Integer, Integer> next = booked.ceilingEntry(start);      // smallest start >= new start
        if (prev != null && prev.getValue() > start) return false;         // previous booking runs into us
        if (next != null && next.getKey() < end) return false;             // we run into the next booking
        booked.put(start, end);
        return true;
    }
}""",
           """from bisect import bisect_left

class MyCalendar:
    def __init__(self):
        self.starts, self.ends = [], []                            # parallel sorted lists

    def book(self, start, end):
        i = bisect_left(self.starts, start)                        # first booking starting at or after `start`
        if i > 0 and self.ends[i - 1] > start:                     # previous booking runs into us
            return False
        if i < len(self.starts) and self.starts[i] < end:          # we run into the next booking
            return False
        self.starts.insert(i, start)
        self.ends.insert(i, end)
        return True"""),
          ("contains nearby almost duplicate (window kept in an ordered set / buckets)",
           """boolean containsNearbyAlmostDuplicate(int[] nums, int indexDiff, int valueDiff) {
    TreeSet<Long> window = new TreeSet<>();
    for (int i = 0; i < nums.length; i++) {
        long x = nums[i];
        Long c = window.ceiling(x - valueDiff);                    // smallest value >= x - t
        if (c != null && c <= x + valueDiff) return true;
        window.add(x);
        if (i >= indexDiff) window.remove((long) nums[i - indexDiff]);   // keep only the last indexDiff values
    }
    return false;
}""",
           """def contains_nearby_almost_duplicate(nums, index_diff, value_diff):
    width = value_diff + 1                                         # values in one bucket differ by <= value_diff
    buckets = {}
    for i, x in enumerate(nums):
        b = x // width
        if b in buckets:
            return True
        if b - 1 in buckets and x - buckets[b - 1] <= value_diff:
            return True
        if b + 1 in buckets and buckets[b + 1] - x <= value_diff:
            return True
        buckets[b] = x
        if i >= index_diff:
            del buckets[nums[i - index_diff] // width]             # keep only the last index_diff values
    return False""")],
    complexity="O(log n) per operation with a balanced tree; list-based bisect inserts cost O(n) shifting but are fast in practice for n up to ~10⁵.",
    traps=["Floor / ceiling on **equal** keys: decide whether a touching boundary counts as overlap (half-open `[start, end)` makes `end == next.start` legal).", "`TreeSet<Integer>` with `x − t` can overflow: use `long`.",
           "Python's `list.insert` is O(n); use `sortedcontainers.SortedList` if allowed, or the bucket trick.", "When keys can repeat use a `TreeMap` of counts."],
    variants=["Stock price fluctuation: `TreeMap<price, count>` for max / min plus a map from timestamp to price.", "Data stream as disjoint intervals: floor / ceiling then merge.", "Sliding window median: two ordered sets (or two heaps with lazy deletion).", "Exam room: gaps between occupied seats in an ordered set."],
    notuse="Only min or max is needed (use a heap), or the keys are small integers (an array or Fenwick tree).",
    problems=[
        (729, "My Calendar I", "M", "my-calendar-i", "floor / ceiling neighbours decide the overlap", "O(log n) per booking / O(n)"),
        (2034, "Stock Price Fluctuation", "M", "stock-price-fluctuation", "Map timestamp → price + TreeMap price → count", "O(log n) per op / O(n)"),
        (220, "Contains Duplicate III", "H", "contains-duplicate-iii", "Sliding window in a TreeSet (or buckets of width t + 1)", "O(n log k) / O(k)"),
        (352, "Data Stream as Disjoint Intervals", "H", "data-stream-as-disjoint-intervals", "Floor / ceiling intervals; merge neighbours on insert", "O(log n) per add / O(n)"),
    ]))

# ---------------------------------------------------------------- 8
P.append(dict(
    title="Offline queries: sort the questions, then sweep", tier="sec", sim="offline", oneline="when answers do not depend on order, sort queries and reuse work",
    why="Often turns an impossible online problem into a simple sweep", signature="LC 2070 / 1697 / 1851",
    when="All queries are known in advance and each asks about a threshold (\"items with price ≤ q\", \"edges with weight < limit\").",
    detect="\"queries[i]\" given as an array · \"for each query find …\" · answers depend only on a threshold · \"closest room\" · \"minimum interval to include each query\".",
    intuition="If you answer queries in the order they come you may have to redo work for each one. But if the whole list is known you may answer them in **any order** and write each answer to its original index. Sort the queries by threshold and sort the data by the same key; then sweep once, absorbing data items into a running structure (a running maximum, a union-find, a heap, a BIT) as the threshold grows. Each item is added once and each query is a cheap lookup.",
    brute="Per query scan: O(n · q). Sort + sweep: O((n + q) log(n + q)).",
    idea="Sort the data by key. Create an index array of the queries sorted by threshold. Keep a pointer `p` into the data. For each query in sorted order: advance `p` while `data[p].key ≤ threshold`, updating the structure; answer the query from the structure; store it at `ans[original_index]`.",
    steps=["Sort data by the key that queries threshold on.", "Sort query **indices** by threshold.", "Sweep: absorb data up to the current threshold.", "Answer from the structure; write to the original position."],
    trace_title="items price:beauty `1:2 2:4 3:2 3:5 5:6`, queries `[3, 1, 6, 2, 5, 4]`",
    trace="""sorted queries: 1 -> best 2, 2 -> 4, 3 -> 5, 4 -> 5, 5 -> 6, 6 -> 6
answers in original order: [5, 2, 6, 4, 6, 5]""",
    code=[("most beautiful item for each query (running maximum)",
           """int[] maximumBeauty(int[][] items, int[] queries) {
    Arrays.sort(items, (x, y) -> x[0] - y[0]);                     // by price
    Integer[] order = new Integer[queries.length];
    for (int i = 0; i < order.length; i++) order[i] = i;
    Arrays.sort(order, (x, y) -> queries[x] - queries[y]);         // answer queries in increasing order
    int[] ans = new int[queries.length];
    int p = 0, best = 0;
    for (int qi : order) {
        while (p < items.length && items[p][0] <= queries[qi]) best = Math.max(best, items[p++][1]);
        ans[qi] = best;                                            // write to the ORIGINAL position
    }
    return ans;
}""",
           """def maximum_beauty(items, queries):
    items = sorted(items)                                          # by price
    order = sorted(range(len(queries)), key=lambda i: queries[i])  # answer queries in increasing order
    ans = [0] * len(queries)
    p = best = 0
    for qi in order:
        while p < len(items) and items[p][0] <= queries[qi]:
            best = max(best, items[p][1])
            p += 1
        ans[qi] = best                                             # write to the ORIGINAL position
    return ans"""),
          ("offline connectivity: is there a path using only edges lighter than the limit?",
           """int[] parent;
int find(int x) {
    while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
    return x;
}
boolean[] distanceLimitedPathsExist(int n, int[][] edges, int[][] queries) {
    parent = new int[n];
    for (int i = 0; i < n; i++) parent[i] = i;
    Arrays.sort(edges, (a, b) -> a[2] - b[2]);                     // lightest edges first
    Integer[] order = new Integer[queries.length];
    for (int i = 0; i < order.length; i++) order[i] = i;
    Arrays.sort(order, (a, b) -> queries[a][2] - queries[b][2]);
    boolean[] ans = new boolean[queries.length];
    int e = 0;
    for (int qi : order) {
        while (e < edges.length && edges[e][2] < queries[qi][2]) {
            parent[find(edges[e][0])] = find(edges[e][1]);         // add every edge below the limit
            e++;
        }
        ans[qi] = find(queries[qi][0]) == find(queries[qi][1]);
    }
    return ans;
}""",
           """def distance_limited_paths_exist(n, edges, queries):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    edges = sorted(edges, key=lambda e: e[2])                      # lightest edges first
    order = sorted(range(len(queries)), key=lambda i: queries[i][2])
    ans = [False] * len(queries)
    e = 0
    for qi in order:
        u, v, limit = queries[qi]
        while e < len(edges) and edges[e][2] < limit:
            parent[find(edges[e][0])] = find(edges[e][1])          # add every edge below the limit
            e += 1
        ans[qi] = find(u) == find(v)
    return ans""")],
    complexity="O((n + q) log(n + q)) for the sorts, O(n + q) for the sweep.",
    traps=["Sort **indices** of the queries, never the query values themselves, or the answers get shuffled.", "Strict vs non-strict thresholds (`<` limit vs `≤`) decide whether the pointer condition uses `<` or `<=`.",
           "Offline works only if all queries are known upfront; online problems need persistent structures.", "Ties in the data are harmless; ties in queries are fine as long as each writes to its own index."],
    variants=["Minimum interval to include each query: sort intervals by start, queries ascending, min-heap by length.", "Closest room: sort queries by size descending and use an ordered set of rooms.", "Count elements ≤ x in a prefix: sort queries by prefix and use a BIT.", "Mo's algorithm: reorder range queries to move two pointers minimally."],
    notuse="Queries arrive online or modify the data, so later queries depend on earlier updates.",
    problems=[
        (2070, "Most Beautiful Item for Each Query", "M", "most-beautiful-item-for-each-query", "Sort items and queries; running maximum beauty", "O((n+q) log(n+q)) / O(q)"),
        (1851, "Minimum Interval to Include Each Query", "H", "minimum-interval-to-include-each-query", "Sort; heap of (length, end) of intervals that started", "O((n+q) log n) / O(n+q)"),
        (1697, "Checking Existence of Edge Length Limited Paths", "H", "checking-existence-of-edge-length-limited-paths", "Sort edges and queries by limit; add edges to a DSU", "O((E+q) log(E+q)) / O(n)"),
        (1847, "Closest Room", "H", "closest-room", "Queries by size descending; ordered set of eligible room ids", "O((n+q) log n) / O(n)"),
    ]))

TOPIC = dict(
    id="ads", file="17_advanced_ds.html", title="Advanced Data Structures — Fenwick, Segment Trees, Sparse Tables, LCA and Ordered Sets",
    lead="When arrays change and you must query ranges, a loop is too slow. This guide covers the structures that appear in hard interview rounds: the Fenwick tree, segment trees (with lazy propagation), the sparse table, counting with ranks, binary lifting for ancestors, ordered sets for neighbour queries, and the offline-queries trick. Each pattern has the intuition, a step-through animation, Java and Python code, and a ladder of LeetCode problems.",
    mindset="Pick the structure from three facts: **does the data change** (updates), **what is the query** (sum, min, count, neighbour, ancestor), and **does the operation have an inverse** (sum yes, min no). Fenwick for invertible operations with point updates, segment tree for everything else (add lazy tags for range updates), sparse table for static idempotent queries, ordered set for neighbours, and sorting for offline questions.",
    qintro="Ask these questions to choose a structure:",
    questions=["**Does the array change between queries?** No → prefix sums or sparse table. Yes → Fenwick or segment tree.", "**Is the query invertible** (sum / xor / count)? → Fenwick; **min / max / gcd** → segment tree.",
               "**Do updates cover whole ranges?** → lazy propagation, or a difference array if everything is offline.", "**Do you need the nearest key** (floor / ceiling)? → ordered set / TreeMap.",
               "**Are all queries known in advance and threshold-based?** → sort them and sweep (offline).", "**Is it a tree with ancestor questions?** → binary lifting (or the recursion for a single LCA)."],
    cues=[
        ["prefix sum with point updates", "**P1** Fenwick tree"],
        ["range min / max / sum with updates, first index ≥ x", "**P2** Segment tree"],
        ["add / assign to a whole range, then query", "**P3** Lazy propagation"],
        ["many min / max / gcd queries, array never changes", "**P4** Sparse table"],
        ["count earlier smaller / larger, reverse pairs", "**P5** Fenwick over ranks"],
        ["k-th ancestor, LCA, tree distance", "**P6** Binary lifting"],
        ["nearest key, calendar overlap, window with value difference", "**P7** Ordered set"],
        ["queries known upfront with thresholds", "**P8** Offline sort and sweep"],
    ],
    choose=[
        ["Sum with point updates", "Fenwick (P1)"],
        ["Min / max with updates", "Segment tree (P2)"],
        ["Range updates", "Lazy tree (P3)"],
        ["Static min / max / gcd", "Sparse table (P4)"],
        ["Pairs counting while sweeping", "Fenwick over ranks (P5)"],
        ["Tree ancestors", "Binary lifting (P6)"],
        ["Neighbour keys", "TreeMap / bisect (P7)"],
        ["Threshold queries", "Offline sweep (P8)"],
    ],
    rule="**choose by update type and operation type**: invertible + point update → Fenwick; non-invertible or search → segment tree; range update → lazy tags; static → sparse table or prefix sums.",
    selftest=[
        ("What does cell i of a Fenwick tree store?", "The sum of the last `lowbit(i) = i & −i` elements ending at position i (a block whose size is a power of two)."),
        ("Why can a sparse table answer min in O(1) using overlapping windows?", "Min is idempotent: counting an element twice does not change the answer. For sums the overlap would double-count, so a sparse table is not used for sums."),
        ("What are the three cases when a segment tree query reaches a node?", "Completely outside (return the identity), completely inside (return the stored value and stop), or partly overlapping (recurse into both children)."),
        ("What is a lazy tag and when is it pushed down?", "A pending update stored on a fully covered node. It is pushed to the children only when a later operation needs to look inside that node."),
        ("How do you count, for each element, how many earlier elements are smaller in O(n log n)?", "Compress values to ranks, sweep left to right, query the Fenwick tree for the prefix below the current rank, then insert the current rank."),
        ("How does binary lifting find the k-th ancestor?", "Precompute `up[j][v]`, the 2^j-th ancestor, and follow the set bits of k: one lookup per set bit, so O(log n)."),
        ("Why does a calendar booking only need to check floor and ceiling?", "In a sorted set of non-overlapping intervals a new interval can only collide with its immediate neighbours; all other intervals are farther away on either side."),
        ("Why must you sort query indices rather than query values in offline problems?", "Each answer must be written back to the original position of its query; sorting values loses that position."),
    ],
    plan=[
        "**Day 1:** Fenwick tree: write add / prefix from memory; solve Range Sum Query - Mutable.",
        "**Day 2:** segment tree (iterative and recursive); solve a min / max variant and the first-index-at-least descent.",
        "**Day 3:** lazy propagation; implement range add + range sum, then My Calendar III.",
        "**Day 4:** counting with Fenwick over ranks (Count of Smaller Numbers After Self, Reverse Pairs).",
        "**Day 5:** sparse table and binary lifting (Kth Ancestor, LCA).",
        "**Day 6:** ordered sets and offline queries; for each of the 8 patterns state in one sentence when you would reach for it.",
    ],
    patterns=P,
)
