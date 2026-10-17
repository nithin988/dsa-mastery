"""Regenerate compact_slugs.txt (number:slug:difficulty, '|' separated) from the content."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from snippets import topics
seen = {}
for t in topics():
    for p in t["patterns"]:
        for (n, name, d, slug, logic, cx) in p["problems"]:
            seen[slug] = (n, slug, d)
s = "|".join("%d:%s:%s" % v for v in sorted(seen.values()))
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "compact_slugs.txt"), "w", encoding="utf-8").write(s)
print(len(seen), "problems written")
