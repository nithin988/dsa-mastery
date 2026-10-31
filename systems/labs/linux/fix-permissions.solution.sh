#!/bin/bash
# Solution for the fix-permissions lab.
cd "$HOME/sys-lab/perm"
chmod 755 deploy.sh
chmod 600 secret.key
chmod 770 shared
chmod 644 public/index.html
ls -l deploy.sh secret.key public/index.html
ls -ld shared
