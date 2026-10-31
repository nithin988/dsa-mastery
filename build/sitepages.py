"""Hub (index.html) and Systems course landing (systems.html)."""
import html
import json

from lib import CSS, ICONS, FAVICON, SITE_URL, icon, rail, rail_button
from syscatalog import TRACKS

HERE_JS = {}


def _read(name):
    import os
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), name), encoding="utf-8") as f:
        return f.read()


def head(title, desc, url, og_title=None):
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc, quote=True)}"><meta name="theme-color" content="#0f172a">
<meta property="og:type" content="website"><meta property="og:site_name" content="Mastery"><meta property="og:title" content="{html.escape(og_title or title, quote=True)}">
<meta property="og:description" content="{html.escape(desc, quote=True)}"><meta property="og:url" content="{url}">
<link rel="icon" href="{FAVICON}">
<style>{CSS}</style></head>"""


def topbar(brand_logo, brand_name, section_href, extra=""):
    return (f'<header class="bar"><div class="bar-in">{rail_button()}<a class="brand" href="{section_href}" aria-label="{brand_name} home"><span class="logo" aria-hidden="true">{brand_logo}</span>'
            f'<b>{brand_name}</b></a><span style="margin-right:auto"></span>{extra}'
            f'<button class="btn" data-share>{icon("share")}<span class="t-long">Share</span></button>'
            f'<button id="b-theme" class="iconbtn" title="Toggle light / dark" aria-label="Toggle light or dark theme">{icon("theme")}</button></div></header>')


def scripts(catalog_json, extra_catalogs="", js="", body_js=""):
    return (f'<script>{extra_catalogs}window.DSA_TOPICS={catalog_json};</script>\n'
            f'<script>(function(){{var IC={json.dumps(ICONS, separators=(",", ":"))};\n{js}\n{_read("rail.js")}\n}})();</script>')


def hub_html(dsa, sysc):
    """dsa and sysc: dicts with counts and catalog json."""
    desc = "Free, practical study courses for engineers: data structures and algorithms, and Linux, Git, troubleshooting and system design. Works offline."
    live = sysc["live"]
    def card(href, ic, title, lead, bullets, stats, cta, pid):
        li = "".join(f"<li>{html.escape(b)}</li>" for b in bullets)
        st = "".join(f'<span class="stat"><b>{n}</b> {html.escape(l)}</span>' for n, l in stats)
        return (f'<article class="ccard" data-course="{pid}"><div class="tcard-h"><span class="no">{icon(ic)}</span><h2>{html.escape(title)}</h2><span class="st" id="st-{pid}">Not started</span></div>'
                f'<div class="tcard-b"><p>{html.escape(lead)}</p><ul class="ticks">{li}</ul><div class="stats" style="margin:0">{st}</div>'
                f'<div><div class="meter" aria-hidden="true"><i id="m-{pid}"></i></div><div class="meta" style="margin-top:6px"><span id="t-{pid}">Not started</span></div></div>'
                f'<div class="act"><a class="btn pri lg" id="open-{pid}" href="{href}"><span>{cta}</span>{icon("arr-r")}</a><a class="btn lg" id="cont-{pid}" href="#" hidden><span>Continue</span>{icon("arr-r")}</a></div></div></article>')
    c1 = card("dsa.html", "code", "DSA Mastery", "Pattern-based data structures and algorithms for coding interviews. Intuition, animations, Java and Python code, and ladders of LeetCode problems.",
              ["Arrays to dynamic programming in 19 topics", "Step-by-step animations of every pattern", "Study planner that fits your weeks"],
              [(dsa["topics"], "topics"), (dsa["problems"], "problems")], "Open DSA Mastery", "dsa")
    c2 = card("systems.html", "server", "Systems Mastery", "Linux, Git, troubleshooting and system design for engineers and interviews: real commands with real output, hands-on labs, playbooks and design walkthroughs.",
              ["Linux and Git you can use under pressure", "Debugging and incident playbooks", "System design with numbers, not just boxes"],
              [(f"{live} of {sysc['total']}", "modules ready"), (sysc["labs"], "labs")], "Open Systems Mastery", "sys")
    hub_js = _read("hub.js")
    return (head("Mastery: free study courses for engineers", desc, SITE_URL)
            + f"""
