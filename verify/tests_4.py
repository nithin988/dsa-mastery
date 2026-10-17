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
