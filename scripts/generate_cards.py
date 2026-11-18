#!/usr/bin/env python3
"""Generates the static README cards (selected-work cards + tech thought of the day) with the
same tokens as scripts/generate_stats.py, so every card shares one look.
Usage: python scripts/generate_cards.py
"""
import datetime, html

# ---- design tokens (keep in sync with generate_stats.py) ----
NAVY, CORAL, SAFFRON, IVORY = "#101827", "#FF754A", "#FF9933", "#F5EBDD"
FONT = "'Segoe UI',Helvetica,Arial,sans-serif"
W, M, R, HDR = 800, 20, 26, 64        # width, outer margin, radius, header height
X0, X1 = M + 28, W - M - 28           # content edges
LABEL, BODY, VALUE = 18, 24, 44       # type scale: label / body / value
TITLE = 32                            # card title (between body and value)


def svg(h, label, body, delay=0.0):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{html.escape(label)}">
<title>{html.escape(label)}</title>
<defs><clipPath id="card"><rect x="{M}" y="{M}" width="{W-2*M}" height="{h-2*M}" rx="{R}"/></clipPath></defs>
<style>text{{font-family:{FONT};font-weight:800}}
.in{{animation:in .8s cubic-bezier(.22,.8,.3,1) {delay}s backwards}}
@keyframes in{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:none}}}}</style>
<rect width="{W}" height="{h}" fill="{IVORY}"/>
{body}</svg>'''


def header(h, left, right):
    return (f'<g clip-path="url(#card)"><rect x="{M}" y="{M}" width="{W-2*M}" height="{h-2*M}" fill="{NAVY}"/>'
            f'<rect x="{M}" y="{M}" width="{W-2*M}" height="{HDR}" fill="{CORAL}"/></g>'
            f'<rect x="{W/2-45:.0f}" y="{M+HDR/2-7:.0f}" width="90" height="14" rx="7" fill="{NAVY}"/>'
            f'<text x="{X0}" y="{M+HDR/2+7:.0f}" font-size="20" letter-spacing="3" fill="{NAVY}">{left}</text>'
            f'<text x="{X1}" y="{M+HDR/2+7:.0f}" font-size="20" letter-spacing="3" fill="{NAVY}" text-anchor="end">{right}</text>')


# ---- selected work: one linked card per project ----
WORK = [
    ("godevelopers", "GoDevelopers", "Developer ecosystem to learn &amp; contribute"),
    ("fairshare", "FairShare", "Shared expenses, balances &amp; settlements"),
    ("dsa-real-world", "DSA Real World", "DSA learning &amp; contributor workflows"),
    ("recap", "Recap / StoryCode", "Programming concepts through stories"),
]
H = 170
for i, (slug, name, desc) in enumerate(WORK):
    cy = M + (H - 2 * M) / 2
    body = (f'<g class="in">'
            f'<g clip-path="url(#card)"><rect x="{M}" y="{M}" width="{W-2*M}" height="{H-2*M}" fill="{NAVY}"/>'
            f'<rect x="{M}" y="{M}" width="10" height="{H-2*M}" fill="{CORAL}"/></g>'
            f'<text x="{X0}" y="{M+40}" font-size="{LABEL}" letter-spacing="3" fill="{CORAL}">PROJECT {i+1:02d}</text>'
            f'<text x="{X0}" y="{M+80}" font-size="{TITLE}" fill="{IVORY}">{name}</text>'
            f'<text x="{X0}" y="{M+114}" font-size="{BODY}" font-weight="600" fill="{SAFFRON}">{desc}</text>'
            f'<circle cx="{X1-28}" cy="{cy:.0f}" r="28" fill="{CORAL}"/>'
            f'<path d="M{X1-37} {cy+9:.0f} L{X1-19} {cy-9:.0f} M{X1-31} {cy-9:.0f} H{X1-19} V{cy+3:.0f}" fill="none" stroke="{NAVY}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
            f'</g>')
    open(f"assets/work-{slug}.svg", "w").write(svg(H, f"{html.unescape(name)} — {html.unescape(desc)}", body, delay=i * 0.12))

# ---- tech thought of the day (changes daily via the workflow) ----
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


def wrap(text, n=30):
    lines, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > n:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    return lines + [cur]


today = datetime.date.today()
thought = THOUGHTS[today.toordinal() % len(THOUGHTS)]
lines = wrap(thought)
assert len(lines) <= 2, thought
TOP = M + HDR; H = TOP + 222 + M; by = TOP + 142   # pill row
q = "".join(f'<text x="{X0+64}" y="{TOP+66+i*44}" font-size="{TITLE}" fill="{IVORY}">{html.escape(l)}</text>' for i, l in enumerate(lines))
body = (f'<g class="in">{header(H, "TECH THOUGHT", today.strftime("%d %b %Y").upper())}'
        f'<text x="{X0-4}" y="{TOP+100}" font-size="96" fill="{CORAL}">&#8220;</text>{q}'
        f'<text x="{X0+64}" y="{by+35}" font-size="{LABEL}" letter-spacing="3" fill="{SAFFRON}">— THE HUSTLER</text>'
        f'<rect x="{X1-340}" y="{by}" width="340" height="56" rx="28" fill="{CORAL}"/>'
        f'<g transform="translate({X1-314},{by+16})" fill="none" stroke="{NAVY}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="4"/><path d="M2 21c0-4 3-7 7-7s7 3 7 7M19 7v6M16 10h6"/></g>'
        f'<text x="{X1-278}" y="{by+35}" font-size="20" letter-spacing="3" fill="{NAVY}">FOLLOW FOR MORE</text>'
        f'</g>')
open("assets/thought.svg", "w").write(svg(H, f"Tech thought: {thought} — The Hustler. Follow for more.", body, delay=5.2))
print("cards written; thought:", thought)
