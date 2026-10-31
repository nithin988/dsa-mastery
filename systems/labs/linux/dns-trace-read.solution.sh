#!/bin/bash
# Solution for the dns-trace-read lab.
D="$HOME/sys-lab/dns"
# a "Received" line names the server that sent the records printed just above it
tld=$(awk '/^example.org/{seen=1} seen && /^;; Received/{print; exit}' "$D/trace.txt" | sed 's/.*(\(.*\)).*/\1/')
final=$(grep '^;; Received' "$D/trace.txt" | tail -1 | sed 's/.*(\(.*\)).*/\1/')
ttl=$(awk '$4=="CNAME"{print $2; exit}' "$D/trace.txt")
now=$(awk '$4=="CNAME"{print $2; exit}' "$D/answer.txt")
addr=$(awk '$4=="A"{print $5}' "$D/answer.txt")
printf 'tld_server=%s\nfinal_server=%s\nttl_final=%s\ncached_for=%s\naddress=%s\n' "$tld" "$final" "$ttl" "$((ttl - now))" "$addr" > "$HOME/sys-lab/answers-dns.txt"
cat "$HOME/sys-lab/answers-dns.txt"
