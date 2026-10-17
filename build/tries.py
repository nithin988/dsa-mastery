"""Content for topic 11: Tries."""

P = []

# ---------------------------------------------------------------- 1
P.append(dict(
    title="Trie basics: insert, search, startsWith", tier="hot", sim="trieinsert", oneline="one letter per edge; shared prefixes share a path",
    why="The default structure for any \"words and prefixes\" question", signature="LC 208 / 14",
    when="You store many strings and repeatedly ask whether a word, or a prefix of some word, is present.",
    detect="\"implement a trie / prefix tree\" · \"starts with\" · \"longest common prefix\" · \"replace words with roots\" · \"search suggestions\".",
    intuition="A dictionary with thumb tabs: the first letter selects a page, the second letter a section within it, and so on. Words that begin the same way follow the same path and only split where they differ, so `app`, `apple` and `apt` share the nodes for `a` and `p`. A flag on a node says \"a word ends here\", so `app` is a word but `ap` is only a prefix.",
    brute="Checking a word against a list costs O(N·L) (N words); a hash set answers word lookups in O(L) but cannot answer \"does any word start with this prefix?\" without scanning. A trie answers both in O(L), independent of N.",
    idea="Each node holds children (an array of 26 or a map) and an `end` flag. **Insert**: walk, creating missing children, then set `end`. **Search**: walk; succeed only if every letter has a child and the final node has `end`. **startsWith**: walk; succeed if every letter has a child.",
    steps=["`cur = root`.", "For each letter: if `cur.child[c]` is missing, create it (insert) or fail (search); move `cur` down.", "Insert: set `cur.end = true` at the last node.", "Search needs `cur.end`; startsWith does not."],
    trace_title="insert app, apple, apt, bat",
    trace="""app    : a p p          (3 new nodes, end at the 2nd p)
apple  : a p p reused, l e new
apt    : a p reused, t new
bat    : b a t          (3 new nodes)
14 letters stored in only 9 nodes (plus the root) thanks to the shared prefix""",
    code=[("trie with a 26-letter array",
           """class Trie {
    static class Node { Node[] next = new Node[26]; boolean end; }
    Node root = new Node();

    void insert(String w) {
        Node cur = root;
        for (char c : w.toCharArray()) {
            int i = c - 'a';
            if (cur.next[i] == null) cur.next[i] = new Node();
            cur = cur.next[i];
        }
        cur.end = true;
    }
    boolean search(String w) { Node n = find(w); return n != null && n.end; }
    boolean startsWith(String p) { return find(p) != null; }
    private Node find(String s) {
        Node cur = root;
        for (char c : s.toCharArray()) {
            cur = cur.next[c - 'a'];
            if (cur == null) return null;
        }
        return cur;
    }
}""",
           """class Trie:
    def __init__(self):
        self.root = {}                          # node = dict letter -> child; '$' marks end of a word

    def insert(self, word):
        cur = self.root
        for c in word:
            cur = cur.setdefault(c, {})
        cur['$'] = True

    def _find(self, s):
        cur = self.root
        for c in s:
            if c not in cur:
                return None
            cur = cur[c]
        return cur

    def search(self, word):
        node = self._find(word)
        return node is not None and '$' in node

    def startsWith(self, prefix):
        return self._find(prefix) is not None"""),
          ("replace words with their shortest dictionary root",
           """String replace(String sentence, List<String> roots) {
    Trie t = new Trie();
    for (String r : roots) t.insert(r);
    StringBuilder out = new StringBuilder();
    for (String w : sentence.split(" ")) {
        Trie.Node cur = t.root; int len = 0;
        for (char c : w.toCharArray()) {
            cur = cur.next[c - 'a'];
            if (cur == null) break;                      // no root continues here
            len++;
            if (cur.end) break;                          // shortest root found
        }
        if (out.length() > 0) out.append(' ');
        out.append(cur != null && cur.end ? w.substring(0, len) : w);
    }
    return out.toString();
}""",
           """def replace_words(roots, sentence):
    trie = Trie()
    for r in roots:
        trie.insert(r)
    out = []
    for w in sentence.split():
        cur, prefix = trie.root, ""
        for c in w:
            if c not in cur:
                break                                    # no root continues here
            cur = cur[c]
            prefix += c
            if '$' in cur:
                break                                    # shortest root found
        out.append(prefix if '$' in cur else w)
    return " ".join(out)""")],
    complexity="Insert / search / startsWith O(L). Space O(total letters) in the worst case (O(26·nodes) with arrays).",
    traps=["Search must check the `end` flag; `startsWith` must not.", "A word that is a prefix of another (`app` / `apple`) needs the flag, not a leaf test.",
           "Array children (`new Node[26]`) waste memory for sparse alphabets; use a map for arbitrary characters.", "Allocating 26 slots per node can exceed memory with millions of nodes."],
    variants=["Hash map children for Unicode or mixed-case input.", "Longest common prefix: walk while the node has exactly one child and is not a word end.", "Longest word built one letter at a time: DFS only through nodes that are word ends."],
    notuse="Only whole-word membership (a hash set is simpler) or prefix queries on a static sorted list (binary search works).",
    problems=[
        (14, "Longest Common Prefix", "E", "longest-common-prefix", "Insert all words; walk while one child and not a word end", "O(S) / O(S)"),
        (720, "Longest Word in Dictionary", "E", "longest-word-in-dictionary", "DFS the trie through word-end nodes only", "O(S) / O(S)"),
        (208, "Implement Trie (Prefix Tree)", "M", "implement-trie-prefix-tree", "Insert, search and startsWith by walking nodes", "O(L) per op / O(S)"),
        (648, "Replace Words", "M", "replace-words", "Walk each word; stop at the first end node", "O(S) / O(S)"),
        (1268, "Search Suggestions System", "M", "search-suggestions-system", "Walk the prefix, collect up to 3 lexicographically smallest", "O(S + L·m) / O(S)"),
    ]))

