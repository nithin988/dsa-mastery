"""Chapter 7: How a request travels (DNS, TCP, TLS, HTTP) and why it fails for one customer."""
import sd2kit as k
from sd2 import scen


def _box(x, y, w, h, title, sub, kind="acc"):
    return (f'<rect class="sd-sh {kind}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>'
            f'<text class="sd-l" x="{x + w / 2:g}" y="{y + 28}" text-anchor="middle">{title}</text>'
            f'<text class="sd-c" x="{x + w / 2:g}" y="{y + 48}" text-anchor="middle">{sub}</text>')


# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "2:14 a.m., your laptop", "kind": "ok",
     "scene": lambda cx, cy, w: k.person(cx - 56, cy - 6, 1.1, "ok") + k.server(cx + 50, cy, "ShopKart", "ok") + k.flow(cx - 32, cy - 4, cx + 18, cy - 4, "ok"),
     "caption": "You open the shop. It loads in under a second. The dashboard is green."},
    {"title": "2:14 a.m., Lagos", "kind": "bad",
     "scene": lambda cx, cy, w: k.phone(cx - 64, cy - 4, "Amara", "bad") + k.alert(cx + 6, cy - 6, None) + k.server(cx + 64, cy, "", "warn") + k.flow(cx - 42, cy - 4, cx - 18, cy - 4, "bad", dash=True),
     "caption": "Same shop, same minute. Her phone spins for a while and then gives up."},
    {"title": "2:51 a.m., found", "kind": "ok",
     "scene": lambda cx, cy, w: k.phone(cx - 64, cy - 4, "Amara", "ok") + k.server(cx + 58, cy, "new address", "ok") + k.flow(cx - 42, cy - 4, cx + 22, cy - 4, "ok") + k.badge(cx - 4, cy - 56, "old DNS answer", "warn"),
     "caption": "Her network was still using the old address, from before tonight's move."},
], "One customer cannot reach ShopKart", "The shop is up for you and down for her. The break is somewhere on the road between.")

