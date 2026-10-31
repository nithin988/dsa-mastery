"""Record the real output of every runnable command in the Systems Mastery modules.

  python verify/sys_record.py            record all live modules into build/sys_outputs.json
  python verify/sys_record.py sh         record one module (by id)
  python verify/sys_record.py --check    re-run everything and fail if the stored output differs

Commands run in order, in one bash session as an ordinary user, in a real Debian (WSL or Docker).
"""
import importlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "build"))
sys.path.insert(0, HERE)
import sys_runner  # noqa: E402
import syscatalog  # noqa: E402
from lib_sys import OUTPUTS_PATH, runnable  # noqa: E402

LABS = os.path.join(ROOT, "systems", "labs")
PREFIX = re.compile(r"^(?:/\S+|bash|rec\.sh): line \d+: ")


def live_modules():
    out = []
    for num, slug, title, blurb, track, modname in syscatalog.MODULES:
        if modname:
            try:
                out.append(importlib.import_module(modname).MODULE)
            except ModuleNotFoundError as e:
                if e.name != modname:
                    raise
    return out


def normalise(text):
    lines = [PREFIX.sub("bash: ", ln) for ln in text.replace("\r\n", "\n").split("\n")]
    return "\n".join(lines)


def record_module(m):
    cmds = runnable(m)
    files = {}
    pre = ["export LC_ALL=C TZ=UTC", 'D="$(dirname "$0")"',
           'find "$HOME" -mindepth 1 -maxdepth 1 ! -name ".*" -exec rm -rf {} +; rm -rf "$HOME"/.sys-lab-*   # clean slate: other modules leave files behind']
    for f in m.get("fixture_files", []):
        kind, name = f.split("/")
        files[name] = sys_runner.read(os.path.join(LABS, kind, name))
    pre += m.get("fixture_pre", [])
    pre += ["cd ~", "set +e"]
    body = []
    for i, c in enumerate(cmds):
        body.append(f'echo "@@B{i}"')
        body.append("{\n" + c["c"] + "\n} 2>&1")
        body.append(f'printf "\\n@@E{i}\\n"')
    files["rec.sh"] = "\n".join(pre + body) + "\n"
    rc, out = sys_runner.run_bash(files, "rec.sh", timeout=300)
    out = out.replace("\r\n", "\n")
    # progress lines overwrite themselves with a bare \r in a terminal: keep what stays on screen
    out = "\n".join(ln.split("\r")[-1] for ln in out.split("\n"))
    entries = []
    for i, c in enumerate(cmds):
        m1 = re.search(rf"@@B{i}\n(.*?)\n@@E{i}\n", out, re.S)
        if not m1:
            raise SystemExit(f"{m['id']}: no output captured for command #{i} {c['c'][:60]!r}\n--- raw output tail ---\n{out[-800:]}")
        e = {"cmd": c["c"], "out": normalise(m1.group(1))}
        if c.get("volatile"):
            e["volatile"] = True  # real output that changes on every run (PIDs, dates, addresses, timings)
        entries.append(e)
    return entries


def env_name():
    rc, out = sys_runner.run_bash({"e.sh": '. /etc/os-release; echo "$PRETTY_NAME"\n'}, "e.sh", 60)
    return out.strip().splitlines()[-1] if out.strip() else "Linux"


def main():
    args = [a for a in sys.argv[1:]]
    check = "--check" in args
    ids = [a for a in args if not a.startswith("--")]
    if sys_runner.backend() is None:
        print("SKIPPED: no Linux backend available (WSL Debian or Docker needed to record or check real output).")
        return 0
    mods = [m for m in live_modules() if not ids or m["id"] in ids]
    stored = {}
    if os.path.exists(OUTPUTS_PATH):
        stored = json.load(open(OUTPUTS_PATH, encoding="utf-8"))
    bad = 0
    env = env_name()
    for m in mods:
        new = record_module(m)
        if check:
            old = stored.get(m["id"], [])
            diffs = [i for i, (a, b) in enumerate(zip(old, new)) if a != b and not b.get("volatile")] + ([min(len(old), len(new))] if len(old) != len(new) else [])
            if diffs:
                bad += 1
                for i in diffs[:5]:
                    o = old[i] if i < len(old) else None
                    n = new[i] if i < len(new) else None
                    print(f"DIFF {m['id']} #{i}: {(n or o)['cmd'][:60]!r}\n  stored: {(o or {}).get('out', '')[:120]!r}\n  now:    {(n or {}).get('out', '')[:120]!r}")
            print(f"{m['id']}: {len(new)} commands, {'DIFFERENT' if diffs else 'unchanged'}")
        else:
            stored[m["id"]] = new
            print(f"{m['id']}: recorded {len(new)} commands")
    if not check:
        stored["_env"] = env
        with open(OUTPUTS_PATH, "w", encoding="utf-8", newline="\n") as f:
            json.dump(stored, f, indent=1, ensure_ascii=False)
        print("wrote", OUTPUTS_PATH, "| environment:", env)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