# ---------------------------------------------------------------- 2
P.append(dict(
    title="Prefix queries and autocomplete", tier="hot", sim="prefix", oneline="walk to the prefix node, then read its subtree",
    why="Counting and listing words by prefix without scanning the dictionary", signature="LC 2185 / 2416 / 745",
    when="You answer many queries of the form \"how many / which words start with p (or end with p)?\".",
    detect="\"count words with a given prefix\" · \"sum of prefix scores\" · \"prefix and suffix search\" · \"autocomplete\" · \"count prefix and suffix pairs\".",
    intuition="Once you have walked to the node for a prefix, **everything below it** is exactly the set of words that start with it. So listing them is a DFS of that subtree, and counting them is O(1) if each node remembers how many words pass through it. The cost of a query depends on the prefix length, not on the size of the dictionary.",
    brute="Scanning every word with `startsWith` costs O(N·L) per query. After building the trie once, each query is O(|p|) for existence and counting, plus the output size for listing.",
    idea="Keep `pass` (or `count`) on each node: increment it for every node on a word's path during insertion. `countPrefix(p)` = `pass` of the prefix node. To list words: DFS from the prefix node, collecting each word-end. For **suffix** queries insert reversed words, or insert `suffix#word` combinations.",
    steps=["Insert every word, incrementing `pass` on each node of its path.", "To query prefix `p`: walk letter by letter; if a child is missing, the answer is 0 / empty.", "Count: return the node's `pass`.", "List: DFS the subtree, appending letters, and output at each word end."],
    trace_title="words apple, app, apt, bat, bar; prefix \"ap\"",
    trace="""root -> a -> p            (prefix node, pass = 3)
subtree words: app, apple, apt
countPrefix(\"ap\") = 3 in two steps
prefix \"ba\" -> 2 ; prefix \"c\" -> no child -> 0""",
    code=[("prefix counts and listing",
           """static class Node { Node[] next = new Node[26]; int pass; boolean end; }
Node root = new Node();

void insert(String w) {
    Node cur = root;
    for (char c : w.toCharArray()) {
        int i = c - 'a';
        if (cur.next[i] == null) cur.next[i] = new Node();
        cur = cur.next[i];
        cur.pass++;                                         // one more word passes through this node
    }
    cur.end = true;
}
int countPrefix(String p) {
    Node cur = root;
    for (char c : p.toCharArray()) { cur = cur.next[c - 'a']; if (cur == null) return 0; }
    return cur.pass;
}
void collect(Node n, StringBuilder sb, List<String> out) {      // all words below n
    if (n.end) out.add(sb.toString());
    for (int i = 0; i < 26; i++) if (n.next[i] != null) {
        sb.append((char) ('a' + i)); collect(n.next[i], sb, out); sb.deleteCharAt(sb.length() - 1);
    }
}""",
           """class Node:
    __slots__ = ("kids", "pass_", "end")
    def __init__(self):
        self.kids, self.pass_, self.end = {}, 0, False

root = Node()
def insert(w):
    cur = root
    for c in w:
        cur = cur.kids.setdefault(c, Node())
        cur.pass_ += 1                                       # one more word passes through this node
    cur.end = True

def count_prefix(p):
    cur = root
    for c in p:
        if c not in cur.kids:
            return 0
        cur = cur.kids[c]
    return cur.pass_

def collect(node, prefix, out):                              # all words below node
    if node.end:
        out.append(prefix)
    for c in sorted(node.kids):
        collect(node.kids[c], prefix + c, out)"""),
          ("prefix AND suffix search: index every 'suffix#word'",
           """class WordFilter {
    Trie t = new Trie();                                        // stores strings over a-z and '{' as the separator
    WordFilter(String[] words) {
        for (int idx = 0; idx < words.length; idx++) {
            String w = words[idx] + "{";                        // '{' is the char after 'z'
            for (int i = 0; i <= words[idx].length(); i++) t.insert(w.substring(i) + words[idx], idx);   // suffix{word -> idx
        }
    }
    int f(String pre, String suf) { return t.maxIndexWithPrefix(suf + "{" + pre); }
}""",
           """class WordFilter:
    def __init__(self, words):
        self.trie = {}                                          # node = dict; '#idx' stores the latest index seen
        for idx, w in enumerate(words):
            key = w + "{" + w
            for i in range(len(w) + 1):                          # every suffix + '{' + word
                cur = self.trie
                for c in key[i:]:
                    cur = cur.setdefault(c, {})
                    cur['#'] = idx                               # larger index overwrites: answer is the max
    def f(self, pre, suf):
        cur = self.trie
        for c in suf + "{" + pre:
            if c not in cur:
                return -1
            cur = cur[c]
        return cur['#']""")],
    complexity="Build O(total letters). Count / existence O(|p|). Listing O(|p| + size of the output subtree).",
    traps=["Increment `pass` on every node **below the root** (not the root itself) during insertion.", "Duplicate words increase `pass` each time: decide whether duplicates count.",
           "For suffix queries reversed words are simpler than combined keys when only one of prefix / suffix is needed.", "Listing words DFS can be large; stop early when only the first k are needed."],
    variants=["Sum of prefix scores of strings: for each word, sum `pass` along its path.", "Count prefix and suffix pairs: compare reversed tries or pair-keys.", "Autocomplete ranking: store a top-k list at each node."],
    notuse="A static word list with few queries (sort + binary search on prefixes).",
    problems=[
        (2185, "Counting Words With a Given Prefix", "E", "counting-words-with-a-given-prefix", "Count with startsWith, or pass counts in a trie", "O(N·L) / O(1)"),
        (3042, "Count Prefix and Suffix Pairs I", "E", "count-prefix-and-suffix-pairs-i", "Brute force is fine; tries solve the larger version", "O(N²·L) / O(1)"),
        (2416, "Sum of Prefix Scores of Strings", "H", "sum-of-prefix-scores-of-strings", "pass counts; sum them along each word's path", "O(S) / O(S)"),
        (745, "Prefix and Suffix Search", "H", "prefix-and-suffix-search", "Insert suffix{word keys, store the largest index", "O(N·L²) / O(N·L²)"),
    ]))

