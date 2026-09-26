# Edge-Case Test Battery — Final Report

Deliverable: `fixture/edge.py` · Outputs: `fixture/edge/` (13 HTML + 13 PDF + 13 cover PNGs) · Date: 2026-09-25

## 1. How the battery works

`edge.py` AST-parses `build.py`, strips its side effects (`write_text`/`print`), execs the remainder to
reuse the real `POINTS` + `repl`, then overrides scenario tokens and renders via
`chromium --headless --print-to-pdf` (SKILL §6 command), falling back to weasyprint. Scoring is
independently reimplemented (`evaluate()`) and cross-checked against `build.py` on the baseline.
Feasible band-edge targets are found by a half-point DP solver (`solve()`) over the 36 points'
integer presence×likelihood space. §7 checks: A4 page size, page count, zero unreplaced `{{}}`,
cover-page footer suppression, footer on every body page, cover PNG ink ratio.

## 2. Scenario results

Baseline roundtrip first: `evaluate()` reproduces `build.py` exactly — **score 38.8 · Σ 291/750 ·
Hybrid · mild 29**.

| scenario | target | score | Σ/750 | band | mild | pages | engine | §7 | status |
|---|---|---|---|---|---|---|---|---|---|
| low10 | 10.0 | 10 | 75 | Human-crafted | 4 | 11 | chromium | 6/6 | PASS |
| high85 | 85.0 | 85 | 637.5 | Vibecoded | 33 | 11 | chromium | 6/6 | PASS |
| all4x5 | 100.0 | 100 | 750 | Vibecoded | 36 | 11 | chromium | 6/6 | PASS |
| edge_14_9 | 14.9 | 14.9 | 112 | Human-crafted | 7 | 11 | chromium | 6/6 | PASS |
| edge_15_0 | 15.0 | 15 | 112.5 | Human + AI assists | 7 | 11 | chromium | 6/6 | PASS |
| edge_34_9 | 34.9 | 34.9 | 262 | Human + AI assists | 13 | 11 | chromium | 6/6 | PASS |
| edge_35_0 | 35.0 | 35 | 262.5 | Hybrid | 13 | 11 | chromium | 6/6 | PASS |
| edge_59_9 | 59.9 | 59.9 | 449.5 | Hybrid | 24 | 11 | chromium | 6/6 | PASS |
| edge_60_0 | 60.0 | 60 | 450 | AI-dominant | 24 | 11 | chromium | 6/6 | PASS |
| edge_79_9 | 79.9 | 79.9 | 599.5 | AI-dominant | 31 | 11 | chromium | 6/6 | PASS |
| edge_80_0 | 80.0 | 80 | 600 | Vibecoded | 31 | 11 | chromium | 6/6 | PASS |
| all0 | 0.0 | 0 | 0 | Human-crafted | 2 | 11 | chromium | 6/6 | PASS |
| groupA50plus | 45.0 | 45 | 337.5 | Hybrid | 20 | 11 | chromium | 6/6 | PASS |

**13 scenarios, 0 failures.** `all0` additionally exposed the div-by-zero (§5.1).
`groupA50plus` puts Group A at 175/337.5 = **51.9%** to exercise the SKILL.md:94 >50% review trigger.

Every band edge behaves lower-bound-inclusive: 14.9→Human-crafted / 15→Human+AI assists,
34.9→Human+AI / 35→Hybrid, 59.9→Hybrid / 60→AI-dominant, 79.9→AI-dominant / 80→Vibecoded.

## 3. Band / clamp rule — verbatim from SKILL.md §3

SKILL.md:71-74 (formula):

```
contributionᵢ = weightᵢ × presenceᵢ(0-4) × likelihoodᵢ(0-5)

AI Usage Score = 100 × Σ contributionᵢ / 750
```

SKILL.md:86 (bands):

> **Bands:** 0-15 Human-crafted · 15-35 Human + AI assists · 35-60 Hybrid · 60-80 AI-dominant · 80-100 Vibecoded.

**Clamp rule: there is none — and none is needed.** §3 contains no clamp, cap, or `min(100, …)`
anywhere; the maximum is bounded by construction (Σweights 37.5 × 4 × 5 = 750 → 100.0 exactly),
verified by `all4x5`. `build.py:57` applies only `round(100*total/750, 1)`.

**Band-edge semantics:** the ranges **overlap at exactly 15 / 35 / 60 / 80 with no stated
tie-break** (SKILL.md:86). `build.py:74-75` resolves each overlap lower-bound-inclusive
(`score >= 15 → "Human + AI assists"`, etc.) — correct, but undocumented. Band is computed on the
*rounded* score (build.py:57 → :74); since all totals are multiples of 0.5, reachable scores
quantize to multiples of 1/15 ≈ 0.0667, so the nearest non-edge neighbors of 15/35/60/80 are
14.933…/15.066… — rounding to 0.1 can never move a score across a band edge.

## 4. §6 / §7 verification

- All 13 PDFs rendered by **chromium 153** with the SKILL §6 command; each **11 pages, A4
  (594.96 × 841.92 pt)**; **0 unreplaced `{{}}` tokens**; footer "For Human Eyes Only" present on
  pages 2–11, **absent on cover** (CSS `@page` margin boxes render correctly in chromium).
- Cover PNG check (SKILL §7.4): `cover-edge_80_0-01.png` (80 / VIBECODED / Σ 600/750) and
  `cover-groupA50plus-01.png` (45 / HYBRID / Σ 337.5/750) visually inspected — score, band pill,
  Σ, date, layout all correct.
- §7 automated checks: **6/6 on every scenario** (A4, ≥8 pages, 0 tokens, cover has no footer,
  body pages have footer, cover ink ratio > 0.01).

