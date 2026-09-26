#!/usr/bin/env python3
"""Edge-case battery for the bytesmith scoring/report pipeline. Usage: python3 edge.py [--html-only] [--scenario NAME]."""
import ast, datetime, os, pathlib, re, subprocess, sys, traceback

# Resolve against this file so the battery runs from any clone. The skill
# override lets CI (or a user) point at an installed copy instead.
REPO = pathlib.Path(__file__).resolve().parent.parent
FIX = REPO / "fixture"
SKILL = pathlib.Path(os.environ.get("BYTESMITH_SKILL_DIR", REPO))
EDGE = FIX / "edge"
TEMPLATE = (SKILL / "report-template.html").read_text()
CSS = (SKILL / "report-styles.css").read_text()
P_LABEL = {0: "None", 1: "Mild", 2: "Moderate", 3: "Heavy", 4: "Extreme"}


def strip_side_effects(tree):
    kept = []
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            f = node.value.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
            if name in ("write_text", "print"):
                continue
        kept.append(node)
    tree.body = kept
    return tree


def load_build_ns():
    tree = strip_side_effects(ast.parse((FIX / "build.py").read_text(), "build.py"))
    # build.py resolves its repo from __file__, so the exec namespace has to
    # look like a module rather than a bare dict.
    ns = {"__name__": "build_ns", "__file__": str(FIX / "build.py")}
    exec(compile(tree, "build.py", "exec"), ns)
    return ns


def band_of(score):
    if score >= 80:
        return "Vibecoded"
    if score >= 60:
        return "AI-dominant"
    if score >= 35:
        return "Hybrid"
    if score >= 15:
        return "Human + AI assists"
    return "Human-crafted"


def evaluate(points):
    rows = []
    total = 0.0
    mild = 0
    for n, name, p, ev, l, w in points:
        c = w * p * l
        total += c
        if p >= 1:
            mild += 1
        rows.append(
            f'<tr><td class="num">{n}</td><td>{name}</td>'
            f'<td><span class="pill p{p}">{P_LABEL[p]}</span></td>'
            f'<td>{ev}</td><td class="num">{l}</td><td class="num">{w:g}</td>'
            f'<td class="num">{c:g}</td></tr>')
    total = round(total, 1)
    score = round(100 * total / 750, 1)
    groups = [
        ("Group A — Visual language (1-16)", lambda n: n <= 16, "A"),
        ("Group B — Component & layout (17-19)", lambda n: 17 <= n <= 19, "B"),
        ("Group C — Motion & interaction (20-23)", lambda n: 20 <= n <= 23, "C"),
        ("Group D — Copy & content (24-31)", lambda n: 24 <= n <= 31, "D"),
        ("Group E — Trust & polish (32-36)", lambda n: n >= 32, "E"),
    ]
    calc = []
    gsum = {}
    for label, fn, letter in groups:
        s = round(sum(w * p * l for n, _, p, _, l, w in points if fn(n)), 1)
        wsum = sum(w for n, _, _, _, _, w in points if fn(n))
        share = 0.0 if total == 0 else s / total * 100
        gsum[letter] = (s, share)
        calc.append(f'<tr><td>{label}</td><td class="num">{wsum:g}</td>'
                    f'<td class="num">{s:g}</td><td class="num">{share:.1f}%</td></tr>')
    return {"points": points, "rows": rows, "total": total, "score": score,
            "band": band_of(score), "mild": mild, "calc": calc, "groups": gsum}


def solve(points, target_halves):
    back = [{0: None}]
    for n, _, _, _, _, w in points:
        w2 = int(round(w * 2))
        cur = {}
        for s in back[-1]:
            for p in range(5):
                for l in range(6):
                    ns_ = s + w2 * p * l
                    if ns_ not in cur:
                        cur[ns_] = (s, p, l)
        back.append(cur)
    if target_halves not in back[-1]:
        return None
    out = {}
    s = target_halves
    for i in range(len(points), 0, -1):
        s, p, l = back[i][s]
        out[points[i - 1][0]] = (p, l)
    return out


def synth_ev(p, l, w):
    if p == 0:
        return f"Synthetic fixture — scored None (0 × likelihood {l}); contribution 0."
    return f"Synthetic fixture — presence {P_LABEL[p]} ({p}) × likelihood {l} (w {w:g})."