# ---------------------------------------------------------------- 3
P.append(dict(
    title="Wildcard matching: '.' branches", tier="hot", sim="wild", oneline="a normal letter follows one child; '.' follows them all",
    why="Turns a dictionary into a pattern matcher", signature="LC 211 / 676",
    when="Queries contain wildcards (a letter that may be anything) or allow exactly one mismatch.",
    detect="\"add and search words\" · \"pattern with dots\" · \"magic dictionary (one letter changed)\" · \"match with ? or *\".",
    intuition="Walking the trie is like following road signs. A normal letter tells you exactly which road to take; a wildcard says \"take any road\". So you need to explore **every** child at a wildcard position and succeed if **any** branch reaches a word end. The recursion tracks the current trie node and the position in the pattern.",
    brute="Comparing the pattern with every stored word is O(N·L). The trie prunes whole groups of words as soon as a fixed letter does not match.",
    idea="`dfs(node, i)`: if `i == len(pattern)` return `node.end`. If `pattern[i]` is a letter, recurse into that child only. If it is `.`, try every child. Return true if any branch succeeds. Variants add a budget (\"exactly one letter changed\").",
    steps=["Insert all words normally.", "`search(pattern)`: call `dfs(root, 0)`.", "Letter → follow one child; wildcard → loop over all children.", "At the end of the pattern the node must be a word end."],
    trace_title="pattern `a.t` in {apt, art, ant, bat}",
    trace="""a   -> node a
.   -> p, r, n   (all children)
t   -> apt, art, ant all end here
matches: apt, art, ant     (bat never explored)""",
    code=[("search with '.' wildcards",
           """boolean search(String word) { return dfs(word, 0, root); }
boolean dfs(String w, int i, Node n) {
    if (n == null) return false;
    if (i == w.length()) return n.end;
    char c = w.charAt(i);
    if (c != '.') return dfs(w, i + 1, n.next[c - 'a']);          // one specific child
    for (Node child : n.next)                                       // wildcard: try every child
        if (child != null && dfs(w, i + 1, child)) return true;
    return false;
}""",
           """def search(self, word):
    def dfs(i, node):
        if i == len(word):
            return '$' in node
        c = word[i]
        if c != '.':
            return c in node and dfs(i + 1, node[c])              # one specific child
        return any(dfs(i + 1, child) for key, child in node.items() if key != '$')   # wildcard: try every child
    return dfs(0, self.root)"""),
          ("magic dictionary: match with exactly one letter changed",
           """boolean search(String w) { return dfs(w, 0, root, false); }
boolean dfs(String w, int i, Node n, boolean changed) {
    if (n == null) return false;
    if (i == w.length()) return changed && n.end;                  // must have used the one change
    int c = w.charAt(i) - 'a';
    if (dfs(w, i + 1, n.next[c], changed)) return true;             // keep the letter
    if (!changed)
        for (int k = 0; k < 26; k++)
            if (k != c && dfs(w, i + 1, n.next[k], true)) return true;   // change it to something else
    return false;
}""",
           """def search(self, word):
    def dfs(i, node, changed):
        if i == len(word):
            return changed and '$' in node                           # must have used the one change
        c = word[i]
        if c in node and dfs(i + 1, node[c], changed):
            return True                                              # keep the letter
        if not changed:
            for k, child in node.items():
                if k != c and k != '$' and dfs(i + 1, child, True):
                    return True                                      # change it to something else
        return False
    return dfs(0, self.root, False)""")],
    complexity="Without wildcards O(L). With w wildcards, up to O(26^w · L) in the worst case; each wildcard multiplies the branching.",
    traps=["Check `node == null` before reading `node.end`.", "A wildcard consumes exactly **one** letter (not zero or many); `*` patterns need DP or a different recursion.",
           "Magic dictionary: exactly one change, not at most one: require the `changed` flag at the end.", "In the map-based trie skip the end marker key when iterating children."],
    variants=["Wildcard `?` (one letter) and `*` (any sequence): recursion with two branches at `*`.", "Approximate matching with edit distance budget k: pass the remaining edits.", "Pattern search on a set of words in a bitmask / regex-engine style."],
    notuse="Only a handful of words (compare directly) or very long wildcards sequences (use DP / regex).",
    problems=[
        (676, "Implement Magic Dictionary", "M", "implement-magic-dictionary", "DFS with a changed flag: exactly one substitution", "O(26·L) / O(S)"),
        (211, "Design Add and Search Words Data Structure", "M", "design-add-and-search-words-data-structure", "DFS; '.' branches to all children", "O(26^w·L) / O(S)"),
    ]))

# ---------------------------------------------------------------- 4
P.append(dict(
    title="Trie + backtracking: Word Search II", tier="hot", sim="pruneword", oneline="stop a DFS the moment its letters are not a prefix of any word",
    why="The classic hard problem where the trie turns exponential into practical", signature="LC 212",
    when="You search a grid (or any state space) for many target words at once.",
    detect="\"word search II\" · \"find all words on the board\" · \"maximum score words formed by letters\" · \"boggle\".",
    intuition="Doing Word Search once per word repeats the same exploration for words that share letters. Instead, put all words in a trie and walk the board **once**, carrying the current trie node. Each step on the board is also a step in the trie: if the trie has no child for the next letter, no target word can start with this path, so cut the branch immediately.",
    brute="Running a full DFS from every cell for each of W words costs O(W · m · n · 3^L). One DFS guided by the trie costs O(m · n · 3^L) total, and pruning makes it far smaller.",
    idea="Insert every word into the trie, storing the full word at its end node. `dfs(r, c, node)`: if the cell is visited or the trie has no child for the letter, return; move to that child; if it holds a word, record it (and clear it to avoid duplicates); mark the cell, explore 4 neighbours, unmark. Optionally prune empty leaf nodes.",
    steps=["Build the trie; store `word` at each end node.", "For every cell: `dfs(r, c, root)`.", "In `dfs`: read the letter, step to `node.next[letter]` or return if missing.", "If `node.word != null`: add it to the answer and set it to null; then mark / recurse / unmark."],
    trace_title="words oath, pea, eat, rain",
    trace="""path o a t h : every step has a trie child, node 'h' holds "oath"  -> FOUND
path o a n   : 'o','a' ok, 'n' has no child under \"oa\"       -> PRUNE""",
    code=[("Word Search II",
           """class TrieNode { TrieNode[] next = new TrieNode[26]; String word; }
List<String> findWords(char[][] board, String[] words) {
    TrieNode root = new TrieNode();
    for (String w : words) {
        TrieNode cur = root;
        for (char c : w.toCharArray()) {
            if (cur.next[c - 'a'] == null) cur.next[c - 'a'] = new TrieNode();
            cur = cur.next[c - 'a'];
        }
        cur.word = w;                                              // store the whole word at its end
    }
    List<String> res = new ArrayList<>();
    for (int r = 0; r < board.length; r++)
        for (int c = 0; c < board[0].length; c++) dfs(board, r, c, root, res);
    return res;
}
void dfs(char[][] b, int r, int c, TrieNode node, List<String> res) {
    if (r < 0 || c < 0 || r >= b.length || c >= b[0].length) return;
    char ch = b[r][c];
    if (ch == '#' || node.next[ch - 'a'] == null) return;           // visited, or not a prefix of any word: PRUNE
    node = node.next[ch - 'a'];
    if (node.word != null) { res.add(node.word); node.word = null; }  // found; avoid duplicates
    b[r][c] = '#';
    dfs(b, r + 1, c, node, res); dfs(b, r - 1, c, node, res); dfs(b, r, c + 1, node, res); dfs(b, r, c - 1, node, res);
    b[r][c] = ch;                                                    // backtrack
}""",
           """def find_words(board, words):
    root = {}
    for w in words:
        cur = root
        for c in w:
            cur = cur.setdefault(c, {})
        cur['$'] = w                                                  # store the whole word at its end
    R, C, res = len(board), len(board[0]), []
    def dfs(r, c, node):
        if not (0 <= r < R and 0 <= c < C):
            return
        ch = board[r][c]
        if ch == '#' or ch not in node:
            return                                                    # visited, or not a prefix of any word: PRUNE
        nxt = node[ch]
        if '$' in nxt:
            res.append(nxt.pop('$'))                                  # found; avoid duplicates
        board[r][c] = '#'
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            dfs(r + dr, c + dc, nxt)
        board[r][c] = ch                                              # backtrack
        if not nxt:
            node.pop(ch)                                              # remove empty branch: speeds up later searches
    for r in range(R):
        for c in range(C):
            dfs(r, c, root)
    return res""")],
    complexity="O(m·n·3^L) worst case, far less in practice thanks to pruning; O(total word letters) for the trie.",
    traps=["Store the **word** at the end node so you do not rebuild the path string.", "Set `node.word = null` after recording, or the same word is returned several times.",
           "Restore the cell after the recursion (backtracking).", "Prune exhausted leaves for large inputs (TLE otherwise)."],
    variants=["Boggle with scores: sum the values of found words.", "Maximum score words formed by letters: DFS over subsets with letter counts (not a trie).", "Word Search I (one word): plain DFS without a trie."],
    notuse="A single word (plain DFS) or a tiny dictionary where per-word search is fast enough.",
    problems=[
        (79, "Word Search", "M", "word-search", "Plain DFS + backtracking for one word", "O(m·n·3^L) / O(L)"),
        (212, "Word Search II", "H", "word-search-ii", "Trie of words guides one DFS over the board", "O(m·n·3^L) / O(S)"),
        (1255, "Maximum Score Words Formed by Letters", "H", "maximum-score-words-formed-by-letters", "Backtrack over words with letter counts (no trie needed)", "O(2^n·L) / O(26)"),
        (140, "Word Break II", "H", "word-break-ii", "Trie or set + memoised DFS over split points", "O(2^n) / O(2^n)"),
    ]))

