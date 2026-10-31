#!/bin/bash
# Lab: read a saved EXPLAIN ANALYZE output and diagnose it. No services needed. Only creates ~/sys-lab/explain.
set -e
L="$HOME/sys-lab"
rm -rf "$L/explain" "$L/check-explain-read.sh" "$L/answers-explain.txt"
mkdir -p "$L/explain"
cat > "$L/explain/plan.txt" <<'EOF'
EXPLAIN (ANALYZE) select o.id, c.name from orders o join customers c on c.id = o.customer_id where o.status = 'paid' and o.created_at > now() - interval '7 days' order by o.created_at desc limit 20;

 Limit  (cost=14850.2..14850.3 rows=20 width=30) (actual time=212.4..212.5 rows=20 loops=1)
   ->  Sort  (cost=14850.2..14861.0 rows=4310 width=30) (actual time=212.4..212.4 rows=20 loops=1)
         Sort Key: o.created_at DESC
         Sort Method: top-N heapsort  Memory: 27kB
         ->  Hash Join  (cost=612.0..14760.1 rows=4310 width=30) (actual time=9.8..209.7 rows=9710 loops=1)
               Hash Cond: (o.customer_id = c.id)
               ->  Seq Scan on orders o  (cost=0.0..14012.0 rows=4310 width=16) (actual time=0.1..198.9 rows=9710 loops=1)
                     Filter: ((status = 'paid') AND (created_at > (now() - '7 days'::interval)))
                     Rows Removed by Filter: 490290
               ->  Hash  (cost=362.0..362.0 rows=20000 width=22) (actual time=9.6..9.6 rows=20000 loops=1)
                     ->  Seq Scan on customers c  (cost=0.0..362.0 rows=20000 width=22) (actual time=0.0..4.1 rows=20000 loops=1)
 Planning Time: 0.4 ms
 Execution Time: 212.9 ms
EOF
cat > "$L/explain/README.txt" <<'EOF'
plan.txt is an EXPLAIN ANALYZE of a slow page query on a table of 500,000 orders.

Questions (write key=value lines into ~/sys-lab/answers-explain.txt):
1. big_scan_table:   the table that is read completely with a Seq Scan and is the real problem (the big one)
2. rows_discarded:   how many rows that scan threw away (Rows Removed by Filter)
3. execution_ms:     total execution time in milliseconds (whole number, as printed)
4. index_columns:    the two columns, comma separated in this order, of the index that would help most
                     (an equality column first, then the range/sort column used in the filter and ORDER BY)
EOF
cat > "$L/check-explain-read.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-explain.txt"
ok=1
chk() { got=$([ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2- | tr -d ' '); if [ "$got" = "$2" ]; then echo "PASS: $1"; else echo "FAIL: $1 ($3)"; ok=0; fi; }
chk big_scan_table orders "the Seq Scan on the 500,000-row table, not the small customers table"
chk rows_discarded 490290 "see 'Rows Removed by Filter'"
chk execution_ms 212 "'Execution Time' as a whole number (212.9 gives 212 or 213: write 212)"
chk index_columns status,created_at "equality column (status) first, then the range and sort column (created_at)"
[ $ok = 1 ] && { echo "All tasks done. Index (status, created_at) lets the database jump to the paid orders and read the newest 20 in order."; exit 0; } || exit 1
EOF
chmod +x "$L/check-explain-read.sh"
echo "Lab ready. Read ~/sys-lab/explain/README.txt"
