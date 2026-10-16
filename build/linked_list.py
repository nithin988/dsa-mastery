"""Content for topic 04: Linked lists."""

P = []

# ---------------------------------------------------------------- 1
P.append(dict(
    title="Pointer basics and the dummy node", tier="hot", sim="delete", oneline="a dummy head removes every special case",
    why="Every linked-list problem starts with safe traversal, insertion and deletion", signature="LC 203 / 82",
    when="You insert, delete or rebuild nodes, especially when the head itself might change.",
    detect="\"remove all nodes with value\" · \"delete duplicates\" · \"insert into a sorted list\" · any code with `if (head == null)` special cases.",
    intuition="A linked list is a treasure hunt: each node only knows where the **next** clue is. To remove a node you must stand on the node **before** it and re-point its arrow past the target. If the target can be the very first node, there is nobody to stand on: so put a fake node (dummy) in front and the first node is no longer special.",
    brute="Without a dummy you write one branch for \"head needs removing\" and another for the middle, and bugs hide in the first. With a dummy there is a single loop and `dummy.next` is always the answer.",
    idea="Keep `prev` on the node before the candidate. If `prev.next` must go, do `prev.next = prev.next.next` and **do not move prev**; otherwise advance `prev`.",
    steps=["`dummy = new ListNode(0, head)`, `prev = dummy`.", "While `prev.next != null`: look at `prev.next`.", "If it matches, unlink it. Otherwise `prev = prev.next`.", "Return `dummy.next`."],
    trace_title="remove 6 from `1 → 6 → 3 → 6`",
    trace="""D -> 1 -> 6 -> 3 -> 6 -> null
prev=D   next=1  keep    prev=1
prev=1   next=6  remove  1 -> 3     (prev stays)
prev=1   next=3  keep    prev=3
prev=3   next=6  remove  3 -> null
result D -> 1 -> 3 -> null""",
    code=[("remove all nodes with a given value",
           """ListNode dummy = new ListNode(0, head), prev = dummy;
while (prev.next != null) {
    if (prev.next.val == val) prev.next = prev.next.next;   // unlink, stay put
    else prev = prev.next;
}
return dummy.next;""",
           """dummy = ListNode(0, head)
prev = dummy
while prev.next:
    if prev.next.val == val:
        prev.next = prev.next.next          # unlink, stay put
    else:
        prev = prev.next
return dummy.next"""),
          ("insert after a node (order of the two assignments matters)",
           """ListNode node = new ListNode(x);
node.next = prev.next;     // 1) new node points to the old next FIRST
prev.next = node;          // 2) then the previous node points to the new node""",
           """node = ListNode(x)
node.next = prev.next      # 1) new node points to the old next FIRST
prev.next = node           # 2) then the previous node points to the new node""")],
    complexity="O(n) time, O(1) space.",
    traps=["Assigning `prev.next = node` before `node.next = prev.next` loses the rest of the list.", "After deleting, **do not** advance `prev`: the new `prev.next` has not been examined.",
           "Check `null` before dereferencing: `cur.next.next` needs `cur.next != null`.", "Sorted duplicates II (remove every value that repeats): skip the whole run and link `prev` past it."],
    variants=["Delete a node given only that node (LC 237): copy the next node's value into it and skip the next node.", "Remove duplicates from a sorted list: compare `cur` with `cur.next`.", "Insert into a sorted list: find the last node smaller than the value."],
    notuse="When you need random access by index (use an array), or the structure never changes.",
    problems=[
        (203, "Remove Linked List Elements", "E", "remove-linked-list-elements", "Dummy head; unlink matches without advancing prev", "O(n) / O(1)"),
        (83, "Remove Duplicates from Sorted List", "E", "remove-duplicates-from-sorted-list", "If cur.val == cur.next.val skip the next node", "O(n) / O(1)"),
        (237, "Delete Node in a Linked List", "M", "delete-node-in-a-linked-list", "Copy next value into this node, then unlink the next", "O(1) / O(1)"),
        (707, "Design Linked List", "M", "design-linked-list", "Implement get, addAtHead, addAtIndex, deleteAtIndex with a dummy head", "O(n) / O(1)"),
        (82, "Remove Duplicates from Sorted List II", "M", "remove-duplicates-from-sorted-list-ii", "Dummy head; skip entire runs of repeated values", "O(n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 2
P.append(dict(
    title="Reversing a linked list", tier="hot", sim="reverse", oneline="flip each arrow as you walk: prev, cur, next",
    why="The building block of half the linked-list questions", signature="LC 206 / 92",
    when="Reverse all of a list, a sub-range, or groups of k; or you need to read the list backwards without extra memory.",
    detect="\"reverse\" · \"reverse between positions\" · \"reverse in groups of k\" · \"swap pairs\" · palindrome and reorder problems (as a step).",
    intuition="A line of people each pointing at the next. To reverse it, walk along and make every person point at the one **behind** them instead. You need three fingers: one on the person you are fixing (`cur`), one on the person behind (`prev`), and one remembering who was next (`nxt`) before you break that link.",
    brute="Copy values into an array and rewrite them: O(n) extra space. Re-pointing arrows in place needs only three pointers: O(1) space.",
    idea="Iterate once. For each node save `nxt = cur.next`, set `cur.next = prev`, then slide `prev = cur`, `cur = nxt`. When `cur` is null, `prev` is the new head.",
    steps=["`prev = null`, `cur = head`.", "Save `nxt = cur.next`.", "Flip: `cur.next = prev`.", "Advance: `prev = cur`, `cur = nxt`. Repeat; return `prev`."],
    trace_title="reverse `1 → 2 → 3`",
    trace="""prev=null cur=1: nxt=2, 1.next=null   prev=1 cur=2
prev=1    cur=2: nxt=3, 2.next=1      prev=2 cur=3
prev=2    cur=3: nxt=null, 3.next=2   prev=3 cur=null
return prev = 3 -> 2 -> 1 -> null""",
    code=[("iterative and recursive reversal",
           """// iterative: O(n) time, O(1) space
ListNode reverse(ListNode head) {
    ListNode prev = null, cur = head;
    while (cur != null) {
        ListNode nxt = cur.next;
        cur.next = prev;
        prev = cur;
        cur = nxt;
    }
    return prev;
}
// recursive: O(n) time, O(n) stack
ListNode reverseRec(ListNode head) {
    if (head == null || head.next == null) return head;
    ListNode newHead = reverseRec(head.next);
    head.next.next = head;      // the node after me now points back to me
    head.next = null;
    return newHead;
}""",
           """def reverse(head):                    # iterative: O(n) time, O(1) space
    prev, cur = None, head
    while cur:
        nxt = cur.next
        cur.next = prev
        prev, cur = cur, nxt
    return prev

def reverse_rec(head):                # recursive: O(n) time, O(n) stack
    if not head or not head.next:
        return head
    new_head = reverse_rec(head.next)
    head.next.next = head             # the node after me now points back to me
    head.next = None
    return new_head"""),
          ("reverse positions left..right (head insertion)",
           """ListNode dummy = new ListNode(0, head), prev = dummy;
for (int i = 1; i < left; i++) prev = prev.next;      // node before the range
ListNode cur = prev.next;
for (int i = 0; i < right - left; i++) {
    ListNode nxt = cur.next;
    cur.next = nxt.next;       // detach nxt
    nxt.next = prev.next;      // put it at the front of the range
    prev.next = nxt;
}
return dummy.next;""",
           """dummy = ListNode(0, head)
prev = dummy
for _ in range(left - 1):
    prev = prev.next                  # node before the range
cur = prev.next
for _ in range(right - left):
    nxt = cur.next
    cur.next = nxt.next               # detach nxt
    nxt.next = prev.next              # put it at the front of the range
    prev.next = nxt
return dummy.next""")],
    complexity="O(n) time; O(1) space iteratively, O(n) stack recursively.",
    traps=["Save `cur.next` **before** overwriting it, or the rest of the list is lost.", "The reversed list's tail must end with `null` (`head.next = null` in the recursive version).",
           "Reverse-in-groups-of-k: check that k nodes remain before reversing, and reconnect the group's old head to the next group's new head.", "Use a dummy node for sub-range reversal so `left = 1` works."],
    variants=["Reverse nodes in k-group: reverse each full block, link blocks together.", "Swap nodes in pairs: reversal with k = 2.", "Reverse a list in two stacks or recursion only when space is allowed."],
    notuse="When the list is doubly linked (swap `prev` and `next` pointers instead) or you only need to read values (use an array or recursion).",
    problems=[
        (206, "Reverse Linked List", "E", "reverse-linked-list", "prev / cur / nxt iterative loop", "O(n) / O(1)"),
        (24, "Swap Nodes in Pairs", "M", "swap-nodes-in-pairs", "Reverse each pair behind a dummy head", "O(n) / O(1)"),
        (92, "Reverse Linked List II", "M", "reverse-linked-list-ii", "Move nodes one by one to the front of the sub-range", "O(n) / O(1)"),
        (2130, "Maximum Twin Sum of a Linked List", "M", "maximum-twin-sum-of-a-linked-list", "Reverse the second half, then pair nodes", "O(n) / O(1)"),
        (25, "Reverse Nodes in k-Group", "H", "reverse-nodes-in-k-group", "Reverse each group of k and reconnect the blocks", "O(n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 3
P.append(dict(
    title="Fast and slow pointers (middle and cycles)", tier="hot", sim="floyd", oneline="tortoise and hare: one runs twice as fast",
    why="Detects cycles and finds middles without extra memory", signature="LC 141 / 876 / 142",
    when="Find the middle, detect a cycle, find where a cycle begins, or detect repetition in a sequence.",
    detect="\"middle of the list\" · \"has a cycle\" · \"where does the cycle begin\" · \"happy number\" · \"find the duplicate\".",
    intuition="Two runners on a track. If the track is a straight line, the fast runner reaches the end first, and when it does the slow one is exactly halfway. If the track is a loop, the fast runner keeps lapping and must eventually catch the slow runner from behind, because it gains one step per move.",
    brute="Store every visited node in a hash set to detect a repeat: O(n) extra space. Floyd's tortoise and hare uses two pointers and O(1) space.",
    idea="`slow` moves 1, `fast` moves 2. If `fast` reaches null: no cycle, and `slow` is the middle. If they meet: a cycle. To find its start, restart one pointer at the head and move both one step at a time; they meet at the cycle's first node.",
    steps=["`slow = fast = head`.", "While `fast != null && fast.next != null`: `slow = slow.next`, `fast = fast.next.next`.", "If `slow == fast`: a cycle. Reset `slow = head`; advance both by 1 until equal; that node is the cycle start.", "If the loop ends, no cycle. `slow` is the middle (the second middle for even length)."],
    trace_title="`3 → 2 → 0 → −4 → (back to 2)`",
    trace="""slow=3  fast=3
slow=2  fast=0
slow=0  fast=2
slow=-4 fast=-4   meet -> cycle exists
reset slow to head: slow=3 fast=-4
slow=2  fast=2    meet -> cycle starts at node 2""",
    code=[("detect a cycle and find its start",
           """ListNode slow = head, fast = head;
while (fast != null && fast.next != null) {
    slow = slow.next;
    fast = fast.next.next;
    if (slow == fast) {                  // cycle found
        slow = head;
        while (slow != fast) { slow = slow.next; fast = fast.next; }
        return slow;                     // first node of the cycle
    }
}
return null;                             // no cycle""",
           """slow = fast = head
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next
    if slow is fast:                     # cycle found
        slow = head
        while slow is not fast:
            slow = slow.next
            fast = fast.next
        return slow                      # first node of the cycle
return None                              # no cycle"""),
          ("middle of the list",
           """ListNode slow = head, fast = head;
while (fast != null && fast.next != null) { slow = slow.next; fast = fast.next.next; }
return slow;        // for even length this is the second middle""",
           """slow = fast = head
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next
return slow         # for even length this is the second middle""")],
    complexity="O(n) time, O(1) space.",
    traps=["Loop condition must check both `fast != null` **and** `fast.next != null` before `fast.next.next`.", "Compare nodes with `==` / `is`, not values: duplicate values are normal.",
           "For even-length lists decide which middle you need; start `fast = head.next` to get the first middle.", "Floyd needs a successor function, not necessarily a list: it also works on `x → f(x)` sequences."],
    variants=["Happy number: the digit-square sequence either reaches 1 or enters a cycle.", "Find the duplicate in an array of n+1 numbers in 1..n: treat `i → a[i]` as a linked list with a cycle.", "Cycle length: after meeting, walk one pointer around until it returns."],
    notuse="When extra memory is allowed and clarity matters more (a `HashSet` of visited nodes is simpler), or the structure is a tree or DAG.",
    problems=[
        (876, "Middle of the Linked List", "E", "middle-of-the-linked-list", "slow 1 step, fast 2 steps; slow is the middle", "O(n) / O(1)"),
        (141, "Linked List Cycle", "E", "linked-list-cycle", "If fast catches slow, there is a cycle", "O(n) / O(1)"),
        (202, "Happy Number", "E", "happy-number", "Floyd on the digit-square sequence", "O(log n) / O(1)"),
        (142, "Linked List Cycle II", "M", "linked-list-cycle-ii", "Reset one pointer to head after the meeting; step together", "O(n) / O(1)"),
        (287, "Find the Duplicate Number", "M", "find-the-duplicate-number", "Treat i → a[i] as next pointers; find the cycle start", "O(n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 4
P.append(dict(
    title="Merging and sorting lists", tier="hot", sim="merge", oneline="a dummy tail collects the smaller head each time",
    why="Merge is the heart of merge sort, k-way merge and many \"combine\" questions", signature="LC 21 / 148 / 23",
    when="Combine sorted lists, or sort a list efficiently.",
    detect="\"merge two sorted lists\" · \"merge k sorted lists\" · \"sort a linked list\" · \"insertion sort list\".",
    intuition="Two queues of people already in height order, merging into one line at a door: look at the two people at the front of each queue and let the shorter one through. You never need to look past the fronts, and you reuse the people (nodes) without copying.",
    brute="Dump all values into an array, sort and rebuild: O(n log n) time and O(n) extra space. Merging sorted lists directly reuses nodes in O(n) time and O(1) space.",
    idea="Keep a `tail` on a dummy node. Compare the two heads, link the smaller to `tail`, advance that list and `tail`. When one list ends, attach the other in one step. Merge sort on a list = split at the middle, sort both halves, merge.",
    steps=["`dummy = new ListNode()`, `tail = dummy`.", "While both lists are non-empty: link the smaller head to `tail`; advance that list and `tail`.", "`tail.next = (a != null) ? a : b`.", "Return `dummy.next`. For k lists use a min-heap of heads or merge pairs (divide and conquer)."],
    trace_title="merge `1→2→4` and `1→3→4`",
    trace="""1 vs 1 -> take list1's 1      1
2 vs 1 -> take list2's 1      1 1
2 vs 3 -> take 2              1 1 2
4 vs 3 -> take 3              1 1 2 3
4 vs 4 -> take list1's 4      1 1 2 3 4
list1 empty -> attach rest 4  1 1 2 3 4 4""",
    code=[("merge two sorted lists",
           """ListNode dummy = new ListNode(), tail = dummy;
while (a != null && b != null) {
    if (a.val <= b.val) { tail.next = a; a = a.next; }
    else { tail.next = b; b = b.next; }
    tail = tail.next;
}
tail.next = (a != null) ? a : b;       // attach whatever is left
return dummy.next;""",
           """dummy = tail = ListNode()
while a and b:
    if a.val <= b.val:
        tail.next, a = a, a.next
    else:
        tail.next, b = b, b.next
    tail = tail.next
tail.next = a or b                      # attach whatever is left
return dummy.next"""),
          ("merge sort a list (split at the middle, sort, merge)",
           """ListNode sortList(ListNode head) {
    if (head == null || head.next == null) return head;
    ListNode slow = head, fast = head.next;              // fast starts one ahead: slow ends at the first half's tail
    while (fast != null && fast.next != null) { slow = slow.next; fast = fast.next.next; }
    ListNode mid = slow.next;
    slow.next = null;                                    // cut into two lists
    return merge(sortList(head), sortList(mid));
}""",
           """def sort_list(head):
    if not head or not head.next:
        return head
    slow, fast = head, head.next                         # slow ends at the first half's tail
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    mid, slow.next = slow.next, None                     # cut into two lists
    return merge(sort_list(head), sort_list(mid))"""),
          ("merge k sorted lists with a min-heap",
           """PriorityQueue<ListNode> pq = new PriorityQueue<>((x, y) -> x.val - y.val);
for (ListNode l : lists) if (l != null) pq.add(l);
ListNode dummy = new ListNode(), tail = dummy;
while (!pq.isEmpty()) {
    ListNode n = pq.poll();
    tail.next = n; tail = n;
    if (n.next != null) pq.add(n.next);
}
return dummy.next;""",
           """import heapq
heap = [(l.val, i, l) for i, l in enumerate(lists) if l]   # i breaks ties (nodes are not comparable)
heapq.heapify(heap)
dummy = tail = ListNode()
while heap:
    _, i, n = heapq.heappop(heap)
    tail.next = n
    tail = n
    if n.next:
        heapq.heappush(heap, (n.next.val, i, n.next))
return dummy.next""")],
    complexity="Merge two: O(n + m) time, O(1) space. Sort list: O(n log n) time, O(log n) stack. Merge k: O(N log k) with a heap.",
    traps=["Use `<=` when comparing to keep the merge stable.", "Cut the list (`slow.next = null`) before recursing, or the halves overlap forever.",
           "Python heaps compare tuples: add an index tiebreaker, because `ListNode` objects are not orderable.", "Do not forget `tail.next = remaining`; one list usually has nodes left."],
    variants=["Merge k lists by pairs (divide and conquer): O(N log k) with O(1) extra space.", "Insertion sort on a list: O(n²) but simple.", "Merge in place into the first array (LC 88 uses the back-to-front trick)."],
    notuse="Unsorted inputs (sort first), or when a random-access array with a built-in sort is allowed.",
    problems=[
        (21, "Merge Two Sorted Lists", "E", "merge-two-sorted-lists", "Dummy tail, take the smaller head, attach the rest", "O(n + m) / O(1)"),
        (147, "Insertion Sort List", "M", "insertion-sort-list", "Insert each node into a growing sorted prefix", "O(n²) / O(1)"),
        (148, "Sort List", "M", "sort-list", "Split at the middle, sort halves, merge", "O(n log n) / O(log n)"),
        (23, "Merge k Sorted Lists", "H", "merge-k-sorted-lists", "Min-heap of heads or merge pairs", "O(N log k) / O(k)"),
    ]))

# ---------------------------------------------------------------- 5
P.append(dict(
    title="Runner gap: nth from end, intersection, rotate", tier="hot", sim="nth", oneline="keep a fixed distance between two pointers",
    why="Gives positions from the end in one pass", signature="LC 19 / 160",
    when="You need the kth node from the end, a position relative to the tail, or the node where two lists join.",
    detect="\"remove the nth node from the end\" · \"intersection of two lists\" · \"rotate list by k\" · \"delete the middle\".",
    intuition="Two people walking with a rope of fixed length between them. When the front person reaches the end, the rear person stands exactly that rope-length from the end. You learn a position counted from the **back** while walking only once from the front.",
    brute="Walk once to count the length, then walk again to length − n: two passes. A fixed gap between two pointers finds it in one pass.",
    idea="Advance `fast` n steps ahead, then move `fast` and `slow` together. When `fast` is on the last node, `slow` is right before the node to remove (use a dummy head so removing the first node works).",
    steps=["Dummy head; `slow = fast = dummy`.", "Move `fast` forward `n` times.", "Move both until `fast.next == null`.", "`slow.next = slow.next.next`; return `dummy.next`."],
    trace_title="remove the 2nd from the end of `1→2→3→4→5`",
    trace="""D 1 2 3 4 5
fast moves 2:   slow=D        fast=2
move together:  slow=1 fast=3 -> slow=2 fast=4 -> slow=3 fast=5
fast.next is null, slow=3 is the node before the target
3.next = 3.next.next   =>  1 → 2 → 3 → 5""",
    code=[("remove the nth node from the end",
           """ListNode dummy = new ListNode(0, head), slow = dummy, fast = dummy;
for (int i = 0; i < n; i++) fast = fast.next;            // build the gap
while (fast.next != null) { fast = fast.next; slow = slow.next; }
slow.next = slow.next.next;                              // delete
return dummy.next;""",
           """dummy = ListNode(0, head)
slow = fast = dummy
for _ in range(n):
    fast = fast.next                                     # build the gap
while fast.next:
    fast, slow = fast.next, slow.next
slow.next = slow.next.next                               # delete
return dummy.next"""),
          ("intersection of two lists (switch heads at the end)",
           """ListNode a = headA, b = headB;
while (a != b) {
    a = (a == null) ? headB : a.next;     // after A ends, continue down B
    b = (b == null) ? headA : b.next;     // after B ends, continue down A
}
return a;                                 // intersection node, or null if none""",
           """a, b = headA, headB
while a is not b:
    a = headB if a is None else a.next    # after A ends, continue down B
    b = headA if b is None else b.next    # after B ends, continue down A
return a                                  # intersection node, or None if none""")],
    complexity="O(n) time, O(1) space.",
    traps=["Without a dummy head, deleting the first node (n equals the length) crashes.", "Stop when `fast.next == null`, not `fast == null`, or `slow` lands on the target instead of before it.",
           "Intersection compares node **identity**, not values.", "Rotate by k: take `k % length`, find the new tail at `length − k − 1`, cut and re-attach."],
    variants=["Rotate list: make the list circular, then break it at `length − k`.", "Swap the kth node from the start with the kth from the end: two pointers and a swap of values.", "Delete the middle node: fast and slow with `prev`."],
    notuse="When the length is already known (index directly) or the list is doubly linked with a tail pointer (walk back).",
    problems=[
        (160, "Intersection of Two Linked Lists", "E", "intersection-of-two-linked-lists", "Switch to the other head at the end so both walk equal distances", "O(n + m) / O(1)"),
        (19, "Remove Nth Node From End of List", "M", "remove-nth-node-from-end-of-list", "Fixed gap of n between fast and slow", "O(n) / O(1)"),
        (2095, "Delete the Middle Node of a Linked List", "M", "delete-the-middle-node-of-a-linked-list", "Fast / slow with a trailing prev", "O(n) / O(1)"),
        (1721, "Swapping Nodes in a Linked List", "M", "swapping-nodes-in-a-linked-list", "Find the kth from start; gap trick finds the kth from end", "O(n) / O(1)"),
        (61, "Rotate List", "M", "rotate-list", "Close into a ring, cut at length − k % length", "O(n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 6
P.append(dict(
    title="Split, reverse, merge (palindrome and reorder)", tier="sec", sim="palilist", oneline="find the middle, reverse the half, compare or interleave",
    why="Combines three earlier patterns into the classic O(1)-space list question", signature="LC 234 / 143",
    when="You must compare the front of the list with the back, or interleave front and back nodes, without extra space.",
    detect="\"palindrome linked list\" · \"reorder list L0→Ln→L1→Ln−1\" · \"twin sum\" · \"compare first half with second half\".",
    intuition="You cannot walk a singly linked list backwards. So fold it like a sheet of paper: find the middle, flip the second half so it runs backwards, and now both halves can be walked forward at the same time, meeting at the fold.",
    brute="Copy values to an array and use two indices: O(n) time and O(n) space. Splitting and reversing in place keeps the extra space at O(1).",
    idea="Three steps you already know: (1) fast/slow to find the middle, (2) reverse the second half, (3) walk both halves together to compare (palindrome) or interleave (reorder).",
    steps=["Fast/slow: stop with `slow` at the end of the first half.", "`second = reverse(slow.next)`; cut with `slow.next = null` if you need two lists.", "Walk `p` over the first half and `q` over the reversed second half together.", "Compare values, or alternate nodes (`a.next = b; b.next = aNext`)."],
    trace_title="`1 → 2 → 3 → 2 → 1`",
    trace="""middle = 3
second half 2 -> 1 reversed = 1 -> 2
compare 1=1, 2=2 -> palindrome""",
    code=[("palindrome list",
           """if (head == null || head.next == null) return true;
ListNode slow = head, fast = head;
while (fast.next != null && fast.next.next != null) { slow = slow.next; fast = fast.next.next; }
ListNode p = head, q = reverse(slow.next);          // reverse() from pattern 2
while (q != null) {
    if (p.val != q.val) return false;
    p = p.next; q = q.next;
}
return true;""",
           """if not head or not head.next:
    return True
slow = fast = head
while fast.next and fast.next.next:
    slow, fast = slow.next, fast.next.next
p, q = head, reverse(slow.next)                    # reverse() from pattern 2
while q:
    if p.val != q.val:
        return False
    p, q = p.next, q.next
return True"""),
          ("reorder list L0 → Ln → L1 → Ln−1 → …",
           """ListNode slow = head, fast = head;
while (fast.next != null && fast.next.next != null) { slow = slow.next; fast = fast.next.next; }
ListNode b = reverse(slow.next);
slow.next = null;                                    // cut the first half off
ListNode a = head;
while (b != null) {
    ListNode an = a.next, bn = b.next;
    a.next = b; b.next = an;                         // interleave
    a = an; b = bn;
}""",
           """slow = fast = head
while fast.next and fast.next.next:
    slow, fast = slow.next, fast.next.next
b = reverse(slow.next)
slow.next = None                                     # cut the first half off
a = head
while b:
    an, bn = a.next, b.next
    a.next, b.next = b, an                           # interleave
    a, b = an, bn""")],
    complexity="O(n) time, O(1) extra space.",
    traps=["Which middle? Use `fast.next != null && fast.next.next != null` so `slow` is the end of the first half (and the exact middle for odd length).", "Cut the list before interleaving or you create a cycle.",
           "Palindrome compare loops over the **shorter** (reversed) half; the middle node of odd lists is ignored.", "Mention restoring the list if mutation is not allowed."],
    variants=["Maximum twin sum: same reversed-half walk, tracking the max pair sum.", "Add Two Numbers II (digits not reversed): reverse both, add, reverse back (or use stacks)."],
    notuse="When extra O(n) memory is fine (an array copy is simpler) or the list is doubly linked (compare from both ends directly).",
    problems=[
        (234, "Palindrome Linked List", "E", "palindrome-linked-list", "Middle, reverse the second half, compare", "O(n) / O(1)"),
        (143, "Reorder List", "M", "reorder-list", "Middle, reverse the second half, interleave", "O(n) / O(1)"),
        (2130, "Maximum Twin Sum of a Linked List", "M", "maximum-twin-sum-of-a-linked-list", "Reverse the second half; pair node i with node n−1−i", "O(n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 7
P.append(dict(
    title="Rearranging and arithmetic with two chains", tier="sec", sim="addnum", oneline="build separate chains, then stitch them together",
    why="Teaches careful pointer bookkeeping with several live lists", signature="LC 2 / 328 / 86",
    when="Add numbers digit by digit, or split nodes into groups and join the groups.",
    detect="\"add two numbers\" · \"odd even linked list\" · \"partition list around x\" · \"split into parts\".",
    intuition="Sorting laundry into two baskets while walking along the list: each node goes onto the end of one of two chains (using a tail pointer for each). At the end you hang the second chain on the tail of the first. For addition, walk both lists together doing grade-school addition with a carry.",
    brute="Copy values into arrays, rearrange, rebuild: O(n) extra space. Rewiring nodes keeps O(1) extra space.",
    idea="Create one dummy head and one tail pointer per output chain. Append each node to the right chain, finish by terminating the last chain (`tail.next = null`) and linking chain A to chain B.",
    steps=["Make dummy heads and tails for each output chain.", "For each node decide its chain and append it: `tail.next = node; tail = node`.", "Terminate the last chain with `null` to avoid cycles.", "Link the first chain's tail to the second chain's dummy head `.next`."],
    trace_title="add `2→4→3` and `5→6→4` (342 + 465)",
    trace="""2+5+0 = 7  carry 0
4+6+0 = 10 digit 0 carry 1
3+4+1 = 8  carry 0
result 7 -> 0 -> 8   (807)""",
    code=[("add two numbers stored in reverse",
           """ListNode dummy = new ListNode(), tail = dummy;
int carry = 0;
while (a != null || b != null || carry > 0) {
    int sum = carry + (a != null ? a.val : 0) + (b != null ? b.val : 0);
    tail.next = new ListNode(sum % 10);
    tail = tail.next;
    carry = sum / 10;
    if (a != null) a = a.next;
    if (b != null) b = b.next;
}
return dummy.next;""",
           """dummy = tail = ListNode()
carry = 0
while a or b or carry:
    total = carry + (a.val if a else 0) + (b.val if b else 0)
    tail.next = ListNode(total % 10)
    tail = tail.next
    carry = total // 10
    a = a.next if a else None
    b = b.next if b else None
return dummy.next"""),
          ("partition list around x (two chains)",
           """ListNode lessD = new ListNode(), geD = new ListNode(), l = lessD, g = geD;
for (ListNode p = head; p != null; p = p.next) {
    if (p.val < x) { l.next = p; l = p; }
    else { g.next = p; g = p; }
}
g.next = null;              // IMPORTANT: end the second chain
l.next = geD.next;          // stitch chains together
return lessD.next;""",
           """less_d, ge_d = ListNode(), ListNode()
l, g = less_d, ge_d
p = head
while p:
    if p.val < x:
        l.next = p
        l = p
    else:
        g.next = p
        g = p
    p = p.next
g.next = None               # IMPORTANT: end the second chain
l.next = ge_d.next          # stitch chains together
return less_d.next"""),
          ("odd-even list (odd positions first, then even positions)",
           """if (head == null) return head;
ListNode odd = head, even = head.next, evenHead = even;
while (even != null && even.next != null) {
    odd.next = even.next;  odd = odd.next;
    even.next = odd.next;  even = even.next;
}
odd.next = evenHead;
return head;""",
           """if not head:
    return head
odd, even, even_head = head, head.next, head.next
while even and even.next:
    odd.next = even.next
    odd = odd.next
    even.next = odd.next
    even = even.next
odd.next = even_head
return head""")],
    complexity="O(n) time, O(1) extra space (O(max(n, m)) for new digit nodes in addition).",
    traps=["Forgetting `g.next = null` after partitioning leaves a cycle or stale tail.", "Keep looping while `carry > 0` so a final carry (999 + 1) creates a new node.",
           "Odd-even groups by **position**, not by value.", "Never lose the head of a chain: keep a dummy, return its `.next`."],
    variants=["Add Two Numbers II (most significant digit first): use stacks or reverse first.", "Split list in k parts: compute base size and remainder.", "Flatten a multilevel doubly linked list: stack or recursion on child pointers."],
    notuse="When values (not nodes) can be moved freely and extra memory is acceptable.",
    problems=[
        (2, "Add Two Numbers", "M", "add-two-numbers", "Digit-by-digit with a carry, new node per digit", "O(max(n, m)) / O(max(n, m))"),
        (328, "Odd Even Linked List", "M", "odd-even-linked-list", "Two interleaved chains, joined at the end", "O(n) / O(1)"),
        (86, "Partition List", "M", "partition-list", "Two chains (< x and ≥ x), stitch them", "O(n) / O(1)"),
        (445, "Add Two Numbers II", "M", "add-two-numbers-ii", "Push digits on stacks (or reverse) and add from the end", "O(n + m) / O(n + m)"),
        (430, "Flatten a Multilevel Doubly Linked List", "M", "flatten-a-multilevel-doubly-linked-list", "Splice child lists in using a stack or recursion", "O(n) / O(depth)"),
    ]))

# ---------------------------------------------------------------- 8
P.append(dict(
    title="Doubly linked list + hash map (LRU design)", tier="hot", sim="lru", oneline="map finds the node, list keeps the order, both in O(1)",
    why="LRU cache is one of the most-asked design questions", signature="LC 146",
    when="You need O(1) lookup **and** O(1) reordering or removal by recency or frequency.",
    detect="\"LRU cache\" · \"LFU cache\" · \"browser history\" · \"copy a list with random pointers\" · \"O(1) get and put with eviction\".",
    intuition="A stack of papers on a desk plus an index card box. The box tells you in O(1) where any paper is (hash map). Pulling a paper out of the middle and putting it on top is O(1) only if each paper knows its neighbours (doubly linked list). The oldest paper sits at the bottom, ready to be thrown away.",
    brute="A plain list needs O(n) to find a key and O(n) to move it. A map alone has no order. Combining both gives O(1) for every operation.",
    idea="Hash map `key → node` for lookup; doubly linked list ordered from most recent (front) to least recent (back). Dummy `head` and `tail` nodes remove all null checks when linking and unlinking.",
    steps=["`get(k)`: if missing return −1; else unlink the node, put it at the front, return the value.", "`put(k, v)`: if present, update and move to front.", "If new and the cache is full, remove `tail.prev` (the LRU) from list and map.", "Insert the new node at the front and add it to the map."],
    trace_title="capacity 3",
    trace="""put(1,A) put(2,B) put(3,C)      list  3 2 1
get(1) -> A                      list  1 3 2   (1 moved to front)
put(4,D): full, evict tail (2)   list  4 1 3
get(2) -> -1                     (not in map)""",
    code=[("LRU cache (Java, manual doubly linked list)",
           """class LRUCache {
    class Node { int k, v; Node prev, next; Node(int k, int v) { this.k = k; this.v = v; } }
    Map<Integer, Node> map = new HashMap<>();
    Node head = new Node(0, 0), tail = new Node(0, 0);   // dummy sentinels
    int cap;
    LRUCache(int cap) { this.cap = cap; head.next = tail; tail.prev = head; }

    int get(int k) {
        Node n = map.get(k);
        if (n == null) return -1;
        unlink(n); addFront(n);
        return n.v;
    }
    void put(int k, int v) {
        Node n = map.get(k);
        if (n != null) { n.v = v; unlink(n); addFront(n); return; }
        if (map.size() == cap) { Node lru = tail.prev; unlink(lru); map.remove(lru.k); }
        n = new Node(k, v); map.put(k, n); addFront(n);
    }
    void unlink(Node n) { n.prev.next = n.next; n.next.prev = n.prev; }
    void addFront(Node n) { n.next = head.next; n.prev = head; head.next.prev = n; head.next = n; }
}""",
           """class Node:
    def __init__(self, k=0, v=0):
        self.k, self.v, self.prev, self.next = k, v, None, None

class LRUCache:
    def __init__(self, cap):
        self.cap, self.map = cap, {}
        self.head, self.tail = Node(), Node()            # dummy sentinels
        self.head.next, self.tail.prev = self.tail, self.head

    def _unlink(self, n):
        n.prev.next, n.next.prev = n.next, n.prev

    def _add_front(self, n):
        n.next, n.prev = self.head.next, self.head
        self.head.next.prev = n
        self.head.next = n

    def get(self, k):
        n = self.map.get(k)
        if not n:
            return -1
        self._unlink(n)
        self._add_front(n)
        return n.v

    def put(self, k, v):
        n = self.map.get(k)
        if n:
            n.v = v
            self._unlink(n)
            self._add_front(n)
            return
        if len(self.map) == self.cap:
            lru = self.tail.prev
            self._unlink(lru)
            del self.map[lru.k]
        n = Node(k, v)
        self.map[k] = n
        self._add_front(n)""")],
    complexity="O(1) time for get and put, O(capacity) space.",
    traps=["Store the **key** in each node so you can delete it from the map on eviction.", "Update the existing node's value on a repeated `put`, and mark it most recent.",
           "Unlink before relinking; order of the four pointer assignments matters.", "In an interview, mention that `LinkedHashMap` (Java) / `OrderedDict` (Python) do this for you, then implement it by hand."],
    variants=["LFU cache: map of frequency → doubly linked list plus a `minFreq` pointer (LC 460).", "Copy list with random pointer: map old node → new node, two passes (LC 138).", "Browser history: doubly linked list (or two stacks)."],
    notuse="When eviction order is irrelevant (a plain `HashMap`) or capacity is tiny (a simple list may be enough).",
    problems=[
        (1472, "Design Browser History", "M", "design-browser-history", "Doubly linked list (or array + pointer); visit truncates forward history", "O(1) per op / O(n)"),
        (138, "Copy List with Random Pointer", "M", "copy-list-with-random-pointer", "Map old node → new node, then wire next and random", "O(n) / O(n)"),
        (146, "LRU Cache", "M", "lru-cache", "Hash map + doubly linked list with sentinels", "O(1) per op / O(cap)"),
        (460, "LFU Cache", "H", "lfu-cache", "Frequency → list of nodes, track the minimum frequency", "O(1) per op / O(cap)"),
    ]))

TOPIC = dict(
    id="linked_list", file="04_linked_list.html", title="Linked Lists — Pattern Guide",
    lead="Linked lists test whether you can manage pointers without losing nodes. This guide covers the dummy node, reversal, fast and slow pointers, merging, the runner gap, split-reverse-merge, two-chain rewiring and LRU design, each with the intuition, a step-through animation that shows the arrows moving, Java and Python code, and a ladder of LeetCode problems.",
    mindset="A singly linked list gives you one thing: **follow `next`**. Everything else is pointer bookkeeping. Three habits solve most problems: use a **dummy head** so the first node is not special, **save `next` before you overwrite it**, and **draw the pointers** before and after each change. Two-pointer tricks (fast/slow, a fixed gap) replace the random access you do not have.",
    qintro="Ask these questions on every linked-list problem:",
    questions=["**Can the head change?** → add a dummy node.", "**Do I need to go backwards or compare from both ends?** → reverse a half, or use a stack.", "**Is there a cycle, or a position counted from the end?** → fast/slow or a fixed gap.",
               "**Am I about to overwrite `next`?** → save it in a temporary first.", "**Must I keep O(1) space?** → rewire nodes in place instead of copying values."],
    cues=[
        ["\"remove / insert\", head might change", "**P1** Dummy node"],
        ["\"reverse\", \"swap pairs\", \"in groups of k\"", "**P2** Reversal"],
        ["\"middle\", \"has a cycle\", \"cycle start\"", "**P3** Fast and slow"],
        ["\"merge sorted lists\", \"sort list\", \"merge k\"", "**P4** Merge and sort"],
        ["\"nth from the end\", \"intersection\", \"rotate\"", "**P5** Runner gap"],
        ["\"palindrome list\", \"reorder list\"", "**P6** Split, reverse, merge"],
        ["\"add two numbers\", \"odd even\", \"partition\"", "**P7** Two chains and carry"],
        ["\"LRU cache\", \"O(1) get/put with order\", \"copy with random pointer\"", "**P8** List + hash map"],
    ],
    choose=[
        ["Head may be deleted or replaced", "Dummy node (P1)"],
        ["Need the list backwards", "Reverse (P2)"],
        ["Position from the middle or detect a loop", "Fast / slow (P3)"],
        ["Combine or order sorted data", "Merge (P4)"],
        ["Position from the end", "Runner gap (P5)"],
        ["Compare front and back in O(1) space", "Split, reverse, compare (P6)"],
        ["Group nodes by a rule", "Two chains (P7)"],
        ["O(1) lookup plus ordering", "Hash map + doubly linked list (P8)"],
    ],
    rule="draw three boxes before coding: **before**, **after the first change**, and **the edge case** (empty list, single node, head removed). If the head can change, a dummy node is almost always the right first line.",
    selftest=[
        ("Why use a dummy node?", "It puts a real node in front of the head, so deleting or inserting at the head follows the same code as any other position, and `dummy.next` is always the answer."),
        ("In iterative reversal, what happens if you do not save `cur.next` first?", "After `cur.next = prev` the link to the rest of the list is gone, so the remaining nodes are lost."),
        ("Why must the fast pointer's loop check `fast.next` too?", "`fast` jumps two nodes; dereferencing `fast.next.next` when `fast.next` is null throws a null-pointer error."),
        ("Why do the slow pointer and fast pointer always meet in a cycle?", "Once both are inside the loop, the gap shrinks by one each step (fast gains 1), so it must reach zero; the fast pointer cannot jump over the slow one."),
        ("How do you find the cycle start after the meeting?", "Reset one pointer to the head and move both one step at a time. The distance from the head to the cycle start equals the distance from the meeting point to the start (mod the cycle length), so they meet at the start."),
        ("How do you get the kth node from the end in one pass?", "Move `fast` k steps ahead, then move both pointers together; when `fast` reaches the end, `slow` is k nodes from the end."),
        ("Why does an LRU cache use a **doubly** linked list?", "To unlink a node from the middle in O(1) you must reach its predecessor, which a singly linked list cannot do without a scan."),
        ("What is the space complexity of the recursive reversal?", "O(n): each recursive call stays on the call stack until the end of the list is reached."),
    ],
    plan=[
        "**Day 1:** pointer basics and the dummy node. Implement insert, delete and traverse from memory, then do the ladder.",
        "**Day 2:** reversal (iterative first, then recursive, then the sub-range version).",
        "**Day 3:** fast/slow pointers and the runner gap; draw the Floyd cycle proof once.",
        "**Day 4:** merge two lists, then sort list, then merge k lists.",
        "**Day 5:** split, reverse, merge (palindrome and reorder); redo reversal without looking.",
        "**Day 6:** two-chain problems and the LRU cache from scratch, twice.",
    ],
    patterns=P,
)
