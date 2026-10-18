"""Content for topic 18: design-style problems (caches, iterators, rate limiters, feeds, editors)."""

P = []

# ---------------------------------------------------------------- 1
P.append(dict(
    title="LRU and LFU caches", tier="hot", sim="lfu", oneline="a hash map for lookup plus an ordered structure for eviction",
    why="The most common design question: O(1) get and put with an eviction policy", signature="LC 146 / 460",
    when="You must cache a bounded number of items and evict by recency (LRU) or by use count (LFU) with O(1) operations.",
    detect="\"LRU cache\" · \"LFU cache\" · \"evict the least …\" · \"O(1) get and put\" · \"capacity\".",
    intuition="Lookup needs a **hash map**; eviction needs **order**. Combine them. LRU: a linked list ordered by recency (head = most recent) where the map points straight at list nodes, so a use is \"unlink + push front\" in O(1) and eviction is \"drop the tail\". LFU: one ordered bucket of keys **per frequency** and a `minFreq` pointer. A use moves the key from bucket `f` to bucket `f + 1`; eviction removes the oldest key of bucket `minFreq`. In Java `LinkedHashMap` (access order) and in Python `OrderedDict` give you the ordered list for free.",
    brute="Scanning for the least recently used key is O(n) per eviction. The map + ordered structure makes everything O(1).",
    idea="LRU: `map: key → node`, doubly linked list (or `LinkedHashMap` / `OrderedDict`). LFU: `values`, `freq`, `buckets: freq → ordered keys`, `minFreq`. A `put` of a new key into a full cache evicts first, then inserts with frequency 1 and sets `minFreq = 1`.",
    steps=["Map key → value (and frequency).", "On every `get` / `put` of an existing key, \"touch\" it (move to the front, or to the next frequency bucket).", "When full and inserting a new key, evict the oldest key of the lowest bucket.", "Update `minFreq` when its bucket becomes empty after a touch."],
    trace_title="LFU capacity 2: put 1, put 2, get 1, put 3, get 2, get 3",
    trace="""put(1,1) put(2,2)      freq: 1->1, 2->1
get(1) = 1              freq: 1->2
put(3,3)                full: evict key 2 (freq 1)
get(2) = -1             get(3) = 3""",
    code=[("LFU cache with frequency buckets (O(1) get and put)",
           """class LFUCache {
    private final int capacity;
    private int minFreq = 0;
    private final Map<Integer, Integer> values = new HashMap<>();
    private final Map<Integer, Integer> freq = new HashMap<>();
    private final Map<Integer, LinkedHashSet<Integer>> buckets = new HashMap<>();   // frequency -> keys, oldest first
    LFUCache(int capacity) { this.capacity = capacity; }
    int get(int key) {
        if (!values.containsKey(key)) return -1;
        touch(key);
        return values.get(key);
    }
    void put(int key, int value) {
        if (capacity == 0) return;
        if (values.containsKey(key)) { values.put(key, value); touch(key); return; }
        if (values.size() == capacity) {
            int victim = buckets.get(minFreq).iterator().next();           // least frequent, then least recent
            buckets.get(minFreq).remove(victim);
            values.remove(victim);
            freq.remove(victim);
        }
        values.put(key, value);
        freq.put(key, 1);
        buckets.computeIfAbsent(1, f -> new LinkedHashSet<>()).add(key);
        minFreq = 1;
    }
    private void touch(int key) {
        int f = freq.get(key);
        buckets.get(f).remove(key);
        if (buckets.get(f).isEmpty() && minFreq == f) minFreq++;           // the lowest bucket emptied
        freq.put(key, f + 1);
        buckets.computeIfAbsent(f + 1, x -> new LinkedHashSet<>()).add(key);
    }
}""",
           """from collections import defaultdict, OrderedDict

class LFUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.min_freq = 0
        self.val = {}
        self.freq = {}
        self.buckets = defaultdict(OrderedDict)                          # frequency -> keys, oldest first

    def _touch(self, key):
        f = self.freq[key]
        del self.buckets[f][key]
        if not self.buckets[f] and self.min_freq == f:                   # the lowest bucket emptied
            self.min_freq += 1
        self.freq[key] = f + 1
        self.buckets[f + 1][key] = None

    def get(self, key):
        if key not in self.val:
            return -1
        self._touch(key)
        return self.val[key]

    def put(self, key, value):
        if self.cap == 0:
            return
        if key in self.val:
            self.val[key] = value
            self._touch(key)
            return
        if len(self.val) == self.cap:
            victim, _ = self.buckets[self.min_freq].popitem(last=False)   # least frequent, then least recent
            del self.val[victim], self.freq[victim]
        self.val[key] = value
        self.freq[key] = 1
        self.buckets[1][key] = None
        self.min_freq = 1"""),
          ("LRU cache in a few lines (LinkedHashMap with access order / OrderedDict)",
           """class LRUCache extends LinkedHashMap<Integer, Integer> {
    private final int capacity;
    LRUCache(int capacity) {
        super(capacity, 0.75f, true);                                      // true = iterate in access order
        this.capacity = capacity;
    }
    public int get(int key) { return super.getOrDefault(key, -1); }
    @Override protected boolean removeEldestEntry(Map.Entry<Integer, Integer> eldest) {
        return size() > capacity;                                          // evict the least recently used
    }
}""",
           """from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.d = OrderedDict()

    def get(self, key):
        if key not in self.d:
            return -1
        self.d.move_to_end(key)                                            # most recently used goes last
        return self.d[key]

    def put(self, key, value):
        self.d[key] = value
        self.d.move_to_end(key)
        if len(self.d) > self.cap:
            self.d.popitem(last=False)                                     # evict the least recently used""")],
    complexity="O(1) per get and put, O(capacity) space.",
    traps=["Updating an **existing** key counts as a use and must not evict anything.", "LFU needs a tie-break (least recently used among the lowest frequency) and a correct `minFreq` update.",
           "A new key into a full LFU cache resets `minFreq` to 1 *after* evicting.", "Capacity 0 is a valid input for LFU."],
    variants=["LRU with a hand-written doubly linked list and sentinels (topic 04).", "TTL caches: store an expiry time and evict lazily.", "All O(1) Data Structure: increment / decrement counts with min and max keys.", "Thread-safe caches: wrap in locks or use segmented maps."],
    notuse="You only need the single most recent item, or capacity is tiny (a list is fine).",
    problems=[
        (146, "LRU Cache", "M", "lru-cache", "Hash map + doubly linked list (or LinkedHashMap / OrderedDict)", "O(1) per op / O(c)"),
        (460, "LFU Cache", "H", "lfu-cache", "Frequency buckets + minFreq", "O(1) per op / O(c)"),
        (432, "All O`one Data Structure", "H", "all-oone-data-structure", "Doubly linked list of count buckets", "O(1) per op / O(n)"),
        (706, "Design HashMap", "E", "design-hashmap", "Array of buckets; the structure behind every map", "O(1) average / O(n)"),
    ]))

