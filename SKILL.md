---
name: bytesmith
description: Use when running inside a webapp, SaaS, portfolio, or landing-page project source repo — or given a URL, screenshot set, or site description — and asked to detect AI-generated vibecode design fingerprints, score an AI Usage Score from 0 to 100, run a forensic audit (36-point design audit or roast), draft a human-craftsmanship countermeasure blueprint, or produce a print-ready PDF report.
---

# Bytesmith

## Overview

Forensic audit of a project's source code and rendered interface that scores how much of it looks AI-generated, roasts it with quoted evidence, and ships a print-ready PDF.

Three rules that override everything else:

1. **No score without evidence.** Every point gets a hex value, a quoted line of copy, or an exact location. "Feels generic" is not evidence. In repo mode, cite the repo-relative `file:line` alongside the visual evidence (see §1).
2. **The report must not commit the crimes it prosecutes.** No purple, no Inter/Geist, no gradients, no glass, no sparkle icons, no emoji, no neon.
3. **The percentage is rhetoric; the evidence table is the product.** A score with no citations is a guess wearing a tuxedo.

## When to Use This Skill

- Input is a **project repo** (primary — the skill runs inside the project: source scan + rendered UI), a **URL**, a **set of screenshots**, or a **written description** of a webapp / SaaS / portfolio / landing page.
- The ask contains any of: *vibe audit*, *AI-generated look*, *design fingerprint*, *AI Usage Score*, *design roast*, *human-made vs AI*, *forensic design report*, *PDF audit*.
- Also for the inverse: an original design brief asking to **avoid** AI fingerprints — read `countermeasures.md` and use it as a pre-flight checklist.

Not for: accessibility audits (use `accessibility`), performance (use `performance-profiling`), copy editing for AI tells in prose (use `stop-slop`), or security reviews.

## Files in This Skill

| File | Read when |
|---|---|
| `checklist.md` | Scoring. The 36 points: detection method, presence anchors, weight tier. |
| `countermeasures.md` | Building the Human-Made Countermeasure Blueprint. |
| `report-template.html` | Assembling the PDF. Copy it — never author HTML from scratch. |
| `report-styles.css` | Ships with the template. Never edit per-run. |

## 1. Ingest & Map

Survey **every** section before scoring anything: nav, hero, logo cloud, features, how-it-works, pricing, testimonials, team, FAQ, footer, legal pages, and mobile at ~390px.

**Repo mode (primary).** When the skill runs inside the project:

1. Detect the stack and dev command from `package.json` scripts (`npm run dev` / `pnpm dev` / `bun dev`), start it in the background, and render `http://localhost:<port>` with the chromium commands below (substitute the local URL). Probe `/terms`, `/privacy`, favicon, title against localhost too.
2. Run a **source scan in parallel**: locate each fingerprint in code — font imports and `font-family` declarations, gradients, color tokens, icon libraries, hero/bento/marquee components, animation libraries, template copy — and record `file:line` anchors in the notes file. Every scored point cites its visual evidence **plus** the `file:line` where the fingerprint lives in source; if a point has no locatable source (pure composition or copy judgment), say so in the evidence.
4. Anchors are **repo-relative paths from the project root**, never bare basenames: `src/app/globals.css:58`, not `globals.css:58`. Shared components get the import path that reaches them (`src/components/tool-shell.tsx:15`). A basename is not actionable once a project has two files of the same name, and the roadmap reader has to open the file cold.
3. Dev server won't start or render → fall back to source-only evidence and mark rendered-only checks (contrast, motion, layout) as gaps in `{{APPENDIX}}`.

**URL mode (secondary):** fetch + render the live site:

```bash
W=/tmp/opencode/bytesmith/<slug>; mkdir -p $W
# Copy + structure: fetch first, it is cheaper than rendering
# Visuals: full-viewport captures (raise height for long pages)
chromium --headless --disable-gpu --no-sandbox --hide-scrollbars \
  --window-size=1440,9000 --screenshot=$W/full.png <URL>
chromium --headless --disable-gpu --no-sandbox --hide-scrollbars \
  --window-size=390,7000 --screenshot=$W/mobile.png <URL>
```

Prefer the `playwright` MCP server when screenshots must be scrolled, interacted with, or stitched — `full_page` screenshots beat a single tall viewport.

Probe separately: `/terms`, `/privacy`, favicon, `<title>`, meta description, og:image. Dead or 404 responses are **evidence for point 35**, not a blocker — note it and continue with what rendered.

Record findings into a working notes file as you go. Appendix evidence comes from this, not from memory.

**Inputs required:** at minimum one visual source — the project's rendered UI (repo mode), a URL to render, a screenshot set (full-page captures at ~1440px and ~390px preferred), or a rendered page description. Copy text may come from source, fetch, OCR, or the description itself. If none of the four exists, say so and stop; do not audit from memory.

