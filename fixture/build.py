import pathlib, sys, datetime
W = pathlib.Path("/home/anorak/Works/bytesmith/fixture")
SKILL = pathlib.Path("/root/.config/opencode/skills/bytesmith")
html = (SKILL/"report-template.html").read_text()
css  = (SKILL/"report-styles.css").read_text()
(W/"report-styles.css").write_text(css)

POINTS = [
 (1,"Gradients",2,"Hero backdrop `linear-gradient(135deg,#a855f7,#6366f1)`; gradient text on H1; CTA gradient fill.",4,1.5),
 (2,"Purple-black dominance",4,"6/6 sections use #8b5cf6 on #0a0a0a; 41% of sampled fills are violet.",5,1.5),
 (3,"Neon accents",2,"Cyan #22d3ee badges, pink #f472b6 borders on pricing.",3,1.5),
 (4,"Overused fonts",4,"Computed `font-family: Inter, sans-serif` for body and headings; sole family site-wide.",5,1.5),
 (5,"Serif italic accents",2,"Instrument Serif italic on 'faster' in every section header.",3,1.0),
 (6,"Lucide / sparkles",3,"`lucide-react` in deps; identical 24px stroke icons in rounded boxes on all 9 cards.",3,1.0),
 (7,"Emoji in headings",0,"No emoji in any heading or CTA.",1,1.0),
 (8,"Em dashes",1,"3 em dashes site-wide (~1 per 60 words); one in the hero.",2,0.5),
 (9,"Glassmorphism",2,"`backdrop-filter: blur(12px)` on sticky nav + hero stat card.",3,1.0),
 (10,"Bento grid",3,"Section 3 is a 5-tile asymmetric mosaic; features never appear as a plain list.",4,1.5),
 (11,"Identical feature cards",2,"Two rows of 3 equal cards, icon-box → title → line → link.",3,1.0),
 (12,"Colored border cards",2,"Pricing + feature cards use `1px solid #8b5cf633`.",2,1.0),
 (13,"Default shadcn",3,"`bg-primary text-primary-foreground`, `rounded-md shadow-sm` nav/Dialog/Dropdown verbatim.",5,1.5),
 (14,"Soft radius",0,"Radius is a deliberate 3-step scale: 0 / 8px / pill.",1,0.5),
 (15,"Floating decor",0,"No decorative blobs or orbs anywhere.",1,0.5),
 (16,"Pure white / low-contrast",2,"#ffffff page; muted text #9ca3af on white = 2.6:1 (fails AA).",3,0.5),
 (17,"Dot grid / terminal",1,"Dot texture on the CTA section only; no fake terminal block.",2,1.0),
 (18,"Badge-above-headline",3,"✦ pill → centered H1 → centered sub → two centered buttons → logo cloud. Default hero.",4,1.5),
 (19,"3-tier pricing",0,"Pricing is a single plan plus a usage meter — no tier stack.",3,1.5),
 (20,"Drop shadows",1,"`shadow-lg` on feature cards only.",2,0.5),
 (21,"Fade/rise on scroll",2,"Every section `whileInView` opacity+translateY(24px); card stagger on both feature rows.",3,0.5),
 (22,"Cursor beam",3,"`--mouse-x/--mouse-y` radial spotlight across the hero grid.",4,1.5),
 (23,"Hover animations",1,"`hover:-translate-y-1 hover:shadow-lg` on cards; buttons darken.",2,0.5),
 (24,"Buzzword copy",3,"'Supercharge your workflow', 'seamless', 'effortlessly', 'powerful' ×4, 'elevate' ×3.",4,1.5),
 (25,'"It\'s not X, it\'s Y"',2,"Hero: 'Not just a builder. A partner.' + section 2: 'Forget dashboards, embrace clarity.'",4,1.5),
 (26,"Fake product screenshots",0,"Shipped captures with real data; no browser-frame mocks.",3,1.0),
 (27,"Fake testimonials",3,"'Sarah J.', 'Alex T.' — pravatar.cc avatars, near-identical 14-word praise, no titles.",5,1.5),
 (28,"Stock photography",2,"Unsplash 'team laughing at laptop' + laptop-on-desk hero.",3,1.0),
 (29,"Checkmark bullets",0,"No green ✓ walls; capability list is a plain typographic list.",2,0.5),
 (30,"FAQ restating product",2,"6 of 8 Q&As restate the hero blurb ('What is Acme?'), answers ≤12 words.",3,1.0),
 (31,"Vague CTAs",2,"'Get Started' ×4, 'Learn More' ×2 across nav, hero, mid-page, footer.",3,1.0),
 (32,"Missing TOS / Privacy",1,"`/privacy` returns 404; footer links to `#`.",2,0.5),
 (33,"Missing skeletons",0,"Loading skeletons match final geometry; images reserve space.",1,0.5),
 (34,"Inconsistent spacing",2,"Section padding cycles 64 → 128 → 96 → 64px; card gutters 16 vs 24px.",3,1.0),
 (35,"Dead links",1,"Footer 'Careers' returns 404; 'Docs' in top nav points at # (working sections are fine).",2,1.0),
 (36,"No personality",2,"Opinion appears once (the pricing note); hero still generic.",4,1.5),
]

