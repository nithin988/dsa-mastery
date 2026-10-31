#!/bin/bash
# Lab: read a service dependency list and find the architecture smells. No services needed. Only creates ~/sys-lab/archsmell.
set -e
L="$HOME/sys-lab"
rm -rf "$L/archsmell" "$L/check-architecture-smell-read.sh" "$L/answers-arch.txt"
mkdir -p "$L/archsmell"
cat > "$L/archsmell/services.txt" <<'EOF'
service    availability  calls                     database
web        99.95         api                       -
api        99.90         orders,users,catalog      -
orders     99.90         payments,inventory        ordersdb
users      99.95         -                         usersdb
catalog    99.90         search                    catalogdb
payments   99.90         ledger                    ordersdb
inventory  99.90         orders                    ordersdb
ledger     99.99         -                         ledgerdb
search     99.50         -                         -
EOF
cat > "$L/archsmell/README.txt" <<'EOF'
services.txt lists each service, its availability (percent), the services it calls synchronously (comma separated) and the database it uses.

Questions (write key=value lines into ~/sys-lab/answers-arch.txt):
1. shared_database:   the database used by more than one service
2. shared_services:   the services that use it, comma separated, in alphabetical order
3. cycle:             the two services that call each other (circular dependency), comma separated, alphabetical
4. weakest_service:   the service with the lowest availability
5. chain_availability: the availability in percent, with two decimals, of one request that goes web -> api -> orders -> payments -> ledger
                       (multiply the five availabilities as fractions, then give the percent; for example 99.00)
EOF
cat > "$L/check-architecture-smell-read.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-arch.txt"
ok=1
chk() { got=$([ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2- | tr -d ' %'); if [ "$got" = "$2" ]; then echo "PASS: $1"; else echo "FAIL: $1 ($3)"; ok=0; fi; }
chk shared_database ordersdb "used by orders, payments and inventory"
chk shared_services inventory,orders,payments "alphabetical"
chk cycle inventory,orders "orders calls inventory, inventory calls orders"
chk weakest_service search "99.50 is the lowest"
chk chain_availability 99.64 "99.95% x 99.90% x 99.90% x 99.90% x 99.99%"
[ $ok = 1 ] && { echo "All tasks done. A shared database and a call cycle mean these services are not independent; availability multiplies along the chain."; exit 0; } || exit 1
EOF
chmod +x "$L/check-architecture-smell-read.sh"
echo "Lab ready. Read ~/sys-lab/archsmell/README.txt"
