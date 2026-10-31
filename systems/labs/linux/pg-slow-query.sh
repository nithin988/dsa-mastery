#!/bin/bash
# Lab: fix a slow query in a live PostgreSQL. Starts a practice server on port 5546 (local socket only). Needs the postgresql package. Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"; D="$L/pglab"
export PATH="$(ls -d /usr/lib/postgresql/*/bin | head -1):$PATH"
[ -d "$D/data" ] && pg_ctl -D "$D/data" -m immediate stop >/dev/null 2>&1 || true
rm -rf "$D" "$L/check-pg-slow-query.sh"
mkdir -p "$D"
initdb -D "$D/data" -A trust -U learner >/dev/null
pg_ctl -D "$D/data" -o "-p 5546 -k $D -c listen_addresses='' -c fsync=off" -l "$D/log" -w start >/dev/null
createdb -h "$D" -p 5546 -U learner shop
psql -X -q -h "$D" -p 5546 -U learner shop <<'EOF'
select setseed(0.5);
create table events(id bigserial primary key, user_id int, kind text, created_at timestamptz);
insert into events(user_id, kind, created_at)
  select 1 + (random()*49999)::int, (array['view','click','buy'])[1+(random()*2)::int], now() - (random()*90 || ' days')::interval
  from generate_series(1, 300000);
analyze events;
EOF
cat > "$D/README.txt" <<'EOS2'
A practice PostgreSQL is running (socket in ~/sys-lab/pglab, port 5546, database shop, user learner).
Connect with:   psql -h ~/sys-lab/pglab -p 5546 -U learner shop

The table events has 300,000 rows. This query is slow, and it runs thousands of times a minute:
    select count(*) from events where user_id = 4242;

Your job: make it fast WITHOUT changing the query. Use EXPLAIN to see how it runs today, then add the right index.
Check your work with:   bash ~/sys-lab/check-pg-slow-query.sh
EOS2
cat > "$L/check-pg-slow-query.sh" <<'EOF'
#!/bin/bash
D="$HOME/sys-lab/pglab"
export PATH="$(ls -d /usr/lib/postgresql/*/bin | head -1):$PATH"
P="psql -X -At -h $D -p 5546 -U learner shop"
$P -c "select 1" >/dev/null 2>&1 || { echo "FAIL: the practice PostgreSQL is not running; run the setup script again"; exit 1; }
plan=$($P -c "explain select count(*) from events where user_id = 4242")
if echo "$plan" | grep -q "Seq Scan"; then echo "FAIL: the query still reads the whole table (Seq Scan). Add an index on the column in the WHERE clause."; exit 1; fi
if ! echo "$plan" | grep -qi "index"; then echo "FAIL: the plan does not use an index:"; echo "$plan"; exit 1; fi
n=$($P -c "select count(*) from events")
[ "$n" = "300000" ] || { echo "FAIL: the table must still have 300000 rows (found $n)"; exit 1; }
echo "PASS: the query now uses an index."
echo "All tasks done. The query reads a few rows instead of the whole table."
exit 0
EOF
chmod +x "$L/check-pg-slow-query.sh"
echo "Lab ready. Read ~/sys-lab/pglab/README.txt"
