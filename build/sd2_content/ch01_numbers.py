"""Chapter 1: Think in numbers (the design method and estimation)."""
import sd2kit as k
from sd2 import scen

# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "Three weeks to launch", "kind": "",
     "scene": lambda cx, cy, w: k.badge(cx, cy - 46, "How many servers?", "acc") + k.person(cx - 46, cy + 14, 1.1) + k.person(cx + 46, cy + 14, 1.1, "warn") + k.note(cx - 46, cy + 50, "advisor") + k.note(cx + 46, cy + 50, "founder"),
     "caption": "An advisor asks the two founders a simple question. Nobody has an answer."},
    {"title": "The guess", "kind": "warn",
     "scene": lambda cx, cy, w: k.badge(cx, cy - 46, "\"One big one?\"", "warn") + k.person(cx - 44, cy + 14, 1.1, "warn") + k.server(cx + 44, cy + 10, "one server", "warn"),
     "caption": "The founder guesses. It sounds fine, but nothing backs it up."},
    {"title": "The napkin", "kind": "ok",
     "scene": lambda cx, cy, w: k.badge(cx, cy - 52, "35 per second on average", "ok") + k.badge(cx, cy - 22, "104 per second at peak", "ok") + k.scaled(k.server(cx - 34, cy + 34, None, "ok") + k.server(cx + 34, cy + 34, None, "ok"), cx, cy + 34, .75),
     "caption": "Two minutes of arithmetic turn the guess into a plan: at least two servers."},
], "ShopKart's launch question, three moments", "A guess is not a design. A few multiplications are.")

