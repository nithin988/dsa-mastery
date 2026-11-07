"""Part 3: the interview playbook page (how to run the 45 minutes, say trade-offs, and what to practise)."""
import html

import sd2kit as k
from sd2 import _page, _sec, _paras, md, ul

SLUG = "playbook"
TITLE = "The interview playbook"
TAGLINE = "How to run the 45 minutes, explain your choices, avoid the usual mistakes, and practise in the right order."

PLAN_FIG = k.figure(720, 190, [
    k.badge(60, 26, "0 to 5", "acc"), k.badge(170, 26, "5 to 10", "acc"), k.badge(280, 26, "10 to 15", "acc"), k.badge(440, 26, "15 to 30", "ok"), k.badge(600, 26, "30 to 40", "ok"), k.badge(690, 26, "40 to 45", "warn"),
    k.person(60, 78, 1), k.note(60, 120, "Clarify", "acc"),
    k.note(170, 80, "Numbers", "acc"), k.note(170, 98, "only if they", "acc"), k.note(170, 114, "change the design", "acc"),
    k.server(280, 76, None), k.note(280, 128, "API and data", "acc"),
    k.balancer(380, 78, None, "ok"), k.cache(440, 78, None, "ok"), k.database(500, 78, None, "ok"), k.note(440, 132, "The whole design, end to end", "ok"),
    k.alert(600, 78, None, "warn"), k.note(600, 128, "Deep dive and failures", "ok"),
    k.clock(690, 78, None, "warn"), k.note(690, 128, "Trade-offs", "warn"),
    k.note(360, 172, "Say the plan out loud at the start, then check in at each stage. Leave real time for the deep dive: that is where senior signal is scored.", ""),
], "A 45 minute design interview", None)

DATA = dict(
    slug=SLUG, title=TITLE, tagline=TAGLINE, num=0,
)

