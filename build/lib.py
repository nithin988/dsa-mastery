"""Shared renderer for every DSA topic page.

A topic is a dict (see build/arrays.py). `render_topic` turns it into one
self-contained HTML file: no external requests, works offline.
Styles live in style.css, page behaviour in engine.js, animations in sims.js.
Visual language: docs/DESIGN_SYSTEM.md (derived from the Kimaru Platform design system).
"""
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


def _read(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return f.read()


# 16px icons, stroke 1.33, round caps and joins (design system section 10). Single source for Python and JS.
ICONS = {
    "target": '<circle cx="8" cy="8" r="6"/><circle cx="8" cy="8" r="2"/>',
    "search": '<circle cx="7" cy="7" r="4.5"/><path d="m14 14-3.5-3.5"/>',
    "bulb": '<path d="M6 12.5h4M6.5 14.5h3M8 1.5a4.5 4.5 0 0 0-2.5 8.2c.4.3.5.7.5 1.3h4c0-.6.1-1 .5-1.3A4.5 4.5 0 0 0 8 1.5z"/>',
    "up": '<path d="M4 12 12 4M6 4h6v6"/>',
    "spark": '<path d="M8 1.5 9.5 6.5 14.5 8 9.5 9.5 8 14.5 6.5 9.5 1.5 8 6.5 6.5z"/>',
    "list": '<path d="M5.5 4h8M5.5 8h8M5.5 12h8M2 4h.01M2 8h.01M2 12h.01"/>',
    "term": '<path d="m3 4.5 3.5 3.5L3 11.5M8 12h5"/>',
    "code": '<path d="m5.5 4.5-3.5 3.5 3.5 3.5M10.5 4.5l3.5 3.5-3.5 3.5"/>',
    "clock": '<circle cx="8" cy="8" r="6"/><path d="M8 4.5V8l2.5 1.5"/>',
    "warn": '<path d="M8 2 14.5 13.5h-13z"/><path d="M8 6.5v3M8 11.5h.01"/>',
    "layers": '<path d="m8 2 6.5 3.5L8 9 1.5 5.5z"/><path d="m1.5 8.5 6.5 3.5 6.5-3.5"/>',
    "no": '<circle cx="8" cy="8" r="6"/><path d="m5.8 5.8 4.4 4.4M10.2 5.8l-4.4 4.4"/>',
    "stairs": '<path d="M2.5 13.5h3v-3h3v-3h3v-3h2"/>',
    "flame": '<path d="M8 14.5c-2.5 0-4-1.7-4-3.8 0-2.2 2-3.2 2.4-5.2.9.6 1.6 1.5 1.8 2.6.6-.5.9-1.4.8-2.4 1.8 1.2 3 3 3 5 0 2-1.5 3.8-4 3.8z"/>',
    "mark": '<path d="M4 2.5h8v11L8 10.5 4 13.5z"/>',
    "down": '<path d="M8 2.5v8M4.5 7.5 8 11l3.5-3.5M2.5 13.5h11"/>',
    "menu": '<path d="M2.5 4h11M2.5 8h11M2.5 12h11"/>',
    "theme": '<circle cx="8" cy="8" r="5.5"/><path d="M8 2.5a5.5 5.5 0 0 0 0 11z" fill="currentColor"/>',
    "right": '<path d="m6 3.5 4.5 4.5L6 12.5"/>',
    "arr-r": '<path d="M2.5 8h11M9 3.5 13.5 8 9 12.5"/>',
    "arr-l": '<path d="M13.5 8h-11M7 3.5 2.5 8 7 12.5"/>',
    "check": '<path d="m3 8.5 3.2 3.2L13 4.8"/>',
    "ext": '<path d="M9 2.5h4.5V7M13.5 2.5 7 9M12 9v4.5H2.5V4H7"/>',
    "play": '<path d="M5 3.2v9.6L12.8 8z"/>',
    "pause": '<path d="M5 3.5v9M11 3.5v9"/>',
    "prev": '<path d="M10 3.5 5.5 8l4.5 4.5"/>',
    "next": '<path d="M6 3.5 10.5 8 6 12.5"/>',
    "reset": '<path d="M3 8a5 5 0 1 0 1.8-3.8M3 2.5v3h3"/>',
    "key": '<circle cx="5.5" cy="10.5" r="3"/><path d="m8 8.5 5.5-5.5M11 5l1.5 1.5M9.5 6.5 11 8"/>',
    "cal": '<rect x="2.5" y="3.5" width="11" height="10" rx="1.5"/><path d="M2.5 6.5h11M5.5 2v3M10.5 2v3"/>',
    "home": '<path d="M2.5 7.5 8 2.5l5.5 5M4 6.5v7h8v-7"/>',
    "branch": '<circle cx="4.5" cy="3.5" r="1.5"/><circle cx="4.5" cy="12.5" r="1.5"/><circle cx="11.5" cy="6" r="1.5"/><path d="M4.5 5v6M11.5 7.5c0 2.5-3 2-7 3.5"/>',
    "server": '<rect x="2.5" y="3" width="11" height="4" rx="1"/><rect x="2.5" y="9" width="11" height="4" rx="1"/><path d="M5 5h.01M5 11h.01"/>',
    "flask": '<path d="M6 2.5h4M6.5 2.5v4L3 12.5a1 1 0 0 0 .9 1.5h8.2a1 1 0 0 0 .9-1.5L9.5 6.5v-4"/><path d="M4.8 10h6.4"/>',
    "share": '<circle cx="4" cy="8" r="1.8"/><circle cx="12" cy="4" r="1.8"/><circle cx="12" cy="12" r="1.8"/><path d="m5.7 7 4.6-2M5.7 9l4.6 2"/>',
    "book": '<path d="M2.5 3.5h4A1.5 1.5 0 0 1 8 5v8a1 1 0 0 0-1-1H2.5zM13.5 3.5h-4A1.5 1.5 0 0 0 8 5v8a1 1 0 0 1 1-1h4.5z"/>',
    "film": '<rect x="2" y="3" width="12" height="10" rx="1.5"/><path d="m6.5 6 3.5 2-3.5 2z"/>',
    "pencil": '<path d="M2.5 13.5 3 10l7-7 3 3-7 7zM9 4l3 3"/>',
}


def icon(name, cls=""):
    c = f"ic {cls}".strip()
    return f'<svg class="{c}" viewBox="0 0 16 16" aria-hidden="true">{ICONS[name]}</svg>'


CSS = _read("style.css")
JS = (
    "(function(){\nvar IC=" + json.dumps(ICONS, separators=(",", ":")) + ";\n"
    + _read("sims.js") + "\n" + _read("engine.js") + "\n" + _read("rail.js") + "\n})();"
)

DIFF = {"E": ("Easy", "dE"), "M": ("Medium", "dM"), "H": ("Hard", "dH")}
TIER = {
    "hot": icon("flame") + " Frequently asked",
    "sec": icon("mark") + " Secondary",
}
LABEL_ICON = {
    "When to use": "target", "Detect it": "search", "Intuition": "bulb", "Brute force → optimised": "up",
    "Core idea": "spark", "How it works": "list", "Watch it run": "film", "Worked trace": "term",
    "Skeleton": "code", "Traps to avoid": "warn", "Variants and follow-ups": "layers", "When NOT to use": "no",
    "Problem ladder": "stairs",
}

FAVICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%230f172a'/%3E"
    "%3Ctext x='16' y='21' font-family='monospace' font-size='13' font-weight='700' fill='%23f8fafc' text-anchor='middle'%3EDSA%3C/text%3E%3C/svg%3E"
)
SITE_URL = "https://nithin988.github.io/dsa-mastery/"


