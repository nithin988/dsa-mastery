#!/bin/bash
# Lab: see how hash-based load balancing spreads users, and what happens when a server is removed. Only creates ~/sys-lab/lb.
set -e
L="$HOME/sys-lab"
rm -rf "$L/lb" "$L/check-lb-distribution.sh" "$L/answers-lb.txt"
mkdir -p "$L/lb"
for i in $(seq -w 1 24); do echo "user$i"; done > "$L/lb/users.txt"
cat > "$L/lb/README.txt" <<'EOS'
users.txt lists 24 users. The load balancer picks a server with:   server = CRC(user) mod N
where CRC(user) is the first number printed by:  printf '%s' user01 | cksum
Servers are numbered 0..N-1.
Questions:
1. With N=3 servers, how many users go to server 0, to server 1, to server 2?
2. One server is removed (N becomes 2). How many users now go to a DIFFERENT server number than before?
EOS
h() { printf '%s' "$1" | cksum | awk '{print $1}'; }
c0=0; c1=0; c2=0; moved=0
while read -r u; do
  x=$(h "$u"); a=$((x % 3)); b=$((x % 2))
  case $a in 0) c0=$((c0+1));; 1) c1=$((c1+1));; 2) c2=$((c2+1));; esac
  [ "$a" != "$b" ] && moved=$((moved+1))
done < "$L/lb/users.txt"
echo "$c0 $c1 $c2 $moved" > "$L/lb/.expected"

cat > "$L/check-lb-distribution.sh" <<'EOF'
#!/bin/bash
L="$HOME/sys-lab"
A="$L/answers-lb.txt"
read -r e0 e1 e2 em < "$L/lb/.expected"
ok=1
get() { [ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2-; }
[ "$(get server0)" = "$e0" ] && [ "$(get server1)" = "$e1" ] && [ "$(get server2)" = "$e2" ] && echo "PASS: distribution with 3 servers" || { echo "FAIL: server0=, server1=, server2= are the user counts per server for N=3"; ok=0; }
[ "$(get moved)" = "$em" ] && echo "PASS: moved" || { echo "FAIL: moved= is how many users change server number when N goes from 3 to 2"; ok=0; }
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-lb-distribution.sh"
echo "Lab ready. See ~/sys-lab/lb/README.txt and users.txt"