# ---------------------------------------------------------------- 2
P.append(dict(
    title="O(1) random access: array + hash map", tier="hot", sim="rset", oneline="delete by swapping with the last element",
    why="Insert, delete and getRandom all in constant time", signature="LC 380 / 528",
    when="You need a collection with O(1) insert, delete **and** uniform random selection, or weighted random selection.",
    detect="\"insert delete getRandom O(1)\" · \"random pick with weight\" · \"random pick index\" · \"shuffle an array\" · \"blacklist random\".",
    intuition="A hash set deletes in O(1) but cannot pick a random element in O(1). An array picks randomly in O(1) but deletes from the middle in O(n). Combine them: keep the values in an **array** and a **map value → index**. To delete, overwrite the doomed slot with the **last** element, fix that element's index in the map, and pop the end. The order of the array does not matter for a random pick. For **weighted** picks, store prefix sums and binary-search a random number in `[0, total)`.",
    brute="Scanning a list for a random element or for a deletion: O(n). Array + map: O(1).",
    idea="`insert(v)`: if absent, `index[v] = items.size()`, append. `remove(v)`: `i = index[v]`, `last = items[-1]`, `items[i] = last`, `index[last] = i`, pop, `delete index[v]` (in that order, so removing the last element itself works). `getRandom`: `items[random(size)]`. Weighted: `prefix[i]`, pick `r < total`, first `prefix > r`.",
    steps=["Append new values and record their index.", "To delete, copy the last element into the hole.", "Update the map for the moved element, pop, and delete the old key.", "Random pick = random index."],
    trace_title="insert 10, 20, 30, 40, remove 20",
    trace="""items [10, 20, 30, 40]  index {10:0, 20:1, 30:2, 40:3}
remove(20): i = 1, last = 40 -> items[1] = 40, index[40] = 1
pop -> items [10, 40, 30], delete index[20]""",
    code=[("RandomizedSet",
           """class RandomizedSet {
    private final List<Integer> items = new ArrayList<>();
    private final Map<Integer, Integer> index = new HashMap<>();
    private final Random rnd = new Random();
    boolean insert(int val) {
        if (index.containsKey(val)) return false;
        index.put(val, items.size());
        items.add(val);
        return true;
    }
    boolean remove(int val) {
        Integer i = index.get(val);
        if (i == null) return false;
        int last = items.get(items.size() - 1);
        items.set(i, last);                                            // move the last element into the hole
        index.put(last, i);
        items.remove(items.size() - 1);
        index.remove(val);                                             // after the put, so removing the last element works
        return true;
    }
    int getRandom() { return items.get(rnd.nextInt(items.size())); }
}""",
           """import random

class RandomizedSet:
    def __init__(self):
        self.items = []
        self.index = {}

    def insert(self, val):
        if val in self.index:
            return False
        self.index[val] = len(self.items)
        self.items.append(val)
        return True

    def remove(self, val):
        if val not in self.index:
            return False
        i, last = self.index[val], self.items[-1]
        self.items[i] = last                                           # move the last element into the hole
        self.index[last] = i
        self.items.pop()
        del self.index[val]                                            # after the assignment, so removing the last element works
        return True

    def get_random(self):
        return random.choice(self.items)"""),
          ("random pick with weight (prefix sums + binary search)",
           """class WeightedPicker {
    private final int[] prefix;
    private final int total;
    private final Random rnd = new Random();
    WeightedPicker(int[] w) {
        prefix = new int[w.length];
        int s = 0;
        for (int i = 0; i < w.length; i++) { s += w[i]; prefix[i] = s; }
        total = s;
    }
    int pick() { return pickAt(rnd.nextInt(total)); }
    int pickAt(int r) {                                                // first index whose prefix sum exceeds r
        int lo = 0, hi = prefix.length - 1;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (prefix[mid] > r) hi = mid; else lo = mid + 1;
        }
        return lo;
    }
}""",
           """import random
from bisect import bisect_right
from itertools import accumulate

class WeightedPicker:
    def __init__(self, w):
        self.prefix = list(accumulate(w))
        self.total = self.prefix[-1]

    def pick(self):
        return self.pick_at(random.randrange(self.total))

    def pick_at(self, r):                                              # first index whose prefix sum exceeds r
        return bisect_right(self.prefix, r)""")],
    complexity="O(1) per insert, remove and getRandom; weighted pick O(log n), O(n) space.",
    traps=["Update the moved element's index **before** deleting the removed key (otherwise deleting the last element resurrects it).", "Uniform means a uniform *index*, which needs an array with no holes.",
           "Weighted pick: random number in `[0, total)` and the **first prefix greater than** it, not greater-or-equal.", "Duplicates (LC 381) need a map from value to a **set** of indices."],
    variants=["Insert Delete GetRandom with duplicates: map value → set of indices.", "Random pick index with equal targets: reservoir sampling.", "Shuffle an array: Fisher–Yates.", "Random pick with blacklist: remap blacklisted slots below `n − |blacklist|`."],
    notuse="Order of elements matters (use an ordered structure) or you never need random access.",
    problems=[
        (380, "Insert Delete GetRandom O(1)", "M", "insert-delete-getrandom-o1", "Array + map; swap-with-last deletion", "O(1) per op / O(n)"),
        (381, "Insert Delete GetRandom O(1) - Duplicates allowed", "H", "insert-delete-getrandom-o1-duplicates-allowed", "Map value → set of indices; same swap trick", "O(1) per op / O(n)"),
        (528, "Random Pick with Weight", "M", "random-pick-with-weight", "Prefix sums + binary search for a random number", "O(log n) per pick / O(n)"),
        (710, "Random Pick with Blacklist", "H", "random-pick-with-blacklist", "Map blacklisted slots in the prefix to valid slots at the end", "O(1) per pick / O(b)"),
    ]))

