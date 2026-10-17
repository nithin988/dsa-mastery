"""Content for topic 14: Greedy algorithms."""

P = []

# ---------------------------------------------------------------- 1
P.append(dict(
    title="What greedy is, and when it is safe", tier="hot", sim="coins", oneline="take the best local choice, but only if a proof says it is safe",
    why="The first question on any optimisation problem: greedy or DP?", signature="LC 860 / 455 / 322",
    when="At each step one option is clearly the best, and an exchange argument shows it can be part of an optimal solution.",
    detect="\"minimum / maximum\" with a simple rule · \"is it always optimal to take the largest?\" · problems where sorting by one key seems to solve everything · coin systems and change-making.",
    intuition="Greedy is walking uphill by always stepping to the steepest neighbouring point. It reaches the top only on a landscape with a single peak. A greedy rule is **safe** when you can show that any optimal solution can be rearranged (the **exchange argument**) so that it starts with your greedy choice without getting worse, or that your partial solution always stays at least as good as any other (**stays-ahead**). Without such an argument you need a counterexample hunt, or dynamic programming.",
    brute="Trying every combination is exponential; dynamic programming explores all sub-choices in polynomial time but is heavier to write. A correct greedy gives O(n) or O(n log n) with tiny code.",
    idea="Decide a rule (largest first, earliest deadline, best ratio, farthest reach). Check it on small cases and try to **break it**. Prove it with an exchange argument: take an optimal solution that disagrees with the rule at the first step, swap in the greedy choice, and show the result is still optimal.",
    steps=["Guess a greedy rule (often after a sort).", "Test it on tiny inputs and adversarial ones (equal values, extremes).", "Prove it (exchange / stays-ahead) or find a counterexample.", "If it fails, the problem usually needs DP or backtracking."],
    trace_title="coins 1, 3, 4 and amount 6",
    trace="""greedy (largest first): 4 + 1 + 1 = 3 coins
optimal               : 3 + 3     = 2 coins
=> greedy is wrong for this coin system
for coins 1, 5, 10, 25 greedy IS optimal (each coin divides the next ones' structure)""",
    code=[("a safe greedy: lemonade change (always give the largest bill first)",
           """int five = 0, ten = 0;
for (int bill : bills) {
    if (bill == 5) five++;
    else if (bill == 10) { if (five == 0) return false; five--; ten++; }
    else {                                                    // 20: prefer 10 + 5 over 5 + 5 + 5, keeping fives
        if (ten > 0 && five > 0) { ten--; five--; }
        else if (five >= 3) five -= 3;
        else return false;
    }
}
return true;""",
           """five = ten = 0
for bill in bills:
    if bill == 5:
        five += 1
    elif bill == 10:
        if five == 0:
            return False
        five -= 1; ten += 1
    else:                                                         # 20: prefer 10 + 5 over 5 + 5 + 5, keeping fives
        if ten and five:
            ten -= 1; five -= 1
        elif five >= 3:
            five -= 3
        else:
            return False
return True"""),
          ("an UNSAFE greedy (coin change) and the DP that fixes it",
           """// greedy: wrong for coins {1, 3, 4}, amount 6
Arrays.sort(coins);
int count = 0;
for (int i = coins.length - 1; i >= 0; i--) { count += amount / coins[i]; amount %= coins[i]; }

// correct: dp[a] = fewest coins that make amount a
int[] dp = new int[amount + 1];
Arrays.fill(dp, amount + 1); dp[0] = 0;
for (int a = 1; a <= amount; a++)
    for (int c : coins) if (c <= a) dp[a] = Math.min(dp[a], dp[a - c] + 1);""",
           """# greedy: wrong for coins [1, 3, 4], amount 6
count = 0
for c in sorted(coins, reverse=True):
    count += amount // c
    amount %= c

# correct: dp[a] = fewest coins that make amount a
dp = [0] + [float('inf')] * amount
for a in range(1, amount + 1):
    for c in coins:
        if c <= a:
            dp[a] = min(dp[a], dp[a - c] + 1)""")],
    complexity="Usually O(n) or O(n log n) (sort) with O(1) extra space.",
    traps=["A rule that works on the samples may still be wrong: build counterexamples (ties, large first, equal items).", "Greedy on \"coin change\" is correct only for special coin systems; general coins need DP.",
           "Sort by the **right key** (end time, ratio, deadline) and break ties deliberately.", "Do not confuse greedy with \"fast heuristic\": an interview answer needs the reason it is optimal."],
    variants=["Stays-ahead proof: after k steps greedy is at least as good as any strategy.", "Matroid structure: why Kruskal and interval scheduling work.", "Greedy + DP hybrids (weighted interval scheduling needs DP)."],
    notuse="When choices interact in ways a local rule cannot see (knapsack, longest path, general change-making): use DP or search.",
    problems=[
        (860, "Lemonade Change", "E", "lemonade-change", "Give the largest bill first for $20; keep the fives", "O(n) / O(1)"),
        (455, "Assign Cookies", "E", "assign-cookies", "Sort both; give each child the smallest cookie that satisfies them", "O(n log n) / O(1)"),
        (1005, "Maximize Sum Of Array After K Negations", "E", "maximize-sum-of-array-after-k-negations", "Flip the smallest (most negative) element each time", "O(n log n) / O(1)"),
        (1217, "Minimum Cost to Move Chips to The Same Position", "E", "minimum-cost-to-move-chips-to-the-same-position", "Even moves are free: answer = min(count even, count odd)", "O(n) / O(1)"),
        (322, "Coin Change", "M", "coin-change", "The counterexample problem: greedy fails, use DP", "O(amount·coins) / O(amount)"),
    ]))

