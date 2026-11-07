"""Systems Mastery S08: containers and cloud basics (real Linux namespaces and limits as an ordinary user, image layers, a permission model)."""

LESSONS = [
    dict(
        title="What a container really is: isolated views and resource limits",
        tier="hot",
        situation="\"It works on my machine\" ends when the program carries its own filesystem and its own view of the machine. A container is not a small virtual computer. It is an ordinary Linux process that has been given a private view of processes, hostnames and networks, and a ceiling on the resources it may use.",
        learn=["Namespaces: a private view of the system", "Limits: a ceiling on memory and CPU", "Why containers start in milliseconds and share the host kernel"],
        model=[
            "A **container** is a normal process (or group of processes) started with three kernel features. **Namespaces** give it its own view: its own process tree (it sees itself as process 1), its own hostname, its own network interfaces, its own mounts and users. **Control groups (cgroups)** and resource limits cap what it may use (memory, CPU, number of processes). And an **image** supplies the files it sees as its root. There is **no second operating system**: all containers on a machine share the host's kernel, which is why they start in milliseconds and use little memory, and also why a kernel bug can affect every container.",
            "A **virtual machine** is different: a hypervisor runs a **whole guest operating system** with its own kernel on emulated hardware: stronger isolation, heavier, slower to start. Containers trade some isolation for speed and density. Security therefore depends on keeping the container unprivileged, dropping capabilities and limiting what it can reach. Docker, containerd and Kubernetes are tools that automate these kernel features; you can see the features themselves with plain commands.",
        ],
        analogy="Rooms in a shared house: each room has its own door, its own thermostat label and its own power limit, but the walls, plumbing and wiring (the kernel) are shared. A virtual machine is a separate house.",
        sim=None,
        walk=[
            ("Start a process in new namespaces", "`unshare` asks the kernel for a private process tree, hostname or network."),
            ("The process sees only its own world", "It believes it is process 1 and it cannot see the host's other processes."),
            ("Put a ceiling on resources", "A memory limit makes a runaway allocation fail instead of taking the machine down."),
            ("Give it its own files", "An image (next lesson) provides the root filesystem."),
        ],
        groups=[
            dict(title="Namespaces and limits you can run without root", cmds=[
                dict(c=r'''echo "--- a private process tree (new PID namespace):"
unshare --user --map-root-user --pid --fork --mount-proc sh -c 'echo "inside: this shell is process $$"; ps -e -o pid,comm | head -4'
echo "--- a private hostname (new UTS namespace):"
unshare -Ur --uts sh -c 'hostname boxed; echo "inside: $(hostname)"'; [ "$(hostname)" != boxed ] && echo "outside: the real hostname is unchanged"
echo "--- a private network (new network namespace): only a loopback interface exists:"
unshare -Urn sh -c 'cat /proc/net/dev | tail -n +3 | cut -d: -f1 | tr -d " "'
echo "--- a memory ceiling (150 MB) on a process that wants 400 MB:"
prlimit --as=150000000 python3 -c 'x = bytearray(400 * 1024 * 1024); print("allocated")' 2>&1 | tail -1''',
                     e="The building blocks of a container, as an ordinary user. In a new **PID namespace** the shell is process 1 and the process list shows only its own children: a container's \"private machine\". A new **UTS namespace** lets it set its own hostname without changing the host's. A new **network namespace** starts with only a loopback interface: no connectivity until something is wired in. And a **memory limit** turns a 400 MB allocation into a `MemoryError` instead of exhausting the host. Docker automates exactly these steps, adds an image filesystem, and applies cgroup limits.",
                     annot=[("inside: this shell is process 1", "in its own PID namespace the first process is process 1"),
                            ("PID COMMAND ... 1 sh / 2 ps / 3 head", "the process list shows only processes inside the namespace"),
                            ("inside: boxed / outside: the real hostname is unchanged", "a private hostname that does not leak to the host"),
                            ("lo", "the only network interface in a fresh network namespace"),
                            ("MemoryError", "the limit stopped a 400 MB allocation under a 150 MB ceiling")]),
            ]),
        ],
        scenario=dict(
            title="\"What is a container, and how is it different from a virtual machine?\"",
            ask="A foundation question for any backend or platform role. They want the kernel mechanisms, not a marketing definition.",
            clarify=[("Is the interviewer after the definition, or the security and performance trade-offs?", "Give the mechanism first, then the trade-offs.")],
            think=[("Define it by mechanism.", "A container is a process with namespaces (isolated views of processes, network, mounts, hostnames, users), cgroup limits on resources, and an image as its root filesystem."),
                   ("Contrast with a VM.", "A VM runs a full guest OS with its own kernel on virtual hardware via a hypervisor; a container shares the host kernel."),
                   ("State the consequences.", "Containers start fast, use less memory and pack densely; isolation is weaker, so a kernel vulnerability or a privileged container can affect the host."),
                   ("Mention hardening.", "Run as a non-root user, drop capabilities, read-only root filesystem, seccomp profiles, and for stronger isolation sandboxed runtimes or micro-VMs."),
                   ("Link to orchestration.", "Kubernetes schedules containers onto machines, restarts them, and wires networking and storage.")],
            answer=["\"A container is an ordinary Linux process that the kernel gives a private view of the system: its own process tree, hostname, network and mounts through namespaces, a ceiling on memory and CPU through cgroups, and a root filesystem from an image. It does not run its own operating system: all containers share the host's kernel.",
                    "A virtual machine runs a complete guest OS with its own kernel on virtual hardware, so it isolates more strongly but is heavier and slower to start. Containers start in milliseconds and pack densely, at the cost of weaker isolation, so I run them unprivileged, drop capabilities and use seccomp, and use sandboxed runtimes where I need stronger separation.\""],
            follow=[("What are cgroups?", "Kernel control groups that limit and account for a set of processes' CPU, memory, I/O and process count."),
                    ("Can a container run a different kernel?", "No: it shares the host kernel (a Linux container needs a Linux kernel; on other systems a hidden VM supplies one)."),
                    ("Why is running as root in a container risky?", "Root inside may map to root on the host if isolation is weak, and a kernel or runtime bug can become a host compromise.")],
            slips=["Saying a container is a lightweight VM.", "Not mentioning the shared kernel.", "Ignoring security hardening."],
        ),
        quick=[("What gives a container its own process tree?", "A PID namespace."), ("What limits a container's memory?", "A cgroup limit (or a resource limit such as prlimit)."), ("Do containers have their own kernel?", "No, they share the host's kernel.")],
        traps=["Treating containers as a security boundary equal to VMs.", "Running everything as root inside the container.", "No memory limit: one container can take down the host."],
    ),
    dict(
        title="Images and layers: why builds are fast and images are small",
        tier="hot",
        situation="Pulling an image takes seconds when most of it is already on the machine, and a build takes a minute when you changed one line. Both come from the same idea: an image is a stack of read-only layers, each identified by the hash of its content.",
        learn=["Layers as content-addressed archives", "Sharing layers between images", "Build caching and why instruction order matters"],
        model=[
            "An **image** is a stack of **layers**, each a compressed archive of the files that one build step added or changed, identified by the **hash of its content**. Two images built on the same base share the **same base layer**: it is stored and downloaded once. A running container adds a thin writable layer on top. Because layers are content-addressed, pulling an image only downloads the layers you do not already have, and pushing uploads only the new ones.",
            "A **build** runs the instructions in order, producing one layer per step, and **caches** each step: if the instruction and everything before it are unchanged, the cached layer is reused. So **order matters**: put the slow, rarely changing steps (installing dependencies) **before** the fast, frequently changing ones (copying your source), or every code change will reinstall everything. Keep images **small** (a minimal base, multi-stage builds, no build tools or caches left behind), because size is pull time, startup time and attack surface.",
        ],
        analogy="A stack of transparent sheets, each with a layer of a drawing. Two drawings that share the same bottom sheets use the same physical sheets. Redrawing the top sheet is quick; changing the bottom one means redrawing everything above it.",
        sim=None,
        walk=[
            ("Each build step produces a layer", "A tar archive of the changes, named by its hash."),
            ("Images list their layers", "Two images with the same base reference the same layer."),
            ("Pull only what is missing", "Existing layers are reused."),
            ("The build cache reuses unchanged steps", "A change invalidates that step and everything after it."),
            ("Order instructions by how often they change", "Dependencies first, source last."),
        ],
        groups=[
            dict(title="Layers as hashes, and a build cache that is only as good as your order", cmds=[
                dict(c=r'''mkdir -p ~/img && cd ~/img && rm -rf base appA appB && mkdir base appA appB
python3 - <<'EOF'
import random
rng = random.Random(1)
open('base/os.bin', 'wb').write(bytes(rng.getrandbits(8) for _ in range(300_000)))      # a 300 KB "operating system" layer
open('appA/app.py', 'w').write('print("service A")\n' * 50); open('appB/app.py', 'w').write('print("service B")\n' * 80)
EOF
layer() { tar --sort=name --mtime='2020-01-01' --owner=0 --group=0 --numeric-owner -cf $1.tar -C $1 . ; }
for d in base appA appB; do layer $d; done
for d in base appA appB; do echo "layer $d: sha256 $(sha256sum $d.tar | cut -c1-12), $(stat -c %s $d.tar) bytes"; done
echo "image A = base + appA     image B = base + appB"
naive=$(( $(stat -c %s base.tar) * 2 + $(stat -c %s appA.tar) + $(stat -c %s appB.tar) )); shared=$(( $(stat -c %s base.tar) + $(stat -c %s appA.tar) + $(stat -c %s appB.tar) ))
echo "if every image carried its own copy: $naive bytes;  with shared layers: $shared bytes (the base is stored once)"
layer base; echo "rebuilding the base from the same files gives the same hash: $(sha256sum base.tar | cut -c1-12)"''',
                     e="Layers are just archives named by their hash. The base layer has one hash no matter which image uses it, so both images **point at the same layer** and the machine stores and downloads it once. Rebuilding the base from identical files reproduces the **same hash** (the tar options fix timestamps and owners so the archive is deterministic), which is what makes the cache and registry work: identical content means identical identity.",
                     annot=[("layer base: sha256 ... , 300xxx bytes", "the big shared layer, identified by the hash of its content"),
                            ("layer appA / appB: different hashes, small sizes", "the application layers differ and are small"),
                            ("with shared layers: ... bytes (the base is stored once)", "images on a shared base cost only their own extra layers"),
                            ("rebuilding the base ... the same hash", "identical content gives identical identity: the basis of caching")]),
                dict(c=r'''python3 - <<'EOF'
import hashlib
def build(steps, cache):
    """steps: list of (instruction, content_hash). A step is reused only if it and every step before it are unchanged."""
    ran, parent = [], ''
    for instr, content in steps:
        key = hashlib.sha256((parent + instr + content).encode()).hexdigest()[:8]
        if key in cache: ran.append('cached  ' + instr)
        else: ran.append('REBUILD ' + instr); cache.add(key)
        parent = key
    return ran
good = lambda src, deps: [('FROM base-os', ''), ('COPY requirements.txt', deps), ('RUN install dependencies (60 s)', deps), ('COPY src/', src)]
bad = lambda src, deps: [('FROM base-os', ''), ('COPY . (source and requirements)', src + deps), ('RUN install dependencies (60 s)', src + deps)]
for name, f in (('good order: dependencies first, source last', good), ('bad order: copy everything first', bad)):
    cache = set(); build(f('src-v1', 'deps-v1'), cache)
    print(name)
    r = build(f('src-v2', 'deps-v1'), cache)
    print('  after changing one line of source:'); [print('     ', x) for x in r]
    print('  slow steps rebuilt:', sum('60 s' in x and x.startswith('REBUILD') for x in r))
EOF''',
                     e="Why instruction order decides build time. With the **good order**, the dependencies are installed in a layer that depends only on `requirements.txt`, so changing one line of source rebuilds only the last copy step and reuses the 60-second install from the cache. With the **bad order**, copying the whole source tree first means any source change invalidates that layer and **everything after it**, so the slow install runs again on every build. The same rule applies to any layered build cache: put what changes least first.",
                     annot=[("good order ... COPY src/ REBUILD, the install cached", "only the step whose inputs changed (and anything after it) is rebuilt"),
                            ("slow steps rebuilt: 0 (good) vs 1 (bad)", "the dependency install is reused in one ordering and repeated in the other")]),
            ]),
        ],
        scenario=dict(
            title="\"Our container image is 2 GB and every build takes 10 minutes. How do you fix it?\"",
            ask="A practical platform question. They want layers, cache order, image size and multi-stage builds.",
            clarify=[("What is in the image, how is it built, and how often does the source change?", "Usually: a fat base, build tools left in, dependencies reinstalled on every change.")],
            think=[("Explain layers and the cache.", "Each step is a cached layer; a change invalidates that step and everything after it."),
                   ("Fix the order.", "Base image, then system packages, then copy the dependency manifest and install, then copy the source: source changes rebuild only the last layer."),
                   ("Shrink the image.", "Minimal base (slim or distroless), multi-stage build so compilers and build caches stay in the build stage, remove package caches in the same step that creates them, a `.dockerignore` for junk."),
                   ("Speed up CI.", "Reuse a remote build cache between runs, build in parallel, pin dependency versions so the cache is stable."),
                   ("Check security and reproducibility.", "Pin base image digests, scan images, avoid secrets in layers (they stay in history)."),
                   ("Measure.", "Image size, pull time, build time before and after, and layers by size.")],
            answer=["\"I would look at the layers. An image is a stack of cached layers and a change invalidates its step and everything after, so I would reorder the build: install dependencies from the manifest first, copy the source last, so a code change rebuilds only the final layer.",
                    "For size I would use a minimal base, a multi-stage build so compilers and caches stay out of the final image, remove package caches in the same step that creates them, and add a dockerignore. In CI I would reuse a remote build cache between runs. I would also pin the base image digest and check that no secret is baked into a layer, since layers keep history. Then I would measure image size, pull time and build time before and after.\""],
            follow=[("What is a multi-stage build?", "A Dockerfile with several stages: build in a fat stage, copy only the artefacts into a small final stage."),
                    ("Why can a secret in an early layer be a problem even if you delete it later?", "Layers are immutable and kept: the file remains in the earlier layer's archive."),
                    ("What does the writable container layer do?", "It holds the container's changes on top of the read-only image layers; it disappears when the container is removed.")],
            slips=["Copying the whole source before installing dependencies.", "Leaving build tools and caches in the final image.", "Baking credentials into layers."],
        ),
        quick=[("What identifies a layer?", "The hash of its content."), ("Why put dependency installation before copying the source?", "So source changes do not invalidate the slow install layer."), ("How do two images share storage?", "They reference the same layers by hash.")],
        traps=["`COPY . .` before the dependency install: every code change reinstalls everything.", "Secrets written into a layer, then deleted in a later one.", "Using `latest` tags: builds are not reproducible."],
    ),
    dict(
        title="The cloud in one page: regions, zones and who is allowed to do what",
        tier="hot",
        situation="Moving to the cloud does not remove the old problems, it changes the vocabulary: failure domains are zones and regions, and security is mostly about who is allowed to call which API. Two ideas explain most of it.",
        learn=["Regions and availability zones as failure domains", "Identity and access management: default deny, explicit deny wins", "Least privilege in practice"],
        model=[
            "A cloud provider is organised into **regions** (a geographic area, for example a metro region) containing several **availability zones** (separate data centres with independent power and networking, close enough for low-latency links). A zone is a **failure domain**: spread copies of a service across zones to survive the loss of one; spread across regions to survive the loss of a region, at the cost of latency and complexity. Latency within a zone is sub-millisecond, between zones a millisecond or two, between regions tens to hundreds of milliseconds. **Managed services** (databases, queues, object storage) shift operations to the provider but still need you to choose zones, backups and access.",
            "Almost everything in the cloud is an **API call**, and **identity and access management (IAM)** decides which identities (people, services) may call which API on which resource. The core rules: **everything is denied by default**; an **allow** statement grants specific actions on specific resources; an **explicit deny always wins**. **Least privilege** means giving each identity only the actions and resources it needs, using **roles** assumed temporarily instead of long-lived keys. Most cloud breaches are not exotic exploits but over-broad permissions, exposed storage buckets and leaked keys.",
        ],
        analogy="A building with several floors on separate power supplies (zones) in several cities (regions), and a badge system where doors are locked by default, each badge opens only the doors written on it, and a \"never this door\" rule overrides everything.",
        sim=None,
        walk=[
            ("Pick regions and zones for the failure you want to survive", "Zones for a data centre loss, regions for a regional outage."),
            ("Give every workload an identity", "A role, not a shared key."),
            ("Write allow statements for exactly what is needed", "Specific actions on specific resources."),
            ("Add explicit denies for the dangerous cases", "They override every allow."),
            ("Review and shrink permissions over time", "Remove what is never used."),
        ],
        groups=[
            dict(title="A permission model, evaluated step by step", cmds=[
                dict(c=r'''python3 - <<'EOF'
from fnmatch import fnmatch
POLICY = [
    {'effect': 'Allow', 'action': 'storage:Get*', 'resource': 'bucket/shop-images/*'},
    {'effect': 'Allow', 'action': 'storage:Put*', 'resource': 'bucket/shop-uploads/*'},
    {'effect': 'Deny',  'action': 'storage:*',    'resource': 'bucket/shop-images/private/*'},
]
def allowed(action, resource):
    matches = [s for s in POLICY if fnmatch(action, s['action']) and fnmatch(resource, s['resource'])]
    if any(s['effect'] == 'Deny' for s in matches): return 'DENY (an explicit deny always wins)'
    if any(s['effect'] == 'Allow' for s in matches): return 'allow'
    return 'DENY (nothing allows it: denied by default)'
for a, r in (('storage:GetObject', 'bucket/shop-images/logo.png'),
             ('storage:GetObject', 'bucket/shop-images/private/passport.jpg'),
             ('storage:PutObject', 'bucket/shop-uploads/new.jpg'),
             ('storage:PutObject', 'bucket/shop-images/logo.png'),
             ('storage:DeleteObject', 'bucket/shop-uploads/new.jpg'),
             ('database:Query', 'db/orders')):
    print('%-22s %-42s -> %s' % (a, r, allowed(a, r)))
EOF''',
                     e="The two rules that explain most IAM behaviour. A request is allowed only if some statement allows that action on that resource; if nothing matches it is denied by default (writing to the images bucket, deleting an upload, querying a database the role was never given). Reading an image is allowed, but reading under the `private/` prefix is blocked by an **explicit deny, which beats the allow** that would otherwise cover it. Real policy languages add conditions and principals, but the evaluation order is the same.",
                     annot=[("GetObject bucket/shop-images/logo.png -> allow", "a matching allow and no deny"),
                            ("GetObject .../private/passport.jpg -> DENY (an explicit deny always wins)", "the deny overrides the broader allow"),
                            ("PutObject bucket/shop-images/logo.png -> DENY (nothing allows it)", "the role may write uploads, not images: default deny"),
                            ("database:Query db/orders -> DENY (nothing allows it)", "no statement covers it, so it is denied")]),
            ]),
        ],
        scenario=dict(
            title="\"How would you give a service access to one storage bucket and nothing else?\"",
            ask="A cloud basics and security question. They want roles, least privilege and the evaluation rules.",
            clarify=[("Read or write? Which prefix? Does it run in the cloud or outside?", "Scope the action and the resource as tightly as possible.")],
            think=[("Use a role, not a key.", "Attach an identity (role) to the workload so it receives short-lived credentials; no long-lived access keys in config."),
                   ("Write the narrowest allow.", "Only the needed actions (get and list, or put) on only that bucket or prefix."),
                   ("Add explicit denies for risks.", "For example deny access to a sensitive prefix, or deny any request not using TLS."),
                   ("Remember the defaults.", "Everything not allowed is denied; an explicit deny overrides allows."),
                   ("Review.", "Use access analysis tools and logs to remove unused permissions; rotate credentials where keys are unavoidable; alert on unusual access."),
                   ("Say why.", "A leaked or compromised service should only be able to touch one bucket.")],
            answer=["\"I would give the service a role with short-lived credentials rather than a long-lived key, and attach a policy that allows only the specific actions it needs, for example get and list, on that one bucket or prefix. Everything else is denied by default, and I would add an explicit deny for anything sensitive, since an explicit deny always overrides an allow.",
                    "Then I would use access analysis and audit logs to remove permissions that are never used, alert on unusual access, and make sure the bucket itself is not public. The point is that if this service is ever compromised, the damage is limited to that one bucket.\""],
            follow=[("What is the difference between a role and a user?", "A role is an identity assumed temporarily by a service or person, with short-lived credentials; a user is a long-lived identity with its own credentials."),
                    ("Why are public storage buckets so often in breach stories?", "Defaults or mistakes grant public read; block public access at the account level and audit it."),
                    ("How do zones relate to resilience?", "Spread replicas across zones so the loss of a data centre leaves the service running.")],
            slips=["Using one broad administrator key for convenience.", "Wildcard actions and resources.", "Keys committed to repositories."],
        ),
        quick=[("What wins when an allow and a deny both match?", "The explicit deny."), ("What happens to a request that no statement allows?", "It is denied by default."), ("What is an availability zone?", "A separate data centre within a region: a failure domain.")],
        traps=["Wildcards (`*`) in both action and resource.", "Long-lived access keys instead of roles.", "A single zone for a service that must stay up."],
    ),
]