# ---------------------------------------------------------------- 3
P.append(dict(
    title="Iterators: lazy traversal with a stack", tier="sec", sim="iter", oneline="keep just enough state to produce the next element on demand",
    why="Implement hasNext / next without materialising the whole sequence", signature="LC 341 / 173",
    when="You expose a sequence one element at a time over a nested or tree-shaped structure.",
    detect="\"flatten nested list iterator\" · \"binary search tree iterator\" · \"zigzag iterator\" · \"peeking iterator\" · \"design an iterator\".",
    intuition="An iterator must be **lazy**: it remembers where it is and does only the work needed for the next element. For nested lists keep a **stack** of pending items; before answering `hasNext` unwrap lists on top until an integer is on top. For a BST keep the stack of the **left spine**: pop the top, then push the left spine of its right child. State is O(depth), each element is pushed and popped once, so `next` is O(1) amortised.",
    brute="Flattening everything into a list in the constructor costs O(n) time and memory up front and fails on huge or infinite sources.",
    idea="Nested: stack of iterators (or items in reverse); `advance()` finds the next integer and stores it in `nextVal`; `hasNext()` is `nextVal != null`. BST: `push_left(node)` walks left pushing; `next()` pops, calls `push_left(node.right)`, returns the value.",
    steps=["Initialise the stack with the structure.", "Before `hasNext` or `next`, unwrap until the top is a value.", "`next` pops that value and prepares the following one.", "State is only the stack (depth), not the whole data."],
    trace_title="`[[1,[2,3]],4,[5]]`",
    trace="""stack: [[1,[2,3]], 4, [5]] (top = first)
hasNext: unwrap [1,[2,3]] -> 1, [2,3], 4, [5]
next() 1 ; next(): unwrap [2,3] -> 2 ; next() 3 ; next() 4 ; unwrap [5] -> next() 5""",
    code=[("flatten a nested list with a stack of iterators",
           """class NestedIterator implements Iterator<Integer> {
    private final Deque<Iterator<?>> stack = new ArrayDeque<>();
    private Integer nextVal = null;
    NestedIterator(List<?> nested) {
        stack.push(nested.iterator());
        advance();
    }
    private void advance() {                                           // find the next integer, unwrapping lists on the way
        nextVal = null;
        while (!stack.isEmpty()) {
            if (!stack.peek().hasNext()) { stack.pop(); continue; }
            Object o = stack.peek().next();
            if (o instanceof Integer) { nextVal = (Integer) o; return; }
            stack.push(((List<?>) o).iterator());
        }
    }
    public boolean hasNext() { return nextVal != null; }
    public Integer next() {
        Integer r = nextVal;
        advance();
        return r;
    }
}""",
           """class NestedIterator:
    def __init__(self, nested):
        self.stack = [iter(nested)]
        self.nxt = None
        self._advance()

    def _advance(self):                                                # find the next integer, unwrapping lists on the way
        self.nxt = None
        while self.stack:
            try:
                o = next(self.stack[-1])
            except StopIteration:
                self.stack.pop()
                continue
            if isinstance(o, list):
                self.stack.append(iter(o))
            else:
                self.nxt = o
                return

    def has_next(self):
        return self.nxt is not None

    def next(self):
        r = self.nxt
        self._advance()
        return r"""),
          ("BST iterator (controlled in-order traversal)",
           """class BSTIterator {
    private final Deque<TreeNode> stack = new ArrayDeque<>();
    BSTIterator(TreeNode root) { pushLeft(root); }
    private void pushLeft(TreeNode node) {
        for (; node != null; node = node.left) stack.push(node);       // the left spine
    }
    int next() {
        TreeNode node = stack.pop();                                   // smallest remaining
        pushLeft(node.right);
        return node.val;
    }
    boolean hasNext() { return !stack.isEmpty(); }
}""",
           """class BSTIterator:
    def __init__(self, root):
        self.stack = []
        self._push_left(root)

    def _push_left(self, node):
        while node:                                                    # the left spine
            self.stack.append(node)
            node = node.left

    def next(self):
        node = self.stack.pop()                                        # smallest remaining
        self._push_left(node.right)
        return node.val

    def has_next(self):
        return bool(self.stack)""")],
    complexity="O(1) amortised per call; O(depth) memory.",
    traps=["The nested iterator must handle **empty lists** (e.g. `[[], [[]]]`): unwrap in a loop, not once.", "Compute the next value in `hasNext` or eagerly after `next`, never rely on `next` being called after `hasNext`.",
           "Python `None` sentinel is unsafe if the data can contain `None`; here values are integers.", "Do not flatten in the constructor: lazy is the point."],
    variants=["Peeking iterator: cache one element ahead.", "Zigzag iterator: queue of iterators, rotate after each element.", "Iterator for combinations: generate in lexicographic order with indices.", "Generators (`yield`) express the same state machine in Python."],
    notuse="The data is small and flattening up front is simpler and acceptable.",
    problems=[
        (173, "Binary Search Tree Iterator", "M", "binary-search-tree-iterator", "Stack of the left spine", "O(1) amortised / O(h)"),
        (284, "Peeking Iterator", "M", "peeking-iterator", "Cache the next element", "O(1) / O(1)"),
        (341, "Flatten Nested List Iterator", "M", "flatten-nested-list-iterator", "Stack of items; unwrap lists in hasNext", "O(1) amortised / O(d)"),
        (1286, "Iterator for Combination", "M", "iterator-for-combination", "Generate combinations in lexicographic order with a bitmask or index list", "O(k) per next / O(k)"),
    ]))

