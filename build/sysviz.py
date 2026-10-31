"""Tiny SVG diagram builder so every Systems visual shares one look (themed through CSS classes dg-*)."""
import html


def _lines(text):
    return str(text).split("\n")


def _wrap(t, width, per):
    """Greedy word wrap using an estimated glyph width."""
    words, lines, cur = str(t).split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cur and len(trial) * per > width:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines or [""]


def box(x, y, w, h, text, kind="", sub=None):
    """A labelled box. Text is fitted: long titles shrink a little, long sub-text wraps, and the box grows
    (about its centre) when its content needs more room, so nothing ever spills outside the rectangle."""
    inner = w - 14
    tl = _lines(text)
    fs = 13
    longest = max(len(l) for l in tl) * 7.4
    if longest > inner:
        fs = max(10.5, round(13 * inner / longest, 1))
    sl = _wrap(sub, inner, 6.3) if sub else []
    content = len(tl) * 16 + (len(sl) * 14 + 3 if sl else 0)
    need = content + 14
    if h < need:
        y -= (need - h) / 2
        h = need
    top = y + (h - content) / 2
    out = f'<rect class="dg-box {kind}" x="{x}" y="{y:g}" width="{w}" height="{h:g}" rx="6"/>'
    sty = f' style="font-size:{fs}px"' if fs != 13 else ""
    for i, l in enumerate(tl):
        out += f'<text class="dg-t {kind}"{sty} x="{x + w / 2}" y="{top + 12 + i * 16:g}" text-anchor="middle">{html.escape(l)}</text>'
    base = top + len(tl) * 16 + 3
    for j, l in enumerate(sl):
        out += f'<text class="dg-s {kind}" x="{x + w / 2}" y="{base + 11 + j * 14:g}" text-anchor="middle">{html.escape(l)}</text>'
    return out


def arrow(x1, y1, x2, y2, label=None, kind=""):
    out = f'<line class="dg-a {kind}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" marker-end="url(#dga)"/>'
    if label:
        out += f'<text class="dg-s" x="{(x1 + x2) / 2}" y="{(y1 + y2) / 2 - 7}" text-anchor="middle">{html.escape(label)}</text>'
    return out


def text(x, y, s, cls="dg-s", anchor="middle"):
    return f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{html.escape(s)}</text>'


def svg(w, h, parts, title):
    defs = '<defs><marker id="dga" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="dg-m" d="M0,0 L10,5 L0,10 z"/></marker></defs>'
    return (f'<svg class="dg" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title, quote=True)}">{defs}' + "".join(parts) + "</svg>")


def figure(w, h, parts, title, caption):
    return f'<figure class="viz">{svg(w, h, parts, title)}<figcaption>{html.escape(caption)}</figcaption></figure>'
