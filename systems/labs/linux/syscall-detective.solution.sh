#!/bin/bash
# Solution for the syscall-detective lab.
L="$HOME/sys-lab"
path=$(strace -f -e trace=%file "$L/bin-sc/reporter" 2>&1 | grep ENOENT | grep -o '"[^"]*reporter\.cfg"' | head -1 | tr -d '"')
echo "missing file: $path"
mkdir -p "$(dirname "$path")"
printf 'mode=fast\n' > "$path"
printf 'missing=%s\n' "$path" > "$L/answers-syscall.txt"
"$L/bin-sc/reporter"
