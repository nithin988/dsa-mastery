"""Systems Mastery S25: security for system design (real hashing, JWT, OpenSSL TLS and mTLS, injection, secrets)."""
from sys_sec_a import LESSONS_A
from sys_sec_b import LESSONS_B, TAIL
from sys_architecture import MODULE as OLD

MODULE = dict(
    id="sec",
    deep=True,
    title="Security for system design",
    lead="Security is a property of the whole design, not a feature added at the end. This module runs the attacks and the defences: a stolen password table cracked in milliseconds and the hash that stops it, one-time codes verified against the official test vectors, a JWT built and forged by hand, a real certificate authority with TLS handshakes that fail for the right reasons and mutual TLS, an IDOR, a SQL injection and an SSRF filter, a secret that survives in git history, envelope encryption with key rotation, and a tamper-evident audit log.",
    time="9 to 11 hours",
    why=[
        "Most breaches are not exotic. They are a missing authorisation check, a password stored with a fast hash, a certificate that expired, a key pushed to a repository, an internal service that trusted anything on the network. The defences are well known; what is scarce is engineers who build them in from the first design.",
        "Security trades off against everything else: latency (encryption, verification), usability (MFA), cost (key management, audit) and speed of delivery. Good designs choose the controls that stop the most breaches first and make the safe path the default one.",
        "In interviews \"how would you secure this?\" tests whether you reason about threats, layers and failure rather than reciting a list of tools.",
    ],
    outcomes=[
        "Store passwords correctly (Argon2id, scrypt, bcrypt with salts), explain why fast hashes and encryption are wrong, and add TOTP and passkeys.",
        "Build and verify a JWT by hand, name its classic mistakes, and explain OAuth 2.0 with PKCE and session versus token trade-offs.",
        "Run a certificate authority, perform and break TLS handshakes with OpenSSL, explain mTLS and certificate lifecycle and expiry monitoring.",
        "Prevent IDOR, SQL injection, XSS, SSRF and CSRF by design, with authorisation centralised and tenant scoped.",
        "Manage secrets, respond to a leaked key, use envelope encryption with rotation and keep tamper-evident audit logs.",
        "Design layered security for a system holding payment and personal data, and prioritise the work.",
    ],
    before=[
        "The networking module (S07) for TLS and HTTP, the APIs module (S23) for tokens and webhooks, and the architecture module (S24) for service boundaries. Python 3, OpenSSL and git run the experiments.",
        "Install the real tools: `sudo apt install openssl python3 git curl` (the Docker lab image has them). You do **not** need root: certificates and keys are created in `~/sec`, servers run on high ports and stop themselves. All credentials in the demos are examples or throwaway values.",
        "Run each lesson's commands in order; the TLS lesson builds on its own earlier commands. Timings depend on your machine; the shapes match.",
    ],
    env=["The scratch folder is `~/sec` (created by the first command)."],
    lessons=LESSONS_A + LESSONS_B,
    labs=[
        [l for l in OLD["labs"] if l["script"] == "token-check"][0],
        dict(kind="linux", script="log-attack-read", dir="attacklog", title="Read the logs: find the attack",
             goal=["Read an authentication log and a web log, identify the attacker, the compromised account and the injection attempts, and decide the first response."],
             story=["The on-call engineer pastes two log excerpts and asks \"are we being attacked?\". Work out who is attacking, what they achieved and what you do first."],
             tasks=["Read `auth.log`, `web.log` and `README.txt` in `~/sys-lab/attacklog`.", "Find the address with the most failed logins, how many failures it made before its first success and the account it got into.", "Count the SQL injection requests in the web log.", "Write `key=value` lines into `~/sys-lab/answers-attack.txt`."],
             check="Run the check script.", check_cmd="bash ~/sys-lab/check-log-attack-read.sh",
             hints=["Count failures per address with awk on column 2 where column 4 is FAIL, then sort the counts.", "Stop counting at the first OK from that address.", "grep -ciE with the pattern for a quote followed by OR, or UNION SELECT, counts the injection lines."],
             solution=["203.0.113.9 has 5 failures, then logs in as ben.", "Two web requests contain injection patterns (the OR and the UNION SELECT).", "First response: reset the compromised account, revoke its sessions and look at what it did; then block and investigate."]),
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
