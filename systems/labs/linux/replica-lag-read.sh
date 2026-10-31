#!/bin/bash
# Lab: read saved replication statistics and decide which replica can serve which reads. No services needed. Only creates ~/sys-lab/replag.
set -e
L="$HOME/sys-lab"
rm -rf "$L/replag" "$L/check-replica-lag-read.sh" "$L/answers-replag.txt"
mkdir -p "$L/replag"
cat > "$L/replag/stat.txt" <<'EOF'
select application_name, state, sync_state, replay_lag, pg_wal_lsn_diff(sent_lsn, replay_lsn) as bytes_behind from pg_stat_replication;

 application_name |   state   | sync_state | replay_lag | bytes_behind
------------------+-----------+------------+------------+--------------
 replica_eu       | streaming | sync       | 00:00:00.2 |        18000
 replica_us       | streaming | async      | 00:00:07.4 |      9400000
 replica_asia     | catchup   | async      | 00:03:12.0 |    412000000
(3 rows)
EOF
cat > "$L/replag/README.txt" <<'EOF'
stat.txt is the output of pg_stat_replication on a primary with three replicas.

Reads for a "my orders" page must show the customer's own latest order, so they may only go to a replica that is at most 1 second behind.
Reads for a nightly report can use any replica that is streaming (not catching up).

Questions (write key=value lines into ~/sys-lab/answers-replag.txt):
1. fresh_replica:     the single replica that may serve the "my orders" page
2. report_replicas:   the replicas that may serve the report, comma separated, in the order listed
3. sync_replica:      the replica whose failure would make COMMIT wait on the primary (the synchronous one)
4. worst_lag_seconds: the replay lag of the worst replica in whole seconds (192 for 3 minutes 12 seconds)
EOF
cat > "$L/check-replica-lag-read.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-replag.txt"
ok=1
chk() { got=$([ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2- | tr -d ' '); if [ "$got" = "$2" ]; then echo "PASS: $1"; else echo "FAIL: $1 ($3)"; ok=0; fi; }
chk fresh_replica replica_eu "only replay_lag under 1 second qualifies"
chk report_replicas replica_eu,replica_us "state must be streaming; the catchup replica is still recovering"
chk sync_replica replica_eu "sync_state is sync"
chk worst_lag_seconds 192 "00:03:12 is 3 x 60 + 12"
[ $ok = 1 ] && { echo "All tasks done. Lag decides which reads a replica may serve; a synchronous replica is a dependency of every commit."; exit 0; } || exit 1
EOF
chmod +x "$L/check-replica-lag-read.sh"
echo "Lab ready. Read ~/sys-lab/replag/README.txt"
