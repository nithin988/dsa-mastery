/* left section rail: mobile drawer behaviour (desktop is pure CSS: hover or focus expands it) */
(function(){var r=document.getElementById('rail'),b=document.getElementById('b-rail'),bd=document.getElementById('rail-bd');if(!r)return;
 function open(o){r.classList.toggle('open',o);if(bd)bd.hidden=!o;if(b)b.setAttribute('aria-expanded',o?'true':'false')}
 if(b)b.onclick=function(){open(!r.classList.contains('open'))};
 if(bd)bd.onclick=function(){open(false)};
 document.addEventListener('keydown',function(e){if(e.key==='Escape'&&r.classList.contains('open')){open(false);if(b)b.focus()}});
 r.addEventListener('click',function(e){if(e.target.closest('a')&&innerWidth<=1020)open(false)});
})();

/* density switch: short view by default, "Show all details" opens every folded explanation */
(function(){var b=document.getElementById('b-density');if(!b)return;var K='sys-density';
 function apply(on,save){document.body.classList.toggle('full',on);b.setAttribute('aria-pressed',on?'true':'false');
  b.firstChild.textContent=on?'Short view':'Show all details';b.classList.toggle('on',on);
  [].forEach.call(document.querySelectorAll('details.more'),function(d){d.open=on});
  if(save)try{localStorage.setItem(K,on?'full':'short')}catch(e){}}
 b.onclick=function(){apply(!document.body.classList.contains('full'),true)};
 var v=null;try{v=localStorage.getItem(K)}catch(e){}
 if(v==='full')apply(true,false);
 window.addEventListener('beforeprint',function(){[].forEach.call(document.querySelectorAll('details'),function(d){d.open=true})});
})();
