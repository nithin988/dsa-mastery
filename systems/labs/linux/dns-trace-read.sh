#!/bin/bash
# Lab: read a saved `dig +trace` and a saved `dig` answer. No network needed. Only creates ~/sys-lab/dns.
set -e
L="$HOME/sys-lab"
rm -rf "$L/dns" "$L/check-dns-trace-read.sh" "$L/answers-dns.txt"
mkdir -p "$L/dns"
cat > "$L/dns/trace.txt" <<'EOS'
; <<>> DiG 9.18 <<>> +trace shop.example.org
.                       518400  IN  NS  a.root-servers.net.
.                       518400  IN  NS  b.root-servers.net.
;; Received 811 bytes from 192.168.1.1#53(192.168.1.1) in 12 ms

org.                    172800  IN  NS  a0.org.afilias-nst.info.
org.                    172800  IN  NS  b0.org.afilias-nst.org.
;; Received 773 bytes from 198.41.0.4#53(a.root-servers.net) in 24 ms

example.org.            86400   IN  NS  ns1.dnshost.example.
example.org.            86400   IN  NS  ns2.dnshost.example.
;; Received 646 bytes from 199.19.56.1#53(a0.org.afilias-nst.info) in 31 ms

shop.example.org.       300     IN  CNAME  shops.cdn-provider.example.
;; Received 118 bytes from 203.0.113.53#53(ns1.dnshost.example) in 18 ms
EOS
cat > "$L/dns/answer.txt" <<'EOS'
;; ANSWER SECTION:
shop.example.org.       187     IN  CNAME  shops.cdn-provider.example.
shops.cdn-provider.example. 42  IN  A      198.51.100.77
;; Query time: 0 msec
;; SERVER: 192.168.1.1#53(192.168.1.1)
EOS
cat > "$L/dns/README.txt" <<'EOS'
trace.txt is the output of `dig +trace shop.example.org`: it shows each server asked on the way down the DNS hierarchy.
answer.txt is an ordinary lookup of the same name made a little later through the local resolver.

Questions:
1. tld_server:    the name of the TLD server (the one that answered the question "who runs example.org?"),
                  i.e. the server named in the line "Received ... from ...(NAME)" that precedes the example.org. NS records.
2. final_server:  the name of the authoritative server that gave the final answer (last "Received" line).
3. ttl_final:     the TTL (seconds) of the CNAME record in the trace.
4. cached_for:    in answer.txt the same CNAME has a smaller TTL: how many seconds of its life have already been used?
                  (ttl_final minus the TTL shown in answer.txt)
5. address:       the final IPv4 address the browser will connect to.
Write key=value lines into ~/sys-lab/answers-dns.txt
EOS
cat > "$L/check-dns-trace-read.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-dns.txt"
ok=1
chk() { got=$([ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2- | tr -d ' ' | sed 's/\.$//'); if [ "$got" = "$2" ]; then echo "PASS: $1"; else echo "FAIL: $1 ($3)"; ok=0; fi; }
chk tld_server a0.org.afilias-nst.info "the server that returned the example.org NS records"
chk final_server ns1.dnshost.example "the last Received line"
chk ttl_final 300 "the TTL column of the CNAME in the trace"
chk cached_for 113 "300 minus the TTL in answer.txt"
chk address 198.51.100.77 "the A record at the end of the chain"
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-dns-trace-read.sh"
echo "Lab ready. Read ~/sys-lab/dns/README.txt"
