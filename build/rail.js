/* left section rail: mobile drawer behaviour (desktop is pure CSS: hover or focus expands it) */
(function(){var r=document.getElementById('rail'),b=document.getElementById('b-rail'),bd=document.getElementById('rail-bd');if(!r)return;
 function open(o){r.classList.toggle('open',o);if(bd)bd.hidden=!o;if(b)b.setAttribute('aria-expanded',o?'true':'false')}
 if(b)b.onclick=function(){open(!r.classList.contains('open'))};
 if(bd)bd.onclick=function(){open(false)};
 document.addEventListener('keydown',function(e){if(e.key==='Escape'&&r.classList.contains('open')){open(false);if(b)b.focus()}});
 r.addEventListener('click',function(e){if(e.target.closest('a')&&innerWidth<=1020)open(false)});
})();
