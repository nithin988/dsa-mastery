var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
function ls(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v)}catch(e){return null}}
var body=document.body;
/* language + theme */
function setLang(l){body.dataset.lang=l;$('#b-java').classList.toggle('on',l==='java');$('#b-py').classList.toggle('on',l==='py');ls('dsa-lang',l)}
setLang(ls('dsa-lang')||'java');
$('#b-java').onclick=function(){setLang('java')};$('#b-py').onclick=function(){setLang('py')};
var th=ls('dsa-theme');if(th)document.documentElement.dataset.theme=th;
$('#b-theme').onclick=function(){var d=document.documentElement,dark=d.dataset.theme?d.dataset.theme==='dark':matchMedia('(prefers-color-scheme:dark)').matches;d.dataset.theme=dark?'light':'dark';ls('dsa-theme',d.dataset.theme)};
/* progress (saved in this browser only) */
function load(){try{return JSON.parse(ls('dsa-progress')||'{}')}catch(e){return {}}}
var prog=load();
function refresh(){var boxes=$$('.pk'),n=0;
 boxes.forEach(function(b){var on=!!prog[b.dataset.k];b.checked=on;b.closest('tr').classList.toggle('done',on);if(on)n++});
 $('#prog').textContent=n+' / '+boxes.length+' solved';$('#pbar').style.width=(boxes.length?100*n/boxes.length:0)+'%';
 $$('.pat').forEach(function(p){var bx=$$('.pk',p),d=bx.filter(function(c){return c.checked}).length,e=$('.pp',p),s=$('nav.side a[href="#'+p.id+'"] .cnt');
  if(e)e.textContent=d+' / '+bx.length+' solved';if(s)s.textContent=d+'/'+bx.length})}
$$('.pk').forEach(function(b){b.onchange=function(){if(b.checked)prog[b.dataset.k]=1;else delete prog[b.dataset.k];ls('dsa-progress',JSON.stringify(prog));refresh()}});
refresh();
/* copy buttons */
$$('.cp').forEach(function(e){e.remove()});
$$('pre').forEach(function(p){var b=document.createElement('button');b.className='cp';b.textContent='Copy';b.onclick=function(){var t=p.querySelector('code').textContent;try{navigator.clipboard.writeText(t);b.textContent='Copied';setTimeout(function(){b.textContent='Copy'},1200)}catch(e){}};p.appendChild(b)});
/* scroll spy */
var links=$$('nav.side a');
if('IntersectionObserver' in window&&links.length){var map={};links.forEach(function(a){map[a.getAttribute('href').slice(1)]=a});
 var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){links.forEach(function(a){a.classList.remove('act')});var a=map[e.target.id];if(a)a.classList.add('act')}})},{rootMargin:'-70px 0px -70% 0px'});
 Object.keys(map).forEach(function(id){var t=document.getElementById(id);if(t)io.observe(t)})}
/* download */
$('#b-dl').onclick=function(){
 var clone=document.documentElement.cloneNode(true);
 $$('.stepper',clone).forEach(function(e){e.innerHTML=''});$$('.cp',clone).forEach(function(e){e.remove()});
 $$('.pk',clone).forEach(function(e){e.removeAttribute('checked')});$$('tr.done',clone).forEach(function(e){e.classList.remove('done')});
 $$('a.act',clone).forEach(function(e){e.classList.remove('act')});
 var h='<!DOCTYPE html>\n'+clone.outerHTML,blob=new Blob([h],{type:'text/html'}),a=document.createElement('a');
 a.href=URL.createObjectURL(blob);a.download=body.dataset.file||'topic.html';document.body.appendChild(a);a.click();a.remove();setTimeout(function(){URL.revokeObjectURL(a.href)},1000)};
