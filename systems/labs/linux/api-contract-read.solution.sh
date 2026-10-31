#!/bin/bash
# Solution for the api-contract-read lab.
cat > "$HOME/sys-lab/answers-api.txt" <<'EOF'
duplicate_orders=41,42
missing_header=Idempotency-Key
wrong_status_path=/orders/999
right_status=404
ignoring_client=app-31
EOF
cat "$HOME/sys-lab/answers-api.txt"