SYS_TRACKS = [("track-1", "Foundations"), ("track-2", "Troubleshooting"), ("track-3", "System design core"), ("track-4", "Design problems"), ("track-5", "Interview and career"), ("track-6", "Extensions")]


def rail(section, root=""):
    """Left section navigation (collapsed icons, expands on hover or focus). section: home | dsa | systems | plan."""
    def item(key, href, ic, label, ext=False):
        cur = ' aria-current="page"' if key == section else ""
        tgt = ' target="_blank" rel="noopener"' if ext else ""
        return f'<a class="rail-i" href="{href}"{cur}{tgt} title="{label}">{icon(ic)}<span class="l">{label}</span></a>'
    subs = ""
    if section == "systems":
        subs = '<div class="rail-sub">' + "".join(f'<a href="{root}systems.html#{a}">{html.escape(n)}</a>' for a, n in SYS_TRACKS) + "</div>"
    return (
        '<nav class="rail" id="rail" aria-label="Sections">'
        f'<a class="rail-i rail-logo" href="{root}index.html" title="Mastery home"><span class="logo" aria-hidden="true">M</span><span class="l"><b>Mastery</b></span></a>'
        '<div class="rail-g">Courses</div>'
        + item("home", root + "index.html", "home", "Home")
        + item("dsa", root + "dsa.html", "code", "DSA Mastery")
        + item("systems", root + "systems.html", "server", "Systems Mastery") + subs
        + '<div class="rail-g">Tools</div>'
        + item("revise", root + "revise.html", "check", "Quick revision")
        + item("plan", root + "plan.html", "cal", "DSA study planner")
        + item("gh", "https://github.com/nithin988/dsa-mastery", "ext", "GitHub", True)
        + '<button class="rail-i rail-pin" id="rail-pin" type="button" aria-pressed="false" title="Keep the menu open"><svg class="ic" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 3l5 5-5 5"/></svg><span class="l">Pin menu</span></button>'
        + "</nav><div class=\"rail-bd\" id=\"rail-bd\" hidden></div>"
    )


