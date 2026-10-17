"""Fix snippets found by the verification run (dead code / mutated input)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from snippets import snippets

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = {'strings': 'strings', 'greedy': 'greedy'}

PY_ANAGRAM = '''from collections import Counter
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
    return not any(count)'''

PY_COINS = '''# greedy: wrong for coins [1, 3, 4], amount 6
def greedy_coins(coins, amount):
    count = 0
    for c in sorted(coins, reverse=True):
        count += amount // c
        amount %= c                                   # (a local copy: the caller's amount is unchanged)
    return count

# correct: dp[a] = fewest coins that make amount a
def min_coins(coins, amount):
    dp = [0] + [float('inf')] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amount]'''

JAVA_COINS = '''// greedy: wrong for coins {1, 3, 4}, amount 6
int greedyCoins(int[] coins, int amount) {
    Arrays.sort(coins);
    int count = 0;
    for (int i = coins.length - 1; i >= 0; i--) { count += amount / coins[i]; amount %= coins[i]; }
    return count;
}

// correct: dp[a] = fewest coins that make amount a
int minCoins(int[] coins, int amount) {
    int[] dp = new int[amount + 1];
    Arrays.fill(dp, amount + 1); dp[0] = 0;
    for (int a = 1; a <= amount; a++)
        for (int c : coins)
            if (c <= a) dp[a] = Math.min(dp[a], dp[a - c] + 1);
    return dp[amount];
}'''

PY_JUMPS = '''# reachable?
def can_jump(a):
    far = 0
    for i, x in enumerate(a):
        if i > far:
            return False                              # a gap we cannot cross
        far = max(far, i + x)
    return True

# minimum jumps (guaranteed reachable)
def min_jumps(a):
    jumps = cur_end = far = 0
    for i in range(len(a) - 1):
        far = max(far, i + a[i])
        if i == cur_end:
            jumps += 1                                # the current level is exhausted: jump
            cur_end = far
    return jumps'''

JAVA_JUMPS = '''// reachable?
boolean canJump(int[] a) {
    int far = 0;
    for (int i = 0; i < a.length; i++) {
        if (i > far) return false;                    // a gap we cannot cross
        far = Math.max(far, i + a[i]);
    }
    return true;
}

// minimum jumps (guaranteed reachable)
int minJumps(int[] a) {
    int jumps = 0, curEnd = 0, far = 0;
    for (int i = 0; i < a.length - 1; i++) {
        far = Math.max(far, i + a[i]);
        if (i == curEnd) { jumps++; curEnd = far; }   // the current level is exhausted: jump
    }
    return jumps;
}'''

EDITS = [
    (('03_strings.html', 1, 1), 'py', PY_ANAGRAM),
    (('14_greedy.html', 1, 2), 'py', PY_COINS),
    (('14_greedy.html', 1, 2), 'java', JAVA_COINS),
    (('14_greedy.html', 2, 1), 'py', PY_JUMPS),
    (('14_greedy.html', 2, 1), 'java', JAVA_JUMPS),
]
by_key = {(s['file'], s['pattern'], s['idx']): s for s in snippets()}
for key, lang, new in EDITS:
    s = by_key[key]
    old = s[lang].strip()
    path = os.path.join(ROOT, 'build', SRC[s['topic']] + '.py')
    text = open(path, encoding='utf-8').read()
    if old not in text:
        print('NOT FOUND', key, lang)
        continue
    open(path, 'w', encoding='utf-8', newline='\n').write(text.replace(old, new.strip(), 1))
    print('patched', key, lang)