def build_scenarios(base):
    scen = []

    def add(name, mapping, escore, eband, extra=None):
        pts = []
        for n, pname, _, _, _, w in base:
            p, l = mapping.get(n, (0, 0))
            pts.append((n, pname, p, synth_ev(p, l, w), l, w))
        scen.append({"name": name, "points": pts, "escore": escore,
                     "eband": eband, "extra": extra or (lambda e: []),
                     "target_halves": sum(int(round(w * 2)) * p * l for _, _, p, _, l, w in pts)})

    def add_dp(name, target_halves, escore, eband, extra=None):
        m = solve(base, target_halves)
        if m is None:
            raise SystemExit(f"DP infeasible for {name} at {target_halves} halves")
        add(name, m, escore, eband, extra)

    add_dp("low10", 150, 10.0, "Human-crafted")
    add_dp("high85", 1275, 85.0, "Vibecoded")
    add("all4x5", {n: (4, 5) for n, *_ in base}, 100.0, "Vibecoded",
        extra=lambda e: [("mild == 36", e["mild"] == 36, f'mild={e["mild"]}'),
                         ("sum == 750", e["total"] == 750.0, f'sum={e["total"]}')])
    for name, halves, escore, eband in [
        ("edge_14_9", 224, 14.9, "Human-crafted"),
        ("edge_15_0", 225, 15.0, "Human + AI assists"),
        ("edge_34_9", 524, 34.9, "Human + AI assists"),
        ("edge_35_0", 525, 35.0, "Hybrid"),
        ("edge_59_9", 899, 59.9, "Hybrid"),
        ("edge_60_0", 900, 60.0, "AI-dominant"),
        ("edge_79_9", 1199, 79.9, "AI-dominant"),
        ("edge_80_0", 1200, 80.0, "Vibecoded"),
    ]:
        add_dp(name, halves, escore, eband)
    all0 = {n: (0, 1) for n, *_ in base}
    all0[7] = (1, 0)
    all0[8] = (1, 0)
    add("all0", all0, 0.0, "Human-crafted",
        extra=lambda e: [("mild == 2", e["mild"] == 2, f'mild={e["mild"]}')])

    A = [pt for pt in base if pt[0] <= 16]
    rest = [pt for pt in base if pt[0] > 16]
    mapping = None
    for a_h in range(350, 337, -1):
        ma, mr = solve(A, a_h), solve(rest, 675 - a_h)
        if ma is not None and mr is not None:
            mapping = {**ma, **mr}
            break
    if mapping is None:
        raise SystemExit("groupA50plus: no feasible split")
    add("groupA50plus", mapping, 45.0, "Hybrid",
        extra=lambda e: [("Group A share > 50%", e["groups"]["A"][1] > 50,
                          f'A={e["groups"]["A"][1]:.1f}%')])
    return scen


def make_html(name, ev, ns):
    repl = dict(ns["repl"])
    score, total, band, mild = ev["score"], ev["total"], ev["band"], ev["mild"]
    today = datetime.date.today().isoformat()
    shares = ", ".join(f"{L} {s:.1f}%" for L, (s, s2) in
                       ((L, (v[0], v[1])) for L, v in ev["groups"].items()))
    trigger = next((f"Group {L} at {p:.1f}%" for L, (s, p) in ev["groups"].items() if p > 50),
                   "none")
    repl.update({
        "{{PROJECT_NAME}}": f"Edge — {name}",
        "{{TARGET_URL}}": f"https://edge.example/{name}",
        "{{REPORT_DATE}}": today,
        "{{AI_SCORE}}": f"{score:g}",
        "{{SCORE_BAND}}": band,
        "{{VERDICT_LINE}}": f"Synthetic edge fixture pinned to {score:g}% — {band}. Not a real audit.",
        "{{RAW_SUM}}": f"{total:g}",
        "{{POINT_COUNT_MILD}}": f"{mild} / 36",
        "{{EXEC_SUMMARY}}": (
            "<p>Edge fixture <strong>" + f"{score:g}%" + "</strong> — " + band +
            ", on a weighted sum of " + f"{total:g}" + " of 750, with " + f"{mild}" +
            " of 36 points at Mild or above. Scenario <em>" + name +
            "</em> pins the score to this exact value to exercise the §3 band table.</p>"
            "<p>Synthetic per-row evidence only; roast, countermeasures, and roadmap prose "
            "are held constant from the baseline report so layout stays comparable.</p>"),
        "{{SCORE_ROWS}}": "\n".join(ev["rows"]),
        "{{CALC_ROWS}}": "\n".join(ev["calc"]),
        "{{APPENDIX}}": (
            "<h3>Method</h3>\n"
            f"<p>Synthetic edge-case fixture generated by <code>edge.py</code> (scenario <em>{name}</em>). "
            f"All 36 points were solved to an exact target sum (Σ = {total:g} / 750) before any total was "
            "computed; evidence strings are per-row synthetic markers, not a real fetch. "
            f"Group shares: {shares}.</p>\n"
            f"<p>Anti-gaming review: §3 requires re-checking any group contributing &gt; 50% of the total "
            f"and naming the decision carrying multiple points; this scenario's review trigger is {trigger}. "
            "The template provides no flag slot for this, so the trigger is stated here in the appendix.</p>\n"
            "<h3>Gaps</h3>\n"
            "<p>Not a real audit — no URL was fetched for this scenario. Likelihood values were chosen by "
            "the solver to hit the band boundary, which is exactly the rigging the §3 anti-gaming rules "
            "exist to catch (the pipeline itself enforces none of them).</p>"),
    })
    missing = [k for k in repl if k not in TEMPLATE]
    if missing:
        raise SystemExit(f"MISSING TOKENS: {missing}")
    html = TEMPLATE
    for k, v in repl.items():
        html = html.replace(k, v)
    if "{{" in html:
        raise SystemExit("UNREPLACED: " + html[html.find("{{"):html.find("{{") + 80])
    return html


