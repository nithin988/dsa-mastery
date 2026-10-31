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


def seq(actors, msgs, title, caption, width=720):
    """Sequence diagram. actors: names. msgs: ('a->b', from_i, to_i, label[, kind]) arrows (kind '' | 'reply' | 'bad'),
    ('note', i, j, text) a note spanning lifelines i..j, ('gap', text) a small full-width heading."""
    n = len(actors)
    xs = [60 + i * (width - 120) / max(1, n - 1) for i in range(n)]
    row, top = 36, 60
    parts_arrows = []
    y = top
    for m in msgs:
        if m[0] == "a->b":
            _, a, b, label = m[:4]
            kind = m[4] if len(m) > 4 else ""
            x1, x2 = xs[a], xs[b]
            cls = "dg-a " + ("dash " if kind == "reply" else "") + ("bad" if kind == "bad" else "")
            off = 5 if x2 > x1 else -5
            parts_arrows.append(f'<line class="{cls.strip()}" x1="{x1 + off:g}" y1="{y:g}" x2="{x2 - off:g}" y2="{y:g}" marker-end="url(#dga)"/>')
            parts_arrows.append(f'<text class="dg-s" x="{(x1 + x2) / 2:g}" y="{y - 7:g}" text-anchor="middle">{html.escape(label)}</text>')
            y += row
        elif m[0] == "note":
            _, i, j, txt = m
            x1, x2 = min(xs[i], xs[j]) - 46, max(xs[i], xs[j]) + 46
            parts_arrows.append(f'<rect class="dg-box acc" x="{x1:g}" y="{y - 15:g}" width="{x2 - x1:g}" height="26" rx="6"/>')
            parts_arrows.append(f'<text class="dg-t acc" x="{(x1 + x2) / 2:g}" y="{y + 3:g}" text-anchor="middle" style="font-size:12px">{html.escape(txt)}</text>')
            y += row
        else:
            parts_arrows.append(f'<text class="dg-t" x="{width / 2:g}" y="{y:g}" text-anchor="middle" style="font-size:12px">{html.escape(m[1])}</text>')
            y += row - 8
    height = y + 4
    out = []
    for i, name in enumerate(actors):
        out.append(f'<line class="dg-life" x1="{xs[i]:g}" y1="40" x2="{xs[i]:g}" y2="{height - 10:g}"/>')
    for i, name in enumerate(actors):
        w = max(80, len(name) * 8 + 24)
        out.append(f'<rect class="dg-box ink" x="{xs[i] - w / 2:g}" y="6" width="{w:g}" height="30" rx="6"/>')
        out.append(f'<text class="dg-t ink" x="{xs[i]:g}" y="26" text-anchor="middle">{html.escape(name)}</text>')
    return figure(width, int(height), out + parts_arrows, title, caption)
