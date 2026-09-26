#!/usr/bin/env python3
"""Generate the bytesmith showcase site from the skill's own source files.

Stdlib only. The page content is parsed out of checklist.md and
countermeasures.md so the showcase can never drift from the skill.

    python3 site/build.py [--skill-dir DIR] [--out DIR]
"""

import argparse
import html
import os
import pathlib
import re
import sys

# ---------------------------------------------------------------- palette

PAPER = "#fbfaf7"
SURFACE = "#f2efe8"
INK = "#14181d"
RUST = "#b4451f"
MOSS = "#4a5d3a"
GOLD = "#8a6d1f"
RULE = "#d9d3c7"

# The showcase and the repository point at each other; neither link is decorative.
REPO = "https://github.com/Himath-Rajapaksha/bytesmith"
SELF_AUDIT = REPO + "/blob/main/examples/bytesmith-showcase-self-audit.pdf"
REPO_SLAB = "Himath-Rajapaksha/bytesmith"
EDGE_SCENARIOS = 13
CI_CHECKS = 9
# This page's own audit result. Kept as constants so the number published here
# is the number in the shipped report -- if one moves, both must be edited.
SELF_SCORE = "11.3"
SELF_BAND = "Human-crafted"
# Verified against the shipped PDF by test_build.py -- see "claims a page
# count" there. Hardcoding it is a drift risk, so the test reads the PDF.
SELF_PAGES = 12
LICENSE = "Apache-2.0"

BANDS = [
    ("0 – 15", "Human-crafted"),
    ("15 – 35", "Human + AI assists"),
    ("35 – 60", "Hybrid"),
    ("60 – 80", "AI-dominant"),
    ("80 – 100", "Vibecoded"),
]

# ---------------------------------------------------------------- parsing


def parse_checklist(text):
    """Return (points, groups).

    points: [(num, title, weight)] in file order.
    groups: [(letter, name, first, last)]
    """
    points = [
        (int(m.group(1)), m.group(2).strip(), float(m.group(3)))
        for m in re.finditer(
            r"^\*\*(\d+)\. (.+?)\*\* — \*w ([\d.]+)\*", text, re.M
        )
    ]
    groups = [
        (letter, name.strip(), int(span.split("-")[0]), int(span.split("-")[1]))
        for letter, name, span in re.findall(
            r"^## ([A-E])\. (.+?) \((\d+-\d+)\)", text, re.M
        )
    ]
    return points, groups


def parse_countermeasures(text):
    """Return [(section_no, section_title, [(fingerprint, antidote), ...]), ...]."""
    sections = []
    current = None
    for line in text.splitlines():
        m = re.match(r"^## (\d+)\. (.+?)\s*$", line)
        if m:
            current = (m.group(1), m.group(2).strip(), [])
            sections.append(current)
            continue
        if line.startswith("## "):  # e.g. "## Assembling the section"
            current = None
            continue
        if current is None:
            continue
        m = re.match(r"^\|\s*(\d+)\s+([^|]+?)\s*\|\s*(.+?)\s*\|\s*$", line)
        if m:
            current[2].append((m.group(1), m.group(2), m.group(3)))
    return [(no, title, rows) for no, title, rows in sections if rows]


def validate(points, groups, sections):
    """Fail loudly rather than publish a page that drifted from the skill."""
    errors = []
    nums = sorted(n for n, _, _ in points)
    if nums != list(range(1, 37)):
        errors.append(f"expected points 1-36, got {len(nums)} rows: {nums[:5]}...")
    total_w = round(sum(w for _, _, w in points), 2)
    if total_w != 37.5:
        errors.append(f"expected sum of weights 37.5, got {total_w}")
    if len(groups) != 5:
        errors.append(f"expected 5 groups A-E, got {len(groups)}")
    letters = "".join(g[0] for g in groups)
    if letters != "ABCDE":
        errors.append(f"expected groups ABCDE, got {letters}")
    # groups must tile 1-36 with no gap or overlap
    covered = []
    for _, _, first, last in groups:
        covered.extend(range(first, last + 1))
    if sorted(covered) != list(range(1, 37)):
        errors.append("groups do not tile 1-36")
    rows = [r for _, _, rs in sections for r in rs]
    if len(rows) != 36:
        errors.append(f"expected 36 countermeasures, got {len(rows)}")
    if sorted(int(r[0]) for r in rows) != list(range(1, 37)):
        errors.append("countermeasure numbers not contiguous 1-36")
    if len(sections) != 5:
        errors.append(f"expected 5 countermeasure sections, got {len(sections)}")
    if errors:
        for e in errors:
            print(f"VALIDATION FAILED: {e}", file=sys.stderr)
        raise SystemExit(1)
    return total_w


