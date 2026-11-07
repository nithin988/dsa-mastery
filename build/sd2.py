"""System Design course v2: one story, twenty pages. Renders the landing page and every chapter and problem page into design/.

Content lives in build/sd2_content/*.py. Experiments and model answers are picked from the verified modules by reference,
so the recorded real output is reused and checked (a stale or missing recording fails the build, like the reference modules)."""
import html
import importlib
import json
import os
import re

import sd2kit
import syscatalog
from lib import CSS, FAVICON, SITE_URL, icon, md, rail, rail_button, ul
import lib_sys
from lib_sys import load_outputs, render_cmd, runnable

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(ROOT, "design")

SITE_CSS = """
.sdw{display:grid;grid-template-columns:230px minmax(0,1fr);gap:34px;max-width:1120px;margin:0 auto;padding:22px 20px 60px}
.sdw main{min-width:0;max-width:780px}
.sdnav{position:sticky;top:76px;align-self:start;font-size:13.5px}
.sdnav h4{margin:0 0 8px;font-size:11.5px;letter-spacing:.8px;text-transform:uppercase;color:var(--faint)}
.sdnav a{display:flex;gap:9px;align-items:center;padding:6px 8px;border-radius:6px;color:var(--mut);text-decoration:none;border-left:3px solid transparent}
.sdnav a b{width:20px;height:20px;border-radius:50%;background:var(--soft);color:var(--mut);display:inline-grid;place-items:center;font-size:11px;flex:none}
.sdnav a:hover{background:var(--soft);color:var(--fg)}
.sdnav a.on{color:var(--fg);font-weight:600;background:var(--acc-soft);border-left-color:var(--acc)}.sdnav a.on b{background:var(--acc);color:#fff}
.sdnav .done{margin-top:14px;padding:10px;border:1px solid var(--line);border-radius:8px;background:var(--surf);font-size:13px}
.sdhero{padding:6px 0 10px}
.sdhero .eyebrow{display:flex;gap:8px;align-items:center;font-size:12.5px;color:var(--mut);margin-bottom:8px}
.sdhero .tag{background:var(--acc-soft);color:var(--acc);border:1px solid var(--acc-line);padding:2px 9px;border-radius:999px;font-weight:600;font-size:12px}
.sdhero h1{margin:0 0 8px;font-size:clamp(27px,4.2vw,38px);line-height:1.15;color:var(--fg);letter-spacing:-.4px}
.sdhero .lead{font-size:17.5px;color:var(--txt);max-width:660px;margin:0 0 14px}
.sdmeta{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 6px}.sdmeta span{background:var(--soft);border:1px solid var(--line);border-radius:999px;padding:3px 11px;font-size:12.5px;color:var(--mut)}
.sdsec{margin:38px 0 0;scroll-margin-top:84px}
.sdsec>h2{display:flex;align-items:center;gap:11px;margin:0 0 4px;font-size:23px;color:var(--fg);letter-spacing:-.2px}
.sdsec>h2 .n{width:30px;height:30px;border-radius:50%;background:var(--ink);color:var(--ink-fg);display:inline-grid;place-items:center;font-size:14px;font-weight:700;flex:none}
.sdsec>h2 small{font-size:12.5px;font-weight:600;color:var(--faint);letter-spacing:.7px;text-transform:uppercase;margin-left:auto}
.sdsec .sub{margin:0 0 14px;color:var(--mut)}
.sdsec p{margin:0 0 12px}
.sdstory{font-size:16.5px;line-height:1.75}
.sdstory p:first-of-type::first-letter{float:left;font-size:44px;line-height:.9;padding:5px 8px 0 0;font-weight:800;color:var(--acc)}
.sdquote{border-left:4px solid var(--acc);background:var(--acc-soft);padding:12px 16px;border-radius:0 8px 8px 0;margin:14px 0;color:var(--fg)}
.sdquote p:last-child{margin-bottom:0}
.sdone{background:var(--ink);color:var(--ink-fg);border-radius:10px;padding:16px 20px;margin:16px 0;font-size:17px;line-height:1.5}
.sdone b{color:inherit;border-bottom:2px solid var(--acc-line)}
.sdsteps{list-style:none;margin:8px 0;padding:0;counter-reset:s;display:grid;gap:14px}
.sdsteps>li{counter-increment:s;border:1px solid var(--line);background:var(--surf);border-radius:10px;padding:14px 16px 6px 56px;position:relative;box-shadow:var(--sh)}
.sdsteps>li::before{content:counter(s);position:absolute;left:14px;top:13px;width:30px;height:30px;border-radius:50%;background:var(--acc);color:#fff;display:grid;place-items:center;font-weight:700}
.sdsteps h3{margin:0 0 3px;font-size:17px;color:var(--fg)}.sdsteps p{margin:0 0 8px}
.sdsteps .sdfig{margin:6px 0 8px}
.sdgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin:8px 0}
.sdcard{border:1px solid var(--line);background:var(--surf);border-radius:10px;padding:13px 15px;box-shadow:var(--sh)}
.sdcard h3{margin:0 0 4px;font-size:15.5px;color:var(--fg);display:flex;gap:8px;align-items:center}.sdcard p{margin:0;font-size:14.5px}
.sdcard.bad{border-color:var(--bad-line);background:var(--bad-soft)}.sdcard.ok{border-color:var(--done-line);background:var(--done-soft)}
.sdreal{display:grid;gap:10px;margin:8px 0}
.sdreal>div{border:1px solid var(--line);background:var(--surf);border-radius:10px;padding:12px 15px;display:grid;grid-template-columns:110px 1fr;gap:14px}
.sdreal b.co{color:var(--acc);font-size:14px}.sdreal p{margin:0 0 4px;font-size:14.5px}.sdreal a{font-size:13px}
.sdnote{font-size:13px;color:var(--faint);margin:6px 0 0}
.sdq{border:1px solid var(--line);background:var(--surf);border-radius:12px;margin:14px 0;box-shadow:var(--sh);overflow:hidden}
.sdq>header{padding:14px 18px;background:var(--hd);border-bottom:1px solid var(--line)}
.sdq>header .who{font-size:12px;color:var(--faint);text-transform:uppercase;letter-spacing:.7px;font-weight:600}
.sdq>header h3{margin:2px 0 4px;font-size:18px;color:var(--fg)}.sdq>header p{margin:0;font-size:14.5px;color:var(--mut)}
.sdq .body{padding:6px 18px 16px}
.sdq h4{margin:16px 0 6px;font-size:12.5px;letter-spacing:.7px;text-transform:uppercase;color:var(--faint)}
.sdq ol.think{margin:0;padding-left:20px}.sdq ol.think li{margin:0 0 6px}.sdq ol.think li span{display:block;color:var(--mut);font-size:14.5px}
.sdq .say{border-left:4px solid var(--done);background:var(--done-soft);padding:10px 15px;border-radius:0 8px 8px 0;font-size:15px}.sdq .say p{margin:0 0 8px}.sdq .say p:last-child{margin:0}
.sdq .say .lbl2{display:block;font-size:11.5px;letter-spacing:.7px;text-transform:uppercase;color:var(--done);font-weight:700;margin-bottom:4px}
.sdq details{border:1px solid var(--line);border-radius:8px;margin:6px 0;background:var(--bg)}.sdq summary{cursor:pointer;padding:8px 12px;font-weight:600;color:var(--fg);font-size:14.5px}.sdq details p{margin:0;padding:0 12px 10px;font-size:14.5px}
.sdq .slips{margin:0;padding-left:20px;color:var(--mut);font-size:14.5px}
.sdrecap{border:1px solid var(--done-line);background:var(--done-soft);border-radius:12px;padding:6px 18px 12px}
.sdrecap ul{margin:6px 0 10px;padding-left:20px}.sdrecap li{margin:0 0 5px}
.sddeeper{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}.sddeeper a{border:1px solid var(--line);border-radius:8px;padding:7px 12px;background:var(--surf);text-decoration:none;font-size:13.5px}
.sdfoot{display:flex;justify-content:space-between;gap:12px;margin:40px 0 0}
.sdfoot a{flex:1;border:1px solid var(--line);background:var(--surf);border-radius:10px;padding:12px 16px;text-decoration:none;color:var(--fg);box-shadow:var(--sh)}
.sdfoot a small{display:block;color:var(--faint);font-size:12px}.sdfoot a.r{text-align:right}
.sdx{border:1px solid var(--line);background:var(--surf);border-radius:12px;padding:14px 18px 8px;margin:14px 0;box-shadow:var(--sh)}.sdx h3{margin:0 0 4px;font-size:17px;color:var(--fg);display:flex;gap:10px;align-items:center}.sdx .xn{width:26px;height:26px;border-radius:7px;background:var(--done);color:#fff;display:inline-grid;place-items:center;font-size:13px}.sdx .what{margin:0 0 8px;color:var(--txt)}.sdx pre.out{margin:6px 0 10px;max-height:340px;overflow:auto}.sdmore{margin:8px 0 6px;border:1px solid var(--line);border-radius:8px;background:var(--bg)}.sdmore summary{cursor:pointer;padding:8px 12px;font-weight:600;font-size:14px;color:var(--acc)}.sdmore pre.sh{margin:0 12px 10px;max-height:380px;overflow:auto}.sdmore p{margin:0 12px 10px;font-size:14.5px}
.sdtable{width:100%;border-collapse:collapse;font-size:14.5px;margin:8px 0}.sdtable th,.sdtable td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}.sdtable th{background:var(--soft);color:var(--fg)}
.sdland .path{position:relative;margin:18px 0 8px;padding-left:44px}
.sdland .path::before{content:"";position:absolute;left:-30px;top:12px;bottom:12px;width:3px;background:linear-gradient(var(--acc),var(--done));border-radius:2px}
.sdland .node{position:relative;display:grid;grid-template-columns:1fr auto;gap:10px;align-items:center;border:1px solid var(--line);background:var(--surf);border-radius:10px;padding:11px 15px;margin:0 0 10px;text-decoration:none;color:inherit;box-shadow:var(--sh)}
.sdland .node::before{content:attr(data-n);position:absolute;left:-44px;top:50%;transform:translateY(-50%);width:28px;height:28px;border-radius:50%;background:var(--surf);border:3px solid var(--acc);display:grid;place-items:center;font-size:12px;font-weight:700;color:var(--fg)}
.sdland .node b{display:block;color:var(--fg);font-size:16px}.sdland .node span{color:var(--mut);font-size:13.5px}
.sdland .node.soon{opacity:.6;background:var(--soft)}.sdland .node.soon::before{border-color:var(--line)}
.sdland .node:not(.soon):hover{border-color:var(--acc);transform:translateX(2px)}
.sdland .pill{font-size:12px;font-weight:600;padding:3px 10px;border-radius:999px;background:var(--done-soft);color:var(--done);border:1px solid var(--done-line);white-space:nowrap}
.sdland .pill.soon{background:var(--soft);color:var(--faint);border-color:var(--line)}
.sdland .tick-ok{color:var(--done);font-weight:700}
.sdland h2{margin:34px 0 4px;font-size:24px;color:var(--fg)}
.sdland .grid2{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}
.sdland .pcard{border:1px solid var(--line);background:var(--surf);border-radius:10px;padding:13px 15px;text-decoration:none;color:inherit;display:block;box-shadow:var(--sh)}
.sdland .pcard b{display:block;color:var(--fg);font-size:15.5px;margin-bottom:2px}.sdland .pcard span{color:var(--mut);font-size:13.5px}.sdland .pcard .row{display:flex;justify-content:space-between;align-items:center;margin-top:8px}
.sdland .pcard.soon{opacity:.6;background:var(--soft)}.sdland .pcard:not(.soon):hover{border-color:var(--acc)}
@media(max-width:1020px){.sdw{grid-template-columns:1fr;gap:0;padding:14px 14px 50px}.sdnav{position:static;display:flex;gap:6px;overflow-x:auto;padding-bottom:10px;margin-bottom:6px;-webkit-overflow-scrolling:touch}.sdnav h4,.sdnav .done{display:none}.sdnav a{flex:none;border:1px solid var(--line);border-radius:999px;padding:5px 11px;border-left-width:1px;white-space:nowrap}.sdnav a b{display:none}.sdreal>div{grid-template-columns:1fr;gap:4px}.sdsteps>li{padding-left:52px}}
@media(max-width:560px){.sdsec>h2{font-size:20px}.sdsec>h2 small{display:none}.sdfoot{flex-direction:column}}
"""

PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | System Design | Mastery</title>
<meta name="description" content="{desc}"><meta name="theme-color" content="#0f172a">
<meta property="og:type" content="article"><meta property="og:site_name" content="Mastery"><meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}"><meta property="og:url" content="{url}">
<link rel="icon" href="{favicon}">
<style>{css}</style></head>
<body class="has-rail" data-sd="{slug}">
<a class="skip" href="#content">Skip to content</a>
{rail}
<header class="bar"><div class="bar-in">{rail_btn}<a class="brand" href="index.html" aria-label="System design home"><span class="logo" aria-hidden="true">SD</span><b>System <span>Design</span></b></a>
<nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Course map</a>{i_right}<span class="cur">{crumb}</span></nav>
<span style="margin-left:auto"></span><button id="b-theme" class="iconbtn" title="Toggle light / dark" aria-label="Toggle light or dark theme">{i_theme}</button></div></header>
<div class="sdw"><nav class="sdnav" aria-label="On this page"><h4>On this page</h4>{nav}<label class="done"><input type="checkbox" id="sd-done"> I finished this page</label></nav>
<main id="content" class="sdmain">{body}</main></div>
<footer class="site-foot"><span>Mastery: free, open study sheets. Progress is saved in your browser only.</span><span><a href="index.html">Course map</a> · <a href="https://github.com/nithin988/dsa-mastery" target="_blank" rel="noopener">GitHub</a></span></footer>
<script>(function(){{var IC={ic};{js}}})();</script>
</body></html>
"""

JS = """
var slug=document.body.getAttribute('data-sd'),K='sd2-done';
function get(){try{return JSON.parse(localStorage.getItem(K)||'{}')}catch(e){return{}}}
var cb=document.getElementById('sd-done');if(cb){var s=get();cb.checked=!!s[slug];cb.onchange=function(){var s=get();if(cb.checked)s[slug]=1;else delete s[slug];try{localStorage.setItem(K,JSON.stringify(s))}catch(e){}}}
var links=[].slice.call(document.querySelectorAll('.sdnav a'));var secs=links.map(function(a){return document.querySelector(a.getAttribute('href'))}).filter(Boolean);
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){links.forEach(function(a){a.classList.toggle('on',a.getAttribute('href')==='#'+e.target.id)})}})},{rootMargin:'-20% 0px -70% 0px'});secs.forEach(function(s){io.observe(s)})}
var tb=document.getElementById('b-theme');if(tb){var R=document.documentElement;var t=null;try{t=localStorage.getItem('theme')}catch(e){}if(t)R.setAttribute('data-theme',t);tb.onclick=function(){var n=R.getAttribute('data-theme')==='dark'?'light':'dark';R.setAttribute('data-theme',n);try{localStorage.setItem('theme',n)}catch(e){}}}
"""


def _mod_of(mid):
    for row in syscatalog.MODULES:
        if row[5]:
            m = importlib.import_module(row[5]).MODULE
            if m["id"] == mid:
                return m
    raise KeyError(mid)


def pick(mid, li, gi, ci):
    """A recorded experiment from a verified reference module: (command dict, recorded entry)."""
    m = _mod_of(mid)
    cmd = m["lessons"][li]["groups"][gi]["cmds"][ci]
    run = runnable(m)
    idx = next(i for i, c in enumerate(run) if c is cmd)
    rec = load_outputs().get(mid, [])
    if idx >= len(rec) or rec[idx]["cmd"] != cmd["c"]:
        raise lib_sys.StaleOutput(f"{mid}: recording for {cmd['c'][:50]!r} is missing or stale; run python verify/sys_record.py {mid}")
    return cmd, rec[idx]


def scen(mid, li):
    return _mod_of(mid)["lessons"][li]["scenario"]


def figure_of(mid, li, vi=0):
    v = _mod_of(mid)["lessons"][li]["visual"]
    return v[vi] if isinstance(v, (list, tuple)) else v


def _paras(items):
    if isinstance(items, str):
        items = [items]
    return "".join(f"<p>{md(p)}</p>" for p in items)


def render_experiments(picks, intro=None):
    """Result first: a plain sentence, the real output, a line-by-line table; the command and full explanation are folded."""
    env = load_outputs().get("_env", "Linux")
    out = ['<div class="sdexp">']
    if intro:
        out.append(_paras(intro))
    for n, p in enumerate(picks, 1):
        title = p[4] if len(p) > 4 else f"Experiment {n}"
        cmd, entry = pick(*p[:4])
        paras_e = [cmd["e"]] if isinstance(cmd["e"], str) else list(cmd["e"])
        head, rest = paras_e[0], paras_e[1:]
        text = entry["out"].rstrip(chr(10))
        annot = ""
        if cmd.get("annot"):
            annot = ('<div class="annot"><span class="lbl">Read it line by line</span><div class="tw"><table><thead><tr><th>In the output</th><th>What it means</th></tr></thead><tbody>'
                     + "".join(f"<tr><td><code>{html.escape(a)}</code></td><td>{md(b)}</td></tr>" for a, b in cmd["annot"]) + "</tbody></table></div></div>")
        more = (f'<details class="sdmore"><summary>Show the command and the full explanation</summary><pre class="sh"><code>{html.escape(cmd["c"])}</code></pre>{_paras(rest) if rest else ""}'
                f'<p class="muted">The same code runs on any Debian or Ubuntu machine as an ordinary user; nothing needs root.</p></details>')
        out.append(f'<article class="sdx"><h3><span class="xn">{n}</span>{html.escape(title)}</h3><p class="what">{md(head)}</p>'
                   f'<div class="out-l"><span class="stamp">Real output · {html.escape(env)}, ordinary user</span></div><pre class="out"><code>{html.escape(text)}</code></pre>{annot}{more}</article>')
    out.append("</div>")
    return "".join(out)


def render_interview(qs, intro=None):
    out = []
    if intro:
        out.append(f'<p class="sub">{md(intro)}</p>')
    for q in qs:
        sc = q["scenario"]
        head_note = q.get("who", "Reported by candidates at large tech companies. Not official.")
        h = [f'<article class="sdq"><header><span class="who">{html.escape(head_note)}</span><h3>{html.escape(sc["title"])}</h3><p>{md(sc["ask"].replace("this module", "this chapter"))}</p></header><div class="body">']
        if sc.get("clarify"):
            h.append("<h4>1. Ask first</h4><ul>" + "".join(f"<li><b>{md(a)}</b> <span class='muted'>{md(b)}</span></li>" for a, b in sc["clarify"]) + "</ul>")
        if sc.get("think"):
            h.append("<h4>2. How to think about it</h4><ol class='think'>" + "".join(f"<li><b>{md(a)}</b><span>{md(b)}</span></li>" for a, b in sc["think"]) + "</ol>")
        h.append('<h4>3. How to say it</h4><div class="say"><span class="lbl2">A model answer, about two minutes aloud</span>' + _paras(sc["answer"]) + "</div>")
        if sc.get("follow"):
            h.append("<h4>4. Likely follow-ups</h4>" + "".join(f"<details><summary>{md(a)}</summary><p>{md(b)}</p></details>" for a, b in sc["follow"]))
        if sc.get("slips"):
            h.append("<h4>Common slips</h4><ul class='slips'>" + "".join(f"<li>{md(s)}</li>" for s in sc["slips"]) + "</ul>")
        h.append("</div></article>")
        out.append("".join(h))
    return "".join(out)


def _sec(sid, n, title, tag, inner, sub=None):
    s = f'<section class="sdsec" id="{sid}"><h2><span class="n">{n}</span>{html.escape(title)}<small>{html.escape(tag)}</small></h2>'
    if sub:
        s += f'<p class="sub">{md(sub)}</p>'
    return s + inner + "</section>"


def _deeper(links):
    if not links:
        return ""
    return ('<p class="sub" style="margin-top:14px">Want every experiment, lab and edge case? The reference lessons for this topic:</p><div class="sddeeper">'
            + "".join(f'<a href="../systems/{href}">{icon("arr-r")} {html.escape(label)}</a>' for label, href in links) + "</div>")


# ----------------------------------------------------------------------------- chapter (building block) page
def render_chapter(c, nav_prev, nav_next, part_total):
    nav_items = [("story", "The story"), ("idea", "The idea"), ("how", "How it works"), ("try", "See it for real"), ("breaks", "How it breaks"), ("real", "Real companies"), ("interview", "In the interview"), ("recap", "Remember")]
    nav = "".join(f'<a href="#{a}"><b>{i + 1}</b>{b}</a>' for i, (a, b) in enumerate(nav_items))
    b = []
    nq = len(c["interview"])
    b.append(f'<header class="sdhero"><div class="eyebrow"><span class="tag">Chapter {c["num"]} of {part_total}</span>The ShopKart story</div>'
             f'<h1>{html.escape(c["title"])}</h1><p class="lead">{md(c["tagline"])}</p>'
             f'<div class="sdmeta"><span>about {html.escape(c["time"])}</span><span>{len(c["how"])} steps</span><span>{len(c["try"])} real experiments</span><span>{nq} interview questions</span></div></header>')
    st = c["story"]
    b.append(_sec("story", 1, st["title"], "The story", f'<div class="sdstory">{_paras(st["paras"])}</div>{st["strip"]}'))
    idea = c["idea"]
    b.append(_sec("idea", 2, idea["title"], "The idea", f'<div class="sdone">{md(idea["one"])}</div>{idea["figure"]}{_paras(idea.get("paras", []))}'))
    steps = "".join(f'<li><h3>{md(h)}</h3><p>{md(t)}</p>{fig or ""}</li>' for h, t, fig in c["how"])
    b.append(_sec("how", 3, "How it works, step by step", "How it works", f'<ol class="sdsteps">{steps}</ol>'))
    b.append(_sec("try", 4, "See it for real", "Real experiments", render_experiments(c["try"], c.get("try_intro")), sub="Every output below was recorded from a real run on Debian Linux as an ordinary user. Read it line by line."))
    cards = "".join(f'<div class="sdcard {k}"><h3>{icon("warn")} {md(t)}</h3><p>{md(x)}</p></div>' for t, x, k in c["breaks"])
    b.append(_sec("breaks", 5, "How it breaks in production", "Failure modes", f'<div class="sdgrid">{cards}</div>'))
    real = "".join(f'<div><b class="co">{html.escape(r["company"])}</b><div><p>{md(r["text"])}</p><a href="{r["url"]}" target="_blank" rel="noopener">{html.escape(r["source"])}</a></div></div>' for r in c["real"])
    b.append(_sec("real", 6, "How real companies do it", "Real companies", f'<div class="sdreal">{real}</div><p class="sdnote">{md(c.get("real_note", "Summaries of public engineering write-ups; check the linked source for details."))}</p>'))
    b.append(_sec("interview", 7, "In the interview", "Top-company questions", render_interview(c["interview"], c.get("interview_intro")), sub=c.get("interview_sub", "Say your answer aloud first, then compare. These are questions candidates report, not official company lists.")))
    rc = c["recap"]
    quick = "".join(f"<details><summary>{md(q)}</summary><p>{md(a)}</p></details>" for q, a in rc["quick"])
    b.append(_sec("recap", 8, "Remember this", "Recap", f'<div class="sdrecap"><h3 style="margin:12px 0 0">The page in {len(rc["points"])} lines</h3>{ul(rc["points"])}</div><h3 style="margin:18px 0 6px">Check yourself</h3>{quick}{_deeper(c.get("deeper"))}'))
    b.append(_foot(nav_prev, nav_next))
    return _page(c, nav, "\n".join(b), f'Chapter {c["num"]} · {c["title"]}')


# ----------------------------------------------------------------------------- problem (whiteboard) page
def render_problem(p, nav_prev, nav_next, part_total):
    nav_items = [("ask", "The question"), ("clarify", "What to ask"), ("numbers", "The numbers"), ("design", "First design"), ("hard", "The hard part"), ("scale", "Scale and failure"), ("say", "Say it in 2 minutes"), ("recap", "Remember")]
    nav = "".join(f'<a href="#{a}"><b>{i + 1}</b>{b}</a>' for i, (a, b) in enumerate(nav_items))
    sc = p["scenario"]
    b = [f'<header class="sdhero"><div class="eyebrow"><span class="tag">Problem {p["num"]} of {part_total}</span>Whiteboard walkthrough</div>'
         f'<h1>{html.escape(p["title"])}</h1><p class="lead">{md(p["tagline"])}</p>'
         f'<div class="sdmeta"><span>about {html.escape(p["time"])}</span><span>{len(p["try"])} real experiments</span><span>{html.escape(p["seen_at"])}</span></div></header>']
    st = p["story"]
    b.append(_sec("ask", 1, st["title"], "The question", f'<div class="sdstory">{_paras(st["paras"])}</div>{st["strip"]}<div class="sdquote"><p><b>The interviewer says:</b> {html.escape(sc["title"].strip(chr(34)))}</p><p class="muted" style="margin-top:6px"><b>What they are looking for:</b> {md(sc["ask"])}</p></div>'))
    b.append(_sec("clarify", 2, "What to ask before drawing anything", "Requirements", "<ul>" + "".join(f"<li><b>{md(a)}</b> <span class='muted'>{md(b_)}</span></li>" for a, b_ in sc["clarify"]) + "</ul>" + _paras(p.get("requirements", [])), sub="Two minutes of questions is what separates a design from a guess. Write the answers on the board."))
    rows = "".join(f"<tr><td>{md(a)}</td><td>{md(b_)}</td></tr>" for a, b_ in p["numbers"])
    b.append(_sec("numbers", 3, "The numbers that shape the design", "Estimates", f'<table class="sdtable"><thead><tr><th>Quantity</th><th>Estimate and what it tells you</th></tr></thead><tbody>{rows}</tbody></table>' + (render_experiments(p["numbers_try"]) if p.get("numbers_try") else "")))
    steps = "".join(f'<li><h3>{md(h)}</h3><p>{md(t)}</p>{fig or ""}</li>' for h, t, fig in p["design"])
    b.append(_sec("design", 4, "A first design that works", "Architecture", p["design_figure"] + f'<ol class="sdsteps">{steps}</ol>'))
    b.append(_sec("hard", 5, p["hard_title"], "The hard part", _paras(p["hard_paras"]) + render_experiments(p["try"]), sub="Every interview has one part where the answer is not obvious. Spend your time here."))
    b.append(_sec("scale", 6, "Scale, failure and trade-offs", "Deep dive", '<div class="sdgrid">' + "".join(f'<div class="sdcard {k}"><h3>{md(t)}</h3><p>{md(x)}</p></div>' for t, x, k in p["scale"]) + "</div>"))
    sayq = render_interview([{"scenario": dict(sc, clarify=None, think=None), "who": p.get("who", "Reported by candidates at large tech companies. Not official.")}])
    real = "".join(f'<div><b class="co">{html.escape(r["company"])}</b><div><p>{md(r["text"])}</p><a href="{r["url"]}" target="_blank" rel="noopener">{html.escape(r["source"])}</a></div></div>' for r in p.get("real", []))
    b.append(_sec("say", 7, "Say it in two minutes", "The answer", sayq + (f'<h3 style="margin:18px 0 6px">What companies have published</h3><div class="sdreal">{real}</div><p class="sdnote">Summaries of public engineering write-ups; check the source for details.</p>' if real else "")))
    rc = p["recap"]
    quick = "".join(f"<details><summary>{md(q)}</summary><p>{md(a)}</p></details>" for q, a in rc["quick"])
    b.append(_sec("recap", 8, "Remember this", "Recap", f'<div class="sdrecap"><h3 style="margin:12px 0 0">The page in {len(rc["points"])} lines</h3>{ul(rc["points"])}</div><h3 style="margin:18px 0 6px">Check yourself</h3>{quick}{_deeper(p.get("deeper"))}'))
    b.append(_foot(nav_prev, nav_next))
    return _page(p, nav, "\n".join(b), f'Problem {p["num"]} · {p["title"]}')


def _foot(prev, nxt):
    def a(x, cls, label):
        if not x:
            return "<span></span>"
        return f'<a class="{cls}" href="{x[0]}.html"><small>{label}</small><strong>{html.escape(x[1])}</strong></a>'
    return f'<nav class="sdfoot">{a(prev, "", "Previous")}{a(nxt, "r", "Next")}</nav>'


def _page(c, nav, body, crumb):
    desc = re.sub(r"[`*]", "", c["tagline"])[:230]
    return PAGE.format(title=html.escape(c["title"]), desc=html.escape(desc, quote=True), url=SITE_URL + "design/" + c["slug"] + ".html", favicon=FAVICON,
                       css=CSS + sd2kit.CSS + SITE_CSS, slug=c["slug"], rail=rail("design", "../"), rail_btn=rail_button(), i_right=icon("right"), i_theme=icon("theme"),
                       crumb=html.escape(crumb), nav=nav, body=body, js=JS, ic=json.dumps({}))


# ----------------------------------------------------------------------------- landing
def render_landing(course):
    done_js = "var s={};try{s=JSON.parse(localStorage.getItem('sd2-done')||'{}')}catch(e){}[].forEach.call(document.querySelectorAll('[data-slug]'),function(n){if(s[n.dataset.slug]){var t=n.querySelector('.pill');if(t){t.textContent='Done';t.classList.add('tick-ok')}}});"
    parts = []
    parts.append('<header class="sdhero"><div class="eyebrow"><span class="tag">System design</span>One story, twenty pages</div>'
                 '<h1>How real products are built</h1><p class="lead">Follow one small shop, ShopKart, as it grows from one server to millions of customers. Every building block arrives when something breaks, so you learn what it is for, how it works and how to explain it in an interview.</p>'
                 '<div class="sdmeta"><span>9 chapters</span><span>10 whiteboard problems</span><span>1 interview playbook</span><span>real experiments, real output</span></div></header>')
    parts.append(sd2kit.strip([
        {"title": "Day 1", "kind": "", "scene": lambda cx, cy, w: sd2kit.crowd(cx, cy - 52, 2, 34, .85) + sd2kit.scaled(sd2kit.server(cx - 46, cy + 22, "web") + sd2kit.database(cx + 46, cy + 22, "data", "ok") + sd2kit.flow(cx - 14, cy + 22, cx + 18, cy + 22, "ok"), cx, cy + 22, .9), "caption": "One server, one database, ten customers. Everything is fine."},
        {"title": "Day 90", "kind": "bad", "scene": lambda cx, cy, w: sd2kit.crowd(cx, cy - 52, 5, 24, .72, "bad") + sd2kit.scaled(sd2kit.server(cx - 46, cy + 22, "web", "warn") + sd2kit.database(cx + 46, cy + 22, "data", "bad") + sd2kit.flow(cx - 14, cy + 22, cx + 18, cy + 22, "bad"), cx, cy + 22, .9), "caption": "Black Friday. Thousands of customers. The site is down."},
        {"title": "Day 365", "kind": "ok", "scene": lambda cx, cy, w: sd2kit.crowd(cx, cy - 52, 5, 24, .72, "ok") + sd2kit.scaled(sd2kit.balancer(cx - 74, cy + 22, None, "ok") + sd2kit.server(cx - 20, cy + 2, None, "ok") + sd2kit.server(cx - 20, cy + 52, None, "ok") + sd2kit.cache(cx + 40, cy + 2, None, "ok") + sd2kit.database(cx + 40, cy + 54, None, "ok"), cx, cy + 22, .74), "caption": "Balancers, caches, replicas, queues. The same shop, ready for the crowd."},
    ], "ShopKart over a year", "The course follows this story: each chapter fixes the thing that just broke."))
    parts.append('<div class="sdland"><h2>Part 1. The ShopKart story</h2><p class="muted">Nine chapters, read in order. Each one starts with something that went wrong.</p><div class="path">')
    for c in course["chapters"]:
        live = c.get("live")
        tag = "a" if live else "div"
        href = f' href="{c["slug"]}.html"' if live else ""
        parts.append(f'<{tag} class="node{"" if live else " soon"}" data-n="{c["num"]}" data-slug="{c["slug"]}"{href}><div><b>{html.escape(c["title"])}</b><span>{md(c["pain"])}</span></div><span class="pill{"" if live else " soon"}">{"Read" if live else "Coming"}</span></{tag}>')
    parts.append('</div><h2>Part 2. Whiteboard problems</h2><p class="muted">The questions candidates report most often. One page each: what to ask, the numbers, a first design, the hard part, and how to say it.</p><div class="grid2">')
    for p in course["problems"]:
        live = p.get("live")
        tag = "a" if live else "div"
        href = f' href="{p["slug"]}.html"' if live else ""
        parts.append(f'<{tag} class="pcard{"" if live else " soon"}" data-slug="{p["slug"]}"{href}><b>{html.escape(p["title"])}</b><span>{md(p["pain"])}</span><div class="row"><span class="muted">Problem {p["num"]}</span><span class="pill{"" if live else " soon"}">{"Read" if live else "Coming"}</span></div></{tag}>')
    parts.append('</div><h2>Part 3. The interview playbook</h2><div class="grid2"><a class="pcard" data-slug="playbook" href="playbook.html"><b>How to run the 45 minutes</b><span>Structure, pacing, trade-offs, and what the big companies are reported to emphasise.</span><div class="row"><span class="muted">Playbook</span><span class="pill">Read</span></div></a></div>')
    parts.append('<h2>How to use this course</h2><div class="sdgrid"><div class="sdcard"><h3>Read one page at a time</h3><p>Each page is complete on its own and takes about 15 minutes. No tiny steps to click through.</p></div><div class="sdcard"><h3>Run the experiments</h3><p>Real commands on a real Linux. Change a number and see what happens. That is where the understanding comes from.</p></div><div class="sdcard"><h3>Say the answers aloud</h3><p>Every page ends with questions people report from big tech interviews, and a model answer to compare with.</p></div></div>')
    parts.append('<p class="sdnote">Prefer the full reference? The earlier, longer modules are still available in the <a href="../systems.html">reference library</a> and each page links to the matching lessons.</p></div>')
    body = "".join(parts)
    desc = "System design explained as one story: a small shop grows from one server to millions of customers. Nine chapters, ten interview problems, real experiments."
    return PAGE.format(title="How real products are built", desc=html.escape(desc, quote=True), url=SITE_URL + "design/", favicon=FAVICON, css=CSS + sd2kit.CSS + SITE_CSS,
                       slug="index", rail=rail("design", "../"), rail_btn=rail_button(), i_right=icon("right"), i_theme=icon("theme"), crumb="Course map",
                       nav='<h4>The course</h4><a href="#"><b>1</b>Part 1: the story</a><a href="#"><b>2</b>Part 2: problems</a><a href="#"><b>3</b>Part 3: playbook</a>',
                       body=f'<div class="sdmain-wrap">{body}</div><script>{done_js}</script>', js=JS, ic="{}")


def build_all():
    from sd2_content import COURSE, load
    os.makedirs(OUT_DIR, exist_ok=True)
    chapters = [c for c in COURSE["chapters"] if c.get("live")]
    problems = [p for p in COURSE["problems"] if p.get("live")]
    items = [("chapter", c) for c in chapters] + [("problem", p) for p in problems]
    pages = []
    for kind, meta in items:
        pages.append((kind, meta, load(meta["slug"])))
    written = []
    for i, (kind, meta, data) in enumerate(pages):
        prev = (pages[i - 1][1]["slug"], pages[i - 1][1]["title"]) if i else None
        nxt = (pages[i + 1][1]["slug"], pages[i + 1][1]["title"]) if i + 1 < len(pages) else None
        data = dict(meta, **data)
        text = (render_chapter(data, prev, nxt, len(COURSE["chapters"])) if kind == "chapter" else render_problem(data, prev, nxt, len(COURSE["problems"])))
        with open(os.path.join(OUT_DIR, meta["slug"] + ".html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        written.append(meta["slug"])
    import sd2_playbook
    last = (pages[-1][1]["slug"], pages[-1][1]["title"]) if pages else None
    with open(os.path.join(OUT_DIR, "playbook.html"), "w", encoding="utf-8", newline=chr(10)) as f:
        f.write(sd2_playbook.render(last, None))
    written.append("playbook")
    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(render_landing(COURSE))
    return written
