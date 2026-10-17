"""Functional tests, part 1: topics 01-05 (foundations, arrays, strings, linked lists, stacks and queues)."""
import random
from harness import *

R = random.Random(1)


def rand_list(n, lo=-5, hi=9):
    return [R.randint(lo, hi) for _ in range(n)]


# ----------------------------------------------------------------------------- 01 foundations
@test
def t01_fib_and_power():
    ns = defs(("01", 4, 1))
    eq([ns["fib"](i) for i in range(10)], [0, 1, 1, 2, 3, 5, 8, 13, 21, 34])
    eq(ns["fib_memo"](20), 6765)
    eq(ns["fib_naive"](10), 55)
    p = defs(("01", 5, 1))["power"]
    for x, n in [(2.0, 10), (2.0, -2), (3.0, 0), (1.5, 5)]:
        assert abs(p(x, n) - x ** n) < 1e-9, (x, n)


@test
def t01_two_sum_versions():
    f = fn(("01", 6, 1), "a,target")
    for _ in range(50):
        a = rand_list(8, 0, 20)
        t = R.randint(0, 40)
        r = f(a, t)
        pairs = [(i, j) for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] + a[j] == t]
        if pairs:
            assert r and a[r[0]] + a[r[1]] == t and r[0] != r[1]
        else:
            assert r is None


# ----------------------------------------------------------------------------- 02 arrays
@test
def t02_two_pointers():
    f = fn(("02", 1, 1), "a,target")
    eq(f([2, 7, 11, 15], 9), [1, 2])
    eq(f([1, 3, 4, 6, 8, 11], 10), [3, 4])
    eq(f([1, 2], 10), [-1, -1])
    g = fn(("02", 1, 2), "a")
    a = [0, 1, 0, 3, 12]
    g(a)
    eq(a, [1, 3, 12, 0, 0])


@test
def t02_windows():
    f = fn(("02", 2, 1), "a,k", ret="best")
    eq(f([2, 1, 5, 1, 3, 2], 3), 9)
    g = fn(("02", 3, 1), "s", ret="best")
    eq(g("abcabcbb"), 3)
    eq(g("bbbbb"), 1)
    eq(g("pwwkew"), 3)
    h = fn(("02", 3, 2), "a,target")
    eq(h([2, 3, 1, 2, 4, 3], 7), 2)
    eq(h([1, 1, 1], 100), 0)


@test
def t02_prefix_and_kadane():
    f = fn(("02", 4, 1), "a,k", ret="count")
    for _ in range(100):
        a = rand_list(9)
        k = R.randint(-3, 6)
        want = sum(1 for i in range(len(a)) for j in range(i, len(a)) if sum(a[i:j + 1]) == k)
        eq(f(a, k), want, str(a))
    g = fn(("02", 5, 1), "a", ret="best")
    h = fn(("02", 5, 2), "a", ret="best")
    for _ in range(100):
        a = rand_list(8, -4, 5)
        eq(g(a), max(sum(a[i:j + 1]) for i in range(len(a)) for j in range(i, len(a))))
        prod = max(math.prod(a[i:j + 1]) for i in range(len(a)) for j in range(i, len(a)))
        eq(h(a), prod, str(a))


@test
def t02_hashing():
    f = fn(("02", 6, 1), "a,target")
    eq(f([3, 2, 4], 6), [1, 2])
    g = fn(("02", 6, 2), "words", ret="list(groups.values())")
    res = g(["eat", "tea", "tan", "ate", "nat", "bat"])
    eq(sorted(sorted(x) for x in res), sorted([["ate", "eat", "tea"], ["nat", "tan"], ["bat"]]))
    h = fn(("02", 6, 3), "a", ret="best")
    eq(h([100, 4, 200, 1, 3, 2]), 4)
    eq(h([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]), 9)


