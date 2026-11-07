"""Chapter 2: One server is not enough (load balancers and proxies)."""
import sd2kit as k
from sd2 import scen

# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "Normal day", "kind": "",
     "scene": lambda cx, cy, w: k.crowd(cx, cy - 52, 2, 34, .85) + k.scaled(k.server(cx, cy + 26, "web server", "ok"), cx, cy + 26, .95),
     "caption": "About 35 visitors a second. One server copes easily and nobody thinks about it."},
    {"title": "Launch, 12:05", "kind": "bad",
     "scene": lambda cx, cy, w: k.crowd(cx, cy - 52, 5, 24, .72, "bad") + k.scaled(k.server(cx - 36, cy + 26, None, "bad") + k.badge(cx + 40, cy + 20, "CPU 100%", "bad") + k.badge(cx + 40, cy + 50, "errors", "bad"), cx, cy + 26, .92),
     "caption": "The email lands: 260 requests a second hit a server that can answer 100. The queue grows and pages time out."},
    {"title": "A front door", "kind": "ok",
     "scene": lambda cx, cy, w: k.crowd(cx, cy - 52, 5, 24, .72, "ok") + k.scaled(k.balancer(cx - 70, cy + 26, None, "ok") + k.server(cx + 4, cy + 26, None, "ok") + k.server(cx + 52, cy + 26, None, "ok") + k.server(cx + 100, cy + 26, None, "ok")
                                                                          + k.flow(cx - 44, cy + 26, cx - 28, cy + 26, "ok"), cx, cy + 26, .7),
     "caption": "A balancer shares the 260 requests a second across four servers. Each does about 65."},
], "ShopKart's launch day, three moments", "The same shop on three days: a normal day, the launch spike, and the same spike with a front door.")

