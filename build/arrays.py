"""Content for topic 02: Arrays, hashing and searching."""

P = []

# ---------------------------------------------------------------- 1
P.append(dict(
    title="Two Pointers", tier="hot", sim="two", oneline="move two indices to avoid O(n²)",
    why="Pairs, palindromes and in-place edits all collapse to it", signature="LC 167 / 15",
    when="A sorted array or a string where two indices moving toward (or along with) each other replace a nested loop.",
    detect="sorted input · \"pair/triplet with target sum\" · \"remove duplicates in place\" · palindrome check · \"reverse in place\" · \"partition so that…\".",
    intuition="Picture two people walking toward each other along a sorted number line. If their combined value is too small, only the left person stepping right can help; if too large, only the right person stepping left can help. Every step permanently rules out one element, so you never look back.",
    brute="Check every pair with two loops: O(n²). Sorting gives each pointer a direction to move, so one pass of n steps is enough: O(n).",
    idea="Two indices, usually `l` and `r`, move based on a comparison. The sorted order guarantees that discarding one end can never throw away the answer.",
    steps=["`l = 0`, `r = n-1`.", "Compare `a[l] + a[r]` with the target.", "Too small → `l++`. Too big → `r--`. Equal → record and finish."],
    trace_title="Two Sum II on `[1,3,4,6,8,11]`, target 10",
    trace="""l=0(1)  r=5(11) sum 12 > 10  r--
l=0(1)  r=4(8)  sum  9 < 10  l++
l=1(3)  r=4(8)  sum 11 > 10  r--
l=1(3)  r=3(6)  sum  9 < 10  l++
l=2(4)  r=3(6)  sum 10 == 10 -> found""",
    code=[("opposite ends (sorted pair sum)",
           """int l = 0, r = n - 1;
while (l < r) {
    int sum = a[l] + a[r];
    if (sum == target) return new int[]{l + 1, r + 1};
    if (sum < target) l++; else r--;
}
return new int[]{-1, -1};""",
           """l, r = 0, len(a) - 1
while l < r:
    s = a[l] + a[r]
    if s == target:
        return [l + 1, r + 1]
    if s < target:
        l += 1
    else:
        r -= 1
return [-1, -1]"""),
          ("same direction (slow writes, fast reads) for in-place edits",
           """int slow = 0;
for (int fast = 0; fast < n; fast++) {
    if (a[fast] != 0) a[slow++] = a[fast];   // keep non-zeros
}
while (slow < n) a[slow++] = 0;""",
           """slow = 0
for fast in range(len(a)):
    if a[fast] != 0:
        a[slow] = a[fast]
        slow += 1
for i in range(slow, len(a)):
    a[i] = 0""")],
    complexity="O(n) time after any sort, O(1) extra space.",
    traps=["3Sum: sort first, fix one element, skip duplicates for the fixed element **and** after finding a triple.",
           "Opposite-end version needs sorted data; same-direction version does not.",
           "Container With Most Water has no sort: you move the **shorter** wall because only that can raise the area."],
    variants=["Closest sum instead of exact (3Sum Closest): track the best difference.", "k-Sum: recurse down to two pointers, O(n^(k-1)).", "Palindrome with deletions: when mismatch, try skipping either side."],
    notuse="When order cannot change and the data is not sortable for the task, or when every pair genuinely matters.",
    problems=[
        (125, "Valid Palindrome", "E", "valid-palindrome", "Ends move inward, skip non-alphanumerics, compare lowercase", "O(n) / O(1)"),
        (283, "Move Zeroes", "E", "move-zeroes", "Slow = next write slot for a non-zero; fast scans", "O(n) / O(1)"),
        (26, "Remove Duplicates from Sorted Array", "E", "remove-duplicates-from-sorted-array", "Slow marks the last unique; copy when fast sees a new value", "O(n) / O(1)"),
        (167, "Two Sum II - Input Array Is Sorted", "M", "two-sum-ii-input-array-is-sorted", "Too small → l++, too big → r--", "O(n) / O(1)"),
        (11, "Container With Most Water", "M", "container-with-most-water", "Move the shorter wall; the taller one alone cannot improve area", "O(n) / O(1)"),
        (15, "3Sum", "M", "3sum", "Sort, fix i, two pointers on the rest, skip duplicates", "O(n²) / O(1)"),
        (16, "3Sum Closest", "M", "3sum-closest", "Same as 3Sum, keep the sum closest to target", "O(n²) / O(1)"),
        (42, "Trapping Rain Water", "H", "trapping-rain-water", "Water at i = min(leftMax, rightMax) − h; advance the side with the smaller max", "O(n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 2
P.append(dict(
    title="Sliding Window (Fixed)", tier="sec", sim="fixed", oneline="add the entering element, drop the leaving one",
    why="Simple, shows up as the warm-up for variable windows", signature="LC 643",
    when="Compute something over every contiguous window of a fixed size `k`.",
    detect="\"subarray/substring of size k\" · max/min/average over windows of length k · \"anagram of a pattern\" (window = pattern length).",
    intuition="A train of k carriages passing a platform: as the front carriage enters, the rear one leaves. You do not recount all k carriages; you add one and remove one.",
    brute="Re-sum every window: O(n·k). Updating the sum incrementally costs O(1) per step: O(n).",
    idea="Keep the window's aggregate; on each step add the entering element and subtract the leaving one.",
    steps=["Build the first window of size `k`.", "For each next index `i`: add `a[i]`, subtract `a[i-k]`.", "Update the answer after each slide."],
    trace_title="max sum, k = 3, `[2,1,5,1,3,2]`",
    trace="""window [2,1,5] = 8   best 8
 +1 -2        -> 7
 +3 -1        -> 9   best 9
 +2 -5        -> 6
=> 9""",
    code=[("max sum of a window of size k",
           """int sum = 0;
for (int i = 0; i < k; i++) sum += a[i];
int best = sum;
for (int i = k; i < n; i++) {
    sum += a[i] - a[i - k];
    best = Math.max(best, sum);
}""",
           """s = sum(a[:k])
best = s
for i in range(k, len(a)):
    s += a[i] - a[i - k]
    best = max(best, s)""")],
    complexity="O(n) time, O(1) space (O(k) if you keep a count map or deque).",
    traps=["Off-by-one on `i - k`.", "Initialise the answer from the first full window, not 0 (breaks with negatives).",
           "For anagram windows compare two 26-slot count arrays, or keep a \"matched characters\" counter to make each step O(1)."],
    variants=["Window maximum: a monotonic deque of indices keeps the max at the front (LC 239).", "Counting distinct values in each window: maintain a count map."],
    notuse="When the window size depends on a condition: that is the variable window (pattern 3).",
    problems=[
        (643, "Maximum Average Subarray I", "E", "maximum-average-subarray-i", "Slide the sum, divide the best by k", "O(n) / O(1)"),
        (1456, "Maximum Number of Vowels in a Substring of Given Length", "M", "maximum-number-of-vowels-in-a-substring-of-given-length", "Count vowels in the window; add entering, drop leaving", "O(n) / O(1)"),
        (567, "Permutation in String", "M", "permutation-in-string", "Window of len(s1); compare 26-count arrays", "O(n) / O(1)"),
        (438, "Find All Anagrams in a String", "M", "find-all-anagrams-in-a-string", "Same as 567 but record every matching start index", "O(n) / O(1)"),
        (1052, "Grumpy Bookstore Owner", "M", "grumpy-bookstore-owner", "Always-happy base + best extra gain from one window of size minutes", "O(n) / O(1)"),
        (239, "Sliding Window Maximum", "H", "sliding-window-maximum", "Deque of indices with decreasing values; the front is the window max", "O(n) / O(k)"),
    ]))

# ---------------------------------------------------------------- 3
P.append(dict(
    title="Sliding Window (Variable)", tier="hot", sim="variable", oneline="grow right, shrink left while invalid",
    why="\"Longest / shortest substring with…\" is everywhere", signature="LC 3 / 76",
    when="Find the longest or shortest contiguous range that satisfies a condition.",
    detect="\"longest/shortest substring with…\" · \"at most K distinct\" · \"subarray sum ≤ S\" · \"smallest window containing…\".",
    intuition="An inchworm: the head (right) stretches forward to take in more; whenever the body becomes illegal, the tail (left) pulls in until it is legal again. Neither end ever moves backwards, so each element is added once and removed once.",
    brute="Check every (start, end) pair and validate each: O(n²) or O(n³). Because the window only ever moves forward, the total work is 2n pointer moves: O(n).",
    idea="Expand `r` to include elements. While the window violates the condition, advance `l` and undo its contribution. Record the best valid window.",
    steps=["Move `r` outward, updating window state (count map, running sum).", "While invalid, advance `l`, undoing its contribution.", "When valid, record the answer (length or position)."],
    trace_title="longest substring without repeats, `\"abcabcbb\"`",
    trace="""r=0 a  window "a"    len 1
r=1 b  window "ab"   len 2
r=2 c  window "abc"  len 3   best 3
r=3 a  duplicate -> drop 'a' (l=1) -> "bca"   len 3
r=4 b  duplicate -> drop 'b' (l=2) -> "cab"   len 3
...
=> 3""",
    code=[("longest valid window (template)",
           """int l = 0, best = 0;
Map<Character, Integer> count = new HashMap<>();
for (int r = 0; r < s.length(); r++) {
    count.merge(s.charAt(r), 1, Integer::sum);
    while (count.get(s.charAt(r)) > 1) {          // window invalid
        count.merge(s.charAt(l), -1, Integer::sum);
        l++;
    }
    best = Math.max(best, r - l + 1);
}""",
           """l = best = 0
count = {}
for r, ch in enumerate(s):
    count[ch] = count.get(ch, 0) + 1
    while count[ch] > 1:                  # window invalid
        count[s[l]] -= 1
        l += 1
    best = max(best, r - l + 1)"""),
          ("shortest valid window (record while valid, shrink as far as possible)",
           """int l = 0, sum = 0, best = Integer.MAX_VALUE;
for (int r = 0; r < n; r++) {
    sum += a[r];
    while (sum >= target) {                       // valid: try to shrink
        best = Math.min(best, r - l + 1);
        sum -= a[l++];
    }
}
return best == Integer.MAX_VALUE ? 0 : best;""",
           """l = total = 0
best = float('inf')
for r, x in enumerate(a):
    total += x
    while total >= target:                # valid: try to shrink
        best = min(best, r - l + 1)
        total -= a[l]
        l += 1
return 0 if best == float('inf') else best""")],
    complexity="O(n) time (each element enters and leaves once), O(k) space for the window state.",
    traps=["Forgetting to undo `l`'s contribution when shrinking.",
           "**Longest** → update the answer after the shrink loop; **shortest** → update inside the loop while valid.",
           "\"Exactly K\" = \"at most K\" − \"at most K−1\".",
           "Negative numbers break shrinking (adding can reduce the sum). Use prefix sum + hash map instead."],
    variants=["At most K distinct / replacements: window is valid while `size − maxFreq ≤ k`.", "Count subarrays: add `r − l + 1` for each valid right end (LC 713).", "Min window containing all of a pattern: keep a `need` count and a `formed` counter."],
    notuse="When the subarray need not be contiguous, or when negatives make the validity non-monotonic.",
    problems=[
        (3, "Longest Substring Without Repeating Characters", "M", "longest-substring-without-repeating-characters", "Count map; shrink while a character repeats", "O(n) / O(min(n,σ))"),
        (1004, "Max Consecutive Ones III", "M", "max-consecutive-ones-iii", "At most k zeros in the window; shrink when exceeded", "O(n) / O(1)"),
        (904, "Fruit Into Baskets", "M", "fruit-into-baskets", "At most 2 distinct types; count map", "O(n) / O(1)"),
        (209, "Minimum Size Subarray Sum", "M", "minimum-size-subarray-sum", "Shrink while sum ≥ target, record the min length", "O(n) / O(1)"),
        (713, "Subarray Product Less Than K", "M", "subarray-product-less-than-k", "Keep product < k; add r−l+1 subarrays ending at r", "O(n) / O(1)"),
        (424, "Longest Repeating Character Replacement", "M", "longest-repeating-character-replacement", "Valid while window − maxFreq ≤ k; window never needs to shrink below its best", "O(n) / O(1)"),
        (76, "Minimum Window Substring", "H", "minimum-window-substring", "Expand until all needed chars are covered, then shrink to the minimum", "O(n+m) / O(m)"),
        (992, "Subarrays with K Different Integers", "H", "subarrays-with-k-different-integers", "atMost(K) − atMost(K−1)", "O(n) / O(K)"),
    ]))

# ---------------------------------------------------------------- 4
P.append(dict(
    title="Prefix Sum", tier="hot", sim="prefix", oneline="precompute running totals; pair with a hash map",
    why="Subarray-sum problems lean on it constantly", signature="LC 560",
    when="Many range-sum queries, or counting subarrays whose sum hits a target.",
    detect="\"sum between i and j\" · repeated range queries · \"number of subarrays with sum = k / divisible by k\" · arrays with negatives.",
    intuition="Think of kilometre markers on a road. The distance between two markers is just the difference of their readings. If the reading at your current position minus an earlier reading equals k, the stretch between them is exactly k long. So ask the map: \"have I seen the reading `current − k` before?\"",
    brute="Sum every subarray: O(n²) (or O(n³)). With prefix sums each range is one subtraction; with a hash map of earlier prefixes each index is one lookup: O(n).",
    idea="`pre[i]` = sum of the first `i` elements, so `sum(i..j) = pre[j+1] − pre[i]`. Combine with a map `prefix → count` to count subarrays in one pass.",
    steps=["Keep a running `sum` and a map `prefix → how many times seen`, seeded with `{0:1}`.", "At each index the number of valid subarrays ending here is `map[sum − k]`.", "Then add the current `sum` to the map."],
    trace_title="count subarrays with sum = 2 in `[1,1,1]`",
    trace="""seed {0:1}
sum 1 -> need -1 (0)   add {1:1}
sum 2 -> need  0 (1!)  count=1  add {2:1}
sum 3 -> need  1 (1!)  count=2  add {3:1}
=> 2""",
    code=[("count subarrays summing to k",
           """Map<Integer, Integer> seen = new HashMap<>();
seen.put(0, 1);                       // empty prefix
int sum = 0, count = 0;
for (int x : a) {
    sum += x;
    count += seen.getOrDefault(sum - k, 0);
    seen.merge(sum, 1, Integer::sum);
}""",
           """seen = {0: 1}                         # empty prefix
total = count = 0
for x in a:
    total += x
    count += seen.get(total - k, 0)
    seen[total] = seen.get(total, 0) + 1"""),
          ("static range-sum queries",
           """int[] pre = new int[n + 1];
for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + a[i];
// sum of a[i..j] inclusive
int rangeSum = pre[j + 1] - pre[i];""",
           """pre = [0] * (len(a) + 1)
for i, x in enumerate(a):
    pre[i + 1] = pre[i] + x
range_sum = pre[j + 1] - pre[i]        # a[i..j] inclusive""")],
    complexity="O(n) time, O(n) space.",
    traps=["Seed the map with `{0:1}` or you miss subarrays that start at index 0.", "Divisible-by-k: normalise the remainder with `((s % k) + k) % k` in Java.",
           "Prefix XOR is the same trick with XOR. For 2D use a 2D prefix with inclusion–exclusion.", "If the array is updated between queries a static prefix goes stale: use a Fenwick or segment tree."],
    variants=["Longest subarray with sum k: store the **first** index of each prefix instead of a count.", "Equal 0s and 1s: map 0 → −1, then longest subarray with sum 0.", "Product except self: prefix and suffix products."],
    notuse="When values change between queries (use BIT / segment tree), or when you only need a single sum (just loop).",
    problems=[
        (303, "Range Sum Query - Immutable", "E", "range-sum-query-immutable", "Build pre[] once; each query is pre[j+1] − pre[i]", "O(n) build, O(1) query / O(n)"),
        (724, "Find Pivot Index", "E", "find-pivot-index", "left == total − left − a[i]", "O(n) / O(1)"),
        (238, "Product of Array Except Self", "M", "product-of-array-except-self", "Prefix-product pass then suffix-product pass", "O(n) / O(1) extra"),
        (560, "Subarray Sum Equals K", "M", "subarray-sum-equals-k", "Map of prefix counts; add count[sum − k]", "O(n) / O(n)"),
        (525, "Contiguous Array", "M", "contiguous-array", "0 → −1; equal prefix sums mean a balanced stretch; store first index", "O(n) / O(n)"),
        (974, "Subarray Sums Divisible by K", "M", "subarray-sums-divisible-by-k", "Count equal prefix remainders; fix negative modulo", "O(n) / O(k)"),
        (304, "Range Sum Query 2D - Immutable", "M", "range-sum-query-2d-immutable", "2D prefix with inclusion–exclusion", "O(mn) build, O(1) query / O(mn)"),
    ]))

# ---------------------------------------------------------------- 5
P.append(dict(
    title="Kadane's Algorithm", tier="sec", sim="kadane", oneline="extend the run or restart it",
    why="One idea, asked as a classic and as many twists", signature="LC 53",
    when="Maximum-sum (or product) contiguous subarray.",
    detect="\"maximum subarray sum/product\" · contiguous segment · a running optimum that can \"restart\".",
    intuition="You are walking and collecting money (positive) or paying tolls (negative). If your wallet balance since the start of the current run has gone negative, that history can only hurt, so drop it and start a fresh run from here.",
    brute="Try every subarray: O(n²). Observing that the best subarray ending at `i` is either `a[i]` alone or extends the best ending at `i−1` gives O(n).",
    idea="`cur = max(a[i], cur + a[i])` is the best subarray **ending at** `i`; `best` is the maximum of `cur` seen so far.",
    steps=["`cur = best = a[0]`.", "For each next element: `cur = max(a[i], cur + a[i])`.", "`best = max(best, cur)`."],
    trace_title="`[-2,1,-3,4,-1,2,1,-5,4]`",
    trace="""cur:  -2  1 -2  4  3  5  6  1  5
best: -2  1  1  4  4  5  6  6  6
=> 6   (subarray [4,-1,2,1])""",
    code=[("maximum subarray sum",
           """int cur = a[0], best = a[0];
for (int i = 1; i < n; i++) {
    cur = Math.max(a[i], cur + a[i]);
    best = Math.max(best, cur);
}""",
           """cur = best = a[0]
for x in a[1:]:
    cur = max(x, cur + x)
    best = max(best, cur)"""),
          ("maximum product subarray (negatives flip sign: track both)",
           """int mx = a[0], mn = a[0], best = a[0];
for (int i = 1; i < n; i++) {
    int x = a[i];
    int hi = Math.max(x, Math.max(mx * x, mn * x));
    int lo = Math.min(x, Math.min(mx * x, mn * x));
    mx = hi; mn = lo;
    best = Math.max(best, mx);
}""",
           """mx = mn = best = a[0]
for x in a[1:]:
    hi = max(x, mx * x, mn * x)
    lo = min(x, mx * x, mn * x)
    mx, mn = hi, lo
    best = max(best, mx)""")],
    complexity="O(n) time, O(1) space.",
    traps=["Initialise from `a[0]`, not 0, or all-negative arrays return 0.", "Max product needs both the running max and min.",
           "Circular array: answer = `max(kadane, total − minSubarray)`, except when every element is negative."],
    variants=["Return the subarray itself: remember `start` whenever you restart.", "One deletion allowed (LC 1186): two DP states."],
    notuse="When the subarray need not be contiguous, or you need a **count** of subarrays rather than the best one.",
    problems=[
        (121, "Best Time to Buy and Sell Stock", "E", "best-time-to-buy-and-sell-stock", "Track the minimum price so far; best = max(price − min)", "O(n) / O(1)"),
        (53, "Maximum Subarray", "M", "maximum-subarray", "cur = max(a[i], cur + a[i])", "O(n) / O(1)"),
        (152, "Maximum Product Subarray", "M", "maximum-product-subarray", "Track running max and min product", "O(n) / O(1)"),
        (918, "Maximum Sum Circular Subarray", "M", "maximum-sum-circular-subarray", "max(Kadane max, total − Kadane min); handle all-negative", "O(n) / O(1)"),
        (1749, "Maximum Absolute Sum of Any Subarray", "M", "maximum-absolute-sum-of-any-subarray", "max(max-Kadane, |min-Kadane|)", "O(n) / O(1)"),
        (1186, "Maximum Subarray Sum with One Deletion", "M", "maximum-subarray-sum-with-one-deletion", "Two states: no deletion yet / one used", "O(n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 6
P.append(dict(
    title="Hashing: Two Sum, Counting, Grouping", tier="hot", sim="hash", oneline="trade space for O(1) lookups",
    why="The single most-asked array idea", signature="LC 1 / 49",
    when="Answer \"have I seen X?\", \"how many times?\" or \"group items by a key\" in O(1) per element.",
    detect="\"find a pair with this complement\" · \"first unique\" · \"group anagrams\" · \"top K frequent\" · counting occurrences · \"longest consecutive run\".",
    intuition="A hash map is a coat-check desk: hand over an item, get an instant answer to \"is it here?\". Instead of searching the whole array for the partner of x, you ask the desk whether `target − x` was checked in earlier.",
    brute="For each element scan the rest for its partner: O(n²). A map that remembers what you have seen makes each lookup O(1): O(n) time for O(n) space.",
    idea="Store what you have seen (value → index, value → count, key → group). For Two Sum look up `target − x`. For grouping, derive a canonical key (sorted string or a 26-count signature).",
    steps=["For each `x`, check whether `target − x` is already in the map.", "If yes, you have the pair; otherwise store `x → index`.", "Store **after** checking so one element is never used twice."],
    trace_title="Two Sum `[3,2,4]`, target 6",
    trace="""3: need 3? no   store {3:0}
2: need 4? no   store {2:1}
4: need 2? yes (index 1) -> [1,2]""",
    code=[("Two Sum",
           """Map<Integer, Integer> seen = new HashMap<>();
for (int i = 0; i < n; i++) {
    Integer j = seen.get(target - a[i]);
    if (j != null) return new int[]{j, i};
    seen.put(a[i], i);
}""",
           """seen = {}
for i, x in enumerate(a):
    if target - x in seen:
        return [seen[target - x], i]
    seen[x] = i"""),
          ("Group Anagrams (canonical key)",
           """Map<String, List<String>> groups = new HashMap<>();
for (String w : words) {
    char[] c = w.toCharArray();
    Arrays.sort(c);
    groups.computeIfAbsent(new String(c), k -> new ArrayList<>()).add(w);
}
return new ArrayList<>(groups.values());""",
           """from collections import defaultdict
groups = defaultdict(list)
for w in words:
    groups[''.join(sorted(w))].append(w)
return list(groups.values())"""),
          ("Longest Consecutive Sequence (start only at run beginnings)",
           """Set<Integer> set = new HashSet<>();
for (int x : a) set.add(x);
int best = 0;
for (int x : set) {
    if (set.contains(x - 1)) continue;        // not the start of a run
    int len = 1;
    while (set.contains(x + len)) len++;
    best = Math.max(best, len);
}""",
           """s = set(a)
best = 0
for x in s:
    if x - 1 in s:
        continue                          # not the start of a run
    length = 1
    while x + length in s:
        length += 1
    best = max(best, length)""")],
    complexity="O(n) time, O(n) space.",
    traps=["Store after checking (otherwise `target = 2x` reuses the same element).", "Pick a stable canonical key when grouping. Sorting costs O(k log k) per word; a count signature is O(k).",
           "Top-K frequent: bucket by frequency for O(n), or a min-heap of size k for O(n log k).", "Hash map worst case is O(n) per operation; say \"expected O(1)\" in interviews."],
    variants=["Return all pairs: store lists of indices, or sort + two pointers to dedupe.", "Subarray problems: pair a map with a prefix sum (pattern 4).", "Design O(1) insert/delete/random: array + map of value → index (swap with last)."],
    notuse="When O(1) extra space is required and the array is sorted (two pointers), or when order of results matters more than speed.",
    problems=[
        (217, "Contains Duplicate", "E", "contains-duplicate", "Set; a repeat means true", "O(n) / O(n)"),
        (242, "Valid Anagram", "E", "valid-anagram", "Compare frequency counts", "O(n) / O(1)"),
        (1, "Two Sum", "E", "two-sum", "Map value → index; look up target − x", "O(n) / O(n)"),
        (49, "Group Anagrams", "M", "group-anagrams", "Key = sorted string or 26-count tuple", "O(N·K log K) / O(N·K)"),
        (347, "Top K Frequent Elements", "M", "top-k-frequent-elements", "Count, then bucket by frequency", "O(n) / O(n)"),
        (36, "Valid Sudoku", "M", "valid-sudoku", "A set per row, column and 3×3 box", "O(81) / O(81)"),
        (128, "Longest Consecutive Sequence", "M", "longest-consecutive-sequence", "Start counting only at numbers with no x−1 present", "O(n) / O(n)"),
        (454, "4Sum II", "M", "4sum-ii", "Map of a+b sums; look up −(c+d)", "O(n²) / O(n²)"),
        (380, "Insert Delete GetRandom O(1)", "M", "insert-delete-getrandom-o1", "Array + map value → index; delete by swapping with the last", "O(1) avg per op / O(n)"),
    ]))

# ---------------------------------------------------------------- 7
P.append(dict(
    title="Dutch National Flag (3-way partition)", tier="sec", sim="dutch", oneline="three pointers, one pass",
    why="One canonical problem, but the partition idea reappears in quicksort", signature="LC 75",
    when="Three-way partition of an array in one pass, in place.",
    detect="\"sort 0s, 1s and 2s\" · partition around a pivot into `<`, `=`, `>` · \"move all X to the front\".",
    intuition="Sorting three colours of laundry into three piles using only the floor in front of you: zeros are thrown to the left pile, twos to the right pile, ones are left where they land in the middle. The middle pointer only advances when it is certain what it is standing on.",
    brute="Counting sort needs two passes (count, then rewrite). Three pointers sort in a single pass with O(1) space.",
    idea="`lo` = end of the 0-zone, `hi` = start of the 2-zone, `mid` scans the unknown middle. Everything before `lo` is 0, everything after `hi` is 2.",
    steps=["`mid` walks right.", "`a[mid] == 0`: swap with `lo`, advance both.", "`a[mid] == 2`: swap with `hi`, `hi--`, **do not** advance `mid`.", "`a[mid] == 1`: advance `mid`."],
    trace_title="`[2,0,2,1,1,0]`",
    trace="""[2,0,2,1,1,0] mid=0 is 2 -> swap hi        [0,0,2,1,1,2]
[0,0,2,1,1,2] mid=0 is 0 -> lo++,mid++
[0,0,2,1,1,2] mid=1 is 0 -> lo++,mid++
[0,0,2,1,1,2] mid=2 is 2 -> swap hi        [0,0,1,1,2,2]
mid=2 is 1, mid=3 is 1 -> mid passes hi -> sorted""",
    code=[("sort colors",
           """int lo = 0, mid = 0, hi = n - 1;
while (mid <= hi) {
    if (a[mid] == 0) { swap(a, lo++, mid++); }
    else if (a[mid] == 2) { swap(a, mid, hi--); }
    else mid++;
}""",
           """lo, mid, hi = 0, 0, len(a) - 1
while mid <= hi:
    if a[mid] == 0:
        a[lo], a[mid] = a[mid], a[lo]
        lo += 1
        mid += 1
    elif a[mid] == 2:
        a[mid], a[hi] = a[hi], a[mid]
        hi -= 1
    else:
        mid += 1""")],
    complexity="O(n) time, O(1) space.",
    traps=["Do **not** advance `mid` after swapping with `hi`: the value swapped in is unexamined.", "Loop condition is `mid <= hi`, not `mid < hi`."],
    variants=["Two categories (move zeroes, sort by parity): a single slow/fast pointer.", "Partition around a pivot value: `<` left, `=` middle, `>` right (quick sort with many duplicates)."],
    notuse="More than three categories (use counting sort) or when a stable order must be preserved.",
    problems=[
        (905, "Sort Array By Parity", "E", "sort-array-by-parity", "Two-way partition: evens to the front", "O(n) / O(1)"),
        (922, "Sort Array By Parity II", "E", "sort-array-by-parity-ii", "Two pointers on even and odd positions, swap mismatches", "O(n) / O(1)"),
        (75, "Sort Colors", "M", "sort-colors", "Dutch flag with lo / mid / hi", "O(n) / O(1)"),
        (2161, "Partition Array According to Given Pivot", "M", "partition-array-according-to-given-pivot", "Three buckets preserving relative order (not in place)", "O(n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 8
P.append(dict(
    title="Binary Search (basic and on the answer)", tier="hot", sim="binary", oneline="halve a monotonic space",
    why="Classic, and \"search on answer\" is an interview favourite", signature="LC 704 / 875",
    when="Sorted data, or a numeric answer space where feasibility is monotonic (once true, always true).",
    detect="sorted array + O(log n) · \"first / last occurrence\" · \"minimise the maximum\" or \"maximise the minimum\" · \"smallest value such that a check passes\".",
    intuition="Guess-the-number game: each guess eliminates half the possibilities. The deep idea is not about arrays; it is about any yes/no question whose answer flips exactly once along a line: `F F F F T T T T`. Binary search finds the flip point.",
    brute="Scan linearly for the first true: O(n). Halving the range each time: O(log n). For \"search on answer\" it is O(n) per check × O(log range) checks.",
    idea="Keep an invariant such as \"the answer is inside `[lo, hi]`\". Look at `mid`: if the condition holds, the answer is at `mid` or to its left (`hi = mid`); otherwise it is to the right (`lo = mid + 1`).",
    steps=["Choose `lo`, `hi` so the answer is guaranteed inside.", "`mid = lo + (hi − lo) / 2`.", "Condition true → `hi = mid`; false → `lo = mid + 1`.", "Stop when `lo == hi`; that is the boundary."],
    trace_title="first index with `a[i] ≥ 7` in `[1,3,5,7,7,7,9,11]`",
    trace="""lo=0 hi=7 mid=3 a=7 >= 7 -> hi=3
lo=0 hi=3 mid=1 a=3 <  7 -> lo=2
lo=2 hi=3 mid=2 a=5 <  7 -> lo=3
lo=hi=3 -> first 7 is at index 3""",
    code=[("lower bound (first index with a[i] >= target)",
           """int lo = 0, hi = n - 1;
while (lo < hi) {
    int mid = lo + (hi - lo) / 2;
    if (a[mid] >= target) hi = mid;   // mid may be the answer
    else lo = mid + 1;
}
return a[lo] == target ? lo : -1;""",
           """lo, hi = 0, len(a) - 1
while lo < hi:
    mid = lo + (hi - lo) // 2
    if a[mid] >= target:
        hi = mid                      # mid may be the answer
    else:
        lo = mid + 1
return lo if a[lo] == target else -1"""),
          ("search on the answer (Koko Eating Bananas: smallest feasible speed)",
           """int lo = 1, hi = max(piles);
while (lo < hi) {
    int mid = lo + (hi - lo) / 2;
    if (hours(piles, mid) <= h) hi = mid;     // feasible: try smaller
    else lo = mid + 1;
}
return lo;
// hours(): sum of ceil(pile / speed)""",
           """lo, hi = 1, max(piles)
while lo < hi:
    mid = lo + (hi - lo) // 2
    if sum(-(-p // mid) for p in piles) <= h:   # feasible: try smaller
        hi = mid
    else:
        lo = mid + 1
return lo""")],
    complexity="O(log n) basic; O(n log range) for search on answer; O(1) space.",
    traps=["Use `lo + (hi − lo) / 2` to avoid integer overflow.", "Pick one invariant and stick to it: `lo < hi` with `hi = mid` (boundary search) vs `lo <= hi` with `hi = mid − 1` (exact search).",
           "`lo = mid` without `+1` can loop forever.", "For \"maximise the minimum\" flip the condition and use `mid = lo + (hi − lo + 1) / 2`."],
    variants=["Last occurrence: lower bound of `target + 1`, minus one.", "Peak element: compare `a[mid]` with `a[mid+1]` and climb.", "Binary search on a 2D matrix: treat it as a flattened sorted array.", "Median of two sorted arrays: binary search the partition of the shorter array."],
    notuse="Unsorted data with no monotonic feasibility relation.",
    problems=[
        (704, "Binary Search", "E", "binary-search", "Classic exact search", "O(log n) / O(1)"),
        (35, "Search Insert Position", "E", "search-insert-position", "Lower bound: first index ≥ target", "O(log n) / O(1)"),
        (69, "Sqrt(x)", "E", "sqrtx", "Largest m with m·m ≤ x (use long)", "O(log x) / O(1)"),
        (34, "Find First and Last Position of Element in Sorted Array", "M", "find-first-and-last-position-of-element-in-sorted-array", "Lower bound of target and of target + 1", "O(log n) / O(1)"),
        (74, "Search a 2D Matrix", "M", "search-a-2d-matrix", "Flatten: mid → (mid / cols, mid % cols)", "O(log mn) / O(1)"),
        (162, "Find Peak Element", "M", "find-peak-element", "Compare mid with mid + 1 and move uphill", "O(log n) / O(1)"),
        (875, "Koko Eating Bananas", "M", "koko-eating-bananas", "Search speed; feasible if total hours ≤ h", "O(n log max) / O(1)"),
        (1011, "Capacity To Ship Packages Within D Days", "M", "capacity-to-ship-packages-within-d-days", "Search capacity in [max, sum]; greedy day count", "O(n log sum) / O(1)"),
        (410, "Split Array Largest Sum", "H", "split-array-largest-sum", "Search the largest-part sum; greedy count of parts ≤ m", "O(n log sum) / O(1)"),
        (4, "Median of Two Sorted Arrays", "H", "median-of-two-sorted-arrays", "Binary search the partition of the shorter array", "O(log min(m,n)) / O(1)"),
    ]))

# ---------------------------------------------------------------- 9
P.append(dict(
    title="Binary Search on a Rotated Array", tier="sec", sim="rotated", oneline="one half is always sorted",
    why="Specific but recurs as a follow-up", signature="LC 33",
    when="A sorted array rotated at an unknown pivot.",
    detect="\"sorted array rotated\" · \"find the minimum in a rotated array\" · plain binary search alone fails.",
    intuition="Cut a sorted deck at a random point and swap the halves. Wherever you look at the middle card, at least one side of it is still a perfectly sorted run. Work out which side that is, check whether your target could live in that run, and discard the other half.",
    brute="Linear scan is O(n). Using the \"one half is sorted\" fact each step still discards half: O(log n).",
    idea="Compare `a[lo]` with `a[mid]` to find the sorted half. If the target lies inside that half's range, search it; otherwise search the other half.",
    steps=["Compute `mid`. If `a[mid] == target`, done.", "If `a[lo] <= a[mid]` the left half is sorted, else the right half is.", "If target is within the sorted half's range, go there; otherwise go to the other half."],
    trace_title="find 0 in `[4,5,6,7,0,1,2]`",
    trace="""lo=0 hi=6 mid=3 (7): left [4..7] sorted, 0 not inside -> lo=4
lo=4 hi=6 mid=5 (1): left [0..1] sorted, 0 inside        -> hi=4
lo=4 hi=4 mid=4 (0): found at index 4""",
    code=[("search a target",
           """int lo = 0, hi = n - 1;
while (lo <= hi) {
    int mid = lo + (hi - lo) / 2;
    if (a[mid] == target) return mid;
    if (a[lo] <= a[mid]) {                    // left half sorted
        if (a[lo] <= target && target < a[mid]) hi = mid - 1; else lo = mid + 1;
    } else {                                  // right half sorted
        if (a[mid] < target && target <= a[hi]) lo = mid + 1; else hi = mid - 1;
    }
}
return -1;""",
           """lo, hi = 0, len(a) - 1
while lo <= hi:
    mid = lo + (hi - lo) // 2
    if a[mid] == target:
        return mid
    if a[lo] <= a[mid]:                       # left half sorted
        if a[lo] <= target < a[mid]:
            hi = mid - 1
        else:
            lo = mid + 1
    else:                                     # right half sorted
        if a[mid] < target <= a[hi]:
            lo = mid + 1
        else:
            hi = mid - 1
return -1"""),
          ("find the minimum",
           """int lo = 0, hi = n - 1;
while (lo < hi) {
    int mid = lo + (hi - lo) / 2;
    if (a[mid] > a[hi]) lo = mid + 1;         // minimum is to the right
    else hi = mid;                            // mid may be the minimum
}
return a[lo];""",
           """lo, hi = 0, len(a) - 1
while lo < hi:
    mid = lo + (hi - lo) // 2
    if a[mid] > a[hi]:
        lo = mid + 1                          # minimum is to the right
    else:
        hi = mid                              # mid may be the minimum
return a[lo]""")],
    complexity="O(log n) time, O(1) space (O(n) worst case with duplicates).",
    traps=["With duplicates, `a[lo] == a[mid] == a[hi]` hides which half is sorted: shrink both ends (LC 81) or do `hi--` (LC 154), degrading to O(n).",
           "Use `<=` in `a[lo] <= a[mid]` (when `lo == mid`) and be careful with strict vs non-strict range checks."],
    variants=["Find the rotation count: index of the minimum.", "Search in a rotated array with duplicates."],
    notuse="The array is not a rotation of a sorted array.",
    problems=[
        (153, "Find Minimum in Rotated Sorted Array", "M", "find-minimum-in-rotated-sorted-array", "Compare mid with hi: bigger → minimum is on the right", "O(log n) / O(1)"),
        (33, "Search in Rotated Sorted Array", "M", "search-in-rotated-sorted-array", "Identify the sorted half, test whether target is inside", "O(log n) / O(1)"),
        (81, "Search in Rotated Sorted Array II", "M", "search-in-rotated-sorted-array-ii", "If a[lo] == a[mid] == a[hi], shrink both ends", "O(log n) avg, O(n) worst / O(1)"),
        (154, "Find Minimum in Rotated Sorted Array II", "H", "find-minimum-in-rotated-sorted-array-ii", "If a[mid] == a[hi], hi--", "O(log n) avg, O(n) worst / O(1)"),
    ]))

# ---------------------------------------------------------------- 10
P.append(dict(
    title="Quick Select and Merge Sort", tier="sec", sim="quick", oneline="partition for kth, merge for counting",
    why="Appears as \"kth element\" and \"count inversions\" questions", signature="LC 215",
    when="Kth smallest/largest without a full sort, counting inversions, or a guaranteed O(n log n) stable sort.",
    detect="\"kth largest/smallest\" · \"count smaller elements after self\" · \"count reverse pairs\" · \"sort with an O(n log n) guarantee\".",
    intuition="Quick select: to find the 3rd tallest person, split the crowd around one person. If exactly two people are taller, you are done; otherwise only one side can contain your answer, so ignore the other. Merge sort: while merging two sorted halves you see, for free, how many elements jumped past each other: that is the inversion count.",
    brute="Sorting everything is O(n log n). Quick select discards one side each time: expected n + n/2 + n/4 + … = O(n).",
    idea="Quick select partitions around a pivot and recurses into the single side containing the target index. Merge sort divides, sorts halves, and merges; counting happens during the merge.",
    steps=["Partition so the pivot lands at its final sorted index `p`.", "`p == target` → done. `p < target` → search the right side. `p > target` → search the left.", "kth largest = index `n − k` in ascending order."],
    trace_title="2nd largest in `[3,2,1,5,6,4]` (target index 4)",
    trace="""pivot 4: [3,2,1,4,6,5]  p=3 < 4 -> search right [6,5]
pivot 5: [5,6]          p=4 == 4 -> answer 5""",
    code=[("quick select (Lomuto partition)",
           """int target = n - k, lo = 0, hi = n - 1;
while (lo <= hi) {
    int p = partition(a, lo, hi);
    if (p == target) return a[p];
    if (p < target) lo = p + 1; else hi = p - 1;
}
return -1;

int partition(int[] a, int lo, int hi) {
    int pivot = a[hi], i = lo;
    for (int j = lo; j < hi; j++)
        if (a[j] < pivot) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; }
    int t = a[i]; a[i] = a[hi]; a[hi] = t;
    return i;
}""",
           """import random
def kth_largest(a, k):
    target, lo, hi = len(a) - k, 0, len(a) - 1
    while lo <= hi:
        r = random.randint(lo, hi)            # random pivot avoids worst case
        a[r], a[hi] = a[hi], a[r]
        pivot, i = a[hi], lo
        for j in range(lo, hi):
            if a[j] < pivot:
                a[i], a[j] = a[j], a[i]
                i += 1
        a[i], a[hi] = a[hi], a[i]
        if i == target:
            return a[i]
        if i < target:
            lo = i + 1
        else:
            hi = i - 1"""),
          ("merge sort with inversion count",
           """long mergeCount(int[] a, int[] tmp, int lo, int hi) {
    if (hi - lo < 1) return 0;
    int mid = (lo + hi) >>> 1;
    long inv = mergeCount(a, tmp, lo, mid) + mergeCount(a, tmp, mid + 1, hi);
    int i = lo, j = mid + 1, k = lo;
    while (i <= mid && j <= hi) {
        if (a[i] <= a[j]) tmp[k++] = a[i++];
        else { tmp[k++] = a[j++]; inv += mid - i + 1; }   // all of a[i..mid] > a[j]
    }
    while (i <= mid) tmp[k++] = a[i++];
    while (j <= hi) tmp[k++] = a[j++];
    System.arraycopy(tmp, lo, a, lo, hi - lo + 1);
    return inv;
}""",
           """def merge_count(a):
    if len(a) <= 1:
        return a, 0
    mid = len(a) // 2
    left, x = merge_count(a[:mid])
    right, y = merge_count(a[mid:])
    out, inv, i, j = [], x + y, 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
            inv += len(left) - i                  # all remaining left > right[j]
    out += left[i:] + right[j:]
    return out, inv""")],
    complexity="Quick select average O(n), worst O(n²) (fix with a random pivot), O(1) space. Merge sort O(n log n) time, O(n) space, stable.",
    traps=["Quick select on already-sorted input with a fixed pivot degrades to O(n²): randomise the pivot.", "Merge sort is not in place (needs an auxiliary array).",
           "Count inversions **during** the merge; use `long` for the count.", "For streaming top-K or when k is small, a heap of size k (O(n log k)) is simpler."],
    variants=["Top-K without ordering: quick select, then take the left or right side.", "Count of smaller numbers after self / reverse pairs: merge sort on indices with a modified count step, or a Fenwick tree."],
    notuse="When a heap is simpler (streaming input), or when you need a stable sort (use merge sort, not quick select).",
    problems=[
        (215, "Kth Largest Element in an Array", "M", "kth-largest-element-in-an-array", "Quick select for index n − k (or a size-k min-heap)", "O(n) avg / O(1)"),
        (973, "K Closest Points to Origin", "M", "k-closest-points-to-origin", "Quick select on squared distance (or a size-k max-heap)", "O(n) avg / O(1)"),
        (912, "Sort an Array", "M", "sort-an-array", "Merge sort (guaranteed O(n log n)); avoid quick sort worst case", "O(n log n) / O(n)"),
        (493, "Reverse Pairs", "H", "reverse-pairs", "Count a[i] > 2·a[j] across the halves before merging", "O(n log n) / O(n)"),
        (315, "Count of Smaller Numbers After Self", "H", "count-of-smaller-numbers-after-self", "Merge sort on indices, or a Fenwick tree over ranks", "O(n log n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 11
P.append(dict(
    title="Other must-know array tricks", tier="sec", sim=None, oneline="small specialised tools: voting, cyclic sort, difference array, matrix moves",
    why="Short specialised ideas that keep appearing", signature="LC 169 / 41",
    when="The problem needs an in-place O(1)-space trick that none of the patterns above cover.",
    detect="\"majority element\" · \"missing / duplicate number in 1..n\" · \"rotate in place\" · \"add a value to a range many times\" · matrix spiral/rotate/zero.",
    intuition="These are small, single-purpose tools. Learn the one-sentence idea of each and you can rebuild the code on demand.",
    brute=None,
    idea="Boyer–Moore voting cancels pairs of different elements so the majority survives. Cyclic sort puts value `x` at index `x−1`. A difference array records range updates as `+v` at the start and `−v` just past the end, then a prefix sum reveals the result. Rotation by `k` is three reversals.",
    steps=["**Voting:** keep `candidate` and `count`; same → `count++`, different → `count--`, at 0 pick a new candidate.", "**Cyclic sort:** while `a[i]` is in `1..n` and not at its home, swap it home; the first index where `a[i] != i+1` is the missing number.",
           "**Difference array:** `diff[l] += v`, `diff[r+1] -= v`, prefix-sum at the end.", "**Rotate by k:** reverse all, reverse the first `k`, reverse the rest.", "**Matrix:** rotate = transpose then reverse each row; zeroes = use the first row and column as markers."],
    trace_title="Boyer–Moore on `[2,2,1,1,2]`",
    trace="""2: cand 2 count 1
2: cand 2 count 2
1: cand 2 count 1
1: cand 2 count 0
2: cand 2 count 1  -> majority 2""",
    code=[("Boyer–Moore majority vote",
           """int cand = 0, count = 0;
for (int x : a) {
    if (count == 0) cand = x;
    count += (x == cand) ? 1 : -1;
}
return cand;   // verify with a second pass if a majority is not guaranteed""",
           """cand, count = None, 0
for x in a:
    if count == 0:
        cand = x
    count += 1 if x == cand else -1
return cand    # verify with a second pass if a majority is not guaranteed"""),
          ("cyclic sort (first missing positive)",
           """for (int i = 0; i < n; i++) {
    while (a[i] > 0 && a[i] <= n && a[a[i] - 1] != a[i]) {
        int j = a[i] - 1, t = a[i]; a[i] = a[j]; a[j] = t;
    }
}
for (int i = 0; i < n; i++) if (a[i] != i + 1) return i + 1;
return n + 1;""",
           """n = len(a)
for i in range(n):
    while 0 < a[i] <= n and a[a[i] - 1] != a[i]:
        j = a[i] - 1
        a[i], a[j] = a[j], a[i]
for i in range(n):
    if a[i] != i + 1:
        return i + 1
return n + 1""")],
    complexity="Each trick is O(n) time and O(1) extra space (difference array uses O(n)).",
    traps=["Voting only guarantees the right answer when a majority exists; otherwise verify.", "Cyclic sort loop must be a `while`, and guard duplicates with `a[a[i]-1] != a[i]` to avoid infinite swaps.", "Rotate: use `k % n` first."],
    variants=["Majority element II (more than n/3): two candidates.", "Find the duplicate: cyclic sort, or Floyd's cycle detection on the index graph."],
    notuse="When a general pattern (hashing, two pointers) already solves it cleanly and space is not a concern.",
    problems=[
        (169, "Majority Element", "E", "majority-element", "Boyer–Moore voting", "O(n) / O(1)"),
        (189, "Rotate Array", "M", "rotate-array", "Reverse all, reverse first k, reverse the rest", "O(n) / O(1)"),
        (48, "Rotate Image", "M", "rotate-image", "Transpose, then reverse each row", "O(n²) / O(1)"),
        (54, "Spiral Matrix", "M", "spiral-matrix", "Four shrinking boundaries", "O(mn) / O(1)"),
        (73, "Set Matrix Zeroes", "M", "set-matrix-zeroes", "First row and column as markers", "O(mn) / O(1)"),
        (31, "Next Permutation", "M", "next-permutation", "Find pivot from the right, swap with next larger, reverse the suffix", "O(n) / O(1)"),
        (229, "Majority Element II", "M", "majority-element-ii", "Two voting candidates, then verify", "O(n) / O(1)"),
        (1109, "Corporate Flight Bookings", "M", "corporate-flight-bookings", "Difference array, then prefix sum", "O(n + m) / O(n)"),
        (287, "Find the Duplicate Number", "M", "find-the-duplicate-number", "Floyd's cycle detection on index → value", "O(n) / O(1)"),
        (41, "First Missing Positive", "H", "first-missing-positive", "Cyclic sort: put x at index x − 1", "O(n) / O(1)"),
    ]))

TOPIC = dict(
    id="arrays", file="02_arrays.html", title="Arrays, Hashing and Searching — Pattern Guide",
    lead="One consolidated guide to the array family: two pointers, sliding window, prefix sums, Kadane, hashing, partitioning, binary search and selection. Every pattern has the intuition, an animation you can step through, code in Java and Python, complexity, traps and a ladder of LeetCode problems.",
    mindset="Most array problems are about **avoiding the O(n²) brute force** by exploiting structure: sortedness, a running aggregate, a hash of what you have seen, or a window you grow and shrink. The workhorses are **two pointers**, **sliding window**, **prefix sum** and **hashing**. Binary search adds O(log n) lookups when the data (or the answer space) is monotonic.",
    questions=["**Is it (or can it be) sorted?** → two pointers or binary search become available.", "**Do I need information about a contiguous range?** → sliding window or prefix sum.",
               "**Do I need \"have I seen this / how many times\"?** → hashing.", "**Can I check a guessed answer quickly?** → binary search on the answer."],
    cues=[
        ["sorted array, \"pair or triplet with target sum\"", "**P1** Two Pointers"],
        ["\"in place\", remove duplicates / move zeroes", "**P1** Two Pointers (slow/fast)"],
        ["\"subarray/substring of size exactly k\"", "**P2** Sliding Window (fixed)"],
        ["\"longest/shortest substring with property\", \"at most K distinct\"", "**P3** Sliding Window (variable)"],
        ["\"many range-sum queries\", \"number of subarrays with sum k\", negatives present", "**P4** Prefix Sum (+ map)"],
        ["\"maximum subarray sum/product\" (contiguous)", "**P5** Kadane"],
        ["\"have I seen this\", \"count occurrences\", \"group by\"", "**P6** Hashing"],
        ["\"sort 0s, 1s, 2s in place\", 3-way partition", "**P7** Dutch National Flag"],
        ["sorted data, O(log n), \"first/last occurrence\"", "**P8** Binary Search"],
        ["\"minimise the max\" / \"maximise the min\", feasibility check", "**P8** Binary Search on the answer"],
        ["\"sorted array rotated at an unknown pivot\"", "**P9** Rotated-array search"],
        ["\"kth largest/smallest\", \"count inversions\"", "**P10** Quick Select / Merge Sort"],
        ["\"majority element\", \"missing number 1..n\", \"rotate in place\"", "**P11** Specialised tricks"],
    ],
    choose=[
        ["Pair or triplet in sorted data", "Two Pointers"],
        ["Property over a contiguous range, fixed size", "Sliding Window (fixed)"],
        ["Longest/shortest range with a condition (non-negative)", "Sliding Window (variable)"],
        ["Subarray sums with negatives, or many range queries", "Prefix Sum (+ hashing)"],
        ["\"Have I seen\", grouping, frequency", "Hashing"],
        ["O(log n) lookup or \"minimise the max\"", "Binary Search"],
        ["Kth element, fast", "Quick Select (or a heap)"],
    ],
    rule="if negatives are present and you are counting subarray sums, prefer **prefix sum + hash map** over a sliding window (shrinking is not monotonic with negatives). If the array is sorted, or you can sort it, reach for **two pointers / binary search** before hashing.",
    selftest=[
        ("Why does Two Sum II with two pointers never miss the answer?", "Each move discards an element that cannot belong to any valid pair with the remaining elements, because the array is sorted. If `a[l] + a[r]` is too small, `a[l]` is too small even for the largest remaining partner."),
        ("Why must a prefix-sum counter start with `{0: 1}`?", "It represents the empty prefix. Without it, subarrays that start at index 0 (where `sum == k` already) are never counted."),
        ("Why does the variable sliding window run in O(n) even though it has a nested loop?", "`l` and `r` only ever move forward, so together they make at most 2n moves. Each element is added once and removed once."),
        ("Sliding window fails for \"subarray sum equals k\" with negative numbers. Why?", "With negatives, extending the window can decrease the sum and shrinking can increase it, so \"shrink while too big\" is no longer valid. Use prefix sums with a hash map."),
        ("In Dutch flag, why do we not advance `mid` after swapping with `hi`?", "The element swapped in from `hi` has not been examined yet; it might be 0, 1 or 2 and must be processed. Elements swapped from `lo` were already seen."),
        ("Binary search: when do you use `hi = mid` versus `hi = mid − 1`?", "`hi = mid` when `mid` itself may be the answer (boundary search with `lo < hi`). `hi = mid − 1` when `mid` has been ruled out (exact search with `lo <= hi`)."),
        ("How do you turn \"exactly K\" into something a sliding window can do?", "Count \"at most K\" minus \"at most K − 1\"."),
        ("When is quick select a bad idea?", "When input arrives as a stream, when a stable order is needed, or when a deterministic worst case matters (use a heap or median-of-medians)."),
    ],
    plan=[
        "**Days 1–2:** two pointers and fixed window. Do the first three problems of each ladder without hints.",
        "**Days 3–4:** variable window and prefix sum. These are the highest-return patterns.",
        "**Days 5–6:** hashing and Kadane; redo anything you needed a hint for.",
        "**Day 7:** binary search (basic), then binary search on the answer.",
        "**Day 8:** rotated search, Dutch flag, quick select, and the specialised tricks.",
        "**Day 9 and after:** redo every problem you ticked after a hint. Cover the code, write the skeleton from memory, then explain the intuition aloud.",
    ],
    patterns=P,
)