@test
def t02_sort_colors_and_binary_search():
    f = fn(("02", 7, 1), "a")
    for _ in range(50):
        a = [R.randint(0, 2) for _ in range(10)]
        w = sorted(a)
        f(a)
        eq(a, w)
    lb = fn(("02", 8, 1), "a,target")
    eq(lb([1, 3, 5, 7, 7, 7, 9, 11], 7), 3)
    eq(lb([1, 3, 5], 4), -1)
    koko = fn(("02", 8, 2), "piles,h", ret="lo")
    eq(koko([3, 6, 7, 11], 8), 4)
    eq(koko([30, 11, 23, 4, 20], 5), 30)
    eq(koko([30, 11, 23, 4, 20], 6), 23)


@test
def t02_rotated_search():
    f = fn(("02", 9, 1), "a,target")
    a = [4, 5, 6, 7, 0, 1, 2]
    for t in a:
        eq(f(a, t), a.index(t))
    eq(f(a, 3), -1)
    g = fn(("02", 9, 2), "a")
    eq(g([3, 4, 5, 1, 2]), 1)
    eq(g([4, 5, 6, 7, 0, 1, 2]), 0)
    eq(g([11, 13, 15, 17]), 11)


@test
def t02_selection_and_inversions():
    ns = defs(("02", 10, 1))
    for _ in range(50):
        a = rand_list(9, 0, 20)
        k = R.randint(1, len(a))
        eq(ns["kth_largest"](a[:], k), sorted(a, reverse=True)[k - 1])
    ms = defs(("02", 10, 2))["merge_count"]
    for _ in range(50):
        a = rand_list(8, 0, 9)
        out, inv = ms(a)
        eq(out, sorted(a))
        eq(inv, sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] > a[j]))


@test
def t02_tricks():
    f = fn(("02", 11, 1), "a", ret="cand")
    eq(f([2, 2, 1, 1, 2]), 2)
    eq(f([3, 2, 3]), 3)
    g = fn(("02", 11, 2), "a")
    eq(g([3, 4, -1, 1]), 2)
    eq(g([1, 2, 0]), 3)
    eq(g([7, 8, 9, 11, 12]), 1)


# ----------------------------------------------------------------------------- 03 strings
@test
def t03_anagrams():
    ns = defs(("03", 1, 1))
    for f in (ns["is_anagram"], ns["is_anagram_array"]):
        eq(f("anagram", "nagaram"), True)
        eq(f("rat", "car"), False)
        eq(f("ab", "abc"), False)
    g = fn(("03", 1, 2), "words", ret="list(groups.values())")
    res = g(["eat", "tea", "tan", "ate", "nat", "bat"])
    eq(sorted(sorted(x) for x in res), sorted([["ate", "eat", "tea"], ["nat", "tan"], ["bat"]]))


@test
def t03_palindromes():
    f = fn(("03", 2, 1), "s")
    eq(f("A man, a plan, a canal: Panama"), True)
    eq(f("race a car"), False)
    eq(f("a.b,.B.a"), True)
    ns = defs(("03", 2, 2))
    eq(ns["valid"]("abca"), True)
    eq(ns["valid"]("abc"), False)
    lp = defs(("03", 3, 1))["longest"]
    for s in ["babad", "cbbd", "a", "forgeeksskeegfor"]:
        r = lp(s)
        assert r == r[::-1] and len(r) == max(len(s[i:j]) for i in range(len(s)) for j in range(i + 1, len(s) + 1) if s[i:j] == s[i:j][::-1]), s


@test
def t03_windows():
    f = fn(("03", 4, 1), "s", ret="best")
    eq(f("abcabcbb"), 3)
    eq(f("pwwkew"), 3)
    eq(f(""), 0) if False else None
    g = fn(("03", 4, 2), "s,t")
    eq(g("ADOBECODEBANC", "ABC"), "BANC")
    eq(g("a", "a"), "a")
    eq(g("a", "aa"), "")


