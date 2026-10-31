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
 open('Start here','content','start');
 kids.forEach(function(e){
  if(e.matches('section.pat')){seenPat=true;var lab=e.classList.contains('lab');var v=open(textOf(e,'h3'),e.id,lab?'lab':'lesson');pend.forEach(function(p){v.els.push(p)});pend=[];v.els.push(e)}
  else if(e.tagName==='H2'&&headsPat(e)){pend.push(e)}
  else if(pend.length&&e.tagName==='P'){pend.push(e)}
  else if(!seenPat){cur.els.push(e)}
  else if(e.tagName==='H2'){open(textOf(e),e.id,'wrap').els.push(e)}
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
 function mark(i){[].forEach.call(side.querySelectorAll('a'),function(a){a.classList.remove('act');a.removeAttribute('aria-current')});
  var a=side.querySelector('a[href="#'+views[i].key+'"]')||(i===0?side.querySelector('a[href="#why"]'):null);if(a){a.classList.add('act');a.setAttribute('aria-current','step')}
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
 apply(pref!=='all',false);
 if(location.hash)setTimeout(function(){go(true)},0);
})();