MODULE = dict(
    id="ct",
    deep=True,
    title="Containers and cloud basics",
    lead="What a container really is, shown with the kernel features themselves (a private process tree, hostname and network, and a memory ceiling, all as an ordinary user), how image layers make builds fast and images small, and the two ideas behind most cloud thinking: failure domains and default-deny permissions.",
    time="4 to 5 hours",
    why=["Containers and the cloud are the default way software is run today. Knowing what is underneath removes the mystery and makes debugging, security and cost much easier."],
    outcomes=["Explain a container by its kernel mechanisms and contrast it with a VM.", "Explain image layers, content addressing and build cache order.", "Explain regions, zones and IAM default-deny with explicit deny precedence."],
    before=["The Linux internals (S04) and networking (S07) modules help. Everything here runs as an ordinary user on Linux; no Docker installation is needed to see the mechanisms."],
    env=["The commands create small scratch folders in your home directory."],
    lessons=LESSONS,
    labs=[],
    cases=[],
    cheat=[["namespace", "a private view: PID, network, mount, hostname, users"], ["cgroup / limit", "a ceiling on memory, CPU and processes"], ["container vs VM", "shares the host kernel vs runs its own kernel"], ["image layer", "an archive named by its content hash; shared between images"], ["build cache", "a changed step invalidates every step after it: order by how often things change"], ["multi-stage build", "build in a fat stage, ship only artefacts"], ["zone / region", "data centre failure domain / geographic area"], ["IAM", "default deny; allow is specific; explicit deny wins; least privilege; roles over keys"]],
    interview_intro="Reference module behind the Systems Mastery chapter on containers and the cloud.",
    interview=[],
    selftest=[("What gives a container its own process tree?", "A PID namespace.")],
    recall=[["container", "process + namespaces + limits + image"]],
    sources=[
        dict(title="Linux man page: namespaces(7)", url="https://man7.org/linux/man-pages/man7/namespaces.7.html", use="Every namespace type used in the experiments", license="Copyright the Linux man-pages project; read online", how="Link only"),
        dict(title="Open Container Initiative: image specification", url="https://github.com/opencontainers/image-spec", use="Layers, manifests and content-addressable digests", license="Apache 2.0; read online", how="Link only"),
        dict(title="AWS IAM: policy evaluation logic", url="https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html", use="Default deny and explicit deny precedence in a real policy system", license="Copyright Amazon; read online", how="Link only"),
    ],
    plan=["Run each experiment and change a number or a path."],
)
