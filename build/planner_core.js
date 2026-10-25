/* Study planner core: pure functions, no DOM. Used by the planner page and by verify/test_planner.js.
   The schedule is computed here (not by the AI), so dates and hours are always consistent. */
var PlannerCore=(function(){
var EFF=0.85;                                   /* people never use 100% of the time they set aside */
var LEVEL={beginner:1.35,intermediate:1,advanced:0.8};
var PMIN={E:20,M:35,H:55};                      /* minutes to solve and review one problem, by difficulty */
var DEPTHS=['light','standard','deep'];
var DEPTH_LABEL={light:'Light',standard:'Standard',deep:'Deep'};

function pad(n){return n<10?'0'+n:''+n}
function iso(d){return d.getFullYear()+'-'+pad(d.getMonth()+1)+'-'+pad(d.getDate())}
function parseISO(s){var p=String(s).split('-');return new Date(+p[0],+p[1]-1,+p[2])}
function addDays(d,n){return new Date(d.getFullYear(),d.getMonth(),d.getDate()+n)}
function diffDays(a,b){return Math.round((Date.UTC(b.getFullYear(),b.getMonth(),b.getDate())-Date.UTC(a.getFullYear(),a.getMonth(),a.getDate()))/86400000)}
function mondayOf(d){var k=(d.getDay()+6)%7;return addDays(d,-k)}
var MON=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],DOW=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
function fmtDay(d){return DOW[d.getDay()]+' '+d.getDate()+' '+MON[d.getMonth()]}
function fmtShort(d){return d.getDate()+' '+MON[d.getMonth()]}
function fmtMin(m){var h=Math.floor(m/60),r=Math.round(m%60);return h?(r?h+'h '+pad(r)+'m':h+'h'):r+'m'}
function clamp(v,lo,hi){v=+v;if(isNaN(v))return lo;return Math.min(hi,Math.max(lo,v))}

function defaultSettings(today,allNums){
  return {topics:allNums.slice(),startDate:today,weeks:12,weekdayHours:2,weekendHours:4,restDay:'sun',level:'intermediate',depth:'standard',checkpoints:true,reviews:true,skipSolved:true};
}

/* validate and normalise a settings object (also used for AI-suggested patches) */
function sanitize(s,allNums){
  var o={},k;
  if(s.topics){var set={};allNums.forEach(function(n){set[n]=1});o.topics=[];(s.topics||[]).forEach(function(n){n=String(n);if(/^\d$/.test(n))n='0'+n;if(set[n]&&o.topics.indexOf(n)<0)o.topics.push(n)});o.topics.sort()}
  if(s.startDate&&/^\d{4}-\d{2}-\d{2}$/.test(s.startDate)&&!isNaN(parseISO(s.startDate)))o.startDate=s.startDate;
  if(s.weeks!==undefined)o.weeks=Math.round(clamp(s.weeks,1,52));
  if(s.weekdayHours!==undefined)o.weekdayHours=Math.round(clamp(s.weekdayHours,0,8)*4)/4;
  if(s.weekendHours!==undefined)o.weekendHours=Math.round(clamp(s.weekendHours,0,12)*4)/4;
  if(s.restDay&&['none','sat','sun'].indexOf(s.restDay)>=0)o.restDay=s.restDay;
  if(s.level&&LEVEL[s.level])o.level=s.level;
  if(s.depth&&DEPTHS.indexOf(s.depth)>=0)o.depth=s.depth;
  ['checkpoints','reviews','skipSolved'].forEach(function(b){if(typeof s[b]==='boolean')o[b]=s[b]});
  return o;
}
function merge(base,patch){var o={};for(var k in base)o[k]=base[k];for(k in patch)o[k]=patch[k];return o}

function capacity(date,s){
  var dow=date.getDay(),h;
  if(dow===0){h=s.restDay==='sun'?0:s.weekendHours}
  else if(dow===6){h=s.restDay==='sat'?0:s.weekendHours}
  else h=s.weekdayHours;
  return Math.round(h*60*EFF);
}

/* which problems of a pattern to include, by depth and tier. The ladder is ordered easy to hard. */
function pickProblems(p,depth){
  var em=p.problems.filter(function(x){return x[2]!=='H'}),h=p.problems.filter(function(x){return x[2]==='H'});
  var hot=p.tier==='hot';
  if(depth==='deep')return p.problems.slice();
  if(depth==='standard')return hot?em.concat(h.slice(0,1)):em.slice(0,3);
  var n=hot?3:1;var pool=em.length?em:p.problems;return pool.slice(0,n);
}

function sortedTopics(data,s){var set={};s.topics.forEach(function(n){set[n]=1});return data.filter(function(t){return set[t.num]})}

/* build the ordered list of study items for a mode */
function buildItems(data,s,progress,mode){
  var L=LEVEL[s.level]||1,items=[],stats={patterns:0,problems:0,skippedSolved:0,droppedPatterns:0,skimmed:0};
  sortedTopics(data,s).forEach(function(t){
    t.patterns.forEach(function(p){
      if(p.tier==='sec'&&mode.secondary==='none'){stats.droppedPatterns++;return}
      var skim=p.tier==='sec'&&mode.secondary==='skim';
      var href='topics/'+t.file+'.html#p'+p.n,base={topicNum:t.num,topicId:t.id,topicTitle:t.title,pn:p.n,pattern:p.title,href:href};
      var list=[];
      var learn={kind:'learn',id:'learn-'+t.num+'-'+p.n,title:'Learn: '+p.title,minutes:Math.round((skim?10:(p.tier==='hot'?40:25))*L),href:href};
      list.push(learn);
      if(skim)stats.skimmed++;
      else{
        if(p.hasCode)list.push({kind:'code',id:'code-'+t.num+'-'+p.n,title:'Write the skeleton from memory: '+p.title,minutes:Math.round(20*L),href:href});
        pickProblems(p,mode.depth).forEach(function(pr){
          if(s.skipSolved&&progress&&progress[t.id+'-'+pr[0]]){stats.skippedSolved++;return}
          list.push({kind:'practice',id:'lc-'+t.num+'-'+p.n+'-'+pr[0],title:'LC '+pr[0]+' '+pr[1],minutes:Math.round(PMIN[pr[2]]*L),url:'https://leetcode.com/problems/'+pr[3]+'/',lc:pr[0],diff:pr[2],href:href});
          stats.problems++;
        });
      }
      list.forEach(function(it){for(var k in base)if(it[k]===undefined)it[k]=base[k]});
      list[list.length-1].last=true;
      items=items.concat(list);stats.patterns++;
    });
  });
  return {items:items,stats:stats};
}

/* day-by-day simulation. Reviews are scheduled after each pattern; one checkpoint per calendar week. */
function schedule(items,s,mode){
  var start=parseISO(s.startDate),end=addDays(start,s.weeks*7-1),queue=items.map(function(x){var c={};for(var k in x)c[k]=x[k];return c});
  var due={},days=[],day=start,guard=0,reviewGaps=mode.reviews===2?[3,10]:mode.reviews===1?[7]:[];
  var totalMin=0;
  function addDue(date,r){var key=iso(date);(due[key]=due[key]||[]).push(r)}
  function pendingReviews(){var n=0;for(var k in due)if(parseISO(k)<=end)n+=due[k].length;return n}
  /* is this the last study day of its calendar week? */
  function lastStudyDay(d){var m=mondayOf(d);for(var i=6;i>=0;i--){var x=addDays(m,i);if(capacity(x,s)>0)return iso(x)===iso(d)}return false}
  while((queue.length||pendingReviews())&&guard++<800){
    var cap=capacity(day,s),entry={date:iso(day),minutes:0,cap:cap,tasks:[]};
    if(cap<=0){entry.rest=true;days.push(entry);day=addDays(day,1);continue}
    var reserve=(mode.checkpoints&&s.checkpoints&&s.weeks>=3&&lastStudyDay(day))?Math.min(45,Math.round(cap*0.4)):0;
    if(cap-reserve<20)reserve=0;
    var room=cap-reserve,used=0;
    /* reviews that are due (or overdue) come first */
    var key=iso(day),carried=[];
    Object.keys(due).forEach(function(k){if(k<=key){carried=carried.concat(due[k]);delete due[k]}});
    carried.forEach(function(r){if(used+r.minutes<=room){entry.tasks.push(r);used+=r.minutes}else addDue(addDays(day,1),r)});
    /* then new material */
    while(queue.length){
      var it=queue[0],rem=room-used;
      if(rem<15)break;
      if(it.minutes<=rem+10){queue.shift();entry.tasks.push(it);used+=it.minutes;
        if(it.last){reviewGaps.forEach(function(g,i){addDue(addDays(day,g),{kind:'review',id:'rev'+(i+1)+'-'+it.topicNum+'-'+it.pn,title:'Review: '+it.pattern,minutes:12,href:it.href,topicNum:it.topicNum,pn:it.pn,pattern:it.pattern})})}}
      else if(used>0&&rem<0.6*it.minutes)break;
      else{var part={};for(var k2 in it)part[k2]=it[k2];part.minutes=rem;part.title=it.title+' (part 1)';part.id=it.id+'-a';part.last=false;
        entry.tasks.push(part);used+=rem;it.minutes-=rem;it.title=it.title.replace(/ \(part \d\)$/,'')+' (part 2)';it.id=it.id.replace(/-a$/,'')+'-b'}
    }
    if(reserve){entry.tasks.push({kind:'checkpoint',id:'ck-'+key,title:'Weekly checkpoint: redo two problems from this week without notes, on a timer',minutes:reserve});used+=reserve}
    entry.minutes=used;totalMin+=used;days.push(entry);day=addDays(day,1);
  }
  /* final mock, appended to the last study day or a new one */
  if(mode.checkpoints&&s.checkpoints&&days.length){
    var last=null;for(var i=days.length-1;i>=0;i--)if(!days[i].rest){last=days[i];break}
    if(last){var fin={kind:'mock',id:'final-mock',title:'Final review and a timed mock interview (see the Interview Playbook)',minutes:60,href:'topics/19_interview_playbook.html'};
      if(last.cap-last.minutes>=45){fin.minutes=Math.min(60,last.cap-last.minutes);last.tasks.push(fin);last.minutes+=fin.minutes;totalMin+=fin.minutes}
      else{var d2=addDays(parseISO(last.date),1),g2=0;while(capacity(d2,s)<=0&&g2++<7)d2=addDays(d2,1);var c2=capacity(d2,s);fin.minutes=Math.max(15,Math.min(60,c2));days.push({date:iso(d2),minutes:fin.minutes,cap:c2,tasks:[fin]});totalMin+=fin.minutes}}
  }
  var finish=null;for(var j=days.length-1;j>=0;j--)if(!days[j].rest&&days[j].tasks.length){finish=days[j].date;break}
  return {days:days,totalMin:totalMin,finish:finish,fits:finish!==null&&parseISO(finish)<=end,end:iso(end)};
}

/* try the requested mode first, then progressively lighter ones until the plan fits the time */
function generate(data,s,progress){
  var allNums=data.map(function(t){return t.num});
  if(!s.topics.length)return {error:'Select at least one topic.'};
  var weekCap=0,start=parseISO(s.startDate);for(var i=0;i<s.weeks*7;i++)weekCap+=capacity(addDays(start,i),s);
  if(weekCap<=0)return {error:'You have no study time in this window. Add some hours per day.'};
  var di=Math.max(0,DEPTHS.indexOf(s.depth)),modes=[];
  var R2=s.reviews===false?0:2,R1=s.reviews===false?0:1;
  for(var d=di;d>=0;d--)modes.push({depth:DEPTHS[d],secondary:'full',reviews:R2,checkpoints:true});
  modes.push({depth:'light',secondary:'skim',reviews:R2,checkpoints:true});
  modes.push({depth:'light',secondary:'none',reviews:R1,checkpoints:true});
  modes.push({depth:'light',secondary:'none',reviews:0,checkpoints:false});
  var res=null,used=null,built=null;
  for(var m=0;m<modes.length;m++){
    var b=buildItems(data,s,progress,modes[m]);
    if(!b.items.length)continue;
    var sch=schedule(b.items,s,modes[m]);
    res=sch;used=modes[m];built=b;
    if(sch.fits)break;
  }
  if(!res)return {error:'Everything in your selected topics is already solved. Pick more topics or turn off "skip solved".'};
  var notes=[],req=buildItems(data,s,progress,{depth:s.depth,secondary:'full',reviews:2,checkpoints:true});
  if(DEPTHS.indexOf(used.depth)<DEPTHS.indexOf(s.depth))notes.push('Practice depth reduced from '+DEPTH_LABEL[s.depth]+' to '+DEPTH_LABEL[used.depth]+' to fit your time.');
  if(used.secondary==='skim')notes.push(built.stats.skimmed+' secondary patterns are reduced to a quick read (no code drill, no problems).');
  if(used.secondary==='none')notes.push(built.stats.droppedPatterns+' secondary patterns were left out so the frequently asked ones fit. Do them later if you finish early.');
  if(!used.checkpoints)notes.push('Weekly checkpoints and the final mock were dropped.');
  else if(used.reviews<R2)notes.push('Spaced reviews were reduced.');
  var shortfallDays=0;if(!res.fits&&res.finish)shortfallDays=diffDays(parseISO(res.end),parseISO(res.finish));
  var spare=0;if(res.fits&&res.finish)spare=diffDays(parseISO(res.finish),parseISO(res.end));
  var tasks=0,topics={};res.days.forEach(function(dd){dd.tasks.forEach(function(t){tasks++;if(t.topicNum)topics[t.topicNum]=1})});
  return {settings:s,days:res.days,weeks:groupWeeks(res.days),mode:used,
    stats:{totalMin:res.totalMin,studyDays:res.days.filter(function(x){return !x.rest&&x.tasks.length}).length,finish:res.finish,end:res.end,fits:res.fits,notes:notes,
      shortfallDays:shortfallDays,spareDays:spare,problems:built.stats.problems,patterns:built.stats.patterns,topics:Object.keys(topics).length,tasks:tasks,
      skippedSolved:built.stats.skippedSolved,requestedMin:req.items.reduce(function(a,x){return a+x.minutes},0)}};
}

function groupWeeks(days){
  var weeks=[],cur=null;
  days.forEach(function(d){var m=iso(mondayOf(parseISO(d.date)));
    if(!cur||cur.key!==m){cur={key:m,start:m,end:iso(addDays(parseISO(m),6)),minutes:0,topics:[],days:[]};weeks.push(cur)}
    cur.days.push(d);cur.minutes+=d.minutes;
    d.tasks.forEach(function(t){if(t.kind==='learn'&&cur.topics.indexOf(t.topicNum)<0)cur.topics.push(t.topicNum)})});
  weeks=weeks.filter(function(w){return w.minutes>0});          /* a week that is only rest days is not shown */
  weeks.forEach(function(w,i){w.n=i+1;if(w.days[0].date>w.start)w.start=w.days[0].date});
  return weeks;
}

/* exports for the page: plain text and calendar */
function toText(plan){
  var o=['DSA Mastery study plan','Finish: '+(plan.stats.finish?fmtDay(parseISO(plan.stats.finish)):'-')+' | '+fmtMin(plan.stats.totalMin)+' over '+plan.stats.studyDays+' study days',''];
  plan.weeks.forEach(function(w){o.push('Week '+w.n+' ('+fmtShort(parseISO(w.start))+' to '+fmtShort(parseISO(w.end))+', '+fmtMin(w.minutes)+')');
    w.days.forEach(function(d){if(d.rest||!d.tasks.length)return;o.push('  '+fmtDay(parseISO(d.date))+' ('+fmtMin(d.minutes)+')');
      d.tasks.forEach(function(t){o.push('    [ ] '+t.title+' ('+t.minutes+' min)')})});o.push('')});
  return o.join('\n');
}
function icsEscape(s){return String(s).replace(/\\/g,'\\\\').replace(/;/g,'\\;').replace(/,/g,'\\,').replace(/\n/g,'\\n')}
function toICS(plan,stamp){
  var o=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//DSA Mastery//Study planner//EN','CALSCALE:GREGORIAN'];
  plan.days.forEach(function(d){if(d.rest||!d.tasks.length)return;var a=parseISO(d.date),b=addDays(a,1);
    var ymd=function(x){return x.getFullYear()+pad(x.getMonth()+1)+pad(x.getDate())};
    o.push('BEGIN:VEVENT','UID:dsa-'+d.date+'@dsa-mastery','DTSTAMP:'+stamp,'DTSTART;VALUE=DATE:'+ymd(a),'DTEND;VALUE=DATE:'+ymd(b),
      'SUMMARY:'+icsEscape('DSA study ('+fmtMin(d.minutes)+')'),'DESCRIPTION:'+icsEscape(d.tasks.map(function(t){return '- '+t.title+' ('+t.minutes+' min)'}).join('\n')),'END:VEVENT')});
  o.push('END:VCALENDAR');return o.join('\r\n');
}

/* ---------- assistant helpers ---------- */
var KEYWORDS=[['arrays|array|hashing|two pointer|sliding window|prefix','02'],['complexity|big-o|big o','01'],['string','03'],['linked','04'],['stack|queue|deque','05'],['sort|interval','06'],['recursion|backtrack','07'],['bit|math','08'],['tree|bst','09'],['heap|priority','10'],['trie','11'],['graph|bfs|dfs|dijkstra|union','12'],['advanced graph|topological|mst|shortest path','13'],['greedy','14'],['dynamic|dp\\b','15'],['knapsack|lcs|edit distance|bitmask','16'],['segment|fenwick|sparse|lca','17'],['design|lru|cache','18'],['playbook|interview process|mock','19']];
function topicsFromText(t,allNums){
  var out=[];t=t.toLowerCase();
  KEYWORDS.forEach(function(k){if(new RegExp('\\b('+k[0]+')').test(t)&&allNums.indexOf(k[1])>=0&&out.indexOf(k[1])<0)out.push(k[1])});
  if(/\bdp\b|dynamic programming/.test(t)){['15','16'].forEach(function(n){if(out.indexOf(n)<0)out.push(n)})}
  if(/graph/.test(t)){['12','13'].forEach(function(n){if(out.indexOf(n)<0)out.push(n)})}
  return out.sort();
}
/* offline assistant: understands the common requests when there is no AI key */
function offlineIntent(text,s,allNums,todayISO){
  var t=text.toLowerCase(),patch={},say=[],m;
  if((m=t.match(/(\d+)\s*(weeks?|wks?)/))){patch.weeks=+m[1];say.push('a window of '+m[1]+' weeks')}
  else if((m=t.match(/(\d+)\s*months?/))){patch.weeks=+m[1]*4;say.push('about '+m[1]+' months')}
  if((m=t.match(/(\d+(?:\.\d+)?)\s*(?:h|hrs?|hours?)\s*(?:per|a|each|every|on)?\s*(?:week\s?days?|days?|daily)/))||(m=t.match(/(?:weekdays?|daily|every day)[^\d]{0,12}(\d+(?:\.\d+)?)\s*(?:h|hrs?|hours?)/))){patch.weekdayHours=+m[1];say.push(m[1]+' hours on weekdays');
    if(/every day|daily|7 days/.test(t)){patch.weekendHours=+m[1];patch.restDay='none'}}
  if((m=t.match(/weekends?[^\d]{0,14}(\d+(?:\.\d+)?)\s*(?:h|hrs?|hours?)/))||(m=t.match(/(\d+(?:\.\d+)?)\s*(?:h|hrs?|hours?)[^.]{0,12}weekends?/))){patch.weekendHours=+m[1];say.push(m[1]+' hours on weekends')}
  if(/weekends? only|only (?:on )?weekends?/.test(t)){patch.weekdayHours=0;say.push('weekends only')}
  if(/beginner|new to|just starting|never done/.test(t)){patch.level='beginner';say.push('a beginner pace')}
  else if(/advanced|experienced|already know|strong/.test(t)){patch.level='advanced';say.push('an advanced pace')}
  else if(/intermediate/.test(t)){patch.level='intermediate'}
  if(/lighter|less|easier|relax|slower|busy/.test(t)){patch.depth='light';say.push('lighter practice')}
  else if(/deeper|deep|thorough|more practice|all problems/.test(t)){patch.depth='deep';say.push('deeper practice')}
  else if(/standard|balanced/.test(t))patch.depth='standard';
  if(/crash|urgent|asap|interview (?:next|in)|faster|quick/.test(t)){patch.depth=patch.depth||'light';say.push('a faster, interview-focused plan')}
  var sel=topicsFromText(text,allNums);
  if(sel.length){
    if(/\b(only|just|focus|focusing)\b/.test(t)){patch.topics=sel;say.push('only topics '+sel.join(', '))}
    else if(/\b(skip|remove|without|drop|exclude)\b/.test(t)){patch.topics=s.topics.filter(function(n){return sel.indexOf(n)<0});say.push('without topics '+sel.join(', '))}
    else if(/\b(add|include|also)\b/.test(t)){patch.topics=s.topics.concat(sel.filter(function(n){return s.topics.indexOf(n)<0}));say.push('adding topics '+sel.join(', '))}
  }
  if(/fell behind|behind|missed|restart|start over|re-?plan/.test(t)){patch.startDate=todayISO;patch.skipSolved=true;say.push('restarting from today and skipping what you have already solved')}
  var clean=sanitize(patch,allNums);
  return {patch:Object.keys(clean).length?clean:null,say:say};
}

/* pull the <settings> block out of a model reply and validate it */
function parseAgentReply(text,allNums){
  var m=text.match(/<settings>([\s\S]*?)<\/settings>/),patch=null;
  if(m){try{var p=sanitize(JSON.parse(m[1]),allNums);if(Object.keys(p).length)patch=p}catch(e){}}
  var shown=text.replace(/<settings>[\s\S]*?(<\/settings>|$)/g,'').replace(/<\/?s(e(t(t(i(n(g(s)?)?)?)?)?)?)?$/,'').trim();
  return {text:shown,patch:patch};
}

return {EFF:EFF,LEVEL:LEVEL,DEPTHS:DEPTHS,DEPTH_LABEL:DEPTH_LABEL,iso:iso,parseISO:parseISO,addDays:addDays,diffDays:diffDays,mondayOf:mondayOf,fmtDay:fmtDay,fmtShort:fmtShort,fmtMin:fmtMin,
  defaultSettings:defaultSettings,sanitize:sanitize,merge:merge,capacity:capacity,buildItems:buildItems,schedule:schedule,generate:generate,toText:toText,toICS:toICS,
  offlineIntent:offlineIntent,parseAgentReply:parseAgentReply,topicsFromText:topicsFromText};
})();
if(typeof module!=='undefined')module.exports=PlannerCore;
