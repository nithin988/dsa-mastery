"""SVG illustration kit for the System Design course: people, servers, databases, caches, queues, gauges and three-panel story strips.
Everything is drawn with CSS classes (sd-*) so pictures follow the light and dark themes. Coordinates are centre-based."""
import html


def _cls(base, kind):
    return f"{base} {kind}".strip()


def person(x, y, s=1.0, kind=""):
    return (f'<circle class="{_cls("sd-pp", kind)}" cx="{x}" cy="{y - 15 * s:g}" r="{7 * s:g}"/>'
            f'<path class="{_cls("sd-pp", kind)}" d="M{x - 12 * s:g},{y + 15 * s:g} v{-8 * s:g} a{12 * s:g},{12 * s:g} 0 0 1 {24 * s:g},0 v{8 * s:g} z"/>')


def scaled(parts, cx, cy, s):
    return f'<g transform="translate({cx:g} {cy:g}) scale({s}) translate({-cx:g} {-cy:g})">{parts}</g>'


def crowd(x, y, n=5, spread=26, s=0.8, kind=""):
    out = ""
    start = x - spread * (n - 1) / 2
    for i in range(n):
        out += person(start + i * spread, y + (6 if i % 2 else 0), s, kind)
    return out


def server(x, y, label=None, kind="", sub=None):
    out = (f'<rect class="{_cls("sd-sh", kind)}" x="{x - 28}" y="{y - 24}" width="56" height="48" rx="7"/>'
           f'<rect class="sd-ln" x="{x - 18}" y="{y - 12}" width="28" height="4" rx="2"/><rect class="sd-ln" x="{x - 18}" y="{y - 2}" width="28" height="4" rx="2"/>'
           f'<circle class="sd-led {kind}" cx="{x + 17}" cy="{y - 10}" r="3"/><circle class="sd-led {kind}" cx="{x + 17}" cy="{y}" r="3"/>'
           f'<rect class="sd-ln" x="{x - 18}" y="{y + 8}" width="36" height="4" rx="2"/>')
    return out + _lbl(x, y + 40, label, sub)


def database(x, y, label=None, kind="", sub=None):
    w, h, e = 44, 50, 9
    top = y - h / 2
    out = (f'<path class="{_cls("sd-sh", kind)}" d="M{x - w / 2},{top + e} v{h - 2 * e} a{w / 2},{e} 0 0 0 {w},0 v{-(h - 2 * e)} a{w / 2},{e} 0 0 0 {-w},0 z"/>'
           f'<ellipse class="{_cls("sd-sh", kind)} sd-top" cx="{x}" cy="{top + e}" rx="{w / 2}" ry="{e}"/>'
           f'<path class="sd-ln2" d="M{x - w / 2},{y + 2} a{w / 2},{e} 0 0 0 {w},0"/>')
    return out + _lbl(x, y + 42, label, sub)


def cache(x, y, label=None, kind="", sub=None):
    out = (f'<rect class="{_cls("sd-sh", kind)}" x="{x - 26}" y="{y - 22}" width="52" height="44" rx="10"/>'
           f'<path class="sd-bolt {kind}" d="M{x + 3},{y - 15} L{x - 10},{y + 3} L{x - 1},{y + 3} L{x - 5},{y + 15} L{x + 10},{y - 4} L{x + 1},{y - 4} z"/>')
    return out + _lbl(x, y + 38, label, sub)


def queue(x, y, label=None, kind="", sub=None, filled=3):
    out = f'<rect class="{_cls("sd-sh", kind)}" x="{x - 44}" y="{y - 16}" width="88" height="32" rx="16"/>'
    for i in range(4):
        cls = "sd-job on" if i < filled else "sd-job"
        out += f'<rect class="{cls}" x="{x - 34 + i * 18}" y="{y - 7}" width="14" height="14" rx="3"/>'
    return out + _lbl(x, y + 32, label, sub)


def balancer(x, y, label=None, kind="", sub=None):
    out = (f'<circle class="{_cls("sd-sh", kind)}" cx="{x}" cy="{y}" r="24"/>'
           f'<path class="sd-ln2" d="M{x - 13},{y} H{x - 2} M{x - 2},{y} L{x + 12},{y - 11} M{x - 2},{y} H{x + 13} M{x - 2},{y} L{x + 12},{y + 11}"/>'
           f'<circle class="sd-led {kind}" cx="{x - 13}" cy="{y}" r="3"/>')
    return out + _lbl(x, y + 40, label, sub)


def cloud(x, y, label=None, kind="", sub=None):
    out = (f'<path class="{_cls("sd-sh", kind)}" d="M{x - 30},{y + 14} a14,14 0 0 1 2,-27 a20,20 0 0 1 38,-4 a15,15 0 0 1 8,31 z"/>')
    return out + _lbl(x, y + 32, label, sub)


