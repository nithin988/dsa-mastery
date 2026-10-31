#!/bin/bash
# Solution for the proc-detective lab.
pid=$(pgrep -f '^nightly-job' | head -1)
{
  echo "pid=$pid"
  echo "exe=$(readlink -f /proc/$pid/exe)"
  echo "cwd=$(readlink -f /proc/$pid/cwd)"
} > "$HOME/sys-lab/answers-proc.txt"
cat "$HOME/sys-lab/answers-proc.txt"
