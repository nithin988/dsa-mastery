/* Systems module reader: one step at a time (default) or everything on one page.
   A module becomes a path of steps: Start here, each lesson, each lab, then each wrap-up section.
   The URL hash picks the step, so links, the sidebar and the back button all work. */
(function(){
 var main=document.getElementById('content'),side=document.querySelector('nav.side');if(!main||!side)return;
 var K='sys-view',btn=document.getElementById('b-view'),views=[],cur=null,idx=0,seenPat=false,pend=[];
 var kids=[].slice.call(main.children).filter(function(e){return !e.classList.contains('chips')});
 function textOf(e,sel){var h=sel?e.querySelector(sel):e;return h?h.textContent.replace(/\s+/g,' ').trim():''}
 function open(title,key,kind){cur={els:[],title:title,key:key,kind:kind};views.push(cur);return cur}
 function headsPat(h){var n=h.nextElementSibling;while(n&&n.tagName==='P')n=n.nextElementSibling;return !!(n&&n.matches('section.pat'))}
 var GROUP={playbooks:'pc',cases:'pc',cheat:'rev',interview:'rev',selftest:'rev',recall:'rev',sources:'more',plan:'more'},GROUP_TITLE={pc:'Playbooks and real cases',rev:'Interview and revision',more:'Further reading and study plan'};
 open('Start here','content','start');
 kids.forEach(function(e){
  if(e.matches('section.pat')){seenPat=true;var lab=e.classList.contains('lab');var v=open(textOf(e,'h3'),e.id,lab?'lab':'lesson');pend.forEach(function(p){v.els.push(p)});pend=[];v.els.push(e)}
  else if(e.tagName==='H2'&&headsPat(e)){pend.push(e)}
  else if(pend.length&&e.tagName==='P'){pend.push(e)}
  else if(!seenPat){cur.els.push(e)}
  else if(e.tagName==='H2'){var g=GROUP[e.id];
   if(g&&cur.group===g){cur.els.push(e)}
   else{var v2=open(g?GROUP_TITLE[g]:textOf(e),e.id,'wrap');v2.group=g;v2.els.push(e)}}
  else{cur.els.push(e)}
 });
 views.forEach(function(v,i){
  v.ids={};v.els.forEach(function(e){if(e.id)v.ids[e.id]=1;[].forEach.call(e.querySelectorAll('[id]'),function(x){v.ids[x.id]=1})});
  var last=v.els[v.els.length-1],bar=document.createElement('div');bar.className='vnav';
  var p=views[i-1],n=views[i+1],lesson=v.kind==='lesson';
  bar.innerHTML=(p?'<a class="vp" href="#'+p.key+'"><small>Previous</small><b>'+esc(p.title)+'</b></a>':'<span></span>')+
   (n?'<a class="vn" href="#'+n.key+'" data-done="'+(lesson?'1':'')+'"><small>'+(lesson?'Done, next':'Next')+'</small><b>'+esc(n.title)+'</b></a>':'<span></span>');
  last.parentNode.insertBefore(bar,last.nextSibling);v.els.push(bar);
  v.els.forEach(function(e){e.setAttribute('data-vw',i)});
 });
 function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;')}
 function find(h){if(!h||h==='content')return 0;for(var i=0;i<views.length;i++)if(views[i].ids[h]||views[i].key===h)return i;return 0}
 var tk=document.getElementById('track'),tkItems=[];
 function boxOf(v){var sec=v.els.filter(function(x){return x.matches&&x.matches('section.pat')})[0];return sec?sec.querySelector('.pk'):null}
 function buildTrack(){if(!tk)return;var mid=document.body.getAttribute('data-topic')||'';
  var items=views.filter(function(v){return v.kind==='lesson'||v.kind==='lab'});
  var h='<div class="tk"><div class="tk-top"><svg class="tk-ring" viewBox="0 0 64 64" aria-hidden="true"><circle class="bg" cx="32" cy="32" r="26"/><circle class="fg" cx="32" cy="32" r="26" transform="rotate(-90 32 32)" stroke-dasharray="163.4" stroke-dashoffset="163.4"/><text x="32" y="37" text-anchor="middle" id="tk-pct">0%</text></svg><div><b>Your progress</b><span id="tk-txt"></span></div></div><h4>Steps</h4><ol class="tk-list">';
  items.forEach(function(v,i){tkItems.push({v:v,box:boxOf(v)});h+='<li><a href="#'+v.key+'" data-k="'+i+'"><span class="d"></span><span>'+esc(v.title.replace(/^Lab \d+: /,'Lab: '))+'</span></a></li>'});
  h+='</ol><a class="tk-go" href="#" id="tk-next">Continue</a><a class="tk-rev" href="../revise.html#'+esc(mid)+'">Quick revision for this module</a></div>';
  tk.innerHTML=h;paintTrack()}
 function paintTrack(){if(!tk||!tkItems.length)return;var done=0,next=null;
  [].forEach.call(tk.querySelectorAll('.tk-list a'),function(a,i){var it=tkItems[i],d=it.box&&it.box.checked;if(d)done++;else if(!next)next=it;
   a.classList.toggle('done',!!d);a.classList.toggle('cur',views[idx]===it.v&&document.body.classList.contains('focus'))});
  var pct=Math.round(done*100/tkItems.length);tk.querySelector('.fg').setAttribute('stroke-dashoffset',(163.4*(1-pct/100)).toFixed(1));
  document.getElementById('tk-pct').textContent=pct+'%';document.getElementById('tk-txt').textContent=done+' of '+tkItems.length+' steps done';
  var go=document.getElementById('tk-next');if(go){if(next){go.textContent=(done?'Continue: ':'Start: ')+next.v.title.replace(/^Lab \d+: /,'Lab: ');go.setAttribute('href','#'+next.v.key)}else{go.textContent='All steps done: revise the interview questions';go.setAttribute('href','#interview')}}}
 function mark(i){paintTrack();[].forEach.call(side.querySelectorAll('a'),function(a){a.classList.remove('act');a.removeAttribute('aria-current')});
  var hh=decodeURIComponent((location.hash||'').slice(1));var a=(hh&&views[i].ids[hh]?side.querySelector('a[href="#'+hh+'"]'):null)||side.querySelector('a[href="#'+views[i].key+'"]')||(i===0?side.querySelector('a[href="#why"]'):null);if(a){a.classList.add('act');a.setAttribute('aria-current','step')}
  [].forEach.call(document.querySelectorAll('.chips a'),function(c){c.classList.toggle('on',c.getAttribute('href')==='#'+views[i].key)});
  var pr=document.getElementById('vpos');if(pr)pr.textContent='Step '+(i+1)+' of '+views.length}
 function show(i){idx=i;views.forEach(function(v,j){v.els.forEach(function(e){e.classList.toggle('vh',j!==i)})});mark(i)}
 function go(scroll){var h=decodeURIComponent((location.hash||'').slice(1)),i=find(h);if(document.body.classList.contains('focus'))show(i);
  if(scroll!==false){var t=h&&h!=='content'?document.getElementById(h):null;var y=t?t.getBoundingClientRect().top+window.scrollY-84:main.getBoundingClientRect().top+window.scrollY-84;window.scrollTo(0,Math.max(0,y))}}
 function apply(focus,save){document.body.classList.toggle('focus',focus);
  if(btn){btn.setAttribute('aria-pressed',focus?'false':'true');btn.firstChild.textContent=focus?'All on one page':'One step at a time';btn.classList.toggle('on',!focus)}
  if(focus)show(find((location.hash||'').slice(1)));else views.forEach(function(v){v.els.forEach(function(e){e.classList.remove('vh')})});
  if(save)try{localStorage.setItem(K,focus?'focus':'all')}catch(e){}}
 main.addEventListener('click',function(e){var a=e.target.closest('a.vn[data-done="1"]');if(!a)return;
  var sec=views[idx].els.filter(function(x){return x.matches&&x.matches('section.pat')})[0];var bx=sec&&sec.querySelector('.pk');if(bx&&!bx.checked)bx.click()});
 window.addEventListener('hashchange',function(){go(true)});
 window.addEventListener('beforeprint',function(){views.forEach(function(v){v.els.forEach(function(e){e.classList.remove('vh')})})});
 window.addEventListener('afterprint',function(){if(document.body.classList.contains('focus'))show(idx)});
 if(btn)btn.onclick=function(){var f=!document.body.classList.contains('focus');apply(f,true);if(f)go(false)};
 var pref='focus';try{pref=localStorage.getItem(K)||'focus'}catch(e){}
 buildTrack();
 document.addEventListener('change',function(e){if(e.target&&e.target.classList&&e.target.classList.contains('pk'))setTimeout(paintTrack,0)});
 apply(pref!=='all',false);
 setTimeout(paintTrack,50);
 if(location.hash)setTimeout(function(){go(true)},0);
})();
