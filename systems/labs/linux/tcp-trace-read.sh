#!/bin/bash
# Lab: read a saved tcpdump capture of one HTTP request. No network needed. Only creates ~/sys-lab/tcp.
set -e
L="$HOME/sys-lab"
rm -rf "$L/tcp" "$L/check-tcp-trace-read.sh" "$L/answers-tcp.txt"
mkdir -p "$L/tcp"
cat > "$L/tcp/capture.txt" <<'EOS'
 1  IP 10.0.0.5.51234 > 10.0.0.9.80: Flags [S], seq 1000, win 64240, length 0
 2  IP 10.0.0.9.80 > 10.0.0.5.51234: Flags [S.], seq 5000, ack 1001, win 65160, length 0
 3  IP 10.0.0.5.51234 > 10.0.0.9.80: Flags [.], ack 1, win 502, length 0
 4  IP 10.0.0.5.51234 > 10.0.0.9.80: Flags [P.], seq 1:101, ack 1, win 502, length 100
 5  IP 10.0.0.9.80 > 10.0.0.5.51234: Flags [.], ack 101, win 509, length 0
 6  IP 10.0.0.9.80 > 10.0.0.5.51234: Flags [P.], seq 1:1461, ack 101, win 509, length 1460
 7  IP 10.0.0.9.80 > 10.0.0.5.51234: Flags [P.], seq 1461:2921, ack 101, win 509, length 1460
 8  IP 10.0.0.5.51234 > 10.0.0.9.80: Flags [.], ack 2921, win 480, length 0
 9  IP 10.0.0.9.80 > 10.0.0.5.51234: Flags [FP.], seq 2921:3500, ack 101, win 509, length 579
10  IP 10.0.0.5.51234 > 10.0.0.9.80: Flags [F.], seq 101, ack 3501, win 480, length 0
11  IP 10.0.0.9.80 > 10.0.0.5.51234: Flags [.], ack 102, win 509, length 0
EOS
cat > "$L/tcp/README.txt" <<'EOS'
capture.txt is a tcpdump capture of one HTTP request from a client (10.0.0.5) to a web server (10.0.0.9, port 80).
Flags: [S] SYN, [S.] SYN-ACK, [.] ACK only, [P.] data (push) with ACK, [F.] FIN with ACK, [FP.] data with FIN.
After the handshake tcpdump shows sequence numbers relative to the start of each side.

Questions (write key=value into ~/sys-lab/answers-tcp.txt):
1. client_port:     the client's ephemeral port
2. request_bytes:   how many bytes of HTTP request the client sent (packet 4)
3. response_bytes:  total bytes of HTTP response the server sent (add the lengths of all server packets that carry data)
4. data_packets_from_server: how many packets from the server carried data (length > 0)
5. closer:          who sent the first FIN: client or server
EOS
cat > "$L/check-tcp-trace-read.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-tcp.txt"
ok=1
chk() { got=$([ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2- | tr -d ' '); if [ "$got" = "$2" ]; then echo "PASS: $1"; else echo "FAIL: $1 ($3)"; ok=0; fi; }
chk client_port 51234 "the number after the client IP in packet 1"
chk request_bytes 100 "the length of packet 4"
chk response_bytes 3499 "1460 + 1460 + 579: sequence numbers are relative, the last data byte before FIN is 3499 (final ack is 3501 = data + FIN)"
chk data_packets_from_server 3 "packets 6, 7 and 9 have length > 0"
chk closer server "look for the first packet with F in its flags: packet 9 is [FP.] from the server"
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-tcp-trace-read.sh"
echo "Lab ready. Read ~/sys-lab/tcp/README.txt"
