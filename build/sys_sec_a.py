"""S25 security for system design: part A (lessons 1 to 3: passwords and MFA, tokens and OAuth, TLS and mTLS)."""
import sysviz as v

OAUTH_SEQ = v.seq(
    ["User", "App", "Auth server", "API"],
    [("a->b", 0, 1, "click 'Sign in with ...'"),
     ("a->b", 1, 2, "redirect: client_id, scope, state, code_challenge"),
     ("a->b", 0, 2, "log in and approve the scopes (the app never sees the password)"),
     ("a->b", 2, 1, "redirect back with a one-time authorisation code", "reply"),
     ("a->b", 1, 2, "exchange code + code_verifier for tokens (server to server)"),
     ("a->b", 2, 1, "access token (short) + refresh token", "reply"),
     ("a->b", 1, 3, "GET /orders  Authorization: Bearer <access token>"),
     ("a->b", 3, 1, "200 (the API checks signature, expiry, audience, scope)", "reply")],
    "OAuth 2.0 authorization code flow with PKCE", "The app gets a limited, short-lived token instead of the user's password")

TLS_VIZ = v.figure(
    720, 232,
    [v.box(10, 20, 150, 56, "ClientHello", "ink", "versions, ciphers, key share"),
     v.arrow(160, 48, 200, 48), v.box(200, 20, 200, 56, "ServerHello + certificate", "acc", "its key share, a certificate chain"),
     v.arrow(400, 48, 440, 48), v.box(440, 20, 270, 56, "Client verifies the certificate", "warn", "chain to a trusted CA, name matches, not expired"),
     v.box(10, 110, 340, 56, "Both derive the same session keys", "ok", "from the key exchange: nobody sent the key itself"),
     v.box(380, 110, 330, 56, "Encrypted, authenticated application data", "ok", "tampering is detected; eavesdroppers see noise"),
     v.text(360, 204, "mTLS adds one step: the server also asks the client for a certificate, so both sides prove who they are.", "dg-s")],
    "The TLS handshake in one picture", "Authenticate the server, agree keys, then protect everything that follows")

