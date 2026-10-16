"""Content for topic 06: Sorting and intervals."""

P = []

# ---------------------------------------------------------------- 1
P.append(dict(
    title="Comparison sorts: merge, quick and what to pick", tier="hot", sim="mergesort", oneline="divide, sort the halves, merge; n log n is the floor",
    why="You must know one O(n log n) sort cold and justify your choice", signature="LC 912 / 88",
    when="You are asked to implement a sort, to merge sorted data, or to count inversions during a sort.",
    detect="\"sort an array\" · \"merge two sorted arrays\" · \"count smaller numbers after self\" · \"reverse pairs\" · \"stable sort needed\".",
    intuition="Merge sort is how you would sort a deck of cards with a friend: split it in two, each sorts their half, then you interleave the two sorted piles by always taking the smaller top card. Interleaving two sorted piles is cheap (one pass), and halving gives only log n rounds. Quick sort instead picks a pivot and throws smaller cards left, larger right.",
    brute="Insertion or bubble sort compares nearly every pair: O(n²). Any comparison sort needs at least n log n comparisons; merge sort reaches it in every case.",
    idea="Merge sort: `sort(left)`, `sort(right)`, `merge`. The merge step is a two-pointer walk over two sorted runs. Quick sort: partition around a pivot, recurse on both sides (average O(n log n), worst O(n²) without a random pivot).",
    steps=["Base case: 0 or 1 elements are sorted.", "Split at `mid`; recursively sort both halves.", "Merge: two pointers `i`, `j`; copy the smaller (`<=` keeps it stable) into a temp array.", "Copy the temp back (or return the merged list)."],
    trace_title="algorithm cheat sheet",
    trace="""algorithm      best        average     worst       space    stable
insertion      O(n)        O(n^2)      O(n^2)      O(1)     yes   (great for tiny or nearly sorted input)
merge          O(n log n)  O(n log n)  O(n log n)  O(n)     yes   (linked lists, stable sort, counting inversions)
quick          O(n log n)  O(n log n)  O(n^2)      O(log n) no    (fastest in practice, random pivot)
heap           O(n log n)  O(n log n)  O(n log n)  O(1)     no    (in-place guarantee)
counting       O(n + k)    O(n + k)    O(n + k)    O(k)     yes   (small integer range)
Java: Arrays.sort(int[]) is dual-pivot quicksort; sort(Object[]) / Collections.sort is TimSort (stable).
Python: list.sort / sorted use TimSort (stable).""",
    code=[("merge sort",
           """void mergeSort(int[] a, int[] tmp, int lo, int hi) {
    if (lo >= hi) return;
    int mid = (lo + hi) >>> 1;
    mergeSort(a, tmp, lo, mid);
    mergeSort(a, tmp, mid + 1, hi);
    int i = lo, j = mid + 1, k = lo;
    while (i <= mid && j <= hi) tmp[k++] = (a[i] <= a[j]) ? a[i++] : a[j++];   // <= keeps it stable
    while (i <= mid) tmp[k++] = a[i++];
    while (j <= hi) tmp[k++] = a[j++];
    System.arraycopy(tmp, lo, a, lo, hi - lo + 1);
}""",
           """def merge_sort(a):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left, right = merge_sort(a[:mid]), merge_sort(a[mid:])
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:                      # <= keeps it stable
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    return out + left[i:] + right[j:]"""),
          ("quick sort with a random pivot",
           """void quickSort(int[] a, int lo, int hi) {
    if (lo >= hi) return;
    int r = lo + (int) (Math.random() * (hi - lo + 1));
    swap(a, r, hi);                                   // random pivot avoids the sorted-input worst case
    int pivot = a[hi], i = lo;
    for (int j = lo; j < hi; j++) if (a[j] < pivot) swap(a, i++, j);
    swap(a, i, hi);
    quickSort(a, lo, i - 1);
    quickSort(a, i + 1, hi);
}""",
           """import random
def quick_sort(a, lo, hi):
    if lo >= hi:
        return
    r = random.randint(lo, hi)
    a[r], a[hi] = a[hi], a[r]                         # random pivot avoids the sorted-input worst case
    pivot, i = a[hi], lo
    for j in range(lo, hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]
    quick_sort(a, lo, i - 1)
    quick_sort(a, i + 1, hi)"""),
          ("merge sorted array into the front array (fill from the back)",
           """int i = m - 1, j = n - 1, k = m + n - 1;
while (j >= 0) {
    if (i >= 0 && a[i] > b[j]) a[k--] = a[i--];
    else a[k--] = b[j--];
}""",
           """i, j, k = m - 1, n - 1, m + n - 1
while j >= 0:
    if i >= 0 and a[i] > b[j]:
        a[k] = a[i]; i -= 1
    else:
        a[k] = b[j]; j -= 1
    k -= 1""")],
    complexity="Merge sort O(n log n) time, O(n) space. Quick sort O(n log n) average, O(n²) worst, O(log n) stack.",
    traps=["Quick sort on already-sorted input with a fixed pivot is O(n²): randomise or use median-of-three.", "`(lo + hi) / 2` can overflow: use `lo + (hi − lo) / 2` or `>>> 1`.",
           "Stability matters when sorting records by one key after another; use `<=` in the merge.", "Merging in place from the **back** avoids overwriting unread elements."],
    variants=["Count inversions or reverse pairs: count cross-half pairs just before merging.", "Sort a linked list: merge sort needs no extra array.", "External sort: sort chunks that fit in memory, then k-way merge with a heap."],
    notuse="Small integer ranges (counting sort), nearly sorted data (insertion sort / TimSort), or when you only need the k-th element (quick select).",
    problems=[
        (88, "Merge Sorted Array", "E", "merge-sorted-array", "Fill from the back with three pointers", "O(m + n) / O(1)"),
        (912, "Sort an Array", "M", "sort-an-array", "Merge sort (guaranteed) or randomised quick sort", "O(n log n) / O(n)"),
        (215, "Kth Largest Element in an Array", "M", "kth-largest-element-in-an-array", "Quick select partition, expected O(n)", "O(n) avg / O(1)"),
        (315, "Count of Smaller Numbers After Self", "H", "count-of-smaller-numbers-after-self", "Merge sort on indices, count elements jumped over", "O(n log n) / O(n)"),
        (493, "Reverse Pairs", "H", "reverse-pairs", "Count a[i] > 2·a[j] across halves before merging", "O(n log n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 2
P.append(dict(
    title="Custom comparators and multi-key sorting", tier="hot", sim="largestnum", oneline="define \"comes first\" and let the sort do the rest",
    why="Many problems are just \"sort by the right rule\"", signature="LC 179 / 406",
    when="The natural order is not the order you want: concatenation order, by frequency then alphabet, by height then position.",
    detect="\"arrange to form the largest\" · \"sort by … then by …\" · \"reconstruct queue\" · \"rank teams\" · \"custom order\".",
    intuition="A comparator answers one question for any two items: **who goes first?** If that answer is consistent (a proper ordering), any sort algorithm will arrange the whole list. For \"largest number\" you cannot compare 3 and 30 numerically, but you can ask which concatenation is bigger: `\"330\"` vs `\"303\"`.",
    brute="Trying all permutations is O(n!). Finding a valid comparator reduces it to one sort: O(n log n).",
    idea="Write `compare(a, b)` returning negative if `a` should come first. It must be **transitive and consistent**. For multiple keys, compare the first key and fall back to the next on ties.",
    steps=["Decide the rule that puts `a` before `b`.", "Check it is a strict weak order (transitive, consistent for ties).", "Sort with the comparator (or a key function).", "Post-process (join, insert at index, strip zeros)."],
    trace_title="largest number from `[3, 30, 34, 5, 9]`",
    trace="""34 vs 3  : "343" > "334"  -> 34 first
3  vs 30 : "330" > "303"  -> 3 first
sorted order: 9, 5, 34, 3, 30
result: "9534330\"""",
    code=[("largest number (comparator on concatenation)",
           """String[] s = new String[n];
for (int i = 0; i < n; i++) s[i] = String.valueOf(nums[i]);
Arrays.sort(s, (x, y) -> (y + x).compareTo(x + y));          // bigger concatenation first
if (s[0].equals("0")) return "0";                              // all zeros
return String.join("", s);""",
           """from functools import cmp_to_key
s = [str(x) for x in nums]
s.sort(key=cmp_to_key(lambda x, y: -1 if x + y > y + x else (1 if x + y < y + x else 0)))
return "0" if s[0] == "0" else "".join(s)"""),
          ("queue reconstruction: sort by height desc, then k asc; insert at index k",
           """Arrays.sort(people, (a, b) -> a[0] != b[0] ? Integer.compare(b[0], a[0]) : Integer.compare(a[1], b[1]));
List<int[]> res = new ArrayList<>();
for (int[] p : people) res.add(p[1], p);                       // taller people are already placed
return res.toArray(new int[0][]);""",
           """people.sort(key=lambda p: (-p[0], p[1]))
res = []
for p in people:
    res.insert(p[1], p)                                       # taller people are already placed
return res""")],
    complexity="O(n log n) comparisons × cost of one comparison.",
    traps=["Never write `(a, b) -> a − b` for ints: it can overflow. Use `Integer.compare`.", "An inconsistent comparator makes Java throw \"Comparison method violates its general contract\".",
           "Edge case: all zeros in largest-number must return `\"0\"`, not `\"000\"`.", "Python 3 has no `cmp=`: use `key=` or `functools.cmp_to_key`."],
    variants=["Sort by frequency then value: `key=(count, value)`.", "Custom alphabet (alien dictionary): map each letter to its rank and compare rank tuples.", "Sort intervals by start, or by end for greedy (patterns 4 and 7)."],
    notuse="When a simple key (one number or string) already gives the order; do not over-engineer a comparator.",
    problems=[
        (2418, "Sort the People", "E", "sort-the-people", "Sort names by height descending", "O(n log n) / O(n)"),
        (1636, "Sort Array by Increasing Frequency", "E", "sort-array-by-increasing-frequency", "Key = (frequency, −value)", "O(n log n) / O(n)"),
        (179, "Largest Number", "M", "largest-number", "Comparator: x + y vs y + x", "O(n log n) / O(n)"),
        (937, "Reorder Data in Log Files", "M", "reorder-data-in-log-files", "Letter logs by content then id; digit logs keep order", "O(n log n) / O(n)"),
        (406, "Queue Reconstruction by Height", "M", "queue-reconstruction-by-height", "Sort tall first, insert at index k", "O(n²) / O(n)"),
        (1366, "Rank Teams by Votes", "M", "rank-teams-by-votes", "Vote counts per position as the sort key, then letter", "O(n·k + k² log k) / O(k²)"),
    ]))

# ---------------------------------------------------------------- 3
P.append(dict(
    title="Counting and bucket sort (beating n log n)", tier="hot", sim="bucket", oneline="when keys are small integers, index instead of compare",
    why="Gives O(n) answers for frequency and range-limited problems", signature="LC 347 / 75",
    when="Values or frequencies lie in a small known range, so you can use them directly as array indices.",
    detect="\"top K frequent\" · \"sort colors / ages / scores in 0..100\" · \"h-index\" · \"sort characters by frequency\" · values up to ~10⁶.",
    intuition="Sorting library books by shelf number is easier than comparing titles: just drop each book in the box labelled with its shelf, then read the boxes in order. Bucket sort uses the key as the box number. Frequencies are ideal keys: no element appears more than `n` times, so there are only `n` boxes.",
    brute="Sorting the entries by count is O(n log n). Placing each value in `bucket[frequency]` and scanning from the highest bucket down is O(n).",
    idea="Count occurrences, then place items in an array of buckets indexed by count (or by value for counting sort). Read the buckets in the order you need.",
    steps=["Count: `cnt[x]++` (hash map or array).", "Create `buckets[0..n]`; put each value `x` into `buckets[cnt[x]]`.", "Scan buckets from high to low, collecting until you have `k` items.", "Counting sort: walk values `0..max` and output each value `cnt[v]` times."],
    trace_title="top 2 frequent in `[1,1,1,2,2,3]`",
    trace="""counts: 1->3, 2->2, 3->1
buckets: [1]={3}  [2]={2}  [3]={1}
scan from high: bucket 3 -> 1, bucket 2 -> 2
=> [1, 2]""",
    code=[("top K frequent elements with buckets",
           """Map<Integer, Integer> cnt = new HashMap<>();
for (int x : nums) cnt.merge(x, 1, Integer::sum);
List<Integer>[] buckets = new List[nums.length + 1];
for (var e : cnt.entrySet()) {
    int f = e.getValue();
    if (buckets[f] == null) buckets[f] = new ArrayList<>();
    buckets[f].add(e.getKey());
}
int[] res = new int[k]; int idx = 0;
for (int f = buckets.length - 1; f >= 1 && idx < k; f--)
    if (buckets[f] != null) for (int x : buckets[f]) if (idx < k) res[idx++] = x;
return res;""",
           """from collections import Counter
cnt = Counter(nums)
buckets = [[] for _ in range(len(nums) + 1)]
for x, f in cnt.items():
    buckets[f].append(x)
res = []
for f in range(len(buckets) - 1, 0, -1):
    for x in buckets[f]:
        res.append(x)
        if len(res) == k:
            return res"""),
          ("counting sort for small integer ranges (sort colors)",
           """int[] count = new int[3];
for (int x : a) count[x]++;
int idx = 0;
for (int v = 0; v < 3; v++)
    while (count[v]-- > 0) a[idx++] = v;""",
           """count = [0] * 3
for x in a:
    count[x] += 1
i = 0
for v in range(3):
    for _ in range(count[v]):
        a[i] = v
        i += 1""")],
    complexity="O(n + k) time, O(n + k) space for range size k.",
    traps=["Only valid when keys are small, non-negative integers (or can be shifted into that range).", "Counting sort is stable only if you place elements from the back using prefix sums.",
           "Top K with ties: decide whether to return all tied items or exactly k.", "A heap of size k is O(n log k) and handles streaming input; buckets need all data first."],
    variants=["H-index: `buckets[min(citations, n)]`, then scan from high to low.", "Radix sort: counting sort digit by digit, O(d·(n + b)).", "Maximum gap: bucket by value range; the answer lies between buckets."],
    notuse="Large or unbounded key ranges (use comparison sort) or streaming data where the full count is unknown.",
    problems=[
        (75, "Sort Colors", "M", "sort-colors", "Counting sort with 3 counters (or one-pass Dutch flag)", "O(n) / O(1)"),
        (347, "Top K Frequent Elements", "M", "top-k-frequent-elements", "Count, bucket by frequency, scan from the top", "O(n) / O(n)"),
        (451, "Sort Characters By Frequency", "M", "sort-characters-by-frequency", "Count letters, bucket by frequency, build output", "O(n) / O(n)"),
        (274, "H-Index", "M", "h-index", "Bucket citations capped at n, scan from the top", "O(n) / O(n)"),
        (692, "Top K Frequent Words", "M", "top-k-frequent-words", "Counts with a (−count, word) key or a heap", "O(n log k) / O(n)"),
    ]))

# ---------------------------------------------------------------- 4
P.append(dict(
    title="Merging intervals", tier="hot", sim="mergeiv", oneline="sort by start, extend the last interval or start a new one",
    why="The template behind most interval questions", signature="LC 56 / 986",
    when="Combine overlapping ranges, find union length, or intersect two interval lists.",
    detect="\"merge intervals\" · \"overlapping\" · \"union of ranges\" · \"summary ranges\" · \"interval list intersections\".",
    intuition="Imagine laying coloured strips on a ruler. Once the strips are sorted by their left end, the only strip a new one can overlap is the latest strip you placed (everything earlier ends before it). So you either stretch that last strip or put a new strip down.",
    brute="Compare every pair of intervals and union overlaps repeatedly: O(n²) or worse. Sorting by start turns it into one linear scan after an O(n log n) sort.",
    idea="Sort by start. Keep a result list. For each interval: if it starts after the last merged interval ends → append; otherwise extend the last interval's end to `max(end, cur.end)`.",
    steps=["Sort intervals by start.", "Put the first interval in `merged`.", "For each next interval: `if start > last.end` append it, else `last.end = max(last.end, end)`.", "Return `merged`."],
    trace_title="`[[8,10],[1,3],[15,18],[2,6]]`",
    trace="""sort by start: [1,3] [2,6] [8,10] [15,18]
[1,3]   start new       merged [1,3]
[2,6]   2 <= 3 overlap  merged [1,6]
[8,10]  8 >  6 gap      merged [1,6] [8,10]
[15,18] 15 > 10 gap     merged [1,6] [8,10] [15,18]""",
    code=[("merge intervals",
           """Arrays.sort(iv, (a, b) -> Integer.compare(a[0], b[0]));
List<int[]> out = new ArrayList<>();
for (int[] cur : iv) {
    if (out.isEmpty() || out.get(out.size() - 1)[1] < cur[0]) out.add(cur);          // gap: new interval
    else out.get(out.size() - 1)[1] = Math.max(out.get(out.size() - 1)[1], cur[1]);  // overlap: extend
}
return out.toArray(new int[0][]);""",
           """iv.sort()
out = []
for s, e in iv:
    if out and out[-1][1] >= s:                      # overlap (touching counts): extend
        out[-1][1] = max(out[-1][1], e)
    else:
        out.append([s, e])                           # gap: new interval
return out"""),
          ("intersection of two sorted interval lists (two pointers)",
           """List<int[]> res = new ArrayList<>();
int i = 0, j = 0;
while (i < A.length && j < B.length) {
    int lo = Math.max(A[i][0], B[j][0]), hi = Math.min(A[i][1], B[j][1]);
    if (lo <= hi) res.add(new int[]{lo, hi});                      // overlap exists
    if (A[i][1] < B[j][1]) i++; else j++;                          // drop the one that ends first
}""",
           """res, i, j = [], 0, 0
while i < len(A) and j < len(B):
    lo, hi = max(A[i][0], B[j][0]), min(A[i][1], B[j][1])
    if lo <= hi:
        res.append([lo, hi])                                      # overlap exists
    if A[i][1] < B[j][1]:
        i += 1                                                    # drop the one that ends first
    else:
        j += 1"""),
          ("remove covered intervals (sort start asc, end desc)",
           """Arrays.sort(iv, (a, b) -> a[0] == b[0] ? Integer.compare(b[1], a[1]) : Integer.compare(a[0], b[0]));
int count = 0, maxEnd = 0;
for (int[] in : iv) if (in[1] > maxEnd) { count++; maxEnd = in[1]; }      // not covered by an earlier one
return count;""",
           """iv.sort(key=lambda p: (p[0], -p[1]))
count = max_end = 0
for s, e in iv:
    if e > max_end:                                  # not covered by an earlier interval
        count += 1
        max_end = e
return count""")],
    complexity="O(n log n) time (sorting), O(n) space for the output.",
    traps=["Decide whether touching intervals (`[1,4]`, `[4,5]`) merge: usually yes (`<=`).", "Extend with `max(last.end, end)`: a later interval can be fully inside the last one.",
           "In Java, mutate a copy or the sorted array's inner arrays carefully; they are shared objects.", "Do not forget to sort, or the single-pass logic is wrong."],
    variants=["Summary ranges on a sorted array: group consecutive numbers.", "Count ways to group overlapping ranges: number of merged groups g → `2^g`.", "Employee free time: merge all schedules, take the gaps."],
    notuse="Intervals that arrive online with queries in between (use a balanced tree / `TreeMap`).",
    problems=[
        (228, "Summary Ranges", "E", "summary-ranges", "Scan, extend a run while consecutive", "O(n) / O(1)"),
        (56, "Merge Intervals", "M", "merge-intervals", "Sort by start, extend or append", "O(n log n) / O(n)"),
        (1288, "Remove Covered Intervals", "M", "remove-covered-intervals", "Sort start asc, end desc; count increasing ends", "O(n log n) / O(1)"),
        (986, "Interval List Intersections", "M", "interval-list-intersections", "Two pointers; advance the interval that ends first", "O(m + n) / O(1)"),
        (2580, "Count Ways to Group Overlapping Ranges", "M", "count-ways-to-group-overlapping-ranges", "Merge, count groups g, answer 2^g mod 1e9+7", "O(n log n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 5
P.append(dict(
    title="Insert into a sorted interval list; calendar booking", tier="hot", sim="insertiv", oneline="copy before, merge the overlap, copy after",
    why="Tests clean three-phase scanning and ordered-set thinking", signature="LC 57 / 729",
    when="Intervals are already sorted and disjoint, and you add one (or many, online) while keeping the invariant.",
    detect="\"insert interval\" · \"my calendar\" · \"data stream as disjoint intervals\" · \"range module\".",
    intuition="A shelf of sorted, non-touching books and a new book to insert. Slide past every book that ends before the new one starts. Then, while books overlap the new one, absorb them (stretch the new book to cover them). Finally put the new book down and copy the remaining books.",
    brute="Append the new interval and re-run merge intervals: O(n log n). Because the list is already sorted, one linear pass in three phases is O(n).",
    idea="Three loops over the same index: (1) `iv[i].end < new.start` → copy; (2) `iv[i].start <= new.end` → merge into `new`; (3) copy the rest. For online insertion keep a `TreeMap` keyed by start and use `floorKey` / `ceilingKey` for neighbours.",
    steps=["Copy all intervals that end before `new.start`.", "While `iv[i].start <= new.end`: `new.start = min`, `new.end = max`; `i++`.", "Add `new`.", "Copy the rest."],
    trace_title="insert `[4,8]` into `[1,2] [3,5] [6,7] [8,10] [12,16]`",
    trace="""[1,2]   ends 2 < 4        copy
[3,5]   3 <= 8  overlap   new = [3,8]
[6,7]   6 <= 8  overlap   new = [3,8]
[8,10]  8 <= 8  overlap   new = [3,10]
[12,16] 12 > 10 after     copy
=> [1,2] [3,10] [12,16]""",
    code=[("insert interval",
           """List<int[]> res = new ArrayList<>();
int i = 0, n = iv.length;
while (i < n && iv[i][1] < ni[0]) res.add(iv[i++]);               // before
while (i < n && iv[i][0] <= ni[1]) {                              // overlapping: absorb
    ni[0] = Math.min(ni[0], iv[i][0]);
    ni[1] = Math.max(ni[1], iv[i][1]);
    i++;
}
res.add(ni);
while (i < n) res.add(iv[i++]);                                   // after
return res.toArray(new int[0][]);""",
           """res, i, n = [], 0, len(iv)
while i < n and iv[i][1] < ni[0]:                                 # before
    res.append(iv[i]); i += 1
while i < n and iv[i][0] <= ni[1]:                                # overlapping: absorb
    ni = [min(ni[0], iv[i][0]), max(ni[1], iv[i][1])]
    i += 1
res.append(ni)
res.extend(iv[i:])                                                # after
return res"""),
          ("My Calendar I: reject overlapping bookings",
           """class MyCalendar {
    TreeMap<Integer, Integer> m = new TreeMap<>();                // start -> end
    boolean book(int s, int e) {
        Integer prev = m.floorKey(s), next = m.ceilingKey(s);
        if (prev != null && m.get(prev) > s) return false;         // previous booking runs into us
        if (next != null && next < e) return false;                // we run into the next booking
        m.put(s, e);
        return true;
    }
}""",
           """import bisect
class MyCalendar:
    def __init__(self):
        self.s = []                                               # sorted (start, end)
    def book(self, start, end):
        i = bisect.bisect_left(self.s, (start, end))
        if i > 0 and self.s[i - 1][1] > start:
            return False                                          # previous booking runs into us
        if i < len(self.s) and self.s[i][0] < end:
            return False                                          # we run into the next booking
        self.s.insert(i, (start, end))
        return True""")],
    complexity="Insert interval: O(n) time, O(n) output. Calendar with a TreeMap: O(log n) per booking.",
    traps=["Overlap test for half-open intervals `[s, e)`: `a.s < b.e && b.s < a.e`; for closed intervals use `<=`.", "The first loop uses `end < new.start` (strict) so touching intervals are merged in the second loop.",
           "Do not mutate the caller's `new` interval if the problem forbids it.", "Python's `list.insert` is O(n); use `sortedcontainers` or a tree for large online inputs."],
    variants=["Data stream as disjoint intervals: `TreeMap` of start → end, merge with neighbours on insert.", "Range module: add, remove and query ranges with a `TreeMap`.", "My Calendar II / III: count overlaps with a difference map (pattern 6)."],
    notuse="When the input is not sorted (merge-sort first) or you only need the number of overlaps (sweep line).",
    problems=[
        (57, "Insert Interval", "M", "insert-interval", "Three phases: before, absorb overlaps, after", "O(n) / O(n)"),
        (729, "My Calendar I", "M", "my-calendar-i", "Check the floor and ceiling neighbours in an ordered map", "O(log n) per op / O(n)"),
        (986, "Interval List Intersections", "M", "interval-list-intersections", "Two pointers over two sorted lists", "O(m + n) / O(1)"),
        (352, "Data Stream as Disjoint Intervals", "H", "data-stream-as-disjoint-intervals", "TreeMap of disjoint intervals; merge neighbours on insert", "O(log n) per op / O(n)"),
        (715, "Range Module", "H", "range-module", "Ordered map add / remove / query over ranges", "O(log n) amortised / O(n)"),
    ]))

# ---------------------------------------------------------------- 6
P.append(dict(
    title="Sweep line: counting overlaps over time", tier="hot", sim="sweep", oneline="turn intervals into +1 / −1 events and scan in time order",
    why="The standard way to answer \"how many at once?\"", signature="LC 253 / 1094 / 218",
    when="You need the maximum number of simultaneous intervals, or a total over time (rooms, platforms, capacity).",
    detect="\"minimum meeting rooms\" · \"car pooling\" · \"maximum concurrent\" · \"skyline\" · \"my calendar III\" · \"minimum platforms\".",
    intuition="Stand at the door and count: every time someone walks in add one, every time someone walks out subtract one. If you list all the entrances and exits in time order, the running count tells you how many are inside at every moment, and the biggest value is the number of rooms you need.",
    brute="Check the overlap count at every possible time: O(n × range). Sorting the 2n events and sweeping once is O(n log n).",
    idea="Convert each `[start, end)` to events `(start, +1)` and `(end, −1)`. Sort by time, with **ends before starts at equal times** (the room is free the moment the old meeting ends). Sweep keeping a running sum and its maximum. Alternative: sort starts and ends separately and use two pointers; or use a min-heap of end times.",
    steps=["Create events `(time, +1/−1)`.", "Sort by time; at ties put `−1` first.", "Sweep: `active += delta`; `peak = max(peak, active)`.", "Return `peak` (rooms) or check `active ≤ capacity` at every step."],
    trace_title="meetings `[0,30] [5,10] [15,20]`",
    trace="""events sorted: 0+  5+  10-  15+  20-  30-
active:        1   2   1    2    1    0
peak = 2 rooms""",
    code=[("minimum meeting rooms (sorted starts and ends)",
           """int n = iv.length;
int[] s = new int[n], e = new int[n];
for (int i = 0; i < n; i++) { s[i] = iv[i][0]; e[i] = iv[i][1]; }
Arrays.sort(s); Arrays.sort(e);
int rooms = 0, j = 0;
for (int i = 0; i < n; i++) {
    if (s[i] < e[j]) rooms++;        // starts before the earliest end: need another room
    else j++;                        // reuse that room
}
return rooms;""",
           """s = sorted(a for a, b in iv)
e = sorted(b for a, b in iv)
rooms = j = 0
for i in range(len(iv)):
    if s[i] < e[j]:
        rooms += 1                   # starts before the earliest end: need another room
    else:
        j += 1                       # reuse that room
return rooms"""),
          ("car pooling (difference array over positions)",
           """int[] diff = new int[1001];
for (int[] t : trips) { diff[t[1]] += t[0]; diff[t[2]] -= t[0]; }      // [from, to) passengers
int cur = 0;
for (int d : diff) { cur += d; if (cur > capacity) return false; }
return true;""",
           """diff = [0] * 1001
for p, a, b in trips:
    diff[a] += p
    diff[b] -= p                                                       # [from, to) passengers
cur = 0
for d in diff:
    cur += d
    if cur > capacity:
        return False
return True"""),
          ("min-heap of end times (also works when you must assign rooms)",
           """Arrays.sort(iv, (a, b) -> Integer.compare(a[0], b[0]));
PriorityQueue<Integer> ends = new PriorityQueue<>();
for (int[] m : iv) {
    if (!ends.isEmpty() && ends.peek() <= m[0]) ends.poll();        // a room freed up
    ends.add(m[1]);
}
return ends.size();""",
           """import heapq
iv.sort()
ends = []
for s, e in iv:
    if ends and ends[0] <= s:
        heapq.heappop(ends)                                          # a room freed up
    heapq.heappush(ends, e)
return len(ends)""")],
    complexity="O(n log n) time (sorting), O(n) space; the difference-array version is O(n + range).",
    traps=["Tie-breaking: with `[s, e)` meetings, process ends before starts at the same time.", "Sorting starts and ends separately loses the pairing, which is fine for counting but not for assigning which room.",
           "Difference arrays need a bounded coordinate range; otherwise compress coordinates or use a `TreeMap`.", "Skyline needs a max-heap of active heights plus event ordering by x, then height."],
    variants=["My Calendar III: `TreeMap<time, delta>`; after each booking sweep for the max.", "Skyline: heap of active buildings.", "Minimum platforms for trains: identical to meeting rooms."],
    notuse="When you only need a yes/no on overlap (sort by start and compare neighbours) or when positions are huge and sparse with no ordered structure available.",
    problems=[
        (729, "My Calendar I", "M", "my-calendar-i", "Reject a booking that overlaps either neighbour", "O(log n) per op / O(n)"),
        (1094, "Car Pooling", "M", "car-pooling", "Difference array, running passenger count vs capacity", "O(n + range) / O(range)"),
        (2406, "Divide Intervals Into Minimum Number of Groups", "M", "divide-intervals-into-minimum-number-of-groups", "Maximum overlap = number of groups", "O(n log n) / O(n)"),
        (732, "My Calendar III", "H", "my-calendar-iii", "TreeMap of deltas; sweep to find the max overlap", "O(n) per op / O(n)"),
        (218, "The Skyline Problem", "H", "the-skyline-problem", "Sweep x; max-heap of active building heights", "O(n log n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 7
P.append(dict(
    title="Greedy interval scheduling", tier="hot", sim="greedyiv", oneline="sort by end time and always take the one that finishes first",
    why="A clean greedy proof (exchange argument) that appears in many forms", signature="LC 435 / 452",
    when="Select the maximum number of non-overlapping intervals, or the minimum removals or points needed to cover/pierce all.",
    detect="\"non-overlapping intervals\" · \"minimum arrows to burst balloons\" · \"maximum events attended\" · \"longest chain of pairs\" · \"partition labels\".",
    intuition="You are choosing which meetings to attend in one room. The meeting that **ends earliest** leaves the most time for everything after it, so taking it can never be worse than taking a longer one that starts at the same place. Repeat on what remains. That is the exchange argument: swap any optimal solution's first meeting for the earliest-ending one and nothing gets worse.",
    brute="Try every subset of intervals: O(2ⁿ). A DP over sorted intervals is O(n²) or O(n log n). The greedy gets O(n log n) with a single scan.",
    idea="Sort by **end**. Keep `lastEnd`. For each interval: if `start >= lastEnd` keep it and update `lastEnd`; otherwise it overlaps, so count it as removed (or skip). Balloons: one arrow bursts everything sharing a point, so count a new arrow when `start > lastEnd`.",
    steps=["Sort by end (ascending).", "`lastEnd = −∞`, `kept = 0`.", "For each interval: if `start >= lastEnd` → keep, `lastEnd = end`.", "Removed = `n − kept`."],
    trace_title="`[1,2] [2,3] [3,4] [1,3]`",
    trace="""sort by end: [1,2] [2,3] [1,3] [3,4]
keep [1,2]  lastEnd 2
keep [2,3]  2 >= 2          lastEnd 3
skip [1,3]  1 <  3 overlap  removed 1
keep [3,4]  3 >= 3          lastEnd 4
=> remove 1""",
    code=[("non-overlapping intervals (minimum removals)",
           """Arrays.sort(iv, (a, b) -> Integer.compare(a[1], b[1]));         // by END
int removed = 0, end = Integer.MIN_VALUE;
for (int[] cur : iv) {
    if (cur[0] >= end) end = cur[1];                                // keep
    else removed++;                                                 // overlaps: drop it
}
return removed;""",
           """iv.sort(key=lambda p: p[1])                                         # by END
removed, end = 0, float('-inf')
for s, e in iv:
    if s >= end:
        end = e                                                     # keep
    else:
        removed += 1                                                # overlaps: drop it
return removed"""),
          ("minimum arrows to burst balloons",
           """Arrays.sort(pts, (a, b) -> Integer.compare(a[1], b[1]));
int arrows = 0; long end = Long.MIN_VALUE;
for (int[] p : pts) {
    if (p[0] > end) { arrows++; end = p[1]; }                       // need a new arrow
}
return arrows;""",
           """pts.sort(key=lambda p: p[1])
arrows, end = 0, float('-inf')
for s, e in pts:
    if s > end:
        arrows += 1                                                 # need a new arrow
        end = e
return arrows""")],
    complexity="O(n log n) time for the sort, O(1) extra space.",
    traps=["Sort by **end**, not start, for selection problems (sorting by start fails on `[1,10] [2,3] [4,5]`).", "Touching intervals `[1,2] [2,3]` do **not** overlap for scheduling (`start >= lastEnd`), but balloons with shared endpoints can share an arrow (`start > end` for a new arrow).",
           "Use `Long` or `Integer.compare` to avoid overflow with extreme coordinates.", "Maximum events attended (one per day) needs a min-heap of end days, not this simple scan."],
    variants=["Maximum length of pair chain: same greedy by end.", "Partition labels: last occurrence of each letter, extend the current part's end.", "Weighted job scheduling: DP + binary search (greedy fails with weights)."],
    notuse="Weighted intervals (use DP), or when you must pick exactly k intervals with other constraints.",
    problems=[
        (646, "Maximum Length of Pair Chain", "M", "maximum-length-of-pair-chain", "Sort by end, greedily extend the chain", "O(n log n) / O(1)"),
        (452, "Minimum Number of Arrows to Burst Balloons", "M", "minimum-number-of-arrows-to-burst-balloons", "Sort by end; new arrow when start > last arrow", "O(n log n) / O(1)"),
        (435, "Non-overlapping Intervals", "M", "non-overlapping-intervals", "Sort by end; count overlaps removed", "O(n log n) / O(1)"),
        (763, "Partition Labels", "M", "partition-labels", "Extend the part to the last index of every letter seen", "O(n) / O(1)"),
        (1353, "Maximum Number of Events That Can Be Attended", "M", "maximum-number-of-events-that-can-be-attended", "Day by day with a min-heap of end days", "O(n log n) / O(n)"),
        (1235, "Maximum Profit in Job Scheduling", "H", "maximum-profit-in-job-scheduling", "Weights break greedy: DP + binary search on end times", "O(n log n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 8
P.append(dict(
    title="Sort first, then two pointers or neighbours", tier="hot", sim="boats", oneline="sorting makes extremes and neighbours meaningful",
    why="A cheap O(n log n) preprocessing step that simplifies many problems", signature="LC 881 / 455",
    when="Pairing smallest with largest, matching two lists, or the answer depends on adjacent elements in sorted order.",
    detect="\"boats to save people\" · \"assign cookies\" · \"minimum difference\" · \"largest perimeter triangle\" · \"two city scheduling\" · \"array partition\".",
    intuition="Once data is sorted, the extremes sit at the ends and the closest values sit side by side. To fit people into 2-seat boats, the heaviest person is the hardest to place, so give them the lightest partner that fits; if even the lightest does not fit, they travel alone. Sorting turns \"who goes with whom\" into walking two pointers inward.",
    brute="Trying every pairing is O(n²) or worse. After sorting, one linear two-pointer pass decides everything.",
    idea="Sort, then either use `l` and `r` at the ends (pair extremes), or scan adjacent elements (minimum difference, duplicates, triangle sides), or use a greedy that processes in sorted order.",
    steps=["Sort the array (or both arrays).", "Choose the pass: opposite ends, adjacent pairs, or matching two sorted lists.", "Apply the greedy rule at each step and move pointers.", "Count or accumulate the answer."],
    trace_title="boats: weights `[1,2,2,3]`, limit 3",
    trace="""l=0(1) r=3(3): 4 > 3  -> 3 goes alone       boats 1
l=0(1) r=2(2): 3 <= 3 -> 1 and 2 share       boats 2
l=1(2) r=1(2): last person alone              boats 3
=> 3 boats""",
    code=[("boats to save people (max 2 per boat)",
           """Arrays.sort(p);
int l = 0, r = p.length - 1, boats = 0;
while (l <= r) {
    if (p[l] + p[r] <= limit) l++;       // lightest shares with the heaviest
    r--;                                 // heaviest always leaves
    boats++;
}
return boats;""",
           """p.sort()
l, r, boats = 0, len(p) - 1, 0
while l <= r:
    if p[l] + p[r] <= limit:
        l += 1                           # lightest shares with the heaviest
    r -= 1                               # heaviest always leaves
    boats += 1
return boats"""),
          ("assign cookies (match two sorted lists)",
           """Arrays.sort(g); Arrays.sort(s);
int child = 0;
for (int cookie : s)
    if (child < g.length && g[child] <= cookie) child++;     // smallest unsatisfied child first
return child;""",
           """g.sort(); s.sort()
child = 0
for cookie in s:
    if child < len(g) and g[child] <= cookie:
        child += 1                                           # smallest unsatisfied child first
return child""")],
    complexity="O(n log n) for the sort, O(n) for the pass, O(1) extra space.",
    traps=["Check `l <= r` (not `<`) so a single remaining person still takes a boat.", "State why the greedy is right: the heaviest must ride, so pair them with the best partner available.",
           "Sorting changes indices; if the answer needs original positions, sort `(value, index)` pairs.", "For circular or time values (minimum time difference), also compare the first and last elements around the wrap."],
    variants=["Minimum difference between any two elements: adjacent pairs after sorting.", "Largest perimeter triangle: sort descending, first triple with `a < b + c`.", "Array partition: pair adjacent sorted elements, sum the minimums.", "Two city scheduling: sort by cost difference."],
    notuse="When order must be preserved and cannot be recovered, or when an O(n) hash-based approach exists and is simpler.",
    problems=[
        (561, "Array Partition", "E", "array-partition", "Sort and sum every other element", "O(n log n) / O(1)"),
        (455, "Assign Cookies", "E", "assign-cookies", "Sort both; feed the least greedy child first", "O(n log n) / O(1)"),
        (976, "Largest Perimeter Triangle", "E", "largest-perimeter-triangle", "Sort descending; first valid triple", "O(n log n) / O(1)"),
        (881, "Boats to Save People", "M", "boats-to-save-people", "Sort; pair heaviest with lightest if it fits", "O(n log n) / O(1)"),
        (539, "Minimum Time Difference", "M", "minimum-time-difference", "Minutes sorted; adjacent gaps plus the wrap-around", "O(n log n) / O(n)"),
        (1029, "Two City Scheduling", "M", "two-city-scheduling", "Sort by cost(A) − cost(B); first half to A", "O(n log n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 9
P.append(dict(
    title="Cyclic sort: use the index as the hash", tier="sec", sim="cyclic", oneline="put each value x at index x − 1, then read the gaps",
    why="O(1)-space answer for missing and duplicate numbers in 1..n", signature="LC 41 / 448",
    when="An array of size n holds numbers from 1..n (possibly with duplicates and gaps) and you must find missing or repeated values.",
    detect="\"missing number\" · \"find all duplicates\" · \"set mismatch\" · \"first missing positive\" · values within `[1, n]`.",
    intuition="Seat numbered guests at a table with n numbered chairs: guest `x` should sit in chair `x`. Walk along and whenever a guest is in the wrong chair, swap them toward their own chair. When every guest who can be seated is seated, any chair holding the wrong guest points straight at the missing or duplicated number.",
    brute="Use a hash set or boolean array: O(n) extra space. Cyclic sort rearranges the input array itself, so the extra space is O(1).",
    idea="For each index `i`: while `a[i]` is in `1..n` and `a[a[i] − 1] != a[i]`, swap `a[i]` into its home. Each swap sends one value to its final place, so total swaps ≤ n. Afterwards, scan for `a[i] != i + 1`.",
    steps=["`i = 0`.", "While `a[i]` is in range and its home does not already hold it: swap `a[i]` with `a[a[i] − 1]`.", "Otherwise `i++`.", "Scan: the first `i` with `a[i] != i + 1` gives the missing number `i + 1` (and `a[i]` is a duplicate)."],
    trace_title="first missing positive in `[3, 4, −1, 1]`",
    trace="""swap 3 home (index 2)   [-1, 4, 3, 1]
swap 4 home (index 3)   [-1, 1, 3, 4]
swap 1 home (index 0)   [ 1,-1, 3, 4]
-1 ignored, 3 and 4 already home
scan: index 1 holds -1 instead of 2 -> first missing positive = 2""",
    code=[("find all numbers disappeared in 1..n (and duplicates)",
           """for (int i = 0; i < n; i++) {
    while (a[i] != a[a[i] - 1]) {                    // its home holds something else
        int j = a[i] - 1, t = a[i]; a[i] = a[j]; a[j] = t;
    }
}
List<Integer> missing = new ArrayList<>();
for (int i = 0; i < n; i++) if (a[i] != i + 1) missing.add(i + 1);   // a[i] is a duplicate""",
           """n = len(a)
for i in range(n):
    while a[i] != a[a[i] - 1]:                       # its home holds something else
        j = a[i] - 1
        a[i], a[j] = a[j], a[i]
missing = [i + 1 for i in range(n) if a[i] != i + 1]          # a[i] is a duplicate"""),
          ("first missing positive (values can be out of range)",
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
    complexity="O(n) time (each swap fixes one value), O(1) extra space; it mutates the input.",
    traps=["The inner loop must be a `while`: after a swap the new `a[i]` may also need moving.", "Guard against duplicates with `a[a[i] − 1] != a[i]` or you loop forever.",
           "Check the range first: `a[i] > 0 && a[i] <= n`.", "If the array may not be modified, use a boolean array or negation marking instead."],
    variants=["Negative marking: flip the sign at index `|x| − 1` instead of swapping (also O(1) space).", "Find the duplicate (Floyd cycle detection, one duplicate, no modification).", "Missing number in 0..n: XOR or sum formula."],
    notuse="Values outside 1..n that carry information, a read-only array, or when a hash set is acceptable and clearer.",
    problems=[
        (268, "Missing Number", "E", "missing-number", "Cyclic sort, or XOR / sum formula", "O(n) / O(1)"),
        (448, "Find All Numbers Disappeared in an Array", "E", "find-all-numbers-disappeared-in-an-array", "Cyclic sort then list misplaced indices", "O(n) / O(1)"),
        (645, "Set Mismatch", "E", "set-mismatch", "After cyclic sort, a[i] != i+1 gives duplicate and missing", "O(n) / O(1)"),
        (442, "Find All Duplicates in an Array", "M", "find-all-duplicates-in-an-array", "Sign-marking or cyclic sort", "O(n) / O(1)"),
        (287, "Find the Duplicate Number", "M", "find-the-duplicate-number", "Cyclic sort, or Floyd's cycle detection", "O(n) / O(1)"),
        (41, "First Missing Positive", "H", "first-missing-positive", "Cyclic sort within 1..n; first mismatch", "O(n) / O(1)"),
    ]))

TOPIC = dict(
    id="sorting_intervals", file="06_sorting_intervals.html", title="Sorting and Intervals — Pattern Guide",
    lead="Sorting is rarely the final answer; it is the move that makes the real answer easy. This guide covers the sorts you must know, custom comparators, counting and bucket sort, and the interval toolbox: merging, inserting, sweep line and greedy scheduling, plus sorting as preprocessing and cyclic sort. Each pattern has the intuition, a step-through animation, Java and Python code, and a ladder of LeetCode problems.",
    mindset="Sorting costs O(n log n) once and then buys you **order**: neighbours are the closest, ends are the extremes, overlaps become adjacent. For interval problems the two decisions are almost always the same: **what do I sort by** (start for merging and inserting, end for greedy selection) and **what do I track while scanning** (the last end, a running count, a heap of end times).",
    qintro="Ask these questions on every sorting or interval problem:",
    questions=["**Will sorting make the answer easier?** → pairs of extremes, adjacent differences, matching two lists.", "**Do I sort by start or by end?** → start to merge/insert; end to select the maximum number.",
               "**Is the range of values small?** → counting or bucket sort in O(n).", "**Do I need the number of overlaps?** → sweep line (+1 / −1 events) or a heap of end times.",
               "**Are the values exactly 1..n?** → cyclic sort with O(1) space."],
    cues=[
        ["\"sort an array\", \"merge sorted\", \"count inversions\"", "**P1** Comparison sorts"],
        ["\"arrange to form the largest\", \"sort by X then Y\"", "**P2** Custom comparator"],
        ["\"top K frequent\", small value range, \"h-index\"", "**P3** Counting and bucket sort"],
        ["\"merge intervals\", \"union of ranges\", \"intersections\"", "**P4** Merge intervals"],
        ["\"insert interval\", \"my calendar\", online booking", "**P5** Insert and ordered intervals"],
        ["\"minimum rooms\", \"maximum concurrent\", \"car pooling\", \"skyline\"", "**P6** Sweep line"],
        ["\"non-overlapping\", \"minimum arrows\", \"maximum events\"", "**P7** Greedy scheduling"],
        ["\"boats\", \"assign\", \"minimum difference\", pairing extremes", "**P8** Sort then two pointers"],
        ["\"missing / duplicate number in 1..n\", O(1) space", "**P9** Cyclic sort"],
    ],
    choose=[
        ["Need a guaranteed O(n log n) stable sort", "Merge sort (P1)"],
        ["Order defined by a rule, not by value", "Comparator (P2)"],
        ["Keys are small integers or frequencies", "Counting / bucket (P3)"],
        ["Combine overlapping ranges", "Sort by start, merge (P4)"],
        ["Add one range to a sorted list", "Three-phase insert (P5)"],
        ["Most ranges overlapping at once", "Sweep line or heap (P6)"],
        ["Keep as many non-overlapping as possible", "Sort by end, greedy (P7)"],
        ["Pair extremes or nearest values", "Sort + two pointers (P8)"],
        ["Missing / duplicate in 1..n, O(1) space", "Cyclic sort (P9)"],
    ],
    rule="**merge → sort by start; select the most → sort by end; count overlaps → sweep or heap.** If the range of values is small, skip sorting and index into an array.",
    selftest=[
        ("Why is merge sort stable and what keeps it stable?", "Taking from the left run when `left[i] <= right[j]` keeps equal elements in their original relative order."),
        ("Why must non-overlapping-interval greedy sort by **end**, not start?", "The interval that ends earliest leaves the most room for later ones. Sorting by start can pick a long interval that blocks many short ones."),
        ("In the sweep line, why process end events before start events at the same time?", "For half-open intervals `[s, e)`, a meeting ending at time t has already freed its room when another starts at t."),
        ("When can bucket sort run in O(n)?", "When keys lie in a known, small range (for example frequencies 1..n or ages 0..120), so each key maps directly to a bucket."),
        ("How does Insert Interval stay O(n) when the list is sorted?", "Intervals before the new one are copied, overlapping ones are absorbed in one scan, and the rest are copied, so each interval is touched once."),
        ("Why does a comparator like `(a, b) -> a − b` risk bugs?", "Subtraction overflows for extreme values; use `Integer.compare`."),
        ("What does cyclic sort guarantee after the swapping loop?", "Every value in 1..n that appears is at index value − 1, so any index with the wrong value reveals a missing number."),
        ("What is the worst case of quick sort and how do you avoid it?", "O(n²) when pivots are always the smallest or largest (for example sorted input with a fixed pivot). Randomise the pivot or use median-of-three."),
    ],
    plan=[
        "**Day 1:** merge sort and quick sort from memory; merge sorted array from the back.",
        "**Day 2:** comparators and multi-key sorts; counting and bucket sort for frequency problems.",
        "**Day 3:** merge intervals and interval intersections; write the three-phase insert without notes.",
        "**Day 4:** sweep line and the heap version of meeting rooms; car pooling with a difference array.",
        "**Day 5:** greedy scheduling: prove to yourself why sorting by end works on one counterexample.",
        "**Day 6:** sort-then-two-pointers problems and cyclic sort; redo anything needing a hint.",
    ],
    patterns=P,
)