def render_pdf(name):
    out = EDGE / f"report-{name}.pdf"
    if out.exists():
        out.unlink()
    r = subprocess.run(["chromium", "--headless", "--disable-gpu", "--no-sandbox",
                        f"--print-to-pdf={out}", "--no-pdf-header-footer",
                        f"report-{name}.html"],
                       cwd=EDGE, capture_output=True, text=True, timeout=180)
    if not out.exists():
        r2 = subprocess.run(["weasyprint", f"report-{name}.html", str(out)],
                            cwd=EDGE, capture_output=True, text=True, timeout=180)
        if not out.exists():
            raise RuntimeError(f"render failed: chromium rc={r.returncode} "
                               f"{r.stderr[-300:]}; weasyprint rc={r2.returncode} {r2.stderr[-300:]}")
        return out, "weasyprint-fallback"
    return out, "chromium"


def checks7(pdf, name):
    res = []
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    pm = re.search(r"Pages:\s+(\d+)", info)
    pages = int(pm.group(1)) if pm else 0
    size = re.search(r"Page size:.*", info)
    size = size.group(0).strip() if size else "?"
    res.append(("A4 page size", "A4" in size, size))
    res.append(("page count >= 8", pages >= 8, f"pages={pages}"))
    txt = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout
    n_tok = txt.count("{{")
    res.append(("no unreplaced {{ tokens", n_tok == 0, f"count={n_tok}"))
    parts = txt.split("\f")
    while parts and not parts[-1].strip():
        parts.pop()
    res.append(("cover has no footer", "For Human Eyes Only" not in parts[0], ""))
    body = parts[1:] if parts else []
    got = sum(1 for p in body if "For Human Eyes Only" in p)
    res.append(("footer on every body page", body and got == len(body), f"{got}/{len(body)}"))
    base = EDGE / f"cover-{name}"
    subprocess.run(["pdftoppm", "-png", "-r", "60", "-f", "1", "-l", "1",
                    str(pdf), str(base)], check=True, capture_output=True)
    png = base.with_name(base.name + "-01.png")
    ok = png.exists() and png.stat().st_size > 5000
    detail = f"{png.name} {png.stat().st_size if png.exists() else 0}B"
    if ok:
        try:
            from PIL import Image
            im = Image.open(png).convert("L")
            data = list(im.getdata())
            ink = sum(1 for v in data if v < 240) / len(data)
            ok = ink > 0.01
            detail += f" ink={ink:.3f}"
        except ImportError:
            detail += " (PIL unavailable, size check only)"
    res.append(("cover renders (§7.4)", ok, detail))
    return res, pages


def repro_build_divzero():
    src = (FIX / "build.py").read_text()
    tree = strip_side_effects(ast.parse(src, "build.py"))
    ns0 = load_build_ns()
    zero_pts = [(n, nm, 0, ev, 1, w) for n, nm, p, ev, l, w in ns0["POINTS"]]
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "POINTS":
            node.value = ast.parse(repr(zero_pts)).body[0].value
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "W":
            node.value = ast.parse(f"pathlib.Path({str(EDGE / '_divzero')!r})").body[0].value
    try:
        exec(compile(tree, "build.py", "exec"),
             {"__name__": "repro", "__file__": str(FIX / "build.py")})
        return "NO CRASH — suspected ZeroDivisionError did not reproduce"
    except ZeroDivisionError as e:
        frames = traceback.extract_tb(sys.exc_info()[2])
        line = [f for f in frames if f.filename == "build.py"][-1].lineno
        return f"REPRODUCED: ZeroDivisionError at build.py:{line} ({e})"


