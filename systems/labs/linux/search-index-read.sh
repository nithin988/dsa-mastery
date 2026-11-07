#!/bin/bash
# Lab: answer search queries by hand from a small document set (an inverted index in your head). No services needed. Only creates ~/sys-lab/searchlab.
set -e
L="$HOME/sys-lab"
rm -rf "$L/searchlab" "$L/check-search-index-read.sh" "$L/answers-search.txt"
mkdir -p "$L/searchlab"
cat > "$L/searchlab/docs.txt" <<'EOF'
1: red running shoes for trail running
2: blue running shorts lightweight
3: red cotton shorts
4: leather office shoes black
5: running socks for trail and road
6: red running shorts
EOF
cat > "$L/searchlab/README.txt" <<'EOF'
docs.txt holds six documents, one per line: "id: text". Treat words as exact lower-case terms (no stemming).

Questions (write key=value lines into ~/sys-lab/answers-search.txt):
1. shoes_docs:    the ids of the documents containing the term "shoes", comma separated, ascending
2. red_and_shorts: the ids of the documents containing BOTH "red" and "shorts", comma separated, ascending
3. most_running:  the id of the document where "running" occurs most often
4. rarest_term:   which of red, running, shoes, shorts appears in the FEWEST documents (its postings list is shortest)

Tip: build the postings with grep -w, for example  grep -w shoes docs.txt | cut -d: -f1
EOF
cat > "$L/check-search-index-read.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-search.txt"
ok=1
chk() { got=$([ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2- | tr -d ' '); if [ "$got" = "$2" ]; then echo "PASS: $1"; else echo "FAIL: $1 ($3)"; ok=0; fi; }
chk shoes_docs 1,4 "grep -w shoes docs.txt"
chk red_and_shorts 3,6 "intersect the postings of red (1,3,6) and shorts (2,3,6)"
chk most_running 1 "document 1 contains running twice"
chk rarest_term shoes "shoes appears in 2 documents, the others in 3 or 4"
[ $ok = 1 ] && { echo "All tasks done. Short postings lists make a term selective: that is what IDF rewards."; exit 0; } || exit 1
EOF
chmod +x "$L/check-search-index-read.sh"
echo "Lab ready. Read ~/sys-lab/searchlab/README.txt"
