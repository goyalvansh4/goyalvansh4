#!/usr/bin/env python3
"""Generates the static README cards — selected-work cards, tech thought of the day and the contact buttons —
in desktop (file.svg) and mobile (file-m.svg) sizes, using the tokens in scripts/theme.py.
Usage: python scripts/generate_cards.py
"""
import datetime, html
from theme import SIZES, frame, NAVY, CORAL, SAFFRON, IVORY, FONT, FONT_CSS

WORK = [
    ("godevelopers", "GoDevelopers", "Developer ecosystem to learn & contribute"),
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
            f'stroke="{NAVY}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')


def follow_pill(x, y, t):
    hd = t["HEAD"]; ph = hd * 2.8; pw = hd * 17; s = hd / 20
    return (f'<rect x="{x-pw:.0f}" y="{y:.0f}" width="{pw:.0f}" height="{ph:.0f}" rx="{ph/2:.0f}" fill="{CORAL}"/>'
            f'<g transform="translate({x-pw+hd*1.3:.0f},{y+ph/2-12*s:.0f}) scale({s:.2f})" fill="none" stroke="{NAVY}" stroke-width="2.4" '
            f'stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="4"/><path d="M2 21c0-4 3-7 7-7s7 3 7 7M19 7v6M16 10h6"/></g>'
            f'<text x="{x-pw+hd*3.1:.0f}" y="{y+ph/2+hd*0.36:.0f}" font-size="{hd}" letter-spacing="3" fill="{NAVY}">FOLLOW FOR MORE</text>'), ph


today = datetime.date.today()
thought = THOUGHTS[today.toordinal() % len(THOUGHTS)]

for kind, t in SIZES.items():
    M, X0, X1, L, B, T = t["M"], t["X0"], t["X1"], t["LABEL"], t["BODY"], t["TITLE"]

    # ---- selected work: one linked card per project ----
    yl = M + 22 + L; yt = yl + T * 1.25; yd = yt + B * 1.45; H = round(yd + 24 + M)
    for i, (slug, name, desc) in enumerate(WORK):
        inner = (f'<rect x="{M}" y="{M}" width="10" height="{H-2*M}" fill="{CORAL}" clip-path="url(#card)"/>'
                 f'<text x="{X0}" y="{yl:.0f}" font-size="{L}" letter-spacing="3" fill="{CORAL}">PROJECT {i+1:02d}</text>'
                 f'<text x="{X0}" y="{yt:.0f}" font-size="{T}" fill="{IVORY}">{html.escape(name)}</text>'
                 f'<text x="{X0}" y="{yd:.0f}" font-size="{B}" font-weight="600" fill="{SAFFRON}">{html.escape(desc)}</text>'
                 + arrow(X1 - T * 0.875, H / 2, T * 0.875))
        open(f"assets/work-{slug}{t['suffix']}.svg", "w").write(frame(t, H, f"{name} — {desc}", inner, delay=i * 0.12))

    # ---- tech thought of the day (rotates daily via the workflow) ----
    TOP = t["TOP"]; lines = wrap(thought, 56 if kind == "desktop" else 30)
    qx = X0 + T * 2; first = TOP + T * 2.06
    inner = f'<text x="{X0-4}" y="{TOP+T*3.1:.0f}" font-size="{T*3}" fill="{CORAL}">&#8220;</text>'
    inner += "".join(f'<text x="{qx:.0f}" y="{first+i*T*1.4:.0f}" font-size="{T}" fill="{IVORY}">{html.escape(l)}</text>' for i, l in enumerate(lines))
    by = first + (len(lines) - 1) * T * 1.4 + T
    pill, ph = follow_pill(X1, by, t)
    inner += f'<text x="{qx:.0f}" y="{by+ph/2+L*0.37:.0f}" font-size="{L}" letter-spacing="3" fill="{SAFFRON}">— THE HUSTLER</text>' + pill
    H = round(by + ph + 24 + M)
    open(f"assets/thought{t['suffix']}.svg", "w").write(
        frame(t, H, f"Tech thought: {thought} — The Hustler. Follow for more.", inner,
              header=("TECH THOUGHT", today.strftime("%d %b %Y").upper()), delay=5.2))

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
