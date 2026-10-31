#!/bin/bash
# Solution for the cert-expiry lab.
cd "$HOME/sys-lab/certs"
list=""
for f in *.pem; do
  if ! openssl x509 -in "$f" -noout -checkend $((30 * 86400)) >/dev/null; then list="$list,${f%.pem}"; fi
done
printf 'expiring=%s\n' "${list#,}" > "$HOME/sys-lab/answers-certs.txt"
cat "$HOME/sys-lab/answers-certs.txt"
