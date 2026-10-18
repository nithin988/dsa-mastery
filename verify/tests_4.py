"""Functional tests, part 4: topics 16-18."""
import itertools
import random
from functools import lru_cache
from harness import *

R = random.Random(4)


# ----------------------------------------------------------------------------- 16 DP II
@test
def t16_knapsack():
    d = defs(("16", 1, 1))
    cp, ts = d["can_partition"], d["find_target_sum_ways"]
    eq(cp([1, 5, 11, 5]), True)
    eq(cp([1, 2, 3, 5]), False)
    eq(ts([1, 1, 1, 1, 1], 3), 5)
    eq(ts([1], 1), 1)
    for _ in range(200):
        a = [R.randint(0, 6) for _ in range(R.randint(1, 8))]
        t = R.randint(-10, 15)
        brute = sum(1 for s in itertools.product((1, -1), repeat=len(a)) if sum(x * y for x, y in zip(a, s)) == t)
        eq(ts(a, t), brute, "target sum %s %s" % (a, t))
        tot = sum(a)
        bp = any(sum(c) * 2 == tot for r in range(len(a) + 1) for c in itertools.combinations(a, r))
        eq(cp(a), bp, "partition %s" % a)
    kn = defs(("16", 1, 2))["knapsack"]
    eq(kn([1, 3, 4, 5], [1, 4, 5, 7], 7), 9)
    for _ in range(100):
        n = R.randint(1, 7)
        w = [R.randint(1, 6) for _ in range(n)]
        v = [R.randint(0, 9) for _ in range(n)]
        cap = R.randint(0, 15)
        best = max(sum(v[i] for i in c) for r in range(n + 1) for c in itertools.combinations(range(n), r)
                   if sum(w[i] for i in c) <= cap)
        eq(kn(w, v, cap), best)


@test
def t16_multi_knapsack():
    f = defs(("16", 2, 1))["find_max_form"]
    eq(f(["10", "0001", "111001", "1", "0"], 5, 3), 4)
    eq(f(["10", "0", "1"], 1, 1), 2)
    for _ in range(100):
        strs = ["".join(R.choice("01") for _ in range(R.randint(1, 4))) for _ in range(R.randint(1, 7))]
        m, n = R.randint(0, 5), R.randint(0, 5)
        best = 0
        for r in range(len(strs) + 1):
            for c in itertools.combinations(strs, r):
                if sum(s.count("0") for s in c) <= m and sum(s.count("1") for s in c) <= n:
                    best = max(best, r)
        eq(f(strs, m, n), best)
    ps = defs(("16", 2, 2))["profitable_schemes"]
    eq(ps(5, 3, [2, 2], [2, 3]), 2)
    eq(ps(10, 5, [2, 3, 5], [6, 7, 8]), 7)


def is_sub(s, t):
    it = iter(t)
    return all(c in it for c in s)


@test
def t16_lcs():
    d = defs(("16", 3, 1))
    lcs, ls = d["lcs"], d["lcs_string"]
    eq(lcs("abcde", "ace"), 3)
    eq(lcs("abc", "def"), 0)
    for _ in range(200):
        a = "".join(R.choice("abc") for _ in range(R.randint(0, 7)))
        b = "".join(R.choice("abc") for _ in range(R.randint(0, 7)))
        best = max(len(s) for r in range(len(a) + 1) for c in itertools.combinations(a, r)
                   for s in ["".join(c)] if is_sub(s, b))
        eq(lcs(a, b), best, "lcs %s %s" % (a, b))
        s = ls(a, b)
        assert len(s) == best and is_sub(s, a) and is_sub(s, b), (a, b, s)
    nd = defs(("16", 3, 2))["num_distinct"]
    eq(nd("rabbbit", "rabbit"), 3)
    eq(nd("babgbag", "bag"), 5)
    for _ in range(100):
        s = "".join(R.choice("ab") for _ in range(R.randint(0, 8)))
        t = "".join(R.choice("ab") for _ in range(R.randint(0, 3)))
        eq(nd(s, t), sum(1 for c in itertools.combinations(range(len(s)), len(t))
                         if "".join(s[i] for i in c) == t))


