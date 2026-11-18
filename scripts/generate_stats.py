#!/usr/bin/env python3
"""Generates profile/stats(-m).svg and profile/top-langs(-m).svg (desktop + mobile)
in the Hustler palette; tokens live in scripts/theme.py. Uses only the standard library.
Usage: GITHUB_TOKEN=... python scripts/generate_stats.py [username]
"""
import json, os, sys, urllib.request, urllib.parse, collections, html

USER = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GH_USER", "goyalvansh4")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
from theme import CORAL, SAFFRON, IVORY, MUTED, SIZES, frame
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

# ---------- render (desktop + mobile, tokens in scripts/theme.py) ----------

items = [("STARS", stars), ("COMMITS", commits), ("PULL REQUESTS", prs), ("ISSUES", issues), ("REPOSITORIES", n_repos), ("FOLLOWERS", followers)]
for kind, t in SIZES.items():
    X0, X1, TOP, L, N = t["X0"], t["X1"], t["TOP"], t["LABEL"], t["NUM"]
    cols = 6 if kind == "desktop" else 3            # one row on desktop, 3 x 2 grid on phones
    rows = len(items) // cols; colw = (X1 - X0) / cols; rowh = L + N + 46
    body = ""
    for i, (lab, val) in enumerate(items):
        c, r = i % cols, i // cols
        x = X0 + colw * c + colw / 2; y = TOP + 26 + r * rowh
        body += (f'<g class="in" style="animation-delay:{i*0.12:.2f}s"><text x="{x:.0f}" y="{y+L+8:.0f}" font-size="{L}" letter-spacing="3" fill="{CORAL}" text-anchor="middle">{lab}</text>'
                 f'<text x="{x:.0f}" y="{y+L+12+N:.0f}" font-size="{N}" fill="{IVORY}" text-anchor="middle">{fmt(val)}</text></g>')
    for c in range(1, cols):
        body += f'<line x1="{X0+colw*c:.0f}" y1="{TOP+30}" x2="{X0+colw*c:.0f}" y2="{TOP+26+rows*rowh-20:.0f}" stroke="{IVORY}" stroke-opacity=".15"/>'
    for r in range(1, rows):
        body += f'<line x1="{X0}" y1="{TOP+26+r*rowh-12:.0f}" x2="{X1}" y2="{TOP+26+r*rowh-12:.0f}" stroke="{IVORY}" stroke-opacity=".15"/>'
    H = TOP + 26 + rows * rowh + t["M"]
    open(f"profile/stats{t['suffix']}.svg", "w").write(frame(t, H, "GitHub stats", body, header=("GITHUB STATS", USER.upper())))

    # top languages: bar + legend (3 columns desktop, 2 on phones)
    B = t["BODY"]; bw = X1 - X0; x = X0; by = TOP + 32; bh = B + 2
    bar = f'<clipPath id="bar"><rect x="{X0}" y="{by}" width="{bw}" height="{bh}" rx="{bh/2:.0f}"/></clipPath><g clip-path="url(#bar)">'
    for i, (n, v) in enumerate(top):
        w = bw * v / total; bar += f'<rect x="{x:.1f}" y="{by}" width="{w:.1f}" height="{bh}" fill="{LANG_COLORS[i]}"/>'; x += w
    bar += "</g>"
    cols = 3 if kind == "desktop" else 2; cw2 = bw / cols; gap = B * 2.1; leg = ""
    for i, (n, v) in enumerate(top):
        lx = X0 + (i % cols) * cw2; ly = by + bh + B * 2.6 + (i // cols) * gap
        right = lx + cw2 - (B * 1.2 if i % cols != cols - 1 else 0)
        leg += (f'<g class="in" style="animation-delay:{i*0.1:.1f}s"><circle cx="{lx+B*0.4:.0f}" cy="{ly-B*0.35:.0f}" r="{B*0.38:.1f}" fill="{LANG_COLORS[i]}"/>'
                f'<text x="{lx+B*1.3:.0f}" y="{ly:.0f}" font-size="{B}" font-weight="600" fill="{IVORY}">{html.escape(n)}</text>'
                f'<text x="{right:.0f}" y="{ly:.0f}" font-size="{B}" fill="{CORAL}" text-anchor="end">{v/total*100:.1f}%</text></g>')
    rows = (len(top) + cols - 1) // cols
    H2 = by + bh + B * 2.6 + (rows - 1) * gap + B * 1.4 + t["M"]
    open(f"profile/top-langs{t['suffix']}.svg", "w").write(frame(t, round(H2), "Top languages", bar + leg, header=("TOP LANGUAGES", USER.upper())))
print("stats:", dict(items), "langs:", top)
