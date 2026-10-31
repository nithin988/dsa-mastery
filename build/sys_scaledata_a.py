"""S19 scaling data: part A (rig, lessons 1 to 3: replication, failover, partitioning)."""
import sysviz as v

RIG = r'''mkdir -p ~/rep && cd ~/rep && cat > rig.sh <<'EOF'
# A private PostgreSQL primary (port 5551) and a streaming replica cloned from it (port 5552). Sockets in ~/rep.
export PG=$(ls -d /usr/lib/postgresql/*/bin | head -1); export PATH=$PG:$PATH
export R=$HOME/rep PGUSER=learner
pq() { psql -X -q -h $R -p 5551 -d postgres "$@"; }       # talk to the primary
rq() { psql -X -q -h $R -p 5552 -d postgres "$@"; }       # talk to the replica
priup() { [ -d $R/primary ] || initdb -D $R/primary -A trust -U learner >/dev/null
          pg_ctl -D $R/primary -o "-p 5551 -k $R -c listen_addresses='' -c fsync=off $*" -l $R/primary.log -w start >/dev/null; }
repup() { priup "$1"; rm -rf $R/replica
          pg_basebackup -h $R -p 5551 -D $R/replica -R -X stream >/dev/null 2>&1
          pg_ctl -D $R/replica -o "-p 5552 -k $R -c listen_addresses='' -c fsync=off $2" -l $R/replica.log -w start >/dev/null; }
repdown() { pg_ctl -D $R/replica -m fast stop >/dev/null 2>&1; pg_ctl -D $R/primary -m fast stop >/dev/null 2>&1; }
EOF
. ./rig.sh; echo "rig ready in $R: rig.sh gives priup, repup, repdown, pq (primary) and rq (replica)"'''

REPL_SEQ = v.seq(
    ["Client", "Primary", "Replica"],
    [("a->b", 0, 1, "INSERT; COMMIT"),
     ("a->b", 1, 0, "OK (primary has it in its WAL)", "reply"),
     ("a->b", 1, 2, "stream the WAL record"),
     ("a->b", 0, 2, "SELECT immediately", "bad"),
     ("a->b", 2, 0, "old data: the replica has not applied it yet", "bad"),
     ("note", 0, 2, "milliseconds later the replica has applied the change and reads agree"),
     ("a->b", 0, 2, "SELECT again"),
     ("a->b", 2, 0, "new data", "reply")],
    "Asynchronous replication and lag", "The primary acknowledges before the replica has applied the change")

SPLIT_VIZ = v.figure(
    720, 226,
    [v.box(10, 80, 130, 56, "Primary", "ok", "writable"),
     v.box(10, 20, 130, 40, "Its replica", "acc", "read only"),
     v.arrow(75, 60, 75, 80),
     v.text(250, 70, "primary stops answering", "dg-s"),
     v.box(330, 80, 130, 56, "Replica promoted", "warn", "now writable"),
     v.arrow(140, 108, 330, 108),
     v.box(560, 80, 150, 56, "Old primary returns", "ink", "still thinks it is the primary"),
     v.text(520, 170, "Two writable nodes with different data: split brain.", "dg-s"),
     v.text(360, 206, "Fencing (shutting the old primary out) must happen before or as part of promotion.", "dg-s")],
    "Failover and split brain", "Promoting a replica is easy; making sure the old primary cannot also accept writes is the hard part")

PART_VIZ = v.figure(
    720, 214,
    [v.box(10, 70, 120, 56, "events", "acc", "one logical table"),
     v.arrow(130, 98, 175, 40), v.arrow(130, 98, 175, 98), v.arrow(130, 98, 175, 156),
     v.box(175, 14, 180, 52, "events_2026_08", "ink", "old: can be archived or dropped"),
     v.box(175, 72, 180, 52, "events_2026_09", "ok", "last month"),
     v.box(175, 130, 180, 52, "events_2026_10", "ok", "current: queries usually go here"),
     v.box(430, 72, 280, 52, "Pruning", "warn", "a query with a date range only touches the matching partitions"),
     v.text(360, 204, "Partitioning splits one table inside one database; sharding splits data across several databases.", "dg-s")],
    "Table partitioning", "Same database, smaller pieces: pruning and cheap deletion of old data")

