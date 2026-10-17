"""Content for topic 09: Binary trees and BSTs."""

P = []

# ---------------------------------------------------------------- 1
P.append(dict(
    title="Thinking recursively on trees (height, depth, symmetry)", tier="hot", sim="height", oneline="solve for the children, trust them, combine at the node",
    why="Almost every tree problem is this one idea", signature="LC 104 / 543",
    when="A property of a tree can be written in terms of the same property of its left and right subtrees.",
    detect="\"maximum depth\" · \"same tree\" · \"invert\" · \"symmetric\" · \"balanced\" · \"diameter\" · \"subtree of another tree\".",
    intuition="A tree is a node plus two smaller trees. So to answer a question about the whole tree, ask the same question of the left subtree and the right subtree (the recursion will handle them), then combine the two answers with this node's own value. The base case is the empty tree.",
    brute="Walking the tree repeatedly for each node (for example recomputing height at every node to check balance) gives O(n²). One recursion that returns the information the parent needs (height, plus a flag) gives O(n).",
    idea="`f(node)`: if `node == null` return the base value; `l = f(left)`, `r = f(right)`; return `combine(node, l, r)`. Often a **global** best is updated on the way while the function returns something else upward (diameter).",
    steps=["Base case: `null` → 0 / true / empty result.", "Recurse into both children.", "Combine with the node: `1 + max(l, r)`, `l && r && node.val == …`, …", "If the answer is a global max (diameter), update it from `l` and `r` before returning."],
    trace_title="height of `3 → (9, 20 → (15, 7))`",
    trace="""h(9)=1  h(15)=1  h(7)=1
h(20)=1+max(1,1)=2
h(3)=1+max(1,2)=3""",
    code=[("height and diameter",
           """int maxDepth(TreeNode r) { return r == null ? 0 : 1 + Math.max(maxDepth(r.left), maxDepth(r.right)); }

int best = 0;
int height(TreeNode n) {                       // diameter = longest path in edges
    if (n == null) return 0;
    int l = height(n.left), r = height(n.right);
    best = Math.max(best, l + r);              // path through this node
    return 1 + Math.max(l, r);                 // only one side can go up
}""",
           """def max_depth(r):
    return 0 if not r else 1 + max(max_depth(r.left), max_depth(r.right))

best = 0
def height(n):                                 # diameter = longest path in edges
    global best
    if not n:
        return 0
    l, r = height(n.left), height(n.right)
    best = max(best, l + r)                    # path through this node
    return 1 + max(l, r)                       # only one side can go up"""),
          ("invert, same tree and symmetric",
           """TreeNode invert(TreeNode r) {
    if (r == null) return null;
    TreeNode l = invert(r.left), rt = invert(r.right);
    r.left = rt; r.right = l;
    return r;
}
boolean same(TreeNode a, TreeNode b) {
    if (a == null || b == null) return a == b;
    return a.val == b.val && same(a.left, b.left) && same(a.right, b.right);
}
boolean mirror(TreeNode a, TreeNode b) {                 // symmetric: compare left with the mirror of right
    if (a == null || b == null) return a == b;
    return a.val == b.val && mirror(a.left, b.right) && mirror(a.right, b.left);
}""",
           """def invert(r):
    if not r:
        return None
    r.left, r.right = invert(r.right), invert(r.left)
    return r

def same(a, b):
    if not a or not b:
        return a is b
    return a.val == b.val and same(a.left, b.left) and same(a.right, b.right)

def mirror(a, b):                                        # symmetric: compare left with the mirror of right
    if not a or not b:
        return a is b
    return a.val == b.val and mirror(a.left, b.right) and mirror(a.right, b.left)""")],
    complexity="O(n) time, O(h) stack space (h = height: log n balanced, n for a chain).",
    traps=["Forgetting the `null` base case; or checking `a == b` only after dereferencing.", "Diameter counts **edges** (`l + r`) vs nodes (`l + r + 1`); read the problem.",
           "Balanced-check: do not recompute heights at every node; return −1 from the recursion as a failure flag.", "Deep (skewed) trees overflow the stack at ~10⁴ depth in Java/Python: use an explicit stack."],
    variants=["Subtree of another tree: for each node run `same`, or serialise both and search.", "Minimum depth: a node with one child is **not** a leaf.", "Count nodes in a complete tree in O(log² n) using heights."],
    notuse="When the property depends on global order (use traversal) or on values elsewhere in the tree (use the path-carrying patterns).",
    problems=[
        (104, "Maximum Depth of Binary Tree", "E", "maximum-depth-of-binary-tree", "1 + max(depth(left), depth(right))", "O(n) / O(h)"),
        (100, "Same Tree", "E", "same-tree", "Compare values, recurse on both pairs", "O(n) / O(h)"),
        (226, "Invert Binary Tree", "E", "invert-binary-tree", "Swap the inverted children", "O(n) / O(h)"),
        (101, "Symmetric Tree", "E", "symmetric-tree", "Mirror comparison of left and right", "O(n) / O(h)"),
        (110, "Balanced Binary Tree", "E", "balanced-binary-tree", "Height recursion returning −1 on imbalance", "O(n) / O(h)"),
        (543, "Diameter of Binary Tree", "E", "diameter-of-binary-tree", "Update best with l + r, return 1 + max(l, r)", "O(n) / O(h)"),
        (572, "Subtree of Another Tree", "E", "subtree-of-another-tree", "At each node test sameTree", "O(m·n) / O(h)"),
    ]))

