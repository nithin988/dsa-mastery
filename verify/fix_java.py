"""One-off patch: turn mixed statement + method Java snippets into compilable class bodies."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from snippets import snippets

NEW = {}

NEW[('02_arrays.html', 10, 1)] = '''int quickSelect(int[] a, int k) {              // kth largest
    int n = a.length, target = n - k, lo = 0, hi = n - 1;
    while (lo <= hi) {
        int p = partition(a, lo, hi);
        if (p == target) return a[p];
        if (p < target) lo = p + 1; else hi = p - 1;
    }
    return -1;
}

int partition(int[] a, int lo, int hi) {
    int pivot = a[hi], i = lo;
    for (int j = lo; j < hi; j++)
        if (a[j] < pivot) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; }
    int t = a[i]; a[i] = a[hi]; a[hi] = t;
    return i;
}'''

NEW[('01_complexity_foundations.html', 1, 1)] = '''// O(1): constant
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
}'''

NEW[('03_strings.html', 3, 1)] = '''String longestPalindrome(String s) {
    int start = 0, best = 0;
    for (int i = 0; i < s.length(); i++) {
        int len = Math.max(expand(s, i, i), expand(s, i, i + 1));
        if (len > best) { best = len; start = i - (len - 1) / 2; }
    }
    return s.substring(start, start + best);
}

int expand(String s, int l, int r) {
    while (l >= 0 && r < s.length() && s.charAt(l) == s.charAt(r)) { l--; r++; }
    return r - l - 1;                       // length of the palindrome found
}'''

NEW[('07_recursion_backtracking.html', 2, 2)] = '''List<List<Integer>> res = new ArrayList<>();

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
}'''

NEW[('07_recursion_backtracking.html', 5, 1)] = '''List<List<Integer>> res = new ArrayList<>();

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
}'''

NEW[('07_recursion_backtracking.html', 5, 2)] = '''List<List<Integer>> res = new ArrayList<>();

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
}'''

NEW[('07_recursion_backtracking.html', 7, 2)] = '''int maxGold(int[][] g) {
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
}'''

NEW[('11_trie.html', 7, 2)] = '''Set<String> prefixes = new HashSet<>(), words = new HashSet<>();

void build(List<String> dict) {
    for (String w : dict) {
        words.add(w);
        for (int i = 1; i <= w.length(); i++) prefixes.add(w.substring(0, i));
    }
}
boolean hasPrefix(String p) { return prefixes.contains(p); }
boolean hasWord(String w) { return words.contains(w); }'''

NEW[('11_trie.html', 8, 2)] = '''List<String> findAllConcatenatedWords(String[] words) {
    List<String> res = new ArrayList<>();
    Set<String> seen = new HashSet<>();
    Arrays.sort(words, (a, b) -> a.length() - b.length());
    for (String w : words) {
        if (!w.isEmpty() && canForm(w, seen)) res.add(w);
        seen.add(w);
    }
    return res;
}
boolean canForm(String w, Set<String> seen) {
    if (seen.isEmpty()) return false;
    boolean[] dp = new boolean[w.length() + 1]; dp[0] = true;
    for (int i = 1; i <= w.length(); i++)
        for (int j = 0; j < i && !dp[i]; j++)
            if (dp[j] && seen.contains(w.substring(j, i))) dp[i] = true;
    return dp[w.length()];
}'''

NEW[('12_graphs_traversal.html', 2, 1)] = '''List<List<Integer>> g;                          // adjacency list
boolean[] seen;

void dfs(int u) {
    seen[u] = true;
    for (int v : g.get(u)) if (!seen[v]) dfs(v);
}
int countComponents(int n) {
    seen = new boolean[n];
    int components = 0;
    for (int u = 0; u < n; u++) if (!seen[u]) { components++; dfs(u); }
    return components;
}

// iterative: avoids stack overflow on long paths
void dfsIterative(int start) {
    Deque<Integer> st = new ArrayDeque<>();
    st.push(start); seen[start] = true;
    while (!st.isEmpty()) {
        int u = st.pop();
        for (int v : g.get(u)) if (!seen[v]) { seen[v] = true; st.push(v); }
    }
}'''

NEW[('12_graphs_traversal.html', 4, 1)] = '''int dfs(char[][] g, int r, int c) {
    if (r < 0 || c < 0 || r >= g.length || c >= g[0].length || g[r][c] != '1') return 0;
    g[r][c] = '0';                                          // sink = mark visited
    return 1 + dfs(g, r + 1, c) + dfs(g, r - 1, c) + dfs(g, r, c + 1) + dfs(g, r, c - 1);
}
int[] islands(char[][] g) {                                 // returns {number of islands, max area}
    int count = 0, best = 0;
    for (int r = 0; r < g.length; r++)
        for (int c = 0; c < g[0].length; c++)
            if (g[r][c] == '1') { count++; best = Math.max(best, dfs(g, r, c)); }
    return new int[]{count, best};
}'''

NEW[('12_graphs_traversal.html', 9, 2)] = '''int[][] D = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

List<List<Integer>> pacificAtlantic(int[][] h) {
    int m = h.length, n = h[0].length;
    boolean[][] pac = new boolean[m][n], atl = new boolean[m][n];
    for (int r = 0; r < m; r++) { dfs(h, pac, r, 0); dfs(h, atl, r, n - 1); }
    for (int c = 0; c < n; c++) { dfs(h, pac, 0, c); dfs(h, atl, m - 1, c); }
    List<List<Integer>> res = new ArrayList<>();
    for (int r = 0; r < m; r++)
        for (int c = 0; c < n; c++) if (pac[r][c] && atl[r][c]) res.add(Arrays.asList(r, c));   // reaches both oceans
    return res;
}
void dfs(int[][] h, boolean[][] seen, int r, int c) {
    seen[r][c] = true;
    for (int[] d : D) {
        int nr = r + d[0], nc = c + d[1];
        if (nr < 0 || nc < 0 || nr >= h.length || nc >= h[0].length || seen[nr][nc]) continue;
        if (h[nr][nc] >= h[r][c]) dfs(h, seen, nr, nc);          // water flows downhill, so we climb in reverse
    }
}'''

NEW[('13_graphs_advanced.html', 8, 1)] = '''int n;
List<Integer>[] g;                                           // original graph
boolean[] seen;
Deque<Integer> order = new ArrayDeque<>();
int[] comp;

void dfs1(int u) { seen[u] = true; for (int v : g[u]) if (!seen[v]) dfs1(v); order.push(u); }   // push AFTER children
void dfs2(List<Integer>[] rev, int u, int id) { seen[u] = true; comp[u] = id; for (int v : rev[u]) if (!seen[v]) dfs2(rev, v, id); }

int kosaraju() {                                             // returns the number of SCCs; comp[u] = its component id
    seen = new boolean[n];
    for (int u = 0; u < n; u++) if (!seen[u]) dfs1(u);
    List<Integer>[] rev = new List[n];                       // reversed graph
    for (int i = 0; i < n; i++) rev[i] = new ArrayList<>();
    for (int u = 0; u < n; u++) for (int v : g[u]) rev[v].add(u);
    Arrays.fill(seen, false);
    comp = new int[n];
    int sccCount = 0;
    while (!order.isEmpty()) { int u = order.pop(); if (!seen[u]) dfs2(rev, u, sccCount++); }    // latest finisher first
    return sccCount;
}'''

NEW[('13_graphs_advanced.html', 9, 1)] = '''Map<String, PriorityQueue<String>> g = new HashMap<>();
LinkedList<String> route = new LinkedList<>();

List<String> findItinerary(List<List<String>> tickets) {
    for (List<String> t : tickets) g.computeIfAbsent(t.get(0), k -> new PriorityQueue<>()).add(t.get(1));
    dfs("JFK");
    return route;
}
void dfs(String u) {
    PriorityQueue<String> pq = g.get(u);
    while (pq != null && !pq.isEmpty()) dfs(pq.poll());     // consume each edge once, smallest destination first
    route.addFirst(u);                                      // add AFTER the edges are exhausted
}'''

NEW[('15_dp_1d_2d.html', 1, 1)] = '''// 1) naive recursion: O(2^n)
int waysNaive(int n) { return n <= 1 ? 1 : waysNaive(n - 1) + waysNaive(n - 2); }

// 2) top-down with memo: O(n) time, O(n) space
int[] memo;
int waysMemo(int n) {
    if (n <= 1) return 1;
    if (memo[n] != 0) return memo[n];
    return memo[n] = waysMemo(n - 1) + waysMemo(n - 2);      // allocate memo = new int[n + 1] first
}

// 3) bottom-up table
int waysTable(int n) {
    int[] dp = new int[n + 1]; dp[0] = 1; if (n >= 1) dp[1] = 1;
    for (int i = 2; i <= n; i++) dp[i] = dp[i - 1] + dp[i - 2];
    return dp[n];
}

// 4) rolling variables: O(1) space
int waysRolling(int n) {
    int a = 1, b = 1;
    for (int i = 2; i <= n; i++) { int c = a + b; a = b; b = c; }
    return b;
}'''

SRC = {'arrays': 'arrays', 'foundations': 'foundations', 'strings': 'strings', 'linked_list': 'linked_list',
       'stack_queue': 'stack_queue', 'sorting_intervals': 'sorting_intervals', 'backtracking': 'recursion_backtracking',
       'bit_math': 'bit_math', 'trees': 'trees', 'heaps': 'heaps', 'trie': 'tries', 'graphs_traversal': 'graphs',
       'graphs_advanced': 'graphs_advanced', 'greedy': 'greedy', 'dp1': 'dp1'}

by_key = {(s['file'], s['pattern'], s['idx']): s for s in snippets()}
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
done = 0
for key, new in NEW.items():
    s = by_key[key]
    old = s['java'].strip()
    path = os.path.join(root, 'build', SRC[s['topic']] + '.py')
    text = open(path, encoding='utf-8').read()
    if old not in text:
        print('NOT FOUND in source:', key)
        continue
    text = text.replace(old, new.strip(), 1)
    open(path, 'w', encoding='utf-8', newline='\n').write(text)
    done += 1
print('patched', done, 'of', len(NEW))
