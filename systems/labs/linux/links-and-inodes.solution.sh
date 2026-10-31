#!/bin/bash
# Solution for the links-and-inodes lab.
cd "$HOME/sys-lab/links"
ln report.txt backup.txt
ln -s report.txt latest.txt
rm report.txt
ls -l
cat backup.txt