# ---------------------------------------------------------------- 5
P.append(dict(
    title="Augmenting nodes: counts, sums and top-k", tier="sec", sim="counts", oneline="store the answer you need on every node of the path",
    why="Most design problems are a trie plus one extra field", signature="LC 677 / 1268",
    when="You need aggregates per prefix: a count, a sum of values, the best suggestions.",
    detect="\"map sum pairs\" · \"search suggestions system\" · \"top k frequent words by prefix\" · \"design file system\" · \"autocomplete ranking\".",
    intuition="Every word's path passes through the nodes of all its prefixes, so **each node is a prefix**. Anything you can accumulate along a word's path (a count, a sum, a running list of the best three words) is therefore available at the prefix node in O(1) after the walk, with no need to search the subtree.",
    brute="Summing over all words with a given prefix by scanning costs O(N·L) per query. Maintaining the aggregate during insertion makes a query O(|p|).",
    idea="Add a field to each node and update it on every insertion along the path. For updates that **replace** a value (Map Sum), add the **delta** (`new − old`) along the path. For top-k suggestions keep a small sorted list per node, or insert words in sorted order and keep the first k.",
    steps=["Decide the field: `count`, `sum`, `top3`.", "On insert: walk the path, updating the field at every node.", "On query: walk to the prefix node; read the field.", "For value replacement use `delta = newValue − oldValue`."],
    trace_title="insert app, apple, apt, app: counts",
    trace="""a:4  p:4  p(2nd):3 (app, apple, app)  l:1 e:1  t:1
countWithPrefix(\"app\") = 3
countWithPrefix(\"ap\")  = 4""",
    code=[("Map Sum Pairs (sum of values by prefix)",
           """class MapSum {
    static class Node { Node[] next = new Node[26]; int sum; }
    Node root = new Node(); Map<String, Integer> val = new HashMap<>();
    void insert(String key, int v) {
        int delta = v - val.getOrDefault(key, 0);              // replacing a value adds only the change
        val.put(key, v);
        Node cur = root;
        for (char c : key.toCharArray()) {
            if (cur.next[c - 'a'] == null) cur.next[c - 'a'] = new Node();
            cur = cur.next[c - 'a'];
            cur.sum += delta;
        }
    }
    int sum(String prefix) {
        Node cur = root;
        for (char c : prefix.toCharArray()) { cur = cur.next[c - 'a']; if (cur == null) return 0; }
        return cur.sum;
    }
}""",
           """class MapSum:
    def __init__(self):
        self.root = {}                                          # node: letter -> child; '#' holds the prefix sum
        self.val = {}
    def insert(self, key, v):
        delta = v - self.val.get(key, 0)                        # replacing a value adds only the change
        self.val[key] = v
        cur = self.root
        for c in key:
            cur = cur.setdefault(c, {})
            cur['#'] = cur.get('#', 0) + delta
    def sum(self, prefix):
        cur = self.root
        for c in prefix:
            if c not in cur:
                return 0
            cur = cur[c]
        return cur.get('#', 0)"""),
          ("search suggestions: keep the 3 smallest words at every node",
           """class Node { Node[] next = new Node[26]; List<String> top = new ArrayList<>(); }
Node root = new Node();
Arrays.sort(products);                                           // sorted insertion => first 3 at each node are the smallest
for (String p : products) {
    Node cur = root;
    for (char c : p.toCharArray()) {
        if (cur.next[c - 'a'] == null) cur.next[c - 'a'] = new Node();
        cur = cur.next[c - 'a'];
        if (cur.top.size() < 3) cur.top.add(p);
    }
}
List<List<String>> res = new ArrayList<>();
Node cur = root;
for (char c : searchWord.toCharArray()) {
    if (cur != null) cur = cur.next[c - 'a'];
    res.add(cur == null ? new ArrayList<>() : cur.top);          // suggestions after each typed letter
}""",
           """products.sort()                                                  # sorted insertion => first 3 at each node are the smallest
root = {}
for p in products:
    cur = root
    for c in p:
        cur = cur.setdefault(c, {'top': []})
        if len(cur['top']) < 3:
            cur['top'].append(p)
res, cur = [], root
for c in searchWord:
    cur = cur.get(c) if cur is not None else None
    res.append(cur['top'] if cur else [])                        # suggestions after each typed letter""")],
    complexity="Insert O(L) (plus O(k) for top-k lists); query O(|p|).",
    traps=["Replacing a key's value must add the **difference**, not the new value again.", "Store the old value in a side map so you can compute the delta.",
           "Top-k at each node: sort the words first, or use a bounded heap when ranking by frequency.", "Prefix `sum(\"\")` (empty prefix) is the sum over everything: handle explicitly if required."],
    variants=["Design file system (path → value): a trie of path segments or a hash map keyed by the full path.", "Autocomplete with hot sentences: store counts at word ends and a ranked list per node.", "Top K frequent words: bucket or heap per node."],
    notuse="A single global query (just loop) or exact-key lookups (hash map).",
    problems=[
        (677, "Map Sum Pairs", "M", "map-sum-pairs", "Prefix sums on every node; update with the delta", "O(L) per op / O(S)"),
        (1166, "Design File System", "M", "design-file-system", "Hash map of full paths (or a trie of segments)", "O(L) per op / O(S)"),
        (1268, "Search Suggestions System", "M", "search-suggestions-system", "Top-3 smallest words stored at each node", "O(S + L) / O(S)"),
        (692, "Top K Frequent Words", "M", "top-k-frequent-words", "Counts then a heap (topic 10), or a trie of buckets", "O(n log k) / O(n)"),
    ]))

