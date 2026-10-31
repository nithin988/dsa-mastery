#!/bin/bash
# Lab: diagnose a sick server from saved command output only (no processes are started). Only touches ~/sys-lab.
set -e
L="$HOME/sys-lab"
rm -rf "$L/captures" "$L/check-load-detective.sh" "$L/answers-load.txt"
mkdir -p "$L/captures"
cd "$L/captures"

cat > uptime.txt <<'EOS'
 14:32:07 up 41 days,  3:12,  2 users,  load average: 18.42, 11.07, 4.31
EOS
cat > nproc.txt <<'EOS'
4
EOS
cat > vmstat.txt <<'EOS'
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 3  9 3811204  61240   1020  48120 9120 11870 9800 12400 5100 9400  6  9  4 81  0
 2 11 3821044  58012    980  45220 8870 12210 9440 12880 5320 9120  5 10  3 82  0
 4  8 3830112  57120    960  44120 9340 11100 9630 11990 5210 9650  7  9  2 82  0
EOS
cat > free.txt <<'EOS'
              total        used        free      shared  buff/cache   available
Mem:           7956        7712          58           4          45          61
Swap:          4095        3745         350
EOS
cat > top.txt <<'EOS'
  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
 2211 app       20   0   14.8g   5.9g  12840 D  14.2  75.9  912:10.31 java
 1902 postgres  20   0  2312m  310m   9120 D   3.1   3.9   20:41.07 postgres
  801 root      20   0  250m    11m   4400 S   0.3   0.1    1:04.55 nginx
 2840 app       20   0  4120m  120m   5100 S   0.2   1.5    3:12.20 worker
EOS
cat > iostat.txt <<'EOS'
Device            r/s     w/s   rkB/s   wkB/s  await  %util
sda            512.0   640.0 38400.0 49600.0  184.2   99.8
EOS
cat > dmesg.txt <<'EOS'
[3519201.442] Out of memory: Killed process 1744 (redis-server) total-vm:812344kB, anon-rss:402112kB
[3519350.118] Out of memory: Killed process 1810 (indexer) total-vm:1204412kB, anon-rss:610244kB
[3519602.771] INFO: task postgres:1902 blocked for more than 120 seconds.
EOS

cat > "$L/check-load-detective.sh" <<'EOF'
#!/bin/bash
A="$HOME/sys-lab/answers-load.txt"
ok=1
get() { [ -f "$A" ] && grep "^$1=" "$A" | head -1 | cut -d= -f2-; }
[ "$(get bottleneck)" = "memory" ] && echo "PASS: bottleneck" || { echo "FAIL: bottleneck= must be one of cpu, memory, disk, network. Look at free, vmstat si/so and the process using the most memory."; ok=0; }
[ "$(get culprit)" = "java" ] && echo "PASS: culprit" || { echo "FAIL: culprit= should be the process holding the most memory (RES) in top.txt"; ok=0; }
[ "$(get oom_victims)" = "2" ] && echo "PASS: oom_victims" || { echo "FAIL: oom_victims= should be the number of processes the kernel killed (see dmesg.txt)"; ok=0; }
[ "$(get why_disk_busy)" = "swap" ] && echo "PASS: why_disk_busy" || { echo "FAIL: why_disk_busy= one word: what is causing the heavy disk activity (a hint: look at si and so)"; ok=0; }
[ $ok = 1 ] && { echo "All tasks done."; exit 0; } || exit 1
EOF
chmod +x "$L/check-load-detective.sh"
echo "Lab ready. Read the files in ~/sys-lab/captures: they were taken from a slow 4-core server."
