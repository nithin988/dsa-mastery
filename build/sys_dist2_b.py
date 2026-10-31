"""S22 distributed systems: part B (lessons 4 to 6: consensus, retries and failure handling, distributed transactions)."""
import sysviz as v

RAFT_SEQ = v.seq(
    ["Leader (term 1)", "Follower B", "Follower C"],
    [("a->b", 0, 1, "heartbeat"),
     ("a->b", 0, 2, "heartbeat"),
     ("note", 0, 2, "the leader crashes: heartbeats stop"),
     ("a->b", 1, 2, "B times out first: becomes candidate, term 2, 'vote for me'"),
     ("a->b", 2, 1, "C grants its vote (one vote per term)", "reply"),
     ("note", 0, 2, "B has a majority of the cluster: leader of term 2"),
     ("a->b", 1, 2, "heartbeat (term 2)")],
    "Leader election (Raft)", "A follower that stops hearing the leader asks for votes; a majority makes it the new leader")

TWOPC_SEQ = v.seq(
    ["Coordinator", "Bank A", "Bank B"],
    [("a->b", 0, 1, "prepare: can you debit 100?"),
     ("a->b", 0, 2, "prepare: can you credit 100?"),
     ("a->b", 1, 0, "yes (locks the row, promises to commit)", "reply"),
     ("a->b", 2, 0, "yes (locks the row, promises to commit)", "reply"),
     ("note", 0, 2, "the coordinator crashes here: both banks hold locks and wait: 'in doubt'"),
     ("a->b", 0, 1, "commit", "bad"),
     ("a->b", 0, 2, "commit", "bad")],
    "Two-phase commit", "Atomic across systems, but a coordinator crash between the phases blocks the participants")

