#!/bin/bash
# Systems Mastery: creates ~/workshop, a small practice area for the Linux shell module.
# Safe by design: it only creates and replaces ~/workshop, and refuses to touch a folder it did not create.
set -e
export LC_ALL=C TZ=UTC
W="$HOME/workshop"
MARK="$HOME/.sys-lab-workshop"

if [ -e "$W" ] && [ ! -e "$MARK" ]; then
  echo "~/workshop already exists and was not created by this script. Rename it and run again."
  exit 1
fi

rm -rf "$W"
mkdir -p "$W"/notes "$W"/logs "$W"/bin "$W"/data "$W"/archive

printf 'Buy milk\nCall the bank\nRenew passport\n' > "$W/notes/todo.txt"
printf '# Ideas\n- learn awk\n- build a blog\n' > "$W/notes/ideas.md"
printf '200 /home\n500 /pay\n200 /home\n404 /old\n500 /pay\n500 /cart\n200 /cart\n500 /pay\n' > "$W/logs/access.log"
printf '2026-01-15 ERROR disk almost full\n2026-01-15 INFO backup finished\n2026-01-16 ERROR disk almost full\n' > "$W/logs/app.log"
printf '#!/bin/bash\necho "Hello from the workshop"\n' > "$W/bin/hello.sh"
chmod 755 "$W/bin/hello.sh"
printf 'alice\nbob\ncarol\ndave\n' > "$W/data/names.txt"
printf 'Welcome to the workshop.\nEverything here is safe to break.\n' > "$W/README.txt"
printf 'old backup\n' > "$W/archive/2025.tar.txt"

# fixed timestamps so listings look the same for everyone
find "$W" -exec touch -h -d '2026-01-15 09:30:00' {} +
touch "$MARK"
touch -d '2026-01-15 09:30:00' "$HOME"

echo "Practice area ready: ~/workshop"
