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

# The generator's own constants, so the assertions below track the source
# rather than a copy of it. Importing is safe: build.py does its work in
# build(), which is only called from main() under __main__.
sys.path.insert(0, str(HERE))
import build as gen  # noqa: E402

DETAIL_MAG = gen.DETAIL_MAG
SLIVER = gen.SLIVER
SLIVER_PX = gen.SLIVER_PX
DENOM = gen.DENOM
CONTRIB = gen.WORKED["w"] * gen.WORKED["presence"] * gen.WORKED["likelihood"]

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
check("ruler svg present", "<svg" in html
      and re.search(r'class="ruler" viewBox="0 0 320 \d+"', html) is not None)
check("ruler has aria-label", 'aria-label="AI Usage Score' in html)
check("ruler labels 0 and 100", ">0<" in html and ">100<" in html)
# FIG. 1 is a title block now, so the band edges are stations on a dimension
# line rather than tick labels. The edges are pinned here so a change to
# SKILL.md's bands cannot silently move a station on the drawing. Counts are
# scoped to the ruler svg, because FIG. 2 uses the same drafting vocabulary.
check("ruler dimension line drawn", svg is not None and 'class="dim"' in svg.group(0))
check("ruler has a witness line per station",
      svg is not None and svg.group(0).count('class="wit"') == 6)
check("ruler has two slashed terminators",
      svg is not None and svg.group(0).count('class="term"') == 2)
check("ruler stations are the real band edges",
      all(f">{e}<" in html for e in (0, 15, 35, 60, 80, 100)))
check("ruler figure is captioned",
      "<figcaption>FIG. 1 &mdash; AI USAGE SCORE, FIVE BANDS, &Sigma;w 37.5"
      in html)
check("ruler aria-label names every band",
      all(b in html for b in ("Human-crafted", "Human plus AI assists",
                              "Hybrid", "AI-dominant", "Vibecoded.")))
check("legend swatch decodes each band fill",
      all(f'class="sw b{i}"' in html for i in range(1, 6)))
check("legend keeps its 5 range spans", html.count('<li><span class="rng">') == 5)

print("\n== how a point is scored (FIG. 2) ==")
fig2 = re.search(r'<svg class="calc-svg".*?</svg>', html, re.S)
check("fig 2 svg present", fig2 is not None
      and re.search(r'class="calc-svg" viewBox="0 0 \d+ \d+', html)
      is not None)
f2 = fig2.group(0) if fig2 else ""
check("section exists and is nav-wired", 'id="scored"' in html and 'href="#scored"' in html)
check("sec-no renumbered 03-05", "03 &mdash; How a point is scored" in html
      and "05 &mdash; Install" in html)
check("worked example is point 12", "Colored Border Cards" in html)
# The arithmetic is generated, not typed, and comes from SKILL.md section 3.
# These regexes tolerate the line wrapping the template leaves in the cell.
check("arithmetic is printed on the page",
      re.search(r"1\.0 (?:&times;|×)\s*1 (?:&times;|×)\s*2 = 2\.000", html)
      is not None)
check("denominator printed and derived",
      re.search(r"750 = 37\.5 (?:&Sigma;|Σ)w (?:&times;|×) 4 (?:&times;|×) 5",
                html) is not None)
# The shipped self-audit prints 0.400 for point 12, which its own cited
# formula cannot produce. The page follows the formula instead, so the
# unreconcilable figure must not appear anywhere in the output.
check("worked figure comes from the formula, not the report",
      "0.400" not in html)
check("presence and likelihood ranges printed",
      f"presence {gen.WORKED['presence_range']}" in f2
      and f"likelihood {gen.WORKED['likelihood_range']}" in f2)
# character references are not decoded inside inline SVG <text>, so a stray
# entity in the figure would render as literal punctuation
check("no character references inside the figures",
      not re.search(r"&[a-z]{2,6};", f2)
      and not re.search(r"&[a-z]{2,6};", svg.group(0)))