**Screenshot-only fallback:** with images and no URL, map screenshots to sections instead of URL probes. Score only what the images show; record `/terms` / `/privacy` and link checks as "not evaluable — no URL"; list every missing source as a gap in `{{APPENDIX}}` rather than inventing evidence.

## 2. Analysis Protocol

Execute in this order. Do not skip ahead.

1. **Ingest & Map** — section inventory + layout, type, color, motion, imagery, copy tone.
2. **Point-by-Point Scoring** — all 36, from `checklist.md`. Each gets **Presence** (None / Mild / Moderate / Heavy / Extreme → 0-4), **Evidence** (specific), **AI Likelihood** (0-5), **Weight** (0.5 / 1.0 / 1.5).
3. **Weighted AI Usage Score** — the math in §3. Publish the raw sum beside the percentage.
4. **The Roast** — §4.
5. **Countermeasure Blueprint** — §5. Every point with presence ≥ Mild gets an alternative.
6. **Executive Summary + Roadmap** — verdict in ≤120 words, then a prioritized remediation table (impact vs effort).

## 3. Scoring Math

```
contributionᵢ = weightᵢ × presenceᵢ(0-4) × likelihoodᵢ(0-5)

AI Usage Score = 100 × Σ contributionᵢ / 750
```

750 = Σweights(37.5) × 4 × 5. Report **one decimal max** and always print `Σ = N / 750` next to it.

**Weight tiers** (`checklist.md` is authoritative; the list below is a mirror — verify it sums to 37.5 before scoring, and do not re-assign mid-audit):

- **1.5 — strong signal.** Rare in handcrafted work: 1, 2, 3, 4, 10, 13, 18, 19, 22, 24, 25, 27, 36.
- **1.0 — neutral.** 5, 6, 7, 9, 11, 12, 17, 26, 28, 30, 31, 34, 35.
- **0.5 — weak / common in human work.** 8, 14, 15, 16, 20, 21, 23, 29, 32, 33.

**Bands** (lower bound inclusive, upper exclusive; last band closed): **[0,15)** Human-crafted · **[15,35)** Human + AI assists · **[35,60)** Hybrid · **[60,80)** AI-dominant · **[80,100]** Vibecoded. A score of exactly 15 is Human + AI assists, not Human-crafted.

**Anti-gaming rules — apply before publishing:**

| Rule | Why |
|---|---|
| Correlated siblings cap each other. If one of {1,2,3} is Heavy, the others max at Moderate. Same for {24,25} and {19,29}. | One design decision must not be scored three times. |
| Absence points (32, 33, 36) never exceed **Mild** unless another point in the same section is ≥ Moderate. | A hobby project fails these without being AI-made. |
| Any group whose **contribution share > 50% of the total** is a *review trigger*, not an error: re-check that its points are not scoring one decision repeatedly, then state in `{{EXEC_SUMMARY}}` or `{{APPENDIX}}` (the template has no dedicated slot for it) which single design decision (if any) carries multiple points. Groups: A Visual language 1-16, B Component & layout 17-19, C Motion & interaction 20-23, D Copy & content 24-31, E Trust & polish 32-36. | Prevents one pattern from silently standing in for five. Do not rebalance scores to dodge the flag: Group A carries 45.3% of total *weight*, so a >50% *contribution* share is normal — the flag is a prompt to re-check, never a defect to score away. |
| Points scored **None** contribute 0 — do not pad with negative evidence. | A site that avoided a trope earns that, and the score should show it. |

## 4. Roast Guidelines

Voice: **authoritative senior designer, dry wit, merciless, never juvenile.**

- Roast **patterns and decisions**, never people, companies' staff, or protected traits.
- Every jab cites a point number and its evidence. "It's giving template" without a citation is deleted.
- Name the *AI smell*: the moment the reader realises nobody made a choice here.
- Minimum one paragraph on the most egregious pattern and one on the total absence of soul.
- Ship 400-700 words as `<p>` paragraphs injected into `{{ROAST}}` — the template already renders the "The Roast" heading; do not add your own (a literal `##` inside HTML would not render anyway). The first paragraph must open with a letter or digit: the CSS drop-cap hangs on `::first-letter`. Narrative, not bullets.

Forbidden: slurs, body-shaming, threats, "just hire a designer", fake laughter, filler praise before the punch.

## 5. Countermeasure Blueprint

For **every** point with presence ≥ Mild, one concrete, executable alternative — never "be more unique". Organize into five fixed sections (read `countermeasures.md` for the catalog):

1. **Visual System** 2. **Typography & Voice** 3. **Interaction & Motion** 4. **Content & Proof** 5. **Structure & Polish**

Each entry: `Point # → diagnosis → specific direction (naming real typefaces, real layout devices, real assets, real copy structures)`.

## 6. PDF Assembly