# ---------------------------------------------------------------- 4
P.append(dict(
    title="Rate limiters and counters over time", tier="hot", sim="rate", oneline="a queue of timestamps, or a bucket that refills with time",
    why="A real-world design question with several accepted algorithms", signature="LC 362 / 359",
    when="You must allow a limited number of events per time window, or answer \"how many events in the last N seconds\".",
    detect="\"rate limiter\" · \"hit counter\" · \"logger rate limiter\" · \"moving average from data stream\" · \"throttle requests\" · \"token bucket\".",
    intuition="**Sliding window log:** remember the timestamps of allowed requests in a queue; before deciding, discard those older than the window, then allow only if fewer than `limit` remain: exact, O(limit) memory per client. **Token bucket:** a bucket holds up to `capacity` tokens and refills continuously at `rate` tokens per second; each request spends a token: O(1) memory and permits bursts. **Fixed window counter** is O(1) but can let through twice the limit around a window boundary; **sliding window counter** blends two adjacent windows to smooth that out.",
    brute="Keeping every request forever and counting the window each time is O(n) per request. Dropping expired entries from a queue makes it amortised O(1).",
    idea="Window log: `while q and q[0] <= now − window: pop`; `if len(q) < limit: push now`. Token bucket: `tokens = min(cap, tokens + (now − last) · rate)`; `last = now`; allow if `tokens ≥ 1` and subtract 1.",
    steps=["Decide the algorithm from the accuracy / memory trade-off.", "On each request first expire old state (timestamps or refill tokens).", "Decide allow or deny from the remaining budget.", "Record the request only if it was allowed."],
    trace_title="limit 3 per 10 s, requests at 1 2 3 5 11 12 13 14",
    trace="""1,2,3 allowed -> window [1,2,3]
5 denied (3 in window)
11: drop 1 -> [2,3] -> allow -> [2,3,11]
12: drop 2 -> allow; 13: drop 3 -> allow; 14: window [11,12,13] full -> deny""",
    code=[("sliding window log limiter",
           """class SlidingWindowLimiter {
    private final int limit;
    private final long windowMs;
    private final Deque<Long> times = new ArrayDeque<>();
    SlidingWindowLimiter(int limit, long windowMs) { this.limit = limit; this.windowMs = windowMs; }
    boolean allow(long now) {
        while (!times.isEmpty() && times.peekFirst() <= now - windowMs) times.pollFirst();   // expire old requests
        if (times.size() >= limit) return false;
        times.addLast(now);
        return true;
    }
}""",
           """from collections import deque

class SlidingWindowLimiter:
    def __init__(self, limit, window):
        self.limit, self.window = limit, window
        self.times = deque()

    def allow(self, now):
        while self.times and self.times[0] <= now - self.window:        # expire old requests
            self.times.popleft()
        if len(self.times) >= self.limit:
            return False
        self.times.append(now)
        return True"""),
          ("token bucket (O(1) memory, allows bursts)",
           """class TokenBucket {
    private final double capacity, ratePerSec;
    private double tokens;
    private double last;
    TokenBucket(double capacity, double ratePerSec) {
        this.capacity = capacity;
        this.ratePerSec = ratePerSec;
        this.tokens = capacity;
        this.last = 0;
    }
    boolean allow(double nowSec) {
        tokens = Math.min(capacity, tokens + (nowSec - last) * ratePerSec);   // refill for the elapsed time
        last = nowSec;
        if (tokens < 1) return false;
        tokens -= 1;
        return true;
    }
}""",
           """class TokenBucket:
    def __init__(self, capacity, rate_per_sec):
        self.capacity, self.rate = capacity, rate_per_sec
        self.tokens = capacity
        self.last = 0

    def allow(self, now):
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)   # refill for the elapsed time
        self.last = now
        if self.tokens < 1:
            return False
        self.tokens -= 1
        return True""")],
    complexity="Window log: amortised O(1) time, O(limit) memory per key. Token bucket: O(1) time and memory per key.",
    traps=["Boundary: is a request exactly `window` seconds old still inside? Use `<=` consistently (`times[0] <= now − window` expires it).", "Only **allowed** requests are recorded; denied ones must not extend the window.",
           "Use one limiter per user / IP / API key (a map of limiters) and clean up idle ones.", "Distributed rate limiting needs shared state (Redis counters / Lua scripts) and clock handling."],
    variants=["Hit counter: queue of timestamps or 300 circular buckets.", "Logger rate limiter: map message → last allowed time.", "Moving average from a data stream: queue + running sum.", "Leaky bucket: fixed outflow rate (a queue that drains)."],
    notuse="A single in-memory counter without time is enough, or you need cross-machine coordination (that is a systems problem beyond a class).",
    problems=[
        (933, "Number of Recent Calls", "E", "number-of-recent-calls", "Queue; drop requests older than 3000 ms", "O(1) amortised / O(n)"),
        (1348, "Tweet Counts Per Frequency", "M", "tweet-counts-per-frequency", "Sorted timestamps per name + binary search per window", "O(log n + k) / O(n)"),
        (622, "Design Circular Queue", "M", "design-circular-queue", "Fixed array with head and size (bucket idea for hit counters)", "O(1) per op / O(k)"),
    ]))

# ---------------------------------------------------------------- 5
P.append(dict(
    title="Versioned and time-based stores", tier="hot", sim="tkv", oneline="append history in time order, then binary-search the version you need",
    why="Key-value stores with history, snapshots and time travel", signature="LC 981 / 1146",
    when="Values change over time and queries ask for the value **as of** a time or snapshot.",
    detect="\"time based key-value store\" · \"snapshot array\" · \"get value at timestamp\" · \"design a database with history\" · \"stock price at time\".",
    intuition="If writes arrive with **increasing timestamps** (or snapshot ids), each key's history is automatically sorted. Store it as a list of `(timestamp, value)` and answer \"value as of `t`\" with a **binary search for the last entry with time ≤ `t`** (upper bound, then step back one). For snapshot arrays store only the **changes** per index with the snapshot id when they happened, so taking a snapshot is O(1) and memory is proportional to the number of writes.",
    brute="Copying the whole state at every snapshot costs O(n) per snapshot. Storing only changes and binary-searching makes `snap` O(1) and `get` O(log h).",
    idea="`set`: append `(t, value)` to the key's list. `get(key, t)`: find the first index with time > `t`; if 0 return empty, else return the value at index − 1. Snapshot array: per index a list of `(snapId, value)` starting with `(0, 0)`; `set` overwrites the last entry if it belongs to the current snapshot; `snap` returns and increments the id.",
    steps=["Append writes to the key's history (already sorted by time).", "For a read, binary-search the upper bound of the query time.", "Step back one entry; before the first entry means \"no value\".", "For snapshots, record only changes and the id at which they happened."],
    trace_title="history `1→a, 4→b, 7→c, 10→d`, get at 8",
    trace="""upper bound of 8: first timestamp > 8 is 10 (index 3)
answer = index 2 -> timestamp 7, value "c"
get at 0: upper bound is index 0 -> no value""",
    code=[("time-based key-value store",
           """class TimeMap {
    private final Map<String, List<Integer>> times = new HashMap<>();
    private final Map<String, List<String>> values = new HashMap<>();
    void set(String key, String value, int timestamp) {
        times.computeIfAbsent(key, k -> new ArrayList<>()).add(timestamp);      // timestamps are increasing
        values.computeIfAbsent(key, k -> new ArrayList<>()).add(value);
    }
    String get(String key, int timestamp) {
        List<Integer> ts = times.get(key);
        if (ts == null) return "";
        int lo = 0, hi = ts.size();                                         // first index with time > timestamp
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (ts.get(mid) <= timestamp) lo = mid + 1; else hi = mid;
        }
        return lo == 0 ? "" : values.get(key).get(lo - 1);
    }
}""",
           """from bisect import bisect_right
from collections import defaultdict

class TimeMap:
    def __init__(self):
        self.times = defaultdict(list)
        self.values = defaultdict(list)

    def set(self, key, value, timestamp):
        self.times[key].append(timestamp)                                   # timestamps are increasing
        self.values[key].append(value)

    def get(self, key, timestamp):
        ts = self.times.get(key)
        if not ts:
            return ""
        i = bisect_right(ts, timestamp)                                     # first index with time > timestamp
        return self.values[key][i - 1] if i else \"\""""),
          ("snapshot array (store only the changes)",
           """class SnapshotArray {
    private final List<int[]>[] history;                                    // per index: {snapId, value}, ids increasing
    private int snapId = 0;
    @SuppressWarnings("unchecked")
    SnapshotArray(int length) {
        history = new List[length];
        for (int i = 0; i < length; i++) {
            history[i] = new ArrayList<>();
            history[i].add(new int[]{0, 0});
        }
    }
    void set(int index, int val) {
        List<int[]> h = history[index];
        int[] last = h.get(h.size() - 1);
        if (last[0] == snapId) last[1] = val; else h.add(new int[]{snapId, val});
    }
    int snap() { return snapId++; }
    int get(int index, int id) {
        List<int[]> h = history[index];
        int lo = 0, hi = h.size();                                          // first entry with snapId > id
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (h.get(mid)[0] <= id) lo = mid + 1; else hi = mid;
        }
        return h.get(lo - 1)[1];
    }
}""",
           """from bisect import bisect_right

class SnapshotArray:
    def __init__(self, length):
        self.history = [[(0, 0)] for _ in range(length)]                    # per index: (snap_id, value), ids increasing
        self.snap_id = 0

    def set(self, index, val):
        h = self.history[index]
        if h[-1][0] == self.snap_id:
            h[-1] = (self.snap_id, val)
        else:
            h.append((self.snap_id, val))

    def snap(self):
        self.snap_id += 1
        return self.snap_id - 1

    def get(self, index, snap_id):
        h = self.history[index]
        i = bisect_right(h, (snap_id, float('inf')))                        # first entry with id > snap_id
        return h[i - 1][1]""")],
    complexity="`set` / `snap` O(1), `get` O(log h) where h is the number of versions of that key.",
    traps=["Binary search for the **last** entry ≤ time: use the upper bound and step back; returning `lo` itself is off by one.", "Handle \"before the first entry\" (empty string / default).",
           "Writes must be in increasing time order for the lists to stay sorted; otherwise use an ordered map (topic 17).", "Snapshot `set` in the same snapshot should overwrite, not append."],
    variants=["Time-ordered writes with deletions: store tombstones.", "Stock price fluctuation: map time → price + ordered counts for max / min.", "Design a spreadsheet / database with transactions: stack of undo logs.", "Persistent data structures: share unchanged parts between versions."],
    notuse="Timestamps can arrive out of order (use a TreeMap) or only the latest value is ever needed (plain map).",
    problems=[
        (981, "Time Based Key-Value Store", "M", "time-based-key-value-store", "Per-key sorted history + upper bound binary search", "O(log n) get / O(n)"),
        (1146, "Snapshot Array", "M", "snapshot-array", "Per-index change log keyed by snapshot id", "O(log s) get / O(writes)"),
        (2034, "Stock Price Fluctuation", "M", "stock-price-fluctuation", "Map timestamp → price + ordered counts for max / min", "O(log n) / O(n)"),
        (1622, "Fancy Sequence", "H", "fancy-sequence", "Store values with lazy affine transforms (a, b) and modular inverses", "O(log MOD) / O(n)"),
    ]))