def phone(x, y, label=None, kind="", sub=None):
    out = (f'<rect class="{_cls("sd-sh", kind)}" x="{x - 14}" y="{y - 24}" width="28" height="48" rx="6"/>'
           f'<rect class="sd-ln" x="{x - 7}" y="{y + 15}" width="14" height="3" rx="1.5"/>')
    return out + _lbl(x, y + 40, label, sub)


def alert(x, y, label=None, kind="bad"):
    out = (f'<path class="{_cls("sd-sh", kind)}" d="M{x},{y - 20} L{x + 21},{y + 16} L{x - 21},{y + 16} z"/>'
           f'<rect class="sd-ex" x="{x - 1.6}" y="{y - 8}" width="3.2" height="12" rx="1.4"/><circle class="sd-ex" cx="{x}" cy="{y + 9}" r="2"/>')
    return out + _lbl(x, y + 33, label, None)


def clock(x, y, label=None, kind=""):
    out = (f'<circle class="{_cls("sd-sh", kind)}" cx="{x}" cy="{y}" r="20"/>'
           f'<path class="sd-ln2" d="M{x},{y - 12} V{y} L{x + 9},{y + 5}"/>')
    return out + _lbl(x, y + 36, label, None)


def gauge(x, y, pct, label=None, kind=""):
    import math
    r = 26
    a = math.pi * (1 - pct / 100)
    nx, ny = x + (r - 6) * math.cos(a), y - (r - 6) * math.sin(a)
    out = (f'<path class="sd-arc" d="M{x - r},{y} A{r},{r} 0 0 1 {x + r},{y}"/>'
           f'<path class="sd-arc on {kind}" d="M{x - r},{y} A{r},{r} 0 0 1 {x + r * math.cos(a):g},{y - r * math.sin(a):g}"/>'
           f'<line class="sd-needle {kind}" x1="{x}" y1="{y}" x2="{nx:g}" y2="{ny:g}"/><circle class="sd-hub {kind}" cx="{x}" cy="{y}" r="3.5"/>'
           f'<text class="sd-gv {kind}" x="{x}" y="{y + 16}" text-anchor="middle">{pct}%</text>')
    return out + (_lbl(x, y + 36, label, None) if label else "")


def _lbl(x, y, label, sub):
    out = ""
    if label:
        out += f'<text class="sd-l" x="{x}" y="{y}" text-anchor="middle">{html.escape(label)}</text>'
    if sub:
        out += f'<text class="sd-c" x="{x}" y="{y + 14}" text-anchor="middle">{html.escape(sub)}</text>'
    return out


