#!/bin/bash
# Solution for the backup-script lab: writes a correct backup.sh.
cat > "$HOME/sys-lab/backup/backup.sh" <<'EOF'
#!/bin/bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "usage: backup.sh SOURCE_DIR DEST_DIR" >&2
  exit 1
fi
src=$1
dest=$2
if [ ! -d "$src" ]; then
  echo "error: $src is not a directory" >&2
  exit 2
fi
mkdir -p "$dest"
count=0
for f in "$src"/*.txt; do
  [ -e "$f" ] || continue
  cp -- "$f" "$dest/"
  count=$((count + 1))
done
echo "copied $count files"
EOF
echo "wrote ~/sys-lab/backup/backup.sh"
