#!/usr/bin/env python3
"""Generates the static README cards — selected-work cards, tech thought of the day and the contact buttons —
in desktop (file.svg) and mobile (file-m.svg) sizes, using the tokens in scripts/theme.py.
Usage: python scripts/generate_cards.py
"""
import datetime, html
from zoneinfo import ZoneInfo
from theme import SIZES, frame, NAVY, CORAL, SAFFRON, IVORY, SOFT, CREAM, INK, FONT, FONT_CSS

WORK = [
    ("fairshare", "FairShare", "Shared expenses, balances & settlements"),
    ("dsa-real-world", "DSA Real World", "DSA learning & contributor workflows"),
    ("recap", "Recap / StoryCode", "Programming concepts through stories"),
]

THOUGHTS = [
    "Ship it. Then make it better.",
    "Done and deployed beats perfect and pending.",
    "Simple scales. Clever breaks at 3 AM.",
    "Every bug is a lesson the code wanted to teach.",
    "Logs are love letters to your future self.",
    "Good naming is half the documentation.",
    "If you do it twice, script it.",
    "Read the error message. Then read it again.",
    "Systems fail. Great engineers plan for it.",
    "Small commits. Big progress.",
    "Tests are the net that lets you move fast.",
    "The best feature is the one users actually use.",
    "Premature optimization is a beautiful trap.",
    "Build. Break. Ship. Restart.",
]


def wrap(text, n):
    lines, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > n:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    return lines + [cur]


def arrow(cx, cy, r):
    s = r / 28
    return (f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="{CORAL}"/>'
            f'<path transform="translate({cx:.0f},{cy:.0f}) scale({s:.2f})" d="M-9 9 L9 -9 M-3 -9 H9 V3" fill="none" '
            f'stroke="{NAVY}" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>')


def date_chip(x, base, L, label):
    fs = L - 1; h = fs * 1.9; w = sum(0.3 if c in " ·:" else 0.62 for c in label) * fs + len(label) * 1.2 + fs * 1.6; y = base - fs * 0.36 - h / 2
    return (f'<rect x="{x:.0f}" y="{y:.1f}" width="{w:.0f}" height="{h:.0f}" rx="{h/2:.0f}" fill="{INK}" fill-opacity=".06" '
            f'stroke="{INK}" stroke-opacity=".28"/>'
            f'<text x="{x+w/2:.0f}" y="{base-0.5:.1f}" font-size="{fs}" letter-spacing="1.2" fill="{INK}" text-anchor="middle">{label}</text>')


# India time: the card flips right after 11:59 PM IST (the workflow runs at 00:00 IST = 18:30 UTC)
now = datetime.datetime.now(ZoneInfo("Asia/Kolkata")); today = now.date()
def stamp(desk):
    """Date + time of this update in IST, e.g. "19 NOV 2026 · 12:00 AM IST" (shorter on mobile)."""
    t = now.strftime("%I:%M %p").lstrip("0")
    return (now.strftime("%d %b %Y") + f" · {t} IST" if desk else now.strftime("%d %b") + f" · {t}").upper()


thought = THOUGHTS[today.toordinal() % len(THOUGHTS)]

