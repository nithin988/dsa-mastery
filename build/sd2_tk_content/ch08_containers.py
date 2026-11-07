"""Chapter 8: Boxes inside boxes (containers: namespaces and limits, image layers and build cache, IAM default deny)."""
import sd2kit as k
from sd2 import scen


def _rect(x, y, w, h, kind, text=None, tkind="sd-l", ty=None):
    out = f'<rect class="sd-sh {kind}" x="{x}" y="{y}" width="{w}" height="{h}" rx="9"/>'
    if text:
        out += f'<text class="{tkind}" x="{x + w / 2:g}" y="{ty if ty is not None else y + h / 2 + 4:g}" text-anchor="middle">{text}</text>'
    return out


def _txt(x, y, text, cls="sd-c", anchor="middle"):
    return f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{text}</text>'


# ----------------------------------------------------------------------------- pictures
STRIP = k.strip([
    {"title": "Last week", "kind": "warn",
     "scene": lambda cx, cy, w: k.server(cx, cy + 12, "one shared server", "warn") + k.badge(cx - 46, cy - 44, "checkout", "ok") + k.badge(cx + 48, cy - 44, "resizer", "warn"),
     "caption": "Priya's photo resizer and the checkout code live side by side on one server."},
    {"title": "1:48 a.m.", "kind": "bad",
     "scene": lambda cx, cy, w: k.server(cx - 40, cy + 12, "", "bad") + k.alert(cx + 40, cy + 6, None) + k.badge(cx, cy - 44, "memory 100%", "bad"),
     "caption": "The resizer eats all the memory. Linux stops the biggest process: checkout."},
    {"title": "With boxes", "kind": "ok",
     "scene": lambda cx, cy, w: k.scaled(k.server(cx - 74, cy + 12, "", "ok") + k.server(cx, cy + 12, "", "ok") + k.server(cx + 74, cy + 12, "", "ok"), cx, cy + 12, .64) + k.badge(cx, cy + 52, "each with a ceiling", "ok"),
     "caption": "Each program in its own container. The runaway one stops; the rest carry on."},
], "ShopKart's shared server, three moments", "The same programs, with and without a box around each.")

_names = [("checkout", "ok"), ("resizer", "warn"), ("search", "ok")]
_boxes = []
for _i, (_n, _kind) in enumerate(_names):
    _x = 36 + _i * 230
    _boxes.append(_rect(_x, 52, 188, 140, "acc" if _kind == "ok" else "warn"))
    _boxes.append(_txt(_x + 94, 76, _n, "sd-l"))
    _boxes.append(_txt(_x + 94, 100, "own process list"))
    _boxes.append(_txt(_x + 94, 118, "own network"))
    _boxes.append(_txt(_x + 94, 136, "own files"))
    _boxes.append(k.badge(_x + 94, 170, "memory ceiling", "warn" if _kind == "warn" else "ok"))

