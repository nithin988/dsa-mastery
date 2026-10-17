"""Type-check Java snippets with javac.

Snippets are excerpts that use variables defined elsewhere (n, nums, g, ...), so 'cannot find symbol' is
expected and ignored. Every OTHER error (incompatible types, missing return, wrong method arguments, ...)
points at a real mistake in the snippet and is reported.
"""
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from snippets import snippets
from check_syntax import SYNTAX

IGNORE = re.compile(r"cannot find symbol|unexpected return value|missing return value|package .* does not exist|"
                    r"is already defined|might not have been initialized|variable .* not initialized", re.I)

MEMBERS = "import java.util.*;\nclass T%d {\n%s\n}\n"
STATEMENTS = "import java.util.*;\nclass T%d { Object m() throws Exception {\n%s\nreturn null; } }\n"


def main():
    all_s = list(snippets())
    work = tempfile.mkdtemp(prefix="jtyp")
    outdir = tempfile.mkdtemp(prefix="jout")
    kind = {}
    # pick wrapper: members if it parses, else statements (decide by a parse-only run)
    for pass_name, tmpl in (("members", MEMBERS), ("statements", STATEMENTS)):
        files = []
        for i, s in enumerate(all_s):
            if i in kind:
                continue
            p = os.path.join(work, f"{pass_name}_T{i}.java")
            os.makedirs(os.path.dirname(p), exist_ok=True)
            # file name must match the class name for javac: use a per-pass directory
            d = os.path.join(work, pass_name)
            os.makedirs(d, exist_ok=True)
            p = os.path.join(d, f"T{i}.java")
            open(p, "w", encoding="utf-8").write(tmpl % (i, s["java"]))
            files.append((i, p))
        r = subprocess.run(["javac", "-proc:none", "-Xlint:none", "-Xmaxerrs", "100000", "-d", outdir] + [p for _, p in files],
                           capture_output=True, text=True)
        errs = {}
        for line in r.stderr.splitlines():
            m = re.match(r"(.+?T(\d+)\.java):(\d+): error: (.*)", line)
            if m:
                errs.setdefault(int(m.group(2)), []).append((int(m.group(3)), m.group(4)))
        for i, _ in files:
            e = errs.get(i, [])
            if any(SYNTAX.search(x[1]) for x in e):
                continue            # does not parse in this wrapper
            kind[i] = (pass_name, [x for x in e if not IGNORE.search(x[1])])
        # a second full compile is needed once syntax errors disappear, because javac skips attribution
        # when any file has a parse error; do a clean semantic pass below
    # semantic pass over the chosen wrappers
    sem = {}
    for pass_name, tmpl in (("members", MEMBERS), ("statements", STATEMENTS)):
        d = os.path.join(work, "sem_" + pass_name)
        os.makedirs(d, exist_ok=True)
        files = []
        for i, (kname, _) in kind.items():
            if kname != pass_name:
                continue
            p = os.path.join(d, f"T{i}.java")
            open(p, "w", encoding="utf-8").write(tmpl % (i, all_s[i]["java"]))
            files.append(p)
        if not files:
            continue
        r = subprocess.run(["javac", "-proc:none", "-Xlint:none", "-Xmaxerrs", "100000", "-d", outdir] + files,
                           capture_output=True, text=True)
        for line in r.stderr.splitlines():
            m = re.match(r"(.+?T(\d+)\.java):(\d+): error: (.*)", line)
            if m and not IGNORE.search(m.group(4)):
                sem.setdefault(int(m.group(2)), []).append((int(m.group(3)), m.group(4)))
    print("snippets:", len(all_s), " wrapped OK:", len(kind))
    print("real type errors in", len(sem), "snippets")
    for i, e in sorted(sem.items()):
        s = all_s[i]
        print("  ", s["file"], "P%d" % s["pattern"], s["label"][:55], "->", e[:3])


if __name__ == "__main__":
    main()