LESSONS_A = [
    dict(
        title="Replication: copies for reads and for survival",
        tier="hot",
        situation="One database server answers 90 percent reads and the CPU is at 85 percent. Adding a second copy that serves the reads sounds easy. It is, until a customer places an order, refreshes the page and the order is not there.",
        learn=["How a replica is built and kept up to date (the log stream)", "Why replicas are read-only and what that gives you", "Replication lag and read-your-writes", "Setting up a real replica and watching it work"],
        model=[
            "**Replication** keeps one or more **copies** of a database on other machines. In PostgreSQL (and most databases) the **primary** accepts writes and ships its **write-ahead log** to **replicas**, which replay it and stay read-only. This gives you **read scaling** (send reads to replicas), **availability** (a replica can be promoted if the primary dies) and a place to run slow reports and backups without disturbing production. It does **not** scale writes: every write still happens on the primary and on every replica.",
            "The default is **asynchronous** replication: the primary acknowledges a commit as soon as its own log is safe, **before** replicas have applied it. So a replica is always slightly **behind** (**replication lag**): usually milliseconds, but seconds or minutes under load or network trouble. Consequences you must design for: a user can write and then read stale data from a replica (**read-your-writes** violated), and two reads from two replicas can disagree. Common fixes: read your own recent writes from the primary, pin a session to one replica, or send reads to a replica only when its lag is below a threshold.",
        ],
        analogy="A newspaper with regional print shops: the head office (primary) sends each edition's content to the shops (replicas) by courier. Readers near a shop get it quickly, but for a short while the shop still prints yesterday's edition.",
        visual=[REPL_SEQ],
        sim=None,
        walk=[
            ("Clone the primary", "`pg_basebackup` copies the primary's data files to a new directory and writes a recovery configuration that points back at the primary."),
            ("The replica streams the log", "It connects to the primary and receives the write-ahead log continuously, replaying each record."),
            ("Reads work, writes are refused", "The replica is in recovery mode: queries are allowed, writes fail with a read-only error."),
            ("Lag is the gap", "Between commit on the primary and replay on the replica there is a delay. You can see it in `pg_stat_replication`."),
            ("Design around the gap", "Route reads that must be fresh to the primary, and everything else to replicas."),
        ],
        groups=[
            dict(title="Build a real replica and watch lag", cmds=[
                dict(c=RIG,
                     e="Creates the rig: helper functions that start a private PostgreSQL **primary** (port 5551), clone it with `pg_basebackup -R` into a **replica** (port 5552) and stop both. `pq` talks to the primary and `rq` to the replica. Everything stays under `~/rep`; no root, no network."),
                dict(volatile=True, c=r'''. ~/rep/rig.sh; repup
pq -c "create table notes(id serial primary key, body text); insert into notes(body) values ('first')"
sleep 1
echo "--- primary: in recovery? $(pq -At -c 'select pg_is_in_recovery()')   replica: in recovery? $(rq -At -c 'select pg_is_in_recovery()')"
echo "--- the replica has the data the primary wrote:"
rq -At -c "select id, body from notes"
echo "--- but it refuses writes:"
rq -c "insert into notes(body) values ('from the replica')" 2>&1 | head -1
echo "--- the primary sees its replica streaming:"
pq -At -c "select application_name, state, sync_state from pg_stat_replication"
repdown''',
                     e="The shape of replication, running. The primary is not in recovery; the replica is. The row written on the primary appears on the replica a moment later. A write sent to the replica is refused (`cannot execute INSERT in a read-only transaction`). From the primary's side `pg_stat_replication` shows one connected replica that is `streaming` and `async`: asynchronous, meaning commits do not wait for it.",
                     annot=[("primary: in recovery? f   replica: in recovery? t", "recovery mode means: replaying the primary's log, read only"),
                            ("1|first", "the replica holds the data written on the primary"),
                            ("ERROR: cannot execute INSERT in a read-only transaction", "writes only go to the primary"),
                            ("walreceiver|streaming|async", "one replica connected and streaming; async means the primary does not wait for it")]),
                dict(volatile=True, c=r'''. ~/rep/rig.sh; repup "" "-c recovery_min_apply_delay=2s"
pq -c "drop table if exists notes; create table notes(id serial primary key, body text)"; sleep 2.5
echo "--- write on the primary, then read the replica at once (the replica is made to apply changes 2 s late):"
pq -c "insert into notes(body) values ('my new order')"
echo "primary sees:        $(pq -At -c 'select count(*) from notes') row(s)"
echo "replica sees (now):  $(rq -At -c 'select count(*) from notes') row(s)"
sleep 3
echo "replica sees (3 s later): $(rq -At -c 'select count(*) from notes') row(s)"
echo "--- how far behind does the primary say the replica is?"
pq -c "insert into notes(body) values ('another')"
pq -At -c "select 'log bytes the replica has not applied yet: ' || pg_wal_lsn_diff(sent_lsn, replay_lsn) from pg_stat_replication"
repdown''',
                     e="Read-your-writes, broken on purpose. Real replicas usually lag by milliseconds; here the replica is configured to apply changes **2 seconds late** (`recovery_min_apply_delay`) so the effect is easy to see: the order is committed on the primary, but a read from the replica right afterwards **does not show it**. A few seconds later it is there. In production the window is shorter, but the bug is identical, and it shows up as \"I placed an order and it vanished\".",
                     annot=[("primary sees: 1 row(s)", "the primary has the committed order"),
                            ("replica sees (now): 0 row(s)", "the replica has received the change but not applied it yet: a stale read"),
                            ("replica sees (3 s later): 1 row(s)", "the replica caught up"),
                            ("log bytes the replica has not applied yet: some hundreds", "the primary can measure how much log the replica has received but not replayed: this gap is the lag")]),
            ]),
        ],
        scenario=dict(
            title="\"We added read replicas and users now report missing data right after they save. What is happening and how do you fix it?\"",
            ask="A realistic production symptom. They want you to name replication lag and offer more than one fix with trade-offs.",
            clarify=[("How are reads routed today? How long is the lag?", "Blind round-robin to replicas is the usual cause; lag of tens of milliseconds is enough to hit it.")],
            think=[("Name the cause.", "Asynchronous replication: the write commits on the primary and is acknowledged before replicas apply it. A read sent to a replica a few milliseconds later does not see the write."),
                   ("Fix 1: read your own writes from the primary.", "After a user writes, send that user's reads to the primary for a short window (or until the replica passes the write's log position). Simple; the primary carries a bit more read load."),
                   ("Fix 2: session stickiness or lag-aware routing.", "Pin a session to one replica (monotonic reads), or only use replicas whose lag is below a threshold; remove lagging replicas from rotation automatically."),
                   ("Fix 3: synchronous or remote_apply replication for critical reads.", "Make commit wait for the replica; correct but slower writes and a new availability dependency."),
                   ("Mention what replicas do not fix.", "Write capacity, and total storage per node. For those you partition or shard."),
                   ("Monitor.", "Alert on replication lag in seconds and bytes, and on replicas leaving the streaming state.")],
            answer=["\"This is replication lag. Replication is asynchronous, so a commit is acknowledged by the primary before replicas apply it, and a read routed to a replica a few milliseconds later does not see the write.",
                    "The usual fix is read-your-writes: after a user writes, route their reads to the primary for a short window, or until the replica has replayed past that write. Alternatively I pin each session to one replica and route only to replicas whose lag is below a threshold, removing lagging ones automatically. For a few critical paths I could use synchronous replication, accepting slower writes and a dependency on the replica. I would also monitor lag and remember that replicas scale reads, not writes: for writes I would partition or shard.\""],
            follow=[("What is monotonic reads?", "A guarantee that one user never sees data go backwards: reading from a newer replica then an older one would; pinning a session to one replica avoids it."),
                    ("How do you measure lag?", "On the primary, `pg_stat_replication` (replay_lag and byte difference between sent and replayed log positions); on the replica, the time since the last replayed transaction."),
                    ("Why not make all replication synchronous?", "Every commit waits for the slowest synchronous replica and stops entirely if it fails: it trades availability and latency for freshness.")],
            slips=["Saying \"add more replicas\" without addressing consistency.", "Forgetting that replicas do not scale writes.", "No lag monitoring or automatic removal."],
        ),
        quick=[
            ("What does a read replica scale: reads, writes, or both?", "Reads only; every write still happens on the primary and every replica."),
            ("What is replication lag?", "The delay between a commit on the primary and its replay on a replica."),
            ("How can you avoid showing a user stale data after they write?", "Read their own recent writes from the primary, or use a replica that has replayed past the write."),
        ],
        traps=[
            "Round-robin reads to replicas for all queries, including ones that follow a write.",
            "Ignoring replicas that fall far behind: they serve very stale data and may never catch up.",
            "Believing replicas make the system write-scalable.",
        ],
    ),
    dict(
        title="Failover, synchronous replication and split brain",
        tier="hot",
        situation="The primary dies at 3 a.m. Promoting a replica takes one command. The hard questions are: did the replica have the last transactions, and what happens when the old primary wakes up and still believes it is in charge?",
        learn=["Synchronous versus asynchronous commit and what each risks", "Promoting a replica", "Split brain and fencing", "Why automatic failover needs a consensus system"],
        model=[
            "With **asynchronous** replication a failover can **lose** the last few committed transactions (the primary acknowledged them, the replica never received them): the **recovery point** is not zero. With **synchronous** replication a commit waits until at least one replica confirms it has the log, so nothing acknowledged is lost, at the price of **higher write latency** and a new **availability risk**: if the synchronous replica is unreachable, commits **wait** (or you must reconfigure and accept the risk).",
            "**Failover** means promoting a replica to primary and sending clients to it. The dangerous failure is **split brain**: the old primary was only unreachable, not dead, and now there are **two writable nodes with different data**. Prevent it with **fencing**: make sure the old primary is shut down or cut off (power, network or a storage lock) before the new one accepts writes. Deciding \"the primary is really gone\" correctly is a distributed consensus problem, so production setups use a tool (Patroni with etcd or Consul, or a managed service) rather than a script, and they test the failover regularly.",
        ],
        analogy="Two pilots, one aircraft: if the captain becomes unresponsive the co-pilot takes the controls. If the captain was only briefly distracted and both fly, the plane is in danger. The cockpit procedure is the fencing.",
        visual=[SPLIT_VIZ],
        sim=None,
        walk=[
            ("Decide how much loss you can accept", "Zero loss needs synchronous replication; accepting a few seconds of loss allows asynchronous."),
            ("Detect failure with care", "A missed heartbeat could be a network blip. Wait long enough, ask more than one observer, ideally a quorum."),
            ("Fence the old primary", "Stop it for certain (or cut its network or storage) so it cannot accept writes."),
            ("Promote the best replica", "Choose the one with the most replayed log; promote it; it becomes writable."),
            ("Redirect clients and rebuild", "Switch the address or proxy to the new primary, and re-create a replica from it. The old primary must be rebuilt, not simply restarted."),
        ],
        groups=[
            dict(title="Synchronous commit, promotion and a split brain", cmds=[
                dict(volatile=True, c=r'''. ~/rep/rig.sh; repup "-c synchronous_standby_names='*'"
pq -c "create table pay(id serial primary key, amt int)"
echo "--- synchronous: commit waits for the replica, then succeeds"
s=$(date +%s%N); pq -c "insert into pay(amt) values (10)"; e=$(date +%s%N); echo "commit took $(( (e-s)/1000000 )) ms"
pq -At -c "select application_name, sync_state from pg_stat_replication"
echo "--- now the replica goes away:"
pg_ctl -D $R/replica -m fast stop >/dev/null; sleep 0.5
timeout 3 psql -X -q -h $R -p 5551 -d postgres -c "insert into pay(amt) values (20)"; echo "exit status after 3 s: $? (124 = still waiting for the replica)"
echo "--- what the primary is waiting on:"
pq -At -c "select wait_event from pg_stat_activity where wait_event = 'SyncRep'" | head -1
pg_ctl -D $R/primary -m immediate stop >/dev/null 2>&1''',
                     e="The price of synchronous replication, shown. With a replica attached the commit succeeds and `pg_stat_replication` says `sync`. When the replica is stopped, the next commit **does not complete**: `timeout` gives up after 3 seconds with status 124, and the server's session sits in the `SyncRep` wait. Nothing was lost, but writes are blocked until a replica is back or an operator removes the requirement. That is the trade: zero data loss, a new way for writes to stop.",
                     annot=[("commit took ~8 ms", "a commit that included a round trip to the replica"),
                            ("replica | sync", "the replica is the synchronous standby"),
                            ("exit status after 3 s: 124", "`timeout` killed the waiting client: the commit never finished"),
                            ("SyncRep", "the backend is waiting for synchronous replication confirmation")]),
                dict(volatile=True, c=r'''. ~/rep/rig.sh; repup
pq -c "create table acc(id int primary key, owner text); insert into acc values (1,'before failover')"; sleep 1
echo "--- the primary 'fails' (stopped hard), the replica is promoted:"
pg_ctl -D $R/primary -m immediate stop >/dev/null 2>&1
pg_ctl -D $R/replica promote -w >/dev/null
echo "replica in recovery? $(rq -At -c 'select pg_is_in_recovery()')  (f means it is now a writable primary)"
rq -c "insert into acc values (2, 'written on the NEW primary')"
echo "--- the old primary comes back, unaware, and accepts a write too:"
pg_ctl -D $R/primary -o "-p 5551 -k $R -c listen_addresses='' -c fsync=off" -l $R/primary2.log -w start >/dev/null
pq -c "insert into acc values (2, 'written on the OLD primary')"
echo "old primary says: $(pq -At -c "select id || ' ' || owner from acc where id = 2")"
echo "new primary says: $(rq -At -c "select id || ' ' || owner from acc where id = 2")"
echo "--- two writable nodes, two different truths for id 2: split brain"
repdown''',
                     e="Split brain, made on purpose. After the primary is stopped, the replica is promoted and becomes writable (`pg_is_in_recovery` is `f`). Then the old primary is started again: nothing tells it to stand down, so it accepts a write for the same key with a different value. Now **both nodes are writable and disagree about row 2**. Merging this by hand is painful and sometimes impossible. This is why failover tooling must fence the old primary and why a restarted old primary must be rebuilt as a replica, not simply started.",
                     annot=[("replica in recovery? f", "promotion succeeded: the replica now accepts writes"),
                            ("old primary says: 2 written on the OLD primary", "the old node still thinks it is in charge and accepted a write"),
                            ("new primary says: 2 written on the NEW primary", "the same key holds a different value on the other node: divergence")]),
            ]),
        ],
        scenario=dict(
            title="\"Design the failover for a primary database. What can go wrong?\"",
            ask="A reliability-flavoured database question. They want: detection, promotion, data loss, split brain and testing.",
            clarify=[("How much data can we afford to lose, and how long can we be unavailable?", "These are the recovery point and recovery time objectives: they decide synchronous or asynchronous, and manual or automatic failover.")],
            think=[("Set the targets.", "RPO zero means synchronous replication to at least one replica (in another zone); RPO of a few seconds allows asynchronous. RTO of seconds needs automation; minutes allow a runbook."),
                   ("Detection.", "Health checks from several vantage points with a timeout that tolerates blips; decisions through a consensus store (etcd, Consul) so exactly one node holds the leader lock."),
                   ("Promotion and fencing.", "Pick the replica with the most log; fence the old primary (STONITH, network or storage fencing, lease expiry) before promoting."),
                   ("Client redirection.", "A virtual IP, DNS with a short TTL, or a proxy/pooler that follows the leader; clients retry idempotent operations."),
                   ("Aftermath.", "Rebuild the old primary as a replica; reconcile any lost transactions if you can read them from its log; post-incident review."),
                   ("Test it.", "Practise failover regularly in production-like environments (game days); an untested failover is a hope, not a design.")],
            answer=["\"First the objectives: how much data can we lose and for how long can we be down. Zero loss means synchronous replication to at least one replica in another zone, at the cost of write latency and the risk that writes stop if that replica is unreachable; a few seconds of loss allows asynchronous.",
                    "For the failover itself I would not write a script: I would use a tool such as Patroni with etcd, where a leader lock held by exactly one node decides who is primary. On failure it fences the old primary, promotes the replica with the most log, and a proxy or virtual IP sends clients to the new primary, with clients retrying idempotent requests. The main risk is split brain, which fencing prevents. Afterwards the old primary is rebuilt as a replica. And I would rehearse the failover regularly, because an untested failover usually fails the first time it is needed.\""],
            follow=[("What is STONITH?", "Shoot The Other Node In The Head: forcibly power off or isolate the suspected-dead node so it cannot keep writing."),
                    ("Why do you need an odd number of voters?", "A majority quorum (2 of 3, 3 of 5) lets one side of a partition continue and the other stop; an even split can deadlock or split."),
                    ("What is the difference between RPO and RTO?", "Recovery point objective: how much data you can lose. Recovery time objective: how long you can be down.")],
            slips=["Promoting without fencing the old primary.", "Claiming zero data loss with asynchronous replication.", "Never rehearsing the failover."],
        ),
        quick=[
            ("What is the risk of asynchronous replication during failover?", "The replica may not have the last committed transactions, so they are lost."),
            ("What is the risk of synchronous replication?", "Commits wait for the replica: slower writes, and writes stop if it is unreachable."),
            ("What is split brain and how is it prevented?", "Two writable primaries with different data; prevent with fencing and a consensus-based leader election."),
        ],
        traps=[
            "Automatic failover on a single missed heartbeat: a network blip becomes an outage and possibly split brain.",
            "Restarting the old primary instead of rebuilding it.",
            "Treating a replica in the same rack or zone as a disaster-recovery copy.",
        ],
    ),
    dict(
        title="Partitioning: splitting a big table inside one database",
        tier="core",
        situation="The events table has two billion rows. Queries almost always ask for the last week, yet every query pays for the whole table's indexes, and deleting data older than a year takes hours and bloats everything. Partitioning splits the table by a key so most queries touch one small piece.",
        learn=["Range, list and hash partitioning", "Partition pruning in a real plan", "Dropping old data in an instant", "Partitioning versus sharding"],
        model=[
            "**Partitioning** splits one logical table into several physical **partitions** inside the same database, by a **key**: a date range (most common for events and logs), a list of values (country), or a hash (even spread). Queries and writes still address the one logical table; the database routes rows to the right partition, and when a query's `where` clause includes the partition key it **prunes** the partitions that cannot match, so it reads only the relevant ones. Indexes are per partition, so they are small and fit in memory.",
            "The best part is **data lifecycle**: removing a month of data becomes `drop table events_2025_01`, which is instant and does not leave bloat, instead of a huge `delete` followed by vacuum. Partitioning does **not** add machines: it is a single-node tool that makes big tables manageable. When one machine is no longer enough, the same idea is applied across machines: **sharding**, the next lesson.",
        ],
        analogy="A filing cabinet with one drawer per month: finding last week's papers means opening one drawer, and shredding last year's means emptying a drawer instead of picking pages out of one giant pile.",
        visual=[PART_VIZ],
        sim=None,
        walk=[
            ("Pick the key your queries filter on", "For time-series data it is almost always the timestamp: most queries want recent data."),
            ("Define partitions", "One per month or day for ranges, created ahead of time by a job."),
            ("Insert as usual", "Rows are routed to the right partition automatically."),
            ("Query with the key", "`where created_at >= ...` lets the planner prune partitions: the plan lists only the ones it will read."),
            ("Retire old data by dropping partitions", "Instant, no bloat; detach first if you want to archive it."),
        ],
        groups=[
            dict(title="Pruning and instant deletion, on real data", cmds=[
                dict(volatile=True, c=r'''. ~/rep/rig.sh; priup
pq <<'EOF'
create table events(id bigserial, at timestamptz not null, kind text) partition by range (at);
create table events_2026_08 partition of events for values from ('2026-08-01') to ('2026-09-01');
create table events_2026_09 partition of events for values from ('2026-09-01') to ('2026-10-01');
create table events_2026_10 partition of events for values from ('2026-10-01') to ('2026-11-01');
insert into events(at, kind) select timestamptz '2026-08-01' + make_interval(secs => random() * 91 * 86400), 'click' from generate_series(1, 300000);
analyze events;
EOF
echo "--- rows per partition:"
pq -At -c "select tableoid::regclass, count(*) from events group by 1 order by 1"
echo "--- a query for one week in October: which partitions does the plan touch?"
pq -At -c "explain (costs off) select count(*) from events where at >= '2026-10-20' and at < '2026-10-27'" | grep -E "Scan|Append"
echo "--- a query with no date filter touches all of them:"
pq -At -c "explain (costs off) select count(*) from events" | grep -E "Scan on"
pg_ctl -D $R/primary -m fast stop >/dev/null''',
                     e="Partitioning, visible in the plan. 300,000 rows were spread over three monthly partitions by the database itself. A query for one week in October is planned against **only `events_2026_10`**: the other two partitions are never opened (**partition pruning**). The same table queried without a date filter has to read every partition. The lesson for design: queries must include the partition key, or partitioning does nothing for reads.",
                     annot=[("events_2026_08|102275, events_2026_09|98805, events_2026_10|98920", "the rows were routed to the right partitions (August is a little larger because of the random dates)"),
                            ("Seq Scan on events_2026_10 events (only)", "pruning: the plan reads one partition for a one-week query"),
                            ("three Parallel Seq Scans without a date filter", "no key in the query means no pruning: every partition is read")]),
                dict(volatile=True, c=r'''. ~/rep/rig.sh; priup
pq -c "create table big_flat(id bigserial, at timestamptz not null, kind text)"
pq -c "insert into big_flat(at, kind) select timestamptz '2026-08-01' + make_interval(secs => random() * 91 * 86400), 'click' from generate_series(1, 300000)"
pq -c "create table big_part(id bigserial, at timestamptz not null, kind text) partition by range (at); create table big_part_old partition of big_part for values from ('2026-08-01') to ('2026-09-01'); create table big_part_new partition of big_part for values from ('2026-09-01') to ('2026-12-01');"
pq -c "insert into big_part(at, kind) select timestamptz '2026-08-01' + make_interval(secs => random() * 91 * 86400), 'click' from generate_series(1, 300000)"
t() { s=$(date +%s%N); pq -c "$1" >/dev/null; e=$(date +%s%N); echo "$2: $(( (e-s)/1000000 )) ms"; }
t "delete from big_flat where at < '2026-09-01'" "delete one month of rows from a plain table"
t "drop table big_part_old" "drop the one-month partition"
echo "--- the plain table still carries the dead rows until vacuum:"
pq -At -c "select 'dead tuples in the plain table: ' || n_dead_tup from pg_stat_user_tables where relname = 'big_flat'"
pg_ctl -D $R/primary -m fast stop >/dev/null''',
                     e="Why partitioning helps retention. Deleting a month of rows from a plain table has to find and mark about a third of the rows (and later vacuum them); dropping a partition just removes a file. The partition drop is several times faster even on this small table, the gap grows with table size, and it leaves nothing to clean up. For logs, events and time-series data this is usually the main reason to partition.",
                     annot=[("delete one month of rows from a plain table: tens of ms", "each row is individually marked deleted (and must be vacuumed later)"),
                            ("drop the one-month partition: a few ms (about 3 times faster here)", "one metadata operation: the whole file disappears (the gap widens with data size)"),
                            ("dead tuples in the plain table: ~100000", "the delete left garbage that vacuum still has to remove")]),
            ]),
        ],
        scenario=dict(
            title="\"Our events table has 2 billion rows. Queries are slow and retention deletes take hours. What do you do?\"",
            ask="They want you to distinguish partitioning from sharding and say when each applies.",
            clarify=[("What do queries filter on, and how long must data be kept?", "Date filters and a retention window make time partitioning ideal.")],
            think=[("Diagnose the pain.", "Big indexes that do not fit in memory, scans over old data, expensive deletes and vacuum."),
                   ("Partition by time.", "Range partitions by day or month on the timestamp; create future partitions ahead of time; indexes are per partition and small."),
                   ("Make queries use the key.", "Every hot query includes a time range so the planner prunes; check plans after the change."),
                   ("Handle retention.", "Detach and archive or drop old partitions: instant, no bloat."),
                   ("Say what it does not solve.", "It does not add capacity: one node still holds everything. If write throughput or total size exceeds one machine, shard across nodes (and each shard can itself be partitioned)."),
                   ("Operational care.", "Automate partition creation and a default partition for unexpected rows; monitor partition counts; avoid queries that scan all partitions.")],
            answer=["\"The symptoms point to a table that is too big to manage as one object: indexes that do not fit in memory, scans over old data, and deletes that take hours and leave bloat. I would partition by time, with a partition per day or month on the timestamp, and make sure the hot queries include a time range so the planner prunes down to one or two partitions. Retention becomes detaching or dropping an old partition, which is instant and leaves no bloat.",
                    "Partitioning is a single-node tool: it makes a large table manageable but does not add capacity. If one machine cannot take the writes or hold the data, I would shard across machines, and each shard can still be partitioned by time. I would automate creating future partitions and have a default partition to catch surprises.\""],
            follow=[("What is the difference between partitioning and sharding?", "Partitions live in one database on one machine; shards live on different machines, each a separate database."),
                    ("What partition key would you avoid?", "One that queries do not filter on (no pruning), or one that gives very uneven partitions."),
                    ("What about a unique constraint across partitions?", "In PostgreSQL a unique or primary key must include the partition key, so a global unique id needs care (include the timestamp or use a separate unique table).")],
            slips=["Using partitioning when the real problem is missing indexes.", "Partitioning on a column the queries never use.", "Forgetting to create the next partition before it is needed."],
        ),
        quick=[
            ("What does partition pruning do?", "Skips partitions that cannot contain matching rows, so a query reads only the relevant ones."),
            ("Why is dropping a partition better than deleting rows?", "It is instant and leaves no dead rows or bloat."),
            ("Does partitioning add write capacity?", "No: everything is still on one machine; sharding adds machines."),
        ],
        traps=[
            "Partitioning by a key that queries do not use: all cost, no benefit.",
            "Too many tiny partitions: planning time and metadata grow.",
            "Forgetting to create future partitions: inserts fail at midnight.",
        ],
    ),
]
