#!/bin/bash
# Solution for the replica-lag-read lab.
cat > "$HOME/sys-lab/answers-replag.txt" <<'EOF'
fresh_replica=replica_eu
report_replicas=replica_eu,replica_us
sync_replica=replica_eu
worst_lag_seconds=192
EOF
cat "$HOME/sys-lab/answers-replag.txt"
