#!/bin/bash
# Solution for the bulk-rename lab.
cd "$HOME/sys-lab/photos"
for f in *.jpeg; do
  mv -- "$f" "${f%.jpeg}.jpg"
done
ls