@test
def t16_edit_wild():
    md = defs(("16", 4, 1))["min_distance"]
    eq(md("horse", "ros"), 3)
    eq(md("intention", "execution"), 5)
    eq(md("", "abc"), 3)

    def ref(a, b):
        @lru_cache(None)
        def g(i, j):
            if i == len(a):
                return len(b) - j
            if j == len(b):
                return len(a) - i
            if a[i] == b[j]:
                return g(i + 1, j + 1)
            return 1 + min(g(i + 1, j + 1), g(i + 1, j), g(i, j + 1))
        return g(0, 0)
    for _ in range(200):
        a = "".join(R.choice("abc") for _ in range(R.randint(0, 6)))
        b = "".join(R.choice("abc") for _ in range(R.randint(0, 6)))
        eq(md(a, b), ref(a, b))
    im = defs(("16", 4, 2))["is_match"]
    eq([im("aa", "a"), im("aa", "*"), im("cb", "?a"), im("adceb", "*a*b"), im("acdcb", "a*c?b"), im("", "***")],
       [False, True, False, True, False, True])
    import re
    for _ in range(300):
        s = "".join(R.choice("ab") for _ in range(R.randint(0, 6)))
        p = "".join(R.choice("ab?*") for _ in range(R.randint(0, 5)))
        rx = "".join(".*" if c == "*" else "." if c == "?" else c for c in p)
        eq(im(s, p), re.fullmatch(rx, s) is not None, "%s %s" % (s, p))


@test
def t16_palindromes():
    d = defs(("16", 5, 1))
    lps, cs = d["longest_palindrome_subseq"], d["count_substrings"]
    eq(lps("bbbab"), 4)
    eq(lps("cbbd"), 2)
    eq(cs("aaa"), 6)
    eq(cs("abc"), 3)
    for _ in range(150):
        s = "".join(R.choice("ab") for _ in range(R.randint(1, 9)))
        best = max(len(x) for r in range(1, len(s) + 1) for c in itertools.combinations(s, r)
                   for x in ["".join(c)] if x == x[::-1])
        eq(lps(s), best, s)
        eq(cs(s), sum(1 for i in range(len(s)) for j in range(i, len(s)) if s[i:j + 1] == s[i:j + 1][::-1]))
    mc = defs(("16", 5, 2))["min_cut"]
    eq(mc("aab"), 1)
    eq(mc("a"), 0)
    eq(mc("ab"), 1)
    for _ in range(100):
        s = "".join(R.choice("ab") for _ in range(R.randint(1, 8)))
        best = len(s)
        for mask in range(1 << (len(s) - 1)):
            parts, cur = [], s[0]
            for i in range(1, len(s)):
                if mask >> (i - 1) & 1:
                    parts.append(cur)
                    cur = s[i]
                else:
                    cur += s[i]
            parts.append(cur)
            if all(p == p[::-1] for p in parts):
                best = min(best, len(parts) - 1)
        eq(mc(s), best, s)


@test
def t16_interval():
    d = defs(("16", 6, 1))
    mc, cut = d["max_coins"], d["min_cost"]
    eq(mc([3, 1, 5, 8]), 167)
    eq(mc([1, 5]), 10)
    eq(cut(7, [1, 3, 4, 5]), 16)
    eq(cut(9, [5, 6, 1, 4, 2]), 22)

    def brute_coins(a):
        if not a:
            return 0
        best = 0
        for i in range(len(a)):
            l = a[i - 1] if i else 1
            r = a[i + 1] if i + 1 < len(a) else 1
            best = max(best, l * a[i] * r + brute_coins(a[:i] + a[i + 1:]))
        return best
    for _ in range(60):
        a = [R.randint(1, 6) for _ in range(R.randint(1, 6))]
        eq(mc(a), brute_coins(a), a)

    def brute_cut(lo, hi, cuts):
        inside = [c for c in cuts if lo < c < hi]
        if not inside:
            return 0
        return hi - lo + min(brute_cut(lo, c, inside) + brute_cut(c, hi, inside) for c in inside)
    for _ in range(60):
        n = R.randint(2, 12)
        cuts = R.sample(range(1, n), R.randint(1, min(5, n - 1)))
        eq(cut(n, cuts), brute_cut(0, n, cuts))
    pw = defs(("16", 6, 2))["predict_the_winner"]
    eq([pw([1, 5, 2]), pw([1, 5, 233, 7])], [False, True])

    def game(a):
        @lru_cache(None)
        def g(i, j):
            if i > j:
                return 0
            return max(a[i] - g(i + 1, j), a[j] - g(i, j - 1))
        return g(0, len(a) - 1) >= 0
    for _ in range(100):
        a = tuple(R.randint(0, 9) for _ in range(R.randint(1, 8)))
        eq(pw(list(a)), game(a))


