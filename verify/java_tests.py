"""Run the published Java snippets: wraps each in a class with a main() that asserts known answers."""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from snippets import snippets

ALL = {(s["file"][:2], s["pattern"], s["idx"]): s["java"] for s in snippets()}

CASES = []


def case(key, body, name=None):
    CASES.append((key, body, name or "%s_P%d_%d" % key))


# ---- 01 / 02 / 03 -------------------------------------------------------------------------
case(("01", 1, 1), 'check(t.steps(8) == 3 && t.first(new int[]{7, 1}) == 7 && t.sum(new int[]{1, 2, 3}) == 6, "shapes");')
case(("02", 10, 1), 'check(t.quickSelect(new int[]{3, 2, 1, 5, 6, 4}, 2) == 5 && t.quickSelect(new int[]{3, 2, 3, 1, 2, 4, 5, 5, 6}, 4) == 4, "quickSelect");')
case(("03", 3, 1), 'String r = t.longestPalindrome("babad"); check(r.equals("bab") || r.equals("aba"), r); check(t.longestPalindrome("cbbd").equals("bb"), "cbbd");')

# ---- 04 / 05 -------------------------------------------------------------------------------
case(("04", 8, 1), 'LRUCache c = t.new LRUCache(2); c.put(1, 1); c.put(2, 2); check(c.get(1) == 1, "get1"); c.put(3, 3); check(c.get(2) == -1, "evicted"); c.put(4, 4); check(c.get(1) == -1 && c.get(3) == 3 && c.get(4) == 4, "lru");')
case(("05", 1, 1), 'MinStack s = t.new MinStack(); s.push(-2); s.push(0); s.push(-3); check(s.getMin() == -3, "min"); s.pop(); check(s.top() == 0 && s.getMin() == -2, "after pop");')
case(("05", 4, 1), 'MyQueue q = t.new MyQueue(); q.push(1); q.push(2); check(q.peek() == 1 && q.pop() == 1 && !q.empty(), "q1"); check(q.pop() == 2 && q.empty(), "q2");')
case(("05", 9, 1), 'MyCircularQueue q = t.new MyCircularQueue(3); check(q.enQueue(1) && q.enQueue(2) && q.enQueue(3) && !q.enQueue(4), "fill"); check(q.Rear() == 3 && q.isFull() && q.deQueue() && q.enQueue(4) && q.Rear() == 4, "wrap");')

# ---- 07 recursion and backtracking ---------------------------------------------------------
case(("07", 2, 2), 'check(t.allSubsets(new int[]{1, 2, 3}).size() == 8, "mask"); t.dfs(new int[]{1, 2, 3}, 0, new ArrayList<>()); check(t.res.size() == 8, "include/exclude");')
case(("07", 5, 1), 'check(t.subsetsWithDup(new int[]{1, 2, 2}).size() == 6, "subsets II");')
case(("07", 5, 2), 'check(t.permuteUnique(new int[]{1, 1, 2}).size() == 3, "permutations II");')
case(("07", 7, 2), 'check(t.maxGold(new int[][]{{0, 6, 0}, {5, 8, 7}, {0, 9, 0}}) == 24, "gold");')
case(("07", 8, 1), '''int[] want = {1, 0, 0, 2, 10, 4, 40};
for (int n = 1; n <= 7; n++) { t.count = 0; t.cols = new boolean[n]; t.d1 = new boolean[2 * n]; t.d2 = new boolean[2 * n]; t.dfs(0, n); check(t.count == want[n - 1], "queens " + n); }''')
case(("07", 9, 1), 'int[] want = {1, 2, 5, 14}; for (int n = 1; n <= 4; n++) { t.res.clear(); t.dfs(0, 0, n, new StringBuilder()); check(t.res.size() == want[n - 1], "parens " + n); }')

