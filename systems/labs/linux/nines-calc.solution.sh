#!/bin/bash
# Solution for the nines-calc lab.
awk 'BEGIN{
  printf "allowed_minutes=%.1f\n", 43200 * (1 - 0.9995)
  printf "series_percent=%.2f\n", 100 * 0.999 * 0.999
  printf "parallel_percent=%.2f\n", 100 * (1 - 0.01 * 0.01)
  printf "worst_case_loss_hours=%d\n", 6
}' > "$HOME/sys-lab/answers-nines.txt"
cat "$HOME/sys-lab/answers-nines.txt"