# ---------------------------------------------------------------- 6
P.append(dict(
    title="Bitwise trie: maximum XOR", tier="hot", sim="xortrie", oneline="a trie over bits; greedily pick the opposite bit",
    why="Beats O(n²) pair checks for XOR problems", signature="LC 421 / 1707",
    when="You want the pair (or element and query) with the largest XOR, or similar bit-wise optimisation.",
    detect="\"maximum XOR of two numbers\" · \"maximum XOR with an element from array\" · \"maximum genetic difference\" · \"XOR query on a range of values\".",
    intuition="XOR is bigger when the **highest** differing bit is 1, no matter what the lower bits are. So to find the best partner for `q`, look at the top bit first: if any stored number has the opposite bit, take it (you gain 2^bit, more than all lower bits combined). If not, you are forced to take the same bit. Repeat for each lower bit. A trie of the numbers' bits lets you do exactly this walk.",
    brute="Comparing every pair is O(n²). A binary trie of depth B (31 for ints) gives each query in O(B): O(n·B) overall.",
    idea="Insert each number as a path of bits from the most significant down to bit 0. Query for `q`: at each bit `b`, want `1 − b`; if that child exists go there and set this bit in the result, otherwise go to the other child.",
    steps=["Fix the number of bits `B` (e.g. 31 or 30).", "Insert: for `bit = B−1 … 0`: `b = (x >> bit) & 1`; create / move to child `b`.", "Query: for each bit, prefer the child `1 − b`; if used, `result |= 1 << bit`.", "Answer = maximum of the query results over all numbers."],
    trace_title="numbers 3, 10, 5, 25, 2, 8; query 5 = 00101",
    trace="""bit4: 5 has 0, want 1: child 1 exists (25 = 11001)      take 1   xor bit 1
bit3: 5 has 0, want 1: child 1 exists under "1"          take 1   xor bit 1
bit2: 5 has 1, want 0: child 0 exists under "11"         take 0   xor bit 1
bit1: 5 has 0, want 1: no child 1 under "110"            take 0   xor bit 0
bit0: 5 has 1, want 0: no child 0 under "1100"           take 1   xor bit 0
partner 11001 = 25, 5 XOR 25 = 11100 = 28 (the overall maximum)""",
    code=[("maximum XOR of two numbers (binary trie)",
           """static class Node { Node[] c = new Node[2]; }
int findMaximumXOR(int[] nums) {
    Node root = new Node();
    int best = 0;
    for (int x : nums) {
        Node cur = root;                                        // insert x
        for (int bit = 30; bit >= 0; bit--) {
            int b = (x >> bit) & 1;
            if (cur.c[b] == null) cur.c[b] = new Node();
            cur = cur.c[b];
        }
        cur = root; int xor = 0;                                // query: best partner among inserted numbers
        for (int bit = 30; bit >= 0; bit--) {
            int b = (x >> bit) & 1;
            if (cur.c[1 - b] != null) { xor |= 1 << bit; cur = cur.c[1 - b]; }   // opposite bit gains this bit
            else cur = cur.c[b];
        }
        best = Math.max(best, xor);
    }
    return best;
}""",
           """def find_maximum_xor(nums):
    root = {}
    best = 0
    for x in nums:
        cur = root                                              # insert x
        for bit in range(30, -1, -1):
            cur = cur.setdefault((x >> bit) & 1, {})
        cur, xor = root, 0                                      # query: best partner among inserted numbers
        for bit in range(30, -1, -1):
            b = (x >> bit) & 1
            if 1 - b in cur:
                xor |= 1 << bit                                 # opposite bit gains this bit
                cur = cur[1 - b]
            else:
                cur = cur[b]
        best = max(best, xor)
    return best"""),
          ("hash-set alternative: build the answer bit by bit",
           """int mask = 0, best = 0;
for (int bit = 30; bit >= 0; bit--) {
    mask |= 1 << bit;
    Set<Integer> prefixes = new HashSet<>();
    for (int x : nums) prefixes.add(x & mask);                  // only the top bits matter so far
    int candidate = best | (1 << bit);                          // hope this bit can be 1
    for (int p : prefixes)
        if (prefixes.contains(p ^ candidate)) { best = candidate; break; }
}
return best;""",
           """mask = best = 0
for bit in range(30, -1, -1):
    mask |= 1 << bit
    prefixes = {x & mask for x in nums}                         # only the top bits matter so far
    candidate = best | (1 << bit)                               # hope this bit can be 1
    if any(p ^ candidate in prefixes for p in prefixes):
        best = candidate
return best""")],
    complexity="O(n·B) time and O(n·B) space for B bits (B = 31 for ints).",
    traps=["Walk from the **most** significant bit; XOR priority follows the top bit.", "Pick the same bit when the opposite child is missing; do not abort.",
           "Insert before querying (or insert all first); querying an empty trie crashes on the first number.", "For \"with element ≤ limit\" queries sort queries and numbers offline, inserting numbers as the limit grows."],
    variants=["Maximum XOR with an element ≤ m (offline queries sorted by m).", "Maximum XOR of a subarray: prefix XORs inserted in a trie.", "Maximum genetic difference on a tree: DFS with insert / remove counts in the trie."],
    notuse="Small arrays (O(n²) is fine) or other bit objectives (AND / OR need different techniques).",
    problems=[
        (421, "Maximum XOR of Two Numbers in an Array", "M", "maximum-xor-of-two-numbers-in-an-array", "Bit trie, greedy opposite-bit walk", "O(n·31) / O(n·31)"),
        (1707, "Maximum XOR With an Element From Array", "H", "maximum-xor-with-an-element-from-array", "Offline: sort queries by limit, insert numbers ≤ limit", "O((n + q)·31) / O(n·31)"),
        (1938, "Maximum Genetic Difference Query", "H", "maximum-genetic-difference-query", "DFS with a counting bit trie (insert on enter, remove on exit)", "O((n + q)·18) / O(n·18)"),
        (2935, "Maximum Strong Pair XOR II", "H", "maximum-strong-pair-xor-ii", "Sorted values with a sliding window of a counting trie", "O(n·20) / O(n·20)"),
    ]))

