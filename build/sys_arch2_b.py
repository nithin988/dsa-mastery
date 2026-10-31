"""S24 architecture patterns: part B (lessons 3 to 5: event sourcing, CQRS, data ownership) and the module tail."""
import sysviz as v

ES_VIZ = v.figure(
    720, 226,
    [v.box(10, 70, 130, 56, "Command", "ink", "withdraw 30"),
     v.arrow(140, 98, 180, 98), v.box(180, 70, 130, 56, "Validate", "warn", "against current state"),
     v.arrow(310, 98, 350, 98), v.box(350, 70, 150, 56, "Event log (append only)", "ok", "Deposited 100, Withdrew 30 ..."),
     v.arrow(500, 98, 540, 98), v.box(540, 70, 170, 56, "Projections", "acc", "balance, statement, fraud view"),
     v.text(360, 168, "State is not stored: it is derived by replaying the events. The log is the source of truth.", "dg-s"),
     v.text(360, 194, "New question next year? Build a new projection from the same history.", "dg-s")],
    "Event sourcing", "Store what happened; compute what is true; rebuild any view from history")

CQRS_VIZ = v.figure(
    720, 240,
    [v.box(10, 20, 150, 52, "Command (write)", "ink", "place order"),
     v.arrow(160, 46, 200, 46), v.box(200, 20, 190, 52, "Write model", "ok", "normalised, consistent, transactional"),
     v.arrow(390, 46, 430, 46), v.box(430, 20, 150, 52, "Events / outbox", "warn", "order placed"),
     v.arrow(580, 46, 610, 46), v.box(610, 20, 100, 52, "Projector", "acc", ""),
     v.arrow(660, 72, 660, 120), v.box(430, 120, 280, 52, "Read model", "ok", "denormalised, shaped for the screen"),
     v.box(10, 120, 150, 52, "Query (read)", "ink", "my orders page"),
     v.arrow(430, 146, 160, 146),
     v.text(360, 206, "The read model is updated after the write: it is eventually consistent, and that gap must be designed for.", "dg-s")],
    "CQRS", "Separate the model that accepts changes from the model that answers questions")

