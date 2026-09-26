# Bytesmith — Make It Official

**Status legend:** `[ ]` pending · `[~]` in progress · `[x]` done · `[!]` blocked
**Source:** `/root/.config/opencode/skills/bytesmith/`
**Created:** 2026-09-25

---

## Open decisions

- [x] What does "official" mean here? → **A. Official locally** (polished, versioned, tested skill in `~/.config/opencode/skills/`). **Phase 4 dropped.**
- [x] Repo visibility & host — n/a (decision A)
- [!] License — n/a unless later published (P3.4 attribution still open)
- [x] Repo name — n/a unless later published

---

## Phase 1 — Polish the skill itself

- [x] Read-through of all 5 files for typos, broken phrasing, inconsistent terminology (presence 0–4 vs likelihood 0–5 wording)
- [x] Validate YAML frontmatter parses and `name: bytesmith` / description ≤ 1024 chars (opencode limit)
- [x] Tune `description` trigger words (URL, screenshot, roast, AI-generated, vibecode, forensic audit, PDF report) — this is what makes the skill fire reliably
- [x] Confirm SKILL.md stays lean; all bulky content lives in `checklist.md` / `countermeasures.md` / template / CSS
- [x] Grep for stale rules (old 40% group cap, wrong weights, wrong band edges) — last known clean, re-verify after edits
- [x] Add a short "Inputs required" note: URL vs screenshots vs description (fallback behavior when only screenshots are given)

## Phase 2 — Test for real (beyond the fixture)

- [x] **Live end-to-end run:** (vercel.com → 15pp, 2.3% Human-crafted) point the skill at a real public site (ideally a known AI-generated landing page) and follow SKILL.md verbatim — every command in the doc
- [x] **Edge-band fixtures:** (13 scenarios in `fixture/edge.py`) render a Human-crafted score (~10) and a Vibecoded score (~85) — cover all 5 band labels, not just Hybrid
- [x] **Extreme-data test:** (all0 / all-max, caps + boundaries) all presence 0 (score 0) and all presence 5×max — check caps, rounding, band boundaries (15/35/60/80 exact values)
- [x] **Anti-gaming test:** (caps enforced by `build.py validate()`) correlated siblings ({1,2,3}, {24,25}, {19,29}) all Extreme — confirm the cap actually clamps and the report says so
- [x] **Group-share trigger test:** (groupA50plus 51.9% passes) force Group A > 50% and confirm the review-trigger language appears (fixture already does this — keep it as regression)
- [x] Test the **weasyprint fallback** (A4/11pp/10 footers; fixed `-o` CLI bug) command path from SKILL.md (chromium path is proven; fallback is not)
- [x] Test screenshot-only input (1440+390 captures verified) (no live URL) — does the ingest step degrade gracefully?
- [x] Verify all SKILL.md verification commands run clean on a fresh render: `pdfinfo`, `grep -c '{{'` = 0, footer text present, cover PNG read

## Phase 3 — Package & document

- [x] Add `README.md` (2 min read: what it is, install = copy folder to skills dir, usage = one example prompt, sample output link)
- [x] Ship a **sample report PDF** (`examples/acme-vibecode-audit.pdf`, 11pp, 38.8) in the repo (`examples/acme-vibecode-audit.pdf` — current fixture output qualifies) as proof of output quality
- [x] Document token contract (15/15 template↔SKILL.md match verified): which `{{TOKENS}}` the template expects and where each is filled (already in SKILL.md §6 — verify it matches the template exactly)
- [!] Attribution note: derived from the "VibeCode Auditor" prompt (original author/license, if known)
- [x] `CHANGELOG.md` with 0.1.0 initial release

## Phase 3b — Repo-first input model (approved 2026-09-26)

- [x] SKILL.md repo-first: description / Overview / When to Use / §1 two entry paths (repo primary, URL secondary)
- [x] Evidence rule: visual + `file:line` in repo mode; roadmap action cell cites `file:line`
- [x] Output: final PDF + report.html → `<project>/bytesmith-report/`
- [x] Tests: token contract 15/15, screenshot ingest, repo-mode dry-run on devpad (next dev → 1440/390 renders → anchors layout.tsx:2, globals.css:58)

## Phase 5 — Website (DONE 2026-09-26)

- [x] Design approved by user; plan in `phase5-showcase-plan.md`
- [x] `site/build.py` — stdlib generator parsing checklist.md + countermeasures.md (asserts 36 pts / Σw 37.5 / 5 groups / 36 CM)
- [x] `site/test_build.py` — 60+ checks incl. forbidden-pattern and contrast-adjacent rules; all pass
- [x] `site/vercel.json` — framework null, outputDirectory dist
- [x] Deployed: **https://bytesmith-rust.vercel.app** (Vercel project `bytesmith`)
- [x] Copy describes repo-first execution ("runs inside your project", `package.json`, `src/app/globals.css:58`)
- [x] Fixed during build: dead `rungs` code; undeclared webfonts (Charter/Lato/Fira Code now actually loaded)
- [x] **Self-audit: 11.3 · Human-crafted · Σ 85/750 · 4 Mild+** — acceptance ≤15 PASS
      PDF: `/home/anorak/Works/bytesmith-site-self-audit.pdf` (11pp A4, §7 5/5)
      Open findings: 5 (3 italic serif spans, Moderate), 12 (moss left-strip), 25 (one X-not-Y pivot), 32 (no terms/privacy)

## Phase 4 — Publish — **DROPPED** (decision A; kept for reference only)

- [ ] Init git repo (proposed location: `/home/anorak/Works/bytesmith/`), first commit, tag `v0.1.0`
- [ ] Push to chosen remote
- [ ] CI (optional, cheap): frontmatter parse check + fixture render + token check on every push — reuse `fixture/build.py` as the test
- [ ] Install path for other machines documented: `git clone … && cp -r bytesmith ~/.config/opencode/skills/`
- [ ] Optional: submit to opencode community skills lists / plugin registry if one applies
- [ ] Update this todo: mark Phase outcomes, archive to `docs/` or delete

---

## Definition of done

- [x] All Phase 1–2 items checked
- [x] At least one **live-site** audit PDF produced and eyeballed page-by-page
- [x] README + sample example exist
- [ ] (If B) repo pushed — n/a (decision A), tagged, install instructions verified from a clean clone
- [ ] Skill invoked successfully by opencode in a fresh session (trigger test: "audit this URL with bytesmith")
