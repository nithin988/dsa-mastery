"""Content for topic 08: Bit manipulation and math."""

P = []

# ---------------------------------------------------------------- 1
P.append(dict(
    title="Bit basics: the operators and the six core tricks", tier="hot", sim="bits", oneline="shift to reach a bit, mask to read or change it",
    why="Every bit problem is built from these few moves", signature="LC 191 / 231",
    when="You need to read, set, clear or flip individual bits, or test a property of the binary form of a number.",
    detect="\"number of 1 bits\" · \"power of two\" · \"reverse bits\" · \"hamming distance\" · \"complement\" · \"is the i-th bit set\".",
    intuition="A number is a row of light switches (bits), and the operators are ways of acting on switches. **AND** keeps only switches that are on in both rows, **OR** turns on every switch that is on in either, **XOR** flips switches where the rows differ, **shifts** slide the whole row. A mask such as `1 << i` is a row with exactly one switch on: AND with it reads that switch, OR sets it, XOR toggles it.",
    brute="Converting to a string of 0/1 characters and looping works but is slow and clumsy. Bit operations act on all 32 bits in one CPU instruction.",
    idea="Memorise the mask idioms: read `(x >> i) & 1`; set `x | (1 << i)`; clear `x & ~(1 << i)`; toggle `x ^ (1 << i)`; clear lowest set bit `x & (x − 1)`; isolate lowest set bit `x & −x`.",
    steps=["Pick the mask: `1 << i` for one bit, `(1 << k) − 1` for the lowest k bits.", "Combine with `&` (keep / read), `|` (set), `^` (toggle).", "Use `x & (x − 1)` to drop the lowest set bit, and `x & −x` to isolate it.", "Use `>>>` (Java) for an unsigned right shift; Python ints are unbounded, so mask with `& 0xFFFFFFFF` for 32-bit behaviour."],
    trace_title="`x = 44 = 00101100`",
    trace="""read bit 2:     (44 >> 2) & 1            = 1
set bit 0:      44 | 1                   = 45  (00101101)
clear bit 2:    45 & ~(1 << 2)           = 41  (00101001)
toggle bit 5:   41 ^ 32                  = 9   (00001001)
drop low bit:   9 & 8                    = 8   (00001000)
low bit only:   9 & -9                   = 1
power of two?   8 & 7 == 0               yes""",
    code=[("the idioms",
           """boolean isSet = ((x >> i) & 1) == 1;
x |= (1 << i);              // set bit i
x &= ~(1 << i);             // clear bit i
x ^= (1 << i);              // toggle bit i
x &= (x - 1);               // clear the lowest set bit
int low = x & -x;           // isolate the lowest set bit
boolean pow2 = x > 0 && (x & (x - 1)) == 0;
int unsigned = x >>> 1;     // >> keeps the sign bit, >>> fills with 0""",
           """is_set = (x >> i) & 1 == 1
x |= 1 << i                 # set bit i
x &= ~(1 << i)              # clear bit i
x ^= 1 << i                 # toggle bit i
x &= x - 1                  # clear the lowest set bit
low = x & -x                # isolate the lowest set bit
pow2 = x > 0 and x & (x - 1) == 0
# Python ints are unbounded: use & 0xFFFFFFFF to emulate 32-bit unsigned"""),
          ("reverse the 32 bits of an integer",
           """int r = 0;
for (int i = 0; i < 32; i++) {
    r = (r << 1) | (n & 1);      // take the lowest bit of n, append it to r
    n >>>= 1;
}
return r;""",
           """r = 0
for _ in range(32):
    r = (r << 1) | (n & 1)       # take the lowest bit of n, append it to r
    n >>= 1
return r""")],
    complexity="O(1) per operation; loops over bits are O(32) = O(1) or O(log n).",
    traps=["Operator precedence: in Java and C, `==` binds tighter than `&`, so write `(x & 1) == 1` (Python is the opposite, but parenthesise anyway).", "Java `int` is 32-bit and signed: `1 << 31` is negative; use `1L << i` for bit 31 and above in `long`.",
           "`>>` is arithmetic (copies the sign bit), `>>>` is logical; they differ for negative numbers.", "Python has no fixed width: `~x` is `−x − 1`, and negative numbers behave as infinite two's complement."],
    variants=["Complement of a number: XOR with a mask of its bit length, `(1 << bitLength) − 1`.", "Hamming distance: `bitCount(x ^ y)`.", "Power of four: power of two **and** the set bit is at an even position (`x & 0x55555555 != 0`)."],
    notuse="When clarity matters more and speed is irrelevant; but in interviews these idioms are expected.",
    problems=[
        (191, "Number of 1 Bits", "E", "number-of-1-bits", "Loop `n &= n − 1` and count", "O(set bits) / O(1)"),
        (231, "Power of Two", "E", "power-of-two", "Exactly one set bit: n > 0 and n & (n − 1) == 0", "O(1) / O(1)"),
        (342, "Power of Four", "E", "power-of-four", "Power of two whose bit sits at an even position", "O(1) / O(1)"),
        (461, "Hamming Distance", "E", "hamming-distance", "Count the set bits of x XOR y", "O(1) / O(1)"),
        (476, "Number Complement", "E", "number-complement", "XOR with a mask of the number's length", "O(1) / O(1)"),
        (190, "Reverse Bits", "E", "reverse-bits", "Shift the lowest bit of n into r, 32 times", "O(32) / O(1)"),
    ]))

