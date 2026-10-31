"""Renderer for Systems Mastery modules (Linux, Git, troubleshooting, system design).

A module is a dict (see build/sys_linux_shell.py). Commands marked run (the default) have their output recorded
from a real Debian container by verify/sys_record.py and stored in build/sys_outputs.json; the build fails if a
command changed after its output was recorded, so the pages cannot show invented output.
"""
import html
import json
import os
import re

from lib import CSS, ICONS, FAVICON, SITE_URL, HERE, icon, md, ul, table, rail, rail_button

OUTPUTS_PATH = os.path.join(HERE, "sys_outputs.json")
LAB_BASE = SITE_URL + "systems/labs/"

JS_PARTS = ("sims_sys.js", "engine.js", "rail.js")
JS = "(function(){\nvar IC=" + json.dumps(ICONS, separators=(",", ":")) + ";\n" + "\n".join(open(os.path.join(HERE, f), encoding="utf-8").read() for f in JS_PARTS) + "\n})();"


class StaleOutput(Exception):
    pass


def load_outputs():
    if os.path.exists(OUTPUTS_PATH):
        with open(OUTPUTS_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def walk_cmds(m):
    """Every command of a module in page order (lessons, groups, commands)."""
    out = []
    for L in m["lessons"]:
        for g in L.get("groups", []):
            for c in g["cmds"]:
                out.append(c)
    return out


def runnable(m):
    return [c for c in walk_cmds(m) if c.get("run", True)]


def slbl(label, ic=None):
    return f'<span class="lbl">{icon(ic) if ic else ""}{html.escape(label)}</span>'


def sblk(label, ic, inner, cls=""):
    return f'<div class="blk {cls}">{slbl(label, ic)}{inner}</div>'


def paras(items):
    if isinstance(items, str):
        items = [items]
    return "".join(f"<p>{md(p)}</p>" for p in items)


def tick(key, text):
    return f'<label class="tick"><input type="checkbox" class="pk" data-k="{key}" aria-label="{html.escape(text)}"><span>{html.escape(text)}</span></label>'


def render_cmd(c, entry, env="Linux"):
    parts_tbl = ""
    if c.get("parts"):
        parts_tbl = '<div class="tw parts"><table><thead><tr><th>Part</th><th>What it does</th></tr></thead><tbody>' + "".join(
            f"<tr><td><code>{html.escape(a)}</code></td><td>{md(b)}</td></tr>" for a, b in c["parts"]) + "</tbody></table></div>"
    if c.get("run", True):
        text = entry["out"].rstrip("\n")
        label = f'<span class="stamp">Real output · {html.escape(env)}, ordinary user</span>'
        out = (f'<pre class="out"><code>{html.escape(text)}</code></pre>' if text
               else '<p class="muted noout">No output. In the shell, silence usually means success.</p>')
    else:
        label = '<span class="stamp ill">Illustrative output · will differ on your machine</span>'
        out = f'<pre class="out ill"><code>{html.escape(c["o"].rstrip())}</code></pre>'
    return (f'<div class="cmd"><pre class="sh"><code>{html.escape(c["c"])}</code></pre>'
            f'<div class="cmd-b">{paras(c["e"])}{parts_tbl}<div class="out-l">{label}</div>{out}</div></div>')


def render_lesson(mid, n, L, outputs, counter):
    pid = f"l{n}"
    tier = L.get("tier", "hot")
    tier_txt = icon("flame") + " Must know" if tier == "hot" else icon("mark") + " Good to know"
    o = [f'<section class="pat {tier}" id="{pid}" aria-labelledby="{pid}-t">']
    o.append(f'<div class="pat-h"><span class="badge">{n}</span><h3 id="{pid}-t">{html.escape(L["title"])}</h3>'
             f'<span class="tier {tier}">{tier_txt}</span><span class="pp"></span>{tick(f"{mid}-L{n}", "Mark done")}</div><div class="pat-b">')
    o.append('<div class="glance"><div class="gi">' + slbl("Situation", "target") + paras(L["situation"]) + "</div>"
             '<div class="gi">' + slbl("You will learn", "list") + ul(L["learn"]) + "</div></div>")
    o.append(f'<div class="callout intu">{slbl("Mental model", "bulb")}{paras(L["model"])}'
             + (f'<p class="analogy"><b>Everyday analogy:</b> {md(L["analogy"])}</p>' if L.get("analogy") else "") + "</div>")
    if L.get("visual"):
        o.append(f'<div class="blk">{slbl("The picture", "layers")}{L["visual"]}</div>')
    if L.get("sim"):
        o.append(f'<div class="blk">{slbl("Watch it run", "film")}<p class="muted" style="margin:0 0 6px">Press play, or step with the buttons, the slider or the arrow keys.</p>'
                 f'<div class="stepper" data-sim="{L["sim"]}"></div></div>')
    for g in L.get("groups", []):
        o.append(f'<div class="blk">{slbl(g["title"], "term")}')
        if g.get("intro"):
            o.append(paras(g["intro"]))
        for c in g["cmds"]:
            entry = None
            if c.get("run", True):
                recorded = outputs.get(mid, [])
                if counter[0] >= len(recorded) or recorded[counter[0]]["cmd"] != c["c"]:
                    raise StaleOutput(f"{mid}: output for command #{counter[0]} ({c['c'][:50]!r}) is missing or stale; run python verify/sys_record.py")
                entry = recorded[counter[0]]
                counter[0] += 1
            o.append(render_cmd(c, entry, outputs.get('_env', 'Linux')))
        o.append("</div>")
    if L.get("playbook"):
        pb = L["playbook"]
        o.append(sblk(pb["title"], "search", paras(pb.get("intro", [])) + table(["Symptom", "Check", "What the output means", "Fix"], pb["rows"], "playbook")))
    if L.get("traps"):
        o.append(sblk("Traps to avoid", "warn", ul(L["traps"]), "warn"))
    o.append("</div></section>")
    return "\n".join(o)


def render_lab(mid, i, lab):
    pid = f"lab{i}"
    kind = lab["kind"]
    url = f'{LAB_BASE}{kind}/{lab["script"]}.sh'
    if kind == "git":
        setup = f'curl -fsSLO {url}\nless {lab["script"]}.sh      # read it first: it only touches ~/sys-lab\nbash {lab["script"]}.sh\ncd ~/sys-lab' + (f'/{lab["dir"]}' if lab.get("dir") else '')
        how = ("Run this in a terminal with Git (Linux, macOS, WSL or Git Bash). The script builds a practice repository in a throwaway folder "
               "(~/sys-lab) and never touches your own projects. To start over, run it again.")
    else:
        setup = (f'# Option A: a disposable Debian container (nothing on your computer changes)\n'
                 f'docker build -t sys-lab https://github.com/nithin988/dsa-mastery.git#main:systems/labs/linux\n'
                 f'docker run --rm -it sys-lab lab {lab["script"]}\n\n'
                 f'# Option B: any Linux, macOS or WSL shell (the script only touches ~/sys-lab)\n'
                 f'curl -fsSLO {url}\nless {lab["script"]}.sh      # read it first\nbash {lab["script"]}.sh\ncd ~/sys-lab')
        how = ("Choose one option. Docker gives you a throwaway system you can break freely; type exit to leave and everything is deleted. "
               "The plain route runs the same script in your own shell, in a folder called ~/sys-lab.")
    o = [f'<section class="pat lab" id="{pid}" aria-labelledby="{pid}-t"><div class="pat-h"><span class="badge">{icon("flask")}</span>'
         f'<h3 id="{pid}-t">Lab {i}: {html.escape(lab["title"])}</h3><span class="tier sec">{icon("flask")} Hands-on</span><span class="pp"></span>'
         f'{tick(f"{mid}-lab{i}", "I completed this lab")}</div><div class="pat-b">']
    o.append('<div class="glance"><div class="gi">' + slbl("Goal", "target") + paras(lab["goal"]) + "</div>"
             '<div class="gi">' + slbl("The situation", "bulb") + paras(lab["story"]) + "</div></div>")
    o.append(sblk("Set it up", "term", f"<p>{md(how)}</p>" + f'<pre class="sh"><code>{html.escape(setup)}</code></pre>'))
    o.append(sblk("Your tasks", "list", ul(lab["tasks"], "ol")))
    o.append(sblk("Check your work", "check", f'<p>{md(lab["check"])}</p>' + (f'<pre class="sh"><code>{html.escape(lab["check_cmd"])}</code></pre>' if lab.get("check_cmd") else "")))
    hints = "".join(f"<details><summary>Hint {k + 1}</summary><p>{md(h)}</p></details>" for k, h in enumerate(lab["hints"]))
    o.append(sblk("Hints (try first, then open one at a time)", "bulb", hints))
    sol = "".join(f"<p>{md(p)}</p>" for p in ([lab["solution"]] if isinstance(lab["solution"], str) else lab["solution"]))
    o.append(f'<div class="blk"><details><summary>Show the solution</summary>{sol}</details></div>')
    o.append("</div></section>")
    return "\n".join(o)


def render_case(c):
    link = f'<p><a href="{c["url"]}" target="_blank" rel="noopener">{icon("ext")} Read the original public write-up</a></p>' if c.get("url") else ""
    return (f'<div class="case"><span class="lbl">{icon("layers")}Real-life case</span><h4>{html.escape(c["title"])}</h4>{paras(c["story"])}'
            f'<p><b>What to take from it:</b> {md(c["lesson"])}</p>{link}</div>')


def render_qa(q):
    o = [f'<details class="qa"><summary>{md(q["q"])}</summary><div class="qa-b">']
    o.append(slbl("Shape of a strong answer", "check") + ul(q["a"]))
    if q.get("follow"):
        o.append(slbl("Follow-ups to expect", "arr-r") + ul(q["follow"]))
    if q.get("mistakes"):
        o.append(slbl("Common mistakes", "warn") + ul(q["mistakes"]))
    if q.get("angle"):
        o.append(f'<p class="angle"><b>Company angle:</b> {md(q["angle"])}</p>')
    o.append("</div></details>")
    return "".join(o)


def render_module(m):
    outputs = load_outputs()
    mid, num = m["id"], m["num"]
    n_total = m.get("_n_total", 29)
    counter = [0]
    lessons, labs = m["lessons"], m.get("labs", [])
    sims = sum(1 for L in lessons if L.get("sim"))
    nq = len(m.get("interview", []))
    side = ['<nav class="side" aria-label="On this page"><h4>Start here</h4><a href="#why">Why it matters</a><a href="#before">Before you start</a><h4>Lessons</h4>']
    for i, L in enumerate(lessons):
        side.append(f'<a href="#l{i+1}"><span class="dot {L.get("tier", "hot")}"></span>{i+1}. {html.escape(L["title"])}<span class="cnt"></span></a>')
    if labs:
        side.append("<h4>Hands-on</h4>")
        for i, lab in enumerate(labs):
            side.append(f'<a href="#lab{i+1}"><span class="dot sec"></span>Lab {i+1}. {html.escape(lab["title"])}<span class="cnt"></span></a>')
    side.append("<h4>Wrap up</h4>")
    extras = [("cheat", "Cheat sheet")]
    if m.get("cases"):
        extras.insert(0, ("cases", "Real-life cases"))
    if m.get("playbooks"):
        extras.insert(0, ("playbooks", "Playbooks"))
    extras += [("interview", "Interview corner"), ("selftest", "Self-test"), ("sources", "Further reading")]
    for a, b in extras:
        side.append(f'<a href="#{a}">{b}</a>')
    side.append("</nav>")
    chips = '<div class="chips" aria-label="Jump to a lesson">' + "".join(f'<a href="#l{i+1}">{i+1}. {html.escape(L["title"])}</a>' for i, L in enumerate(lessons)) + "</div>"

    b = []
    b.append(f'<header class="hero"><div class="eyebrow"><span class="tag">Module {num} of {n_total}</span>{html.escape(m["track"])}</div>'
             f'<h1>{html.escape(m["title"])}</h1><p class="lead">{md(m["lead"])}</p><div class="stats">'
             f'<span class="stat"><b>{len(lessons)}</b> lessons</span><span class="stat"><b>{len(labs)}</b> labs</span>'
             f'<span class="stat"><b>{sims}</b> animations</span><span class="stat"><b>{nq}</b> interview questions</span>'
             f'<span class="stat">about <b>{html.escape(m["time"])}</b></span></div></header>')
    b.append(f'<h2 id="why">Why this matters</h2><div class="callout">{slbl("A real situation", "bulb")}{paras(m["why"])}</div>'
             f'<div class="callout intu">{slbl("After this module you can", "check")}{ul(m["outcomes"])}</div>')
    b.append(f'<h2 id="before">Before you start</h2>{paras(m["before"])}')
    if m.get("env"):
        b.append(f'<div class="callout">{slbl("Your practice shell", "term")}{paras(m["env"])}</div>')
    b.append("<h2>The lessons</h2>")
    for i, L in enumerate(lessons):
        b.append(render_lesson(mid, i + 1, L, outputs, counter))
    if labs:
        b.append("<h2>Hands-on labs</h2><p class=\"muted\">Reading is not enough for this material. Each lab sets up a realistic mess for you to fix.</p>")
        for i, lab in enumerate(labs):
            b.append(render_lab(mid, i + 1, lab))
    if m.get("playbooks"):
        b.append('<h2 id="playbooks">Troubleshooting playbooks</h2>')
        for pb in m["playbooks"]:
            b.append(f"<h3 style='margin:14px 0 4px;font-size:16px'>{html.escape(pb['title'])}</h3>{paras(pb.get('intro', []))}" + table(["Symptom", "Check", "What the output means", "Fix"], pb["rows"], "playbook"))
    if m.get("cases"):
        b.append('<h2 id="cases">Real-life cases</h2>' + "".join(render_case(c) for c in m["cases"]))
    b.append('<h2 id="cheat">Cheat sheet</h2><p class="muted">Print this section or keep it open next to your terminal.</p>' + table(["Command or idea", "What it does"], m["cheat"], "cheat"))
    b.append(f'<h2 id="interview">Interview corner</h2><p class="muted">{md(m.get("interview_intro", "Questions like these are common in engineering interviews. Say your answer out loud, then open the question."))}</p>'
             + "".join(render_qa(q) for q in m["interview"]) + f'<div style="margin-top:10px">{tick(f"{mid}-iv", "I can answer these out loud")}</div>')
    st = "".join(f"<details><summary>{md(q)}</summary><p>{md(a)}</p></details>" for q, a in m["selftest"])
    b.append('<h2 id="selftest">Self-test</h2><p class="muted">Answer in your head first, then open the question.</p>' + st)
    b.append('<h2 id="recall">One-line recall</h2>' + table(["Idea", "In one line"], m["recall"]))
    src_rows = [[f'[{s["title"]}]({s["url"]})' if False else s["title"], s["use"], s["license"], s["how"]] for s in m["sources"]]
    src_html = '<div class="tw"><table><thead><tr><th>Resource</th><th>Best for</th><th>Licence or terms</th><th>How this module uses it</th></tr></thead><tbody>' + "".join(
        f'<tr><td><a href="{s["url"]}" target="_blank" rel="noopener">{html.escape(s["title"])}</a></td><td>{md(s["use"])}</td><td>{md(s["license"])}</td><td>{md(s["how"])}</td></tr>' for s in m["sources"]) + "</tbody></table></div>"
    b.append('<h2 id="sources">Further reading</h2><p class="muted">Every explanation in this module is written for this course. These are the best free sources to go deeper; where a licence forbids copying, we only link.</p>' + src_html)
    b.append('<h2 id="plan">Study plan</h2>' + ul(m["plan"], "ol"))
    prev, nxt = m.get("prev"), m.get("next")
    foot = '<nav class="foot" aria-label="Previous and next module">'
    foot += (f'<a class="nxt" href="{prev[0]}.html"><small>{icon("arr-l")}Previous</small><strong>{html.escape(prev[1])}</strong></a>' if prev
             else f'<a class="nxt" href="../systems.html"><small>{icon("arr-l")}Back</small><strong>All Systems modules</strong></a>')
    foot += (f'<a class="nxt next r" href="{nxt[0]}.html"><small>Next module{icon("arr-r")}</small><strong>{html.escape(nxt[1])}</strong></a>' if nxt
             else f'<a class="nxt next r" href="../systems.html"><small>More coming{icon("check")}</small><strong>Back to the Systems course</strong></a>')
    foot += "</nav>"
    b.append(foot)
    desc = re.sub(r"[`*]", "", m["lead"])[:240]
    return PAGE_SYS.format(
        title=html.escape(m["title"]), fname=m["file"], mid=mid, css=CSS, js=JS, num=num, side="".join(side), chips=chips, body="\n".join(b),
        desc=html.escape(desc, quote=True), url=SITE_URL + "systems/" + m["file"], favicon=FAVICON, cat=m.get("_catalog", "[]"),
        short=html.escape(m["title"]), rail=rail("systems", "../"), rail_btn=rail_button(),
        i_menu=icon("menu"), i_theme=icon("theme"), i_down=icon("down"), i_right=icon("right"),
    )


PAGE_SYS = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | Systems Mastery</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0f172a">
<meta property="og:type" content="article"><meta property="og:site_name" content="Systems Mastery"><meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}"><meta property="og:url" content="{url}">
<link rel="icon" href="{favicon}">
<style>{css}</style></head>
<body class="has-rail" data-file="{fname}" data-topic="{mid}" data-store="sys-progress" data-last="sys-last" data-word="done">
<a class="skip" href="#content">Skip to content</a>
{rail}
<header class="bar"><div class="bar-in">{rail_btn}<a class="brand" href="../systems.html" aria-label="Systems Mastery home"><span class="logo" aria-hidden="true">SYS</span><b>Systems <span>Mastery</span></b></a>
<nav class="crumbs" aria-label="Breadcrumb"><a href="../systems.html">Systems modules</a>{i_right}<span class="cur">{num} · {short}</span></nav>
<span class="prog" id="prog" aria-live="polite"></span>
<span class="menu"><button id="b-topics" class="btn" aria-haspopup="true" aria-expanded="false" aria-controls="topics-panel">{i_menu}<span class="t-long">All modules</span></button>
<div class="panel" id="topics-panel" role="menu" aria-label="All modules" hidden></div></span>
<button id="b-theme" class="iconbtn" title="Toggle light / dark" aria-label="Toggle light or dark theme">{i_theme}</button>
<button id="b-dl" class="btn pri" title="Save this page as a standalone HTML file">{i_down}<span class="t-long">Download</span></button></div>
<div class="pbar" role="progressbar" aria-label="Steps done in this module" aria-valuemin="0" aria-valuemax="100"><i id="pbar"></i></div></header>
<div class="wrap">{side}<main id="content">{chips}
{body}
</main></div>
<footer class="site-foot"><span>Systems Mastery: free, open study sheets. Progress is saved in your browser only.</span><span><a href="../systems.html">All Systems modules</a> · <a href="https://github.com/nithin988/dsa-mastery" target="_blank" rel="noopener">GitHub</a></span></footer>
<script>window.DSA_TOPICS={cat};</script>
<script>{js}</script>
</body></html>
"""
