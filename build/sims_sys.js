/* Animations for Systems Mastery modules. Same step format as sims.js:
   {a:[cells], ptr:{label:idx}, hi:[], ok:[], dim:[], aux:{label,items}, note, cols?, graph?:{nodes,edges,directed,w,h}, eok?} */
function rng(x,y){var r=[];for(var i=x;i<=y;i++)r.push(i);return r}
function mapStr(m){var k=Object.keys(m);return '{'+k.map(function(x){return x+':'+m[x]}).join(', ')+'}'}
var SIM={
/* ---- S02: Linux shell ---- */
cdtree:function(){var S=[];
 var nodes=[{x:210,y:25,label:'/'},{x:110,y:75,label:'home'},{x:310,y:75,label:'etc'},{x:110,y:125,label:'me'},{x:110,y:175,label:'work'},{x:50,y:228,label:'logs'},{x:110,y:228,label:'notes'},{x:170,y:228,label:'bin'}];
 var edges=[[0,1],[0,2],[1,3],[3,4],[4,5],[4,6],[4,7]];
 var G={nodes:nodes,edges:edges,w:420,h:255};
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
 return S}
};
