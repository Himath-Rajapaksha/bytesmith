#!/usr/bin/env python3
"""Assert the generated showcase page is internally consistent and rule-clean.

    python3 site/test_build.py
"""

import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
DIST = HERE / "dist"
INDEX = DIST / "index.html"

failures = []


def check(label, cond, detail=""):
    if cond:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label} {detail}")
        failures.append(label)


print("== build ==")
r = subprocess.run(
    [sys.executable, str(HERE / "build.py")], capture_output=True, text=True
)
check("build.py exits 0", r.returncode == 0, r.stderr.strip()[:300])
check("index.html written", INDEX.exists())

html = INDEX.read_text(encoding="utf-8")
low = html.lower()

print("\n== content parity with the skill ==")
check("36 point rows", len(re.findall(r'<td class="num">\d+</td>', html)) == 36)
check("36 blueprint disclosures", html.count("<details>") == 36)
check("5 group heads", html.count('class="group-head"') == 5)
svg = re.search(r'<svg class="ruler".*?</svg>', html, re.S)
check("ruler svg has 5 band rects",
      svg is not None and len(re.findall(r'<rect ', svg.group(0))) == 5)
check("5 band labels in key", html.count('<li><span class="rng">') == 5)
check("all 36 point numbers present",
      all(f'<td class="num">{n}</td>' in html for n in range(1, 37)))
check("no unreplaced build tokens", "{{" not in html, )

print("\n== palette (design constraint) ==")
for name, hexv in [
    ("paper", "#fbfaf7"), ("surface", "#f2efe8"), ("ink", "#14181d"),
    ("rust", "#b4451f"), ("moss", "#4a5d3a"), ("gold", "#8a6d1f"),
    ("rule", "#d9d3c7"),
]:
    check(f"{name} {hexv} present", hexv in low)

print("\n== forbidden patterns (own checklist) ==")
# gradients: no gradient declarations of any kind
grad = re.findall(r"(linear-gradient|radial-gradient|conic-gradient|gradient-to)", low)
check("no gradients", not grad, f"found {set(grad)}")
# Inter / the overused-font list, outside of the fingerprint name in prose
# Inter / the overused-font list: only a *real* font reference counts, so match
# word boundaries. The page may still name these families inside quoted remedy
# text (that is the antidote telling you to avoid them) — that is not a violation.
QUOTED_OK = ("not* inter", "not inter", "forbidden", "overused", "antidote")
for fam in ["inter", "geist", "space grotesk", "plus jakarta", "satoshi",
            "instrument serif", "general sans"]:
    hits = [m.start() for m in re.finditer(rf"\b{fam}\b", low)]
    bad = [
        h for h in hits
        if not any(k in low[max(0, h - 200):h + 200] for k in QUOTED_OK)
    ]
    check(f"no '{fam}' as an actual font", not bad, f"{len(bad)} bare use(s)")
# and the font stacks themselves must not name any of them
stacks = re.findall(r"font-family:[^;}]+", low)
bad_stacks = [s for s in stacks if any(
    re.search(rf"\b{f}\b", s) for f in
    ["inter", "geist", "space grotesk", "plus jakarta", "satoshi"])]
check("no forbidden family in any font-family stack", not bad_stacks, str(bad_stacks))
# "bento" may appear only as the NAME of fingerprint 10 or in the scanner list.
BENTo_OK = ["hero and bento components", "bento grids", "10 · bento", "anti"]
bento_hits = [m.start() for m in re.finditer(r"\bbento\b", low)]
bad_bento = [
    h for h in bento_hits
    if not any(k in low[max(0, h - 120):h + 120] for k in BENTo_OK)
]
check("'bento' only as a named fingerprint, never a layout", not bad_bento,
      f"{len(bad_bento)} other use(s)")
# the actual layout crime: an equal-weight 3-up mosaic of cards
check("no 3-up equal grid", "repeat(3" not in low.replace("repeat(3,", "@", 0)
      or "cards" not in low)
check("no card mosaic class", not re.search(r'class="[^"]*\b(cards|card-grid|bento)\b', html))
# layout is tables, definition lists and ruled steps
check("uses table rows for the checklist", html.count("<tr>") >= 36)
check("uses ruled steps not cards", html.count('<li><b>') == 5)
check("no sparkle/emoji glyphs", not re.search(r"[\U0001F300-\U0001FAFF✨]", html))
check("single primary CTA", low.count('class="cta"') == 1)
check("CTA left-aligned in flow", "text-align: center" not in low)

print("\n== typography ==")
check("serif display stack", "charter" in low and "serif" in low)
check("sans text stack", "lato" in low)
check("mono spec stack", "fira code" in low)
check("h1 uses serif", re.search(r"h1\s*\{[^}]*var\(--serif\)", html) is not None)
# smart punctuation is fine in prose, but code samples must stay ASCII
smart = {"–": "en dash", "—": "em dash", "‘": "curly quote",
         "’": "curly quote", "“": "curly quote", "”": "curly quote"}
bad_code = [
    (m.group(1), ch)
    for m in re.finditer(r"<code>(.*?)</code>", html)
    for ch in m.group(1) if ch in smart
]
check("no smart punctuation inside <code>", not bad_code, str(bad_code[:3]))
check("code samples use ascii hyphens",
      all("–" not in m.group(1) for m in re.finditer(r"<code>(.*?)</code>", html)))

print("\n== copy: repo-first execution model ==")
check("says it runs in your project", "runs inside your project" in low)
check("mentions package.json", "package.json" in low)
check("promises file:line anchors", "src/app/globals.css:58" in html)
check("output path stated", "bytesmith-report" in low)
check("no URL-only framing", "point it at a url" not in low)
check("hero headline present", "every ai-built page leaves prints." in low)
check("eyebrow present", "forensic design audit for the web" in low)

print("\n== hero asymmetry + band artifact ==")
check("hero grid 7fr 5fr", re.search(r"\.hero\s*\{[^}]*7fr 5fr", html) is not None)
check("ruler svg present", "<svg" in html and 'viewBox="0 0 320 52"' in html)
check("ruler has aria-label", 'aria-label="AI Usage Score' in html)
check("ruler labels 0 and 100", ">0<" in html and ">100<" in html)

print("\n== structure ==")
check("single h1", html.count("<h1>") == 1)
check("section ids wired to nav",
      all(f'id="{i}"' in html for i in ["runs", "points", "blueprint", "install"]))
check("has viewport meta", 'name="viewport"' in html)
check("has description meta", 'name="description"' in html)
check("lang attribute", 'lang="en"' in html)
check("responsive breakpoint", "@media (max-width" in low)
check("no external JS", "<script" not in low)

print("\n== radius assigned by hierarchy (not one soft value) ==")
check("sharp rules/rows", "border-radius: 0" in low)
check("tight panel radius", "border-radius: 2px" in low)
check("no pill buttons", "border-radius: 999" not in low and "50%" not in low.replace("50%", "", 0) or "border-radius" not in low)

print()
if failures:
    print(f"{len(failures)} FAILURE(S): {failures}")
    raise SystemExit(1)
print("all checks passed")
