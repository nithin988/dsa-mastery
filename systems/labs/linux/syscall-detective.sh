#!/bin/bash
# Lab: a program fails with a vague message; use strace to see which file it really asks the kernel for.
# Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
rm -rf "$L/bin-sc" "$L/state" "$L/check-syscall-detective.sh" "$L/answers-syscall.txt"
mkdir -p "$L/bin-sc" "$L/state"

cat > "$L/bin-sc/reporter" <<'EOS'
#!/bin/bash
# reporter: builds the nightly report. It needs a settings file but never says which one.
cfg="$HOME/sys-lab/state/.conf.d/reporter.cfg"
if [ ! -r "$cfg" ]; then
  echo "reporter: configuration error" >&2
  exit 1
fi
. "$cfg"
echo "report generated (mode=${mode:-unset})"
EOS
chmod +x "$L/bin-sc/reporter"

cat > "$L/check-syscall-detective.sh" <<'EOF'
#!/bin/bash
L="$HOME/sys-lab"
ok=1
A="$L/answers-syscall.txt"
want="$L/state/.conf.d/reporter.cfg"
got=""
[ -f "$A" ] && got=$(grep '^missing=' "$A" | head -1 | cut -d= -f2-)
if [ "$got" = "$want" ] || [ "$got" = "~/sys-lab/state/.conf.d/reporter.cfg" ]; then echo "PASS: you found the exact path the program asks for"; else echo "FAIL: write missing=<full path of the file the program opens> into ~/sys-lab/answers-syscall.txt"; ok=0; fi
out=$("$L/bin-sc/reporter" 2>&1); rc=$?
if [ $rc -eq 0 ] && echo "$out" | grep -q "report generated (mode=fast)"; then echo "PASS: reporter now works"; else echo "FAIL: reporter still fails, or the file does not say mode=fast"; ok=0; fi
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-syscall-detective.sh"
echo "Lab ready. Try: ~/sys-lab/bin-sc/reporter   (it fails with a vague message)"