# ---------------------------------------------------------------- template

CSS = f"""
:root {{
  --paper: {PAPER};
  --surface: {SURFACE};
  --ink: {INK};
  --rust: {RUST};
  --moss: {MOSS};
  --gold: {GOLD};
  --rule: {RULE};
  --serif: "Charter", "Bitstream Charter", "Source Serif 4", Georgia, serif;
  --sans: "Lato", system-ui, sans-serif;
  --mono: "Fira Code", ui-monospace, monospace;
  --measure: 62ch;
}}
* {{ box-sizing: border-box; }}
html {{ -webkit-text-size-adjust: 100%; }}
body {{
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: var(--sans);
  font-size: 17px;
  line-height: 1.6;
  font-feature-settings: "kern" 1;
}}
.wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 28px; }}

/* ---- masthead: a printed rule, not a badge strip ---- */
.masthead {{
  border-bottom: 1px solid var(--rule);
  padding: 22px 0;
  display: flex; align-items: baseline; gap: 18px;
}}
.wordmark {{
  font-family: var(--serif);
  font-size: 21px; letter-spacing: -0.01em; margin: 0;
}}
.wordmark .cut {{ color: var(--rust); }}
.masthead nav {{ margin-left: auto; display: flex; gap: 20px; }}
.masthead nav a {{
  color: var(--ink); text-decoration: none;
  font-size: 13.5px; letter-spacing: 0.04em; text-transform: uppercase;
  border-bottom: 1px solid transparent; padding-bottom: 2px;
}}
.masthead nav a:hover {{ border-bottom-color: var(--rust); }}

/* ---- hero: asymmetric 7/5, left-aligned ---- */
.hero {{
  display: grid; grid-template-columns: 7fr 5fr; gap: 56px;
  padding: 76px 0 72px; align-items: start;
}}
.eyebrow {{
  font-family: var(--mono); font-size: 12px; letter-spacing: 0.16em;
  text-transform: uppercase; color: var(--rust); margin: 0 0 22px;
}}
h1 {{
  font-family: var(--serif); font-weight: 700;
  font-size: clamp(38px, 5.2vw, 62px); line-height: 1.04;
  letter-spacing: -0.022em; margin: 0 0 26px; max-width: 15ch;
}}
.lede {{
  font-size: 19.5px; line-height: 1.62; color: #33383f;
  max-width: var(--measure); margin: 0 0 30px;
}}
.lede em {{ font-family: var(--serif); font-style: italic; color: var(--ink); }}
.cta {{
  display: inline-block; background: var(--ink); color: var(--paper);
  padding: 13px 26px; border-radius: 3px; text-decoration: none;
  font-size: 15px; letter-spacing: 0.02em;
  border-bottom: 3px solid var(--rust);
}}
.cta:hover {{ background: #23282f; }}
.cta-note {{
  font-family: var(--mono); font-size: 12.5px; color: #5c626a;
  margin: 16px 0 0; max-width: 46ch; line-height: 1.55;
}}

.artifact {{
  border: 1px solid var(--ink); background: var(--surface);
  padding: 22px 20px 18px; border-radius: 2px;
}}
.artifact h2 {{
  font-family: var(--mono); font-size: 11.5px; letter-spacing: 0.14em;
  text-transform: uppercase; color: #5c626a; margin: 0 0 20px; font-weight: 400;
}}
.ruler {{ display: block; width: 100%; height: auto; }}
.band-key {{ margin: 4px 0 0; padding: 0; list-style: none; }}
.band-key li {{
  display: grid; grid-template-columns: 74px 1fr; gap: 10px;
  font-size: 13px; padding: 7px 0; border-top: 1px solid var(--rule);
}}
.band-key li:first-child {{ border-top: 0; }}
.band-key .rng {{
  font-family: var(--mono); font-size: 11.5px; color: var(--rust);
  padding-top: 1px;
}}
.band-key .lab {{ color: var(--ink); }}

/* ---- sections ---- */
section {{ border-top: 1px solid var(--rule); padding: 60px 0; }}
.sec-no {{
  font-family: var(--mono); font-size: 12px; letter-spacing: 0.14em;
  color: var(--rust); margin: 0 0 12px;
}}
h2 {{
  font-family: var(--serif); font-size: clamp(27px, 3.1vw, 36px);
  letter-spacing: -0.015em; margin: 0 0 20px; line-height: 1.14;
  max-width: 24ch;
}}
.sub {{ color: #3b4149; max-width: var(--measure); margin: 0 0 34px; }}

/* how-it-runs: numbered steps on a rule, not cards */
.steps {{ margin: 0; padding: 0; list-style: none; counter-reset: s; max-width: 74ch; }}
.steps li {{
  counter-increment: s; padding: 22px 0 22px 60px;
  border-top: 1px solid var(--rule); position: relative;
}}
.steps li:last-child {{ border-bottom: 1px solid var(--rule); }}
.steps li::before {{
  content: counter(s, decimal-leading-zero);
  position: absolute; left: 0; top: 24px;
  font-family: var(--mono); font-size: 12.5px; color: var(--rust);
}}
.steps b {{ display: block; font-size: 17px; margin-bottom: 5px; }}
.steps span {{ color: #3b4149; }}
code {{
  font-family: var(--mono); font-size: 13px; background: var(--surface);
  border: 1px solid var(--rule); border-radius: 2px; padding: 1px 5px;
}}

/* checklist: definition rows */
.group-head {{
  display: flex; align-items: baseline; gap: 14px; margin: 40px 0 0;
  padding-bottom: 10px; border-bottom: 2px solid var(--ink);
}}
.group-head .ltr {{
  font-family: var(--serif); font-size: 26px; color: var(--rust);
  line-height: 1;
}}
.group-head h3 {{
  font-family: var(--sans); font-size: 14px; font-weight: 700;
  letter-spacing: 0.08em; text-transform: uppercase; margin: 0;
}}
.group-head .rng {{
  margin-left: auto; font-family: var(--mono); font-size: 11.5px; color: #6a7078;
}}
table {{ width: 100%; border-collapse: collapse; margin-bottom: 8px; }}
th {{
  text-align: left; font-family: var(--mono); font-size: 11px;
  letter-spacing: 0.12em; text-transform: uppercase; color: #6a7078;
  font-weight: 400; padding: 10px 12px 10px 0; border-bottom: 1px solid var(--rule);
}}
td {{
  padding: 9px 12px 9px 0; border-bottom: 1px solid var(--rule);
  vertical-align: top; font-size: 15px;
}}
td.num {{ font-family: var(--mono); font-size: 12.5px; color: var(--rust); width: 2.6em; }}
td.w {{ font-family: var(--mono); font-size: 12.5px; color: #6a7078; width: 3.4em; }}
td.cm {{ color: #3b4149; font-size: 14.5px; }}

/* blueprint sections */
.cm-sec {{ margin-top: 36px; }}
.cm-sec h3 {{
  font-family: var(--serif); font-size: 21px; margin: 0 0 4px;
  letter-spacing: -0.01em;
}}
.cm-sec .hint {{
  font-family: var(--mono); font-size: 11.5px; color: #6a7078;
  margin: 0 0 12px; letter-spacing: 0.06em; text-transform: uppercase;
}}
details {{ border-top: 1px solid var(--rule); }}
details:last-of-type {{ border-bottom: 1px solid var(--rule); }}
summary {{
  cursor: pointer; padding: 13px 0; font-size: 15px;
  display: flex; align-items: baseline; gap: 10px; list-style: none;
}}
summary::-webkit-details-marker {{ display: none; }}
summary::before {{
  content: "+"; font-family: var(--mono); color: var(--rust); width: 1em;
}}
details[open] summary::before {{ content: "\\2212"; }}
summary .fp {{ font-weight: 700; }}
summary .rng {{
  margin-left: auto; font-family: var(--mono); font-size: 11.5px; color: #6a7078;
}}
details .antidote {{
  margin: 0 0 16px 1.9em; color: #3b4149; font-size: 15px; max-width: 70ch;
}}

/* proof / install */
.spec {{
  font-family: var(--mono); font-size: 13px; background: var(--surface);
  border-left: 3px solid var(--moss); padding: 16px 18px; margin: 0 0 28px;
  overflow-x: auto; line-height: 1.7; color: #2b3037;
}}
.spec b {{ color: var(--moss); font-weight: 400; }}
.two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 56px; align-items: start; }}
ol.install {{ padding-left: 1.3em; margin: 0; }}
ol.install li {{ margin-bottom: 11px; }}
ol.install code {{ font-size: 12.5px; }}
.fine {{
  font-size: 13.5px; color: #5c626a; border-top: 1px solid var(--rule);
  padding-top: 18px; margin-top: 30px;
}}

footer {{
  border-top: 1px solid var(--ink); padding: 30px 0 60px;
  display: flex; gap: 20px; align-items: baseline;
  font-size: 13px; color: #5c626a;
}}
footer .wordmark {{ font-size: 17px; color: var(--ink); }}
footer .right {{ margin-left: auto; font-family: var(--mono); font-size: 12px; }}
footer a {{ color: inherit; text-decoration: none; border-bottom: 1px solid var(--rule); }}
footer a:hover {{ border-bottom-color: var(--rust); }}
.masthead nav a[href^="http"] {{ color: var(--moss); }}
p a {{
  color: var(--rust); text-decoration: none;
  border-bottom: 1px solid #d8b6a6; font-weight: 700;
}}
p a:hover {{ border-bottom-color: var(--rust); }}

/* radius by hierarchy, not one soft value everywhere */
.cta, .artifact, details, .spec {{ border-radius: 2px; }}
code {{ border-radius: 2px; }}
table, .steps li, .band-key li {{ border-radius: 0; }}

@media (max-width: 880px) {{
  .hero {{ grid-template-columns: 1fr; gap: 40px; padding: 52px 0 48px; }}
  .two {{ grid-template-columns: 1fr; gap: 36px; }}
  .masthead nav {{ gap: 14px; }}
  .masthead nav a {{ font-size: 12px; }}
  .steps li {{ padding-left: 44px; }}
  h1 {{ font-size: clamp(34px, 8.4vw, 46px); }}
  .band-key li {{ grid-template-columns: 66px 1fr; }}
}}
@media print {{
  .masthead nav {{ display: none; }}
}}
"""