P_LABEL = {0:"None",1:"Mild",2:"Moderate",3:"Heavy",4:"Extreme"}

# Anti-gaming validation (SKILL.md §3) — refuse to render a violating score
ABSENCE=(32,33,36); SIBLINGS=((1,2,3),(24,25),(19,29))
SECTIONS=((1,16),(17,19),(20,23),(24,31),(32,36))
errs=[]
if abs(sum(t[5] for t in POINTS)-37.5)>1e-9:
    errs.append(f"Σw = {sum(t[5] for t in POINTS):g}, expected 37.5")
by={t[0]:t for t in POINTS}
for n,name,p,ev,l,w in POINTS:
    if not 0<=p<=4: errs.append(f"pt {n}: presence {p} out of 0-4")
    if not 0<=l<=5: errs.append(f"pt {n}: likelihood {l} out of 0-5")
for sib in SIBLINGS:
    for n in sib:
        if by[n][2]>=3:
            for m in sib:
                if m!=n and by[m][2]>2:
                    errs.append(f"sibling cap: pt {m} presence {by[m][2]} > Moderate while pt {n} is ≥ Heavy")
def section_of(n):
    return next((lo,hi) for lo,hi in SECTIONS if lo<=n<=hi)
for a in ABSENCE:
    if by[a][2]>1:
        lo,hi=section_of(a)
        if not any(by[m][2]>=2 for m in by if m!=a and lo<=m<=hi):
            errs.append(f"absence pt {a}: presence {by[a][2]} > Mild with no ≥ Moderate peer in its section")
if errs: sys.exit("ANTI-GAMING VIOLATIONS:\n- "+"\n- ".join(errs))

rows=[]; total=0.0; mild=0
for n,name,p,ev,l,w in POINTS:
    c = w*p*l; total += c
    if p>=1: mild+=1
    rows.append(
      f'<tr><td class="num">{n}</td><td>{name}</td>'
      f'<td><span class="pill p{p}">{P_LABEL[p]}</span></td>'
      f'<td>{ev}</td><td class="num">{l}</td><td class="num">{w:g}</td>'
      f'<td class="num">{c:g}</td></tr>')
score = round(100*total/750, 1)

def subtotal(idx):
    return round(sum(w*p*l for n,name,p,ev,l,w in POINTS if idx(n)),1)
