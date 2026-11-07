"""Chapter 14: Case files, how real outages happened (primary postmortems retold for learners)."""
import sd2kit as k

# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "Monday, 9:30 a.m.", "kind": "bad",
     "scene": lambda cx, cy, w: k.person(cx - 44, cy - 6, 1.1, "warn") + k.alert(cx + 40, cy - 4, None),
     "caption": "The weekend outage is over. Your manager asks: what exactly happened, and could it happen again?"},
    {"title": "Monday, 11:00 a.m.", "kind": "warn",
     "scene": lambda cx, cy, w: k.cloud(cx - 40, cy, "other firms", "warn") + k.flow(cx - 8, cy, cx + 26, cy, "warn") + k.person(cx + 56, cy - 6, 1.0, "ok"),
     "caption": "You read how GitLab, AWS, Cloudflare, GitHub, Meta and Google lost whole days, and what they wrote down."},
    {"title": "Monday, 4:00 p.m.", "kind": "ok",
     "scene": lambda cx, cy, w: k.person(cx - 50, cy - 6, 1.1, "ok") + k.server(cx + 36, cy, "checked", "ok") + k.flow(cx - 24, cy, cx + 6, cy, "ok"),
     "caption": "You test your own backups and add one safety check. Other people's bad nights became your list."},
], "ShopKart reads other people's outages", "Learning from a failure that happened to someone else costs nothing but reading time.")

READ_FIG = k.figure(720, 188, [
    k.badge(76, 50, "1. trigger", "warn"), k.flow(122, 50, 188, 50, "warn"),
    k.badge(246, 50, "2. it spreads", "bad"), k.flow(300, 50, 366, 50, "bad"),
    k.badge(424, 50, "3. slow to see", "bad"), k.flow(484, 50, 550, 50, "warn"),
    k.badge(610, 50, "4. the fix", "ok"),
    k.note(76, 100, "a small change", "", "middle"), k.note(246, 100, "no brake stops it", "", "middle"),
    k.note(424, 100, "tools or access fail", "", "middle"), k.note(610, 100, "learn and change", "", "middle"),
    k.note(360, 150, "Every case in this chapter fits this chain. The trigger is rarely the real cause.", "acc"),
], "The shape of an outage", None)


def _fig(parts, title, h=182):
    return k.figure(720, h, parts, title, None)


F_GITLAB = _fig([
    k.person(50, 64, 1.1, "warn"), k.flow(84, 64, 170, 64, "bad", "wipe data"),
    k.server(210, 62, "primary", "bad"), k.server(560, 62, "replica", "warn"),
    k.note(210, 128, "wiped by mistake", "bad"), k.note(560, 128, "was the intended target", "warn"),
    k.flow(244, 62, 526, 62, "warn", "replication broken", dash=True),
    k.note(360, 164, "Meant for the replica, ran on the primary. About 300 GB went in a second or two.", "acc"),
], "GitLab: the right command on the wrong machine")

F_AWS = _fig([
    k.person(50, 64, 1.1, "warn"), k.flow(84, 64, 172, 64, "warn", "remove a few"),
    k.server(212, 62, "billing servers", "warn"),
    k.badge(390, 22, "input typo", "bad"), k.flow(246, 62, 460, 62, "bad", "far more removed"),
    k.server(500, 62, "index", "bad"), k.server(620, 62, "placement", "bad"),
    k.note(560, 128, "S3 cannot serve requests", "bad"),
    k.note(360, 164, "A routine playbook command removed too much capacity, and both core parts had to restart.", "acc"),
], "AWS S3: one mistyped input in a routine command")

F_CF = _fig([
    k.person(50, 64, 1.1, "warn"), k.flow(84, 64, 170, 64, "warn", "new WAF rule"),
    k.cloud(210, 62, "global edge", "warn"), k.flow(244, 62, 360, 62, "bad", "in seconds"),
    k.server(400, 62, "every server", "bad"), k.gauge(560, 70, 98, "CPU", "bad"),
    k.note(560, 128, "all cores busy: 502 errors", "bad"),
    k.note(360, 164, "A rule with a costly pattern ran on all live traffic worldwide the moment it shipped.", "acc"),
], "Cloudflare: a rule that ate every CPU")