def ruler_svg():
    """The band-ruler: a measure with the five bands in their real colors."""
    stops = []
    edges = [0, 15, 35, 60, 80, 100]
    fills = [MOSS, GOLD, "#c9a227", RUST, "#8c2f16"]
    for i in range(5):
        x = edges[i] * 3.2
        w = (edges[i + 1] - edges[i]) * 3.2
        stops.append(
            f'<rect x="{x}" y="0" width="{w}" height="26" fill="{fills[i]}"></rect>'
        )
    ticks = []
    labels = []
    for i, e in enumerate(edges):
        x = e * 3.2
        ticks.append(f'<line x1="{x}" y1="26" x2="{x}" y2="34" stroke="{INK}" stroke-width="1"></line>')
        anchor = "start" if i == 0 else ("end" if i == len(edges) - 1 else "middle")
        labels.append(
            f'<text x="{x}" y="46" font-family="Fira Code, monospace" font-size="10" '
            f'fill="#5c626a" text-anchor="{anchor}">{e}</text>'
        )
    return (
        '<svg class="ruler" viewBox="0 0 320 52" role="img" '
        'aria-label="AI Usage Score from 0 to 100 divided into five bands">'
        + "".join(stops)
        + "".join(ticks)
        + "".join(labels)
        + "</svg>"
    )