SECTIONS = [
    ("rubric", "What interviewers are looking for", "The rubric",
     _paras(["Interview-prep sites and engineers who run these interviews describe the same flow, even when they give it different names: **clarify the requirements, estimate only what changes the design, define the API and data, draw the high-level design, go deep on the hard part, then cover failures and trade-offs.** Senior-level signal is usually scored in the deep dive, so a candidate who runs out of time before it loses the chance to show it."]) +
     '<div class="sdgrid">' + "".join(f'<div class="sdcard"><h3>{md(t)}</h3><p>{md(x)}</p></div>' for t, x in [
         ("Scoping", "Do you ask what the system must do, for whom, and how big, before you draw?"),
         ("Structure", "Can you break a vague problem into stages and drive the conversation?"),
         ("Depth", "Do you understand how at least one part really works, with numbers?"),
         ("Trade-offs", "Do you say what each choice costs and when you would choose differently?"),
         ("Failure thinking", "Do you ask what happens when this node, queue or region dies?"),
         ("Communication", "Can the interviewer follow you, and do you adapt when they push back?")]) + "</div>"
     + '<p class="sdnote">Sources: <a href="https://www.hellointerview.com/learn/courses/system-design/lesson/orientation/delivery" target="_blank" rel="noopener">Hello Interview delivery framework</a> and a <a href="https://handbook-hld.pages.dev/curriculum/interview-framework/frameworks-compared/" target="_blank" rel="noopener">comparison of common frameworks</a>. These are third-party summaries, not official company rubrics.</p>'),
    ("plan", "The 45 minutes, minute by minute", "The plan",
     PLAN_FIG + '<table class="sdtable"><thead><tr><th>Minutes</th><th>Stage</th><th>What you say and do</th></tr></thead><tbody>' + "".join(f"<tr><td>{a}</td><td><b>{b}</b></td><td>{md(c)}</td></tr>" for a, b, c in [
         ("0 to 5", "Clarify", "Ask 4 to 6 questions: users, features in and out of scope, scale, latency, consistency. Write the answers down."),
         ("5 to 10", "Numbers", "Only the estimates that decide something: requests per second, storage, bandwidth. State the conclusion: \"so one cache tier is enough\"."),
         ("10 to 15", "API and data", "The three or four endpoints and the main entities. Choose the shape of the store and say why."),
         ("15 to 30", "High-level design", "Draw the flows end to end: the write path, the read path. Name each component and what problem it solves."),
         ("30 to 40", "Deep dive and failure", "Pick the hardest part (or the one they point at) and go deep. Then: what breaks, how you would know, what you would do."),
         ("40 to 45", "Wrap up", "Summarise the decisions and trade-offs, what you would improve with more time, and how you would monitor it.")]) + "</tbody></table>"),
    ("say", "Say it like this", "Sentences that work",
     _paras(["Good answers sound the same in every interview because they follow the same moves. Keep these sentence starters in your head:"]) +
     '<div class="sdgrid">' + "".join(f'<div class="sdcard ok"><h3>{md(t)}</h3><p>{md(x)}</p></div>' for t, x in [
         ("Opening", "\"Before I draw anything, I would like to ask a few questions, then do a quick estimate, then sketch the design, then go deep on the hardest part. Is that a good use of the time?\""),
         ("Clarifying", "\"Do we need X? I will assume yes unless you say otherwise. How many users, and how fresh must the data be?\""),
         ("Estimating", "\"That is about 12,000 writes a second at peak. One database node handles a few thousand, so we need partitioning from day one.\""),
         ("Choosing", "\"I would use a cache-aside Redis here because reads are 100 times the writes and a few seconds of staleness is fine.\""),
         ("Trade-off", "\"The cost of this choice is more complex writes. I would accept that because ... If the requirement were strict consistency, I would instead ...\""),
         ("Failure", "\"If this node dies, clients retry on the replica within a few seconds, and we lose at most the last second of data because replication is asynchronous.\""),
         ("Being challenged", "\"That is a fair point. The constraint I was optimising for was latency. If cost matters more, I would change this part by ...\"")]) + "</div>"),
    ("mistakes", "The ten mistakes that cost the most", "Mistakes",
     '<div class="sdgrid">' + "".join(f'<div class="sdcard bad"><h3>{md(t)}</h3><p>{md(x)}</p></div>' for t, x in [
         ("Starting to draw at once", "Without requirements you design the wrong system. Ask first."),
         ("Technology name-dropping", "\"Use Kafka\" is not a reason. Say what problem it solves here and what it costs."),
         ("No numbers", "Boxes without numbers cannot be judged. Estimate, then let the numbers choose."),
         ("Estimating for 20 minutes", "Estimates serve the design. Take the number you need and move on."),
         ("A diagram with no flows", "Show how one request travels: the write path and the read path."),
         ("Equal time on every box", "Spend your time where the problem is hard."),
         ("Ignoring failure", "Every component dies. Say what happens and how you would notice."),
         ("Defending instead of exploring", "A challenge is information about their constraint. Ask what it is."),
         ("Premature scale", "Start simple, then show where and why it must grow."),
         ("Forgetting to summarise", "Finish with the decisions, the trade-offs and what you would do next.")]) + "</div>"),
    ("companies", "What the big companies are reported to emphasise", "Company styles",
     _paras(["Candidates and prep sites report patterns, and they are only patterns. Always prepare the fundamentals; use this table to choose which problems to practise first. These are third-party reports, not official statements from any company."]) +
     '<table class="sdtable"><thead><tr><th>Company style (reported)</th><th>Questions people report</th><th>Practise these pages</th></tr></thead><tbody>' + "".join(f"<tr><td><b>{a}</b></td><td>{md(b)}</td><td>{c}</td></tr>" for a, b, c in [
         ("Meta", "News feed, messaging (WhatsApp and Messenger style), photo sharing, notifications.", '<a href="news-feed.html">News feed</a>, <a href="chat.html">Chat</a>, <a href="notifications.html">Notifications</a>'),
         ("Google", "Search and autocomplete, maps and nearby, file storage, video; often asks architecturally similar problems rather than its own products.", '<a href="search-autocomplete.html">Search</a>, <a href="ride-hailing.html">Nearby search</a>, <a href="file-storage.html">File storage</a>, <a href="video-streaming.html">Video</a>'),
         ("Amazon", "E-commerce and warehouse style systems, rate limiting, recommendation; operational depth and Leadership Principles woven into the discussion.", '<a href="rate-limiter.html">Rate limiter</a>, <a href="booking-payments.html">Booking and payments</a>, <a href="08-reliability.html">Chapter 8</a>'),
         ("Microsoft", "More classic object-oriented design (parking lot, elevator, library) alongside distributed design; coverage is thinner.", "Low-level design (not yet in this course)"),
         ("Across companies", "URL shortener (the most reported), rate limiter, caches such as Redis or Memcached, key-value stores.", '<a href="url-shortener.html">URL shortener</a>, <a href="rate-limiter.html">Rate limiter</a>, <a href="03-caching.html">Chapter 3</a>')]) + "</tbody></table>"
     + '<p class="sdnote">Sources: <a href="https://prachub.com/resources/system-design-interview-questions-faang-2026" target="_blank" rel="noopener">FAANG question summary</a>, <a href="https://www.designgurus.io/blog/system-design-interviews-at-google-meta-amazon" target="_blank" rel="noopener">Design Gurus overview</a>. Rankings differ between sources; treat them as directional.</p>'),
    ("practice", "A four-week practice plan", "Practice",
     _paras(["Read a page, run its experiments, then **say the model answer aloud without looking**, timed. Reading is not practising; speaking is."]) +
     '<table class="sdtable"><thead><tr><th>Week</th><th>Focus</th><th>Do this</th></tr></thead><tbody>' + "".join(f"<tr><td><b>{a}</b></td><td>{md(b)}</td><td>{c}</td></tr>" for a, b, c in [
         ("1", "The building blocks", 'Chapters <a href="01-numbers.html">1</a> to <a href="05-scaling-data.html">5</a>. After each, explain the block to a friend in two minutes: what broke, what it does, what it costs.'),
         ("2", "Failure and operations", 'Chapters <a href="06-queues.html">6</a> to <a href="09-security.html">9</a>. For each, write three failure scenarios and what you would do.'),
         ("3", "Classic problems", 'Problems <a href="url-shortener.html">1</a> to <a href="chat.html">4</a> and <a href="search-autocomplete.html">8</a>. Time yourself: 45 minutes, whiteboard or paper, then compare with the page.'),
         ("4", "Harder problems and mocks", 'Problems <a href="video-streaming.html">5</a> to <a href="ride-hailing.html">7</a>, <a href="notifications.html">9</a>, <a href="booking-payments.html">10</a>. Do two full mock interviews with a friend, who should interrupt with the follow-ups listed on each page.')]) + "</tbody></table>"),
    ("check", "Are you ready? A self-check", "Checklist",
     ul(["I can turn \"a million users\" into requests per second and storage in under a minute.",
         "For each building block I can say what problem it solves, how it works and how it breaks.",
         "I always ask clarifying questions and write down the answers.",
         "I can draw the write path and the read path for any of the ten problems.",
         "I can state at least two trade-offs for every choice I make.",
         "I know what happens when each component fails, and how I would notice.",
         "I can explain a design clearly in two minutes and in forty-five."])),
]


def render(nav_prev, nav_next):
    from sd2 import _foot
    nav_items = [(sid, short) for sid, _t, short, _b in SECTIONS]
    nav = "".join(f'<a href="#{a}"><b>{i + 1}</b>{b}</a>' for i, (a, b) in enumerate(nav_items))
    body = [f'<header class="sdhero"><div class="eyebrow"><span class="tag">Part 3</span>The interview playbook</div><h1>{html.escape(TITLE)}</h1><p class="lead">{md(TAGLINE)}</p>'
            f'<div class="sdmeta"><span>about 20 minutes</span><span>{len(SECTIONS)} sections</span><span>a four-week plan</span></div></header>']
    for i, (sid, title, tag, inner) in enumerate(SECTIONS, 1):
        body.append(_sec(sid, i, title, tag, inner))
    body.append(_foot(nav_prev, nav_next))
    return _page(dict(slug=SLUG, title=TITLE, tagline=TAGLINE), nav, "\n".join(body), "The interview playbook")