# ---------------------------------------------------------------- 6
P.append(dict(
    title="Feeds and leaderboards: heaps behind a design API", tier="hot", sim="twitter", oneline="k-way merge the newest items; keep only the top K",
    why="Social-feed and ranking questions are heap problems with an API on top", signature="LC 355 / 1244",
    when="The API asks for the most recent N items across many sources, or the top K scores of a changing table.",
    detect="\"design Twitter\" · \"news feed\" · \"leaderboard\" · \"top K\" · \"merge k sorted lists\" · \"most recent items from followees\".",
    intuition="Each user's tweets are already sorted by time, so building a feed is a **k-way merge** of the followees' lists. Put the newest tweet of each followee in a **max-heap** keyed by time; pop the newest, then push that user's next older tweet. You stop after 10 pops, so you never touch old tweets. A leaderboard keeps `id → score` in a map and answers `top(K)` with a **min-heap of size K** (or `nlargest`).",
    brute="Concatenating and sorting all tweets is O(T log T). The heap merge does O(k + 10 log k) work.",
    idea="`postTweet`: append `(clock++, id)` to the user's list. `follow` / `unfollow`: set operations. `getNewsFeed`: heap of `(−time, tweetId, user, index)` for the newest tweet of the user and each followee; pop up to 10, pushing the previous tweet of the popped user. Leaderboard: `addScore` = `scores[id] += s`; `top(K)` = sum of `K` largest values.",
    steps=["Store tweets per user with a global increasing clock.", "Build a heap with each source's newest item.", "Pop the best, push the same source's next item.", "Stop at the requested count."],
    trace_title="users A, B, C; 5 newest",
    trace="""heap: a3@9, b2@7, c2@8
pop a3 -> push a2@4;  pop c2 -> push c1@6;  pop b2 -> push b1@3
pop c1 -> push c0@2;  pop a2 -> push a1@1
feed [a3, c2, b2, c1, a2]""",
    code=[("Twitter: post, follow, unfollow and news feed",
           """class Twitter {
    private int clock = 0;
    private final Map<Integer, List<int[]>> tweets = new HashMap<>();          // user -> [time, tweetId], oldest first
    private final Map<Integer, Set<Integer>> following = new HashMap<>();
    void postTweet(int userId, int tweetId) {
        tweets.computeIfAbsent(userId, k -> new ArrayList<>()).add(new int[]{clock++, tweetId});
    }
    List<Integer> getNewsFeed(int userId) {
        Set<Integer> users = new HashSet<>(following.getOrDefault(userId, new HashSet<>()));
        users.add(userId);
        PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> b[0] - a[0]);   // newest first: {time, tweetId, user, index}
        for (int u : users) {
            List<int[]> list = tweets.get(u);
            if (list != null) {
                int i = list.size() - 1;
                pq.add(new int[]{list.get(i)[0], list.get(i)[1], u, i});
            }
        }
        List<Integer> feed = new ArrayList<>();
        while (!pq.isEmpty() && feed.size() < 10) {
            int[] top = pq.poll();
            feed.add(top[1]);
            if (top[3] > 0) {                                                   // push that user's next older tweet
                int i = top[3] - 1;
                int[] t = tweets.get(top[2]).get(i);
                pq.add(new int[]{t[0], t[1], top[2], i});
            }
        }
        return feed;
    }
    void follow(int followerId, int followeeId) {
        following.computeIfAbsent(followerId, k -> new HashSet<>()).add(followeeId);
    }
    void unfollow(int followerId, int followeeId) {
        if (following.containsKey(followerId)) following.get(followerId).remove(followeeId);
    }
}""",
           """import heapq
from collections import defaultdict

class Twitter:
    def __init__(self):
        self.clock = 0
        self.tweets = defaultdict(list)                                         # user -> (time, tweet_id), oldest first
        self.following = defaultdict(set)

    def post_tweet(self, user_id, tweet_id):
        self.tweets[user_id].append((self.clock, tweet_id))
        self.clock += 1

    def get_news_feed(self, user_id):
        heap = []                                                               # max-heap on time via negation
        for u in self.following[user_id] | {user_id}:
            if self.tweets[u]:
                i = len(self.tweets[u]) - 1
                t, tid = self.tweets[u][i]
                heap.append((-t, tid, u, i))
        heapq.heapify(heap)
        feed = []
        while heap and len(feed) < 10:
            _, tid, u, i = heapq.heappop(heap)
            feed.append(tid)
            if i > 0:                                                           # push that user's next older tweet
                t, tid2 = self.tweets[u][i - 1]
                heapq.heappush(heap, (-t, tid2, u, i - 1))
        return feed

    def follow(self, follower_id, followee_id):
        self.following[follower_id].add(followee_id)

    def unfollow(self, follower_id, followee_id):
        self.following[follower_id].discard(followee_id)"""),
          ("leaderboard (top K with a min-heap)",
           """class Leaderboard {
    private final Map<Integer, Integer> scores = new HashMap<>();
    void addScore(int playerId, int score) { scores.merge(playerId, score, Integer::sum); }
    int top(int k) {
        PriorityQueue<Integer> heap = new PriorityQueue<>();                // min-heap holding the K best so far
        for (int s : scores.values()) {
            heap.add(s);
            if (heap.size() > k) heap.poll();
        }
        int sum = 0;
        for (int s : heap) sum += s;
        return sum;
    }
    void reset(int playerId) { scores.put(playerId, 0); }
}""",
           """import heapq
from collections import defaultdict

class Leaderboard:
    def __init__(self):
        self.scores = defaultdict(int)

    def add_score(self, player_id, score):
        self.scores[player_id] += score

    def top(self, k):
        return sum(heapq.nlargest(k, self.scores.values()))                  # a min-heap of size k inside

    def reset(self, player_id):
        self.scores[player_id] = 0""")],
    complexity="Feed: O(k + 10 log k) per call; post O(1); top(K) O(n log K).",
    traps=["Include the user's **own** tweets in their feed.", "Use one global increasing clock, not the per-user count, so tweets from different users compare correctly.",
           "Heap entries must carry the source and index so you can push the next item.", "`unfollow` of a user you do not follow must not crash; a user cannot unfollow themselves (not stored)."],
    variants=["Merge k sorted lists / arrays: same heap shape (topic 10).", "Top K frequent: map + heap.", "Leaderboard with rank queries: balanced tree or a Fenwick tree over scores (topic 17).", "Pagination: store a cursor (time, id) per request."],
    notuse="Few sources: sorting a small merged list is simpler.",
    problems=[
        (355, "Design Twitter", "M", "design-twitter", "Per-user tweet lists + heap merge for the feed", "O(k + 10 log k) / O(T)"),
        (1845, "Seat Reservation Manager", "M", "seat-reservation-manager", "Min-heap of released seats plus a counter for the next fresh seat", "O(log n) per op / O(n)"),
        (23, "Merge k Sorted Lists", "H", "merge-k-sorted-lists", "Min-heap over the heads of the lists", "O(N log k) / O(k)"),
        (347, "Top K Frequent Elements", "M", "top-k-frequent-elements", "Count + heap (or bucket sort by frequency)", "O(n log k) / O(n)"),
    ]))

