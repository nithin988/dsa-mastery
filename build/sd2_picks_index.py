"""List every verified experiment and model-answer scenario that a System Design page can pick by reference.

  python build/sd2_picks_index.py [module id ...]    (no argument: all deep reference modules)

Usage inside a content file:   ("cache", 3, 0, 0, "A stampede, and how one lock stops it")   -> pick(module, lesson, group, command, title)
                               scen("cache", 3)                                              -> the lesson's interview scenario dict
                               figure_of("dw", 0)                                            -> the lesson's first picture (HTML)"""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import syscatalog  # noqa: E402
from lib_sys import load_outputs, runnable  # noqa: E402


def main():
    want = set(sys.argv[1:])
    rec = load_outputs()
    for row in syscatalog.MODULES:
        if not row[5]:
            continue
        m = importlib.import_module(row[5]).MODULE
        if (want and m["id"] not in want) or (not want and not m.get("deep")):
            continue
        run = runnable(m)
        print(f'\n=== module "{m["id"]}": {m["title"]}   (reference page systems/{row[1]}.html)')
        for li, L in enumerate(m["lessons"]):
            sc = L.get("scenario")
            print(f'  lesson {li}: {L["title"]}')
            if sc:
                print(f'      scenario: {sc["title"][:110]}')
            vis = L.get("visual")
            if vis:
                print(f'      visuals: {len(vis) if isinstance(vis, (list, tuple)) else 1} (figure_of("{m["id"]}", {li}, i))')
            for gi, g in enumerate(L.get("groups", [])):
                for ci, c in enumerate(g["cmds"]):
                    ok = ""
                    if c.get("run", True):
                        idx = next((i for i, x in enumerate(run) if x is c), None)
                        r = rec.get(m["id"], [])
                        ok = "recorded" if idx is not None and idx < len(r) and r[idx]["cmd"] == c["c"] else "NOT RECORDED"
                    else:
                        ok = "illustrative"
                    first = c["c"].strip().splitlines()[0][:70] if c["c"].strip() else ""
                    print(f'      pick ("{m["id"]}", {li}, {gi}, {ci})  [{ok}]  {g["title"][:50]} :: {first}')


if __name__ == "__main__":
    main()