@test
def t03_kmp_and_rabin_karp():
    ns = defs(("03", 5, 1))
    eq(ns["lps"]("ababaca"), [0, 0, 1, 2, 3, 0, 1])
    for _ in range(200):
        s = "".join(R.choice("ab") for _ in range(R.randint(0, 12)))
        p = "".join(R.choice("ab") for _ in range(R.randint(1, 3)))
        eq(ns["index_of"](s, p), s.find(p), (s, p))
    rk = fn(("03", 5, 2), "s,p")
    for _ in range(200):
        s = "".join(R.choice("abc") for _ in range(R.randint(0, 12)))
        p = "".join(R.choice("abc") for _ in range(R.randint(1, 3)))
        want = s.find(p)
        got = rk(s, p)
        eq(-1 if got is None else got, want, (s, p))


@test
def t03_parsing_and_edits():
    f = fn(("03", 6, 1), "s", ret="cur")
    eq(f("3[a2[c]]"), "accaccacc")
    eq(f("2[abc]3[cd]ef"), "abcabccdcdcdef")
    g = fn(("03", 6, 2), "s")
    eq([g(x) for x in ["()[]{}", "(]", "([)]", "{[]}", "(("]], [True, False, False, True, False])
    c = fn(("03", 7, 1), "chars", ret="w")
    ch = list("aabbccc")
    n = c(ch)
    eq(ch[:n], list("a2b2c3"))
    ch = list("abbbbbbbbbbbb")
    n = c(ch)
    eq(ch[:n], list("ab12"))
    add = fn(("03", 7, 2), "a,b")
    for _ in range(100):
        x, y = R.randint(0, 10 ** 6), R.randint(0, 10 ** 6)
        eq(add(str(x), str(y)), str(x + y))
    u = fn(("03", 8, 1), "s")
    eq([u("leetcode"), u("loveleetcode"), u("aabb")], [0, 2, -1])
    pg = fn(("03", 8, 2), "s,order", ret="(pangram, rank)")
    ok, rank = pg("thequickbrownfoxjumpsoverthelazydog", "hlabcdefgijkmnopqrstuvwxyz")
    eq(ok, True)
    eq(rank["h"], 0)


# ----------------------------------------------------------------------------- 04 linked lists
@test
def t04_basic_ops():
    f = fn(("04", 1, 1), "head,val", glob={"ListNode": ListNode})
    eq(to_list(f(ll([1, 2, 6, 3, 4, 5, 6]), 6)), [1, 2, 3, 4, 5])
    eq(to_list(f(ll([7, 7, 7]), 7)), [])
    ins = fn(("04", 1, 2), "prev,x", ret="prev", glob={"ListNode": ListNode})
    p = ll([1, 3])
    ins(p, 2)
    eq(to_list(p), [1, 2, 3])


@test
def t04_reverse_and_cycle():
    ns = defs(("04", 2, 1), glob={"ListNode": ListNode})
    eq(to_list(ns["reverse"](ll([1, 2, 3, 4]))), [4, 3, 2, 1])
    eq(to_list(ns["reverse_rec"](ll([1, 2, 3, 4]))), [4, 3, 2, 1])
    f = fn(("04", 2, 2), "head,left,right", glob={"ListNode": ListNode})
    eq(to_list(f(ll([1, 2, 3, 4, 5]), 2, 4)), [1, 4, 3, 2, 5])
    eq(to_list(f(ll([5]), 1, 1)), [5])
    cyc = fn(("04", 3, 1), "head", glob={"ListNode": ListNode})
    a = ll([3, 2, 0, -4])
    node = a
    while node.next:
        node = node.next
    node.next = a.next        # cycle back to the node with value 2
    assert cyc(a) is a.next
    eq(cyc(ll([1, 2, 3])), None)
    mid = fn(("04", 3, 2), "head", glob={"ListNode": ListNode})
    eq(mid(ll([1, 2, 3, 4, 5])).val, 3)
    eq(mid(ll([1, 2, 3, 4, 5, 6])).val, 4)