# ---------------------------------------------------------------- 2
P.append(dict(
    title="DFS traversals and root-to-leaf paths", tier="hot", sim="traversal", oneline="pre, in, post differ only in when the node is visited",
    why="Foundation for path sums, serialisation, BST checks and more", signature="LC 94 / 112 / 437",
    when="You need every node in a specific order, or you accumulate state while walking down root-to-leaf paths.",
    detect="\"inorder / preorder / postorder\" · \"path sum\" · \"all root-to-leaf paths\" · \"sum root to leaf numbers\" · \"number of paths with sum\".",
    intuition="Walk around the outline of the tree with your hand on the wall. You pass each node three times: on the way down its left side (**preorder** moment), underneath it between the subtrees (**inorder**), and on the way up its right side (**postorder**). Choose the moment at which you write the node's value down.",
    brute="Collecting paths by repeatedly searching from the root is wasteful. A single DFS carrying the running state (current sum, current path) as arguments visits each node once.",
    idea="`dfs(node, state)`: do the work **before** recursing (preorder), **between** (inorder) or **after** (postorder). Pass the accumulated state down as parameters; backtrack mutable state (a path list) after the calls.",
    steps=["Base case: `null` returns.", "Preorder work: use `node` (push to path, add to sum).", "Recurse left, (inorder work), recurse right.", "Postorder work, then undo any mutable state (pop the path)."],
    trace_title="tree `1 → (2 → (4, 5), 3)`",
    trace="""preorder  : 1 2 4 5 3
inorder   : 4 2 5 1 3
postorder : 4 5 2 3 1""",
    code=[("three orders and a root-to-leaf path sum",
           """void pre(TreeNode n, List<Integer> out)  { if (n == null) return; out.add(n.val); pre(n.left, out); pre(n.right, out); }
void in(TreeNode n, List<Integer> out)   { if (n == null) return; in(n.left, out); out.add(n.val); in(n.right, out); }
void post(TreeNode n, List<Integer> out) { if (n == null) return; post(n.left, out); post(n.right, out); out.add(n.val); }

boolean hasPathSum(TreeNode n, int target) {
    if (n == null) return false;
    if (n.left == null && n.right == null) return n.val == target;    // leaf: nothing left to add
    return hasPathSum(n.left, target - n.val) || hasPathSum(n.right, target - n.val);
}""",
           """def pre(n, out):
    if not n: return
    out.append(n.val); pre(n.left, out); pre(n.right, out)

def inorder(n, out):
    if not n: return
    inorder(n.left, out); out.append(n.val); inorder(n.right, out)

def post(n, out):
    if not n: return
    post(n.left, out); post(n.right, out); out.append(n.val)

def has_path_sum(n, target):
    if not n:
        return False
    if not n.left and not n.right:                         # leaf: nothing left to add
        return n.val == target
    return has_path_sum(n.left, target - n.val) or has_path_sum(n.right, target - n.val)"""),
          ("all root-to-leaf paths and path sum III (prefix sums on a tree)",
           """void paths(TreeNode n, List<Integer> path, List<List<Integer>> res) {
    if (n == null) return;
    path.add(n.val);                                               // choose
    if (n.left == null && n.right == null) res.add(new ArrayList<>(path));
    paths(n.left, path, res); paths(n.right, path, res);
    path.remove(path.size() - 1);                                  // un-choose (backtrack)
}
// number of downward paths summing to target
int count = 0; Map<Long, Integer> seen = new HashMap<>();
void dfs(TreeNode n, long cur, int target) {
    if (n == null) return;
    cur += n.val;
    count += seen.getOrDefault(cur - target, 0);                   // a prefix that leaves exactly target
    seen.merge(cur, 1, Integer::sum);
    dfs(n.left, cur, target); dfs(n.right, cur, target);
    seen.merge(cur, -1, Integer::sum);                             // leaving this node's subtree
}  // call with seen.put(0L, 1)""",
           """def paths(n, path, res):
    if not n:
        return
    path.append(n.val)                                             # choose
    if not n.left and not n.right:
        res.append(path[:])
    paths(n.left, path, res); paths(n.right, path, res)
    path.pop()                                                     # un-choose (backtrack)

# number of downward paths summing to target
from collections import defaultdict
seen, count = defaultdict(int), 0
seen[0] = 1
def dfs(n, cur):
    global count
    if not n:
        return
    cur += n.val
    count += seen[cur - target]                                    # a prefix that leaves exactly target
    seen[cur] += 1
    dfs(n.left, cur); dfs(n.right, cur)
    seen[cur] -= 1                                                 # leaving this node's subtree""")],
    complexity="O(n) time; O(h) space (plus the path list).",
    traps=["Copy the path when recording: `new ArrayList<>(path)`.", "Check leaf with **both** children null, not just one.",
           "Path Sum III: values can be negative, so you need prefix sums with a map, and you must undo the map entry after the recursion.", "Use `long` for sums when node values can be large."],
    variants=["Sum root-to-leaf numbers: pass `cur * 10 + val` down.", "Path Sum II: collect the paths whose sum matches.", "Iterative traversals with an explicit stack (pattern 9)."],
    notuse="When you need nodes level by level (BFS) or the structure of subtrees combined bottom-up (return values).",
    problems=[
        (144, "Binary Tree Preorder Traversal", "E", "binary-tree-preorder-traversal", "Node, left, right", "O(n) / O(h)"),
        (94, "Binary Tree Inorder Traversal", "E", "binary-tree-inorder-traversal", "Left, node, right", "O(n) / O(h)"),
        (145, "Binary Tree Postorder Traversal", "E", "binary-tree-postorder-traversal", "Left, right, node", "O(n) / O(h)"),
        (112, "Path Sum", "E", "path-sum", "Subtract val down; at a leaf compare with 0", "O(n) / O(h)"),
        (257, "Binary Tree Paths", "E", "binary-tree-paths", "Build the path string down to each leaf", "O(n) / O(h)"),
        (129, "Sum Root to Leaf Numbers", "M", "sum-root-to-leaf-numbers", "Pass cur × 10 + val down; add at leaves", "O(n) / O(h)"),
        (113, "Path Sum II", "M", "path-sum-ii", "Backtrack a path list; record at matching leaves", "O(n²) / O(h)"),
        (437, "Path Sum III", "M", "path-sum-iii", "Prefix-sum map along the root path; undo on return", "O(n) / O(h)"),
    ]))

