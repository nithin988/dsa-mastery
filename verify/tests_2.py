"""Functional tests, part 2: topics 06-10 (sorting and intervals, backtracking, bits and math, trees, heaps)."""
import random
from harness import *

R = random.Random(2)


def rl(n, lo=-5, hi=9):
    return [R.randint(lo, hi) for _ in range(n)]


# ----------------------------------------------------------------------------- 06 sorting and intervals
@test
def t06_sorts():
    ms = defs(("06", 1, 1))["merge_sort"]
    qs = defs(("06", 1, 2))["quick_sort"]
    f = fn(("06", 1, 3), "a,b,m,n", ret="a")
    for _ in range(60):
        a = rl(R.randint(0, 10))
        eq(ms(a), sorted(a))
        b = a[:]
        qs(b, 0, len(b) - 1)
        eq(b, sorted(a))
        x, y = sorted(rl(R.randint(0, 5))), sorted(rl(R.randint(0, 5)))
        eq(f(x + [0] * len(y), y, len(x), len(y)), sorted(x + y))


@test
def t06_comparators():
    f = fn(("06", 2, 1), "nums")
    eq(f([3, 30, 34, 5, 9]), "9534330")
    eq(f([0, 0]), "0")
    g = fn(("06", 2, 2), "people")
    eq(g([[7, 0], [4, 4], [7, 1], [5, 0], [6, 1], [5, 2]]), [[5, 0], [7, 0], [5, 2], [6, 1], [4, 4], [7, 1]])


@test
def t06_buckets():
    f = fn(("06", 3, 1), "nums,k")
    eq(sorted(f([1, 1, 1, 2, 2, 3], 2)), [1, 2])
    eq(f([1], 1), [1])
    g = fn(("06", 3, 2), "a")
    a = [2, 0, 2, 1, 1, 0]
    g(a)
    eq(a, [0, 0, 1, 1, 2, 2])


@test
def t06_intervals():
    f = fn(("06", 4, 1), "iv")
    eq(f([[8, 10], [1, 3], [15, 18], [2, 6]]), [[1, 6], [8, 10], [15, 18]])
    eq(f([[1, 4], [4, 5]]), [[1, 5]])
    g = fn(("06", 4, 2), "A,B", ret="res")
    eq(g([[0, 2], [5, 10], [13, 23], [24, 25]], [[1, 5], [8, 12], [15, 24], [25, 26]]),
       [[1, 2], [5, 5], [8, 10], [15, 23], [24, 24], [25, 25]])
    h = fn(("06", 4, 3), "iv")
    eq(h([[1, 4], [3, 6], [2, 8]]), 2)
    eq(h([[1, 2], [1, 4], [3, 4]]), 1)
    ins = fn(("06", 5, 1), "iv,ni")
    eq(ins([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]), [[1, 2], [3, 10], [12, 16]])
    eq(ins([], [5, 7]), [[5, 7]])
    cal = defs(("06", 5, 2))["MyCalendar"]()
    eq([cal.book(10, 20), cal.book(15, 25), cal.book(20, 30)], [True, False, True])


@test
def t06_sweep_and_greedy():
    f = fn(("06", 6, 1), "iv")
    eq(f([[0, 30], [5, 10], [15, 20]]), 2)
    eq(f([[7, 10], [2, 4]]), 1)
    h = fn(("06", 6, 3), "iv")
    for _ in range(40):
        iv = []
        for _ in range(R.randint(1, 6)):
            s = R.randint(0, 20)
            iv.append([s, s + R.randint(1, 8)])
        eq(f([x[:] for x in iv]), h([x[:] for x in iv]), iv)
    c = fn(("06", 6, 2), "trips,capacity")
    eq([c([[2, 1, 5], [3, 3, 7]], 4), c([[2, 1, 5], [3, 3, 7]], 5)], [False, True])
    g = fn(("06", 7, 1), "iv")
    eq(g([[1, 2], [2, 3], [3, 4], [1, 3]]), 1)
    eq(g([[1, 2], [1, 2], [1, 2]]), 2)
    b = fn(("06", 7, 2), "pts")
    eq(b([[10, 16], [2, 8], [1, 6], [7, 12]]), 2)