F_GH = _fig([
    k.server(120, 58, "East Coast", "warn"), k.server(600, 58, "West Coast", "warn"),
    k.flow(154, 58, 566, 58, "bad", "link cut for 43 seconds", dash=True),
    k.note(120, 128, "writes West never saw", "bad"), k.note(600, 128, "writes East never saw", "bad"),
    k.note(360, 164, "Both sides then accepted writes, so neither copy of the database could simply win.", "acc"),
], "GitHub: two databases, both thinking they were in charge")

F_FB = _fig([
    k.cloud(100, 62, "backbone", "bad"), k.flow(134, 62, 230, 62, "bad", "all links down"),
    k.server(270, 60, "DNS servers", "warn"), k.flow(304, 60, 400, 60, "warn", "withdraw routes"),
    k.cloud(440, 62, "internet", "bad"), k.note(440, 128, "cannot find facebook.com", "bad"),
    k.person(600, 62, 1.1, "warn"), k.note(600, 128, "tools and doors also down", "warn"),
    k.note(360, 164, "The safety reaction of the DNS servers made the outage total. Fixing it needed people on site.", "acc"),
], "Facebook (Meta): the network that fixes the network was down")

F_GCP = _fig([
    k.database(70, 62, "policy row", "warn"), k.flow(104, 62, 200, 62, "bad", "copied in seconds"),
    k.server(240, 60, "region A", "bad"), k.server(350, 60, "region B", "bad"), k.server(460, 60, "region C", "bad"),
    k.note(350, 128, "same blank value, same crash", "bad"),
    k.flow(500, 60, 580, 60, "warn", "restart"), k.database(620, 62, "database", "warn"),
    k.note(620, 128, "overloaded by retries", "warn"),
    k.note(360, 164, "One bad data row crashed every region. Then the restart crowd hit the database.", "acc"),
], "Google Cloud: bad data, global crash, restart herd")

