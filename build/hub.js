/* hub page: per-course progress and "continue" links, from the two separate progress stores */
var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
function ls(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v)}catch(e){return null}}
var th=ls('dsa-theme');if(th)document.documentElement.dataset.theme=th;
$('#b-theme').onclick=function(){var d=document.documentElement,dark=d.dataset.theme==='dark';d.dataset.theme=dark?'light':'dark';ls('dsa-theme',d.dataset.theme)};
function read(k){try{return JSON.parse(ls(k)||'{}')}catch(e){return {}}}
function course(pid,list,store,lastKey,dir,noun){
  var prog=read(store),total=0,solved=0;
  list.forEach(function(t){var n=0;Object.keys(prog).forEach(function(k){if(k.indexOf(t.id+'-')===0)n++});t.solved=n;total+=t.total;solved+=Math.min(n,t.total)});
  var pct=total?Math.round(100*solved/total):0,st=$('#st-'+pid);
  $('#m-'+pid).style.width=pct+'%';
  $('#t-'+pid).textContent=solved===0?'Not started':solved+' of '+total+' '+noun+' ('+pct+'%)';
  st.textContent=solved===0?'Not started':pct>=100?'Done':'In progress';st.className='st '+(solved===0?'':pct>=100?'done':'doing');
  var last=ls(lastKey),lt=list.filter(function(t){return t.file===last})[0];
  if(lt){var nx=lt.solved>=lt.total?list[list.indexOf(lt)+1]:lt;if(nx){var a=$('#cont-'+pid);a.href=dir+nx.file+'.html';$('span',a).textContent=(lt.solved>=lt.total?'Next: ':'Continue: ')+nx.num+' '+nx.title;a.hidden=false;$('#open-'+pid).classList.remove('pri');a.classList.add('pri')}}
}
course('dsa',window.HUB_DSA||[],'dsa-progress','dsa-last','topics/','problems solved');
course('sys',window.HUB_SYS||[],'sys-progress','sys-last','systems/','steps done');
function share(btn){var url=location.href.split('#')[0],lab=$('span',btn);
 function done(){var old=lab.textContent;lab.textContent='Link copied';setTimeout(function(){lab.textContent=old},1600)}
 if(navigator.share){navigator.share({title:'Mastery',text:'Free study courses for engineers: DSA, Linux, Git, troubleshooting and system design.',url:url}).catch(function(){})}
 else if(navigator.clipboard){navigator.clipboard.writeText(url).then(done,function(){})}}
$$('[data-share]').forEach(function(b){b.onclick=function(){share(b)}});