LESSONS_B = [
    dict(
        title="Consensus and leader election: how a cluster agrees",
        tier="hot",
        situation="Five servers must agree on who the leader is, and on the order of changes, even when some crash or lose contact. This is what etcd, ZooKeeper, Consul and the control planes of Kubernetes and most databases depend on.",
        learn=["Leader, followers and terms (Raft)", "Why a majority makes two leaders impossible", "How many failures a cluster survives", "What an uncommitted entry is"],
        model=[
            "**Consensus** protocols (Paxos, **Raft**) let a group of machines agree on a value, or on an **ordered log of changes**, despite crashes and message loss. In Raft one node is the **leader** for a numbered **term**: it receives all writes, appends them to its log, replicates them to **followers**, and sends **heartbeats**. If followers stop hearing heartbeats they time out (after a **randomised** delay, so they rarely time out together), one becomes a **candidate** in a new term and asks for votes; each node votes **once per term**; a candidate that gets a **majority** becomes leader. Because any two majorities overlap in at least one node, which votes only once, **two leaders cannot exist in the same term**.",
            "An entry is **committed** once the leader has stored it on a **majority**; only then is the client told it succeeded, and a later leader is guaranteed to have it. So a cluster of **2f + 1** nodes tolerates **f** failures: 3 nodes tolerate 1, 5 tolerate 2, and an even number adds cost without adding tolerance (4 nodes still tolerate only 1). If a majority is unreachable the cluster **stops accepting writes** rather than risk disagreement: it chooses consistency over availability. Costs: every write needs a round trip to a majority, so keep the nodes close; and do not run consensus yourself: use etcd, ZooKeeper, or a database or cloud service that has it, for **small, critical data** (leader election, configuration, locks, cluster membership), not as a general data store.",
        ],
        analogy="A committee elects a chair by majority vote. If the chair disappears, the first member to notice calls an election; because a majority is needed and everyone votes once, there can never be two chairs at once. A decision counts only when a majority has written it in their minutes.",
        visual=[RAFT_SEQ],
        sim=None,
        walk=[
            ("Followers wait for heartbeats", "Each has a random election timeout (for example 150 to 300 ms)."),
            ("The leader fails; one follower times out first", "It increments the term, votes for itself and asks the others for votes."),
            ("Each node votes once per term", "A node grants its vote to the first candidate it hears in that term (if the candidate's log is up to date)."),
            ("A majority wins", "The candidate becomes leader and sends heartbeats; the others become followers."),
            ("Writes commit on a majority", "The leader replies to the client once a majority has stored the entry."),
        ],
        groups=[
            dict(title="A toy Raft cluster: elect, lose the leader, lose the majority", cmds=[
                dict(c=r'''python3 - <<'EOF'
import random
rng = random.Random(4)
class Cluster:
    def __init__(self, n):
        self.n = n; self.alive = set(range(n)); self.term = 0; self.leader = None
        self.log, self.committed = [], 0
    def majority(self): return self.n // 2 + 1
    def election(self):
        # each living node picks a random election timeout; the earliest one becomes a candidate
        timeouts = {i: rng.randint(150, 300) for i in self.alive}
        cand = min(timeouts, key=timeouts.get)
        self.term += 1
        votes = len(self.alive)                       # every living node votes once for this term (they all grant the first request)
        if votes >= self.majority():
            self.leader = cand
            return 'term %d: node %d times out first (%d ms), gets %d of %d votes -> LEADER' % (self.term, cand, timeouts[cand], votes, self.n)
        self.leader = None
        return 'term %d: node %d asks for votes, gets only %d of %d (majority is %d) -> NO LEADER, cluster stops accepting writes' % (self.term, cand, votes, self.n, self.majority())
    def write(self, entry):
        if self.leader is None or self.leader not in self.alive: return 'write %r REFUSED: no leader' % entry
        self.log.append(entry); acks = len(self.alive)
        if acks >= self.majority():
            self.committed = len(self.log); return 'write %r COMMITTED (stored on %d of %d nodes)' % (entry, acks, self.n)
        return 'write %r NOT committed: only %d of %d nodes reachable' % (entry, acks, self.n)
c = Cluster(5)
print(c.election()); print(c.write('x=1'))
print('--- the leader (node %d) crashes' % c.leader); c.alive.discard(c.leader); print(c.election()); print(c.write('x=2'))
print('--- a second node crashes (3 of 5 left)'); c.alive.discard(max(c.alive)); print(c.election()); print(c.write('x=3'))
print('--- a third node crashes (2 of 5 left)'); c.alive.discard(max(c.alive)); print(c.election()); print(c.write('x=4'))
print()
print('nodes  majority  failures tolerated')
for n in (3, 4, 5, 6, 7): print('%5d  %8d  %8d' % (n, n // 2 + 1, n - (n // 2 + 1)))
EOF''',
                     e="A toy Raft cluster shows the rules without the networking. The first election finds a leader with all five votes and a write commits on five nodes. After the leader crashes, the others elect a new one in a **higher term** and carry on. With two of five nodes down (three left) there is still a majority and writes commit. With **three** down (two left) no candidate can reach three votes: there is **no leader**, writes are refused rather than risking two sides disagreeing. The table at the end is the arithmetic to memorise: 4 nodes tolerate no more failures than 3, and 6 no more than 5, which is why clusters have odd sizes.",
                     annot=[("term 1: node N times out first ... 5 of 5 votes -> LEADER", "the node whose random timeout fired first wins the election"),
                            ("--- the leader crashes ... term 2 ... 4 of 5 votes -> LEADER", "a new election in a higher term; the cluster keeps working with four nodes"),
                            ("3 of 5 left ... COMMITTED (stored on 3 of 5 nodes)", "three is still a majority of five"),
                            ("2 of 5 left ... NO LEADER ... REFUSED: no leader", "no majority: the cluster stops accepting writes: consistency over availability"),
                            ("4 nodes: majority 3, failures tolerated 1", "an even size adds cost but not fault tolerance")]),
            ]),
        ],
        scenario=dict(
            title="\"Explain how Raft elects a leader and why it can't have two leaders. How many nodes do you run?\"",
            ask="A standard senior-level question. Concrete mechanics, plus judgement about cluster size and placement.",
            clarify=[("Which failures must the cluster survive: one machine, one rack, one data centre?", "Placement decides the node count and how many sites.")],
            think=[("Explain the election.", "Followers expect heartbeats. On timeout (randomised, so rarely simultaneous) a follower becomes a candidate, increments the term, votes for itself and requests votes. Each node votes once per term, and only for a candidate whose log is at least as up to date as its own."),
                   ("Explain why not two leaders.", "A candidate needs a majority. Any two majorities share a node, and that node voted only once in the term, so two candidates cannot both win the same term. A leader from an older term learns of the higher term and steps down."),
                   ("Explain commit.", "The leader appends to its log, replicates, and commits when a majority has stored the entry; only then does it acknowledge. Any future leader must have won votes from a majority, so it has every committed entry."),
                   ("Size and placement.", "2f + 1 nodes tolerate f failures: three for one failure, five for two. Even sizes waste a node. Spread across failure domains: three nodes across three zones survive a zone loss; two sites cannot hold a majority symmetrically, so use three sites or accept that one site is the master."),
                   ("State the costs.", "Writes need a majority round trip (latency grows with distance); throughput is limited to what the leader handles; use for small, critical data, not bulk storage."),
                   ("Say what not to do.", "Do not implement it yourself; use etcd, ZooKeeper, Consul or a managed service; do not stretch a small cluster across a high-latency link.")],
            answer=["\"In Raft, followers expect heartbeats from the leader. If one stops hearing them it waits a random election timeout, becomes a candidate, increments the term, votes for itself and asks the others for votes. Each node votes once per term, and only for a candidate whose log is at least as up to date as its own. A candidate that gets a majority becomes leader.",
                    "Two leaders cannot exist in one term because two majorities always overlap in at least one node, and that node voted only once. A write commits when the leader has stored it on a majority, so any future leader, which also needed a majority, has it. I would run an odd number: three nodes survive one failure and five survive two, spread across failure domains, for example three zones. The costs are a majority round trip per write and a limit to small, critical data, so I would use etcd or ZooKeeper for leader election, configuration and locks, never implement it myself, and not stretch it over a slow link.\""],
            follow=[("What happens during a network partition?", "The side with a majority keeps a leader and continues; the minority side cannot elect one and refuses writes; when the partition heals the minority nodes catch up and the old leader steps down."),
                    ("Why a randomised timeout?", "So nodes rarely time out simultaneously, which avoids repeated split votes where nobody gets a majority."),
                    ("Is Raft the same as Paxos?", "Same guarantees; Raft was designed to be easier to understand and implement, with an explicit leader and a log structure.")],
            slips=["Saying a four-node cluster is more resilient than three.", "Placing two of three nodes in one data centre.", "Using consensus as a general-purpose database."],
        ),
        quick=[
            ("How many failures does a 5-node Raft cluster tolerate?", "Two: a majority of three must stay up."),
            ("Why can two leaders not exist in the same term?", "Each needs a majority, any two majorities share a node, and a node votes once per term."),
            ("When does Raft consider an entry committed?", "When the leader has stored it on a majority of nodes."),
        ],
        traps=[
            "Even-sized clusters: no extra tolerance, more cost.",
            "Splitting a small cluster across two sites: losing the bigger site loses the majority.",
            "Using the consensus store for large or high-volume data.",
        ],
    ),
    dict(
        title="Retries, timeouts, circuit breakers and retry storms",
        tier="hot",
        situation="A downstream service has a two-second hiccup. Every client retries immediately, three times. The service, which could have recovered, is now receiving four times its normal load and never gets back up. Retries are medicine and poison.",
        learn=["How naive retries amplify an outage", "Exponential backoff with jitter", "Timeouts, deadlines and retry budgets", "Circuit breakers: stop calling something that is down"],
        model=[
            "A retry converts a transient failure into success only if the failure really was transient. If the service is overloaded, **immediate retries multiply the load** (a **retry storm**), and layered retries multiply further (three layers of three retries is 27 times). The standard remedies: **exponential backoff** (wait 1 s, 2 s, 4 s ...), with **jitter** (randomise the wait so thousands of clients do not retry at the same instant), a **bounded number of attempts**, a **retry budget** (for example at most 10 percent of requests may be retries), and an overall **deadline** that is passed down the call chain so nobody works on an answer the caller has already given up on. Only retry **idempotent** operations (or ones carrying an idempotency key), and only on errors that can be transient (timeouts, 503), not on errors that will never succeed (400, 404).",
            "A **circuit breaker** wraps calls to a dependency and counts failures. **Closed**: calls pass through. After too many failures it **opens**: calls fail immediately without touching the sick dependency (giving it room to recover and giving callers a fast failure or a fallback). After a cool-down it goes **half-open**: a few trial calls are allowed; if they succeed it closes, otherwise it opens again. Related protections: **bulkheads** (separate pools so one slow dependency cannot use all threads), **load shedding** and **timeouts** on every call (a call without a timeout can hang forever and hold a thread). Fast failure with a graceful fallback usually beats a slow failure.",
        ],
        analogy="A crowd all redialling a busy phone line makes the line permanently busy; if each person waits a random, growing time before trying again, the line recovers. A circuit breaker is the fuse box: after repeated faults it cuts the circuit so the wiring can cool down, then tests it carefully.",
        sim=None,
        walk=[
            ("A dependency starts failing", "Calls return errors or time out."),
            ("Naive clients retry at once", "Load on the struggling service multiplies; it cannot recover."),
            ("Backoff with jitter spreads the retries", "Retries arrive later and at different moments; the load stays near normal."),
            ("The breaker opens", "After enough failures, calls fail fast; the dependency gets quiet time."),
            ("Half-open probes and recovery", "A few trial calls; when they succeed the circuit closes and traffic returns."),
        ],
        groups=[
            dict(title="A retry storm, then backoff and a breaker (simulated time)", cmds=[
                dict(c=r'''python3 - <<'EOF'
import random
# 200 clients each need ONE answer from a service that is down for the first 2 seconds. Time advances in 10 ms ticks.
def simulate(strategy, seed=7):
    rng = random.Random(seed)
    done, attempts, in_outage = {}, 0, 0
    state = [{'t': 0, 'n': 0} for _ in range(200)]          # per-client: next attempt time and attempts so far
    breaker = {'open_until': -1, 'fails': 0}
    for tick in range(0, 1000):                              # 10 seconds
        now = tick * 10
        for i, s in enumerate(state):
            if i in done or s['t'] > now: continue
            if strategy == 'breaker' and now < breaker['open_until']:      # open: fail fast without calling the service
                s['t'] = now + 200 + rng.randint(0, 200); continue
            attempts += 1; s['n'] += 1
            ok = now >= 2000                                  # the service recovers at 2 s
            if not ok: in_outage += 1
            if ok: done[i] = now; continue
            if strategy == 'breaker':
                breaker['fails'] += 1
                if breaker['fails'] >= 20: breaker['open_until'], breaker['fails'] = now + 500, 0
            if strategy == 'naive':   s['t'] = now + 10                                              # retry immediately, forever
            elif strategy == 'backoff': s['t'] = now + int(100 * 2 ** min(s['n'], 5) * (0.5 + rng.random()))   # exponential + jitter
            else:                     s['t'] = now + int(100 * 2 ** min(s['n'], 5) * (0.5 + rng.random()))
    finish = max(done.values()) if len(done) == 200 else None
    return attempts, in_outage, finish
print('%-22s %10s %22s %16s' % ('strategy', 'requests', 'sent while down', 'all served at'))
for name in ('naive', 'backoff', 'breaker'):
    a, o, f = simulate(name)
    print('%-22s %10d %22d %13s' % ({'naive': 'immediate retry', 'backoff': 'backoff + jitter', 'breaker': 'backoff + breaker'}[name], a, o, ('%.2f s' % (f / 1000)) if f else 'never'))
EOF''',
                     e="The same outage, three client strategies (a simulation in virtual time, so it repeats exactly). With **immediate retries**, 200 clients hammer the dead service every 10 ms for two seconds: 40,000 requests, all wasted, all load on a service trying to start (a real server would not survive it, even though in this simulation everyone is served the instant it returns). **Exponential backoff with jitter** sends about 800 requests in the same window, a fiftieth of the load, but its clients are sleeping through long delays, so the last one is served at 6.5 seconds: backoff trades some extra waiting for protection (cap the delay to tune it). Adding a **circuit breaker** (open for half a second, then probing) sends only 80 requests during the outage and finishes at 2.5 seconds: the best of both here, because clients wait locally for a short time and come back quickly.",
                     annot=[("immediate retry: 40200 requests, 40000 while down", "every client retries every tick: the retry storm"),
                            ("backoff + jitter: 806 while down, all served at 6.48 s", "about a fiftieth of the load, but the longest delays make the last client wait until 6.5 s"),
                            ("backoff + breaker: 80 while down, all served at 2.48 s", "the breaker refuses calls locally for half-second stretches, then probes: little load and quick recovery"),
                            ("immediate retry: all served at 2.00 s", "the fastest recovery here, bought with 40,000 requests a real service could not have absorbed")]),
            ]),
        ],
        scenario=dict(
            title="\"A downstream service becomes slow and then your whole system falls over. What happened and how do you prevent it?\"",
            ask="A cascading-failure question. They want the chain of events and several layers of defence, not one trick.",
            clarify=[("Were there retries, timeouts and shared thread pools? Was the failing service overloaded or down?", "Cascades usually combine missing timeouts, aggressive retries and shared resources.")],
            think=[("Reconstruct the cascade.", "Service B slows. Callers' threads wait on B (no or long timeouts), so A's thread pool fills with waiting requests. A stops answering its own callers, who retry, increasing the load on A and on B. Retries at several layers multiply. Everything becomes slow, then fails."),
                   ("Defence 1: timeouts and deadlines.", "Every remote call has a timeout shorter than the caller's own; propagate a deadline so no one works on abandoned requests."),
                   ("Defence 2: disciplined retries.", "Only idempotent calls, bounded attempts, exponential backoff with jitter, a retry budget, and retry at one layer only."),
                   ("Defence 3: circuit breakers and fallbacks.", "Fail fast when a dependency is sick; return cached or degraded data instead of an error where possible."),
                   ("Defence 4: isolation and shedding.", "Bulkheads (separate pools per dependency), admission control and load shedding at the edge (429 or 503 early), queue limits."),
                   ("Defence 5: verify.", "Chaos and load tests that make a dependency slow (not just down); dashboards for retries, breaker state and saturation.")],
            answer=["\"A dependency slowed down, callers' threads piled up waiting for it because the timeouts were long or missing, so the caller's own pool filled and it stopped serving its callers. Those callers retried, adding load to everything, and retries at several layers multiplied it. A slow dependency is more dangerous than a dead one because it holds resources.",
                    "To prevent it I would put a timeout on every remote call, shorter than the caller's own, and pass a deadline down the chain. Retries only for idempotent calls, with a bounded count, exponential backoff and jitter, a retry budget and retries at one layer only. Circuit breakers fail fast when a dependency is sick, with a fallback such as cached or degraded data. I would isolate dependencies with separate pools, and shed load at the edge with 429 or 503 instead of queueing without limit. Then I would test it by making dependencies slow, not only dead, and watch retries, breaker state and saturation.\""],
            follow=[("Why is slow worse than down?", "A down service fails fast and frees resources; a slow one ties up threads, connections and memory in every caller until they fail too."),
                    ("What is a retry budget?", "A cap on retries relative to normal traffic (for example retries may add at most 10 percent): it stops retries from amplifying an outage."),
                    ("What is hedging?", "Sending a duplicate request to another replica after a delay and using the first answer: cuts tail latency for idempotent reads at the cost of extra load.")],
            slips=["Adding retries as the fix for overload.", "No timeouts on outbound calls.", "Retrying at every layer of the stack."],
        ),
        quick=[
            ("Why add jitter to backoff?", "So many clients do not retry at the same instant and overload the recovering service."),
            ("What do the three circuit breaker states mean?", "Closed: calls pass; open: calls fail fast; half-open: a few trial calls test recovery."),
            ("Why is a slow dependency worse than a dead one?", "It holds threads and connections in every caller until they fail too."),
        ],
        traps=[
            "Retrying non-idempotent calls or non-transient errors.",
            "Layered retries multiplying load (3 x 3 x 3 = 27).",
            "Timeouts longer than the caller's own timeout: work continues for nobody.",
        ],
    ),
    dict(
        title="Distributed transactions: two-phase commit and sagas",
        tier="hot",
        situation="Moving money between two banks, or booking a flight, a hotel and a car, must be all or nothing, but each step lives in a different service with its own database. A single database transaction no longer exists.",
        learn=["Two-phase commit and its blocking problem", "Sagas and compensating actions", "Why steps must be idempotent", "Choosing between them"],
        model=[
            "**Two-phase commit (2PC)** makes a transaction atomic across several systems: a **coordinator** asks every participant to **prepare** (each locks its data and promises it can commit), and if all say yes it tells them to **commit**; any no (or timeout) means **abort**. It is correct but **blocking**: if the coordinator crashes after the participants prepared, they hold locks and cannot decide on their own (**in doubt**) until it returns. It also needs every system to support it and holds locks across network round trips, so it scales poorly and is rare between independent services.",
            "A **saga** replaces one big atomic transaction with a **sequence of local transactions**, each followed, if a later step fails, by a **compensating action** that semantically undoes it (refund the payment, release the room). There is no isolation (other transactions see the intermediate state), so design for it: show \"pending\", reserve rather than commit, order steps so the least reversible comes last. Sagas are driven by **orchestration** (a coordinator service tells each step what to do) or **choreography** (each service reacts to events). Every step and every compensation must be **idempotent and retryable**, because messages are redelivered, and the saga's progress must be stored durably (often with the outbox pattern) so it can resume after a crash.",
        ],
        analogy="2PC is a group booking where everyone is asked \"can you commit?\" and must wait on the phone until the organiser calls back: if the organiser vanishes, everyone is stuck holding the line. A saga is booking each part separately and, if the last booking fails, cancelling the earlier ones one by one.",
        visual=[TWOPC_SEQ],
        sim=None,
        walk=[
            ("Split the business transaction into steps", "Reserve flight, reserve hotel, charge card, issue tickets: each is a local transaction in one service."),
            ("Define a compensation for each step", "Cancel reservation, refund, void ticket: each is itself idempotent."),
            ("Run the steps in order, durably", "The saga's state (which steps are done) is stored so a crash can resume."),
            ("On failure, compensate in reverse", "Undo the completed steps from last to first."),
            ("Expose the intermediate state honestly", "Show pending status; do not treat reserved as confirmed."),
        ],
        groups=[
            dict(title="A blocked 2PC and a saga that compensates", cmds=[
                dict(c=r'''python3 - <<'EOF'
# Two-phase commit: a coordinator and two participants.
class Participant:
    def __init__(self, name): self.name, self.state, self.locked = name, 'idle', False
    def prepare(self): self.state, self.locked = 'prepared (locks held, waiting for the decision)', True; return 'yes'
    def commit(self): self.state, self.locked = 'committed', False
    def abort(self): self.state, self.locked = 'aborted', False
def two_phase_commit(parts, crash_after_prepare):
    votes = [p.prepare() for p in parts]
    if crash_after_prepare: return 'coordinator CRASHED after the prepare phase'
    if all(v == 'yes' for v in votes):
        for p in parts: p.commit()
        return 'coordinator committed everyone'
    for p in parts: p.abort()
    return 'coordinator aborted everyone'
for crash in (False, True):
    a, b = Participant('bank A'), Participant('bank B')
    print(two_phase_commit([a, b], crash))
    for p in (a, b): print('   %s: %s%s' % (p.name, p.state, '   <- IN DOUBT: blocked, rows locked' if p.locked else ''))
EOF''',
                     e="Two-phase commit, normal and broken. When the coordinator survives, both banks commit and release their locks. When it crashes **after** both have prepared, neither bank can decide alone: a participant that already promised to commit must not abort (the other might have committed) and cannot commit (the other might have aborted). Both sit **in doubt**, with the accounts locked, until the coordinator recovers. This blocking is the central weakness of 2PC and the reason it is avoided between independent services.",
                     annot=[("coordinator committed everyone / committed / committed", "the happy path: atomic across both systems"),
                            ("coordinator CRASHED after the prepare phase", "the failure window between the two phases"),
                            ("bank A: prepared ... IN DOUBT: blocked, rows locked", "the participant has promised and now must wait: locks held, nobody can use the rows")]),
                dict(c=r'''python3 - <<'EOF'
# A saga: book flight, book hotel, charge card. Each step has a compensation; failures undo completed steps in reverse.
log = []
def step(name, action, undo, fail=False):
    return dict(name=name, action=action, undo=undo, fail=fail)
def run_saga(steps):
    done = []
    for s in steps:
        if s['fail']:
            log.append('%-14s FAILED' % s['name'])
            for d in reversed(done): log.append('%-14s compensate: %s' % (d['name'], d['undo']))
            return 'saga aborted: all earlier steps compensated'
        log.append('%-14s done:       %s' % (s['name'], s['action'])); done.append(s)
    return 'saga completed'
print(run_saga([step('book flight', 'seat 14C held', 'seat released'), step('book hotel', 'room 302 held', 'room released'), step('charge card', 'authorised 480', 'authorisation voided')]))
print('\n'.join('  ' + l for l in log)); log.clear()
print()
print(run_saga([step('book flight', 'seat 14C held', 'seat released'), step('book hotel', 'room 302 held', 'room released'), step('charge card', 'authorised 480', 'authorisation voided', fail=True)]))
print('\n'.join('  ' + l for l in log))
EOF''',
                     e="A saga with no global lock. The happy path runs three local steps in order. In the failing run the card step fails, so the saga walks **backwards** through the completed steps and runs each compensation: the hotel room and then the seat are released. Each compensation is a new business action, not a database rollback, so the world passes through intermediate states (a seat was briefly held for someone who then did not pay), which is why sagas lack isolation and why real systems show \"pending\" and use reservations that expire.",
                     annot=[("happy path: book flight done / book hotel done / charge card done", "each step is a local transaction in its own service"),
                            ("charge card FAILED", "a later step fails: the saga must undo the earlier ones"),
                            ("book hotel compensate: room released / book flight compensate: seat released", "compensations run in reverse order, each as a new business action")]),
            ]),
        ],
        scenario=dict(
            title="\"A transfer touches two services with separate databases. How do you keep it atomic?\"",
            ask="The distributed transaction question. They want to hear why 2PC is avoided, how a saga works, and what you give up.",
            clarify=[("Do both services support a prepare phase? Is temporary inconsistency acceptable?", "Independent services usually do not share a transaction manager; a few seconds of \"pending\" is normally fine.")],
            think=[("Say why not a distributed ACID transaction.", "2PC needs every participant to support it, holds locks across network round trips, blocks if the coordinator fails, and hurts availability and throughput."),
                   ("Describe the saga.", "A sequence of local transactions with compensations. Debit account A (local), then credit account B (local); if crediting fails, compensate by refunding A."),
                   ("Choose orchestration or choreography.", "Orchestration: a coordinator service holds the saga state and calls each step (clear, easier to monitor, a central component). Choreography: each service listens for events and emits the next (decoupled, harder to follow as it grows)."),
                   ("Make every step safe to repeat.", "Idempotency keys on every step and compensation; the saga state and messages stored durably with the outbox pattern; retries with backoff; a dead-letter queue for stuck sagas with alerts."),
                   ("Handle isolation.", "Intermediate states are visible: use a pending/held status, reserve before commit, order the steps so the hardest to undo comes last, and expire reservations."),
                   ("Offer the simpler alternative.", "If both pieces of data can live in one database, use one local transaction and avoid the problem; split services only where the benefit outweighs this cost.")],
            answer=["\"I would avoid a distributed ACID transaction: two-phase commit needs every participant to support it, holds locks across network calls and blocks if the coordinator dies, which hurts availability and throughput. Instead I would use a saga: debit account A in its own local transaction, then credit account B in its own; if the credit fails, run a compensation that refunds A.",
                    "I would orchestrate it from a service that stores the saga state durably, using the outbox pattern so the state and messages stay consistent. Every step and compensation carries an idempotency key and is retried with backoff, and stuck sagas go to a dead-letter queue with an alert. Because intermediate states are visible I would show a pending status and use reservations that expire. And if the two pieces of data can live in one database, a local transaction is simpler than any of this.\""],
            follow=[("Orchestration or choreography?", "Orchestration for processes with many steps and clear ownership (easier to see state and debug); choreography for small, loosely coupled flows, at the risk of an implicit, hard-to-follow workflow."),
                    ("What if a compensation fails?", "Retry it (idempotently) until it succeeds, alert if it cannot; some steps need manual resolution, which is why steps are ordered by reversibility."),
                    ("How is a saga different from a transaction?", "No isolation and no automatic rollback: intermediate states are visible and undoing is a new business action.")],
            slips=["Proposing 2PC between independent microservices.", "Compensations that are not idempotent.", "Ignoring the intermediate states users and other services can see."],
        ),
        quick=[
            ("What is the main weakness of two-phase commit?", "It blocks: participants hold locks and cannot decide if the coordinator fails after the prepare phase."),
            ("What is a compensating action?", "A business operation that semantically undoes a completed step, such as a refund."),
            ("Why must saga steps be idempotent?", "Messages and retries cause repeats; repeating a step or compensation must be harmless."),
        ],
        traps=[
            "Compensations that cannot be retried safely.",
            "Treating a saga as isolated: other transactions see the intermediate state.",
            "Splitting data across services when one database transaction would have been enough.",
        ],
    ),
]
