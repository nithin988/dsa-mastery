"""Find snippets where a top-level `return` is followed by more top-level statements (unreachable code)."""
import ast, os, re, sys, textwrap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from snippets import snippets
from check_syntax import check_java

def py_dead(code):
    tree = ast.parse(textwrap.dedent(code))
    body = tree.body
    for i, st in enumerate(body):
        if isinstance(st, ast.Return) and i < len(body) - 1:
            return True
    return False

def java_dead(code):
    depth, seen_ret = 0, False
    for raw in code.splitlines():
        line = re.sub(r"//.*", "", raw).strip()
        if not line:
            continue
        if depth == 0 and seen_ret:
            return True
        if depth == 0 and re.match(r"return\b.*;\s*$", line):
            seen_ret = True
        depth += line.count("{") - line.count("}")
    return False

all_s = list(snippets())
_, kinds = check_java(all_s)
print("PYTHON snippets with dead code after a top-level return:")
for s in all_s:
    if py_dead(s["py"]):
        print("  ", s["file"], "P%d.%d" % (s["pattern"], s["idx"]), s["label"][:60])
print("JAVA statement-style snippets with dead code after a top-level return:")
for i, s in enumerate(all_s):
    if kinds.get(i) == "statements" and java_dead(s["java"]):
        print("  ", s["file"], "P%d.%d" % (s["pattern"], s["idx"]), s["label"][:60])