# ---- 08 bits and math ---------------------------------------------------------------------
case(("08", 7, 1), 'check(t.gcd(48, 18) == 6 && t.lcm(4, 6) == 12 && t.countPrimes(10) == 4 && t.countPrimes(100) == 25 && t.countPrimes(2) == 0, "number theory");')
case(("08", 6, 1), 'check(t.power(3, 13, 1_000_000_007L) == 1594323L && t.power(2, 10, 1000) == 24 && t.power(7, 0, 5) == 1, "power");')

# ---- 10 heaps ----------------------------------------------------------------------------
case(("10", 1, 2), 'MinHeap h = t.new MinHeap(); Random r = new Random(5); int[] a = new int[60]; for (int i = 0; i < a.length; i++) { a[i] = r.nextInt(100); h.push(a[i]); } Arrays.sort(a); for (int x : a) check(h.pop() == x, "heap order");')
case(("10", 3, 1), 'MedianFinder m = t.new MedianFinder(); m.addNum(1); m.addNum(2); check(m.findMedian() == 1.5, "1.5"); m.addNum(3); check(m.findMedian() == 2.0, "2");')

# ---- 11 tries -----------------------------------------------------------------------------
case(("11", 1, 1), 'Trie tr = t.new Trie(); tr.insert("apple"); tr.insert("app"); check(tr.search("app") && !tr.search("ap") && tr.startsWith("ap") && !tr.startsWith("b"), "trie");')
case(("11", 5, 1), 'MapSum m = t.new MapSum(); m.insert("apple", 3); check(m.sum("ap") == 3, "s1"); m.insert("app", 2); check(m.sum("ap") == 5, "s2"); m.insert("apple", 2); check(m.sum("ap") == 4, "s3");')
case(("11", 8, 2), 'String[] w = {"cat", "cats", "catsdogcats", "dog", "dogcatsdog", "hippopotamuses", "rat", "ratcatdogcat"}; check(t.findAllConcatenatedWords(w).size() == 3, "concat");')
case(("11", 9, 1), 'StreamChecker s = t.new StreamChecker(new String[]{"cd", "f", "kl"}); boolean[] want = {false, false, false, true, false, true, false, false, false, false, false, true}; String in = "abcdefghijkl"; for (int i = 0; i < 12; i++) check(s.query(in.charAt(i)) == want[i], "stream " + i);')

# ---- 12 graphs ---------------------------------------------------------------------------
case(("12", 2, 1), '''t.g = new ArrayList<>(); for (int i = 0; i < 8; i++) t.g.add(new ArrayList<>());
int[][] e = {{0,1},{0,2},{1,3},{1,4},{2,5},{6,7}}; for (int[] x : e) { t.g.get(x[0]).add(x[1]); t.g.get(x[1]).add(x[0]); }
check(t.countComponents(8) == 2, "components");''')
case(("12", 4, 1), '''char[][] g = {"11000".toCharArray(), "11000".toCharArray(), "00100".toCharArray(), "00011".toCharArray()};
int[] r = t.islands(g); check(r[0] == 3 && r[1] == 4, "islands " + r[0] + "," + r[1]);''')
case(("12", 9, 2), '''int[][] h = {{1,2,2,3,5},{3,2,3,4,4},{2,4,5,3,1},{6,7,1,4,5},{5,1,1,2,4}};
check(t.pacificAtlantic(h).size() == 7, "pacific atlantic");''')

# ---- 13 advanced graphs ------------------------------------------------------------------
case(("13", 2, 1), 'DSU d = t.new DSU(6); check(d.union(0, 1) && !d.union(1, 0) && d.union(2, 3) && d.union(1, 3), "unions"); check(d.components == 3 && d.find(0) == d.find(3) && d.find(4) != d.find(0), "components");')
case(("13", 8, 1), '''t.n = 6; t.g = new List[6]; for (int i = 0; i < 6; i++) t.g[i] = new ArrayList<>();
int[][] e = {{0,1},{1,2},{2,0},{2,3},{3,4},{4,5},{5,3}}; for (int[] x : e) t.g[x[0]].add(x[1]);
check(t.kosaraju() == 2 && t.comp[0] == t.comp[2] && t.comp[3] == t.comp[5] && t.comp[0] != t.comp[3], "scc");''')
case(("13", 9, 1), '''List<List<String>> tk = new ArrayList<>(); tk.add(Arrays.asList("MUC", "LHR")); tk.add(Arrays.asList("JFK", "MUC")); tk.add(Arrays.asList("SFO", "SJC")); tk.add(Arrays.asList("LHR", "SFO"));
check(t.findItinerary(tk).toString().equals("[JFK, MUC, LHR, SFO, SJC]"), "itinerary");''')

