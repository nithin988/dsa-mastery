"""Systems Mastery S23: APIs and contracts (deep version, a real teaching API called with curl)."""
from sys_apis_a import LESSONS_A
from sys_apis_b import LESSONS_B, TAIL

MODULE = dict(
    id="api",
    deep=True,
    title="APIs and contracts: HTTP, pagination, rate limits and reliable interfaces",
    lead="An API is a promise that other people's code will rely on for years. This module runs a real teaching API and calls it with curl: verbs and status codes that mean something, pagination that stays fast at a million rows, a deprecation that warns before it breaks, rate limiting algorithms compared, REST versus gRPC versus GraphQL, idempotency keys that make retries safe, the 202 pattern for long work and webhooks you can trust.",
    time="9 to 11 hours",
    why=[
        "APIs are the seams of every system: between services, between a company and its customers, between a phone and a backend. A badly designed seam is expensive forever: you cannot take a field back once a thousand clients depend on it.",
        "Most API incidents are not exotic: a retried POST creates two orders, a client hammers the service because nothing told it to slow down, a renamed field breaks every mobile app, a list endpoint falls over at page 90,000. They are all preventable by design.",
        "In interviews \"design the API\" is part of nearly every problem. The weak answer lists endpoints. The strong answer gives resources and verbs by guarantee, status codes, pagination, versioning, rate limits, retry safety and what happens at the edges.",
    ],
    outcomes=[
        "Design resources, choose verbs by their guarantees, return status codes clients can act on, and use one error shape.",
        "Paginate with cursors, measure offset versus keyset, and evolve an API with additive changes and polite deprecation.",
        "Compare fixed window, sliding window and token bucket limiters, return 429 with Retry-After, and design distributed limiting.",
        "Choose between REST, gRPC and GraphQL by caller, and explain over-fetching, N+1 and BFFs.",
        "Make creates idempotent, long work asynchronous with 202 and job resources, and webhooks signed, retried and deduplicated.",
        "Answer API design interview questions with a complete, defensible design.",
    ],
    before=[
        "The networking module (S07) for HTTP, the caching module (S17) for ETags, and the queues module (S20) for the async patterns. Python 3 and curl run the experiments.",
        "Install nothing special: `python3` and `curl` are enough. The teaching API is one Python file created by the first command; it runs as an ordinary user on port 8301 and stops itself.",
        "Run the first lesson's commands in order: the rig is reused by every later lesson. Timings depend on your machine; the shapes match.",
    ],
    env=["The rig lives in `~/api`. Every command begins with `. ~/api/rig.sh; apiup` and ends with `apidown`."],
    lessons=LESSONS_A + LESSONS_B,
    labs=[
        dict(kind="linux", script="api-contract-read", dir="apiread", title="Read an API's responses and find the contract bugs",
             goal=["Read saved HTTP exchanges and decide which responses break good API practice, which retries are safe and which limit applies."],
             story=["A partner reports duplicate orders and a client that hammers your API. You are given a capture of the traffic: find what is wrong before changing any code."],
             tasks=["Read `traffic.txt` and `README.txt` in `~/sys-lab/apiread`.", "Find the request that created duplicate orders and the missing header that would have prevented it.", "Find the response that uses the wrong status for an error, and the client that ignored Retry-After.", "Write `key=value` lines into `~/sys-lab/answers-api.txt`."],
             check="Run the check script.", check_cmd="bash ~/sys-lab/check-api-contract-read.sh",
             hints=["Duplicate orders come from two POSTs with identical bodies and no `Idempotency-Key`.", "An error returned with status 200 hides failures from clients and monitoring.", "`Retry-After: 2` followed by a new request after 0 seconds means the client ignored it."],
             solution=["The two POSTs at 10:00:01 and 10:00:03 have no Idempotency-Key and created orders 41 and 42.", "The `GET /orders/999` returned 200 with an error in the body; it should be 404.", "client `app-31` sent three requests in the same second after `Retry-After: 2`."]),
    ],
    cases=[],
    cheat=TAIL["cheat"],
    interview_intro=TAIL["interview_intro"],
    interview=TAIL["interview"],
    selftest=TAIL["selftest"],
    recall=TAIL["recall"],
    sources=TAIL["sources"],
    plan=TAIL["plan"],
)