# ---------------------------------------------------------------- 2
P.append(dict(
    title="XOR tricks: cancelling pairs", tier="hot", sim="xor", oneline="x ^ x = 0, so equal pairs vanish",
    why="Gives O(1)-space answers to \"find the odd one out\" questions", signature="LC 136 / 268",
    when="All values appear in pairs except one (or two), or a value is missing from a known range.",
    detect="\"single number\" · \"missing number\" · \"find the difference\" · \"every element appears twice except\" · \"duplicate or missing\".",
    intuition="XOR is addition modulo 2 with no carry: `x ^ x = 0`, `x ^ 0 = x`, and it is commutative and associative. So XOR-ing a whole list makes every pair cancel to zero and leaves the unpaired number, no matter the order. No hash map is needed.",
    brute="Count occurrences in a hash map: O(n) time and O(n) space. XOR gives the same answer in O(n) time with O(1) space.",
    idea="Fold the array with XOR. For a missing number in `0..n`, XOR all indices and all values; the missing one is the only number not cancelled. For **two** unique numbers, XOR everything to get `a ^ b`, find any set bit of it, and split the numbers into two groups by that bit.",
    steps=["`acc = 0`; for each value `acc ^= v`.", "Pairs cancel; `acc` is the answer for one unique number.", "Missing number: `acc = n`, then `acc ^= i ^ a[i]` for each index.", "Two unique numbers: `d = acc & −acc` splits them; XOR each group separately."],
    trace_title="`[4,1,2,1,2]`",
    trace="""0 ^ 4 = 4    (100)
4 ^ 1 = 5    (101)
5 ^ 2 = 7    (111)
7 ^ 1 = 6    (110)   the two 1s cancelled
6 ^ 2 = 4    (100)   the two 2s cancelled
=> 4""",
    code=[("single number and missing number",
           """int single = 0;
for (int x : nums) single ^= x;                        // pairs cancel

int missing = nums.length;                              // numbers 0..n, one is absent
for (int i = 0; i < nums.length; i++) missing ^= i ^ nums[i];""",
           """single = 0
for x in nums:
    single ^= x                                        # pairs cancel

missing = len(nums)                                    # numbers 0..n, one is absent
for i, x in enumerate(nums):
    missing ^= i ^ x"""),
          ("two numbers appear once, all others twice",
           """int all = 0;
for (int x : nums) all ^= x;                           // all = a ^ b, a != b
int bit = all & -all;                                  // a bit where a and b differ
int a = 0, b = 0;
for (int x : nums) { if ((x & bit) == 0) a ^= x; else b ^= x; }
return new int[]{a, b};""",
           """all_xor = 0
for x in nums:
    all_xor ^= x                                       # a ^ b, a != b
bit = all_xor & -all_xor                               # a bit where a and b differ
a = b = 0
for x in nums:
    if x & bit:
        b ^= x
    else:
        a ^= x
return [a, b]""")],
    complexity="O(n) time, O(1) space.",
    traps=["Only works when every other value appears an **even** number of times (use bit counting mod 3 for \"three times\").", "Missing number with negatives or a range that does not start at 0 needs adjusting (use the sum formula or offset).",
           "`a ^ b` can be 0 only if `a == b`; for two uniques it is non-zero, so a differing bit exists.", "Do not confuse XOR (`^`) with exponent in Python (`**`)."],
    variants=["Single Number II (others appear 3 times): count each bit position mod 3, or use `ones` and `twos` accumulators.", "Find the difference between two strings: XOR all characters.", "Prefix XOR: subarray XOR = `prefix[j] ^ prefix[i − 1]` (like prefix sums)."],
    notuse="Values repeating an odd number of times, or when you must return the positions or counts of duplicates.",
    problems=[
        (136, "Single Number", "E", "single-number", "XOR everything; pairs vanish", "O(n) / O(1)"),
        (389, "Find the Difference", "E", "find-the-difference", "XOR all characters of both strings", "O(n) / O(1)"),
        (268, "Missing Number", "E", "missing-number", "XOR indices with values, or the sum formula", "O(n) / O(1)"),
        (260, "Single Number III", "M", "single-number-iii", "XOR all, split by the lowest differing bit", "O(n) / O(1)"),
        (137, "Single Number II", "M", "single-number-ii", "Count each bit mod 3 (or ones/twos accumulators)", "O(n) / O(1)"),
        (1442, "Count Triplets That Can Form Two Arrays of Equal XOR", "M", "count-triplets-that-can-form-two-arrays-of-equal-xor", "Prefix XOR: equal prefixes mean a zero-XOR subarray", "O(n²) / O(1)"),
    ]))