LESSONS_B = [
    dict(
        title="Event-driven design and event sourcing: store what happened",
        tier="hot",
        situation="An account table shows a balance of 70. Why? When did it change? What was it last Tuesday? Auditors, fraud analysts and bug hunters all ask questions that a table of current state cannot answer, because it forgot the history. Another approach stores the history and derives the state.",
        learn=["Events as facts, versus current-state tables", "Rebuilding state by replaying events", "Snapshots, projections and time travel", "What event sourcing costs"],
        model=[
            "In a **CRUD** design the database holds only the **current state**; every update overwrites the past. In an **event-driven** design components communicate by publishing **events** (facts that happened: `OrderPlaced`, `PaymentSettled`) which others react to, decoupling the producer from its consumers. **Event sourcing** goes further: the **append-only log of events is the source of truth**, and any current state is **derived** by replaying (folding) the events. You get a complete audit trail for free, the ability to answer \"what was the state at time T?\", and the power to **build new views from old history** (a new projection for a new question) or to **fix a bug and replay**.",
            "The costs are real: the model is unfamiliar; queries on current state need **projections** (read models) that are eventually consistent; replaying a long history is slow, so you keep periodic **snapshots**; events live **forever**, so their **schema must evolve** (upcasting old versions, never editing history); correcting a mistake means appending a **compensating event**, not editing; and deleting personal data under privacy law needs a plan (crypto-shredding or separate personal data store). Use event sourcing where history **is** the business (finance, ledgers, bookings, audit-heavy domains) and plain events or CRUD elsewhere.",
        ],
        analogy="A bank statement versus a balance sticker. The sticker says 70. The statement lists every deposit and withdrawal, so you can prove the 70, find the mistake, or work out what the balance was on any day, and the balance is simply the statement added up.",
        visual=[ES_VIZ],
        sim=None,
        walk=[
            ("A command arrives", "\"Withdraw 30\" is checked against the current state (built from events)."),
            ("If valid, append an event", "`Withdrew 30` is added to the log. Nothing is ever updated or deleted."),
            ("Projections update", "A balance view, a statement view and a fraud view each consume the events."),
            ("Replay for new questions", "A new projection can be built from the full history at any time."),
            ("Snapshots keep replay fast", "Periodically store the folded state and replay only events after it."),
        ],
        groups=[
            dict(title="Rebuild state from events, time travel and fixing a bug by replaying", cmds=[
                dict(c=r'''python3 - <<'EOF'
# An account as a log of events. State is never stored: it is computed by folding the events.
events = [
    ('Opened',    {'owner': 'asha'}),
    ('Deposited', {'amount': 100}),
    ('Withdrew',  {'amount': 30}),
    ('Deposited', {'amount': 50}),
    ('Withdrew',  {'amount': 200}),          # a withdrawal the business rule must reject (insufficient funds): recorded as a Rejected fact
]
def apply(state, ev):
    kind, d = ev
    if kind == 'Opened':    return {'owner': d['owner'], 'balance': 0, 'rejected': 0}
    if kind == 'Deposited': return dict(state, balance=state['balance'] + d['amount'])
    if kind == 'Withdrew':
        if d['amount'] > state['balance']: return dict(state, rejected=state['rejected'] + 1)   # the rule lives in the fold
        return dict(state, balance=state['balance'] - d['amount'])
    return state
def fold(evs, upto=None):
    s = None
    for ev in evs[:upto]: s = apply(s, ev)
    return s
print('current state:                ', fold(events))
print('state after the 3rd event:    ', fold(events, 3), '  <- time travel: what was true then')
print('state after the 4th event:    ', fold(events, 4))
print()
# A new requirement arrives next year: "how much was ever withdrawn?" The old system never stored it. Replay builds it:
withdrawn = sum(d['amount'] for k, d in events if k == 'Withdrew' and d['amount'] <= 100)
print('new projection built from old history: total successfully withdrawn = %d' % withdrawn)
# A bug fix: suppose a fee of 1 should apply on every successful withdrawal. Replay with the corrected rule:
def apply_fixed(state, ev):
    s = apply(state, ev)
    if ev[0] == 'Withdrew' and ev[1]['amount'] <= state['balance']: s = dict(s, balance=s['balance'] - 1)
    return s
s = None
for ev in events: s = apply_fixed(s, ev)
print('after replaying with the fee rule: ', s, ' <- the history was not edited; only the interpretation changed')
EOF''',
                     e="Event sourcing in thirty lines. The state is never stored: the current balance of 120 is the result of folding five events. Stopping the fold early gives the state at any earlier point (**time travel**), so an auditor can ask what was true after the third event. A requirement that arrives later (\"how much was ever withdrawn?\") is answered by a **new projection over the old events**, something a table of current balances could never do. And a **rule change** is applied by replaying the same history through the corrected logic: the facts stay untouched, only their interpretation changes.",
                     annot=[("current state: balance 120, rejected 1", "the result of folding all five events"),
                            ("state after the 3rd event: balance 70", "time travel: stop the fold earlier"),
                            ("total successfully withdrawn = 30", "a brand new question answered from old history"),
                            ("after replaying with the fee rule: balance 119", "same events, corrected rule (a fee of 1 on the one successful withdrawal): history not edited")]),
                dict(volatile=True, c=r'''python3 - <<'EOF'
# Snapshots: replaying a long history is slow, so keep a periodic snapshot and replay only what came after it.
import time
events = [('Deposited', 1) if i % 3 else ('Withdrew', 1) for i in range(1_000_000)]
def fold(evs, start=0):
    bal = start
    for k, a in evs: bal += a if k == 'Deposited' else -a
    return bal
t = time.perf_counter(); full = fold(events); full_ms = (time.perf_counter() - t) * 1000
snap_at = 990_000; snap = fold(events[:snap_at])                 # a snapshot taken earlier
t = time.perf_counter(); fast = fold(events[snap_at:], snap); snap_ms = (time.perf_counter() - t) * 1000
print('replay all 1,000,000 events:            balance %d in %6.0f ms' % (full, full_ms))
print('snapshot + replay the last 10,000:      balance %d in %6.0f ms   (same answer: %s)' % (fast, snap_ms, full == fast))
EOF''',
                     e="Why snapshots exist. Folding a million events takes real time (and a busy account may have far more); folding the last ten thousand on top of a stored snapshot gives the **same balance** in a fraction of the time. A snapshot is only a cache: it can be thrown away and rebuilt from the log at any time, because the log remains the source of truth.",
                     annot=[("replay all 1,000,000 events: tens of ms here", "the cost grows with the history (a busy account has far more events)"),
                            ("snapshot + replay the last 10,000: about a hundredth of the time (same answer: True)", "a snapshot turns a long replay into a short one")]),
            ]),
        ],
        scenario=dict(
            title="\"When would you use event sourcing, and what are the problems with it?\"",
            ask="A pattern-judgement question. They want a clear use case and an honest list of costs.",
            clarify=[("Is history itself valuable to the business: audit, regulation, \"as of\" queries, undo?", "If history is the product (banking, ledgers, bookings), event sourcing fits; if only the current state matters, it is overkill.")],
            think=[("Define it.", "The append-only event log is the source of truth; current state is derived by replaying; views are projections."),
                   ("Give the benefits.", "Complete audit trail by construction; time travel; new read models from old data; easy debugging (replay what happened); natural integration through events; scales writes (append-only)."),
                   ("Give the costs.", "Eventual consistency of read models; event schema evolution forever (versioning, upcasting); replay time (snapshots); learning curve; harder ad hoc queries; privacy deletion (GDPR) needs crypto-shredding or segregated personal data; no editing of history, only compensating events."),
                   ("Say where it fits.", "Ledgers, payments, inventory movements, order lifecycles, collaborative editing, anything with legal audit needs. Not simple CRUD admin screens."),
                   ("Say how to start small.", "Event-sourced aggregates only for the core domain; elsewhere CRUD plus published events (outbox); do not build your own event store if a database or product exists."),
                   ("Distinguish from event-driven.", "Event-driven architecture uses events to communicate between components; event sourcing uses events as storage. You can have either without the other.")],
            answer=["\"Event sourcing stores an append-only log of events as the source of truth and derives the current state by replaying them, with projections for the views. I would use it where history is the business: payments, ledgers, orders and bookings, anything with audit or as-of requirements, because it gives a complete audit trail, time travel, the ability to build new views from old history, and easy debugging by replay.",
                    "The costs are real: read models are eventually consistent, event schemas must evolve forever through versioning and upcasting, long histories need snapshots, ad hoc queries are harder, corrections are compensating events rather than edits, and privacy deletion needs a plan such as crypto-shredding. So I would apply it only to the core domain, use plain CRUD with an outbox elsewhere, and keep in mind that event-driven communication and event sourcing are different things: you can have either one without the other.\""],
            follow=[("How do you evolve event schemas?", "Version events, keep old versions readable, and upcast them to the current shape when loading; never edit stored events; prefer additive changes."),
                    ("How do you handle GDPR deletion?", "Keep personal data out of events (reference an id) or encrypt it with a per-person key that you delete (crypto-shredding), so the history stays but the data becomes unreadable."),
                    ("What is the difference from an audit table?", "An audit log is a side record of changes to state that remains the source of truth; in event sourcing the events are the source of truth and the state is derived.")],
            slips=["Using event sourcing for ordinary CRUD.", "Forgetting schema evolution and privacy deletion.", "Confusing event-driven with event sourcing."],
        ),
        quick=[
            ("What is the source of truth in event sourcing?", "The append-only log of events; current state is derived by replaying it."),
            ("What is a snapshot for?", "A stored folded state so that only later events need to be replayed: a cache that can be rebuilt."),
            ("How do you correct a mistake in event sourcing?", "Append a compensating event; never edit stored events."),
        ],
        traps=[
            "Putting personal data in immutable events with no deletion plan.",
            "Treating projections as always up to date: they lag the log.",
            "Event schemas designed without versioning: the first change becomes a migration crisis.",
        ],
    ),
    dict(
        title="CQRS and read models: different shapes for writing and reading",
        tier="hot",
        situation="The \"my orders\" page needs a join over five tables and an aggregate, runs on every page view, and slows the system that must also accept writes. Writing wants normalised, consistent data; reading wants one pre-shaped row. They pull the same schema in opposite directions.",
        learn=["Commands versus queries", "A write model and a read model, built from events", "The consistency gap between them", "When CQRS is overkill"],
        model=[
            "**CQRS** (Command Query Responsibility Segregation) separates the model that handles **commands** (changes: validated, normalised, transactional) from the model that answers **queries** (shaped exactly for the screen, often **denormalised** and pre-aggregated). A **projector** updates the read model from the stream of changes (events or an outbox). Benefits: reads can be extremely fast and simple, read and write sides **scale independently**, each is optimised for its job, and you can build **several read models** (a search index, a summary table, a cache) from the same changes. It pairs naturally with event sourcing but does not require it.",
            "The cost is the **consistency gap**: the read model is updated **after** the write, so a user can write and then read stale data (**eventual consistency**). Design for it: show the user their own change optimistically, read their own writes from the write side for a moment, or accept a few hundred milliseconds of lag. You also now have two models and a pipeline to build, monitor and repair (a projector that falls behind or breaks needs a **rebuild** from history). Use CQRS when read and write needs differ sharply or read load dwarfs writes; for ordinary screens a good index, a view or a cache is simpler.",
        ],
        analogy="A restaurant's order tickets (written in the kitchen's shorthand for cooking) and the printed bill (a different shape, assembled from the tickets for the customer). Updating the bill takes a moment after the ticket; nobody tries to cook from the bill.",
        visual=[CQRS_VIZ],
        sim=None,
        walk=[
            ("Commands change the write model", "Normalised tables, constraints, transactions: correctness first."),
            ("Each change emits an event", "Through an outbox in the same transaction."),
            ("The projector updates the read model", "One pre-shaped row per order, already joined and totalled."),
            ("Queries read only the read model", "A single indexed lookup: no joins on the hot path."),
            ("Handle the gap and the rebuild", "Show the user's own writes immediately; rebuild the read model from history if it breaks."),
        ],
        groups=[
            dict(title="A write model, a read model and the gap between them (PostgreSQL)", cmds=[
                dict(volatile=True, c=r'''. ~/arch/rig.sh; pgup
pq <<'EOF'
select setseed(0.3) as s \gset
create table customers(id int primary key, name text);
create table orders(id serial primary key, customer_id int references customers, created timestamptz default now());
create table order_items(order_id int references orders, sku int, qty int, price numeric(8,2));
create index on order_items(order_id); create index on orders(customer_id);
insert into customers select g, 'customer ' || g from generate_series(1, 2000) g;
insert into orders(customer_id) select 1 + (random()*1999)::int from generate_series(1, 100000);
insert into order_items select o.id, (random()*500)::int, 1 + (random()*3)::int, round((random()*90 + 5)::numeric, 2) from orders o, generate_series(1, 4);
-- the read model: one pre-shaped row per customer, built by a projector
create table customer_order_summary(customer_id int primary key, name text, order_count int, total numeric(12,2));
insert into customer_order_summary
  select c.id, c.name, count(distinct o.id), sum(i.qty * i.price) from customers c join orders o on o.customer_id = c.id join order_items i on i.order_id = o.id group by c.id, c.name;
analyze;
EOF
echo "--- the screen needs: name, order count and total for customer 77"
echo "write model (join + aggregate over 400,000 rows):"
pq -At -c "explain (analyze, costs off, timing off, summary off) select c.name, count(distinct o.id), sum(i.qty*i.price) from customers c join orders o on o.customer_id=c.id join order_items i on i.order_id=o.id where c.id = 77 group by c.name" | grep -E "Scan|Join|Nested" | head -4
t() { echo "  $2: $(pq -At -c "explain (analyze, costs off) $1" | grep 'Execution Time')"; }
t "select c.name, count(distinct o.id), sum(i.qty*i.price) from customers c join orders o on o.customer_id=c.id join order_items i on i.order_id=o.id where c.id = 77 group by c.name" "join on the write model"
t "select name, order_count, total from customer_order_summary where customer_id = 77" "read model lookup"
pgdown''',
                     e="The same answer from two shapes of data. The write model is correctly normalised, so the \"my summary\" screen needs a join across customers, orders and 400,000 order items and an aggregate. The **read model** stores exactly what the screen shows, one row per customer, so the query is a single primary-key lookup. (Even here the join is fast thanks to indexes; at real scale, or with more tables, the gap grows, and the read model can live on another machine altogether.) The price is that someone has to keep it up to date, which is the next experiment.",
                     annot=[("Index Scan ... Nested Loop ... (the write-model plan)", "several indexes and joins to assemble one answer"),
                            ("join on the write model: Execution Time: 1.6 ms", "work done on every page view: several index lookups and an aggregate"),
                            ("read model lookup: Execution Time: 0.03 ms", "a single primary-key lookup of a pre-shaped row: about 50 times less work, and the gap grows with data volume")]),
                dict(volatile=True, c=r'''. ~/arch/rig.sh; pgup
pq <<'EOF'
create table change_log(id serial primary key, customer_id int, amount numeric(12,2), applied boolean default false);
EOF
echo "before:  read model says: $(pq -At -c 'select order_count || chr(32) || total from customer_order_summary where customer_id = 77')"
echo "--- a new order for customer 77 worth 250 is written (write model + change_log in one transaction)"
pq -c "begin; insert into orders(customer_id) values (77); insert into change_log(customer_id, amount) values (77, 250); commit;"
echo "right after the write:  read model says: $(pq -At -c 'select order_count || chr(32) || total from customer_order_summary where customer_id = 77')   <- stale: the projector has not run yet"
echo "--- the projector runs (every few hundred milliseconds in real systems):"
pq -c "with c as (update change_log set applied = true where not applied returning customer_id, amount) update customer_order_summary s set order_count = order_count + 1, total = total + c.amount from c where s.customer_id = c.customer_id"
echo "after the projector:   read model says: $(pq -At -c 'select order_count || chr(32) || total from customer_order_summary where customer_id = 77')"
echo "--- rebuild: if the projector had a bug, delete the read model and rebuild it from the write model"
pq -c "truncate customer_order_summary; insert into customer_order_summary select c.id, c.name, count(distinct o.id), sum(i.qty*i.price) from customers c join orders o on o.customer_id=c.id left join order_items i on i.order_id=o.id group by c.id, c.name"
echo "after the rebuild (note the new order has no items yet, so its 250 is not in this total):  $(pq -At -c 'select order_count || chr(32) || total from customer_order_summary where customer_id = 77')"
pgdown''',
                     e="The consistency gap, made visible. The write and the change record commit together. Immediately afterwards the **read model still shows the old numbers**: until the projector applies the change, a user who just placed an order would not see it on their summary page. After the projector runs, the read model catches up. The last step shows the safety net of CQRS: a broken read model can be **thrown away and rebuilt** from the write model (here the rebuilt total differs by 250 because this toy order has no item rows; in a real system the rebuild reproduces what the projector should have produced).",
                     annot=[("before: read model says: N orders, total T", "the starting state"),
                            ("right after the write: read model says: the same numbers <- stale", "the read model lags the write: eventual consistency"),
                            ("after the projector: N+1 orders, T+250", "the projector applied the change"),
                            ("after the rebuild: the order count includes the new order, the total reflects the item rows", "a read model can be rebuilt from the write side at any time")]),
            ]),
        ],
        scenario=dict(
            title="\"Our order history page is slow and is hurting checkout. Would you use CQRS? How would you keep the data consistent?\"",
            ask="A pragmatic pattern question. A good answer tries cheaper fixes first and handles the consistency gap explicitly.",
            clarify=[("How slow, and what does the query do? What is the read-to-write ratio? Is slightly stale data acceptable?", "A missing index or an unbounded query is cheaper to fix than a new architecture.")],
            think=[("Try the cheap fixes first.", "Look at the query plan, add indexes, paginate, cache, or a database view or materialised view refreshed periodically."),
                   ("Introduce a read model if that is not enough.", "A denormalised table or search index shaped for the page, updated by events from the write side; reads and writes then scale independently."),
                   ("Pipeline.", "Write transaction includes an outbox event; a projector consumes it and updates the read model idempotently (by event id, tolerant of duplicates and replays)."),
                   ("Handle the consistency gap.", "Show the user's own new order optimistically in the UI; for a short window read their own recent writes from the write side; accept sub-second lag elsewhere; show \"updating\" if needed."),
                   ("Operate it.", "Monitor projector lag and failures; a rebuild procedure from the write model or event history; version the read model schema."),
                   ("Say when not to.", "When reads and writes have similar shapes, volume is modest, or strong read-after-write consistency is required everywhere: CQRS adds a pipeline and a consistency problem.")],
            answer=["\"First I would look for cheaper fixes: the query plan, indexes, pagination, a cache or a materialised view. If the page still needs a shape the normalised write model cannot serve cheaply, I would add a read model: a denormalised table or search index containing exactly what the page shows, updated by a projector that consumes events from an outbox written in the same transaction as the order.",
                    "The projector must be idempotent so duplicates and replays are harmless. Because the read model lags the write, I would show the user's own new order optimistically or read their recent writes from the write side for a short time, and accept sub-second lag for everyone else. I would monitor projector lag and have a rebuild procedure from the write model. And I would not use CQRS if reads and writes have similar shapes, volume is modest, or strong read-after-write consistency is needed everywhere.\""],
            follow=[("How does CQRS relate to event sourcing?", "They combine well (events feed projections) but are independent: you can use CQRS with ordinary tables and an outbox."),
                    ("What if the projector falls behind?", "Alert on lag, scale consumers, and design the UI to tolerate it; a rebuild or catch-up job restores correctness."),
                    ("Can you have multiple read models?", "Yes: a summary table, a search index, a cache, an analytics store, each built from the same events for its own query shape.")],
            slips=["Using CQRS before trying an index or a view.", "Ignoring the consistency gap.", "A projector that is not idempotent."],
        ),
        quick=[
            ("What does CQRS separate?", "The model for commands (writes) from the model for queries (reads)."),
            ("What is the main cost of a CQRS read model?", "Eventual consistency: the read model lags the write side."),
            ("How do you recover a broken read model?", "Rebuild it from the write model or the event history."),
        ],
        traps=[
            "A read model that is updated outside the transaction with no outbox: updates can be lost.",
            "Telling users \"saved\" and then showing them stale data with no explanation.",
            "Projectors that are not idempotent: replays double-count.",
        ],
    ),
    dict(
        title="Service boundaries and data ownership: the shared database trap",
        tier="hot",
        situation="Two services read the same table. One team renames a column and the other service breaks in production. Or services call each other in a ring and nobody can deploy without everyone. Where you draw boundaries, and who owns which data, decides whether services are independent or just far apart.",
        learn=["Why each service must own its data", "Bounded contexts: drawing boundaries around meaning, not tables", "API composition versus a shared database", "Smells of a distributed monolith"],
        model=[
            "The test of a service boundary is **independence**: can the team change its internals, its schema and its deployment without coordinating with anyone? A **shared database** destroys that: every consumer is coupled to the schema, a migration needs every consumer to change, and one team's slow query slows everyone. The rule is **one service owns each piece of data and exposes it only through an API or events**; other services keep **their own copies** of what they need (a read-optimised copy updated from events), or **compose** answers by calling the owner. The price is that **joins across services** disappear: you assemble data in an **API composition** layer or BFF, or from local copies.",
            "Draw boundaries around **business capabilities** and **meaning** (a **bounded context** in domain-driven design): \"customer\" means something different to billing, shipping and marketing, and each context has its own model, so forcing one shared `Customer` table creates coupling and constant compromise. Watch for the **distributed monolith** smells: a change needing several services to deploy together, services sharing a database or library of domain types, long synchronous call chains, circular dependencies, and one team owning many tiny services nobody understands. **Conway's law** (systems mirror the communication structure of the organisation) means boundaries should follow team boundaries, not the other way round.",
        ],
        analogy="Departments in a company that each keep their own files and answer requests by phone, instead of everyone rummaging in one shared filing cabinet. When accounting reorganises its folders nobody else notices, because everyone goes through the front desk.",
        sim=None,
        walk=[
            ("Find the business capabilities", "Orders, payments, catalogue, shipping: each with its own vocabulary."),
            ("Give each one its own data store", "Only its service reads or writes it directly."),
            ("Expose data through contracts", "Versioned APIs for queries, events for changes."),
            ("Keep local copies where needed", "A read-only copy of the few fields a service needs, updated from events."),
            ("Check for smells", "Joint deployments, shared tables, call cycles: signs the boundaries are wrong."),
        ],
        groups=[
            dict(title="A schema change breaks a service that reaches into another's tables", cmds=[
                dict(volatile=True, c=r'''. ~/arch/rig.sh; pgup
pq <<'EOF'
create table orders_svc_orders(id serial primary key, customer text, status text, total int);
insert into orders_svc_orders(customer, status, total) values ('asha', 'paid', 120), ('ben', 'new', 80);
EOF
echo "--- the shipping team reads the orders team's table directly (a shared database):"
shipping_query="select id, customer from orders_svc_orders where status = 'paid'"
pq -At -c "$shipping_query"
echo "--- the orders team improves its schema (rename status -> state) and deploys; they never heard of the shipping query:"
pq -c "alter table orders_svc_orders rename column status to state"
echo "--- production, next morning, shipping runs its query:"
pq -At -c "$shipping_query" 2>&1 | head -2
echo "--- the same change behind an API: the orders service adapts its own response, no consumer breaks"
cat > $AR/orders_api.py <<'EOF'
# The orders service's public contract: a stable response shape that does NOT depend on its table layout.
def orders_api(rows):
    return [{'id': r[0], 'customer': r[1], 'status': r[2]} for r in rows if r[2] == 'paid']      # 'status' stays in the contract
EOF
rows=$(pq -At -F, -c "select id, customer, state from orders_svc_orders")
python3 - "$rows" <<'EOF'
import sys; sys.path.insert(0, '.')
import os; sys.path.insert(0, os.path.expanduser('~/arch'))
from orders_api import orders_api
rows = [tuple(int(x) if x.isdigit() else x for x in line.split(',')) for line in sys.argv[1].splitlines()]
print('API response after the schema change:', orders_api(rows))
EOF
pgdown''',
                     e="The shared-database trap, reproduced. Shipping queries the orders table directly. The orders team renames a column for good internal reasons and deploys: **shipping's query now fails in production** (`column \"status\" does not exist`) even though neither team did anything unreasonable. The coupling was invisible until it broke. When consumers go through the orders service's **API**, the service can rename its columns freely and keep the contract (`status`) stable: the schema is an implementation detail, not a public interface.",
                     annot=[("1|asha", "shipping's query works while the schema is unchanged"),
                            ("ERROR: column \"status\" does not exist", "the orders team renamed it: a consumer outside the team broke"),
                            ("API response after the schema change: [{'id': 1, 'customer': 'asha', 'status': 'paid'}]", "the contract is stable even though the table changed")]),
                dict(c=r'''python3 - <<'EOF'
# Smell test: given which services call which, find cycles and the length of the longest synchronous chain.
calls = {'web': ['api'], 'api': ['orders', 'users', 'catalog'], 'orders': ['payments', 'inventory'], 'payments': ['ledger'],
         'inventory': ['orders'], 'catalog': ['search'], 'users': [], 'ledger': [], 'search': []}
def find_cycle(graph):
    state, stack = {}, []
    def dfs(n):
        state[n] = 1; stack.append(n)
        for m in graph[n]:
            if state.get(m) == 1: return stack[stack.index(m):] + [m]
            if m not in state:
                c = dfs(m)
                if c: return c
        stack.pop(); state[n] = 2
    for n in graph:
        if n not in state:
            c = dfs(n)
            if c: return c
def longest(graph, n, seen=()):
    return 1 + max([longest(graph, m, seen + (n,)) for m in graph[n] if m not in seen] or [0])
print('circular dependency:', ' -> '.join(find_cycle(calls) or ['none']))
print('longest synchronous chain from web:', longest(calls, 'web'), 'services deep')
print('availability of that chain at 99.9%% each: %.2f%%' % (100 * 0.999 ** longest(calls, 'web')))
EOF''',
                     e="Two cheap checks on a dependency map. A **circular dependency** (`orders -> inventory -> orders`) means neither service can be deployed, tested or reasoned about alone: a sign the boundary is in the wrong place (merge them, or break the cycle with an event). The **longest synchronous chain** matters for both latency (the sum of every hop) and availability (the product); five deep at 99.9 percent each is already 99.5 percent. These two numbers belong in every architecture review.",
                     annot=[("circular dependency: orders -> inventory -> orders", "two services that call each other cannot evolve independently"),
                            ("longest synchronous chain from web: 5 services deep", "web, api, orders, payments, ledger"),
                            ("availability of that chain at 99.9% each: 99.50%", "0.999^5: deeper chains cost reliability")]),
            ]),
        ],
        scenario=dict(
            title="\"Two services need the same customer data. How do you share it without coupling them?\"",
            ask="The data-ownership question every microservices interview contains. They want a clear stance and the alternatives.",
            clarify=[("Which fields do they need, how fresh must they be, and how often do they read?", "A few fields read often and tolerating some staleness can be copied; fields that must be exactly current should be fetched.")],
            think=[("State the rule.", "One service owns the customer data and is the only writer; others do not read its database."),
                   ("Option 1: query the owner.", "A synchronous API call (with timeouts, caching and a fallback). Simple and always current; adds latency and a runtime dependency."),
                   ("Option 2: keep a local copy.", "The owner publishes `CustomerChanged` events; the consumer stores the few fields it needs in its own store. Fast and resilient to the owner's outage; eventually consistent; must handle replays and ordering."),
                   ("Option 3: pass what is needed.", "Include the needed fields in the request or event itself (the order carries the customer's shipping address as of purchase time)."),
                   ("Reject the shared table.", "Schema coupling, joint deployments, hidden dependencies, one team's load on another's database."),
                   ("Choose by freshness and failure behaviour.", "Display data: local copy. Money or consent: ask the owner. Historical records: snapshot into the record."),
                   ("Operate it.", "Version the events and APIs, monitor consumer lag, and provide a backfill/replay path for new consumers.")],
            answer=["\"One service owns the customer data and is the only one that writes it; nobody else reads its database, because a shared schema couples every consumer to every migration. Other services get what they need in one of three ways. They can call the owner's API, which is always current but adds latency and a runtime dependency. They can keep a local copy of just the fields they need, fed by customer-changed events: fast and resilient, but eventually consistent, so the consumer must handle replays and ordering. Or the needed values can be carried in the request or event itself, like the shipping address copied into the order at purchase time, which is also correct for history.",
                    "I choose by freshness and failure behaviour: display data from a local copy, anything involving money or consent from the owner, and historical records as snapshots. I version the APIs and events, monitor consumer lag, and give new consumers a replay or backfill path.\""],
            follow=[("What if the consumer needs a join across both services' data?", "Do the join in an API composition layer or BFF, or build a read model (CQRS) fed from both services' events; avoid cross-database joins."),
                    ("How do you keep a local copy correct?", "Idempotent event handlers, version or sequence checks to ignore stale events, periodic reconciliation against the owner, and a backfill procedure."),
                    ("Is a shared library of domain types OK?", "A library of shared domain models couples deployments (everyone must upgrade together); share contracts (schemas), not behaviour.")],
            slips=["Letting services read each other's tables \"for speed\".", "Local copies with no plan for ordering or replay.", "Sharing a domain model library across services."],
        ),
        quick=[
            ("Why is a shared database a bad service boundary?", "Every consumer is coupled to the schema, so changes need coordinated deployments and break silently."),
            ("What is a bounded context?", "A boundary within which a model and its vocabulary are consistent: the same word can mean different things in different contexts."),
            ("Name two smells of a distributed monolith.", "Services that must be deployed together, and circular or very deep synchronous call chains (also shared databases)."),
        ],
        traps=[
            "Splitting services by technical layer (UI service, data service) instead of by capability.",
            "Reading another service's tables because \"the API is slow\".",
            "Assuming a local copy of data is current.",
        ],
    ),
]