# ---- 14 / 15 -----------------------------------------------------------------------------
case(("14", 1, 2), 'check(t.greedyCoins(new int[]{1, 3, 4}, 6) == 3 && t.minCoins(new int[]{1, 3, 4}, 6) == 2, "coins");')
case(("14", 2, 1), 'check(t.canJump(new int[]{2, 3, 1, 1, 4}) && !t.canJump(new int[]{3, 2, 1, 0, 4}) && t.minJumps(new int[]{2, 3, 1, 1, 4}) == 2, "jumps");')
case(("15", 1, 1), 't.memo = new int[11]; check(t.waysNaive(10) == 89 && t.waysMemo(10) == 89 && t.waysTable(10) == 89 && t.waysRolling(10) == 89 && t.waysRolling(1) == 1, "stairs");')


# ---- 16 DP II ----------------------------------------------------------------------------
case(("16", 1, 1), 'check(t.canPartition(new int[]{1, 5, 11, 5}) && !t.canPartition(new int[]{1, 2, 3, 5}), "partition"); check(t.findTargetSumWays(new int[]{1, 1, 1, 1, 1}, 3) == 5, "target sum");')
case(("16", 1, 2), 'check(t.knapsack(new int[]{1, 3, 4, 5}, new int[]{1, 4, 5, 7}, 7) == 9, "knapsack");')
case(("16", 2, 1), 'check(t.findMaxForm(new String[]{"10", "0001", "111001", "1", "0"}, 5, 3) == 4, "ones and zeroes");')
case(("16", 2, 2), 'check(t.profitableSchemes(5, 3, new int[]{2, 2}, new int[]{2, 3}) == 2 && t.profitableSchemes(10, 5, new int[]{2, 3, 5}, new int[]{6, 7, 8}) == 7, "schemes");')
case(("16", 3, 1), 'check(t.lcs("abcde", "ace") == 3 && t.lcsString("abcde", "ace").equals("ace") && t.lcs("abc", "def") == 0, "lcs");')
case(("16", 3, 2), 'check(t.numDistinct("rabbbit", "rabbit") == 3 && t.numDistinct("babgbag", "bag") == 5, "distinct");')
case(("16", 4, 1), 'check(t.minDistance("horse", "ros") == 3 && t.minDistance("intention", "execution") == 5 && t.minDistance("", "abc") == 3, "edit");')
case(("16", 4, 2), 'check(!t.isMatch("aa", "a") && t.isMatch("aa", "*") && !t.isMatch("cb", "?a") && t.isMatch("adceb", "*a*b") && !t.isMatch("acdcb", "a*c?b") && t.isMatch("", "***"), "wildcard");')
case(("16", 5, 1), 'check(t.longestPalindromeSubseq("bbbab") == 4 && t.longestPalindromeSubseq("cbbd") == 2 && t.countSubstrings("aaa") == 6 && t.countSubstrings("abc") == 3, "palindromes");')
case(("16", 5, 2), 'check(t.minCut("aab") == 1 && t.minCut("a") == 0 && t.minCut("ab") == 1, "min cut");')
case(("16", 6, 1), 'check(t.maxCoins(new int[]{3, 1, 5, 8}) == 167 && t.maxCoins(new int[]{1, 5}) == 10, "balloons"); check(t.minCost(7, new int[]{1, 3, 4, 5}) == 16 && t.minCost(9, new int[]{5, 6, 1, 4, 2}) == 22, "cut stick");')
case(("16", 6, 2), 'check(!t.predictTheWinner(new int[]{1, 5, 2}) && t.predictTheWinner(new int[]{1, 5, 233, 7}), "predict");')
case(("16", 7, 1), 'check(t.minAssignmentCost(new int[][]{{9, 2, 7}, {6, 4, 3}, {5, 8, 1}}) == 9, "assignment");')
case(("16", 7, 2), 'check(t.tsp(new int[][]{{0, 10, 15, 20}, {10, 0, 35, 25}, {15, 35, 0, 30}, {20, 25, 30, 0}}) == 80, "tsp");')
case(("16", 8, 1), 'check(t.atMostNGivenDigitSet(new String[]{"1", "3", "5", "7"}, 100) == 20 && t.atMostNGivenDigitSet(new String[]{"1", "4", "9"}, 1000000000) == 29523 && t.atMostNGivenDigitSet(new String[]{"7"}, 8) == 1, "digit set");')
case(("16", 8, 2), 'check(t.countNumbersWithUniqueDigits(0) == 1 && t.countNumbersWithUniqueDigits(2) == 91 && t.countNumbersWithUniqueDigits(3) == 739, "unique digits");')
case(("16", 9, 1), 'check(t.maxResult(new int[]{1, -1, -2, 4, -7, 3}, 2) == 7 && t.maxResult(new int[]{10, -5, -2, 4, 0, 3}, 3) == 17, "jump VI");')
case(("16", 9, 2), 'check(t.constrainedSubsetSum(new int[]{10, 2, -10, 5, 20}, 2) == 37 && t.constrainedSubsetSum(new int[]{-1, -2, -3}, 1) == -1, "constrained");')


