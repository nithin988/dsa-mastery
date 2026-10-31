#!/bin/bash
# Solution for the port-detective lab.
L="$HOME/sys-lab"
ss -ltnp | grep ':8088'
pid=$(ss -ltnp | grep ':8088' | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2)
kill -TERM "$pid"
sleep 1
nohup python3 "$L/net/webapp.py" > /dev/null 2>&1 &
sleep 1
curl -s http://127.0.0.1:8088/ping
