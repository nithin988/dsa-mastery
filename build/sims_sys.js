/* Animations for Systems Mastery modules. Same step format as sims.js:
   {a:[cells], ptr:{label:idx}, hi:[], ok:[], dim:[], aux:{label,items}, note, cols?, graph?:{nodes,edges,directed,w,h}, eok?} */
function rng(x,y){var r=[];for(var i=x;i<=y;i++)r.push(i);return r}
function mapStr(m){var k=Object.keys(m);return '{'+k.map(function(x){return x+':'+m[x]}).join(', ')+'}'}
var SIM={
/* ---- S02: Linux shell ---- */
cdtree:function(){var S=[];
 var nodes=[{x:240,y:30,label:'/'},{x:130,y:88,label:'home'},{x:350,y:88,label:'etc'},{x:130,y:148,label:'me'},{x:130,y:208,label:'work'},{x:40,y:275,label:'logs'},{x:130,y:275,label:'notes'},{x:220,y:275,label:'bin'}];
 var edges=[[0,1],[0,2],[1,3],[3,4],[4,5],[4,6],[4,7]];
 var G={nodes:nodes,edges:edges,w:480,h:310};
 function st(at,cmd,pwd,note,ok){S.push({a:[],graph:G,ptr:{'you are here':at},ok:ok||[],aux:{label:'terminal',items:['$ '+cmd,'pwd → '+pwd]},note:note})}
 st(3,'(shell starts)','/home/me','Every shell session has a current directory ("cwd"). A new session starts in your home directory, written ~ for short. The tree shows the directories we will visit: / is the root of everything.');
 st(4,'cd work','/home/me/work','cd work is a relative path: it starts from where you are now (/home/me) and goes down into work. No leading slash means "relative to here".');
 st(5,'cd logs','/home/me/work/logs','Another relative step. Each cd changes only your current directory, never the files.');
 st(4,'cd ..','/home/me/work','.. always means "the parent directory", one step up the tree. A single . means "here".');
 st(2,'cd /etc','/etc','A path that starts with / is absolute: it starts at the root and works from anywhere, whatever your current directory is.');
 st(3,'cd ~   (or just cd)','/home/me','~ is shorthand for your home directory, and cd with no argument takes you home. Absolute paths never depend on where you are; relative paths always do. That difference explains most "No such file or directory" errors.',[3]);
 return S},
perm:function(){var S=[];
 function row(sym,oct,note,hi,aux){var a=sym.split('');S.push({a:a,ptr:{},hi:hi||[],aux:{label:'permissions',items:aux},note:note})}
 S.push({a:['r','w','x','r','-','x','r','-','-'],ptr:{owner:0,group:3,others:6},aux:{label:'ls -l shows',items:['-rwxr-xr-- 1 me team report.sh']},note:'ls -l prints nine permission characters after the file type. They are three groups of three: what the owner may do, what members of the file group may do, and what everyone else may do. r = read, w = write, x = execute (run, or enter for a directory). A dash means "not allowed".'});
 S.push({a:['r','w','x','r','-','x','r','-','-'],ptr:{owner:0,group:3,others:6},hi:[0,1,2],aux:{label:'owner',items:['r=4 w=2 x=1','4+2+1 = 7']},note:'Each permission has a value: r is 4, w is 2, x is 1. Add up what is allowed in a group to get one digit. The owner has all three: 4+2+1 = 7.'});
 S.push({a:['r','w','x','r','-','x','r','-','-'],ptr:{owner:0,group:3,others:6},hi:[3,4,5],aux:{label:'group',items:['r=4 x=1, no w','4+0+1 = 5']},note:'The group may read and execute but not write: 4+0+1 = 5.'});
 S.push({a:['r','w','x','r','-','x','r','-','-'],ptr:{owner:0,group:3,others:6},hi:[6,7,8],aux:{label:'others',items:['r=4 only','4+0+0 = 4']},note:'Everyone else may only read: 4. Put the three digits together and this file is mode 754: chmod 754 report.sh sets exactly these permissions.'});
 S.push({a:['r','w','-','r','-','-','-','-','-'],ptr:{owner:0,group:3,others:6},hi:[0,1,2,3,4,5,6,7,8],aux:{label:'chmod 640 notes.txt',items:['6 = rw-','4 = r--','0 = ---']},note:'A common pair to remember: 640 (owner reads and writes, group reads, others nothing) for private files, and 755 for programs and directories that everyone may run or enter. Never "fix" an error with chmod 777: it lets everyone write.'});
 S.push({a:['r','w','x','r','-','x','r','-','x'],ptr:{owner:0,group:3,others:6},ok:[2,5,8],aux:{label:'directories',items:['x on a directory = may enter it','r on a directory = may list it']},note:'On a directory, x means you may enter it (cd into it or reach files inside) and r means you may list its names. Missing x on a directory is the classic reason "Permission denied" appears for a file that looks fine.'});
 return S},
pipe:function(){var S=[],raw=['200 /home','500 /pay','200 /home','404 /old','500 /pay','500 /cart','200 /cart','500 /pay'];
 function st(a,cmd,note,hi,dim,ok){S.push({a:a,ptr:{},hi:hi||[],dim:dim||[],ok:ok||[],aux:{label:'pipeline so far',items:[cmd]},note:note})}
 st(raw,'cat access.log','Each program in a pipeline does one small job and passes its output to the next with the | symbol. Here is a tiny web log: a status code and a path per line. Question: which paths fail with status 500, and how often?');
 var g=raw.map(function(x,i){return x.indexOf('500')===0?-1:i}).filter(function(i){return i>=0});
 st(raw,'cat access.log | grep "^500"','grep keeps only the lines that match. The five lines that do not start with 500 are dropped.',[1,4,5,7],g);
 var k=['500 /pay','500 /pay','500 /cart','500 /pay'];
 st(['500 /pay','500 /pay','500 /cart','500 /pay'],'… | grep "^500"','Only four lines are passed on. The next program receives exactly these.',rng(0,3));
 st(['/pay','/pay','/cart','/pay'],'… | cut -d" " -f2','cut splits each line on spaces (-d" ") and keeps the 2nd field (-f2): the path.',rng(0,3));
 st(['/cart','/pay','/pay','/pay'],'… | sort','uniq only compares neighbouring lines, so identical lines must be next to each other first. sort puts them in order.',[1,2,3]);
 st(['1 /cart','3 /pay'],'… | uniq -c','uniq -c collapses neighbouring duplicates and prefixes a count: /pay failed 3 times, /cart once.',[1],[],[1]);
 st(['3 /pay','1 /cart'],'… | sort -rn','sort -rn sorts numerically, biggest first. Four tiny tools, one pipeline: "top failing paths". This is the Unix idea: small tools that do one thing, joined together.',[0],[],[0]);
 return S},
/* ---- S03: text processing and scripting ---- */
awkf:function(){var S=[],rows=['alice 42 eng','bob 17 ops','carol 63 eng','dave 8 ops'];
 function f(i){return rows[i].split(' ')}
 S.push({a:rows,ptr:{},aux:{label:'input: name, score, team',items:['awk reads one line at a time']},note:'awk is a tiny programming language built for columns of text. It reads input one line (a "record") at a time and splits each line into fields on whitespace: $1 is the first field, $2 the second, and $0 is the whole line.'});
 rows.forEach(function(r,i){var fs=f(i);S.push({a:rows,ptr:{'line':i},hi:[i],aux:{label:'line '+(i+1)+' split into fields',items:['$1 = '+fs[0],'$2 = '+fs[1],'$3 = '+fs[2],'NR = '+(i+1)]},note:'awk \'{print $1, $3}\' prints fields 1 and 3 of every line. For line '+(i+1)+' that is: '+fs[0]+' '+fs[2]+'.'})});
 S.push({a:['alice eng','bob ops','carol eng','dave ops'],ptr:{},ok:[0,1,2,3],aux:{label:'output',items:['awk \'{print $1, $3}\' people.txt']},note:'Output is one printed line per input line. Use -F to change the separator: awk -F, \'{print $2}\' file.csv splits on commas instead of whitespace.'});
 return S},
awksum:function(){var S=[],sc=[42,17,63,8],sum=0,cnt=0;
 S.push({a:['BEGIN','line 1','line 2','line 3','line 4','END'],ptr:{},aux:{label:'program',items:['awk \'{sum += $2; n++} END {print sum, sum/n}\'']},note:'An awk program is pattern { action } pairs. Here the action has no pattern, so it runs for every line. BEGIN runs once before the first line, END once after the last. Variables start at 0 or empty and need no declaration.'});
 sc.forEach(function(v,i){sum+=v;cnt++;S.push({a:['BEGIN','line 1','line 2','line 3','line 4','END'],ptr:{now:i+1},hi:[i+1],ok:rng(0,i),aux:{label:'variables',items:['$2 = '+v,'sum = '+sum,'n = '+cnt]},note:'Line '+(i+1)+': add $2 ('+v+') to sum, giving '+sum+', and count it. awk keeps the variables between lines.'})});
 S.push({a:['BEGIN','line 1','line 2','line 3','line 4','END'],ptr:{END:5},hi:[5],ok:rng(0,4),aux:{label:'END prints',items:[sum+' '+(sum/cnt)]},note:'After the last line END runs: it prints the total ('+sum+') and the average ('+(sum/cnt)+'). Summing a column is the single most common awk job: totals, averages, counts per group.'});
 return S},
sedsub:function(){var S=[],line='ERROR: disk full on /var',steps=[
 ['s/ERROR/WARN/','WARN: disk full on /var','s/old/new/ replaces the first match on each line. The pattern between the first two slashes is a regular expression; the text between the last two is the replacement.'],
 ['s/disk/DISK/g','ERROR: DISK full on /var','Add g (global) to replace every match on the line, not only the first.'],
 ['s#/var#/srv#','ERROR: disk full on /srv','Any character can be the delimiter. When the text contains slashes, # keeps the command readable.'],
 ['/disk/d','(line deleted)','A pattern before a command picks which lines it applies to. /disk/d deletes every line that contains disk.'],
 ['-n \'/ERROR/p\'','ERROR: disk full on /var','-n turns off automatic printing and p prints only the lines you select: this makes sed behave like grep.']];
 S.push({a:[line],ptr:{input:0},aux:{label:'input line',items:[line]},note:'sed is a stream editor: it reads text line by line, applies edit commands, and writes the result. It never changes the input file unless you use -i. The most important command is s (substitute).'});
 steps.forEach(function(s){S.push({a:[s[1]],ptr:{result:0},hi:[0],aux:{label:'sed '+s[0],items:['input:  '+line,'output: '+s[1]]},note:s[2]})});
 S.push({a:[line],ptr:{},ok:[0],aux:{label:'in place',items:['sed -i.bak \'s/ERROR/WARN/\' app.log']},note:'sed -i edits the file in place. Always give a backup suffix (-i.bak) when you are not sure: there is no undo, and the -i syntax differs slightly between Linux and macOS.'});
 return S},
xargs:function(){var S=[],files=['a.tmp','b.tmp','c.tmp','d.tmp','e.tmp'];
 S.push({a:files,ptr:{},aux:{label:'find . -name "*.tmp" prints one name per line',items:['xargs turns those lines into arguments']},note:'Some commands take their input as arguments, not as text on stdin (rm, mv, cp, mkdir). A pipe cannot feed those directly. xargs reads lines from stdin and builds a command line from them.'});
 S.push({a:files,ptr:{},hi:rng(0,4),aux:{label:'… | xargs rm',items:['rm a.tmp b.tmp c.tmp d.tmp e.tmp']},note:'By default xargs packs as many names as fit onto one command: a single rm with five arguments.'});
 S.push({a:files,ptr:{'run 1':0},hi:[0,1],ok:[],aux:{label:'… | xargs -n 2 echo',items:['echo a.tmp b.tmp','echo c.tmp d.tmp','echo e.tmp']},note:'-n 2 limits each run to two arguments, so xargs makes three commands. Use it to see what will happen before you run something destructive.'});
 S.push({a:files,ptr:{},ok:rng(0,4),aux:{label:'file names with spaces',items:['find ... -print0 | xargs -0 rm']},note:'A file called "my notes.tmp" would be split into two arguments. The safe pair is find -print0 (separate names with a NUL byte) and xargs -0 (read NUL-separated input). Make it a habit.'});
 return S},
/* ---- S04: Linux system internals ---- */
procstate:function(){var S=[],st=['created','running','sleeping','stopped','zombie','gone'];
 function s(at,ok,aux,note,dim){S.push({a:st,ptr:{'PID 4242':at},hi:[at],ok:ok||[],dim:dim||[],aux:{label:'process 4242',items:aux},note:note})}
 s(0,[],['ps STAT: -','parent: the shell (PID 900)'],'Every process is created by another process. The shell calls fork(): the kernel makes a near-copy of itself (the child, PID 4242) and the child then calls exec() to replace its program with the command you typed. Until it is scheduled it is just "created".');
 s(1,[],['ps STAT: R','using the CPU'],'Running (R): the process is on a CPU, or ready and waiting for its turn. The scheduler hands out CPU time in slices; "running" does not mean "using 100% CPU all the time".');
 s(2,[],['ps STAT: S (or D)','waiting for disk or network'],'Sleeping (S): the process asked for something slow (a file read, a network packet, a timer) and the kernel parked it. A sleeping process costs no CPU. D means uninterruptible sleep, usually disk I/O: it cannot be killed until the I/O returns, and many of them is a sign of a stuck disk or NFS.');
 s(1,[],['ps STAT: R','data arrived'],'The data arrived, so the kernel wakes the process and it runs again. Most processes spend most of their life alternating between running and sleeping.');
 s(3,[],['ps STAT: T','pressed Ctrl-Z'],'Stopped (T): Ctrl-Z sends SIGTSTP. The process is frozen in memory, not running, not dead. fg or bg (which send SIGCONT) resume it.');
 s(1,[],['ps STAT: R','fg resumed it'],'SIGCONT resumes it. Nothing was lost.');
 s(4,[],['ps STAT: Z','exited, parent has not called wait()'],'Zombie (Z): the process has exited, but its parent has not yet collected its exit code with wait(). The kernel keeps a tiny entry so the parent can still learn how it ended. A zombie uses no CPU or memory; a pile of them means the parent has a bug.');
 s(5,[4],['entry removed','parent called wait()'],'The parent calls wait(), reads the exit status, and the kernel removes the entry. If the parent dies first, the orphan is adopted by PID 1 (init or systemd), which always reaps its children. You cannot kill a zombie, only fix or kill its parent.');
 return S},
signals:function(){var S=[],sg=['SIGINT 2','SIGTERM 15','SIGKILL 9','SIGSTOP 19','SIGHUP 1','SIGCHLD 17'];
 function s(at,aux,note,ok,dim){S.push({a:sg,ptr:{sent:at},hi:[at],ok:ok||[],dim:dim||[],aux:{label:'signal',items:aux},note:note})}
 S.push({a:sg,ptr:{},aux:{label:'signals',items:['a signal = a tiny message the kernel delivers to a process']},note:'A signal is an asynchronous message to a process: "interrupt", "please stop", "stop now". The process may have a handler that runs when the signal arrives, or it may use the default action (usually terminate). Two signals can never be caught: SIGKILL and SIGSTOP.'});
 s(0,['sent by: Ctrl-C','can be caught: yes','default: terminate'],'SIGINT (2) is what Ctrl-C sends: "the user wants you to stop". Programs may catch it to clean up first. A well-written program flushes its files and exits.');
 s(1,['sent by: kill PID (the default)','can be caught: yes','default: terminate'],'SIGTERM (15) is the polite request "please shut down". It is what kill, systemd and Kubernetes send first. A good service catches it, finishes in-flight work, releases locks and exits.',[1]);
 s(2,['sent by: kill -9 PID','can be caught: NO','default: terminate immediately'],'SIGKILL (9) cannot be caught, blocked or ignored: the kernel removes the process. It gets no chance to clean up, so temp files, locks and half-written data are left behind. Use it only after SIGTERM has failed.',[],[0,1]);
 s(3,['sent by: kill -STOP PID','can be caught: NO','effect: freeze'],'SIGSTOP (19) freezes a process and cannot be caught either; SIGCONT (18) resumes it. Debuggers and job control use this pair.');
 s(4,['sent when: the terminal closes','can be caught: yes','default: terminate'],'SIGHUP (1) historically meant "the terminal hung up", which is why background jobs die when you close an SSH session unless you use nohup or tmux. Many daemons reuse it to mean "reload your configuration".');
 s(5,['sent by: the kernel to a parent','can be caught: yes','default: ignore'],'SIGCHLD (17) tells a parent that one of its children has stopped or exited. A parent that handles it (by calling wait) avoids zombies.');
 S.push({a:sg,ptr:{},ok:[1],aux:{label:'rule of thumb',items:['TERM first, wait, then KILL only if needed']},note:'Order of escalation when stopping a process: SIGTERM, wait several seconds, then SIGKILL. Exit codes show how a process ended: 128 plus the signal number, so 143 means it was killed by SIGTERM and 137 by SIGKILL.'});
 return S},
inode:function(){var S=[];
 function G(nodes,edges,dirs){return {nodes:nodes,edges:edges,directed:true,w:430,h:230}}
 var N=[{x:70,y:35,label:'name A'},{x:70,y:115,label:'name B'},{x:70,y:195,label:'sym S'},{x:240,y:75,label:'inode'},{x:380,y:75,label:'data'}];
 function st(nodes,edges,ptr,aux,note,ok,dim){S.push({a:[],graph:{nodes:nodes,edges:edges,directed:true,w:430,h:230},ptr:ptr,ok:ok||[],dim:dim||[],aux:{label:'filesystem',items:aux},note:note})}
 st([N[0],N[3],N[4]],[[0,1],[1,2]],{'link count 1':1},['echo hi > A','stat A: links = 1'],'A file has two parts: its data blocks on disk, and an inode that stores everything about the file except its name (size, owner, permissions, where the blocks are). The name lives in a directory entry that points to the inode.');
 st([N[0],N[1],N[3],N[4]],[[0,2],[1,2],[2,3]],{'link count 2':2},['ln A B','stat A: links = 2'],'A hard link (ln A B) is a second name for the same inode. There is no "original": A and B are equal names for one file, and the inode now counts two links. Edit through either name and both see it.',[2]);
 st([N[0],N[1],N[2],N[3],N[4]],[[0,3],[1,3],[3,4],[2,0]],{'link count 2':3},['ln -s A S','S is a tiny file that contains the text "A"'],'A symbolic link (ln -s A S) is different: a small file whose content is a path. It points to a NAME, not an inode. It has its own inode and does not change A\'s link count.',[3]);
 st([N[1],N[2],N[3],N[4]],[[0,2],[2,3]],{'link count 1':2},['rm A','B still works; S is now dangling'],'Delete name A. The inode still has one link (B), so the data survives and B works. S pointed to the name A, which no longer exists: it is now a dangling symlink and reading it fails.',[1],[1]);
 st([N[2],N[3]],[],{'link count 0':1},['rm B','data blocks freed'],'Delete the last name and the link count drops to 0. The kernel frees the inode and its data. One more subtlety: if a process still has the file open, the data stays until it closes it, which is why deleting a huge log may not free disk space until the program is restarted.',[],[]);
 return S},
mem:function(){var S=[],n=12;
 function row(kernel,app,cache,free){var a=[],i;for(i=0;i<kernel;i++)a.push('kernel');for(i=0;i<app;i++)a.push('app');for(i=0;i<cache;i++)a.push('cache');for(i=0;i<free;i++)a.push('free');return a}
 function s(k,a,c,f,aux,note,ok,dim){var arr=row(k,a,c,f);S.push({a:arr,cols:6,ptr:{},ok:ok||[],dim:dim||[],aux:{label:'free -m (in blocks)',items:aux},note:note})}
 s(1,2,0,9,['used: 3','free: 9','buff/cache: 0','available: 9'],'Physical memory (RAM), drawn as 12 blocks. The kernel uses some, applications use some, and the rest is free. The kernel does not like wasted RAM, as the next step shows.');
 s(1,2,5,4,['used: 3','free: 4','buff/cache: 5','available: 9'],'A program reads a big file. The kernel keeps those disk pages in the page cache so the next read is instant. Now "free" is small, which looks alarming, but the cache can be dropped at any moment. The column that matters is available: free plus reclaimable cache.',[3,4,5,6,7],[]);
 s(1,5,4,2,['used: 6','free: 2','buff/cache: 4','available: 6'],'Applications ask for more memory, so the kernel quietly shrinks the cache to satisfy them. Reading free: "used" excludes cache, "available" is the honest number for "how much can new programs get".');
 s(1,8,1,2,['used: 9','free: 2','buff/cache: 1','available: 3'],'Pressure rises. The cache is nearly gone. If the system has swap, the kernel starts moving the least-used application pages to disk. That keeps programs alive but makes them very slow, and heavy swapping (thrashing) is a classic cause of "the server is crawling".');
 s(1,11,0,0,['used: 12','free: 0','available: 0','swap: full'],'Nothing left to reclaim and no swap left. The kernel cannot satisfy an allocation.',[],[]);
 s(1,6,0,5,['OOM killer chose the biggest app','available: 5'],'The kernel\'s last resort is the OOM killer: it picks a process (by memory use and an adjustable score) and kills it with SIGKILL to free memory. Look for "Out of memory: Killed process" in dmesg or the journal. In containers the same happens at the memory limit of the cgroup, which is why a pod dies with exit code 137.',[1,2,3,4,5,6,7],[]);
 return S},
/* ---- S05 / S06: Git ---- */
git3:function(){var S=[],A=['Working directory','Staging area','Repository'];
 function s(vals,hi,ok,dim,aux,note){S.push({a:A.map(function(n,i){return n+'\n'+vals[i]}),ptr:{},hi:hi,ok:ok,dim:dim,aux:{label:'hello.txt',items:aux},note:note})}
 s(['v1','v1','v1'],[],[0,1,2],[],['all three agree','git status: nothing to commit'],'Git keeps your work in three places. The working directory is the files you edit. The staging area (also called the index) is a draft of your next commit. The repository is the permanent history. Right now hello.txt is version 1 everywhere.');
 s(['v2','v1','v1'],[0],[],[],['edited in the working directory','git status: modified, not staged'],'You edit hello.txt. Only the working directory changed. Git notices the difference and reports "Changes not staged for commit".');
 s(['v2','v2','v1'],[1],[],[],['git add hello.txt','git status: Changes to be committed'],'git add copies the current content into the staging area. You decide exactly what goes into the next commit: staging lets you commit part of your work and leave the rest.');
 s(['v2','v2','v2'],[2],[0,1,2],[],['git commit -m "Update hello"','new commit created'],'git commit takes everything in the staging area and saves it as a new, permanent snapshot in the repository, with a message, an author, a time and a parent. All three places agree again.');
 s(['v3','v2','v2'],[0],[],[],['edited again','working = v3, others = v2'],'Another edit makes the working copy differ again.');
 s(['v2','v2','v2'],[0],[0,1,2],[],['git restore hello.txt','v3 is gone, for good'],'git restore hello.txt throws the edit away and copies the staged version back into the working directory. This is one of the few Git commands that can lose work: the discarded edit was never committed, so there is no way back. Commit often to stay safe.');
 return S},
commits:function(){var S=[];
 var N=[{x:50,y:100,label:'C1'},{x:140,y:100,label:'C2'},{x:230,y:100,label:'C3'},{x:320,y:45,label:'F1'},{x:320,y:155,label:'M1'},{x:410,y:100,label:'MC'}];
 function G(nodes,edges){return {nodes:nodes,edges:edges,directed:true,w:470,h:200}}
 function s(ns,es,ptr,ok,aux,note){S.push({a:[],graph:G(ns,es),ptr:ptr,ok:ok||[],aux:{label:'git log --graph',items:aux},note:note})}
 s(N.slice(0,3),[[1,0],[2,1]],{'main, HEAD':2},[],['C1 <- C2 <- C3','arrows point to the PARENT'],'A commit is a snapshot plus a pointer to its parent. The arrows in Git run from child to parent, because a commit knows where it came from but not what comes after. A branch is just a movable label on a commit; HEAD says which branch you are on.');
 s(N.slice(0,3),[[1,0],[2,1]],{main:2,'feature, HEAD':2},[],['git switch -c feature','a new label, no new commits'],'git switch -c feature creates a new branch label on the same commit and moves HEAD to it. Branches are cheap because nothing is copied: it is only a 40-character pointer.');
 s(N.slice(0,4),[[1,0],[2,1],[3,2]],{main:2,'feature, HEAD':3},[],['git commit (on feature)','feature moves forward, main stays'],'A new commit F1 is made while you are on feature, so the feature label moves forward to F1. main stays where it was. The two lines of work are now independent.');
 s(N.slice(0,5),[[1,0],[2,1],[3,2],[4,2]],{'main, HEAD':4,feature:3},[],['git switch main; git commit','history has diverged'],'Meanwhile someone commits M1 on main. Both F1 and M1 have C3 as their parent: the history has diverged into two branches that each contain something the other lacks.');
 s(N,[[1,0],[2,1],[3,2],[4,2],[5,4],[5,3]],{'main, HEAD':5,feature:3},[5],['git merge feature','MC has TWO parents'],'git merge feature creates a merge commit MC with two parents (M1 and F1) that combines both lines of work. If main had not moved, Git would simply slide the main label forward ("fast-forward") and create no merge commit. A conflict only appears when both sides changed the same lines.');
 return S},
remote:function(){var S=[];
 var N=[{x:50,y:100,label:'C1'},{x:140,y:100,label:'C2'},{x:230,y:100,label:'C3'},{x:320,y:100,label:'C4'},{x:410,y:100,label:'C5'}];
 function G(n,e){return {nodes:N.slice(0,n),edges:e,directed:true,w:470,h:190}}
 function s(n,e,ptr,ok,aux,note){S.push({a:[],graph:G(n,e),ptr:ptr,ok:ok||[],aux:{label:'local repository',items:aux},note:note})}
 s(3,[[1,0],[2,1]],{'main, HEAD, origin/main':2},[],['you and the server agree'],'A remote (usually called origin) is another copy of the repository, for example on GitHub. origin/main is your local, read-only bookmark of where main was on the server the last time you talked to it. Right now everything matches.');
 s(3,[[1,0],[2,1]],{'main, HEAD, origin/main':2},[],['teammate pushes C4 to the server','you cannot see it yet'],'A teammate pushes a new commit C4 to the server. Your computer does not know yet: Git never talks to the network unless you ask. Your origin/main bookmark is stale.');
 s(4,[[1,0],[2,1],[3,2]],{'main, HEAD':2,'origin/main':3},[3],['git fetch','C4 downloaded, origin/main moved'],'git fetch downloads the new commits and moves origin/main to C4, but changes none of your own branches or files. It is always safe. git status now says "Your branch is behind origin/main by 1 commit".');
 s(4,[[1,0],[2,1],[3,2]],{'main, HEAD, origin/main':3},[3],['git pull   (fetch + merge)','main fast-forwards to C4'],'git pull is fetch followed by merge (or rebase if you configure it). Because you had no commits of your own, main simply fast-forwards to C4.');
 s(5,[[1,0],[2,1],[3,2],[4,3]],{'main, HEAD':4,'origin/main':3},[4],['you commit C5','ahead of origin/main by 1'],'You make a commit C5. Your main is now one commit ahead of origin/main. Nobody else can see C5 yet.');
 s(5,[[1,0],[2,1],[3,2],[4,3]],{'main, HEAD, origin/main':4},[4],['git push','server now has C5'],'git push uploads C5 and moves the server\'s main, and your origin/main bookmark, to C5. If a teammate had pushed first, the push would be rejected ("non-fast-forward") and you would fetch, integrate their work and push again. Never fix that with a force push on a shared branch.');
 return S},
rebase:function(){var S=[];
 var N=[{x:40,y:105,label:'C1'},{x:130,y:105,label:'C2'},{x:220,y:105,label:'C3'},{x:130,y:35,label:'F1'},{x:220,y:35,label:'F2'},{x:310,y:105,label:"F1'"},{x:400,y:105,label:"F2'"}];
 function G(ns,es){return {nodes:ns,edges:es,directed:true,w:470,h:170}}
 function s(ns,es,ptr,ok,dim,aux,note){S.push({a:[],graph:G(ns,es),ptr:ptr,ok:ok||[],dim:dim||[],aux:{label:'history',items:aux},note:note})}
 s(N.slice(0,5),[[1,0],[2,1],[3,0],[4,3]],{main:2,'feature, HEAD':4},[],[],['feature branched off C1','main has moved on to C3'],'Your feature branch was created from C1, but main has since gained C2 and C3. You want your work on top of the latest main before opening a pull request.');
 s(N.slice(0,5).concat([N[5]]),[[1,0],[2,1],[3,0],[4,3],[5,2]],{main:2,'feature, HEAD':4},[5],[3,4],['git rebase main','replaying F1 on top of C3'],'git rebase main takes each of your commits and replays them, one at a time, on top of the new base. The first replay produces F1\' (F1 prime): the same change, but a brand new commit with a different parent and therefore a different hash.');
 s(N,[[1,0],[2,1],[3,0],[4,3],[5,2],[6,5]],{main:2,'feature, HEAD':6},[5,6],[3,4],['feature now = C3 + F1\' + F2\'','old F1, F2 are abandoned'],'F2 is replayed too. The feature label moves to F2\'. The old F1 and F2 still exist (the reflog remembers them) but nothing points at them, so they fade away. The history is now one straight line, which makes it easy to read and to fast-forward merge.');
 s(N,[[1,0],[2,1],[3,0],[4,3],[5,2],[6,5]],{'main, feature':6,HEAD:6},[6],[3,4],['git switch main; git merge feature','fast-forward, no merge commit'],'Merging the rebased branch into main is a fast-forward: main just slides forward to F2\'. Result: a linear history. Trade-off: rebase rewrites commits, so never rebase a branch other people already based work on.');
 return S},
reset:function(){var S=[],A=['HEAD (last commit)','Staging area','Working directory'];
 function s(v,hi,dim,aux,note){S.push({a:A.map(function(n,i){return n+'\n'+v[i]}),ptr:{},hi:hi,dim:dim,ok:[],aux:{label:'file content',items:aux},note:note})}
 s(['v2','v2','v2'],[],[],['history: v1 <- v2','git reset HEAD~1 undoes the last commit'],'Setup: two commits, v1 then v2 (HEAD). The three areas all hold v2. git reset moves the branch pointer back to an earlier commit. The three modes differ in how far the change is rolled back in the other two areas.');
 s(['v1','v2','v2'],[0],[],['git reset --soft HEAD~1','commit undone, changes stay STAGED'],'--soft moves only HEAD. The commit is gone from history, but its changes are still staged, ready to commit again. Use it to redo a commit message or to squash the last commits into one.');
 s(['v1','v1','v2'],[0,1],[],['git reset --mixed HEAD~1   (the default)','commit undone, changes stay in the files'],'--mixed (the default) also resets the staging area. The changes are still in your working files but are no longer staged. Use it to split one big commit into several.');
 s(['v1','v1','v1'],[0,1,2],[2],['git reset --hard HEAD~1','commit undone, edits DISCARDED'],'--hard resets everything, including your working files: uncommitted edits are lost for good. It is the dangerous one. The undone commit itself can still be rescued from the reflog, but uncommitted work cannot.');
 s(['v2','v2','v2'],[],[0,1,2],['git revert HEAD','safe on shared branches'],'On a branch others use, do not reset. git revert makes a NEW commit that undoes an old one, leaving history intact and every clone consistent. Reset rewrites history; revert adds to it.');
 return S},
reflog:function(){var S=[];
 function cells(n){var all=['reflog: reset --hard HEAD~2','reflog: commit "Add search"','reflog: commit "Add login"','reflog: commit "Init"'];return all.slice(4-n)}
 function s(a,tip,hi,ok,dim,aux,note){S.push({a:a,ptr:tip,hi:hi,ok:ok,dim:dim,aux:{label:'git log vs git reflog',items:aux},note:note})}
 s(['Init','Add login','Add search'],{'main (tip)':2},[],[],[],['git log: Add search, Add login, Init'],'Three commits on main. You think the last two are rubbish and run git reset --hard HEAD~2.');
 s(['Init','Add login','Add search'],{'main (tip)':0},[0],[],[1,2],['git log: Init only','"Add login" and "Add search" look gone'],'The branch label moved back to Init. git log no longer shows the two commits. It looks like they were destroyed, but only the label moved: the commits are still in the object database.');
 s(['reset: moving to HEAD~2','commit: Add search','commit: Add login','commit: Init'],{'HEAD@{0}':0,'HEAD@{1}':1},[1],[],[],['git reflog','a journal of where HEAD has been'],'The reflog is Git\'s private journal of every place HEAD and each branch pointed, kept locally for about 90 days. It shows that two entries ago HEAD was on "Add search". This is how you find a lost commit.');
 s(['reset: moving to HEAD~2','commit: Add search','commit: Add login','commit: Init'],{'HEAD@{1}':1},[],[1],[],['git reset --hard HEAD@{1}','branch restored to "Add search"'],'git reset --hard HEAD@{1} (or git switch -c rescued <hash>) points the branch at the old commit again. Nothing was lost. The limits: the reflog is local to your machine, it expires, and it cannot restore edits that were never committed.');
 return S},
bisect:function(){var S=[],c=['c1','c2','c3','c4','c5','c6','c7','c8'];
 function s(ptr,ok,dim,hi,aux,note){S.push({a:c.slice(),ptr:ptr,ok:ok,dim:dim,hi:hi,aux:{label:'git bisect',items:aux},note:note})}
 s({good:0,bad:7},[0],[],[],['git bisect start; git bisect bad; git bisect good c1','8 commits between'],'The test passed at c1 and fails at c8, and somewhere in between a commit broke it. Looking at them one by one takes up to 7 tests. git bisect does a binary search: each test halves the suspects, so n commits need only about log2(n) tests (a thousand commits need ten).');
 s({good:0,testing:3,bad:7},[0],[4,5,6],[3],['test c4 ... passes: git bisect good','suspects: c5 to c8'],'Git checks out the middle commit, c4. You run the test: it passes, so the bug was introduced after c4. Four commits are ruled out in one step.');
 s({good:3,testing:5,bad:7},[0,1,2,3],[6],[5],['test c6 ... fails: git bisect bad','suspects: c5 and c6'],'Next middle is c6: the test fails, so the bug is in c5 or c6.');
 s({good:3,testing:4,bad:5},[0,1,2,3],[6,7],[4],['test c5 ... passes: git bisect good','first bad commit: c6'],'c5 passes and c6 fails: c6 is the commit that introduced the bug. Three tests instead of seven. git bisect run ./test.sh automates all of it: Git runs your script at every step and reports the first bad commit by itself.');
 S.push({a:c.slice(),ptr:{'first bad':5},ok:[0,1,2,3,4],dim:[],hi:[5],aux:{label:'finish',items:['git bisect reset  (return to your branch)']},note:'Read the culprit with git show c6: now you know exactly who changed what, and when. Always finish with git bisect reset to go back to your branch.'});
 return S},
/* ---- S01: how a computer runs programs ---- */
forkexec:function(){var S=[];
 function G(nodes,edges){return {nodes:nodes,edges:edges,directed:true,w:460,h:140}}
 var sh={x:90,y:60,label:'bash'},ch={x:250,y:60,label:'bash'},ls={x:250,y:60,label:'ls'},k={x:380,y:160,label:'kernel'};
 function st(g,ptr,aux,note,ok,dim){S.push({a:[],graph:g,ptr:ptr,ok:ok||[],dim:dim||[],aux:{label:'process table',items:aux},note:note})}
 st(G([sh],[]),{'PID 100':0},['PID 100  bash  (your shell)','waiting for you to type'],'You type ls and press Enter. The shell is a program like any other: a process (here PID 100) that read your line. It does not contain code for ls. To run another program it asks the kernel to create a new process.');
 st(G([sh,ch],[[0,1]]),{'PID 100':0,'PID 101':1},['fork() returned in both processes','101 is a copy of 100'],'Step 1, fork(): the kernel makes a near-copy of the calling process. The child (PID 101) has the same memory contents, the same open files and the same code as the shell. fork returns 0 in the child and the child\'s PID in the parent, which is how each knows who it is.',[1]);
 st(G([sh,ls],[[0,1]]),{'PID 100':0,'PID 101':1},['PID 101  ls   (after exec)','same PID, new program'],'Step 2, exec(): the child asks the kernel to replace its program with /bin/ls. The process keeps its PID and its open files, but its code, stack and heap are thrown away and replaced. This fork-then-exec pair is how almost every program on Linux starts.',[1]);
 st(G([sh,ls],[[0,1]]),{'PID 100':0,'PID 101':1},['101 runs: lists files','100 sleeps in wait()'],'While ls runs, the shell calls wait() and sleeps, using no CPU. This is why your prompt does not return until the command ends. Adding & at the end of a command simply skips the wait.',[1],[0]);
 st(G([sh,ls],[[0,1]]),{'PID 100':0,'PID 101 exit 0':1},['101 exited with status 0','entry kept until 100 reads it'],'ls finishes and exits with a status code (0 means success). The kernel keeps a small record of the dead child until its parent collects the status.',[0],[1]);
 st(G([sh],[]),{'PID 100':0},['wait() returned: $? = 0','prompt is back'],'wait() returns, the shell stores the status in $?, the dead child\'s record is removed, and the prompt comes back. Every command you have ever typed went through exactly this cycle: fork, exec, wait.',[0]);
 return S},
syscall:function(){var S=[],c=['openat','read','write','close','exit'];
 function s(at,aux,note,ok,dim){S.push({a:c,ptr:{now:at},hi:[at],ok:ok||[],dim:dim||[],aux:{label:'cat notes.txt',items:aux},note:note})}
 S.push({a:c,ptr:{},aux:{label:'cat notes.txt',items:['a program cannot touch the disk itself']},note:'A normal program runs in user mode: it can compute, but it cannot read a disk, send a packet or create a process. Only the kernel can. A system call is the controlled doorway: the program asks, the CPU switches into kernel mode, the kernel checks permissions and does the work, then switches back.'});
 s(0,['openat("notes.txt") = 3','kernel finds the file, checks permissions','returns file descriptor 3'],'cat first asks the kernel to open the file. The kernel checks that you may read it and returns a small number, a file descriptor (3 here; 0, 1 and 2 are already stdin, stdout and stderr). If you may not read it, the call fails with "Permission denied" and the program has to deal with that.');
 s(1,['read(3) = 64 bytes','data copied from the page cache'],'cat asks for the next bytes from descriptor 3. The kernel copies them from its page cache (or the disk if they are not cached) into cat\'s memory.',[0]);
 s(2,['write(1) = 64 bytes','descriptor 1 is stdout'],'Output is also a system call: write to descriptor 1. Whether that is your terminal, a file or a pipe is decided by the shell before cat started. cat does not know or care.',[0,1]);
 s(3,['close(3) = 0','descriptor 3 is free again'],'Closing releases the descriptor. Forgetting this in a long-running program is a classic leak: eventually "Too many open files".',[0,1,2]);
 s(4,['exit_group(0)','status 0 goes to the parent'],'The last call ends the process and hands the exit status to the parent. strace shows you this whole conversation for any program, which makes it the best tool for "why does this program fail or hang?".',[0,1,2,3]);
 return S},
vmem:function(){var S=[];
 function s(a,hi,aux,note,ok,dim,ptr){S.push({a:a,ptr:ptr||{},hi:hi||[],ok:ok||[],dim:dim||[],aux:{label:'address translation',items:aux},note:note})}
 s(['A: 0x1000','A: 0x2000','B: 0x1000','B: 0x2000'],[],['process A and process B','both use address 0x1000'],'Every process believes it owns a private memory starting at address 0. Process A and process B can both use the address 0x1000 and not collide, because these are virtual addresses, not real ones.');
 s(['A: 0x1000','A: 0x2000','B: 0x1000','B: 0x2000'],[0,2],['A:0x1000 -> frame 7','B:0x1000 -> frame 3'],'The CPU\'s memory unit translates each virtual address to a physical frame using a page table that the kernel keeps per process. The same virtual address 0x1000 leads to different physical frames, so A cannot read B\'s data.',[],[1,3]);
 s(['A: 0x1000','A: 0x2000','B: 0x1000','B: 0x2000'],[1],['A:0x2000 -> not in RAM yet','page fault!'],'Memory is handed out lazily. When A touches an address that has no frame yet, the CPU raises a page fault, the kernel finds a free frame, fills it (zeros, or the file contents for a program or library) and the instruction simply retries. A program never sees this happen.',[],[0,2,3]);
 s(['A: 0x1000','A: 0x2000','B: 0x1000','B: 0x2000'],[1,3],['A:0x2000 -> frame 9','B:0x2000 -> frame 9 (shared library)'],'Frames can be shared on purpose: two processes running the same program or library map the same read-only frames, so the code is in RAM only once. This is why 50 copies of a program cost far less than 50 times its size.',[1,3]);
 s(['A: 0x1000','A: 0x2000','B: 0x1000','B: 0x2000'],[0],['A:0x9000 -> not mapped','SIGSEGV: segmentation fault'],'If a program touches an address that is not mapped at all (a null pointer, a freed buffer) the kernel has no frame to give. It delivers SIGSEGV and the process dies with "Segmentation fault". Isolation is enforced by hardware, so one buggy program cannot corrupt another.',[],[1,2,3]);
 return S},
sched:function(){var S=[];
 function s(a,ptr,aux,note,ok,dim,hi){S.push({a:a,ptr:ptr||{},hi:hi||[],ok:ok||[],dim:dim||[],aux:{label:'1 CPU, 3 runnable processes',items:aux},note:note})}
 s(['','','','','',''],{},['A, B, C all want the CPU','only one can run at a time'],'One CPU core runs exactly one thing at any instant. Here are three processes that all want to run. The row below is time, in small slices of a few milliseconds each.');
 s(['A','','','','',''],{'CPU now':0},['slice 1: A runs'],'The scheduler picks A for a short time slice.',[0]);
 s(['A','B','','','',''],{'CPU now':1},['slice 2: B runs','context switch A -> B'],'When A\'s slice ends the kernel saves A\'s CPU registers, loads B\'s and lets it run. This is a context switch. It costs a little time, which is why thousands of runnable processes on a few cores slow everything.',[0,1]);
 s(['A','B','C','A','B','C'],{'CPU now':5},['each gets a turn in order'],'Round after round the processes share the core. Each makes progress, and because the slices are tiny it looks as if all three run at once. That is concurrency: many tasks in progress, not necessarily at the same instant.',[0,1,2,3,4,5]);
 s(['A','B','A','B','A','B'],{'2 cores':3},['2 cores: A and B run in parallel','C waits for a free core'],'With two cores, two processes run at the very same instant. That is parallelism. Real programs mix both: more cores means more real parallelism, more processes than cores means time-sharing.',[],[]);
 s(['A','wait','B','C','B','C'],{'A waits for network':1},['A asked the network and sleeps','B and C use its slices'],'When a process waits for slow I/O it is taken off the CPU, so the others get its slices. A server with a thousand mostly-waiting connections needs far fewer cores than one with a thousand busy ones. Load average counts the running and waiting processes, which is why it can be high even when the CPU is idle.',[],[]);
 return S},
/* ---- S07: networking ---- */
layers:function(){var S=[],L=['HTTP data','+ TCP header','+ IP header','+ Ethernet frame'];
 function s(upto,aux,note,ok){S.push({a:L,ptr:{wrapped:upto},hi:[upto],ok:ok||[],aux:{label:'sending GET /index.html',items:aux},note:note})}
 s(0,['your app: "GET /index.html"','plain bytes, no addresses yet'],'The browser has a request: a few lines of text. On its own it has no idea where to go. Each layer below adds one envelope with the information that layer needs, like putting a letter in an envelope, then in a bigger one.');
 s(1,['TCP adds: source port, destination port 443','sequence numbers for ordering'],'TCP (transport layer) adds ports, so the data reaches the right program on the machine (443 is HTTPS), and sequence numbers so lost or reordered pieces can be repaired. Your computer may have hundreds of open connections; the ports keep them apart.',[0]);
 s(2,['IP adds: source and destination IP address','routers read only this part'],'IP (network layer) adds the addresses of the two machines. Routers on the way read only the IP header and decide where to forward the packet next. They never look inside at the HTTP data.',[0,1]);
 s(3,['Ethernet or Wi-Fi adds: next-hop hardware address','only valid for this one link'],'The link layer adds the hardware (MAC) address of the next device on this one network segment, usually your router. At every hop this outer envelope is thrown away and a new one is made for the next link, while the IP packet inside stays the same.',[0,1,2]);
 return S},
tcp:function(){var S=[];
 function G(nodes,edges,eok){return {nodes:nodes,edges:edges,directed:true,w:460,h:150}}
 var C={x:70,y:80,label:'client'},V={x:390,y:80,label:'server'};
 function st(edge,aux,note,ok){S.push({a:[],graph:{nodes:[C,V],edges:edge,directed:true,w:460,h:150},ptr:{},ok:ok||[],aux:{label:'TCP',items:aux},note:note})}
 st([],['server: LISTEN on port 80','client: CLOSED'],'The server program has told the kernel "I accept connections on port 80": the port is in the LISTEN state (you see it with ss -ltn). Nothing is connected yet.');
 st([[0,1]],['client -> server: SYN','"I want to talk, my first number is x"'],'Step 1 of the three-way handshake: the client sends SYN. If no program listens on that port the server\'s kernel answers with RST and you see "Connection refused" instantly. If a firewall drops the packet silently you see nothing, and the connection attempt times out instead.');
 st([[1,0]],['server -> client: SYN-ACK','"OK, here is my number y"'],'Step 2: the server answers SYN-ACK: it acknowledges the client\'s number and offers its own.');
 st([[0,1]],['client -> server: ACK','connection ESTABLISHED'],'Step 3: the client acknowledges. Both sides are now ESTABLISHED. One round trip has passed, which is why a far-away server feels slow to start: distance costs latency before a single byte of your data moves.',[0,1]);
 st([[0,1],[1,0]],['data flows both ways','every segment is acknowledged'],'Data now flows in numbered segments. The receiver acknowledges what arrived; if an acknowledgement does not come back the sender retransmits. That is how TCP turns an unreliable network into a reliable byte stream, at the price of some waiting.',[0,1]);
 st([[0,1],[1,0]],['FIN / ACK from both sides','then TIME_WAIT on the closer'],'Closing takes FIN and ACK in each direction. The side that closes first keeps the connection in TIME_WAIT for a short while so late packets cannot be confused with a new connection. A busy server with tens of thousands of TIME_WAIT sockets is normal; a pile of CLOSE_WAIT sockets means the application forgot to close.',[0,1]);
 return S},
dns:function(){var S=[];
 var N=[{x:50,y:115,label:'you'},{x:170,y:115,label:'resolver'},{x:300,y:35,label:'root'},{x:300,y:115,label:'.com'},{x:300,y:195,label:'auth'}];
 function st(active,edges,aux,note,ok){var dim=[0,1,2,3,4].filter(function(i){return active.indexOf(i)<0});S.push({a:[],graph:{nodes:N,edges:[[0,1],[1,2],[1,3],[1,4]],directed:true,w:480,h:230},eok:edges,ptr:{},ok:ok||[],dim:dim,aux:{label:'looking up www.example.com',items:aux},note:note})}
 st([0,1],[0],['you -> resolver: www.example.com ?','cache: empty'],'Your program asks the system resolver, which first checks /etc/hosts and its own cache. If it does not know, it forwards the question to a recursive resolver (your ISP\'s, your router\'s, or a public one like 1.1.1.1 or 8.8.8.8).');
 st([0,1,2],[1],['resolver -> root: who knows .com ?','root: ask the .com servers'],'The recursive resolver starts at the top: one of the 13 root server addresses it already knows. The root does not know the answer, but it knows who is responsible for .com and sends a referral.');
 st([0,1,3],[2],['resolver -> .com: who knows example.com ?','.com: ask these name servers'],'The .com servers do not know the host either, but they know which name servers are authoritative for example.com and refer the resolver to them.');
 st([0,1,4],[3],['resolver -> authoritative: www.example.com ?','answer: A 203.0.113.10, TTL 300'],'The authoritative server for the domain holds the real record and answers with an A record (an IPv4 address; AAAA is IPv6) and a TTL: how many seconds the answer may be cached.',[3]);
 st([0,1],[0],['resolver -> you: 203.0.113.10','cached for 300 s'],'The resolver returns the answer and remembers it for the TTL, so the next person to ask gets it in milliseconds. This is why DNS changes seem to "take time to propagate": caches everywhere hold the old answer until their TTL runs out. Lower the TTL before a planned change.',[0]);
 return S},
tls:function(){var S=[];
 function st(edge,aux,note,ok){S.push({a:[],graph:{nodes:[{x:70,y:70,label:'client'},{x:390,y:70,label:'server'}],edges:edge,directed:true,w:460,h:140},ptr:{},ok:ok||[],aux:{label:'TLS 1.3 handshake',items:aux},note:note})}
 st([[0,1]],['ClientHello','supported ciphers, a random value, key share, SNI'],'The client opens with ClientHello: which encryption algorithms it supports, a random number, its half of a key exchange, and the server name it wants (SNI), so one IP address can host many sites.');
 st([[1,0]],['ServerHello + certificate','server key share, signed proof'],'The server picks the algorithms, sends its half of the key exchange and its certificate: a document that says "this public key belongs to example.com", signed by a certificate authority (CA). From here on both sides can compute the same secret key, and everything after is encrypted.');
 st([[0,1]],['client checks the certificate','chain, name, dates, revocation'],'The client verifies the certificate: is it signed by a CA it trusts (the chain leads to a root in its trust store), does the name match, is it within its dates? If any check fails you see errors like "self-signed certificate" or "certificate has expired". Never "fix" this with curl -k in production code; that turns off the whole point.',[0]);
 st([[0,1],[1,0]],['Finished messages','HTTP now flows, encrypted'],'Both sides send Finished to prove they derived the same keys. Encrypted HTTP follows. In TLS 1.3 this takes one round trip; older versions took two, and resuming a session can skip most of it.',[0,1]);
 return S},
url:function(){var S=[],L=['DNS','TCP','TLS','HTTP','Render'];
 function s(at,aux,note,ok){S.push({a:L,ptr:{now:at},hi:[at],ok:ok||[],aux:{label:'https://shop.example.com/cart',items:aux},note:note})}
 s(0,['browser cache, OS cache, resolver','result: 203.0.113.7'],'You press Enter. If the browser does not already have the page, the first job is to turn shop.example.com into an IP address: browser cache, then the operating system and /etc/hosts, then the recursive resolver, then (if needed) the chain of authoritative servers. Cost: 0 to a few round trips.');
 s(1,['SYN, SYN-ACK, ACK','port 443'],'Next the browser opens a TCP connection to port 443 of that address: the three-way handshake, one round trip. A refused connection or a timeout here points at the server, a firewall or the network path, not the website code.',[0]);
 s(2,['ClientHello ... Finished','certificate checked'],'Then TLS: agree on keys and check the server\'s certificate. One more round trip. Errors here (expired certificate, wrong name) are certificate problems, not application problems.',[0,1]);
 s(3,['GET /cart HTTP/1.1','Host: shop.example.com','200 OK + HTML'],'Now the actual request: a method, a path and headers, answered by a status line, headers and a body. The status code is your first clue: 2xx fine, 3xx redirect, 4xx the request was wrong, 5xx the server failed. Keep-alive and HTTP/2 reuse the connection so later requests skip the earlier steps.',[0,1,2]);
 s(4,['parse HTML','fetch CSS, JS, images (repeat 1-4)','paint'],'The browser parses the HTML, finds more resources and repeats the cycle for each (often over the same connection), then paints the page. When someone says "the site is slow", this is the chain to walk: which step is slow?',[0,1,2,3]);
 return S},
/* ---- S09: debugging method ---- */
dbgloop:function(){var S=[],L=['Observe','Hypothesise','Predict','Test','Conclude'];
 function s(at,aux,note,ok){S.push({a:L,ptr:{now:at},hi:[at],ok:ok||[],aux:{label:'checkout returns 500',items:aux},note:note})}
 s(0,['what exactly happens?','when did it start?','who is affected?'],'Start with facts, not theories: the exact error, the time it began, who and what is affected, and what changed just before (a deploy, a config edit, a traffic spike). Write them down. Most wasted debugging hours come from skipping this step and fixing a guess.');
 s(1,['H1: the database is down','H2: last deploy broke the payment call'],'Turn the facts into one or two specific, testable guesses. A good hypothesis can be proven wrong. "Something is broken in the backend" is not testable; "the payment call times out since the 14:05 deploy" is.',[0]);
 s(2,['if H2 is true: errors start at 14:05','and only the payment path fails'],'Before you test, predict what you would see if the hypothesis were true. This is the discipline that stops you reading results to fit your theory.',[0,1]);
 s(3,['grep errors by minute','check one path at a time'],'Run the cheapest test that can separate the hypotheses: one grep, one curl, one diff. Change ONE thing at a time, otherwise you cannot tell what mattered.',[0,1,2]);
 s(4,['errors began 14:05, payment path only','H2 confirmed, H1 rejected'],'Compare the result with the prediction. If it matches, act (roll back, fix); if not, you have eliminated a cause, which is progress, so go back to Hypothesise with the new facts. Finish by writing what you learned.',[0,1,2,3]);
 return S},
halve:function(){var S=[],n=16,c=[];for(var i=1;i<=n;i++)c.push('L'+i);
 function s(lo,hi,aux,note,ok){var dim=[],h=[];for(var i=0;i<n;i++){if(i<lo||i>hi)dim.push(i);else h.push(i)}S.push({a:c,ptr:{},hi:h,dim:dim,ok:ok||[],aux:{label:'config with 16 lines, one is bad',items:aux},note:note})}
 s(0,15,['16 suspects','app fails with the full file'],'The app rejects a 16-line config but does not say which line is wrong. Reading all 16 is slow; guessing is unreliable. Halving finds the culprit in at most four tests.');
 s(0,7,['keep lines 1-8 only','app still fails'],'Test the first half. It still fails, so the bad line is in lines 1 to 8. Eight suspects remain.');
 s(0,3,['keep lines 1-4 only','app works'],'Keep only lines 1 to 4: it works, so the bad line is NOT here. It must be in lines 5 to 8.');
 s(4,5,['lines 1-4 plus 5-6','app fails'],'Add lines 5 and 6 to the good lines 1 to 4: it fails again. The culprit is line 5 or 6.');
 s(4,4,['lines 1-4 plus 5','app fails: line 5 is the culprit'],'Add just line 5: it fails. Found it in four tests instead of up to sixteen. The same idea powers git bisect (over commits), disabling half the plugins, or removing half of a failing test.',[4]);
 return S},
/* ---- S10: performance triage ---- */
usegrid:function(){var S=[],R=['CPU','Memory','Disk','Network'];
 function s(at,aux,note,ok){S.push({a:R,ptr:{check:at},hi:[at],ok:ok||[],aux:{label:'USE method',items:aux},note:note})}
 S.push({a:R,ptr:{},aux:{label:'for every resource ask 3 questions',items:['Utilization: how busy is it?','Saturation: is work queueing?','Errors: is anything failing?']},note:'The USE method (Brendan Gregg) turns "the server is slow" into a checklist. For each resource ask: how busy is it (utilization), is work waiting in a queue (saturation), and is it reporting errors? A resource can be only 60% utilized and still saturated in bursts, which is why you check all three.'});
 s(0,['U: mpstat, top (%us + %sy)','S: load average above core count, vmstat r column','E: rarely: dmesg for throttling'],'CPU: utilization is the busy percentage per core. Saturation shows as runnable tasks waiting: load average well above the core count, or a high r column in vmstat. One core pegged at 100% while others idle usually means a single-threaded bottleneck.');
 s(1,['U: free -m (available, not free)','S: swap in/out (vmstat si/so), PSI memory','E: dmesg: Out of memory: Killed process'],'Memory: low "free" is normal because of the page cache; look at available. Saturation is swapping (si and so above zero for a while) or memory pressure; the extreme error is the OOM killer in the kernel log.',[0]);
 s(2,['U: iostat -x %util, df -h','S: avgqu-sz / await rising, vmstat wa','E: dmesg I/O errors, df -i (inodes)'],'Disk: %util near 100 and a rising await means requests queue. A full filesystem or exhausted inodes is an "error" even when the disk is idle: writes fail.',[0,1]);
 s(3,['U: bandwidth vs link speed','S: ss -s, retransmits, drops','E: ip -s link (errors, dropped)'],'Network: compare throughput with the link capacity, look for retransmissions and dropped packets (saturation and errors) and for sockets piling up in odd states with ss -s.',[0,1,2]);
 return S},
triage60:function(){var S=[],C=['uptime','dmesg','vmstat','mpstat','pidstat','iostat','free','ss'];
 function s(at,aux,note,ok){S.push({a:C,ptr:{run:at},hi:[at],ok:ok||[],aux:{label:'first 60 seconds',items:aux},note:note})}
 s(0,['load averages 1, 5, 15 min','is it rising or falling?'],'uptime: three load averages. If the 1-minute number is far above the 15-minute one the problem is recent and getting worse; far below means it already passed. Compare with the number of cores.');
 s(1,['dmesg -T | tail','OOM kills, disk errors, link flaps'],'dmesg: the kernel\'s own complaints. Out-of-memory kills, I/O errors and network resets all show up here, and they are quick to rule in or out.',[0]);
 s(2,['vmstat 1 5','r b si so us sy id wa'],'vmstat: one line per second. r (runnable) above the core count means CPU queueing, b blocked on I/O, si/so swapping, wa time waiting on disk, id idle. Ignore the first line: it is an average since boot.',[0,1]);
 s(3,['mpstat -P ALL 1','one core busy or all?'],'mpstat per core: reveals a single saturated core that the overall average hides.',[0,1,2]);
 s(4,['pidstat 1 5','which process uses CPU?'],'pidstat: CPU per process over time, better than a single top snapshot for spotting a burst.',[0,1,2,3]);
 s(5,['iostat -xz 1','await, %util per device'],'iostat -xz: per-disk utilization and wait time. Large await with high %util means the disk is the bottleneck.',[0,1,2,3,4]);
 s(6,['free -m','available, swap used'],'free: how much memory can still be handed out (available) and whether swap is in use.',[0,1,2,3,4,5]);
 s(7,['ss -s','sockets by state, retransmits via sar -n'],'ss -s: socket totals and odd states; a pile in TIME-WAIT or CLOSE-WAIT or many retransmits points to the network or the application. Now pick the resource that is saturated and dig in only there.',[0,1,2,3,4,5,6]);
 return S},
/* ---- S11: deep debugging tools ---- */
straceread:function(){var S=[],T=['execve(...)','openat(config) = -1 ENOENT','openat(data) = 3','read(3, ...) = 4096','connect(db) ...','write(1, ...) = 12'];
 function s(at,aux,note,ok,dim){S.push({a:T,ptr:{'last line':at},hi:[at],ok:ok||[],dim:dim||[],aux:{label:'strace output, newest at the right',items:aux},note:note})}
 s(0,['the program asked to be started','everything after is its behaviour'],'strace prints one line per system call, in order. The first lines are the program loading itself. Focus on what comes after: which files it opens, which sockets it talks to, and what the kernel answers.');
 s(1,['ENOENT = no such file','the program wanted a config that is missing'],'A call that returns -1 with an error name is a clue. ENOENT means a file it wanted does not exist; EACCES means permission denied; ECONNREFUSED means nothing listened on that port. This one line explains most "it fails with no message" bugs.',[0]);
 s(2,['openat(data) = 3','descriptor 3 now means the data file'],'A successful open returns a file descriptor (3). Later calls refer to it by number, so reading the trace means following the numbers.',[0,1]);
 s(3,['read(3) returned 4096 bytes','progress is being made'],'The program reads its data in chunks. Many fast reads in a row mean it is busy; the interesting case is when one call never returns.',[0,1,2]);
 s(4,['connect(db) ... no result yet','the last line did not finish'],'HANG: if the final line is a call without a result, the program is blocked inside it. Here it waits for a connection to the database. That is your answer: the process is not busy, it is waiting on the network, and the next question is why the database does not answer.',[0,1,2,3],[5]);
 s(5,['write(1, ...) = 12','output reached stdout'],'In a healthy run the trace ends with writes and an exit. With -T you also see how long each call took, which shows slow calls. With -c you get a summary table of counts and time per system call.',[0,1,2,3,4]);
 return S},
backtrace:function(){var S=[],F=['main()','run_job()','parse_line()','copy_name()'];
 function s(at,aux,note,ok){S.push({a:F,ptr:{'frame #0':at},hi:[at],ok:ok||[],aux:{label:'gdb backtrace (bt)',items:aux},note:note})}
 s(3,['Program received signal SIGSEGV','#0 copy_name() crash.c:2'],'The program crashed with a segmentation fault. gdb stops at the exact place: frame #0, the function that was running, with file and line. That is where the bad memory access happened.');
 s(2,['#1 parse_line() crash.c:6','called copy_name(NULL)'],'Frame #1 is the caller. It passed a null pointer into copy_name. Often the real bug is here, in who passed the bad value, not where it blew up.',[3]);
 s(1,['#2 run_job() crash.c:9','called parse_line(buf)'],'Each frame up the stack shows how the program got there. Use `up` and `info locals` in gdb to inspect variables at each level.',[3,2]);
 s(0,['#3 main() crash.c:12','the program started here'],'The bottom of the stack is main. Reading the backtrace from frame #0 upwards answers three questions: what failed, who called it with what, and where to look first. A core dump lets you do this after the crash, on a different machine.',[3,2,1]);
 return S},
/* ---- S12: troubleshooting playbooks ---- */
zombie:function(){var S=[];
 function st(nodes,edges,ptr,aux,note,ok,dim){S.push({a:[],graph:{nodes:nodes,edges:edges,directed:true,w:460,h:150},ptr:ptr,ok:ok||[],dim:dim||[],aux:{label:'ps shows',items:aux},note:note})}
 var P={x:80,y:75,label:'parent'},C1={x:260,y:30,label:'c1 Z'},C2={x:260,y:75,label:'c2 Z'},C3={x:260,y:120,label:'c3 Z'},I={x:400,y:75,label:'init'};
 st([P,C1,C2,C3],[[0,1],[0,2],[0,3]],{'PID 500':0},['parent 500 S sleeping','three children: STAT Z, <defunct>'],'A buggy parent starts children and never calls wait(). Each child finishes, but the kernel keeps a small record (the exit status) until the parent collects it. These records are zombies: no CPU, no memory, just a process-table slot. ps shows them as Z or <defunct>.');
 st([P,C1,C2,C3],[[0,1],[0,2],[0,3]],{'kill -9 c1 ?':1},['kill -9 on a zombie: no effect','it is already dead'],'You cannot kill a zombie: it is already dead. Sending signals to it does nothing, which is why people think they are stuck. The record waits for its parent to call wait().',[],[1,2,3]);
 st([P,C1,C2,C3],[[0,1],[0,2],[0,3]],{'who is PPID?':0},['ps -o pid,ppid,stat','all three have PPID 500'],'Look at the PPID column: it names the guilty parent. The fix is in that process (call wait(), or handle SIGCHLD), not in the zombies.',[0]);
 st([P,I],[[0,1]],{'kill 500':0},['parent 500 stopped','children re-parented to init'],'Stopping the parent (SIGTERM first) orphans the children. PID 1 (init or systemd) adopts orphans and always calls wait(), so the zombies vanish at once. A handful of short-lived zombies is normal; a growing pile means the parent has a bug that needs fixing.',[1]);
 return S},
incident:function(){var S=[],L=['Detect','Triage','Mitigate','Diagnose','Fix','Review'];
 function s(at,aux,note,ok){S.push({a:L,ptr:{now:at},hi:[at],ok:ok||[],aux:{label:'incident flow',items:aux},note:note})}
 s(0,['alert or user report','what is broken, since when?'],'Something tells you: an alert, a customer, a graph. Write down the time and the exact symptom. Detection speed is a property of your monitoring, which is why alerts should fire before customers write in.');
 s(1,['scope: all users or some?','severity and owner'],'Triage: how bad is it and who is affected? A broken checkout for everyone is not the same as a single slow export. Pick one person to lead and one channel to talk in.',[0]);
 s(2,['roll back the deploy','failover, disable the flag'],'Mitigate first: stop the damage with the quickest safe action (roll back, fail over, switch off a feature flag, add capacity). Understanding can wait; customers cannot.',[0,1]);
 s(3,['playbook: DNS, TCP, TLS, HTTP','USE method, strace, logs'],'Now diagnose calmly with the method from the earlier modules: observe, hypothesise, test, narrow. Keep a running timeline of what you tried and saw.',[0,1,2]);
 s(4,['permanent fix','verify with the original symptom'],'Fix the cause, then prove it fixed the original symptom, not a nearby one. Remove the temporary mitigation only when you are sure.',[0,1,2,3]);
 s(5,['blameless postmortem','actions with owners and dates'],'Review: write what happened, why it was possible, and what changes so it cannot recur (a test, an alert, a runbook entry). Blameless means asking how the system allowed the mistake, not who made it.',[0,1,2,3,4]);
 return S}
};
