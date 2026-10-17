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
function graphSVG(s){var g=s.graph,W=g.w||360,H=g.h||210,R=17,lines='',nodes='',lab={};
 Object.keys(s.ptr||{}).forEach(function(k){(lab[s.ptr[k]]=lab[s.ptr[k]]||[]).push(k)});
 function esc(t){return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;')}
 g.edges.forEach(function(e,k){var a=g.nodes[e[0]],b=g.nodes[e[1]],on=(s.eok||[]).indexOf(k)>=0,x1=a.x,y1=a.y,x2=b.x,y2=b.y,mk='';
  if(g.directed){var dx=x2-x1,dy=y2-y1,L=Math.sqrt(dx*dx+dy*dy)||1;x1+=dx/L*R;y1+=dy/L*R;x2-=dx/L*(R+4);y2-=dy/L*(R+4);mk=' marker-end="url(#'+(on?'garrOn':'garr')+')"'}
  lines+='<line class="ge'+(on?' on':'')+'" x1="'+x1+'" y1="'+y1+'" x2="'+x2+'" y2="'+y2+'"'+mk+'/>';
  if(e[2]!==undefined)lines+='<text class="gw" x="'+((a.x+b.x)/2)+'" y="'+((a.y+b.y)/2-6)+'">'+esc(e[2])+'</text>'});
 g.nodes.forEach(function(n,i){var c='tn'+((s.hi||[]).indexOf(i)>=0?' in':'')+((s.ok||[]).indexOf(i)>=0?' ok':'')+((s.dim||[]).indexOf(i)>=0?' dim':'');
  nodes+='<g class="'+c+'"><circle cx="'+n.x+'" cy="'+n.y+'" r="'+R+'"/><text x="'+n.x+'" y="'+n.y+'">'+esc(n.label===undefined?i:n.label)+'</text></g>';
  if(lab[i])nodes+='<text class="tp" x="'+n.x+'" y="'+(n.y-R-7)+'">'+esc(lab[i].join(', '))+'</text>'});
 var defs='<defs><marker id="garr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="mk" d="M0,0 L10,5 L0,10 z"/></marker><marker id="garrOn" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="mk2" d="M0,0 L10,5 L0,10 z"/></marker></defs>';
 return '<svg viewBox="0 0 '+W+' '+H+'" style="width:100%;max-width:'+W+'px" role="img" aria-label="Graph">'+defs+lines+nodes+'</svg>'}

function treeSVG(s){var T=s.tree,n=T.length,last=0,i;for(i=0;i<n;i++)if(T[i]!==null&&T[i]!==undefined)last=i;
 var D=Math.floor(Math.log2(last+1))+1,W=Math.max(300,Math.pow(2,D-1)*56),H=D*64+30,R=18;
 function pos(k){var d=Math.floor(Math.log2(k+1)),j=k-(Math.pow(2,d)-1),w=Math.pow(2,d);return {x:(j+0.5)/w*W,y:d*64+40}}
 var lines='',nodes='',lab={};Object.keys(s.ptr||{}).forEach(function(k){(lab[s.ptr[k]]=lab[s.ptr[k]]||[]).push(k)});
 for(i=0;i<=last;i++){if(T[i]===null||T[i]===undefined)continue;var p=pos(i);
  if(i>0){var par=Math.floor((i-1)/2);if(T[par]!==null&&T[par]!==undefined){var q=pos(par);lines+='<line x1="'+q.x+'" y1="'+q.y+'" x2="'+p.x+'" y2="'+p.y+'"/>'}}
  var c='tn'+((s.hi||[]).indexOf(i)>=0?' in':'')+((s.ok||[]).indexOf(i)>=0?' ok':'')+((s.dim||[]).indexOf(i)>=0?' dim':'');
  nodes+='<g class="'+c+'"><circle cx="'+p.x+'" cy="'+p.y+'" r="'+R+'"/><text x="'+p.x+'" y="'+p.y+'">'+String(T[i]).replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</text></g>';
  if(lab[i])nodes+='<text class="tp" x="'+p.x+'" y="'+(p.y-R-7)+'">'+lab[i].join(', ').replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</text>'}
 return '<svg viewBox="0 0 '+W+' '+H+'" style="width:100%;max-width:'+W+'px" role="img" aria-label="Binary tree">'+lines+nodes+'</svg>'}

function stepper(el){
 var steps=SIM[el.dataset.sim](),i=0,timer=null,speed=1300,max=0;
 steps.forEach(function(s){max=Math.max(max,(s.a||[]).length)});
 el.setAttribute('tabindex','0');el.setAttribute('aria-label','Step-by-step animation');
 el.innerHTML='<div class="st-prog"><i></i></div><div class="st-view"></div><div class="st-tree" style="display:none"></div><div class="st-aux"></div><div class="st-note" aria-live="polite"></div>'+
  '<div class="st-ctl"><button data-a="prev" title="Previous (←)">◀</button><button data-a="play" title="Play / pause (space)">▶ Play</button><button data-a="next" title="Next (→)">▶|</button><button data-a="reset" title="Restart">↺</button>'+
  '<input type="range" min="0" max="'+(steps.length-1)+'" value="0" aria-label="Step"><select aria-label="Speed"><option value="2200">Slow</option><option value="1300" selected>Normal</option><option value="600">Fast</option></select><span class="st-count"></span></div>';
 var view=$('.st-view',el),aux=$('.st-aux',el),note=$('.st-note',el),cnt=$('.st-count',el),play=$('[data-a=play]',el),bar=$('.st-prog i',el),rg=$('input',el),sel=$('select',el);
 var cells=[],h='';for(var k=0;k<max;k++)h+='<div class="cellw"><div class="ptr"></div><div class="cell"></div><div class="idx">'+k+'</div></div>'+(k<max-1?'<div class="edge"></div>':'');
 view.innerHTML=h;$$('.cellw',view).forEach(function(w){cells.push({w:w,p:$('.ptr',w),c:$('.cell',w),v:null})});var edges=$$('.edge',view);
 var tb=$('.st-tree',el);
 function draw(){var s=steps[i],lab={};
  if(s.tree||s.graph){view.style.display='none';tb.style.display='block';tb.innerHTML=s.tree?treeSVG(s):graphSVG(s)}else{view.style.display='';tb.style.display='none';tb.innerHTML=''}
  s.a=s.a||[];Object.keys(s.ptr||{}).forEach(function(k){var ix=s.ptr[k];(lab[ix]=lab[ix]||[]).push(k)});
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