# ---------------------------------------------------------------- 7
P.append(dict(
    title="Compressed tries and alternatives", tier="sec", sim="radix", oneline="merge chains into labelled edges, or use a sorted list / prefix set",
    why="Know the memory trade-offs and when a trie is overkill", signature="LC 1233 / 1023",
    when="Memory is a concern, or a simpler structure answers the prefix question.",
    detect="\"remove sub-folders\" · \"delete duplicate folders\" · \"camelcase matching\" · \"how would you reduce the memory of a trie?\".",
    intuition="Most nodes of a large trie have exactly one child, forming long chains. Replace each chain by a single edge labelled with the whole string and the node count shrinks to the number of branching points. For a **static** dictionary you can often do without any tree: a sorted array answers prefix queries with two binary searches, and a hash set of all prefixes answers them in O(1) at the price of more memory.",
    brute="A plain trie costs O(total letters) nodes (each with up to 26 pointers). A radix trie has at most 2W nodes for W words.",
    idea="Pick the structure by the workload: dynamic insertions + many prefix queries → trie; static data + few queries → sorted array + binary search; membership only → hash set; memory-critical → compressed (radix) trie or a double-array trie.",
    steps=["Identify whether the dictionary is static or changing.", "Estimate memory: nodes × (pointer array or map).", "Choose: trie, compressed trie, sorted array with binary search, or a hash set of prefixes.", "State the trade-off in the interview."],
    trace_title="test, team, toast",
    trace="""plain trie : 11 nodes (one per letter) + root
radix trie : root -> t -> {e -> {st, am}, oast}   (6 nodes, string labels)""",
    code=[("remove sub-folders: sort, then prefix + '/' check (no trie needed)",
           """Arrays.sort(folder);                                       // a parent sorts right before its children
List<String> res = new ArrayList<>();
for (String f : folder) {
    if (res.isEmpty() || !f.startsWith(res.get(res.size() - 1) + "/")) res.add(f);
}
return res;""",
           """folder.sort()                                                # a parent sorts right before its children
res = []
for f in folder:
    if not res or not f.startswith(res[-1] + "/"):
        res.append(f)
return res"""),
          ("set of all prefixes: O(1) prefix test, O(total letters²) memory",
           """Set<String> prefixes = new HashSet<>(), words = new HashSet<>();
for (String w : dict) {
    words.add(w);
    for (int i = 1; i <= w.length(); i++) prefixes.add(w.substring(0, i));
}
boolean hasPrefix(String p) { return prefixes.contains(p); }
boolean hasWord(String w) { return words.contains(w); }""",
           """prefixes, words = set(), set(dict_words)
for w in dict_words:
    for i in range(1, len(w) + 1):
        prefixes.add(w[:i])
has_prefix = lambda p: p in prefixes
has_word = lambda w: w in words""")],
    complexity="Radix trie: O(L) lookups with far fewer nodes; sorted array: O(L log N) per query; prefix set: O(L) per query, O(total letters²) extra space.",
    traps=["A prefix set stores every prefix as a separate string: memory grows quadratically with word length.", "Sorting + `startsWith` for sub-folders needs the trailing `/` check (`/a` is not a parent of `/ab`).",
           "Compressed tries need label splitting on insert; easy to get wrong in an interview, so implement the plain trie first.", "Binary search for the prefix range needs `lower_bound(prefix)` to `lower_bound(prefix + '\\uffff')`."],
    variants=["Delete duplicate folders: serialise each subtree and hash it.", "Camelcase matching: two-pointer match per query (no trie).", "Ternary search tries: less memory than 26-array nodes with ordered traversal."],
    notuse="Plain tries are fine for interview-sized inputs; reach for these only when asked about memory.",
    problems=[
        (1233, "Remove Sub-Folders from the Filesystem", "M", "remove-sub-folders-from-the-filesystem", "Sort, keep a folder unless it starts with the previous kept one + '/'", "O(n log n·L) / O(n)"),
        (1023, "Camelcase Matching", "M", "camelcase-matching", "Two pointers per query; uppercase letters must match exactly", "O(q·L) / O(1)"),
        (1948, "Delete Duplicate Folders in System", "H", "delete-duplicate-folders-in-system", "Trie of folders; serialise subtrees and delete duplicates", "O(S) / O(S)"),
    ]))