IDEA_FIG = k.figure(720, 290, [
    k.crowd(60, 124, 3, 22, .8), k.note(60, 170, "Customers"),
    k.flow(112, 130, 180, 130, "acc", "one address"),
    k.balancer(214, 130, "Balancer"),
    k.flow(240, 112, 388, 46, "ok"), k.flow(240, 122, 388, 106, "ok"), k.flow(240, 138, 388, 166, "ok"), k.flow(240, 148, 388, 226, "warn", dash=True),
    k.server(420, 44, None, "ok"), k.server(420, 104, None, "ok"), k.server(420, 164, None, "ok"), k.server(420, 224, None, "bad"),
    k.note(466, 48, "A: healthy", "ok", "start"), k.note(466, 108, "B: healthy", "ok", "start"), k.note(466, 168, "C: healthy", "ok", "start"), k.note(466, 228, "D: down, skipped", "bad", "start"),
    k.note(360, 276, "Customers see one address. The balancer sends each request to a healthy server.", ""),
], "A balancer in front of four servers, one of them down", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


HOW = [
    ("Put one front door in front of many servers",
     "Customers talk to **one address**. A **load balancer** receives every request and passes it to one of several identical servers behind it. Adding capacity then means adding a server, not buying a bigger one.",
     _small([k.person(50, 44, .95), k.flow(76, 44, 140, 44, "acc"), k.balancer(170, 44, "balancer"), k.flow(196, 30, 330, 20, "ok"), k.flow(196, 44, 330, 44, "ok"), k.flow(196, 58, 330, 68, "ok"),
             k.server(360, 20, None, "ok"), k.server(360, 66, None, "ok"), k.note(470, 24, "A and B look the same", "ok", "start"), k.note(470, 70, "add more to grow", "ok", "start")], "A balancer and identical servers", h=108)),
    ("Choose who gets the next request",
     "**Round robin** hands requests out in turn: A, B, C, A, B, C. **Least connections** gives the next request to the server with the fewest requests in progress, which copes better when some requests are slower. **Hashing** sends the same user to the same server each time.",
     _small([k.badge(100, 40, "round robin", "acc"), k.note(100, 76, "A, B, C, A, B, C"), k.badge(320, 40, "least connections", "acc"), k.note(320, 76, "the least busy one"),
             k.badge(545, 40, "hash of user", "acc"), k.note(545, 76, "same user, same server")], "Three ways to choose a server", h=96)),
    ("Check that servers are healthy",
     "The balancer **probes** every server every fraction of a second. A server that fails a couple of probes is taken out of the rotation, and put back once it passes again. Customers never see the dead server.",
     _small([k.balancer(70, 44, "balancer"), k.flow(98, 36, 220, 26, "ok", "probe"), k.flow(98, 52, 220, 62, "bad", "no answer", dash=True), k.server(250, 24, None, "ok"), k.server(250, 70, None, "bad"),
             k.badge(400, 24, "A: UP", "ok"), k.badge(400, 70, "B: DOWN", "bad"), k.note(530, 48, "traffic skips B", "ok")], "Health checks remove a dead server", h=112)),
    ("Keep the servers interchangeable",
     "If a server remembers your login or cart in its own memory, the balancer must always send you back to it. Instead keep that state in a **shared store** (a cache or the database), so any server can handle any request, and a server can disappear without anyone noticing.",
     _small([k.server(70, 24, None, "ok"), k.server(70, 74, None, "ok"), k.flow(100, 28, 214, 46, "acc"), k.flow(100, 70, 214, 54, "acc"), k.cache(250, 50, "shared store", "ok"),
             k.note(420, 38, "login and cart live here,", "ok", "start"), k.note(420, 58, "not in one server", "ok", "start")], "Shared state keeps servers interchangeable", h=112)),
]

DATA = dict(
    time="15 minutes",
    tagline="One server has a ceiling. A load balancer lets many servers share the work, survive a crash and be updated without anyone noticing, and it starts with one idea: customers see one address.",
    story=dict(
        title="Launch day, 12:05",
        paras=[
            "ShopKart launches at noon with an email to 200,000 subscribers. The founders did their napkin sums in chapter 1: about 35 requests a second on a normal day, and one server that can answer about 100 a second. They feel safe with the single server they bought.",
            "At 12:05 the traffic peaks at **260 requests a second**, two and a half times what the server can answer. Its CPU sits at 100%, requests queue up, pages that took 80 milliseconds now time out, and visitors see an error page. A founder refreshes the site on a phone and watches it fail, on the one day that matters most.",
            "By 12:30 they add a **load balancer** and three more servers. The same traffic now spreads across four machines, each handling about 65 requests a second, and the errors stop. That afternoon they also learn that a balancer is useful for more than speed: it hides a dead server, and it lets you update servers one at a time.",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: one address, many servers",
        one="A **load balancer** is a front door. It receives every request at one address and hands each one to a healthy server behind it, so capacity can grow by adding machines and one failure does not take the shop down.",
        figure=IDEA_FIG,
        paras=["This is called **horizontal scaling**: more machines, not a bigger machine. It works best when the servers are **stateless**, meaning any server can answer any request. Real systems use balancers like **nginx** and **HAProxy** (software you run yourself) or a cloud load balancer, and often put them at several layers."]),
    how=HOW,
    try_intro=["Four experiments with real nginx and HAProxy in front of three small test servers, A, B and C. First: how requests are shared out. Then: what happens when one server is slow. Then: how the balancer finds out that a server died. Last: changing the balancer's own settings without dropping a single request."],
    **{"try": [("lb", 0, 0, 2, "Round robin: who answers nine requests?"),
               ("lb", 1, 0, 1, "A slow server: round robin versus least connections"),
               ("lb", 2, 0, 1, "Kill a server and watch the health check"),
               ("lb", 2, 0, 2, "Reload the balancer's settings with no failed requests")]},
    breaks=[
        ("The balancer is a single point of failure", "One balancer in front of many servers just moves the weak spot. Run two, and share one address between them or use a cloud balancer that is already redundant.", "bad"),
        ("Not enough spare capacity", "ShopKart's four servers handle 260 requests a second at about 65 each. If one dies, the other three take 87 each, close to their limit of 100. Plan for one more server than you need.", "bad"),
        ("A shallow health check", "A check that only asks \"does the port answer?\" passes while the application cannot reach its database. Make the check test what the server really needs.", ""),
        ("Even by count is not even by load", "Round robin gave 20, 20, 20 even with a slow server C, so every third customer waited. Least connections gave C only 3 of 60. Pick the algorithm that fits how uneven your requests are.", ""),
        ("Sticky sessions and hot servers", "Sending each user to the same server fixes memory-based logins, but a few busy users can overload one server while others sit idle. Prefer shared state and keep stickiness as a last resort.", ""),
        ("Deploys that drop requests", "Restarting a server that is still serving traffic breaks requests in flight. Take it out of rotation, let it finish, update it, check it, put it back. The reload test above lost none of 120 requests.", "bad"),
    ],
    real=[
        dict(company="nginx", text="The official documentation for nginx's upstream module describes how to spread requests across a group of servers with round robin (the default), least connections and hashing, and how to mark servers as failed or down.", url="https://nginx.org/en/docs/http/ngx_http_upstream_module.html", source="nginx documentation: ngx_http_upstream_module"),
        dict(company="Google", text="Google's Maglev paper describes a software network load balancer that runs on ordinary servers, and a form of consistent hashing it uses so that connections keep reaching the same backend even when the pool changes.", url="https://research.google/pubs/maglev-a-fast-and-reliable-software-network-load-balancer/", source="Maglev: A Fast and Reliable Software Network Load Balancer (NSDI 2016)"),
        dict(company="HAProxy", text="The HAProxy documentation covers its health checks and balancing algorithms, which is the second engine used in the experiments above.", url="https://docs.haproxy.org/", source="HAProxy documentation"),
    ],
    interview=[dict(scenario=scen("lb", 0), who="A basic question reported by candidates at many companies, not official."),
               dict(scenario=scen("lb", 1), who="A common follow-up when you say \"I would add a load balancer\": reported by candidates, not official."),
               dict(scenario=scen("lb", 2), who="An operational question often reported for senior roles: reported by candidates, not official.")],
    interview_sub="Say your answer aloud first, then compare with the model answer. These are the shapes of question candidates report, not official lists.",
    recap=dict(
        points=["A load balancer gives customers one address and spreads requests over many identical servers.",
                "More servers (horizontal scaling) is how you grow, but only if servers are stateless.",
                "Round robin is even by count; least connections is even by load when requests differ.",
                "Health checks take a dead server out of rotation within a second or so, so customers see no errors.",
                "Reload or drain before you change anything: a graceful reload dropped none of 120 requests.",
                "The balancer itself needs a spare, and the servers need one spare server of capacity."],
        quick=[("What does a load balancer give you besides speed?", "Resilience (a dead server is skipped) and safe deploys (take servers out one at a time)."),
               ("When is least connections better than round robin?", "When requests take very different times, so equal counts would not mean equal load."),
               ("Why keep servers stateless?", "Any server can answer any request, so servers can be added, removed or fail without losing users' logins or carts.")]),
    deeper=[("Why a front door", "S16_load_balancers_proxies.html#l1"), ("Algorithms", "S16_load_balancers_proxies.html#l2"), ("Health checks and zero downtime deploys", "S16_load_balancers_proxies.html#l3"), ("Layer 4 versus layer 7", "S16_load_balancers_proxies.html#l4"), ("What else a proxy does", "S16_load_balancers_proxies.html#l5"), ("Reliable balancers and regions", "S16_load_balancers_proxies.html#l6"), ("Proxies and gateways in networking", "S07_networking_for_engineers.html#l8")],
)
