#!/bin/bash
# Lab: read saved HAProxy statistics. No network or services needed. Only creates ~/sys-lab/stats.
set -e
L="$HOME/sys-lab"
rm -rf "$L/stats" "$L/check-lb-stats-read.sh" "$L/answers-stats.txt"
mkdir -p "$L/stats"
cat > "$L/stats/stats.csv" <<'EOS'
# pxname,svname,qcur,qmax,scur,smax,slim,stot,bin,bout,dreq,dresp,ereq,econ,eresp,wretr,wredis,status,weight,act,bck,chkfail
web,FRONTEND,,,40,180,2000,10000,5100000,48200000,0,0,0,,,,,OPEN,,,,
web,web1,0,4,25,110,,6000,3000000,28900000,,0,,0,0,0,0,UP,3,1,0,2
web,web2,0,3,15,70,,3000,1500000,14300000,,0,,0,0,0,0,UP,2,1,0,1
web,web3,0,0,0,25,,1000,600000,5000000,,0,,12,0,0,0,DOWN,1,1,0,9
web,BACKEND,0,7,40,180,200,10000,5100000,48200000,0,0,,12,0,0,0,UP,6,2,0,0
EOS
cat > "$L/stats/README.txt" <<'EOS'
stats.csv is HAProxy's statistics (the stats page in CSV form), trimmed to the useful columns.
Columns:  pxname  svname  qcur  qmax  scur  smax  slim  stot  bin  bout  dreq  dresp  ereq  econ  eresp  wretr  wredis  status  weight  act  bck  chkfail
  stot   = total sessions handled since start        scur = sessions right now        smax = most sessions at once
  econ   = connection errors to the server           status = UP or DOWN              weight = the configured weight
  chkfail = number of failed health checks

Questions (write key=value lines into ~/sys-lab/answers-stats.txt):
1. down:            the name of the server that is DOWN
2. busiest:         the name of the server with the largest stot
3. share_percent:   the busiest server's share of the traffic, as a whole percentage (its stot divided by the sum of the three servers' stot)
4. weight_busiest:  the configured weight of the busiest server
5. conn_errors:     the total number of connection errors (econ) across the three servers
EOS
cat > "$L/check-lb-stats-read.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-stats.txt"
ok=1
chk() { got=$([ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2- | tr -d ' %'); if [ "$got" = "$2" ]; then echo "PASS: $1"; else echo "FAIL: $1 ($3)"; ok=0; fi; }
chk down web3 "look at the status column"
chk busiest web1 "the largest stot among web1, web2, web3"
chk share_percent 60 "6000 / (6000 + 3000 + 1000)"
chk weight_busiest 3 "the weight column of the busiest server"
chk conn_errors 12 "add the econ column of the three servers"
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-lb-stats-read.sh"
echo "Lab ready. Read ~/sys-lab/stats/README.txt"