```bash
W=/tmp/opencode/bytesmith/<slug>
# Repo mode: deliverable lands inside the audited project (committable/shareable)
OUT=<project>/bytesmith-report/bytesmith-<score>-audit.pdf
# URL mode: outside the audited site
OUT=/home/anorak/Works/<slug>-vibecode-audit.pdf
mkdir -p $(dirname $OUT)
cp <skill>/report-template.html <skill>/report-styles.css $W/
# inject data into report-template.html (see below), then:
cd $W && chromium --headless --disable-gpu --no-sandbox \
  --print-to-pdf="$OUT" --no-pdf-header-footer report.html 2>/dev/null
cp $W/report.html $(dirname $OUT)/   # keep the HTML next to the PDF
```

Injection: replace `{{PLACEHOLDER}}` tokens with `python3` (`str.replace` on a dict), never `sed` — the payload contains quotes, newlines, and HTML.

| Token | Fills |
|---|---|
| `{{PROJECT_NAME}}` `{{TARGET_URL}}` `{{REPORT_DATE}}` | Cover |
| `{{AI_SCORE}}` `{{SCORE_BAND}}` `{{VERDICT_LINE}}` | Cover + exec summary |
| `{{RAW_SUM}}` `{{POINT_COUNT_MILD}}` | `{{RAW_SUM}}` = bare weighted sum (e.g. `297` — the template appends `/ 750` at four sites; never include the denominator yourself) · `{{POINT_COUNT_MILD}}` = count of points ≥ Mild |
| `{{EXEC_SUMMARY}}` | ≤120-word verdict |
| `{{SCORE_ROWS}}` | 36 `<tr>` — #, name, presence, evidence, likelihood, weight, contribution |
| `{{CALC_ROWS}}` | 5 group rows: Σw / Σcontribution / share — the total row and band are already in the template |
| `{{ROAST}}` | 400-700 word narrative |
| `{{COUNTERMEASURES}}` | 5 category blocks |
| `{{ROADMAP_ROWS}}` | 5 `<td>` cells in template order: priority · effort · action · points affected · est. score delta — in repo mode the action cell carries the repo-relative `file:line` to edit (`src/app/globals.css:58`, never a bare basename) |
| `{{APPENDIX}}` | Raw notes, per-page observations, gaps |

`weasyprint report.html "$OUT"` (positional args — weasyprint ≥67 has no `-o` flag) is the fallback if Chromium ever fails **or if §7 check 3 finds 0 footers** (Chromium has historically dropped `@page` margin boxes; weasyprint has better margin-box compliance, weaker grid/flex).

## 7. Verification

Run all four; a failed check means do not deliver:

```bash
pdfinfo "$OUT" | grep -E 'Pages|Page size'     # A4; page count must be 20 or fewer (see below)
grep -c '{{' $W/report.html                     # must be 0 — leftover tokens before render
pdftotext "$OUT" - | grep -c '{{'               # must be 0 — no unreplaced tokens in the PDF
pdftotext "$OUT" - | grep -F 'For Human Eyes Only'   # footer on every page except the cover; if 0, Chromium dropped margin boxes → re-render with weasyprint (§6)
pdftoppm -png -r 60 -f 1 -l 1 "$OUT" $W/cover && ls $W/cover-*.png   # cover renders
```

Then read the file `ls` printed (`cover-1.png` under 10 pages; pdftoppm zero-pads to page-number width, so `cover-01.png` at 10+ pages): score legible, no clipped text, no pure-white-on-white. Read one image at a time and verify its content matches the filename.

**Over 20 pages is a failure, not a rounding error.** Length is a scope symptom, not a formatting one — a long report means the audit unit was too big (25 tool pages, a whole docs site) or the evidence strings are running to paragraphs. Fix the scope, not the CSS:

- **State a bounded audit unit up front** and audit all of it — `{{PROJECT_NAME}}` on the cover plus one line in `{{EXEC_SUMMARY}}`. "DevPad, home page + `/tools/json-formatter`" beats an implied whole-site sweep that quietly covers 1 page in 25.
- **Never infer coverage you did not render.** If 24 of 25 tool pages share a code path, say so in `{{APPENDIX}}` and score the shared path once — do not restate the same point 25 times.
- **If it still runs long, ship it anyway and flag it:** one line in `{{EXEC_SUMMARY}}` naming the page count and the reason. An honest 24-page report beats a quietly truncated one — never cut a scored point to hit a number.

## Common Mistakes

- **Authoring a fresh HTML/CSS report each run.** Broken page breaks, missing footers, unpadded tables. Copy the template.
- **Committing the crime.** Purple, Inter, gradients, emoji, sparkle icons, glass in the report itself.
- **Binary scoring.** Presence is a 5-step scale. "It has Inter" ≠ "Inter is the entire type system".
- **Double-counting** correlated points (gradients/purple/rainbow; buzzwords/formulaic copy).
- **Inventing evidence** for a section that did not load. Write "not reachable — paywall/login" instead.
- **Score without the raw sum.** One decimal plus `Σ/750` or it is theater.
- **Countermeasures that are vibes.** "Add personality" is not a countermeasure; "replace Instrument Serif pull-quotes with a 1970s newspaper slab (e.g. sentinel-style) used only on pull-quotes" is.
