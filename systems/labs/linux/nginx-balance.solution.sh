#!/bin/bash
# Solution for the nginx-balance lab: fix the three mistakes (missing semicolon, missing third server, wrong upstream name).
D="$HOME/sys-lab/nginxlab"
sed -i 's#server 127.0.0.1:9102$#server 127.0.0.1:9102;\n    server 127.0.0.1:9103;#; s#proxy_pass http://apps;#proxy_pass http://app;#' "$D/balancer.conf"
nginx -t -c "$D/balancer.conf" -p "$D/"
nginx -c "$D/balancer.conf" -p "$D/"
sleep 1
for i in $(seq 1 9); do curl -s http://127.0.0.1:8190/; done | sort | uniq -c