TAIL = dict(
    cases=[],
    cheat=[
        ["monolith", "one deployable: simple, function calls, one transaction"],
        ["modular monolith", "strict internal modules each owning tables: most benefits, little tax"],
        ["microservices tax", "network calls, no shared transaction, tracing, deployment, on-call"],
        ["availability in series", "multiply: 5 x 99.9% = 99.5%; add fallbacks and redundancy"],
        ["when to split", "independent deploys, scaling, team boundaries, security: concrete reasons"],
        ["distributed monolith", "services deployed together, shared database, long sync chains"],
        ["strangler fig", "router in front; move one capability at a time; rollback is a route"],
        ["shadow traffic", "copy real requests to the new system and compare, unseen by users"],
        ["percentage rollout", "1, 10, 50, 100 percent with fallback and comparison"],
        ["event-driven", "components communicate by publishing facts"],
        ["event sourcing", "the append-only event log is the source of truth; state is a fold"],
        ["snapshot", "stored folded state so replay starts late"],
        ["event schema evolution", "version, upcast, never edit history; compensating events"],
        ["CQRS", "separate write model and read model; projector between them"],
        ["consistency gap", "read model lags the write: optimistic UI, read own writes"],
        ["rebuild", "a read model can be rebuilt from the write side or history"],
        ["data ownership", "one service owns and writes each piece of data"],
        ["shared database", "couples schemas and deployments: avoid"],
        ["API composition / local copy", "query the owner / keep a copy fed by events"],
        ["Conway's law", "architecture mirrors team structure: align boundaries with teams"],
    ],
    interview_intro="Architecture answers are judged on reasoning from problems and on honest costs: say what hurts, what the pattern fixes, what it makes harder, and how you would adopt it in small, reversible steps. The worked scenarios in each lesson are the models to practise with.",
    interview=[
        dict(q="We have a monolith and 60 engineers. Should we move to microservices?",
             a=["Diagnose first: slow releases from tests or tangled code are not fixed by services; independent deployment, scaling and team autonomy are.", "Improve and modularise the monolith first; extract services only for concrete reasons, along seams with clean data ownership, with a strangler approach.", "Count the costs: latency, failures, no shared transactions, operations, availability in series; measure deployment frequency, lead time and incidents before and after."],
             follow=["What is a distributed monolith?", "What platform do you need first?"], mistakes=["Because big companies do it.", "Ignoring operational cost."],
             angle="Reported by candidates as a common architecture discussion prompt at large companies; not official."),
        dict(q="How do you migrate a critical legacy system with no downtime?",
             a=["Strangler pattern: a router or facade in front; build one capability at a time.", "Shadow traffic to compare, percentage rollout with fallback, one-line rollback; migrate data with CDC or dual writes and continuous comparison before switching authority.", "Decide the point of no return explicitly; retire the old only when traffic and dependencies are zero."],
             follow=["What is shadow traffic?", "How do you keep data in sync?"], mistakes=["A big-bang rewrite.", "No rollback."],
             angle="Amazon-style: expect \"what could go wrong at each step and how do you detect it?\"; reported by candidates, not official."),
        dict(q="When would you use event sourcing, and what are the problems?",
             a=["The log of events is the source of truth; state is derived; use where history is the business (ledgers, bookings, audit).", "Benefits: audit, time travel, new projections from old history, replay for bug fixes.", "Costs: eventual consistency, schema evolution forever, snapshots, privacy deletion, compensating events; event-driven is not the same as event sourcing."],
             follow=["How do you evolve event schemas?", "GDPR deletion?"], mistakes=["Event sourcing for plain CRUD."]),
        dict(q="The order history page is slow and hurts checkout. Would you use CQRS?",
             a=["Cheaper fixes first: plan, indexes, pagination, cache, materialised view.", "If needed, a read model shaped for the page, updated by an idempotent projector from outbox events.", "Handle the consistency gap (optimistic UI, read own writes), monitor lag, rebuild from the write model; skip CQRS when shapes and volumes are similar."],
             follow=["CQRS versus event sourcing?", "What if the projector falls behind?"], mistakes=["CQRS before an index.", "Ignoring the gap."]),
        dict(q="Two services need the same customer data. How do you share it without coupling?",
             a=["One owner and only writer; no shared tables.", "Query the owner (current, adds latency and dependency), keep a local copy fed by events (fast, resilient, eventually consistent), or pass the needed values in the request or event (snapshots for history).", "Choose by freshness and failure behaviour; version contracts; monitor lag; provide replay."],
             follow=["How do you do joins across services?", "Is a shared domain library OK?"], mistakes=["Shared tables.", "Assuming local copies are current."],
             angle="Google-style: candidates commonly report follow-ups on consistency and evolution of contracts; reported by candidates, not official."),
    ],
    selftest=[
        ("What does a network call add compared with a function call?", "Latency, serialisation and new failure modes."),
        ("What is the availability of 5 services in series at 99.9% each?", "About 99.5%."),
        ("What is a modular monolith?", "One deployable with enforced internal module boundaries and data ownership."),
        ("What does the strangler pattern use to move traffic?", "A routing layer in front of old and new systems."),
        ("What is shadow traffic?", "Copies of real requests sent to the new system to compare answers without affecting users."),
        ("What is the source of truth in event sourcing?", "The append-only event log."),
        ("What is a snapshot in event sourcing?", "A stored folded state so replay can start later."),
        ("How do you correct a mistake in an event-sourced system?", "Append a compensating event."),
        ("What does CQRS separate?", "The command (write) model and the query (read) model."),
        ("What is the main cost of a CQRS read model?", "Eventual consistency: it lags the write side."),
        ("Why is a shared database a bad boundary?", "It couples every consumer to the schema and to each other's deployments."),
        ("What is a bounded context?", "A boundary within which a model and vocabulary are consistent."),
        ("What is Conway's law?", "A system's design mirrors the communication structure of the organisation that builds it."),
    ],
    recall=[
        ["monolith", "simple, one deployable"],
        ["services tax", "network, consistency, operations"],
        ["series availability", "multiply"],
        ["strangler", "router, one route at a time"],
        ["shadow traffic", "compare unseen"],
        ["event sourcing", "log is truth; state is a fold"],
        ["CQRS", "write model + read model"],
        ["consistency gap", "read lags write"],
        ["data ownership", "one owner, no shared tables"],
        ["distributed monolith", "all costs, no independence"],
    ],
    sources=[
        dict(title="Strangler Fig Application (Martin Fowler)", url="https://martinfowler.com/bliki/StranglerFigApplication.html", use="The original description of the incremental migration pattern", license="Copyright Martin Fowler; read online", how="Link only"),
        dict(title="Microservices (Martin Fowler and James Lewis)", url="https://martinfowler.com/articles/microservices.html", use="The classic definition of microservices and their trade-offs", license="Copyright the authors; read online", how="Link only"),
        dict(title="Microservices.io pattern language (Chris Richardson)", url="https://microservices.io/patterns/index.html", use="Catalogue of patterns: saga, CQRS, API composition, database per service, strangler", license="Copyright Chris Richardson; read online", how="Link only"),
        dict(title="CQRS (Martin Fowler)", url="https://martinfowler.com/bliki/CQRS.html", use="When CQRS helps and when it is overkill", license="Copyright Martin Fowler; read online", how="Link only"),
        dict(title="Event Sourcing (Martin Fowler)", url="https://martinfowler.com/eaaDev/EventSourcing.html", use="The pattern and its consequences", license="Copyright Martin Fowler; read online", how="Link only"),
        dict(title="Bounded Context (Martin Fowler)", url="https://martinfowler.com/bliki/BoundedContext.html", use="Drawing boundaries around meaning", license="Copyright Martin Fowler; read online", how="Link only"),
        dict(title="nginx: split_clients module", url="https://nginx.org/en/docs/http/ngx_http_split_clients_module.html", use="Percentage-based routing as used in the rollout demo", license="Copyright nginx; read online", how="Link only"),
    ],
    plan=[
        "**Hours 1 to 2:** monolith or services: measure the hop cost and the availability table; add your own chain.",
        "**Hours 3 to 4:** strangler: run the three nginx demos; add a second migrated route and a header-based canary.",
        "**Hours 5 to 6:** event sourcing: add a new event type and a new projection; then the architecture-smell-read lab.",
        "**Hours 7 to 8:** CQRS: change the projector interval in your head and decide how the UI copes with the gap.",
        "**Hour 9:** data ownership: break the shared-table demo again and fix it with an API and an event-fed copy.",
        "**Hours 10 and 11:** say each interview scenario aloud for two minutes, timed, and compare with the written answer.",
    ],
)