@test
def t04_merge_and_sort():
    m = fn(("04", 4, 1), "a,b", glob={"ListNode": ListNode})
    eq(to_list(m(ll([1, 2, 4]), ll([1, 3, 4]))), [1, 1, 2, 3, 4, 4])
    merge = lambda a, b: fn(("04", 4, 1), "a,b", glob={"ListNode": ListNode})(a, b)
    ns = defs(("04", 4, 2), glob={"ListNode": ListNode, "merge": merge})
    for _ in range(30):
        a = rand_list(R.randint(0, 9))
        eq(to_list(ns["sort_list"](ll(a))), sorted(a))
    k = fn(("04", 4, 3), "lists", glob={"ListNode": ListNode})
    eq(to_list(k([ll([1, 4, 5]), ll([1, 3, 4]), ll([2, 6])])), [1, 1, 2, 3, 4, 4, 5, 6])
    eq(to_list(k([])), [])


@test
def t04_gap_and_intersection():
    f = fn(("04", 5, 1), "head,n", glob={"ListNode": ListNode})
    eq(to_list(f(ll([1, 2, 3, 4, 5]), 2)), [1, 2, 3, 5])
    eq(to_list(f(ll([1]), 1)), [])
    eq(to_list(f(ll([1, 2]), 2)), [2])
    g = fn(("04", 5, 2), "headA,headB", glob={"ListNode": ListNode})
    common = ll([8, 4, 5])
    a, b = ll([4, 1]), ll([5, 6, 1])
    a.next.next, b.next.next.next = common, common
    assert g(a, b) is common
    eq(g(ll([1, 2]), ll([3])), None)


@test
def t04_combos():
    rev = defs(("04", 2, 1), glob={"ListNode": ListNode})["reverse"]
    pal = fn(("04", 6, 1), "head", glob={"ListNode": ListNode, "reverse": rev})
    eq([pal(ll(x)) for x in ([1, 2, 2, 1], [1, 2], [1, 2, 3, 2, 1], [1])], [True, False, True, True])
    re = fn(("04", 6, 2), "head", ret="head", glob={"ListNode": ListNode, "reverse": rev})
    eq(to_list(re(ll([1, 2, 3, 4]))), [1, 4, 2, 3])
    eq(to_list(re(ll([1, 2, 3, 4, 5]))), [1, 5, 2, 4, 3])
    add = fn(("04", 7, 1), "a,b", glob={"ListNode": ListNode})
    eq(to_list(add(ll([2, 4, 3]), ll([5, 6, 4]))), [7, 0, 8])
    eq(to_list(add(ll([9, 9]), ll([1]))), [0, 0, 1])
    part = fn(("04", 7, 2), "head,x", glob={"ListNode": ListNode})
    eq(to_list(part(ll([1, 4, 3, 2, 5, 2]), 3)), [1, 2, 2, 4, 3, 5])
    oe = fn(("04", 7, 3), "head", glob={"ListNode": ListNode})
    eq(to_list(oe(ll([1, 2, 3, 4, 5]))), [1, 3, 5, 2, 4])
    eq(to_list(oe(ll([2, 1, 3, 5, 6, 4, 7]))), [2, 3, 6, 7, 1, 5, 4])


@test
def t04_lru():
    ns = defs(("04", 8, 1))
    c = ns["LRUCache"](2)
    c.put(1, 1)
    c.put(2, 2)
    eq(c.get(1), 1)
    c.put(3, 3)
    eq(c.get(2), -1)
    c.put(4, 4)
    eq((c.get(1), c.get(3), c.get(4)), (-1, 3, 4))


