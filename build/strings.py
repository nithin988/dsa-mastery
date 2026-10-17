"""Content for topic 03: Strings."""

P = []

# ---------------------------------------------------------------- 1
P.append(dict(
    title="Frequency counting and anagrams", tier="hot", sim="anagram", oneline="count letters, compare the counts",
    why="Most string questions reduce to \"which letters, how many\"", signature="LC 242 / 49",
    when="Order does not matter, only which characters appear and how often.",
    detect="\"anagram\" · \"permutation of\" · \"can construct\" · \"first unique character\" · \"isomorphic\" · \"group by letters\".",
    intuition="Two words are anagrams when they are built from the same bag of tiles. Do not sort the tiles; just count them. Add one for every tile in the first word, subtract one for every tile in the second, and the bag is balanced exactly when every count returns to zero.",
    brute="Sort both strings and compare: O(n log n). Counting into a 26-slot array is one pass: O(n) time, O(1) space.",
    idea="Replace the string by its **letter-count signature**. Two strings with the same signature are anagrams, and the signature can also be a hash key for grouping.",
    steps=["Make `int[26] count` (or a map when characters are not just `a–z`).", "For each character of the first string do `count[c - 'a']++`; for the second do `count[c - 'a']--`.", "If any count is non-zero (or goes negative early), the answer is no.", "For grouping, use the sorted string or the 26-count tuple as the dictionary key."],
    trace_title="`\"listen\"` vs `\"silent\"`",
    trace="""+l +i +s +t +e +n   -> l1 i1 s1 t1 e1 n1
-s -i -l -e -n -t   -> all counts back to 0  -> anagrams""",
    code=[("valid anagram with a 26-slot array",
           """if (s.length() != t.length()) return false;
int[] count = new int[26];
for (int i = 0; i < s.length(); i++) {
    count[s.charAt(i) - 'a']++;
    count[t.charAt(i) - 'a']--;
}
for (int c : count) if (c != 0) return false;
return true;""",
           """from collections import Counter
def is_anagram(s, t):
    return Counter(s) == Counter(t)

# or without a library, 26 slots:
def is_anagram_array(s, t):
    if len(s) != len(t):
        return False
    count = [0] * 26
    for a, b in zip(s, t):
        count[ord(a) - 97] += 1
        count[ord(b) - 97] -= 1
    return not any(count)"""),
          ("group anagrams: the count signature as the key",
           """Map<String, List<String>> groups = new HashMap<>();
for (String w : words) {
    int[] c = new int[26];
    for (char ch : w.toCharArray()) c[ch - 'a']++;
    String key = Arrays.toString(c);               // same letters -> same key
    groups.computeIfAbsent(key, k -> new ArrayList<>()).add(w);
}
return new ArrayList<>(groups.values());""",
           """from collections import defaultdict
groups = defaultdict(list)
for w in words:
    c = [0] * 26
    for ch in w:
        c[ord(ch) - 97] += 1
    groups[tuple(c)].append(w)          # same letters -> same key
return list(groups.values())""")],
    complexity="O(n) time, O(1) space for a fixed alphabet (O(k) for k distinct characters).",
    traps=["Check lengths first; different lengths can never be anagrams.", "`count[c - 'a']` only works for lowercase `a–z`. For Unicode or mixed case use a `HashMap`.",
           "For Group Anagrams, sorting each word costs O(k log k); the count key is O(k).", "Isomorphic strings need a **two-way** mapping (a→b and b→a), not one."],
    variants=["Fixed-size window of an anagram check: slide the counts (LC 438, 567).", "Ransom note: counts of the magazine must cover counts of the note.", "Sort by frequency: bucket by count."],
    notuse="When characters must stay in order (use two pointers or DP), or when only one specific position matters.",
    problems=[
        (242, "Valid Anagram", "E", "valid-anagram", "+1 for one word, −1 for the other, all zeros", "O(n) / O(1)"),
        (383, "Ransom Note", "E", "ransom-note", "Count the magazine, spend letters for the note", "O(n + m) / O(1)"),
        (205, "Isomorphic Strings", "E", "isomorphic-strings", "Two maps: s→t and t→s must both be consistent", "O(n) / O(1)"),
        (290, "Word Pattern", "E", "word-pattern", "Same two-way mapping idea with words", "O(n) / O(n)"),
        (49, "Group Anagrams", "M", "group-anagrams", "Key = sorted word or 26-count tuple", "O(N·K) / O(N·K)"),
        (451, "Sort Characters By Frequency", "M", "sort-characters-by-frequency", "Count, then bucket by frequency", "O(n) / O(n)"),
        (438, "Find All Anagrams in a String", "M", "find-all-anagrams-in-a-string", "Fixed window of len(p) with sliding counts", "O(n) / O(1)"),
        (567, "Permutation in String", "M", "permutation-in-string", "Same window; matches when counts equal", "O(n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 2
P.append(dict(
    title="Two pointers on strings", tier="hot", sim="palin", oneline="compare from both ends, skip what does not count",
    why="Palindromes and in-place reversals are string staples", signature="LC 125 / 680",
    when="Checking symmetry, reversing, or merging two strings position by position.",
    detect="\"palindrome\" · \"reverse in place\" · \"is subsequence\" · \"ignore case / non-alphanumeric\" · \"at most one deletion\".",
    intuition="Read a word from both ends toward the middle like closing a zipper. As long as the two teeth match, keep closing; the first mismatch tells you the answer. Characters that do not count (spaces, punctuation) are simply stepped over without comparing.",
    brute="Build the reversed string and compare: O(n) time but O(n) extra space and a second pass. Two pointers compare in place with O(1) space.",
    idea="`l` starts at the left, `r` at the right. Skip irrelevant characters, compare the relevant pair, move both inward, stop when they cross.",
    steps=["`l = 0`, `r = n − 1`.", "While `l < r`: advance `l` past non-alphanumerics; retreat `r` past non-alphanumerics.", "Compare the two characters (lower-case). Mismatch → false.", "Move both inward. If the loop ends, it is a palindrome."],
    trace_title="`\"a.b,.B.a\"`",
    trace="""l=0 'a'  r=7 'a'  match
l=1 '.'  skip l
l=2 'b'  r=6 '.'  skip r
l=2 'b'  r=5 'B'  match (ignore case)
l=3 ','  skip, l=4 '.' skip, pointers meet -> palindrome""",
    code=[("valid palindrome (ignore case and punctuation)",
           """int l = 0, r = s.length() - 1;
while (l < r) {
    while (l < r && !Character.isLetterOrDigit(s.charAt(l))) l++;
    while (l < r && !Character.isLetterOrDigit(s.charAt(r))) r--;
    if (Character.toLowerCase(s.charAt(l)) != Character.toLowerCase(s.charAt(r))) return false;
    l++; r--;
}
return true;""",
           """l, r = 0, len(s) - 1
while l < r:
    while l < r and not s[l].isalnum():
        l += 1
    while l < r and not s[r].isalnum():
        r -= 1
    if s[l].lower() != s[r].lower():
        return False
    l += 1
    r -= 1
return True"""),
          ("palindrome with at most one deletion",
           """boolean valid(String s) {
    int l = 0, r = s.length() - 1;
    while (l < r) {
        if (s.charAt(l) != s.charAt(r))
            return isPal(s, l + 1, r) || isPal(s, l, r - 1);   // skip either side once
        l++; r--;
    }
    return true;
}
boolean isPal(String s, int l, int r) {
    while (l < r) if (s.charAt(l++) != s.charAt(r--)) return false;
    return true;
}""",
           """def valid(s):
    def is_pal(l, r):
        while l < r:
            if s[l] != s[r]:
                return False
            l += 1
            r -= 1
        return True
    l, r = 0, len(s) - 1
    while l < r:
        if s[l] != s[r]:
            return is_pal(l + 1, r) or is_pal(l, r - 1)   # skip either side once
        l += 1
        r -= 1
    return True""")],
    complexity="O(n) time, O(1) extra space.",
    traps=["Keep the `l < r` guard inside the skip loops or the pointers cross and index out of range.", "Compare lower-cased characters; `Character.toLowerCase` / `str.lower()`.",
           "With one deletion allowed you must try **both** sides, not just one.", "Strings are immutable: reversing \"in place\" needs a `char[]` (Java) or a list (Python)."],
    variants=["Is subsequence: two pointers, one per string, advance `t` always and `s` on a match.", "Reverse vowels: two pointers that stop only at vowels.", "Merge two strings alternately."],
    notuse="When you need all palindromic substrings or the longest one (use expand-around-centre), or the comparison is not positional.",
    problems=[
        (344, "Reverse String", "E", "reverse-string", "Swap ends and move inward", "O(n) / O(1)"),
        (125, "Valid Palindrome", "E", "valid-palindrome", "Skip non-alphanumerics, compare ignoring case", "O(n) / O(1)"),
        (392, "Is Subsequence", "E", "is-subsequence", "Advance s only when characters match", "O(n) / O(1)"),
        (345, "Reverse Vowels of a String", "E", "reverse-vowels-of-a-string", "Both pointers stop only on vowels, then swap", "O(n) / O(n)"),
        (680, "Valid Palindrome II", "E", "valid-palindrome-ii", "On mismatch try skipping the left or the right", "O(n) / O(1)"),
        (1768, "Merge Strings Alternately", "E", "merge-strings-alternately", "Take one character from each, then append the rest", "O(n + m) / O(n + m)"),
    ]))

# ---------------------------------------------------------------- 3
P.append(dict(
    title="Expand around the centre (palindromic substrings)", tier="hot", sim="center", oneline="every palindrome mirrors around a centre",
    why="The standard answer to \"longest palindromic substring\"", signature="LC 5 / 647",
    when="Find the longest or count all palindromic substrings.",
    detect="\"longest palindromic substring\" · \"count palindromic substrings\" · \"palindrome that contains the middle\".",
    intuition="Drop a pebble in water: ripples spread outward symmetrically. A palindrome is a ripple pattern: from its centre, the left and right characters match at every distance. So instead of testing every substring, test every possible centre and let the ripple grow as long as both sides match.",
    brute="Check every substring for being a palindrome: O(n³). Expanding from each of the `2n − 1` centres costs O(n) each: O(n²) with O(1) space.",
    idea="A palindrome centre is either a character (odd length) or the gap between two characters (even length). For each centre expand `l--`, `r++` while `s[l] == s[r]`.",
    steps=["For each `i` from `0` to `n − 1`, expand from `(i, i)` (odd) and `(i, i + 1)` (even).", "While `l ≥ 0`, `r < n` and `s[l] == s[r]`, widen.", "Track the best `(start, length)` or add one to a counter for each successful expansion.", "Return the best substring or the count."],
    trace_title="`\"babad\"`",
    trace="""centre 'b'(0): b            len 1
centre 'a'(1): a -> bab       len 3   best
centre 'b'(2): b -> aba       len 3
centres 'a'(3),'d'(4): len 1
even centres: all mismatch immediately
=> \"bab\"  (\"aba\" is equally valid)""",
    code=[("longest palindromic substring",
           """String longestPalindrome(String s) {
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
}""",
           """def longest(s):
    def expand(l, r):
        while l >= 0 and r < len(s) and s[l] == s[r]:
            l -= 1
            r += 1
        return r - l - 1                    # length of the palindrome found
    start = best = 0
    for i in range(len(s)):
        length = max(expand(i, i), expand(i, i + 1))
        if length > best:
            best = length
            start = i - (length - 1) // 2
    return s[start:start + best]""")],
    complexity="O(n²) time, O(1) space. Manacher's algorithm reaches O(n) but is rarely required.",
    traps=["Forget the even-length centres and `\"abba\"` fails.", "Start index of the best palindrome is `i − (len − 1) / 2` for both parities.",
           "Return length as `r − l − 1` after the loop has stepped one too far on each side.", "Do not use a DP table when O(1) space is enough; DP is O(n²) space."],
    variants=["Count palindromic substrings: add `1` for every successful expansion.", "Longest palindromic **subsequence** is a different problem (DP, topic 16).", "Shortest palindrome by adding characters in front: KMP prefix function (pattern 5)."],
    notuse="When n is huge and O(n²) is too slow (use Manacher), or the problem is about subsequences rather than substrings.",
    problems=[
        (409, "Longest Palindrome", "E", "longest-palindrome", "Count pairs of letters; one odd letter can sit in the middle", "O(n) / O(1)"),
        (647, "Palindromic Substrings", "M", "palindromic-substrings", "Each successful expansion is one palindrome", "O(n²) / O(1)"),
        (5, "Longest Palindromic Substring", "M", "longest-palindromic-substring", "Best expansion over odd and even centres", "O(n²) / O(1)"),
        (131, "Palindrome Partitioning", "M", "palindrome-partitioning", "Backtrack; precompute palindromes with centre expansion or DP", "O(n·2ⁿ) / O(n)"),
        (214, "Shortest Palindrome", "H", "shortest-palindrome", "Longest palindromic prefix via the KMP prefix function of s + '#' + reverse(s)", "O(n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 4
P.append(dict(
    title="Sliding window on strings", tier="hot", sim="minwin", oneline="grow right, shrink left, track what the window holds",
    why="\"Longest / shortest substring with…\" is the most common string pattern", signature="LC 3 / 76",
    when="A contiguous substring must satisfy a condition about its letters.",
    detect="\"longest substring without repeating\" · \"at most K distinct\" · \"minimum window containing\" · \"replace at most k characters\".",
    intuition="An inchworm along the text. The head stretches right to take in letters; whenever the body breaks the rule, the tail pulls in until it is legal again. Neither end ever steps backwards, so every letter enters once and leaves once.",
    brute="Test every substring: O(n²) substrings × O(n) to check = O(n³). The window visits each position twice at most: O(n).",
    idea="Keep a count map for the window and a `formed` counter of how many requirements are satisfied. Expand `r`; while the window is valid (min-window) or invalid (longest), move `l`.",
    steps=["Build `need` counts for the target (if any); `have` counts for the window; `formed = 0`.", "Expand `r`: add `s[r]`, update `have` and `formed`.", "While the window is valid (or invalid, for \"longest\"): record the answer, drop `s[l]`, `l++`.", "Return the best window."],
    trace_title="minimum window containing `ABC` in `\"ADOBECODEBANC\"`",
    trace="""r=5   ADOBEC covers A,B,C            len 6   best
      shrink: drop A -> invalid
r=10  DOBECODEBA covers again; shrink down to CODEBA (len 6), drop C -> invalid
r=12  ODEBANC covers; shrink down to BANC (len 4)   best
=> \"BANC\"""",
    code=[("longest substring without repeating characters",
           """int[] last = new int[128];              // last index + 1 of each character
int best = 0, l = 0;
for (int r = 0; r < s.length(); r++) {
    char c = s.charAt(r);
    l = Math.max(l, last[c]);            // jump past the previous copy
    best = Math.max(best, r - l + 1);
    last[c] = r + 1;
}""",
           """last = {}
best = l = 0
for r, c in enumerate(s):
    if c in last and last[c] >= l:
        l = last[c] + 1                  # jump past the previous copy
    last[c] = r
    best = max(best, r - l + 1)"""),
          ("minimum window substring (need / have / formed)",
           """int[] need = new int[128], have = new int[128];
int required = 0;
for (char c : t.toCharArray()) { if (need[c]++ == 0) required++; }
int l = 0, formed = 0, bestLen = Integer.MAX_VALUE, bestL = 0;
for (int r = 0; r < s.length(); r++) {
    char c = s.charAt(r);
    if (++have[c] == need[c] && need[c] > 0) formed++;
    while (formed == required) {
        if (r - l + 1 < bestLen) { bestLen = r - l + 1; bestL = l; }
        char d = s.charAt(l++);
        if (have[d]-- == need[d] && need[d] > 0) formed--;
    }
}
return bestLen == Integer.MAX_VALUE ? "" : s.substring(bestL, bestL + bestLen);""",
           """from collections import Counter
need = Counter(t)
have = {}
required, formed = len(need), 0
l, best, best_l = 0, float('inf'), 0
for r, c in enumerate(s):
    have[c] = have.get(c, 0) + 1
    if c in need and have[c] == need[c]:
        formed += 1
    while formed == required:
        if r - l + 1 < best:
            best, best_l = r - l + 1, l
        d = s[l]
        have[d] -= 1
        if d in need and have[d] < need[d]:
            formed -= 1
        l += 1
return "" if best == float('inf') else s[best_l:best_l + best]""")],
    complexity="O(n + m) time, O(σ) space for the character counts (σ = alphabet size).",
    traps=["Track `formed` (number of letters whose requirement is met), not the sum of counts; extra copies must not count twice.", "Longest → update the answer after fixing the window; shortest → update inside the shrink loop.",
           "\"Replace at most k\" windows are valid while `size − maxFreq ≤ k`.", "Reading `last[c]` without `max(l, …)` lets `l` move backwards."],
    variants=["At most K distinct characters: shrink while `map.size() > K`.", "Exactly K distinct: `atMost(K) − atMost(K − 1)`.", "Fixed window anagram search: pattern 1 on a window of length `|p|`."],
    notuse="When the substring does not need to be contiguous (subsequence → DP), or when you need every occurrence with overlaps counted through a different rule.",
    problems=[
        (3, "Longest Substring Without Repeating Characters", "M", "longest-substring-without-repeating-characters", "Jump l past the previous copy of s[r]", "O(n) / O(σ)"),
        (424, "Longest Repeating Character Replacement", "M", "longest-repeating-character-replacement", "Valid while size − maxFreq ≤ k", "O(n) / O(1)"),
        (2024, "Maximize the Confusion of an Exam", "M", "maximize-the-confusion-of-an-exam", "Longest window with at most k of the minority answer", "O(n) / O(1)"),
        (567, "Permutation in String", "M", "permutation-in-string", "Fixed window with sliding counts", "O(n) / O(1)"),
        (76, "Minimum Window Substring", "H", "minimum-window-substring", "need / have / formed, shrink while valid", "O(n + m) / O(σ)"),
        (30, "Substring with Concatenation of All Words", "H", "substring-with-concatenation-of-all-words", "Window over word-length steps, for each of the wordLen offsets", "O(n·wordLen) / O(words)"),
    ]))

# ---------------------------------------------------------------- 5
P.append(dict(
    title="String matching: KMP, Z and rolling hash", tier="sec", sim="kmp", oneline="never re-read text: reuse what already matched",
    why="Appears as \"find the needle\", repeated-substring and palindrome-prefix tricks", signature="LC 28 / 459",
    when="Find a pattern in a text in linear time, or reason about borders (prefix = suffix).",
    detect="\"first occurrence of\" · \"repeated substring pattern\" · \"longest happy prefix\" · \"shortest palindrome\" · \"duplicate substring of length L\".",
    intuition="While matching a long pattern you fail late: say 5 characters matched, the 6th differs. The naive method forgets everything and slides by one. But the 5 matched characters tell you something: if the start of the pattern also appears at their end, you can keep that overlap and continue without moving backwards in the text. The `lps` array stores that overlap for every prefix.",
    brute="Try every start position and compare: O(n·m). KMP precomputes the longest border of each pattern prefix and never moves the text pointer backwards: O(n + m).",
    idea="`lps[i]` = length of the longest proper prefix of `p[0..i]` that is also a suffix. On a mismatch after `j` matched characters, fall back to `j = lps[j − 1]` instead of restarting at 0. A **rolling hash** (Rabin–Karp) instead compares window hashes in O(1) per step.",
    steps=["Build `lps` for the pattern: compare `p[i]` with `p[len]`; on a mismatch fall back `len = lps[len − 1]` until `len = 0`.", "Scan the text with index `i` and matched length `j`.", "On a match advance both; on a mismatch with `j > 0` set `j = lps[j − 1]`; if `j == m` a match ends at `i`.", "Rolling hash: `h = (h·B − out·B^m + in) mod M`, then verify on hash equality."],
    trace_title="lps for `\"ababaca\"`",
    trace="""i=1 b vs a  no          lps 0
i=2 a vs a  yes len=1   lps 1
i=3 b vs b  yes len=2   lps 2
i=4 a vs a  yes len=3   lps 3
i=5 c vs b  no -> len=lps[2]=1, c vs b no -> len=0, c vs a no   lps 0
i=6 a vs a  yes len=1   lps 1
lps = [0,0,1,2,3,0,1]""",
    code=[("KMP: prefix function and search",
           """int[] lps(String p) {
    int[] f = new int[p.length()];
    for (int i = 1, len = 0; i < p.length(); ) {
        if (p.charAt(i) == p.charAt(len)) f[i++] = ++len;
        else if (len > 0) len = f[len - 1];
        else f[i++] = 0;
    }
    return f;
}
int indexOf(String s, String p) {
    if (p.isEmpty()) return 0;
    int[] f = lps(p);
    for (int i = 0, j = 0; i < s.length(); ) {
        if (s.charAt(i) == p.charAt(j)) { i++; j++; if (j == p.length()) return i - j; }
        else if (j > 0) j = f[j - 1];
        else i++;
    }
    return -1;
}""",
           """def lps(p):
    f, length, i = [0] * len(p), 0, 1
    while i < len(p):
        if p[i] == p[length]:
            length += 1
            f[i] = length
            i += 1
        elif length:
            length = f[length - 1]
        else:
            f[i] = 0
            i += 1
    return f

def index_of(s, p):
    if not p:
        return 0
    f, j = lps(p), 0
    for i, c in enumerate(s):
        while j and c != p[j]:
            j = f[j - 1]
        if c == p[j]:
            j += 1
        if j == len(p):
            return i - j + 1
    return -1"""),
          ("Rabin–Karp rolling hash (find a window with the same hash)",
           """long M = 1_000_000_007L, B = 131;
long h = 0, pw = 1;                                 // pw = B^(m-1)
for (int i = 0; i < m; i++) { h = (h * B + p.charAt(i)) % M; if (i < m - 1) pw = pw * B % M; }
long w = 0;
for (int i = 0; i < n; i++) {
    if (i >= m) w = ((w - s.charAt(i - m) * pw % M) + M) % M;   // remove the outgoing char
    w = (w * B + s.charAt(i)) % M;                              // add the incoming char
    if (i >= m - 1 && w == h && s.startsWith(p, i - m + 1)) return i - m + 1;
}""",
           """M, B = 1_000_000_007, 131
m = len(p)
h = 0
for c in p:
    h = (h * B + ord(c)) % M
pw = pow(B, m - 1, M)
w = 0
for i, c in enumerate(s):
    if i >= m:
        w = (w - ord(s[i - m]) * pw) % M              # remove the outgoing char
    w = (w * B + ord(c)) % M                           # add the incoming char
    if i >= m - 1 and w == h and s.startswith(p, i - m + 1):
        return i - m + 1""")],
    complexity="KMP: O(n + m) time, O(m) space. Rabin–Karp: O(n + m) expected, O(n·m) worst case on hash collisions.",
    traps=["The fall-back is `len = lps[len − 1]`, **not** `len = 0` (and not `len − 1`).", "Rolling hash: always verify on equality (collisions exist) and add `M` before the modulo when subtracting.",
           "Empty pattern: return 0 by convention (LC 28).", "In an interview, `s.indexOf(p)` is usually not allowed for the \"implement strStr\" question."],
    variants=["Repeated substring pattern: `(s + s).indexOf(s, 1) != s.length()`, or `n % (n − lps[n−1]) == 0` with `lps[n−1] > 0`.", "Z-function: `z[i]` = length of the longest match between `s` and `s[i..]`; pattern matching on `p + '#' + s`.", "Binary search on length + rolling hash for the longest duplicate substring (LC 1044)."],
    notuse="When a built-in search is allowed and input is small, or when you need many patterns at once (use a trie or Aho–Corasick).",
    problems=[
        (28, "Find the Index of the First Occurrence in a String", "E", "find-the-index-of-the-first-occurrence-in-a-string", "Naive O(n·m), then KMP", "O(n + m) / O(m)"),
        (459, "Repeated Substring Pattern", "E", "repeated-substring-pattern", "Border check with lps, or search s in (s + s) minus the ends", "O(n) / O(n)"),
        (1392, "Longest Happy Prefix", "H", "longest-happy-prefix", "Answer is lps[n − 1] of the whole string", "O(n) / O(n)"),
        (686, "Repeated String Match", "M", "repeated-string-match", "Repeat a enough times, then search for b", "O(n + m) / O(n + m)"),
        (187, "Repeated DNA Sequences", "M", "repeated-dna-sequences", "Hash every 10-letter window (rolling hash or set)", "O(n) / O(n)"),
        (214, "Shortest Palindrome", "H", "shortest-palindrome", "lps of s + '#' + reverse(s) gives the longest palindromic prefix", "O(n) / O(n)"),
        (1044, "Longest Duplicate Substring", "H", "longest-duplicate-substring", "Binary search the length, check with a rolling hash", "O(n log n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 6
P.append(dict(
    title="Stack-based parsing and decoding", tier="hot", sim="decode", oneline="push context on an opener, resolve it on a closer",
    why="Nested or balanced structure in strings is always a stack", signature="LC 20 / 394",
    when="The string has brackets, nesting, or operators that must be resolved in order.",
    detect="\"valid parentheses\" · \"decode string\" · \"simplify path\" · \"remove adjacent duplicates\" · \"evaluate expression\" · \"calculator\".",
    intuition="Like opening nested Russian dolls: each opener makes you remember where you were, and each closer returns you to the most recent unfinished doll. \"Most recent unfinished\" is exactly what a stack gives you.",
    brute="Repeatedly scan and replace innermost brackets: O(n²). One left-to-right pass with a stack resolves everything in O(n).",
    idea="On an opening symbol, push the state you will need later (count, previous text, previous operator). On a closing symbol, pop it and combine it with what you have built inside.",
    steps=["Scan left to right keeping the current text and number being built.", "`[`: push `(count, text so far)` and reset current text.", "`]`: pop `(count, prev)`; current = `prev + current × count`.", "Letter: append to the current text. Digit: extend the number."],
    trace_title="decode `\"3[a2[c]]\"`",
    trace="""3     num=3
[     push (3,\"\")   cur=\"\"
a     cur=\"a\"
2     num=2
[     push (2,\"a\")  cur=\"\"
c     cur=\"c\"
]     pop (2,\"a\")  cur=\"a\"+\"cc\"=\"acc\"
]     pop (3,\"\")   cur=\"acc\"*3=\"accaccacc\"""",
    code=[("decode string k[text]",
           """Deque<int[]> counts = new ArrayDeque<>();
Deque<StringBuilder> texts = new ArrayDeque<>();
StringBuilder cur = new StringBuilder();
int num = 0;
for (char c : s.toCharArray()) {
    if (Character.isDigit(c)) num = num * 10 + (c - '0');
    else if (c == '[') { counts.push(new int[]{num}); texts.push(cur); num = 0; cur = new StringBuilder(); }
    else if (c == ']') {
        StringBuilder prev = texts.pop();
        prev.append(String.valueOf(cur).repeat(counts.pop()[0]));
        cur = prev;
    } else cur.append(c);
}
return cur.toString();""",
           """stack, cur, num = [], "", 0
for c in s:
    if c.isdigit():
        num = num * 10 + int(c)
    elif c == '[':
        stack.append((num, cur))
        num, cur = 0, ""
    elif c == ']':
        k, prev = stack.pop()
        cur = prev + cur * k
    else:
        cur += c
return cur"""),
          ("valid parentheses",
           """Deque<Character> st = new ArrayDeque<>();
for (char c : s.toCharArray()) {
    if (c == '(' || c == '[' || c == '{') st.push(c);
    else {
        if (st.isEmpty()) return false;
        char o = st.pop();
        if ((c == ')' && o != '(') || (c == ']' && o != '[') || (c == '}' && o != '{')) return false;
    }
}
return st.isEmpty();""",
           """pairs = {')': '(', ']': '[', '}': '{'}
st = []
for c in s:
    if c in pairs:
        if not st or st.pop() != pairs[c]:
            return False
    else:
        st.append(c)
return not st""")],
    complexity="O(n) time (each character pushed and popped at most once), O(n) space.",
    traps=["Multi-digit counts (`12[a]`): build the number, do not read one digit.", "Pop only after checking the stack is non-empty.", "Return `stack.isEmpty()` at the end, not `true`; unclosed openers must fail.",
           "String concatenation in a loop is O(n²): use `StringBuilder` / list and join."],
    variants=["Basic calculator: stack of (result, sign) saved at `(`.", "Calculator II (no parentheses): stack of numbers, apply `*` and `/` immediately, sum at the end.", "Simplify path: split on `/`, push directories, pop on `..`.", "Remove adjacent duplicates: push unless top equals current."],
    notuse="When the structure is flat (no nesting), a simple loop or two pointers suffices.",
    problems=[
        (20, "Valid Parentheses", "E", "valid-parentheses", "Push openers; each closer must match the top", "O(n) / O(n)"),
        (1047, "Remove All Adjacent Duplicates In String", "E", "remove-all-adjacent-duplicates-in-string", "Push unless the top equals the current character", "O(n) / O(n)"),
        (71, "Simplify Path", "M", "simplify-path", "Split on '/', push names, pop on '..'", "O(n) / O(n)"),
        (394, "Decode String", "M", "decode-string", "Stack of (count, text before the bracket)", "O(n + output) / O(n)"),
        (227, "Basic Calculator II", "M", "basic-calculator-ii", "Resolve * and / immediately, sum the stack", "O(n) / O(n)"),
        (224, "Basic Calculator", "H", "basic-calculator", "Push (result, sign) at '(' and restore at ')'", "O(n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 7
P.append(dict(
    title="In-place edits and simulation", tier="sec", sim="compress", oneline="a read pointer, a write pointer, one pass",
    why="Parsing, arithmetic and compression questions test careful implementation", signature="LC 443 / 8",
    when="Transform a string step by step with exact rules: compress, add, parse, reverse words.",
    detect="\"in place\" · \"compress\" · \"string to integer\" · \"add two numbers as strings\" · \"reverse words\" · \"zigzag\".",
    intuition="Think of a scribe copying a document onto the same page: the reading finger always runs ahead of the writing pen, so the pen never overwrites something it still needs. Two indices over the same array give you an in-place rewrite in a single pass.",
    brute="Build a new string with repeated concatenation: O(n²) copies. A single pass with a `StringBuilder` is O(n) time; a read/write pointer pair also gives O(1) extra space.",
    idea="Separate **reading** from **writing**. `r` scans input groups or tokens; `w` writes the result at the front. For arithmetic, process digits from the right with a carry.",
    steps=["`r = w = 0`.", "Read one logical unit (a run of equal characters, a number, a word) starting at `r` and advance `r` past it.", "Write its encoded form at `w` and advance `w`.", "At the end, the answer is the first `w` characters."],
    trace_title="compress `\"aabbccc\"` in place",
    trace="""group aa -> write a2     [a,2,b,b,c,c,c]  w=2
group bb -> write b2     [a,2,b,2,c,c,c]  w=4
group ccc-> write c3     [a,2,b,2,c,3,c]  w=6
=> first 6 characters \"a2b2c3\"""",
    code=[("string compression in place",
           """int w = 0, r = 0;
while (r < chars.length) {
    char c = chars[r];
    int start = r;
    while (r < chars.length && chars[r] == c) r++;      // read a whole run
    chars[w++] = c;
    int count = r - start;
    if (count > 1) for (char d : String.valueOf(count).toCharArray()) chars[w++] = d;
}
return w;""",
           """w = r = 0
while r < len(chars):
    c, start = chars[r], r
    while r < len(chars) and chars[r] == c:             # read a whole run
        r += 1
    chars[w] = c
    w += 1
    count = r - start
    if count > 1:
        for d in str(count):
            chars[w] = d
            w += 1
return w"""),
          ("add two numeric strings (digit by digit with a carry)",
           """StringBuilder sb = new StringBuilder();
int i = a.length() - 1, j = b.length() - 1, carry = 0;
while (i >= 0 || j >= 0 || carry > 0) {
    int sum = carry;
    if (i >= 0) sum += a.charAt(i--) - '0';
    if (j >= 0) sum += b.charAt(j--) - '0';
    sb.append(sum % 10);
    carry = sum / 10;
}
return sb.reverse().toString();""",
           """out, i, j, carry = [], len(a) - 1, len(b) - 1, 0
while i >= 0 or j >= 0 or carry:
    s = carry
    if i >= 0:
        s += ord(a[i]) - 48
        i -= 1
    if j >= 0:
        s += ord(b[j]) - 48
        j -= 1
    out.append(str(s % 10))
    carry = s // 10
return ''.join(reversed(out))""")],
    complexity="O(n) time, O(1) extra space for pointer-based rewrites (O(n) when you build a new string).",
    traps=["The write pointer must never pass the read pointer.", "Do not use `+=` in a loop; use `StringBuilder` / list.", "atoi: skip leading spaces, read one optional sign, stop at the first non-digit, clamp on overflow.",
           "Reverse words: split on runs of spaces and trim; consecutive spaces create empty tokens."],
    variants=["Reverse words in place: reverse the whole string, then reverse each word.", "Multiply strings: grade-school multiplication into an int array.", "Zigzag conversion: simulate rows with a direction flag."],
    notuse="When the transformation needs random access to later input (then build a new string instead of overwriting).",
    problems=[
        (14, "Longest Common Prefix", "E", "longest-common-prefix", "Compare column by column until a mismatch", "O(S) / O(1)"),
        (58, "Length of Last Word", "E", "length-of-last-word", "Scan from the right, skip spaces, count letters", "O(n) / O(1)"),
        (415, "Add Strings", "E", "add-strings", "Digits from the right with a carry", "O(max(m,n)) / O(max(m,n))"),
        (67, "Add Binary", "E", "add-binary", "Same with base 2", "O(max(m,n)) / O(max(m,n))"),
        (443, "String Compression", "M", "string-compression", "Read a run, write char and count at the front", "O(n) / O(1)"),
        (151, "Reverse Words in a String", "M", "reverse-words-in-a-string", "Split on whitespace, reverse, join", "O(n) / O(n)"),
        (8, "String to Integer (atoi)", "M", "string-to-integer-atoi", "Trim, sign, digits, clamp on overflow", "O(n) / O(1)"),
        (43, "Multiply Strings", "M", "multiply-strings", "result[i + j + 1] accumulates products; carry at the end", "O(m·n) / O(m + n)"),
        (6, "Zigzag Conversion", "M", "zigzag-conversion", "Row index bounces between 0 and numRows − 1", "O(n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 8
P.append(dict(
    title="Character arithmetic and two-pass counting", tier="sec", sim="unique", oneline="characters are numbers: index with c − 'a'",
    why="Unlocks O(1)-space tricks for many easy and medium problems", signature="LC 387 / 1189",
    when="The alphabet is small and fixed, and you need order-aware answers (first, last, earliest).",
    detect="\"first unique character\" · \"maximum number of balloons\" · \"pangram\" · \"alien dictionary order\" · \"half of the string\" · \"minimum steps to make anagrams\".",
    intuition="A character is just a small integer. `'d' − 'a' = 3` is a free array index. Two passes are a classic combo: the first pass collects facts (counts), the second pass uses them in the original order (find the first with count 1).",
    brute="Nested loops comparing each character with all others: O(n²). One counting pass plus one scan: O(n).",
    idea="Map each character to a slot (`c − 'a'`), collect counts in pass one, then answer questions that depend on position in pass two. A bitmask can store \"has this letter been seen\" in one int.",
    steps=["Allocate `int[26]` (or `int[128]` for ASCII).", "Pass 1: count with `count[c − 'a']++`.", "Pass 2: scan the original string and test `count[c − 'a']` for the condition.", "For custom orders, build `rank[c]` from the given order and compare ranks."],
    trace_title="first unique character in `\"loveleetcode\"`",
    trace="""counts: l2 o2 v1 e4 t1 c1 d1
scan:   l(2) o(2) v(1) -> index 2""",
    code=[("first unique character",
           """int[] count = new int[26];
for (char c : s.toCharArray()) count[c - 'a']++;
for (int i = 0; i < s.length(); i++)
    if (count[s.charAt(i) - 'a'] == 1) return i;
return -1;""",
           """from collections import Counter
count = Counter(s)
for i, c in enumerate(s):
    if count[c] == 1:
        return i
return -1"""),
          ("bitmask of seen letters (pangram) and custom order ranks",
           """int mask = 0;
for (char c : s.toCharArray()) mask |= 1 << (c - 'a');
boolean pangram = mask == (1 << 26) - 1;

int[] rank = new int[26];
for (int i = 0; i < order.length(); i++) rank[order.charAt(i) - 'a'] = i;   // alien alphabet""",
           """mask = 0
for c in s:
    mask |= 1 << (ord(c) - 97)
pangram = mask == (1 << 26) - 1

rank = {c: i for i, c in enumerate(order)}      # alien alphabet""")],
    complexity="O(n) time, O(1) space (fixed alphabet).",
    traps=["`c − 'a'` is only valid for lowercase letters; guard or normalise otherwise.", "Alien dictionary: also check the prefix rule (`\"app\"` must come before `\"apple\"`).",
           "`Character` arithmetic in Java promotes to `int`; cast back to `char` when building strings.", "Decide whether case matters before indexing."],
    variants=["Maximum number of balloons: counts divided by required copies, take the minimum.", "Minimum steps to make anagrams: sum of positive differences in counts.", "Caesar shift: `(c − 'a' + k) % 26 + 'a'`."],
    notuse="Large or Unicode alphabets (use a hash map) or problems that need substrings rather than single characters.",
    problems=[
        (387, "First Unique Character in a String", "E", "first-unique-character-in-a-string", "Count, then scan for the first count of 1", "O(n) / O(1)"),
        (1832, "Check if the Sentence Is Pangram", "E", "check-if-the-sentence-is-pangram", "26-bit mask of seen letters", "O(n) / O(1)"),
        (1189, "Maximum Number of Balloons", "E", "maximum-number-of-balloons", "Min over count / needed for b, a, l, o, n", "O(n) / O(1)"),
        (1704, "Determine if String Halves Are Alike", "E", "determine-if-string-halves-are-alike", "Count vowels in each half", "O(n) / O(1)"),
        (953, "Verifying an Alien Dictionary", "E", "verifying-an-alien-dictionary", "Rank each letter, compare adjacent words", "O(total chars) / O(1)"),
        (1347, "Minimum Number of Steps to Make Two Strings Anagram", "M", "minimum-number-of-steps-to-make-two-strings-anagram", "Sum of positive count differences", "O(n) / O(1)"),
    ]))

TOPIC = dict(
    id="strings", file="03_strings.html", title="Strings — Pattern Guide",
    lead="Strings are arrays of characters with extra rules: immutability, small alphabets, and substring structure. This guide covers counting, two pointers, palindromes, windows, pattern matching, stack parsing, in-place edits and character tricks, each with the intuition, a step-through animation, Java and Python code, and a ladder of LeetCode problems.",
    mindset="Almost every string problem becomes easy once you ask **what it is really about**: letter counts (hashing), symmetry (two pointers or a centre), a contiguous range (window), repeated structure (a border or a hash), or nesting (a stack). Because strings are immutable, also watch the hidden cost of building them: use `StringBuilder` / `''.join`.",
    qintro="Ask these questions on every string problem:",
    questions=["**Does order matter?** If not, count characters. If yes, think pointers, window or stack.", "**Is the answer a substring (contiguous) or a subsequence?** Substring → window or centre; subsequence → pointers or DP.",
               "**How big is the alphabet?** 26 or 128 → a fixed array and O(1) space.", "**Is there nesting or a closing token?** → stack.", "**Am I building the result with `+=` in a loop?** → switch to a builder."],
    cues=[
        ["\"anagram\", \"permutation\", \"can construct\", \"group by letters\"", "**P1** Frequency counting"],
        ["\"palindrome\" (whole string), \"reverse in place\", \"is subsequence\"", "**P2** Two pointers"],
        ["\"longest / count palindromic substring\"", "**P3** Expand around the centre"],
        ["\"longest / shortest substring with…\", \"minimum window\"", "**P4** Sliding window"],
        ["\"find the needle\", \"repeated substring\", \"longest prefix that is also a suffix\"", "**P5** KMP / Z / rolling hash"],
        ["brackets, \"decode\", \"simplify path\", \"calculator\"", "**P6** Stack parsing"],
        ["\"in place\", \"compress\", \"add / multiply strings\", \"atoi\"", "**P7** Read / write pointers, simulation"],
        ["\"first unique\", \"pangram\", \"alien order\", small alphabet", "**P8** Character arithmetic"],
    ],
    choose=[
        ["Compare the multiset of letters", "Frequency counting (P1)"],
        ["Check symmetry in O(1) space", "Two pointers (P2)"],
        ["Find all or the longest palindromic substring", "Expand around the centre (P3)"],
        ["Best contiguous range under a rule", "Sliding window (P4)"],
        ["Search a pattern in linear time", "KMP or rolling hash (P5)"],
        ["Nested or balanced structure", "Stack (P6)"],
        ["Rewrite or do arithmetic on strings", "Pointers and carries (P7)"],
        ["Position-aware facts about a small alphabet", "Two-pass counting (P8)"],
    ],
    rule="if the question says **substring**, think window or centre; if it says **subsequence**, think two pointers or DP; if it says **anagram or permutation**, think counts; if it has **brackets**, think stack.",
    selftest=[
        ("Why compare character counts instead of sorting to test anagrams?", "Counting is O(n) time and O(1) space for a fixed alphabet; sorting is O(n log n)."),
        ("Why must expand-around-centre try even-length centres as well?", "A palindrome like \"abba\" has no single middle character; its centre is the gap between the two b's, so only the even expansion finds it."),
        ("In KMP, what does `lps[i]` mean and why does a mismatch use `lps[len − 1]`?", "`lps[i]` is the longest proper prefix of `p[0..i]` that is also its suffix. After a mismatch the next-best partial match is the longest border of what has matched so far, which is `lps[len − 1]`, so the text pointer never moves back."),
        ("What is the complexity of building a string with `s += c` in a loop of n iterations?", "O(n²), because each concatenation copies the existing string. Use `StringBuilder` or `''.join` for O(n)."),
        ("Why is `3[a2[c]]` naturally solved with a stack?", "The innermost bracket must be finished first. A stack stores the unfinished outer context (count and text) and returns it in last-in, first-out order."),
        ("When does a window for \"minimum window substring\" count as valid?", "When every required letter has at least its needed count inside the window, tracked by a `formed` counter that equals the number of distinct required letters."),
        ("Why is `count[c − 'a']` risky?", "It only works for lowercase `a–z`. Uppercase, digits or Unicode produce negative or out-of-range indices; use a larger array or a hash map."),
        ("Subsequence or substring: which problem allows a sliding window?", "Substring (contiguous). Subsequence problems use two pointers (matching) or dynamic programming."),
    ],
    plan=[
        "**Days 1–2:** frequency counting and two pointers. Do every Easy on both ladders without hints.",
        "**Day 3:** expand around the centre and the fixed-window anagram problems.",
        "**Days 4–5:** variable sliding window (LC 3, 424, 76). These recur constantly.",
        "**Day 6:** stack parsing: parentheses, decode string, calculator.",
        "**Day 7:** in-place edits and character tricks; implement atoi and add-strings carefully.",
        "**Day 8:** KMP: build lps by hand for three strings, then code it. Revisit anything you needed a hint for.",
    ],
    patterns=P,
)
