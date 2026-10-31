#!/bin/bash
# Solution for the read-the-trace lab.
F="$HOME/sys-lab/trace/app.log"
first=$(grep -m1 ' ERROR ' "$F" | awk '{print $2}')
frame=$(grep -A1 -n '^Traceback' "$F" >/dev/null; awk '/^Traceback/{t=1} t&&/File /{last=$0} /^KeyError/{print last; exit}' "$F")
file=$(echo "$frame" | sed 's/.*\/\([a-z_]*\.py\)".*/\1/')
line=$(echo "$frame" | sed 's/.*line \([0-9]*\),.*/\1/')
key=$(grep -m1 '^KeyError' "$F" | sed "s/KeyError: '\(.*\)'/\1/")
printf 'file=%s\nline=%s\nmissing_key=%s\nfirst_error_time=%s\n' "$file" "$line" "$key" "$first" > "$HOME/sys-lab/answers-trace.txt"
cat "$HOME/sys-lab/answers-trace.txt"
