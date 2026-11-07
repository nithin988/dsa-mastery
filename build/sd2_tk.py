"""Systems Mastery (the engineering toolkit) rebuilt in the same story format as System Design: 14 chapters in five parts.

Chapter content lives in build/sd2_tk_content/*.py and is picked from the verified reference modules, exactly like the System Design pages."""
import html
import importlib
import os

import sd2
import sd2kit as k
from lib import CSS, FAVICON, SITE_URL, icon, md, ul
from sd2 import PAGE, JS, SITE_CSS, CTX, _sec, _paras, _page, _foot, _deeper, render_interview, ROOT

OUT = os.path.join(ROOT, "toolkit")

# (slug, title, the incident that opens the chapter, content module or None)
PARTS = [
    ("Part 1. The machine", "How a computer runs your program, and how to get around it.", [
        ("01-how-programs-run", "Why did my program do that?", "A script works on your laptop and fails on the server, and nobody can say why.", "ch01_programs"),
        ("02-linux-shell", "Find your way around", "2:07 a.m., a disk is full and you do not know where to look.", "ch02_shell"),
        ("03-text-and-logs", "The log has the answer", "A million log lines, one customer complaint, and ten minutes.", "ch03_text"),
        ("04-linux-internals", "What is the machine doing?", "The server is up, but is it healthy? Processes, memory, disk and permissions.", "ch04_internals"),
    ]),
    ("Part 2. Working together", "Version control for a team that moves fast.", [
        ("05-git-basics", "Never lose work", "Two people edit the same file and one change quietly vanishes.", "ch05_git"),
        ("06-git-in-teams", "When the team grows and things go wrong", "A bad commit reached production on Friday afternoon.", "ch06_git_teams"),
    ]),
    ("Part 3. Connected systems", "How requests travel, and how software is packaged to run anywhere.", [
        ("07-networking", "How a request travels", "The site works for you, and not for a customer in another country.", "ch07_networking"),
        ("08-containers-and-cloud", "Boxes inside boxes", "\"It works on my machine.\" Containers, images and the cloud.", "ch08_containers"),
    ]),
    ("Part 4. When things break", "A method, the tools, and the runbooks.", [
        ("09-debugging", "Debug like a detective", "Three people, five theories, no answer.", "ch09_debugging"),
        ("10-performance", "The server is slow", "Everything is up and everything is slow: CPU, memory, disk or network?", "ch10_performance"),
        ("11-deep-tools", "When the usual tools are not enough", "The logs say nothing and the metrics look fine, but the process hangs.", "ch11_deep_tools"),
        ("12-playbooks", "The runbook", "The same incident, the fourth time, and still no checklist.", "ch12_playbooks"),
    ]),
    ("Part 5. Operating for real", "Run systems the way mature teams do.", [
        ("13-reliability-practice", "Measure, alert, respond", "Alerts at 3 a.m. for things nobody can fix, and none for the thing that mattered.", "ch13_reliability"),
        ("14-case-files", "Case files: how real outages happened", "What went wrong at companies you have heard of, and what they changed.", "ch14_cases"),
    ]),
]