def main():
    args = sys.argv[1:]
    html_only = "--html-only" in args
    only = args[args.index("--scenario") + 1] if "--scenario" in args else None

    ns = load_build_ns()
    base = ns["POINTS"]
    EDGE.mkdir(exist_ok=True)
    (EDGE / "report-styles.css").write_text(CSS)
    (EDGE / "_divzero").mkdir(exist_ok=True)

    bev = evaluate(base)
    sanity = [("score", bev["score"] == 38.8, bev["score"]),
              ("sum", bev["total"] == 291.0, bev["total"]),
              ("band", bev["band"] == "Hybrid", bev["band"]),
              ("mild", bev["mild"] == 29, bev["mild"])]
    print("== baseline roundtrip (evaluate vs build.py) ==")
    for label, ok, got in sanity:
        print(f"  {'PASS' if ok else 'FAIL'} {label}: {got}")

    scenarios = build_scenarios(base)
    if only:
        scenarios = [s for s in scenarios if s["name"] == only]
        if not scenarios:
            raise SystemExit(f"unknown scenario {only}")

    failures = list(f"baseline:{l}" for l, ok, _ in sanity if not ok)
    table = []
    print("== scenarios ==")
    for sc in scenarios:
        name = sc["name"]
        ev = evaluate(sc["points"])
        rows_fail = []
        if ev["score"] != sc["escore"]:
            rows_fail.append(f"score {ev['score']} != {sc['escore']}")
        if ev["band"] != sc["eband"]:
            rows_fail.append(f"band {ev['band']} != {sc['eband']}")
        if ev["total"] * 2 != sc["target_halves"]:
            rows_fail.append(f"sum {ev['total']} != {sc['target_halves'] / 2}")
        for label, ok, detail in sc["extra"](ev):
            if not ok:
                rows_fail.append(f"{label}: {detail}")

        html = make_html(name, ev, ns)
        for label, ok, detail in [
            ("no '{{' in html", "{{" not in html, ""),
            ("hardcoded 54.7% absent", "54.7%" not in html, ""),
            ("band rendered", f">{ev['band']}<" in html, ev["band"]),
            ("score rendered", f">{ev['score']:g}%<" in html, f"{ev['score']:g}"),
            ("sum rendered", f"{ev['total']:g} / 750" in html, f"{ev['total']:g}"),
        ]:
            if not ok:
                rows_fail.append(f"{label}: {detail}")

        (EDGE / f"report-{name}.html").write_text(html)
        pages = "-"
        engine = "-"
        n_ok = n_all = 0
        if not html_only:
            try:
                pdf, engine = render_pdf(name)
                res, pages = checks7(pdf, name)
                n_ok = sum(1 for _, ok, _ in res if ok)
                n_all = len(res)
                for label, ok, detail in res:
                    if not ok:
                        rows_fail.append(f"§7 {label}: {detail}")
            except Exception as e:
                rows_fail.append(f"render/§7 exception: {e}")
        status = "PASS" if not rows_fail else "FAIL"
        for f in rows_fail:
            failures.append(f"{name}: {f}")
        print(f"  [{status}] score: {ev['score']:g} sum: {ev['total']:g} "
              f"band: {ev['band']} mild: {ev['mild']} "
              f"engine={engine} pages={pages} §7={n_ok}/{n_all}")
        for f in rows_fail:
            print(f"      ! {f}")
        table.append((name, f"{ev['score']:g}", f"{ev['total']:g}", ev["band"],
                      ev["mild"], str(pages), engine, f"{n_ok}/{n_all}", status))

    print("== bug repro: build.py all-zero run ==")
    dz = repro_build_divzero()
    print(f"  {dz}")

    print("== summary table ==")
    hdr = ("scenario", "score", "sum", "band", "mild", "pages", "engine", "§7", "status")
    w = [max(len(str(r[i])) for r in [hdr] + table) for i in range(len(hdr))]
    print("  " + "  ".join(str(h).ljust(w[i]) for i, h in enumerate(hdr)))
    for r in table:
        print("  " + "  ".join(str(c).ljust(w[i]) for i, c in enumerate(r)))
    print(f"== {len(table)} scenarios, {len(failures)} failures ==")
    for f in failures:
        print(f"  FAIL {f}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
