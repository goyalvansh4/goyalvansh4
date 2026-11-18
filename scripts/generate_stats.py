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
def card(w, h, title, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title)}">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset=".35" stop-color="{NAVY}"/><stop offset="1" stop-color="{NAVY2}"/></linearGradient></defs>
<style>text{{font-family:{FONT}}}
.in{{animation:in .7s ease-out backwards}}
@keyframes in{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}</style>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="26" fill="url(#g)" stroke="{CORAL}" stroke-width="2"/>
<rect x="1" y="1" width="{w-2}" height="54" rx="26" fill="{CORAL}"/><rect x="1" y="28" width="{w-2}" height="27" fill="{CORAL}"/>
<text x="32" y="35" font-size="17" font-weight="800" letter-spacing="3" fill="{NAVY}">{html.escape(title)}</text>
<text x="{w-32}" y="35" font-size="17" font-weight="800" letter-spacing="3" fill="{NAVY}" text-anchor="end">{html.escape(USER.upper())}</text>
{body}</svg>'''

# ---------- stats card ----------
items = [("STARS", stars), ("COMMITS", commits), ("PULL REQUESTS", prs), ("ISSUES", issues), ("REPOSITORIES", n_repos), ("FOLLOWERS", followers)]
W, H = 1200, 230; colw = (W - 64) / len(items); body = ""
for i, (lab, val) in enumerate(items):
    x = 32 + colw * i + colw / 2
    body += f'<g class="in" style="animation-delay:{i*0.12:.2f}s"><text x="{x:.0f}" y="146" font-size="52" font-weight="800" fill="{IVORY}" text-anchor="middle">{fmt(val)}</text>'
    body += f'<text x="{x:.0f}" y="182" font-size="13" font-weight="800" letter-spacing="2.5" fill="{CORAL}" text-anchor="middle">{lab}</text></g>'
    if i: body += f'<line x1="{32+colw*i:.0f}" y1="100" x2="{32+colw*i:.0f}" y2="190" stroke="{IVORY}" stroke-opacity=".15"/>'
open("profile/stats.svg", "w").write(card(W, H, "GITHUB STATS", body))

# ---------- top languages card ----------
H2 = 250; bx, bw = 32, W - 64; x = bx; bar = f'<clipPath id="c"><rect x="{bx}" y="92" width="{bw}" height="22" rx="11"/></clipPath><g clip-path="url(#c)">'
for i, (n, v) in enumerate(top):
    w = bw * v / total; bar += f'<rect x="{x:.1f}" y="92" width="{w:.1f}" height="22" fill="{LANG_COLORS[i]}"/>'; x += w
bar += "</g>"
leg = ""
cols = 3; cw2 = bw / cols
for i, (n, v) in enumerate(top):
    lx = bx + (i % cols) * cw2; ly = 160 + (i // cols) * 44
    leg += f'<g class="in" style="animation-delay:{i*0.1:.1f}s"><circle cx="{lx+8:.0f}" cy="{ly-6}" r="7" fill="{LANG_COLORS[i]}"/><text x="{lx+26:.0f}" y="{ly}" font-size="18" font-weight="700" fill="{IVORY}">{html.escape(n)}</text><text x="{lx+cw2-24:.0f}" y="{ly}" font-size="18" font-weight="800" fill="{CORAL}" text-anchor="end">{v/total*100:.1f}%</text></g>'
open("profile/top-langs.svg", "w").write(card(W, H2, "TOP LANGUAGES", bar + leg))
print("stats:", dict(items), "langs:", top)
