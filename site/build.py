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

# Repo root: the cited source files (SKILL.md, checklist.md, README.md, ...)
# live one level above site/.
ROOT = pathlib.Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- palette

PAPER = "#fbfaf7"
SURFACE = "#f2efe8"
INK = "#14181d"
RUST = "#b4451f"
MOSS = "#4a5d3a"
GOLD = "#8a6d1f"
RULE = "#d9d3c7"

# Two derived steps of the palette, kept in report-styles.css byte-for-byte.
# RUST_LIFT is rust lifted for dark grounds: #b4451f on #14181d is 3.24:1,
# which clears the 3:1 large-text floor the 78pt cover numeral needs and
# fails the 4.5:1 floor the 8pt cover eyebrow needs. Lifted, it is 6.76:1.
# RUST_RULE is rust darkened for underlines: the link underline is what
# identifies a link (WCAG 1.4.11), so it has to clear 3:1 against the
# surface it sits on. 4.13:1 on paper, 3.75:1 on surface.
RUST_LIFT = "#e08a5f"
RUST_RULE = "#b4653f"

# Ink value steps. Every one clears 4.5:1 on --paper. TEXT_LABEL is 4.79:1 on
# paper and 4.35:1 on --surface, so it is only ever used for small mono
# labels on paper.
TEXT = "#2b3037"
TEXT_QUIET = "#3b4149"
TEXT_META = "#5c626a"
TEXT_LABEL = "#6a7078"

# The five band fills. One Python list feeds both the :root tokens and the
# inline ruler svg, so the legend swatch and the bar cannot drift apart,
# and the hexes stay legible in the served HTML for anyone hex-dumping it.
BAND_FILLS = ["#4a5d3a", "#8a6d1f", "#c9a227", "#b4451f", "#8c2f16"]

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

# The band edges, straight out of SKILL.md §3: half-open intervals, lower
# bound inclusive, last band closed. A score of exactly 15 is
# "Human + AI assists", not "Human-crafted" -- which is why the edges are
# stations on the ruler rather than a range printed in the legend.
BAND_EDGES = [0, 15, 35, 60, 80, 100]

# One fingerprint resolved end to end, for the "How a point is scored"
# section. Every number below is read from checklist.md and SKILL.md §3,
# and the contribution is computed rather than typed, so the page cannot
# print an arithmetic error. Point 12 is the specimen because it is one of
# the four findings the shipped self-audit raised, and the fix is a single
# declaration in this file -- so the worked example is checkable against
# the diff.
WORKED = {
    "point": 12,
    "name": "Colored Border Cards",
    "w": 1.0,
    "w_tier": "0.5 / 1.0 / 1.5",
    "w_src": (
        "checklist.md &sect;A lists 12 at <b>w 1.0</b> &mdash; the neutral "
        "tier, the tier handcrafted work lands in most often."
    ),
    "presence": 1,
    "presence_label": "Mild",
    "presence_range": "0–4",
    "presence_src": (
        "One instance: a 3px moss left-strip on the output block. "
        "Searched, found once, not structural &mdash; which is the "
        "definition of Mild, and one step below Moderate."
    ),
    "likelihood": 2,
    "likelihood_range": "0–5",
    "likelihood_src": (
        "How strongly does one tinted strip imply a machine? On a page whose "
        "other two hundred rules are neutral hairlines, two. The same strip "
        "on a page of tinted strips would be four."
    ),
}

# The scoring denominators, from SKILL.md §3. Also computed, not typed.
SUM_W = 37.5
MAX_PRESENCE = 4
MAX_LIKELIHOOD = 5
DENOM = SUM_W * MAX_PRESENCE * MAX_LIKELIHOOD  # 750

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


def cite_line(relpath, needle):
    """1-based line number of `needle` in `relpath`. Fails the build if it moved."""
    p = ROOT / relpath
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if needle in line:
            return i
    raise SystemExit(f"{relpath}: cite needle not found: {needle!r}")


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
  --rust-lift: {RUST_LIFT};
  --rust-rule: {RUST_RULE};
  --text: {TEXT};
  --text-quiet: {TEXT_QUIET};
  --text-meta: {TEXT_META};
  --text-label: {TEXT_LABEL};

  --serif: "Charter", "Bitstream Charter", "Source Serif 4", Georgia, serif;
  --sans: "Lato", system-ui, sans-serif;
  --mono: "Fira Code", ui-monospace, monospace;

  /* Two measures. 62ch for prose, 56ch for the two densest texts on the
     page: the antidote column of the 36-point table and the remedy text
     inside a disclosure. Both sit under the 80-character line. */
  --measure: 62ch;
  --measure-dense: 56ch;

  /* Type scale: major third, 1.25, off a 17px base. This is point 4's own
     antidote applied to this page -- "set a type scale with a real ratio
     (1.25 / 1.333) instead of 16/18/20/24". The steps are derived, not
     declared, so no font-size on this page can drift off the scale
     without someone changing --base or --r. --s3 = 33.2px,
     --s6 = 64.9px, --t--1 = 13.6px, --t--2 = 10.9px. */
  --base: 17px;
  --r: 1.25;
  --s1: calc(var(--base) * var(--r));
  --s2: calc(var(--s1) * var(--r));
  --s3: calc(var(--s2) * var(--r));
  --s4: calc(var(--s3) * var(--r));
  --s5: calc(var(--s4) * var(--r));
  --s6: calc(var(--s5) * var(--r));
  --t--2: calc(var(--base) / var(--r) / var(--r));
  --t--1: calc(var(--base) / var(--r));

  /* The five band fills. The same list draws the ruler and the legend. */
  --band-1: {BAND_FILLS[0]};
  --band-2: {BAND_FILLS[1]};
  --band-3: {BAND_FILLS[2]};
  --band-4: {BAND_FILLS[3]};
  --band-5: {BAND_FILLS[4]};
}}
* {{ box-sizing: border-box; }}
html {{ -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }}
body {{
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: var(--sans);
  font-size: var(--base);
  line-height: 1.6;
  font-feature-settings: "kern" 1;
}}
.wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 28px; }}

/* ---- focus. WCAG 2.2 2.4.11 Focus Appearance is AA, and this
   stylesheet previously declared no focus state at all: the one blind
   spot in the tool's own instrument. 2px ink, 2px offset, 17:1 against
   the paper it lands on. ---- */
a:focus-visible, summary:focus-visible {{
  outline: 2px solid var(--ink);
  outline-offset: 2px;
}}
/* ---- skip link: the first stop for a keyboard user, so it must be the
   first thing in the document and it must become visible on focus. ---- */
.skip {{
  position: absolute; left: -9999px; top: 0; z-index: 30;
  background: var(--ink); color: var(--paper);
  font-size: var(--t--1); text-decoration: none;
  padding: 13px 20px; border-bottom: 3px solid var(--rust);
}}
.skip:focus-visible {{ position: fixed; left: 10px; top: 10px; }}
@media (prefers-reduced-motion: reduce) {{
  html {{ scroll-behavior: auto; }}
}}

