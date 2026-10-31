#!/bin/bash
# Solution for the config-bisect lab: halve the file until one line remains.
L="$HOME/sys-lab/cfg"
lo=1; hi=16
while [ "$lo" -lt "$hi" ]; do
  mid=$(( (lo + hi) / 2 ))
  sed -n "${lo},${mid}p" "$L/app.conf" > /tmp/half.conf
  if "$L/app" /tmp/half.conf >/dev/null 2>&1; then lo=$((mid + 1)); else hi=$mid; fi
done
echo "bad_line=$lo" > "$HOME/sys-lab/answers-cfg.txt"
cat "$HOME/sys-lab/answers-cfg.txt"