# ---------------------------------------------------------------- 7
P.append(dict(
    title="Frequency stack and bucketed structures", tier="sec", sim="fstack", oneline="one stack per frequency level; the highest non-empty level is the answer",
    why="A custom stack whose pop depends on counts, in O(1)", signature="LC 895 / 1396",
    when="The structure must pop or return the element that is the most (or least) of something, with ties broken by recency.",
    detect="\"maximum frequency stack\" · \"max stack\" · \"all O(1) data structure\" · \"design underground system\" · \"most frequent / most recent\".",
    intuition="If every element has a frequency and you want to pop the **most frequent, most recent**, keep a stack **per frequency level**. Pushing `x` for the f-th time puts `x` on the stack of level `f` (it also stays on the lower levels). The top of the highest non-empty level is exactly the element with the highest frequency, and within a level the stack order is recency. Popping removes it from the top level and lowers its frequency by one; if that level empties, decrement `maxFreq`.",
    brute="Scanning all elements for the highest frequency is O(n) per pop. Level stacks make push and pop O(1).",
    idea="`freq[x]` and `groups[f]` = stack of values that reached frequency `f`. `push(x)`: `f = ++freq[x]`, `maxFreq = max(maxFreq, f)`, `groups[f].push(x)`. `pop()`: `x = groups[maxFreq].pop()`, `freq[x]--`, if the group is empty `maxFreq--`. Aggregations like average travel time use a map key → (sum, count).",
    steps=["Keep a frequency map and a stack per frequency.", "Push: bump the frequency and add to the matching stack.", "Pop: take from the stack of the maximum frequency.", "Lower the frequency and the maximum if a level empties."],
    trace_title="push 5 7 5 7 4 5, then pop four times",
    trace="""levels: 1:[5,7,4]  2:[5,7]  3:[5]
pop -> 5 (level 3)   pop -> 7 (level 2)
pop -> 5 (level 2)   pop -> 4 (level 1)""",
    code=[("FreqStack",
           """class FreqStack {
    private final Map<Integer, Integer> freq = new HashMap<>();
    private final Map<Integer, Deque<Integer>> groups = new HashMap<>();      // frequency -> stack of values reaching it
    private int maxFreq = 0;
    void push(int x) {
        int f = freq.merge(x, 1, Integer::sum);
        maxFreq = Math.max(maxFreq, f);
        groups.computeIfAbsent(f, k -> new ArrayDeque<>()).push(x);
    }
    int pop() {
        int x = groups.get(maxFreq).pop();                                   // most frequent, most recent
        freq.merge(x, -1, Integer::sum);
        if (groups.get(maxFreq).isEmpty()) maxFreq--;
        return x;
    }
}""",
           """from collections import defaultdict

class FreqStack:
    def __init__(self):
        self.freq = defaultdict(int)
        self.groups = defaultdict(list)                                       # frequency -> stack of values reaching it
        self.max_freq = 0

    def push(self, x):
        self.freq[x] += 1
        f = self.freq[x]
        self.max_freq = max(self.max_freq, f)
        self.groups[f].append(x)

    def pop(self):
        x = self.groups[self.max_freq].pop()                                  # most frequent, most recent
        self.freq[x] -= 1
        if not self.groups[self.max_freq]:
            self.max_freq -= 1
        return x"""),
          ("underground system (map to running sum and count)",
           """class UndergroundSystem {
    private final Map<Integer, Object[]> inTrip = new HashMap<>();             // id -> {station, time}
    private final Map<String, long[]> stats = new HashMap<>();                 // "from>to" -> {total time, trips}
    void checkIn(int id, String station, int t) { inTrip.put(id, new Object[]{station, t}); }
    void checkOut(int id, String station, int t) {
        Object[] in = inTrip.remove(id);
        long[] s = stats.computeIfAbsent(in[0] + ">" + station, k -> new long[2]);
        s[0] += t - (int) in[1];
        s[1]++;
    }
    double getAverageTime(String from, String to) {
        long[] s = stats.get(from + ">" + to);
        return (double) s[0] / s[1];
    }
}""",
           """from collections import defaultdict

class UndergroundSystem:
    def __init__(self):
        self.in_trip = {}                                                      # id -> (station, time)
        self.stats = defaultdict(lambda: [0, 0])                               # (from, to) -> [total time, trips]

    def check_in(self, id, station, t):
        self.in_trip[id] = (station, t)

    def check_out(self, id, station, t):
        start, t0 = self.in_trip.pop(id)
        s = self.stats[(start, station)]
        s[0] += t - t0
        s[1] += 1

    def get_average_time(self, start, end):
        total, trips = self.stats[(start, end)]
        return total / trips""")],
    complexity="O(1) per operation, O(n) space.",
    traps=["An element stays on every lower level; popping from the top level must not remove it from the lower ones.", "Decrement `maxFreq` only when the **top** level empties.",
           "A lower-frequency element pushed later beats nothing: the highest level always wins.", "Averages: store sum and count, never the average itself."],
    variants=["Max stack: stack + max-heap with lazy deletion or two stacks.", "All O(1) data structure: doubly linked list of count buckets.", "Design hit counter with buckets: array indexed by `time % 300`.", "LRU-style \"most recently used\" stack."],
    notuse="You only need the maximum without ties (a heap is fine) or counts are small and pops are rare.",
    problems=[
        (895, "Maximum Frequency Stack", "H", "maximum-frequency-stack", "Stack per frequency + maxFreq", "O(1) per op / O(n)"),
        (1396, "Design Underground System", "M", "design-underground-system", "Map to (sum, count); check-ins in a map", "O(1) per op / O(n)"),
        (155, "Min Stack", "M", "min-stack", "Parallel stack of minimums", "O(1) per op / O(n)"),
        (225, "Implement Stack using Queues", "E", "implement-stack-using-queues", "Rotate the queue after each push", "O(n) push / O(n)"),
    ]))

