"""Problem 2: Design a rate limiter."""
import sd2kit as k
from sd2 import scen

STRIP = k.strip([
    {"title": "A partner script", "kind": "warn",
     "scene": lambda cx, cy, w: k.server(cx, cy - 10, "partner script", "warn") + k.badge(cx, cy + 50, "2,000 requests/s", "warn"),
     "caption": "A partner's loop has a bug and calls the ShopKart API as fast as it can."},
    {"title": "Everyone suffers", "kind": "bad",
     "scene": lambda cx, cy, w: k.crowd(cx, cy - 52, 4, 26, .72, "bad") + k.scaled(k.server(cx, cy + 22, "API", "bad") + k.badge(cx, cy + 82, "timeouts", "bad"), cx, cy + 22, .9),
     "caption": "The API is saturated. Ordinary customers, who send 2 requests a second, get errors."},
    {"title": "With a limiter", "kind": "ok",
     "scene": lambda cx, cy, w: k.server(cx - 50, cy - 10, None, "warn") + k.flow(cx - 20, cy - 10, cx + 20, cy - 10, "bad") + k.badge(cx + 66, cy - 10, "429", "bad") + k.crowd(cx, cy + 42, 4, 26, .72, "ok"),
     "caption": "The script is told to slow down. Everyone else carries on as normal."},
], "One noisy client and a fair shop", "A rate limiter is a doorman: each client gets a fair share, and the rest wait.")


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


DESIGN_FIG = k.figure(720, 270, [
    k.crowd(60, 70, 3, 26, .8), k.note(60, 120, "Clients"),
    k.flow(110, 70, 170, 70, "acc"),
    k.balancer(200, 70, "Gateway", "acc"),
    k.flow(226, 70, 290, 70, "acc", "1. check"),
    k.cache(330, 70, "Redis shards", "warn", "token buckets"),
    k.flow(356, 70, 420, 70, "ok", "2. allow"),
    k.server(460, 70, "API servers", "ok"),
    k.flow(488, 70, 560, 70, "ok"),
    k.database(600, 68, "data", "ok"),
    '<path class="sd-a bad" d="M200,96 V170" fill="none" marker-end="url(#dga)"/>',
    k.badge(200, 190, "429 + Retry-After", "bad"),
    k.note(330, 150, "one atomic script per check", "warn"),
    k.note(460, 150, "never sees the excess", "ok"),
    k.note(360, 232, "The gateway asks Redis before the request reaches the application.", ""),
    k.note(360, 254, "If the limiter is down, allow with a small local limit (fail open) and alert.", ""),
], "A rate limiter at the gateway with sharded Redis counters", None)