check("detail magnification declared and consistent",
      f">DETAIL {DETAIL_MAG}:1<" in f2 and 'class="break"' in f2)
check("the sliver really is too narrow to draw at scale",
      f"{SLIVER_PX:.2f} of 304 drawn units" in f2 and SLIVER_PX < 1.5)
check("schematic tagged not to scale",
      "SCHEMATIC" in f2 and "NOT TO SCALE" in f2)
check("fig 2 has witness lines, a datum and a leader",
      'class="wit"' in f2 and 'class="datum"' in f2 and 'class="lead"' in f2)
check("fig 2 aria-label is complete",
      'aria-label="Annotated section drawing' in f2
      and "0.267 per cent of the bar's width" in f2)
check("fig 2 has no band names (it is not the ruler)",
      "Vibecoded" not in f2)
check("fig 2 is captioned", "<figcaption>FIG. 2 &mdash; POINT 12 RESOLVED." in html)
check("worked-example cells avoid the checklist num class",
      '<td class="v">2.000</td>' in html and html.count('<td class="num">') == 36)
check("the scoring section states which source wins a disagreement",
      re.search(r"the\s+report is wrong and the\s+formula is what settles it",
                html) is not None)

print("\n== the four open findings are closed ==")
# point 5: three italic serif spans in one hero paragraph scored 0.800. The
# shipped blueprint's own remedy is to keep exactly one.
check("exactly one italic on the page", html.count("<em>") == 1)
check("the survivor is 'line to change'", "<em>line to change</em>" in html)
# point 25: the X-not-Y pivot, 0.267. The remedy is a flat claim.
check("pivot removed", "not the vibe to change" not in html)
check("flat claim printed", "Every point names the" in html)
# point 12: the 3px moss left-strip was all of 0.400.
check("moss left-strip removed from .spec", "border-left" not in low)
check(".spec uses a rule box + ink top rule",
      re.search(r"\.spec\s*\{[^}]*border:\s*1px solid var\(--rule\)", html)
      is not None
      and re.search(r"\.spec\s*\{[^}]*border-top:\s*2px solid var\(--ink\)", html)
      is not None)
# point 32: /terms and /privacy did not exist and the footer carried no legal
# links. 0.800 -- the largest of the four.
check("footer links both legal pages",
      html.count('href="/terms"') == 1 and html.count('href="/privacy"') == 1)
check("page states the four findings are closed",
      "The four findings are closed" in html)
check("no fabricated post-fix score",
      "2.0 —" not in html and "2.0 &mdash;" not in html)

print("\n== legal pages (point 32) ==")
for slug, words in (("terms", ("apache-2.0", "no warranty")),
                    ("privacy", ("no analytics", "no cookies",
                                 "opens no network sockets"))):
    p = DIST / f"{slug}.html"
    check(f"{slug}.html generated", p.exists())
    if not p.exists():
        continue
    doc = p.read_text(encoding="utf-8")
    dlow = doc.lower()
    check(f"{slug} has exactly one h1", doc.count("<h1>") == 1)
    check(f"{slug} states its own subject",
          all(w in dlow for w in words))
    check(f"{slug} is dated", "2026-09-26" in doc)
    check(f"{slug} ships no JS", "<script" not in dlow)
    check(f"{slug} has no dead links", 'href="#"' not in dlow and 'href=""' not in dlow)
    check(f"{slug} reuses the palette",
          all(h in dlow for h in ("#fbfaf7", "#14181d", "#b4451f", "#d9d3c7")))
    check(f"{slug} reuses the type system",
          "charter" in dlow and "lato" in dlow and "fira code" in dlow)
    check(f"{slug} has a focus ring and a skip link",
          ":focus-visible" in dlow and 'class="skip"' in dlow)
    check(f"{slug} is linked from its sibling", f'href="/{slug}"' in doc)
    check(f"{slug} has no unreplaced tokens", "{{" not in doc)
