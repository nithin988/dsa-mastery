# DSA Mastery design system

The look of every page comes from **one stylesheet**, `build/style.css`. Its tokens and components follow the
Kimaru Platform design system (`docs/DESIGN_SYSTEM.md` in the master-demo codebase), adapted for a long-form
reading site. Change a token in `:root`, run `python build/build.py`, and all 19 topic pages and the landing page update.

## Principles

- **Neutral first.** Slate greys carry structure (borders, cards, headings, body text). Colour appears only to carry meaning.
- **Light by default.** Dark mode is opt-in through the theme button (`data-theme="dark"`) and is remembered in the browser.
- **Flat and quiet.** `rounded-md` (6px) cards and buttons, `shadow-sm` elevation, no gradients, no decorative animation.
- **Accessible.** Every text and background pair meets WCAG AA (4.5:1), visible focus rings, skip link, keyboard-operable
  menus and animations, `prefers-reduced-motion` respected. Controls are 32px high (40px for the main landing-page actions).
- **Offline.** No external fonts, scripts or images. System font stack, inline SVG icons.

## Tokens (light)

| Token | Value | Use |
|---|---|---|
| `--bg` / `--surf` / `--hd` | `#f8fafc` / `#fff` / `#f8fafc` | page, card body, card header bar |
| `--fg` / `--txt` / `--mut` | `#0f172a` / `#334155` / `#475569` | headings, body text, secondary text |
| `--line` / `--line2` | `#e2e8f0` / `#f1f5f9` | card borders, internal dividers |
| `--ink` | `#0f172a` | primary buttons, number badges |
| `--acc` | `#3162b4` | links, focus ring, highlighted animation cells |
| `--ok` `--med` `--bad` | green-700, yellow-700, red-700 | difficulty: Easy, Medium, Hard |
| `--warn` | amber-700 | "frequently asked" tier, traps callout |
| `--info` | sky-700 | intuition callout, animation note |
| `--done` | teal-700 | solved problems (the "confirmed" state) |

Deliberate deviations from the source design system, for contrast: secondary text uses slate-600 instead of gray-400,
and the confirmed state uses teal-700 instead of teal-600. The Kimaru logo is not used; the brand blue is reused only as the link/focus accent.

## Components

| Component | Pattern |
|---|---|
| Top bar | sticky 48px, white, bottom border, brand, breadcrumb, progress, language segment, topic menu, theme, download |
| Card (`.pat`, `.tcard`) | white body, 1px slate-200 border, `shadow-sm`, 50px `#f8fafc` header bar with badge, title, status pill |
| Callout | neutral `#f8fafc` box with a 2px left accent (sky = intuition, amber = traps, green = complexity) |
| Pill | `rounded-full`, soft background, 700-level text (difficulty, tier, status) |
| Buttons | primary dark (`.btn.pri`), secondary light (`.btn`), icon-only (`.iconbtn`) |
| Table | uppercase 11px header on `#f8fafc`, row hover, solved row tinted teal |
| Animation panel (`.stepper`) | header bar, progress strip, canvas, note, controls with 16px icons |
| Topic menu | popover with phases, per-topic solved counts, arrow-key navigation, Esc to close |

## Icons

Inline SVG, 16x16, `stroke-width` 1.33, round caps and joins, `currentColor`. The single source is the `ICONS` dict in
`build/lib.py`; add a new icon there and use `icon("name")` in Python or `ic('name')` in JavaScript.

## Page flow

1. **Landing page:** hero with the primary action (Start, or Continue where you left off), progress summary, three-step
   "how it works", then the learning path grouped into six phases with search and status filters.
2. **Topic page:** breadcrumb and step indicator, header with counts, mindset, priority, cues, the patterns (each a card),
   recall tables, self-test, study plan, then previous / next topic cards.
3. **Progress:** ticks on the problem ladders are stored in the browser (`localStorage`) and feed the progress bar, the topic
   menu and the landing page cards.