# ---------------------------------------------------------------- 3
P.append(dict(
    title="BFS: level order and its variations", tier="hot", sim="levelorder", oneline="a queue; process exactly size() nodes per level",
    why="Level order, right-side view and minimum depth appear constantly", signature="LC 102 / 199",
    when="You need nodes grouped by depth, the nearest leaf, or a view of the tree from the side.",
    detect="\"level order\" · \"zigzag\" · \"right side view\" · \"minimum depth\" · \"average of levels\" · \"maximum width\".",
    intuition="Ripples in a pond: everything at distance 1 from the root is dealt with before anything at distance 2. A queue naturally gives that order: new children join the back while the current level is still being served from the front. If you freeze the queue's size at the start of a round, that round is exactly one level.",
    brute="DFS with a depth parameter and a list-of-lists also gives levels, but BFS finds the **shallowest** answer first, so you can stop early (minimum depth).",
    idea="`queue = [root]`; while not empty: `size = queue.size()`; repeat `size` times: pop `node`, record it, enqueue its non-null children.",
    steps=["Start with the root in the queue.", "For each round take `size = queue.size()`.", "Pop `size` nodes; append their values to the level list; push children.", "Add the level list to the result."],
    trace_title="`3 → (9, 20 → (15, 7))`",
    trace="""queue [3]       level 0: 3
queue [9,20]    level 1: 9 20
queue [15,7]    level 2: 15 7
=> [[3],[9,20],[15,7]]""",
    code=[("level order, right-side view and zigzag",
           """List<List<Integer>> res = new ArrayList<>();
if (root == null) return res;
Queue<TreeNode> q = new ArrayDeque<>();
q.add(root);
boolean leftToRight = true;
while (!q.isEmpty()) {
    int size = q.size();                                   // exactly this level
    LinkedList<Integer> level = new LinkedList<>();
    for (int i = 0; i < size; i++) {
        TreeNode n = q.poll();
        if (leftToRight) level.addLast(n.val); else level.addFirst(n.val);   // zigzag
        if (n.left != null) q.add(n.left);
        if (n.right != null) q.add(n.right);
    }
    res.add(level);                                        // right view: level.getLast() before reversing
    leftToRight = !leftToRight;
}""",
           """from collections import deque
res = []
if not root:
    return res
q, left_to_right = deque([root]), True
while q:
    level = deque()
    for _ in range(len(q)):                                # exactly this level
        n = q.popleft()
        if left_to_right: level.append(n.val)
        else: level.appendleft(n.val)                      # zigzag
        if n.left: q.append(n.left)
        if n.right: q.append(n.right)
    res.append(list(level))                                # right view: the last visited node of the level
    left_to_right = not left_to_right"""),
          ("minimum depth (stop at the first leaf)",
           """if (root == null) return 0;
Queue<TreeNode> q = new ArrayDeque<>(); q.add(root);
int depth = 1;
while (!q.isEmpty()) {
    for (int i = q.size(); i > 0; i--) {
        TreeNode n = q.poll();
        if (n.left == null && n.right == null) return depth;     // nearest leaf
        if (n.left != null) q.add(n.left);
        if (n.right != null) q.add(n.right);
    }
    depth++;
}
return depth;""",
           """if not root:
    return 0
q, depth = deque([root]), 1
while q:
    for _ in range(len(q)):
        n = q.popleft()
        if not n.left and not n.right:
            return depth                                         # nearest leaf
        if n.left: q.append(n.left)
        if n.right: q.append(n.right)
    depth += 1""")],
    complexity="O(n) time, O(w) space where w is the maximum width (up to n/2).",
    traps=["Capture `size = q.size()` **before** the inner loop (the queue grows inside it).", "Do not enqueue `null` children.",
           "Minimum depth: a node with one child is not a leaf; the BFS version handles this automatically.", "Maximum width: number nodes with heap indexes (`2i`, `2i + 1`) and use `long` / relative indexes to avoid overflow."],
    variants=["Right-side view: last node of each level (or DFS visiting right first).", "Average / maximum of each level: aggregate inside the loop.", "Bottom-up level order: reverse the result list."],
    notuse="When you need the path itself or bottom-up information (use DFS).",
    problems=[
        (637, "Average of Levels in Binary Tree", "E", "average-of-levels-in-binary-tree", "Sum the level, divide by its size", "O(n) / O(w)"),
        (111, "Minimum Depth of Binary Tree", "E", "minimum-depth-of-binary-tree", "BFS and stop at the first leaf", "O(n) / O(w)"),
        (102, "Binary Tree Level Order Traversal", "M", "binary-tree-level-order-traversal", "Queue, process size() nodes per level", "O(n) / O(w)"),
        (107, "Binary Tree Level Order Traversal II", "M", "binary-tree-level-order-traversal-ii", "Same, then reverse the list of levels", "O(n) / O(w)"),
        (199, "Binary Tree Right Side View", "M", "binary-tree-right-side-view", "Last node of each level", "O(n) / O(w)"),
        (103, "Binary Tree Zigzag Level Order Traversal", "M", "binary-tree-zigzag-level-order-traversal", "Alternate the insertion end per level", "O(n) / O(w)"),
        (515, "Find Largest Value in Each Tree Row", "M", "find-largest-value-in-each-tree-row", "Track the max inside each level", "O(n) / O(w)"),
        (662, "Maximum Width of Binary Tree", "M", "maximum-width-of-binary-tree", "Level order with heap-style indexes", "O(n) / O(w)"),
    ]))

# ---------------------------------------------------------------- 4
P.append(dict(
    title="Path problems: return one value, record another", tier="hot", sim="maxpath", oneline="the best path through a node is not what you return to the parent",
    why="The standard trap in hard tree questions", signature="LC 124 / 543",
    when="The answer is a best path that can bend at any node (maximum path sum, longest same-value path).",
    detect="\"maximum path sum\" · \"longest univalue path\" · \"diameter\" · \"path may start and end anywhere\" · \"distribute coins\".",
    intuition="A path that bends at a node uses **both** of its sides (left arm + node + right arm). But when this node reports to its parent, the parent can only extend **one** arm of it. So each node does two different things: it **records** the best bent path through itself into a global answer, and it **returns** the best single arm (node + the better child arm). Negative arms are dropped by clamping at 0.",
    brute="Trying every pair of nodes as path endpoints is O(n²). A single post-order pass with this record-versus-return split is O(n).",
    idea="`gain(node) = node.val + max(0, gain(left), gain(right))` is what you return. Before returning, set `best = max(best, node.val + max(0, gain(left)) + max(0, gain(right)))`.",
    steps=["Post-order: compute `l = max(0, gain(left))`, `r = max(0, gain(right))`.", "Record `best = max(best, node.val + l + r)`.", "Return `node.val + max(l, r)` to the parent.", "Initialise `best = −∞` (not 0) so all-negative trees work."],
    trace_title="`−10 → (9, 20 → (15, 7))`",
    trace="""9  : through 9           return 9
15 : through 15          return 15
7  : through 7           return 7
20 : 20+15+7 = 42 best   return 20+15 = 35
-10: -10+9+35 = 34       return max(0,-10+35) = 25
answer 42""",
    code=[("binary tree maximum path sum",
           """int best = Integer.MIN_VALUE;
int gain(TreeNode n) {
    if (n == null) return 0;
    int l = Math.max(0, gain(n.left));            // ignore negative arms
    int r = Math.max(0, gain(n.right));
    best = Math.max(best, n.val + l + r);         // best path that bends at n
    return n.val + Math.max(l, r);                // only one arm can continue upward
}""",
           """best = float('-inf')
def gain(n):
    global best
    if not n:
        return 0
    l = max(0, gain(n.left))                      # ignore negative arms
    r = max(0, gain(n.right))
    best = max(best, n.val + l + r)               # best path that bends at n
    return n.val + max(l, r)                      # only one arm can continue upward"""),
          ("count good nodes (carry the maximum so far downward)",
           """int good(TreeNode n, int maxSoFar) {
    if (n == null) return 0;
    int here = n.val >= maxSoFar ? 1 : 0;
    int m = Math.max(maxSoFar, n.val);
    return here + good(n.left, m) + good(n.right, m);
}""",
           """def good(n, max_so_far):
    if not n:
        return 0
    here = 1 if n.val >= max_so_far else 0
    m = max(max_so_far, n.val)
    return here + good(n.left, m) + good(n.right, m)""")],
    complexity="O(n) time, O(h) space.",
    traps=["Returning the bent path (both arms) to the parent: wrong, the parent can only use one arm.", "Initialising `best` to 0 breaks trees whose nodes are all negative.",
           "For diameter-style problems edge count vs node count differs by one.", "Longest univalue path: only extend an arm if the child has the same value as the node."],
    variants=["Longest univalue path: arms extend only through equal values.", "Distribute coins: each subtree returns its surplus; moves += |surplus|.", "Binary tree cameras: tri-state return (covered, camera, needs cover) (pattern 8)."],
    notuse="Paths that must go from the root downward (a simple DFS with accumulated state is enough).",
    problems=[
        (1448, "Count Good Nodes in Binary Tree", "M", "count-good-nodes-in-binary-tree", "Carry max-so-far down; count nodes ≥ it", "O(n) / O(h)"),
        (687, "Longest Univalue Path", "M", "longest-univalue-path", "Extend an arm only through equal child values; record l + r", "O(n) / O(h)"),
        (979, "Distribute Coins in Binary Tree", "M", "distribute-coins-in-binary-tree", "Each subtree returns surplus; add |surplus| to moves", "O(n) / O(h)"),
        (124, "Binary Tree Maximum Path Sum", "H", "binary-tree-maximum-path-sum", "Record node + l + r, return node + max(l, r)", "O(n) / O(h)"),
    ]))