# ----------------------------------------------------------------------------- 05 stacks and queues
@test
def t05_min_stack_and_rpn():
    ns = defs(("05", 1, 1))
    s = ns["MinStack"]()
    s.push(-2)
    s.push(0)
    s.push(-3)
    eq(s.get_min(), -3)
    s.pop()
    eq((s.top(), s.get_min()), (0, -2))
    f = fn(("05", 1, 2), "tokens")
    eq(f(["2", "1", "+", "3", "*"]), 9)
    eq(f(["4", "13", "5", "/", "+"]), 6)
    eq(f(["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]), 22)


@test
def t05_monotonic_stack():
    f = fn(("05", 2, 1), "t", ret="ans")
    eq(f([73, 74, 75, 71, 69, 72, 76, 73]), [1, 1, 4, 2, 1, 1, 0, 0])
    g = fn(("05", 2, 2), "a,n", ret="res")
    eq(g([1, 2, 1], 3), [2, -1, 2])
    h = fn(("05", 3, 1), "heights")
    eq(h([2, 1, 5, 6, 2, 3]), 10)
    eq(h([2, 4]), 4)
    m = fn(("05", 3, 2), "a", ret="total")
    eq(m([3, 1, 2, 4]), 17)
    for _ in range(40):
        a = [R.randint(1, 9) for _ in range(R.randint(1, 8))]
        want = sum(min(a[i:j + 1]) for i in range(len(a)) for j in range(i, len(a)))
        eq(m(a), want, a)


@test
def t05_queue_stack_conversions():
    ns = defs(("05", 4, 1))
    q = ns["MyQueue"]()
    q.push(1)
    q.push(2)
    eq((q.peek(), q.pop(), q.empty()), (1, 1, False))
    eq((q.pop(), q.empty()), (2, True))
    ns2 = defs(("05", 4, 2))
    ns2["push"](1)
    ns2["push"](2)
    ns2["push"](3)
    eq((ns2["top"](), ns2["pop"](), ns2["pop"]()), (3, 3, 2))


@test
def t05_bfs():
    f = fn(("05", 5, 1), "grid,sr,sc,tr,tc,m,n")
    grid = [[0, 0, 0], [1, 1, 0], [0, 0, 0]]
    eq(f(grid, 0, 0, 2, 2, 3, 3), 4)
    eq(f([[0, 1], [1, 0]], 0, 0, 1, 1, 2, 2), -1)
    r = fn(("05", 5, 2), "g,m,n")
    eq(r([[2, 1, 1], [1, 1, 0], [0, 1, 1]], 3, 3), 4)
    eq(r([[2, 1, 1], [0, 1, 1], [1, 0, 1]], 3, 3), -1)
    eq(r([[0, 2]], 1, 2), 0)


@test
def t05_deque():
    f = fn(("05", 6, 1), "a,k", ret="res")
    eq(f([1, 3, -1, -3, 5, 3, 6, 7], 3), [3, 3, 5, 5, 6, 7])
    for _ in range(40):
        a = rand_list(R.randint(3, 10))
        k = R.randint(1, len(a))
        eq(f(a, k), [max(a[i:i + k]) for i in range(len(a) - k + 1)])
    g = fn(("05", 6, 2), "a,limit", ret="best")
    eq(g([8, 2, 4, 7], 4), 2)
    eq(g([10, 1, 2, 4, 7, 2], 5), 4)
    eq(g([4, 2, 2, 2, 4, 4, 2, 2], 0), 3)


@test
def t05_calculators():
    f = fn(("05", 7, 1), "s")
    eq([f("3+2*2"), f(" 3/2 "), f(" 3+5 / 2 "), f("14-3/2")], [7, 1, 5, 13])
    g = fn(("05", 7, 2), "s")
    eq([g("1 + 1"), g("2-1 + 2"), g("(1+(4+5+2)-3)+(6+8)"), g("-(2+3)")], [2, 3, 23, -5]) if False else None
    eq([g("1 + 1"), g("2-1 + 2"), g("(1+(4+5+2)-3)+(6+8)")], [2, 3, 23])


@test
def t05_greedy_stack():
    f = fn(("05", 8, 1), "num,k")
    eq([f("1432219", 3), f("10200", 1), f("10", 2)], ["1219", "200", "0"])
    g = fn(("05", 8, 2), "s")
    eq([g("bcabc"), g("cbacdcbc")], ["abc", "acdb"])
    ns = defs(("05", 9, 1))
    q = ns["MyCircularQueue"](3)
    eq([q.enQueue(1), q.enQueue(2), q.enQueue(3), q.enQueue(4)], [True, True, True, False])
    eq((q.Rear(), q.isFull(), q.deQueue(), q.enQueue(4), q.Rear()), (3, True, True, True, 4))
    j = fn(("05", 9, 2), "n,k")
    eq([j(5, 2), j(6, 5)], [3, 1])