/* ---- masthead: a printed rule, not a badge strip ---- */
.masthead {{
  border-bottom: 1px solid var(--rule);
  padding: 20px 0 18px;
  display: flex; align-items: baseline; gap: 18px; flex-wrap: wrap;
}}
.wordmark {{
  font-family: var(--serif);
  font-size: var(--s1); letter-spacing: -0.01em; margin: 0;
}}
.wordmark .cut {{ color: var(--rust); }}
.masthead nav {{ margin-left: auto; display: flex; gap: 20px; flex-wrap: wrap; }}
.masthead nav a {{
  color: var(--ink); text-decoration: none; position: relative;
  font-size: var(--t--1); letter-spacing: 0.04em; text-transform: uppercase;
  border-bottom: 1px solid transparent; padding-bottom: 2px;
}}
.masthead nav a:hover {{ border-bottom-color: var(--rust); }}
/* WCAG 2.2 2.5.8 Target Size (Minimum), and 2.5.5 at AAA. The inline
   content box of a link is the font's content area, not its line box, so
   a 13.6px mono link measures 18px tall. The hit area is grown with a
   pseudo-element rather than with padding, which would move the type;
   13px vertically lands every footer and nav link on 44px. The horizontal
   inset is 4px, under the 20px nav gap and the 16px legal gap, so no two
   targets overlap. Inline links inside a sentence are exempt and are
   left alone. */
.masthead nav a::after, footer a::after {{
  content: ""; position: absolute; inset: -13px -4px;
}}

/* ---- hero: asymmetric 7/5, left-aligned ---- */
.hero {{
  display: grid; grid-template-columns: 7fr 5fr; gap: 56px;
  padding: 76px 0 72px; align-items: start;
}}
.eyebrow {{
  font-family: var(--mono); font-size: var(--t--1);
  letter-spacing: 0.16em; text-transform: uppercase;
  color: var(--rust); margin: 0 0 22px;
}}
h1 {{
  font-family: var(--serif); font-weight: 700;
  font-size: clamp(var(--s3), 5.2vw, var(--s6)); line-height: 1.04;
  letter-spacing: -0.022em; margin: 0 0 26px; max-width: 15ch;
  text-wrap: balance;
}}
.lede {{
  font-size: var(--s1); line-height: 1.62; color: var(--text);
  max-width: var(--measure); margin: 0 0 30px; text-wrap: pretty;
}}
/* The page's only italic on purpose. Point 5 is its largest open finding:
   the shipped self-audit counted three italic serif spans in one hero
   paragraph. Two are gone. The remaining one carries the argument, which
   is the cure its own blueprint prescribed. See countermeasures.md §2. */
