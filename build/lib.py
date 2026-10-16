"""Shared renderer for every DSA topic page.

A topic is a dict (see build/arrays.py). `render_topic` turns it into one
self-contained HTML file: no external requests, works offline.
"""
import html
import re

DIFF = {"E": ("Easy", "dE"), "M": ("Medium", "dM"), "H": ("Hard", "dH")}
TIER = {"hot": "🔥 Frequently asked", "sec": "🧊 Secondary"}


def md(s):
    """Tiny inline markup: `code`, **bold**. Everything else is escaped."""
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    return s


def ul(items, tag="ul"):
    return f"<{tag}>" + "".join(f"<li>{md(i)}</li>" for i in items) + f"</{tag}>"


def code_block(java, py):
    return (
        f'<pre class="code-java"><code>{html.escape(java.strip())}</code></pre>'
        f'<pre class="code-py"><code>{html.escape(py.strip())}</code></pre>'
    )


def problems_table(topic_id, probs):
    rows = []
    for lc, name, d, slug, logic, cx in probs:
        label, cls = DIFF[d]
        rows.append(
            f'<tr><td><input type="checkbox" class="pk" data-k="{topic_id}-{lc}" aria-label="Solved LC {lc}"></td>'
            f'<td><a href="https://leetcode.com/problems/{slug}/" target="_blank" rel="noopener">LC {lc}</a></td>'
            f"<td>{html.escape(name)}</td><td class=\"{cls}\">{label}</td>"
            f"<td>{md(logic)}</td><td class=\"cx\">{md(cx)}</td></tr>"
        )
    return (
        '<div class="tw"><table class="ladder"><thead><tr><th></th><th>Problem</th><th>Title</th>'
        "<th>Level</th><th>One-line logic</th><th>Time / Space</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


def render_pattern(topic_id, n, p):
    pid = f"p{n}"
    out = [f'<section class="pat" id="{pid}">']
    out.append(
        f'<h3>Pattern {n} — {html.escape(p["title"])} <span class="tier {p["tier"]}">{TIER[p["tier"]]}</span></h3>'
    )
    out.append(f'<p><strong>When to use</strong> — {md(p["when"])}</p>')
    out.append(f'<p><strong>Detect</strong> — {md(p["detect"])}</p>')
    if p.get("intuition"):
        out.append(f'<div class="callout intu"><strong>Intuition</strong><p>{md(p["intuition"])}</p></div>')
    if p.get("brute"):
        out.append(f'<p><strong>Brute force → optimised</strong> — {md(p["brute"])}</p>')
    out.append(f'<p><strong>Core idea</strong> — {md(p["idea"])}</p>')
    out.append("<p><strong>How it works</strong></p>" + ul(p["steps"], "ol"))
    if p.get("sim"):
        out.append(
            '<p><strong>Watch it run</strong> <span class="muted">(step through it yourself)</span></p>'
            f'<div class="stepper" data-sim="{p["sim"]}"></div>'
        )
    if p.get("trace"):
        out.append(f'<p><strong>Trace</strong> — {md(p["trace_title"])}</p><pre><code>{html.escape(p["trace"].strip())}</code></pre>')
    for label, java, py in p["code"]:
        out.append(f"<p><strong>Skeleton</strong> — {md(label)}</p>" + code_block(java, py))
    out.append(f'<p><strong>Complexity</strong> — {md(p["complexity"])}</p>')
    out.append("<p><strong>Traps</strong></p>" + ul(p["traps"]))
    if p.get("variants"):
        out.append("<p><strong>Variants and follow-ups</strong></p>" + ul(p["variants"]))
    out.append(f'<p><strong>When NOT to use</strong> — {md(p["notuse"])}</p>')
    out.append("<p><strong>Problem ladder</strong> <span class=\"muted\">(easy → hard; tick what you have solved)</span></p>")
    out.append(problems_table(topic_id, p["problems"]))
    out.append("</section>")
    return "\n".join(out)


def table(headers, rows, cls=""):
    h = "".join(f"<th>{html.escape(x)}</th>" for x in headers)
    r = "".join("<tr>" + "".join(f"<td>{md(c)}</td>" for c in row) + "</tr>" for row in rows)
    return f'<div class="tw"><table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{r}</tbody></table></div>'


def render_topic(t):
    tid = t["id"]
    pats = t["patterns"]
    all_keys = sum(len(p["problems"]) for p in pats)
    toc = [("mindset", "The mindset"), ("priority", "Pattern priority"), ("cues", "Problem-cue selector")]
    toc += [(f"p{i+1}", f"{i+1}. {p['title']}") for i, p in enumerate(pats)]
    toc += [("recall", "One-line recall"), ("choose", "Choosing between patterns"), ("selftest", "Self-test"), ("plan", "Study plan")]
    toc_html = "<ol>" + "".join(f'<li><a href="#{a}">{html.escape(b)}</a></li>' for a, b in toc) + "</ol>"

    prio_rows = [
        [str(i + 1), f"**{p['title']}** (P{i+1})", p["why"], p["signature"]] for i, p in enumerate(pats)
    ]
    hot = [r for r, p in zip(prio_rows, pats) if p["tier"] == "hot"]
    sec = [r for r, p in zip(prio_rows, pats) if p["tier"] == "sec"]
    ph = ["#", "Pattern", "Why it matters", "Signature problem"]

    body = []
    body.append(f'<h1>{html.escape(t["title"])}</h1>')
    body.append(f'<p class="lead">{md(t["lead"])}</p>')
    body.append(
        '<div class="callout"><strong>How to use this page.</strong> For each pattern read <em>Detect</em> and '
        "<em>Intuition</em> first, step through the animation, then write the skeleton from memory before opening "
        "the code. Finish by solving the problem ladder in order and ticking each problem; your ticks are saved in "
        "this browser.</div>"
    )
    body.append('<h2 id="contents">Contents</h2>' + toc_html)
    body.append('<h2 id="mindset">The mindset</h2>' + f"<p>{md(t['mindset'])}</p><p>Ask three questions on every array problem:</p>" + ul(t["questions"]))
    body.append(
        '<h2 id="priority">Pattern priority</h2><p class="muted">Ranked by how often these show up in interviews '
        "(judgement from the common interview lists and company question banks, not hard data).</p>"
        "<h3>🔥 Frequently asked — master these first</h3>" + table(ph, hot) + "<h3>🧊 Secondary — know them</h3>" + table(ph, sec)
    )
    body.append('<h2 id="cues">Problem-cue selector</h2>' + table(["If the problem says / looks like…", "Pattern"], t["cues"]))
    body.append("<h2>The patterns</h2>")
    for i, p in enumerate(pats):
        body.append(render_pattern(tid, i + 1, p))
    body.append(
        '<h2 id="recall">One-line recall</h2>'
        + table(["#", "Pattern", "Tier", "Core idea in one line"], [[str(i + 1), p["title"], "🔥" if p["tier"] == "hot" else "🧊", p["oneline"]] for i, p in enumerate(pats)])
    )
    body.append('<h2 id="choose">Choosing between patterns</h2>' + table(["Need", "Use"], t["choose"]) + f"<p><strong>Rule of thumb:</strong> {md(t['rule'])}</p>")
    st = "".join(f"<details><summary>{md(q)}</summary><p>{md(a)}</p></details>" for q, a in t["selftest"])
    body.append('<h2 id="selftest">Self-test</h2><p class="muted">Answer in your head first, then click to reveal.</p>' + st)
    body.append('<h2 id="plan">Study plan</h2>' + ul(t["plan"], "ol"))

    page = PAGE.format(
        title=html.escape(t["title"]),
        fname=t["file"],
        tid=tid,
        total=all_keys,
        css=CSS,
        js=JS,
        body="\n".join(body),
    )
    return page


CSS = """
:root{--bg:#fff;--fg:#1c1f24;--mut:#5b6470;--line:#d9dee5;--card:#f6f8fa;--acc:#0b63d1;--hot:#c2410c;--cool:#0e7490;
--ok:#15803d;--warn:#b45309;--cellbg:#fff;--in:#dbeafe;--okbg:#dcfce7;--dim:#eef0f3;--code:#f2f4f7}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#101418;--fg:#e6e9ee;--mut:#98a2b0;--line:#2b333d;--card:#171c22;--acc:#6cb0ff;--hot:#fb923c;--cool:#22d3ee;--ok:#4ade80;--warn:#fbbf24;--cellbg:#171c22;--in:#16324f;--okbg:#14391f;--dim:#1b2128;--code:#1c222a}}
:root[data-theme=dark]{--bg:#101418;--fg:#e6e9ee;--mut:#98a2b0;--line:#2b333d;--card:#171c22;--acc:#6cb0ff;--hot:#fb923c;--cool:#22d3ee;--ok:#4ade80;--warn:#fbbf24;--cellbg:#171c22;--in:#16324f;--okbg:#14391f;--dim:#1b2128;--code:#1c222a}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}
main{max-width:920px;margin:0 auto;padding:16px 16px 80px}
.bar{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding:8px 16px}
.bar .t{font-weight:700;margin-right:auto}
.bar button,.bar a.btn,.st-ctl button{font:inherit;font-size:13px;padding:5px 11px;border:1px solid var(--line);border-radius:7px;background:var(--card);color:var(--fg);cursor:pointer;text-decoration:none}
.bar button:hover,.bar a.btn:hover,.st-ctl button:hover{border-color:var(--acc)}
.bar button.on{background:var(--acc);color:#fff;border-color:var(--acc)}
.prog{font-size:13px;color:var(--mut)}
h1{font-size:28px;margin:18px 0 6px}
h2{font-size:21px;margin:34px 0 8px;padding-bottom:5px;border-bottom:1px solid var(--line);scroll-margin-top:60px}
h3{font-size:17px;margin:0 0 6px;scroll-margin-top:60px}
.lead{font-size:16px;color:var(--mut)}
.muted{color:var(--mut);font-size:13px;font-weight:400}
a{color:var(--acc)}
code{background:var(--code);padding:1px 5px;border-radius:4px;font:12.5px Consolas,Menlo,monospace}
pre{background:var(--code);border:1px solid var(--line);border-radius:8px;padding:11px 13px;overflow-x:auto;margin:8px 0}
pre code{background:none;padding:0}
.callout{border-left:4px solid var(--acc);background:var(--card);padding:8px 14px;border-radius:0 8px 8px 0;margin:12px 0}
.callout.intu{border-color:var(--cool)}.callout p{margin:4px 0 2px}
.pat{margin:26px 0;padding:16px 16px 6px;border:1px solid var(--line);border-radius:12px}
.tier{font-size:12px;font-weight:600;padding:2px 8px;border-radius:99px;border:1px solid currentColor;margin-left:6px;white-space:nowrap}
.tier.hot{color:var(--hot)}.tier.sec{color:var(--cool)}
.tw{overflow-x:auto;margin:8px 0}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th,td{border:1px solid var(--line);padding:6px 9px;text-align:left;vertical-align:top}
th{background:var(--card)}
.ladder td:first-child{width:28px;text-align:center}
.cx{white-space:nowrap}
.dE{color:var(--ok);font-weight:600}.dM{color:var(--warn);font-weight:600}.dH{color:var(--hot);font-weight:600}
tr.done td{background:var(--okbg)}
details{border:1px solid var(--line);border-radius:8px;padding:7px 12px;margin:7px 0;background:var(--card)}
summary{cursor:pointer;font-weight:600}
.code-java,.code-py{display:none}
body[data-lang=java] .code-java,body[data-lang=py] .code-py{display:block}
.stepper{border:1px solid var(--line);border-radius:10px;padding:12px;margin:8px 0 12px;background:var(--card)}
.st-view{display:flex;gap:6px;flex-wrap:wrap;justify-content:center;padding-top:6px}
.cellw{display:flex;flex-direction:column;align-items:center;min-width:44px}
.ptr{height:20px;font:700 11px Consolas,monospace;color:var(--acc);white-space:nowrap}
.cell{min-width:44px;height:44px;display:flex;align-items:center;justify-content:center;border:2px solid var(--line);border-radius:8px;background:var(--cellbg);font:600 15px Consolas,monospace;padding:0 6px;transition:background .15s}
.cell.in{background:var(--in);border-color:var(--acc)}
.cell.ok{background:var(--okbg);border-color:var(--ok)}
.cell.dim{background:var(--dim);color:var(--mut);border-style:dashed}
.idx{font:11px Consolas,monospace;color:var(--mut)}
.st-note{min-height:44px;margin:10px 2px 8px;font-size:14px}
.st-ctl{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.st-count{margin-left:auto;font-size:12px;color:var(--mut)}
@media (max-width:600px){.bar .t{display:none}.bar{padding:6px 10px;gap:6px}body{font-size:14.5px}.pat{padding:12px 10px 4px}.cell{min-width:36px;height:38px;font-size:13px}.cellw{min-width:36px}}
@media print{.bar,.st-ctl{display:none}.pat{break-inside:avoid-page}.code-java,.code-py{display:block!important}details{break-inside:avoid}details>p{display:block}}
"""

PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>{css}</style></head>
<body data-lang="java" data-file="{fname}" data-topic="{tid}" data-total="{total}">
<div class="bar"><span class="t">{title}</span>
<span class="prog" id="prog">0 / {total} solved</span>
<button id="b-java" class="on">Java</button><button id="b-py">Python</button>
<button id="b-theme" title="Toggle light / dark">◐</button>
<button id="b-dl" title="Save this page as a standalone HTML file">⬇ Download</button></div>
<main>
{body}
<p class="muted" style="margin-top:40px">Part of <a href="index.html">DSA Mastery</a>. Open source revision sheets for interview preparation.</p>
</main>
<script>{js}</script>
</body></html>
"""

JS = r"""
(function(){
var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
function ls(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v)}catch(e){return null}}
var body=document.body,topic=body.dataset.topic;
/* language + theme */
function setLang(l){body.dataset.lang=l;$('#b-java').classList.toggle('on',l==='java');$('#b-py').classList.toggle('on',l==='py');ls('dsa-lang',l)}
setLang(ls('dsa-lang')||'java');
$('#b-java').onclick=function(){setLang('java')};$('#b-py').onclick=function(){setLang('py')};
var th=ls('dsa-theme');if(th)document.documentElement.dataset.theme=th;
$('#b-theme').onclick=function(){var d=document.documentElement,dark=d.dataset.theme?d.dataset.theme==='dark':matchMedia('(prefers-color-scheme:dark)').matches;d.dataset.theme=dark?'light':'dark';ls('dsa-theme',d.dataset.theme)};
/* progress */
function load(){try{return JSON.parse(ls('dsa-progress')||'{}')}catch(e){return {}}}
var prog=load();
function refresh(){var n=0,boxes=$$('.pk');boxes.forEach(function(b){var on=!!prog[b.dataset.k];b.checked=on;b.closest('tr').classList.toggle('done',on);if(on)n++});$('#prog').textContent=n+' / '+boxes.length+' solved'}
$$('.pk').forEach(function(b){b.onchange=function(){if(b.checked)prog[b.dataset.k]=1;else delete prog[b.dataset.k];ls('dsa-progress',JSON.stringify(prog));refresh()}});
refresh();
/* download */
$('#b-dl').onclick=function(){
 var clone=document.documentElement.cloneNode(true);
 $$('.stepper',clone).forEach(function(e){e.innerHTML=''});
 $$('.pk',clone).forEach(function(e){e.removeAttribute('checked')});
 $$('tr.done',clone).forEach(function(e){e.classList.remove('done')});
 var h='<!DOCTYPE html>\n'+clone.outerHTML,blob=new Blob([h],{type:'text/html'}),a=document.createElement('a');
 a.href=URL.createObjectURL(blob);a.download=body.dataset.file||'topic.html';document.body.appendChild(a);a.click();a.remove();setTimeout(function(){URL.revokeObjectURL(a.href)},1000)};
/* simulators: each returns [{a,ptr,hi,ok,dim,note}] */
function rng(x,y){var r=[];for(var i=x;i<=y;i++)r.push(i);return r}
function mapStr(m){var k=Object.keys(m);return '{'+k.map(function(x){return x+':'+m[x]}).join(', ')+'}'}
var SIM={
two:function(){var a=[1,3,4,6,8,11],t=10,S=[],l=0,r=a.length-1;
 while(l<r){var s=a[l]+a[r];
  if(s===t){S.push({a:a,ptr:{l:l,r:r},ok:[l,r],note:a[l]+' + '+a[r]+' = '+s+' equals the target '+t+'. Found the pair at indices '+l+' and '+r+'.'});break}
  if(s<t){S.push({a:a,ptr:{l:l,r:r},note:a[l]+' + '+a[r]+' = '+s+' is smaller than '+t+'. The sum must grow, so move l right (a[l] can never pair with anything smaller than a[r]).'});l++}
  else{S.push({a:a,ptr:{l:l,r:r},note:a[l]+' + '+a[r]+' = '+s+' is bigger than '+t+'. The sum must shrink, so move r left (a[r] is too large for every remaining partner).'});r--}}
 S.unshift({a:a,ptr:{l:0,r:a.length-1},note:'Sorted array, target '+t+'. Put one pointer at each end.'});return S},
fixed:function(){var a=[2,1,5,1,3,2],k=3,S=[],sum=0;for(var i=0;i<k;i++)sum+=a[i];var best=sum;
 S.push({a:a,ptr:{},hi:rng(0,k-1),note:'First window of size '+k+': sum = '+sum+'. Best so far = '+best+'.'});
 for(i=k;i<a.length;i++){sum+=a[i]-a[i-k];best=Math.max(best,sum);S.push({a:a,ptr:{i:i},hi:rng(i-k+1,i),note:'Slide: add '+a[i]+', drop '+a[i-k]+' → sum = '+sum+'. Best so far = '+best+'. (One add and one subtract, not a re-sum.)'})}
 S.push({a:a,ptr:{},ok:[2,3,4],note:'Maximum window sum of size '+k+' is '+best+'.'});return S},
variable:function(){var s='abcabcbb'.split(''),S=[],l=0,c={},best=0,bl=0;
 for(var r=0;r<s.length;r++){var ch=s[r];c[ch]=(c[ch]||0)+1;
  S.push({a:s,ptr:{l:l,r:r},hi:rng(l,r),note:"Expand: add '"+ch+"' at r="+r+'.'+(c[ch]>1?" '"+ch+"' now appears twice, so the window is invalid.":' Window "'+s.slice(l,r+1).join('')+'" is valid.')});
  while(c[ch]>1){c[s[l]]--;l++;S.push({a:s,ptr:{l:l,r:r},hi:rng(l,r),note:'Shrink: drop the left character, l becomes '+l+'. Window "'+s.slice(l,r+1).join('')+'".'})}
  if(r-l+1>best){best=r-l+1;bl=l}}
 S.push({a:s,ptr:{},ok:rng(bl,bl+best-1),note:'Longest substring without repeats has length '+best+'. Each index entered and left the window once, so O(n).'});return S},
prefix:function(){var a=[3,4,7,2,-3,1,4,2],k=7,S=[],m={0:1},sum=0,cnt=0;
 S.push({a:a,ptr:{},note:'Count subarrays with sum = '+k+'. Seed the map with {0:1} (the empty prefix).'});
 for(var i=0;i<a.length;i++){sum+=a[i];var need=sum-k,add=m[need]||0;cnt+=add;m[sum]=(m[sum]||0)+1;
  S.push({a:a,ptr:{i:i},ok:add?[i]:[],note:'Prefix sum = '+sum+'. Need an earlier prefix of '+sum+' − '+k+' = '+need+': seen '+add+' time(s), so '+add+' subarray(s) end here. Total = '+cnt+'. Map = '+mapStr(m)})}
 return S},
kadane:function(){var a=[-2,1,-3,4,-1,2,1,-5,4],S=[],cur=a[0],st=0,best=a[0],bs=0,be=0;
 S.push({a:a,ptr:{i:0},hi:[0],ok:[0],note:'Start: cur = '+cur+', best = '+best+'.'});
 for(var i=1;i<a.length;i++){var restart=a[i]>cur+a[i];
  if(restart){cur=a[i];st=i}else{cur+=a[i]}
  if(cur>best){best=cur;bs=st;be=i}
  S.push({a:a,ptr:{i:i},hi:rng(st,i),ok:rng(bs,be),note:(restart?'The running sum was negative, so restart at index '+i+': cur = '+cur+'.':'Extend the run: cur = '+cur+'.')+' best = '+best+' (green).'})}
 return S},
hash:function(){var a=[5,1,9,3,7],t=12,S=[],m={};S.push({a:a,ptr:{},note:'Find two numbers that sum to '+t+'. Keep a map value → index of what we have already seen.'});
 for(var i=0;i<a.length;i++){var need=t-a[i];
  if(need in m){S.push({a:a,ptr:{i:i},ok:[m[need],i],note:'Need '+need+' for '+a[i]+': it is in the map at index '+m[need]+'. Answer = ['+m[need]+', '+i+'].'});break}
  m[a[i]]=i;S.push({a:a,ptr:{i:i},note:'At '+a[i]+': need '+need+', not seen yet. Store '+a[i]+' → '+i+'. Map = '+mapStr(m)})}
 return S},
dutch:function(){var a=[2,0,2,1,1,0],S=[],lo=0,mid=0,hi=a.length-1;
 function p(n,ok){S.push({a:a.slice(),ptr:{lo:lo,mid:mid,hi:hi},ok:ok||[],note:n})}
 p('lo marks the end of the 0s, hi the start of the 2s, mid scans the unknown middle.');
 while(mid<=hi){var v=a[mid];
  if(v===0){a[mid]=a[lo];a[lo]=0;lo++;mid++;p('a[mid] was 0: swap into the 0-zone, advance lo and mid.')}
  else if(v===2){a[mid]=a[hi];a[hi]=2;hi--;p('a[mid] was 2: swap with a[hi], shrink hi. Do NOT advance mid; the swapped-in value is unexamined.')}
  else{mid++;p('a[mid] is 1: it already belongs in the middle zone, advance mid.')}}
 S.push({a:a.slice(),ptr:{},ok:rng(0,a.length-1),note:'mid passed hi: sorted in one pass, O(n), O(1) space.'});return S},
binary:function(){var a=[1,3,5,7,7,7,9,11],t=7,S=[],lo=0,hi=a.length-1;
 S.push({a:a,ptr:{lo:lo,hi:hi},note:'Find the FIRST index with a[i] ≥ '+t+' (lower bound). Invariant: the answer is always inside [lo, hi].'});
 while(lo<hi){var mid=lo+((hi-lo)>>1);
  if(a[mid]>=t){S.push({a:a,ptr:{lo:lo,mid:mid,hi:hi},hi:rng(lo,hi),note:'mid = '+mid+', a[mid] = '+a[mid]+' ≥ '+t+'. mid could be the answer, so keep it: hi = mid.'});hi=mid}
  else{S.push({a:a,ptr:{lo:lo,mid:mid,hi:hi},hi:rng(lo,hi),note:'mid = '+mid+', a[mid] = '+a[mid]+' < '+t+'. Everything up to mid is too small: lo = mid + 1.'});lo=mid+1}}
 S.push({a:a,ptr:{lo:lo},ok:[lo],note:'lo = hi = '+lo+'. First occurrence of '+t+' is at index '+lo+'. Each step halved the range: O(log n).'});return S},
rotated:function(){var a=[4,5,6,7,0,1,2],t=0,S=[],lo=0,hi=a.length-1;
 S.push({a:a,ptr:{lo:lo,hi:hi},note:'Sorted array rotated at an unknown point. Search for '+t+'. One half around mid is always sorted.'});
 while(lo<=hi){var mid=lo+((hi-lo)>>1);
  if(a[mid]===t){S.push({a:a,ptr:{lo:lo,mid:mid,hi:hi},ok:[mid],note:'a[mid] = '+t+'. Found at index '+mid+'.'});break}
  if(a[lo]<=a[mid]){var go=a[lo]<=t&&t<a[mid];S.push({a:a,ptr:{lo:lo,mid:mid,hi:hi},hi:rng(lo,mid),note:'Left half ['+lo+'..'+mid+'] is sorted ('+a[lo]+' ≤ '+a[mid]+'). '+t+(go?' lies inside it: hi = mid − 1.':' is not inside it: search the right, lo = mid + 1.')});if(go)hi=mid-1;else lo=mid+1}
  else{var go2=a[mid]<t&&t<=a[hi];S.push({a:a,ptr:{lo:lo,mid:mid,hi:hi},hi:rng(mid,hi),note:'Right half ['+mid+'..'+hi+'] is sorted. '+t+(go2?' lies inside it: lo = mid + 1.':' is not inside it: search the left, hi = mid − 1.')});if(go2)lo=mid+1;else hi=mid-1}}
 return S},
quick:function(){var a=[3,2,1,5,6,4],S=[],target=a.length-2,lo=0,hi=a.length-1;
 function dim(){var d=[];for(var x=0;x<a.length;x++)if(x<lo||x>hi)d.push(x);return d}
 S.push({a:a.slice(),ptr:{},note:'2nd largest = element at sorted index n − k = '+target+'. Partition around a pivot; recurse into ONE side only.'});
 while(lo<=hi){var pv=a[hi],i=lo;
  S.push({a:a.slice(),ptr:{lo:lo,pivot:hi},dim:dim(),hi:[hi],note:'Partition ['+lo+'..'+hi+'] with pivot '+pv+' (last element). i marks where the next smaller element goes.'});
  for(var j=lo;j<hi;j++){if(a[j]<pv){var tm=a[i];a[i]=a[j];a[j]=tm;i++;S.push({a:a.slice(),ptr:{i:i,j:j,pivot:hi},dim:dim(),note:a[i-1]+' < '+pv+': swap into the "smaller" zone, i = '+i+'.'})}
   else S.push({a:a.slice(),ptr:{i:i,j:j,pivot:hi},dim:dim(),note:a[j]+' ≥ '+pv+': leave it, move j on.'})}
  var t2=a[i];a[i]=a[hi];a[hi]=t2;
  if(i===target){S.push({a:a.slice(),ptr:{p:i},ok:[i],dim:dim(),note:'Pivot lands at index '+i+' = target index. Answer: '+a[i]+'.'});break}
  S.push({a:a.slice(),ptr:{p:i},ok:[i],dim:dim(),note:'Pivot '+pv+' is now at its final sorted index '+i+(i<target?' < target '+target+': only the right side can contain it.':' > target '+target+': only the left side can contain it.')});
  if(i<target)lo=i+1;else hi=i-1}
 return S}};
function stepper(el){var steps=SIM[el.dataset.sim](),i=0,timer=null;
 el.innerHTML='<div class="st-view"></div><div class="st-note"></div><div class="st-ctl"><button data-a="prev">◀ Prev</button><button data-a="play">▶ Play</button><button data-a="next">Next ▶</button><button data-a="reset">↺ Reset</button><span class="st-count"></span></div>';
 var view=$('.st-view',el),note=$('.st-note',el),cnt=$('.st-count',el),play=$('[data-a=play]',el);
 function draw(){var s=steps[i],lab={};Object.keys(s.ptr||{}).forEach(function(k){var ix=s.ptr[k];(lab[ix]=lab[ix]||[]).push(k)});
  var h='';s.a.forEach(function(v,ix){var c='cell'+((s.hi||[]).indexOf(ix)>=0?' in':'')+((s.ok||[]).indexOf(ix)>=0?' ok':'')+((s.dim||[]).indexOf(ix)>=0?' dim':'');
   h+='<div class="cellw"><div class="ptr">'+(lab[ix]?lab[ix].join(','):'')+'</div><div class="'+c+'">'+v+'</div><div class="idx">'+ix+'</div></div>'});
  view.innerHTML=h;note.textContent=s.note;cnt.textContent='Step '+(i+1)+' / '+steps.length}
 function stop(){if(timer){clearInterval(timer);timer=null;play.textContent='▶ Play'}}
 el.onclick=function(e){var a=e.target.dataset&&e.target.dataset.a;if(!a)return;
  if(a==='next'){stop();if(i<steps.length-1)i++}else if(a==='prev'){stop();if(i>0)i--}else if(a==='reset'){stop();i=0}
  else if(a==='play'){if(timer){stop();return}if(i>=steps.length-1)i=0;play.textContent='❚❚ Pause';draw();timer=setInterval(function(){if(i<steps.length-1){i++;draw()}else stop()},1400);return}
  draw()};
 draw()}
$$('.stepper').forEach(stepper);
})();
"""
