#!/bin/bash
# Solution for the query-plan lab.
python3 - <<'EOF'
import os, sqlite3
c = sqlite3.connect(os.path.expanduser("~/sys-lab/db/shop.db"))
print("before:", c.execute("EXPLAIN QUERY PLAN SELECT count(*) FROM orders WHERE customer_id = 4242 AND status = 'shipped'").fetchall())
c.execute("CREATE INDEX idx_orders_customer_status ON orders(customer_id, status)")
c.commit()
print("after: ", c.execute("EXPLAIN QUERY PLAN SELECT count(*) FROM orders WHERE customer_id = 4242 AND status = 'shipped'").fetchall())
EOF