.lede em {{ font-family: var(--serif); font-style: italic; color: var(--ink); }}
.cta {{
  display: inline-block; background: var(--ink); color: var(--paper);
  padding: 13px 26px; border-radius: 3px; text-decoration: none;
  font-size: var(--t--1); letter-spacing: 0.02em;
  border-bottom: 3px solid var(--rust);
}}
.cta:hover {{ background: #23282f; }}
.cta-note {{
  font-family: var(--mono); font-size: var(--t--1); color: var(--text-meta);
  margin: 16px 0 0; max-width: 46ch; line-height: 1.55;
}}

/* ---- hero artifact: the ruler, drawn as a title block ---- */
.artifact {{
  border: 1px solid var(--ink); background: var(--surface);
  padding: 22px 20px 18px; border-radius: 2px;
}}
.fig {{ margin: 0; }}
/* The ruler prints measured numbers, so the digits must line up. The
   property inherits into the svg <text> nodes. */
.ruler {{ display: block; width: 100%; height: auto; font-variant-numeric: tabular-nums; }}
figcaption {{
  font-family: var(--mono); font-size: var(--t--2);
  letter-spacing: 0.08em; color: var(--text-meta);
  margin: 12px 0 0; padding-top: 9px; border-top: 1px solid var(--rule);
}}
.band-key {{ margin: 16px 0 0; padding: 0; list-style: none; }}
.band-key li {{
  display: grid; grid-template-columns: 68px 1fr; gap: 12px;
  font-size: var(--t--1); padding: 8px 0; border-top: 1px solid var(--rule);
}}
.band-key li:first-child {{ border-top: 0; }}
.band-key .rng {{
  font-family: var(--mono); font-size: var(--t--2); color: var(--rust);
  font-variant-numeric: tabular-nums; padding-top: 3px;
}}
.band-key .lab {{ color: var(--ink); display: flex; align-items: center; gap: 9px; }}
/* Legend key. Hairline ink border so it reads as a drawing symbol rather
   than a dot, and a 0 radius to match the rules it decodes. */
.sw {{ width: 10px; height: 10px; flex: 0 0 10px; border: 1px solid var(--ink); }}
.sw.b1 {{ background: var(--band-1); }}
.sw.b2 {{ background: var(--band-2); }}
.sw.b3 {{ background: var(--band-3); }}
.sw.b4 {{ background: var(--band-4); }}
.sw.b5 {{ background: var(--band-5); }}

/* ---- sections ---- */
section {{ border-top: 1px solid var(--rule); padding: 60px 0; scroll-margin-top: 16px; }}
.sec-no {{
  font-family: var(--mono); font-size: var(--t--1); letter-spacing: 0.14em;
  color: var(--rust); margin: 0 0 12px;
}}
h2 {{
  font-family: var(--serif); font-size: clamp(var(--s2), 3.1vw, var(--s3));
  letter-spacing: -0.015em; margin: 0 0 20px; line-height: 1.14;
  max-width: 24ch; text-wrap: balance;
}}
.sub {{ color: var(--text-quiet); max-width: var(--measure); margin: 0 0 34px; text-wrap: pretty; }}

/* how-it-runs: numbered steps on a rule, not cards */
.steps {{ margin: 0; padding: 0; list-style: none; counter-reset: s; max-width: 74ch; }}
.steps li {{
  counter-increment: s; padding: 22px 0 22px 60px;
  border-top: 1px solid var(--rule); position: relative;
}}
.steps li:last-child {{ border-bottom: 1px solid var(--rule); }}
.steps li::before {{
  content: counter(s, decimal-leading-zero);
  position: absolute; left: 0; top: 25px;
  font-family: var(--mono); font-size: var(--t--1); color: var(--rust);
}}
.steps b {{ display: block; font-size: var(--base); margin-bottom: 5px; }}
.steps span {{ color: var(--text-quiet); }}
code {{
  font-family: var(--mono); font-size: var(--t--1); background: var(--surface);
  border: 1px solid var(--rule); border-radius: 2px; padding: 1px 5px;
}}

/* checklist: definition rows */
.group-head {{
  display: flex; align-items: baseline; gap: 14px; margin: 40px 0 0;
  padding-bottom: 10px; border-bottom: 2px solid var(--ink);
}}
.group-head .ltr {{
  font-family: var(--serif); font-size: var(--s2); color: var(--rust);
  line-height: 1;
}}
.group-head h3 {{
  font-family: var(--sans); font-size: var(--t--1); font-weight: 700;
  letter-spacing: 0.08em; text-transform: uppercase; margin: 0;
}}
.group-head .rng {{
  margin-left: auto; font-family: var(--mono); font-size: var(--t--2);
  color: var(--text-label); font-variant-numeric: tabular-nums;
}}
table {{ width: 100%; border-collapse: collapse; margin-bottom: 8px; }}
th {{
  text-align: left; font-family: var(--mono); font-size: var(--t--2);
  letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-label);
  font-weight: 400; padding: 10px 12px 10px 0; border-bottom: 1px solid var(--rule);
}}
th.w {{ text-align: right; padding-right: 14px; }}
td {{
  padding: 9px 12px 9px 0; border-bottom: 1px solid var(--rule);
  vertical-align: top; font-size: var(--base); text-wrap: pretty;
}}
/* Measured numbers. Tabular figures so the weight column reads as a
   column, and the two hex widths so the index never shifts. */
td.num {{
  font-family: var(--mono); font-size: var(--t--2); color: var(--rust);
  width: 30px; font-variant-numeric: tabular-nums;
}}
td.w {{
  font-family: var(--mono); font-size: var(--t--2); color: var(--text-label);
  width: 44px; text-align: right; font-variant-numeric: tabular-nums;
}}
td.cm {{ color: var(--text-quiet); font-size: var(--t--1); max-width: var(--measure-dense); }}

/* how a point is scored: a section drawing, then the rows it annotates */
.calc {{ max-width: 74ch; }}
.calc-svg {{ display: block; width: 100%; height: auto; }}
.calc-t {{ margin-top: 32px; }}
.calc-t th, .calc-t td {{ padding: 11px 14px 11px 0; }}
.calc-t td.k {{ font-size: var(--t--1); font-weight: 700; color: var(--ink); width: 10em; }}
.calc-t td.v {{
  font-family: var(--mono); font-size: var(--t--1); color: var(--rust);
  width: 8.5em; font-variant-numeric: tabular-nums;
}}
.calc-t td.f {{ font-size: var(--t--1); color: var(--text-quiet); max-width: var(--measure-dense); }}
/* the presence label is prose sitting next to a numeral, not a second
   numeral -- so it steps down a level and changes face */
.calc-t td.v .lbl {{
  font-family: var(--sans); font-size: var(--t--2);
  color: var(--text-quiet); padding-left: 3px;
}}
.calc-t tr.sum td {{ border-top: 2px solid var(--ink); border-bottom: 2px solid var(--ink); }}
.calc-t tr.sum td.k, .calc-t tr.sum td.v {{ font-weight: 700; }}
.calc-t tr.sum td.v {{ color: var(--ink); font-size: var(--s1); }}
.calc-t tr.sum td.f {{ color: var(--text-quiet); }}

/* blueprint sections */
.cm-sec {{ margin-top: 36px; }}
.cm-sec h3 {{
  font-family: var(--serif); font-size: var(--s1); margin: 0 0 4px;
  letter-spacing: -0.01em;
}}
.cm-sec .hint {{
  font-family: var(--mono); font-size: var(--t--2); color: var(--text-label);
  margin: 0 0 12px; letter-spacing: 0.06em; text-transform: uppercase;
}}
details {{ border-top: 1px solid var(--rule); }}
details:last-of-type {{ border-bottom: 1px solid var(--rule); }}
summary {{
  cursor: pointer; padding: 14px 0; font-size: var(--t--1);
  display: flex; align-items: baseline; gap: 10px; list-style: none;
}}
summary::-webkit-details-marker {{ display: none; }}
summary::before {{
  content: "+"; font-family: var(--mono); color: var(--rust); width: 1em;
}}
details[open] summary::before {{ content: "\\2212"; }}
summary .fp {{ font-weight: 700; }}
summary .rng {{
  margin-left: auto; font-family: var(--mono); font-size: var(--t--2);
  color: var(--text-label); font-variant-numeric: tabular-nums;
}}
details .antidote {{
  margin: 0 0 16px 1.9em; color: var(--text-quiet); font-size: var(--t--1);
  max-width: var(--measure-dense); text-wrap: pretty;
}}

/* proof / install */
/* Point 12 remedy, applied. This block used to be defined by a 3px moss
   left-strip -- the coloured left-strip variant, and the entire reason
   the shipped self-audit raised point 12. A container is now held off
   the page by a 1px rule box, a surface fill and a 2px ink top rule:
   the same move the tables already make. The colour role moved out of
   the container and into the text, which is what countermeasures.md
   section 1 asks for. */
.spec {{
  font-family: var(--mono); font-size: var(--t--1); background: var(--surface);
  border: 1px solid var(--rule); border-top: 2px solid var(--ink);
  border-radius: 2px;
  padding: 16px 18px; margin: 0 0 28px;
  overflow-x: auto; line-height: 1.7; color: var(--text);
  font-variant-numeric: tabular-nums; white-space: pre-wrap;
}}
.spec b {{ color: var(--moss); font-weight: 400; }}
.two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 56px; align-items: start; }}
ol.install {{ padding-left: 1.3em; margin: 0; }}
ol.install li {{ margin-bottom: 11px; }}
ol.install code {{ font-size: var(--t--1); }}
.fine {{
  font-size: var(--t--1); color: var(--text-meta); border-top: 1px solid var(--rule);
  padding-top: 18px; margin-top: 30px; max-width: var(--measure);
  text-wrap: pretty;
}}

footer {{
  border-top: 1px solid var(--ink); padding: 30px 0 60px;
  display: flex; gap: 20px; align-items: baseline; flex-wrap: wrap;
  font-size: var(--t--1); color: var(--text-meta);
}}
footer .wordmark {{ font-size: var(--base); color: var(--ink); }}
footer .legal {{ display: flex; gap: 16px; }}
footer .right {{ margin-left: auto; font-family: var(--mono); font-size: var(--t--1); }}
footer a {{
  color: inherit; text-decoration: none; position: relative;
  border-bottom: 1px solid var(--rust-rule);
}}
footer a:hover {{ border-bottom-color: var(--rust); }}
.masthead nav a[href^="http"] {{ color: var(--moss); }}
p a {{
  color: var(--rust); text-decoration: none;
  border-bottom: 1px solid var(--rust-rule); font-weight: 700;
}}
p a:hover {{ border-bottom-color: var(--rust); }}

/* ---- legal pages: /terms and /privacy, generated by this script ---- */
.legal {{ padding: 54px 0 30px; max-width: 74ch; }}
.legal h1 {{
  font-size: clamp(var(--s3), 4vw, var(--s5)); max-width: none; margin: 0 0 10px;
}}
.legal h2 {{
  font-family: var(--sans); font-size: var(--t--1); font-weight: 700;
  letter-spacing: 0.08em; text-transform: uppercase;
  margin: 34px 0 8px; padding-top: 14px; max-width: none;
  border-top: 1px solid var(--rule);
}}
.legal p, .legal li {{
  max-width: var(--measure); color: var(--text-quiet);
  font-size: var(--t--1); margin: 0 0 12px; text-wrap: pretty;
}}
.legal ul {{ padding-left: 1.2em; margin: 0 0 12px; }}
.legal .stamp {{
  font-family: var(--mono); font-size: var(--t--2);
  letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--text-meta); margin: 0 0 8px;
}}
.legal .note {{ max-width: var(--measure); color: var(--text-meta); }}
.legal .back {{
  font-family: var(--mono); font-size: var(--t--1);
  color: var(--text-meta); text-decoration: none; position: relative;
  border-bottom: 1px solid var(--rust-rule);
}}
.legal .back:hover {{ border-bottom-color: var(--rust); }}