# ---------------------------------------------------------------- 8
P.append(dict(
    title="Segmentation with a trie: word break", tier="hot", sim="wordbreak", oneline="walk the dictionary trie from each reachable position",
    why="Turns repeated substring-in-set checks into one guided walk", signature="LC 139 / 472",
    when="You split a string into dictionary words (or check whether it can be), especially with long strings or many words.",
    detect="\"word break\" · \"concatenated words\" · \"can the string be segmented\" · \"palindrome pairs\" · \"longest word that can be built from others\".",
    intuition="`dp[i]` says \"the first i letters can be split into words\". From each reachable position i, you want to know which dictionary words start there. Instead of testing every substring `s[i..j]` against a set (and building each substring), **walk the trie** letter by letter from position i: every time the walk reaches a word-end, mark `dp[j + 1]`, and stop the moment the trie has no child: no longer word can match.",
    brute="Testing all O(n²) substrings against a hash set builds O(n²) substrings (O(n³) work). The trie walk from each position is bounded by the longest dictionary word L: O(n·L).",
    idea="Build a trie of the dictionary. `dp[0] = true`. For each `i` with `dp[i]`: walk `cur` along `s[i..]`; break when a child is missing; when `cur.end`, set `dp[j + 1] = true`. Answer `dp[n]`.",
    steps=["Insert all dictionary words into a trie.", "`dp[0] = true`.", "For `i` where `dp[i]`: walk the trie along `s[i], s[i+1], …`.", "On a word end at `j`: `dp[j + 1] = true`; on a missing child: stop the walk."],
    trace_title="`leetcode` with {leet, code}",
    trace="""dp[0]=T: walk l e e t -> word end at 3 -> dp[4]=T ; next 'c' has no child, stop
dp[4]=T: walk c o d e -> word end at 7 -> dp[8]=T
dp[8] = true : leet + code""",
    code=[("word break with a trie",
           """boolean wordBreak(String s, List<String> dict) {
    Node root = new Node();
    for (String w : dict) {                                      // build the trie
        Node cur = root;
        for (char c : w.toCharArray()) {
            if (cur.next[c - 'a'] == null) cur.next[c - 'a'] = new Node();
            cur = cur.next[c - 'a'];
        }
        cur.end = true;
    }
    int n = s.length();
    boolean[] dp = new boolean[n + 1];
    dp[0] = true;
    for (int i = 0; i < n; i++) {
        if (!dp[i]) continue;
        Node cur = root;
        for (int j = i; j < n; j++) {
            cur = cur.next[s.charAt(j) - 'a'];
            if (cur == null) break;                              // no dictionary word continues
            if (cur.end) dp[j + 1] = true;                       // a word ends at j
        }
    }
    return dp[n];
}""",
           """def word_break(s, words):
    root = {}
    for w in words:
        cur = root
        for c in w:
            cur = cur.setdefault(c, {})
        cur['$'] = True
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True
    for i in range(n):
        if not dp[i]:
            continue
        cur = root
        for j in range(i, n):
            if s[j] not in cur:
                break                                            # no dictionary word continues
            cur = cur[s[j]]
            if '$' in cur:
                dp[j + 1] = True                                 # a word ends at j
    return dp[n]"""),
          ("concatenated words: sort by length, test each word against shorter ones",
           """List<String> res = new ArrayList<>();
Set<String> seen = new HashSet<>();
Arrays.sort(words, (a, b) -> a.length() - b.length());
for (String w : words) {
    if (!w.isEmpty() && canForm(w, seen)) res.add(w);
    seen.add(w);
}
boolean canForm(String w, Set<String> seen) {
    if (seen.isEmpty()) return false;
    boolean[] dp = new boolean[w.length() + 1]; dp[0] = true;
    for (int i = 1; i <= w.length(); i++)
        for (int j = 0; j < i && !dp[i]; j++)
            if (dp[j] && seen.contains(w.substring(j, i))) dp[i] = true;
    return dp[w.length()];
}""",
           """words.sort(key=len)
seen, res = set(), []
def can_form(w):
    if not seen:
        return False
    dp = [True] + [False] * len(w)
    for i in range(1, len(w) + 1):
        dp[i] = any(dp[j] and w[j:i] in seen for j in range(i))
    return dp[-1]
for w in words:
    if w and can_form(w):
        res.append(w)
    seen.add(w)""")],
    complexity="O(n·L) time for word break with a trie (L = longest word), O(total dictionary letters + n) space.",
    traps=["`dp[j + 1]` (not `dp[j]`) when a word ends at index `j`.", "Break the walk as soon as the child is missing; that is where the speed-up comes from.",
           "Concatenated words must be built from **at least two** shorter words; process by increasing length so only shorter words are available.", "Word Break II (all sentences) needs memoised DFS on the same trie."],
    variants=["Palindrome pairs: trie of reversed words with palindromic-suffix flags.", "Longest word in dictionary built letter by letter: DFS over word-end nodes only.", "Counting the number of segmentations: replace the boolean with a count."],
    notuse="A very small dictionary of short words (a hash set with `substring` is simple enough).",
    problems=[
        (139, "Word Break", "M", "word-break", "dp over positions; walk the trie from each reachable i", "O(n·L) / O(S + n)"),
        (472, "Concatenated Words", "H", "concatenated-words", "Sort by length; word break each word against shorter ones", "O(N·L²) / O(N·L)"),
        (336, "Palindrome Pairs", "H", "palindrome-pairs", "Trie of reversed words with palindrome-suffix indexes", "O(N·L²) / O(N·L)"),
    ]))

# ---------------------------------------------------------------- 9
P.append(dict(
    title="Design with tries: streams, reversed tries", tier="sec", sim="stream", oneline="reverse the words so suffix matching becomes a prefix walk",
    why="Streaming and design questions combine a trie with a small buffer", signature="LC 1032",
    when="Data arrives one character at a time and you must detect dictionary words ending at the latest character.",
    detect="\"stream of characters\" · \"suffix matches a word\" · \"encrypt and decrypt strings\" · \"autocomplete system\" · online text filters.",
    intuition="A new letter can only **end** a word. To test whether some dictionary word ends here, read the stream **backwards** from the newest letter and compare with the words **also stored backwards**. The reversed trie turns a suffix question into a prefix walk, and the walk can never be longer than the longest word, so each new letter costs at most that many steps.",
    brute="Re-checking every dictionary word against the end of the stream costs O(N·L) per letter. The reversed trie costs O(L) per letter, independent of N.",
    idea="Insert each word **reversed**. Keep a buffer of the recent letters (at most the longest word long). On each `query(c)`: append `c`; walk the trie from the newest letter backwards; return true as soon as a word-end node is reached.",
    steps=["Insert `reverse(word)` for every word.", "Maintain a buffer (or deque) of the last `maxLen` letters.", "On each letter: walk the trie along the buffer from newest to oldest.", "If any node on the walk is a word end → true; if a child is missing → false."],
    trace_title="words cd, f, kl; stream a b c d f k l",
    trace="""a b c  -> false
d      : read d, c  -> reversed 'dc' = word 'cd'  -> TRUE
f      : read f     -> word 'f'                   -> TRUE
k      : false
l      : read l, k  -> reversed 'lk' = word 'kl'  -> TRUE""",
    code=[("stream of characters (reversed trie)",
           """class StreamChecker {
    static class Node { Node[] next = new Node[26]; boolean end; }
    Node root = new Node();
    StringBuilder buf = new StringBuilder();
    int maxLen = 0;
    StreamChecker(String[] words) {
        for (String w : words) {
            maxLen = Math.max(maxLen, w.length());
            Node cur = root;
            for (int i = w.length() - 1; i >= 0; i--) {                 // insert the word reversed
                int c = w.charAt(i) - 'a';
                if (cur.next[c] == null) cur.next[c] = new Node();
                cur = cur.next[c];
            }
            cur.end = true;
        }
    }
    boolean query(char letter) {
        buf.append(letter);
        if (buf.length() > maxLen) buf.deleteCharAt(0);                  // keep only what can matter
        Node cur = root;
        for (int i = buf.length() - 1; i >= 0 && cur != null; i--) {     // newest letter first
            cur = cur.next[buf.charAt(i) - 'a'];
            if (cur != null && cur.end) return true;
        }
        return false;
    }
}""",
           """from collections import deque
class StreamChecker:
    def __init__(self, words):
        self.root = {}
        self.max_len = max(len(w) for w in words)
        self.buf = deque(maxlen=self.max_len)                       # only the last max_len letters matter
        for w in words:
            cur = self.root
            for c in reversed(w):                                    # insert the word reversed
                cur = cur.setdefault(c, {})
            cur['$'] = True

    def query(self, letter):
        self.buf.append(letter)
        cur = self.root
        for c in reversed(self.buf):                                 # newest letter first
            if c not in cur:
                return False
            cur = cur[c]
            if '$' in cur:
                return True
        return False""")],
    complexity="Query O(L) with L the longest word; build O(total letters); space O(total letters + L).",
    traps=["Insert the words **reversed**, and read the buffer **newest first**.", "Stop at the **first** word end on the walk (shorter words that are suffixes also count).",
           "Cap the buffer at the longest word length or memory grows forever.", "Do not reset the buffer between queries: words can span earlier letters."],
    variants=["Aho-Corasick automaton: all words at once in O(1) per letter (failure links).", "Encrypt / decrypt strings: map letters to keys, trie over encrypted dictionary for decryption counts.", "Autocomplete System: trie with hot-sentence counts and a current-prefix cursor."],
    notuse="A small word list where scanning suffixes directly is fast enough.",
    problems=[
        (1032, "Stream of Characters", "H", "stream-of-characters", "Reversed trie and a bounded buffer", "O(L) per query / O(S)"),
        (2227, "Encrypt and Decrypt Strings", "H", "encrypt-and-decrypt-strings", "Encrypt each dictionary word; count by encrypted string", "O(L) per op / O(D·L)"),
        (1166, "Design File System", "M", "design-file-system", "Path → value with parent-existence check (hash map or trie)", "O(L) per op / O(S)"),
    ]))