# ---------------------------------------------------------------- 3
P.append(dict(
    title="Counting set bits (Kernighan and bit DP)", tier="hot", sim="kernighan", oneline="n & (n − 1) removes one set bit per step",
    why="Population count shows up in many easy problems and as a building block", signature="LC 191 / 338",
    when="Count 1 bits of one number, or of every number from 0 to n.",
    detect="\"number of 1 bits\" · \"counting bits\" · \"sort by number of set bits\" · \"binary gap\" · \"prime number of set bits\".",
    intuition="Checking every one of 32 bits is wasteful when only a few are set. The trick `n & (n − 1)` always deletes the **lowest** 1: subtracting 1 turns that bit to 0 and all the zeros below it to 1, so AND-ing wipes out precisely that bit. Repeat until nothing is left; the number of repeats is the answer.",
    brute="Test all 32 bits: O(32). Kernighan's loop runs once per set bit. For many numbers, reuse earlier answers: `bits[i] = bits[i >> 1] + (i & 1)`.",
    idea="Loop `while n != 0: n &= n − 1; count++`. For all numbers up to n use the recurrence on the number with its last bit removed.",
    steps=["`count = 0`.", "While `n != 0`: `n &= n − 1`; `count++`.", "Return `count`.", "For 0..n: `bits[0] = 0`; `bits[i] = bits[i >> 1] + (i & 1)`."],
    trace_title="`13 = 1101`",
    trace="""13 (1101) & 12 (1100) = 12 (1100)   count 1
12 (1100) & 11 (1011) =  8 (1000)   count 2
 8 (1000) &  7 (0111) =  0          count 3
=> 3 set bits""",
    code=[("Kernighan's algorithm",
           """int count = 0;
while (n != 0) {
    n &= n - 1;              // drop the lowest set bit
    count++;
}
return count;
// built-in: Integer.bitCount(n)""",
           """count = 0
while n:
    n &= n - 1               # drop the lowest set bit
    count += 1
return count
# built-in: n.bit_count() (3.10+) or bin(n).count('1')"""),
          ("counting bits for 0..n with DP",
           """int[] bits = new int[n + 1];
for (int i = 1; i <= n; i++) bits[i] = bits[i >> 1] + (i & 1);     // reuse the answer for i / 2""",
           """bits = [0] * (n + 1)
for i in range(1, n + 1):
    bits[i] = bits[i >> 1] + (i & 1)                                # reuse the answer for i // 2""")],
    complexity="Kernighan: O(set bits) ≤ O(32). Counting bits 0..n: O(n) time, O(n) space.",
    traps=["In Java use `>>>` or the `n != 0` loop for negative numbers (an unsigned view); `n > 0` would skip them.", "In Python the loop `n &= n − 1` never terminates for a negative `n`; mask to 32 bits first (`n &= 0xFFFFFFFF`).",
           "The DP recurrence needs `i >> 1` computed **before** `i`, so iterate upward.", "Do not forget `bits[0] = 0`."],
    variants=["Hamming weight of all numbers in a range with a lookup table of bytes.", "Binary gap: scan positions of set bits.", "Check alternating bits: `n ^ (n >> 1)` is all ones."],
    notuse="You can call `Integer.bitCount` / `int.bit_count()` unless the interviewer asks you to implement it.",
    problems=[
        (338, "Counting Bits", "E", "counting-bits", "bits[i] = bits[i >> 1] + (i & 1)", "O(n) / O(n)"),
        (693, "Binary Number with Alternating Bits", "E", "binary-number-with-alternating-bits", "x = n ^ (n >> 1) must be all ones", "O(1) / O(1)"),
        (868, "Binary Gap", "E", "binary-gap", "Track the distance between consecutive set bits", "O(log n) / O(1)"),
        (762, "Prime Number of Set Bits in Binary Representation", "E", "prime-number-of-set-bits-in-binary-representation", "bitCount then check against small primes", "O(n) / O(1)"),
        (1356, "Sort Integers by The Number of 1 Bits", "E", "sort-integers-by-the-number-of-1-bits", "Sort by (bitCount, value)", "O(n log n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 4
P.append(dict(
    title="Bitmasks: subsets and state compression", tier="hot", sim="masksubs", oneline="an integer is a set; bit i means \"item i is in\"",
    why="The bridge from backtracking to bitmask dynamic programming", signature="LC 78 / 89 / 1239",
    when="Enumerate all subsets of up to ~20 items, or remember which of a few items you have used.",
    detect="\"all subsets\" · \"gray code\" · \"smallest sufficient team\" · \"visit all nodes\" · small n (≤ 20) with \"set of chosen items\" as state.",
    intuition="A set of up to 32 yes/no items fits in one integer: bit i is 1 if item i is in the set. Counting from 0 to 2ⁿ − 1 visits every possible set exactly once. Set operations become single instructions: union `|`, intersection `&`, difference `& ~`, membership `& (1 << i)`.",
    brute="Recursive subset generation uses a list and a call stack. A mask loop uses neither and is the key to **bitmask DP**, where the state \"which items are already used\" is an integer you can use as an array index.",
    idea="`for (mask = 0; mask < (1 << n); mask++)`: item `i` is chosen when `mask >> i & 1`. Submasks of `m`: `for (s = m; s > 0; s = (s − 1) & m)`. Gray code: `i ^ (i >> 1)` changes one bit between neighbours.",
    steps=["Let `n` be the number of items; there are `2ⁿ` masks.", "Loop `mask` from `0` to `(1 << n) − 1`.", "Inner loop over bits to read the chosen items (or use the mask as a DP state).", "To iterate submasks of `m`, use `s = (s − 1) & m` until `s` becomes 0."],
    trace_title="items `a, b, c`",
    trace="""mask 0 = 000  {}
mask 1 = 001  {a}
mask 2 = 010  {b}
mask 3 = 011  {a,b}
mask 4 = 100  {c}
mask 5 = 101  {a,c}
mask 6 = 110  {b,c}
mask 7 = 111  {a,b,c}""",
    code=[("enumerate subsets, submasks and gray code",
           """for (int mask = 0; mask < (1 << n); mask++) {
    List<Integer> subset = new ArrayList<>();
    for (int i = 0; i < n; i++) if ((mask >> i & 1) == 1) subset.add(a[i]);
    res.add(subset);
}
// every non-empty submask of m
for (int s = m; s > 0; s = (s - 1) & m) { /* use s */ }
// n-bit gray code: consecutive values differ in exactly one bit
for (int i = 0; i < (1 << n); i++) gray.add(i ^ (i >> 1));""",
           """for mask in range(1 << n):
    res.append([a[i] for i in range(n) if mask >> i & 1])

s = m                                           # every non-empty submask of m
while s:
    # use s
    s = (s - 1) & m

gray = [i ^ (i >> 1) for i in range(1 << n)]    # consecutive values differ in exactly one bit"""),
          ("track which letters a string uses (unique-character concatenation)",
           """int best = 0;
int[] masks = new int[n]; boolean[] ok = new boolean[n];
for (int i = 0; i < n; i++) {
    int m = 0; boolean unique = true;
    for (char c : arr.get(i).toCharArray()) { if ((m >> (c - 'a') & 1) == 1) { unique = false; break; } m |= 1 << (c - 'a'); }
    masks[i] = m; ok[i] = unique;
}
// dfs(index, usedMask): add arr[i] only if ok[i] && (usedMask & masks[i]) == 0""",
           """def mask_of(w):
    m = 0
    for c in w:
        bit = 1 << (ord(c) - 97)
        if m & bit:
            return -1                          # repeated letter: word unusable
        m |= bit
    return m
# dfs(i, used): take arr[i] only if mask_of(arr[i]) != -1 and used & mask == 0""")],
    complexity="O(2ⁿ · n) to enumerate subsets; works for n up to about 20–25.",
    traps=["Use `1 << i` as `int` only up to 31; use `1L << i` for larger masks.", "Operator precedence: `mask >> i & 1` parses as `(mask >> i) & 1`, which is what you want, but parenthesise for clarity.",
           "`(s − 1) & m` stops at 0: handle the empty submask separately if needed.", "If n > 25, bitmask enumeration is too slow: look for DP or pruning."],
    variants=["Bitmask DP (travelling salesman, assignment): `dp[mask][last]`.", "Subset sums in `2^(n/2)` with meet in the middle.", "Smallest sufficient team: `dp[skillMask] = smallest team covering it`."],
    notuse="n larger than ~25, or when the items have structure that lets you do polynomial DP.",
    problems=[
        (78, "Subsets", "M", "subsets", "Every mask 0..2ⁿ−1 is one subset", "O(n·2ⁿ) / O(1) extra"),
        (89, "Gray Code", "M", "gray-code", "i ^ (i >> 1) for i in 0..2ⁿ−1", "O(2ⁿ) / O(1) extra"),
        (1239, "Maximum Length of a Concatenated String with Unique Characters", "M", "maximum-length-of-a-concatenated-string-with-unique-characters", "Letter mask per word; include if masks do not overlap", "O(2ⁿ) / O(n)"),
        (1125, "Smallest Sufficient Team", "H", "smallest-sufficient-team", "dp over skill masks", "O(2^S · P) / O(2^S)"),
        (847, "Shortest Path Visiting All Nodes", "H", "shortest-path-visiting-all-nodes", "BFS over (node, visitedMask) states", "O(2ⁿ·n) / O(2ⁿ·n)"),
    ]))

# ---------------------------------------------------------------- 5
P.append(dict(
    title="Arithmetic with bits: adder, shifts and ranges", tier="sec", sim="adder", oneline="XOR is add without carry; AND shifted is the carry",
    why="Shows you understand how addition and division work underneath", signature="LC 371 / 201",
    when="Arithmetic is forbidden or must be done at bit level, or a range operation has a bitwise pattern.",
    detect="\"sum of two integers without + or −\" · \"divide without /\" · \"bitwise AND of a range\" · \"multiply by powers of two\" · \"minimum flips\".",
    intuition="Adding two bits: the sum bit is their XOR; a carry is produced only when both are 1 (AND), and it belongs one position to the left. So `a + b = (a ^ b) + ((a & b) << 1)`. Apply it again to the right-hand pair until no carry remains. For the range AND of `[l, r]`, only the common binary prefix of `l` and `r` survives; every lower bit varies somewhere in the range and ANDs to 0.",
    brute="Looping `b` times with `a++` is O(b). The XOR/carry loop is O(32). The range AND by looping from `l` to `r` is O(r − l); shifting until `l == r` is O(32).",
    idea="Adder: `while (b != 0) { carry = (a & b) << 1; a ^= b; b = carry; }`. Range AND: shift both right until equal, then shift back. Multiplying by 2ᵏ is `<< k`; dividing is `>> k` (floor for non-negatives).",
    steps=["Adder: compute `sum = a ^ b` and `carry = (a & b) << 1`.", "Set `a = sum`, `b = carry`; repeat until `b == 0`.", "Range AND: `shift = 0`; while `l != r`: `l >>= 1`, `r >>= 1`, `shift++`.", "Return `l << shift`."],
    trace_title="`5 + 3` (0101 + 0011)",
    trace="""a=0101 b=0011  xor 0110  carry 0010
a=0110 b=0010  xor 0100  carry 0100
a=0100 b=0100  xor 0000  carry 1000
a=0000 b=1000  xor 1000  carry 0000  -> 8""",
    code=[("add two integers without +",
           """while (b != 0) {
    int carry = (a & b) << 1;     // positions where both bits are 1 carry to the left
    a = a ^ b;                    // sum without the carry
    b = carry;
}
return a;                          // works for negatives too: Java ints wrap in two's complement""",
           """MASK, MAX = 0xFFFFFFFF, 0x7FFFFFFF           # Python ints are unbounded: emulate 32 bits
while b:
    a, b = (a ^ b) & MASK, ((a & b) << 1) & MASK
return a if a <= MAX else ~(a ^ MASK)           # convert back to a signed value"""),
          ("bitwise AND of a range [l, r]",
           """int shift = 0;
while (l != r) { l >>= 1; r >>= 1; shift++; }      // keep only the common prefix
return l << shift;""",
           """shift = 0
while l != r:
    l >>= 1
    r >>= 1
    shift += 1                                      # keep only the common prefix
return l << shift""")],
    complexity="O(32) = O(1) for the adder and range AND.",
    traps=["In Python the carry loop never ends for negative numbers unless you mask to 32 bits.", "Shifting by ≥ 32 in Java uses the shift count mod 32.",
           "Divide two integers: handle `Integer.MIN_VALUE / −1` overflow and use `long` for the subtraction loop.", "`x << 1` overflows silently in Java; use `long` when needed."],
    variants=["Divide without `/`: subtract the largest `divisor << k` that fits, accumulate `1 << k`.", "Minimum flips to make `a | b == c`: compare bit by bit.", "Swap two variables without a temp: `a ^= b; b ^= a; a ^= b`."],
    notuse="Normal arithmetic: use `+`; this is for interviews that explicitly forbid it.",
    problems=[
        (371, "Sum of Two Integers", "M", "sum-of-two-integers", "XOR for the sum, AND << 1 for the carry, repeat", "O(1) / O(1)"),
        (201, "Bitwise AND of Numbers Range", "M", "bitwise-and-of-numbers-range", "Common binary prefix of l and r", "O(1) / O(1)"),
        (1318, "Minimum Flips to Make a OR b Equal to c", "M", "minimum-flips-to-make-a-or-b-equal-to-c", "Check each bit position against c", "O(1) / O(1)"),
        (29, "Divide Two Integers", "M", "divide-two-integers", "Subtract shifted divisors; guard the overflow case", "O(log² n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 6
P.append(dict(
    title="Fast exponentiation and modular arithmetic", tier="hot", sim="fastpow", oneline="square the base, multiply when the exponent bit is 1",
    why="Turns O(n) powers into O(log n) and keeps numbers from overflowing", signature="LC 50 / 1922",
    when="Raise to huge powers, compute results \"modulo 10⁹ + 7\", or search for a square root.",
    detect="\"pow(x, n)\" · \"count good numbers\" · \"modulo 10^9 + 7\" · \"super pow\" · \"square root\" · exponents up to 10⁹ or more.",
    intuition="`3^13 = 3^8 · 3^4 · 3^1` because 13 in binary is `1101`. You only need the squares `3, 9, 81, 6561, …` (each is the previous squared) and multiply together those that correspond to 1 bits. That is log₂(13) ≈ 4 squarings instead of 12 multiplications. When the answer must be modulo `M`, reduce after every multiplication; the rules `(a·b) mod M = ((a mod M)(b mod M)) mod M` make this safe.",
    brute="Multiply n times: O(n), impossible for n = 10⁹. Repeated squaring: O(log n).",
    idea="Walk the exponent's bits from the least significant: `if (e & 1) result *= base`; `base *= base`; `e >>= 1`. For division modulo a prime `p`, use the inverse `a^(p − 2) mod p` (Fermat).",
    steps=["`result = 1`, `base %= M`.", "While `e > 0`: if `e` is odd, `result = result · base mod M`.", "`base = base · base mod M`; `e >>= 1`.", "Return `result`. For negative exponents, invert the base and negate `e`."],
    trace_title="`3^13` (13 = 1101)",
    trace="""bit0 = 1  result = 3          base 3 -> 9
bit1 = 0  skip                base 9 -> 81
bit2 = 1  result = 3*81 = 243 base 81 -> 6561
bit3 = 1  result = 243*6561 = 1594323
=> 3^13 = 1594323""",
    code=[("binary exponentiation with a modulus",
           """long power(long base, long exp, long mod) {
    long result = 1;
    base %= mod;
    while (exp > 0) {
        if ((exp & 1) == 1) result = result * base % mod;
        base = base * base % mod;                 // base^(2^k)
        exp >>= 1;
    }
    return result;
}
// modular inverse for prime mod: power(a, mod - 2, mod)""",
           """def power(base, exp, mod):
    result, base = 1, base % mod
    while exp > 0:
        if exp & 1:
            result = result * base % mod
        base = base * base % mod                  # base^(2^k)
        exp >>= 1
    return result
# built-in: pow(base, exp, mod); modular inverse for prime mod: pow(a, mod - 2, mod)"""),
          ("integer square root by binary search",
           """int lo = 1, hi = x, ans = 0;
while (lo <= hi) {
    int mid = lo + (hi - lo) / 2;
    if (mid <= x / mid) { ans = mid; lo = mid + 1; }     // x / mid avoids overflow of mid * mid
    else hi = mid - 1;
}
return ans;""",
           """lo, hi, ans = 1, x, 0
while lo <= hi:
    mid = (lo + hi) // 2
    if mid * mid <= x:
        ans, lo = mid, mid + 1
    else:
        hi = mid - 1
return ans                                          # or math.isqrt(x)""")],
    complexity="O(log exp) multiplications; sqrt by binary search O(log x).",
    traps=["Multiplying two numbers below 10⁹ + 7 needs `long` (they overflow `int`).", "Take the modulo after **each** multiplication.",
           "Negative exponent: compute `1 / base` once, or `power(1/base, −exp)`; beware `−Integer.MIN_VALUE`.", "Division mod p is **not** `a / b % p`: multiply by the modular inverse."],
    variants=["Count good numbers: `5^ceil(n/2) · 4^floor(n/2) mod M` with fast power.", "Super pow: exponent given as an array of digits; use `a^(10k + d) = (a^k)^10 · a^d`.", "Matrix exponentiation for Fibonacci in O(log n)."],
    notuse="Small exponents (a simple loop), or floating-point powers where the language provides `Math.pow`.",
    problems=[
        (69, "Sqrt(x)", "E", "sqrtx", "Binary search the largest m with m·m ≤ x", "O(log x) / O(1)"),
        (367, "Valid Perfect Square", "E", "valid-perfect-square", "Binary search m·m == x", "O(log x) / O(1)"),
        (50, "Pow(x, n)", "M", "powx-n", "Repeated squaring; handle negative n", "O(log n) / O(1)"),
        (1922, "Count Good Numbers", "M", "count-good-numbers", "5^(even positions) · 4^(odd positions) mod 10⁹+7", "O(log n) / O(1)"),
        (372, "Super Pow", "M", "super-pow", "Exponent as digits: fold with pow(a, 10) · pow(a, d)", "O(n log 10) / O(1)"),
    ]))

# ---------------------------------------------------------------- 7
P.append(dict(
    title="GCD, primes and divisibility", tier="hot", sim="sieve", oneline="Euclid for GCD; cross out multiples for primes",
    why="Number-theory staples: GCD, primality, factorisation", signature="LC 204 / 1979",
    when="Divisibility, common factors, counting or generating primes, or simplifying fractions and ratios.",
    detect="\"greatest common divisor\" · \"count primes\" · \"ugly numbers\" · \"water and jug\" · \"smallest multiple\" · \"prime factors\".",
    intuition="Euclid: any number that divides both `a` and `b` also divides `a mod b`, so `gcd(a, b) = gcd(b, a mod b)`, and the numbers shrink very fast. The sieve flips primality testing around: instead of testing every number, a prime **crosses out all its multiples**, so what is never crossed out is prime. Starting at `p²` is enough because smaller multiples have a smaller prime factor and were already crossed out.",
    brute="Test each number up to n by trial division: O(n√n). The sieve is O(n log log n). GCD by listing divisors is O(n); Euclid is O(log min(a, b)).",
    idea="`gcd(a, b) = b == 0 ? a : gcd(b, a % b)`; `lcm(a, b) = a / gcd(a, b) * b`. Sieve: `for p from 2 while p·p ≤ n: if prime[p]: mark p·p, p·p + p, …`. Factorise by trial division up to √n, dividing out each prime completely.",
    steps=["GCD: repeat `(a, b) = (b, a mod b)` until `b == 0`.", "Sieve: boolean array `composite[0..n]`.", "For `p = 2` while `p·p ≤ n`: if not composite, mark `p·p, p·p + p, …`.", "Primes are the unmarked numbers ≥ 2."],
    trace_title="`gcd(48, 18)` and the sieve up to 30",
    trace="""gcd(48,18) -> gcd(18,12) -> gcd(12,6) -> gcd(6,0) = 6
sieve: p=2 crosses 4 6 8 ... 30
       p=3 crosses 9 15 21 27 (6,12,... already crossed)
       p=5 crosses 25
       p=7: 49 > 30 stop
primes: 2 3 5 7 11 13 17 19 23 29""",
    code=[("gcd, lcm and the sieve",
           """int gcd(int a, int b) { return b == 0 ? a : gcd(b, a % b); }
long lcm(int a, int b) { return (long) a / gcd(a, b) * b; }     // divide first to avoid overflow

int countPrimes(int n) {                                          // primes < n
    boolean[] comp = new boolean[Math.max(n, 2)];
    int count = 0;
    for (int i = 2; i < n; i++) {
        if (comp[i]) continue;
        count++;
        for (long j = (long) i * i; j < n; j += i) comp[(int) j] = true;
    }
    return count;
}""",
           """from math import gcd
def lcm(a, b):
    return a // gcd(a, b) * b                                    # divide first

def count_primes(n):                                             # primes < n
    if n < 3:
        return 0
    sieve = [True] * n
    sieve[0] = sieve[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = [False] * len(range(i * i, n, i))
    return sum(sieve)"""),
          ("prime factorisation by trial division",
           """Map<Integer, Integer> factors = new TreeMap<>();
for (int p = 2; (long) p * p <= n; p++) {
    while (n % p == 0) { factors.merge(p, 1, Integer::sum); n /= p; }
}
if (n > 1) factors.merge(n, 1, Integer::sum);       // what remains is a single prime""",
           """factors = {}
p = 2
while p * p <= n:
    while n % p == 0:
        factors[p] = factors.get(p, 0) + 1
        n //= p
    p += 1
if n > 1:
    factors[n] = factors.get(n, 0) + 1              # what remains is a single prime""")],
    complexity="GCD O(log min(a, b)). Sieve O(n log log n) time, O(n) space. Factorisation O(√n).",
    traps=["Start inner marking at `i·i` and use `long` for `i·i` to avoid overflow.", "`lcm` as `a * b / gcd` can overflow: divide first.",
           "Primes strictly less than `n` for LC 204; `n < 3` has no primes.", "Water and Jug: reachable amounts are multiples of `gcd(x, y)` up to `x + y`."],
    variants=["Ugly numbers: divide out 2, 3 and 5 and test for 1; Ugly Number II uses three pointers.", "GCD of an array: fold `gcd` over the elements.", "GCD of strings: the answer has length `gcd(len1, len2)` if `s1 + s2 == s2 + s1`."],
    notuse="Very large n (use segmented sieve) or one-off primality of a huge number (use Miller–Rabin).",
    problems=[
        (263, "Ugly Number", "E", "ugly-number", "Divide by 2, 3, 5 while possible; result must be 1", "O(log n) / O(1)"),
        (1979, "Find Greatest Common Divisor of Array", "E", "find-greatest-common-divisor-of-array", "gcd(min, max)", "O(n + log max) / O(1)"),
        (1071, "Greatest Common Divisor of Strings", "E", "greatest-common-divisor-of-strings", "Check s1+s2 == s2+s1; answer length = gcd of lengths", "O(n + m) / O(n + m)"),
        (204, "Count Primes", "M", "count-primes", "Sieve of Eratosthenes starting at i²", "O(n log log n) / O(n)"),
        (365, "Water and Jug Problem", "M", "water-and-jug-problem", "Target reachable iff target % gcd(x, y) == 0 and target ≤ x + y", "O(log) / O(1)"),
        (264, "Ugly Number II", "M", "ugly-number-ii", "Three pointers multiplying by 2, 3, 5 and taking the min", "O(n) / O(n)"),
    ]))

# ---------------------------------------------------------------- 8
P.append(dict(
    title="Digits and number manipulation", tier="hot", sim="digits", oneline="peel with % 10, build with × 10 + d, guard overflow first",
    why="Many easy-medium questions test exactly this loop and its edge cases", signature="LC 7 / 9 / 168",
    when="Reverse, compare, add or convert the digits of a number, or work in another base.",
    detect="\"reverse integer\" · \"palindrome number\" · \"plus one\" · \"add digits\" · \"excel column title\" · \"convert to base k\" · \"roman numerals\".",
    intuition="`x % 10` is the last digit and `x / 10` removes it; `rev * 10 + d` appends a digit. These two moves are all you need to take a number apart and put it back together in any order. The same idea in base 26 (letters) or base 2 gives column titles and binary conversion. In fixed-width integers the danger is overflow, so check **before** multiplying.",
    brute="Converting to a string and back is simple but may be disallowed, uses extra memory and hides overflow behaviour. The arithmetic loop is O(log₁₀ n) with O(1) space.",
    idea="`while x != 0: d = x % 10; x /= 10; rev = rev * 10 + d`. For base `b`, use `% b` and `/ b`. For a base with no zero digit (Excel columns), subtract 1 before each step (bijective numeration).",
    steps=["Take the last digit `d = x % 10`; drop it with `x /= 10`.", "Before `rev = rev · 10 + d`, check `rev > MAX / 10` (or equal and `d > 7`).", "Repeat until `x == 0`.", "Excel column: `n−−; ch = 'A' + n % 26; n /= 26`; reverse the result."],
    trace_title="reverse `1234`",
    trace="""d=4  rev = 0*10+4 = 4     x=123
d=3  rev = 4*10+3 = 43    x=12
d=2  rev = 43*10+2 = 432  x=1
d=1  rev = 432*10+1 = 4321 x=0""",
    code=[("reverse integer (32-bit overflow check)",
           """int rev = 0;
while (x != 0) {
    int d = x % 10;                                   // negative x gives negative digits in Java
    x /= 10;
    if (rev > Integer.MAX_VALUE / 10 || (rev == Integer.MAX_VALUE / 10 && d > 7)) return 0;
    if (rev < Integer.MIN_VALUE / 10 || (rev == Integer.MIN_VALUE / 10 && d < -8)) return 0;
    rev = rev * 10 + d;
}
return rev;""",
           """sign = -1 if x < 0 else 1
x, rev = abs(x), 0
while x:
    rev = rev * 10 + x % 10
    x //= 10
rev *= sign
return rev if -2**31 <= rev <= 2**31 - 1 else 0       # Python ints do not overflow: check at the end"""),
          ("Excel column title (base 26 with no zero digit)",
           """StringBuilder sb = new StringBuilder();
while (n > 0) {
    n--;                                              // shift to 0-based: A = 0 .. Z = 25
    sb.append((char) ('A' + n % 26));
    n /= 26;
}
return sb.reverse().toString();""",
           """out = []
while n > 0:
    n -= 1                                            # shift to 0-based: A = 0 .. Z = 25
    out.append(chr(65 + n % 26))
    n //= 26
return ''.join(reversed(out))""")],
    complexity="O(number of digits) = O(log n) time, O(1) space.",
    traps=["Java `%` and `/` truncate toward zero: `-12 % 10 == -2`. Python `//` floors: `-12 // 10 == -2`. Use `abs` or handle the sign explicitly.", "Check overflow **before** `rev * 10 + d`, not after.",
           "Palindrome number: negatives and numbers ending in 0 (except 0) are not palindromes; reverse only half to avoid overflow.", "Plus one: carry through 9s and prepend a 1 if every digit was 9."],
    variants=["Convert to base k: collect `n % k` then reverse.", "Roman numerals: greedy over a value table.", "Add digits (digital root): `1 + (n − 1) % 9` for n > 0.", "Happy number: repeat the digit-square sum with cycle detection."],
    notuse="Numbers beyond 64-bit: operate on digit strings or arrays (big integers).",
    problems=[
        (9, "Palindrome Number", "E", "palindrome-number", "Reverse half of the digits; no overflow", "O(log n) / O(1)"),
        (66, "Plus One", "E", "plus-one", "Carry from the right; all 9s adds a leading 1", "O(n) / O(1)"),
        (258, "Add Digits", "E", "add-digits", "Digital root formula 1 + (n − 1) % 9", "O(1) / O(1)"),
        (504, "Base 7", "E", "base-7", "Repeated % 7 and / 7; mind the sign", "O(log n) / O(1)"),
        (168, "Excel Sheet Column Title", "E", "excel-sheet-column-title", "Bijective base 26: decrement before each step", "O(log n) / O(1)"),
        (13, "Roman to Integer", "E", "roman-to-integer", "Subtract when a smaller value precedes a larger one", "O(n) / O(1)"),
        (7, "Reverse Integer", "M", "reverse-integer", "Pop and push digits; guard overflow first", "O(log n) / O(1)"),
    ]))

# ---------------------------------------------------------------- 9
P.append(dict(
    title="Formulas and observation-based math", tier="sec", sim="trailing", oneline="find the pattern, count instead of simulate",
    why="Many \"hard-looking\" problems collapse into a short formula", signature="LC 172 / 319",
    when="Brute-force simulation is too slow but the answer has a counting or mathematical structure.",
    detect="\"trailing zeroes of n!\" · \"bulb switcher\" · \"number of odd numbers in a range\" · \"minimum moves to make elements equal\" · \"power of three\" · sum or product patterns.",
    intuition="Ask what is actually being counted. Trailing zeros of `n!` come from factors of 10 = 2 × 5, and 2s are far more common than 5s, so count 5s: one for each multiple of 5, one more for each multiple of 25, and so on: `n/5 + n/25 + n/125 + …`. A bulb is toggled once for each divisor of its number, so it ends on only if it has an odd number of divisors, which happens exactly for perfect squares: the answer is `⌊√n⌋`.",
    brute="Computing 125! and counting zeros (or simulating n rounds of toggles) is huge or O(n²). Reasoning about factors gives O(log n) or O(1).",
    idea="Reduce the problem to a quantity you can count with a formula: divisors, factors of a prime, sums of arithmetic series `n(n + 1)/2`, medians for minimising absolute differences, parity (even/odd counts).",
    steps=["Write a tiny example by hand and look for the pattern.", "Identify what is being counted (factors, divisors, parity, differences).", "Derive the formula; verify on 3–4 small cases.", "Watch overflow: use `long` for sums like `n(n + 1)/2`."],
    trace_title="trailing zeros of `125!`",
    trace="""125 / 5   = 25   (multiples of 5)
125 / 25  = 5    (multiples of 25: extra 5)
125 / 125 = 1    (multiples of 125: extra 5)
total = 25 + 5 + 1 = 31 zeros""",
    code=[("trailing zeroes and bulb switcher",
           """int trailingZeroes(int n) {
    int count = 0;
    while (n > 0) { n /= 5; count += n; }          // n/5 + n/25 + n/125 + ...
    return count;
}
int bulbSwitch(int n) { return (int) Math.sqrt(n); }   // bulbs with an odd number of divisors = perfect squares""",
           """def trailing_zeroes(n):
    count = 0
    while n > 0:
        n //= 5
        count += n                                  # n/5 + n/25 + n/125 + ...
    return count

def bulb_switch(n):
    from math import isqrt
    return isqrt(n)                                 # bulbs with an odd number of divisors = perfect squares"""),
          ("minimum moves to equalise (moves of ±1): move everything to the median",
           """Arrays.sort(a);
int median = a[a.length / 2], moves = 0;
for (int x : a) moves += Math.abs(x - median);       // the median minimises the sum of absolute differences
return moves;""",
           """a.sort()
median = a[len(a) // 2]
return sum(abs(x - median) for x in a)              # the median minimises the sum of absolute differences""")],
    complexity="Usually O(1) or O(log n), or O(n log n) with a sort.",
    traps=["Verify formulas on small cases; an off-by-one in the pattern is the usual failure.", "Use `long` for `n·(n + 1)/2` and large products.",
           "Integer vs floating-point square roots: `(int) Math.sqrt` can be off for huge n; check neighbours or use `isqrt`.", "Minimum moves to equal elements with +1 on **n−1** elements (LC 453) is `sum − n · min`, a different rule from ±1 on one element (LC 462, median)."],
    variants=["Power of three: `n > 0 && 1162261467 % n == 0` (largest power of 3 in int).", "Fizz Buzz: modulo checks in the right order (15 first).", "Count odd numbers in [low, high]: `(high + 1) / 2 − low / 2`."],
    notuse="When no pattern emerges after small cases: fall back to DP or simulation with a good complexity estimate.",
    problems=[
        (412, "Fizz Buzz", "E", "fizz-buzz", "Check divisibility by 15 first, then 3, then 5", "O(n) / O(1)"),
        (1523, "Count Odd Numbers in an Interval Range", "E", "count-odd-numbers-in-an-interval-range", "(high + 1) / 2 − low / 2", "O(1) / O(1)"),
        (326, "Power of Three", "E", "power-of-three", "Loop divide by 3, or 3^19 % n == 0", "O(log n) / O(1)"),
        (172, "Factorial Trailing Zeroes", "M", "factorial-trailing-zeroes", "Count factors of 5: n/5 + n/25 + …", "O(log n) / O(1)"),
        (319, "Bulb Switcher", "M", "bulb-switcher", "Perfect squares have an odd number of divisors: floor(sqrt n)", "O(1) / O(1)"),
        (453, "Minimum Moves to Equal Array Elements", "M", "minimum-moves-to-equal-array-elements", "Incrementing n−1 equals decrementing one: sum − n·min", "O(n) / O(1)"),
        (462, "Minimum Moves to Equal Array Elements II", "M", "minimum-moves-to-equal-array-elements-ii", "Move everything to the median", "O(n log n) / O(1)"),
    ]))

TOPIC = dict(
    id="bit_math", file="08_bit_math.html", title="Bit Manipulation and Math — Pattern Guide",
    lead="Bits and numbers give you the shortest, fastest solutions when you know the handful of tricks. This guide covers bit operators and masks, XOR cancellation, counting set bits, bitmask subsets, arithmetic with bits, fast exponentiation with modulus, GCD and primes, digit manipulation and formula-based reasoning. Each pattern has the intuition, a step-through animation, Java and Python code, and a ladder of LeetCode problems.",
    mindset="Bit and math problems reward **noticing structure**: a number is a row of switches, a pair cancels under XOR, a multiple is crossed out by its prime, a huge power is a few squarings. Learn the idioms by heart (`x & (x − 1)`, `x & −x`, `a ^ b`, `base * base % mod`, `gcd(b, a % b)`), then spend your time on recognising which one a problem is hiding.",
    qintro="Ask these questions on every bit or math problem:",
    questions=["**Does it ask about pairs, odd one out or parity?** → XOR.", "**Is the input a small set of choices?** → bitmask (n ≤ 20).", "**Are the numbers or exponents huge, or a modulus given?** → fast power and modular arithmetic.",
               "**Is divisibility, factors or primes involved?** → GCD, sieve, factorisation.", "**Could 32-bit overflow occur?** → check before multiplying; use `long`; mind signs and Java vs Python division."],
    cues=[
        ["\"is the i-th bit set\", \"power of two\", \"reverse bits\"", "**P1** Bit basics"],
        ["\"appears twice except one\", \"missing number\"", "**P2** XOR cancellation"],
        ["\"number of 1 bits\", \"counting bits\"", "**P3** Counting set bits"],
        ["\"all subsets\" with n ≤ 20, \"set of used items\"", "**P4** Bitmask enumeration"],
        ["\"without + / − / ×\", \"AND of a range\"", "**P5** Arithmetic with bits"],
        ["\"pow\", \"mod 10^9 + 7\", huge exponent, sqrt", "**P6** Fast power and modular arithmetic"],
        ["\"gcd\", \"count primes\", \"ugly number\", \"factors\"", "**P7** GCD and primes"],
        ["\"reverse integer\", \"palindrome number\", \"column title\", base conversion", "**P8** Digits"],
        ["\"trailing zeroes\", \"bulb switcher\", counting by pattern", "**P9** Formulas"],
    ],
    choose=[
        ["Read or change a specific bit", "Masks (P1)"],
        ["Find the unpaired value in O(1) space", "XOR (P2)"],
        ["Count 1 bits", "Kernighan or bit DP (P3)"],
        ["Try every subset of ≤ 20 items", "Mask loop (P4)"],
        ["Add / divide without the operator", "XOR + carry, shifts (P5)"],
        ["Large power or answer modulo M", "Repeated squaring (P6)"],
        ["Common factors, primes", "Euclid, sieve (P7)"],
        ["Digit by digit work", "`% 10`, `/ 10` (P8)"],
        ["Looks like a simulation but has structure", "Derive the formula (P9)"],
    ],
    rule="if a **pair cancels**, think XOR; if the **state is a small set**, think bitmask; if the **exponent is huge**, think repeated squaring; if **divisibility** appears, think GCD / primes; if the brute force is a simulation, search for the **counting formula**.",
    selftest=[
        ("What does `x & (x − 1)` do and why?", "It clears the lowest set bit. Subtracting 1 flips the lowest 1 to 0 and every 0 below it to 1, so AND-ing keeps everything above and zeroes that bit and everything below."),
        ("Why does XOR-ing all elements find the single number when others appear twice?", "`x ^ x = 0`, XOR is commutative and associative, and `x ^ 0 = x`, so every pair cancels and only the unpaired value remains."),
        ("How many masks are there for n items, and what does bit i mean?", "There are 2ⁿ masks; bit i being 1 means item i is included in the subset."),
        ("Why does the sieve start crossing out at p²?", "Smaller multiples `p·k` with `k < p` have a smaller prime factor and were already crossed out by that smaller prime."),
        ("Why is binary exponentiation O(log n)?", "The exponent is halved each step (`e >>= 1`), so there are about log₂ e iterations, each with at most two multiplications."),
        ("Why check overflow **before** `rev * 10 + d`?", "Once the multiplication overflows, the value has already wrapped and cannot be reliably compared afterwards."),
        ("Why does `n! ` have more factors of 2 than 5, and what does that mean for trailing zeros?", "Even numbers are more frequent than multiples of 5, so the number of 10 = 2 × 5 pairs is limited by the 5s: count `n/5 + n/25 + …`."),
        ("Java `-7 / 2` versus Python `-7 // 2`?", "Java truncates toward zero giving −3; Python floors giving −4. Convert carefully when porting division and modulo logic."),
    ],
    plan=[
        "**Day 1:** operators and the six mask idioms; reverse bits and power-of-two problems.",
        "**Day 2:** XOR problems (single number I–III, missing number) and counting bits.",
        "**Day 3:** bitmask subsets, gray code and the unique-characters concatenation problem.",
        "**Day 4:** bit arithmetic (add without +, range AND) and fast power with a modulus.",
        "**Day 5:** GCD, the sieve and factorisation; write each from memory.",
        "**Day 6:** digit problems with overflow handling, then formula problems (trailing zeroes, bulb switcher).",
    ],
    patterns=P,
)