# ---------------------------------------------------------------- 2
P.append(dict(
    title="Jump games: farthest reach and levels", tier="hot", sim="jump2", oneline="track the farthest index you can reach; levels give the minimum jumps",
    why="The model for \"reach the end\" and interval covering problems", signature="LC 55 / 45",
    when="You move forward by variable amounts and ask whether the end is reachable or how few moves are needed.",
    detect="\"jump game\" · \"minimum number of jumps\" · \"video stitching\" · \"minimum taps to water the garden\" · \"cover [0, T] with intervals\".",
    intuition="You never need to decide which exact landing spot to use; you only need to know **how far you could get**. The set of indices reachable with k jumps is a contiguous range, so you can sweep through it once, keeping the farthest index any of its members can reach. That farthest point defines the next range. Each time you pass the end of the current range you have paid for one more jump.",
    brute="DP over positions (`dp[i] = min jumps`) is O(n²). The level sweep keeps just two numbers and runs in O(n).",
    idea="Reachability: `far = max(far, i + a[i])`; fail if `i > far`. Minimum jumps: maintain `curEnd` (end of the current level) and `far`; when `i == curEnd`: `jumps++`, `curEnd = far`. Interval covering is the same idea after turning intervals into `reach[start] = max end`.",
    steps=["`far = 0`, `curEnd = 0`, `jumps = 0`.", "For each `i` before the last index: `far = max(far, i + a[i])`.", "If `i == curEnd`: take a jump: `jumps++`, `curEnd = far`.", "Reachability variant: return false if `i > far`."],
    trace_title="`[2,3,1,1,4]` minimum jumps",
    trace="""i=0: far=2   i==curEnd(0) -> jumps 1, curEnd 2
i=1: far=4
i=2: far=4   i==curEnd(2) -> jumps 2, curEnd 4
reached the last index: 2 jumps (0 -> 1 -> 4)""",
    code=[("can reach, and minimum jumps",
           """// reachable?
int far = 0;
for (int i = 0; i < n; i++) {
    if (i > far) return false;                    // a gap we cannot cross
    far = Math.max(far, i + a[i]);
}
return true;

// minimum jumps (guaranteed reachable)
int jumps = 0, curEnd = 0; far = 0;
for (int i = 0; i < n - 1; i++) {
    far = Math.max(far, i + a[i]);
    if (i == curEnd) { jumps++; curEnd = far; }   // the current level is exhausted: jump
}
return jumps;""",
           """# reachable?
far = 0
for i, x in enumerate(a):
    if i > far:
        return False                              # a gap we cannot cross
    far = max(far, i + x)
return True

# minimum jumps (guaranteed reachable)
jumps = cur_end = far = 0
for i in range(len(a) - 1):
    far = max(far, i + a[i])
    if i == cur_end:
        jumps += 1                                # the current level is exhausted: jump
        cur_end = far
return jumps"""),
          ("minimum taps to water a garden (intervals as jumps)",
           """int[] reach = new int[n + 1];                               // reach[l] = farthest right end of a tap starting at l
for (int i = 0; i <= n; i++) {
    int l = Math.max(0, i - ranges[i]), r = Math.min(n, i + ranges[i]);
    reach[l] = Math.max(reach[l], r);
}
int taps = 0, curEnd = 0, far = 0;
for (int i = 0; i <= n; i++) {
    if (i > far) return -1;                                      // gap: nothing waters position i
    far = Math.max(far, reach[i]);
    if (i == curEnd && curEnd < n) { taps++; curEnd = far; }     // must open one more tap
}
return curEnd >= n ? taps : -1;""",
           """reach = [0] * (n + 1)                                         # reach[l] = farthest right end of a tap starting at l
for i, r in enumerate(ranges):
    l = max(0, i - r)
    reach[l] = max(reach[l], min(n, i + r))
taps = cur_end = far = 0
for i in range(n + 1):
    if i > far:
        return -1                                                # gap: nothing waters position i
    far = max(far, reach[i])
    if i == cur_end and cur_end < n:
        taps += 1                                                # must open one more tap
        cur_end = far
return taps if cur_end >= n else -1""")],
    complexity="O(n) time, O(1) space (O(n) for the interval conversion).",
    traps=["Loop to `n − 2` for minimum jumps (the last index needs no further jump), or you add one jump too many.", "In the reachability version check `i > far` **before** updating `far`.",
           "For intervals, convert them to `reach[left] = max right` first; gaps mean impossible.", "Jump Game IV (teleport on equal values) is BFS, not this greedy."],
    variants=["Video stitching: sort clips, extend coverage greedily.", "Minimum number of taps: same sweep over the `reach` array.", "Jump Game III / VII: BFS or sliding-window reachability."],
    notuse="Costs per jump (use Dijkstra / DP) or when jumps are restricted to exact lengths.",
    problems=[
        (55, "Jump Game", "M", "jump-game", "far = max(far, i + a[i]); fail if i > far", "O(n) / O(1)"),
        (45, "Jump Game II", "M", "jump-game-ii", "Level sweep with curEnd and far", "O(n) / O(1)"),
        (1024, "Video Stitching", "M", "video-stitching", "Sort clips by start; always extend with the farthest end", "O(n log n) / O(1)"),
        (1326, "Minimum Number of Taps to Open to Water a Garden", "H", "minimum-number-of-taps-to-open-to-water-a-garden", "Convert taps to reach[]; jump-game-II sweep", "O(n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 3
P.append(dict(
    title="Running balance with resets: gas station", tier="hot", sim="gas", oneline="when the running total goes negative, restart after this point",
    why="The cleanest example of a greedy proof about prefixes", signature="LC 134",
    when="You walk a circle (or line) gaining and spending, and want a start position that never goes negative.",
    detect="\"gas station\" · \"circular tour\" · \"starting index so the running sum never drops below 0\" · \"balanced loop\".",
    intuition="Suppose you start at station `s` and run out of fuel at station `i`. Then **none** of the stations between `s` and `i` can be a good start either: each of them would arrive at `i` with no more fuel than you did (you had a non-negative tank at every intermediate station, so starting later only loses that head start). So skip them all and try `i + 1`. In addition, a solution exists exactly when the **total** gas is at least the total cost.",
    brute="Trying every start and simulating the loop is O(n²). With the skip argument each station is visited once: O(n).",
    idea="`total += gas[i] − cost[i]`; `tank += gas[i] − cost[i]`. If `tank < 0`: `start = i + 1`, `tank = 0`. At the end, if `total ≥ 0` the answer is `start`, otherwise −1.",
    steps=["`total = tank = start = 0`.", "For each `i`: add the net gain `gas[i] − cost[i]` to both.", "If `tank < 0`: reset `tank = 0`, `start = i + 1`.", "Return `start` if `total ≥ 0`, else −1."],
    trace_title="gas `[1,2,3,4,5]`, cost `[3,4,5,1,2]`",
    trace="""net:   -2 -2 -2  3  3
i=0 tank -2 <0 -> start 1
i=1 tank -2 <0 -> start 2
i=2 tank -2 <0 -> start 3
i=3 tank 3 ; i=4 tank 6
total 0 >= 0 -> answer 3""",
    code=[("gas station",
           """int total = 0, tank = 0, start = 0;
for (int i = 0; i < gas.length; i++) {
    int diff = gas[i] - cost[i];
    total += diff;
    tank += diff;
    if (tank < 0) { start = i + 1; tank = 0; }       // no start up to i works: try the next station
}
return total >= 0 ? start : -1;""",
           """total = tank = start = 0
for i in range(len(gas)):
    diff = gas[i] - cost[i]
    total += diff
    tank += diff
    if tank < 0:
        start = i + 1                                # no start up to i works: try the next station
        tank = 0
return start if total >= 0 else -1"""),
          ("maximum coins you can get (sort, then take every second pile)",
           """Arrays.sort(piles);
int res = 0;
for (int i = piles.length / 3; i < piles.length; i += 2) res += piles[i];   // you take the second largest of each triple
return res;""",
           """piles.sort()
return sum(piles[len(piles) // 3::2])                # you take the second largest of each triple""")],
    complexity="O(n) time, O(1) space.",
    traps=["The answer is guaranteed unique when it exists; do not search for the best of several.", "Reset `tank` to 0 and `start` to `i + 1` **together**.",
           "Check `total ≥ 0`: a start found by the loop is valid only if the whole loop has enough fuel.", "Index `start` can equal `n` only if `total < 0`; guard before returning."],
    variants=["Car pooling / meeting overload: running balance with difference arrays.", "Maximum subarray (Kadane): the same \"restart when negative\" idea (topic 02).", "Circular array maximum sum: total − minimum subarray."],
    notuse="When values arrive in a fixed order you cannot rotate, or you need the **best** (not just any valid) start.",
    problems=[
        (134, "Gas Station", "M", "gas-station", "Reset the start when the tank goes negative; check total ≥ 0", "O(n) / O(1)"),
        (1094, "Car Pooling", "M", "car-pooling", "Running balance of passengers with a difference array", "O(n + range) / O(range)"),
        (1561, "Maximum Number of Coins You Can Get", "M", "maximum-number-of-coins-you-can-get", "Sort; take every second pile from the middle onwards", "O(n log n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 4
P.append(dict(
    title="Stock trading: collect every rise", tier="hot", sim="stock", oneline="a rise from a to c is the sum of the small rises between",
    why="Shows how a global optimum can be built from local gains", signature="LC 121 / 122 / 714",
    when="You trade a price series many times (or once) and want maximum profit.",
    detect="\"best time to buy and sell stock\" · \"unlimited transactions\" · \"transaction fee\" · \"at most k transactions\".",
    intuition="If the price rises from 1 to 5 over several days, buying on day 1 and selling on day 5 earns the same as buying and selling on each rising day: `(5 − 1) = (2 − 1) + (3 − 2) + …`. So when you may trade unlimited times, just collect **every** positive day-to-day difference. For a single trade, the best buy is the lowest price **before** the sale, so keep the running minimum.",
    brute="Trying every (buy, sell) pair is O(n²). Collecting the positive differences, or tracking a running minimum, is O(n).",
    idea="Unlimited transactions: `profit += max(0, p[i] − p[i−1])`. One transaction: `profit = max(profit, p[i] − minSoFar)`. With a **fee**, use two states (cash, holding) and let the greedy become a tiny DP.",
    steps=["Unlimited: for each `i`: `if p[i] > p[i-1]: profit += p[i] - p[i-1]`.", "Single: keep `minPrice`; update `best = max(best, p[i] − minPrice)`.", "With a fee: `cash = max(cash, hold + p − fee)`, `hold = max(hold, cash − p)`.", "At most 2 or k transactions: DP over states (topic 16)."],
    trace_title="`[7,1,5,3,6,4]`, unlimited trades",
    trace="""7->1 drop
1->5 +4
5->3 drop
3->6 +3
6->4 drop
profit 7  (buy 1 sell 5, buy 3 sell 6)""",
    code=[("one transaction and unlimited transactions",
           """// at most one transaction
int minPrice = Integer.MAX_VALUE, best = 0;
for (int p : prices) {
    minPrice = Math.min(minPrice, p);
    best = Math.max(best, p - minPrice);
}
// unlimited transactions
int profit = 0;
for (int i = 1; i < prices.length; i++)
    if (prices[i] > prices[i - 1]) profit += prices[i] - prices[i - 1];""",
           """# at most one transaction
min_price, best = float('inf'), 0
for p in prices:
    min_price = min(min_price, p)
    best = max(best, p - min_price)
# unlimited transactions
profit = sum(max(0, prices[i] - prices[i - 1]) for i in range(1, len(prices)))"""),
          ("with a transaction fee (two states)",
           """int cash = 0, hold = -prices[0];                          // cash: no share held, hold: share held
for (int i = 1; i < prices.length; i++) {
    cash = Math.max(cash, hold + prices[i] - fee);          // sell today (pay the fee)
    hold = Math.max(hold, cash - prices[i]);                // buy today
}
return cash;""",
           """cash, hold = 0, -prices[0]                                  # cash: no share held, hold: share held
for p in prices[1:]:
    cash = max(cash, hold + p - fee)                          # sell today (pay the fee)
    hold = max(hold, cash - p)                                # buy today
return cash""")],
    complexity="O(n) time, O(1) space.",
    traps=["With a transaction cap (k) greedy no longer works; use DP.", "Do not buy and sell on the same day for \"one transaction\" if the problem forbids it (it is harmless, profit 0).",
           "Initialise `minPrice` to infinity / the first price, and `best` to 0 (no trade).", "The fee version is not \"sum of rises\": a small rise may be smaller than the fee."],
    variants=["Cooldown after selling: three states (DP).", "At most two transactions: forward and backward passes or a 4-state DP.", "Best time to buy and sell with an arbitrary k: DP."],
    notuse="Limits on the number of transactions or complex fee rules; those are state-machine DPs.",
    problems=[
        (121, "Best Time to Buy and Sell Stock", "E", "best-time-to-buy-and-sell-stock", "Running minimum price; best = max(p − min)", "O(n) / O(1)"),
        (122, "Best Time to Buy and Sell Stock II", "M", "best-time-to-buy-and-sell-stock-ii", "Add every positive day-to-day difference", "O(n) / O(1)"),
        (714, "Best Time to Buy and Sell Stock with Transaction Fee", "M", "best-time-to-buy-and-sell-stock-with-transaction-fee", "Two-state greedy / DP: cash and hold", "O(n) / O(1)"),
        (123, "Best Time to Buy and Sell Stock III", "H", "best-time-to-buy-and-sell-stock-iii", "At most two trades: four-state DP", "O(n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 5
P.append(dict(
    title="Two-pass greedy: satisfy left, then right", tier="hot", sim="candy", oneline="one pass per direction; combine with max",
    why="Handles constraints that depend on both neighbours", signature="LC 135 / 42",
    when="Each element's value depends on both its left and right neighbours (or prefix and suffix).",
    detect="\"candy\" · \"trapping rain water\" · \"shortest distance to a character\" · \"product except self\" · \"shortest unsorted subarray\".",
    intuition="A rule such as \"a higher rating than your neighbour gets more candy\" involves both sides. Handle one side at a time: sweep left to right so every child satisfies the **left** rule, then sweep right to left so every child satisfies the **right** rule, keeping the larger requirement so the first pass is not undone. Each pass is easy because it only looks one way.",
    brute="Repeatedly adjusting candies until stable can be O(n²). Two linear passes finish in O(n).",
    idea="Pass 1 (L→R): `if r[i] > r[i−1]: c[i] = c[i−1] + 1`. Pass 2 (R→L): `if r[i] > r[i+1]: c[i] = max(c[i], c[i+1] + 1)`. Total = sum of `c`. The same left/right pass idea computes prefix/suffix maxima (rain water) or nearest occurrences.",
    steps=["Initialise `c[i] = 1`.", "Left to right: raise `c[i]` above its left neighbour when the rating is higher.", "Right to left: raise `c[i]` above its right neighbour with `max`.", "Sum the candies."],
    trace_title="ratings `[1,3,2,2,1]`",
    trace="""start      [1,1,1,1,1]
L -> R     [1,2,1,1,1]
R -> L     [1,2,1,2,1]   (3 > 2 keeps 2; second 2 > 1 becomes 2)
total 7""",
    code=[("candy",
           """int n = r.length;
int[] c = new int[n];
Arrays.fill(c, 1);
for (int i = 1; i < n; i++) if (r[i] > r[i - 1]) c[i] = c[i - 1] + 1;                       // left rule
for (int i = n - 2; i >= 0; i--) if (r[i] > r[i + 1]) c[i] = Math.max(c[i], c[i + 1] + 1);   // right rule
int sum = 0; for (int x : c) sum += x;
return sum;""",
           """n = len(r)
c = [1] * n
for i in range(1, n):
    if r[i] > r[i - 1]:
        c[i] = c[i - 1] + 1                                  # left rule
for i in range(n - 2, -1, -1):
    if r[i] > r[i + 1]:
        c[i] = max(c[i], c[i + 1] + 1)                       # right rule
return sum(c)"""),
          ("trapping rain water (prefix max pass, suffix max pass)",
           """int n = h.length, water = 0;
int[] left = new int[n], right = new int[n];
left[0] = h[0];
for (int i = 1; i < n; i++) left[i] = Math.max(left[i - 1], h[i]);              // tallest bar to the left (inclusive)
right[n - 1] = h[n - 1];
for (int i = n - 2; i >= 0; i--) right[i] = Math.max(right[i + 1], h[i]);       // tallest bar to the right (inclusive)
for (int i = 0; i < n; i++) water += Math.min(left[i], right[i]) - h[i];""",
           """n = len(h)
left, right = [0] * n, [0] * n
left[0] = h[0]
for i in range(1, n):
    left[i] = max(left[i - 1], h[i])                         # tallest bar to the left (inclusive)
right[-1] = h[-1]
for i in range(n - 2, -1, -1):
    right[i] = max(right[i + 1], h[i])                       # tallest bar to the right (inclusive)
water = sum(min(left[i], right[i]) - h[i] for i in range(n))""")],
    complexity="O(n) time, O(n) space (the water problem reaches O(1) with two pointers).",
    traps=["Use `max(c[i], c[i+1] + 1)` in the second pass; plain assignment can break the left rule.", "Equal ratings do **not** require more candy (strict inequality only).",
           "Do not try to do both neighbours in one pass; two independent passes are simpler and correct.", "Trapping rain water needs the **inclusive** prefix and suffix maxima."],
    variants=["Shortest distance to a character: nearest occurrence on the left, then on the right, take the min.", "Product of array except self: prefix products, then suffix products.", "Shortest unsorted continuous subarray: scan from both ends for the violation points."],
    notuse="Constraints that involve non-adjacent elements or cycles; use a graph / DP.",
    problems=[
        (821, "Shortest Distance to a Character", "E", "shortest-distance-to-a-character", "Pass 1: distance to the left occurrence; pass 2: to the right; min", "O(n) / O(n)"),
        (581, "Shortest Unsorted Continuous Subarray", "M", "shortest-unsorted-continuous-subarray", "Scan for the last drop from the left and the last rise from the right", "O(n) / O(1)"),
        (135, "Candy", "H", "candy", "Left pass, right pass with max", "O(n) / O(n)"),
        (42, "Trapping Rain Water", "H", "trapping-rain-water", "Prefix max and suffix max arrays (or two pointers)", "O(n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 6
P.append(dict(
    title="Greedy on characters: last occurrences and counts", tier="hot", sim="partition", oneline="cut as soon as everything in the part is closed off",
    why="String problems with \"as many parts / as few changes as possible\"", signature="LC 763 / 921",
    when="Split, balance or rearrange a string by simple local rules based on counts or last positions.",
    detect="\"partition labels\" · \"split a string into balanced strings\" · \"minimum add to make parentheses valid\" · \"minimum deletions so frequencies are unique\" · \"swaps to balance brackets\".",
    intuition="For Partition Labels: a part that contains the letter `a` must stretch to the **last** `a`, and every letter inside it forces the same. Extend the end while you scan; the moment your position equals the end, nothing inside refers to anything outside, so you can cut right here, and cutting as early as possible produces the most parts.",
    brute="Trying all cut positions is exponential. Precomputing each letter's last index and sweeping once is O(n).",
    idea="Precompute a table (last index, counts). Maintain the current requirement (`end`, balance, used frequencies) while scanning and cut / fix greedily when the requirement is met or violated.",
    steps=["Build `last[c]` (or a count array).", "Scan left to right, extending `end = max(end, last[s[i]])`.", "When `i == end`: record a part of size `end − start + 1`; set `start = i + 1`.", "For balance problems keep a counter and count the repairs."],
    trace_title="`ababcbacadefegdehijhklij`",
    trace="""a b a b c b a c a   last a = 8 -> end 8, cut at 8   size 9
d e f e g d e       cut at 14                      size 7
h i j h k l i j     cut at 23                      size 8
=> [9, 7, 8]""",
    code=[("partition labels",
           """int[] last = new int[26];
for (int i = 0; i < s.length(); i++) last[s.charAt(i) - 'a'] = i;
List<Integer> res = new ArrayList<>();
int start = 0, end = 0;
for (int i = 0; i < s.length(); i++) {
    end = Math.max(end, last[s.charAt(i) - 'a']);       // this part must reach the last occurrence
    if (i == end) { res.add(end - start + 1); start = i + 1; }
}
return res;""",
           """last = {c: i for i, c in enumerate(s)}
res, start, end = [], 0, 0
for i, c in enumerate(s):
    end = max(end, last[c])                              # this part must reach the last occurrence
    if i == end:
        res.append(end - start + 1)
        start = i + 1
return res"""),
          ("minimum deletions to make character frequencies unique",
           """int[] cnt = new int[26];
for (char c : s.toCharArray()) cnt[c - 'a']++;
Set<Integer> used = new HashSet<>();
int deletions = 0;
for (int f : cnt) {
    while (f > 0 && !used.add(f)) { f--; deletions++; }       // lower the frequency until it is unused
}
return deletions;""",
           """from collections import Counter
used, deletions = set(), 0
for f in Counter(s).values():
    while f > 0 and f in used:
        f -= 1                                                # lower the frequency until it is unused
        deletions += 1
    used.add(f)
return deletions"""),
          ("minimum insertions to make parentheses valid (counter greedy)",
           """int open = 0, adds = 0;
for (char c : s.toCharArray()) {
    if (c == '(') open++;
    else if (open > 0) open--;
    else adds++;                                              // unmatched ')' needs a '(' in front
}
return adds + open;                                           // plus a ')' for every unmatched '('""",
           """open_, adds = 0, 0
for c in s:
    if c == '(':
        open_ += 1
    elif open_:
        open_ -= 1
    else:
        adds += 1                                             # unmatched ')' needs a '(' in front
return adds + open_                                           # plus a ')' for every unmatched '('""")],
    complexity="O(n) time, O(1) space (alphabet-sized tables).",
    traps=["Update `end` **before** testing `i == end`.", "Reset `start` (and `end`) after each cut.",
           "Frequency problems: a frequency of 0 may be reused (do not add 0 to `used`).", "Balanced splits: greedily cut as soon as the running balance hits 0."],
    variants=["Split a string in balanced strings: count R − L, cut when it returns to 0.", "Minimum swaps to balance brackets: unmatched `]` count / 2 rounded up.", "Remove duplicate letters / smallest subsequence: stack + last indices (topic 05)."],
    notuse="Constraints that need look-ahead beyond counts and last positions (use DP).",
    problems=[
        (1221, "Split a String in Balanced Strings", "E", "split-a-string-in-balanced-strings", "Running R − L; cut at each zero", "O(n) / O(1)"),
        (921, "Minimum Add to Make Parentheses Valid", "M", "minimum-add-to-make-parentheses-valid", "Counter of open parentheses; unmatched ')' each cost one", "O(n) / O(1)"),
        (763, "Partition Labels", "M", "partition-labels", "Extend end to last occurrence; cut when i == end", "O(n) / O(1)"),
        (1647, "Minimum Deletions to Make Character Frequencies Unique", "M", "minimum-deletions-to-make-character-frequencies-unique", "Lower each duplicate frequency until unused", "O(n + 26²) / O(26)"),
        (1963, "Minimum Number of Swaps to Make the String Balanced", "M", "minimum-number-of-swaps-to-make-the-string-balanced", "Count unmatched ']' → (count + 1) / 2 swaps", "O(n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 7
P.append(dict(
    title="Digits and numbers: improve the leftmost position", tier="hot", sim="maxswap", oneline="the most significant digit matters most: fix it first",
    why="Lexicographic / numeric construction problems fall to this", signature="LC 670 / 738",
    when="You rearrange or modify digits (swap once, make non-decreasing, remove some) to get the largest or smallest number.",
    detect="\"maximum swap\" · \"monotone increasing digits\" · \"maximum 69 number\" · \"remove k digits\" · \"largest number\" · \"create maximum number\".",
    intuition="In a number the leftmost digit is worth more than everything to its right combined. So a single improvement at the leftmost possible position beats any improvement elsewhere. For Maximum Swap: find the leftmost digit that has a **larger digit somewhere to its right**, and swap it with the largest such digit (taking its **last** occurrence so the smaller digit moves as far right as possible).",
    brute="Trying every pair of positions is O(n²) per number. Recording the last index of each digit makes the choice O(10·n).",
    idea="Precompute `last[d]`. For each position `i` from the left: for digits `d` from 9 down to `a[i] + 1`: if `last[d] > i`, swap `a[i]` and `a[last[d]]` and stop. For \"monotone increasing\": scan from the right, whenever `a[i−1] > a[i]` decrement `a[i−1]` and mark everything from `i` onwards to become 9.",
    steps=["Store the digits in an array.", "Record the last index of each digit 0–9.", "For `i` left to right: look for a larger digit to the right (9 down to `a[i] + 1`).", "On the first hit, swap and finish."],
    trace_title="`2736`",
    trace="""last: 2@0 7@1 3@2 6@3
i=0 digit 2: larger digit to the right? 9..3 -> 7 at index 1
swap positions 0 and 1 -> 7236""",
    code=[("maximum swap and monotone increasing digits",
           """int maximumSwap(int num) {
    char[] d = String.valueOf(num).toCharArray();
    int[] last = new int[10];
    for (int i = 0; i < d.length; i++) last[d[i] - '0'] = i;
    for (int i = 0; i < d.length; i++)
        for (int dig = 9; dig > d[i] - '0'; dig--)
            if (last[dig] > i) {                                    // a larger digit later: swap with its LAST occurrence
                char t = d[i]; d[i] = d[last[dig]]; d[last[dig]] = t;
                return Integer.parseInt(new String(d));
            }
    return num;
}
int monotoneIncreasingDigits(int n) {
    char[] d = String.valueOf(n).toCharArray();
    int mark = d.length;
    for (int i = d.length - 1; i > 0; i--)
        if (d[i - 1] > d[i]) { d[i - 1]--; mark = i; }              // lower the previous digit, everything after becomes 9
    for (int i = mark; i < d.length; i++) d[i] = '9';
    return Integer.parseInt(new String(d));
}""",
           """def maximum_swap(num):
    d = list(str(num))
    last = {int(c): i for i, c in enumerate(d)}
    for i, c in enumerate(d):
        for dig in range(9, int(c), -1):
            if last.get(dig, -1) > i:                               # a larger digit later: swap with its LAST occurrence
                j = last[dig]
                d[i], d[j] = d[j], d[i]
                return int(''.join(d))
    return num

def monotone_increasing_digits(n):
    d = list(str(n))
    mark = len(d)
    for i in range(len(d) - 1, 0, -1):
        if d[i - 1] > d[i]:
            d[i - 1] = str(int(d[i - 1]) - 1)                       # lower the previous digit, everything after becomes 9
            mark = i
    for i in range(mark, len(d)):
        d[i] = '9'
    return int(''.join(d))""")],
    complexity="O(n·10) = O(n) time, O(10) space.",
    traps=["Swap with the **last** occurrence of the larger digit, not the first.", "Stop after the first successful swap (only one swap allowed).",
           "Monotone digits: scan from the **right** so a decrement can cascade leftwards.", "Convert with `String.valueOf` / `str`, then back; mind leading zeros."],
    variants=["Maximum 69 number: change the first 6 to 9.", "Remove k digits: monotonic stack (topic 05).", "Largest number: custom comparator `a + b` vs `b + a` (topic 06).", "Create maximum number from two arrays: choose the best subsequences greedily, then merge."],
    notuse="Multiple swaps or arbitrary rearrangements (different greedy / DP).",
    problems=[
        (1323, "Maximum 69 Number", "E", "maximum-69-number", "Change the first 6 to 9", "O(n) / O(n)"),
        (670, "Maximum Swap", "M", "maximum-swap", "Swap the leftmost improvable digit with the last largest to its right", "O(n) / O(1)"),
        (738, "Monotone Increasing Digits", "M", "monotone-increasing-digits", "Right-to-left fix: decrement, then 9s after the mark", "O(n) / O(1)"),
        (402, "Remove K Digits", "M", "remove-k-digits", "Monotonic stack removes larger digits first", "O(n) / O(n)"),
        (321, "Create Maximum Number", "H", "create-maximum-number", "Best subsequence from each array, then the best merge", "O((m+n)³) / O(k)"),
    ]))

# ---------------------------------------------------------------- 8
P.append(dict(
    title="Tracking a range of possibilities: valid parenthesis string", tier="hot", sim="parenrange", oneline="keep the interval of reachable balances instead of all choices",
    why="Turns 3^k choices into two integers", signature="LC 678 / 1541",
    when="Some symbols are flexible (wildcards) and you need to know whether **some** assignment works.",
    detect="\"valid parenthesis string with *\" · \"minimum insertions to balance\" · \"check if a parentheses string can be valid\" · locked / unlocked characters.",
    intuition="A `*` can be `(`, `)` or nothing, so the number of unmatched `(` after each character is not one number but a **set** of possible numbers, and that set is always a contiguous range `[lo, hi]`. Each character just moves or widens the interval: `(` shifts it up, `)` shifts it down, `*` stretches it both ways. If `hi` ever drops below 0 there are too many `)` even in the best case; at the end the string is valid if `0` is inside the range, i.e. `lo == 0`.",
    brute="Trying all assignments of each `*` is 3^k. The interval keeps only the smallest and largest possibilities in O(1) per character.",
    idea="`lo = hi = 0`. `(`: `lo++, hi++`. `)`: `lo--, hi--`. `*`: `lo--, hi++`. After each step: if `hi < 0` return false; `lo = max(lo, 0)`. Finally return `lo == 0`.",
    steps=["`lo = hi = 0`.", "Update by the current character as above.", "Fail immediately when `hi < 0`.", "Clamp `lo` to 0; at the end accept iff `lo == 0`."],
    trace_title="`(*))`",
    trace="""(   lo 1 hi 1
*   lo 0 hi 2     ( * could be ')' or '(' )
)   lo 0 hi 1
)   lo 0 hi 0
lo == 0 -> valid""",
    code=[("valid parenthesis string",
           """int lo = 0, hi = 0;                              // fewest / most possible unmatched '('
for (char c : s.toCharArray()) {
    if (c == '(') { lo++; hi++; }
    else if (c == ')') { lo--; hi--; }
    else { lo--; hi++; }                          // '*' as ')' or as '('
    if (hi < 0) return false;                     // too many ')' even if every '*' is '('
    lo = Math.max(lo, 0);                         // cannot have a negative count of unmatched '('
}
return lo == 0;""",
           """lo = hi = 0                                       # fewest / most possible unmatched '('
for c in s:
    if c == '(':
        lo += 1; hi += 1
    elif c == ')':
        lo -= 1; hi -= 1
    else:
        lo -= 1; hi += 1                           # '*' as ')' or as '('
    if hi < 0:
        return False                               # too many ')' even if every '*' is '('
    lo = max(lo, 0)                                # cannot have a negative count of unmatched '('
return lo == 0"""),
          ("minimum remove to make parentheses valid (stack of indices)",
           """Deque<Integer> st = new ArrayDeque<>();
boolean[] remove = new boolean[s.length()];
for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (c == '(') st.push(i);
    else if (c == ')') { if (st.isEmpty()) remove[i] = true; else st.pop(); }     // unmatched ')'
}
while (!st.isEmpty()) remove[st.pop()] = true;                                     // unmatched '('
StringBuilder sb = new StringBuilder();
for (int i = 0; i < s.length(); i++) if (!remove[i]) sb.append(s.charAt(i));""",
           """st, remove = [], set()
for i, c in enumerate(s):
    if c == '(':
        st.append(i)
    elif c == ')':
        if st: st.pop()
        else: remove.add(i)                                                         # unmatched ')'
remove.update(st)                                                                   # unmatched '('
return ''.join(c for i, c in enumerate(s) if i not in remove)""")],
    complexity="O(n) time, O(1) space (the stack version O(n)).",
    traps=["Clamp `lo` at 0 after **each** character.", "Check `hi < 0` before clamping `lo`.",
           "At the end test `lo == 0`, not `lo == hi`.", "Another valid approach: two passes (left to right, right to left) counting `(`+`*` and `)`+`*`."],
    variants=["Minimum insertions where `))` closes one `(`: track needed closers, count pairs.", "Check if a parentheses string can be valid (locked bits): same range with locked characters fixed.", "Interval of possible values appears in many \"wildcard\" greedy problems."],
    notuse="When wildcards carry different options that cannot be summarised by a count.",
    problems=[
        (1249, "Minimum Remove to Make Valid Parentheses", "M", "minimum-remove-to-make-valid-parentheses", "Stack of indices; remove unmatched ones", "O(n) / O(n)"),
        (678, "Valid Parenthesis String", "M", "valid-parenthesis-string", "Maintain [lo, hi] of unmatched '('", "O(n) / O(1)"),
        (1541, "Minimum Insertions to Balance a Parentheses String", "M", "minimum-insertions-to-balance-a-parentheses-string", "Each '(' needs two ')': track needed closers", "O(n) / O(1)"),
        (2116, "Check if a Parentheses String Can Be Valid", "M", "check-if-a-parentheses-string-can-be-valid", "Same range idea with locked / unlocked characters", "O(n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 9
P.append(dict(
    title="Ratio and value-per-cost greedy: fractional knapsack", tier="hot", sim="fracknap", oneline="sort by value per unit and take the best first",
    why="Shows exactly where greedy works, and where the 0/1 version breaks it", signature="LC 1710 / 1833",
    when="Items can be taken in any amount (or in uniform units) and each has a value and a cost; you want maximum value for a budget.",
    detect="\"maximum units on a truck\" · \"maximum ice cream bars\" · \"maximum bags with full capacity\" · \"fractional knapsack\" · \"best ratio first\".",
    intuition="If you can pour from containers, fill your bottle with the most valuable liquid per litre first, then the next, and so on. Any other order could be improved by swapping a litre of a lower-value liquid for a litre of a higher-value one, so taking best-ratio first is optimal. This only works because you can take **fractions** (or unit-sized items). With indivisible items a big high-ratio item can leave unusable space and a worse choice may fit better.",
    brute="Trying all subsets is O(2ⁿ). Sorting by ratio and filling the knapsack is O(n log n).",
    idea="Sort items by value-per-unit (or units-per-box) descending. Take whole items while capacity remains; take a fraction of the next one if allowed. For **cheapest first** budget problems (ice cream bars) sort by cost ascending.",
    steps=["Compute the ratio value / weight for each item.", "Sort descending by ratio.", "Take items fully while they fit; for the first that does not, take the fraction `remaining / weight` (if allowed).", "Sum the value."],
    trace_title="items (value, weight): A (60,10), B (100,20), C (120,30); capacity 50",
    trace="""ratios: A 6   B 5   C 4
take A  (cap 40)  value 60
take B  (cap 20)  value 160
take 20/30 of C   value 160 + 80 = 240
(0/1 version: best is B + C = 220, greedy by ratio gets A + B = 160  -> greedy fails)""",
    code=[("fractional knapsack and maximum units on a truck",
           """// fractional knapsack: items {value, weight}
Arrays.sort(items, (a, b) -> Double.compare((double) b[0] / b[1], (double) a[0] / a[1]));   // best ratio first
double total = 0; int cap = capacity;
for (int[] it : items) {
    if (cap >= it[1]) { total += it[0]; cap -= it[1]; }
    else { total += it[0] * ((double) cap / it[1]); break; }                                // take a fraction and stop
}

// maximum units on a truck: boxTypes {numberOfBoxes, unitsPerBox}
Arrays.sort(boxTypes, (a, b) -> b[1] - a[1]);                                                // most units per box first
int units = 0;
for (int[] t : boxTypes) {
    int take = Math.min(truckSize, t[0]);
    units += take * t[1]; truckSize -= take;
    if (truckSize == 0) break;
}""",
           """# fractional knapsack: items (value, weight)
items.sort(key=lambda it: it[0] / it[1], reverse=True)                                       # best ratio first
total, cap = 0.0, capacity
for v, w in items:
    if cap >= w:
        total += v; cap -= w
    else:
        total += v * cap / w                                                                  # take a fraction and stop
        break

# maximum units on a truck: boxTypes (numberOfBoxes, unitsPerBox)
box_types.sort(key=lambda t: t[1], reverse=True)                                              # most units per box first
units = 0
for boxes, per in box_types:
    take = min(truck_size, boxes)
    units += take * per
    truck_size -= take
    if truck_size == 0:
        break"""),
          ("maximum ice cream bars (cheapest first)",
           """Arrays.sort(costs);
int bars = 0;
for (int c : costs) {
    if (coins < c) break;                       // cannot afford the next cheapest
    coins -= c; bars++;
}
return bars;""",
           """costs.sort()
bars = 0
for c in costs:
    if coins < c:
        break                                   # cannot afford the next cheapest
    coins -= c
    bars += 1
return bars""")],
    complexity="O(n log n) for the sort, O(1) extra space.",
    traps=["Ratio greedy is **wrong for 0/1 knapsack**: use DP.", "Compare ratios as doubles (or cross-multiply) to avoid integer division.",
           "Take the fraction only for the last item and then stop.", "When all costs are 1 (unit items) the problem is just \"sort and take the cheapest\"."],
    variants=["Maximum bags with full capacity: sort remaining space ascending and fill the smallest first.", "Minimum cost to hire K workers: sort by wage / quality ratio plus a heap (topic 10).", "Huffman coding: repeatedly merge the two smallest weights (heap)."],
    notuse="Indivisible items with arbitrary weights (0/1 knapsack → DP, topic 16).",
    problems=[
        (1710, "Maximum Units on a Truck", "E", "maximum-units-on-a-truck", "Sort box types by units per box, take the best first", "O(n log n) / O(1)"),
        (1833, "Maximum Ice Cream Bars", "M", "maximum-ice-cream-bars", "Sort costs ascending; buy while affordable", "O(n log n) / O(1)"),
        (2279, "Maximum Bags With Full Capacity of Rocks", "M", "maximum-bags-with-full-capacity-of-rocks", "Fill the bags that need the fewest rocks first", "O(n log n) / O(n)"),
        (857, "Minimum Cost to Hire K Workers", "H", "minimum-cost-to-hire-k-workers", "Sort by wage/quality ratio; heap of the k smallest qualities", "O(n log n) / O(n)"),
    ]))

TOPIC = dict(
    id="greedy", file="14_greedy.html", title="Greedy Algorithms — Pattern Guide",
    lead="Greedy algorithms make the locally best choice at every step and never look back. They are short and fast when they are correct, and confidently wrong when they are not. This guide teaches when a greedy rule is safe (exchange argument, stays-ahead), then the recurring forms: jump games, running balance with resets, stock trading, two-pass sweeps, character and digit constructions, range tracking, and ratio-based selection. Each pattern has the intuition, a step-through animation, Java and Python code, and a ladder of LeetCode problems.",
    mindset="Greedy is a proof obligation, not a technique. For every rule you try, ask: **why can the first choice always be extended to an optimal answer?** Typical safe rules are \"take the one that ends first\", \"take the one that reaches farthest\", \"fix the most significant position first\", \"take the best ratio\". When you cannot argue it and a small counterexample exists, move to dynamic programming.",
    qintro="Ask these questions on every optimisation problem:",
    questions=["**Is there an obvious local rule (largest, earliest, farthest, best ratio)?**", "**Can I break it with a small counterexample?** (try ties, extremes, 3–4 elements)", "**Can I argue an exchange: swap an optimal choice for mine without loss?**",
               "**Do choices interact so that today's pick changes what is possible later?** → DP.", "**Does sorting by a key make the rule a single scan?**"],
    cues=[
        ["\"is the largest-first rule optimal?\", change-making", "**P1** Greedy and its proof"],
        ["\"can you reach the end\", \"minimum jumps\", \"cover with intervals\"", "**P2** Jump games"],
        ["\"circular tour\", running sum must stay ≥ 0", "**P3** Running balance with resets"],
        ["\"buy and sell\", unlimited transactions", "**P4** Stock greedy"],
        ["\"depends on both neighbours\", candy, rain water", "**P5** Two-pass greedy"],
        ["\"as many parts as possible\", balance counts in strings", "**P6** Greedy on characters"],
        ["\"swap once for the largest number\", digit constructions", "**P7** Leftmost-position greedy"],
        ["wildcard `*` in brackets", "**P8** Range of possibilities"],
        ["\"best value per unit\", \"maximum items within budget\"", "**P9** Ratio greedy"],
    ],
    choose=[
        ["Choices are independent and a rule is provable", "Greedy (all patterns)"],
        ["Choices interact; no safe local rule", "Dynamic programming (topics 15–16)"],
        ["Maximum number of non-overlapping intervals", "Sort by end time (topic 06 P7)"],
        ["Best ratio, items divisible", "Sort by ratio (P9)"],
        ["Reach farthest / fewest moves forward", "Level sweep (P2)"],
        ["Constraints from both sides", "Two passes (P5)"],
        ["Heap makes the best option cheap to get", "Greedy + heap (topic 10)"],
    ],
    rule="**sort by the right key, then scan once; keep a small amount of state (farthest, running balance, count, range); and justify the rule with an exchange argument.** If you can build a counterexample in a minute, it is DP.",
    selftest=[
        ("What is an exchange argument?", "Take an optimal solution that differs from the greedy one at the first step, swap in the greedy choice, and show the result is no worse. Repeating this shows greedy is optimal."),
        ("Why does greedy fail for coin change with coins {1, 3, 4} and amount 6?", "Greedy takes 4 then 1 + 1 (3 coins) but 3 + 3 uses only 2. The locally largest coin forces a worse overall result, so the choice is not safe."),
        ("Why can you reset the start in the gas-station problem when the tank goes negative?", "Any station between the old start and the failure point arrives at the failure with at most the fuel that the old start had (which was already negative), so none of them works; try the next station."),
        ("Why is summing every positive daily difference optimal for unlimited stock trades?", "A rise from a to c equals the sum of the smaller rises in between, so capturing every small rise matches the best single long trades and ignores the drops."),
        ("Why does Candy need two passes and a `max`?", "Each child depends on both neighbours. The left-to-right pass satisfies the left rule, the right-to-left pass the right rule, and `max` keeps the earlier requirement from being lowered."),
        ("In Jump Game II why loop only to `n − 2`?", "Once you can reach the last index no further jump is needed; counting a jump at the last index would add one too many."),
        ("Why does fractional knapsack by ratio work but 0/1 knapsack does not?", "With fractions you can always swap a lower-ratio unit for a higher-ratio one. With whole items a high-ratio item may leave unusable capacity, so a combination of lower-ratio items can be better."),
        ("What invariant does the valid-parenthesis-string solution keep?", "The interval `[lo, hi]` of possible unmatched `(` counts, which is always contiguous; `hi < 0` is a failure and `lo == 0` at the end means success."),
    ],
    plan=[
        "**Day 1:** the proof mindset: coin change counterexample, then lemonade change, assign cookies.",
        "**Day 2:** jump games and interval covering; write the level sweep from memory.",
        "**Day 3:** gas station and stock trading; explain why each rule is safe.",
        "**Day 4:** two-pass greedy: candy, trapping rain water.",
        "**Day 5:** character and digit constructions: partition labels, maximum swap, monotone digits.",
        "**Day 6:** range tracking (valid parenthesis string), ratio greedy, then redo each problem and write its exchange argument in one sentence.",
    ],
    patterns=P,
)