IDEA_FIG = k.figure(720, 266, [
    k.person(44, 94, 1.2), k.note(44, 128, "Customer"),
    k.flow(64, 96, 104, 96, "acc"),
    _box(106, 60, 126, 72, "1. DNS", "name to address", "acc"), k.flow(232, 96, 254, 96, "acc"),
    _box(254, 60, 126, 72, "2. TCP", "open connection", "acc"), k.flow(380, 96, 402, 96, "acc"),
    _box(402, 60, 126, 72, "3. TLS", "secure + identity", "acc"), k.flow(528, 96, 550, 96, "acc"),
    _box(550, 60, 126, 72, "4. HTTP", "ask for the page", "acc"),
    k.badge(169, 160, "455 ms", "warn"), k.badge(317, 160, "75 ms"), k.badge(465, 160, "185 ms"), k.badge(613, 160, "69 ms"),
    k.note(169, 196, "stale address", "bad"), k.note(317, 196, "refused or timeout", "bad"), k.note(465, 196, "certificate error", "bad"), k.note(613, 196, "5xx or wrong page", "bad"),
    k.note(360, 230, "Times from one real recorded request to a public site; your own shop will differ.", ""),
    k.note(360, 254, "Test the trips in order. The first one that fails is your culprit.", "acc"),
], "A web request is four trips in a row", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


HOW = [
    ("Find the address (DNS)",
     "Browsers need a number, not a name. A **resolver** (usually run by your internet provider) asks the **DNS** system for the address behind `shopkart.example` and **remembers the answer for its time to live (TTL)**, in seconds. Until the TTL runs out it will not ask again, even if you have moved the shop.",
     _small([k.person(46, 44, 1.0), k.flow(70, 44, 190, 44, "acc", "name?"), k.cloud(226, 44, "resolver"), k.flow(262, 44, 390, 44, "ok", "address"),
             k.clock(430, 40, "TTL"), k.note(545, 44, "cached until TTL ends", "warn")], "DNS lookup and the TTL", h=104)),
    ("Open a connection (TCP)",
     "**TCP** opens a connection with a three step handshake: the client sends SYN, the server answers SYN-ACK, the client replies ACK. A **port** is a numbered door on the machine, such as 443 for secure web traffic. If nothing is behind the door you get an instant \"connection refused\"; if a firewall drops the packets you get silence and a timeout.",
     _small([k.person(40, 48, 0.95), k.flow(66, 24, 296, 24, "acc", "1. SYN"), k.flow(296, 48, 66, 48, "ok", "2. SYN-ACK"), k.flow(66, 72, 296, 72, "acc", "3. ACK"),
             k.server(330, 48, "server"), k.note(522, 40, "refused: instant", "bad"), k.note(522, 64, "dropped: timeout", "warn")], "TCP handshake", h=116)),
    ("Make it private and check who is there (TLS)",
     "**TLS** agrees secret keys, and the server shows a **certificate**: a signed ID card for its name. The client checks that the chain of signatures ends at a root it trusts, that the name matches, and that today's date is inside the validity window. If any check fails, the connection stops before a single byte of the page is sent.",
     _small([k.person(46, 52, 1.0), k.flow(70, 52, 262, 52, "acc", "hello, show your ID"), k.server(298, 52, "server"),
             k.note(452, 14, "the client checks three things", "acc"), k.badge(452, 34, "name matches", "ok"), k.badge(452, 62, "not expired", "ok"), k.badge(452, 90, "trusted issuer", "ok")], "TLS certificate checks", h=116)),
    ("Ask for the page (HTTP)",
     "Only now does the browser send `GET /product/42`. The server answers with a **status code**: 2xx worked, 3xx go somewhere else, 4xx you asked wrongly, 5xx we failed. Reusing the same connection skips the first three trips for the next request.",
     _small([k.person(40, 46, 0.95), k.flow(66, 34, 262, 34, "acc", "GET /product/42"), k.flow(262, 60, 66, 60, "ok", "200 OK + the page"), k.server(298, 46, "server"),
             k.badge(470, 22, "2xx worked", "ok"), k.badge(470, 50, "4xx you asked wrongly", "warn"), k.badge(470, 78, "5xx we failed", "bad")], "HTTP request and status codes", h=112)),
]

DATA = dict(
    time="20 minutes",
    tagline="A web request is four trips in a row: find the address, connect, secure, ask. Learn to test each trip on its own and a customer who cannot load the site becomes a ten minute problem.",
    story=dict(
        title="Wednesday, 2:14 a.m.",
        paras=[
            "ShopKart now has customers in four countries. At 2:14 a.m. the support inbox gets a message from Amara in Lagos: the site \"just spins\" on her phone, and has done for two hours. You open ShopKart on your laptop and it loads in under a second. You try again. Fine. The monitoring dashboard is green.",
            "Your tools say the shop is up, and one customer says it is not. Both are true. Between her phone and your server a request makes four separate trips. It looks up an address (**DNS**), opens a connection (**TCP**), agrees a secret (**TLS**) and finally asks for the page (**HTTP**). Your laptop passes all four. Hers fails at one of them.",
            "You do not guess. You walk the four trips in order, one command each. At 2:51 you find it. At 9 p.m. the team moved the shop to a new load balancer with a new address, and the old DNS answer had been set to be remembered for 24 hours. Amara's network still hands out the old address, where nobody answers.",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: four trips, tested in order",
        one="A web request is a relay of four trips: **DNS** finds the address, **TCP** opens a connection, **TLS** makes it private and proves who is at the other end, and **HTTP** asks for the page. Each trip fails in its own recognisable way, so the symptom tells you where to look.",
        figure=IDEA_FIG,
        paras=["A wrong or missing address points at DNS. \"Connection refused\" or a long hang points at TCP. A certificate warning points at TLS. A number such as 503 is an HTTP answer, which means the network itself worked. In the recorded request above, the address lookup alone took 0.455 s of a 0.795 s total, so the first trip is often the slowest."]),
    how=HOW,
    try_intro=["Four experiments. First, time the four trips on a real site. Then look at a real DNS answer, see what distance costs, and run the ladder you will use at 2 a.m."],
    **{"try": [
        ("nw", 0, 0, 0, "The four trips, timed on a real site",
         {"annot": [("0.455118 s", "DNS finished 0.455 s after the start. This is the whole address lookup."),
                    ("0.530521 s", "TCP connected. Subtract the line above: the handshake took 0.075 s, about one round trip to the server."),
                    ("0.715045 s", "TLS finished. The secure handshake added 0.185 s."),
                    ("0.783969 s", "First byte of the page. The server needed another 0.069 s to start answering."),
                    ("HTTP version:          2", "The same connection speaks HTTP/2, which can carry many requests at once.")],
          "e": ["A real request to a real site, timed at each trip. Notice which trip took longest.",
                "Each line is a running clock, not a duration, so subtract neighbours. DNS took 0.455 s, which is 57 percent of the 0.795 s total. TCP added 0.075 s, TLS added 0.185 s, and waiting for the first byte added 0.069 s."]}),
        ("nw", 3, 0, 0, "What a slow DNS answer looks like",
         {"annot": [("timed out", "Two tries to the resolver went unanswered. dig waited and tried again."),
                    ("Query time: 2183 msec", "The answer arrived after 2.2 seconds. Every customer behind a slow resolver pays this before anything else happens."),
                    ("142", "Seconds left in the resolver's memory for this record: the TTL counting down. When it reaches 0 the resolver asks again."),
                    ("ANSWER: 2", "Two addresses came back. Clients try them in turn.")],
          "e": ["Asking a resolver for an address. This run was slow: two tries timed out before the answer came.",
                "The number in the fourth column of each answer line is the remaining TTL. A resolver that cached this record 24 hours ago with a 24 hour TTL would keep giving the old address for up to a day, which is exactly what happened to Amara."]}),
        ("nw", 2, 0, 1, "Distance costs time on every trip"),
        ("nw", 8, 0, 0, "The ladder: DNS, then TCP, then HTTP, one command each"),
    ]},
    breaks=[
        ("Stale DNS after a move", "A resolver keeps the old address until the TTL ends, so some customers reach the old server for hours. Fix: lower the TTL a day before any move, and keep the old address answering until the old TTL has passed.", "bad"),
        ("A firewall that drops instead of refusing", "A closed port answers at once with \"refused\". A firewall that silently drops packets leaves the client waiting for a timeout. An instant error means nobody is listening; a long hang means something is dropping the traffic.", ""),
        ("An expired or mismatched certificate", "After the certificate's end date every client refuses the site, and a certificate for `www.shopkart.example` does not cover `shopkart.example` unless both names are listed. Fix: automate renewal and alert weeks before the date.", "bad"),
        ("Distance", "Each trip needs round trips, and a round trip to the far side of the world is slow. In the recorded model one megabyte needed 7 round trips plus a handshake: 1,600 ms at 200 ms per trip, against 80 ms at 10 ms. Fix: serve from nearby with a CDN, and reuse connections.", ""),
        ("Blaming the network for an HTTP answer", "A 503 from the load balancer looks like \"the network is down\" but it is a healthy network delivering a bad answer. Read the status code before you blame the road.", ""),
        ("Testing from the wrong place", "Your laptop has a warm DNS cache, a good route and a different resolver from your customer. Test from outside (a phone on mobile data, or a checking service) before you say \"it works for me\".", ""),
    ],
    real=[
        dict(company="IETF standard", text="The DNS specification defines each record's **TTL** as the time interval, in seconds, that the record may be cached before it should be discarded. That is why a changed address takes time to reach everyone.", url="https://www.rfc-editor.org/rfc/rfc1035", source="RFC 1035: Domain Names, Implementation and Specification"),
        dict(company="IETF standard", text="The current TCP specification describes the three way handshake that opens a connection and the reset that answers a connection to a port where nothing is listening.", url="https://www.rfc-editor.org/rfc/rfc9293", source="RFC 9293: Transmission Control Protocol"),
        dict(company="IETF standard", text="The TLS 1.3 specification describes how client and server agree on keys and how the server proves its identity with a certificate, so that traffic cannot be read or changed on the way.", url="https://www.rfc-editor.org/rfc/rfc8446", source="RFC 8446: TLS 1.3"),
    ],
    real_tag="Primary sources",
    real_title="Where this is written down",
    real_note="Summaries of the public standards; read the linked document for the exact wording.",
    interview=[dict(scenario=scen("nw", 8), who="A very common operations prompt: reported by candidates, not official."),
               dict(scenario=scen("nw", 3), who="A frequent follow-up to any DNS change: reported by candidates, not official."),
               dict(scenario=scen("nw", 5), who="A common incident prompt: reported by candidates, not official.")],
    interview_sub="Say your answer aloud first, then compare with the model answer. These are the shapes of question candidates report, not official lists.",
    recap=dict(
        points=["A request is four trips in a row: DNS, TCP, TLS, HTTP. Test them in that order.",
                "DNS answers are remembered for the TTL, so a change reaches people at different times.",
                "\"Refused\" is instant and means nobody is listening; a long hang means traffic is being dropped.",
                "A certificate must match the name, be in date and chain to a trusted root, or TLS stops the connection.",
                "An HTTP status code means the network worked: read it before blaming the road.",
                "Distance multiplies every round trip, so move content closer and reuse connections."],
        quick=[("A customer cannot load the site but you can. What is your first move?", "Test from outside your own network, then walk the ladder: DNS, TCP, TLS, HTTP, one command each. The first trip that fails is the culprit."),
               ("What is the difference between \"connection refused\" and a timeout?", "Refused is an instant reset: the machine answered but nothing listens on that port. A timeout is silence: packets are being dropped by a firewall or a bad route."),
               ("Why does a DNS change not reach everyone at once?", "Resolvers remember each answer for its TTL. Lower the TTL before the change and keep the old address answering until the old TTL has passed.")]),
    deeper=[("The whole journey of a URL", "S07_networking_for_engineers.html#l1"), ("TCP and UDP", "S07_networking_for_engineers.html#l3"), ("DNS", "S07_networking_for_engineers.html#l4"), ("HTTP", "S07_networking_for_engineers.html#l5"), ("TLS and certificates", "S07_networking_for_engineers.html#l6"), ("Debugging the network", "S07_networking_for_engineers.html#l9")],
)