# ----------------------------------------------------------------------------- cases
CASES = [
    dict(
        when="31 January 2017", company="GitLab", title="The database that was wiped, and the backups that were not there",
        summary="An engineer fighting a database slowdown late at night deleted the data on the wrong server. GitLab.com then needed about 18 hours to come back, and some data created that day was lost for good.",
        figure=F_GITLAB,
        what_happened=[
            "GitLab.com ran one main PostgreSQL database and one copy of it, called a **secondary**, that follows every change. On the evening of 31 January the main database came under heavy load, partly from spam and partly from a background job deleting a user account that had been flagged by mistake. The secondary fell behind and then stopped following.",
            "An engineer tried to rebuild the secondary by emptying its data folder and copying a fresh version. Very late at night, the delete command was run on the **primary** instead. About 300 GB of live data was removed before the engineer noticed and stopped it.",
            "Then the team went looking for backups. Several of them turned out to be unusable or missing. The best option left was a copy of production taken by an engineer about six hours earlier, to use in a test environment.",
        ],
        timeline=[
            ("About 17:20 UTC", "An engineer takes a snapshot of production for testing. This accidentally becomes the newest copy of the data."),
            ("About 19:00", "Database load rises. Users cannot post comments for several hours."),
            ("About 23:00", "The secondary has fallen behind and the history it needs is already gone from the primary. Manual rebuilding starts."),
            ("About 23:30", "The delete command runs on the primary. The engineer stops it, but about 300 GB is already gone."),
            ("1 February, about 17:00", "After copying the six hour old snapshot over slow disks (about 18 hours in total), GitLab.com is back, without webhooks."),
            ("About 18:00", "Webhooks are restored and final checks finish."),
        ],
        root_cause="A manual, undocumented rebuild procedure was run under stress and the engineer was on the wrong server. Behind that sat a second cause: nobody owned and tested the backups, so when they were needed they did not work.",
        why_spread="A tired person, a slow rebuild and an unusual load all landed together. Backup failures were silent: the daily dump job ran with the wrong tool version and its failure emails were rejected, so nobody knew for a long time.",
        what_changed="GitLab listed fifteen follow-ups, including a shell prompt that clearly shows which host and environment you are on, monitoring for backups, automated tests that restore a backup, point in time recovery, hourly snapshots and a named owner for data durability.",
        lesson=[
            "**A backup you have never restored is a hope, not a backup.** Schedule a restore test and alert when a backup job fails or is empty.",
            "Make dangerous commands hard to point at the wrong target: colour the prompt for production, show the hostname, and write the rebuild steps down before you need them.",
        ],
        url="https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/", source="GitLab: Postmortem of database outage of January 31",
        caveat="The post gives the lost window as 17:20 to 23:30 UTC in one place and a different end time in its introduction, so treat the exact window as approximate. Counts of lost data (about 5,000 projects, 5,000 comments, 700 users) are GitLab's estimates and were stated as minimums.",
    ),
    dict(
        when="28 February 2017", company="Amazon Web Services", title="One mistyped input took down S3 in a whole region",
        summary="A routine command to remove a few servers removed far more than intended. S3 in the US East (Northern Virginia) region could not serve requests for about four hours, and much of the internet noticed.",
        figure=F_AWS,
        what_happened=[
            "The S3 team was investigating why a billing system was slow. An authorised engineer ran a command from an established playbook to take a small number of servers out of service. One input was entered wrongly, and a much larger set of servers was removed.",
            "Those servers also supported two core parts of S3: the **index**, which knows where every object lives, and the **placement** part, which decides where new objects are stored. Without enough capacity both had to restart, and S3 could not answer requests while they did.",
            "Other AWS services that depend on S3 suffered too, including launching new EC2 instances and some data volumes. Even AWS's own status dashboard needed S3, so for a while it could not show updates and AWS used banner text and Twitter instead.",
        ],
        timeline=[
            ("9:37 a.m. PST", "The command is run and the large set of servers is removed."),
            ("12:26 p.m.", "The index part can serve some requests again (GET, LIST and DELETE)."),
            ("1:18 p.m.", "The index part is fully recovered."),
            ("1:54 p.m.", "The placement part finishes recovering and S3 operates normally. That is about 4 hours 17 minutes after the start (our sum of the stated times)."),
        ],
        root_cause="The tool allowed one input to remove too much capacity, and nothing blocked a removal that would take a subsystem below its safe minimum.",
        why_spread="The same machines served several subsystems in one region, so a mistake in billing became an outage of core storage. The restarts were slow because AWS had not fully restarted those subsystems in a large region for years, and S3 had grown a lot in that time.",
        what_changed="AWS changed the tool to remove capacity more slowly and to refuse removals that would go below minimum capacity, began auditing other tools for the same weakness, moved up work to split the index into smaller cells, and made the status dashboard run across several regions.",
        lesson=[
            "**Put a seatbelt on destructive tools:** limits, dry runs, a maximum blast radius and a minimum safe capacity that the tool refuses to cross.",
            "Do not host your status page or your incident tools on the thing that is failing. And practise a full restart before the day you need one.",
        ],
        url="https://aws.amazon.com/message/41926/", source="AWS: Summary of the Amazon S3 Service Disruption in the Northern Virginia (US-EAST-1) Region",
        caveat="Times are Pacific. The total duration is our own sum from the stated start and finish times; the summary does not state a single total.",
    ),
    dict(
        when="2 July 2019", company="Cloudflare", title="A firewall rule that used all the CPU, worldwide, in seconds",
        summary="Cloudflare shipped a new rule for its web application firewall (WAF). One pattern in it was so expensive to match that servers everywhere ran out of CPU, and customers saw 502 errors for 27 minutes.",
        figure=F_CF,
        what_happened=[
            "A **WAF** inspects web requests and blocks attacks. Cloudflare engineers merged a change to its managed rules. It contained a **regular expression** (a text pattern) that, on some inputs, makes the matching engine try an enormous number of combinations, called **backtracking**.",
            "The rule was deployed in a mode that only observes and does not block, but it still had to run against live traffic. CPUs that serve web traffic went to nearly 100 percent across the network, and customers and their visitors got 502 errors.",
            "Engineers first saw a flood of pager alerts, then worked out that the WAF was the cause and used a global switch to turn it off. Traffic and CPU returned to normal two minutes later. The team confirmed the cause and re-enabled the WAF about 45 minutes after that.",
        ],
        timeline=[
            ("13:31 UTC", "The change is merged after approval."),
            ("13:37", "Automatic build finishes and the tests pass."),
            ("13:42", "The change starts deploying and goes worldwide almost at once."),
            ("About 13:45", "The first pager alert fires, followed by many more."),
            ("14:00", "The WAF is identified as the cause and an attack is ruled out."),
            ("14:07", "The WAF is switched off globally."),
            ("14:09", "Traffic and CPU are back to normal. The outage lasted 27 minutes."),
            ("14:52", "A fix is confirmed and the WAF is turned back on."),
        ],
        root_cause="A badly behaved pattern met a regular expression engine with no guarantee about how long matching can take. Contributing causes Cloudflare listed include a CPU protection that had been removed by mistake in an earlier refactor, and tests that never measured CPU use.",
        why_spread="Firewall rules were allowed to skip the normal staged rollout so that attacks could be answered fast. They travelled through a system that updates every server in seconds, so a mistake reached the whole network before anyone could see a pattern.",
        what_changed="Cloudflare restored the CPU protection, reviewed all 3,868 managed rules for backtracking, added performance profiling to the tests, planned a switch to regex engines with run time guarantees, changed the procedure to staged rollouts, and planned an emergency way to take its own dashboard and API off the edge.",
        lesson=[
            "**Ship in stages, even your fast lane.** A small first slice with a metric watching it turns a worldwide outage into a blip.",
            "Test the cost of a change, not just whether it gives the right answer, and keep a global off switch that you have practised.",
        ],
        url="https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/", source="Cloudflare blog: Details of the Cloudflare outage on July 2, 2019",
    ),
    dict(
        when="21 to 22 October 2018", company="GitHub", title="Forty three seconds of network trouble, a day of degraded service",
        summary="A short loss of connectivity between two GitHub sites made its database failover choose a different primary. Fixing the resulting split took over 24 hours, though GitHub reported no user data lost.",
        figure=F_GH,
        what_happened=[
            "GitHub was replacing faulty optical network equipment. At 22:52 UTC on 21 October the maintenance cut the link between its East Coast network hub and its main East Coast data centre. The link came back after 43 seconds.",
            "In that short gap, the software that manages MySQL failover, called Orchestrator, decided that databases on the West Coast should become the primaries. When the link returned, the application began writing to the West primaries, but the East still held a few seconds of writes the West never had. Neither side was safe to fail back to.",
            "GitHub chose to restore from backups and rebuild replicas, which took hours because of the data size. While databases were served from across the country, pages were slow and some users saw inconsistent data. A large backlog of webhook events and Pages builds then had to be processed.",
        ],
        timeline=[
            ("22:52 UTC, 21 Oct", "Maintenance cuts the link for 43 seconds. Failover moves database primaries to the West Coast."),
            ("23:02", "First responders see databases in an unexpected state."),
            ("23:09 to 23:13", "Status goes yellow, then red, and an incident coordinator takes charge."),
            ("23:19", "Webhooks and Pages builds are paused to protect data already received."),
            ("00:05, 22 Oct", "The recovery plan is set: restore from backups, resync replicas, return to a stable layout."),
            ("11:12", "All database primaries are back on the East Coast."),
            ("16:24", "Replicas catch up and the original layout is restored. The backlog is still being worked through."),
            ("23:03", "Status returns to green, 24 hours 11 minutes after the start."),
        ],
        root_cause="The failover tool was free to promote a primary in another region after a brief connectivity blip, creating two sets of writes that could not be merged cleanly.",
        why_spread="Recovery took far longer than first estimated because estimates assumed steady progress, while replication catching up slows down as it nears the end and morning traffic added more writes. More than five million webhook events and about 80,000 Pages builds queued up; about 200,000 webhook payloads expired before they could be processed.",
        what_changed="GitHub reconfigured Orchestrator to stop promoting primaries across regional boundaries, sped up a more detailed status system, continued work on running from several data centres at once, and planned more fault injection and testing of its assumptions.",
        lesson=[
            "**An automatic fix can be the larger problem.** Decide in advance which failovers a machine may do alone, and limit them to cases you have tested.",
            "Give estimates in ranges and say what is unknown. Pause side effects such as webhooks early so the damage stops growing while you recover.",
        ],
        url="https://github.blog/news-insights/company-news/oct21-post-incident-analysis/", source="GitHub blog: October 21 post-incident analysis",
        caveat="Inconsistent writes were still being reconciled when GitHub published, so this retelling reflects the post as written, not any later update.",
    ),
    dict(
        when="4 October 2021", company="Meta (Facebook)", title="The command that cut the backbone and locked the engineers out",
        summary="During routine maintenance, a command took down every connection in Meta's backbone network. Its DNS servers then pulled themselves off the internet, and the tools to fix things went with them.",
        figure=F_FB,
        what_happened=[
            "Meta's data centres talk to each other over a global **backbone** network. During routine maintenance, a command meant to check the backbone's capacity instead took down all of its connections. Meta's systems audit such commands, but a bug in the audit tool let this one through.",
            "Meta's **DNS** servers (the internet's phone book) are programmed to stop advertising their routes over **BGP** (how networks announce what they can reach) when they cannot reach the data centres, as a health signal. With the backbone down they all did, so the name servers were unreachable even though they were running.",
            "Internal tools and even normal and out of band access also failed, so engineers had to go on site. Physical security and secure access protocols are strict, which slowed things down. Services were then brought back gradually to avoid power and traffic surges.",
        ],
        timeline=[
            ("Routine maintenance", "A command intended to assess backbone capacity takes down all backbone connections."),
            ("Seconds later", "Data centres are cut off from each other and from the internet. DNS servers withdraw their BGP routes."),
            ("Next", "Engineers cannot reach systems remotely. Many internal tools that depend on DNS fail too."),
            ("Then", "Teams are sent to the data centres, confirm the cause and bring the backbone back."),
            ("Last", "Services are restored in stages to avoid power and traffic surges."),
        ],
        root_cause="A faulty command, combined with a bug in the audit tool that should have blocked it, disabled the backbone network.",
        why_spread="The DNS servers' protective behaviour was sensible on its own but turned a backbone failure into a global disappearance. The people and tools needed to repair the network depended on that same network.",
        what_changed="Meta said it would strengthen testing, drills and resilience. It had never run a storm drill simulating a global backbone loss and planned to simulate such events. It also said its strict security slowed recovery and that it considers that trade worth making.",
        lesson=[
            "**Keep a way in that does not depend on the thing that is broken:** out of band access, an emergency account and a contact list that is not stored on your own servers.",
            "Ask what each safety reaction does when everything fails at once, and practise the worst day, not only the likely ones.",
        ],
        url="https://engineering.fb.com/2021/10/05/networking-infrastructure/outage-details/", source="Engineering at Meta: More details about the October 4 outage",
        caveat="The post gives no clock times or total duration, so none are stated here. Timeline entries are in the order the post describes.",
    ),
    dict(
        when="12 June 2025", company="Google Cloud", title="A blank field, a null pointer and a global crash loop",
        summary="A new check in a core Google Cloud service met a policy row with blank fields and crashed. Because the data copies worldwide in seconds, API requests failed in many regions, and recovery took hours.",
        figure=F_GCP,
        what_happened=[
            "A service called Service Control checks quotas and policies for API requests. On 29 May 2025 Google added a new check to it. The code did not handle a missing value, and the check was not protected by a feature flag.",
            "On 12 June, a policy change was inserted that contained blank fields. Service Control read it, tried to use a value that was not there (a **null pointer**) and crashed over and over. Users saw 503 errors across Google Cloud, Google Workspace and other Google products.",
            "Engineers started triage within minutes and prepared a kill switch for the faulty path. When the services restarted in big regions such as us-central1, they all hit the same database table at once and overloaded it, because there was no randomised wait between retries.",
        ],
        timeline=[
            ("About 10:45 PDT", "The policy change with blank fields is inserted and copied to every region."),
            ("Within 2 minutes", "Triage begins. The root cause is found within about 10 minutes."),
            ("About 25 minutes in", "A kill switch for the faulty path is ready. Rollout finishes within about 40 minutes."),
            ("About 2 hours in", "Most regions have recovered by bypassing the quota check."),
            ("Up to 2 hours 40 minutes", "us-central1 recovers slowly because restarting tasks overload the database."),
            ("18:18", "The status page lists the incident as over, after about 7.5 hours."),
        ],
        root_cause="New code that skipped error handling and had no feature flag read unexpected blank data and crashed instead of carrying on.",
        why_spread="The policy data is replicated globally within seconds, so every region received the bad row almost at once and ran the same faulty code. Restarts without randomised exponential backoff then created a herd of retries.",
        what_changed="Google committed to making failing checks fail open, to rolling out globally replicated data in steps, to requiring feature flags (off by default) for changes to critical programs, to auditing systems for randomised backoff, and to keeping its status and monitoring tools running even if Cloud is down.",
        lesson=[
            "**Treat data like code:** a configuration or policy change can crash everything, so roll it out in steps with a check at each step.",
            "Add random jitter to retries so a recovering system is not knocked down again by its own clients.",
        ],
        url="https://status.cloud.google.com/incidents/ow5i3PPK96RduMcb1SsW", source="Google Cloud: incident report for 12 June 2025",
        caveat="Google's pages give slightly different start times (10:45 to 10:51) and an early estimate of three hours that was later revised, so we quote approximate times and the final end time from the status page.",
    ),
]

