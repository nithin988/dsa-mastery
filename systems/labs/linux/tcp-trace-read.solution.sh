#!/bin/bash
# Solution for the tcp-trace-read lab. In each line field 3 is the sender, e.g. 10.0.0.9.80
F="$HOME/sys-lab/tcp/capture.txt"
port=$(awk 'NR==1{n=split($3,a,"."); print a[n]}' "$F")
req=$(awk 'NR==4{print $NF}' "$F")
resp=$(awk '$3=="10.0.0.9.80" && $NF>0 {s+=$NF} END{print s}' "$F")
pk=$(awk '$3=="10.0.0.9.80" && $NF>0 {c++} END{print c}' "$F")
closer=$(awk '/Flags \[F/{ if ($3=="10.0.0.9.80") print "server"; else print "client"; exit }' "$F")
printf 'client_port=%s\nrequest_bytes=%s\nresponse_bytes=%s\ndata_packets_from_server=%s\ncloser=%s\n' "$port" "$req" "$resp" "$pk" "$closer" > "$HOME/sys-lab/answers-tcp.txt"
cat "$HOME/sys-lab/answers-tcp.txt"
