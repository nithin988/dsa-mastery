var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
function ls(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v)}catch(e){return null}}
function ic(n,c){return '<svg class="ic '+(c||'')+'" viewBox="0 0 16 16" aria-hidden="true">'+IC[n]+'</svg>'}
var th=ls('dsa-theme');if(th)document.documentElement.dataset.theme=th;
$('#b-theme').onclick=function(){var d=document.documentElement,dark=d.dataset.theme==='dark';d.dataset.theme=dark?'light':'dark';ls('dsa-theme',d.dataset.theme)};
var T=window.DSA_TOPICS||[],prog={},B=document.body,STORE=B.dataset.store||'dsa-progress',LASTK=B.dataset.last||'dsa-last',DIR=B.dataset.dir||'topics/',WORD=B.dataset.word||'solved';
try{prog=JSON.parse(ls(STORE)||'{}')}catch(e){}
function solvedFor(id){var n=0;Object.keys(prog).forEach(function(k){if(k.indexOf(id+'-')===0)n++});return n}
var totalAll=0,solvedAll=0,state={q:'',f:'all'};
T.forEach(function(t){t.solved=solvedFor(t.id);t.status=t.solved===0?'new':(t.solved>=t.total?'done':'doing');totalAll+=t.total;solvedAll+=Math.min(t.solved,t.total)});
/* per-card progress */
$$('.tcard').forEach(function(c){var t=T.filter(function(x){return x.file===c.dataset.file})[0];if(!t)return;
 var st=$('.st',c),m=$('.meter i',c),txt=$('.solved',c),pc=t.total?100*Math.min(t.solved,t.total)/t.total:0;
 st.className='st '+(t.status==='doing'?'doing':t.status==='done'?'done':'');st.textContent=t.status==='new'?'Not started':t.status==='doing'?'In progress':'Done';
 m.style.width=pc+'%';txt.textContent=Math.min(t.solved,t.total)+' / '+t.total+' '+WORD;c.dataset.status=t.status});
/* overall */
var pct=totalAll?Math.round(100*solvedAll/totalAll):0;
$('#k-pct').textContent=pct+'%';$('#k-bar').style.width=pct+'%';$('#k-txt').textContent=solvedAll+' of '+totalAll+' '+(B.dataset.unit||'problems')+' '+WORD+' (saved in this browser)';
$('#k-meter').setAttribute('aria-valuenow',pct);
var done=T.filter(function(t){return t.status==='done'}).length;$('#k-topics').textContent=done+' / '+T.length+' '+(B.dataset.noun||'topics')+' done';
/* continue where you left off */
var last=ls(LASTK),lt=T.filter(function(t){return t.file===last})[0];
if(lt){var nx=lt.status==='done'?T[T.indexOf(lt)+1]:lt;var a=$('#cta-continue');if(nx){a.href=DIR+nx.file+'.html';$('span',a).textContent=(lt.status==='done'?'Next: ':'Continue: ')+nx.num+' '+nx.title;a.hidden=false;$('#cta-start').classList.remove('pri');$('#cta-start').classList.add('sec');a.classList.add('pri')}}
/* filter and search */
function apply(){var q=state.q.trim().toLowerCase(),shown=0;
 $$('.tcard').forEach(function(c){var ok=(state.f==='all'||c.dataset.status===state.f)&&(!q||c.dataset.title.toLowerCase().indexOf(q)>=0||c.dataset.blurb.toLowerCase().indexOf(q)>=0||c.dataset.num.indexOf(q)>=0);c.hidden=!ok;if(ok)shown++});
 $$('.phase').forEach(function(p){p.hidden=!$$('.tcard',p).some(function(c){return !c.hidden})});
 $('#empty').hidden=shown>0;$('#count').textContent=shown+' of '+$$('.tcard').length+' '+(B.dataset.noun||'topics')}
$('#q').oninput=function(){state.q=this.value;apply()};
$$('.filters button').forEach(function(b){b.onclick=function(){state.f=b.dataset.f;$$('.filters button').forEach(function(x){x.setAttribute('aria-pressed',x===b)});apply()}});
apply();
/* share */
function share(btn){var url=location.href.split('#')[0],lab=$('span',btn);
 function done(){var old=lab.textContent;lab.textContent='Link copied';setTimeout(function(){lab.textContent=old},1600)}
 if(navigator.share){navigator.share({title:'DSA Mastery',text:'Free pattern-based DSA study sheets with animations, Java and Python code.',url:url}).catch(function(){})}
 else if(navigator.clipboard){navigator.clipboard.writeText(url).then(done,function(){})}}
$$('[data-share]').forEach(function(b){b.onclick=function(){share(b)}});
