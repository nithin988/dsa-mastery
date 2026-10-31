#!/bin/bash
# Lab: decode Snowflake-style IDs into time, machine and sequence. Only creates ~/sys-lab/snow.
set -e
L="$HOME/sys-lab"
rm -rf "$L/snow" "$L/check-snowflake-id.sh" "$L/answers-snow.txt"
mkdir -p "$L/snow"
export L
python3 - <<'EOF'
import os
L = os.environ["L"] + "/snow"
fields = [(86400000, 3, 0), (86400001, 3, 1), (172800123, 17, 4095)]   # (ms since epoch, machine, sequence)
ids = [(t << 22) | (m << 12) | s for t, m, s in fields]
open(L + "/ids.txt", "w").write("\n".join(map(str, ids)) + "\n")
open(L + "/.expected", "w").write("%d %d %d\n" % (fields[2][0], fields[2][1], fields[2][2]))
EOF
cat > "$L/snow/README.txt" <<'EOS'
Each ID is a 63-bit number laid out like this (high bits first):
    41 bits  milliseconds since a custom epoch     (id >> 22)
    10 bits  machine id                            ((id >> 12) & 1023)
    12 bits  sequence within that millisecond      (id & 4095)
ids.txt has three IDs, one per line.
Questions (decode the THIRD id):
1. ms:      the 41-bit timestamp part, in milliseconds since the custom epoch
2. machine: the machine id
3. seq:     the sequence number
4. Which of the three IDs is the smallest number, and is that also the oldest? (they sort by time) - no answer needed.
Shell arithmetic works:  echo $(( 172800123 << 22 ))   and   echo $(( id >> 22 ))
EOS
cat > "$L/check-snowflake-id.sh" <<'EOF'
#!/bin/bash
L="$HOME/sys-lab"
A="$L/answers-snow.txt"
read -r em emc es < "$L/snow/.expected"
ok=1
get() { [ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2-; }
[ "$(get ms)" = "$em" ] && echo "PASS: ms" || { echo "FAIL: ms= is id >> 22 for the third id"; ok=0; }
[ "$(get machine)" = "$emc" ] && echo "PASS: machine" || { echo "FAIL: machine= is (id >> 12) & 1023"; ok=0; }
[ "$(get seq)" = "$es" ] && echo "PASS: seq" || { echo "FAIL: seq= is id & 4095"; ok=0; }
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-snowflake-id.sh"
echo "Lab ready. See ~/sys-lab/snow/README.txt"
