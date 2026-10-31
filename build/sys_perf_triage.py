"""Systems Mastery S10: Linux performance triage."""
import sysviz as v

USE_VIZ = v.figure(
    720, 200,
    [v.box(120, 12, 480, 36, "Symptom: \"the server is slow\"", "ink"),
     v.arrow(360, 48, 360, 70),
     v.box(20, 70, 160, 52, "CPU", "acc", "U: busy %  S: run queue"),
     v.box(200, 70, 160, 52, "Memory", "acc", "U: available  S: swapping"),
     v.box(380, 70, 160, 52, "Disk", "acc", "U: %util  S: await"),
     v.box(560, 70, 140, 52, "Network", "acc", "U: bandwidth  S: drops"),
     v.arrow(360, 122, 360, 146),
     v.box(160, 146, 400, 40, "The resource that is saturated is your bottleneck", "ok")],
    "The USE method", "Check utilization, saturation and errors for each resource, then dig only where it is saturated")

MODULE = dict(
    id="pt",
    title="Linux performance triage",
    lead="\"The server is slow\" is not a diagnosis. This module gives you a fixed order of questions (the USE method), a first-60-seconds command checklist, and the skill of reading `vmstat`, `iostat`, `free` and `top` output to decide whether CPU, memory, disk or network is the bottleneck.",
    time="4 to 5 hours",
    why=[
        "At 14:30 the dashboard goes red and everyone says \"the server is slow\". The junior engineer opens `top`, sees a number, and restarts something. The senior engineer runs eight commands in sixty seconds, finds the machine swapping itself to death, and names the one process responsible.",
        "Performance questions are a staple of operations and SRE interviews: \"load average is 20 on a 4-core box, what do you check?\" The answer is a method, not a guess.",
    ],
    outcomes=[
        "Apply the USE method (utilization, saturation, errors) to CPU, memory, disk and network.",
        "Run a first-60-seconds checklist and say what each command tells you.",
        "Read load average, `vmstat`, `iostat`, `free` and `top` without being fooled by the page cache.",
        "Tell a CPU problem from memory pressure, disk saturation and network trouble.",
        "Name the culprit process and the evidence for it.",
    ],
    before=[
        "Earlier modules on processes and memory help, but each idea is re-explained briefly.",
        "Tools: `vmstat`, `free`, `top`, `ps` (procps) and `mpstat`, `iostat`, `pidstat` (the `sysstat` package: `sudo apt install sysstat`). All outputs are from a real machine and **will differ on yours** (numbers change every second); learn to read the shape, not the digits.",
    ],
    env=["Everything is read-only except two tiny load generators that stop themselves."],
    lessons=[
        dict(
            title="The USE method: a map for \"it is slow\"",
            tier="hot",
            situation="Users complain about slowness. You have four suspects (CPU, memory, disk, network) and a clock running. Checking them in random order wastes the clock.",
            learn=["Utilization, saturation and errors", "Why saturation matters more than utilization", "Load average and pressure"],
            model=[
                "For every resource ask three questions: **Utilization** (how busy is it?), **Saturation** (is work waiting in a queue?) and **Errors** (is it failing?). A resource at 60% average utilization can still be saturated in bursts, and saturation is what users feel as slowness. **Load average** counts tasks that are running or waiting; compare it to the core count. On modern kernels **pressure stall information** (`/proc/pressure/*`) states directly how much time tasks spent stalled waiting for CPU, memory or I/O.",
            ],
            analogy="A supermarket: utilization is how many tills are open and busy, saturation is the length of the queue, errors are broken tills.",
            visual=USE_VIZ,
            sim="usegrid",
            groups=[
                dict(title="First numbers", cmds=[
                    dict(volatile=True, c="nproc; cat /proc/loadavg", e="Cores, then the 1, 5 and 15 minute load averages followed by running/total tasks and the last PID. Load near or below the core count is fine; far above means a queue.", parts=[("nproc", "number of CPU cores")]),
                    dict(volatile=True, c="cat /proc/pressure/cpu; cat /proc/pressure/memory", e="Pressure stall information: `some` is the share of time at least one task was stalled. `avg10` means the last 10 seconds. Anything persistently above a few percent means real contention. (Needs a Linux kernel with PSI, version 4.20 or later.)"),
                ]),
            ],
            quick=[
                ("Why can a resource be slow at 60% utilization?", "Work may arrive in bursts that queue (saturation); the average hides the peaks."),
                ("A 4-core server shows load average 18. What does it suggest?", "About 14 more tasks are waiting than there are cores: CPU saturation, or tasks blocked on I/O or memory; check which."),
            ],
            traps=[
                "Linux load average includes tasks blocked on disk I/O, so high load does not always mean busy CPUs.",
                "Averages hide spikes; look at per-second output while the problem is happening.",
            ],
        ),
        dict(
            title="CPU: busy, queued or one core stuck",
            tier="hot",
            situation="CPU is the first thing everybody blames. It is sometimes right, and the numbers tell you which kind of CPU problem it is.",
            learn=["User, system, idle and iowait time", "Run queue and per-core view", "Finding the process"],
            model=[
                "CPU time splits into **user** (your code), **system** (kernel on your behalf), **idle** and **iowait** (idle while waiting for disk). High user time is the application working; high system time means lots of system calls or context switches; high iowait means the CPU is waiting for disk, not busy. In `vmstat`, the **r** column is the run queue: tasks ready to run. `r` above the core count means CPU saturation. **mpstat** shows each core: one core at 100% while the rest idle is a single-threaded bottleneck the average hides.",
            ],
            analogy="A kitchen: busy cooks (user), cooks fetching ingredients from the store room (system), cooks waiting on a delivery (iowait).",
            groups=[
                dict(title="Create load and find it", cmds=[
                    dict(volatile=True, c="(yes > /dev/null &); sleep 2; ps -eo pid,pcpu,comm --sort=-pcpu | head -3; pkill yes", e="We start a CPU burner for two seconds, list processes by CPU share (the burner is at the top near 100%) and stop it. In real life the top line is your suspect.", parts=[("--sort=-pcpu", "highest CPU first"), ("pcpu", "share of CPU time since the process started")]),
                    dict(volatile=True, c="vmstat 1 3", e="One line per second (ignore the first, it is an average since boot). Read: `r` runnable tasks, `b` blocked, `si so` swap in/out, `us sy id wa` CPU split. Idle with a tiny `r` means no CPU problem.", parts=[("1 3", "every 1 second, 3 times")]),
                    dict(volatile=True, c="mpstat -P ALL 1 1 | tail -n +4 | head -4", e="Per core: `%usr %sys %iowait %idle`. If one core is near 100% busy and the others are idle, the program is stuck on a single thread.", parts=[("-P ALL", "every core, not only the average")]),
                ]),
            ],
            quick=[
                ("What does a high `iowait` mean?", "CPUs are idle because tasks are waiting for disk I/O; the disk, not the CPU, is the limit."),
                ("What does `r` greater than the core count in `vmstat` mean?", "More runnable tasks than cores: the CPU is saturated and tasks queue."),
            ],
            traps=[
                "The first line of `vmstat` is an average since boot; it is not the current state.",
                "`top` shows a snapshot; a short burst between refreshes is invisible. Use `pidstat 1` for per-second history.",
            ],
        ),
        dict(
            title="Memory: available, swap and pressure",
            tier="hot",
            situation="`free` shows almost nothing free and someone panics. Or the machine really is out of memory and crawling because it is swapping.",
            learn=["available versus free", "Swapping as saturation", "Finding the biggest process"],
            model=[
                "Linux uses spare RAM as a file cache, so small **free** memory is normal. The honest number is **available** (free plus what can be reclaimed). **Saturation** is swapping: pages being written to (`so`) and read from (`si`) disk continuously. A machine that is swapping heavily is slow because every memory access might become a disk read, and the disk then looks busy as a side effect. The extreme error is the **OOM killer** removing a process (see `dmesg`).",
            ],
            analogy="A desk (RAM) and a filing cabinet (swap): when the desk is overflowing you keep fetching papers from the cabinet and never get any work done.",
            groups=[
                dict(title="Read the memory numbers", cmds=[
                    dict(volatile=True, c="free -m", e="Look at `available`, not `free`, and at `Swap used`. A large `buff/cache` is healthy. Swap used and still growing is the warning.", parts=[("-m", "show megabytes")]),
                    dict(volatile=True, c="ps -eo rss,pmem,comm --sort=-rss | head -4", e="Processes by resident memory (RSS, in KiB), biggest first. This names the heavy user.", parts=[("rss", "memory actually in RAM")]),
                    dict(volatile=True, c="vmstat 1 2 | tail -1 | awk '{print \"swap in:\", $7, \"swap out:\", $8}'", e="The `si` and `so` columns pulled out: both should be 0 on a healthy machine. Non-zero values sustained for many seconds mean the system is swapping."),
                ]),
            ],
            quick=[
                ("Why is low `free` memory usually not a problem?", "Linux fills spare RAM with the page cache; `available` shows what can be handed to programs."),
                ("How do you recognise swap thrashing in `vmstat`?", "Large `si` and `so` values at the same time as high iowait and a growing run queue."),
            ],
            traps=[
                "Judge a process by RSS, not VSZ, and remember shared memory is counted in each user.",
                "Adding swap hides a leak and makes the machine slow instead of failing fast; find the leak.",
            ],
        ),
        dict(
            title="Disk: busy, full or out of inodes",
            tier="hot",
            situation="Writes are slow, or fail with \"No space left on device\" while `df` says there is room. Three different problems share one symptom.",
            learn=["Throughput versus latency (`await`)", "Space and inode exhaustion", "`iostat -x`"],
            model=[
                "Disk problems come in three kinds. **Busy**: `%util` near 100 with a rising `await` (average wait per request) means requests queue; users feel latency. **Full**: `df -h` shows space used, and on some systems a nearly full disk slows down. **Out of inodes**: `df -i` shows file-count capacity; millions of tiny files can fill it while space remains. Always check space *and* inodes when you see \"No space left on device\".",
            ],
            analogy="A warehouse: the loading dock can be jammed (busy), the shelves can be full (space) or the label printer can be out of labels (inodes).",
            groups=[
                dict(title="Space, inodes and speed", cmds=[
                    dict(volatile=True, c="df -h / | tail -1; df -i / | tail -1", e="Space used and inodes used for the root filesystem. Either at 100% causes write failures.", parts=[("df -i", "inode usage instead of space")]),
                    dict(c="mkdir -p ~/perf && dd if=/dev/zero of=~/perf/big bs=1M count=50 status=none && du -sh ~/perf; rm -r ~/perf", e="Make a 50 MB file, measure the folder with `du` (what a directory is using, as opposed to `df` for the whole filesystem), then clean up."),
                    dict(volatile=True, c="iostat -dx 1 2 | awk '/^Device/{n=split($0,h)} /^sd/{for(i=1;i<=n;i++) if(h[i]==\"r/s\"||h[i]==\"w/s\"||h[i]~/await/||h[i]==\"%util\") printf \"%s=%s \", h[i], $i; print $1}' | tail -n 2", e="Per-device operations per second, wait per request (`await`, or `r_await` and `w_await` in newer versions) and `%util`, with the device name last. Sustained `%util` near 100 with a large wait means the disk is saturated. Plain `iostat -dx 1` prints many more columns.", parts=[("-d", "devices only"), ("-x", "extended statistics")]),
                ]),
            ],
            quick=[
                ("\"No space left on device\" but `df -h` shows free space. What next?", "Check inodes with `df -i`; the filesystem may be out of inodes."),
                ("Which `iostat` columns show disk saturation?", "`await` (wait per request) rising together with `%util` near 100."),
            ],
            traps=[
                "A deleted file that a process still holds open keeps using space: compare `df` with `du` and look for open deleted files with `lsof +L1`.",
                "`%util` is misleading on SSDs and arrays that handle many requests in parallel; trust `await`.",
            ],
        ),
        dict(
            title="Network: throughput, drops and sockets",
            tier="sec",
            situation="The CPU and disk look fine but requests are slow or time out. The network has capacity, drops and queues just like the others.",
            learn=["Interface counters", "Socket summary with `ss -s`", "Retransmits as a symptom"],
            model=[
                "For the network, **utilization** is traffic compared to the link speed, **saturation** is drops and queueing (and TCP retransmissions, where the sender resends data that did not arrive), and **errors** are interface error counters. Do a quick look at the interface counters and the socket summary before blaming the application.",
            ],
            analogy="A motorway: capacity (link speed), traffic jams (queues and drops) and accidents (errors).",
            groups=[
                dict(title="Counters and sockets", cmds=[
                    dict(volatile=True, c="ip -s link show lo | head -6", e="Byte and packet counters with `errors` and `dropped` columns. Rising errors or drops mean a problem on that interface.", parts=[("-s", "include statistics")]),
                    dict(volatile=True, c="ss -s | head -4", e="Socket totals by state. Thousands in `timewait` can be normal; a growing `closed` or orphaned count or very high totals warrant a closer look with `ss -tan`."),
                ]),
            ],
            quick=[
                ("What do TCP retransmissions indicate?", "Packets were lost or delayed; the network path (or an overloaded receiver) is struggling."),
            ],
            traps=[
                "Packet loss to one destination can be a remote problem; compare with other destinations before blaming local hardware.",
            ],
        ),
        dict(
            title="The first 60 seconds",
            tier="hot",
            situation="You have just been paged. You do not yet know which resource. A fixed sequence finds the bottleneck fast and keeps you from tunnel vision.",
            learn=["Eight commands in a fixed order", "Reading them together", "From finding to fixing"],
            model=[
                "Run the same short sequence every time: `uptime`, `dmesg | tail`, `vmstat 1`, `mpstat -P ALL 1`, `pidstat 1`, `iostat -xz 1`, `free -m`, `ss -s`. Together they cover all four resources in about a minute. Then **decide**: which resource shows saturation? Dig into that one only. Reading the outputs together matters: high load, high `wa`, heavy `si/so` and a huge process in `top` tell one story (memory), while high `us` and a hot core tell another (CPU).",
            ],
            analogy="A paramedic's checklist: airway, breathing, circulation, in the same order every time, then treat what is wrong.",
            sim="triage60",
            playbook=dict(title="Reading the combination", intro=["Match the pattern you see, then follow the pointer."], rows=[
                ["High load, high `us`, busy `r`", "`pidstat 1`, `top`", "CPU-bound process", "Profile it or scale out; check for runaway loops"],
                ["High load, high `wa`, high `await`", "`iostat -xz 1`, `pidstat -d 1`", "Disk saturation", "Find the heavy writer or reader; faster disk or less I/O"],
                ["High load, `si/so` active, low `available`", "`free -m`, `ps --sort=-rss`", "Memory pressure and swapping", "Find the leak or oversized process; restart or add memory"],
                ["Low CPU and disk, slow requests", "`ss -s`, `sar -n DEV`, retransmits", "Network or a slow dependency", "Check packet loss and the services you call"],
                ["Everything quiet but still slow", "`strace -c`, application logs", "Locks, waiting on a remote service or the app itself", "Profile the application"],
            ]),
            groups=[
                dict(title="The opening moves", cmds=[
                    dict(volatile=True, c="uptime; vmstat 1 3 | tail -2; free -m | head -2", e="Three of the eight in one go: load averages, current CPU, run queue and swap activity, and memory. Even this partial list usually tells you which resource to chase."),
                ]),
            ],
            quick=[
                ("Name four commands from the first-60-seconds list.", "`uptime`, `vmstat 1`, `mpstat -P ALL 1` or `pidstat 1`, `iostat -xz 1`, `free -m`, `ss -s`, `dmesg | tail`."),
                ("After the checklist, what is the next step?", "Identify the saturated resource and investigate only that one in depth."),
            ],
            traps=[
                "Do not restart services before capturing evidence; a restart destroys the very state you need.",
                "Capture the outputs into a file during the incident; you will want them for the postmortem.",
            ],
        ),
    ],
    labs=[
        dict(kind="linux", script="triage-box", dir="triage", title="One box, three hogs",
             goal=["Name the heaviest user of CPU, of memory and of disk space using standard tools."],
             story=["A practice machine has two runaway processes and a data directory that keeps growing. Different tools answer different questions: the busiest CPU process is not necessarily the biggest memory user."],
             tasks=["Find the process using the most CPU.", "Find the process holding the most memory (RSS).", "Find which directory under `~/sys-lab/triage` uses the most disk space.", "Write `cpu=`, `mem=` and `disk=` (just names) into `~/sys-lab/answers-triage.txt`."],
             check="Run the check script.", check_cmd="bash ~/sys-lab/check-triage-box.sh",
             hints=["`ps -eo pcpu,comm --sort=-pcpu | head`", "`ps -eo rss,comm --sort=-rss | head`", "`du -s ~/sys-lab/triage/*/ | sort -rn | head -3`"],
             solution=["CPU: `ps -eo pcpu,comm --sort=-pcpu | head -3` shows `cpuburn`.", "Memory: `ps -eo rss,comm --sort=-rss | head -3` shows `memhog`.", "Disk: `du -s ~/sys-lab/triage/*/ | sort -rn | head -1` shows `spool`.", "Write the three lines to the answers file."],
             cleanup=["pkill -x cpuburn; pkill -x memhog; true"]),
        dict(kind="linux", script="load-detective", dir="captures", title="Diagnose a slow server from its numbers",
             goal=["Read saved `uptime`, `vmstat`, `free`, `top`, `iostat` and `dmesg` output and decide what is wrong."],
             story=["A 4-core server was slow at 14:32. Someone saved the output of the usual commands before restarting it. Nothing is running on your machine: you only have the evidence, which is exactly the interview situation."],
             tasks=["Is the bottleneck cpu, memory, disk or network? Read `vmstat.txt` (`si so`, `wa`) and `free.txt`.", "Which process holds the most memory in `top.txt`?", "How many processes did the kernel kill for lack of memory (`dmesg.txt`)?", "Why is the disk so busy? Write one word.", "Write `bottleneck=`, `culprit=`, `oom_victims=` and `why_disk_busy=` into `~/sys-lab/answers-load.txt`."],
             check="Run the check script.", check_cmd="bash ~/sys-lab/check-load-detective.sh",
             hints=["Load is 18 on 4 cores, but `us` is only 5 to 7 and `wa` is above 80. The CPU is waiting, not working.", "`si` and `so` are huge and `free.txt` shows almost no available memory with swap nearly full.", "The disk is busy because of the swapping: it is a symptom, not the cause."],
             solution=["Bottleneck: memory (swap thrashing).", "Culprit: `java` (5.9 GB resident of 8 GB).", "OOM victims: 2 (`redis-server` and `indexer`).", "The disk activity is `swap`."]),
    ],
    cases=[],
    cheat=[
        ["uptime; cat /proc/loadavg", "load averages, compare with `nproc`"],
        ["vmstat 1", "run queue, swap, I/O wait, CPU split per second"],
        ["mpstat -P ALL 1", "per-core CPU"],
        ["pidstat 1 / pidstat -d 1", "CPU / disk per process over time"],
        ["top, then M or P", "sort by memory or CPU"],
        ["ps -eo pid,pcpu,rss,comm --sort=-pcpu | head", "top CPU processes"],
        ["free -m", "memory: read `available` and swap"],
        ["iostat -xz 1", "disk: await and %util"],
        ["df -h; df -i", "space and inode use"],
        ["du -sh * | sort -h", "what is using the space here"],
        ["ss -s; ip -s link", "socket summary; interface errors and drops"],
        ["dmesg | tail", "kernel messages: OOM, I/O errors"],
        ["cat /proc/pressure/{cpu,memory,io}", "how long tasks were stalled"],
    ],
    interview_intro="Performance questions reward structure: name the method, name the commands, then describe how you would read the combination.",
    interview=[
        dict(q="A server has load average 20 on 4 cores. How do you investigate?",
             a=["Load counts runnable and blocked tasks, so first decide which: `vmstat 1` (`r` runnable versus `b` blocked, `wa`, `si/so`).", "If `r` is high and `us` is high it is CPU: find the process with `pidstat 1` or `top`.", "If `wa` is high or tasks are in D state it is I/O: `iostat -xz 1`, and check whether swapping is the cause with `free` and `si/so`.", "Then act on the resource that is saturated."],
             follow=["Can load be high with idle CPUs?", "What does D state mean?"], mistakes=["Assuming high load always means a busy CPU."],
             angle="Reported by candidates as a typical SRE or systems question at large tech companies; not official."),
        dict(q="What is the USE method?",
             a=["For every resource (CPU, memory, disk, network) check utilization, saturation and errors.", "It gives a complete, fast checklist and focuses on saturation, which is what users feel as slowness."],
             follow=["How does USE differ from the RED method?"], mistakes=["Checking only utilization."]),
        dict(q="free shows only 100 MB free on a 16 GB machine. Is that a problem?",
             a=["Not necessarily: Linux uses spare memory as page cache.", "Check `available`, swap usage and swap activity (`si`, `so`), and memory pressure.", "It is a problem if available is small and the system is swapping or the OOM killer has run."],
             follow=["How can you tell cache from a leak?"], mistakes=["Restarting everything because free is low."]),
        dict(q="The disk is at 100% utilization. How do you find the cause and decide whether it matters?",
             a=["`iostat -xz 1` for `await` and queue; if `await` is large users are affected.", "`pidstat -d 1` or `iotop` to find the process doing the I/O.", "Check whether swapping is the source before blaming the application."],
             follow=["Why is `%util` unreliable on SSDs?"], mistakes=["Ignoring `await`."]),
        dict(q="How do you find which process is using the most memory, CPU and disk?",
             a=["CPU: `ps -eo pcpu,comm --sort=-pcpu | head` or `pidstat 1`.", "Memory: `ps -eo rss,comm --sort=-rss | head`.", "Disk I/O: `pidstat -d 1`; disk space: `du -sh * | sort -h`."],
             follow=["How do you do this inside a container?"], mistakes=["Using VSZ for memory."]),
        dict(q="Everything looks idle but users still see slow requests. What now?",
             a=["The bottleneck may be outside the machine or inside the application: slow dependencies, lock contention, thread pools exhausted.", "Check request latency by component, application logs and traces, and use `strace -c` or a profiler on the process."],
             follow=["How do traces help?"], mistakes=["Concluding \"no problem\" because host metrics are quiet."]),
    ],
    selftest=[
        ("What do the letters U, S and E stand for in the USE method?", "Utilization, Saturation, Errors."),
        ("What is the difference between `free` and `available` memory?", "Free is untouched RAM; available includes memory the kernel can reclaim, such as cache."),
        ("What do `si` and `so` in `vmstat` measure?", "Memory swapped in from disk and out to disk."),
        ("What does `r` in `vmstat` represent?", "Tasks that are runnable and waiting for a CPU (the run queue)."),
        ("Which two `iostat -x` columns show a saturated disk?", "`await` rising together with `%util` near 100."),
        ("What command shows inode usage?", "`df -i`."),
        ("Why can load average be high while CPUs are idle?", "Load includes tasks blocked in uninterruptible I/O sleep."),
        ("What should you do before restarting a misbehaving service?", "Capture evidence (outputs, logs, a heap or thread dump) because a restart destroys the state."),
    ],
    recall=[
        ["USE", "utilization, saturation, errors for each resource"],
        ["load average", "running plus waiting tasks, compare with cores"],
        ["available", "the honest memory number"],
        ["si/so", "swap in/out: memory saturation"],
        ["await", "disk wait per request: disk saturation"],
        ["wa", "CPU idle while waiting for disk"],
        ["df -i", "inode usage"],
        ["first 60 s", "uptime, dmesg, vmstat, mpstat, pidstat, iostat, free, ss"],
    ],
    sources=[
        dict(title="Brendan Gregg: The USE Method", url="https://www.brendangregg.com/usemethod.html", use="The origin and full checklists for Linux", license="Copyright the author; read online", how="Link only"),
        dict(title="Netflix TechBlog: Linux Performance Analysis in 60,000 Milliseconds", url="https://netflixtechblog.com/linux-performance-analysis-in-60-000-milliseconds-accc10403c55", use="The original first-minute command checklist", license="Copyright Netflix; read online", how="Link only; our checklist is written separately"),
        dict(title="Kernel docs: Pressure Stall Information", url="https://docs.kernel.org/accounting/psi.html", use="What `/proc/pressure/*` reports", license="Linux kernel documentation (GPL-2.0)", how="Link only"),
        dict(title="sysstat (iostat, mpstat, pidstat) project", url="https://github.com/sysstat/sysstat", use="The tools used in this module", license="GPL-2.0", how="Link only"),
    ],
    plan=[
        "**Hour 1:** the USE method and the CPU lesson; run `vmstat 1` while you start and stop a load.",
        "**Hour 2:** memory and disk lessons; then Lab 1.",
        "**Hour 3:** network and the first-60-seconds lesson; then Lab 2 (reading evidence).",
        "**Hours 4 and 5:** practise the 60-second sequence on your own machine and say the interview answers out loud.",
    ],
)
