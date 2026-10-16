"""Content for topic 05: Stacks, queues and deques."""

P = []

# ---------------------------------------------------------------- 1
P.append(dict(
    title="Stack basics: undo, matching and bookkeeping", tier="hot", sim="minstack", oneline="last in, first out: remember what to come back to",
    why="Stacks model \"most recent unfinished thing\" and appear everywhere", signature="LC 20 / 155",
    when="You must process things in reverse order of arrival, undo, match openers with closers, or keep extra info alongside each item.",
    detect="\"valid parentheses\" · \"undo / backspace\" · \"evaluate postfix\" · \"min / max in O(1)\" · \"validate a push-pop sequence\".",
    intuition="A stack of plates: you can only touch the top one. That is exactly what you need when the **most recent** unfinished item must be resolved first: the innermost open bracket, the last typed character, the latest operand. If each plate also carries a sticky note (for example the minimum so far), you get extra facts for free.",
    brute="Scanning the whole collection each time you need the minimum is O(n). Storing the running minimum with each entry makes `getMin` O(1) with O(n) space.",
    idea="Push when you start something; pop when you finish or cancel it. Store **pairs** `(value, extra)` so every entry carries the aggregate (min, max, count, previous state) that popping must restore.",
    steps=["Decide what you push: a value, an index, or a `(value, aggregate)` pair.", "Decide when you pop: on a closer, on a backspace, on an operator.", "On pop, use the popped item to update the answer.", "At the end, the stack must be empty (balanced) or hold the unresolved items."],
    trace_title="Min Stack: push 5, 3, 7, 3 then pop twice",
    trace="""push 5   stack [5]          mins [5]
push 3   stack [5,3]        mins [5,3]
push 7   stack [5,3,7]      mins [5,3,3]
push 3   stack [5,3,7,3]    mins [5,3,3,3]    getMin = 3
pop      stack [5,3,7]      mins [5,3,3]      getMin = 3
pop      stack [5,3]        mins [5,3]        getMin = 3""",
    code=[("min stack: each entry stores the min so far",
           """class MinStack {
    Deque<int[]> st = new ArrayDeque<>();                 // {value, minSoFar}
    void push(int x) { int m = st.isEmpty() ? x : Math.min(x, st.peek()[1]); st.push(new int[]{x, m}); }
    void pop() { st.pop(); }
    int top() { return st.peek()[0]; }
    int getMin() { return st.peek()[1]; }
}""",
           """class MinStack:
    def __init__(self):
        self.s = []                                       # (value, min_so_far)
    def push(self, x):
        m = min(x, self.s[-1][1]) if self.s else x
        self.s.append((x, m))
    def pop(self):
        self.s.pop()
    def top(self):
        return self.s[-1][0]
    def get_min(self):
        return self.s[-1][1]"""),
          ("evaluate reverse Polish notation",
           """Deque<Integer> st = new ArrayDeque<>();
for (String t : tokens) {
    switch (t) {
        case "+": st.push(st.pop() + st.pop()); break;
        case "*": st.push(st.pop() * st.pop()); break;
        case "-": { int b = st.pop(), a = st.pop(); st.push(a - b); break; }   // order matters
        case "/": { int b = st.pop(), a = st.pop(); st.push(a / b); break; }   // truncates toward zero
        default: st.push(Integer.parseInt(t));
    }
}
return st.pop();""",
           """st = []
for t in tokens:
    if t in "+-*/" and len(t) == 1:
        b, a = st.pop(), st.pop()                      # b is the right operand
        st.append(a + b if t == '+' else a - b if t == '-' else a * b if t == '*' else int(a / b))
    else:
        st.append(int(t))
return st.pop()""")],
    complexity="O(1) per push/pop, O(n) space.",
    traps=["Pop the **right operand first**: `b = pop(); a = pop(); a − b`.", "Division truncates toward zero: use `int(a / b)` in Python, not `//`.",
           "Check the stack is non-empty before `pop` / `peek` (use `isEmpty` or a guard).", "Java: prefer `ArrayDeque` over the legacy synchronised `Stack` class."],
    variants=["Backspace string compare: process each string with a stack (or two pointers from the end for O(1) space).", "Max stack with `popMax`: add a second structure.", "Validate stack sequences: simulate pushes and greedily pop when the top matches the next popped value."],
    notuse="When you need random access in the middle, or both ends (use a deque).",
    problems=[
        (20, "Valid Parentheses", "E", "valid-parentheses", "Push openers; each closer must match the top", "O(n) / O(n)"),
        (844, "Backspace String Compare", "E", "backspace-string-compare", "Stack per string where # pops; compare the results", "O(n) / O(n)"),
        (155, "Min Stack", "M", "min-stack", "Store (value, minSoFar) per entry", "O(1) per op / O(n)"),
        (150, "Evaluate Reverse Polish Notation", "M", "evaluate-reverse-polish-notation", "Push numbers; operators pop two operands", "O(n) / O(n)"),
        (946, "Validate Stack Sequences", "M", "validate-stack-sequences", "Simulate: push, then pop while top equals the next popped", "O(n) / O(n)"),
        (71, "Simplify Path", "M", "simplify-path", "Split on '/', push names, pop on '..'", "O(n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 2
P.append(dict(
    title="Monotonic stack: next greater / smaller element", tier="hot", sim="nge", oneline="keep a stack sorted; a bigger arrival resolves smaller waiting items",
    why="Turns \"for each element find the next bigger/smaller\" from O(n²) to O(n)", signature="LC 739 / 496",
    when="For every element you need the nearest element to the left or right that is greater (or smaller).",
    detect="\"next greater element\" · \"days until a warmer temperature\" · \"stock span\" · \"previous smaller\" · \"final price with a discount\".",
    intuition="People queueing in a ticket line, each waiting to see someone taller than themselves. When a taller person arrives, every shorter waiting person behind them finally gets their answer and leaves the line. People still in line are waiting; and because anyone shorter than a taller newcomer was just resolved, the people still waiting are always in decreasing height order: a monotonic stack.",
    brute="For each element scan right until something bigger appears: O(n²). With a monotonic stack each index is pushed once and popped once: O(n).",
    idea="Keep a stack of **indices** whose answers are still unknown, with values in decreasing order (for next greater). For each new element, while it is greater than the value at the stack top, pop and record the answer for the popped index; then push the new index.",
    steps=["Empty stack of indices; answers default to 0 / −1.", "For each `i`: `while stack and a[i] > a[stack.top]`: pop `j`, set `ans[j] = i − j` (or `a[i]`).", "Push `i`.", "Indices left at the end have no next greater element."],
    trace_title="temperatures `[73,74,75,71,69,72,76,73]`",
    trace="""i=0 73 push 0                     stack [0]
i=1 74 > 73 pop 0 -> ans[0]=1     stack [1]
i=2 75 > 74 pop 1 -> ans[1]=1     stack [2]
i=3 71 push                       stack [2,3]
i=4 69 push                       stack [2,3,4]
i=5 72 pops 4 (ans 1), 3 (ans 2)  stack [2,5]
i=6 76 pops 5 (ans 1), 2 (ans 4)  stack [6]
i=7 73 push                       stack [6,7]
=> [1,1,4,2,1,1,0,0]""",
    code=[("next greater element: days until warmer",
           """int[] ans = new int[n];
Deque<Integer> st = new ArrayDeque<>();                 // indices, values decreasing
for (int i = 0; i < n; i++) {
    while (!st.isEmpty() && t[i] > t[st.peek()]) {
        int j = st.pop();
        ans[j] = i - j;
    }
    st.push(i);
}
return ans;""",
           """ans = [0] * len(t)
st = []                                                  # indices, values decreasing
for i, x in enumerate(t):
    while st and x > t[st[-1]]:
        j = st.pop()
        ans[j] = i - j
    st.append(i)
return ans"""),
          ("circular array: loop twice over the indices",
           """int[] res = new int[n];
Arrays.fill(res, -1);
Deque<Integer> st = new ArrayDeque<>();
for (int i = 0; i < 2 * n; i++) {
    int idx = i % n;
    while (!st.isEmpty() && a[st.peek()] < a[idx]) res[st.pop()] = a[idx];
    if (i < n) st.push(idx);                              // only push during the first lap
}""",
           """res = [-1] * n
st = []
for i in range(2 * n):
    idx = i % n
    while st and a[st[-1]] < a[idx]:
        res[st.pop()] = a[idx]
    if i < n:
        st.append(idx)                                    # only push during the first lap""")],
    complexity="O(n) time (each index pushed and popped once), O(n) space.",
    traps=["Store **indices**, not values, when you need distances or positions.", "Strict vs non-strict comparison decides how ties behave: `>` finds strictly greater.",
           "Direction: scan right-to-left to build \"next greater\" with the stack holding candidates, or left-to-right and resolve on arrival (shown here).", "Circular arrays: iterate `2n` times with `i % n` and push only during the first lap."],
    variants=["Previous greater / smaller: scan left to right and read the stack top before pushing.", "Online stock span: stack of `(price, span)` pairs.", "132 pattern: monotonic stack plus a tracked \"third\" value."],
    notuse="When you need the k-th greater element or a range query (use a heap, sparse table or segment tree).",
    problems=[
        (496, "Next Greater Element I", "E", "next-greater-element-i", "Monotonic stack over nums2, map value → next greater", "O(n + m) / O(n)"),
        (1475, "Final Prices With a Special Discount in a Shop", "E", "final-prices-with-a-special-discount-in-a-shop", "Next smaller-or-equal price via a monotonic stack", "O(n) / O(n)"),
        (739, "Daily Temperatures", "M", "daily-temperatures", "Pop indices when a warmer day arrives; answer = i − j", "O(n) / O(n)"),
        (503, "Next Greater Element II", "M", "next-greater-element-ii", "Circular: iterate 2n with i % n", "O(n) / O(n)"),
        (901, "Online Stock Span", "M", "online-stock-span", "Stack of (price, span); merge spans of smaller prices", "O(1) amortised / O(n)"),
        (456, "132 Pattern", "M", "132-pattern", "Scan right to left, stack plus the best 'third' value", "O(n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 3
P.append(dict(
    title="Monotonic stack for ranges: rectangles and contributions", tier="hot", sim="hist", oneline="a popped bar's reach is bounded by its neighbours on the stack",
    why="Unlocks the hardest stack problems: histogram, maximal rectangle, subarray minimums", signature="LC 84 / 907",
    when="Each element is the minimum (or maximum) of some range and you need that range's width.",
    detect="\"largest rectangle in a histogram\" · \"sum of subarray minimums\" · \"maximal rectangle\" · \"trapping rain water\" · \"maximum subarray min-product\".",
    intuition="Each bar wants to stretch left and right as far as it can before hitting a shorter bar. A stack of increasing heights tells you both walls at the moment a bar is popped: the new top of the stack is its left wall (the previous shorter bar) and the arriving bar is its right wall (the next shorter bar).",
    brute="For each bar expand left and right until a shorter bar: O(n²). The stack finds both boundaries for every bar in one pass: O(n).",
    idea="Keep indices with increasing heights. When bar `i` is shorter than the top, pop `top`: its height is `a[top]`, its width is `i − newTop − 1` (or `i` if the stack is empty). Append a sentinel `0` to flush everything.",
    steps=["Stack of indices with increasing heights; add a `0` sentinel at the end.", "While `a[i] < a[stack.top]`: pop `top`; `left = stack.top` or `−1` if empty.", "Width = `i − left − 1`; area = `a[top] × width`; update the best.", "Push `i`."],
    trace_title="heights `[2,1,5,6,2,3]`",
    trace="""push 0(2); i=1 h=1 < 2 pop 0: width 1 -> area 2
push 1(1); push 2(5); push 3(6)
i=4 h=2 < 6 pop 3: width 1 -> 6
        < 5 pop 2: width 2 -> 10   best
push 4(2); push 5(3)
sentinel 0: pop 5 area 3, pop 4 area 8, pop 1 area 6
=> 10""",
    code=[("largest rectangle in a histogram",
           """int best = 0;
Deque<Integer> st = new ArrayDeque<>();                        // indices, heights increasing
for (int i = 0; i <= n; i++) {
    int h = (i == n) ? 0 : heights[i];                         // sentinel flushes the stack
    while (!st.isEmpty() && h < heights[st.peek()]) {
        int height = heights[st.pop()];
        int left = st.isEmpty() ? -1 : st.peek();
        best = Math.max(best, height * (i - left - 1));
    }
    st.push(i);
}
return best;""",
           """best = 0
st = []                                                        # indices, heights increasing
for i, h in enumerate(heights + [0]):                          # sentinel flushes the stack
    while st and h < heights[st[-1]]:
        height = heights[st.pop()]
        left = st[-1] if st else -1
        best = max(best, height * (i - left - 1))
    st.append(i)
return best"""),
          ("sum of subarray minimums (contribution of each element)",
           """int[] left = new int[n], right = new int[n];
Deque<Integer> st = new ArrayDeque<>();
for (int i = 0; i < n; i++) {                                  // distance to previous STRICTLY smaller
    while (!st.isEmpty() && a[st.peek()] >= a[i]) st.pop();
    left[i] = st.isEmpty() ? i + 1 : i - st.peek();
    st.push(i);
}
st.clear();
for (int i = n - 1; i >= 0; i--) {                             // distance to next smaller-or-equal
    while (!st.isEmpty() && a[st.peek()] > a[i]) st.pop();
    right[i] = st.isEmpty() ? n - i : st.peek() - i;
    st.push(i);
}
long sum = 0;
for (int i = 0; i < n; i++) sum = (sum + (long) a[i] * left[i] * right[i]) % 1_000_000_007L;""",
           """n = len(a)
left, right, st = [0] * n, [0] * n, []
for i in range(n):                                             # distance to previous STRICTLY smaller
    while st and a[st[-1]] >= a[i]:
        st.pop()
    left[i] = i + 1 if not st else i - st[-1]
    st.append(i)
st = []
for i in range(n - 1, -1, -1):                                 # distance to next smaller-or-equal
    while st and a[st[-1]] > a[i]:
        st.pop()
    right[i] = n - i if not st else st[-1] - i
    st.append(i)
total = sum(a[i] * left[i] * right[i] for i in range(n)) % (10**9 + 7)""")],
    complexity="O(n) time, O(n) space.",
    traps=["Without the `0` sentinel, bars left on the stack are never evaluated.", "Width when the stack is empty is `i` (the bar extends to the very left), i.e. `i − (−1) − 1`.",
           "Tie-breaking for contribution counting: make one side strict and the other non-strict so each subarray is counted exactly once.", "Maximal Rectangle: run the histogram algorithm on each row, building heights row by row."],
    variants=["Maximal rectangle of 1s: histogram per row.", "Trapping rain water: stack of bars; each pop closes a basin whose depth is `min(left, right) − popped`.", "Maximum subarray min-product: prefix sums plus boundaries from this pattern."],
    notuse="When elements are processed one by one with removals from the middle (use a heap with lazy deletion or a tree).",
    problems=[
        (907, "Sum of Subarray Minimums", "M", "sum-of-subarray-minimums", "Each element's left × right reach × value", "O(n) / O(n)"),
        (1856, "Maximum Subarray Min-Product", "M", "maximum-subarray-min-product", "For each element as the min: prefix sum over its reach", "O(n) / O(n)"),
        (84, "Largest Rectangle in Histogram", "H", "largest-rectangle-in-histogram", "Pop taller bars; width from the new top to the arrival", "O(n) / O(n)"),
        (42, "Trapping Rain Water", "H", "trapping-rain-water", "Stack of decreasing bars; each pop fills a basin", "O(n) / O(n)"),
        (85, "Maximal Rectangle", "H", "maximal-rectangle", "Histogram of consecutive 1s per row, largest rectangle each time", "O(m·n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 4
P.append(dict(
    title="Queues, and stacks and queues from each other", tier="sec", sim="twostack", oneline="two stacks make a queue; each item moves at most once",
    why="Classic design question that tests amortised thinking", signature="LC 232 / 225",
    when="You must implement one structure with another, or process items in arrival order (FIFO).",
    detect="\"implement queue using stacks\" · \"implement stack using queues\" · \"number of recent calls\" · \"first in, first out\".",
    intuition="A stack reverses order; a second stack reverses it **again**, restoring the original order. Pour a full stack into an empty one and the oldest item ends up on top. Pour only when the second stack is empty, and each item is poured at most once: every dequeue is cheap on average.",
    brute="Move all elements to the other stack on every dequeue: O(n) each. Moving only when the out-stack is empty makes each element move once: O(1) amortised.",
    idea="`in` receives pushes; `out` serves pops and peeks. If `out` is empty, pour `in` into it. A stack from one queue: after pushing, rotate the earlier elements behind the new one.",
    steps=["`push(x)`: push onto `in`.", "`pop()` / `peek()`: if `out` is empty, pop everything from `in` onto `out`; then pop/peek `out`.", "`empty()`: both stacks empty.", "Stack from a queue: `q.add(x)`, then rotate `size − 1` elements to the back."],
    trace_title="enqueue 1,2,3 then dequeue",
    trace="""enqueue 1,2,3          in [1,2,3]  out []
dequeue: out empty -> pour  in []  out [3,2,1]  pop -> 1
enqueue 4              in [4]      out [3,2]
dequeue                out [3] -> 2
dequeue                out [] -> 3   (in untouched)
dequeue: pour [4] -> out [4] -> 4""",
    code=[("queue using two stacks",
           """class MyQueue {
    Deque<Integer> in = new ArrayDeque<>(), out = new ArrayDeque<>();
    void push(int x) { in.push(x); }
    int pop()  { shift(); return out.pop(); }
    int peek() { shift(); return out.peek(); }
    boolean empty() { return in.isEmpty() && out.isEmpty(); }
    private void shift() { if (out.isEmpty()) while (!in.isEmpty()) out.push(in.pop()); }
}""",
           """class MyQueue:
    def __init__(self):
        self.inn, self.out = [], []
    def push(self, x):
        self.inn.append(x)
    def _shift(self):
        if not self.out:
            while self.inn:
                self.out.append(self.inn.pop())
    def pop(self):
        self._shift()
        return self.out.pop()
    def peek(self):
        self._shift()
        return self.out[-1]
    def empty(self):
        return not self.inn and not self.out"""),
          ("stack using one queue (rotate after each push)",
           """Queue<Integer> q = new LinkedList<>();
void push(int x) {
    q.add(x);
    for (int i = 0; i < q.size() - 1; i++) q.add(q.poll());   // new element to the front
}
int pop() { return q.poll(); }
int top() { return q.peek(); }""",
           """from collections import deque
q = deque()
def push(x):
    q.append(x)
    for _ in range(len(q) - 1):
        q.append(q.popleft())                                  # new element to the front
def pop():
    return q.popleft()
def top():
    return q[0]""")],
    complexity="Queue from stacks: O(1) amortised per operation. Stack from one queue: O(n) push, O(1) pop.",
    traps=["Only pour when `out` is **empty**; pouring earlier breaks the order.", "`peek` must also pour, like `pop`.",
           "Java: use `ArrayDeque`, not `Stack`, and `offer/poll/peek` for queues.", "Python lists make `pop(0)` O(n): use `collections.deque` as a queue."],
    variants=["Number of recent calls: a queue where old timestamps are popped from the front.", "Moving average from a data stream: queue plus running sum.", "Circular queue (pattern 9) for fixed capacity."],
    notuse="When you simply need a queue and your language has one (`ArrayDeque`, `deque`).",
    problems=[
        (232, "Implement Queue using Stacks", "E", "implement-queue-using-stacks", "In/out stacks; pour only when out is empty", "O(1) amortised / O(n)"),
        (225, "Implement Stack using Queues", "E", "implement-stack-using-queues", "Rotate the queue after each push", "O(n) push / O(n)"),
        (933, "Number of Recent Calls", "E", "number-of-recent-calls", "Queue of timestamps; pop those older than t − 3000", "O(1) amortised / O(n)"),
        (1700, "Number of Students Unable to Eat Lunch", "E", "number-of-students-unable-to-eat-lunch", "Count preferences; stop when the top sandwich has no taker", "O(n) / O(1)"),
        (2073, "Time Needed to Buy Tickets", "E", "time-needed-to-buy-tickets", "Queue simulation, or sum of min(tickets[i], tickets[k]) with order tweak", "O(n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 5
P.append(dict(
    title="BFS with a queue: levels and shortest paths", tier="hot", sim="bfs", oneline="a queue explores in rings of equal distance",
    why="The default tool for shortest path on unweighted graphs, grids and trees", signature="LC 102 / 994 / 127",
    when="Fewest steps in an unweighted graph or grid, level-by-level processing, or spreading from one or many sources.",
    detect="\"minimum number of steps / moves / mutations\" · \"level order\" · \"shortest path in a grid\" · \"rotting oranges\" · \"word ladder\".",
    intuition="Drop a stone in a pond: ripples spread outward one ring at a time. A queue gives the same behaviour: everything at distance 1 is enqueued before anything at distance 2, so the first time you reach a node is by the shortest path.",
    brute="Trying all paths with DFS is exponential. BFS visits each node and edge once: O(V + E), and the first arrival is guaranteed shortest.",
    idea="Enqueue the start (mark seen). Repeatedly dequeue a node, enqueue its unseen neighbours with `dist + 1`. For levels, process exactly `size` nodes per round. For many sources (rotting oranges), enqueue them all first.",
    steps=["`queue = [start]`, `seen = {start}`.", "Round-by-round: `size = queue.size()`; process `size` nodes, enqueue unseen neighbours, mark them seen **when enqueued**.", "Increase `steps` after each round.", "Return the step count when the goal is dequeued; −1 if the queue empties."],
    trace_title="shortest distance from 0 in the graph 0→1,2  1→3  2→3,4  3→5  4→5  5→6",
    trace="""queue [0]            dist 0
pop 0 -> add 1,2     dist 1
pop 1 -> add 3       dist 2
pop 2 -> add 4 (3 already seen)
pop 3 -> add 5       dist 3
pop 4 -> 5 already seen
pop 5 -> add 6       dist 4
=> shortest 0..6 = 4 edges""",
    code=[("BFS template on a grid (shortest steps)",
           """int[][] DIRS = {{1,0},{-1,0},{0,1},{0,-1}};
Queue<int[]> q = new ArrayDeque<>();
boolean[][] seen = new boolean[m][n];
q.add(new int[]{sr, sc}); seen[sr][sc] = true;
int steps = 0;
while (!q.isEmpty()) {
    for (int s = q.size(); s > 0; s--) {                  // one full level
        int[] cur = q.poll();
        if (cur[0] == tr && cur[1] == tc) return steps;
        for (int[] d : DIRS) {
            int r = cur[0] + d[0], c = cur[1] + d[1];
            if (r >= 0 && r < m && c >= 0 && c < n && !seen[r][c] && grid[r][c] == 0) {
                seen[r][c] = true;                         // mark when enqueued
                q.add(new int[]{r, c});
            }
        }
    }
    steps++;
}
return -1;""",
           """from collections import deque
q = deque([(sr, sc)])
seen = {(sr, sc)}
steps = 0
while q:
    for _ in range(len(q)):                                # one full level
        r, c = q.popleft()
        if (r, c) == (tr, tc):
            return steps
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and (nr, nc) not in seen and grid[nr][nc] == 0:
                seen.add((nr, nc))                         # mark when enqueued
                q.append((nr, nc))
    steps += 1
return -1"""),
          ("multi-source BFS (rotting oranges)",
           """int fresh = 0;
Queue<int[]> q = new ArrayDeque<>();
for (int r = 0; r < m; r++) for (int c = 0; c < n; c++) {
    if (g[r][c] == 2) q.add(new int[]{r, c});            // ALL sources start in the queue
    else if (g[r][c] == 1) fresh++;
}
int minutes = 0;
while (!q.isEmpty() && fresh > 0) {
    minutes++;
    for (int s = q.size(); s > 0; s--) {
        int[] p = q.poll();
        for (int[] d : new int[][]{{1,0},{-1,0},{0,1},{0,-1}}) {
            int r = p[0] + d[0], c = p[1] + d[1];
            if (r >= 0 && r < m && c >= 0 && c < n && g[r][c] == 1) { g[r][c] = 2; fresh--; q.add(new int[]{r, c}); }
        }
    }
}
return fresh == 0 ? minutes : -1;""",
           """fresh, q = 0, deque()
for r in range(m):
    for c in range(n):
        if g[r][c] == 2:
            q.append((r, c))                                # ALL sources start in the queue
        elif g[r][c] == 1:
            fresh += 1
minutes = 0
while q and fresh:
    minutes += 1
    for _ in range(len(q)):
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and g[nr][nc] == 1:
                g[nr][nc] = 2
                fresh -= 1
                q.append((nr, nc))
return minutes if fresh == 0 else -1""")],
    complexity="O(V + E) time (grid: O(m·n)), O(V) space.",
    traps=["Mark nodes **seen when you enqueue** them, not when you dequeue, or the same node enters the queue many times.", "Use `size = q.size()` captured **before** the inner loop to separate levels.",
           "Weighted edges break BFS: use Dijkstra (0/1 weights: 0-1 BFS with a deque).", "For word ladder, generate neighbours by changing one letter at a time and use a set of unseen words."],
    variants=["Bidirectional BFS: search from both ends for large branching factors.", "0-1 BFS: deque where 0-weight edges push front and 1-weight edges push back.", "Level order on trees: same loop without a seen set."],
    notuse="Weighted shortest paths (Dijkstra), or when you must enumerate every path (DFS / backtracking).",
    problems=[
        (102, "Binary Tree Level Order Traversal", "M", "binary-tree-level-order-traversal", "Process exactly queue.size() nodes per level", "O(n) / O(n)"),
        (994, "Rotting Oranges", "M", "rotting-oranges", "Multi-source BFS, one minute per level", "O(m·n) / O(m·n)"),
        (1091, "Shortest Path in Binary Matrix", "M", "shortest-path-in-binary-matrix", "BFS with 8 directions", "O(n²) / O(n²)"),
        (542, "01 Matrix", "M", "01-matrix", "Multi-source BFS from every 0", "O(m·n) / O(m·n)"),
        (752, "Open the Lock", "M", "open-the-lock", "BFS over 4-digit states, skip deadends", "O(10⁴) / O(10⁴)"),
        (127, "Word Ladder", "H", "word-ladder", "BFS changing one letter at a time", "O(N·L²) / O(N·L)"),
    ]))

# ---------------------------------------------------------------- 6
P.append(dict(
    title="Monotonic deque: sliding-window extremes", tier="hot", sim="dequemax", oneline="a deque of candidates, best at the front",
    why="Gives O(n) window max/min, where a heap would be O(n log n)", signature="LC 239 / 1438",
    when="Maximum or minimum of every window, or a window constrained by max − min.",
    detect="\"sliding window maximum\" · \"longest subarray with |max − min| ≤ limit\" · \"shortest subarray with sum ≥ K\" · DP where `dp[i]` depends on the best of the last k values.",
    intuition="Imagine a queue of candidates for \"tallest person in the window\". When a new tall person arrives, everyone shorter standing behind them can **never** be the tallest again (the newcomer is both taller and stays longer). So kick them out from the back. And people who walk out of the window leave from the front. The front is always the champion.",
    brute="Scan each window for its maximum: O(n·k). A heap gives O(n log n). The monotonic deque gives O(n) because each index enters and leaves once.",
    idea="Deque of indices with **decreasing** values (for max). For each `i`: pop front if it left the window; pop back while `a[back] ≤ a[i]`; push `i`; the front is the window maximum.",
    steps=["Pop the front if `front ≤ i − k`.", "Pop from the back while `a[back] ≤ a[i]`.", "Push `i` at the back.", "If `i ≥ k − 1`, record `a[front]`."],
    trace_title="`[1,3,-1,-3,5,3,6,7]`, k = 3",
    trace="""i=0  dq [0]
i=1  3 beats 1 -> pop 0     dq [1]
i=2  push                   dq [1,2]          max 3
i=3  push                   dq [1,2,3]        max 3
i=4  5 beats all; front 1 left window -> dq [4]   max 5
i=5  push                   dq [4,5]          max 5
i=6  6 beats 3, 5           dq [6]            max 6
i=7  7 beats 6              dq [7]            max 7
=> [3,3,5,5,6,7]""",
    code=[("sliding window maximum",
           """Deque<Integer> dq = new ArrayDeque<>();                     // indices, values decreasing
int[] res = new int[n - k + 1];
for (int i = 0; i < n; i++) {
    if (!dq.isEmpty() && dq.peekFirst() <= i - k) dq.pollFirst();   // left the window
    while (!dq.isEmpty() && a[dq.peekLast()] <= a[i]) dq.pollLast();  // can never be max again
    dq.offerLast(i);
    if (i >= k - 1) res[i - k + 1] = a[dq.peekFirst()];
}
return res;""",
           """from collections import deque
dq, res = deque(), []                                      # indices, values decreasing
for i, x in enumerate(a):
    if dq and dq[0] <= i - k:
        dq.popleft()                                       # left the window
    while dq and a[dq[-1]] <= x:
        dq.pop()                                           # can never be max again
    dq.append(i)
    if i >= k - 1:
        res.append(a[dq[0]])
return res"""),
          ("longest subarray with max − min ≤ limit (two deques)",
           """Deque<Integer> mx = new ArrayDeque<>(), mn = new ArrayDeque<>();
int l = 0, best = 0;
for (int r = 0; r < n; r++) {
    while (!mx.isEmpty() && mx.peekLast() < a[r]) mx.pollLast();
    mx.offerLast(a[r]);
    while (!mn.isEmpty() && mn.peekLast() > a[r]) mn.pollLast();
    mn.offerLast(a[r]);
    while (mx.peekFirst() - mn.peekFirst() > limit) {          // shrink until valid
        if (mx.peekFirst() == a[l]) mx.pollFirst();
        if (mn.peekFirst() == a[l]) mn.pollFirst();
        l++;
    }
    best = Math.max(best, r - l + 1);
}""",
           """mx, mn = deque(), deque()
l = best = 0
for r, x in enumerate(a):
    while mx and mx[-1] < x:
        mx.pop()
    mx.append(x)
    while mn and mn[-1] > x:
        mn.pop()
    mn.append(x)
    while mx[0] - mn[0] > limit:                           # shrink until valid
        if mx[0] == a[l]:
            mx.popleft()
        if mn[0] == a[l]:
            mn.popleft()
        l += 1
    best = max(best, r - l + 1)""")],
    complexity="O(n) time, O(k) space.",
    traps=["Store **indices** in the deque (to know when the front leaves the window), except in the value-based variant above.", "Use `<=` when popping the back so equal elements do not pile up (or use `<` to keep duplicates, consistently).",
           "Pop the front **before** reading the maximum.", "For minimum, flip the comparison."],
    variants=["Shortest subarray with sum ≥ K (with negatives): monotonic deque over prefix sums.", "Jump Game VI: DP where the best previous score in the last k positions comes from a deque.", "Constrained subsequence sum: same DP idea."],
    notuse="Window sizes that vary independently (use a heap with lazy deletion or a balanced tree), or when you need the k-th largest rather than the max.",
    problems=[
        (1438, "Longest Continuous Subarray With Absolute Diff ≤ Limit", "M", "longest-continuous-subarray-with-absolute-diff-less-than-or-equal-to-limit", "Two monotonic deques for max and min; shrink while spread > limit", "O(n) / O(n)"),
        (1696, "Jump Game VI", "M", "jump-game-vi", "dp[i] = a[i] + max(dp[i−k..i−1]) via a deque", "O(n) / O(k)"),
        (239, "Sliding Window Maximum", "H", "sliding-window-maximum", "Deque of decreasing values, front is the max", "O(n) / O(k)"),
        (862, "Shortest Subarray with Sum at Least K", "H", "shortest-subarray-with-sum-at-least-k", "Increasing deque over prefix sums", "O(n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 7
P.append(dict(
    title="Expression evaluation with stacks", tier="sec", sim="calc", oneline="defer + and −, resolve * and / immediately",
    why="Calculator questions test careful parsing plus stack discipline", signature="LC 227 / 224",
    when="Evaluate arithmetic strings with operator precedence or parentheses.",
    detect="\"basic calculator\" · \"evaluate expression\" · \"postfix\" · \"parse and compute\".",
    intuition="Precedence means multiplication binds tighter than addition. So when you see `+ 2 * 2`, you cannot add `2` yet because the `*` is about to claim it. Delay additions by pushing terms on a stack, but settle `*` and `/` on the spot against the top of the stack. At the end every item on the stack is a term to add. Parentheses are a fresh calculation: save the running result and sign, compute inside, then combine.",
    brute="Repeatedly find the highest-precedence operator and rewrite the string: O(n²). One left-to-right pass with a stack is O(n).",
    idea="Track `num` (current number) and `sign` (the **previous** operator). When you reach an operator or the end, apply `sign` to `num`: `+` push, `−` push negative, `*`/`/` combine with the top. For parentheses, push `(result, sign)` on `(` and restore on `)`.",
    steps=["`num = 0`, `sign = '+'`, empty stack.", "Digit: `num = num × 10 + d`.", "At an operator (or the last character): apply the previous `sign` to `num`; set `sign` to this operator; `num = 0`.", "Return the sum of the stack."],
    trace_title="`3+2*2`",
    trace="""'3' num=3
'+'  sign was '+' -> push 3         sign='+'
'2' num=2
'*'  sign was '+' -> push 2         sign='*'
'2' num=2 (end)  sign '*' -> top 2*2=4   stack [3,4]
sum = 7""",
    code=[("Basic Calculator II (+ - * /, no parentheses)",
           """Deque<Integer> st = new ArrayDeque<>();
int num = 0; char sign = '+';
for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (Character.isDigit(c)) num = num * 10 + (c - '0');
    if ((!Character.isDigit(c) && c != ' ') || i == s.length() - 1) {
        if (sign == '+') st.push(num);
        else if (sign == '-') st.push(-num);
        else if (sign == '*') st.push(st.pop() * num);
        else st.push(st.pop() / num);                       // truncates toward zero
        sign = c; num = 0;
    }
}
int sum = 0;
for (int x : st) sum += x;
return sum;""",
           """st, num, sign = [], 0, '+'
for i, c in enumerate(s):
    if c.isdigit():
        num = num * 10 + int(c)
    if (not c.isdigit() and c != ' ') or i == len(s) - 1:
        if sign == '+':
            st.append(num)
        elif sign == '-':
            st.append(-num)
        elif sign == '*':
            st.append(st.pop() * num)
        else:
            st.append(int(st.pop() / num))                  # truncate toward zero
        sign, num = c, 0
return sum(st)"""),
          ("Basic Calculator (+ - and parentheses)",
           """Deque<Integer> st = new ArrayDeque<>();
int res = 0, num = 0, sign = 1;
for (char c : s.toCharArray()) {
    if (Character.isDigit(c)) num = num * 10 + (c - '0');
    else if (c == '+' || c == '-') { res += sign * num; num = 0; sign = (c == '+') ? 1 : -1; }
    else if (c == '(') { st.push(res); st.push(sign); res = 0; sign = 1; }
    else if (c == ')') { res += sign * num; num = 0; res *= st.pop(); res += st.pop(); }
}
return res + sign * num;""",
           """st, res, num, sign = [], 0, 0, 1
for c in s:
    if c.isdigit():
        num = num * 10 + int(c)
    elif c in '+-':
        res += sign * num
        num, sign = 0, 1 if c == '+' else -1
    elif c == '(':
        st.append(res)
        st.append(sign)
        res, sign = 0, 1
    elif c == ')':
        res += sign * num
        num = 0
        res = res * st.pop() + st.pop()
return res + sign * num""")],
    complexity="O(n) time, O(n) space.",
    traps=["Apply the **previous** operator when you hit the next one; the last number needs the end-of-input check.", "Division truncates toward zero: negative operands differ between Java `/` and Python `//`.",
           "Skip spaces but still treat the last character as an end marker.", "Unary minus at the start or after `(` is covered by starting with `sign = 1` and `res = 0`."],
    variants=["Infix to postfix (shunting-yard): operator stack with precedence.", "Number of atoms: stack of maps for nested formulas.", "Decode string (strings topic) uses the same save-and-restore idea."],
    notuse="When the grammar needs functions, variables, or exponents with associativity rules (write a proper recursive-descent parser).",
    problems=[
        (150, "Evaluate Reverse Polish Notation", "M", "evaluate-reverse-polish-notation", "Operands on a stack; operators pop two", "O(n) / O(n)"),
        (227, "Basic Calculator II", "M", "basic-calculator-ii", "Resolve * and / immediately; sum the stack", "O(n) / O(n)"),
        (224, "Basic Calculator", "H", "basic-calculator", "Push (result, sign) at '(' and restore at ')'", "O(n) / O(n)"),
        (726, "Number of Atoms", "H", "number-of-atoms", "Stack of count maps; multiply on ')'", "O(n²) / O(n)"),
    ]))

# ---------------------------------------------------------------- 8
P.append(dict(
    title="Greedy stack: remove to make smallest", tier="hot", sim="removek", oneline="pop larger earlier items while you still may remove",
    why="Powerful greedy template behind several medium problems", signature="LC 402 / 316 / 735",
    when="You may delete up to k items, or merge neighbours, to make a result smallest, largest or conflict-free.",
    detect="\"remove k digits\" · \"remove duplicate letters\" · \"asteroid collision\" · \"car fleet\" · \"remove adjacent duplicates (k)\".",
    intuition="To make a number as small as possible, you want small digits at the front. If a digit is **bigger than the one that follows it**, deleting it improves the number more than deleting anything later. A stack lets you look back at the most recent kept digit and cancel it the moment a smaller digit arrives.",
    brute="Try every set of k deletions: exponential. The greedy stack decides each deletion locally and is correct, in O(n).",
    idea="Scan left to right; while you still may remove and the stack top is worse than the incoming item, pop it. Then push the incoming item. At the end, remove leftovers from the top.",
    steps=["Empty stack, `k` removals left.", "For each digit: `while k > 0 and stack and top > digit`: pop, `k--`.", "Push the digit.", "If `k > 0` still, drop `k` items from the end; strip leading zeros; return `\"0\"` if empty."],
    trace_title="remove 3 digits from `\"1432219\"`",
    trace="""1  push            [1]
4  push            [1,4]
3  4>3 pop (k=2)   [1,3]
2  3>2 pop (k=1)   [1,2]
2  push            [1,2,2]
1  2>1 pop (k=0)   [1,2,1]
9  push            [1,2,1,9]  -> "1219\"""",
    code=[("remove k digits",
           """StringBuilder sb = new StringBuilder();                    // used as the stack
for (char c : num.toCharArray()) {
    while (k > 0 && sb.length() > 0 && sb.charAt(sb.length() - 1) > c) {
        sb.deleteCharAt(sb.length() - 1);
        k--;
    }
    sb.append(c);
}
while (k-- > 0 && sb.length() > 0) sb.deleteCharAt(sb.length() - 1);   // leftover removals
String r = sb.toString().replaceFirst("^0+", "");
return r.isEmpty() ? "0" : r;""",
           """st = []
for c in num:
    while k and st and st[-1] > c:
        st.pop()
        k -= 1
    st.append(c)
if k:
    st = st[:-k]                                           # leftover removals
return ''.join(st).lstrip('0') or '0'"""),
          ("remove duplicate letters (smallest, each letter once)",
           """int[] last = new int[26];
for (int i = 0; i < s.length(); i++) last[s.charAt(i) - 'a'] = i;
boolean[] in = new boolean[26];
StringBuilder st = new StringBuilder();
for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (in[c - 'a']) continue;
    while (st.length() > 0 && st.charAt(st.length() - 1) > c && last[st.charAt(st.length() - 1) - 'a'] > i) {
        in[st.charAt(st.length() - 1) - 'a'] = false;       // it will appear again later: safe to remove
        st.deleteCharAt(st.length() - 1);
    }
    st.append(c); in[c - 'a'] = true;
}
return st.toString();""",
           """last = {c: i for i, c in enumerate(s)}
st, seen = [], set()
for i, c in enumerate(s):
    if c in seen:
        continue
    while st and st[-1] > c and last[st[-1]] > i:          # it will appear again later: safe to remove
        seen.discard(st.pop())
    st.append(c)
    seen.add(c)
return ''.join(st)""")],
    complexity="O(n) time, O(n) space.",
    traps=["Leading zeros: strip them, and return `\"0\"` for an empty result.", "Leftover `k` removals come off the **end** (the stack is already non-decreasing).",
           "Remove-duplicate-letters: only pop a letter if it occurs **again later** (`last[x] > i`), or you lose it forever.", "Asteroid collision: loop while the top moves right and the new one moves left; compare sizes."],
    variants=["Asteroid collision: stack of surviving asteroids; collisions only when top > 0 and new < 0.", "Car fleet: sort by position, stack of arrival times.", "Remove all adjacent duplicates II: stack of `(char, count)`."],
    notuse="When removals are not local (global optimisation, use DP) or the order of survivors can change.",
    problems=[
        (1047, "Remove All Adjacent Duplicates In String", "E", "remove-all-adjacent-duplicates-in-string", "Push unless the top equals the current character", "O(n) / O(n)"),
        (1209, "Remove All Adjacent Duplicates in String II", "M", "remove-all-adjacent-duplicates-in-string-ii", "Stack of (char, count); pop when count reaches k", "O(n) / O(n)"),
        (735, "Asteroid Collision", "M", "asteroid-collision", "Stack of survivors; resolve right-moving vs left-moving", "O(n) / O(n)"),
        (853, "Car Fleet", "M", "car-fleet", "Sort by position, stack arrival times, merge fleets", "O(n log n) / O(n)"),
        (402, "Remove K Digits", "M", "remove-k-digits", "Pop larger digits while k > 0", "O(n) / O(n)"),
        (316, "Remove Duplicate Letters", "M", "remove-duplicate-letters", "Pop larger letters that appear again later", "O(n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 9
P.append(dict(
    title="Circular buffers and queue simulation", tier="sec", sim="circular", oneline="wrap indices with % capacity",
    why="Design questions and Josephus-style simulations use it", signature="LC 622 / 1823",
    when="A fixed-size queue or deque, or items that cycle round and round.",
    detect="\"design circular queue / deque\" · \"circular game, eliminate every kth\" · \"ring buffer\" · \"rotate items in a loop\".",
    intuition="A clock face: after 12 comes 1 again. Use a fixed array as the clock; `head` is where the next item leaves, `tail` is where the next one arrives, and both move clockwise with `% capacity`. No element is ever shifted, so every operation is O(1).",
    brute="Shifting all elements on each dequeue is O(n). Wrapping `head` and `tail` indices keeps enqueue and dequeue O(1).",
    idea="Fixed array `buf`, `head`, and `size`. Write position = `(head + size) % cap`. A separate `size` counter distinguishes full from empty (both have `head == tail`).",
    steps=["`enqueue(x)`: if full return false; `buf[(head + size) % cap] = x`; `size++`.", "`dequeue()`: if empty return false; `head = (head + 1) % cap`; `size--`.", "Front: `buf[head]`; rear: `buf[(head + size − 1) % cap]`.", "Simulation problems: use a queue and rotate: move `k − 1` items to the back, remove one."],
    trace_title="capacity 4",
    trace="""enqueue A,B,C,D   buf [A,B,C,D] head 0 tail 0 size 4 (full)
enqueue E         fails (full)
dequeue -> A      head 1 size 3
enqueue E         written at slot 0 (wrap): [E,B,C,D]
dequeue -> B, C   head 3""",
    code=[("circular queue",
           """class MyCircularQueue {
    int[] buf; int head = 0, size = 0;
    MyCircularQueue(int k) { buf = new int[k]; }
    boolean enQueue(int v) { if (isFull()) return false; buf[(head + size) % buf.length] = v; size++; return true; }
    boolean deQueue() { if (isEmpty()) return false; head = (head + 1) % buf.length; size--; return true; }
    int Front() { return isEmpty() ? -1 : buf[head]; }
    int Rear()  { return isEmpty() ? -1 : buf[(head + size - 1) % buf.length]; }
    boolean isEmpty() { return size == 0; }
    boolean isFull() { return size == buf.length; }
}""",
           """class MyCircularQueue:
    def __init__(self, k):
        self.buf, self.head, self.size = [0] * k, 0, 0
    def enQueue(self, v):
        if self.isFull():
            return False
        self.buf[(self.head + self.size) % len(self.buf)] = v
        self.size += 1
        return True
    def deQueue(self):
        if self.isEmpty():
            return False
        self.head = (self.head + 1) % len(self.buf)
        self.size -= 1
        return True
    def Front(self):
        return -1 if self.isEmpty() else self.buf[self.head]
    def Rear(self):
        return -1 if self.isEmpty() else self.buf[(self.head + self.size - 1) % len(self.buf)]
    def isEmpty(self):
        return self.size == 0
    def isFull(self):
        return self.size == len(self.buf)"""),
          ("circular elimination game (queue rotation)",
           """Queue<Integer> q = new ArrayDeque<>();
for (int i = 1; i <= n; i++) q.add(i);
while (q.size() > 1) {
    for (int i = 0; i < k - 1; i++) q.add(q.poll());       // skip k-1 friends
    q.poll();                                              // eliminate the kth
}
return q.peek();""",
           """from collections import deque
q = deque(range(1, n + 1))
while len(q) > 1:
    q.rotate(-(k - 1))                                     # skip k-1 friends
    q.popleft()                                            # eliminate the kth
return q[0]""")],
    complexity="O(1) per operation, O(capacity) space. Josephus by simulation: O(n·k).",
    traps=["`head == tail` is ambiguous (full or empty): keep a `size` counter or leave one slot empty.", "Negative modulo: `(x − 1) % n` is negative in Java for `x = 0`; use `(x + n − 1) % n`.",
           "Rear index is `(head + size − 1) % cap`.", "A circular deque also needs `front = (front − 1 + cap) % cap` for insert-front."],
    variants=["Circular deque: add insert-front and delete-last.", "Josephus problem has an O(n) recurrence: `f(n, k) = (f(n − 1, k) + k) % n`.", "Moving average with a fixed-size ring buffer and a running sum."],
    notuse="When capacity is unbounded (use a dynamic `ArrayDeque`) or when you need random insertion in the middle.",
    problems=[
        (1700, "Number of Students Unable to Eat Lunch", "E", "number-of-students-unable-to-eat-lunch", "Rotate the student queue until no one wants the top sandwich", "O(n) / O(1)"),
        (622, "Design Circular Queue", "M", "design-circular-queue", "Array with head and size, wrap with %", "O(1) per op / O(k)"),
        (641, "Design Circular Deque", "M", "design-circular-deque", "Ring buffer with front and rear wrap-around", "O(1) per op / O(k)"),
        (1823, "Find the Winner of the Circular Game", "M", "find-the-winner-of-the-circular-game", "Queue rotation, or the Josephus recurrence", "O(n) / O(1)"),
        (503, "Next Greater Element II", "M", "next-greater-element-ii", "Circular scan: 2n steps with i % n", "O(n) / O(n)"),
    ]))

TOPIC = dict(
    id="stack_queue", file="05_stack_queue.html", title="Stacks, Queues and Deques — Pattern Guide",
    lead="Stacks, queues and deques are the simplest structures with the biggest payoff. This guide covers stack bookkeeping, monotonic stacks, two-stack queues, BFS, monotonic deques, expression evaluation, greedy stacks and circular buffers, each with the intuition, a step-through animation that shows the structure changing, Java and Python code, and a ladder of LeetCode problems.",
    mindset="A **stack** answers \"what is the most recent unfinished thing?\"; a **queue** answers \"what has waited longest?\"; a **deque** lets you drop candidates from both ends. Most interview questions are one of three moves: **match** (openers and closers), **wait for a better element** (monotonic stack or deque), or **spread level by level** (BFS). Recognise which, and the code is short.",
    qintro="Ask these questions on every problem:",
    questions=["**Is there nesting, undo, or \"most recent first\"?** → stack.", "**For each element, do I need the nearest bigger or smaller one?** → monotonic stack.", "**Do I need minimum steps or level order?** → BFS with a queue.",
               "**Do I need the max or min of a sliding window?** → monotonic deque.", "**Can I delete items greedily to make the result smaller?** → stack with pops."],
    cues=[
        ["brackets, undo, backspace, postfix, \"min in O(1)\"", "**P1** Stack basics"],
        ["\"next greater / warmer / smaller\", \"stock span\"", "**P2** Monotonic stack"],
        ["\"largest rectangle\", \"sum of subarray minimums\", \"trapping water\"", "**P3** Monotonic stack for ranges"],
        ["\"queue using stacks\", \"stack using queues\"", "**P4** Queues and conversions"],
        ["\"minimum steps\", \"level order\", \"spreading\", \"shortest path in a grid\"", "**P5** BFS"],
        ["\"sliding window maximum\", \"max − min ≤ limit\"", "**P6** Monotonic deque"],
        ["\"calculator\", \"evaluate expression\"", "**P7** Expression evaluation"],
        ["\"remove k digits\", \"remove duplicates\", \"asteroid collision\"", "**P8** Greedy stack"],
        ["\"circular queue / deque\", \"eliminate every kth\"", "**P9** Circular buffers"],
    ],
    choose=[
        ["Match or undo the most recent thing", "Stack (P1)"],
        ["Nearest greater or smaller to the left/right", "Monotonic stack (P2, P3)"],
        ["Fewest steps, equal-cost moves", "BFS queue (P5)"],
        ["Max/min of every window", "Monotonic deque (P6)"],
        ["Parse an expression", "Stack with deferred operators (P7)"],
        ["Delete to minimise or maximise a sequence", "Greedy stack (P8)"],
        ["Fixed-size FIFO", "Circular buffer (P9)"],
    ],
    rule="if you catch yourself writing a nested loop that scans to the right (or left) for the next bigger or smaller value, it is a **monotonic stack**; if it scans a window for its max, it is a **monotonic deque**.",
    selftest=[
        ("Why does the monotonic stack run in O(n) even with a `while` inside a `for`?", "Each index is pushed once and popped at most once, so the total number of pops across the whole loop is at most n."),
        ("In the histogram algorithm, why add a sentinel height of 0 at the end?", "It forces every remaining bar to be popped and evaluated; without it, bars still on the stack are never counted."),
        ("Why is `dequeue` on a two-stack queue O(1) **amortised** even though pouring is O(n)?", "Every element is poured from `in` to `out` at most once, so across m operations the total pouring work is at most m."),
        ("In BFS, why mark a node as seen when you enqueue it rather than when you dequeue it?", "Otherwise the same node can be enqueued by several neighbours before it is processed, growing the queue and wasting work (or breaking distances)."),
        ("Why does BFS give shortest paths only on unweighted graphs?", "It reaches nodes in order of the number of edges. With weights, a path with more edges can be cheaper, so you need Dijkstra."),
        ("When does the monotonic deque pop from the front?", "When the index at the front is outside the current window (`front ≤ i − k`)."),
        ("In Basic Calculator II, why do we apply the **previous** sign when reading an operator?", "The number just read belongs to the operator that came before it; the new operator will apply to the next number."),
        ("A circular queue has `head == tail`. Is it full or empty?", "Ambiguous: keep a separate `size` counter (or leave one slot unused) to tell them apart."),
    ],
    plan=[
        "**Day 1:** stack basics and expression evaluation (RPN, min stack, calculator II).",
        "**Day 2:** monotonic stack: next greater element, daily temperatures, circular variant.",
        "**Day 3:** monotonic stack for ranges: histogram first, then subarray minimums; redo without notes.",
        "**Day 4:** BFS: level order, rotting oranges, word ladder; write the template from memory.",
        "**Day 5:** monotonic deque: sliding window maximum, then the two-deque variant.",
        "**Day 6:** greedy stack (remove k digits, asteroid collision) and the design problems (queue from stacks, circular queue).",
    ],
    patterns=P,
)
