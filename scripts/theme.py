"""Shared design tokens + card frame for every generated README card.

Each card is rendered twice:
  desktop (1200 wide, file.svg)    — shown on wide screens, same type scale as assets/id-card.png
  mobile  (800 wide,  file-m.svg)  — shown under 600px via <picture>, larger type so it stays readable
"""
import base64, html, os

NAVY, NAVY2, CORAL, SAFFRON, IVORY, MUTED = "#101827", "#2C2332", "#FF754A", "#FF9933", "#F5EBDD", "#9AA3B5"
FONT = "Poppins,'Segoe UI',Helvetica,Arial,sans-serif"

# Poppins (SIL OFL, assets/fonts/OFL.txt) is embedded in every SVG so it renders the same everywhere.
_FONTS = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")


def _face(file, weight):
    data = base64.b64encode(open(os.path.join(_FONTS, file), "rb").read()).decode()
    return f"@font-face{{font-family:Poppins;font-weight:{weight};src:url(data:font/woff2;base64,{data}) format('woff2')}}"


FONT_CSS = _face("poppins-semibold.woff2", "100 600") + _face("poppins-bold.woff2", "700 900")

SIZES = {
    #          canvas  margin radius header  pill      header label body title value number
    "desktop": dict(W=1200, M=28, R=28, HDR=60, PILL=(110, 14), HEAD=13, LABEL=11, BODY=15, TITLE=20, VALUE=26, NUM=38, PAD=32, suffix=""),
    "mobile":  dict(W=800,  M=20, R=26, HDR=54, PILL=(84, 12),  HEAD=14, LABEL=12, BODY=16, TITLE=22, VALUE=30, NUM=42, PAD=28, suffix="-m"),
}
for t in SIZES.values():
    t["X0"], t["X1"] = t["M"] + t["PAD"], t["W"] - t["M"] - t["PAD"]   # content edges
    t["TOP"] = t["M"] + t["HDR"]                                         # body start under the header


def frame(t, h, label, inner, header=None, delay=None):
    """Ivory canvas + rounded navy card (+ optional coral header with badge slot)."""
    W, M, R, HDR = t["W"], t["M"], t["R"], t["HDR"]
    head = ""
    if header:
        left, right = (html.escape(s) for s in header)
        pw, ph = t["PILL"]; cy = M + HDR / 2; base = cy + t["HEAD"] * 0.36
        head = (f'<rect x="{M}" y="{M}" width="{W-2*M}" height="{HDR}" fill="{CORAL}" clip-path="url(#card)"/>'
                f'<rect x="{W/2-pw/2:.0f}" y="{cy-ph/2:.0f}" width="{pw}" height="{ph}" rx="{ph/2:.0f}" fill="{NAVY}"/>'
                f'<text x="{t["X0"]}" y="{base:.0f}" font-size="{t["HEAD"]}" letter-spacing="3" fill="{NAVY}">{left}</text>'
                f'<text x="{t["X1"]}" y="{base:.0f}" font-size="{t["HEAD"]}" letter-spacing="3" fill="{NAVY}" text-anchor="end">{right}</text>')
    body = f'<rect x="{M}" y="{M}" width="{W-2*M}" height="{h-2*M}" rx="{R}" fill="{NAVY}"/>{head}{inner}'
    if delay is not None:
        body = f'<g class="in" style="animation-delay:{delay:.2f}s">{body}</g>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{html.escape(label)}">
<title>{html.escape(label)}</title>
<defs><clipPath id="card"><rect x="{M}" y="{M}" width="{W-2*M}" height="{h-2*M}" rx="{R}"/></clipPath></defs>
<style>{FONT_CSS}
text{{font-family:{FONT};font-weight:700}}
.in{{animation:in .8s cubic-bezier(.22,.8,.3,1) backwards}}
@keyframes in{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:none}}}}</style>
<rect width="{W}" height="{h}" fill="{IVORY}"/>
{body}</svg>'''