IDEA_FIG = k.figure(720, 280, [
    k.crowd(70, 50, 3, 26, .8), k.note(70, 96, "100,000 users a day"),
    k.flow(124, 52, 196, 52, "acc", "x 30 requests"),
    k.badge(250, 52, "3 million a day", "acc"),
    k.flow(310, 52, 376, 52, "acc", "÷ 86,400 s"),
    k.badge(430, 52, "35 per second", "acc"),
    k.flow(488, 52, 554, 52, "warn", "x 3 for peak"),
    k.badge(610, 52, "104 per second", "warn"),
    '<path class="sd-a warn" d="M610,66 V140" fill="none" marker-end="url(#dga)"/>',
    k.note(624, 108, "÷ 60 each", "warn", "start"),
    k.server(570, 176, None, "ok"), k.server(650, 176, None, "ok"),
    k.note(560, 226, "2 servers: 100 a second each, 60% busy", "ok"),
    k.note(190, 168, "Every step is one multiplication", ""), k.note(190, 188, "or one division.", ""),
    k.note(360, 262, "Say each assumption aloud. The answer matters less than the reasoning.", ""),
], "From users to requests per second to servers", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


HOW = [
    ("Start with what it must do, how well, and how big",
     "Write three short lists: **what** the system does (browse, buy, pay), **how well** (fast, always up, never loses an order), and **how big** (users, requests, data). Most bad designs answer a question nobody asked.",
     _small([k.badge(100, 40, "What it does", "acc"), k.note(100, 76, "browse, buy, pay"), k.badge(320, 40, "How well", "acc"), k.note(320, 76, "fast, up, safe"),
             k.badge(540, 40, "How big", "acc"), k.note(540, 76, "users, requests, data"),
             k.flow(166, 40, 250, 40, "acc"), k.flow(380, 40, 462, 40, "acc")], "Three lists of requirements", h=98)),
    ("Know a few numbers by heart",
     "Memory is fast, the network is slower, and crossing an ocean is slower still: the gaps are **a thousand times or more**. Knowing these gaps tells you why caches, copies near users and fewer network calls exist.",
     _small([k.badge(80, 40, "memory: 0.0001 ms", "ok"), k.flow(150, 40, 214, 40, "warn", "1,000s x"), k.badge(300, 40, "same data centre: 0.5 ms", "warn"),
             k.flow(398, 40, 458, 40, "bad", "300 x"), k.badge(560, 40, "across an ocean: 150 ms", "bad"),
             k.note(320, 88, "Rough orders of magnitude: exact values do not matter", "")], "Rough latency ladder", h=104)),
    ("Turn users into load and servers",
     "Requests per day divided by 86,400 seconds gives requests per second. Multiply by about 3 for the busiest hour, then divide by what one server can do (and keep it about 60% busy so there is room to spare).",
     _small([k.person(40, 44, .9), k.note(40, 78, "users"), k.flow(66, 44, 126, 44, "acc", "x 30"), k.badge(190, 44, "3M/day", "acc"), k.flow(236, 44, 296, 44, "acc", "÷ 86,400"),
             k.badge(352, 44, "35/s", "acc"), k.flow(386, 44, 440, 44, "warn", "x 3"), k.badge(492, 44, "104/s", "warn"), k.flow(528, 44, 576, 44, "ok"), k.server(606, 42, None, "ok")], "Users to load to servers", h=100)),
    ("Estimate storage, and say the trade-off",
     "Rows per day times bytes per row times days gives storage. Then state the choice you made and what it costs: \"One database is simple and cheap now, but I will need a copy for safety.\" Naming the price of a choice is what makes it a design.",
     _small([k.database(70, 40, "orders", "ok"), k.note(70, 96, "1.5 GB a year", "ok"), k.cloud(200, 40, "photos", "warn"), k.note(200, 96, "75 GB", "warn"),
             k.flow(270, 44, 350, 44, "acc", "so"), k.badge(450, 44, "photos are the big part", "acc"), k.note(520, 96, "choice: simple now, with a price later", "")], "Storage estimate and a trade-off", h=112)),
]

DATA = dict(
    time="15 minutes",
    tagline="Before you draw a single box, work out how big the thing will get. A few multiplications turn a guess into a plan, and they are the most useful skill in a design interview.",
    story=dict(
        title="Three weeks before launch",
        paras=[
            "ShopKart is two founders and a laptop. Launch is in three weeks. An advisor looks at the plan and asks one simple question: \"How many servers do you need for launch?\" There is a long silence. One founder says, \"One big one, I think?\" Nobody knows if that is right.",
            "The advisor takes a napkin. \"How many people will visit in a day?\" The founders hope for 100,000. \"How many clicks each?\" About 30. So 100,000 times 30 is **3 million requests a day**. A day has 86,400 seconds, so that is **35 requests a second** on average, and the busiest hour is roughly three times that: **about 104 a second**. If one server handles about 100 a second and you keep it 60% busy, you need two.",
            "The whole thing took two minutes, and it changed the conversation from opinion to numbers. But ShopKart still buys the single cheap server, because \"35 a second sounds small\". The napkin used an ordinary day. Launch day will not be ordinary, and chapter 2 shows what that costs.",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: estimate first, then design",
        one="A **back-of-envelope estimate** is quick arithmetic with rounded numbers that tells you the **size** of a problem, so you pick the right kind of design.",
        figure=IDEA_FIG,
        paras=["The result decides the design. 35 requests a second is a tiny system: one or two servers and one database. 35,000 a second is a different world, with many servers, caches and copies of the data. Interviews follow the same path: requirements, numbers, data, a first design, a deep dive, then trade-offs. Always state **assumptions** and **trade-offs** out loud, because that is the part the other person is grading."]),
    how=HOW,
    try_intro=["Four short experiments. First: how much slower is each kind of access, measured on a real machine. Then: the same arithmetic as the napkin, on a bigger system of 40 million users, to see load, storage and servers come out of simple multiplication."],
    **{"try": [("dm", 2, 0, 0, "How different are memory, disk and network speeds?"),
               ("dm", 3, 0, 0, "From users to requests per second"),
               ("dm", 3, 0, 1, "From messages to storage per year"),
               ("dm", 3, 0, 2, "From peak load to a number of servers")]},
    breaks=[
        ("Using the average, not the peak", "35 requests a second is the daily average, but real traffic arrives in waves. Size for the busiest hour (about 3 times the average) and for special events such as a launch or a sale.", "bad"),
        ("Hiding the assumptions", "\"We need 29 servers\" means nothing without \"I assumed 2,000 requests a second per server and 60% busy\". Say each assumption so the other person can fix it.", ""),
        ("False precision", "11,574 requests a second and \"about 10,000\" lead to the same design. Round early and keep the arithmetic easy to follow.", ""),
        ("Planning only for today", "Systems that are right today are wrong in a year. Leave room for 3 to 10 times growth, and say which part will break first.", "bad"),
        ("No trade-off named", "Every choice has a price: cheaper but slower, simpler but less safe. A design with no stated price sounds like a design nobody has thought about.", ""),
    ],
    real=[
        dict(company="Google (Peter Norvig)", text="Norvig's essay \"Teach Yourself Programming in Ten Years\" includes a short table of approximate timings, such as a main memory reference, a round trip inside one data centre and a packet crossing an ocean. It is a classic source for the \"numbers every engineer should know\" idea.", url="https://norvig.com/21-days.html", source="Peter Norvig: Teach Yourself Programming in Ten Years"),
        dict(company="Google (Jeff Dean)", text="Jeff Dean's talks on building large distributed systems have popularised a list of latency numbers every engineer should know and the habit of doing quick estimates before choosing a design.", url="https://www.cs.cornell.edu/projects/ladis2009/talks/dean-keynote-ladis2009.pdf", source="Jeff Dean: Designs, Lessons and Advice from Building Large Distributed Systems (LADIS 2009)"),
    ],
    interview=[
        dict(scenario=dict(
            title="\"Estimate the load and storage for a chat app with 40 million daily users.\"",
            ask="Give me requests per second, storage per year and a rough number of servers. Talk me through the arithmetic.",
            clarify=[
                ["What counts as a request: a message sent, or any call to the server?", "Pick one and say it. For this estimate, one message sent equals one request."],
                ["How many messages does a user send a day, and how big is a message?", "Assume 25 messages a day and about 150 bytes each. Say these are assumptions."],
                ["How long do we keep messages, and is there a launch or peak event?", "Assume we keep them for years; peak hour is about 3 times the average."],
            ],
            think=[
                ["Messages a day.", "40 million users times 25 messages is 1 billion messages a day."],
                ["Requests per second.", "1 billion divided by 86,400 is about 11,574 a second on average, and about 34,722 at peak (3 times)."],
                ["Storage.", "1 billion messages times 150 bytes times 365 days is about 54.8 TB a year, before copies and indexes."],
                ["Servers.", "If one server handles 2,000 requests a second and we keep it 60% busy, that is 1,200 each, so 34,722 divided by 1,200 is about 29 servers."],
                ["Sanity check and trade-off.", "29 servers and 55 TB a year is big but ordinary: it needs many servers and data spread over several databases, but not an exotic design."],
            ],
            answer=[
                "\"Let me state my assumptions: 40 million daily users, 25 messages each, about 150 bytes a message. That is 1 billion messages a day. Divided by 86,400 seconds, it is about 11,500 messages a second on average, and about 35,000 at the busiest hour if I use a factor of three.",
                "For storage, 1 billion messages times 150 bytes is 150 GB a day, about 55 TB a year before replicas. If a server handles 2,000 requests a second and I keep it 60% busy, I need about 29 servers at peak. So this needs many servers and the data split across machines, which I would plan for from the start. I would double check the 150 byte assumption first, because storage scales directly with it.\"",
            ],
            follow=[
                ["Why multiply by 3 for the peak?", "Traffic is not flat: evenings and events are busier than the daily average. 3 is a common rule of thumb; use your own data if you have it."],
                ["What would change if messages included photos?", "Storage jumps by orders of magnitude, since a photo is hundreds of KB against 150 bytes of text. Photos would go to cheap object storage and a CDN, not the main database."],
                ["How do you know your estimate is reasonable?", "Compare with known systems, check the units, and see whether the answer changes your design. If 10 times more or less would give the same design, the estimate is good enough."],
            ],
            slips=["Starting to draw boxes before knowing the size.", "Giving numbers with no assumptions behind them.", "Using the daily average instead of the peak.", "Mixing up bits and bytes, or MB and GB."]),
            who="The shape of estimation question candidates report at many large companies (chat, feed, storage): reported by candidates, not official."),
        dict(scenario=dict(
            title="\"Design a photo sharing app.\" (A vague question: where do you begin?)",
            ask="I have given you one line on purpose. Show me how you would start, before any design.",
            clarify=[
                ["Who are the users and what are the main actions?", "Upload a photo, see a feed, follow people. Say which three you will cover and which you leave out."],
                ["What matters most: speed, never losing a photo, or cost?", "Ask. Usually: never lose a photo, fast feed, cost second. This guides every later choice."],
                ["How big: users, uploads a day, photo size?", "If they do not say, offer an assumption and do the arithmetic."],
            ],
            think=[
                ["Do not draw yet.", "Spend the first minutes on requirements: what it does, how well, how big."],
                ["Estimate.", "For example 10 million daily users, 1 upload each at 2 MB is 20 TB a day: that tells you photos need object storage and a CDN, not the main database."],
                ["Name the first design and the likely trouble spot.", "Upload service, object storage, metadata database, feed. The trouble is storage cost and feed speed."],
                ["Flag trade-offs as you go.", "Fast uploads versus checking each photo, for example. Say which you chose and what it costs."],
            ],
            answer=[
                "\"I would start with requirements, not boxes. For this app I would cover uploading a photo, following people and viewing a feed, and leave comments and messages out for now. The quality that matters most is never losing a photo, then a fast feed.",
                "Then a quick estimate: if 10 million people upload one 2 MB photo a day, that is about 20 TB a day, so photos go to cheap object storage behind a CDN, and only small records go in the database. With that size in mind I can draw the upload path and the feed, and I will say the price of each choice as I go.\"",
            ],
            follow=[
                ["Why ask questions before designing?", "The right design depends on size and priorities. A design for 1,000 users is wrong for 100 million and costs time to build."],
                ["What if the interviewer will not give numbers?", "Offer your own, say they are assumptions, and ask if they are close enough. That shows the skill."],
            ],
            slips=["Jumping straight to databases and load balancers.", "Asking too many questions and never designing.", "Never saying what the numbers imply for the design."]),
            who="A very common opening move in system design interviews: reported by candidates, not official."),
        dict(scenario=dict(
            title="\"What trade-off did you make there, and why?\"",
            ask="You picked an option. Tell me what you gave up. They are testing whether you know every choice has a price.",
            clarify=[
                ["Which choice are they asking about?", "Name it clearly first: for example one database instead of many, or a cache instead of fresh reads."],
                ["What does the product need most?", "The trade-off only makes sense against a goal: speed, safety, cost or simplicity."],
            ],
            think=[
                ["Say what you chose and what you gain.", "For example: one database is simple and cheap to run."],
                ["Say what you give up.", "It is a single point of failure and has a ceiling on size and writes."],
                ["Say when you would change your mind.", "When writes pass what one machine handles, or when downtime costs more than the extra copy."],
            ],
            answer=[
                "\"I chose a single database with one copy for backup. The gain is that it is simple, cheap and easy to reason about. The price is that it is a single point of failure, with a ceiling on how much it can handle.",
                "At today's size, about a hundred requests a second and a few gigabytes, that price is fine. I would change my mind when traffic or data grows a lot, or when an hour of downtime costs more than running a second copy.\"",
            ],
            follow=[
                ["How would you know when to change?", "Watch numbers: database CPU, write rate, storage, and the time to recover from a failure. Set a threshold in advance."],
                ["Is there ever a choice with no trade-off?", "Rarely. If you cannot find the price, you have not looked closely enough."],
            ],
            slips=["Presenting a choice as obviously best.", "Listing downsides but never saying when they matter.", "Not tying the trade-off to the goals of the product."]),
            who="A behavioural style follow-up reported by candidates, not official."),
    ],
    interview_sub="Say your answer aloud first, then compare with the model answer. These are the shapes of question candidates report, not official lists.",
    recap=dict(
        points=["Estimate before you design: the size of the problem decides the shape of the solution.",
                "Requirements come first: what it does, how well, how big.",
                "Know the gaps: memory, the network in one data centre and across an ocean differ by orders of magnitude.",
                "Users per day times actions, divided by 86,400, gives the average per second; multiply by about 3 for the peak.",
                "Storage is rows times bytes times days; divide peak load by one server's share (at about 60% busy) for servers.",
                "State assumptions and the price of each choice out loud."],
        quick=[("How many requests a second is 3 million requests a day?", "About 35 (3,000,000 divided by 86,400)."),
               ("Why design for the peak and not the average?", "Traffic comes in waves and events; a system sized for the average fails exactly when the most customers arrive."),
               ("Why keep a server only about 60% busy?", "It leaves room for spikes, failures and slow requests; at 100% busy, queues build and everything gets slow.")]),
    deeper=[("The six steps of a design discussion", "S15_design_method_estimation.html#l1"), ("Requirements", "S15_design_method_estimation.html#l2"), ("Numbers every engineer should know", "S15_design_method_estimation.html#l3"), ("Back of envelope: users to QPS, storage and servers", "S15_design_method_estimation.html#l4"), ("Trade-offs and how to talk about them", "S15_design_method_estimation.html#l5")],
)