check("index links both legal pages in the footer",
      'class="legal"><a href="/terms">' in html
      and '<a href="/privacy">' in html)

print("\n== accessibility ==")
# The audit's own instrument had no focus state at all. WCAG 2.2 2.4.11
# Focus Appearance is AA, and there was nothing to pass.
check("focus-visible ring declared",
      re.search(r":focus-visible\s*\{[^}]*outline:\s*2px solid var\(--ink\)", html)
      is not None)
check("focus ring is offset from the component",
      re.search(r":focus-visible\s*\{[^}]*outline-offset:\s*2px", html) is not None)
check("skip link exists and is first in body",
      'class="skip" href="#main"' in html
      and re.search(r'<body>\s*<a class="skip"', html) is not None)
check("skip link has a target", 'id="main"' in html and "<main" in html)
check("skip link becomes visible on focus",
      re.search(r"\.skip:focus-visible\s*\{[^}]*position:\s*fixed", html) is not None)
check("reduced motion respected",
      "@media (prefers-reduced-motion: reduce)" in html)
# the page prints measured numbers, so the digits must line up
for sel in [r"\.ruler\s*\{[^}]*tabular-nums",
            r"\.spec\s*\{[^}]*tabular-nums",
            r"td\.num\s*\{[^}]*tabular-nums",
            r"td\.w\s*\{[^}]*tabular-nums"]:
    check(f"tabular-nums on {sel.split('}')[0][2:]}", re.search(sel, html) is not None)
# point 4's own antidote, applied to the page that publishes it
check("type scale declared as a ratio", "--r: 1.25" in low)
check("scale steps are derived from the ratio",
      "calc(var(--base) * var(--r))" in low
      and "calc(var(--base) / var(--r))" in low)
ad_hoc = re.findall(r"font-size:\s*(\d+(?:\.\d+)?)px", html)
check("no ad-hoc pixel font sizes left", not ad_hoc, str(sorted(set(ad_hoc))))
check("measure is a variable", "--measure: 62ch" in low)
check("dense measure is a second variable", "--measure-dense: 56ch" in low)
check("dense measure used by the table", "max-width: var(--measure-dense)" in html)
check("h1 and h2 balance their lines",
      re.search(r"h1\s*\{[^}]*text-wrap:\s*balance", html) is not None
      and re.search(r"h2\s*\{[^}]*text-wrap:\s*balance", html) is not None)
check("prose sets its orphans",
      re.search(r"\.lede\s*\{[^}]*text-wrap:\s*pretty", html) is not None
      and re.search(r"\.sub\s*\{[^}]*text-wrap:\s*pretty", html) is not None)
check("interactive target sizes grown to 44px",
      "inset: -13px -4px" in html)
check("narrow-screen antidote column is dropped, not shrunk",
      re.search(r"@media \(max-width: 560px\)\s*\{\s*th\.cm, td\.cm", html)
      is not None)
# the PDF cover eyebrow was 3.24:1 on ink
rpt = HERE.parent / "report-styles.css"
rs = rpt.read_text(encoding="utf-8")
check("PDF lifts rust for the cover eyebrow",
      "--rust-lift: #e08a5f" in rs and re.search(
          r"\.cover \.eyebrow\s*\{[^}]*color:\s*var\(--rust-lift\)", rs) is not None)
check("PDF cover band chip lifted too",
      re.search(r"\.cover \.band\s*\{[^}]*border:\s*1px solid var\(--rust-lift\)", rs)
      is not None)
check("the 78pt score numeral keeps --rust (3.24:1 clears large text)",
      re.search(r"\.cover \.score-num\s*\{[^}]*color:\s*var\(--rust\)", rs) is not None)

print("\n== one palette, two files ==")


def root_tokens(text):
    body = re.search(r":root\s*\{(.*?)\}", text, re.S)
    body = body.group(1) if body else text
    return {k: v.strip() for k, v in
            re.findall(r"--([a-z0-9-]+)\s*:\s*([^;]+);", body)}