@test
def t16_bitmask():
    f = defs(("16", 7, 1))["min_assignment_cost"]
    eq(f([[9, 2, 7], [6, 4, 3], [5, 8, 1]]), 9)
    for _ in range(100):
        n = R.randint(1, 6)
        c = [[R.randint(0, 9) for _ in range(n)] for _ in range(n)]
        eq(f(c), min(sum(c[i][p[i]] for i in range(n)) for p in itertools.permutations(range(n))))
    tsp = defs(("16", 7, 2))["tsp"]
    eq(tsp([[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]]), 80)
    for _ in range(60):
        n = R.randint(2, 6)
        d = [[0 if i == j else R.randint(1, 9) for j in range(n)] for i in range(n)]
        best = min(sum(d[a][b] for a, b in zip((0,) + p, p + (0,))) for p in itertools.permutations(range(1, n)))
        eq(tsp(d), best)


@test
def t16_digits():
    f = defs(("16", 8, 1))["at_most_n_given_digit_set"]
    eq(f(["1", "3", "5", "7"], 100), 20)
    eq(f(["1", "4", "9"], 1000000000), 29523)
    eq(f(["7"], 8), 1)
    for _ in range(150):
        digs = sorted(R.sample("123456789", R.randint(1, 4)))
        n = R.randint(1, 3000)
        eq(f(digs, n), sum(1 for x in range(1, n + 1) if set(str(x)) <= set(digs)), "%s %s" % (digs, n))
    u = defs(("16", 8, 2))["count_numbers_with_unique_digits"]
    for n in range(0, 5):
        eq(u(n), sum(1 for x in range(10 ** n) if len(set(str(x))) == len(str(x))), n)


@test
def t16_deque():
    f = defs(("16", 9, 1))["max_result"]
    eq(f([1, -1, -2, 4, -7, 3], 2), 7)
    eq(f([10, -5, -2, 4, 0, 3], 3), 17)
    eq(f([1, -5, -20, 4, -1, 3, -6, -3], 2), 0)
    g = defs(("16", 9, 2))["constrained_subset_sum"]
    eq(g([10, 2, -10, 5, 20], 2), 37)
    eq(g([-1, -2, -3], 1), -1)
    eq(g([10, -2, -10, -5, 20], 2), 23)

    def brute_jump(a, k):
        n = len(a)
        dp = [None] * n
        dp[0] = a[0]
        for i in range(1, n):
            dp[i] = a[i] + max(dp[j] for j in range(max(0, i - k), i))
        return dp[-1]

    def brute_sub(a, k):
        n = len(a)
        dp = [0] * n
        for i in range(n):
            dp[i] = a[i] + max([0] + [dp[j] for j in range(max(0, i - k), i)])
        return max(dp)
    for _ in range(200):
        a = [R.randint(-9, 9) for _ in range(R.randint(1, 12))]
        k = R.randint(1, 5)
        eq(f(a, k), brute_jump(a, k), "%s %s" % (a, k))
        eq(g(a, k), brute_sub(a, k), "%s %s" % (a, k))


