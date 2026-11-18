"""Shared design tokens + card frame for every generated README card.

Cards are drawn at the size GitHub actually displays them, so font sizes are real on-screen pixels:
  desktop (880 wide, file.svg)    — README column on desktop
  mobile  (400 wide, file-m.svg)  — shown under 600px via <picture>
Canvas is transparent: cards sit directly on GitHub's background (no ivory frame).
"""
import base64, html, os

NAVY, CORAL, SAFFRON, IVORY, MUTED = "#101827", "#FF754A", "#FF9933", "#F5EBDD", "#9AA3B5"
CREAM, INK = "#FFF3DF", "#172033"   # hero banner palette (cream card + ink text)
SOFT = "#C9CCD3"   # secondary text on navy (high contrast, calmer than ivory)
FONT = "Poppins,'Segoe UI',Helvetica,Arial,sans-serif"

# Poppins (SIL OFL, assets/fonts/OFL.txt) is embedded in every SVG so it renders the same everywhere.
_FONTS = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")


def _face(file, weight):
    data = base64.b64encode(open(os.path.join(_FONTS, file), "rb").read()).decode()
    return f"@font-face{{font-family:Poppins;font-weight:{weight};src:url(data:font/woff2;base64,{data}) format('woff2')}}"


FONT_CSS = _face("poppins-semibold.woff2", "100 600") + _face("poppins-bold.woff2", "700 900")

SIZES = {
    #               canvas  radius header pill      header label body title number padding gap-below
    "desktop": dict(W=880, R=18, HDR=46, PILL=(84, 10), HEAD=13, LABEL=13, BODY=15, TITLE=20, NUM=32, PAD=26, GAP=16, suffix=""),
    "mobile":  dict(W=400, R=16, HDR=40, PILL=(56, 8),  HEAD=12, LABEL=12, BODY=14, TITLE=18, NUM=26, PAD=18, GAP=12, suffix="-m"),
}
M = 1  # inset so the 1px outline isn't clipped
for t in SIZES.values():
    t["X0"], t["X1"] = M + t["PAD"], t["W"] - M - t["PAD"]   # content edges
    t["TOP"] = M + t["HDR"]                                   # body start under a header


def frame(t, h, label, inner, header=None, delay=None, fill=NAVY, stroke=CORAL, stroke_opacity=".35"):
    """Rounded card of height h on a transparent canvas (+ optional coral header with badge slot)."""
    W, R, HDR = t["W"], t["R"], t["HDR"]
    head = ""
    if header:
        left, right = (html.escape(s) for s in header)
        pw, ph = t["PILL"]; cy = M + HDR / 2; base = cy + t["HEAD"] * 0.36
        head = (f'<rect x="{M}" y="{M}" width="{W-2*M}" height="{HDR}" fill="{CORAL}" clip-path="url(#card)"/>'
                f'<rect x="{W/2-pw/2:.0f}" y="{cy-ph/2:.0f}" width="{pw}" height="{ph}" rx="{ph/2:.0f}" fill="{NAVY}"/>'
                f'<text x="{t["X0"]}" y="{base:.0f}" font-size="{t["HEAD"]}" letter-spacing="2" fill="{NAVY}">{left}</text>'
                f'<text x="{t["X1"]}" y="{base:.0f}" font-size="{t["HEAD"]}" letter-spacing="2" fill="{NAVY}" text-anchor="end">{right}</text>')
    body = (f'<rect x="{M}" y="{M}" width="{W-2*M}" height="{h-2*M}" rx="{R}" fill="{fill}" '
            f'stroke="{stroke}" stroke-opacity="{stroke_opacity}"/>{head}{inner}')
    if delay is not None:
        body = f'<g class="in" style="animation-delay:{delay:.2f}s">{body}</g>'
    H = h + t["GAP"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{html.escape(label)}">
<title>{html.escape(label)}</title>
<defs><clipPath id="card"><rect x="{M}" y="{M}" width="{W-2*M}" height="{h-2*M}" rx="{R}"/></clipPath></defs>
<style>{FONT_CSS}
text{{font-family:{FONT};font-weight:700}}
.in{{animation:in .8s cubic-bezier(.22,.8,.3,1) backwards}}
@keyframes in{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:none}}}}</style>
{body}</svg>'''