/* radius by hierarchy, not one soft value everywhere */
.cta {{ border-radius: 3px; }}
.artifact, details, .spec, code {{ border-radius: 2px; }}
table, .steps li, .band-key li, .sw, .calc-t td {{ border-radius: 0; }}

@media (max-width: 880px) {{
  .hero {{ grid-template-columns: 1fr; gap: 40px; padding: 52px 0 48px; }}
  .two {{ grid-template-columns: 1fr; gap: 36px; }}
  .masthead nav {{ gap: 14px; }}
  .masthead nav a {{ font-size: var(--t--2); }}
  .steps li {{ padding-left: 44px; }}
  h1 {{ font-size: clamp(var(--s3), 8.4vw, var(--s4)); }}
  .band-key li {{ grid-template-columns: 60px 1fr; gap: 10px; }}
  .calc-t td.k {{ width: 7em; }}
  .calc-t td.v {{ width: 7em; }}
}}
/* Four columns do not fit 320px, and a 36-row reference table that scrolls
   sideways fails WCAG 1.4.10. The antidote column is dropped rather than
   made tiny: every row's remedy is one tap away in the blueprint below,
   and the checklist section says so. Nothing is lost, only moved. */
@media (max-width: 560px) {{
  th.cm, td.cm {{ display: none; }}
  /* the two fixed column widths would leave the source column about 75px,
     which is one word per line. Letting them size to their content hands
     the width back to the column that needs it. */
  .calc-t td.k, .calc-t td.v {{ width: auto; }}
  .calc-t th:nth-child(2) {{ width: auto; }}
  td.num {{ width: 24px; }}
  td.w {{ width: 38px; }}
  td {{ padding-right: 8px; }}
  .legal {{ padding-top: 36px; }}
}}
@media print {{
  .masthead nav, .skip {{ display: none; }}
}}
"""


# 320 user units across the ruler, 3.2 per score point.
RULER_U = 3.2
RULER_STRIP_H = 18      # the band bar
RULER_WIT_Y0 = 18       # witness lines fall from the bar to the dimension line
RULER_DIM_Y = 30        # the dimension line itself
RULER_LABEL_Y = 45      # station numbers
RULER_VIEW_H = 52       # the old height; kept in the test as a floor


def ruler_svg():
    """FIG. 1. The band-ruler, drawn as a title block.

    A technical-drawing measure rather than a stacked bar: the five bands
    in their real fills, the four interior boundaries inked so each station
    is a hard edge, witness lines dropping from every station to a
    dimension line with slashed terminators, and the six real band edges
    labelled. The edges are the only numbers on the figure; the legend
    below carries the band names, so nothing is printed twice.
    """
    edges = BAND_EDGES
    n = len(edges)
    bar = []
    for i in range(n - 1):
        x = edges[i] * RULER_U
        w = (edges[i + 1] - edges[i]) * RULER_U
        bar.append(
            f'<rect x="{x:g}" y="0" width="{w:g}" height="{RULER_STRIP_H}" '
            f'fill="{BAND_FILLS[i]}"></rect>'
        )
    # Interior boundaries: a 1px ink line on each, because adjacent band
    # fills differ by only 1.47-2.28:1 and read as a hue step, not an edge.
    bounds = "".join(
        f'<line x1="{e * RULER_U:g}" y1="0" x2="{e * RULER_U:g}" '
        f'y2="{RULER_STRIP_H}" stroke="{INK}" stroke-width="1"></line>'
        for e in edges[1:-1]
    )
    # Witness lines, one per station, from the bar down to the dimension line.
    wit = "".join(
        f'<line class="wit" x1="{e * RULER_U:g}" y1="{RULER_WIT_Y0}" '
        f'x2="{e * RULER_U:g}" y2="{RULER_DIM_Y}" stroke="{INK}" '
        'stroke-width="1"></line>'
        for e in edges
    )
    # Interior station ticks crossing the dimension line, plus two slashed
    # terminators at the ends. Slashes rather than arrowheads: at this scale
    # a slash is the ISO convention and stays legible.
    ticks = "".join(
        f'<line x1="{e * RULER_U:g}" y1="{RULER_DIM_Y - 3}" '
        f'x2="{e * RULER_U:g}" y2="{RULER_DIM_Y + 3}" stroke="{INK}" '
        'stroke-width="1"></line>'
        for e in edges[1:-1]
    )
    x0, x1 = edges[0] * RULER_U, edges[-1] * RULER_U
    terms = (
        f'<line class="term" x1="{x0:g}" y1="{RULER_DIM_Y + 4}" '
        f'x2="{x0 + 5:g}" y2="{RULER_DIM_Y - 4}" stroke="{INK}" '
        'stroke-width="1.5"></line>'
        f'<line class="term" x1="{x1:g}" y1="{RULER_DIM_Y + 4}" '
        f'x2="{x1 - 5:g}" y2="{RULER_DIM_Y - 4}" stroke="{INK}" '
        'stroke-width="1.5"></line>'
    )
    labels = []
    for i, e in enumerate(edges):
        x = e * RULER_U
        anchor = "start" if i == 0 else ("end" if i == n - 1 else "middle")
        labels.append(
            f'<text x="{x:g}" y="{RULER_LABEL_Y}" font-family="Fira Code, monospace" '
            f'font-size="10" fill="{TEXT_META}" text-anchor="{anchor}">{e}</text>'
        )
    aria = (
        "AI Usage Score scale from 0 to 100 on a dimension line, band edges at "
        "0, 15, 35, 60 and 80. Five bands: 0 to 15 Human-crafted, 15 to 35 Human "
        "plus AI assists, 35 to 60 Hybrid, 60 to 80 AI-dominant, 80 to 100 "
        "Vibecoded."
    )
    return (
        f'<svg class="ruler" viewBox="0 0 320 {RULER_VIEW_H}" role="img" '
        f'aria-label="{aria}">'
        + "".join(bar)
        + bounds
        + wit
        + f'<line class="dim" x1="{x0:g}" y1="{RULER_DIM_Y}" x2="{x1:g}" '
        f'y2="{RULER_DIM_Y}" stroke="{INK}" stroke-width="1.5"></line>'
        + ticks
        + terms
        + "".join(labels)
        + "</svg>"
    )


# FIG. 2 geometry. 320 wide, 172 tall. The upper half is a schematic chain
# of the three inputs, the lower half is the one thing on the page that is
# drawn to scale: this point's contribution against the 750 capacity.
#
# The contribution is computed from the formula in SKILL.md §3, not copied
# out of the shipped self-audit. That report's own contribution column does
# not reconcile with the formula it cites -- its four findings carry ratios
# of 0.20, 0.20, 0.089 and 0.80 against w x presence x likelihood, so no one
# normalisation explains it. The skill's own law is "no score without
# evidence", and the evidence here is the formula, so the formula wins.
# Reproducing the figure instead would be the page committing the crime it
# prosecutes: a number the stated method does not produce.
SC_U = 320                     # viewBox width
BAR_X, BAR_W = 8.0, 304.0      # the 750-capacity bar
PX_PER_UNIT = BAR_W / DENOM    # 0.4053 px per unit of contribution
DETAIL_MAG = 50                # magnification of the DETAIL callout
SLIVER = WORKED["w"] * WORKED["presence"] * WORKED["likelihood"]
SLIVER_PX = SLIVER * PX_PER_UNIT          # 0.81 px at 1:1 - sub-pixel
DETAIL_PX = SLIVER_PX * DETAIL_MAG        # 40.5 px at 50:1


def _t(x, y, s, size=8, fill=None, anchor="start", ls=None, weight=None):
    """One svg <text>. Dimension text is set in the mono face at 7.5-11px."""
    a = [f'x="{x:g}"', f'y="{y:g}"',
         'font-family="Fira Code, monospace"', f'font-size="{size}"',
         f'fill="{fill or TEXT_QUIET}"', f'text-anchor="{anchor}"']
    if ls:
        a.append(f'letter-spacing="{ls}"')
    if weight:
        a.append(f'font-weight="{weight}"')
    return f'<text {" ".join(a)}>{s}</text>'


def scoring_svg():
    """FIG. 2. One fingerprint, resolved end to end, as a section drawing.

    Reads left to right, top to bottom, the way an engineering section
    annotates a part: three dimensioned inputs, a common datum they all
    hang from, a leader into the resolved contribution, then the same
    contribution drawn twice more -- once to scale against the 750
    denominator, where it is 0.81 of 304 drawing units and so cannot be
    drawn at all, and once as a DETAIL callout at 50:1 behind a break
    line, which is the drafting convention for a feature too small to
    draw at scale.

    The schematic half is tagged NOT TO SCALE because it is not. The
    capacity half is to scale, and the DETAIL is labelled with its
    magnification so the exaggeration is declared, not hidden. "Scale"
    here means scale within the figure: a viewBox has no absolute size,
    so the sub-pixel claim is stated in drawn units and as a share.
    """
    w = WORKED["w"]
    p = WORKED["presence"]
    l = WORKED["likelihood"]
    contribution = w * p * l
    share = contribution / DENOM * 100
    g = []

    # ---- schematic half
    g.append(_t(8, 9.5, "SCHEMATIC \u2014 NOT TO SCALE", size=7.5, fill=TEXT_META,
                ls="0.06em"))
    # The cell labels carry the term and its permitted range. The weight
    # tier list is not repeated here -- it is in the row below, and a
    # drawing that prints a number twice is a drawing nobody trusts.
    cells = [
        (8.0, 74.0, "weight w", f"{w:.1f}"),
        (108.0, 92.0, f"presence {WORKED['presence_range']}",
         f"{p}  {WORKED['presence_label']}"),
        (226.0, 86.0, f"likelihood {WORKED['likelihood_range']}", f"{l}"),
    ]
    for x, cw, label, value in cells:
        g.append(f'<rect x="{x:g}" y="12" width="{cw:g}" height="24" '
                 f'fill="{SURFACE}" stroke="{INK}" stroke-width="1"></rect>')
        g.append(_t(x + 7, 21.5, label, size=8, fill=INK))
        g.append(_t(x + 7, 32.5, value, size=11, fill=INK, weight="700"))
    # operators sit in the gaps, where they belong
    g.append(_t(100, 28.5, "\u00d7", size=11, fill=INK, anchor="middle"))
    g.append(_t(219, 28.5, "\u00d7", size=11, fill=INK, anchor="middle"))

    # witness lines from each cell to a common datum rule
    for x, cw, _, _ in cells:
        cx = x + cw / 2
        g.append(f'<line class="wit" x1="{cx:g}" y1="36" x2="{cx:g}" y2="40" '
                 f'stroke="{INK}" stroke-width="1"></line>')
    g.append(f'<line class="datum" x1="{BAR_X:g}" y1="40" x2="{BAR_X + BAR_W:g}" '
             f'y2="40" stroke="{INK}" stroke-width="1"></line>')
    # leader with an arrowhead, dropping the datum into the product block
    g.append(f'<line class="lead" x1="160" y1="40" x2="160" y2="45" '
             f'stroke="{RUST}" stroke-width="1"></line>')
    g.append(f'<path class="lead" d="M 156.6 45 L 160 49.4 L 163.4 45 Z" '
             f'fill="{RUST}"></path>')

    # ---- the resolved contribution, as a filled datum
    g.append(f'<rect x="{BAR_X:g}" y="49" width="{BAR_W:g}" height="30" '
             f'fill="{INK}"></rect>')
    g.append(_t(BAR_X + 10, 61, "CONTRIBUTION", size=8, fill=PAPER, ls="0.14em"))
    g.append(_t(BAR_X + 10, 73,
                f"{w:.1f} \u00d7 {p} \u00d7 {l} = {contribution:.3f}",
                size=12, fill=PAPER))

    # ---- true scale: this contribution against the 750 denominator
    g.append(f'<rect x="{BAR_X:g}" y="90" width="{BAR_W:g}" height="8" '
             f'fill="{SURFACE}" stroke="{INK}" stroke-width="1"></rect>')
    # The true position, 0.81 of 304 drawn units in from the datum. A 1px
    # witness is the most this drawing can honestly show at that scale.
    sx = BAR_X + SLIVER_PX
    g.append(f'<line class="wit" x1="{sx:.2f}" y1="88" x2="{sx:.2f}" y2="100" '
             f'stroke="{RUST}" stroke-width="1"></line>')
    dy = 108
    g.append(f'<line class="dim" x1="{BAR_X:g}" y1="{dy}" '
             f'x2="{BAR_X + BAR_W:g}" y2="{dy}" stroke="{INK}" '
             'stroke-width="1.5"></line>')
    g.append(f'<line class="term" x1="{BAR_X:g}" y1="{dy + 4}" '
             f'x2="{BAR_X + 5:g}" y2="{dy - 4}" stroke="{INK}" '
             'stroke-width="1.5"></line>'
             f'<line class="term" x1="{BAR_X + BAR_W:g}" y1="{dy + 4}" '
             f'x2="{BAR_X + BAR_W - 5:g}" y2="{dy - 4}" stroke="{INK}" '
             'stroke-width="1.5"></line>')
    g.append(_t(BAR_X, 120, "0", size=8.5, fill=TEXT_META))
    g.append(_t(BAR_X + BAR_W, 120, f"{DENOM:g}", size=8.5, fill=TEXT_META,
                anchor="end"))
    g.append(_t(BAR_X, 131,
                f"{DENOM:g} = {SUM_W:g} \u03a3w \u00d7 {MAX_PRESENCE}"
                f" \u00d7 {MAX_LIKELIHOOD}",
                size=8, fill=TEXT_META))

    # ---- DETAIL callout, reached by a break line
    dx = 120.0
    g.append(f'<polyline class="break" fill="none" stroke="{RUST}" '
             f'stroke-width="1" points="'
             f'{sx:.2f},140 {BAR_X + 30:.0f},140 {BAR_X + 42:.0f},146 '
             f'{BAR_X + 54:.0f},140 {BAR_X + 70:.0f},140 '
             f'{BAR_X + 82:.0f},146 {BAR_X + 94:.0f},140 {dx - 6:g},140'
             f'"></polyline>')
    g.append(f'<rect x="{dx:g}" y="136" width="{DETAIL_PX:.1f}" height="8" '
             f'fill="{RUST}" stroke="{INK}" stroke-width="1"></rect>')
    ddy = 152
    g.append(f'<line class="dim" x1="{dx:g}" y1="{ddy}" '
             f'x2="{dx + DETAIL_PX:.1f}" y2="{ddy}" stroke="{INK}" '
             'stroke-width="1.5"></line>')
    g.append(f'<line class="term" x1="{dx:g}" y1="{ddy + 3}" '
             f'x2="{dx + 4:g}" y2="{ddy - 3}" stroke="{INK}" '
             'stroke-width="1.5"></line>'
             f'<line class="term" x1="{dx + DETAIL_PX:.1f}" y1="{ddy + 3}" '
             f'x2="{dx + DETAIL_PX - 4:.1f}" y2="{ddy - 3}" stroke="{INK}" '
             'stroke-width="1.5"></line>')
    g.append(_t(dx, 164, "0", size=8.5, fill=TEXT_META))
    g.append(_t(dx + DETAIL_PX, 164, f"{contribution:.3f}", size=8.5,
                fill=TEXT_META, anchor="end"))
    # Right-hand annotation, anchored to the right margin the way the other
    # right-hand dimension text is. It balances the left-aligned stations and
    # says the share rather than restating the fraction, which the detail's
    # own dimension line and the table row already carry. It sits on the same
    # rows as the detail bar so the association is spatial, not implied --
    # set next to the derivation on the left it reads as one run of text.
    g.append(_t(312, 140, f"DETAIL {DETAIL_MAG}:1", size=7.5, fill=TEXT_META,
                anchor="end", ls="0.06em"))
    g.append(_t(312, 151, f"{share:.3f}% OF CAPACITY", size=7.5, fill=TEXT_META,
                anchor="end", ls="0.06em"))

    aria = (
        f"Annotated section drawing resolving fingerprint {WORKED['point']}, "
        f"{WORKED['name']}. Weight {w:.1f}, presence {p} "
        f"({WORKED['presence_label']}), likelihood {l}, giving a "
        f"contribution of {contribution:.3f} against a maximum of {DENOM:g}. "
        f"At the scale of the lower bar that contribution is {SLIVER_PX:.2f} of "
        f"{BAR_W:g} drawn units, or {share:.3f} per cent of the bar's width, "
        f"which is too narrow to draw; it is therefore repeated as a detail at "
        f"{DETAIL_MAG} to one, with its magnification stated on the drawing."
    )
    return (
        f'<svg class="calc-svg" viewBox="0 0 {SC_U} 175" role="img" '
        f'aria-label="{aria}">' + "".join(g) + "</svg>"
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

    # Computed, not typed: the worked example's contribution and its share of
    # the denominator. A change to WORKED or to the math in SKILL.md §3 moves
    # every number on the page at once, so the page cannot print a stale one.
    contribution = (WORKED["w"] * WORKED["presence"] * WORKED["likelihood"])
    if round(total_w * MAX_PRESENCE * MAX_LIKELIHOOD, 1) != DENOM:
        raise SystemExit(
            f"VALIDATION FAILED: checklist sums to {total_w:g}, so the "
            f"denominator is {total_w * MAX_PRESENCE * MAX_LIKELIHOOD:g}, "
            f"not {DENOM:g}"
        )

    # ---- hero artifact. The legend decodes each fill to a name; the ruler
    # above it carries the stations, so the two never print the same number.
    key_rows = "".join(
        f'<li><span class="rng">{e(rng)}</span>'
        f'<span class="lab"><span class="sw b{i + 1}"></span>{e(lab)}</span></li>'
        for i, (rng, lab) in enumerate(BANDS)
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
            '<table><thead><tr><th>#</th><th>Fingerprint</th>'
            '<th class="w">Weight</th>'
            f'<th class="cm">Antidote</th></tr></thead><tbody>{"".join(rows)}</tbody></table>'
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
<a class="skip" href="#main">Skip to content</a>
<div class="wrap">

<header class="masthead">
  <p class="wordmark">Byte<span class="cut">smith</span></p>
  <nav>
    <a href="#runs">How it runs</a>
    <a href="#points">The 36 points</a>
    <a href="#scored">Scoring</a>
    <a href="#blueprint">Blueprint</a>
    <a href="#install">Install</a>
    <a href="{REPO}">Source</a>
  </nav>
</header>

<main id="main">
<div class="hero">
  <div>
    <p class="eyebrow">Forensic design audit for the web</p>
    <h1>Every AI-built page leaves prints.</h1>
    <p class="lede">Bytesmith reads a codebase the way a forensic reader reads a
    manuscript. Thirty-six weighted fingerprints, from gradient text to three
    equal cards, each one scored for presence and for how strongly it implies a
    machine wrote the page. Every point names the <em>line to change</em>.</p>
    <a class="cta" href="#install">Install the skill</a>
    <p class="cta-note">Runs inside your project. Point it at a repo, a live URL,
    a folder of screenshots, or a written description.</p>
  </div>

  <aside class="artifact">
    <figure class="fig">
    {ruler_svg()}
    <figcaption>FIG. 1 &mdash; AI USAGE SCORE, FIVE BANDS, &Sigma;w {total_w:g}</figcaption>
    </figure>
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
    AI-likelihood 0–5, weighted across five groups. Output is
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
  blueprint below, and on a narrow screen the column is dropped rather than
  shrunk &#8212; every row still opens the same remedy one tap away.</p>
  {"".join(group_blocks)}
</section>

<section id="scored">
  <p class="sec-no">03 &mdash; How a point is scored</p>
  <h2>One fingerprint, taken apart.</h2>
  <p class="sub">A score is three numbers multiplied. The weight comes from the
  checklist. Presence and likelihood come from reading one page against the
  thirty-five others it is sitting next to. Here is point
  {WORKED["point"]} &mdash; {e(WORKED["name"])} &mdash; run through the whole
  calculation, because it is a finding against this very page and you can check
  the fix in the diff. The same arithmetic runs on all {len(points)}.</p>

  <figure class="fig calc">
    {scoring_svg()}
    <figcaption>FIG. 2 &mdash; POINT {WORKED["point"]} RESOLVED. {WORKED["w"]:.1f} w
    &times; {WORKED["presence"]} PRESENCE &times; {WORKED["likelihood"]}
    LIKELIHOOD = {contribution:.3f} OF {DENOM:g}. THE UPPER HALF IS SCHEMATIC; THE
    LOWER HALF IS TO SCALE, WHICH IS WHY THE CONTRIBUTION APPEARS TWICE.</figcaption>
  </figure>

  <table class="calc-t">
    <thead><tr><th>Term</th><th>Value</th><th>Where it comes from</th></tr></thead>
    <tbody>
      <tr><td class="k">weight <code>w</code></td><td class="v">{WORKED["w"]:.1f}</td>
        <td class="f">{WORKED["w_src"]}</td></tr>
      <tr><td class="k">presence</td>
        <td class="v">{WORKED["presence"]}<span class="lbl">{WORKED["presence_label"]}</span></td>
        <td class="f">{WORKED["presence_src"]}</td></tr>
      <tr><td class="k">likelihood</td><td class="v">{WORKED["likelihood"]}</td>
        <td class="f">{WORKED["likelihood_src"]}</td></tr>
      <tr class="sum"><td class="k">contribution</td>
        <td class="v">{contribution:.3f}</td>
        <td class="f">{WORKED["w"]:.1f} &times; {WORKED["presence"]} &times;
        {WORKED["likelihood"]} = {contribution:.3f}, which is
        {contribution / DENOM * 100:.3f}% of the {DENOM:g} denominator. A point at
        presence 4 with likelihood 5 and weight 1.5 would be
        1.5 &times; 4 &times; 5 = 30.000, or 4.0 points of score. The range this
        single point can occupy is
        {WORKED["w"]:.1f} &times; 0 &times; 0 = 0.000 to
        {WORKED["w"]:.1f} &times; 4 &times; 5 = {WORKED["w"] * 4 * 5:.3f}.</td></tr>
    </tbody>
  </table>

  <p class="sub" style="margin-top:26px">Two of those three numbers are the hard
  part, and the checklist says so out loud: presence is applied literally, from a
  five-step anchor table, while likelihood is judged &ldquo;given what else is on
  the page&rdquo;. That is the whole reason a score is evidence rather than a
  number someone liked. The denominator is not negotiable &#8212; {DENOM:g} is
  &Sigma;w {SUM_W:g} multiplied by a maximum presence of {MAX_PRESENCE} and a
  maximum likelihood of {MAX_LIKELIHOOD}, so it stays put while the checklist
  changes underneath it, and two pages with the same proportions cannot drift
  onto different scales. The worked figure above is computed from that formula
  every time the page is built, not typed in. If a report ever prints a
  different number for point {WORKED["point"]}, the report is wrong and the
  formula is what settles it.</p>
</section>

<section id="blueprint">
  <p class="sec-no">04 &mdash; The blueprint</p>
  <h2>What to do about each one.</h2>
  <p class="sub">The same {sum(len(r) for _, _, r in sections)} rows the skill
  ships, generated from <code>countermeasures.md</code> by the same pass. Expand
  any row for the specific remedy.</p>
  {"".join(cm_blocks)}
</section>

<section id="install">
  <p class="sec-no">05 &mdash; Install</p>
  <div class="two">
    <div>
      <h2>Copy the folder. Ask a question.</h2>
      <ol class="install">
        <li><code>git clone {REPO[:-6]}.git</code></li>
        <li><code>cp -r bytesmith ~/.config/opencode/skills/</code></li>
        <li>Open the project you want read.</li>
        <li>Ask: <code>run a bytesmith audit on this project</code></li>
      </ol>
      <p class="sub" style="margin-top:26px">It writes
      <code>&lt;project&gt;/bytesmith-report/</code> &mdash; the PDF and the HTML
      both, so you can edit the report and re-print it. Nothing is uploaded: the
      skill&rsquo;s own Python opens no sockets, and given a URL the operator&rsquo;s
      browser fetches it from the operator&rsquo;s own machine.</p>
    </div>
    <div>
      <h2>What comes out.</h2>
      <div class="spec"><b>score</b>   38.8 / 100 &nbsp;·&nbsp; Hybrid
<b>raw</b>     &Sigma; 291 / 750
<b>mild</b>    29 of 36 points
<b>group A</b> 53.8% contribution share
<b>pages</b>   11 &nbsp;·&nbsp; A4 &nbsp;·&nbsp; footers on pp. 2&ndash;11</div>
      <p class="sub" style="margin:0">Those figures are the shipped sample
      report &mdash; an AI-generated landing page, rendered and scored by the
      unmodified skill.</p>
      <p class="sub" style="margin:18px 0 0">This page was then held to the
      same instrument. <b>{SELF_SCORE} &mdash; {SELF_BAND}</b>, four points at Mild
      or worse, published rather than quietly fixed, and then all four fixed in
      this build rather than in the number:
      <a href="{SELF_AUDIT}">read the {SELF_PAGES}-page audit of this page</a>.</p>
    </div>
  </div>
  <p class="fine"><b>The four findings are closed.</b> The report&rsquo;s roadmap
  priced them at &minus;4.0, &minus;2.0, &minus;2.0 and &minus;1.3, which puts
  the page at 2.0. All four are done in source: the two decorative italic spans
  are gone, the moss left-strip is gone, the rhetorical pivot is now a flat claim,
  and the terms and privacy pages exist and are dated. The score on this page is
  still the {SELF_SCORE} that was published, because that is what the shipped
  report says; a re-audit has not been run, so a new number would be a guess.</p>
  <p class="fine"><b>No testimonials here.</b> Point 27 asks for quotes that can
  be verified &mdash; full name, role, company, something to link. This project
  has one changelog entry and nobody on record who has agreed to be quoted, so
  the page carries an empty state rather than a quote row. Manufacturing
  consensus is the exact failure the tool is built to catch, and it is not a
  failure worth committing to a landing page.</p>
  <p class="fine"><b>How this is kept honest.</b> Every push runs {CI_CHECKS} checks:
  frontmatter and the 15-token report contract, checklist integrity
  (36 points, &Sigma;w 37.5, groups tiling 1&ndash;36), 36 remedies across 5 sections, a
  PDF that must render A4 with no unreplaced tokens and a footer on every page
  but the cover, a {EDGE_SCENARIOS}-scenario battery covering the band edges and
  the 0 and 100 bounds, and this page&rsquo;s own assertions. It runs on GitHub&rsquo;s
  image, not on one machine &mdash; which is how three portability bugs in the
  fixture suite got found and fixed.
  <a href="{REPO}/actions">See the runs.</a></p>
  <p class="fine"><b>Licence.</b> {LICENSE}. Fork it, retune the checklist for
  your own domain, redistribute it commercially. The express patent grant in
  &sect;3 is the reason for Apache over MIT, and the definitions explicitly reach
  documentation and configuration source &mdash; which matters when the artefact is
  mostly markdown and CSS. Mark the files you change.</p>
  <p class="fine">Band edges: 0 Human-crafted &middot; 15 Human + AI assists &middot; 35 Hybrid
  &middot; 60 AI-dominant &middot; 80 Vibecoded. Intervals are half-open, so a
  score of exactly 15 is Human + AI assists. Anti-gaming caps keep correlated
  siblings from stacking, and a group holding over half the score is flagged for
  review rather than quietly rebalanced.</p>
</section>
</main>

<footer>
  <span class="wordmark">Byte<span class="cut">smith</span></span>
  <span>Forensic design audit &middot; checklist and blueprint are the skill&rsquo;s own files</span>
  <span class="legal"><a href="/terms">Terms</a><a href="/privacy">Privacy</a></span>
  <span class="right"><a href="{REPO}">github.com/{REPO_SLAB}</a> &nbsp;&middot;&nbsp; {LICENSE}</span>
</footer>

</div>
</body>
</html>
"""

    (out / "index.html").write_text(page, encoding="utf-8")
    written = [out / "index.html"]

    # ---- /terms and /privacy. Point 32 of the checklist is scored on these
    # existing, dated and linked. They were missing, which cost the page
    # 0.800 of its 11.3 -- the largest single contribution of the four open
    # findings. They ship from the same generator, in the same design
    # system, because a legal stub reads worse than an honest page and
    # neither of those is a page worth linking to.
    for slug, title, desc, stamp, body in legal_pages():
        doc = legal_page(slug, title, desc, stamp, body)
        (out / f"{slug}.html").write_text(doc, encoding="utf-8")
        written.append(out / f"{slug}.html")

    for path in written:
        print(f"wrote {path} ({path.stat().st_size:,} bytes)")
    print(f"  points={len(points)} sum_w={total_w} groups={len(groups)} "
          f"countermeasures={sum(len(r) for _, _, r in sections)}")