def rail_button():
    return f'<button id="b-rail" class="iconbtn rail-btn" aria-label="Open the sections menu" aria-expanded="false" aria-controls="rail">{icon("menu")}</button>'


def md(s):
    """Tiny inline markup: `code`, **bold**. Everything else is escaped."""
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    return s


def ul(items, tag="ul"):
    return f"<{tag}>" + "".join(f"<li>{md(i)}</li>" for i in items) + f"</{tag}>"


def lbl(label):
    ic = icon(LABEL_ICON[label]) if label in LABEL_ICON else ""
    return f'<span class="lbl">{ic}{html.escape(label)}</span>'


def blk(label, inner, cls=""):
    return f'<div class="blk {cls}">{lbl(label)}{inner}</div>'


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
            f'<tr><td><input type="checkbox" class="pk" data-k="{topic_id}-{lc}" aria-label="Mark LC {lc} {html.escape(name)} as solved"></td>'
            f'<td class="t"><a href="https://leetcode.com/problems/{slug}/" target="_blank" rel="noopener">LC {lc}</a></td>'
            f'<td>{html.escape(name)}</td><td><span class="pill {cls}">{label}</span></td>'
            f"<td>{md(logic)}</td><td class=\"c\">{md(cx)}</td></tr>"
        )
    return (
        '<div class="tw"><table class="ladder"><thead><tr><th><span class="sr" style="position:absolute;left:-9999px">Solved</span></th><th>Problem</th><th>Title</th>'
        "<th>Level</th><th>One-line logic</th><th>Time / Space</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


def render_pattern(topic_id, n, p, unit="Pattern"):
    pid = f"p{n}"
    o = [f'<section class="pat {p["tier"]}" id="{pid}" aria-labelledby="{pid}-t">']
    o.append(
        f'<div class="pat-h"><span class="badge">{n}</span><h3 id="{pid}-t">{html.escape(p["title"])}</h3>'
        f'<span class="tier {p["tier"]}">{TIER[p["tier"]]}</span><span class="pp"></span></div><div class="pat-b">'
    )
    o.append(
        '<div class="glance">'
        f'<div class="gi">{lbl("When to use")}{md(p["when"])}</div>'
        f'<div class="gi">{lbl("Detect it")}{md(p["detect"])}</div></div>'
    )
    if p.get("intuition"):
        o.append(f'<div class="callout intu">{lbl("Intuition")}<p>{md(p["intuition"])}</p></div>')
    if p.get("brute"):
        o.append(blk("Brute force → optimised", f'<p>{md(p["brute"])}</p>'))
    o.append(blk("Core idea", f'<p>{md(p["idea"])}</p>'))
    o.append(blk("How it works", ul(p["steps"], "ol")))
    if p.get("sim"):
        o.append(
            f'<div class="blk">{lbl("Watch it run")}'
            '<p class="muted" style="margin:0 0 6px">Press play, or step with the buttons, the slider or the ← → keys.</p>'
            f'<div class="stepper" data-sim="{p["sim"]}"></div></div>'
        )
    if p.get("trace"):
        o.append(blk("Worked trace", f'<p>{md(p["trace_title"])}</p><pre class="trace"><code>{html.escape(p["trace"].strip())}</code></pre>'))
    for label, java, py in p["code"]:
        o.append(blk("Skeleton", f"<p>{md(label)}</p>" + code_block(java, py)))
    o.append(f'<div class="cx">{icon("clock")}<span>Complexity: {md(p["complexity"])}</span></div>')
    o.append(blk("Traps to avoid", ul(p["traps"]), "warn"))
    if p.get("variants"):
        o.append(blk("Variants and follow-ups", ul(p["variants"])))
    o.append(blk("When NOT to use", f'<p>{md(p["notuse"])}</p>'))
    o.append(blk("Problem ladder", '<p class="muted">Easy to hard. Tick what you have solved; ticks are saved in this browser only.</p>' + problems_table(topic_id, p["problems"])))
    o.append("</div></section>")
    return "\n".join(o)


def table(headers, rows, cls=""):
    h = "".join(f"<th>{html.escape(x)}</th>" for x in headers)
    r = "".join("<tr>" + "".join(f"<td>{md(c)}</td>" for c in row) + "</tr>" for row in rows)
    return f'<div class="tw"><table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{r}</tbody></table></div>'


def render_topic(t):
    tid = t["id"]
    pats = t["patterns"]
    unit = t.get("unit", "Pattern")
    total = len({pr[0] for p in pats for pr in p["problems"]})
    num = t["file"].split("_")[0]
    n_topics = t.get("_n_topics", 19)
    phase = t.get("_phase", "")

    side = ['<nav class="side" aria-label="On this page"><h4>Start here</h4>']
    for a, b in [("mindset", "The mindset"), ("priority", "Priority"), ("cues", "Problem cues")]:
        side.append(f'<a href="#{a}">{b}</a>')
    side.append(f"<h4>{unit}s</h4>")
    for i, p in enumerate(pats):
        side.append(f'<a href="#p{i+1}"><span class="dot {p["tier"]}"></span>{i+1}. {html.escape(p["title"])}<span class="cnt"></span></a>')
    side.append("<h4>Wrap up</h4>")
    for a, b in [("recall", "One-line recall"), ("choose", "Choosing"), ("selftest", "Self-test"), ("plan", "Study plan")]:
        side.append(f'<a href="#{a}">{b}</a>')
    side.append("</nav>")

    chips = '<div class="chips" aria-label="Jump to a section">' + "".join(f'<a href="#p{i+1}">{i+1}. {html.escape(p["title"])}</a>' for i, p in enumerate(pats)) + "</div>"

    prio_rows = [[str(i + 1), f"**{p['title']}**", p["why"], p["signature"]] for i, p in enumerate(pats)]
    hot = [r for r, p in zip(prio_rows, pats) if p["tier"] == "hot"]
    sec = [r for r, p in zip(prio_rows, pats) if p["tier"] == "sec"]
    ph = ["#", unit, "Why it matters", "Signature problem"]

    sims = sum(1 for p in pats if p.get("sim"))
    b = []
    b.append(
        f'<header class="hero"><div class="eyebrow"><span class="tag">Topic {num} of {n_topics}</span>{html.escape(phase)}</div>'
        f'<h1>{html.escape(t["title"])}</h1>'
        f'<p class="lead">{md(t["lead"])}</p><div class="stats">'
        f'<span class="stat"><b>{len(pats)}</b> {unit.lower()}s</span><span class="stat"><b>{total}</b> practice problems</span>'
        f'<span class="stat"><b>{sims}</b> animations</span><span class="stat">Java + Python</span></div></header>'
    )
    b.append(
        f'<div class="callout"><span class="lbl">{icon("book")}How to use this page</span><p>For each section: read <em>Detect</em> and <em>Intuition</em>, '
        "play the animation, then try to write the skeleton from memory before opening the code. Finish by solving the problem ladder in order.</p></div>"
    )
    b.append('<h2 id="mindset">The mindset</h2>' + f"<p>{md(t['mindset'])}</p><p>{md(t.get('qintro', 'Ask these questions on every problem:'))}</p>" + ul(t["questions"]))
    b.append(
        '<h2 id="priority">Priority</h2><p class="muted">Ranked by how often these show up in interviews '
        "(our judgement from the common interview lists and company question banks, not hard data).</p>"
        f"<h3 style='margin:14px 0 4px;font-size:15px'><span class='tier hot'>{TIER['hot']}</span> master these first</h3>" + table(ph, hot)
        + f"<h3 style='margin:14px 0 4px;font-size:15px'><span class='tier sec'>{TIER['sec']}</span> know them</h3>" + table(ph, sec)
    )
    b.append('<h2 id="cues">Problem cues</h2><p class="muted">If the problem says this, think of that.</p>' + table(["If the problem says / looks like…", unit], t["cues"]))
    b.append("<h2>" + t.get("units_heading", "The patterns") + "</h2>")
    for i, p in enumerate(pats):
        b.append(render_pattern(tid, i + 1, p, unit))
    tier_txt = {"hot": "Frequently asked", "sec": "Secondary"}
    b.append(
        '<h2 id="recall">One-line recall</h2>'
        + table(["#", unit, "Tier", "Core idea in one line"], [[str(i + 1), p["title"], tier_txt[p["tier"]], p["oneline"]] for i, p in enumerate(pats)])
    )
    b.append('<h2 id="choose">Choosing between them</h2>' + table(["Need", "Use"], t["choose"]) + f'<div class="callout"><span class="lbl">{icon("spark")}Rule of thumb</span><p>{md(t["rule"])}</p></div>')
    st = "".join(f"<details><summary>{md(q)}</summary><p>{md(a)}</p></details>" for q, a in t["selftest"])
    b.append('<h2 id="selftest">Self-test</h2><p class="muted">Answer in your head first, then open the question to reveal the answer.</p>' + st)
    b.append('<h2 id="plan">Study plan</h2>' + ul(t["plan"], "ol"))
    prev, nxt = t.get("prev"), t.get("next")
    foot = '<nav class="foot" aria-label="Previous and next topic">'
    if prev:
        foot += f'<a class="nxt" href="{prev[0]}.html"><small>{icon("arr-l")}Previous</small><strong>{html.escape(prev[1])}</strong></a>'
    else:
        foot += f'<a class="nxt" href="../dsa.html"><small>{icon("arr-l")}Back</small><strong>All topics</strong></a>'
    if nxt:
        foot += f'<a class="nxt next r" href="{nxt[0]}.html"><small>Next topic{icon("arr-r")}</small><strong>{html.escape(nxt[1])}</strong></a>'
    else:
        foot += f'<a class="nxt next r" href="../dsa.html"><small>Finished{icon("check")}</small><strong>Back to all topics</strong></a>'
    foot += "</nav>"
    b.append(foot)

    desc = re.sub(r"[`*]", "", t["lead"])[:240]
    return PAGE.format(
        title=html.escape(t["title"]), fname=t["file"], tid=tid, css=CSS, js=JS, num=num, n=n_topics,
        side="".join(side), chips=chips, body="\n".join(b), desc=html.escape(desc, quote=True),
        url=SITE_URL + "topics/" + t["file"], favicon=FAVICON, cat=t.get("_catalog", "[]"),
        short=html.escape(t["title"].split(" — ")[0]),
        rail=rail("dsa", "../"), rail_btn=rail_button(), i_menu=icon("list"), i_cal=icon("cal"), i_theme=icon("theme"), i_down=icon("down"), i_right=icon("right"),
    )


PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | DSA Mastery</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0f172a">
<meta property="og:type" content="article"><meta property="og:site_name" content="DSA Mastery"><meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}"><meta property="og:url" content="{url}">
<link rel="icon" href="{favicon}">
<style>{css}</style></head>
<body class="has-rail" data-lang="java" data-file="{fname}" data-topic="{tid}">
<a class="skip" href="#content">Skip to content</a>
{rail}
<header class="bar"><div class="bar-in">{rail_btn}<a class="brand" href="../index.html" aria-label="DSA Mastery home"><span class="logo" aria-hidden="true">DSA</span><b>DSA <span>Mastery</span></b></a>
<nav class="crumbs" aria-label="Breadcrumb"><a href="../dsa.html">DSA topics</a>{i_right}<span class="cur">{num} · {short}</span></nav>
<span class="prog" id="prog" aria-live="polite"></span>
<span class="seg" role="group" aria-label="Code language"><button id="b-java" class="on" aria-pressed="true">Java</button><button id="b-py" aria-pressed="false">Python</button></span>
<span class="menu"><button id="b-topics" class="btn" aria-haspopup="true" aria-expanded="false" aria-controls="topics-panel">{i_menu}<span class="t-long">All topics</span></button>
<div class="panel" id="topics-panel" role="menu" aria-label="All topics" hidden></div></span>
<a class="btn" href="../plan.html" title="Build a study plan">{i_cal}<span class="t-long">Planner</span></a>
<button id="b-theme" class="iconbtn" title="Toggle light / dark" aria-label="Toggle light or dark theme">{i_theme}</button>
<button id="b-dl" class="btn pri" title="Save this page as a standalone HTML file">{i_down}<span class="t-long">Download</span></button></div>
<div class="pbar" role="progressbar" aria-label="Problems solved on this page" aria-valuemin="0" aria-valuemax="100"><i id="pbar"></i></div></header>
<div class="wrap">{side}<main id="content">{chips}
{body}
</main></div>
<footer class="site-foot"><span>DSA Mastery: free, open study sheets. Progress is saved in your browser only.</span><span><a href="../dsa.html">All DSA topics</a> · <a href="https://github.com/nithin988/dsa-mastery" target="_blank" rel="noopener">GitHub</a></span></footer>
<script>window.DSA_TOPICS={cat};</script>
<script>{js}</script>
</body></html>
"""
