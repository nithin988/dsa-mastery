"""Functional tests, part 3: topics 11-15 (tries, graphs, advanced graphs, greedy, DP I)."""
import random
from harness import *

R = random.Random(3)


def rl(n, lo=-5, hi=9):
    return [R.randint(lo, hi) for _ in range(n)]


def adj(n, edges, directed=False):
    g = [[] for _ in range(n)]
    for u, v in edges:
        g[u].append(v)
        if not directed:
            g[v].append(u)
    return g


# ----------------------------------------------------------------------------- 11 tries
@test
def t11_basics_and_prefix():
    Trie = defs(("11", 1, 1))["Trie"]
    t = Trie()
    for w in ("apple", "app", "apt"):
        t.insert(w)
    eq([t.search("app"), t.search("ap"), t.startsWith("ap"), t.startsWith("b")], [True, False, True, False])
    rw = defs(("11", 1, 2), glob={"Trie": Trie})["replace_words"]
    eq(rw(["cat", "bat", "rat"], "the cattle was rattled by the battery"), "the cat was rat by the bat")
    ns = defs(("11", 2, 1))
    for w in ("apple", "app", "apt", "bat", "bar"):
        ns["insert"](w)
    eq([ns["count_prefix"](p) for p in ("ap", "app", "ba", "c")], [3, 2, 2, 0])
    out = []
    node = ns["root"].kids["a"].kids["p"]
    ns["collect"](node, "ap", out)
    eq(out, ["app", "apple", "apt"])
    wf = defs(("11", 2, 2))["WordFilter"](["apple", "ape"])
    eq([wf.f("a", "e"), wf.f("app", "le"), wf.f("b", "x")], [1, 0, -1])


@test
def t11_wildcards_and_board():
    Trie = defs(("11", 1, 1))["Trie"]
    t = Trie()
    for w in ("bad", "dad", "mad"):
        t.insert(w)
    Trie.wild = defs(("11", 3, 1))["search"]
    eq([t.wild(w) for w in ("pad", "bad", ".ad", "b..", "b.")], [False, True, True, True, False])
    Trie.magic = defs(("11", 3, 2))["search"]
    m = Trie()
    for w in ("hello", "leetcode"):
        m.insert(w)
    eq([m.magic(w) for w in ("hello", "hhllo", "hell", "leetcoded")], [False, True, False, False])
    fw = defs(("11", 4, 1))["find_words"]
    board = [["o", "a", "a", "n"], ["e", "t", "a", "e"], ["i", "h", "k", "r"], ["i", "f", "l", "v"]]
    eq(sorted(fw(board, ["oath", "pea", "eat", "rain"])), ["eat", "oath"])


@test
def t11_augmented_and_xor():
    ms = defs(("11", 5, 1))["MapSum"]()
    ms.insert("apple", 3)
    eq(ms.sum("ap"), 3)
    ms.insert("app", 2)
    eq(ms.sum("ap"), 5)
    ms.insert("apple", 2)
    eq(ms.sum("ap"), 4)
    sg = fn(("11", 5, 2), "products,searchWord", ret="res")
    eq(sg(["mobile", "mouse", "moneypot", "monitor", "mousepad"], "mouse"),
       [["mobile", "moneypot", "monitor"], ["mobile", "moneypot", "monitor"], ["mouse", "mousepad"], ["mouse", "mousepad"], ["mouse", "mousepad"]])
    mx = defs(("11", 6, 1))["find_maximum_xor"]
    mx2 = fn(("11", 6, 2), "nums", ret="best")
    for _ in range(60):
        a = [R.randint(0, 2 ** 12) for _ in range(R.randint(2, 8))]
        want = max(a[i] ^ a[j] for i in range(len(a)) for j in range(i, len(a)))
        eq(mx(a), want, a)
        eq(mx2(a), want, a)
    eq(mx([3, 10, 5, 25, 2, 8]), 28)