# ------------------------------------------------------------ legal pages

LEGAL_DATE = "2026-09-26"

TERMS_BODY = [
    ("h2", "The licence"),
    ("p", f"Bytesmith is released under the {LICENSE} licence. The full text "
     "ships in the repository as LICENSE, and the attribution notice ships as "
     "NOTICE. You may use it, fork it, retune the checklist for your own "
     "domain, and redistribute it commercially, including inside a closed "
     "source product, subject to &sect;4 of the licence: mark the files you "
     "change."),
    ("p", "The express patent grant in &sect;3 is the reason this is Apache "
     "rather than MIT. It is not decoration &mdash; the definitions in &sect;0 "
     "explicitly reach documentation and configuration source, which is most "
     "of what this project is. A permissive licence that did not cover the "
     "artefact would be a licence that did not cover the thing it was "
     "written for."),

    ("h2", "What the output is"),
    ("p", "An audit is an argument with citations, not a certification. Every "
     "scored point carries evidence: a hex value, a quoted line of copy, or a "
     "repo-relative file and line. That evidence is the product. A score on "
     "its own is a number, and a number without sources cannot be argued with."),
    ("p", "Scores are reproducible only against the checklist version you ran. "
     "A different checklist, or a different reviewer reading the same page "
     "honestly, can produce a different number. The remedy is not to re-roll "
     "until the score improves; it is to change the page, or to argue with "
     "the specific citation &mdash; which is what the report is built to let "
     "you do."),

    ("h2", "No warranty"),
    ("p", "Provided AS IS, without warranty of any kind, as &sect;7 of the "
     "licence states. The skill will read a codebase and form an opinion "
     "about it. Some of those opinions will be wrong, and a mistaken finding "
     "can send you rewriting a page that was fine. Read the evidence, not "
     "just the verdict, and decide for yourself what to change."),

    ("h2", "Attribution"),
    ("p", "If you redistribute the skill, keep the NOTICE file. If you publish "
     "a report it generated, the report already names itself: the footer on "
     "every page but the cover is generated by the skill and says so."),
]

