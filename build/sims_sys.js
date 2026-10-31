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
 return S}
};
