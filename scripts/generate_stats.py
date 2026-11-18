#!/usr/bin/env python3
"""Generates profile/github(-m).svg — stats + top languages in one card (desktop + mobile)
in the Hustler palette; tokens live in scripts/theme.py. Uses only the standard library.
Usage: GITHUB_TOKEN=... python scripts/generate_stats.py [username]
"""
import json, os, sys, urllib.request, urllib.parse, collections, html

USER = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GH_USER", "goyalvansh4")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
from theme import CORAL, SAFFRON, IVORY, MUTED, SOFT, SIZES, frame
LANG_COLORS = [CORAL, SAFFRON, IVORY, "#FFC48A", "#C9573A", MUTED]

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

# ---------- render: one GitHub card (stats + top languages), desktop + mobile ----------
items = [("STARS", stars), ("COMMITS", commits), ("PULL REQUESTS", prs), ("ISSUES", issues), ("REPOSITORIES", n_repos), ("FOLLOWERS", followers)]
for kind, t in SIZES.items():
    X0, X1, TOP, L, N, B = t["X0"], t["X1"], t["TOP"], t["LABEL"], t["NUM"], t["BODY"]
    desk = kind == "desktop"
    # stats grid: one row on desktop, 3 x 2 on phones
    cols = 6 if desk else 3; rows = len(items) // cols; colw = (X1 - X0) / cols; rowh = L + N + 26
    y0 = TOP + 22; body = ""
    for i, (lab, val) in enumerate(items):
        c, r = i % cols, i // cols
        x = X0 + colw * c + colw / 2; y = y0 + r * rowh
        body += (f'<g class="in" style="animation-delay:{i*0.1:.1f}s"><text x="{x:.0f}" y="{y+L:.0f}" font-size="{L}" letter-spacing="1.5" fill="{SOFT}" text-anchor="middle">{lab}</text>'
                 f'<text x="{x:.0f}" y="{y+L+8+N*0.9:.0f}" font-size="{N}" fill="{IVORY}" text-anchor="middle">{fmt(val)}</text></g>')
    for c in range(1, cols):
        body += f'<line x1="{X0+colw*c:.0f}" y1="{y0}" x2="{X0+colw*c:.0f}" y2="{y0+rows*rowh-22:.0f}" stroke="{IVORY}" stroke-opacity=".1"/>'
    for r in range(1, rows):
        body += f'<line x1="{X0}" y1="{y0+r*rowh-12:.0f}" x2="{X1}" y2="{y0+r*rowh-12:.0f}" stroke="{IVORY}" stroke-opacity=".1"/>'
    ys = y0 + rows * rowh - 6
    body += f'<line x1="{X0}" y1="{ys}" x2="{X1}" y2="{ys}" stroke="{IVORY}" stroke-opacity=".1"/>'

    # top languages
    yl = ys + 22 + L
    body += f'<text x="{X0}" y="{yl}" font-size="{L}" letter-spacing="1.5" fill="{CORAL}">TOP LANGUAGES</text>'
    bw = X1 - X0; x = X0; by = yl + 14; bh = 10
    body += f'<clipPath id="bar"><rect x="{X0}" y="{by}" width="{bw}" height="{bh}" rx="5"/></clipPath><g clip-path="url(#bar)">'
    for i, (n, v) in enumerate(top):
        w = bw * v / total; body += f'<rect x="{x:.1f}" y="{by}" width="{w:.1f}" height="{bh}" fill="{LANG_COLORS[i]}"/>'; x += w
    body += "</g>"
    lcols = 3 if desk else 2; cw2 = bw / lcols; gap = B * 1.9
    for i, (n, v) in enumerate(top):
        lx = X0 + (i % lcols) * cw2; ly = by + bh + 14 + B + (i // lcols) * gap
        right = lx + cw2 - (24 if i % lcols != lcols - 1 else 0)
        body += (f'<circle cx="{lx+5}" cy="{ly-B*0.33:.0f}" r="5" fill="{LANG_COLORS[i]}"/>'
                 f'<text x="{lx+16}" y="{ly:.0f}" font-size="{B}" font-weight="600" fill="{IVORY}">{html.escape(n)}</text>'
                 f'<text x="{right:.0f}" y="{ly:.0f}" font-size="{B}" font-weight="600" fill="{SOFT}" text-anchor="end">{v/total*100:.1f}%</text>')
    lrows = (len(top) + lcols - 1) // lcols
    H = round(by + bh + 14 + B + (lrows - 1) * gap + t["PAD"] - 4)
    open(f"profile/github{t['suffix']}.svg", "w").write(frame(t, H, "GitHub stats and top languages", body, header=("GITHUB", "@" + USER.upper())))
print("stats:", dict(items), "langs:", top)
