# Bytesmith

**A forensic design audit skill for AI-built web UIs.** It scores how much of a webapp,
SaaS, portfolio, or landing page looks AI-generated — a 36-point audit weighted to
750 — then roasts it with quoted evidence, ships a human-craftsmanship countermeasure
blueprint, and prints it all as a PDF.

**Bands:** [0,15) Human-crafted · [15,35) Human + AI assists · [35,60) Hybrid ·
[60,80) AI-dominant · [80,100] Vibecoded.

The showcase page audits its own author with the unmodified skill and scored
**11.3 — Human-crafted**: https://bytesmith-rust.vercel.app

## Install

```bash
git clone https://github.com/Himath-Rajapaksha/bytesmith.git
cp -r bytesmith ~/.config/opencode/skills/     # opencode
# codex / claude-code: copy the same folder into that tool's skills directory
```

Already have a checkout you're developing in? `./install.sh` re-syncs this
directory into your skills dir without re-cloning.

## Usage

Run it **inside the project you want audited** (primary mode):

> "run a bytesmith audit on this project"

The agent starts your dev server, renders the UI, scans the source for fingerprints
(`file:line` anchors for every point), scores all 36 checks, and writes the report to
`<project>/bytesmith-report/`.

Also works on a live site, screenshots, or a written description:

> "audit https://example.com with bytesmith"

Each scored point cites visual evidence plus the source line to change; the roadmap
rows name the exact `file:line` to edit.

## What's in the box

| File | Role |
|---|---|
| `SKILL.md` | the protocol — ingest, scoring, anti-gaming, assembly, verification |
| `checklist.md` | 36 fingerprints, presence 0–4 × likelihood 1–5, Σw = 37.5, max 750 |
| `countermeasures.md` | 36 remedies in the 5 fixed blueprint sections |
| `report-template.html` + `report-styles.css` | the 15-token PDF template |
| `examples/acme-vibecode-audit.pdf` | 11-page sample report, score 38.8 · Hybrid |
| `fixture/build.py` · `fixture/edge.py` | baseline renderer and the 13-scenario edge battery |
| `site/build.py` | generator for the showcase page |

## Sample output

`examples/acme-vibecode-audit.pdf` — 11-page A4 report: cover, exec summary, 36-row
evidence table, group calc, roast, countermeasures, roadmap, raw notes.

## Development

```bash
python3 fixture/build.py            # render the baseline report
python3 fixture/edge.py --all       # 13-scenario battery (band edges, bounds, anti-gaming)
python3 site/test_build.py          # showcase page assertions
./install.sh                        # sync into ~/.config/opencode/skills/
```

Both suites run in CI on every push.

## License

Apache-2.0 — see [LICENSE](LICENSE) and [NOTICE](NOTICE).

You are free to fork it, retune the checklist for your own domain, and redistribute
it commercially. The one ask: keep the Apache-2.0 grant intact, and mark files you
change (§4b).
