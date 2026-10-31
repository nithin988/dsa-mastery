#!/bin/bash
# Lab: fix four permission problems. Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
P="$L/perm"
rm -rf "$P" "$L/check-fix-permissions.sh"
mkdir -p "$P/shared" "$P/public"
printf '#!/bin/bash\necho "deploy ok"\n' > "$P/deploy.sh"
printf 'PRIVATE KEY (practice only)\n' > "$P/secret.key"
printf '<h1>hello</h1>\n' > "$P/public/index.html"
chmod 644 "$P/deploy.sh" "$P/secret.key"
chmod 700 "$P/shared"
chmod 600 "$P/public/index.html"

cat > "$L/check-fix-permissions.sh" <<'EOF'
#!/bin/bash
P="$HOME/sys-lab/perm"
ok=1
chk() { got=$(stat -c %a "$P/$1" 2>/dev/null); if [ "$got" = "$2" ]; then echo "PASS: $1 is $2"; else echo "FAIL: $1 is '$got', want $2 ($3)"; ok=0; fi; }
chk deploy.sh 755 "the owner must be able to run it, others may read and run"
chk secret.key 600 "only the owner may read or write a private key"
chk shared 770 "owner and group full access, others none"
chk public/index.html 644 "everyone may read, only the owner writes"
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-fix-permissions.sh"
echo "Lab ready. Work in ~/sys-lab/perm"