# ----------------------------------------------------------------------------- 17 advanced data structures
@test
def t17_fenwick():
    F = defs(("17", 1, 1))["FenwickTree"]
    d = defs(("17", 1, 2))
    for _ in range(100):
        n = R.randint(1, 20)
        a = [R.randint(-9, 9) for _ in range(n)]
        f = F(n)
        for i, x in enumerate(a):
            f.add(i, x)
        for _ in range(30):
            if R.random() < 0.4:
                i, v = R.randrange(n), R.randint(-5, 5)
                a[i] += v
                f.add(i, v)
            else:
                l = R.randrange(n)
                r = R.randrange(l, n)
                eq(f.range(l, r), sum(a[l:r + 1]), "range %d %d" % (l, r))
        t = d["build_fenwick"](a)
        g = F(n)
        for i, x in enumerate(a):
            g.add(i, x)
        eq(t[1:], g.t[1:], "O(n) build")
    for _ in range(100):
        n = R.randint(1, 12)
        cnt = [R.randint(0, 3) for _ in range(n)]
        if sum(cnt) == 0:
            continue
        t = d["build_fenwick"](cnt)
        flat = [i + 1 for i, c in enumerate(cnt) for _ in range(c)]
        for k in range(1, len(flat) + 1):
            eq(d["kth_smallest"](t, n, k), flat[k - 1], "kth")


@test
def t17_segment_tree():
    S = defs(("17", 2, 1))["SegmentTree"]
    M = defs(("17", 2, 2))["MaxSegmentTree"]
    a = [2, 1, 5, 3, 4, 2, 6, 1]
    eq(S(a).query(2, 6), 20)
    for _ in range(100):
        n = R.randint(1, 17)
        a = [R.randint(-9, 9) for _ in range(n)]
        s, m = S(a), M(a)
        for _ in range(30):
            if R.random() < 0.4:
                i, v = R.randrange(n), R.randint(-9, 9)
                a[i] = v
                s.update(i, v)
                m.update(i, v)
            else:
                l = R.randrange(n)
                r = R.randrange(l, n)
                eq(s.query(l, r), sum(a[l:r + 1]), "sum %d %d n=%d" % (l, r, n))
            x = R.randint(-10, 10)
            want = next((i for i, v in enumerate(a) if v >= x), -1)
            eq(m.first_at_least(x), want, "first >= %d in %s" % (x, a))


@test
def t17_lazy():
    L = defs(("17", 3, 1))["LazySegmentTree"]
    A = defs(("17", 3, 2))["AddMaxTree"]
    a = [1, 2, 3, 4]
    t = L(a)
    t.add(0, 1, 10)
    eq(t.query(1, 2), 15)
    for _ in range(100):
        n = R.randint(1, 15)
        a = [R.randint(-9, 9) for _ in range(n)]
        t = L(a)
        for _ in range(30):
            l = R.randrange(n)
            r = R.randrange(l, n)
            if R.random() < 0.5:
                v = R.randint(-5, 5)
                for i in range(l, r + 1):
                    a[i] += v
                t.add(l, r, v)
            else:
                eq(t.query(l, r), sum(a[l:r + 1]), "lazy sum")
        n = R.randint(1, 15)
        b = [0] * n
        mt = A(n)
        for _ in range(25):
            l = R.randrange(n)
            r = R.randrange(l, n)
            v = R.randint(-3, 4)
            for i in range(l, r + 1):
                b[i] += v
            mt.update(l, r, v)
            eq(mt.max(), max(b), "max after add")


@test
def t17_sparse():
    T = defs(("17", 4, 1))["SparseTable"]
    G = defs(("17", 4, 2))["GcdTable"]
    import math
    for _ in range(100):
        n = R.randint(1, 20)
        a = [R.randint(1, 60) for _ in range(n)]
        t, g = T(a), G(a)
        for l in range(n):
            for r in range(l, n):
                eq(t.min(l, r), min(a[l:r + 1]), "min")
                eq(g.query(l, r), math.gcd(*a[l:r + 1]), "gcd")


@test
def t17_rank_sweep():
    d = defs(("17", 5, 1))
    eq(d["count_smaller"]([5, 2, 6, 1]), [2, 1, 1, 0])
    eq(d["count_smaller"]([-1, -1]), [0, 0])
    rp = defs(("17", 5, 2))["reverse_pairs"]
    eq(rp([1, 3, 2, 3, 1]), 2)
    eq(rp([2, 4, 3, 5, 1]), 3)
    for _ in range(200):
        a = [R.randint(-8, 8) for _ in range(R.randint(1, 12))]
        eq(d["count_smaller"](a), [sum(1 for y in a[i + 1:] if y < a[i]) for i in range(len(a))], a)
        eq(rp(a), sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] > 2 * a[j]), a)