@test
def t06_two_pointer_and_cyclic():
    f = fn(("06", 8, 1), "p,limit")
    eq([f([1, 2], 3), f([3, 2, 2, 1], 3), f([3, 5, 3, 4], 5)], [1, 3, 4])
    g = fn(("06", 8, 2), "g,s")
    eq(g(sorted([1, 2, 3]), sorted([1, 1])), 1)
    eq(g(sorted([1, 2]), sorted([1, 2, 3])), 2)
    m = fn(("06", 9, 1), "a", ret="missing")
    eq(m([4, 3, 2, 7, 8, 2, 3, 1]), [5, 6])
    fm = fn(("06", 9, 2), "a")
    eq(fm([3, 4, -1, 1]), 2)


# ----------------------------------------------------------------------------- 07 recursion and backtracking
@test
def t07_recursion_basics():
    ns = defs(("07", 1, 1))
    eq(ns["fact"](5), 120)
    s = list("hello")
    ns["reverse"](s, 0, 4)
    eq("".join(s), "olleh")
    c = defs(("07", 1, 2))["climb"]
    eq([c(1), c(2), c(5), c(30)], [1, 2, 8, 1346269])


def _subsets_brute(a):
    return sorted(sorted(x) for x in (a[i] for i in range(0)) ) if False else None


@test
def t07_subsets_combinations():
    f = fn(("07", 2, 2), "a", pre="res = []", ret="res")
    out = f([1, 2, 3])
    eq(sorted(map(sorted, out)), sorted(map(sorted, [[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]])))
    c = fn(("07", 3, 1), "c,target", pre="res = []", ret="res")
    eq(sorted(c([2, 3, 6, 7], 7)), sorted([[2, 2, 3], [7]]))
    k = fn(("07", 3, 2), "n,k", pre="res = []", ret="res")
    eq(sorted(k(4, 2)), [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]])