# ----------------------------------------------------------------------------- interviews
INTERVIEWS = [
    dict(
        who="Reported by candidates in reliability and operations interviews, not official. Often asked as: tell me about an outage you studied.",
        scenario=dict(
            title="Walk me through a public outage and what you would change",
            ask="Pick a well known incident, explain what happened in simple terms, and say what you would do differently.",
            clarify=[("Is it fine to pick any public postmortem?", "Yes, choose one you know well enough to explain in two minutes."),
                     ("Should I focus on the trigger or the system?", "Both: the trigger starts it, the system decides how bad it gets.")],
            think=[("Say the trigger in one sentence.", "For example: a command removed more servers than intended."),
                   ("Explain why it spread.", "Which missing brake let a small mistake reach everyone?"),
                   ("Explain why it lasted.", "Slow detection, slow restart, missing access or a missing runbook."),
                   ("Finish with two changes you would make.", "Preferably a guard on the tool and a practised recovery.")],
            answer=["I will take the AWS S3 outage of February 2017. An engineer ran a routine playbook command to remove a few servers from a billing subsystem. One input was wrong, so far more servers went, including ones that supported the index and placement parts of S3. Both had to restart, and S3 in that region could not serve requests for a few hours.",
                    "The trigger was a typo, but the cause was a tool with no limit and a restart nobody had practised at that size. I would make the tool refuse to go below a minimum capacity, remove capacity slowly, and rehearse full restarts. AWS announced changes of exactly that kind, and also moved its status page off S3."],
            follow=[("Why not just blame the engineer?", "A blameless review asks why the tool allowed it. Humans make typos; systems should make them harmless."),
                    ("How would you know the restart takes hours?", "By practising it on a copy and timing it, before the real day.")],
            slips=["Blaming one person and stopping there.", "Retelling the story without any change you would make.", "Quoting numbers you are not sure of; say approximately."],
        )),
    dict(
        who="A common incident response scenario, reported by candidates, not official.",
        scenario=dict(
            title="You are on call and the whole site is returning errors. What do you do in the first 15 minutes?",
            ask="Describe how you would lead an incident from the first alert to a stable state.",
            clarify=[("Do I have a runbook, a status page, a team?", "Assume some, but say what you would do if not."),
                     ("Did anything change recently?", "A recent deploy or config push is the most common cause.")],
            think=[("Declare it and name roles.", "One incident lead, one person fixing, one person communicating."),
                   ("Stop the bleeding first.", "Rollback or disable the last change; this is faster than finding the root cause."),
                   ("Check what changed.", "Deploys, config, data pushes, certificates, expiring things."),
                   ("Communicate early and honestly.", "Update the status page; say what you know and do not know."),
                   ("Write it down afterwards.", "A blameless postmortem with timeline, causes and owners for actions.")],
            answer=["First I would confirm the alert is real, declare an incident and set roles, so that one person leads and is not also debugging. I would ask what changed in the last hour, because most outages follow a change. If a change is the suspect, I would roll it back or switch off the feature right away, before I understand everything.",
                    "While that happens, someone posts an honest status update, and I keep a timeline as we go. Once users are served again, I would look for the real cause, and write a blameless postmortem within a few days with specific actions and owners. The Cloudflare 2019 outage is a good example: a global off switch ended the pain in minutes, and the lasting fixes came afterwards."],
            follow=[("What if rollback is not possible?", "Use a feature flag or kill switch, shed load, or fail over; have these ready beforehand."),
                    ("What if your own tools are down?", "Meta and Google both found this. Keep an out of band way in and a status page hosted elsewhere.")],
            slips=["Diving into root cause before stopping the harm.", "No communication to users or colleagues.", "Several people changing things at once with no lead."],
        )),
    dict(
        who="Reported by candidates for senior and SRE roles, not official.",
        scenario=dict(
            title="How would you write a good postmortem, and what makes one blameless?",
            ask="Explain what a useful postmortem contains and how you keep it from becoming a hunt for someone to blame.",
            clarify=[("Who reads it?", "Engineers, managers, sometimes customers. Write so a new joiner can follow it.")],
            think=[("Facts first.", "Dates, times, durations and impact, from logs not memory."),
                   ("A timeline.", "What happened, when, and what people knew at each point."),
                   ("Causes, plural.", "A trigger plus the conditions that let it become an outage."),
                   ("Actions with owners and dates.", "Each action reduces a specific risk."),
                   ("Blameless means system focused.", "Ask how the system allowed the mistake, not who made it.")],
            answer=["A good postmortem has a plain summary, the impact, a precise timeline, the causes, what went well and what did not, and a short list of actions with owners and dates. I would build the timeline from logs and chat history, not from memory, and state what we knew at each moment, so readers can see why decisions made sense at the time.",
                    "Blameless does not mean nobody is accountable. It means we assume people acted reasonably with what they knew, and ask how the system, tools and process let a normal mistake cause harm. GitLab's postmortem is a good model: it names the mistake, then asks why backups did not save them and lists specific follow-ups, including an owner for data durability."],
            follow=[("How do you stop the actions being forgotten?", "Track them in your normal ticket system, review them monthly and close the loop publicly."),
                    ("When would you not write one?", "Almost never for customer impact. Keep it shorter for small incidents.")],
            slips=["Listing a single root cause and stopping there.", "Actions with no owner or date.", "Naming individuals as the cause."],
        )),
]