<body class="has-rail" data-hub="1">
<a class="skip" href="#content">Skip to content</a>
{rail("home")}
{topbar("M", "Mastery", "index.html", f'<a class="btn" href="plan.html">{icon("cal")}<span class="t-long">DSA planner</span></a><a class="btn" href="https://github.com/nithin988/dsa-mastery" target="_blank" rel="noopener">{icon("ext")}<span class="t-long">GitHub</span></a>')}
<main id="content" class="home">
<section class="hero" style="margin-bottom:20px"><div class="eyebrow"><span class="tag">Free and open</span>Works offline</div>
<h1>Learn what engineering interviews and real jobs ask for</h1>
<p class="lead">Two separate courses, built the same careful way: plain explanations first, then animations, real commands and code you can run, then practice. Pick where to start. Your progress is saved in your browser only.</p></section>
<div class="courses">{c1}{c2}</div>
<section class="how" aria-label="How the courses work">
<div><b><span class="no">1</span>Understand</b>A mental model in plain words, with an everyday analogy, before any jargon.</div>
<div><b><span class="no">2</span>See and try</b>Animations to watch it work, and labs or code you run yourself.</div>
<div><b><span class="no">3</span>Be interview ready</b>Real questions, traps, and checklists from the way these topics are actually tested.</div></section>
</main>
<footer class="site-foot"><span>Mastery: free, open study sheets. Progress is saved in your browser only. <a href="https://github.com/nithin988/dsa-mastery/blob/main/ROADMAP.md">Roadmap</a></span><span><a href="https://github.com/nithin988/dsa-mastery" target="_blank" rel="noopener">GitHub</a></span></footer>
{scripts("[]", f"window.HUB_DSA={dsa['catalog']};window.HUB_SYS={sysc['catalog']};", hub_js)}
</body></html>
""")


def systems_html(rows, catalog_json, stats):
    """rows: list of dicts {num, slug, title, blurb, track, module (or None), lessons, labs, sims}."""
    desc = "Linux, Git, troubleshooting and system design for engineers and interviews, with real command output, hands-on labs and design walkthroughs."
    sections = []
    for ti, (tname, tdesc) in enumerate(TRACKS, 1):
        cards = []
        for r in rows:
            if r["track"] != ti:
                continue
            if r["module"]:
                f = r["slug"]
                n = r["lessons"] + r["labs"] + 1
                cards.append(
                    f'<article class="tcard" data-file="{f}" data-num="{r["num"]}" data-title="{html.escape(r["title"], quote=True)}" data-blurb="{html.escape(r["blurb"], quote=True)}" data-status="new">'
                    f'<div class="tcard-h"><span class="no">{r["num"]}</span><h3>{html.escape(r["title"])}</h3><span class="st">Not started</span></div>'
                    f'<div class="tcard-b"><p>{html.escape(r["blurb"])}</p>'
                    f'<div class="meta"><span>{icon("layers")}{r["lessons"]} lessons</span><span>{icon("flask")}{r["labs"]} labs</span><span>{icon("film")}{r["sims"]} animations</span></div>'
                    f'<div><div class="meter" aria-hidden="true"><i></i></div><div class="meta" style="margin-top:6px"><span class="solved">0 / {n} done</span></div></div>'
                    f'<div class="act"><a class="btn pri" href="systems/{f}.html">Open{icon("arr-r")}</a>'
                    f'<a class="btn" href="systems/{f}.html" download="{f}.html" title="Save this module as a standalone HTML file">{icon("down")}Download</a></div></div></article>')
            else:
                cards.append(
                    f'<article class="tcard planned" data-file="" data-num="{r["num"]}" data-title="{html.escape(r["title"], quote=True)}" data-blurb="{html.escape(r["blurb"], quote=True)}" data-status="planned">'
                    f'<div class="tcard-h"><span class="no">{r["num"]}</span><h3>{html.escape(r["title"])}</h3><span class="st">Planned</span></div>'
                    f'<div class="tcard-b"><p>{html.escape(r["blurb"])}</p></div></article>')
        sections.append(
            f'<section class="phase" id="track-{ti}" aria-labelledby="tr-{ti}"><div class="phase-h"><span class="ph">Track {ti}</span>'
            f'<h2 id="tr-{ti}">{html.escape(tname)}</h2><span>{html.escape(tdesc)}</span></div><div class="grid">{"".join(cards)}</div></section>')
    first = next(r for r in rows if r["module"])
    home_js = _read("home.js")
    return (head("Systems Mastery: Linux, Git, troubleshooting and system design", desc, SITE_URL + "systems.html", "Systems Mastery")
            + f"""