def build(skill_dir, out_dir):
    skill = pathlib.Path(skill_dir)
    points, groups = parse_checklist((skill / "checklist.md").read_text())
    sections = parse_countermeasures((skill / "countermeasures.md").read_text())
    total_w = validate(points, groups, sections)

    cmap = {}
    for _, _, rows in sections:
        for num, fp, anti in rows:
            cmap[int(num)] = (fp, anti)

    e = html.escape
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # ---- hero artifact
    key_rows = "".join(
        f'<li><span class="rng">{e(rng)}</span><span class="lab">{e(lab)}</span></li>'
        for rng, lab in BANDS
    )

    # ---- checklist tables, one per group
    group_blocks = []
    for letter, name, first, last in groups:
        rows = []
        for num, title, weight in points:
            if not (first <= num <= last):
                continue
            anti = cmap.get(num, ("", "—"))[1]
            rows.append(
                f'<tr><td class="num">{num}</td><td>{e(title)}</td>'
                f'<td class="w">w {weight:g}</td><td class="cm">{e(anti)}</td></tr>'
            )
        group_blocks.append(
            f'<div class="group-head"><span class="ltr">{letter}</span>'
            f"<h3>{e(name)}</h3><span class=\"rng\">points {first}–{last}</span></div>"
            "<table><thead><tr><th>#</th><th>Fingerprint</th><th>Weight</th>"
            f"<th>Antidote</th></tr></thead><tbody>{''.join(rows)}</tbody></table>"
        )

    # ---- blueprint, section by section, antidote behind a disclosure
    cm_blocks = []
    for no, title, rows in sections:
        items = []
        for num, fp, anti in rows:
            items.append(
                f"<details><summary><span class=\"fp\">{e(num)} · {e(fp)}</span>"
                f'<span class="rng">point {e(num)}</span></summary>'
                f'<p class="antidote">{e(anti)}</p></details>'
            )
        cm_blocks.append(
            f'<div class="cm-sec"><h3>{e(no)}. {e(title)}</h3>'
            f'<p class="hint">{len(rows)} remedies</p>{"".join(items)}</div>'
        )

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bytesmith — forensic design audit for AI-built pages</title>
<meta name="description" content="Bytesmith scores how much of a webapp looks AI-generated across 36 weighted design fingerprints, cites the source line to change, and prints a print-ready PDF report.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bitstream+Charter:ital,wght@0,400;0,700;1,400&family=Fira+Code:wght@400&family=Lato:wght@400;700&display=swap">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">