# ---------------------------------------------------------------- 8
P.append(dict(
    title="Two stacks around a cursor: editors and history", tier="sec", sim="editor", oneline="characters before the cursor on one stack, after it on the other",
    why="Efficient local edits without shifting arrays", signature="LC 2296 / 1472",
    when="Edits and moves happen at a movable position (cursor, current page) and you need them fast.",
    detect="\"text editor\" · \"cursor left / right\" · \"browser history\" · \"undo / redo\" · \"design a document editor\".",
    intuition="Split the text at the cursor: everything **before** it on a left stack and everything **after** it on a right stack, with the character next to the cursor on top of each. Typing pushes onto the left stack, backspace pops it, and moving the cursor transfers characters from one stack to the other. Every operation touches only the characters involved, never the whole text. Browser history is the same picture with pages: back moves one entry from the \"past\" stack to the \"future\" stack, visiting a new page clears the future.",
    brute="A single array makes inserts and deletes in the middle O(n) because the tail shifts. Two stacks make them O(k) in the characters moved.",
    idea="`left` holds chars before the cursor, `right` holds chars after it in reverse. `addText`: append to `left`. `deleteText(k)`: pop up to `k` from `left`. `cursorLeft(k)`: move up to `k` chars from `left` to `right`; `cursorRight(k)` the opposite. Return the last 10 chars of `left`.",
    steps=["Keep `left` and `right` stacks.", "Insert → push on `left`; delete → pop from `left`.", "Move cursor → transfer between stacks.", "Report from the end of `left`."],
    trace_title="`abc`, `de`, cursorLeft 2, add `X`, delete 1, cursorRight 1",
    trace="""add abc, de     left "abcde"  right ""
cursorLeft 2    left "abc"    right "de"
add X           left "abcX"
delete 1        left "abc"
cursorRight 1   left "abcd"   right "e"  -> text "abcde", cursor after "abcd\"""",
    code=[("text editor with two stacks",
           """class TextEditor {
    private final StringBuilder left = new StringBuilder();                    // text before the cursor
    private final StringBuilder right = new StringBuilder();                   // text after the cursor, reversed (end = next char)
    void addText(String text) { left.append(text); }
    int deleteText(int k) {
        int d = Math.min(k, left.length());
        left.setLength(left.length() - d);                                     // backspace d characters
        return d;
    }
    String cursorLeft(int k) { move(k, left, right); return lastTen(); }
    String cursorRight(int k) { move(k, right, left); return lastTen(); }
    private void move(int k, StringBuilder from, StringBuilder to) {
        for (; k > 0 && from.length() > 0; k--) {
            to.append(from.charAt(from.length() - 1));
            from.setLength(from.length() - 1);
        }
    }
    private String lastTen() { return left.substring(Math.max(0, left.length() - 10)); }
}""",
           """class TextEditor:
    def __init__(self):
        self.left = []                                                          # text before the cursor
        self.right = []                                                         # text after the cursor, reversed (end = next char)

    def add_text(self, text):
        self.left.extend(text)

    def delete_text(self, k):
        d = min(k, len(self.left))
        del self.left[len(self.left) - d:]                                      # backspace d characters
        return d

    def cursor_left(self, k):
        for _ in range(min(k, len(self.left))):
            self.right.append(self.left.pop())
        return ''.join(self.left[-10:])

    def cursor_right(self, k):
        for _ in range(min(k, len(self.right))):
            self.left.append(self.right.pop())
        return ''.join(self.left[-10:])"""),
          ("browser history (array + pointer)",
           """class BrowserHistory {
    private final List<String> pages = new ArrayList<>();
    private int cur = 0;
    BrowserHistory(String homepage) { pages.add(homepage); }
    void visit(String url) {
        while (pages.size() > cur + 1) pages.remove(pages.size() - 1);          // visiting clears the forward history
        pages.add(url);
        cur++;
    }
    String back(int steps) { cur = Math.max(0, cur - steps); return pages.get(cur); }
    String forward(int steps) { cur = Math.min(pages.size() - 1, cur + steps); return pages.get(cur); }
}""",
           """class BrowserHistory:
    def __init__(self, homepage):
        self.pages = [homepage]
        self.cur = 0

    def visit(self, url):
        del self.pages[self.cur + 1:]                                            # visiting clears the forward history
        self.pages.append(url)
        self.cur += 1

    def back(self, steps):
        self.cur = max(0, self.cur - steps)
        return self.pages[self.cur]

    def forward(self, steps):
        self.cur = min(len(self.pages) - 1, self.cur + steps)
        return self.pages[self.cur]""")],
    complexity="O(k) per operation where k is the number of characters (pages) moved or changed.",
    traps=["The right stack is **reversed**: its last element is the character right after the cursor.", "Clamp moves and deletes to what is available.",
           "Browser history: a new visit must discard forward pages.", "Return only the last 10 characters before the cursor, not the whole text."],
    variants=["Undo / redo: two stacks of operations.", "Gap buffer: one array with a movable gap (what many real editors use).", "Rope / piece table for very large documents.", "Doubly linked list of pages with a current pointer."],
    notuse="Edits only at the end (a single stack or builder is enough) or the document is huge and edits are random (rope).",
    problems=[
        (1472, "Design Browser History", "M", "design-browser-history", "Array + pointer; visit truncates the forward part", "O(1) amortised / O(n)"),
        (2296, "Design a Text Editor", "H", "design-a-text-editor", "Two stacks around the cursor", "O(k) per op / O(n)"),
        (71, "Simplify Path", "M", "simplify-path", "Stack of directory names", "O(n) / O(n)"),
        (1670, "Design Front Middle Back Queue", "M", "design-front-middle-back-queue", "Two deques kept balanced around the middle", "O(1) per op / O(n)"),
    ]))