class _TN:
    def __init__(self, v, l=None, r=None):
        self.val, self.left, self.right = v, l, r


@test
def t17_lca():
    TA = defs(("17", 6, 1))["TreeAncestor"]
    eq(TA(7, [-1, 0, 0, 1, 1, 2, 2]).get_kth_ancestor(3, 1), 1)
    eq(TA(7, [-1, 0, 0, 1, 1, 2, 2]).get_kth_ancestor(5, 2), 0)
    eq(TA(7, [-1, 0, 0, 1, 1, 2, 2]).get_kth_ancestor(6, 3), -1)
    eq(TA(9, [-1, 0, 0, 1, 1, 2, 2, 3, 3]).lca(7, 6), 0)
    for _ in range(100):
        n = R.randint(1, 30)
        par = [-1] + [R.randrange(i) for i in range(1, n)]
        t = TA(n, par)

        def anc(v):
            out = []
            while v >= 0:
                out.append(v)
                v = par[v]
            return out
        for _ in range(30):
            u, v = R.randrange(n), R.randrange(n)
            au, av = anc(u), anc(v)
            sv = set(av)
            want = next(x for x in au if x in sv)
            eq(t.lca(u, v), want, "lca %d %d %s" % (u, v, par))
            k = R.randint(0, 6)
            eq(t.get_kth_ancestor(u, k), au[k] if k < len(au) else -1)
    root = _TN(3, _TN(5, _TN(6), _TN(2, _TN(7), _TN(4))), _TN(1, _TN(0), _TN(8)))
    f = defs(("17", 6, 2))["lowest_common_ancestor"]
    eq(f(root, root.left, root.right).val, 3)
    eq(f(root, root.left, root.left.right.right).val, 5)


@test
def t17_ordered():
    C = defs(("17", 7, 1))["MyCalendar"]
    c = C()
    eq([c.book(10, 20), c.book(15, 25), c.book(20, 30)], [True, False, True])
    for _ in range(100):
        c, booked = C(), []
        for _ in range(25):
            s = R.randint(0, 40)
            e = s + R.randint(1, 8)
            ok = all(e <= bs or s >= be for bs, be in booked)
            eq(c.book(s, e), ok)
            if ok:
                booked.append((s, e))
    f = defs(("17", 7, 2))["contains_nearby_almost_duplicate"]
    eq([f([1, 2, 3, 1], 3, 0), f([1, 0, 1, 1], 1, 2), f([1, 5, 9, 1, 5, 9], 2, 3)], [True, True, False])
    for _ in range(300):
        a = [R.randint(-20, 20) for _ in range(R.randint(1, 12))]
        k, t = R.randint(1, 5), R.randint(0, 6)
        want = any(abs(a[i] - a[j]) <= t for i in range(len(a)) for j in range(i + 1, min(len(a), i + k + 1)))
        eq(f(a, k, t), want, "%s %d %d" % (a, k, t))


@test
def t17_offline():
    mb = defs(("17", 8, 1))["maximum_beauty"]
    eq(mb([[1, 2], [3, 2], [2, 4], [5, 6], [3, 5]], [1, 2, 3, 4, 5, 6]), [2, 4, 5, 5, 6, 6])
    eq(mb([[1, 2], [2, 4], [3, 2], [3, 5], [5, 6]], [3, 1, 6, 2, 5, 4]), [5, 2, 6, 4, 6, 5])
    for _ in range(100):
        items = [[R.randint(1, 9), R.randint(1, 9)] for _ in range(R.randint(1, 8))]
        qs = [R.randint(0, 10) for _ in range(R.randint(1, 8))]
        eq(mb(items, qs), [max([b for p, b in items if p <= q] or [0]) for q in qs])
    dl = defs(("17", 8, 2))["distance_limited_paths_exist"]
    eq(dl(3, [[0, 1, 2], [1, 2, 4], [2, 0, 8], [1, 0, 16]], [[0, 1, 2], [0, 2, 5]]), [False, True])
    for _ in range(100):
        n = R.randint(2, 7)
        edges = [[R.randrange(n), R.randrange(n), R.randint(1, 9)] for _ in range(R.randint(0, 9))]
        qs = [[R.randrange(n), R.randrange(n), R.randint(1, 10)] for _ in range(R.randint(1, 6))]
        want = []
        for u, v, lim in qs:
            seen, st = {u}, [u]
            while st:
                x = st.pop()
                for a, b, w in edges:
                    if w < lim:
                        for p, q in ((a, b), (b, a)):
                            if p == x and q not in seen:
                                seen.add(q)
                                st.append(q)
            want.append(v in seen)
        eq(dl(n, [e[:] for e in edges], qs), want, "%d %s %s" % (n, edges, qs))


