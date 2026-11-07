"""Render ONE System Design page for review without touching the shared build.

  python build/sd2_check.py <slug> [out.html]

Renders the page to out.html (default: the scratch folder given by SD2_SCRATCH, else the system temp folder) and prints problems:
a missing or stale experiment recording, a figure whose text may overflow, and content fields that are missing. Exit code 1 on any error."""
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sd2  # noqa: E402
from sd2_content import COURSE, load  # noqa: E402

CHAPTER_KEYS = ["time", "tagline", "story", "idea", "how", "try", "breaks", "real", "interview", "recap"]
PROBLEM_KEYS = ["time", "seen_at", "tagline", "story", "numbers", "design_figure", "design", "hard_title", "hard_paras", "try", "scale", "scenario", "recap"]


def main():
    slug = sys.argv[1]
    meta = next((r for r in COURSE["chapters"] + COURSE["problems"] if r["slug"] == slug), None)
    if not meta:
        print("unknown slug", slug)
        return 1
    is_chapter = meta in COURSE["chapters"]
    data = dict(meta, **load(slug))
    problems = []
    for k in (CHAPTER_KEYS if is_chapter else PROBLEM_KEYS):
        if k not in data or not data[k]:
            problems.append(f"missing or empty field: {k}")
    if is_chapter and len(data.get("how", [])) < 3:
        problems.append("a chapter needs at least 3 'how it works' steps, each with a small figure")
    if is_chapter and len(data.get("interview", [])) < 2:
        problems.append("a chapter needs at least 2 interview questions")
    if is_chapter and len(data.get("real", [])) < 1:
        problems.append("a chapter needs at least 1 sourced real-company note")
    text = (sd2.render_chapter(data, None, None, 9) if is_chapter else sd2.render_problem(data, None, None, 10)) if not problems else ""
    if text:
        figs = len(re.findall(r"<svg", text))
        print(f"figures: {figs}")
        if figs < 6:
            problems.append(f"only {figs} figures; aim for at least 6 (story strip, master picture, one per step)")
        for em in ("—", "–"):
            if em in text:
                problems.append(f"contains a dash character {em!r}: use commas, colons or full stops")
        # crude overflow check: any SVG <text> longer than its panel is likely to be clipped at 720 wide
        for m in re.finditer(r'<text class="[^"]*" x="([\d.]+)" y="[\d.]+"[^>]*text-anchor="(\w+)">([^<]+)</text>', text):
            x, anchor, t = float(m.group(1)), m.group(2), m.group(3)
            w = len(t) * 6.6
            left = x - w / 2 if anchor == "middle" else x if anchor == "start" else x - w
            right = left + w
            if left < -4 or right > 724:
                problems.append(f"figure text may be clipped (x {left:.0f} to {right:.0f}): {t[:50]!r}")
        out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.environ.get("SD2_SCRATCH", tempfile.gettempdir()), slug + ".html")
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        print("rendered", out, f"({len(text) // 1024} KB)")
    for p in problems:
        print("PROBLEM:", p)
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