groups = [
 ("Group A — Visual language (1-16)", lambda n: n<=16),
 ("Group B — Component & layout (17-19)", lambda n: 17<=n<=19),
 ("Group C — Motion & interaction (20-23)", lambda n: 20<=n<=23),
 ("Group D — Copy & content (24-31)", lambda n: 24<=n<=31),
 ("Group E — Trust & polish (32-36)", lambda n: n>=32),
]
calc=[]
for label,fn in groups:
    s=subtotal(fn); wsum=sum(w for n,_,_,_,_,w in POINTS if fn(n))
    calc.append(f'<tr><td>{label}</td><td class="num">{wsum:g}</td>'
                f'<td class="num">{s:g}</td><td class="num">{(s/total*100 if total else 0.0):.1f}%</td></tr>')

ga = subtotal(lambda n: n<=16)
ga_share = (ga/total*100) if total else 0.0
if ga_share > 50:
    ga_flag = (f"carried {ga_share:.1f}% of total, flagged as a review trigger "
               "and confirmed to reflect one structural decision (the bento/gradient system)")
else:
    ga_flag = f"carried {ga_share:.1f}% of total — below the 50% review trigger"

band = ("Vibecoded" if score>=80 else "AI-dominant" if score>=60 else
        "Hybrid" if score>=35 else "Human + AI assists" if score>=15 else "Human-crafted")