# ---- 17 advanced data structures ---------------------------------------------------------
case(("17", 1, 1), 'FenwickTree f = t.new FenwickTree(8); int[] a = {3, 2, -1, 6, 5, 4, -3, 3}; for (int i = 0; i < 8; i++) f.add(i, a[i]); check(f.prefix(6) == 16 && f.range(2, 5) == 14, "prefix"); f.add(2, 10); check(f.prefix(6) == 26, "update");')
case(("17", 1, 2), 'long[] tr = t.buildFenwick(new int[]{3, 2, -1, 6, 5, 4, -3, 3}); check(tr[8] == 19 && tr[4] == 10 && tr[6] == 9, "build"); long[] c = t.buildFenwick(new int[]{0, 2, 1, 0, 3}); check(t.kthSmallest(c, 5, 1) == 2 && t.kthSmallest(c, 5, 3) == 3 && t.kthSmallest(c, 5, 4) == 5, "kth");')
case(("17", 2, 1), 'SegmentTree s = t.new SegmentTree(new int[]{2, 1, 5, 3, 4, 2, 6, 1}); check(s.query(2, 6) == 20 && s.query(0, 7) == 24, "query"); s.update(4, 9); check(s.query(2, 6) == 25, "update");')
case(("17", 2, 2), 'MaxSegmentTree m = t.new MaxSegmentTree(new int[]{1, 3, 2, 7, 4}); check(m.firstAtLeast(3) == 1 && m.firstAtLeast(5) == 3 && m.firstAtLeast(8) == -1, "first"); m.update(0, 9); check(m.firstAtLeast(8) == 0, "after update");')
case(("17", 3, 1), 'LazySegmentTree z = t.new LazySegmentTree(new int[]{1, 2, 3, 4}); z.add(0, 1, 10); check(z.query(1, 2) == 15 && z.query(0, 3) == 30, "lazy");')
case(("17", 3, 2), 'AddMaxTree a = t.new AddMaxTree(6); a.update(0, 2, 1); a.update(1, 4, 1); check(a.max() == 2, "two"); a.update(1, 1, 1); check(a.max() == 3, "three");')
case(("17", 4, 1), 'SparseTable s = t.new SparseTable(new int[]{5, 2, 4, 7, 6, 3, 1, 8}); check(s.min(1, 6) == 1 && s.min(0, 3) == 2 && s.min(4, 5) == 3 && s.min(7, 7) == 8, "min");')
case(("17", 4, 2), 'GcdTable g = t.new GcdTable(new int[]{12, 18, 24, 7, 14}); check(g.query(0, 2) == 6 && g.query(2, 4) == 1 && g.query(3, 4) == 7, "gcd");')
case(("17", 5, 1), 'check(t.countSmaller(new int[]{5, 2, 6, 1}).toString().equals("[2, 1, 1, 0]"), "smaller");')
case(("17", 5, 2), 'check(t.reversePairs(new int[]{1, 3, 2, 3, 1}) == 2 && t.reversePairs(new int[]{2, 4, 3, 5, 1}) == 3, "reverse pairs");')
case(("17", 6, 1), 'TreeAncestor ta = t.new TreeAncestor(9, new int[]{-1, 0, 0, 1, 1, 2, 2, 3, 3}); check(ta.getKthAncestor(7, 2) == 1 && ta.getKthAncestor(7, 4) == -1 && ta.lca(7, 6) == 0 && ta.lca(7, 4) == 1 && ta.lca(8, 3) == 3, "lca");')
case(("17", 7, 1), 'MyCalendar c = t.new MyCalendar(); check(c.book(10, 20) && !c.book(15, 25) && c.book(20, 30) && !c.book(5, 11), "calendar");')
case(("17", 7, 2), 'check(t.containsNearbyAlmostDuplicate(new int[]{1, 2, 3, 1}, 3, 0) && t.containsNearbyAlmostDuplicate(new int[]{1, 0, 1, 1}, 1, 2) && !t.containsNearbyAlmostDuplicate(new int[]{1, 5, 9, 1, 5, 9}, 2, 3), "near dup");')
case(("17", 8, 1), 'int[] r = t.maximumBeauty(new int[][]{{1, 2}, {3, 2}, {2, 4}, {5, 6}, {3, 5}}, new int[]{3, 1, 6, 2, 5, 4}); check(Arrays.toString(r).equals("[5, 2, 6, 4, 6, 5]"), Arrays.toString(r));')
case(("17", 8, 2), 'boolean[] r = t.distanceLimitedPathsExist(3, new int[][]{{0, 1, 2}, {1, 2, 4}, {2, 0, 8}, {1, 0, 16}}, new int[][]{{0, 1, 2}, {0, 2, 5}}); check(!r[0] && r[1], "limited paths");')


