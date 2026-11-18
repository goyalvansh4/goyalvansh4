#!/usr/bin/env python3
"""Generates profile/stats.svg and profile/top-langs.svg in the Hustler palette
(navy / coral / saffron / ivory). Uses only the standard library.
Usage: GITHUB_TOKEN=... python scripts/generate_stats.py [username]
"""
import json, os, sys, urllib.request, urllib.parse, collections, html

USER = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GH_USER", "goyalvansh4")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
NAVY, NAVY2, CORAL, SAFFRON, IVORY, MUTED = "#101827", "#2C2332", "#FF754A", "#FF9933", "#F5EBDD", "#9AA3B5"
LANG_COLORS = [CORAL, SAFFRON, IVORY, "#FFC48A", "#C9573A", MUTED]
FONT = "'Segoe UI',Helvetica,Arial,sans-serif"

def api(path, accept="application/vnd.github+json"):
    req = urllib.request.Request("https://api.github.com" + path, headers={"Accept": accept, "User-Agent": "hustler-stats"})
    if TOKEN: req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)

def safe(fn, default):
    try: return fn()
    except Exception as e:
        print("warn:", e, file=sys.stderr); return default

def fmt(n):
    if n is None: return "—"
    return f"{n/1000:.1f}k" if n >= 10000 else f"{n:,}"

# ---------- data ----------
user = safe(lambda: api(f"/users/{USER}"), {})
repos, page = [], 1
while True:
    chunk = safe(lambda: api(f"/users/{USER}/repos?per_page=100&type=owner&page={page}"), [])
    repos += chunk
    if len(chunk) < 100: break
    page += 1
if not repos:  # fallback when core rate-limit is exhausted
    s = safe(lambda: api(f"/search/repositories?q=user:{USER}&per_page=100"), {})
    repos = s.get("items", [])
own = [r for r in repos if not r.get("fork")]
stars = sum(r.get("stargazers_count", 0) for r in own)
commits = safe(lambda: api(f"/search/commits?q=author:{USER}")["total_count"], 0)
prs = safe(lambda: api(f"/search/issues?q=author:{USER}+type:pr")["total_count"], 0)
issues = safe(lambda: api(f"/search/issues?q=author:{USER}+type:issue")["total_count"], 0)
n_repos = user.get("public_repos")
if n_repos is None: n_repos = safe(lambda: api(f"/search/repositories?q=user:{USER}&per_page=1")["total_count"], None)
followers = user.get("followers")

langs = collections.Counter(); ok = True
for r in own:
    d = safe(lambda: api(f"/repos/{USER}/{r['name']}/languages"), None)
    if d is None: ok = False; break
    langs.update(d)
if not ok:  # rate-limited: use each repo's primary language instead (never mix units)
    langs = collections.Counter(r["language"] for r in own if r.get("language"))
top = langs.most_common(6); total = sum(v for _, v in top) or 1

# ---------- svg helpers ----------
# Same look as assets/id-card.png: ivory canvas, navy card, coral header strip with a badge slot.
# Cards are 800px wide with large type so they stay readable when GitHub shrinks them on phones.
M, R, HDR = 20, 26, 64  # outer margin, corner radius, header height

def card(w, h, title, body):
    cw, ch = w - 2 * M, h - 2 * M
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title)}">
<defs><clipPath id="card"><rect x="{M}" y="{M}" width="{cw}" height="{ch}" rx="{R}"/></clipPath></defs>
<style>text{{font-family:{FONT}}}
.in{{animation:in .7s ease-out backwards}}
@keyframes in{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}</style>
<rect width="{w}" height="{h}" fill="{IVORY}"/>
<g clip-path="url(#card)"><rect x="{M}" y="{M}" width="{cw}" height="{ch}" fill="{NAVY}"/><rect x="{M}" y="{M}" width="{cw}" height="{HDR}" fill="{CORAL}"/></g>
<rect x="{w/2-45:.0f}" y="{M+HDR/2-7:.0f}" width="90" height="14" rx="7" fill="{NAVY}"/>
<text x="{M+28}" y="{M+HDR/2+7:.0f}" font-size="20" font-weight="800" letter-spacing="3" fill="{NAVY}">{html.escape(title)}</text>
<text x="{w-M-28}" y="{M+HDR/2+7:.0f}" font-size="20" font-weight="800" letter-spacing="3" fill="{NAVY}" text-anchor="end">{html.escape(USER.upper())}</text>
{body}</svg>'''

W = 800; X0, X1 = M + 28, W - M - 28  # content edges
TOP = M + HDR                           # body starts here

# ---------- stats card: 3 x 2 grid ----------
items = [("STARS", stars), ("COMMITS", commits), ("PULL REQUESTS", prs), ("ISSUES", issues), ("REPOSITORIES", n_repos), ("FOLLOWERS", followers)]
H = TOP + 262 + M; colw = (X1 - X0) / 3; rowh = 124; body = ""
for i, (lab, val) in enumerate(items):
    c, r = i % 3, i // 3
    x = X0 + colw * c + colw / 2; y = TOP + 22 + r * rowh
    body += f'<g class="in" style="animation-delay:{i*0.12:.2f}s"><text x="{x:.0f}" y="{y+30}" font-size="18" font-weight="800" letter-spacing="3" fill="{CORAL}" text-anchor="middle">{lab}</text>'
    body += f'<text x="{x:.0f}" y="{y+94}" font-size="60" font-weight="800" fill="{IVORY}" text-anchor="middle">{fmt(val)}</text></g>'
for c in (1, 2):
    body += f'<line x1="{X0+colw*c:.0f}" y1="{TOP+30}" x2="{X0+colw*c:.0f}" y2="{TOP+240}" stroke="{IVORY}" stroke-opacity=".15"/>'
body += f'<line x1="{X0}" y1="{TOP+22+rowh-8}" x2="{X1}" y2="{TOP+22+rowh-8}" stroke="{IVORY}" stroke-opacity=".15"/>'
open("profile/stats.svg", "w").write(card(W, H, "GITHUB STATS", body))

# ---------- top languages card: bar + 2-column legend ----------
bw = X1 - X0; x = X0; by = TOP + 32
bar = f'<clipPath id="bar"><rect x="{X0}" y="{by}" width="{bw}" height="26" rx="13"/></clipPath><g clip-path="url(#bar)">'
for i, (n, v) in enumerate(top):
    w = bw * v / total; bar += f'<rect x="{x:.1f}" y="{by}" width="{w:.1f}" height="26" fill="{LANG_COLORS[i]}"/>'; x += w
bar += "</g>"
leg = ""; cols = 2; cw2 = bw / cols; rows = (len(top) + cols - 1) // cols
for i, (n, v) in enumerate(top):
    lx = X0 + (i % cols) * cw2; ly = by + 84 + (i // cols) * 50
    leg += f'<g class="in" style="animation-delay:{i*0.1:.1f}s"><circle cx="{lx+10:.0f}" cy="{ly-8}" r="9" fill="{LANG_COLORS[i]}"/><text x="{lx+32:.0f}" y="{ly}" font-size="24" font-weight="700" fill="{IVORY}">{html.escape(n)}</text><text x="{lx+cw2-(28 if i % cols == 0 else 0):.0f}" y="{ly}" font-size="24" font-weight="800" fill="{CORAL}" text-anchor="end">{v/total*100:.1f}%</text></g>'
H2 = by + 84 + (rows - 1) * 50 + 34 + M
open("profile/top-langs.svg", "w").write(card(W, H2, "TOP LANGUAGES", bar + leg))
print("stats:", dict(items), "langs:", top)