DATA = dict(
    time="35 minutes",
    tagline="Six well documented public outages, retold in plain language: what happened, how it spread, what changed, and what to take back to your own system.",
    story=dict(
        title="Monday, 9:30 a.m.",
        paras=[
            "It has been a rough weekend at ShopKart. The pager went off four times, and by Sunday morning everyone has a theory about what went wrong. Your manager puts a coffee next to your keyboard and says: \"Before we argue about our own outage, read how the big ones went. I want to see what the pattern is.\"",
            "You expected the big companies to be a different species. They are not. A mistyped input, a backup nobody had tried to restore, a rule that nobody tested for cost: the same small human things, on a larger stage. The writing they published afterwards is some of the best teaching material in engineering.",
            "So this page is a set of **case files**. Each one is retold from the company's own postmortem, with the date, the timeline, the cause, the reason it spread and what they changed. At the end you will see the patterns, and you will turn them into a short list for ShopKart.",
        ],
        strip=STRIP),
    how_to_read=[
        "A **postmortem** (also called an incident review) is the written account of an outage after it is over. A good one is **blameless**: it asks how the system let a normal mistake cause harm, instead of asking who to punish. That is why companies can publish them.",
        "Read each one in the same order. What was the **trigger** (the small thing that started it)? What made it **spread** (the missing brake)? Why did it **last** (slow to detect, slow to restart, or missing access)? What did they **change**? The trigger is usually boring. The other three are where you learn.",
        "Be careful with numbers. Times differ by time zone, and a company's first estimate is often revised. Where a source is vague or two figures disagree, the case file says so in its note. Always read the original, which is linked under each case.",
    ],
    read_figure=READ_FIG,
    cases=CASES,
    patterns=[
        ("The trigger is small and ordinary", "A typo, a routine command, a regex, a blank field, a short network drop. If the only fix is \"be more careful\", you have not found the cause."),
        ("Nothing limited the blast radius", "S3, Cloudflare and Google all spread a mistake everywhere at once. Staged rollouts, minimum capacity limits and cell based design turn global failures into local ones."),
        ("The safety net had a hole", "GitLab's backups, Meta's audit tool and Cloudflare's removed CPU protection all failed quietly. Test the guard, not just the thing it guards."),
        ("Recovery was slower than the break", "Restores, restarts and replication catch up took hours in S3, GitLab, GitHub and Google. Time a full recovery before you need one."),
        ("The tools to fix it were affected", "AWS and Google's status pages and Meta's internal tools depended on the failing systems. Keep a separate way in and a separate way to talk."),
        ("Automatic helpers can make it worse", "GitHub's failover and Meta's DNS withdrawal did what they were designed to do, with an unexpected result. Ask what each automation does when everything fails together."),
    ],
    interview_intro="Incident questions test calm thinking more than facts. These three are shapes candidates report for operations and reliability roles.",
    interview=INTERVIEWS,
    recap=dict(
        points=["A postmortem is a blameless written account: trigger, spread, duration, changes.",
                "Small triggers cause big outages when nothing limits the blast radius.",
                "A backup you have not restored is only a hope; test restores on a schedule.",
                "Roll out changes, even rules and data, in stages with a metric watching each step.",
                "Keep a way in and a way to communicate that does not depend on the failing system.",
                "Add jitter to retries, and practise the full recovery, not only the failure."],
        quick=[("What makes a postmortem blameless?", "It asks how the system and process allowed a normal mistake to do damage, rather than who made it."),
               ("What did the S3 and Cloudflare cases have in common?", "A small change reached too much at once, because no limit or staged rollout stopped it."),
               ("Why did GitLab not simply restore a backup?", "The backup jobs had failed silently and the other options were unusable, so the best copy was a six hour old test snapshot.")]),
    deeper=[("Playbooks and runbooks", "S12_troubleshooting_playbooks.html"), ("Reliability practice", "S13_reliability_practice.html")],
)
