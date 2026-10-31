"""Tiny SVG diagram builder so every Systems visual shares one look (themed through CSS classes dg-*)."""
import html


def _lines(text):
    return str(text).split("\n")


def box(x, y, w, h, text, kind="", sub=None):
    ls = _lines(text)
    ty = y + h / 2 - (len(ls) - 1) * 9 + 5 - (7 if sub else 0)
    out = f'<rect class="dg-box {kind}" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>'
    for i, l in enumerate(ls):
        out += f'<text class="dg-t {kind}" x="{x + w / 2}" y="{ty + i * 18}" text-anchor="middle">{html.escape(l)}</text>'
    if sub:
        out += f'<text class="dg-s" x="{x + w / 2}" y="{y + h / 2 + 18}" text-anchor="middle">{html.escape(sub)}</text>'
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
