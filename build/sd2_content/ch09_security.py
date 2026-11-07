"""Chapter 9: Keep it safe (security for system design)."""
import sd2kit as k
from sd2 import scen

# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "10:05 a.m.", "kind": "warn",
     "scene": lambda cx, cy, w: k.person(cx, cy - 46, 1.1, "warn") + k.badge(cx, cy, "/invoices/1002", "warn") + k.note(cx, cy + 34, "Ben changes the last digit", "warn"),
     "caption": "A customer notices the invoice number in the web address and tries the next one."},
    {"title": "10:06 a.m.", "kind": "bad",
     "scene": lambda cx, cy, w: k.person(cx - 50, cy - 20, 1, "bad") + k.flow(cx - 30, cy - 20, cx + 20, cy - 20, "bad") + k.database(cx + 52, cy - 20, None, "bad") + k.badge(cx, cy + 34, "invoice of Ana", "bad"),
     "caption": "The server only checks that Ben is logged in. It does not check that the invoice is his."},
    {"title": "After the fix", "kind": "ok",
     "scene": lambda cx, cy, w: k.person(cx - 50, cy - 20, 1, "ok") + k.flow(cx - 30, cy - 20, cx + 20, cy - 20, "ok") + k.database(cx + 52, cy - 20, None, "ok") + k.badge(cx, cy + 34, "404 not found", "ok"),
     "caption": "Every lookup says whose it is. Someone else's invoice looks exactly like one that does not exist."},
], "ShopKart's invoice leak", "One missing check, and the fix is one line in the query.")