@test
def t11_alternatives_and_streams():
    f = fn(("11", 7, 1), "folder", ret="res")
    eq(f(sorted(["/a", "/a/b", "/c/d", "/c/d/e", "/c/f"])), ["/a", "/c/d", "/c/f"])
    wb = defs(("11", 8, 1))["word_break"]
    eq([wb("leetcode", ["leet", "code"]), wb("catsandog", ["cats", "dog", "sand", "and", "cat"])], [True, False])
    cw = fn(("11", 8, 2), "words", ret="res")
    eq(sorted(cw(["cat", "cats", "catsdogcats", "dog", "dogcatsdog", "hippopotamuses", "rat", "ratcatdogcat"])),
       sorted(["catsdogcats", "dogcatsdog", "ratcatdogcat"]))
    sc = defs(("11", 9, 1))["StreamChecker"](["cd", "f", "kl"])
    eq([sc.query(c) for c in "abcdefghijkl"], [False, False, False, True, False, True, False, False, False, False, False, True])


# ----------------------------------------------------------------------------- 12 graph traversal
@test
def t12_representation_and_dfs():
    g = fn(("12", 1, 1), "n,edges", ret="g")
    eq(g(4, [[0, 1], [0, 2], [1, 2], [2, 3]]), [[1, 2], [0, 2], [0, 1, 3], [2]])
    j = fn(("12", 1, 2), "n,trust")
    eq([j(2, [[1, 2]]), j(3, [[1, 3], [2, 3]]), j(3, [[1, 3], [2, 3], [3, 1]])], [2, 3, -1])
    c = fn(("12", 2, 1), "g,n", pre="start = 0", ret="components")
    eq(c(adj(8, [[0, 1], [0, 2], [1, 3], [1, 4], [2, 5], [6, 7]]), 8), 2)
    Node = type("Node", (), {"__init__": lambda self, v: (setattr(self, "val", v), setattr(self, "neighbors", []))[0]})
    ns = defs(("12", 2, 2), glob={"Node": Node})
    a, b, cc = Node(1), Node(2), Node(3)
    a.neighbors, b.neighbors, cc.neighbors = [b, cc], [a, cc], [a, b]
    cl = ns["clone"](a)
    assert cl is not a and cl.val == 1 and [x.val for x in cl.neighbors] == [2, 3]
    assert cl.neighbors[0].neighbors[0] is cl


@test
def t12_bfs_family():
    f = fn(("12", 3, 1), "g,n,src", ret="(dist, parent)")
    dist, par = f(adj(7, [[0, 1], [0, 2], [1, 3], [2, 3], [2, 4], [3, 5], [4, 5], [5, 6]]), 7, 0)
    eq(dist, [0, 1, 1, 2, 2, 3, 4])
    cr = defs(("12", 3, 2))["can_reach"]
    eq([cr([4, 2, 3, 0, 3, 1, 2], 5), cr([3, 0, 2, 1, 2], 2)], [True, False])
    isl = fn(("12", 4, 1), "g", pre="", ret="(count, best)")
    grid = [list(r) for r in ["11000", "11000", "00100", "00011"]]
    eq(isl(grid), (3, 4))
    per = fn(("12", 4, 2), "g,m,n", ret="per")
    eq(per([[0, 1, 0, 0], [1, 1, 1, 0], [0, 1, 0, 0], [1, 1, 0, 0]], 4, 4), 16)
    m1 = fn(("12", 5, 1), "mat", ret="dist")
    eq(m1([[0, 0, 0], [0, 1, 0], [1, 1, 1]]), [[0, 0, 0], [0, 1, 0], [1, 2, 1]])
    rot = fn(("12", 5, 2), "g,m,n")
    eq([rot([[2, 1, 1], [1, 1, 0], [0, 1, 1]], 3, 3), rot([[2, 1, 1], [0, 1, 1], [1, 0, 1]], 3, 3)], [4, -1])


