/* Quick revision page: interview questions, flashcards and cheat sheets drawn from every live module. */
var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
function ls(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v)}catch(e){return null}}
var th=ls('dsa-theme');if(th)document.documentElement.dataset.theme=th;
$('#b-theme').onclick=function(){var d=document.documentElement,dark=d.dataset.theme==='dark';d.dataset.theme=dark?'light':'dark';ls('dsa-theme',d.dataset.theme)};
$$('[data-share]').forEach(function(b){b.onclick=function(){var u=location.href.split('#')[0];if(navigator.share){navigator.share({title:document.title,url:u}).catch(function(){})}else if(navigator.clipboard){navigator.clipboard.writeText(u);b.querySelector('span:last-child').textContent='Link copied'}}});
var D=window.REVISE,mods=D.modules;
function esc(t){return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function md(t){return esc(t).replace(/`([^`]+)`/g,'<code>$1</code>').replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>')}
function lis(a){return '<ul>'+a.map(function(x){return '<li>'+md(x)+'</li>'}).join('')+'</ul>'}
var st={tab:'q',mod:'all',angle:false,text:'',unknown:false,deck:[],i:0,flip:false};
var known={};try{known=JSON.parse(ls('rev-known')||'{}')}catch(e){}
function saveKnown(){ls('rev-known',JSON.stringify(known))}
function chosen(){return mods.filter(function(m){return st.mod==='all'||m.id===st.mod})}
function company(a){if(!a)return '';if(/amazon/i.test(a))return 'Amazon-style';if(/google/i.test(a))return 'Google-style';return 'Large tech (reported)'}

function viewQ(){var h='',n=0,t=st.text.toLowerCase();
 chosen().forEach(function(m){m.interview.forEach(function(q){
  if(st.angle&&!q.angle)return;
  if(t&&(q.q+' '+q.a.join(' ')).toLowerCase().indexOf(t)<0)return;
  n++;var c=company(q.angle);
  h+='<details class="qa"><summary><span class="mtag">'+esc(m.num)+'</span> '+md(q.q)+(c?' <span class="co">'+esc(c)+'</span>':'')+'</summary><div class="qa-b">'
   +'<span class="lbl">Shape of a strong answer</span>'+lis(q.a)
   +(q.follow&&q.follow.length?'<span class="lbl">Follow-ups to expect</span>'+lis(q.follow):'')
   +(q.mistakes&&q.mistakes.length?'<span class="lbl">Common mistakes</span>'+lis(q.mistakes):'')
   +(q.angle?'<p class="angle"><b>Company angle:</b> '+md(q.angle)+'</p>':'')
   +'<p class="muted"><a href="systems/'+esc(m.file)+'#interview">Open in module '+esc(m.num)+'</a></p></div></details>'})});
 return '<div class="rv-bar"><label class="search" style="flex:1;min-width:200px"><input id="rq" type="search" placeholder="Search questions" value="'+esc(st.text)+'" aria-label="Search questions"></label>'
  +'<label class="chk"><input type="checkbox" id="rang"'+(st.angle?' checked':'')+'> Company-angle questions only</label><span class="muted">'+n+' questions</span></div>'
  +'<p class="muted">Tip: read the question, answer out loud for one minute, then open it and compare. Company angles are themes candidates report, not official lists.</p>'
  +(h||'<p class="empty">No questions match.</p>')}

function buildDeck(){var d=[];chosen().forEach(function(m){
  (m.selftest||[]).forEach(function(p,i){d.push({id:m.id+':s:'+i,m:m,f:p[0],b:p[1]})});
  (m.recall||[]).forEach(function(p,i){d.push({id:m.id+':r:'+i,m:m,f:'In one line: '+p[0],b:p[1]})})});
 if(st.unknown)d=d.filter(function(c){return !known[c.id]});
 for(var i=d.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1)),x=d[i];d[i]=d[j];d[j]=x}
 st.deck=d;st.i=0;st.flip=false}
function viewF(){var d=st.deck,tot=0,kn=0;chosen().forEach(function(m){tot+=(m.selftest||[]).length+(m.recall||[]).length});
 Object.keys(known).forEach(function(k){if(chosen().some(function(m){return k.indexOf(m.id+':')===0}))kn++});
 var c=d[st.i],h='<div class="rv-bar"><label class="chk"><input type="checkbox" id="runk"'+(st.unknown?' checked':'')+'> Hide cards I know</label><button class="btn" id="rshuf">Shuffle</button><button class="btn" id="rreset">Reset progress</button><span class="muted">'+kn+' of '+tot+' known</span></div>';
 if(!c)return h+'<p class="empty">'+(tot&&kn>=tot?'You know every card in this selection. Nice.':'No cards.')+'</p>';
 h+='<div class="fc" id="fc" tabindex="0" role="button" aria-label="Flip card"><div class="fc-m">'+esc(c.m.num)+' · '+esc(c.m.title)+' · card '+(st.i+1)+' of '+d.length+'</div>'
  +'<div class="fc-t">'+(st.flip?md(c.b):md(c.f))+'</div><div class="fc-h">'+(st.flip?'Answer':'Question')+' · press Space or click to flip</div></div>'
  +'<div class="fc-a"><button class="btn" id="fprev">Previous</button><button class="btn" id="fagain">Again later</button><button class="btn pri" id="fknow">I know it</button><button class="btn" id="fnext">Next</button></div>';
 return h}

function viewC(){var h='<p class="muted">One page per module. Print it or keep it next to your terminal.</p>';
 chosen().forEach(function(m){h+='<details class="qa"'+(st.mod!=='all'?' open':'')+'><summary><span class="mtag">'+esc(m.num)+'</span> '+esc(m.title)+' <span class="muted">('+m.cheat.length+' lines)</span></summary><div class="qa-b"><div class="tw"><table><thead><tr><th>Command or idea</th><th>What it does</th></tr></thead><tbody>'
  +m.cheat.map(function(r){return '<tr><td><code>'+esc(r[0])+'</code></td><td>'+md(r[1])+'</td></tr>'}).join('')+'</tbody></table></div></div></details>'});
 return h}

function viewH(){return $('#how-tpl').innerHTML}

function render(){var b=$('#rv-body');
 $$('#rv-tabs button').forEach(function(x){x.setAttribute('aria-pressed',x.dataset.t===st.tab?'true':'false')});
 $('#rv-mod').disabled=st.tab==='h';
 b.innerHTML=st.tab==='q'?viewQ():st.tab==='f'?viewF():st.tab==='c'?viewC():viewH();wire()}
function wire(){var q=$('#rq');if(q){q.oninput=function(){st.text=q.value;var p=q.selectionStart;render();var n=$('#rq');n.focus();n.setSelectionRange(p,p)}}
 var a=$('#rang');if(a)a.onchange=function(){st.angle=a.checked;render()};
 var u=$('#runk');if(u)u.onchange=function(){st.unknown=u.checked;buildDeck();render()};
 var s=$('#rshuf');if(s)s.onclick=function(){buildDeck();render()};
 var r=$('#rreset');if(r)r.onclick=function(){chosen().forEach(function(m){Object.keys(known).forEach(function(k){if(k.indexOf(m.id+':')===0)delete known[k]})});saveKnown();buildDeck();render()};
 var f=$('#fc');if(f){f.onclick=function(){st.flip=!st.flip;render();$('#fc').focus()};f.onkeydown=function(e){if(e.key===' '||e.key==='Enter'){e.preventDefault();f.click()}}}
 function go(d){st.i=(st.i+d+st.deck.length)%st.deck.length;st.flip=false;render()}
 var pv=$('#fprev');if(pv)pv.onclick=function(){go(-1)};var nx=$('#fnext');if(nx)nx.onclick=function(){go(1)};
 var ag=$('#fagain');if(ag)ag.onclick=function(){var c=st.deck.splice(st.i,1)[0];st.deck.push(c);if(st.i>=st.deck.length)st.i=0;st.flip=false;render()};
 var kw=$('#fknow');if(kw)kw.onclick=function(){var c=st.deck[st.i];known[c.id]=1;saveKnown();st.deck.splice(st.i,1);if(st.i>=st.deck.length)st.i=0;st.flip=false;render()}}

var sel=$('#rv-mod');sel.innerHTML='<option value="all">All modules</option>'+mods.map(function(m){return '<option value="'+m.id+'">'+esc(m.num)+' '+esc(m.title)+'</option>'}).join('');
sel.onchange=function(){st.mod=sel.value;buildDeck();render()};
$$('#rv-tabs button').forEach(function(x){x.onclick=function(){st.tab=x.dataset.t;if(st.tab==='f')buildDeck();render();ls('rev-tab',st.tab)}});
(function(){var h=location.hash.slice(1);if(h&&mods.some(function(m){return m.id===h})){st.mod=h;sel.value=h}var t=ls('rev-tab');if(t&&/^[qfch]$/.test(t))st.tab=t;buildDeck();render()})();