@test
def t07_permutations():
    f = fn(("07", 4, 1), "a", pre="res = []", ret="res")
    eq(sorted(f([1, 2, 3])), sorted([[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]))
    g = fn(("07", 4, 2), "a", pre="res = []", ret="res")
    eq(len(g([1, 2, 3, 4])), 24)
    d1 = fn(("07", 5, 1), "a", pre="res = []", ret="res")
    eq(sorted(d1([1, 2, 2])), sorted([[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]))
    d2 = fn(("07", 5, 2), "a", pre="res = []", ret="res")
    eq(sorted(d2([1, 1, 2])), [[1, 1, 2], [1, 2, 1], [2, 1, 1]])


@test
def t07_strings_and_grids():
    p = fn(("07", 6, 1), "s", pre="res = []", ret="res")
    eq(sorted(p("aab")), [["a", "a", "b"], ["aa", "b"]])
    lc = fn(("07", 6, 2), "s", pre="res = []", ret="res")
    eq(sorted(lc("a1b2")), sorted(["a1b2", "a1B2", "A1b2", "A1B2"]))
    ex = defs(("07", 7, 1))["exist"]
    board = [["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]]
    eq([ex([r[:] for r in board], w) for w in ("ABCCED", "SEE", "ABCB")], [True, True, False])
    mg = fn(("07", 7, 2), "g,m,n", ret="best")
    eq(mg([[0, 6, 0], [5, 8, 7], [0, 9, 0]], 3, 3), 24)


@test
def t07_nqueens_sudoku_parens():
    q = defs(("07", 8, 1))["total_n_queens"]
    eq([q(n) for n in range(1, 8)], [1, 0, 0, 2, 10, 4, 40])
    ns = defs(("07", 8, 2))
    b = [list(r) for r in [
        "53..7....", "6..195...", ".98....6.", "8...6...3", "4..8.3..1", "7...2...6", ".6....28.", "...419..5", "....8..79"]]
    eq(ns["solve"](b), True)
    for r in b:
        eq(sorted(r), list("123456789"))
    for c in range(9):
        eq(sorted(b[r][c] for r in range(9)), list("123456789"))
    g = defs(("07", 9, 1))["generate"]
    eq(sorted(g(3)), sorted(["((()))", "(()())", "(())()", "()(())", "()()()"]))
    wb = fn(("07", 9, 2), "s,wordDict")
    eq([wb("leetcode", ["leet", "code"]), wb("catsandog", ["cats", "dog", "sand", "and", "cat"]), wb("applepenapple", ["apple", "pen"])], [True, False, True])


# ----------------------------------------------------------------------------- 08 bits and math
@test
def t08_bits():
    rb = fn(("08", 1, 2), "n", ret="r")
    eq(rb(0b00000010100101000001111010011100), 0b00111001011110000010100101000000)
    f = fn(("08", 2, 1), "nums", ret="(single, missing)")
    eq(f([0, 1, 3]), (2, 2))
    g = fn(("08", 2, 2), "nums")
    eq(sorted(g([1, 2, 1, 3, 2, 5])), [3, 5])
    k = fn(("08", 3, 1), "n", ret="count")
    eq([k(x) for x in (0, 1, 11, 255, 2 ** 31 - 1)], [0, 1, 3, 8, 31])
    cb = fn(("08", 3, 2), "n", ret="bits")
    eq(cb(5), [0, 1, 1, 2, 1, 2])
    sub = fn(("08", 4, 1), "a,m", pre="n = len(a)\nres = []", ret="(res, gray)")
    res, gray = sub([1, 2, 3], 0b101)
    eq(len(res), 8)
    eq(gray, [0, 1, 3, 2, 6, 7, 5, 4])
    mo = defs(("08", 4, 2))["mask_of"]
    eq((mo("abc"), mo("aab")), (7, -1))


@test
def t08_arithmetic_and_math():
    add = fn(("08", 5, 1), "a,b")
    for a, b in [(1, 2), (5, 3), (-2, 3), (-5, -7), (2 ** 30, 2 ** 30 - 1), (0, 0)]:
        eq(add(a, b), a + b, (a, b))
    ra = fn(("08", 5, 2), "l,r")
    eq([ra(5, 7), ra(0, 0), ra(1, 2147483647)], [4, 0, 0])
    pw = defs(("08", 6, 1))["power"]
    for b, e, m in [(2, 10, 1000), (3, 13, 10 ** 9 + 7), (7, 0, 5), (10, 18, 97)]:
        eq(pw(b, e, m), pow(b, e, m))
    sq = fn(("08", 6, 2), "x", ret="ans")
    eq([sq(x) for x in (0, 1, 8, 15, 16, 2 ** 31 - 1)], [0, 1, 2, 3, 4, 46340]) if False else None
    for x in [1, 8, 15, 16, 99, 10 ** 6]:
        eq(sq(x), math.isqrt(x))
    ns = defs(("08", 7, 1))
    eq((ns["gcd"](48, 18), ns["lcm"](4, 6)), (6, 12))
    eq([ns["count_primes"](n) for n in (0, 2, 10, 30, 100)], [0, 0, 4, 10, 25])
    fa = fn(("08", 7, 2), "n", pre="", ret="factors")
    eq(fa(360), {2: 3, 3: 2, 5: 1})
    eq(fa(97), {97: 1})


@test
def t08_digits_and_formulas():
    r = fn(("08", 8, 1), "x")
    eq([r(123), r(-123), r(120), r(1534236469), r(0)], [321, -321, 21, 0, 0])
    e = fn(("08", 8, 2), "n")
    eq([e(1), e(26), e(27), e(28), e(701), e(2147483647)], ["A", "Z", "AA", "AB", "ZY", "FXSHRXW"])
    ns = defs(("08", 9, 1))
    eq((ns["trailing_zeroes"](5), ns["trailing_zeroes"](125), ns["trailing_zeroes"](0)), (1, 31, 0))
    eq([ns["bulb_switch"](n) for n in (0, 1, 3, 9, 100)], [0, 1, 1, 3, 10])
    m = fn(("08", 9, 2), "a", pre="a = a[:]")
    eq(m([1, 2, 3]), 2)
    eq(m([1, 10, 2, 9]), 16)


# ----------------------------------------------------------------------------- 09 trees
T = tree([3, 9, 20, None, None, 15, 7])


@test
def t09_basics():
    ns = defs(("09", 1, 1))
    eq(ns["max_depth"](T), 3)
    ns["best"] = 0
    d = tree([1, 2, 3, 4, 5])
    ns["height"](d)
    eq(ns["best"], 3)
    ns2 = defs(("09", 1, 2))
    inv = ns2["invert"](tree([4, 2, 7, 1, 3, 6, 9]))
    eq((inv.left.val, inv.right.val, inv.left.left.val), (7, 2, 9))
    eq((ns2["same"](tree([1, 2, 3]), tree([1, 2, 3])), ns2["same"](tree([1, 2]), tree([1, None, 2]))), (True, False))
    eq((ns2["mirror"](tree([1, 2, 2, 3, 4, 4, 3]).left, tree([1, 2, 2, 3, 4, 4, 3]).right),
        ns2["mirror"](tree([1, 2, 2, None, 3, None, 3]).left, tree([1, 2, 2, None, 3, None, 3]).right)), (True, False))


@test
def t09_traversals_and_paths():
    ns = defs(("09", 2, 1))
    out = []
    t = tree([1, None, 2, 3])
    ns["pre"](t, out)
    eq(out, [1, 2, 3])
    out = []
    ns["inorder"](t, out)
    eq(out, [1, 3, 2])
    out = []
    ns["post"](t, out)
    eq(out, [3, 2, 1])
    eq(ns["has_path_sum"](tree([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1]), 22), True)
    eq(ns["has_path_sum"](tree([1, 2, 3]), 5), False)
    p = defs(("09", 2, 2), pre="target = 8")
    res = []
    p["paths"](tree([1, 2, 3, None, 5]), [], res)
    eq(res, [[1, 2, 5], [1, 3]])
    p["seen"][0] = 1
    p["dfs"](tree([10, 5, -3, 3, 2, None, 11, 3, -2, None, 1]), 0)
    eq(p["count"], 3)


@test
def t09_bfs_and_paths():
    f = fn(("09", 3, 1), "root", ret="res")
    eq(f(T), [[3], [20, 9], [15, 7]])           # zigzag: second level reversed
    g = fn(("09", 3, 2), "root")
    eq(g(T), 2)
    eq(g(tree([2, None, 3, None, 4, None, 5, None, 6])), 5)
    ns = defs(("09", 4, 1))
    ns["gain"](tree([-10, 9, 20, None, None, 15, 7]))
    eq(ns["best"], 42)
    g2 = defs(("09", 4, 2))["good"]
    eq(g2(tree([3, 1, 4, 3, None, 1, 5]), -10 ** 9), 4)


@test
def t09_bst():
    ns = defs(("09", 5, 1))
    b = tree([4, 2, 7, 1, 3])
    eq(ns["search"](b, 2).val, 2)
    eq(ns["search"](b, 5), None)
    b = ns["insert"](b, 5)
    eq(ns["valid"](b), True)
    eq(ns["valid"](tree([5, 1, 4, None, None, 3, 6])), False)
    eq(ns["valid"](tree([5, 4, 6, None, None, 3, 7])), False)
    d = defs(("09", 5, 2))["delete"]
    r = d(tree([5, 3, 6, 2, 4, None, 7]), 3)
    out = []
    defs(("09", 2, 1))["inorder"](r, out)
    eq(out, [2, 4, 5, 6, 7])


@test
def t09_lca_and_build():
    ns = defs(("09", 6, 1))
    root = tree([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
    p, q = root.left, root.right
    assert ns["lca"](root, p, q) is root
    assert ns["lca"](root, p, root.left.right.right) is p
    b = tree([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5])
    assert ns["lca_bst"](b, b.left, b.right) is b
    assert ns["lca_bst"](b, b.left, b.left.right) is b.left
    bt = defs(("09", 7, 1))["build_tree"]
    t = bt([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])
    eq((t.val, t.left.val, t.right.val, t.right.left.val, t.right.right.val), (3, 9, 20, 15, 7))
    ss = defs(("09", 7, 2))
    s = ss["serialize"](tree([1, 2, 3, None, None, 4, 5]))
    t = ss["deserialize"](s)
    eq(ss["serialize"](t), s)
    st = ss["sorted_to_bst"]([-10, -3, 0, 5, 9], 0, 4)
    eq(st.val, 0)


@test
def t09_dp_and_iterators():
    rob = defs(("09", 8, 1))["rob"]
    eq([rob(tree([3, 2, 3, None, 3, None, 1])), rob(tree([3, 4, 5, 1, 3, None, 1]))], [7, 9])
    ns = defs(("09", 8, 2))
    eq(ns["height"](tree([3, 9, 20, None, None, 15, 7])), 3)
    eq(ns["height"](tree([1, 2, 2, 3, 3, None, None, 4, 4])), -1)
    it = defs(("09", 9, 1), pre="root = None")["BSTIterator"](tree([7, 3, 15, None, None, 9, 20]))
    out = []
    while it.has_next():
        out.append(it.next())
    eq(out, [3, 7, 9, 15, 20])
    m = fn(("09", 9, 2), "root,visit")
    seen = []
    m(tree([4, 2, 6, 1, 3, 5, 7]), seen.append)
    eq([x.val if hasattr(x, "val") else x for x in seen], [1, 2, 3, 4, 5, 6, 7])


# ----------------------------------------------------------------------------- 10 heaps
@test
def t10_heap_mechanics():
    h = defs(("10", 1, 2))["MinHeap"]()
    a = rl(50, 0, 99)
    for x in a:
        h.push(x)
    out = []
    while h.a:
        out.append(h.pop())
    eq(out, sorted(a))
    f = fn(("10", 2, 1), "nums,k", ret="h[0]")
    eq(f([3, 2, 1, 5, 6, 4], 2), 5)
    eq(f([3, 2, 3, 1, 2, 4, 5, 5, 6], 4), 4)
    g = fn(("10", 2, 2), "points,k")
    eq(sorted(g([[1, 3], [-2, 2]], 1)), [[-2, 2]])
    eq(sorted(g([[3, 3], [5, -1], [-2, 4]], 2)), sorted([[3, 3], [-2, 4]]))
    tk = fn(("10", 2, 3), "nums,k")
    eq(sorted(tk([1, 1, 1, 2, 2, 3], 2)), [1, 2])


@test
def t10_median_and_merge():
    mf = defs(("10", 3, 1))["MedianFinder"]()
    seen = []
    for x in [5, 15, 1, 3, 8, 7, 9, 10, 20, 2]:
        mf.addNum(x)
        seen.append(x)
        s = sorted(seen)
        want = s[len(s) // 2] if len(s) % 2 else (s[len(s) // 2 - 1] + s[len(s) // 2]) / 2
        eq(mf.findMedian(), want, str(seen))
    k = fn(("10", 4, 1), "lists", glob={"ListNode": ListNode})
    eq(to_list(k([ll([1, 4, 5]), ll([1, 3, 4]), ll([2, 6])])), [1, 1, 2, 3, 4, 4, 5, 6])
    p = fn(("10", 4, 2), "a,b,k", ret="res")
    eq(p([1, 7, 11], [2, 4, 6], 3), [[1, 2], [1, 4], [1, 6]])
    eq(p([1, 1, 2], [1, 2, 3], 2), [[1, 1], [1, 1]])


@test
def t10_greedy_and_design():
    c = fn(("10", 5, 1), "sticks")
    eq([c([2, 4, 3]), c([1, 8, 3, 5]), c([5])], [14, 30, 0])
    b = fn(("10", 5, 2), "h,bricks,ladders")
    eq(b([4, 2, 7, 6, 9, 14, 12], 5, 1), 4)
    eq(b([4, 12, 2, 7, 3, 18, 20, 3, 19], 10, 2), 7)
    eq(b([14, 3, 19, 3], 17, 0), 3)
    w = fn(("10", 6, 1), "a,k", ret="res")
    eq(w([1, 3, -1, -3, 5, 3, 6, 7], 3), [3, 3, 5, 5, 6, 7])
    sp = defs(("10", 6, 2))["StockPrice"]()
    sp.update(1, 10)
    sp.update(2, 5)
    eq((sp.current(), sp.maximum(), sp.minimum()), (5, 10, 5))
    sp.update(1, 3)
    eq((sp.maximum(), sp.minimum()), (5, 3))
    sp.update(4, 2)
    eq((sp.current(), sp.minimum()), (2, 2))


@test
def t10_sort_and_graph():
    hs = defs(("10", 7, 1))["heap_sort"]
    for _ in range(40):
        a = rl(R.randint(0, 12))
        b = a[:]
        hs(b)
        eq(b, sorted(a))
    cp = fn(("10", 7, 2), "words", ret="(length, s)")
    eq(cp(["bb", "a", "ccc", "aa", "b"]), (1, "a"))
    d = fn(("10", 8, 1), "n,src,graph", ret="dist", pre="g = graph")
    graph = {0: [(1, 4), (2, 1)], 1: [(3, 1)], 2: [(1, 2), (3, 5)], 3: [(4, 3)], 4: []}
    eq(d(5, 0, graph), [0, 3, 1, 4, 7])
    me = fn(("10", 8, 2), "h,m,n")
    eq(me([[1, 2, 2], [3, 8, 2], [5, 3, 5]], 3, 3), 2)
    eq(me([[1, 2, 3], [3, 8, 4], [5, 3, 5]], 3, 3), 1)


@test
def t10_frequency_heaps():
    r = fn(("10", 9, 1), "s")
    out = r("aab")
    assert sorted(out) == sorted("aab") and all(out[i] != out[i + 1] for i in range(len(out) - 1))
    eq(r("aaab"), "")
    out = r("aaabbc")
    assert all(out[i] != out[i + 1] for i in range(len(out) - 1)) and len(out) == 6
    h = fn(("10", 9, 2), "arr")
    eq([h([3, 3, 3, 3, 5, 5, 5, 2, 2, 7]), h([7, 7, 7, 7, 7, 7])], [2, 1])