CHAPTERS = []
for pi, (_pt, _pd, rows) in enumerate(PARTS):
    for slug, title, pain, mod in rows:
        CHAPTERS.append(dict(slug=slug, num=len(CHAPTERS) + 1, title=title, pain=pain, mod=mod, part=pi,
                             live=bool(mod) and os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sd2_tk_content", mod + ".py"))))

CASES_SLUG = "14-case-files"


def load(slug):
    for c in CHAPTERS:
        if c["slug"] == slug:
            return importlib.import_module("sd2_tk_content." + c["mod"]).DATA
    raise KeyError(slug)


# ----------------------------------------------------------------------------- case files page
def render_cases(c, prev, nxt):
    nav_items = [("story", "The story"), ("read", "How to read a postmortem"), ("cases", "The case files"), ("patterns", "Patterns across outages"), ("interview", "In the interview"), ("recap", "Remember")]
    nav = "".join(f'<a href="#{a}"><b>{i + 1}</b>{b}</a>' for i, (a, b) in enumerate(nav_items))
    b = [f'<header class="sdhero"><div class="eyebrow"><span class="tag">Chapter {c["num"]} of {len(CHAPTERS)}</span>{CTX["story"]}</div><h1>{html.escape(c["title"])}</h1>'
         f'<p class="lead">{md(c["tagline"])}</p><div class="sdmeta"><span>about {html.escape(c["time"])}</span><span>{len(c["cases"])} case files</span><span>every claim sourced</span></div></header>']
    st = c["story"]
    b.append(_sec("story", 1, st["title"], "The story", f'<div class="sdstory">{_paras(st["paras"])}</div>{st["strip"]}'))
    b.append(_sec("read", 2, "How to read a postmortem", "Method", _paras(c["how_to_read"]) + (c.get("read_figure") or "")))
    cases = []
    for n, cs in enumerate(c["cases"], 1):
        tl = "".join(f"<li><b>{md(t)}</b><span>{md(x)}</span></li>" for t, x in cs["timeline"])
        cards = "".join(f'<div class="sdcard {kind}"><h3>{md(t)}</h3><p>{md(x)}</p></div>' for t, x, kind in [("Root cause", cs["root_cause"], "bad"), ("Why it spread", cs["why_spread"], ""), ("What changed", cs["what_changed"], "ok")])
        cases.append(f'<article class="sdq"><header><span class="who">{html.escape(cs["when"])} · {html.escape(cs["company"])}</span><h3>{n}. {html.escape(cs["title"])}</h3><p>{md(cs["summary"])}</p></header><div class="body">'
                     + (cs.get("figure") or "") + "<h4>What happened</h4>" + _paras(cs["what_happened"]) + f"<h4>Timeline</h4><ol class='think'>{tl}</ol>"
                     + f'<div class="sdgrid">{cards}</div><h4>The lesson</h4><div class="say"><span class="lbl2">Take this to your own system</span>{_paras(cs["lesson"])}</div>'
                     + f'<p class="sdnote">Source: <a href="{cs["url"]}" target="_blank" rel="noopener">{html.escape(cs["source"])}</a>. {md(cs.get("caveat", "Summarised from the company or project write-up; read the source for the full detail."))}</p></div></article>')
    b.append(_sec("cases", 3, "The case files", "Case files", "".join(cases), sub=c.get("cases_sub", "Each case is told the same way: what happened, the timeline, the root cause, why it spread, what changed, and what to take away.")))
    pat = "".join(f'<div class="sdcard"><h3>{md(t)}</h3><p>{md(x)}</p></div>' for t, x in c["patterns"])
    b.append(_sec("patterns", 4, "Patterns across the outages", "Patterns", f'<div class="sdgrid">{pat}</div>'))
    b.append(_sec("interview", 5, "In the interview", "Questions", render_interview(c["interview"], c.get("interview_intro")), sub="Say your answer aloud first, then compare. These are questions candidates report, not official lists."))
    rc = c["recap"]
    quick = "".join(f"<details><summary>{md(q)}</summary><p>{md(a)}</p></details>" for q, a in rc["quick"])
    b.append(_sec("recap", 6, "Remember this", "Recap", f'<div class="sdrecap"><h3 style="margin:12px 0 0">The page in {len(rc["points"])} lines</h3>{ul(rc["points"])}</div><h3 style="margin:18px 0 6px">Check yourself</h3>{quick}{_deeper(c.get("deeper"))}'))
    b.append(_foot(prev, nxt))
    return _page(c, nav, "\n".join(b), f'Chapter {c["num"]} · {c["title"]}')


# ----------------------------------------------------------------------------- landing
def render_landing():
    done_js = "var s={};try{s=JSON.parse(localStorage.getItem('sd2-done')||'{}')}catch(e){}[].forEach.call(document.querySelectorAll('[data-slug]'),function(n){if(s[n.dataset.slug]){var t=n.querySelector('.pill');if(t){t.textContent='Done';t.classList.add('tick-ok')}}});"
    p = ['<header class="sdhero"><div class="eyebrow"><span class="tag">Systems Mastery</span>Fourteen chapters, one night shift</div>'
         '<h1>Be the engineer people call when things break</h1><p class="lead">You have just joined ShopKart as its first engineer who looks after the machines. Every chapter starts at 2 a.m. with something that went wrong, then teaches the Linux, Git, networking and debugging skills that fix it, with real commands, real output and the questions interviewers ask.</p>'
         '<div class="sdmeta"><span>14 chapters</span><span>five parts</span><span>real commands, real output</span><span>interview questions on every page</span></div></header>']
    p.append(k.strip([
        {"title": "2:07 a.m.", "kind": "bad", "scene": lambda cx, cy, w: k.phone(cx - 44, cy, "pager", "bad") + k.alert(cx + 40, cy - 4, None), "caption": "The pager goes off. The site is slow and nobody knows why."},
        {"title": "2:19 a.m.", "kind": "warn", "scene": lambda cx, cy, w: k.person(cx - 50, cy - 8, 1.1, "warn") + k.server(cx + 36, cy, "server", "warn") + k.flow(cx - 24, cy, cx + 6, cy, "warn"), "caption": "You follow a method: look, measure, narrow down. The log shows the culprit."},
        {"title": "2:41 a.m.", "kind": "ok", "scene": lambda cx, cy, w: k.person(cx - 50, cy - 8, 1.1, "ok") + k.server(cx + 36, cy, "fixed", "ok") + k.flow(cx - 24, cy, cx + 6, cy, "ok"), "caption": "Fixed, written up, and next time there is a runbook."},
    ], "One night shift", "Every chapter follows this shape: something breaks, you learn the skill, you fix it for good."))
    p.append('<div class="sdland">')
    for pi, (pt, pd, _rows) in enumerate(PARTS):
        p.append(f'<h2>{html.escape(pt)}</h2><p class="muted">{html.escape(pd)}</p><div class="path">')
        for c in [c for c in CHAPTERS if c["part"] == pi]:
            live = c["live"]
            tag, href = ("a", f' href="{c["slug"]}.html"') if live else ("div", "")
            p.append(f'<{tag} class="node{"" if live else " soon"}" data-n="{c["num"]}" data-slug="{c["slug"]}"{href}><div><b>{html.escape(c["title"])}</b><span>{md(c["pain"])}</span></div><span class="pill{"" if live else " soon"}">{"Read" if live else "Coming"}</span></{tag}>')
        p.append("</div>")
    p.append('<h2>How to use this course</h2><div class="sdgrid"><div class="sdcard"><h3>Read one chapter at a time</h3><p>About 20 minutes each. A story, a picture, real commands, and the interview questions on the same page.</p></div>'
             '<div class="sdcard"><h3>Type the commands</h3><p>Every command ran for real as an ordinary user. Change something and see what happens: that is where the skill comes from.</p></div>'
             '<div class="sdcard"><h3>Go deeper when you need</h3><p>Each chapter links to the full reference lessons and labs. Looking for system design? Try the <a href="../design/index.html">System Design course</a>.</p></div></div>'
             '<p class="sdnote">The earlier long modules are still available in the <a href="../systems.html">reference library</a>.</p></div>')
    desc = "Linux, Git, networking, debugging and operations, taught as a night shift at a small shop: fourteen chapters with real commands and interview questions."
    return PAGE.format(title="Be the engineer people call when things break", desc=html.escape(desc, quote=True), url=SITE_URL + "toolkit/", favicon=FAVICON, css=CSS + k.CSS + SITE_CSS,
                       slug="index", rail_btn=sd2.rail_button(), **sd2._ctx_fields(), i_right=icon("right"), i_theme=icon("theme"), crumb="Course map",
                       nav="<h4>The course</h4>" + "".join(f'<a href="#"><b>{i + 1}</b>{html.escape(pt.split(". ", 1)[1])}</a>' for i, (pt, _pd, _r) in enumerate(PARTS)),
                       body=f'<div>{"".join(p)}</div><script>{done_js}</script>', js=JS, ic="{}")


def build():
    sd2.set_course("toolkit")
    try:
        os.makedirs(OUT, exist_ok=True)
        live = [c for c in CHAPTERS if c["live"]]
        written = []
        for i, c in enumerate(live):
            prev = (live[i - 1]["slug"], live[i - 1]["title"]) if i else None
            nxt = (live[i + 1]["slug"], live[i + 1]["title"]) if i + 1 < len(live) else None
            data = dict(c, **load(c["slug"]))
            text = render_cases(data, prev, nxt) if c["slug"] == CASES_SLUG else sd2.render_chapter(data, prev, nxt, len(CHAPTERS))
            with open(os.path.join(OUT, c["slug"] + ".html"), "w", encoding="utf-8", newline=chr(10)) as f:
                f.write(text)
            written.append(c["slug"])
        with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8", newline=chr(10)) as f:
            f.write(render_landing())
        written.append("index")
        return written
    finally:
        sd2.set_course("design")