def main():
    work = tempfile.mkdtemp(prefix="jrun")
    files = []
    for i, (key, body, name) in enumerate(CASES):
        cls = "J%d" % i
        src = ("import java.util.*;\npublic class %s {\n%s\n"
               "static void check(boolean c, String m) { if (!c) throw new RuntimeException(\"FAIL: \" + m); }\n"
               "public static void main(String[] args) throws Exception { %s t = new %s();\n%s\nSystem.out.println(\"ok\"); }\n}\n"
               % (cls, ALL[key], cls, cls, body))
        path = os.path.join(work, cls + ".java")
        open(path, "w", encoding="utf-8").write(src)
        files.append((cls, name, path))
    r = subprocess.run(["javac", "-proc:none", "-Xlint:none", "-d", work] + [f[2] for f in files], capture_output=True, text=True)
    if r.returncode != 0:
        print("COMPILE ERRORS:")
        print(r.stderr[:4000])
        return 1
    bad = 0
    for cls, name, _ in files:
        p = subprocess.run(["java", "-cp", work, cls], capture_output=True, text=True, timeout=60)
        if p.returncode != 0 or "ok" not in p.stdout:
            bad += 1
            print("FAIL", name, (p.stderr or p.stdout).strip().splitlines()[-1:] )
    print("java cases: %d, passed %d, failed %d" % (len(files), len(files) - bad, bad))
    return bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
