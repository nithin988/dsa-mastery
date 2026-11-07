#!/bin/bash
# Solution for the search-index-read lab.
F="$HOME/sys-lab/searchlab/docs.txt"
ids() { grep -w "$1" "$F" | cut -d: -f1 | sort -n; }
shoes=$(ids shoes | paste -sd, -)
both=$(comm -12 <(ids red) <(ids shorts) | paste -sd, -)
most=$(awk -F: '{n=gsub(/running/, "running", $2); if (n>m) {m=n; id=$1}} END{print id}' "$F")
rarest=$(for t in red running shoes shorts; do echo "$(ids $t | wc -l) $t"; done | sort -n | head -1 | awk '{print $2}')
printf 'shoes_docs=%s\nred_and_shorts=%s\nmost_running=%s\nrarest_term=%s\n' "$shoes" "$both" "$most" "$rarest" > "$HOME/sys-lab/answers-search.txt"
cat "$HOME/sys-lab/answers-search.txt"