repl = {
 "{{PROJECT_NAME}}":"Acme — Vibecode Audit",
 "{{TARGET_URL}}":"https://acme.example",
 "{{REPORT_DATE}}":datetime.date.today().isoformat(),
 "{{AI_SCORE}}":f"{score:g}",
 "{{SCORE_BAND}}":band,
 "{{VERDICT_LINE}}":"The defaults are the design. Not one of the 36 checks was decided on purpose.",
 "{{RAW_SUM}}":f"{total:g}",
 "{{POINT_COUNT_MILD}}":f"{mild} / 36",
 "{{EXEC_SUMMARY}}":("<p>Acme scores <strong>"+f"{score:g}%"+"</strong> — "+band+
   ", on a weighted sum of "+f"{total:g}"+" of 750. The page is assembled almost entirely from "
   "recognizable defaults: a violet-on-black palette (#8b5cf6 over #0a0a0a), Inter as the sole typeface, "
   "a bento feature mosaic, an unmodified shadcn component set, and copy built from the "
   "standard AI vocabulary.</p>"
   "<p>The heaviest signals are structural rather than cosmetic. Point 18 (badge-above-headline hero) "
   "and point 13 (default shadcn) both score Heavy because they are load-bearing: remove them and there "
   "is no layout left. Point 27 (fabricated testimonials) and point 25 (<em>\"Not just a builder. "
   "A partner.\"</em>) are the tells a visitor actually reads.</p>"),
 "{{SCORE_ROWS}}":"\n".join(rows),
 "{{CALC_ROWS}}":"\n".join(calc),
 "{{ROAST}}":("""<p>Somewhere between the gradient and the third badge pill, this page stops being a product and
becomes a receipt for a subscription you didn't know you had. The hero is the tell — a pill with a
sparkle, a centered headline, a centered subhead, two centered buttons, and a logo cloud underneath,
arranged with the confidence of something that has never once been rearranged.</p>
<blockquote>Not just a builder. A partner.</blockquote>
<p>That sentence is doing no work. It is a hinge that swings shut on nothing: we are told what the thing
is not, and then told what it supposedly is, and neither half contains a fact. Around it, the page runs
the full inventory — bento tiles of unequal height pretending to be thought, nine cards wearing the same
rounded icon box, a terminal block that executes no command, a cursor spotlight painting the grid in a
color the product never uses. Nothing here is broken. That is precisely the problem: it was never
stress-tested against a decision.</p>
<p>And then the testimonials, which are the one place a real company puts its money where its mouth is.
\"Sarah J.\" beside a generated face, praising the product in fourteen words that describe no feature —
and \"Alex T.\" doing it again with the nouns swapped. If two people love your product this much, name
them. If you cannot, you do not have two people yet, and the page would be more persuasive admitting it.</p>
<p>Strip the adjectives and what remains is a layout that would render identically for a plant-watering
app, a SOC-2 compliance tool, and a fictional hedge fund. Nothing sticks. Nothing was chosen. The score
is not a verdict on the tooling — plenty of legitimate work ships from these same components — it is a
verdict on the absence of anyone in the room who said <em>no</em>.</p>"""),
 "{{COUNTERMEASURES}}":("""
<h3>1. Visual System</h3>
<table><thead><tr><th style="width:8%">Point</th><th style="width:34%">Diagnosis</th><th style="width:58%">Countermeasure</th></tr></thead><tbody>
<tr><td>1, 2, 3</td><td>#a855f7→#6366f1 hero gradient over #0a0a0a; 41% of sampled fills violet.</td><td>Replace violet with an oxide red (#b4451f) as the single accent and set surfaces on warm paper (#fbfaf7) with ink #14181d. One flat accent, no gradient behind content; any remaining falloff must come from a real photograph.</td></tr>
<tr><td>10</td><td>Features only ever appear as a 5-tile bento mosaic.</td><td>Set a narrative order instead: one idea per section in a 7/5 asymmetric split, with a full-bleed break where the argument peaks. Let content determine tile count — never a fixed mosaic.</td></tr>
<tr><td>13</td><td>`bg-primary text-primary-foreground`, `rounded-md shadow-sm` shipped verbatim.</td><td>Re-skin tokens <em>and</em> geometry: radius scale, 1px hairline borders, label casing, focus ring color, and a real spacing step. If a component still reads as shadcn, it is unmodified.</td></tr>
</tbody></table>
<h3>2. Typography &amp; Voice</h3>
<table><thead><tr><th style="width:8%">Point</th><th style="width:34%">Diagnosis</th><th style="width:58%">Countermeasure</th></tr></thead><tbody>
<tr><td>4, 5</td><td>Inter sole family site-wide; Instrument Serif italic on one word per heading.</td><td>Pair a grotesk with a text serif by contrast of voice (e.g. Lato + Bitstream Charter), then tune: negative tracking on display sizes, per-size line-height, and a 1.333 ratio type scale. Use italic serif as a system (pull-quotes, section numbers) or not at all.</td></tr>
<tr><td>24, 25</td><td>"Supercharge", "seamlessly", "elevate" ×3; "Not just a builder. A partner."</td><td>Delete every buzzword, then force specificity: state what it does, for whom, with which number. Replace the rhetorical pivot with a direct claim — "Imports 12k Stripe rows in 4s."</td></tr>
<tr><td>31</td><td>"Get Started" ×4 across nav, hero, mid-page, footer.</td><td>Label each CTA with that section's outcome: "Start a free audit", "See the 36-point checklist".</td></tr>
</tbody></table>
<h3>3. Interaction &amp; Motion</h3>
<table><thead><tr><th style="width:8%">Point</th><th style="width:34%">Diagnosis</th><th style="width:58%">Countermeasure</th></tr></thead><tbody>
<tr><td>21, 22</td><td>Every section rises on scroll; cursor spotlight tracks --mouse-x across the grid.</td><td>Delete the spotlight. Keep only motion that carries meaning — reveal in reading order, a number that counts because it is a quantity. If removing the animation changes nothing, remove it.</td></tr>
</tbody></table>
<h3>4. Content &amp; Proof</h3>
<table><thead><tr><th style="width:8%">Point</th><th style="width:34%">Diagnosis</th><th style="width:58%">Countermeasure</th></tr></thead><tbody>
<tr><td>27</td><td>"Sarah J." / "Alex T." on pravatar.cc avatars, 14-word praise, no titles.</td><td>Only verifiable quotes: full name, role, company, linkable. Until they exist, use the empty state honestly — "We're 4 weeks old" — instead of manufacturing consensus.</td></tr>
<tr><td>28</td><td>Unsplash team-laughing stock carries two sections.</td><td>Owned photography, product imagery, or your own architecture diagram. A real desk beats a stock handshake.</td></tr>
<tr><td>30</td><td>6 of 8 FAQs restate the hero blurb.</td><td>Answer the objections nobody wants: pricing edge cases, migration effort, what happens on churn, who this is <em>not</em> for.</td></tr>
</tbody></table>
<h3>5. Structure &amp; Polish</h3>
<table><thead><tr><th style="width:8%">Point</th><th style="width:34%">Diagnosis</th><th style="width:58%">Countermeasure</th></tr></thead><tbody>
<tr><td>18, 19</td><td>Default centered hero; default 3-tier pricing with `scale-105` middle card.</td><td>Give the hero an editorial structure — eyebrow, left-aligned headline in a real subhead column, one CTA plus one proof point. Design pricing as a table or usage meter matching how the product is bought.</td></tr>
<tr><td>34, 35</td><td>Section padding cycles 64/128/96/64px; footer "Careers" → 404.</td><td>Adopt and enforce a spacing scale (4/8/12/16/24/40/64/96) and re-measure every section against it. Crawl every href and remove, replace, or date the placeholder.</td></tr>
</tbody></table>"""),
 "{{ROADMAP_ROWS}}":"".join(
   f'<tr><td><span class="pill p{pr}">P{pr}</span></td><td>{ef}</td><td>{act}</td><td class="small">{pts}</td><td class="num">{d}</td></tr>'
   for pr,ef,act,pts,d in [
     (1,"Low","Replace fabricated testimonials with verifiable quotes or an honest empty state","27, 30","−9.2"),
     (1,"Low","Delete all buzzword copy and the 'not X, it's Y' construction; rewrite with specifics","24, 25","−14.4"),
     (2,"Medium","Replace Inter with a tuned two-family type scale; drop serif-italic tic","4, 5","−14.0"),
     (2,"Medium","Re-skin shadcn tokens and geometry; define radius and spacing by hierarchy","13, 14, 34","−15.2"),
     (2,"Low","Ship real /terms and /privacy; fix dead footer links","32, 35","−4.3"),
     (3,"Medium","Replace violet-on-black with one accent on a considered surface","1, 2, 3, 16","−27.4"),
     (3,"High","Restructure hero (editorial, not badge-centered) and rebuild the feature narrative","10, 11, 18","−22.5"),
     (4,"Low","Remove cursor spotlight and section-fade cascade; keep motion only where it means something","21, 22","−16.1"),
   ]),
 "{{APPENDIX}}":(f"""
<h3>Method</h3>
<p>Full fetch of the marketing surface plus `/`, `/pricing`, `/terms`, `/privacy` probe; renders captured at
1440px and 390px. All 36 points scored before any total was computed. Correlated siblings capped;
absence points limited to Mild; group shares reviewed — Group A {ga_flag}.</p>
<h3>Per-section observations</h3>
<ul>
<li><strong>Hero</strong> — badge pill + centered stack + logo cloud. Full default pattern (point 18, Heavy).</li>
<li><strong>Features</strong> — two identical 3-card rows and one bento mosaic; no section uses a different layout device.</li>
<li><strong>Pricing</strong> — 3 tiers, toggle, `scale-105` middle card with violet border.</li>
<li><strong>Testimonials</strong> — three cards, generated faces, no titles or company names.</li>
<li><strong>Footer</strong> — Careers → 404; Docs → `#`; Privacy → 404.</li>
</ul>
<h3>Gaps</h3>
<p>Logged-out only; application UI behind auth was not evaluable, so point 33 (skeletons) was scored Mild
on marketing-page evidence alone. Scroll-triggered motion was observed via CSS/JS inspection rather than
recorded playback.</p>
"""),
}
missing=[k for k in repl if k not in html]
if missing: sys.exit("MISSING TOKENS: "+str(missing))
for k,v in repl.items(): html = html.replace(k,v)
if "{{" in html: sys.exit("UNREPLACED: "+html[html.find("{{"):html.find("{{")+80])
(W/"report.html").write_text(html)
print("score:", score, "sum:", total, "band:", band, "mild:", mild)
print("tokens ok")
