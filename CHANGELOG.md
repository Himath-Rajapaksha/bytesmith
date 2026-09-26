# Changelog

## 0.1.0 — 2026-09-26

Initial release, published under Apache-2.0.

- **36-point forensic checklist** (`checklist.md`): Σw = 37.5, max score 750, five
  groups (Visual language 1-16, Component & layout 17-19, Motion & interaction
  20-23, Copy & content 24-31, Trust & polish 32-36), presence 0-4 × likelihood 1-5.
- **Bands:** [0,15) Human-crafted · [15,35) Human + AI assists · [35,60) Hybrid ·
  [60,80) AI-dominant · [80,100] Vibecoded (half-open, lower bound inclusive).
- **Repo-first ingest:** run inside a project — dev server render + source scan with
  `file:line` anchors; report lands in `<project>/bytesmith-report/`. URL mode,
  screenshot-only mode, and description mode retained.
- **Anti-gaming enforcement:** sibling caps {1,2,3}, {24,25}, {19,29}; absence points
  32/33/36 capped at Mild absent a Moderate peer in Group E; group-share >50% is a
  review trigger; machine-checked by `fixture/build.py` `validate()`.
- **PDF pipeline:** 15-token template, chromium print-to-pdf primary, weasyprint
  fallback (positional args — no `-o` since weasyprint 67), §7 four-check verification.
- **Countermeasure blueprint** (`countermeasures.md`): one concrete remedy per point
  ≥ Mild, five fixed sections, no vibes.
- **Tested:** live E2E on vercel.com (2.3%, Human-crafted, 15 pages), 13-scenario edge
  battery (band edges, bounds 0/100, all-zero, group trigger) all green, weasyprint
  fallback, screenshot-only ingest, repo-mode dry-run.
- **Repo-first ingest:** run inside a project — dev server render + source scan with
  `file:line` anchors; report lands in `<project>/bytesmith-report/`. URL mode,
  screenshot-only mode, and description mode retained.
- **Anti-gaming enforcement:** sibling caps {1,2,3}, {24,25}, {19,29}; absence points
  32/33/36 capped at Mild absent a Moderate peer in Group E; group-share >50% is a
  review trigger; machine-checked by `fixture/build.py` `validate()`.
- **PDF pipeline:** 15-token template, chromium print-to-pdf primary, weasyprint
  fallback (positional args — no `-o` since weasyprint 67), §7 four-check verification.
- **Page-count bound:** over 20 pages is a scope failure, not a rounding error — narrow
  the audit unit rather than truncating scored points.
- **Countermeasure blueprint** (`countermeasures.md`): one concrete remedy per point
  ≥ Mild, five fixed sections, no vibes.
- **Tested:** live E2E on vercel.com (2.3%, Human-crafted, 15 pages), 13-scenario edge
  battery (band edges, bounds 0/100, all-zero, group trigger) all green, weasyprint
  fallback, screenshot-only ingest, repo-mode dry-run, showcase self-audit (11.3%).
