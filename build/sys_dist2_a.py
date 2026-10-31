"""S22 distributed systems: part A (lessons 1 to 3: partial failure, time and ordering, replication and quorums)."""
import sysviz as v

LOST_REPLY_SEQ = v.seq(
    ["Client", "Network", "Payment server"],
    [("a->b", 0, 2, "POST /charge $50"),
     ("a->b", 2, 2, "charge the card: done"),
     ("a->b", 2, 0, "200 OK", "bad"),
     ("note", 0, 2, "the reply is lost: the client sees only a timeout"),
     ("a->b", 0, 2, "retry: POST /charge $50"),
     ("a->b", 2, 2, "charge the card again", "bad"),
     ("note", 0, 2, "the customer paid twice; with an idempotency key the retry would have been recognised")],
    "Partial failure", "The operation happened, only the answer was lost: the client cannot tell")

CLOCK_VIZ = v.figure(
    720, 214,
    [v.box(10, 20, 200, 56, "Node A clock: 10:00:05", "warn", "5 seconds fast"),
     v.box(260, 20, 200, 56, "Node B clock: 10:00:00", "ok", "correct"),
     v.box(510, 20, 200, 56, "Node C clock: 09:59:58", "warn", "2 seconds slow"),
     v.text(360, 108, "Write 1 at A (really 10:00:00 sharp, stamped 10:00:05). Write 2 at B (really 10:00:02, stamped 10:00:02).", "dg-s"),
     v.text(360, 132, "\"Last write wins\" by timestamp keeps write 1: the later write was thrown away.", "dg-s"),
     v.text(360, 164, "Logical clocks and version vectors order events by what could have influenced what, not by watches.", "dg-s"),
     v.text(360, 192, "Google's Spanner uses atomic clocks and waits out the uncertainty; most systems cannot.", "dg-s")],
    "Clocks disagree", "Timestamps from different machines cannot reliably order events")

QUORUM_VIZ = v.figure(
    720, 226,
    [v.box(10, 80, 100, 56, "Writer", "ink"),
     v.arrow(110, 98, 170, 40), v.arrow(110, 108, 170, 108), v.arrow(110, 118, 170, 176),
     v.box(170, 14, 130, 48, "Replica 1: new", "ok", "acked"), v.box(170, 84, 130, 48, "Replica 2: new", "ok", "acked"), v.box(170, 154, 130, 48, "Replica 3: old", "warn", "not yet"),
     v.box(430, 80, 100, 56, "Reader", "ink"),
     v.arrow(430, 98, 300, 40), v.arrow(430, 108, 300, 176),
     v.text(600, 70, "N = 3, W = 2, R = 2", "dg-s"), v.text(600, 94, "2 + 2 > 3", "dg-s"),
     v.text(600, 118, "any read of two replicas", "dg-s"), v.text(600, 142, "includes at least one new copy", "dg-s"),
     v.text(360, 218, "Choose the read with the newest version: the overlap guarantees you see the latest acknowledged write.", "dg-s")],
    "Quorums", "If the write set and the read set must overlap, a read always meets at least one copy of the latest write")