def flow(x1, y1, x2, y2, kind="", label=None, dash=False):
    cls = _cls("sd-a", kind) + (" dash" if dash else "")
    out = f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" marker-end="url(#dga)"/>'
    if label:
        out += f'<text class="sd-c" x="{(x1 + x2) / 2}" y="{(y1 + y2) / 2 - 7}" text-anchor="middle">{html.escape(label)}</text>'
    return out


def note(x, y, text, kind="", anchor="middle"):
    return f'<text class="sd-n {kind}" x="{x}" y="{y}" text-anchor="{anchor}">{html.escape(text)}</text>'


def badge(x, y, text, kind=""):
    w = max(38, 7.2 * len(text) + 16)
    return (f'<rect class="sd-badge {kind}" x="{x - w / 2:g}" y="{y - 11}" width="{w:g}" height="22" rx="11"/>'
            f'<text class="sd-bt {kind}" x="{x}" y="{y + 4}" text-anchor="middle">{html.escape(text)}</text>')


def svg(w, h, parts, title):
    defs = '<defs><marker id="dga" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="dg-m" d="M0,0 L10,5 L0,10 z"/></marker></defs>'
    return f'<svg class="dg sd" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title, quote=True)}">{defs}' + "".join(parts) + "</svg>"


def figure(w, h, parts, title, caption=None):
    cap = f"<figcaption>{html.escape(caption)}</figcaption>" if caption else ""
    return f'<figure class="viz sdfig">{svg(w, h, parts, title)}{cap}</figure>'


def strip(panels, title, caption=None):
    """Three (or two or four) story panels side by side. panels: list of dicts(title, kind, scene(callable cx, cy -> svg parts string), caption)."""
    n = len(panels)
    pw, gap, ph = (720 - (n - 1) * 14) / n, 14, 276
    parts = []
    for i, p in enumerate(panels):
        x0 = i * (pw + gap)
        kind = p.get("kind", "")
        parts.append(f'<rect class="sd-panel {kind}" x="{x0:g}" y="0" width="{pw:g}" height="{ph}" rx="10"/>')
        parts.append(f'<text class="sd-pt {kind}" x="{x0 + 14:g}" y="26" text-anchor="start">{html.escape(p["title"])}</text>')
        parts.append(p["scene"](x0 + pw / 2, 122, pw))
        for j, line in enumerate(_wrap(p["caption"], pw - 28, 6.4)):
            parts.append(f'<text class="sd-pc" x="{x0 + pw / 2:g}" y="{ph - 52 + j * 15}" text-anchor="middle">{html.escape(line)}</text>')
    return figure(720, ph, parts, title, caption)


def _wrap(t, width, per):
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


CSS = """
.sdfig{margin:18px 0}.sdfig svg{width:100%;height:auto;display:block}
.sd-sh{fill:var(--surf);stroke:var(--faint);stroke-width:2}
.sd-sh.ok{fill:var(--done-soft);stroke:var(--done)}.sd-sh.bad{fill:var(--bad-soft);stroke:var(--bad)}.sd-sh.warn{fill:var(--warn-soft);stroke:var(--warn)}.sd-sh.acc{fill:var(--acc-soft);stroke:var(--acc)}.sd-sh.ink{fill:var(--ink);stroke:var(--ink)}
.sd-top{fill:var(--soft)}.sd-sh.ok.sd-top{fill:var(--done-soft)}
.sd-pp{fill:var(--acc-soft);stroke:var(--acc);stroke-width:1.8}.sd-pp.bad{fill:var(--bad-soft);stroke:var(--bad)}.sd-pp.ok{fill:var(--done-soft);stroke:var(--done)}.sd-pp.warn{fill:var(--warn-soft);stroke:var(--warn)}
.sd-ln{fill:var(--line);}.sd-ln2{fill:none;stroke:var(--faint);stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.sd-led{fill:var(--faint)}.sd-led.ok{fill:var(--done)}.sd-led.bad{fill:var(--bad)}.sd-led.warn{fill:var(--warn)}.sd-led.acc{fill:var(--acc)}
.sd-bolt{fill:var(--acc)}.sd-bolt.ok{fill:var(--done)}.sd-bolt.warn{fill:var(--warn)}
.sd-job{fill:var(--soft);stroke:var(--line);stroke-width:1}.sd-job.on{fill:var(--acc);stroke:var(--acc)}
.sd-ex{fill:var(--bad)}
.sd-arc{fill:none;stroke:var(--line);stroke-width:7;stroke-linecap:round}.sd-arc.on{stroke:var(--done)}.sd-arc.on.bad{stroke:var(--bad)}.sd-arc.on.warn{stroke:var(--warn)}
.sd-needle{stroke:var(--fg);stroke-width:2.5;stroke-linecap:round}.sd-hub{fill:var(--fg)}
.sd-gv{font:700 13px system-ui,sans-serif;fill:var(--fg)}.sd-gv.bad{fill:var(--bad)}.sd-gv.ok{fill:var(--done)}
.sd-l{font:600 12.5px system-ui,sans-serif;fill:var(--fg)}.sd-c{font:11.5px system-ui,sans-serif;fill:var(--mut)}
.sd-n{font:600 12px system-ui,sans-serif;fill:var(--mut)}.sd-n.bad{fill:var(--bad)}.sd-n.ok{fill:var(--done)}.sd-n.warn{fill:var(--warn)}.sd-n.acc{fill:var(--acc)}
.sd-a{stroke:var(--faint);stroke-width:2.2;fill:none}.sd-a.acc{stroke:var(--acc)}.sd-a.ok{stroke:var(--done)}.sd-a.bad{stroke:var(--bad)}.sd-a.warn{stroke:var(--warn)}.sd-a.dash{stroke-dasharray:5 5}
.sd-badge{fill:var(--soft);stroke:var(--line)}.sd-badge.ok{fill:var(--done-soft);stroke:var(--done)}.sd-badge.bad{fill:var(--bad-soft);stroke:var(--bad)}.sd-badge.warn{fill:var(--warn-soft);stroke:var(--warn)}.sd-badge.acc{fill:var(--acc-soft);stroke:var(--acc)}
.sd-bt{font:700 11.5px system-ui,sans-serif;fill:var(--fg)}
.sd-panel{fill:var(--surf);stroke:var(--line);stroke-width:1.5}.sd-panel.bad{fill:var(--bad-soft);stroke:var(--bad-line)}.sd-panel.ok{fill:var(--done-soft);stroke:var(--done-line)}.sd-panel.warn{fill:var(--warn-soft);stroke:var(--warn-line)}
.sd-pt{font:700 13px system-ui,sans-serif;fill:var(--fg);letter-spacing:.2px}.sd-pt.bad{fill:var(--bad)}.sd-pt.ok{fill:var(--done)}.sd-pt.warn{fill:var(--warn)}
.sd-pc{font:12.5px system-ui,sans-serif;fill:var(--txt)}
"""