# ----------------------------------------------------------------------------- 18 design problems
@test
def t18_caches():
    L = defs(("18", 1, 1))["LFUCache"]
    c = L(2)
    out = []
    c.put(1, 1); c.put(2, 2); out.append(c.get(1)); c.put(3, 3); out.append(c.get(2)); out.append(c.get(3))
    c.put(4, 4); out += [c.get(1), c.get(3), c.get(4)]
    eq(out, [1, -1, 3, -1, 3, 4])

    class Model:
        def __init__(self, cap):
            self.cap, self.d, self.t = cap, {}, 0

        def get(self, k):
            if k not in self.d:
                return -1
            self.t += 1
            v, f, _ = self.d[k]
            self.d[k] = [v, f + 1, self.t]
            return v

        def put(self, k, v):
            if self.cap == 0:
                return
            self.t += 1
            if k in self.d:
                self.d[k] = [v, self.d[k][1] + 1, self.t]
                return
            if len(self.d) == self.cap:
                victim = min(self.d, key=lambda x: (self.d[x][1], self.d[x][2]))
                del self.d[victim]
            self.d[k] = [v, 1, self.t]
    for _ in range(200):
        cap = R.randint(0, 4)
        a, m = L(cap), Model(cap)
        for _ in range(40):
            k = R.randint(0, 5)
            if R.random() < 0.5:
                v = R.randint(0, 99)
                a.put(k, v)
                m.put(k, v)
            else:
                eq(a.get(k), m.get(k), "lfu get")
    U = defs(("18", 1, 2))["LRUCache"]
    for _ in range(100):
        cap = R.randint(1, 4)
        a, order = U(cap), []
        vals = {}
        for _ in range(40):
            k = R.randint(0, 6)
            if R.random() < 0.5:
                v = R.randint(0, 99)
                a.put(k, v)
                vals[k] = v
                if k in order:
                    order.remove(k)
                order.append(k)
                if len(order) > cap:
                    del vals[order.pop(0)]
            else:
                want = vals.get(k, -1)
                eq(a.get(k), want, "lru get")
                if k in order:
                    order.remove(k)
                    order.append(k)


@test
def t18_random_set():
    S = defs(("18", 2, 1))["RandomizedSet"]
    for _ in range(100):
        s, ref = S(), set()
        for _ in range(60):
            v = R.randint(0, 8)
            if R.random() < 0.5:
                eq(s.insert(v), v not in ref)
                ref.add(v)
            else:
                eq(s.remove(v), v in ref)
                ref.discard(v)
            eq(sorted(s.items), sorted(ref))
            eq(all(s.items[s.index[x]] == x for x in s.index), True)
            if ref:
                assert s.get_random() in ref
    W = defs(("18", 2, 2))["WeightedPicker"]
    for _ in range(100):
        w = [R.randint(1, 6) for _ in range(R.randint(1, 7))]
        p = W(w)
        flat = [i for i, x in enumerate(w) for _ in range(x)]
        for r in range(sum(w)):
            eq(p.pick_at(r), flat[r])
        assert 0 <= p.pick() < len(w)


class _Node:
    def __init__(self, val):
        self.val, self.left, self.right = val, None, None


def _insert(root, v):
    if root is None:
        return _Node(v)
    if v < root.val:
        root.left = _insert(root.left, v)
    else:
        root.right = _insert(root.right, v)
    return root