# ---------------------------------------------------------------- 5
P.append(dict(
    title="Binary search trees: search, insert, delete, validate", tier="hot", sim="bstinsert", oneline="left < node < right, and inorder is sorted",
    why="BST questions test whether you use the ordering property", signature="LC 98 / 230 / 700",
    when="The tree has the BST invariant and you want O(h) lookup, or you need sorted order.",
    detect="\"search in a BST\" · \"insert / delete\" · \"validate BST\" · \"kth smallest\" · \"two sum IV\" · \"minimum absolute difference\" · \"recover a BST\".",
    intuition="A BST is binary search turned into a shape: at each node one comparison throws away half of the remaining values. The ordering also means an **inorder walk lists values in sorted order**, so many BST tasks (kth smallest, minimum difference, validation, recovery) are really \"walk inorder and compare neighbours\".",
    brute="Treating a BST as a plain tree (full DFS) costs O(n) per query. Using the ordering gives O(h): O(log n) when balanced.",
    idea="Search/insert: compare, go left or right. Delete: leaf → remove; one child → replace by the child; two children → copy the inorder successor (smallest in the right subtree) and delete it. Validate: carry an allowed `(low, high)` range down, or check that inorder is strictly increasing.",
    steps=["Search: `val < node` → left, `val > node` → right, else found.", "Insert: walk down to a null child and attach.", "Delete: handle 0, 1, 2 children (successor swap for two).", "Validate: pass `(low, high)` bounds; each node must satisfy `low < val < high`."],
    trace_title="insert 7 into `8 → (3 → (1, 6), 10 → (·, 14))`",
    trace="""7 < 8  go left
7 > 3  go right
7 > 6  go right -> empty slot
attach 7 as the right child of 6""",
    code=[("search, insert and validate",
           """TreeNode search(TreeNode n, int v) {
    while (n != null && n.val != v) n = v < n.val ? n.left : n.right;
    return n;
}
TreeNode insert(TreeNode n, int v) {
    if (n == null) return new TreeNode(v);
    if (v < n.val) n.left = insert(n.left, v); else n.right = insert(n.right, v);
    return n;
}
boolean valid(TreeNode n, long low, long high) {            // long: node values can be Integer.MIN/MAX
    if (n == null) return true;
    if (n.val <= low || n.val >= high) return false;
    return valid(n.left, low, n.val) && valid(n.right, n.val, high);
}""",
           """def search(n, v):
    while n and n.val != v:
        n = n.left if v < n.val else n.right
    return n

def insert(n, v):
    if not n:
        return TreeNode(v)
    if v < n.val:
        n.left = insert(n.left, v)
    else:
        n.right = insert(n.right, v)
    return n

def valid(n, low=float('-inf'), high=float('inf')):
    if not n:
        return True
    if n.val <= low or n.val >= high:
        return False
    return valid(n.left, low, n.val) and valid(n.right, n.val, high)"""),
          ("delete a node",
           """TreeNode delete(TreeNode root, int key) {
    if (root == null) return null;
    if (key < root.val) root.left = delete(root.left, key);
    else if (key > root.val) root.right = delete(root.right, key);
    else {
        if (root.left == null) return root.right;           // 0 or 1 child
        if (root.right == null) return root.left;
        TreeNode m = root.right;                             // two children: inorder successor
        while (m.left != null) m = m.left;
        root.val = m.val;
        root.right = delete(root.right, m.val);
    }
    return root;
}""",
           """def delete(root, key):
    if not root:
        return None
    if key < root.val:
        root.left = delete(root.left, key)
    elif key > root.val:
        root.right = delete(root.right, key)
    else:
        if not root.left:                                    # 0 or 1 child
            return root.right
        if not root.right:
            return root.left
        m = root.right                                       # two children: inorder successor
        while m.left:
            m = m.left
        root.val = m.val
        root.right = delete(root.right, m.val)
    return root""")],
    complexity="O(h) per operation (O(log n) balanced, O(n) for a chain); validation is O(n).",
    traps=["Validating only against the **parent** is wrong: every node in the left subtree must be below the **ancestor** too. Use bounds or inorder.", "Use `long` bounds (or nullable bounds) because values can equal `Integer.MIN_VALUE` / `MAX_VALUE`.",
           "Duplicates: decide a rule (left or right); most problems say BST values are unique.", "Delete with two children: replace with the successor, then delete the successor from the right subtree."],
    variants=["Kth smallest: inorder with a counter; stop at k.", "Recover BST: inorder finds the two swapped nodes (first and last violations).", "Two Sum IV: inorder list + two pointers, or hash set.", "Minimum absolute difference: minimum gap between consecutive inorder values."],
    notuse="Unordered trees, or when worst-case O(n) height is unacceptable (use a balanced tree such as TreeMap / red-black).",
    problems=[
        (700, "Search in a Binary Search Tree", "E", "search-in-a-binary-search-tree", "Walk left or right by comparison", "O(h) / O(1)"),
        (530, "Minimum Absolute Difference in BST", "E", "minimum-absolute-difference-in-bst", "Inorder: smallest adjacent difference", "O(n) / O(h)"),
        (653, "Two Sum IV - Input is a BST", "E", "two-sum-iv-input-is-a-bst", "Inorder to an array + two pointers", "O(n) / O(n)"),
        (701, "Insert into a Binary Search Tree", "M", "insert-into-a-binary-search-tree", "Walk down to a null child and attach", "O(h) / O(h)"),
        (98, "Validate Binary Search Tree", "M", "validate-binary-search-tree", "Carry (low, high) bounds down", "O(n) / O(h)"),
        (230, "Kth Smallest Element in a BST", "M", "kth-smallest-element-in-a-bst", "Inorder, stop at the kth", "O(h + k) / O(h)"),
        (450, "Delete Node in a BST", "M", "delete-node-in-a-bst", "Successor replacement for two children", "O(h) / O(h)"),
        (99, "Recover Binary Search Tree", "M", "recover-binary-search-tree", "Inorder: find the two out-of-order nodes and swap values", "O(n) / O(h)"),
    ]))