LESSONS_A = [
    dict(
        title="Partial failure: when a timeout means \"I do not know\"",
        tier="hot",
        situation="A client sends a payment request and the connection times out. Did the charge happen? On one machine a call returns or crashes. Across a network there is a third outcome, and almost every distributed technique exists because of it.",
        learn=["The three outcomes of a remote call", "Why retries can duplicate effects", "Timeouts: choosing them and what they mean", "Making a retry harmless with an idempotency key"],
        model=[
            "A local function call returns a value or throws. A **remote** call has a third outcome: **no answer**. The request may have been lost on the way, the server may be slow or dead, or the server may have **done the work and the reply was lost**. From the client's side these look identical: only a **timeout**. A timeout therefore does not mean \"it failed\"; it means \"I do not know\". Treating it as failure (and refunding, re-ordering or retrying blindly) is the root of double charges and lost updates.",
            "The cure is to make repetition **safe**. An **idempotent** operation has the same effect whether performed once or many times (`set status = paid` is idempotent; `add 50 to the balance` is not). For operations that are not naturally idempotent, the client sends a unique **idempotency key**; the server remembers the key and the result, and a repeated request returns the stored result instead of repeating the work. Timeouts should be chosen deliberately (longer than the normal latency tail, shorter than the user's patience) and every retry must be bounded, delayed (backoff) and idempotent.",
        ],
        analogy="You post a letter asking someone to pay a bill and hear nothing back. Either the letter was lost, or it arrived and their reply was lost. Writing a second letter might make them pay twice, unless each letter carries the same invoice number and they check it.",
        visual=[LOST_REPLY_SEQ],
        sim=None,
        walk=[
            ("The client sends and waits", "A timer starts; the request travels to the server."),
            ("The server does the work", "It charges the card and records it."),
            ("The reply is lost", "The network drops it, or the connection breaks, or the server crashes after charging."),
            ("The client times out and cannot know", "It must choose: give up (and maybe lose the sale), or retry (and maybe charge twice)."),
            ("An idempotency key resolves it", "The retry carries the same key; the server finds the stored result and answers without charging again."),
        ],
        groups=[
            dict(title="A lost reply, for real, and the fix", cmds=[
                dict(volatile=True, c=r'''mkdir -p ~/dist && cd ~/dist && cat > lostreply.py <<'EOF'
# A real TCP server that charges a card and then loses the FIRST reply (the connection is closed without answering).
import socket, threading, time
charges = []                                  # the effects that really happened
results = {}                                  # idempotency key -> stored result
state = {'drop_next': True}
def handle(conn):
    data = conn.recv(1024).decode().strip(); key, amount = data.split()
    if key in results:                        # a repeat of a request we already did: return the stored answer
        conn.sendall(('OK %s\n' % results[key]).encode()); conn.close(); return
    charges.append((key, int(amount)))        # do the work: charge the card
    results[key] = 'charged %s' % amount
    if state['drop_next']:                    # the reply is lost: close without answering
        state['drop_next'] = False; conn.close(); return
    conn.sendall(('OK %s\n' % results[key]).encode()); conn.close()
srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); srv.bind(('127.0.0.1', 7301)); srv.listen(8)
def serve():
    while True:
        c, _ = srv.accept(); threading.Thread(target=handle, args=(c,)).start()
threading.Thread(target=serve, daemon=True).start()
def call(key, amount):
    s = socket.create_connection(('127.0.0.1', 7301)); s.settimeout(0.5)
    s.sendall(('%s %d\n' % (key, amount)).encode())
    try:
        r = s.recv(1024).decode().strip()
        return r or 'no answer (connection closed)'
    except socket.timeout:
        return 'timeout'
def attempt(label, keys):
    charges.clear(); results.clear(); state['drop_next'] = True
    for i, k in enumerate(keys, 1):
        print('%s attempt %d: %s' % (label, i, call(k, 50)))
        if i == 1: continue
    print('   cards actually charged: %d time(s) -> %s' % (len(charges), [c[0] for c in charges]))
attempt('naive retry (new key each time)', ['req-1', 'req-2'])
attempt('retry with the SAME idempotency key', ['pay-777', 'pay-777'])
EOF
python3 lostreply.py''',
                     e="The double charge, with real sockets. The server charges the card and then loses the reply. The client sees no answer and, quite reasonably, retries. If each attempt is a new request, the card is charged **twice**. If the retry carries the **same idempotency key**, the server recognises it, does **not** charge again, and returns the stored result: one charge, and the client finally gets its answer. Nothing about the network changed; only the protocol became safe to repeat.",
                     annot=[("naive retry attempt 1: no answer (connection closed)", "the client cannot tell whether the charge happened"),
                            ("naive retry attempt 2: OK charged 50", "the retry succeeded, as it should"),
                            ("cards actually charged: 2 time(s)", "both attempts were executed: the customer paid twice"),
                            ("same key: attempt 2: OK charged 50 / charged: 1 time(s)", "the repeat was recognised by its key and answered from the stored result")]),
            ]),
        ],
        scenario=dict(
            title="\"A payment API call times out. What should the client do? How do you design the API?\"",
            ask="The most common distributed-systems interview opener. The trap is saying \"retry\" or \"fail\" without addressing the unknown outcome.",
            clarify=[("Is the operation safe to repeat? Who generates the identifier?", "Charges are not naturally idempotent; the client should generate the key before the first attempt so every retry reuses it.")],
            think=[("Name the ambiguity.", "A timeout is not a failure. Three possibilities: request never arrived, server processed it and the reply was lost, or the server is still working. The client cannot distinguish them."),
                   ("Make the operation idempotent.", "Client sends a unique idempotency key (a UUID per intended payment) in a header. Server stores key, request fingerprint and result atomically with the effect (same transaction or unique constraint). A repeat returns the stored result."),
                   ("Define the client behaviour.", "Retry with the same key, bounded attempts, exponential backoff with jitter, and a total deadline. After exhausting retries, show \"processing\" and reconcile by querying the payment status by key rather than guessing."),
                   ("Handle edge cases on the server.", "Same key with a different request body is an error; the key's record expires after days; concurrent requests with the same key: the second waits or gets a conflict; do not record the key if the effect failed in a retryable way."),
                   ("Offer a status endpoint.", "`GET /payments/{key}` lets the client (or a reconciliation job) learn the real outcome after an unknown result."),
                   ("Say what it costs.", "Storage and lookup of keys, and discipline: every mutating endpoint that might be retried needs the same treatment.")],
            answer=["\"A timeout means I do not know: the request may never have arrived, or it may have succeeded with the reply lost. So the client must not assume failure. I would make the payment endpoint idempotent: the client generates a unique idempotency key before the first attempt and sends it with every retry. The server stores the key and the result in the same transaction as the charge, so a repeat returns the stored result instead of charging again.",
                    "On the client I retry with the same key, a bounded number of times, with exponential backoff and jitter and an overall deadline; if it is still unknown I show a processing state and look up the payment by key rather than guessing. The server rejects the same key with a different body, expires keys after a few days, and handles two concurrent requests with the same key safely. A status endpoint lets reconciliation find the real outcome. The cost is storing keys and applying the same discipline to every mutating endpoint that can be retried.\""],
            follow=[("Who should generate the idempotency key?", "The client, before the first attempt, so that retries reuse it; a server-generated id would be lost with the lost reply."),
                    ("How long do you keep keys?", "Longer than any client could plausibly retry (commonly 24 hours to a few days); then expire to bound storage."),
                    ("What if the server crashes between charging and recording the key?", "That is why the effect and the key must be committed atomically (one transaction); for external effects, use the provider's idempotency key as well.")],
            slips=["Answering \"just retry\" or \"treat it as failed\".", "Generating the key on the server.", "Storing the key outside the transaction that performs the effect."],
        ),
        quick=[
            ("What does a timeout tell you about a remote operation?", "Only that no answer arrived in time; it may or may not have happened."),
            ("What is an idempotent operation?", "One that has the same effect whether done once or many times."),
            ("Why must the client generate the idempotency key?", "So every retry reuses it; a server-side id would be lost together with the lost reply."),
        ],
        traps=[
            "Treating a timeout as proof of failure and refunding or reordering automatically.",
            "Idempotency keys stored in a cache that can evict them: a retry after eviction repeats the effect.",
            "Retrying non-idempotent calls without a key.",
        ],
    ),
    dict(
        title="Time and ordering: why clocks lie and what to use instead",
        tier="hot",
        situation="Two servers log events with timestamps and the log says the reply happened before the request. A database that resolves conflicts by \"latest timestamp wins\" silently throws away a newer write. Clocks across machines cannot be trusted for ordering.",
        learn=["Clock drift, skew and why NTP is not enough", "Last-write-wins and the data it loses", "Lamport clocks: a counter that respects cause and effect", "Version vectors: detecting true concurrency"],
        model=[
            "Every machine has its own clock; they **drift** (run at slightly different speeds) and are corrected by NTP, which narrows the gap to milliseconds on a good day and to much more on a bad one; clocks can even **jump backwards**. So comparing **wall-clock timestamps from different machines** cannot reliably tell which event happened first. A database that resolves conflicting writes by **last-write-wins (LWW)** on those timestamps will sometimes keep the older write and discard the newer one, silently. (Within one machine, use the **monotonic** clock for measuring durations, since the wall clock can be adjusted.)",
            "What matters for correctness is usually **causality**: did event A possibly influence event B? A **Lamport clock** is a counter each node increments on every event and sets to `max(own, received) + 1` when it receives a message: if A caused B then A's counter is lower than B's (the converse is not true). **Version vectors** (one counter per node) go further: comparing two vectors tells you whether one version **descends from** the other or whether they are **concurrent** (a real conflict that needs resolving, by merging, by the application or by a CRDT). Dynamo-style stores and many collaboration tools use these ideas; Google Spanner instead uses GPS and atomic clocks and **waits out** the clock uncertainty.",
        ],
        analogy="Two people in different time zones with unreliable watches try to agree who spoke first. Comparing watches fails. Numbering the letters they send each other (and always numbering above the highest number they have seen) gives an order that respects who replied to whom.",
        visual=[CLOCK_VIZ],
        sim=None,
        walk=[
            ("Each node stamps events with its own clock", "A is 5 seconds fast, B is exact, C is 2 seconds slow."),
            ("A conflict is resolved by timestamp", "Last-write-wins compares stamps from different machines."),
            ("The wrong write wins", "A's older write carries a larger timestamp, so the newer write from B is discarded."),
            ("Logical clocks order by causality", "A counter that jumps ahead when a message arrives guarantees that effects are ordered after causes."),
            ("Version vectors expose real conflicts", "Neither version descends from the other: keep both and merge, instead of silently losing one."),
        ],
        groups=[
            dict(title="Skewed clocks lose a write; logical clocks do not", cmds=[
                dict(c=r'''python3 - <<'EOF'
# Three replicas with skewed clocks. Real (true) times: write X at t=100.0 on node A, write Y at t=102.0 on node B.
skew = {'A': +5.0, 'B': 0.0, 'C': -2.0}                     # seconds each node's clock is wrong by
def stamp(node, true_time): return true_time + skew[node]
x = ('X: first write',  stamp('A', 100.0))                  # stamped 105.0
y = ('Y: second write', stamp('B', 102.0))                  # stamped 102.0
print('write X happened first, at true time 100.0 on node A, stamped %.1f' % x[1])
print('write Y happened later,  at true time 102.0 on node B, stamped %.1f' % y[1])
winner = max((x, y), key=lambda w: w[1])
print('last-write-wins by timestamp keeps:', winner[0], '   <- the OLDER write won; Y was silently discarded')

# Lamport clocks: a counter that jumps past anything it has seen
class Node:
    def __init__(self, name): self.name, self.t = name, 0
    def event(self): self.t += 1; return self.t
    def send(self): return self.event()
    def receive(self, t): self.t = max(self.t, t) + 1; return self.t
a, b = Node('A'), Node('B')
e1 = a.event()                     # A does something
m = a.send()                       # A sends a message to B
e2 = b.receive(m)                  # B receives it: B's counter jumps past A's
e3 = b.event()
print('Lamport timestamps: A event=%d, A send=%d, B receive=%d, B next event=%d  (cause < effect always)' % (e1, m, e2, e3))
EOF''',
                     e="Two experiments in one. First, the timestamp problem: node A's clock is 5 seconds fast, so write **X, which happened first, is stamped 105**, while write **Y, which happened two seconds later, is stamped 102**. \"Last write wins\" keeps X and silently discards Y: a real lost update caused only by clock skew. Second, Lamport clocks: each node counts events and, on receiving a message, jumps its counter past the sender's, so every effect has a higher number than its cause even though the nodes never share a clock.",
                     annot=[("write X ... stamped 105.0", "the earlier write carries the larger timestamp because its node's clock is fast"),
                            ("last-write-wins by timestamp keeps: X: first write", "the older write wins: the newer write was lost without any error"),
                            ("Lamport timestamps: A event=1, A send=2, B receive=3, B next event=4", "B's counter jumped past A's: causes always have lower numbers than effects")]),
                dict(c=r'''python3 - <<'EOF'
# Version vectors: one counter per node. Compare two versions of the same value.
def bump(vv, node): n = dict(vv); n[node] = n.get(node, 0) + 1; return n
def compare(a, b):
    nodes = set(a) | set(b)
    a_ge = all(a.get(n, 0) >= b.get(n, 0) for n in nodes); b_ge = all(b.get(n, 0) >= a.get(n, 0) for n in nodes)
    if a_ge and b_ge: return 'identical'
    if a_ge: return 'first descends from second (second can be discarded)'
    if b_ge: return 'second descends from first (first can be discarded)'
    return 'CONCURRENT: neither saw the other: a real conflict to merge'
v0 = {}
v1 = bump(v0, 'A')                      # A writes the cart:   {A:1}
v2 = bump(v1, 'A')                      # A writes again:      {A:2}
print('A:1 vs A:2           ->', compare(v1, v2))
va = bump(v2, 'A')                      # later, A adds an item: {A:3}
vb = bump(v2, 'B')                      # meanwhile B (cut off from A) adds another item: {A:2, B:1}
print('%s vs %s ->' % (va, vb), compare(va, vb))
merged = {n: max(va.get(n, 0), vb.get(n, 0)) for n in sorted(set(va) | set(vb))}
merged = bump(merged, 'A')
print('after merging both carts the new version is', merged, '->', compare(merged, va), '/', compare(merged, vb))
EOF''',
                     e="Version vectors tell **replaced** from **concurrent**. Version `{A:2}` clearly descends from `{A:1}`: the older one can be discarded safely. But A adding an item (`{A:3}`) while B, unaware, adds another (`{A:2, B:1}`) produces two versions where **neither descends from the other**: a true conflict. Instead of letting a timestamp pick a loser, the system keeps both and merges them (for a shopping cart, the union of items); the merged version then descends from both. This is how Dynamo-style stores avoid silently losing writes.",
                     annot=[("A:1 vs A:2 -> second descends from first", "an ordinary update: the old version can be dropped"),
                            ("{'A': 3} vs {'A': 2, 'B': 1} -> CONCURRENT", "two writers that did not see each other: neither may be silently discarded"),
                            ("merged ... first descends from second", "the merged version supersedes both: the conflict is resolved")]),
            ]),
        ],
        scenario=dict(
            title="\"Why can't we just use timestamps to order events across servers? What do real systems do?\"",
            ask="A classic that separates people who have read about distributed systems from those who have been burned by them.",
            clarify=[("What needs ordering: logs for humans, or conflicting writes to the same data?", "Logs only need approximate order; conflict resolution needs a rule that does not lose data.")],
            think=[("Explain why timestamps fail.", "Clocks drift and are corrected by NTP with bounded but nonzero error (milliseconds to seconds); they can step backwards; virtual machines pause. Two machines cannot agree on 'now' to better than their error."),
                   ("Show the consequence.", "Last-write-wins on timestamps can discard the newer of two writes when the writer's clock is ahead, and it does so silently."),
                   ("Give the alternatives.", "A single leader that assigns order (one clock, one sequence number); logical clocks (Lamport) for a consistent order respecting causality; version vectors to detect concurrency and merge; CRDTs for data types that merge automatically; consensus for a replicated log."),
                   ("Mention hardware solutions.", "Google Spanner's TrueTime uses GPS and atomic clocks to expose a bounded uncertainty and waits it out before committing: possible because they control the hardware."),
                   ("Give practical advice.", "Use monotonic clocks for durations; use the database's sequence or a leader for ordering; use timestamps only when losing a rare write is acceptable; include the clock source in your trust assumptions; monitor clock offset."),
                   ("Connect to a design.", "A collaborative editor: CRDTs or operational transforms. A shopping cart: version vectors with merge. A bank: single leader and transactions.")],
            answer=["\"Because clocks on different machines disagree: they drift, NTP corrects them only to within some error, and they can even step backwards. So a timestamp comparison across machines can say the wrong thing, and a database that resolves conflicts with last-write-wins can silently discard the newer write when the other writer's clock was ahead.",
                    "What real systems do depends on the need. If one node can assign order, a single leader with sequence numbers avoids the problem. To order by cause and effect without shared time, Lamport clocks; to detect real concurrency, version vectors, and then merge, sometimes automatically with CRDTs. Where strict ordering across machines is essential, consensus provides a replicated log, and Google Spanner uses atomic clocks and waits out the uncertainty. In practice I use monotonic clocks for durations, leaders or sequences for ordering, and accept timestamps only where losing a rare write is fine.\""],
            follow=[("What is a CRDT?", "A conflict-free replicated data type: a structure (counter, set, text) designed so concurrent updates always merge to the same result on every replica without coordination."),
                    ("What is the difference between wall-clock and monotonic time?", "Wall-clock time can be adjusted or jump; monotonic time only moves forward and is right for measuring elapsed time within one machine."),
                    ("How does Spanner get away with it?", "TrueTime returns an interval of uncertainty (a few milliseconds) from GPS and atomic clocks; a transaction waits out that interval before committing so timestamps are consistent with real time.")],
            slips=["Saying NTP solves it.", "Using timestamps to resolve conflicts on data that must not lose writes.", "Confusing Lamport ordering with real time."],
        ),
        quick=[
            ("Why is last-write-wins by timestamp dangerous?", "With skewed clocks it can keep the older write and silently discard the newer one."),
            ("What guarantee does a Lamport clock give?", "If A caused B then A's timestamp is lower than B's (not the converse)."),
            ("What does a version vector detect that a Lamport clock cannot?", "Whether two versions are concurrent (a true conflict) rather than one replacing the other."),
        ],
        traps=[
            "Using wall-clock time to measure durations: it can jump.",
            "Trusting NTP to a precision it does not provide.",
            "Resolving conflicts by timestamp on data where a lost write matters (money, inventory).",
        ],
    ),
    dict(
        title="Replication, consistency and quorums: CAP made concrete",
        tier="hot",
        situation="A write returned success. A moment later a read from another replica returns the old value. How many replicas must you talk to for that not to happen, and what must you give up when the network splits?",
        learn=["Strong, eventual and read-your-writes consistency", "The quorum rule W + R > N, measured", "CAP and PACELC without the slogans", "What happens during a partition: refuse, or diverge and merge"],
        model=[
            "With **N** copies of each item, a write that waits for **W** acknowledgements and a read that asks **R** replicas will always see the latest acknowledged write if **W + R > N**, because the write set and the read set must **overlap** in at least one replica (the reader picks the newest version among the answers). Smaller W or R gives lower latency and higher availability but allows **stale reads**. A quorum system tolerates **N − W** replicas down for writes and **N − R** for reads. This is a tunable dial, per request, in Dynamo-style stores (Cassandra, DynamoDB, Riak).",
            "**CAP** says that during a network **partition** a replicated system must choose between **consistency** (some requests are refused or wait) and **availability** (every request is answered, but replicas may disagree and need merging later). Partitions are a fact of networks, so \"CA\" is not a real option. **PACELC** adds the everyday trade-off: even **Else** (no partition) you choose between **Latency** and **Consistency**, for example by waiting for more replicas. A **CP** system (a single-leader database, ZooKeeper, etcd) refuses writes on the minority side; an **AP** system (Dynamo-style, DNS) keeps answering and reconciles later, so it needs a merge rule (version vectors, CRDTs, or last-write-wins with its risks).",
        ],
        analogy="A club decides by asking members. If every decision needs 2 of 3 signatures and every check asks 2 of 3 members, at least one member who signed is always asked. If the club's phone line splits it in two, one side can refuse to decide (consistent, unavailable) or each side can carry on and sort out contradictions later (available, inconsistent).",
        visual=[QUORUM_VIZ],
        sim=None,
        walk=[
            ("Write to W replicas", "The coordinator sends the write to all N replicas and waits for W acknowledgements."),
            ("Read from R replicas", "The reader asks R replicas and takes the answer with the newest version."),
            ("Overlap guarantees freshness", "If W + R > N the two sets share at least one replica holding the latest write."),
            ("A partition splits the cluster", "A minority side cannot reach enough replicas for a quorum."),
            ("Choose: refuse or diverge", "CP refuses on the minority side; AP accepts on both sides and merges later."),
        ],
        groups=[
            dict(title="Stale reads by quorum size, and a partition both ways", cmds=[
                dict(c=r'''python3 - <<'EOF'
import random
rng = random.Random(3)
N, trials = 3, 20000
print('N=3 replicas. A write is acknowledged after W replicas have it; a read asks R replicas and takes the newest.')
print(' W  R  W+R>N   stale reads out of %d' % trials)
for W, R in ((1, 1), (2, 1), (1, 2), (2, 2), (3, 1)):
    stale = 0
    for _ in range(trials):
        has_new = set(rng.sample(range(N), W))          # the W replicas that acknowledged the write (the others lag)
        asked = set(rng.sample(range(N), R))            # the R replicas the reader happens to ask
        if not (asked & has_new): stale += 1            # the read saw no copy of the new value
    print('%2d %2d   %-5s   %5d  (%4.1f%%)' % (W, R, 'yes' if W + R > N else 'no', stale, 100 * stale / trials))
print()
print('fault tolerance with N=5:')
for W, R in ((3, 3), (5, 1), (1, 5)):
    print('  W=%d R=%d  consistent: %-3s  writes survive %d failed replica(s), reads survive %d' % (W, R, 'yes' if W + R > 5 else 'no', 5 - W, 5 - R))
EOF''',
                     e="The quorum rule, measured by simulation. With W + R ≤ N a read can miss every replica that has the new value: the stale-read column is large (a third of reads for W=1, R=1). The moment W + R > N the stale column is **exactly zero**, because the sets must overlap. The fault-tolerance lines show the other side of the dial: W=5, R=1 is consistent but a single failed replica stops all writes; W=3, R=3 is consistent and tolerates two failures for both.",
                     annot=[("W=1 R=1 ... 13324 stale (66.6%)", "two thirds of reads miss the one replica that has the new value"),
                            ("W=2 R=2 ... 0 stale", "2 + 2 > 3: every read overlaps the write set"),
                            ("W=3 R=1 ... 0 stale", "writing to all replicas makes any single read safe, at the cost of writes failing if any replica is down"),
                            ("W=3 R=3 consistent yes, writes survive 2 ...", "a majority quorum tolerates two of five replicas failing")]),
                dict(c=r'''python3 - <<'EOF'
# Three replicas A, B, C hold balance=100. A partition cuts C off from A and B. Two clients each try to withdraw 70.
def cp(): # consistent: a write needs a majority (2 of 3)
    bal = {'A': 100, 'B': 100, 'C': 100}; ok = []
    reach = {'client1': ['A', 'B'], 'client2': ['C']}           # client1 can reach A and B; client2 only C
    for c, nodes in reach.items():
        if len(nodes) >= 2 and bal[nodes[0]] >= 70:
            for n in nodes: bal[n] -= 70
            ok.append('%s withdrew 70' % c)
        else: ok.append('%s REFUSED (no quorum)' % c)
    return bal, ok
def ap(): # available: every side accepts
    bal = {'A': 100, 'B': 100, 'C': 100}; ok = []
    for c, nodes in {'client1': ['A', 'B'], 'client2': ['C']}.items():
        for n in nodes: bal[n] -= 70
        ok.append('%s withdrew 70' % c)
    return bal, ok
for name, f in (('CP (refuse without a quorum)', cp), ('AP (always answer)', ap)):
    bal, ok = f(); print(name); print('   ', '; '.join(ok)); print('    balances during the partition:', bal)
print()
print('AP after the partition heals: replicas disagree (A,B say 30; C says 30) but 140 was paid out of a 100 account.')
print('A merge rule can reconcile the counts (the account is overdrawn by 40); it cannot un-pay the cash.')
EOF''',
                     e="CAP in two lines of output. During the partition, the **consistent** design refuses client 2 (it cannot reach a majority), so the account is never overdrawn: some requests fail. The **available** design lets both clients withdraw 70 from a balance of 100: everyone was served, and the system has paid out 140. After the partition heals the replicas can be merged, but the cash is gone. Neither choice is wrong: a bank usually picks consistency for withdrawals; a shopping cart picks availability and merges.",
                     annot=[("CP: client2 REFUSED (no quorum)", "the minority side cannot reach a majority, so it refuses: consistency preserved, availability lost for that client"),
                            ("AP: both clients withdrew 70", "both sides answered: availability kept, consistency lost"),
                            ("140 was paid out of a 100 account", "the price of availability for operations that cannot be merged away")]),
            ]),
        ],
        scenario=dict(
            title="\"Explain CAP and PACELC with an example. Would you choose CP or AP for a shopping cart? For a bank balance?\"",
            ask="They want you to move past the \"pick two\" slogan and tie the choice to the data.",
            clarify=[("What does a user see when the system is wrong or unavailable, and what does it cost?", "Overdrawing an account costs money; a briefly stale cart costs little.")],
            think=[("State CAP precisely.", "In the presence of a network partition, a replicated system must choose between consistency (linearizable reads and writes) and availability (every request to a non-failed node gets a response). Partitions are not optional, so \"CA\" is not a design choice for a distributed system."),
                   ("Add PACELC.", "When there is no partition you still trade latency against consistency, for example by waiting for synchronous replicas or a quorum."),
                   ("Give examples.", "CP: a single-leader database with synchronous replicas, ZooKeeper, etcd (the minority side stops). AP: Dynamo-style stores, Cassandra with low consistency levels, DNS (answer always, reconcile later)."),
                   ("Decide by the data.", "Bank balance and inventory at checkout: CP, because incorrect answers are expensive. Shopping cart, likes, session data, product catalogue reads: AP with merging, because availability matters more and conflicts are mergeable."),
                   ("Mention tunability.", "Per operation: quorum reads and writes (W + R > N) for the critical paths; weaker settings elsewhere. Most systems are not simply CP or AP."),
                   ("Say how AP systems reconcile.", "Read repair, anti-entropy, version vectors, CRDTs, or application-level merge; last-write-wins only where losing a write is acceptable.")],
            answer=["\"CAP says that when the network partitions, a replicated system must choose between consistency, meaning reads and writes behave as if there is one up-to-date copy, and availability, meaning every request to a working node gets an answer. Partitions will happen, so it is really a choice between C and A during a partition. PACELC adds that even without a partition there is a trade-off between latency and consistency, for example how many replicas I wait for.",
                    "For a bank balance I would choose consistency: a single leader or a quorum, refusing on the minority side, because a wrong answer costs money. For a shopping cart I would choose availability with a merge rule, such as a union of items using version vectors or a CRDT, because being able to add to the cart matters more and conflicts are easy to merge. Most real systems let me tune this per operation with quorum settings, so I would use strong settings on the critical paths and weaker ones elsewhere.\""],
            follow=[("What is the difference between CAP consistency and ACID consistency?", "CAP consistency is linearizability (all nodes agree on the latest value); ACID consistency means the database moves between states that satisfy its constraints."),
                    ("What is eventual consistency?", "If updates stop, all replicas converge to the same value; in the meantime reads can return older values."),
                    ("What is read repair?", "When a read finds replicas disagreeing it writes the newest version back to the stale ones, healing divergence lazily.")],
            slips=["\"Pick two of three\" as the whole answer.", "Saying we choose CA.", "Labelling a whole system CP or AP when it is tunable per request."],
        ),
        quick=[
            ("When does a read see the latest acknowledged write?", "When W + R > N: the read and write sets overlap."),
            ("How many replica failures does N=5, W=3 tolerate for writes?", "N - W = 2."),
            ("What does a CP system do on the minority side of a partition?", "Refuses requests it cannot serve consistently."),
        ],
        traps=[
            "Believing quorums alone order concurrent writes: you still need version vectors or a leader.",
            "W = N: any single failed replica stops all writes.",
            "Calling a system CP or AP in general: consistency is usually tunable per operation.",
        ],
    ),
]