@test
def t18_iterators():
    N = defs(("18", 3, 1))["NestedIterator"]

    def flat(x):
        out = []
        for e in x:
            out += flat(e) if isinstance(e, list) else [e]
        return out

    def gen(depth):
        return [gen(depth - 1) if depth > 0 and R.random() < 0.4 else R.randint(-3, 9) for _ in range(R.randint(0, 4))]
    cases = [[[1, [2, 3]], 4, [5]], [], [[], [[]]], [[], 0, [[], 0]]]
    for _ in range(200):
        cases.append(gen(3))
    for c in cases:
        it = N(c)
        got = []
        while it.has_next():
            got.append(it.next())
        eq(got, flat(c), c)
    B = defs(("18", 3, 2))["BSTIterator"]
    for _ in range(100):
        vals = [R.randint(0, 30) for _ in range(R.randint(0, 12))]
        root = None
        for v in vals:
            root = _insert(root, v)
        it, got = B(root), []
        while it.has_next():
            got.append(it.next())
        eq(got, sorted(vals))


@test
def t18_rate_limiters():
    S = defs(("18", 4, 1))["SlidingWindowLimiter"]
    s = S(3, 10)
    eq([s.allow(t) for t in [1, 2, 3, 5, 11, 12, 13, 14]], [True, True, True, False, True, True, True, False])
    for _ in range(100):
        limit, win = R.randint(1, 4), R.randint(1, 8)
        s, allowed, t = S(limit, win), [], 0
        for _ in range(40):
            t += R.randint(0, 4)
            want = sum(1 for x in allowed if x > t - win) < limit
            eq(s.allow(t), want, "limiter")
            if want:
                allowed.append(t)
    T = defs(("18", 4, 2))["TokenBucket"]
    b = T(2, 1)
    eq([b.allow(0), b.allow(0), b.allow(0), b.allow(1), b.allow(1), b.allow(3.5), b.allow(3.5), b.allow(3.5)],
       [True, True, False, True, False, True, True, False])


@test
def t18_time_stores():
    M = defs(("18", 5, 1))["TimeMap"]
    m = M()
    m.set("foo", "bar", 1)
    eq([m.get("foo", 1), m.get("foo", 3), m.get("none", 1)], ["bar", "bar", ""])
    m.set("foo", "bar2", 4)
    eq([m.get("foo", 4), m.get("foo", 5), m.get("foo", 0)], ["bar2", "bar2", ""])
    for _ in range(100):
        m, hist, t = M(), {}, 0
        for _ in range(30):
            k = R.choice("ab")
            if R.random() < 0.5:
                t += R.randint(1, 3)
                v = "v%d" % t
                m.set(k, v, t)
                hist.setdefault(k, []).append((t, v))
            else:
                q = R.randint(0, t + 2)
                want = ""
                for ts, v in hist.get(k, []):
                    if ts <= q:
                        want = v
                eq(m.get(k, q), want)
    SA = defs(("18", 5, 2))["SnapshotArray"]
    s = SA(3)
    s.set(0, 5)
    eq(s.snap(), 0)
    s.set(0, 6)
    eq([s.get(0, 0), s.get(1, 0)], [5, 0])
    for _ in range(100):
        n = R.randint(1, 4)
        s, cur, snaps = SA(n), [0] * n, []
        for _ in range(30):
            r = R.random()
            if r < 0.5:
                i, v = R.randrange(n), R.randint(0, 9)
                s.set(i, v)
                cur[i] = v
            elif r < 0.7:
                eq(s.snap(), len(snaps))
                snaps.append(cur[:])
            elif snaps:
                sid, i = R.randrange(len(snaps)), R.randrange(n)
                eq(s.get(i, sid), snaps[sid][i])