/* animated stepper */
function stepper(el){
 var steps=SIM[el.dataset.sim](),i=0,timer=null,speed=1300,max=0;
 steps.forEach(function(s){max=Math.max(max,s.a.length)});
 el.setAttribute('tabindex','0');el.setAttribute('aria-label','Step-by-step animation');
 el.innerHTML='<div class="st-prog"><i></i></div><div class="st-view"></div><div class="st-aux"></div><div class="st-note" aria-live="polite"></div>'+
  '<div class="st-ctl"><button data-a="prev" title="Previous (←)">◀</button><button data-a="play" title="Play / pause (space)">▶ Play</button><button data-a="next" title="Next (→)">▶|</button><button data-a="reset" title="Restart">↺</button>'+
  '<input type="range" min="0" max="'+(steps.length-1)+'" value="0" aria-label="Step"><select aria-label="Speed"><option value="2200">Slow</option><option value="1300" selected>Normal</option><option value="600">Fast</option></select><span class="st-count"></span></div>';
 var view=$('.st-view',el),aux=$('.st-aux',el),note=$('.st-note',el),cnt=$('.st-count',el),play=$('[data-a=play]',el),bar=$('.st-prog i',el),rg=$('input',el),sel=$('select',el);
 var cells=[],h='';for(var k=0;k<max;k++)h+='<div class="cellw"><div class="ptr"></div><div class="cell"></div><div class="idx">'+k+'</div></div>'+(k<max-1?'<div class="edge"></div>':'');
 view.innerHTML=h;$$('.cellw',view).forEach(function(w){cells.push({w:w,p:$('.ptr',w),c:$('.cell',w),v:null})});var edges=$$('.edge',view);
 function draw(){var s=steps[i],lab={};Object.keys(s.ptr||{}).forEach(function(k){var ix=s.ptr[k];(lab[ix]=lab[ix]||[]).push(k)});
  cells.forEach(function(o,ix){if(ix>=s.a.length){o.w.style.display='none';return}o.w.style.display='';
   var v=String(s.a[ix]);if(o.v!==null&&o.v!==v){o.c.classList.remove('pop');void o.c.offsetWidth;o.c.classList.add('pop')}
   o.v=v;o.c.textContent=v;
   o.c.className='cell'+((s.hi||[]).indexOf(ix)>=0?' in':'')+((s.ok||[]).indexOf(ix)>=0?' ok':'')+((s.dim||[]).indexOf(ix)>=0?' dim':'')+(o.c.classList.contains('pop')?' pop':'');
   o.p.innerHTML=lab[ix]?'<b>'+lab[ix].join(', ')+'</b>':''});
  view.style.maxWidth=s.cols?(s.cols*53)+'px':'';
  edges.forEach(function(g,k){var t=k<s.a.length-1?(s.edges?(s.edges[k]||''):(s.link?'→':'')):'';g.textContent=t;g.style.display=t?'':'none'});
  if(s.aux){aux.innerHTML='<span class="al">'+s.aux.label+'</span>'+s.aux.items.map(function(t){return '<span class="chip">'+String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</span>'}).join('')}else aux.innerHTML='';
  note.textContent=s.note;cnt.textContent=(i+1)+' / '+steps.length;bar.style.width=(100*(i+1)/steps.length)+'%';rg.value=i}
 function stop(){if(timer){clearInterval(timer);timer=null;play.textContent='▶ Play'}}
 function go(n){i=Math.max(0,Math.min(steps.length-1,n));draw()}
 function start(){if(i>=steps.length-1)i=0;play.textContent='❚❚ Pause';draw();timer=setInterval(function(){if(i<steps.length-1){i++;draw()}else stop()},speed)}
 $('[data-a=prev]',el).onclick=function(){stop();go(i-1)};$('[data-a=next]',el).onclick=function(){stop();go(i+1)};
 $('[data-a=reset]',el).onclick=function(){stop();go(0)};play.onclick=function(){timer?stop():start()};
 rg.oninput=function(){stop();go(+rg.value)};sel.onchange=function(){speed=+sel.value;if(timer){stop();start()}};
 el.onkeydown=function(e){if(e.target!==el)return;if(e.key==='ArrowRight'){stop();go(i+1);e.preventDefault()}else if(e.key==='ArrowLeft'){stop();go(i-1);e.preventDefault()}else if(e.key===' '){timer?stop():start();e.preventDefault()}};
 draw()}
$$('.stepper').forEach(stepper);