site_tok, pdf_tok = root_tokens(html), root_tokens(rs)
# The three font stacks differ on purpose: the PDF needs print-safe
# substitutes for headless Linux, the site needs screen fallbacks. Nothing
# else may disagree, or the two files have drifted apart under the same name.
conflicts = {k: (site_tok[k], pdf_tok[k]) for k in set(site_tok) & set(pdf_tok)
             if site_tok[k] != pdf_tok[k]}
check("only the font stacks differ between the two stylesheets",
      set(conflicts) <= {"mono", "sans", "serif"}, str(conflicts))
for name in ("paper", "ink", "rule", "rust", "rust-lift", "moss", "gold"):
    check(f"--{name} is byte-identical in both",
          site_tok.get(name) == pdf_tok.get(name),
          f"site={site_tok.get(name)} pdf={pdf_tok.get(name)}")
check("no token name means two colours across the two files",
      all(k in ("mono", "sans", "serif") for k in conflicts), str(conflicts))
check("site surface and PDF paper-2 are the same hex under two names",
      site_tok.get("surface") == pdf_tok.get("paper-2"))

print("\n== showcase <-> repository cross-links ==")
REPO = "https://github.com/Himath-Rajapaksha/bytesmith"
check("nav links to the repo", f'href="{REPO}"' in html)
check("footer links to the repo", html.count(f'href="{REPO}"') >= 2)
check("install step shows git clone", "git clone" in low and REPO in html)
check("no bare cp-only install", "cp -r bytesmith ~/.config/opencode/skills/" in low)
check("states its own audited score", "11.3" in html and "human-crafted" in low)
check("links the self-audit report",
      "bytesmith-showcase-self-audit.pdf" in html)
check("names the license", "apache-2.0" in low)
# a link that 404s is exactly what point 35 punishes, so the targets must exist
for rel in ["examples/bytesmith-showcase-self-audit.pdf",
            "examples/acme-vibecode-audit.pdf",
            "LICENSE", "NOTICE"]:
    check(f"link target exists: {rel}", (HERE.parent / rel).exists())

print("\n== claims match the artifacts they describe ==")
# A page that states a number must state the real one. This reads the shipped
# PDF rather than trusting the constant, which is the only way a stale figure
# gets caught: the "11-page" claim outlived a re-render that made it 12.
pdf = HERE.parent / "examples" / "bytesmith-showcase-self-audit.pdf"
if pdf.exists():
    try:
        import re as _re
        raw = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
        m = _re.search(r"Pages:\s+(\d+)", raw.stdout)
        if m:
            actual = int(m.group(1))
            claimed = _re.search(r"read the (\d+)-page audit", html)
            check("claims a page count", claimed is not None)
            check(f"page count claim matches the PDF ({actual})",
                  claimed is not None and int(claimed.group(1)) == actual,
                  f"page says {claimed.group(1) if claimed else '?'}, PDF has {actual}")
    except FileNotFoundError:
        print("  SKIP  pdfinfo unavailable; cannot verify the page-count claim")
    txt = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout
    m = _re.search(r"\b(\d+\.\d)\b", txt.split("Σ =")[0] if "Σ =" in txt else "")
    check("self-audit score appears in the shipped PDF", "11.3" in txt)
    check("self-audit band appears in the shipped PDF", "HUMAN-CRAFTED" in txt.upper())
else:
    check("self-audit PDF shipped", False, "file missing")
check("no 'parsed live' claim (page ships no JS)", "parsed live" not in low)
check("copy states build-time generation", "at build time" in low)
check("verification claims are checkable", "/actions" in html)
check("licence rationale stated", "express patent grant" in low)

print("\n== structure ==")
check("single h1", html.count("<h1>") == 1)
check("section ids wired to nav",
      all(f'id="{i}"' in html for i in ["runs", "points", "scored", "blueprint", "install"]))
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
