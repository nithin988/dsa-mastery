"""Quick revision page (revise.html): interview questions, flashcards, cheat sheets and a guide to answering well."""
import html
import json

from lib import SITE_URL, icon, rail
from sitepages import head, topbar, scripts, _read

HOW = """
<div class="how-grid">
<section class="hw"><h3>1. \"Something is broken, what do you do?\"</h3>
<p>Situation questions test your <b>order of thinking</b>. Use five beats and say each one out loud:</p>
<ol>
<li><b>Clarify</b>: what exactly is failing, since when, for whom, and what changed just before?</li>
<li><b>Locate</b>: name the layers or resources you would check, in order (DNS, TCP, TLS, HTTP; or CPU, memory, disk, network).</li>
<li><b>Evidence</b>: for each, the one command you would run and what output would confirm or reject the idea.</li>
<li><b>Act</b>: mitigate first (roll back, fail over, switch a flag off), then fix the cause.</li>
<li><b>Prevent</b>: the test, alert or runbook entry that stops it happening silently again.</li>
</ol>
<div class="ex"><span class="lbl">A one-minute answer: \"The site is down\"</span>
<p>\"First I would find out whether it is down for everyone or some users, since when, and what changed. Then I would walk the request path: does the name resolve (<code>getent hosts</code>), does the port accept connections (<code>nc -zv</code>), is the certificate valid (<code>openssl s_client</code>), what status does <code>curl -sv</code> show. If a deploy went out just before, I would roll it back to stop the harm, then read the logs of the failing step to find the cause. Afterwards I would write a short postmortem and add an alert for this failure.\"</p></div></section>

<section class="hw"><h3>2. \"Explain X\" (concept questions)</h3>
<ol>
<li>One plain sentence: what it is and why it exists.</li>
<li>An everyday analogy.</li>
<li>How it works in three steps (draw it if you can).</li>
<li>What goes wrong, or the trade-off.</li>
<li>A command or example you have actually run.</li>
</ol>
<p class="muted">Stop after about two minutes and ask whether they want more depth. Interviewers prefer a clear short answer they can steer.</p></section>

<section class="hw"><h3>3. \"Tell me about a time...\" (behavioural)</h3>
<p>Use <b>STAR</b>: Situation, Task, Action (what <em>you</em> did, not the team), Result (with a number), then one thing you learned. Prepare two or three real stories and make each one flexible:</p>
<ul>
<li>An outage or hard bug you diagnosed with evidence.</li>
<li>A time you owned something end to end, including the boring parts.</li>
<li>A time you disagreed, or changed your mind because of data.</li>
</ul></section>

<section class="hw"><h3>4. What big companies tend to look for</h3>
<p><b>Amazon</b> publishes its <a href="https://www.amazon.jobs/en/principles" target="_blank" rel="noopener">Leadership Principles</a>. Candidates commonly report behavioural questions tied to them, for example Ownership, Dive Deep, Customer Obsession, Bias for Action, Earn Trust and Deliver Results. An incident story fits naturally: customer impact first, you owned it, you went to the root cause with evidence, you acted fast (a rollback), you wrote it up.</p>
<p><b>Google</b> does not publish question lists on its careers pages; its <a href="https://grow.google/certificates/interview-warmup/" target="_blank" rel="noopener">own preparation advice</a> recommends the STAR method and practising out loud. Candidates commonly report that interviewers probe how you reason about scale, ambiguity and trade-offs, so narrate your assumptions and say what you would measure.</p>
<p class="muted">Everything about specific companies on this site is what candidates report, not official. The method above works whoever asks.</p></section>

<section class="hw"><h3>5. The night before</h3>
<ul>
<li>Read the cheat sheet of each module you were asked about.</li>
<li>Do five flashcards per module and answer them aloud.</li>
<li>Rehearse your two best stories with the numbers.</li>
<li>Pick one command per layer you can explain line by line.</li>
<li>Write three questions to ask the interviewer (how incidents are handled, what on-call looks like, what you would own in the first 90 days).</li>
</ul></section>
</div>
"""


def revise_html(live_modules, catalog_json):
    mods = []
    for m in live_modules:
        mods.append({"id": m["id"], "num": m["num"], "title": m["title"], "file": m["file"],
                     "interview": m.get("interview", []), "cheat": m.get("cheat", []),
                     "selftest": m.get("selftest", []), "recall": m.get("recall", [])})
    data = json.dumps({"modules": mods}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    nq = sum(len(m["interview"]) for m in mods)
    ncards = sum(len(m["selftest"]) + len(m["recall"]) for m in mods)
    desc = "Quick interview revision for Linux, Git, troubleshooting and system design: questions with strong-answer outlines, flashcards, cheat sheets and a guide to explaining how you would resolve a situation."
    return (head("Quick revision | Mastery", desc, SITE_URL + "revise.html", "Quick revision")
            + f"""
<body class="has-rail" data-revise="1">
<a class="skip" href="#content">Skip to content</a>
{rail("revise")}
{topbar("M", "Mastery", "index.html")}
<main id="content" class="home revise">
<section class="hero" style="margin-bottom:16px"><div class="eyebrow"><span class="tag">Revision</span>The night before</div>
<h1>Quick revision</h1>
<p class="lead">Everything you need to refresh before an interview, and nothing else: {nq} questions with the shape of a strong answer, {ncards} flashcards, one-page cheat sheets, and a guide to explaining how you would diagnose and resolve a situation.</p></section>
<div class="rv-top"><div id="rv-tabs" class="filters" role="group" aria-label="Revision mode">
<button data-t="q" aria-pressed="true">Questions</button><button data-t="f" aria-pressed="false">Flashcards</button><button data-t="c" aria-pressed="false">Cheat sheets</button><button data-t="h" aria-pressed="false">How to answer</button></div>
<label class="sel">Module <select id="rv-mod" aria-label="Choose a module"></select></label></div>
<div id="rv-body" aria-live="polite"></div>
<template id="how-tpl">{HOW}</template>
</main>
<footer class="site-foot"><span>Mastery: free, open study sheets. Company notes are what candidates report, not official. Progress is saved in your browser only.</span><span><a href="systems.html">Systems Mastery</a> · <a href="https://github.com/nithin988/dsa-mastery" target="_blank" rel="noopener">GitHub</a></span></footer>
{scripts("[]", "window.REVISE=" + data + ";", _read("revise.js"))}
</body></html>
""")
