# Human-Made Countermeasure Blueprint

Every point scoring **presence ≥ Mild** needs one row here. Direction must be executable — a real typeface name, a real layout device, a real asset strategy, a real copy structure. "Be more unique" is not a countermeasure.

Blueprint ships as five sections, in this order:

## 1. Visual System

| Fingerprints | Antidote |
|---|---|
| 1 Gradients | Replace with a single flat brand color, or a *photographic/texture* light source (one real photo, one hard-lit studio backdrop). If a gradient must survive, it needs a stated reason — light falloff, material — and only one. |
| 2 Purple-black | Pick a non-violet hue from the product's domain (a clinic's chartreuse, a foundry's oxide red, a terminal's phosphor). Build surface from warm neutrals (`#14181d` ink on `#fbfaf7` paper) or a *tinted* neutral — never `#0a0a0a`. |
| 3 Neon/pastel | Reserve chroma for one semantic role (status, price delta, verified). Everything else reads by value, not hue. |
| 9 Glassmorphism | Give surfaces an edge: hairline rule, inset, or a printed-matter card with real weight. |
| 10 Bento | Choose a narrative order — one idea per section, stacked, with deliberate asymmetry (7/5, full-bleed break, sidebar). Variety must come from content, not from a mosaic component. |
| 11 3-card rows | Vary by importance: one dominant item + two subordinate; or a row of 5 small; or a definition list. Never three equal boxes. |
| 12 Colored borders | Use fill, value contrast, or a rule to define containers. Tinted borders are the AI default. |
| 13 Default shadcn | Re-skin tokens *and* geometry: radius, border weight, label typography, focus rings, spacing. If a component still reads as shadcn, it is unmodified. |
| 14 Soft radius | Assign radius by hierarchy (sharp for rules/structure, soft for touch targets). Uniform radius = no decision. |
| 15 Decor blobs | Remove. Replace with content: a real diagram, a data plot, an owned artifact. |
| 16 Pure white / low-contrast dark | Choose an intentional surface: warm paper, tinted dark, or a printed stock. Fix body text to ≥4.5:1 against it. |
| 17 Dot grid / terminal | Kill decorative terminal blocks unless the product *is* a CLI — then make them real, with output that means something. Drop the dot texture; use paper grain or nothing. |
| 20 Drop shadows | Depth from overlap, scale, and value — not from blur. Where a shadow survives, make it tight and contact-like, not a floating glow. |

## 2. Typography & Voice

| Fingerprints | Antidote |
|---|---|
| 4 Overused fonts | Pick a family that is *not* Inter/Geist/Space Grotesk/Instrument Serif. Pair by contrast of voice (a grotesk + a real serif, or a narrow + a wide). Then tune: set explicit tracking on display sizes (negative on large), fix line-height per size, set a type scale with a real ratio (1.25 / 1.333) instead of 16/18/20/24. |
| 5 Serif italic accents | Use italic serif as a *system* (pull-quotes, section numbers, footnote asides) or not at all. A single decorative word in every headline is a tic. |
| 6 Lucide / sparkles | Source an icon set with a point of view (Feather alternatives from a different school, custom 16px glyphs, or none). If the product needs icons, draw 6 for the 6 places they matter — not 60 identical rounded strokes. |
| 7 Emoji in headings | Text or a real icon. Emoji belongs in one place at most: a changelog or a casual banner. |
| 8 Em dashes | Vary punctuation: colon, semicolon, short sentence, full stop. Count them; if >1 per 100 words in headings, cut. |
| 24 Buzzwords | Delete every word in the buzzword list. Then force specificity: state *what it does, for whom, with which number*. "Imports 12k rows from Stripe in 4 seconds" beats "supercharge your workflow". |
| 25 "Not X, it's Y" | State the thing directly. One concrete claim beats a rhetorical pivot. |
| 31 Vague CTAs | Label with the value: "Start a free audit", "See the 36-point checklist", "Ship your first import". Each section's CTA should name that section's outcome. |
| 36 No personality | Write something only this team would write — a real opinion, a real limit, a real story, a named customer, a stated what-we-don't-do. Then design one visual moment (a hero artifact, a typographic set piece) that could not belong to anyone else. |

## 3. Interaction & Motion

| Fingerprints | Antidote |
|---|---|
| 21 Fade/rise on scroll | Motion must mean something: reveal that follows the reading order, a transition that explains state, a number that counts *because* it is a quantity. If removing the animation changes nothing, remove it. |
| 22 Cursor beam | Delete. If the hero needs life, give it a real behavior: hover-scrubbed data, a drag, a live preview. |
| 23 Hover | Differentiate by control type: links underline, cards lift *slightly*, buttons darken, rows tint. One easing family, varied durations — not `transition-all` everywhere. |
| 33 Missing skeletons | Add loading states that match final geometry (skeleton rows at real heights), `loading="lazy"` on media, and reserve space so nothing jumps. |

## 4. Content & Proof

| Fingerprints | Antidote |
|---|---|
| 26 Fake screenshots | Ship the real interface, real data, real numbers you can defend — a live embed, a real capture, or a scrollable demo. Never a browser frame with invented charts. |
| 27 Fake testimonials | Only verifiable quotes: full name, role, company, linkable. If you don't have them yet, use the empty state honestly — "we're 4 weeks old" — instead of manufacturing consensus. |
| 28 Stock photos | Owned photography, product imagery, diagrams of your own architecture, or no photo. A real desk beats a stock handshake every time. |
| 29 Checkmarks | Vary by meaning: differentiated bullets, a comparison table with real caveats (including what you *don't* do), or plain typographic lists. |
| 30 Restating FAQ | Answer the objection nobody wants to answer: pricing edge cases, migration effort, what happens on churn, why not X, who this is *for*. One hard answer is worth ten soft ones. |

## 5. Structure & Polish

| Fingerprints | Antidote |
|---|---|
| 18 Badge-above-headline | Give the hero an asymmetric or editorial structure: eyebrow set differently, headline left-aligned with a real subhead column, one CTA and one proof point instead of two centered buttons. |
| 19 3-tier pricing | Design pricing as a table, a calculator, a single-plan with addons, or a usage meter — whatever matches how the product is actually bought. |
| 32 Missing TOS/Privacy | Ship real `/terms` and `/privacy`, linked in the footer, dated, and matching what the product actually does. |
| 34 Inconsistent spacing | Define and enforce a spacing scale (e.g. 4/8/12/16/24/40/64/96) and a section rhythm; re-measure every section against it. Same for grid gutters and card padding. |
| 35 Dead links | Crawl every `href`. Remove, replace, or mark as "coming soon" with a real date. A 404 in the footer is a confession. |

---

## Assembling the section

For each of the five categories emit:

```html
<section>
  <h2>1. Visual System</h2>
  <table>
    <tr><th>Point</th><th>Diagnosis</th><th>Countermeasure</th></tr>
    <!-- one row per fingerprint with presence >= Mild -->
  </table>
</section>
```

Rules:

- **One row per scored point** — the reader cross-references against `{{SCORE_ROWS}}`.
- Diagnosis cites the evidence from the audit ("violet `#8b5cf6` on `#0a0a0a` across all 6 sections"), not a restatement of the checklist.
- Countermeasure names real fonts, real colors, real layout moves, real copy structures.
- If a countermeasure would *contradict* another (e.g. keep the gradient vs kill it), resolve it and note the tradeoff — never ship conflicting advice.
