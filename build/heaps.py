"""Content for topic 10: Heaps and priority queues."""

P = []

# ---------------------------------------------------------------- 1
P.append(dict(
    title="Heap fundamentals: sift up, sift down, heapify", tier="hot", sim="heapops", oneline="a tree in an array that always knows its minimum",
    why="Everything else in this topic is built on three operations", signature="LC 1046 / 703",
    when="You repeatedly need the smallest (or largest) item of a changing collection.",
    detect="\"always take the largest / smallest\" · \"kth largest in a stream\" · \"last stone weight\" · \"priority\" · \"process in order of cost\".",
    intuition="A tournament bracket where the champion is always at the top: when a new player joins they play their way **up** while they beat their parent; when the champion leaves, the last player is moved to the top and plays their way **down** until they are no better than both children. Both walks are at most the height of the tree (log n), and the champion is available instantly.",
    brute="Keeping the collection sorted costs O(n) per insert; scanning for the minimum costs O(n) per query. A heap gives O(log n) insert and remove, and O(1) peek.",
    idea="A complete binary tree stored in an array: parent of `i` is `(i − 1) / 2`, children are `2i + 1` and `2i + 2`. Min-heap rule: parent ≤ children. **Push** = append, then sift up. **Pop** = move the last element to the root, then sift down. **Heapify** an array in O(n) by sifting down from the last parent to the root.",
    steps=["Push `x`: append at index `n`, swap with the parent while smaller.", "Peek: return `a[0]`.", "Pop: save `a[0]`, put the last element at the root, sift down choosing the **smaller** child each time.", "Heapify: for `i = n/2 − 1` down to `0`, sift down."],
    trace_title="push 5, 3, 8, 1 then pop (min-heap)",
    trace="""push 5     [5]
push 3     [5,3]      swap up -> [3,5]
push 8     [3,5,8]
push 1     [3,5,8,1]  swap with 5 -> swap with 3 -> [1,3,8,5]
pop        take 1, move last (5) to root: [5,3,8] -> swap with 3 -> [3,5,8]""",
    code=[("library priority queues",
           """PriorityQueue<Integer> minHeap = new PriorityQueue<>();                         // smallest first
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Collections.reverseOrder());   // largest first
minHeap.offer(5); minHeap.offer(3);
int smallest = minHeap.peek();       // O(1)
int removed  = minHeap.poll();       // O(log n)
PriorityQueue<Integer> fromList = new PriorityQueue<>(Arrays.asList(4, 1, 7)); // heapify in O(n)""",
           """import heapq
h = []                                  # a list is the heap; heapq is a MIN-heap
heapq.heappush(h, 5); heapq.heappush(h, 3)
smallest = h[0]                         # O(1) peek
removed = heapq.heappop(h)              # O(log n)
heapq.heapify(lst)                      # in place, O(n)
heapq.heappush(h, -x)                   # max-heap trick: store negatives"""),
          ("min-heap implemented by hand",
           """class MinHeap {
    int[] a = new int[16]; int n = 0;
    void push(int x) {
        if (n == a.length) a = Arrays.copyOf(a, 2 * n);
        a[n] = x; int i = n++;
        while (i > 0 && a[(i - 1) / 2] > a[i]) { swap(i, (i - 1) / 2); i = (i - 1) / 2; }   // sift up
    }
    int pop() {
        int top = a[0]; a[0] = a[--n]; int i = 0;
        while (true) {                                                                       // sift down
            int l = 2 * i + 1, r = l + 1, m = i;
            if (l < n && a[l] < a[m]) m = l;
            if (r < n && a[r] < a[m]) m = r;
            if (m == i) break;
            swap(i, m); i = m;
        }
        return top;
    }
    void swap(int i, int j) { int t = a[i]; a[i] = a[j]; a[j] = t; }
}""",
           """class MinHeap:
    def __init__(self):
        self.a = []
    def push(self, x):
        a = self.a
        a.append(x); i = len(a) - 1
        while i > 0 and a[(i - 1) // 2] > a[i]:                  # sift up
            a[(i - 1) // 2], a[i] = a[i], a[(i - 1) // 2]
            i = (i - 1) // 2
    def pop(self):
        a = self.a
        top, a[0] = a[0], a[-1]
        a.pop(); i, n = 0, len(a)
        while True:                                              # sift down
            l, r, m = 2 * i + 1, 2 * i + 2, i
            if l < n and a[l] < a[m]: m = l
            if r < n and a[r] < a[m]: m = r
            if m == i: break
            a[i], a[m] = a[m], a[i]; i = m
        return top""")],
    complexity="Push / pop O(log n), peek O(1), heapify O(n), space O(n). Removing an arbitrary item is O(n) to find it.",
    traps=["A heap is **not sorted**; only the root is guaranteed to be the minimum. Iterating a `PriorityQueue` does not give sorted order.", "Python's `heapq` is a min-heap only: negate values for a max-heap.",
           "Java `PriorityQueue.remove(obj)` is O(n); use lazy deletion for frequent removals.", "Do not mutate an element that is inside the heap; remove and re-insert instead."],
    variants=["Max-heap: reverse the comparison.", "Indexed / decrease-key heaps for Dijkstra optimisations.", "d-ary heaps and Fibonacci heaps exist, but binary heaps are what interviews expect."],
    notuse="When you need sorted iteration or range queries (use a balanced tree / `TreeMap`), or only one-time min / max (a single pass suffices).",
    problems=[
        (1046, "Last Stone Weight", "E", "last-stone-weight", "Max-heap: smash the two heaviest, push the difference", "O(n log n) / O(n)"),
        (703, "Kth Largest Element in a Stream", "E", "kth-largest-element-in-a-stream", "Min-heap of size k; its root is the answer", "O(log k) per add / O(k)"),
        (1337, "The K Weakest Rows in a Matrix", "E", "the-k-weakest-rows-in-a-matrix", "Heap of (soldiers, row) pairs", "O(m·n + m log k) / O(k)"),
        (506, "Relative Ranks", "E", "relative-ranks", "Max-heap of (score, index) popped in rank order", "O(n log n) / O(n)"),
        (1962, "Remove Stones to Minimize the Total", "M", "remove-stones-to-minimize-the-total", "Max-heap: halve the biggest pile k times", "O((n + k) log n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 2
P.append(dict(
    title="Top K: keep a heap of size k", tier="hot", sim="topk", oneline="to keep the k largest, use a MIN-heap of size k",
    why="The most common heap question: avoid sorting everything", signature="LC 215 / 347 / 973",
    when="You need the k largest, k smallest, k most frequent or k closest items.",
    detect="\"kth largest\" · \"top k frequent\" · \"k closest points\" · \"k closest elements\" · \"k smallest pairs\".",
    intuition="You are selecting a team of k tallest people from a crowd walking past one at a time. Keep the current best k in a little room; the **shortest of the k** stands at the door (min-heap root). A new person who is not taller than the door person can never make the team. If they are taller, they swap places with the door person. The door person is exactly the kth tallest so far.",
    brute="Sorting everything is O(n log n). A heap of size k costs O(log k) per element: O(n log k) time and O(k) space, and it works on a stream you cannot store.",
    idea="For **k largest** keep a **min**-heap of size k (pop the smallest when it grows past k). For **k smallest** keep a **max**-heap of size k. The root is the boundary element (kth largest / kth smallest).",
    steps=["Create an empty heap of the opposite type.", "For each item: push it.", "If the heap size exceeds `k`, pop the root.", "At the end the heap holds the answer; the root is the kth."],
    trace_title="2nd largest of `[3,2,1,5,6,4]`",
    trace="""push 3  [3]
push 2  [2,3]
push 1  size 3 > 2 -> pop 1   [2,3]
push 5  pop 2                 [3,5]
push 6  pop 3                 [5,6]
push 4  pop 4                 [5,6]
root = 5  -> 2nd largest""",
    code=[("kth largest with a size-k min-heap",
           """PriorityQueue<Integer> pq = new PriorityQueue<>();            // min-heap
for (int x : nums) {
    pq.offer(x);
    if (pq.size() > k) pq.poll();                              // drop the smallest of k+1
}
return pq.peek();                                              // kth largest""",
           """import heapq
h = []
for x in nums:
    heapq.heappush(h, x)
    if len(h) > k:
        heapq.heappop(h)                                       # drop the smallest of k+1
return h[0]                                                    # kth largest
# or: heapq.nlargest(k, nums)[-1]"""),
          ("k closest points to the origin (max-heap on distance, size k)",
           """PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> Integer.compare(d(b), d(a)));   // farthest on top
for (int[] p : points) {
    pq.offer(p);
    if (pq.size() > k) pq.poll();                              // remove the farthest
}
return pq.toArray(new int[0][]);
// int d(int[] p) { return p[0] * p[0] + p[1] * p[1]; }   // squared distance: no sqrt needed""",
           """import heapq
h = []                                                         # max-heap via negated distance
for x, y in points:
    heapq.heappush(h, (-(x * x + y * y), x, y))
    if len(h) > k:
        heapq.heappop(h)                                       # remove the farthest
return [[x, y] for _, x, y in h]"""),
          ("top k frequent elements",
           """Map<Integer, Integer> cnt = new HashMap<>();
for (int x : nums) cnt.merge(x, 1, Integer::sum);
PriorityQueue<Integer> pq = new PriorityQueue<>((a, b) -> cnt.get(a) - cnt.get(b));        // least frequent on top
for (int x : cnt.keySet()) { pq.offer(x); if (pq.size() > k) pq.poll(); }
int[] res = new int[k];
for (int i = k - 1; i >= 0; i--) res[i] = pq.poll();""",
           """from collections import Counter
import heapq
cnt = Counter(nums)
return heapq.nlargest(k, cnt.keys(), key=cnt.get)              # O(n log k)""")],
    complexity="O(n log k) time, O(k) space.",
    traps=["The heap type is the **opposite** of what you want: k largest ↔ min-heap.", "Compare squared distances; avoid `sqrt` and floating-point error.",
           "Pop **after** pushing (size k + 1 → k) or compare with the root before pushing; both work.", "When k is close to n, sorting or quickselect (O(n) average) may be simpler."],
    variants=["Quickselect gives the kth in O(n) average but needs the whole array in memory.", "k closest elements to x in a sorted array: binary search on the left bound.", "Top k frequent words: tie-break alphabetically in the comparator."],
    notuse="k = 1 (a single pass min / max), or k ≈ n (just sort).",
    problems=[
        (215, "Kth Largest Element in an Array", "M", "kth-largest-element-in-an-array", "Size-k min-heap (or quickselect)", "O(n log k) / O(k)"),
        (973, "K Closest Points to Origin", "M", "k-closest-points-to-origin", "Size-k max-heap on squared distance", "O(n log k) / O(k)"),
        (347, "Top K Frequent Elements", "M", "top-k-frequent-elements", "Count, then a size-k min-heap on frequency", "O(n log k) / O(n)"),
        (692, "Top K Frequent Words", "M", "top-k-frequent-words", "Heap with (count, word) ordering for ties", "O(n log k) / O(n)"),
        (658, "Find K Closest Elements", "M", "find-k-closest-elements", "Heap of (distance, value), or binary search the window", "O(n log k) / O(k)"),
    ]))

# ---------------------------------------------------------------- 3
P.append(dict(
    title="Two heaps: running median", tier="hot", sim="median", oneline="a max-heap for the lower half, a min-heap for the upper half",
    why="The classic hard heap question, and a pattern for balanced halves", signature="LC 295 / 480",
    when="You need the median (or any middle value) of a growing or sliding collection.",
    detect="\"median from a data stream\" · \"sliding window median\" · \"maximise capital (IPO)\" · \"balance two halves\".",
    intuition="Split the numbers into the smaller half and the larger half. The median is at the boundary, so you only need **the biggest of the small half** and **the smallest of the large half**: exactly what a max-heap and a min-heap hand you instantly. Keep the halves the same size (or the lower one bigger by one) and the median is one or two heap tops.",
    brute="Sorting after each insert is O(n log n) per query; inserting into a sorted array is O(n). Two heaps make insert O(log n) and median O(1).",
    idea="`low` = max-heap of the smaller half, `high` = min-heap of the larger half. Add: push to `low`, move `low`'s top to `high`, and if `high` is bigger move its top back. Median: `low.top` if the sizes differ, else the average of the two tops.",
    steps=["`low.add(x)`.", "`high.add(low.poll())` (keeps every `low` ≤ every `high`).", "If `high.size() > low.size()`, `low.add(high.poll())`.", "Median = `low.peek()` if `low` is larger, else `(low.peek() + high.peek()) / 2`."],
    trace_title="stream `5, 15, 1, 3`",
    trace="""add 5   low [5]       high []        median 5
add 15  low [5]       high [15]      median 10
add 1   low [1,5]     high [15]      median 5
add 3   low [1,3]     high [5,15]    median 4""",
    code=[("find median from a data stream",
           """class MedianFinder {
    PriorityQueue<Integer> low = new PriorityQueue<>(Collections.reverseOrder());   // max-heap: smaller half
    PriorityQueue<Integer> high = new PriorityQueue<>();                             // min-heap: larger half
    void addNum(int x) {
        low.offer(x);
        high.offer(low.poll());                       // largest of the small half moves up
        if (high.size() > low.size()) low.offer(high.poll());   // rebalance: low may be one bigger
    }
    double findMedian() {
        return low.size() > high.size() ? low.peek() : (low.peek() + high.peek()) / 2.0;
    }
}""",
           """import heapq
class MedianFinder:
    def __init__(self):
        self.low, self.high = [], []                  # low is a max-heap (negated), high a min-heap
    def addNum(self, x):
        heapq.heappush(self.low, -x)
        heapq.heappush(self.high, -heapq.heappop(self.low))   # largest of the small half moves up
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))
    def findMedian(self):
        if len(self.low) > len(self.high):
            return -self.low[0]
        return (-self.low[0] + self.high[0]) / 2""")],
    complexity="add O(log n), median O(1), space O(n).",
    traps=["Use `/ 2.0` (or `/ 2` in Python 3) for the average; integer division loses the half.", "Keep the invariant `|low| − |high| ∈ {0, 1}` after every insert.",
           "Python: negate values in the max-heap, and negate again when reading.", "Sliding window median needs deletions: use lazy deletion with counters or a sorted multiset."],
    variants=["Sliding window median: two heaps with lazy deletion, or one balanced structure.", "IPO / maximise capital: a min-heap of projects by capital plus a max-heap of affordable profits.", "Median of two sorted arrays: binary search instead (topic 02)."],
    notuse="A static array (use quickselect) or when only approximate quantiles are needed (use sketches).",
    problems=[
        (295, "Find Median from Data Stream", "H", "find-median-from-data-stream", "Max-heap low + min-heap high, balanced sizes", "O(log n) per add / O(n)"),
        (502, "IPO", "H", "ipo", "Min-heap by capital to unlock, max-heap by profit to pick", "O(n log n) / O(n)"),
        (480, "Sliding Window Median", "H", "sliding-window-median", "Two heaps with lazy deletion (or a sorted structure)", "O(n log k) / O(n)"),
    ]))

# ---------------------------------------------------------------- 4
P.append(dict(
    title="K-way merge", tier="hot", sim="kmerge", oneline="one candidate per list in the heap; pop, then push that list's next",
    why="Merging sorted streams efficiently is a frequent hard-ish question", signature="LC 23 / 373 / 632",
    when="You have k sorted sequences (or a sorted matrix / pair space) and need the smallest items in order.",
    detect="\"merge k sorted lists\" · \"kth smallest in a sorted matrix\" · \"k pairs with smallest sums\" · \"smallest range covering k lists\" · \"ugly numbers\".",
    intuition="k queues of customers, each already in order of arrival time. The next customer to serve overall is the earliest among the **fronts** of the k queues. A heap holds exactly those k fronts: pop the earliest, serve them, and put their queue's **next** customer in. The heap never grows beyond k.",
    brute="Concatenate everything and sort: O(N log N). Comparing the k heads linearly each time: O(N·k). The heap gives O(N log k).",
    idea="Heap entries `(value, listIndex, positionInList)`. Pop the smallest, output it, and push the next element of that same list (if any). For implicit sorted spaces (matrix rows, pair sums `a[i] + b[j]`) the \"next\" is the neighbour to the right or below.",
    steps=["Push the first element of every list.", "Pop the minimum and append it to the output.", "Push the next element from the same list.", "Repeat until the heap is empty (or you have produced k items)."],
    trace_title="`[1,4,5]`, `[1,3,4]`, `[2,6]`",
    trace="""heap: 1(L0) 1(L1) 2(L2)
pop 1(L0) push 4       out 1
pop 1(L1) push 3       out 1 1
pop 2(L2) push 6       out 1 1 2
pop 3(L1) push 4       out ... 3
...                    out 1 1 2 3 4 4 5 6""",
    code=[("merge k sorted linked lists",
           """PriorityQueue<ListNode> pq = new PriorityQueue<>((a, b) -> a.val - b.val);
for (ListNode l : lists) if (l != null) pq.offer(l);                // the head of each list
ListNode dummy = new ListNode(), tail = dummy;
while (!pq.isEmpty()) {
    ListNode n = pq.poll();
    tail.next = n; tail = n;
    if (n.next != null) pq.offer(n.next);                           // next candidate from the same list
}
return dummy.next;""",
           """import heapq
heap = [(l.val, i, l) for i, l in enumerate(lists) if l]            # i breaks ties: nodes are not comparable
heapq.heapify(heap)
dummy = tail = ListNode()
while heap:
    _, i, n = heapq.heappop(heap)
    tail.next = n; tail = n
    if n.next:
        heapq.heappush(heap, (n.next.val, i, n.next))               # next candidate from the same list
return dummy.next"""),
          ("k pairs with the smallest sums (implicit sorted lists)",
           """PriorityQueue<int[]> pq = new PriorityQueue<>((x, y) -> x[0] - y[0]);   // {sum, i, j}
for (int i = 0; i < Math.min(k, a.length); i++) pq.offer(new int[]{a[i] + b[0], i, 0});
List<List<Integer>> res = new ArrayList<>();
while (k-- > 0 && !pq.isEmpty()) {
    int[] t = pq.poll();
    res.add(List.of(a[t[1]], b[t[2]]));
    if (t[2] + 1 < b.length) pq.offer(new int[]{a[t[1]] + b[t[2] + 1], t[1], t[2] + 1});   // advance j
}""",
           """import heapq
heap = [(a[i] + b[0], i, 0) for i in range(min(k, len(a)))]        # row i is the sorted list a[i] + b[*]
heapq.heapify(heap)
res = []
while heap and len(res) < k:
    s, i, j = heapq.heappop(heap)
    res.append([a[i], b[j]])
    if j + 1 < len(b):
        heapq.heappush(heap, (a[i] + b[j + 1], i, j + 1))          # advance j""")],
    complexity="O(N log k) time for N total elements, O(k) heap space.",
    traps=["Python tuples compare element by element: add an index tiebreaker so non-comparable objects are never compared.", "Push the **next** element of the list you just popped, not of an arbitrary list.",
           "Smallest range covering k lists: also track the current maximum while popping minima.", "Sorted matrix: start with the first column (or row), not all cells."],
    variants=["Kth smallest in a sorted matrix: pop k times (or binary search on value).", "Ugly Number II / super ugly numbers: k pointers = k implicit sorted lists.", "Merge k sorted arrays into one array: same heap with array indexes."],
    notuse="k = 2 (a simple two-pointer merge is enough) or when all data fits and you can just sort.",
    problems=[
        (373, "Find K Pairs with Smallest Sums", "M", "find-k-pairs-with-smallest-sums", "Heap of (sum, i, j); advance j", "O(k log k) / O(k)"),
        (378, "Kth Smallest Element in a Sorted Matrix", "M", "kth-smallest-element-in-a-sorted-matrix", "Heap seeded with the first column; pop k times", "O(k log n) / O(n)"),
        (786, "K-th Smallest Prime Fraction", "M", "k-th-smallest-prime-fraction", "Heap of fractions i/j for each denominator j", "O(k log n) / O(n)"),
        (23, "Merge k Sorted Lists", "H", "merge-k-sorted-lists", "Heap of the k list heads", "O(N log k) / O(k)"),
        (632, "Smallest Range Covering Elements from K Lists", "H", "smallest-range-covering-elements-from-k-lists", "Min-heap plus a tracked max; shrink the range", "O(N log k) / O(k)"),
        (1439, "Find the Kth Smallest Sum of a Matrix With Sorted Rows", "H", "find-the-kth-smallest-sum-of-a-matrix-with-sorted-rows", "Merge rows one by one keeping only k sums", "O(m·k log k) / O(k)"),
    ]))

# ---------------------------------------------------------------- 5
P.append(dict(
    title="Greedy with a heap: always take the best available", tier="hot", sim="ropes", oneline="the heap serves up the cheapest (or best) option every time",
    why="Many scheduling and \"minimum cost\" greedy problems need a fast min / max", signature="LC 1167 / 1642 / 621",
    when="At each step the greedy choice is \"the smallest cost / largest gain currently available\", and the available set changes.",
    detect="\"minimum cost to connect\" · \"furthest building you can reach\" · \"task scheduler\" · \"minimum refuelling stops\" · \"hire k workers\" · \"meeting rooms\".",
    intuition="Connecting ropes: every time you join two ropes, the result gets joined again later and its cost is paid again. So the shortest ropes should be joined first, when they are still cheap, and the long ones last. The heap hands you the two shortest in O(log n) every time. The same \"best option right now\" idea solves scheduling: always run the task with the most remaining work, or spend the cheapest resource first.",
    brute="Re-sorting after each step is O(n log n) per step, O(n² log n) overall. A heap makes each step O(log n).",
    idea="State the greedy rule, then maintain the candidate set in a heap: pop the best, act, push any new candidates. A **regret** variant: take every option now, and when you run out of a resource, undo (pop) the most wasteful earlier choice.",
    steps=["Identify what you repeatedly need: the cheapest, the largest, the earliest.", "Heap the candidates by that key.", "Loop: pop the best, update the answer, push new candidates created by the action.", "For regret problems: push every choice, and pop the worst one when a limit is exceeded."],
    trace_title="connect sticks `[1, 8, 3, 5]`",
    trace="""join 1+3 = 4   cost 4    heap [4,5,8]
join 4+5 = 9   cost 9    heap [8,9]
join 8+9 = 17  cost 17   heap [17]
total = 4 + 9 + 17 = 30""",
    code=[("minimum cost to connect sticks",
           """PriorityQueue<Integer> pq = new PriorityQueue<>();
for (int s : sticks) pq.offer(s);
int cost = 0;
while (pq.size() > 1) {
    int a = pq.poll(), b = pq.poll();
    cost += a + b;
    pq.offer(a + b);                       // the merged stick can be joined again
}
return cost;""",
           """import heapq
heapq.heapify(sticks)
cost = 0
while len(sticks) > 1:
    a, b = heapq.heappop(sticks), heapq.heappop(sticks)
    cost += a + b
    heapq.heappush(sticks, a + b)          # the merged stick can be joined again
return cost"""),
          ("furthest building you can reach (regret with a min-heap)",
           """PriorityQueue<Integer> climbs = new PriorityQueue<>();           // bricks used on the biggest climbs so far
for (int i = 0; i + 1 < h.length; i++) {
    int d = h[i + 1] - h[i];
    if (d <= 0) continue;
    climbs.offer(d);
    if (climbs.size() > ladders) bricks -= climbs.poll();      // give the SMALLEST climb to bricks, keep ladders for big ones
    if (bricks < 0) return i;
}
return h.length - 1;""",
           """import heapq
climbs = []                                                    # the biggest climbs, which get the ladders
for i in range(len(h) - 1):
    d = h[i + 1] - h[i]
    if d <= 0:
        continue
    heapq.heappush(climbs, d)
    if len(climbs) > ladders:
        bricks -= heapq.heappop(climbs)                        # smallest climb falls back to bricks
    if bricks < 0:
        return i
return len(h) - 1""")],
    complexity="Typically O(n log n) time, O(n) space.",
    traps=["Prove (or at least state) why the greedy choice is safe; wrong greedy rules are the usual failure.", "Heap entries often need a pair: `(priority, payload)`.",
           "Task scheduler with cooldown: pair the heap with a waiting queue of (time ready, count).", "Min-cost hire K workers: sort by wage/quality ratio, keep a max-heap of the k smallest qualities."],
    variants=["Task scheduler: max-heap of remaining counts plus a cooldown queue (or the closed-form formula).", "Minimum refuelling stops: push every reachable station's fuel, pop the biggest when you run dry.", "Meeting rooms II: min-heap of end times (topic 06)."],
    notuse="Greedy does not apply (DP needed), or all decisions are known in advance (just sort).",
    problems=[
        (1642, "Furthest Building You Can Reach", "M", "furthest-building-you-can-reach", "Min-heap of climbs; spill the smallest to bricks", "O(n log L) / O(L)"),
        (621, "Task Scheduler", "M", "task-scheduler", "Max-heap of counts with a cooldown queue", "O(n log 26) / O(26)"),
        (871, "Minimum Number of Refueling Stops", "H", "minimum-number-of-refueling-stops", "Max-heap of passed stations; refuel with the biggest when stuck", "O(n log n) / O(n)"),
        (502, "IPO", "H", "ipo", "Unlock by capital, pick the max profit each round", "O(n log n) / O(n)"),
        (857, "Minimum Cost to Hire K Workers", "H", "minimum-cost-to-hire-k-workers", "Sort by wage/quality; max-heap of the k smallest qualities", "O(n log n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 6
P.append(dict(
    title="Lazy deletion and heap + hash map designs", tier="sec", sim="lazy", oneline="leave stale entries; discard them when they reach the top",
    why="Heaps cannot delete from the middle cheaply, so real designs use this trick", signature="LC 239 / 2034",
    when="Elements expire or change (leave a window, price updated, order cancelled) but you still need the current best.",
    detect="\"sliding window maximum with a heap\" · \"stock price fluctuation\" · \"order backlog\" · \"number container system\" · \"design Twitter feed\".",
    intuition="Instead of searching the pile to throw out an old paper, just leave it there and check the **top** paper each time you need the best one: if it is out of date, throw it away and look at the next. Stale items never affect the answer because you only ever act on the top, and each item is thrown away at most once.",
    brute="Removing an arbitrary item from a heap is O(n) (find, then re-heapify). Lazy deletion keeps every operation O(log n) amortised.",
    idea="Store enough in each entry to tell whether it is still valid (an index, a timestamp, a version). Keep a source-of-truth structure (a map, the current window bounds). Before using the top: `while top is stale: pop`.",
    steps=["Push entries with an identity (value, index / timestamp).", "Update the truth: window start, `map[key] = newValue`.", "Before reading the top, pop while the top does not match the truth.", "Each entry is pushed once and popped once: O(log n) amortised."],
    trace_title="windows of 3 over `[9,3,1,2,5]`",
    trace="""i=2 push (1,2): top (9,0) valid        max 9
i=3 push (2,3): top (9,0) index 0 <= 0 stale -> pop
                top (3,1) valid               max 3
i=4 push (5,4): top (5,4)                     max 5""",
    code=[("sliding window maximum with a heap",
           """PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> b[0] - a[0]);   // {value, index}, max on top
int[] res = new int[n - k + 1];
for (int i = 0; i < n; i++) {
    pq.offer(new int[]{a[i], i});
    if (i >= k - 1) {
        while (pq.peek()[1] <= i - k) pq.poll();                // stale: left the window
        res[i - k + 1] = pq.peek()[0];
    }
}""",
           """import heapq
h, res = [], []
for i, x in enumerate(a):
    heapq.heappush(h, (-x, i))                                  # max-heap via negation
    if i >= k - 1:
        while h[0][1] <= i - k:
            heapq.heappop(h)                                    # stale: left the window
        res.append(-h[0][0])"""),
          ("stock price: current price per timestamp may change",
           """class StockPrice {
    Map<Integer, Integer> price = new HashMap<>();                       // the truth: timestamp -> price
    PriorityQueue<int[]> mx = new PriorityQueue<>((a, b) -> b[0] - a[0]);   // {price, timestamp}
    PriorityQueue<int[]> mn = new PriorityQueue<>((a, b) -> a[0] - b[0]);
    int latest = 0;
    void update(int t, int p) { price.put(t, p); latest = Math.max(latest, t); mx.offer(new int[]{p, t}); mn.offer(new int[]{p, t}); }
    int current() { return price.get(latest); }
    int maximum() { while (price.get(mx.peek()[1]) != mx.peek()[0]) mx.poll(); return mx.peek()[0]; }   // discard stale
    int minimum() { while (price.get(mn.peek()[1]) != mn.peek()[0]) mn.poll(); return mn.peek()[0]; }
}""",
           """import heapq
class StockPrice:
    def __init__(self):
        self.price, self.latest = {}, 0                       # the truth: timestamp -> price
        self.mx, self.mn = [], []                             # (−price, ts) and (price, ts)
    def update(self, t, p):
        self.price[t] = p
        self.latest = max(self.latest, t)
        heapq.heappush(self.mx, (-p, t)); heapq.heappush(self.mn, (p, t))
    def current(self):
        return self.price[self.latest]
    def maximum(self):
        while -self.mx[0][0] != self.price[self.mx[0][1]]:
            heapq.heappop(self.mx)                            # discard stale
        return -self.mx[0][0]
    def minimum(self):
        while self.mn[0][0] != self.price[self.mn[0][1]]:
            heapq.heappop(self.mn)
        return self.mn[0][0]""")],
    complexity="O(log n) amortised per operation, O(n) space (stale entries stay until they surface).",
    traps=["Check validity of the **top** in a loop (`while`), not an `if`: several stale entries can sit on top.", "Keep the truth structure in sync (update the map before pushing).",
           "Memory can grow with stale entries; for very long streams, rebuild occasionally.", "Window maximum in O(n) uses a monotonic deque instead (topic 05)."],
    variants=["Order backlog: two heaps (buy / sell), pop while quantities are exhausted.", "Number container system: map index → number plus a min-heap of indices per number.", "Design Twitter: merge the latest tweets of followees with a heap (k-way merge)."],
    notuse="When a `TreeMap` / sorted set supports direct removal in O(log n), or a monotonic deque gives O(n).",
    problems=[
        (239, "Sliding Window Maximum", "H", "sliding-window-maximum", "Heap of (value, index); pop stale tops", "O(n log n) / O(n)"),
        (2034, "Stock Price Fluctuation", "M", "stock-price-fluctuation", "Map of truth + max-heap + min-heap with lazy deletion", "O(log n) per op / O(n)"),
        (2349, "Design a Number Container System", "M", "design-a-number-container-system", "Map index → number; per-number min-heap of indices", "O(log n) per op / O(n)"),
        (1801, "Number of Orders in the Backlog", "M", "number-of-orders-in-the-backlog", "Buy max-heap and sell min-heap; match and reduce quantities", "O(n log n) / O(n)"),
        (355, "Design Twitter", "M", "design-twitter", "Heap-merge the most recent tweets of followees", "O(F log F) per feed / O(n)"),
    ]))

# ---------------------------------------------------------------- 7
P.append(dict(
    title="Heap sort and comparator-driven heaps", tier="sec", sim="heapsort", oneline="build a max-heap, then move the max to the end n times",
    why="The in-place O(n log n) sort, and the template for custom priorities", signature="LC 912 / 1985",
    when="You need an O(1)-space O(n log n) sort, or the priority is a custom rule (length then alphabet, distance then index).",
    detect="\"sort in place with guaranteed O(n log n)\" · \"kth largest number as strings\" · \"distant barcodes\" · priorities with several keys.",
    intuition="Heap sort keeps the unsorted part as a heap and builds the sorted part from the back: the maximum is at the root, swap it to the last slot (its final place), shrink the heap, and sift the new root down to restore order. After n rounds the array is sorted. For custom priorities, the comparator is the rule that says which of two items is \"smaller\" (comes out first).",
    brute="Selection sort finds the maximum in O(n) every round: O(n²). The heap finds it in O(1) and repairs in O(log n).",
    idea="(1) Heapify the array into a max-heap (sift down from `n/2 − 1` to 0). (2) For `end = n − 1` down to 1: swap `a[0]` and `a[end]`, then sift down the root within `[0, end)`.",
    steps=["Heapify: sift down each parent from the last one to the root.", "Swap the root (max) with the last element of the heap.", "Shrink the heap by one; sift the new root down.", "Repeat until the heap has one element."],
    trace_title="heap sort `[4,10,3,5,1]`",
    trace="""heapify -> [10,5,3,4,1]        max-heap
swap 10 with last: [1,5,3,4 | 10]   sift -> [5,4,3,1 | 10]
swap 5  with last: [1,4,3 | 5,10]   sift -> [4,1,3 | 5,10]
swap 4  with last: [3,1 | 4,5,10]   sift -> [3,1 | ...]
swap 3, then 1     sorted [1,3,4,5,10]""",
    code=[("heap sort in place",
           """void heapSort(int[] a) {
    int n = a.length;
    for (int i = n / 2 - 1; i >= 0; i--) sift(a, i, n);          // build a max-heap in O(n)
    for (int end = n - 1; end > 0; end--) {
        int t = a[0]; a[0] = a[end]; a[end] = t;                  // max goes to its final place
        sift(a, 0, end);                                          // repair the shrunken heap
    }
}
void sift(int[] a, int i, int n) {
    while (true) {
        int l = 2 * i + 1, r = l + 1, m = i;
        if (l < n && a[l] > a[m]) m = l;
        if (r < n && a[r] > a[m]) m = r;
        if (m == i) return;
        int t = a[i]; a[i] = a[m]; a[m] = t; i = m;
    }
}""",
           """def heap_sort(a):
    n = len(a)
    def sift(i, size):
        while True:
            l, r, m = 2 * i + 1, 2 * i + 2, i
            if l < size and a[l] > a[m]: m = l
            if r < size and a[r] > a[m]: m = r
            if m == i: return
            a[i], a[m] = a[m], a[i]
            i = m
    for i in range(n // 2 - 1, -1, -1):                           # build a max-heap in O(n)
        sift(i, n)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]                               # max goes to its final place
        sift(0, end)                                              # repair the shrunken heap"""),
          ("custom priority: shorter strings first, ties alphabetically",
           """PriorityQueue<String> pq = new PriorityQueue<>((x, y) ->
    x.length() != y.length() ? Integer.compare(x.length(), y.length()) : x.compareTo(y));
for (String s : words) pq.offer(s);""",
           """import heapq
h = [(len(s), s) for s in words]                                  # tuples compare element by element
heapq.heapify(h)
length, s = heapq.heappop(h)""")],
    complexity="Heap sort: O(n log n) in every case, O(1) extra space, not stable. Heapify alone is O(n).",
    traps=["Sift down within `[0, size)`, not the whole array, once the heap has shrunk.", "Comparators for numeric strings must compare by **length first**, then lexicographically.",
           "Not stable: equal items can change relative order.", "Use `Integer.compare` instead of subtraction in comparators to avoid overflow."],
    variants=["Introsort (quick sort that falls back to heap sort) is what many libraries use.", "Distant barcodes: max-heap by count, place the top two alternately.", "Kth largest string-number: comparator on length then lexicographic."],
    notuse="You need stability (use merge sort / TimSort) or the data is small and nearly sorted (insertion sort).",
    problems=[
        (912, "Sort an Array", "M", "sort-an-array", "Heap sort as an in-place O(n log n) option", "O(n log n) / O(1)"),
        (1985, "Find the Kth Largest Integer in the Array", "M", "find-the-kth-largest-integer-in-the-array", "Numbers as strings: compare by length, then lexicographically", "O(n log k · L) / O(k)"),
        (1054, "Distant Barcodes", "M", "distant-barcodes", "Max-heap by count; alternate the two most frequent", "O(n log k) / O(k)"),
        (215, "Kth Largest Element in an Array", "M", "kth-largest-element-in-an-array", "Heap sort idea: k extractions from a max-heap", "O(n + k log n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 8
P.append(dict(
    title="Best-first search: Dijkstra and friends", tier="hot", sim="dijkstra", oneline="always expand the cheapest unfinished node",
    why="Weighted shortest paths are impossible at scale without a priority queue", signature="LC 743 / 1631",
    when="Shortest (cheapest) paths on a graph with non-negative weights, or any search where the next state to expand is the lowest-cost one.",
    detect="\"network delay time\" · \"cheapest flights\" · \"path with minimum effort\" · \"swim in rising water\" · \"path with maximum probability\".",
    intuition="Spilling water from a source: it reaches the nearest places first, then spreads further. A priority queue orders the frontier by distance so the next node you finalise is the closest one you have not finished. Because weights are non-negative, nothing found later can be shorter, so a node is final the **first time** it is popped.",
    brute="Bellman-Ford relaxes every edge V times: O(V·E). Dijkstra with a heap is O((V + E) log V).",
    idea="`dist[src] = 0`; push `(0, src)`. Pop `(d, u)`; if `d > dist[u]` skip (stale). Otherwise relax every edge `u → v` with weight `w`: if `d + w < dist[v]`, update and push `(dist[v], v)`. The priority can be any additive or monotone cost (max edge on the path, product of probabilities).",
    steps=["`dist` array filled with ∞; `dist[src] = 0`; heap = `[(0, src)]`.", "Pop the smallest `(d, u)`; skip it if it is stale.", "For each neighbour `v`: if `d + w < dist[v]`, set it and push.", "Stop early when the target is popped, or run until the heap is empty."],
    trace_title="edges A→B 4, A→C 1, C→B 2, B→D 1, C→D 5, D→E 3",
    trace="""pop (0,A): B=4, C=1
pop (1,C): B=3 (better), D=6
pop (3,B): D=4 (better)
pop (4,D): E=7
pop (6,D): stale, skip
pop (7,E)
dist: A0 B3 C1 D4 E7""",
    code=[("Dijkstra with a priority queue",
           """int[] dist = new int[n];
Arrays.fill(dist, Integer.MAX_VALUE);
dist[src] = 0;
PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);        // {distance, node}
pq.offer(new int[]{0, src});
while (!pq.isEmpty()) {
    int[] cur = pq.poll();
    int d = cur[0], u = cur[1];
    if (d > dist[u]) continue;                                               // stale entry
    for (int[] e : graph[u]) {                                                // e = {neighbour, weight}
        int v = e[0], w = e[1];
        if (d + w < dist[v]) { dist[v] = d + w; pq.offer(new int[]{dist[v], v}); }
    }
}""",
           """import heapq
dist = [float('inf')] * n
dist[src] = 0
heap = [(0, src)]
while heap:
    d, u = heapq.heappop(heap)
    if d > dist[u]:
        continue                                                              # stale entry
    for v, w in graph[u]:
        if d + w < dist[v]:
            dist[v] = d + w
            heapq.heappush(heap, (dist[v], v))"""),
          ("path with minimum effort (cost = largest step on the path)",
           """int[][] effort = new int[m][n];
for (int[] row : effort) Arrays.fill(row, Integer.MAX_VALUE);
effort[0][0] = 0;
PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);        // {effort, r, c}
pq.offer(new int[]{0, 0, 0});
int[][] D = {{1,0},{-1,0},{0,1},{0,-1}};
while (!pq.isEmpty()) {
    int[] cur = pq.poll(); int e = cur[0], r = cur[1], c = cur[2];
    if (r == m - 1 && c == n - 1) return e;
    if (e > effort[r][c]) continue;
    for (int[] d : D) {
        int nr = r + d[0], nc = c + d[1];
        if (nr < 0 || nc < 0 || nr >= m || nc >= n) continue;
        int ne = Math.max(e, Math.abs(h[nr][nc] - h[r][c]));                 // cost combines with max, not +
        if (ne < effort[nr][nc]) { effort[nr][nc] = ne; pq.offer(new int[]{ne, nr, nc}); }
    }
}""",
           """import heapq
effort = [[float('inf')] * n for _ in range(m)]
effort[0][0] = 0
heap = [(0, 0, 0)]
while heap:
    e, r, c = heapq.heappop(heap)
    if (r, c) == (m - 1, n - 1):
        return e
    if e > effort[r][c]:
        continue
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < m and 0 <= nc < n:
            ne = max(e, abs(h[nr][nc] - h[r][c]))                             # cost combines with max, not +
            if ne < effort[nr][nc]:
                effort[nr][nc] = ne
                heapq.heappush(heap, (ne, nr, nc))""")],
    complexity="O((V + E) log V) time, O(V + E) space.",
    traps=["**Negative weights break Dijkstra** (use Bellman-Ford).", "Skip stale entries (`d > dist[u]`) or the complexity degrades.",
           "Use `long` (or a large sentinel that cannot overflow when added to) for distances.", "State-augmented searches (cheapest flight with ≤ K stops) need the number of stops in the state."],
    variants=["Path with maximum probability: max-heap on probability (or min-heap on −log p).", "Swim in rising water / minimum effort: the priority is a **max** along the path.", "0-1 BFS: when weights are 0 or 1, a deque is enough (topic 05).", "A*: add a heuristic to the priority."],
    notuse="Unweighted graphs (BFS), graphs with negative weights, or all-pairs shortest paths (Floyd-Warshall).",
    problems=[
        (743, "Network Delay Time", "M", "network-delay-time", "Dijkstra from k; answer is the largest distance", "O(E log V) / O(V + E)"),
        (1514, "Path with Maximum Probability", "M", "path-with-maximum-probability", "Max-heap on probability, multiply along edges", "O(E log V) / O(V + E)"),
        (1631, "Path With Minimum Effort", "M", "path-with-minimum-effort", "Dijkstra where cost = max edge difference", "O(m·n log(m·n)) / O(m·n)"),
        (787, "Cheapest Flights Within K Stops", "M", "cheapest-flights-within-k-stops", "State (cost, node, stops left), or Bellman-Ford with K rounds", "O(E·K) / O(V)"),
        (778, "Swim in Rising Water", "H", "swim-in-rising-water", "Dijkstra where cost = max cell height on the path", "O(n² log n) / O(n²)"),
    ]))

# ---------------------------------------------------------------- 9
P.append(dict(
    title="Frequency heaps: reorganise and rank by count", tier="sec", sim="reorg", oneline="a max-heap of counts decides what to place next",
    why="Rearrangement and \"remove to minimise\" problems on counts", signature="LC 767 / 1405",
    when="You must order items so equal ones are separated, or remove the most frequent items first.",
    detect="\"reorganize string\" · \"longest happy string\" · \"reduce array size to half\" · \"least number of unique integers\" · \"rearrange so no two adjacent are equal\".",
    intuition="Seating guests so no two from the same family sit together: always seat someone from the **largest remaining family**, but never the same family twice in a row. If the biggest family is more than half the seats (rounded up), it is impossible. A max-heap on counts gives the biggest family instantly; holding the family just seated out of the heap for one round enforces the no-repeat rule.",
    brute="Trying permutations is factorial. Sorting once is not enough because counts change after every placement. The heap re-ranks in O(log k) per step.",
    idea="Max-heap of `(count, letter)`. Pop the top, append it, decrement; keep it **out** of the heap until the next letter has been placed, then push it back if its count is still positive.",
    steps=["Count frequencies; push `(count, letter)` into a max-heap.", "Pop the top, append the letter, decrement its count.", "Push the **previous** letter back if it still has copies; hold the current one.", "If at the end the string is shorter than the input, return failure."],
    trace_title="`\"aaabbc\"`",
    trace="""heap a3 b2 c1
place a (a2 held)            "a"
place b, push a2 back        "ab"   (b1 held)
place a, push b1 back        "aba"  (a1 held)
place b, push a1 back        "abab" (b0)
place a                       "ababa"
place c                       "ababac\"""",
    code=[("reorganize string",
           """int[] cnt = new int[26];
for (char c : s.toCharArray()) cnt[c - 'a']++;
PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> b[1] - a[1]);          // {letter, count}, biggest count first
for (int i = 0; i < 26; i++) if (cnt[i] > 0) pq.offer(new int[]{i, cnt[i]});
StringBuilder sb = new StringBuilder();
int[] prev = null;
while (!pq.isEmpty()) {
    int[] cur = pq.poll();
    sb.append((char) ('a' + cur[0]));
    cur[1]--;
    if (prev != null && prev[1] > 0) pq.offer(prev);                           // eligible again
    prev = cur;                                                                // held out for one round
}
return sb.length() == s.length() ? sb.toString() : "";""",
           """from collections import Counter
import heapq
heap = [(-c, ch) for ch, c in Counter(s).items()]
heapq.heapify(heap)
res, prev = [], None
while heap:
    c, ch = heapq.heappop(heap)
    res.append(ch)
    if prev and prev[0] < 0:
        heapq.heappush(heap, prev)                                           # eligible again
    prev = (c + 1, ch)                                                       # held out for one round (count is negative)
return ''.join(res) if len(res) == len(s) else ''"""),
          ("reduce the array to at most half its size (remove the most frequent values)",
           """Map<Integer, Integer> cnt = new HashMap<>();
for (int x : arr) cnt.merge(x, 1, Integer::sum);
PriorityQueue<Integer> pq = new PriorityQueue<>(Collections.reverseOrder());
pq.addAll(cnt.values());
int removed = 0, sets = 0;
while (removed * 2 < arr.length) { removed += pq.poll(); sets++; }              // take the biggest groups first
return sets;""",
           """from collections import Counter
import heapq
heap = [-c for c in Counter(arr).values()]
heapq.heapify(heap)
removed = sets = 0
while removed * 2 < len(arr):
    removed += -heapq.heappop(heap)                                          # take the biggest groups first
    sets += 1
return sets""")],
    complexity="O(n log k) time for k distinct items, O(k) space.",
    traps=["Without holding back the last item, you can place the same letter twice in a row.", "Impossible when `maxCount > (n + 1) / 2`: detect early or check the length at the end.",
           "Longest happy string: also limit **three** in a row, so track the last two placed.", "Tie-breaking in the heap affects which valid answer you get, not whether one exists."],
    variants=["Task scheduler: same hold-back idea with a cooldown queue.", "Sort characters by frequency: heap or bucket sort (topic 06).", "Least unique integers after k removals: remove the smallest counts first (min-heap)."],
    notuse="When a counting / bucket approach is simpler, or when you only need the single most frequent item.",
    problems=[
        (1338, "Reduce Array Size to The Half", "M", "reduce-array-size-to-the-half", "Remove the most frequent values first", "O(n log n) / O(n)"),
        (1481, "Least Number of Unique Integers after K Removals", "M", "least-number-of-unique-integers-after-k-removals", "Remove the least frequent values first", "O(n log n) / O(n)"),
        (451, "Sort Characters By Frequency", "M", "sort-characters-by-frequency", "Max-heap of counts, or buckets", "O(n log k) / O(n)"),
        (767, "Reorganize String", "M", "reorganize-string", "Most frequent letter not equal to the previous one", "O(n log k) / O(k)"),
        (1405, "Longest Happy String", "M", "longest-happy-string", "Max-heap; avoid three equal in a row by using the next letter", "O(n log 3) / O(1)"),
    ]))

TOPIC = dict(
    id="heaps", file="10_heap_priority_queue.html", title="Heaps and Priority Queues — Pattern Guide",
    lead="A heap answers \"what is the smallest (or largest) thing right now?\" in O(1) and keeps that answer up to date in O(log n). This guide covers heap mechanics, top-K, the two-heap median, k-way merge, greedy with heaps, lazy deletion, heap sort and comparators, Dijkstra, and frequency heaps. Each pattern has the intuition, a step-through animation that draws the heap as a tree, Java and Python code, and a ladder of LeetCode problems.",
    mindset="Reach for a heap when the problem keeps asking for **the best remaining item** while the set of items changes. Three questions pick the pattern: do I need the **k best** (size-k heap), the **middle** (two heaps), or the **next in global order across several sources** (k-way merge, Dijkstra)? And remember that a heap is only partially ordered: only the top is guaranteed.",
    qintro="Ask these questions on every heap problem:",
    questions=["**Do I repeatedly need the min or max of a changing set?** → heap.", "**Do I need only the k best?** → a heap of size k, of the **opposite** type.", "**Do I need the median or a boundary between two halves?** → two heaps.",
               "**Am I merging sorted sources or expanding the cheapest state next?** → k-way merge / Dijkstra.", "**Do entries expire or change?** → lazy deletion."],
    cues=[
        ["\"largest / smallest repeatedly\", \"stream\", \"last stone\"", "**P1** Heap mechanics"],
        ["\"kth largest\", \"top k frequent\", \"k closest\"", "**P2** Size-k heap"],
        ["\"median\", \"balance two halves\"", "**P3** Two heaps"],
        ["\"merge k sorted\", \"kth smallest in sorted matrix / pairs\"", "**P4** K-way merge"],
        ["\"minimum cost to connect\", \"refuelling stops\", \"task scheduling\"", "**P5** Greedy with a heap"],
        ["items expire or are updated, design problems", "**P6** Lazy deletion"],
        ["\"sort in place\", custom multi-key priority", "**P7** Heap sort and comparators"],
        ["\"shortest path with weights\", \"minimum effort\"", "**P8** Dijkstra"],
        ["\"reorganise\", \"no two adjacent equal\", frequency ranking", "**P9** Frequency heaps"],
    ],
    choose=[
        ["Always take the best of a changing set", "Heap (P1)"],
        ["Only the k best of a large stream", "Size-k heap of the opposite type (P2)"],
        ["Running median", "Two heaps (P3)"],
        ["Smallest items across sorted lists", "K-way merge (P4)"],
        ["Cheapest option now, repeatedly", "Greedy + heap (P5)"],
        ["Remove from the middle of a heap", "Lazy deletion (P6)"],
        ["Weighted shortest path", "Dijkstra (P8)"],
        ["Arrange so equal items are separated", "Max-heap of counts, hold back one (P9)"],
    ],
    rule="**k largest → min-heap of size k; k smallest → max-heap of size k; median → two heaps; sorted sources → k-way merge; weighted shortest path → Dijkstra.** If you need arbitrary removal, use lazy deletion or a `TreeMap`.",
    selftest=[
        ("Why use a MIN-heap to keep the k largest elements?", "Its root is the smallest of the k kept values, so it is exactly the element to evict when a larger one arrives, and it is also the kth largest."),
        ("What is the time complexity of heapify, and why is it not O(n log n)?", "O(n): most nodes are near the bottom and sift down only a few levels; the work sums to a geometric series."),
        ("In the two-heap median, what invariant keeps the median at the tops?", "Every element of the max-heap is ≤ every element of the min-heap, and their sizes differ by at most one (low is never smaller)."),
        ("Why is the heap in a k-way merge never larger than k?", "It holds exactly one candidate (the current front) from each non-exhausted list; popping one pushes at most one."),
        ("Why does Dijkstra fail with negative edges?", "It assumes that when a node is popped its distance is final; a negative edge found later could give a shorter path to an already-finalised node."),
        ("What does lazy deletion do and when is the stale item removed?", "It leaves an invalid item inside the heap and discards it only when it reaches the top, checked against the source of truth."),
        ("Why does `PriorityQueue` iteration not return sorted order?", "A heap only guarantees the root; the array layout is a partial order. Poll repeatedly or sort a copy to get sorted order."),
        ("How do you build a max-heap with Python's `heapq`?", "Push negated values (or `(−priority, item)` tuples) and negate again when reading."),
    ],
    plan=[
        "**Day 1:** heap mechanics: implement push, pop and heapify by hand; then last stone weight and kth largest stream.",
        "**Day 2:** top-K problems (215, 347, 973, 692) until the \"opposite heap\" rule is automatic.",
        "**Day 3:** two heaps: find median from data stream; draw the invariant before coding.",
        "**Day 4:** k-way merge: merge k lists, kth smallest in a sorted matrix, k smallest pairs.",
        "**Day 5:** greedy with a heap (connect sticks, furthest building, task scheduler) and lazy deletion designs.",
        "**Day 6:** Dijkstra on weighted graphs and grids; then reorganize string.",
    ],
    patterns=P,
)