IDEA_FIG = k.figure(720, 262, [
    k.person(60, 80, 1.25), k.note(60, 130, "Customer"),
    k.flow(94, 80, 158, 80, "acc"),
    k.badge(200, 80, "1. Who are you?", "acc"),
    k.flow(246, 80, 304, 80, "acc"),
    k.badge(358, 80, "2. May you?", "warn"),
    k.flow(412, 80, 470, 80, "acc"),
    k.badge(530, 80, "3. Safe input?", "ok"),
    k.flow(590, 80, 640, 80, "acc"),
    k.database(680, 78, None, "ok"),
    k.note(200, 124, "authentication", "acc"), k.note(358, 124, "authorisation", "warn"), k.note(530, 124, "validation", "ok"),
    k.note(360, 170, "Around all three: encrypted wire (TLS), secrets kept out of code, data encrypted at rest.", ""),
    k.note(360, 196, "Each layer assumes the one before it can fail.", ""),
    k.badge(360, 232, "Defence in depth", "ok"),
], "Three questions on every request, with layers around them", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


HOW = [
    ("Check the owner, not only the login",
     "**Authentication** asks who you are. **Authorisation** asks what you may touch. The invoice bug is an **IDOR** (insecure direct object reference): the server trusts an id from the client. Put the owner in the query, so another customer's invoice is simply not found.",
     _small([k.person(50, 44, 1), k.flow(76, 44, 150, 44, "acc", "invoice 1001"), k.server(186, 44, "API"), k.flow(216, 44, 290, 44, "ok"),
             k.badge(420, 36, "WHERE id = 1001", "acc"), k.badge(420, 66, "AND owner = ben", "ok"), k.flow(520, 50, 570, 50, "ok"), k.database(600, 44, None, "ok")], "Scoped lookup", h=108)),
    ("Prove who you are, and store passwords safely",
     "Never store passwords. Store a **salted, slow hash** (Argon2id, scrypt or bcrypt): the salt makes equal passwords look different, and the slowness makes guessing expensive. After login, hand out a short-lived **token**. A signed **JWT** carries claims, but it is only encoded, not secret.",
     _small([k.badge(80, 44, "password + salt", "acc"), k.flow(150, 44, 230, 44, "acc", "slow hash"), k.badge(290, 44, "x91f...", "ok"), k.flow(330, 44, 400, 44, "acc", "login"),
             k.badge(470, 44, "token, 10 min", "ok"), k.note(580, 48, "signed, not secret", "warn")], "Hashing and tokens", h=96)),
    ("Encrypt the wire, and treat input as hostile",
     "**TLS** encrypts traffic and, if the client checks the certificate and name, proves the server is the real one. **mTLS** makes both sides show certificates, so internal services know who is calling. Pass user input to the database as **parameters**, never glued into the SQL text.",
     _small([k.server(60, 44, "orders", "acc"), k.flow(90, 44, 190, 44, "ok", "TLS, both sides"), k.server(226, 44, "payments", "acc"), k.badge(440, 36, "name = ?", "ok"), k.badge(440, 66, "value sent apart", "ok"), k.flow(520, 50, 570, 50, "ok"), k.database(600, 44, None, "ok")], "TLS and parameters", h=108)),
    ("Keep secrets out of code, and encrypt in layers",
     "Keys and passwords belong in a secrets manager, not in the repository: git remembers every old commit. With **envelope encryption**, a random data key encrypts the data and a master key encrypts that data key, so rotating the master key re-wraps one small key, not all the data.",
     _small([k.database(60, 44, "data", "ok"), k.badge(190, 36, "data key", "acc"), k.badge(190, 66, "locks the data", "acc"), k.flow(240, 44, 320, 44, "acc", "wrapped by"), k.badge(400, 44, "master key", "warn"), k.note(540, 40, "master key stays in a", "warn"), k.note(540, 56, "key service", "warn")], "Envelope encryption", h=104)),
]

DATA = dict(
    time="18 minutes",
    tagline="Security is not a feature you add at the end: it is a handful of habits on every request. Learn the few that stop most real breaches.",
    story=dict(
        title="Invoice 1002 belongs to someone else",
        paras=[
            "ShopKart lets customers download invoices at addresses like `/invoices/1001`. On a Thursday morning a customer, Ben, spots the number in the web address. Out of curiosity he changes it to 1002. An invoice opens: someone else's name, address and what they bought.",
            "He emails support, politely, and attaches a screenshot. The engineer who reads it checks the code in five minutes. The server confirms that the request has a valid login, then loads the invoice with that number. It never asks whose invoice it is. Anyone logged in could read all of them by counting upwards.",
            "No password was cracked and no server was hacked. The feature simply forgot one question. Most serious breaches look like this: **a missing check, not a clever exploit**. This chapter is the short list of checks to build in from the start, and how to explain them.",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: ask three questions, and expect each layer to fail",
        one="**Security** for a system designer means three questions on every request (who are you, may you do this, is this input safe) plus layers around them, so that when one layer fails the next still holds. This is called **defence in depth**.",
        figure=IDEA_FIG,
        paras=["Everything here is defensive. You are not learning to attack: you are learning which mistakes real breaches share, so you can design them out. Start with the cheap, high-impact habits: check ownership on every object, hash passwords properly, use TLS everywhere, use parameterised queries and keep secrets out of code."]),
    how=HOW,
    try_intro=["Three experiments on a safe, local practice setup. First: the invoice bug and its fix. Then: how fast weak password storage falls and what slow hashing costs an attacker. Then: how a token is built and why it must be checked carefully."],
    **{"try": [("sec", 3, 0, 0, "The invoice bug (IDOR) and its one-line fix"), ("sec", 0, 0, 0, "How fast weak password storage falls"), ("sec", 1, 0, 0, "A token built, and the checks that must not be skipped")]},
    breaks=[
        ("Trusting the id in the address", "Any endpoint that takes an object id must check that the caller may access that object. Fix: scope every query by owner or tenant, and return the same \"not found\" for missing and forbidden. Random ids help a little but are not the fix.", "bad"),
        ("Fast, unsalted password hashes", "In the recorded run an unsalted SHA-256 table of 20,000 guesses was built in 0.024 s and cracked 4 of 5 users. Fix: a salted slow hash (one scrypt check took 144 ms), plus multi-factor authentication for important accounts.", "bad"),
        ("Tokens accepted without full checks", "A token must be verified for signature, expiry, audience and the expected algorithm. In the recorded run a naive verifier accepted an unsigned token as an admin. Fix: pin the algorithm, keep expiry short, never put secrets in the payload.", ""),
        ("Switching certificate checks off", "Using `curl -k` or disabling verification \"just to make it work\" accepts any server. Fix: trust your own certificate authority properly, use mTLS between services, and alert well before certificates expire.", ""),
        ("User input glued into queries or pages", "Joining text into SQL lets input change the query (injection); printing it raw into a page can run script (XSS). Fix: parameterised queries, and encode output for the place it lands.", "bad"),
        ("Secrets in the repository", "Deleting a key from the latest commit leaves it in history. Fix: use a secrets manager, scan history, and if a real key leaks, rotate it at once.", ""),
    ],
    real=[
        dict(company="OWASP", text="The OWASP Top 10 lists **broken access control** as the first category of web application risk, and describes the same mistake as the invoice story: letting users act on records they should not reach.", url="https://owasp.org/Top10/A01_2021-Broken_Access_Control/", source="OWASP Top 10 (2021): A01 Broken Access Control"),
        dict(company="OWASP", text="The Password Storage Cheat Sheet recommends **Argon2id** as the first choice for hashing passwords, with scrypt and bcrypt as alternatives, each used with a unique salt and tuned costs.", url="https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html", source="OWASP Password Storage Cheat Sheet"),
        dict(company="AWS", text="The AWS Key Management Service documentation describes **envelope encryption**: encrypting data with a data key and protecting that data key with another key.", url="https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html", source="AWS KMS Developer Guide: Concepts"),
    ],
    interview=[dict(scenario=scen("sec", 3), who="A common security prompt: reported by candidates at large tech companies, not official."),
               dict(scenario=scen("sec", 0), who="A frequent question about leaks and passwords: reported by candidates, not official."),
               dict(scenario=scen("sec", 1), who="A senior prompt on tokens and multi-tenant APIs: reported by candidates, not official.")],
    interview_sub="Say your answer aloud first, then compare with the model answer. These are the shapes of question candidates report, not official lists.",
    recap=dict(
        points=["Authentication is who you are; authorisation is what you may touch. Check both on every request.",
                "An IDOR is a missing ownership check: scope every query by owner or tenant.",
                "Store a salted, slow hash of each password, never the password; add multi-factor for important accounts.",
                "A JWT is signed, not secret: verify signature, expiry, audience and algorithm, and keep it short-lived.",
                "Use TLS everywhere, mTLS between services, parameterised queries, and never turn verification off.",
                "Keep secrets out of git, encrypt data with a wrapped data key, and rotate on any leak."],
        quick=[("Why not just use random invoice ids?", "Random ids make guessing hard, but the real fix is the ownership check; ids leak through logs, links and emails."),
               ("What does a salt do?", "It makes equal passwords hash differently and forces an attacker to attack each hash on its own."),
               ("Why does envelope encryption help rotation?", "Rotating the master key re-wraps only the small data key, so the large data is not re-encrypted.")]),
    deeper=[("Passwords and multi-factor authentication", "S25_security_for_design.html#l1"), ("Sessions, tokens, JWT and OAuth", "S25_security_for_design.html#l2"), ("TLS and mTLS", "S25_security_for_design.html#l3"), ("Authorisation, IDOR and injection", "S25_security_for_design.html#l4"), ("Secrets and encryption", "S25_security_for_design.html#l5"), ("Rate limits for safe APIs", "S23_architecture_api_patterns.html#l3"), ("Reliable APIs and idempotency", "S23_architecture_api_patterns.html#l5")],
)