@test
def t18_feed():
    T = defs(("18", 6, 1))["Twitter"]
    t = T()
    t.post_tweet(1, 5)
    eq(t.get_news_feed(1), [5])
    t.follow(1, 2)
    t.post_tweet(2, 6)
    eq(t.get_news_feed(1), [6, 5])
    t.unfollow(1, 2)
    eq(t.get_news_feed(1), [5])
    for _ in range(100):
        t = T()
        posts, follow, tid = [], {u: set() for u in range(4)}, 0
        for _ in range(40):
            r = R.random()
            u = R.randrange(4)
            if r < 0.5:
                tid += 1
                t.post_tweet(u, tid)
                posts.append((u, tid))
            elif r < 0.65:
                v = R.randrange(4)
                t.follow(u, v)
                follow[u].add(v)
            elif r < 0.8:
                v = R.randrange(4)
                t.unfollow(u, v)
                follow[u].discard(v)
            else:
                vis = follow[u] | {u}
                want = [i for (w, i) in reversed(posts) if w in vis][:10]
                eq(t.get_news_feed(u), want, "feed")
    Lb = defs(("18", 6, 2))["Leaderboard"]
    lb = Lb()
    for i, s in [(1, 73), (2, 56), (3, 39), (4, 51), (5, 4)]:
        lb.add_score(i, s)
    eq(lb.top(1), 73)
    lb.reset(1)
    lb.reset(2)
    lb.add_score(2, 51)
    eq(lb.top(3), 141)


@test
def t18_frequency_stack():
    F = defs(("18", 7, 1))["FreqStack"]
    f = F()
    for x in [5, 7, 5, 7, 4, 5]:
        f.push(x)
    eq([f.pop() for _ in range(4)], [5, 7, 5, 4])
    for _ in range(150):
        f, items = F(), []
        for _ in range(40):
            if items and R.random() < 0.45:
                cnt = {}
                for x in items:
                    cnt[x] = cnt.get(x, 0) + 1
                mx = max(cnt.values())
                idx = max(i for i, x in enumerate(items) if cnt[x] == mx)
                want = items.pop(idx)
                eq(f.pop(), want, "freq pop")
            else:
                x = R.randint(0, 4)
                f.push(x)
                items.append(x)
    U = defs(("18", 7, 2))["UndergroundSystem"]
    u = U()
    u.check_in(45, "Leyton", 3)
    u.check_in(32, "Paradise", 8)
    u.check_in(27, "Leyton", 10)
    u.check_out(45, "Waterloo", 15)
    u.check_out(27, "Waterloo", 20)
    u.check_out(32, "Cambridge", 22)
    eq(u.get_average_time("Paradise", "Cambridge"), 14.0)
    eq(u.get_average_time("Leyton", "Waterloo"), 11.0)


@test
def t18_editor():
    E = defs(("18", 8, 1))["TextEditor"]
    e = E()
    e.add_text("leetcode")
    eq(e.delete_text(4), 4)
    e.add_text("practice")
    eq(e.cursor_right(3), "etpractice")
    eq(e.cursor_left(8), "leet")
    eq(e.delete_text(10), 4)
    eq(e.cursor_left(2), "")
    eq(e.cursor_right(6), "practi")
    for _ in range(150):
        e, text, cur = E(), "", 0
        for _ in range(40):
            r = R.random()
            if r < 0.3:
                s = "".join(R.choice("abc") for _ in range(R.randint(1, 4)))
                e.add_text(s)
                text = text[:cur] + s + text[cur:]
                cur += len(s)
            elif r < 0.5:
                k = R.randint(0, 5)
                d = min(k, cur)
                eq(e.delete_text(k), d)
                text = text[:cur - d] + text[cur:]
                cur -= d
            elif r < 0.75:
                cur = max(0, cur - R.randint(0, 5)) if False else cur
                k = R.randint(0, 5)
                cur = max(0, cur - k)
                eq(e.cursor_left(k), text[max(0, cur - 10):cur])
            else:
                k = R.randint(0, 5)
                cur = min(len(text), cur + k)
                eq(e.cursor_right(k), text[max(0, cur - 10):cur])
    B = defs(("18", 8, 2))["BrowserHistory"]
    b = B("leetcode.com")
    b.visit("google.com")
    b.visit("facebook.com")
    b.visit("youtube.com")
    eq([b.back(1), b.back(1), b.forward(1)], ["facebook.com", "google.com", "facebook.com"])
    b.visit("linkedin.com")
    eq([b.forward(2), b.back(2), b.back(7)], ["linkedin.com", "google.com", "leetcode.com"])