PRIVACY_BODY = [
    ("h2", "What this page does"),
    ("p", "Nothing. This is a static HTML file with one stylesheet inline. No "
     "analytics, no cookies, no local storage, no session, no fingerprinting, "
     "no error reporting, and no JavaScript at all &mdash; which is checkable "
     "in about four seconds: view source and search for the word script. It "
     "comes back empty."),
    ("p", "Your browser makes one third-party request: to the two Google Fonts "
     "origins named in this page&rsquo;s head, for the three typefaces. Like "
     "every web request, that hands those origins your IP address and user "
     "agent. If you would rather not, block fonts.googleapis.com and the page "
     "falls back to the local serif and sans already named in each stack. "
     "Nothing about the page breaks; it stops looking quite as specific."),
    ("p", "That is the entire inventory. Every other link on this page is a "
     "plain hyperlink to a public repository, a public report, or a section "
     "of this page."),

    ("h2", "What the skill does"),
    ("p", "The skill runs on your machine, inside your project. It reads your "
     "source files, starts your own dev server, renders your own interface, "
     "and writes a folder called bytesmith-report/ next to your project. The "
     "skill&rsquo;s own code opens no network sockets and sends no telemetry: "
     "it is markdown and Python standard library, and you can read all of it."),
    ("p", "If you point it at a URL instead of a project, the fetch is made by "
     "your own browser, from your own machine, to the host you named. "
     "Whatever that host logs is between you and that host, not between you "
     "and this project."),

    ("h2", "What it never does"),
    ("ul", "No cookies are set by this project, on this page or in the report "
     "it generates."),
    ("ul", "No third-party script is loaded. The only external request is the "
     "font stylesheet above."),
    ("ul", "Nothing is uploaded, and no score, source file or page is retained "
     "anywhere but on your disk."),
    ("p", "If this project ever gains any of those, this page changes before "
     "the change ships. A privacy page that has drifted from the product is "
     "worse than no privacy page, which is a sentence worth taking "
     "seriously from a tool that scores pages on exactly this kind of "
     "emptiness."),

    ("h2", "Contact"),
    ("p", f"Questions or corrections belong in the repository's issue tracker, "
     f"at the project page. Corrections that turn out to be wrong are welcome "
     f"and will be made."),

    ("h2", "Dated"),
    ("p", f"This page was last reviewed on {LEGAL_DATE}. It is short because "
     "the product is small, not because a lawyer was not consulted."),
]