LESSONS_A = [
    dict(
        title="Passwords and multi-factor authentication: what \"secure\" really costs",
        tier="hot",
        situation="Your user table leaks. Whether that is an embarrassing afternoon or a headline depends entirely on one design decision made years ago: how the passwords were stored. A second decision, whether a stolen password is enough to log in, decides the rest.",
        learn=["Why fast hashes are the wrong tool for passwords", "Salts, and what they defeat", "Slow, memory-hard hashes (scrypt, bcrypt, Argon2)", "One-time codes (TOTP) and how they work"],
        model=[
            "Never store passwords, store a **hash**: a one-way function of the password; at login hash what was typed and compare. But a hash such as SHA-256 is designed to be **fast**, so an attacker with a stolen table can try **billions of guesses a second** and recover every weak password. Without a **salt** (a random value stored with each hash and mixed in) identical passwords produce identical hashes (one cracked hash reveals every user with that password) and precomputed tables work. The right tool is a deliberately **slow, memory-hard password hash** (**Argon2id**, **scrypt** or **bcrypt**) with a per-user salt, tuned so that one verification takes tens to hundreds of milliseconds: negligible for a login, ruinous for an attacker trying millions of guesses. Also: throttle login attempts, check new passwords against lists of breached ones, and compare in **constant time**.",
            "Passwords alone are not enough, so add a **second factor**: **TOTP** (the six-digit codes from an authenticator app) computes `HMAC(shared secret, current 30-second counter)` and takes six digits of it, so server and phone agree without talking; **WebAuthn/passkeys** use public-key cryptography bound to the website's origin, which also defeats phishing. SMS codes are better than nothing but can be intercepted or SIM-swapped. For recovery, use a process that is no weaker than the login (otherwise attackers will use it). Design the whole lifecycle: sign-up, login, reset, device trust, lockout and alerting.",
        ],
        analogy="A fast hash is a lock that anyone can try a million keys on per second. A slow, salted hash is a lock that takes a second per attempt and is different for every door: the thief with a bag of stolen locks gets nowhere in a lifetime. A second factor is the second key that is on your phone, not in the stolen bag.",
        sim=None,
        walk=[
            ("Receive the password over TLS only", "Never log it, never email it back."),
            ("Generate a random salt per user", "Stored next to the hash; it need not be secret."),
            ("Hash with a slow, memory-hard function", "Argon2id or scrypt or bcrypt, with parameters tuned to about 100 ms."),
            ("Compare in constant time and throttle", "Rate limit by account and by source; alert on spikes."),
            ("Add a second factor and a safe recovery path", "TOTP or passkeys; recovery codes; no weaker back door."),
        ],
        groups=[
            dict(title="How fast hashes fall, and what salting and slow hashing change", cmds=[
                dict(volatile=True, c=r'''mkdir -p ~/sec && cd ~/sec && python3 - <<'EOF'
import hashlib, os, random, time
rng = random.Random(1)
words = ['pass', 'word', 'love', 'admin', 'welcome', 'qwerty', 'dragon', 'monkey', 'letmein', 'sunshine']
dictionary = sorted({w + (str(n) if n else '') for w in words for n in range(2000)})          # 20,000 likely passwords
print('an attacker\'s guess list: %d candidate passwords' % len(dictionary))
users = {'ana': 'dragon1987', 'ben': 'welcome77', 'cho': 'qwerty', 'dev': 'monkey1999', 'eli': 'Tr0ub4dor&3x!long-and-unique'}
# 1. stored as plain SHA-256, no salt
table = {u: hashlib.sha256(p.encode()).hexdigest() for u, p in users.items()}
lookup = {}; t = time.perf_counter()
for guess in dictionary: lookup[hashlib.sha256(guess.encode()).hexdigest()] = guess
build = time.perf_counter() - t
cracked = {u: lookup[h] for u, h in table.items() if h in lookup}
print('unsalted SHA-256: built a table of %d hashes in %.3f s and cracked %d of %d users: %s' % (len(lookup), build, len(cracked), len(users), sorted(cracked)))
# 2. identical passwords reveal each other without a salt
same = {u: hashlib.sha256(b'welcome77').hexdigest() for u in ('x', 'y')}
print('two users with the same password, no salt: hashes equal? %s' % (same['x'] == same['y']))
salted = {u: (s, hashlib.sha256(s + b'welcome77').hexdigest()) for u, s in (('x', os.urandom(8)), ('y', os.urandom(8)))}
print('two users with the same password, salted:  hashes equal? %s' % (salted['x'][1] == salted['y'][1]))
# 3. a slow, memory-hard hash (scrypt), per-user salt
salt = os.urandom(16)
t = time.perf_counter(); hashlib.scrypt(b'welcome77', salt=salt, n=2**14, r=8, p=1); one = time.perf_counter() - t
print('scrypt (n=2^14): one verification takes %.0f ms; trying the same %d guesses would take %.0f minutes per stolen hash on this CPU core' % (one * 1000, len(dictionary), one * len(dictionary) / 60))
EOF''',
                     e="Three experiments in one. With **unsalted SHA-256** the attacker hashes a list of likely passwords once (a few hundredths of a second for 20,000) and then looks up every stolen hash: four of the five users fall instantly; only the long, unique password survives. Next, without salts two users with the same password have **identical hashes**, a free hint to the attacker; with salts they differ. Finally **scrypt** makes each guess cost tens of milliseconds and a lot of memory, so even this tiny dictionary would take **minutes per stolen hash**, and real attackers' lists have billions of entries. (Attackers use GPUs that are far faster than this CPU core; the principle, making each guess expensive, is why password hashes are slow on purpose.)",
                     annot=[("an attacker's guess list: 20000 candidate passwords", "a small dictionary of likely passwords"),
                            ("unsalted SHA-256: built a table of 20000 hashes in 0.014 s and cracked 4 of 5 users", "fast hashing and no salt: one table cracks every weak password at once; only the long unique password survives"),
                            ("same password, no salt: hashes equal? True / salted: False", "salts stop one cracked hash from revealing other users"),
                            ("scrypt (n=2^14): one verification takes 99 ms; ... 33 minutes per stolen hash", "slowness is the defence: negligible for one login, ruinous for millions of guesses")]),
                dict(c=r'''cd ~/sec && python3 - <<'EOF'
# TOTP (RFC 6238) in a few lines: HMAC-SHA1 over a 30-second counter, then "dynamic truncation" to digits.
import hmac, hashlib, struct, time
def totp(secret, t, digits=6, step=30):
    counter = struct.pack('>Q', int(t // step))
    h = hmac.new(secret, counter, hashlib.sha1).digest()
    off = h[-1] & 0x0F
    code = (struct.unpack('>I', h[off:off + 4])[0] & 0x7FFFFFFF) % 10 ** digits
    return str(code).zfill(digits)
secret = b'12345678901234567890'                   # the official test secret from RFC 6238
print('RFC 6238 test vector, time 59 s, 8 digits:  %s   (the RFC says 94287082)' % totp(secret, 59, 8))
print('RFC 6238 test vector, time 1111111109 s:    %s   (the RFC says 07081804)' % totp(secret, 1111111109, 8))
now = 1_800_000_000
print('code at t=now:       ', totp(secret, now))
print('code 15 s later:     ', totp(secret, now + 15), ' (same 30-second window: same code)')
print('code 31 s later:     ', totp(secret, now + 31), ' (next window: a new code)')
print('servers accept the previous and next window too, to forgive small clock differences between phone and server.')
EOF''',
                     e="A one-time-code algorithm you can verify yourself. The function reproduces the **official test vectors from RFC 6238** exactly (94287082 and 07081804), which is how you know the implementation is right. The code depends only on a shared secret and the current time divided into 30-second windows, so the phone and the server compute the same digits without any communication. The secret must be stored encrypted on the server, and codes should be accepted once only to prevent replay inside the window.",
                     annot=[("time 59 s, 8 digits: 94287082", "matches the RFC test vector: the implementation is correct"),
                            ("time 1111111109 s: 07081804", "second official vector"),
                            ("code 15 s later: the same code", "the 30-second window has not changed"),
                            ("code 31 s later: a new code", "a new window gives a new code")]),
            ]),
        ],
        scenario=dict(
            title="\"How should we store user passwords, and how do we make a database leak survivable?\"",
            ask="The most basic security design question, used to see whether you know why and not just which function.",
            clarify=[("What is the threat: a stolen database backup, SQL injection, a rogue employee? Do we have users with high privilege?", "All three; assume the hash table will leak one day.")],
            think=[("State the principle.", "Store a verifier, not the password. Assume the table leaks, and make the stolen data as useless as possible."),
                   ("Choose the function.", "Argon2id (or scrypt, or bcrypt): slow and memory-hard, with a per-user random salt, parameters tuned to roughly 100 ms per hash on your hardware, stored with the hash so they can be upgraded."),
                   ("Explain why not SHA-256, MD5 or encryption.", "Fast hashes allow billions of guesses per second; unsalted hashes allow precomputation and expose duplicates; encryption is reversible, so the key becomes the single point of failure."),
                   ("Add defences around it.", "Rate limiting and lockout per account and per source, breached-password checks, a pepper kept outside the database (an HSM or secret manager) as defence in depth, constant-time comparison."),
                   ("Add a second factor.", "TOTP or passkeys; recovery codes; protect the reset flow as strongly as login."),
                   ("Plan for upgrades.", "Rehash on login when parameters improve; force resets after a breach; log and alert on credential stuffing patterns."),
                   ("Reduce the problem.", "Prefer delegating login to an identity provider or passkeys so you store fewer secrets at all.")],
            answer=["\"I store a verifier, not the password, and I assume the table will leak. I use Argon2id, or scrypt or bcrypt, with a random salt per user and parameters tuned so one hash takes about a hundred milliseconds, recorded with the hash so I can raise them later. SHA-256 or MD5 would let an attacker try billions of guesses a second, unsalted hashes allow precomputed tables and reveal duplicate passwords, and encryption is reversible so the key becomes the single point of failure.",
                    "Around that I add rate limiting and lockout per account and per source, a check against known breached passwords, a pepper held outside the database in a secret manager, and constant-time comparison. I add a second factor, TOTP or passkeys, with a recovery flow no weaker than login, rehash on login when parameters improve, and alert on credential stuffing patterns. Better still, I delegate authentication to an identity provider so I store fewer secrets.\""],
            follow=[("What is a pepper?", "A secret value mixed into every password hash and kept outside the database (secret manager or HSM), so a stolen table alone is not enough to crack hashes."),
                    ("What is credential stuffing?", "Attackers try username and password pairs leaked from other sites; defences are rate limiting, breached-password checks, MFA and bot detection."),
                    ("Why are passkeys better?", "They use public-key cryptography bound to the site's origin: nothing secret is stored on the server, nothing can be phished or reused elsewhere.")],
            slips=["\"I would hash with SHA-256 and a salt.\"", "Encrypting passwords instead of hashing them.", "No plan for rate limiting or a second factor."],
        ),
        quick=[
            ("Why is SHA-256 a poor password hash?", "It is fast, so an attacker can try billions of guesses per second."),
            ("What does a salt prevent?", "Precomputed tables and the equality of hashes for identical passwords."),
            ("How does TOTP work?", "An HMAC of a shared secret and the current 30-second counter, truncated to six digits."),
        ],
        traps=[
            "Writing your own cryptography or password hashing scheme.",
            "A reset flow weaker than the login: attackers use it instead.",
            "Logging passwords (or whole request bodies) in debug logs.",
        ],
    ),
    dict(
        title="Sessions, tokens, JWT and OAuth: proving who you are on every request",
        tier="hot",
        situation="After login, every request must carry proof of identity. Sessions, JWTs, API keys, OAuth: which one, and why do so many public incidents come from a token that the server accepted when it should not have?",
        learn=["Server-side sessions versus signed tokens", "How a JWT is built and verified, byte by byte", "The classic JWT mistakes (alg none, no expiry, trusting the payload)", "OAuth 2.0 with PKCE: delegating access without sharing passwords"],
        model=[
            "A **server-side session** gives the browser a random opaque id (in a cookie flagged `HttpOnly`, `Secure`, `SameSite`) and keeps the data on the server: easy to revoke, needs shared storage across servers. A **signed token** such as a **JWT** (`header.payload.signature`, each part base64url) carries the claims itself (`sub`, `exp`, `aud`, roles) plus a signature (**HMAC** with a shared secret, or **RSA/ECDSA** with a private key and a public verification key). Any server can verify it **without a lookup**, which scales well, but it **cannot be revoked** before it expires, so keep access tokens **short-lived** (minutes) and use a **refresh token** (stored securely, rotated, revocable) to get new ones. The payload is encoded, **not encrypted**: never put secrets in it.",
            "Verifying a token means checking **everything**: the signature with the **expected algorithm** (never trust the `alg` in the token itself: `alg: none` attacks, and confusing an RSA public key for an HMAC secret), `exp` and `nbf` times, `iss` (issuer), `aud` (audience: this token is for me), and scopes or roles for the requested action. **OAuth 2.0** lets a user grant an app **limited** access to an API **without giving it their password**: the app redirects to the authorisation server, the user logs in there and approves **scopes**, the app receives a one-time **code** and exchanges it (with **PKCE**, a per-request secret that stops code interception) for tokens. **OpenID Connect** adds an **ID token** that says who the user is. Use an established identity provider and library; do not hand-roll this.",
        ],
        analogy="A session is a cloakroom ticket: a meaningless number, and the coat (data) stays at the venue. A JWT is a signed wristband that says who you are and when it expires: any door can check it without calling the front desk, but a stolen wristband works until it expires.",
        visual=[OAUTH_SEQ],
        sim=None,
        walk=[
            ("Authenticate once", "Password plus second factor, or an external identity provider."),
            ("Issue a short-lived token", "Signed claims with an expiry of minutes, and an audience."),
            ("Verify every field on every request", "Signature with the expected algorithm, expiry, issuer, audience, scope."),
            ("Refresh safely", "A refresh token, rotated on use, revocable, stored securely."),
            ("Revoke when needed", "Short lifetimes, a denylist for emergencies, key rotation."),
        ],
        groups=[
            dict(title="A JWT built and broken by hand", cmds=[
                dict(c=r'''cd ~/sec && python3 - <<'EOF'
import base64, hashlib, hmac, json
SECRET = b'server-side-secret'
b64 = lambda b: base64.urlsafe_b64encode(b).rstrip(b'=').decode()
unb64 = lambda s: base64.urlsafe_b64decode(s + '=' * (-len(s) % 4))
def make(claims, alg='HS256'):
    h = b64(json.dumps({'alg': alg, 'typ': 'JWT'}, separators=(',', ':')).encode()); p = b64(json.dumps(claims, separators=(',', ':')).encode())
    sig = b64(hmac.new(SECRET, ('%s.%s' % (h, p)).encode(), hashlib.sha256).digest()) if alg == 'HS256' else ''
    return '%s.%s.%s' % (h, p, sig)
def verify_good(token, now):
    h, p, s = token.split('.')
    if json.loads(unb64(h))['alg'] != 'HS256': return 'REJECT: algorithm is not the one we expect'
    if not hmac.compare_digest(s, b64(hmac.new(SECRET, ('%s.%s' % (h, p)).encode(), hashlib.sha256).digest())): return 'REJECT: bad signature'
    c = json.loads(unb64(p))
    if c['exp'] < now: return 'REJECT: expired'
    if c.get('aud') != 'orders-api': return 'REJECT: wrong audience'
    return 'ACCEPT as %s (role %s)' % (c['sub'], c['role'])
def verify_naive(token, now):                      # a typical bug: trusts the alg field in the token itself
    h, p, s = token.split('.')
    if json.loads(unb64(h))['alg'] == 'none': return 'ACCEPT as %s (role %s)  <- no signature checked' % (json.loads(unb64(p))['sub'], json.loads(unb64(p))['role'])
    return verify_good(token, now)
now = 1_800_000_000
good = make({'sub': 'ben', 'role': 'user', 'aud': 'orders-api', 'exp': now + 600})
print('payload is only encoded, not encrypted:', json.loads(unb64(good.split('.')[1])))
print('1. genuine token:                  ', verify_good(good, now))
h, p, s = good.split('.'); forged_payload = b64(json.dumps({'sub': 'ben', 'role': 'admin', 'aud': 'orders-api', 'exp': now + 600}, separators=(',', ':')).encode())
print('2. role changed to admin, old sig: ', verify_good('%s.%s.%s' % (h, forged_payload, s), now))
print('3. expired token:                  ', verify_good(make({'sub': 'ben', 'role': 'user', 'aud': 'orders-api', 'exp': now - 1}), now))
print('4. token for another service:      ', verify_good(make({'sub': 'ben', 'role': 'user', 'aud': 'billing-api', 'exp': now + 600}), now))
none = make({'sub': 'mallory', 'role': 'admin', 'aud': 'orders-api', 'exp': now + 600}, alg='none')
print('5. alg=none token, naive verifier: ', verify_naive(none, now))
print('6. alg=none token, correct verifier:', verify_good(none, now))
EOF''',
                     e="The anatomy of a JWT and of the mistakes made with it. The payload is plain base64: anyone can read it, so no secrets in tokens. A correct verifier checks the signature with the **expected** algorithm, then expiry and audience, and rejects the tampered role, the expired token and the token meant for another service. The famous **`alg: none`** attack works against a verifier that believes the algorithm named inside the untrusted token: it accepts an unsigned token that claims to be an administrator. The fix is one line: the **server** decides which algorithm and key to use.",
                     annot=[("payload ... {'sub': 'ben', 'role': 'user', ...}", "anyone can read a JWT's claims: it is signed, not encrypted"),
                            ("2. role changed to admin, old sig: REJECT: bad signature", "changing the payload invalidates the signature"),
                            ("3. expired token: REJECT: expired / 4. wrong audience: REJECT", "signature alone is not enough: check exp and aud"),
                            ("5. alg=none, naive verifier: ACCEPT as mallory (role admin)", "trusting the token's own header lets an attacker skip the signature"),
                            ("6. alg=none, correct verifier: REJECT", "the server enforces the algorithm")]),
            ]),
        ],
        scenario=dict(
            title="\"Design authentication and authorisation for a multi-tenant SaaS API used by a web app, a mobile app and partner integrations.\"",
            ask="A synthesis question. They want identity, tokens, scopes, tenant isolation and revocation in one coherent design.",
            clarify=[("Which user types and integrations exist, and what must a leaked token be able to do?", "Users in the web and mobile apps, machine clients for partners; blast radius should be small.")],
            think=[("Delegate identity.", "Use an identity provider (OIDC): login, MFA, social and enterprise SSO (SAML/OIDC), password hashing, account recovery. Do not build it."),
                   ("Web and mobile.", "OAuth 2.0 authorisation code flow with PKCE; short-lived access tokens (about 5 to 15 minutes) and rotating refresh tokens; web apps use HttpOnly Secure SameSite cookies or a backend-for-frontend holding the tokens."),
                   ("Partners and machines.", "OAuth client credentials with scoped tokens, or API keys that are hashed at rest, scoped, rotatable and rate limited; mTLS for high-trust integrations."),
                   ("Verification at the API.", "A gateway or middleware validates signature (keys from the provider's JWKS endpoint, cached and rotated), expiry, issuer, audience and scopes; services trust only validated claims."),
                   ("Tenant isolation.", "The tenant id comes from the verified token, never from a request parameter; every query is scoped by tenant; automated tests that try cross-tenant access; row-level security as a second barrier."),
                   ("Revocation and incident response.", "Short lifetimes, refresh-token revocation, a denylist of token ids for emergencies, key rotation, audit logs of authentication and authorisation decisions."),
                   ("Say what you will not do.", "No secrets in JWTs, no long-lived access tokens, no custom crypto, no trust in client-supplied roles.")],
            answer=["\"I would not build identity: I would use an OpenID Connect provider for login, MFA, SSO and recovery. The web and mobile apps use the authorisation code flow with PKCE and get short-lived access tokens of a few minutes plus rotating refresh tokens, with web tokens held in HttpOnly cookies or by a backend-for-frontend. Partners use client credentials with scoped tokens, or hashed, scoped, rotatable API keys, and mTLS where trust must be high.",
                    "The API gateway validates every token: signature with the expected algorithm and keys from the provider's JWKS, expiry, issuer, audience and scopes. The tenant id comes only from the verified token and every query is scoped by it, with row-level security as a second barrier and automated cross-tenant tests. For revocation I rely on short lifetimes, refresh-token revocation and an emergency denylist, with key rotation and audit logs. I would never put secrets in tokens or trust client-supplied roles.\""],
            follow=[("Why short-lived access tokens?", "They cannot be revoked individually without a lookup, so a short lifetime bounds how long a stolen token is useful."),
                    ("Where should a browser app keep tokens?", "Not in localStorage (reachable by injected scripts); use HttpOnly Secure SameSite cookies or have a backend hold the tokens and give the browser a session cookie."),
                    ("What is PKCE for?", "It binds the authorisation code to the client that asked for it, so an intercepted code cannot be exchanged by someone else (essential for mobile and single-page apps).")],
            slips=["Putting the role in a client-controlled field or unverified token.", "Long-lived access tokens with no revocation plan.", "Rolling your own login."],
        ),
        quick=[
            ("What does a verifier have to check on a JWT?", "Signature with the expected algorithm, expiry, issuer, audience and scopes."),
            ("Why is the `alg: none` attack possible?", "A verifier trusts the algorithm named in the untrusted token instead of enforcing its own."),
            ("What does OAuth let an app do?", "Get limited, revocable access to a user's data without ever seeing their password."),
        ],
        traps=[
            "Treating a JWT as encrypted: its payload is readable by anyone.",
            "Taking the tenant or role from a request parameter instead of the verified token.",
            "Storing tokens where scripts can read them (localStorage) in a browser app.",
        ],
    ),
    dict(
        title="TLS and mTLS: encrypting the wire and proving who is on the other end",
        tier="hot",
        situation="\"We use HTTPS\" is not a security architecture. Who issued the certificate? What happens when it expires at 3 a.m.? How do two internal services know they are talking to each other and not to something that wandered into the network?",
        learn=["What the handshake achieves", "Certificates, chains and what verification checks", "Failures you will meet: unknown CA, wrong name, expiry", "Mutual TLS between services"],
        model=[
            "**TLS** gives a connection three properties: **confidentiality** (encryption), **integrity** (tampering is detected) and **authentication** of the server. In the handshake the server presents a **certificate** (a public key and a name, signed by a **certificate authority**); the client verifies the **chain** up to a CA it trusts, that the **name** matches the host it meant to reach, and that the certificate is **within its validity dates**; then both sides derive fresh session keys from a key exchange (TLS 1.3 uses ephemeral keys, giving **forward secrecy**: a later key theft cannot decrypt recorded traffic). A client that skips verification (`curl -k`, `verify=False`) has encryption without authentication: any attacker in the middle can impersonate the server.",
            "**Mutual TLS (mTLS)** adds the reverse: the server also demands a **client certificate**, so each side proves its identity cryptographically. It is the standard way to authenticate **service to service** inside a system (often automated by a service mesh or a certificate manager issuing short-lived certificates) and for high-trust partner integrations. The operational burden is **certificate lifecycle**: issuance, rotation, revocation and, above all, **expiry**; expired certificates are among the most common causes of outages, so automate renewal (ACME), use short lifetimes, and **monitor days-to-expiry**. Terminate TLS where you decided (edge, proxy or service), and remember that traffic **behind** the terminator is plain text unless you re-encrypt it.",
        ],
        analogy="A passport check. The customs officer (client) checks that the passport (certificate) was issued by a government they recognise (CA), that the photo and name match the person in front of them (hostname), and that it has not expired. In mutual TLS the traveller also checks the officer's credentials before handing anything over.",
        visual=[TLS_VIZ],
        sim=None,
        walk=[
            ("The client says hello", "Offers TLS versions, ciphers and a key share."),
            ("The server answers with its certificate", "Plus its key share; the connection is already encrypted from here in TLS 1.3."),
            ("The client verifies", "Chain to a trusted CA, name matches, dates valid; any failure aborts the connection."),
            ("Both derive session keys", "From the key exchange; the keys never cross the wire."),
            ("With mTLS, the client proves itself too", "It presents its own certificate, which the server verifies against its CA."),
        ],
        groups=[
            dict(title="A real certificate authority, TLS handshakes, failures and mTLS (openssl)", cmds=[
                dict(volatile=True, c=r'''mkdir -p ~/sec/pki && cd ~/sec/pki
mk() { openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes -keyout $1.key -out $1.pem -subj "/CN=$2" -days 365 2>/dev/null; }
mk ca "Demo Root CA"
openssl req -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes -keyout server.key -out server.csr -subj "/CN=shop.internal" 2>/dev/null
printf 'subjectAltName=DNS:shop.internal\n' > san.ext
openssl x509 -req -in server.csr -CA ca.pem -CAkey ca.key -CAcreateserial -out server.pem -days 30 -extfile san.ext 2>/dev/null
echo "--- the server certificate:"
openssl x509 -in server.pem -noout -subject -issuer -dates -ext subjectAltName 2>/dev/null | sed 's/^ *//'
echo "--- does it chain to our CA?"
openssl verify -CAfile ca.pem server.pem
echo "--- days left (a monitor would alert below, say, 14):"
openssl x509 -in server.pem -noout -checkend $((14*86400)) && echo "valid for at least 14 more days" || echo "EXPIRES WITHIN 14 DAYS"
openssl x509 -in server.pem -noout -checkend $((60*86400)) >/dev/null && echo "valid for 60 more days" || echo "would be expired in 60 days"''',
                     e="A miniature public-key infrastructure with real `openssl`. First a **root CA** (a self-signed certificate), then a **server certificate** for the name `shop.internal`, signed by that CA and valid for 30 days. `openssl verify` confirms the chain, and `-checkend` is the one-line **expiry monitor** every certificate should have: it exits non-zero if the certificate expires within the given number of seconds. (Real CAs work the same way; the trust comes from clients having the CA's certificate in their trust store.)",
                     annot=[("subject=CN=shop.internal / issuer=CN=Demo Root CA", "the certificate names its owner and its signer"),
                            ("X509v3 Subject Alternative Name: DNS:shop.internal", "the name clients will match against the host they connect to (the name is printed on the line after the label)"),
                            ("server.pem: OK", "the chain verifies against our CA"),
                            ("Certificate will not expire / valid for at least 14 more days / would be expired in 60 days", "the expiry check: a monitor should alarm well before the date (the first line is openssl's own message for the 14-day check)")]),
                dict(volatile=True, c=r'''cd ~/sec/pki
openssl s_server -accept 8443 -cert server.pem -key server.key -www -quiet >/dev/null 2>&1 &
sleep 0.7
echo "--- 1. client trusts our CA and checks the name:"
echo | openssl s_client -connect 127.0.0.1:8443 -CAfile ca.pem -verify_hostname shop.internal -verify_return_error 2>&1 | grep -E "Protocol|Verification|Cipher is|TLSv" | head -4
echo "--- 2. client does not know our CA (as if the certificate came from an unknown issuer):"
echo | openssl s_client -connect 127.0.0.1:8443 -verify_return_error 2>&1 | grep -iE "error|Verify return" | head -2
echo "--- 3. the certificate is fine but the name is wrong (an impostor with a valid certificate for another host):"
echo | openssl s_client -connect 127.0.0.1:8443 -CAfile ca.pem -verify_hostname evil.example -verify_return_error 2>&1 | grep -iE "error|mismatch" | head -2
echo "--- 4. the same request with verification switched off (curl -k) succeeds against ANYONE:"
curl -sk https://127.0.0.1:8443/ -o /dev/null -w "curl -k -> HTTP %{http_code}\n"
kill %1 2>/dev/null; wait 2>/dev/null; true''',
                     e="Four handshakes against a real TLS server. (1) A client that **trusts our CA and checks the name** completes the handshake: TLS 1.3 with a modern cipher and `Verification: OK`. (2) A client that does not trust the issuer **refuses**: the error is `unable to get local issuer certificate`. (3) With a correct chain but the **wrong hostname** the check fails: this is what stops an attacker who holds a valid certificate for *their own* site. (4) The same server with verification disabled (`curl -k`) succeeds, which is exactly why disabling verification \"to make the error go away\" removes the authentication half of TLS.",
                     annot=[("Protocol: TLSv1.3 / Verification: OK", "encrypted, and the server's identity was checked"),
                            ("verify error: unable to get local issuer certificate", "the client has no trusted CA that signed this certificate"),
                            ("Hostname mismatch / verify error", "valid chain, wrong name: refuse"),
                            ("curl -k -> HTTP 200", "encryption without authentication: anyone in the middle would also be accepted")]),
                dict(volatile=True, c=r'''cd ~/sec/pki
openssl req -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes -keyout client.key -out client.csr -subj "/CN=orders-service" 2>/dev/null
openssl x509 -req -in client.csr -CA ca.pem -CAkey ca.key -CAcreateserial -out client.pem -days 30 2>/dev/null
openssl s_server -accept 8444 -cert server.pem -key server.key -CAfile ca.pem -Verify 1 -www -quiet >/dev/null 2>&1 &
sleep 0.7
echo "--- mTLS: the server REQUIRES a client certificate"
echo "client WITHOUT a certificate:"
curl -sS --cacert ca.pem --resolve shop.internal:8444:127.0.0.1 -o /dev/null -w "HTTP %{http_code}
" https://shop.internal:8444/ 2>&1 | head -2
echo "client WITH the certificate for orders-service:"
curl -sS --cacert ca.pem --cert client.pem --key client.key --resolve shop.internal:8444:127.0.0.1 -o /dev/null -w "HTTP %{http_code}
" https://shop.internal:8444/ 2>&1 | head -2
kill %1 2>/dev/null; wait 2>/dev/null; true''',
                     e="Mutual TLS. The same server is started with `-Verify 1`, meaning a client certificate signed by the CA is **required**. A client without one is rejected (curl reports a `certificate required` alert); a client holding a certificate issued to `orders-service` gets through and receives an HTTP 200. The server now knows **which** service is calling, from a credential that cannot be forged without the private key. In production the certificates are short-lived and issued and rotated automatically (a service mesh or a certificate manager), so nobody handles keys by hand.",
                     annot=[("client WITHOUT a certificate: curl: (56) ... tlsv13 alert certificate required", "the server refuses callers that cannot prove their identity (TLS 1.3 reports it just after the handshake)"),
                            ("client WITH the certificate: HTTP 200", "the verified identity (CN=orders-service) is available to the server for authorisation")]),
            ]),
        ],
        scenario=dict(
            title="\"How do you secure traffic between 40 internal services? What happens when a certificate expires?\"",
            ask="An operations-flavoured security question. They want encryption, identity, automation and failure handling.",
            clarify=[("Do we run on our own machines or a cloud, do we have a service mesh, and what is our threat model inside the network?", "Assume the internal network can be compromised: zero trust.")],
            think=[("State the goals.", "Encrypt in transit, authenticate both ends, authorise each call, and make rotation boring."),
                   ("Choose the mechanism.", "mTLS between services, with identities per workload (SPIFFE-style IDs in SANs); implemented by a service mesh sidecar or library; a private CA (or a managed one) issuing short-lived certificates, for example 24 hours."),
                   ("Automate the lifecycle.", "Automatic issuance and rotation (mesh control plane, cert-manager, ACME); no humans handling private keys; keys never leave the workload."),
                   ("Authorise after authenticating.", "mTLS says who; policies say what: service A may call endpoint X of service B; deny by default."),
                   ("Expiry handling.", "Monitor days-to-expiry for every certificate (`-checkend`-style probes), alert at 30 and 14 days, renew automatically well before expiry, test rotation regularly, and have a break-glass procedure."),
                   ("Edge versus inside.", "Terminate public TLS at the edge with automated public certificates; re-encrypt to backends; keep the root CA offline and protected."),
                   ("Account for failure.", "CA outage must not stop traffic (short but not too short lifetimes, cached trust bundles); clock skew breaks validation (NTP monitoring); revocation by short lifetime rather than CRL where possible.")],
            answer=["\"I would authenticate and encrypt service-to-service traffic with mutual TLS, giving each workload its own identity in its certificate, implemented by a service mesh or library with a private CA issuing short-lived certificates, say 24 hours, rotated automatically so no human handles keys. mTLS tells me who is calling; authorisation policies say what they may call, with deny by default.",
                    "For expiry, every certificate is monitored for days remaining with alerts well ahead, renewal is automatic and rehearsed, and there is a break-glass procedure. Public traffic terminates at the edge with automatically renewed certificates and is re-encrypted to the backends. I keep the root CA protected and offline, make sure an outage of the CA does not stop existing traffic, monitor clock skew, and rely on short lifetimes rather than revocation lists.\""],
            follow=[("What is a service mesh doing here?", "A sidecar proxy per workload handles mTLS, identity, retries and policy, so applications get encryption and authentication without code changes."),
                    ("What is forward secrecy?", "Session keys come from ephemeral key exchange, so stealing a server's long-term key later cannot decrypt traffic recorded earlier."),
                    ("Why not just use a VPN or a private network?", "A network perimeter authenticates the network, not the workload: anything inside can talk to anything; zero trust authenticates every call.")],
            slips=["Disabling certificate verification to fix errors.", "Manual certificate rotation.", "No monitoring of expiry dates."],
        ),
        quick=[
            ("What three things does a TLS client verify about a server certificate?", "The chain to a trusted CA, that the name matches the host, and that it is within its validity dates."),
            ("What does mTLS add to TLS?", "The server also requires and verifies a client certificate, so both sides authenticate."),
            ("Why is `curl -k` dangerous in production code?", "It keeps encryption but removes server authentication: a man in the middle is accepted."),
        ],
        traps=[
            "A certificate that expires on a weekend because renewal was manual and nobody was watching.",
            "Verification disabled in a client library, left in \"temporarily\".",
            "Assuming traffic behind the load balancer is protected when TLS terminates at the edge.",
        ],
    ),
]