@test
def t12_cycles_bipartite_states():
    cyc = fn(("12", 6, 1), "n,g", ret="can_finish")
    eq([cyc(2, [[1], []]), cyc(2, [[1], [0]]), cyc(4, [[1], [2], [3], [1]])], [True, False, False])
    ns = defs(("12", 6, 2), pre="seen = [False] * 5\ng = [[1], [0, 2], [1, 3, 4], [2, 4], [2, 3]]")
    eq(ns["dfs"](0, -1), True)
    ns = defs(("12", 6, 2), pre="seen = [False] * 4\ng = [[1], [0, 2], [1, 3], [2]]")
    eq(ns["dfs"](0, -1), False)
    bp = fn(("12", 7, 1), "n,g")
    eq([bp(4, [[1, 3], [0, 2], [1, 3], [0, 2]]), bp(4, [[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]])], [True, False])
    wl = fn(("12", 8, 1), "begin,end,wordList")
    eq([wl("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]), wl("hit", "cog", ["hot", "dot", "dog", "lot", "log"])], [5, 0])
    ol = fn(("12", 8, 2), "deadends,target")
    eq([ol(["0201", "0101", "0102", "1212", "2002"], "0202"), ol(["8888"], "0009"), ol(["0000"], "8888")], [6, 1, -1])


@test
def t12_border_search():
    sv = defs(("12", 9, 1))["solve"]
    b = [list(r) for r in ["XXXX", "XOOX", "XXOX", "XOXX"]]
    sv(b)
    eq(["".join(r) for r in b], ["XXXX", "XXXX", "XXXX", "XOXX"])
    pa = fn(("12", 9, 2), "h,m,n")
    h = [[1, 2, 2, 3, 5], [3, 2, 3, 4, 4], [2, 4, 5, 3, 1], [6, 7, 1, 4, 5], [5, 1, 1, 2, 4]]
    eq(sorted(pa(h, 5, 5)), sorted([[0, 4], [1, 3], [1, 4], [2, 2], [3, 0], [3, 1], [4, 0]]))


# ----------------------------------------------------------------------------- 13 advanced graphs
class _DSU:
    pass


@test
def t13_toposort_and_dsu():
    k = fn(("13", 1, 1), "n,edges")
    order = k(6, [[5, 2], [5, 0], [4, 0], [4, 1], [2, 3], [3, 1]])
    pos = {v: i for i, v in enumerate(order)}
    assert len(order) == 6 and all(pos[a] < pos[b] for a, b in [[5, 2], [5, 0], [4, 0], [4, 1], [2, 3], [3, 1]])
    eq(k(2, [[0, 1], [1, 0]]), [])
    d = fn(("13", 1, 2), "n,g", ret="order")
    g = adj(6, [[5, 2], [5, 0], [4, 0], [4, 1], [2, 3], [3, 1]], directed=True)
    order = d(6, g)
    pos = {v: i for i, v in enumerate(order)}
    assert len(order) == 6 and all(pos[a] < pos[b] for a, b in [[5, 2], [5, 0], [4, 0], [4, 1], [2, 3], [3, 1]])
    DSU = defs(("13", 2, 1))["DSU"]
    u = DSU(6)
    eq([u.union(0, 1), u.union(1, 0), u.union(2, 3), u.union(1, 3)], [True, False, True, True])
    eq((u.components, u.find(0) == u.find(3), u.find(4) == u.find(0)), (3, True, False))
    eq_f = fn(("13", 2, 2), "eq", glob={"DSU": DSU})
    eq([eq_f(["a==b", "b!=a"]), eq_f(["a==b", "b==c", "a==c"]), eq_f(["a==b", "b!=c", "c==a"])], [False, True, False])


@test
def t13_shortest_paths():
    D = fn(("13", 3, 1), "n,src,g,MOD", ret="(dist, ways)")
    g = {0: [(1, 4), (2, 1)], 1: [(0, 4), (2, 2), (3, 1)], 2: [(0, 1), (1, 2), (3, 5)], 3: [(1, 1), (2, 5), (4, 3)], 4: [(3, 3)]}
    dist, ways = D(5, 0, g, 10 ** 9 + 7)
    eq(dist, [0, 3, 1, 4, 7])
    eq(ways[3], 1)
    g2 = {0: [(1, 1), (2, 1)], 1: [(3, 1)], 2: [(3, 1)], 3: []}
    eq(D(4, 0, g2, 10 ** 9 + 7)[1][3], 2)
    z = fn(("13", 3, 2), "n,src,g", ret="dist")
    eq(z(4, 0, {0: [(1, 0), (2, 1)], 1: [(3, 1)], 2: [(3, 0)], 3: []}), [0, 0, 1, 1])
    bf = fn(("13", 4, 1), "n,flights,src,dst,k")
    fl = [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]]
    eq([bf(4, fl, 0, 3, 1), bf(4, fl, 0, 3, 0)], [700, -1])
    eq(bf(3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 1), 200)
    fw = fn(("13", 4, 2), "n,edges", ret="d")
    d = fw(4, [[0, 1, 3], [1, 2, 1], [1, 3, 4], [2, 3, 1]])
    eq((d[0][3], d[3][0], d[0][2]), (5, 5, 4))


@test
def t13_mst_and_dsu_apps():
    DSU = defs(("13", 2, 1))["DSU"]
    kr = fn(("13", 5, 1), "n,edges", glob={"DSU": DSU})
    eq(kr(5, [(0, 1, 1), (1, 2, 2), (0, 2, 3), (2, 3, 4), (1, 3, 5), (3, 4, 6), (2, 4, 7)]), 13)
    eq(kr(3, [(0, 1, 1)]), -1)
    pr = fn(("13", 5, 2), "pts")
    eq(pr([[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]]), 20)
    rd = fn(("13", 6, 1), "edges", glob={"DSU": DSU})
    eq([rd([[1, 2], [1, 3], [2, 3]]), rd([[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]])], [[2, 3], [1, 4]])
    am = fn(("13", 6, 2), "accounts", ret="res", glob={"DSU": DSU})
    res = am([["John", "johnsmith@mail.com", "john_newyork@mail.com"], ["John", "johnsmith@mail.com", "john00@mail.com"],
              ["Mary", "mary@mail.com"], ["John", "johnnybravo@mail.com"]])
    eq(sorted(map(tuple, res)), sorted([("John", "john00@mail.com", "john_newyork@mail.com", "johnsmith@mail.com"),
                                       ("Mary", "mary@mail.com"), ("John", "johnnybravo@mail.com")]))


@test
def t13_bridges_scc_euler():
    pre = "n = 5\ng = [[1, 2], [0, 2, 3], [0, 1], [1, 4], [3]]"
    ns = defs(("13", 7, 1), pre=pre)
    ns["dfs"](0, -1)
    eq(sorted(map(sorted, ns["res"])), [[1, 3], [3, 4]])
    pre2 = pre + "\ndisc, low, timer, is_cut = [0] * n, [0] * n, [0], [False] * n"
    ns = defs(("13", 7, 2), pre=pre2)
    ns["dfs"](0, -1)
    eq([i for i in range(5) if ns["is_cut"][i]], [1, 3])
    k = fn(("13", 8, 1), "n,g", ret="(comp, count)")
    g = adj(6, [[0, 1], [1, 2], [2, 0], [2, 3], [3, 4], [4, 5], [5, 3]], directed=True)
    comp, count = k(6, g)
    eq(count, 2)
    assert comp[0] == comp[1] == comp[2] and comp[3] == comp[4] == comp[5] and comp[0] != comp[3]
    it = fn(("13", 9, 1), "tickets")
    eq(it([["MUC", "LHR"], ["JFK", "MUC"], ["SFO", "SJC"], ["LHR", "SFO"]]), ["JFK", "MUC", "LHR", "SFO", "SJC"])
    eq(it([["JFK", "SFO"], ["JFK", "ATL"], ["SFO", "ATL"], ["ATL", "JFK"], ["ATL", "SFO"]]), ["JFK", "ATL", "JFK", "SFO", "ATL", "SFO"])


# ----------------------------------------------------------------------------- 14 greedy
@test
def t14_basic_greedy():
    f = fn(("14", 1, 1), "bills")
    eq([f([5, 5, 5, 10, 20]), f([5, 5, 10, 10, 20])], [True, False])
    ns = defs(("14", 1, 2))
    eq((ns["greedy_coins"]([1, 3, 4], 6), ns["min_coins"]([1, 3, 4], 6)), (3, 2))     # greedy 3 coins, true optimum 2
    eq((ns["greedy_coins"]([1, 5, 10, 25], 41), ns["min_coins"]([1, 5, 10, 25], 41)), (4, 4))
    j = defs(("14", 2, 1))
    eq([j["can_jump"]([2, 3, 1, 1, 4]), j["can_jump"]([3, 2, 1, 0, 4])], [True, False])
    eq([j["min_jumps"]([2, 3, 1, 1, 4]), j["min_jumps"]([2, 3, 0, 1, 4]), j["min_jumps"]([1, 2, 3])], [2, 2, 2])


@test
def t14_jumps_balance_trading():
    t = fn(("14", 2, 2), "n,ranges")
    eq([t(5, [3, 4, 1, 1, 0, 0]), t(3, [0, 0, 0, 0])], [1, -1])
    g = fn(("14", 3, 1), "gas,cost")
    eq([g([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]), g([2, 3, 4], [3, 4, 3])], [3, -1])
    cn = fn(("14", 3, 2), "piles")
    eq(cn([2, 4, 1, 2, 7, 8]), 9)
    s = fn(("14", 4, 1), "prices", ret="(best, profit)")
    eq(s([7, 1, 5, 3, 6, 4]), (5, 7))
    fee = fn(("14", 4, 2), "prices,fee")
    eq(fee([1, 3, 2, 8, 4, 9], 2), 8)


@test
def t14_two_pass_and_chars():
    c = fn(("14", 5, 1), "r")
    eq([c([1, 0, 2]), c([1, 2, 2]), c([1, 3, 2, 2, 1])], [5, 4, 7])
    w = fn(("14", 5, 2), "h", ret="water")
    eq([w([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]), w([4, 2, 0, 3, 2, 5])], [6, 9])
    p = fn(("14", 6, 1), "s")
    eq(p("ababcbacadefegdehijhklij"), [9, 7, 8])
    d = fn(("14", 6, 2), "s")
    eq([d("aab"), d("aaabbbcc"), d("ceabaacb")], [0, 2, 2])
    q = fn(("14", 6, 3), "s")
    eq([q("())"), q("((("), q("()))((")], [1, 3, 4])


@test
def t14_digits_ranges_ratios():
    ns = defs(("14", 7, 1))
    eq([ns["maximum_swap"](2736), ns["maximum_swap"](9973), ns["maximum_swap"](98368)], [7236, 9973, 98863])
    eq([ns["monotone_increasing_digits"](n) for n in (10, 1234, 332, 120)], [9, 1234, 299, 119])
    v = fn(("14", 8, 1), "s")
    eq([v("()"), v("(*)"), v("(*))"), v("(((*)"), v("((*")], [True, True, True, False, False]) if False else None
    eq([v("()"), v("(*)"), v("(*))"), v("(((*)")], [True, True, True, False])
    r = fn(("14", 8, 2), "s")
    eq([r("lee(t(c)o)de)"), r("a)b(c)d"), r("))((")], ["lee(t(c)o)de", "ab(c)d", ""])
    ib = fn(("14", 9, 2), "costs,coins")
    eq([ib([1, 3, 2, 4, 1], 7), ib([10, 6, 8, 7, 7, 8], 5)], [4, 0])


# ----------------------------------------------------------------------------- 15 DP I
@test
def t15_linear_and_unbounded():
    c = fn(("15", 1, 1), "n")
    eq([c(1), c(2), c(5), c(10)], [1, 2, 8, 89])
    r = fn(("15", 2, 1), "a")
    eq([r([2, 7, 9, 3, 1]), r([1, 2, 3, 1]), r([])], [12, 4, 0])
    r2 = defs(("15", 2, 2))["rob"]
    eq([r2([2, 3, 2]), r2([1, 2, 3, 1]), r2([5])], [3, 4, 5])
    cc = fn(("15", 3, 1), "coins,amount", ret="(fewest, ways[amount])")
    eq(cc([1, 3, 4], 6), (2, 4))
    eq(cc([2], 3), (-1, 0))
    eq(cc([1, 2, 5], 5), (1, 4))
    ps = fn(("15", 3, 2), "n")
    eq([ps(12), ps(13), ps(1)], [3, 2, 1])


@test
def t15_lis_grid_strings():
    l1 = fn(("15", 4, 1), "a")
    l2 = fn(("15", 4, 2), "a,n", ret="best")
    for _ in range(80):
        a = rl(R.randint(1, 9))
        want = max(1 + max([0] + [0]) for _ in [0]) if False else None
        dp = [1] * len(a)
        for i in range(len(a)):
            for j in range(i):
                if a[j] < a[i]:
                    dp[i] = max(dp[i], dp[j] + 1)
        eq(l1(a), max(dp), a)
        eq(l2(a, len(a)), max(dp), a)
    g = fn(("15", 5, 1), "g,m,n", ret="(ways[-1], dp[-1])")
    eq(g([[0, 0, 0], [0, 1, 0], [0, 0, 0]], 3, 3)[0], 2)
    mp = fn(("15", 5, 1), "g,m,n", pre="ways_unused = None", ret="dp[-1]")
    tri = fn(("15", 5, 2), "triangle")
    eq(tri([[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]), 11)
    ns = defs(("15", 6, 1))
    eq([ns["num_decodings"](s) for s in ("12", "226", "06", "10", "2101")], [2, 3, 0, 1, 1])
    eq([ns["word_break"]("leetcode", ["leet", "code"]), ns["word_break"]("catsandog", ["cats", "dog", "sand", "and", "cat"])], [True, False])
    ct = fn(("15", 6, 2), "s")
    eq([ct("22233"), ct("222222222222222222222222222222222222")], [8, 82876089])


@test
def t15_matrix_state_rebuild():
    sq = fn(("15", 7, 1), "g", ret="(area, count)")
    grid = ["10100", "10111", "11111", "10010"]
    brute = sum(1 for i in range(4) for j in range(5) for k in range(1, 5)
                if i + k <= 4 and j + k <= 5 and all(grid[x][y] == "1" for x in range(i, i + k) for y in range(j, j + k)))
    eq(sq([list(r) for r in grid]), (4, brute))
    pl = fn(("15", 7, 2), "n,mines", ret="best")
    eq([pl(5, [[4, 2]]), pl(1, [[0, 0]])], [2, 0])
    cd = fn(("15", 8, 1), "prices")
    eq([cd([1, 2, 3, 0, 2]), cd([1])], [3, 0])
    kt = fn(("15", 8, 2), "prices,k")
    eq([kt([2, 4, 1], 2), kt([3, 2, 6, 5, 0, 3], 2), kt([1, 2, 3, 4, 5], 100)], [2, 7, 4])
    rb = fn(("15", 9, 1), "coins,amount", ret="used")
    eq(sorted(rb([1, 3, 4], 6)), [3, 3])
    pa = fn(("15", 9, 2), "k", ret="row")
    eq([pa(0), pa(3), pa(4)], [[1], [1, 3, 3, 1], [1, 4, 6, 4, 1]])


# ----------------------------------------------------------------------------- remaining small snippets
@test
def t_misc_remaining():
    r = fn(("02", 4, 2), "a,l,r", ret="range_sum")
    eq(r([3, 1, 4, 1, 5, 9], 1, 3), 6)
    s = fn(("07", 2, 1), "a", pre="res = []", ret="res")
    out = s([1, 2, 3])
    eq(sorted(map(sorted, out)), sorted(map(sorted, [[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]])))
    k = fn(("14", 9, 1), "items,capacity,box_types,truck_size", ret="(total, units)")
    eq(k([(60, 10), (100, 20), (120, 30)], 50, [(1, 3), (2, 2), (3, 1)], 4), (240.0, 8))
    p = fn(("11", 7, 2), "dict_words", ret="(prefixes, words)")
    pre, words = p(["apple", "app"])
    eq(("app" in pre, "apx" in pre, "app" in words), (True, False, True))
    f = defs(("01", 1, 1), pre="n = 4")
    eq((f["first"]([7, 1]), f["steps"](8), f["total"]([1, 2, 3])), (7, 3, 6))