<header class="masthead">
  <p class="wordmark">Byte<span class="cut">smith</span></p>
  <nav>
    <a href="#runs">How it runs</a>
    <a href="#points">The 36 points</a>
    <a href="#blueprint">Blueprint</a>
    <a href="#install">Install</a>
    <a href="{REPO}">Source</a>
  </nav>
</header>

<div class="hero">
  <div>
    <p class="eyebrow">Forensic design audit for the web</p>
    <h1>Every AI-built page leaves prints.</h1>
    <p class="lede">Bytesmith reads a codebase the way a forensic reader reads a
    manuscript: 36 weighted fingerprints, from <em>gradient text</em> to
    <em>three equal cards</em>, each one scored for presence and for how strongly
    it implies a machine wrote the page. It cites the <em>line to change</em>,
    not the vibe to change.</p>
    <a class="cta" href="#install">Install the skill</a>
    <p class="cta-note">Runs inside your project. Point it at a repo, a live URL,
    a folder of screenshots, or a written description.</p>
  </div>

  <aside class="artifact">
    <h2>AI Usage Score</h2>
    {ruler_svg()}
    <ul class="band-key">{key_rows}</ul>
  </aside>
</div>

<section id="runs">
  <p class="sec-no">01 — How it runs</p>
  <h2>Source and screen, read together.</h2>
  <p class="sub">A screenshot tells you what a page looks like. The source tells
  you which decision to reverse. Bytesmith takes both, and every scored point
  carries its own location.</p>
  <ol class="steps">
    <li><b>It starts your app.</b><span>Detects the dev command from
    <code>package.json</code>, serves the project, and renders the real
    interface at desktop and mobile widths.</span></li>
    <li><b>It scans the source in parallel.</b><span>Font imports,
    <code>font-family</code> declarations, gradients, color tokens, icon
    libraries, hero and bento components, template copy — each recorded
    as <code>src/app/globals.css:58</code>, never a bare filename.</span></li>
    <li><b>It scores all 36 fingerprints.</b><span>Presence 0–4 against an
    AI-likelihood 1–5, weighted across five groups. Output is
    <code>Σ 291 / 750</code>, banded on a single ruler.</span></li>
    <li><b>It writes the countermeasure blueprint.</b><span>One concrete
    remedy per point at Mild or worse — flat color instead of gradient, a
    non-violet domain hue, radius assigned by hierarchy.</span></li>
    <li><b>It prints the report.</b><span>An A4 PDF, footers on every page
    but the cover, and a roadmap whose action cells name the line to edit.</span></li>
  </ol>
</section>

<section id="points">
  <p class="sec-no">02 — The checklist</p>
  <h2>Thirty-six fingerprints, five groups, no vibes.</h2>
  <p class="sub">Every row on this page is generated from the skill's own
  <code>checklist.md</code> at build time &#8212; {len(points)} points, weights
  summing to {total_w:g}, maximum attainable score 750. There is no JavaScript
  here; the numbers below were checked into the HTML by
  <code>site/build.py</code>, which refuses to emit a page unless the checklist
  still holds {len(points)} points, still sums to {total_w:g}, and its five
  groups still tile 1&#8211;36. The antidote column is the matching row of the
  blueprint below.</p>
  {"".join(group_blocks)}
</section>