<body class="has-rail" data-store="sys-progress" data-last="sys-last" data-dir="systems/" data-word="done" data-unit="steps" data-noun="modules">
<a class="skip" href="#content">Skip to content</a>
{rail("systems")}
{topbar("SYS", "Systems <span>Mastery</span>", "systems.html")}
<main id="content" class="home">
<section class="home-hero">
<div class="hero"><div class="eyebrow"><span class="tag">Course 2</span>Linux, Git, troubleshooting, system design</div>
<h1>Be the engineer people call when things break</h1>
<p class="lead">Practical systems skills, taught from first principles: every command with real output, labs that break things on purpose, troubleshooting playbooks, real outages, and system design with numbers. Written for engineering interviews at large companies and for the job itself.</p>
<div class="cta"><a id="cta-start" class="btn pri lg" href="systems/{first['slug']}.html"><span>Start with {first['num']}</span>{icon("arr-r")}</a>
<a id="cta-continue" class="btn lg" href="#" hidden><span>Continue</span>{icon("arr-r")}</a>
<a class="btn lg" href="revise.html">{icon("check")}<span>Quick revision</span></a><button class="btn lg" data-share>{icon("share")}<span>Share with friends</span></button></div></div>
<div class="kpis"><div class="kpi"><b>{stats['live']} / {stats['total']}</b><span>modules ready</span></div><div class="kpi"><b>{stats['lessons']}</b><span>lessons</span></div>
<div class="kpi"><b>{stats['labs']}</b><span>hands-on labs</span></div><div class="kpi"><b>{stats['questions']}</b><span>interview questions</span></div>
<div class="kpi wide"><span>Your progress</span><b id="k-pct">0%</b><div class="meter" id="k-meter" role="progressbar" aria-label="Overall progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><i id="k-bar"></i></div>
<span id="k-txt" style="margin-top:8px">0 steps done (saved in this browser)</span><span id="k-topics" style="margin-top:2px"></span></div></div>
</section>
<section class="how" aria-label="How the course works">
<div><b><span class="no">1</span>Learn the pieces</b>Every building block explained from the inside: the problem it solves, how it works step by step, a flow diagram, and real tools with every line of output explained.</div>
<div><b><span class="no">2</span>Solve whole problems</b>From a URL shortener to payments: requirements, numbers, API, data, architecture, deep dives and trade-offs, worked end to end.</div>
<div><b><span class="no">3</span>Explain it out loud</b>Worked interview scenarios with the reasoning shown, what to clarify, follow-ups and common slips, plus a quick revision space.</div></section>
<div class="tools"><h2 id="path">All modules</h2><span class="muted" id="count" aria-live="polite"></span>
<label class="search">{icon("search")}<input id="q" type="search" placeholder="Search modules" aria-label="Search modules"></label>
<span class="filters" role="group" aria-label="Filter by progress"><button data-f="all" aria-pressed="true">All</button><button data-f="new" aria-pressed="false">Not started</button><button data-f="doing" aria-pressed="false">In progress</button><button data-f="done" aria-pressed="false">Done</button></span></div>
{"".join(sections)}
<p class="empty" id="empty" hidden>No modules match your search or filter.</p>
</main>
<footer class="site-foot"><span>Systems Mastery: free, open study sheets. Progress is saved in your browser only. <a href="https://github.com/nithin988/dsa-mastery/blob/main/docs/COURSE2_PLAN.md">Course plan</a></span><span><a href="https://github.com/nithin988/dsa-mastery" target="_blank" rel="noopener">GitHub</a></span></footer>
{scripts(catalog_json, "", home_js)}
</body></html>
""")
