"""Tiny test harness: runs the published Python snippets against known answers.

get(file_prefix, pattern, idx)      -> the Python source of that snippet
fn(key, params, ret=None)           -> a function whose body is the snippet (use `ret` to return a variable)
defs(key, pre="")                   -> namespace after exec-ing a snippet that defines functions / classes
"""
import collections
import heapq
import math
import os
import random
import sys
import textwrap
import traceback
from bisect import bisect_left, bisect_right
from functools import lru_cache, cmp_to_key

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from snippets import snippets

_ALL = {}
for _s in snippets():
    _ALL[(_s["file"][:2], _s["pattern"], _s["idx"])] = _s["py"]

BASE = {
    "collections": collections, "heapq": heapq, "math": math, "random": random,
    "deque": collections.deque, "defaultdict": collections.defaultdict, "Counter": collections.Counter,
    "bisect_left": bisect_left, "bisect_right": bisect_right, "lru_cache": lru_cache, "cmp_to_key": cmp_to_key,
}

TESTS = []


def test(f):
    TESTS.append(f)
    return f


def get(prefix, pat, idx=1):
    return _ALL[(prefix, pat, idx)]


def fn(key, params="", ret=None, pre="", glob=None):
    code = get(*key)
    body = pre + "\n" + code + ("\nreturn " + ret if ret else "")
    src = "def __f(%s):\n%s\n" % (params, textwrap.indent(textwrap.dedent(body), "    "))
    ns = dict(BASE)
    if glob:
        ns.update(glob)
    exec(src, ns)
    return ns["__f"]


def defs(key, pre="", glob=None):
    ns = dict(BASE)
    if glob:
        ns.update(glob)
    exec(textwrap.dedent(pre + "\n" + get(*key)), ns)
    return ns


def eq(got, want, msg=""):
    assert got == want, "%s got %r, expected %r" % (msg, got, want)


class ListNode:
    def __init__(self, val=0, next=None):
        self.val, self.next = val, next


def ll(vals):
    d = ListNode()
    t = d
    for v in vals:
        t.next = ListNode(v)
        t = t.next
    return d.next


def to_list(n, limit=10000):
    out = []
    while n and limit:
        out.append(n.val)
        n = n.next
        limit -= 1
    return out


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right


def tree(vals):
    """level-order list with None gaps -> TreeNode"""
    if not vals or vals[0] is None:
        return None
    nodes = [TreeNode(v) if v is not None else None for v in vals]
    kids = collections.deque(nodes[1:])
    for n in nodes:
        if n is None:
            continue
        if kids:
            n.left = kids.popleft()
        if kids:
            n.right = kids.popleft()
    return nodes[0]


def run_all(selected=None):
    ok = bad = 0
    for t in TESTS:
        if selected and selected not in t.__name__:
            continue
        try:
            t()
            ok += 1
        except Exception:
            bad += 1
            print("FAIL", t.__name__)
            print("   ", traceback.format_exc().strip().splitlines()[-1])
    print("passed %d, failed %d" % (ok, bad))
    return bad


BASE["ListNode"] = ListNode
BASE["TreeNode"] = TreeNode