TOPIC = dict(
    id="trie", file="11_trie.html", title="Tries — Pattern Guide",
    lead="A trie turns a pile of strings into a tree you can walk one letter at a time, so prefix questions cost O(length) regardless of how many words you store. This guide covers trie basics, prefix counting and autocomplete, wildcard matching, trie + backtracking (Word Search II), augmenting nodes with counts and top-k, the bitwise trie for maximum XOR, compressed tries and alternatives, word break and streams. Each pattern has the intuition, a step-through animation that draws the trie, Java and Python code, and a ladder of LeetCode problems.",
    mindset="Reach for a trie when the same prefixes appear again and again: shared prefixes share nodes, and a node **is** a prefix. Three ideas cover almost everything: walk the trie letter by letter (insert / search / startsWith), **store extra information on the nodes** (count, sum, word, top-k), and let the trie **guide a search** so impossible branches are cut early (backtracking, word break, wildcards).",
    qintro="Ask these questions on every string-collection problem:",
    questions=["**Do I query by prefix (or suffix)?** → trie (reversed for suffixes).", "**Do I need a count, sum or best list per prefix?** → augment the nodes.", "**Am I searching a board or string for many words at once?** → trie + DFS with pruning.",
               "**Are the keys numbers and I want XOR / bitwise optimisation?** → binary trie.", "**Is the data static and small?** → a sorted list or hash set may be enough."],
    cues=[
        ["\"implement a trie\", \"starts with\", \"longest common prefix\"", "**P1** Trie basics"],
        ["\"count words with prefix\", \"autocomplete\", \"prefix and suffix search\"", "**P2** Prefix queries"],
        ["pattern with `.` wildcards, \"one letter changed\"", "**P3** Wildcard matching"],
        ["\"find all words on the board\"", "**P4** Trie + backtracking"],
        ["\"sum by prefix\", \"search suggestions\", per-prefix top-k", "**P5** Augmented nodes"],
        ["\"maximum XOR\", bits of numbers", "**P6** Bitwise trie"],
        ["memory concerns, \"remove sub-folders\"", "**P7** Compressed tries and alternatives"],
        ["\"word break\", \"concatenated words\"", "**P8** Segmentation with a trie"],
        ["\"stream of characters\", suffix match online", "**P9** Reversed trie / streams"],
    ],
    choose=[
        ["Exact word membership only", "Hash set (simplest)"],
        ["Prefix existence or counting", "Trie with pass counts (P1, P2)"],
        ["Wildcards in the query", "Trie + DFS branching (P3)"],
        ["Many words on a grid", "Trie guiding backtracking (P4)"],
        ["Aggregate per prefix", "Trie with an extra field (P5)"],
        ["Maximise XOR", "Binary trie (P6)"],
        ["Suffix matches on a stream", "Reversed trie + buffer (P9)"],
    ],
    rule="if the question mentions **prefix** (or **suffix**, **wildcard**, **many words at once**), build a trie; the hard part is deciding what extra field each node should carry.",
    selftest=[
        ("What is the time complexity of insert, search and startsWith in a trie?", "O(L) where L is the length of the word or prefix, independent of the number of stored words."),
        ("Why do you need an `end` flag on trie nodes?", "A node can be a prefix of other words without being a word itself (`app` inside `apple`); the flag distinguishes a stored word from a mere prefix."),
        ("How does a trie speed up Word Search II?", "It lets one DFS carry the current trie node and stop as soon as the letters so far are not a prefix of any target word, instead of running a separate DFS per word."),
        ("In Map Sum, why update nodes by `new − old` when a key is reinserted?", "Each node on the key's path already includes the old value in its sum; adding only the difference corrects it without recomputing."),
        ("Why does the maximum-XOR walk prefer the opposite bit at every level?", "A 1 in a higher bit is worth more than all lower bits combined, so choosing the opposite bit (when it exists) maximises the XOR greedily from the top bit down."),
        ("Why is the stream-of-characters trie built from reversed words?", "A word must end at the newest letter, so reading the stream backwards from the latest letter turns the suffix test into an ordinary prefix walk."),
        ("When would you avoid a trie?", "When only whole-word membership is needed (hash set), when the data is static and small (sorted array + binary search), or when memory per node (26 pointers) is a problem."),
        ("How does a compressed (radix) trie reduce memory?", "It merges chains of single-child nodes into one node or edge labelled with the whole string, so the number of nodes is bounded by the number of branch points and words."),
    ],
    plan=[
        "**Day 1:** implement a trie from memory (array and map versions); longest common prefix and replace words.",
        "**Day 2:** prefix counting and autocomplete; Map Sum and search suggestions.",
        "**Day 3:** wildcard search (add and search words, magic dictionary).",
        "**Day 4:** Word Search II: build the trie, DFS with pruning, remove found words.",
        "**Day 5:** bitwise trie: maximum XOR, then the offline variant with a limit.",
        "**Day 6:** word break and concatenated words; stream of characters with a reversed trie.",
    ],
    patterns=P,
)
