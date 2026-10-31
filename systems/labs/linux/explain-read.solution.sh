#!/bin/bash
# Solution for the explain-read lab.
cat > "$HOME/sys-lab/answers-explain.txt" <<'EOF'
big_scan_table=orders
rows_discarded=490290
execution_ms=212
index_columns=status,created_at
EOF
cat "$HOME/sys-lab/answers-explain.txt"
