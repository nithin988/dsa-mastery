#!/bin/bash
# Systems Mastery: creates ~/textlab, small data files for the text processing module.
# Safe by design: it only creates and replaces ~/textlab, and refuses to touch a folder it did not create.
set -e
export LC_ALL=C TZ=UTC
T="$HOME/textlab"
MARK="$HOME/.sys-lab-textlab"
if [ -e "$T" ] && [ ! -e "$MARK" ]; then
  echo "~/textlab already exists and was not created by this script. Rename it and run again."
  exit 1
fi
rm -rf "$T"
mkdir -p "$T/tmpfiles" "$T/scratch"

printf 'alice 42 eng\nbob 17 ops\ncarol 63 eng\ndave 8 ops\n' > "$T/people.txt"
printf 'region,product,units,price\nnorth,widget,10,2.50\nsouth,widget,4,2.50\nnorth,gadget,3,10.00\neast,widget,7,2.50\nsouth,gadget,6,10.00\neast,gadget,1,10.00\n' > "$T/sales.csv"
printf 'apple\nbanana\napple\ncherry\nbanana\napple\ndate\n' > "$T/words.txt"
cat > "$T/server.log" <<'EOF'
2026-01-15 10:01:12 INFO  api request ok (host=web1) 120ms
2026-01-15 10:01:15 ERROR db timeout (host=db1) 3000ms
2026-01-15 10:02:01 INFO  api request ok (host=web2) 98ms
2026-01-15 10:02:44 WARN  slow query (host=db1) 1450ms
2026-01-15 10:03:10 ERROR db timeout (host=db1) 3000ms
2026-01-15 10:03:55 INFO  api request ok (host=web1) 110ms
2026-01-15 11:00:02 ERROR disk full (host=web2) 5ms
2026-01-15 11:00:30 INFO  backup started (host=db2) 20ms
2026-01-15 11:15:09 WARN  retrying connection (host=web1) 200ms
2026-01-15 11:15:40 ERROR db timeout (host=db1) 3000ms
2026-01-16 09:00:00 INFO  api request ok (host=web1) 101ms
2026-01-16 09:00:12 ERROR upstream refused (host=web2) 12ms
2026-01-16 09:01:00 INFO  api request ok (host=web2) 95ms
2026-01-16 09:02:30 WARN  slow query (host=db2) 1800ms
EOF
for f in a.tmp b.tmp c.tmp "my notes.tmp" keep.txt; do printf 'x\n' > "$T/tmpfiles/$f"; done

find "$T" -exec touch -h -d '2026-01-15 09:30:00' {} +
touch "$MARK"
touch -d '2026-01-15 09:30:00' "$HOME"
echo "Practice data ready: ~/textlab"
