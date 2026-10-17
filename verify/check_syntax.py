"""Syntax-check every Python snippet (ast.parse) and every Java snippet (javac parse errors only)."""
import ast
import os
import re
import subprocess
import sys
import tempfile
import textwrap

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from snippets import snippets

SYNTAX = re.compile(r"(?<!un)expected|illegal start|not a statement|unclosed|reached end of file|class, interface|else without|orphaned|invalid method declaration|<identifier>|malformed", re.I)


def check_python(all_s):
    bad = []
    for s in all_s:
        try:
            ast.parse(textwrap.dedent(s["py"]))
        except SyntaxError as e:
            bad.append((s, f"line {e.lineno}: {e.msg}"))
    return bad


WRAPPERS = [
    ("members", "import java.util.*;\nclass T {\n%s\n}\n"),
    ("statements", "import java.util.*;\nclass T { void m() {\n%s\n} }\n"),
]


def javac_errors(files):
    cmd = ["javac", "-proc:none", "-Xlint:none", "-Xmaxerrs", "100000", "-d", tempfile.gettempdir()] + files
    r = subprocess.run(cmd, capture_output=True, text=True)
    errs = {}
    for line in (r.stderr or "").splitlines():
        m = re.match(r"(.+?\.java):(\d+): error: (.*)", line)
        if m:
            errs.setdefault(os.path.basename(m.group(1)), []).append((int(m.group(2)), m.group(3)))
    return errs


def check_java(all_s):
    work = tempfile.mkdtemp(prefix="jchk")
    pending = list(range(len(all_s)))
    result = {}
    for name, tmpl in WRAPPERS:
        files = {}
        for i in pending:
            code = all_s[i]["java"]
            code = re.sub(r"^\s*//\s*Java\s*$", "", code, flags=re.M)
            fname = f"S{i}_{name}"
            path = os.path.join(work, fname, "T.java")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "w", encoding="utf-8").write(tmpl % code)
            files[i] = path
        # javac needs unique file paths; class T repeats across directories which is fine when compiled separately,
        # so rename the class per file instead.
        for i, path in files.items():
            src = open(path, encoding="utf-8").read().replace("class T ", f"class T{i} ", 1)
            newp = os.path.join(os.path.dirname(path), f"T{i}.java")
            open(newp, "w", encoding="utf-8").write(src)
            os.remove(path)
            files[i] = newp
        errs = javac_errors(list(files.values()))
        nxt = []
        for i, path in files.items():
            e = errs.get(os.path.basename(path), [])
            syn = [x for x in e if SYNTAX.search(x[1])]
            if not syn:
                result[i] = (name, [])
            else:
                nxt.append(i)
                result[i] = (None, syn[:3])
        pending = nxt
    bad = [(all_s[i], result[i][1]) for i in pending]
    return bad, {i: result[i][0] for i in result if result[i][0]}


if __name__ == "__main__":
    all_s = list(snippets())
    print("snippets:", len(all_s))
    pb = check_python(all_s)
    print("python syntax failures:", len(pb))
    for s, m in pb:
        print("  PY", s["file"], "P%d" % s["pattern"], s["label"][:50], "->", m)
    jb, ok = check_java(all_s)
    print("java syntax failures:", len(jb), "(parsed OK:", len(ok), ")")
    for s, errs in jb:
        print("  JAVA", s["file"], "P%d" % s["pattern"], s["label"][:50], "->", errs)