DATA = dict(
    time="25 minutes",
    seen_at="A staple of API and infrastructure interviews",
    tagline="The algorithm fits on one slide. The interview is about doing it correctly across a fleet of servers, at a million checks a second, without the limiter becoming the outage.",
    story=dict(
        title="The partner whose loop never stopped",
        paras=[
            "ShopKart has a public API used by partner shops. One afternoon a partner deploys a script with a bug: it retries immediately in a loop and sends about 2,000 requests a second. A normal customer sends two. The API servers saturate, and every other customer sees timeouts.",
            "Nobody attacked ShopKart, and the partner is apologetic. But it shows a gap: **one client can consume everyone's capacity**. The team wants a rule: each client gets a fair share, short bursts are fine, and anything beyond that is told, politely and clearly, to wait. That rule is a rate limiter.",
        ],
        strip=STRIP),
    requirements=["Functional: limit requests per client (and per endpoint class), allow short bursts, answer rejected calls with `429 Too Many Requests` and a `Retry-After` header. Non-functional: adds only a few milliseconds to a request, works across many servers, survives its own failure, and is easy to explain to customers (clear limits, visible usage)."],
    numbers=[
        ("Fleet traffic", "The prompt assumes about **1 million requests per second** across all API servers. Every one needs a limit check."),
        ("Cost of one check", "A single Redis node handles on the order of **100,000 such checks a second** (the order of magnitude used in the model answer below). So 1,000,000 / 100,000 = about **10 shards**, and a dozen leaves headroom."),
        ("State per key", "A token bucket stores two numbers: tokens left and the last refill time. As an estimate, assume about 100 bytes per key with overhead: **one million active keys is roughly 100 MB**. Memory is not the problem; the request rate is."),
        ("Latency budget", "The check must cost a few milliseconds at most (assumption: a 5 ms timeout). A limiter slower than the thing it protects is a bug."),
        ("The rule itself", "Example plan: 10 requests per second with a burst of 10, per customer and endpoint class. Bursts are allowed, but the average cannot exceed the rate."),
    ],
    design_figure=DESIGN_FIG,
    design=[
        ("Choose the key and the rule", "Limit per authenticated customer and endpoint class (for example `cust:42:search`), with a global limit as a safety net. Use the IP address only as a coarse backstop for anonymous traffic, since many people share one IP.",
         _small([k.person(60, 44, 1), k.flow(86, 44, 170, 44, "acc", "API key"), k.badge(280, 44, "cust:42:search", "acc"), k.flow(370, 44, 430, 44, "acc"), k.badge(520, 44, "10/s, burst 10", "ok")], "The key and the rule", h=92)),
        ("A token bucket: refill, then take one", "A bucket holds up to 10 tokens and gains 10 a second. Each request takes one token; with none left, the request is rejected. An idle client saves up a burst, and the average never exceeds the refill rate.",
         _small([k.badge(80, 44, "bucket: 10 tokens", "ok"), k.flow(150, 44, 220, 44, "ok", "take 1"), k.badge(290, 44, "9 left", "ok"), k.flow(330, 44, 400, 44, "warn", "..."), k.badge(450, 44, "0 left", "bad"), k.flow(490, 44, 540, 44, "bad"), k.badge(590, 44, "429", "bad")], "Token bucket", h=92)),
        ("One atomic script in Redis", "The buckets live in Redis, spread over shards by hashing the key. Each check runs as a single Lua script that refills, takes a token and writes back, so no other request can slip in between the read and the write.",
         _small([k.server(60, 44, "gateway 1", "acc"), k.server(60, 90, None, "acc"), k.flow(90, 44, 180, 56, "acc", "script"), k.cache(220, 56, "Redis", "warn"), k.flow(250, 56, 330, 56, "ok", "allow or deny"), k.badge(430, 56, "refill, take, save: one step", "ok")], "Atomic check", h=124)),
        ("Say no clearly, and fail safely", "Rejected calls get `429` with `Retry-After` and rate-limit headers, so good clients can back off. If Redis is slow or down, **fail open** with a conservative local limit and an alert, rather than blocking all customers.",
         _small([k.cache(60, 44, "Redis down", "bad"), k.flow(90, 44, 190, 44, "warn", "timeout 5 ms"), k.badge(280, 44, "local limit", "warn"), k.flow(340, 44, 400, 44, "ok"), k.badge(480, 44, "requests keep flowing", "ok"), k.note(580, 80, "alert fires", "bad")], "Failing open", h=100)),
    ],
    hard_title="The hard part: counting correctly when many servers check at once",
    hard_paras=[
        "There are two real decisions. **Which algorithm**: a fixed window is cheap but lets a client send a double burst across the boundary (10 at the end of one second, 10 at the start of the next). A sliding window log is exact but stores every request. A token bucket allows a bounded burst and an average rate with two numbers per key, which is why it is the usual choice.",
        "**How to count across servers**: if each server reads a counter, decides, then writes it back, two servers can read the same value and both admit the request. Under load that over-admits badly. The fix is to make read, refill, take and write one atomic step inside Redis. The two experiments below show both problems with real numbers.",
    ],
    **{"try": [("api", 2, 0, 0, "Three algorithms facing the same burst"), ("dw", 4, 0, 1, "A race you can see: naive check versus atomic script"), ("api", 2, 0, 1, "A real 429 with Retry-After")]},
    scale=[
        ("A million checks a second", "Shard Redis by key with consistent hashing (about 10 to 12 shards at 100,000 checks a second each). Add local buckets in each gateway that borrow a small batch of tokens, trading a bounded inaccuracy for far fewer round trips.", ""),
        ("One hot customer", "A single key lives on one shard. Split a very large customer's bucket into several sub-buckets on different shards, each with a share of the limit.", ""),
        ("Redis is down or slow", "Fail open with a conservative local limit and an alert, and keep a short timeout so the limiter never costs more than it saves. Some products (login, payments) may prefer fail closed: say which and why.", "bad"),
        ("Retry storms", "When everyone is rejected, everyone retries together. Send `Retry-After`, ask clients for jittered exponential backoff, and shed load on the server side as a second defence.", "bad"),
        ("Fairness and explanation", "Customers accept limits they can see. Publish the limits, return remaining-quota headers, and give a dashboard of 429s per customer and top consumers.", "ok"),
    ],
    scenario=scen("dw", 4),
    who="A very commonly reported question, especially for API and platform roles: reported by candidates, not official.",
    real=[
        dict(company="Stripe", text="Stripe has written about running **four kinds of limiters** (request rate, concurrent requests, and two load shedders that protect the fleet) and about using a token bucket for the request rate limiter, with Redis holding the counters.", url="https://stripe.com/blog/rate-limiters", source="Stripe Blog: Scaling your API with rate limiters"),
        dict(company="IETF", text="RFC 6585 defines the **429 Too Many Requests** status code and says the response may include a `Retry-After` header telling the client when to try again.", url="https://www.rfc-editor.org/rfc/rfc6585", source="RFC 6585: Additional HTTP Status Codes"),
        dict(company="Redis", text="The Redis documentation describes running **Lua scripts** with `EVAL`, which execute atomically on the server: the property a limiter needs for its check-and-update.", url="https://redis.io/docs/latest/commands/eval/", source="Redis documentation: EVAL"),
    ],
    recap=dict(
        points=["A rate limiter gives each client a fair share so one noisy client cannot starve the rest.",
                "Token bucket: refill at a steady rate, take one token per request, allow a bounded burst.",
                "Fixed windows allow a double burst at the boundary; the recorded run admitted up to 20 in one second against a limit of 10.",
                "Check and update must be atomic: the recorded naive check admitted 60 requests against a limit of 10; the Lua script admitted exactly 10.",
                "Scale with sharded Redis and local token batches; split hot keys.",
                "Return `429` with `Retry-After`, and decide fail open or fail closed before the interviewer asks."],
        quick=[("Why not a fixed window counter?", "A client can send a full limit at the end of one window and again at the start of the next, doubling the burst."),
               ("Why a Lua script instead of GET then SET?", "The script is atomic. With GET then SET, concurrent clients read the same value and over-admit."),
               ("What should the limiter do when Redis is down?", "Usually fail open with a conservative local limit and an alert; protect critical flows like login separately.")]),
    deeper=[("Distributed rate limiter, full lesson", "S27_design_warmups.html#l5"), ("Rate limiting and quotas in APIs", "S23_architecture_api_patterns.html#l3"), ("Reliable APIs and idempotency", "S23_architecture_api_patterns.html#l5"), ("Overload and load shedding", "S26_designing_for_reliability.html#l5")],
)