for kind, t in SIZES.items():
    X0, X1, L, B, T, P, W = t["X0"], t["X1"], t["LABEL"], t["BODY"], t["TITLE"], t["PAD"], t["W"]
    desk = kind == "desktop"

    # ---- selected work: number + name + description + arrow (no header, so it reads differently) ----
    dx = X0 + T * 2.4; tx = dx + T * 0.8; ar = T * 0.9   # number | divider | text
    for i, (slug, name, desc) in enumerate(WORK):
        lines = wrap(desc, 200 if desk else 32)
        yt = P + T * 0.95; yd = yt + 10 + B
        h = round(yd + (len(lines) - 1) * B * 1.45 + P - 2)
        inner = (f'<text x="{X0}" y="{h/2+T*0.55:.0f}" font-size="{T*1.6:.0f}" fill="{CORAL}">{i+1:02d}</text>'
                 f'<line x1="{dx:.0f}" y1="{P}" x2="{dx:.0f}" y2="{h-P}" stroke="{IVORY}" stroke-opacity=".12"/>'
                 f'<text x="{tx:.0f}" y="{yt:.0f}" font-size="{T}" fill="{IVORY}">{html.escape(name)}</text>'
                 + "".join(f'<text x="{tx:.0f}" y="{yd+j*B*1.45:.0f}" font-size="{B}" font-weight="600" fill="{SOFT}">{html.escape(l)}</text>' for j, l in enumerate(lines))
                 + arrow(X1 - ar, h / 2, ar))
        open(f"assets/work-{slug}{t['suffix']}.svg", "w").write(frame(t, h, f"{name} — {desc}", inner, delay=i * 0.1))

    # ---- tech thought of the day: cream card styled like the hero banner (rotates daily via the workflow) ----
    lines = wrap(thought, 52 if desk else 26)
    cr = 100 if desk else 56; ccx, ccy = W - (50 if desk else 24), -40 if desk else -30
    deco = (f'<g clip-path="url(#card)"><circle cx="{ccx}" cy="{ccy}" r="{cr}" fill="{CORAL}"/>'
            f'<circle cx="{ccx}" cy="{ccy}" r="{cr*1.45:.0f}" fill="none" stroke="{CORAL}" stroke-opacity=".55" stroke-width="1.5"/></g>')
    yl = P + L; fs = L / 13
    flag = (f'<path transform="translate({X0},{yl-L*0.95:.0f}) scale({fs:.2f})" d="M1 0v16M1 1h11l-3 4 3 4H1" '
            f'fill="{SAFFRON}" stroke="{SAFFRON}" stroke-width="2" stroke-linejoin="round"/>')
    inner = deco + flag + (
        f'<text x="{X0+L*1.6:.0f}" y="{yl}" font-size="{L}" letter-spacing="1.5" fill="{SAFFRON}">TECH THOUGHT</text>'
        # date chip sits right after the label, clear of the coral corner decoration
        + date_chip(X0 + L*1.6 + L*10.6, yl, L, stamp(desk)))
    qs = round(T * 1.2); yq = yl + 16 + qs
    inner += "".join(f'<text x="{X0}" y="{yq+j*qs*1.3:.0f}" font-size="{qs}" fill="{INK}">{html.escape(l)}</text>' for j, l in enumerate(lines))
    ph = t["HEAD"] * 2.6; pw = t["HEAD"] * 13.5; py = yq + (len(lines) - 1) * qs * 1.3 + 18
    inner += (f'<text x="{X0}" y="{py+ph/2+L*0.36:.0f}" font-size="{L}" letter-spacing="1.5" fill="{CORAL}">— THE HUSTLER</text>'
              f'<rect x="{X1-pw:.0f}" y="{py:.0f}" width="{pw:.0f}" height="{ph:.0f}" rx="{ph/2:.0f}" fill="{CORAL}"/>'
              f'<text x="{X1-pw/2:.0f}" y="{py+ph/2+t["HEAD"]*0.36:.0f}" font-size="{t["HEAD"]}" letter-spacing="1.5" fill="{INK}" text-anchor="middle">FOLLOW FOR MORE</text>')
    h = round(py + ph + P)
    open(f"assets/thought{t['suffix']}.svg", "w").write(
        frame(t, h, f"Tech thought: {thought} — The Hustler. Follow for more.", inner, delay=5.2,
              fill=CREAM, stroke=INK, stroke_opacity="1"))

# ---- contact buttons (icon + label centred; widths measured for Poppins Bold 14px, letter-spacing .8) ----
ICONS = {
    "portfolio": '<circle cx="12" cy="12" r="10"/><ellipse cx="12" cy="12" rx="4.2" ry="10"/><path d="M2 12h20"/>',
    "linkedin": '<rect x="2" y="2" width="20" height="20" rx="4"/><path d="M7.5 10.5v6M7.5 7.6v.1M11.5 16.5v-6M11.5 13c0-1.7 1.2-2.5 2.5-2.5s2.5.8 2.5 2.5v3.5"/>',
    "email": '<rect x="2" y="4" width="20" height="16" rx="3"/><path d="m3 7 9 6.5L21 7"/>',
}
BUTTONS = [("portfolio", 84.0, True, 4.22), ("linkedin", 69.1, False, 4.52), ("email", 44.7, False, 4.82)]
for name, tw, solid, delay in BUTTONS:
    lab = name.upper(); x0 = round((164 - (24 + 10 + tw)) / 2)
    fg = NAVY if solid else CORAL; tc = NAVY if solid else IVORY
    open(f"assets/btn-{name}.svg", "w").write(f'''<svg xmlns="http://www.w3.org/2000/svg" width="164" height="52" viewBox="0 0 164 52" role="img" aria-label="{lab}">
<title>{lab}</title>
<style>{FONT_CSS}
.b{{animation:rise .9s cubic-bezier(.22,.8,.3,1) {delay}s backwards}}
@keyframes rise{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:translateY(0)}}}}
text{{font-family:{FONT};font-weight:700;letter-spacing:.8px;font-size:14px}}
</style>
<g class="b">
<rect x="2" y="4" width="160" height="44" rx="22" fill="{CORAL if solid else NAVY}" stroke="{CORAL}" stroke-width="2"/>
<g transform="translate({x0},14)" fill="none" stroke="{fg}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>
<text x="{x0+34}" y="31" textLength="{tw}" lengthAdjust="spacing" fill="{tc}">{lab}</text>
</g></svg>''')

print("cards written; thought:", thought)
