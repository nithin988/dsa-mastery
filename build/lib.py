"""Shared renderer for every DSA topic page.

A topic is a dict (see build/arrays.py). `render_topic` turns it into one
self-contained HTML file: no external requests, works offline.
Styles live in style.css, page behaviour in engine.js, animations in sims.js.
"""
import html
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


def _read(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return f.read()


CSS = _read("style.css")
JS = "(function(){\n" + _read("sims.js") + "\n" + _read("engine.js") + "\n})();"

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


def blk(label, inner, cls=""):
    return f'<div class="blk {cls}"><span class="lbl">{label}</span>{inner}</div>'


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
            f'<td class="t"><a href="https://leetcode.com/problems/{slug}/" target="_blank" rel="noopener">LC {lc}</a></td>'
            f'<td>{html.escape(name)}</td><td><span class="pill {cls}">{label}</span></td>'
            f"<td>{md(logic)}</td><td class=\"c\">{md(cx)}</td></tr>"
        )
    return (
        '<div class="tw"><table class="ladder"><thead><tr><th></th><th>Problem</th><th>Title</th>'
        "<th>Level</th><th>One-line logic</th><th>Time / Space</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


def render_pattern(topic_id, n, p, unit="Pattern"):
    pid = f"p{n}"
    o = [f'<section class="pat {p["tier"]}" id="{pid}">']
    o.append(
        f'<div class="pat-h"><span class="badge">{n}</span><h3>{html.escape(p["title"])}</h3>'
        f'<span class="tier {p["tier"]}">{TIER[p["tier"]]}</span><span class="pp"></span></div>'
    )
    o.append(
        '<div class="glance">'
        f'<div class="gi"><span class="lbl">When to use</span>{md(p["when"])}</div>'
        f'<div class="gi"><span class="lbl">Detect it</span>{md(p["detect"])}</div></div>'
    )
    if p.get("intuition"):
        o.append(f'<div class="callout intu"><span class="lbl">Intuition</span><p>{md(p["intuition"])}</p></div>')
    if p.get("brute"):
        o.append(blk("Brute force → optimised", f'<p>{md(p["brute"])}</p>'))
    o.append(blk("Core idea", f'<p>{md(p["idea"])}</p>'))
    o.append(blk("How it works", ul(p["steps"], "ol")))
    if p.get("sim"):
        o.append(
            '<span class="lbl" style="margin-top:14px">Watch it run</span>'
            '<p class="muted" style="margin:0 0 4px">Press Play, or step with the buttons, the slider or the ← → keys.</p>'
            f'<div class="stepper" data-sim="{p["sim"]}"></div>'
        )
    if p.get("trace"):
        o.append(blk("Worked trace", f'<p>{md(p["trace_title"])}</p><pre class="trace"><code>{html.escape(p["trace"].strip())}</code></pre>'))
    for label, java, py in p["code"]:
        o.append(blk("Skeleton", f"<p>{md(label)}</p>" + code_block(java, py)))
    o.append(f'<div class="cx">⏱ Complexity — {md(p["complexity"])}</div>')
    o.append(blk("Traps to avoid", ul(p["traps"]), "warn"))
    if p.get("variants"):
        o.append(blk("Variants and follow-ups", ul(p["variants"])))
    o.append(blk("When NOT to use", f'<p>{md(p["notuse"])}</p>'))
    o.append(blk("Problem ladder", '<p class="muted">Easy → hard. Tick what you have solved; ticks are saved in this browser.</p>' + problems_table(topic_id, p["problems"])))
    o.append("</section>")
    return "\n".join(o)


def table(headers, rows, cls=""):
    h = "".join(f"<th>{html.escape(x)}</th>" for x in headers)
    r = "".join("<tr>" + "".join(f"<td>{md(c)}</td>" for c in row) + "</tr>" for row in rows)
    return f'<div class="tw"><table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{r}</tbody></table></div>'


def render_topic(t):
    tid = t["id"]
    pats = t["patterns"]
    unit = t.get("unit", "Pattern")
    total = sum(len(p["problems"]) for p in pats)
    num = t["file"].split("_")[0]

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

    chips = '<div class="chips">' + "".join(f'<a href="#p{i+1}">{i+1}. {html.escape(p["title"])}</a>' for i, p in enumerate(pats)) + "</div>"

    prio_rows = [[str(i + 1), f"**{p['title']}**", p["why"], p["signature"]] for i, p in enumerate(pats)]
    hot = [r for r, p in zip(prio_rows, pats) if p["tier"] == "hot"]
    sec = [r for r, p in zip(prio_rows, pats) if p["tier"] == "sec"]
    ph = ["#", unit, "Why it matters", "Signature problem"]

    sims = sum(1 for p in pats if p.get("sim"))
    b = []
    b.append(
        f'<header class="hero"><div class="eyebrow">Topic {num}</div><h1>{html.escape(t["title"])}</h1>'
        f'<p class="lead">{md(t["lead"])}</p><div class="stats">'
        f'<span class="stat"><b>{len(pats)}</b> {unit.lower()}s</span><span class="stat"><b>{total}</b> practice problems</span>'
        f'<span class="stat"><b>{sims}</b> animations</span><span class="stat">Java + Python</span></div></header>'
    )
    b.append(
        '<div class="callout"><span class="lbl">How to use this page</span><p>For each section: read <em>Detect</em> and <em>Intuition</em>, '
        "play the animation, then try to write the skeleton from memory before opening the code. Finish by solving the problem ladder in order.</p></div>"
    )
    b.append('<h2 id="mindset">The mindset</h2>' + f"<p>{md(t['mindset'])}</p><p>{md(t.get('qintro', 'Ask these questions on every problem:'))}</p>" + ul(t["questions"]))
    b.append(
        '<h2 id="priority">Priority</h2><p class="muted">Ranked by how often these show up in interviews '
        "(our judgement from the common interview lists and company question banks, not hard data).</p>"
        "<h3 style='margin:14px 0 4px;font-size:16px'>🔥 Frequently asked — master these first</h3>" + table(ph, hot)
        + "<h3 style='margin:14px 0 4px;font-size:16px'>🧊 Secondary — know them</h3>" + table(ph, sec)
    )
    b.append('<h2 id="cues">Problem cues</h2><p class="muted">If the problem says this, think of that.</p>' + table(["If the problem says / looks like…", unit], t["cues"]))
    b.append("<h2>" + t.get("units_heading", "The patterns") + "</h2>")
    for i, p in enumerate(pats):
        b.append(render_pattern(tid, i + 1, p, unit))
    b.append(
        '<h2 id="recall">One-line recall</h2>'
        + table(["#", unit, "Tier", "Core idea in one line"], [[str(i + 1), p["title"], "🔥" if p["tier"] == "hot" else "🧊", p["oneline"]] for i, p in enumerate(pats)])
    )
    b.append('<h2 id="choose">Choosing between them</h2>' + table(["Need", "Use"], t["choose"]) + f'<div class="callout"><span class="lbl">Rule of thumb</span><p>{md(t["rule"])}</p></div>')
    st = "".join(f"<details><summary>{md(q)}</summary><p>{md(a)}</p></details>" for q, a in t["selftest"])
    b.append('<h2 id="selftest">Self-test</h2><p class="muted">Answer in your head first, then click to reveal.</p>' + st)
    b.append('<h2 id="plan">Study plan</h2>' + ul(t["plan"], "ol"))
    prev, nxt = t.get("prev"), t.get("next")
    foot = '<div class="foot"><span>'
    foot += f'<a href="{prev[0]}.html">← {html.escape(prev[1])}</a>' if prev else '<a href="../index.html">← All topics</a>'
    foot += "</span><span>"
    foot += f'<a href="{nxt[0]}.html">{html.escape(nxt[1])} →</a>' if nxt else ""
    foot += "</span></div>"
    b.append(foot)

    return PAGE.format(
        title=html.escape(t["title"]), fname=t["file"], tid=tid, css=CSS, js=JS,
        side="".join(side), chips=chips, body="\n".join(b),
    )


PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>{css}</style></head>
<body data-lang="java" data-file="{fname}" data-topic="{tid}">
<div class="bar"><div class="bar-in"><a class="brand" href="../index.html"><b>DSA</b> <span>Mastery</span></a>
<span class="prog" id="prog"></span>
<span class="seg"><button id="b-java" class="on">Java</button><button id="b-py">Python</button></span>
<button id="b-theme" title="Toggle light / dark" aria-label="Toggle theme">◐</button>
<button id="b-dl" title="Save this page as a standalone HTML file">⬇ Download</button></div><div class="pbar"><i id="pbar"></i></div></div>
<div class="wrap">{side}<main>{chips}
{body}
</main></div>
<script>{js}</script>
</body></html>
"""