IDEA_FIG = k.figure(720, 272, [
    _rect(20, 14, 680, 196, "", None),
    _txt(36, 36, "One Linux machine, one kernel underneath", "sd-l", "start"),
    "".join(_boxes),
    k.note(360, 234, "A container is an ordinary process with a private view and a ceiling.", "acc"),
    k.note(360, 258, "It shares the machine's kernel. A virtual machine does not.", ""),
], "Three containers on one machine", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


HOW = [
    ("A private view and a ceiling",
     "A **namespace** gives a process its own view of one thing: its own list of processes, its own hostname, its own network. Inside, the first process is number 1 and the machine seems to be its own. **Limits** cap what a process may use. In the recorded run a process that asked for 400 MB under a 150 MB ceiling got an error, and nothing else was harmed.",
     _small([_rect(20, 12, 240, 78, "acc"), _txt(140, 34, "inside the box", "sd-l"), _txt(140, 56, "process list: only itself"), _txt(140, 74, "network: only lo"),
             k.gauge(350, 54, 100, "asks 400 MB", "bad"), k.flow(390, 52, 466, 52, "bad"), k.badge(548, 52, "150 MB ceiling", "warn"), k.note(548, 82, "MemoryError", "bad")], "Namespaces and limits", h=108)),
    ("An image is stacked layers",
     "An **image** is the finished package your container starts from. It is a stack of read only **layers**, each named by a hash of its contents, so the same contents always get the same name. Two images on the same base store that base only once.",
     _small([_rect(40, 14, 190, 34, "acc", "app A: 10,240 bytes"), _rect(250, 14, 190, 34, "acc", "app B: 10,240 bytes"), _rect(40, 56, 400, 34, "ok", "shared base layer: 307,200 bytes"),
             k.note(550, 40, "two images,", "acc"), k.note(550, 60, "one copy of the base", "ok")], "Layers shared between images", h=106)),
    ("Order the build for the cache",
     "A build step is reused only if it and every step before it are unchanged. Put slow steps that rarely change (installing dependencies) first, and the code you edit all day last. Then a one line change rebuilds one cheap step instead of a 60 second install.",
     _small([k.note(60, 34, "good order", "ok"), k.badge(170, 30, "base: cached", "ok"), k.badge(330, 30, "deps, 60 s: cached", "ok"), k.badge(500, 30, "src: rebuilt", "warn"),
             k.note(60, 80, "bad order", "bad"), k.badge(170, 76, "base: cached", "ok"), k.badge(330, 76, "copy all: rebuilt", "warn"), k.badge(500, 76, "deps, 60 s: rebuilt", "bad")], "Build cache and instruction order", h=104)),
    ("Give each box only the permissions it needs",
     "In the cloud, **IAM** (identity and access management) says who may do what to which resource. The safe rule is **default deny**: nothing is allowed unless a policy allows it, and an explicit deny always beats an allow.",
     _small([k.server(60, 52, "resizer role"), k.flow(92, 22, 292, 22, "ok"), k.flow(92, 52, 292, 52, "ok"), k.flow(92, 82, 292, 82, "bad", dash=True),
             k.badge(410, 22, "read shop-images: allow", "ok"), k.badge(410, 52, "write shop-uploads: allow", "ok"), k.badge(410, 82, "database: denied", "bad")], "IAM default deny", h=116)),
]

DATA = dict(
    time="20 minutes",
    tagline="A container is an ordinary program with a private view of the machine and a ceiling on what it may use. Learn how that works, how to build small fast images, and how to give each box only the permissions it needs.",
    story=dict(
        title="Sunday, 1:48 a.m.",
        paras=[
            "ShopKart has just added photo uploads, and Priya wrote a small program, the resizer, that shrinks each photo. It works perfectly on her laptop. On the shop's one server it needs a different version of an image library from the one the checkout code uses, so you install both side by side, carefully, and tell nobody. \"It works on my machine\" is now true on two machines.",
            "At 1:48 a.m. the pager goes off: checkout is down. The memory dial is at 100%. A customer uploaded a huge photo, the resizer kept asking for more memory, and Linux, to keep the machine alive, stopped the largest program it could find. That was checkout, not the resizer. Your own program killed the thing that earns money.",
            "By morning the fix is clear: give each program its own box, with its own files and a memory ceiling, so a runaway stops alone. That box is a **container**. Two more rules make containers safe in the cloud: build the package so that rebuilds are quick, and give every box only the permissions it needs. This chapter covers all three.",
        ],
        strip=STRIP),
    idea=dict(
        title="The idea: a private view and a ceiling",
        one="A **container** is not a tiny computer. It is an ordinary process that the Linux kernel has given a private view (its own process list, hostname, network and files) and a ceiling (a limit on memory and CPU).",
        figure=IDEA_FIG,
        paras=["Because containers share the machine's kernel, they start in a fraction of a second and cost almost nothing to run. The price is weaker isolation than a virtual machine, which carries a whole kernel of its own. That trade is why containers suit your own services, and why the permissions you give them matter so much."]),
    how=HOW,
    try_intro=["Four experiments, all run as an ordinary user. First, build a box and hit its ceiling. Then see why images share layers, why instruction order changes build time, and how default deny decides every request."],
    **{"try": [
        ("ct", 0, 0, 0, "A box and a ceiling, built in four commands"),
        ("ct", 1, 0, 0, "Layers named by their contents, and shared"),
        ("ct", 1, 0, 1, "The same code change, in a good and a bad build order"),
        ("ct", 2, 0, 0, "Default deny, step by step"),
    ]},
    breaks=[
        ("No memory limit", "One leak takes the whole machine, and the kernel picks its own victim, which may be the wrong program. Fix: set a memory and CPU limit on every container, and alert well before the ceiling.", "bad"),
        ("Huge, slow images", "Everything copied in, nothing ordered: the image is large and every build repeats the slow steps. Fix: a small base, only runtime files in the final image, dependencies first and source last.", ""),
        ("Secrets baked into a layer", "A password copied into an early layer stays in the image history even if a later step deletes the file, because layers are only ever added. Fix: pass secrets in when the container starts, never copy them in.", "bad"),
        ("Running as root inside", "By default the process may run as the root user inside the box, and a mistake or a bug can then reach further than it should. Fix: run as an ordinary user and drop the extra capabilities.", ""),
        ("A policy that allows everything", "A policy with action `*` on resource `*` works today and is the quickest way to leak customer data tomorrow. Fix: start from nothing, add one allow per real need, and review it against the access logs.", "bad"),
        ("A moving base tag", "`FROM base:latest` builds a different image next month from the same recipe. Fix: pin a version, or better a digest, and rebuild on purpose.", ""),
    ],
    real=[
        dict(company="Linux man pages", text="The `namespaces(7)` page describes a namespace as wrapping a global system resource in an abstraction, so that processes inside it see their own isolated instance of that resource.", url="https://man7.org/linux/man-pages/man7/namespaces.7.html", source="namespaces(7), Linux manual page"),
        dict(company="Docker", text="The documentation on build cache describes that once a layer changes, every layer after it must be rebuilt, which is why the order of instructions matters.", url="https://docs.docker.com/build/cache/", source="Docker docs: Build cache"),
        dict(company="Amazon Web Services", text="The IAM documentation on policy evaluation describes that requests are denied by default, that an explicit allow can permit them, and that an explicit deny overrides any allow.", url="https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html", source="AWS IAM: Policy evaluation logic"),
    ],
    real_tag="Primary sources",
    real_title="Where this is written down",
    real_note="Summaries of public documentation; read the linked page for the exact wording.",
    interview=[dict(scenario=scen("ct", 0), who="A very common basics question: reported by candidates, not official."),
               dict(scenario=scen("ct", 1), who="A common practical prompt: reported by candidates, not official."),
               dict(scenario=scen("ct", 2), who="A common cloud security prompt: reported by candidates, not official.")],
    interview_sub="Say your answer aloud first, then compare with the model answer. These are the shapes of question candidates report, not official lists.",
    recap=dict(
        points=["A container is an ordinary process with a private view (namespaces) and a ceiling (limits).",
                "Containers share the host kernel, so they start fast and isolate less than a virtual machine.",
                "An image is a stack of read only layers named by a hash of their contents; shared layers are stored once.",
                "A build step is cached only if it and everything before it is unchanged: slow and stable steps first.",
                "Cloud permissions are default deny: nothing works until a policy allows it, and an explicit deny wins.",
                "Give every service its own role with the smallest set of allows that makes it work."],
        quick=[("What is a container, and how is it different from a virtual machine?", "A container is a process with its own view and limits, sharing the host kernel. A virtual machine runs a full operating system with its own kernel, so it isolates more and costs more."),
               ("Why does the order of lines in a build file change the build time?", "A step is reused only if it and every earlier step are unchanged. Put slow, rarely changing steps first and your source code last."),
               ("What does default deny mean for a cloud role?", "Everything is refused unless a policy explicitly allows it, and an explicit deny beats any allow, so you grant the minimum and add more only when something needs it.")]),
    deeper=[("What a container really is", "S08_containers_cloud_basics.html#l1"), ("Images and layers", "S08_containers_cloud_basics.html#l2"), ("The cloud in one page", "S08_containers_cloud_basics.html#l3")],
)
