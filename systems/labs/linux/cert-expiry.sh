#!/bin/bash
# Lab: which certificates expire within 30 days? Generates five certificates in ~/sys-lab/certs. Needs openssl. Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
rm -rf "$L/certs" "$L/check-cert-expiry.sh" "$L/answers-certs.txt"
mkdir -p "$L/certs"
cd "$L/certs"
mk() { openssl req -x509 -newkey rsa:2048 -nodes -keyout /dev/null -out "$1.pem" -days "$2" -subj "/CN=$1.example.test" 2>/dev/null; }
mk api 12
mk shop 90
mk blog 400
mk mail 25
mk admin 2

cat > "$L/check-cert-expiry.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-certs.txt"
got=""
[ -f "$A" ] && got=$(grep '^expiring=' "$A" | head -1 | cut -d= -f2- | tr ',' '\n' | sort | paste -sd, -)
if [ "$got" = "admin,api,mail" ]; then echo "PASS: you found every certificate that expires within 30 days"; echo "All tasks done."; exit 0; fi
echo "FAIL: expiring= should list, comma-separated, every certificate name (file name without .pem) that expires within 30 days. You wrote: '$got'"; exit 1
EOF
chmod +x "$L/check-cert-expiry.sh"
echo "Lab ready. Five certificates are in ~/sys-lab/certs"