def legal_pages():
    """(slug, title, meta description, stamp, body blocks) for each legal page."""
    return [
        ("terms", "Terms",
         "The licence Bytesmith ships under, what its output is and is not, "
         "and the absence of warranty.",
         f"Last reviewed {LEGAL_DATE}", TERMS_BODY),
        ("privacy", "Privacy",
         "What this page and the bytesmith skill collect, which is close to "
         "nothing, stated precisely.",
         f"Last reviewed {LEGAL_DATE}", PRIVACY_BODY),
    ]


def legal_page(slug, title, desc, stamp, body):
    """One legal page, same design system as the index, no separate stylesheet."""
    blocks = []
    for kind, text in body:
        if kind == "h2":
            blocks.append(f"<h2>{text}</h2>")
        elif kind == "ul":
            blocks.append(f"<ul><li>{text}</li></ul>")
        else:
            blocks.append(f"<p>{text}</p>")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} &mdash; Bytesmith</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bitstream+Charter:ital,wght@0,400;0,700;1,400&family=Fira+Code:wght@400&family=Lato:wght@400;700&display=swap">
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="wrap">

<header class="masthead">
  <p class="wordmark">Byte<span class="cut">smith</span></p>
  <nav><a href="/">Bytesmith</a><a href="/terms">Terms</a><a href="/privacy">Privacy</a></nav>
</header>

<main id="main" class="legal">
  <p class="sec-no">{title}</p>
  <h1>{title}</h1>
  <p class="stamp">{stamp}</p>
  {"".join(blocks)}
  <p class="note" style="margin-top:38px"><a class="back" href="/">Back to the
  showcase</a> &nbsp;&middot;&nbsp; <a class="back" href="{REPO}">source</a>
  &nbsp;&middot;&nbsp; {LICENSE}</p>
</main>

</div>
</body>
</html>
"""



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