## 5. Bugs found (file:line)

### 5.1 `build.py:72` — ZeroDivisionError on a legal all-None score — **FIXED**
```python
f'<td class="num">{s:g}</td><td class="num">{s/total*100:.1f}%</td></tr>')
```
§3 explicitly allows zero totals ("Points scored **None** contribute 0 — do not pad", SKILL.md:95).
`total == 0` crashes the group-table loop. Reproduced by `edge.py`'s `repro_build_divzero`
(AST-rewrites POINTS to all-zero presence → `ZeroDivisionError` at build.py:72).
The score itself (build.py:57) is safe — constant denominator 750. `edge.py` guards with
`share = 0.0 if total == 0 else …`.
**Fix applied:** `build.py` now guards `share = (s/total*100 if total else 0.0):.1f`; re-run of the
battery confirms `NO CRASH` and `all0` passes.

### 5.2 `build.py:160` — hardcoded group-share percentage in appendix prose — **FIXED**
```
…Group A carried 54.7% of total, flagged as a review trigger…
```
54.7% = 162.5/297, true **only for the baseline**. Any other score makes the sentence false:
the `groupA50plus` fixture's real figure is 51.9%. The string ships in the published baseline
`report.html:272`. (`edge.py:169,196` computes and formats the share dynamically.)
**Fix applied:** `{{APPENDIX}}` is now an f-string computing `ga_share` dynamically; the flag
text flips at the >50% trigger. Baseline now reads 53.8% (162.5/291).

### 5.3 `SKILL.md:86` — overlapping band endpoints, no tie-break — **FIXED**
"0-15 … 15-35 … 35-60 … 60-80 … 80-100" assigns e.g. 15 to two bands. Resolution
(lower-bound-inclusive, build.py:74-75) exists only in code, not in the spec. Fix: write
`[0,15) [15,35) [35,60) [60,80) [80,100]` explicitly.
**Fix applied:** SKILL.md:86 now states the half-open intervals plus "a score of exactly 15 is
Human + AI assists, not Human-crafted"; battery's 14.9/15.0/34.9/… edges verify it.

### 5.4 `SKILL.md:94` vs `report-template.html` — no slot for the group-review trigger — **WORKAROUND DOCUMENTED**
§3 requires the report to "state … which single design decision … is carrying multiple points",
but the template's 15 tokens (`{{AI_SCORE}} {{APPENDIX}} {{CALC_ROWS}} {{COUNTERMEASURES}}
{{EXEC_SUMMARY}} {{POINT_COUNT_MILD}} {{PROJECT_NAME}} {{RAW_SUM}} {{REPORT_DATE}}
{{ROADMAP_ROWS}} {{ROAST}} {{SCORE_BAND}} {{SCORE_ROWS}} {{TARGET_URL}} {{VERDICT_LINE}}`)
contain no group-share/decision slot. The rule can only be satisfied by freeform `{{APPENDIX}}`
text — which is exactly where bug 5.2 hides.
**Mitigation applied:** SKILL.md:94 now explicitly directs the statement to `{{EXEC_SUMMARY}}`
or `{{APPENDIX}}` "(the template has no dedicated slot for it)"; 5.2's dynamic f-string makes
the freeform text trustworthy. Token contract stays at 15.

### 5.5 `SKILL.md:92-95` — anti-gaming rules unenforced; report claims otherwise — **FIXED (machine-enforced)**
Sibling caps `{1,2,3}` / `{24,25}` / `{19,29}` (SKILL.md:92, checklist.md:15) and "absence points
(32, 33, 36) never exceed Mild" (SKILL.md:93; checklist.md:154 "Absence-only — max Mild") are
prose instructions. `build.py:14-54` scores `POINTS` with zero validation of either rule, yet the
generated `{{EXEC_SUMMARY}}` (build.py:~158-160) asserts "absence points limited to Mild; group
shares reviewed … confirmed to reflect one structural decision" unconditionally. A hand-built
`POINTS` violating the caps still publishes a report claiming compliance. `edge.py`'s fixtures are
constraint-clean, but nothing checks it.
**Fix applied:** `build.py` `validate()` (after `P_LABEL`) enforces Σw=37.5, presence 0-4,
likelihood 0-5, all three sibling caps, and the absence-section rule — exiting with
`ANTI-GAMING VIOLATIONS:…`. Baseline fixture corrected (point 1 presence 3 → 2) to comply;
that is why the baseline moved 39.6 → 38.8.

### Non-bug observations
- SKILL.md:94 says "Group A legitimately tops out at 45% of total **weight**" (17/37.5 = 45.3%) —
  that is weight share, not score share; score share exceeds 50% routinely (baseline 53.8%),
  so the trigger is normal, not exceptional.
- Band is applied to the rounded score (build.py:57→:74); harmless here (see §3), but fragile if
  rounding precision ever changes.

## 6. Verdict

The scoring → banding → render → PDF pipeline is **correct on all 13 edge fixtures** (band edges,
bounds 0/100, all-zero, group trigger), renders deterministically per SKILL §6, and passes §7 6/6
everywhere. All five defects are now fixed: 5.1 div-by-zero guarded (repro no longer crashes),
5.2 group share computed dynamically (53.8% at baseline), 5.3 half-open bands written into
SKILL.md, 5.4 review-trigger statement routed to `{{EXEC_SUMMARY}}`/`{{APPENDIX}}` in SKILL.md,
5.5 anti-gaming rules machine-enforced by `build.py` `validate()`. Baseline moved 39.6 → 38.8
(Σ297 → Σ291) because point 1's presence was corrected 3 → 2 to satisfy the sibling cap;
`edge.py --all` re-run: **13 scenarios, 0 failures** against the new baseline.