TOPIC = dict(
    id="design", file="18_design_problems.html", title="Design Problems — Caches, Iterators, Rate Limiters, Feeds and Editors",
    lead="Design questions ask you to build a small class with an API and strict time limits per operation. The skill is choosing the right combination of basic structures: a hash map for lookup plus an ordered structure for policy, a stack for local state, a heap for \"top\" queries, a sorted list for history. This guide covers the eight designs that appear most in interviews: LRU / LFU, O(1) random sets, iterators, rate limiters, time-based stores, feeds and leaderboards, frequency stacks and text editors.",
    mindset="Write down the API first, then the **required complexity of each method**. Every method that must be O(1) needs direct access (a map or an array); every method that needs order needs a list, heap or sorted structure; and the two have to be kept **consistent** on every update. Walk through one operation sequence by hand before coding.",
    qintro="Ask these questions before writing code:",
    questions=["**What is the API and the required complexity of each method?**", "**What must be looked up by key?** → hash map.", "**What needs an order** (recency, frequency, time)? → linked list, bucket stacks, heap or sorted list.",
               "**Which updates must keep two structures in sync?** (map and list, index map and array)", "**What are the edge cases?** (capacity 0, empty structure, duplicate keys, updating an existing key, removing the last element)"],
    cues=[
        ["evict least recently / frequently used", "**P1** LRU / LFU"],
        ["insert, delete, random in O(1)", "**P2** Array + map"],
        ["hasNext / next over nested or tree data", "**P3** Iterator with a stack"],
        ["at most N requests per window", "**P4** Rate limiter"],
        ["value as of a time or snapshot", "**P5** History + binary search"],
        ["recent items from many sources, top K", "**P6** Heap-based feed"],
        ["pop most frequent, ties by recency", "**P7** Frequency stack"],
        ["edits around a movable cursor", "**P8** Two stacks"],
    ],
    choose=[
        ["Eviction policy", "Map + ordered list / buckets (P1)"],
        ["Random + delete", "Array + index map (P2)"],
        ["Lazy traversal", "Explicit stack (P3)"],
        ["Throttle", "Timestamp queue or token bucket (P4)"],
        ["Versions", "Sorted history + bisect (P5)"],
        ["Top K / merge", "Heap (P6)"],
        ["Count-based pop", "Stack per level (P7)"],
        ["Cursor", "Two stacks (P8)"],
    ],
    rule="**map for lookup, ordered structure for policy, keep both in sync.** Check the O(1) claim for every method, and test an empty structure, a full structure and an update of an existing key.",
    selftest=[
        ("What two structures give O(1) get and put for an LRU cache?", "A hash map from key to node plus a doubly linked list ordered by recency (or `LinkedHashMap` / `OrderedDict`): a use unlinks and moves the node to the front, eviction drops the tail."),
        ("How does an LFU cache pick its victim in O(1)?", "It keeps an insertion-ordered bucket of keys per frequency and a `minFreq` pointer; the victim is the oldest key in bucket `minFreq`."),
        ("Why does RandomizedSet delete by swapping with the last element?", "Deleting from the middle of an array shifts everything (O(n)); overwriting the hole with the last element and popping the end is O(1), and order does not matter for random picks."),
        ("Why must a nested-list iterator avoid flattening in the constructor?", "Iterators should be lazy: flattening costs O(n) time and memory up front and cannot handle huge or infinite data; a stack makes each call O(1) amortised."),
        ("How does a token bucket differ from a sliding-window log?", "The bucket stores only a token count and last time (O(1) memory) and allows bursts; the log stores every recent timestamp (exact but O(limit) memory)."),
        ("How do you answer \"value at time t\" in a time-based store?", "Keep each key's history sorted by time and binary search for the last entry with timestamp ≤ t (upper bound, then step back one)."),
        ("Why use a heap for a news feed?", "Each followee's tweets are already sorted, so the feed is a k-way merge: pop the newest from a heap of the newest tweet per source and push the next older one; only 10 pops are needed."),
        ("What data layout makes cursor-based text editing efficient?", "Two stacks: characters before the cursor and characters after it (reversed); typing, deleting and moving only touch the characters involved."),
    ],
    plan=[
        "**Day 1:** LRU cache (linked list version) and LFU cache; explain the O(1) bookkeeping out loud.",
        "**Day 2:** RandomizedSet (and duplicates), random pick with weight.",
        "**Day 3:** iterators (BST iterator, nested list iterator, peeking iterator).",
        "**Day 4:** rate limiter variants and the time-based key-value store / snapshot array.",
        "**Day 5:** Design Twitter, leaderboard, frequency stack.",
        "**Day 6:** text editor and browser history; then re-implement two designs from scratch without looking.",
    ],
    patterns=P,
)