<section id="blueprint">
  <p class="sec-no">03 — The blueprint</p>
  <h2>What to do about each one.</h2>
  <p class="sub">The same {sum(len(r) for _, _, r in sections)} rows the skill
  ships, generated from <code>countermeasures.md</code> by the same pass. Expand
  any row for the specific remedy.</p>
  {"".join(cm_blocks)}
</section>

<section id="install">
  <p class="sec-no">04 — Install</p>
  <div class="two">
    <div>
      <h2>Copy the folder. Ask a question.</h2>
      <ol class="install">
        <li><code>git clone {REPO[:-6]}.git</code></li>
        <li><code>cp -r bytesmith ~/.config/opencode/skills/</code></li>
        <li>Open the project you want read.</li>
        <li>Ask: <em>"run a bytesmith audit on this project"</em></li>
      </ol>
      <p class="sub" style="margin-top:26px">It writes
      <code>&lt;project&gt;/bytesmith-report/</code> — the PDF and the HTML
      both, so you can edit the report and re-print it.</p>
    </div>
    <div>
      <h2>What comes out.</h2>
      <div class="spec"><b>score</b>  38.8 / 100 &nbsp;·&nbsp; Hybrid
<b>raw</b>   Σ 291 / 750
<b>mild</b>  29 of 36 points
<b>group A</b> 53.8% contribution share
<b>pages</b> 11 &nbsp;·&nbsp; A4 &nbsp;·&nbsp; footers on pp. 2–11</div>
      <p class="sub" style="margin:0">Those figures are the shipped sample
      report — an AI-generated landing page, rendered and scored by the
      unmodified skill.</p>
      <p class="sub" style="margin:18px 0 0">This page was then held to the
      same instrument. <b>{SELF_SCORE} — {SELF_BAND}</b>, four points at Mild
      or worse, published rather than quietly fixed:
      <a href="{SELF_AUDIT}">read the {SELF_PAGES}-page audit of this page</a>.</p>
    </div>
  </div>
  <p class="fine"><b>How this is kept honest.</b> Every push runs {CI_CHECKS} checks:
  frontmatter and the 15-token report contract, checklist integrity
  (36 points, Σw 37.5, groups tiling 1–36), 36 remedies across 5 sections, a
  PDF that must render A4 with no unreplaced tokens and a footer on every page
  but the cover, a {EDGE_SCENARIOS}-scenario battery covering the band edges and
  the 0 and 100 bounds, and this page's own assertions. It runs on GitHub's
  image, not on one machine — which is how three portability bugs in the
  fixture suite got found and fixed.
  <a href="{REPO}/actions">See the runs.</a></p>
  <p class="fine"><b>Licence.</b> {LICENSE}. Fork it, retune the checklist for
  your own domain, redistribute it commercially. The express patent grant in
  §3 is the reason for Apache over MIT, and the definitions explicitly reach
  documentation and configuration source — which matters when the artefact is
  mostly markdown and CSS. Mark the files you change.</p>
  <p class="fine">Band edges: 0 Human-crafted · 15 Human + AI assists · 35 Hybrid
  · 60 AI-dominant · 80 Vibecoded. Anti-gaming caps keep correlated siblings
  from stacking, and a group holding over half the score is flagged for
  review rather than quietly rebalanced.</p>
</section>

<footer>
  <span class="wordmark">Byte<span class="cut">smith</span></span>
  <span>Forensic design audit · checklist and blueprint are the skill's own files</span>
  <span class="right"><a href="{REPO}">github.com/{REPO_SLAB}</a> &nbsp;·&nbsp; {LICENSE}</span>
</footer>

</div>
</body>
</html>
"""

    (out / "index.html").write_text(page, encoding="utf-8")
    print(f"wrote {out / 'index.html'} ({len(page):,} bytes)")
    print(f"  points={len(points)} sum_w={total_w} groups={len(groups)} "
          f"countermeasures={sum(len(r) for _, _, r in sections)}")


def main():
    ap = argparse.ArgumentParser()
    here = pathlib.Path(__file__).resolve().parent
    # Default to the repo this file lives in, so the generator works from any
    # clone. BYTESMITH_SKILL_DIR (or --skill-dir) points it at an installed
    # copy of the skill instead, e.g. to build the site against what a user
    # actually has installed.
    default_skill = os.environ.get("BYTESMITH_SKILL_DIR") or str(here.parent)
    ap.add_argument("--skill-dir", default=default_skill)
    ap.add_argument("--out", default=str(here / "dist"))
    a = ap.parse_args()
    build(a.skill_dir, a.out)


if __name__ == "__main__":
    main()
