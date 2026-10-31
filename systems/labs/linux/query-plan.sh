#!/bin/bash
# Lab: make a slow query use an index. Creates ~/sys-lab/db/shop.db (SQLite). Needs python3 (built-in sqlite3 module).
set -e
L="$HOME/sys-lab"
rm -rf "$L/db" "$L/check-query-plan.sh" "$L/answers-plan.txt"
mkdir -p "$L/db"
python3 - <<'EOF'
import os, random, sqlite3
p = os.path.expanduser("~/sys-lab/db/shop.db")
c = sqlite3.connect(p)
c.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER, status TEXT, amount REAL)")
rng = random.Random(5)
rows = [(i, rng.randint(1, 5000), rng.choice(["new", "paid", "shipped", "returned"]), round(rng.uniform(5, 500), 2)) for i in range(1, 60001)]
c.executemany("INSERT INTO orders VALUES (?,?,?,?)", rows)
c.commit()
EOF
cat > "$L/db/slow.sql" <<'EOS'
-- This query is slow on a big table:
SELECT count(*) FROM orders WHERE customer_id = 4242 AND status = 'shipped';
EOS
cat > "$L/db/README.txt" <<'EOS'
shop.db is a SQLite database with an `orders` table (60,000 rows).
slow.sql holds a query that scans the whole table.

Open it with:   python3 -c "import sqlite3; c=sqlite3.connect('shop.db'); print(c.execute('EXPLAIN QUERY PLAN SELECT count(*) FROM orders WHERE customer_id = 4242 AND status = \'shipped\'').fetchall())"
(or the sqlite3 command line tool if you have it: sqlite3 shop.db)

Goal: make the plan say SEARCH ... USING INDEX instead of SCAN. Do not delete or change any rows.
EOS

cat > "$L/check-query-plan.sh" <<'EOF'
#!/bin/bash
L="$HOME/sys-lab"
A="$L/answers-plan.txt"
python3 - <<'PY'
import os, sqlite3, sys
c = sqlite3.connect(os.path.expanduser("~/sys-lab/db/shop.db"))
n = c.execute("SELECT count(*) FROM orders").fetchone()[0]
plan = " ".join(r[3] for r in c.execute("EXPLAIN QUERY PLAN SELECT count(*) FROM orders WHERE customer_id = 4242 AND status = 'shipped'"))
ok = True
if n == 60000:
    print("PASS: the data is untouched (60,000 rows)")
else:
    print("FAIL: the table must still have 60,000 rows (found %d)" % n); ok = False
if "SEARCH" in plan and "INDEX" in plan:
    print("PASS: the query now uses an index: " + plan)
else:
    print("FAIL: the query still scans the table: " + plan + ". Create an index that helps the WHERE clause."); ok = False
sys.exit(0 if ok else 1)
PY
EOF
chmod +x "$L/check-query-plan.sh"
echo "Lab ready. See ~/sys-lab/db/README.txt"