# ---------------------------------------------------------------- 6
P.append(dict(
    title="Lowest common ancestor and tree distances", tier="hot", sim="lca", oneline="the first node with a target on both sides",
    why="A top interview question with a neat O(n) one-pass solution", signature="LC 236 / 235",
    when="Find where two nodes' root paths meet, or measure distances between nodes.",
    detect="\"lowest common ancestor\" · \"all nodes at distance K\" · \"smallest subtree with all deepest nodes\" · \"distance between two nodes\".",
    intuition="Imagine two climbers at nodes p and q moving up toward the root. The lowest common ancestor is the first node they both pass. In a recursion from the top: a node reports \"I found a target in my subtree\" upward; the first node that hears reports from **both** sides (or is itself a target and hears from one side) is the meeting point.",
    brute="Store the root path to each node and compare them: O(n) time and extra memory. The recursive return-value solution does it in one pass with no paths.",
    idea="`lca(node)`: if `node` is null or equals `p` or `q`, return it. Recurse into both children. If both return non-null, `node` is the LCA; otherwise return whichever is non-null. For a BST, compare values and walk down: if both are smaller go left, both larger go right, else the current node is the LCA.",
    steps=["Base: `null`, `p`, or `q` → return the node.", "`l = lca(left)`, `r = lca(right)`.", "Both non-null → return `node`.", "Otherwise return the non-null one (or null)."],
    trace_title="LCA of 6 and 4 in `3 → (5 → (6, 2 → (7, 4)), 1 → (0, 8))`",
    trace="""6 is p: returns 6
7: neither, null      4 is q: returns 4
2: left null, right 4 -> returns 4
5: left 6, right 4 both non-null -> LCA = 5
1: nothing found -> null
3: left 5, right null -> returns 5""",
    code=[("LCA in a binary tree and in a BST",
           """TreeNode lca(TreeNode r, TreeNode p, TreeNode q) {
    if (r == null || r == p || r == q) return r;
    TreeNode l = lca(r.left, p, q), rt = lca(r.right, p, q);
    if (l != null && rt != null) return r;                 // p and q are on different sides
    return l != null ? l : rt;
}
TreeNode lcaBST(TreeNode r, TreeNode p, TreeNode q) {
    while (r != null) {
        if (p.val < r.val && q.val < r.val) r = r.left;
        else if (p.val > r.val && q.val > r.val) r = r.right;
        else return r;                                      // they split here (or one equals r)
    }
    return null;
}""",
           """def lca(r, p, q):
    if not r or r is p or r is q:
        return r
    l, rt = lca(r.left, p, q), lca(r.right, p, q)
    if l and rt:
        return r                                            # p and q are on different sides
    return l or rt

def lca_bst(r, p, q):
    while r:
        if p.val < r.val and q.val < r.val:
            r = r.left
        elif p.val > r.val and q.val > r.val:
            r = r.right
        else:
            return r                                        # they split here (or one equals r)
    return None""")],
    complexity="Binary tree: O(n) time, O(h) space. BST: O(h) time, O(1) space.",
    traps=["The recursion assumes **both** p and q exist in the tree; if not, you need a second pass or counters.", "A node can be its own ancestor: if p is above q the answer is p.",
           "Compare node **references**, not values, unless values are unique and the problem says so.", "Distance K nodes: convert to a graph (parent pointers) and BFS from the target."],
    variants=["LCA of deepest leaves: return (depth, node) from each subtree.", "Distance between p and q: `depth(p) + depth(q) − 2·depth(lca)`.", "All nodes at distance K: parent map + BFS."],
    notuse="Many repeated LCA queries on a fixed tree: preprocess with binary lifting or Euler tour + RMQ.",
    problems=[
        (235, "Lowest Common Ancestor of a Binary Search Tree", "M", "lowest-common-ancestor-of-a-binary-search-tree", "Walk down by values until the paths split", "O(h) / O(1)"),
        (236, "Lowest Common Ancestor of a Binary Tree", "M", "lowest-common-ancestor-of-a-binary-tree", "Return node when both sides report", "O(n) / O(h)"),
        (1123, "Lowest Common Ancestor of Deepest Leaves", "M", "lowest-common-ancestor-of-deepest-leaves", "Return (depth, lca) from each subtree", "O(n) / O(h)"),
        (865, "Smallest Subtree with all the Deepest Nodes", "M", "smallest-subtree-with-all-the-deepest-nodes", "Same as 1123", "O(n) / O(h)"),
        (863, "All Nodes Distance K in Binary Tree", "M", "all-nodes-distance-k-in-binary-tree", "Parent map, then BFS k levels from the target", "O(n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 7
P.append(dict(
    title="Construct and serialise trees", tier="sec", sim="build", oneline="preorder gives the root, inorder splits the subtrees",
    why="Tests whether you understand what each traversal encodes", signature="LC 105 / 297",
    when="Rebuild a tree from traversals, convert a sorted array to a balanced BST, or turn a tree into a string and back.",
    detect="\"construct from preorder and inorder\" · \"serialize and deserialize\" · \"sorted array to BST\" · \"flatten\" · \"maximum binary tree\".",
    intuition="Preorder always starts with the root; inorder tells you how many nodes lie to the left of that root. So the first preorder value is a root, finding it in inorder splits the remaining values into a left group and a right group, and the same trick rebuilds each subtree. Serialisation is just recording a preorder with explicit null markers so the shape is unambiguous.",
    brute="Searching inorder for each root costs O(n) each, so O(n²) total. A hash map from value to inorder index makes each lookup O(1), O(n) overall.",
    idea="`build(l, r)` over the inorder window: take `pre[idx++]` as the root, `m = pos[root]`; `root.left = build(l, m − 1)`; `root.right = build(m + 1, r)`. Always build left before right so the preorder pointer advances correctly.",
    steps=["Map each inorder value to its index.", "Keep a global preorder pointer.", "Take the next preorder value as the root; find `m` in inorder.", "Build the left window `[l, m − 1]`, then the right window `[m + 1, r]`."],
    trace_title="`pre = [3,9,20,15,7]`, `in = [9,3,15,20,7]`",
    trace="""root 3: inorder splits [9] | [15,20,7]
  left : root 9 (leaf)
  right: root 20 splits [15] | [7]
         left 15, right 7
tree: 3 -> (9, 20 -> (15, 7))""",
    code=[("build from preorder and inorder",
           """int pre = 0; Map<Integer, Integer> pos = new HashMap<>();
TreeNode build(int[] preorder, int l, int r) {
    if (l > r) return null;
    int rootVal = preorder[pre++];                          // next unused preorder value is the root
    TreeNode node = new TreeNode(rootVal);
    int m = pos.get(rootVal);                               // pos: value -> index in inorder
    node.left = build(preorder, l, m - 1);                  // left first: preorder visits it first
    node.right = build(preorder, m + 1, r);
    return node;
}""",
           """def build_tree(preorder, inorder):
    pos = {v: i for i, v in enumerate(inorder)}
    it = iter(preorder)
    def build(l, r):
        if l > r:
            return None
        root = TreeNode(next(it))                           # next unused preorder value is the root
        m = pos[root.val]
        root.left = build(l, m - 1)                         # left first: preorder visits it first
        root.right = build(m + 1, r)
        return root
    return build(0, len(inorder) - 1)"""),
          ("serialise with null markers; sorted array to balanced BST",
           """String serialize(TreeNode n) {
    if (n == null) return "#";
    return n.val + "," + serialize(n.left) + "," + serialize(n.right);        // preorder + null markers
}
TreeNode deserialize(Deque<String> t) {
    String s = t.poll();
    if (s.equals("#")) return null;
    TreeNode n = new TreeNode(Integer.parseInt(s));
    n.left = deserialize(t); n.right = deserialize(t);
    return n;
}   // call: deserialize(new ArrayDeque<>(Arrays.asList(data.split(","))))

TreeNode sortedToBST(int[] a, int l, int r) {
    if (l > r) return null;
    int m = l + (r - l) / 2;                                // middle becomes the root: balanced
    TreeNode n = new TreeNode(a[m]);
    n.left = sortedToBST(a, l, m - 1); n.right = sortedToBST(a, m + 1, r);
    return n;
}""",
           """def serialize(n):
    if not n:
        return "#"
    return f"{n.val},{serialize(n.left)},{serialize(n.right)}"          # preorder + null markers

def deserialize(data):
    tokens = iter(data.split(","))
    def build():
        t = next(tokens)
        if t == "#":
            return None
        n = TreeNode(int(t))
        n.left = build()
        n.right = build()
        return n
    return build()

def sorted_to_bst(a, l, r):
    if l > r:
        return None
    m = (l + r) // 2                                        # middle becomes the root: balanced
    n = TreeNode(a[m])
    n.left, n.right = sorted_to_bst(a, l, m - 1), sorted_to_bst(a, m + 1, r)
    return n""")],
    complexity="O(n) time (with the index map), O(n) space.",
    traps=["Build **left before right** (preorder order) or the pointer is wrong.", "Values must be unique for the inorder map (otherwise the split is ambiguous).",
           "Preorder alone (or inorder alone) does not determine a tree; you need inorder plus another, or null markers.", "Postorder + inorder: the root is the **last** postorder value; build **right before left**."],
    variants=["Construct from inorder and postorder: take roots from the end; right subtree first.", "Maximum binary tree: monotonic stack or recursion on the maximum.", "Flatten to a linked list: preorder rewiring (right pointers).", "BST serialisation: preorder alone is enough (use value bounds to rebuild)."],
    notuse="If the tree is huge and memory is tight, stream the serialisation with an iterator instead of building the whole string.",
    problems=[
        (108, "Convert Sorted Array to Binary Search Tree", "E", "convert-sorted-array-to-binary-search-tree", "Middle as root, recurse on each half", "O(n) / O(log n)"),
        (105, "Construct Binary Tree from Preorder and Inorder Traversal", "M", "construct-binary-tree-from-preorder-and-inorder-traversal", "Preorder root + inorder split + index map", "O(n) / O(n)"),
        (106, "Construct Binary Tree from Inorder and Postorder Traversal", "M", "construct-binary-tree-from-inorder-and-postorder-traversal", "Roots from the end of postorder; build right first", "O(n) / O(n)"),
        (654, "Maximum Binary Tree", "M", "maximum-binary-tree", "Maximum as root; recurse (or monotonic stack)", "O(n) / O(n)"),
        (114, "Flatten Binary Tree to Linked List", "M", "flatten-binary-tree-to-linked-list", "Rewire preorder using the left subtree's rightmost node", "O(n) / O(1)"),
        (1008, "Construct Binary Search Tree from Preorder Traversal", "M", "construct-binary-search-tree-from-preorder-traversal", "Insert with an upper bound while consuming preorder", "O(n) / O(h)"),
        (449, "Serialize and Deserialize BST", "M", "serialize-and-deserialize-bst", "Preorder only; rebuild with bounds", "O(n) / O(n)"),
        (297, "Serialize and Deserialize Binary Tree", "H", "serialize-and-deserialize-binary-tree", "Preorder with null markers (or level order)", "O(n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 8
P.append(dict(
    title="Tree DP: return a tuple from each node", tier="sec", sim="robber", oneline="each subtree reports its best answer under every state",
    why="Generalises the path pattern to choices at each node", signature="LC 337 / 968",
    when="You decide something per node (rob it, put a camera on it) and the choices of neighbours interact.",
    detect="\"house robber III\" · \"binary tree cameras\" · \"maximum sum BST\" · \"split the tree to maximise a product\" · \"largest BST subtree\".",
    intuition="At each node you face a small decision, and the only thing that matters about each child subtree is the best result **for each state of the child**. So each node returns a tiny table, for example `[best if I skip this node, best if I take this node]`, and the parent combines the tables of its children. It is dynamic programming where the \"order\" is the tree itself.",
    brute="Trying every subset of nodes is exponential. Plain recursion that recomputes sub-results is O(2ⁿ) without memoisation. Returning the tuple computes each subtree once: O(n).",
    idea="Define the states, then write the transition: `take = val + skip(left) + skip(right)`; `skip = max(left) + max(right)`. Return `(skip, take)` and answer with `max` at the root.",
    steps=["List the states a node can be in (skip, take / covered, camera, needs cover).", "Write the value for each state using the children's tuples.", "Return the tuple from a post-order recursion.", "The answer is the best of the root's states."],
    trace_title="House Robber III on `3 → (2 → (·, 3), 3 → (·, 1))`",
    trace="""leaf 3 (under 2): skip 0, take 3
node 2: take 2+0 = 2; skip max(0,3) = 3      -> (3, 2)
leaf 1: skip 0, take 1
node 3 (right): take 3+0 = 3; skip 1         -> (1, 3)
root 3: take 3+3+1 = 7; skip 3+3 = 6
answer max(7, 6) = 7""",
    code=[("house robber III",
           """int[] dfs(TreeNode n) {                          // {skip, take}
    if (n == null) return new int[]{0, 0};
    int[] l = dfs(n.left), r = dfs(n.right);
    int take = n.val + l[0] + r[0];               // children must be skipped
    int skip = Math.max(l[0], l[1]) + Math.max(r[0], r[1]);
    return new int[]{skip, take};
}
// answer: max(dfs(root)[0], dfs(root)[1])""",
           """def rob(root):
    def dfs(n):                                  # returns (skip, take)
        if not n:
            return (0, 0)
        l, r = dfs(n.left), dfs(n.right)
        take = n.val + l[0] + r[0]               # children must be skipped
        skip = max(l) + max(r)
        return (skip, take)
    return max(dfs(root))"""),
          ("balanced check and total-sum product (return a number, record another)",
           """int height(TreeNode n) {                          // -1 signals "not balanced"
    if (n == null) return 0;
    int l = height(n.left); if (l < 0) return -1;
    int r = height(n.right); if (r < 0 || Math.abs(l - r) > 1) return -1;
    return 1 + Math.max(l, r);
}
// split the tree by removing one edge to maximise (sum1 * sum2):
long best = 0;
long sum(TreeNode n, long total) {
    if (n == null) return 0;
    long s = n.val + sum(n.left, total) + sum(n.right, total);
    best = Math.max(best, s * (total - s));
    return s;
}""",
           """def height(n):                                   # -1 signals "not balanced"
    if not n:
        return 0
    l = height(n.left)
    if l < 0: return -1
    r = height(n.right)
    if r < 0 or abs(l - r) > 1: return -1
    return 1 + max(l, r)

# split the tree by removing one edge to maximise sum1 * sum2:
best = 0
def sub(n, total):
    global best
    if not n:
        return 0
    s = n.val + sub(n.left, total) + sub(n.right, total)
    best = max(best, s * (total - s))
    return s""")],
    complexity="O(n) time, O(h) space.",
    traps=["Decide the state meanings precisely before coding (what does `skip` allow the child to do?).", "A child that is `null` must return the identity tuple (0, 0) or the right \"covered\" state.",
           "Binary tree cameras: three states (covered without camera, has camera, not covered); greedy placement on the parent of an uncovered leaf also works.", "Use `long` when multiplying large sums."],
    variants=["Maximum sum BST: return (isBST, min, max, sum) from each subtree.", "Sum of distances in a tree: two passes (down, then re-rooting).", "Longest path with different adjacent characters: record top two arms."],
    notuse="When choices do not interact between neighbours (a plain traversal suffices).",
    problems=[
        (337, "House Robber III", "M", "house-robber-iii", "Return (skip, take) from every node", "O(n) / O(h)"),
        (1339, "Maximum Product of Splitted Binary Tree", "M", "maximum-product-of-splitted-binary-tree", "Total sum first; each subtree sum s gives s × (total − s)", "O(n) / O(h)"),
        (968, "Binary Tree Cameras", "H", "binary-tree-cameras", "Three-state return, or greedy from the leaves", "O(n) / O(h)"),
        (1373, "Maximum Sum BST in Binary Tree", "H", "maximum-sum-bst-in-binary-tree", "Return (isBST, min, max, sum)", "O(n) / O(h)"),
        (834, "Sum of Distances in Tree", "H", "sum-of-distances-in-tree", "Subtree counts, then re-root with a second DFS", "O(n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 9
P.append(dict(
    title="Iterative traversals and O(1)-space walks", tier="sec", sim="iterinorder", oneline="an explicit stack replaces the call stack",
    why="Avoids stack overflow and powers the BST iterator", signature="LC 94 / 173",
    when="Recursion depth could be huge, you must produce nodes lazily (an iterator), or you need O(1) extra space.",
    detect="\"BST iterator\" · \"inorder without recursion\" · \"iterative postorder\" · \"O(1) space traversal\" · \"flatten in place\".",
    intuition="Recursion secretly keeps a stack of \"nodes whose left subtree I am still exploring\". Do the same by hand: dive left, pushing every node you pass. When you cannot go further left, pop the top (that node is next in inorder), visit it, and step into its right subtree. Morris traversal goes further: it temporarily threads a link from each node's inorder predecessor back to the node, so no stack is needed.",
    brute="Recursive traversal uses O(h) call-stack space and can overflow on skewed trees. The explicit stack has the same O(h) space but no overflow risk; Morris uses O(1) extra space.",
    idea="Inorder: `while cur != null or stack: while cur: push, cur = left; pop → visit; cur = node.right`. BST iterator: keep the same stack lazily; `next()` pops and pushes the left chain of the right child.",
    steps=["Dive left, pushing nodes.", "Pop a node and visit it.", "Move to its right child and repeat.", "Preorder: push right then left; postorder: reverse a modified preorder, or use two stacks."],
    trace_title="inorder of the BST `4 → (2 → (1, 3), 6 → (5, 7))`",
    trace="""push 4, 2, 1     pop 1 visit
pop 2 visit      go right -> push 3   pop 3 visit
pop 4 visit      go right -> push 6, 5   pop 5 visit
pop 6 visit      go right -> push 7   pop 7 visit
output 1 2 3 4 5 6 7""",
    code=[("iterative inorder and the BST iterator",
           """List<Integer> res = new ArrayList<>();
Deque<TreeNode> st = new ArrayDeque<>();
TreeNode cur = root;
while (cur != null || !st.isEmpty()) {
    while (cur != null) { st.push(cur); cur = cur.left; }     // dive left
    cur = st.pop();
    res.add(cur.val);                                          // visit
    cur = cur.right;                                           // then the right subtree
}

class BSTIterator {
    Deque<TreeNode> st = new ArrayDeque<>();
    BSTIterator(TreeNode root) { pushLeft(root); }
    void pushLeft(TreeNode n) { while (n != null) { st.push(n); n = n.left; } }
    int next() { TreeNode n = st.pop(); pushLeft(n.right); return n.val; }
    boolean hasNext() { return !st.isEmpty(); }
}""",
           """res, st, cur = [], [], root
while cur or st:
    while cur:
        st.append(cur)                                          # dive left
        cur = cur.left
    cur = st.pop()
    res.append(cur.val)                                         # visit
    cur = cur.right                                             # then the right subtree

class BSTIterator:
    def __init__(self, root):
        self.st = []
        self._push_left(root)
    def _push_left(self, n):
        while n:
            self.st.append(n)
            n = n.left
    def next(self):
        n = self.st.pop()
        self._push_left(n.right)
        return n.val
    def has_next(self):
        return bool(self.st)"""),
          ("Morris inorder traversal (O(1) extra space)",
           """TreeNode cur = root;
while (cur != null) {
    if (cur.left == null) { visit(cur); cur = cur.right; }
    else {
        TreeNode pre = cur.left;
        while (pre.right != null && pre.right != cur) pre = pre.right;   // inorder predecessor
        if (pre.right == null) { pre.right = cur; cur = cur.left; }       // thread back to cur
        else { pre.right = null; visit(cur); cur = cur.right; }          // remove the thread
    }
}""",
           """cur = root
while cur:
    if not cur.left:
        visit(cur)
        cur = cur.right
    else:
        pre = cur.left
        while pre.right and pre.right is not cur:
            pre = pre.right                                              # inorder predecessor
        if not pre.right:
            pre.right = cur                                              # thread back to cur
            cur = cur.left
        else:
            pre.right = None                                             # remove the thread
            visit(cur)
            cur = cur.right""")],
    complexity="O(n) time; O(h) space with a stack, O(1) with Morris (the tree is restored).",
    traps=["The inner `while (cur != null)` is required; a single `if` skips deep left chains.", "Iterator `next()` must push the left chain of the **right** child after popping.",
           "Morris must remove the thread on the second visit or the tree stays corrupted.", "Iterative postorder is trickiest: reverse of (node, right, left), or track the last visited node."],
    variants=["Iterative preorder: stack; push right child first so left is processed first.", "Leaf-similar trees: compare the leaf sequences produced lazily by two iterators.", "Convert BST to greater tree: reverse inorder (right, node, left) with a running sum."],
    notuse="When recursion depth is small and clarity matters more (plain recursion is fine).",
    problems=[
        (94, "Binary Tree Inorder Traversal", "E", "binary-tree-inorder-traversal", "Do it with the explicit stack loop", "O(n) / O(h)"),
        (872, "Leaf-Similar Trees", "E", "leaf-similar-trees", "Collect leaf sequences (or two lazy iterators) and compare", "O(n) / O(h)"),
        (145, "Binary Tree Postorder Traversal", "E", "binary-tree-postorder-traversal", "Iterative: reverse of (node, right, left)", "O(n) / O(h)"),
        (173, "Binary Search Tree Iterator", "M", "binary-search-tree-iterator", "Stack of the left chain; amortised O(1) next()", "O(1) amortised / O(h)"),
        (538, "Convert BST to Greater Tree", "M", "convert-bst-to-greater-tree", "Reverse inorder with a running total", "O(n) / O(h)"),
    ]))

TOPIC = dict(
    id="trees", file="09_trees.html", title="Binary Trees and BSTs — Pattern Guide",
    lead="Trees are recursion made visible. This guide covers thinking recursively on trees, depth-first traversals and path problems, level-order BFS, the \"record one value, return another\" path pattern, binary search trees, lowest common ancestors, constructing and serialising trees, tree dynamic programming and iterative traversals. Each pattern has the intuition, a step-through animation that draws the tree, Java and Python code, and a ladder of LeetCode problems.",
    mindset="Every tree problem is the same three questions: **what do I do at the null case**, **what do I need from my two children**, and **what do I return to my parent**? Decide whether the answer flows **down** (pass state as arguments), **up** (return values) or **across** levels (BFS), and remember that a BST gives you an extra gift: inorder is sorted.",
    qintro="Ask these questions on every tree problem:",
    questions=["**What is the answer for an empty tree?** → the base case.", "**What do I need from the left and right subtrees?** → the return value.",
               "**Is information passed down (bounds, sum so far) or up (height, gain)?**", "**Do I need levels or shortest depth?** → BFS with a queue.", "**Is it a BST?** → use ordering (inorder, bounds, go left/right)."],
    cues=[
        ["\"height\", \"same tree\", \"invert\", \"balanced\", \"diameter\"", "**P1** Recursive thinking"],
        ["\"traversal order\", \"path sum\", \"all paths\"", "**P2** DFS and root-to-leaf paths"],
        ["\"level order\", \"right side view\", \"minimum depth\"", "**P3** BFS"],
        ["\"maximum path sum\", \"longest path that may bend\"", "**P4** Record vs return"],
        ["\"BST\", \"validate\", \"kth smallest\", \"insert / delete\"", "**P5** BST operations"],
        ["\"lowest common ancestor\", \"distance between nodes\"", "**P6** LCA"],
        ["\"construct from traversals\", \"serialize\"", "**P7** Construct and serialise"],
        ["\"rob\", \"cameras\", choices per node", "**P8** Tree DP"],
        ["\"iterator\", \"without recursion\", \"O(1) space\"", "**P9** Iterative traversals"],
    ],
    choose=[
        ["A property of the whole tree from its subtrees", "Post-order recursion (P1)"],
        ["State flows down from ancestors", "DFS with parameters (P2)"],
        ["Group by depth or find nearest leaf", "BFS (P3)"],
        ["Best path that can turn at a node", "Record and return (P4)"],
        ["Ordered data in a tree", "BST ordering (P5)"],
        ["Where two nodes' paths meet", "LCA recursion (P6)"],
        ["Rebuild a tree", "Preorder root + inorder split (P7)"],
        ["Choices that interact along edges", "Tuple-returning DP (P8)"],
        ["Avoid recursion depth issues", "Explicit stack or Morris (P9)"],
    ],
    rule="if the answer for a node depends on its **children**, recurse and return; if it depends on its **ancestors**, pass it down; if it is about **levels**, use a queue; if the tree is a **BST**, use its order.",
    selftest=[
        ("Why is the time complexity of most tree recursions O(n) and the space O(h)?", "Each node is visited once, and the recursion stack holds one frame per level of the current path, so its depth is the height of the tree."),
        ("In maximum path sum, why do we return `node + max(l, r)` but record `node + l + r`?", "A path that bends at the node uses both arms, but the parent can extend only one arm of this node, so only one arm can be returned."),
        ("How do you validate a BST correctly?", "Carry `(low, high)` bounds down so every node is compared with all its ancestors, or check that an inorder traversal is strictly increasing."),
        ("Why does inorder traversal of a BST give sorted order?", "Left subtree values are smaller than the node and right subtree values are larger, so visiting left, node, right always lists values in ascending order."),
        ("In the LCA recursion, when is a node the answer?", "When both subtree calls return non-null (one target on each side), or when the node itself is a target and the other target is below it."),
        ("Which two traversals determine a binary tree uniquely?", "Inorder together with preorder, or inorder together with postorder (for unique values). Preorder and postorder alone are ambiguous in general."),
        ("Why must `size = q.size()` be read before the inner loop in level-order traversal?", "The queue grows while you add children, so the size must be fixed at the start of the round to know where the level ends."),
        ("What is the idea of the tree-DP pair (skip, take)?", "Each subtree reports its best result for each state of its root, and the parent combines the children's reports according to which states are compatible."),
    ],
    plan=[
        "**Day 1:** base case and return-value recursion: depth, same tree, invert, symmetric, balanced, diameter.",
        "**Day 2:** DFS traversals and root-to-leaf path problems; Path Sum I–III.",
        "**Day 3:** BFS level-order and its variations; write the template from memory.",
        "**Day 4:** BST operations and validation; kth smallest and recover BST.",
        "**Day 5:** LCA, construct-from-traversals and serialisation.",
        "**Day 6:** path-sum-with-bending (LC 124), tree DP (house robber III), and the iterative traversals.",
    ],
    patterns=P,
)
