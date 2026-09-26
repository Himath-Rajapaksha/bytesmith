# 36-Point Checklist

Presence scale (apply literally):

| Score | Label | Meaning |
|---|---|---|
| 0 | **None** | Searched for it, not present. |
| 1 | **Mild** | Present once, or only in one secondary section. |
| 2 | **Moderate** | Present in 2-3 sections, or a notable single instance. |
| 3 | **Heavy** | Structural — drives the layout, not a garnish. |
| 4 | **Extreme** | The page could not exist without it; visibly automated. |

AI Likelihood (0-5): how strongly this pattern's *presence* implies AI authorship in this codebase, **given what else is on the page**. A purple gradient on a charity site is a 5; on a crypto site it may be a 1.

Correlated siblings: if one of **{1,2,3}** scores Heavy, the other two cap at Moderate. Same cap logic for **{24,25}** and **{19,29}**.

---

## A. Visual Language (1-16)

**1. Gradients** — *w 1.5*
Detect: hero/backdrop/button fills blending ≥2 hues; `linear-gradient`/`radial-gradient` in rendered CSS; gradient text.
Anchors: 0 none · 1 one accent · 2 hero + CTA · 3 gradient is the backdrop of most sections · 4 gradient text + gradient buttons + gradient blobs.

**2. Purple-and-Black Dominance** — *w 1.5*
Detect: violet/indigo as the primary hue on near-black (`#0a0a0a`–`#18181b`); hex-dump the 8 most-used fills. Classic triad: `#8b5cf6`, `#6366f1`, `#a855f7`.
Anchors: 0 no violet · 1 violet on a neutral page · 2 violet = brand + black is the field · 3 violet+black is every section · 4 whole page is one violet ramp.

**3. Neon / Pastel Accents** — *w 1.5*
Detect: `#22d3ee`, `#34d399`, `#f472b6`, `#facc15` used as glow/border/text on dark; pastel gradient chips.
Anchors: 0 none · 1 one status color · 2 badges + buttons · 3 accent color carries the hierarchy · 4 glow on everything.

**4. Overused Fonts** — *w 1.5*
Detect: Inter, Geist, Space Grotesk, Instrument Serif, Plus Jakarta Sans, Satoshi, General Sans — as *the only* family. Read `font-family` from computed styles; check both headings and body.
Anchors: 0 none of them · 1 one used sparingly · 2 them as body/headings · 3 site's entire type system · 4 they appear with default tracking/leading too (no typographic tuning at all).

**5. Serif Italic Accents** — *w 1.0*
Detect: single italic serif word dropped into a sans headline ("Ship *faster*"). Instrument Serif / Playfair / Newsreader italic.
Anchors: 0 none · 1 one hero instance · 2 every section header · 3 italic serif is the identity · 4 it recurs in every text node, nav and buttons included.

**6. Lucide / Sparkle Icons** — *w 1.0*
Detect: `lucide`/`lucide-react` in deps, `stroke-linecap="round"` SVG set, the ✦ sparkle glyph, identical 24px 2px-stroke icon in a rounded container on every card.
Anchors: 0 distinct icons · 1 Lucide for nav only · 2 identical Lucide boxes on all feature cards · 3 Lucide + sparkles + emoji mixed · 4 every element, including plain links, wears an icon box.

**7. Emoji in Headings** — *w 1.0*
Detect: emoji inside `<h1>`–`<h3>`, section eyebrows, or CTAs (🚀 ⚡ ✨ 🔒 🎉).
Anchors: 0 none · 1 one eyebrow · 2 section headers · 3 emoji as the icon system · 4 emoji appear in every heading, nav item, and CTA.

**8. Em Dashes** — *w 0.5*
Detect: `—` density per 100 words in headings and hero copy (read the copy; do not guess from screenshots).
Anchors: 0 none · 1 occasional · 2 one per section heading · 3 the default connector everywhere · 4 multiple per heading; prose is unreadable without them. **Note:** human writers use these too — likelihood rarely above 2.

**9. Glassmorphism** — *w 1.0*
Detect: `backdrop-filter: blur()` + translucent `rgba` fill + 1px `rgba(255,255,255,.1)` border on nav/cards/modals.
Anchors: 0 none · 1 nav bar · 2 nav + cards · 3 glass is the layout system · 4 even body copy and footers sit in blurred panels.

**10. Bento Grids** — *w 1.5*
Detect: asymmetric 2×2 / 3-col mosaic of unequal-height cards with different internal components — the AI "variety grid".
Anchors: 0 none · 1 one mosaic section · 2 bento is how all features are shown · 3 bento runs down the whole page · 4 no full-width section exists; hero and footer are mosaics too.

**11. Identical Feature Cards (3-card row)** — *w 1.0*
Detect: exactly 3 (or 4) equal cards, same structure: icon-box → title → one line → link. Generated from a `features[]` array.
Anchors: 0 varied layouts · 1 one such row · 2 most sections are such rows · 3 entire page is a card matrix · 4 source shows one features[] array rendered N times.

**12. Colored Border Cards** — *w 1.0*
Detect: cards defined by `1px solid` tinted borders (`#8b5cf633`) instead of fill/shadow/contrast; colored top-strip or left-strip variants.
Anchors: 0 none · 1 one callout · 2 pricing + features · 3 all containers · 4 borders and tinted strips everywhere; no filled or value-contrasted surface at all.

**13. Default shadcn / Tailwind Components** — *w 1.5*
Detect: shadcn/ui defaults shipped untouched — `rounded-md`, `bg-primary text-primary-foreground`, `shadow-sm`, `Ring`/`Dialog`/`Sheet` in default styling, `$bg-background $text-foreground` tokens, `space-y-4` + `flex items-center justify-between` header pattern.
Anchors: 0 customized · 1 some defaults · 2 recognizable shadcn component set · 3 verbatim defaults for nav, dialog, dropdown, form · 4 default tokens untouched in source (`bg-background`, `rounded-md` sitewide).

**14. Soft Corner Radius** — *w 0.5*
Detect: universal `rounded-lg`/`rounded-xl`/`rounded-2xl` (12-24px) on everything; radius applied uniformly rather than by hierarchy.
Anchors: 0 sharp/considered · 1 one radius scale · 2 everything soft · 3 soft radius even on tags, inputs, images · 4 a single radius value applied to every element, rules and text included.

**15. Floating 3D Shapes / Decor Blobs** — *w 0.5*
Detect: orbiting spheres, torus renders, gradient blobs, grain-noise PNG, low-opacity decorative orbs behind content.
Anchors: 0 none · 1 one hero decor · 2 background decor throughout · 3 decor competes with content · 4 blobs are layered behind every section, footer included.

**16. Pure White / Low-Contrast Dark** — *w 0.5*
Detect: `#ffffff` page or `#0a0a0a` page with body text `< 4.5:1`; both are the "default" starting point.
Anchors: 0 considered surface · 1 near-default · 2 default + poor text contrast · 3 default surface AND failing contrast across the site · 4 the same, with body text under 3:1 sitewide.

## B. Component & Layout Tells (17-19)

**17. Dot Grids / Terminal Windows** — *w 1.0*
Detect: `radial-gradient` dot/cross pattern as section background; faux terminal blocks with 3 traffic-light dots and monospace `npm install` lines; code windows that do nothing.
Anchors: 0 none · 1 one section · 2 decorative terminal in features · 3 the dot grid is the page texture · 4 dot grid everywhere plus a faux traffic-light terminal in every section.

**18. Badge-Above-Headline** — *w 1.5*
Detect: pill/badge with a ✦ emoji + short label sitting above `<h1>`, then centered headline, then centered sub, then two centered buttons. (`px-4 py-1.5 rounded-full text-xs border`)
Anchors: 0 unconventional hero · 1 badge only · 2 badge + centered stack · 3 badge + centered stack + logo cloud below = the default hero · 4 the same default hero is cloned as every section header.

**19. Three-Tier Pricing** — *w 1.5*
Detect: 3 columns, monthly/annual toggle, middle card "Most Popular" with a colored border and a `scale-105`.
Anchors: 0 other pricing design · 1 3 tiers but hand-styled · 2 default 3-tier + popular badge · 3 full default component with toggle · 4 the default pricing block plus default testimonial and FAQ blocks beneath it.

## C. Motion & Interaction (20-23)

**20. Drop Shadows** — *w 0.5*
Detect: `shadow-lg` / `box-shadow: 0 10px 40px rgba(0,0,0,.1)` on cards, floating navs, buttons as the primary depth device.
Anchors: 0 flat/considered · 1 cards only · 2 shadows everywhere · 3 shadow stacks (inner + outer) · 4 stacked inner + outer + glow shadows on every box, text run, and input.

**21. Fade / Rise on Scroll** — *w 0.5*
Detect: every section `opacity 0 → 1` + `translateY(24px)` on intersection; identical staggered card reveals (Framer Motion `whileInView`, AOS).
Anchors: 0 intentional motion · 1 one hero reveal · 2 all sections · 3 section reveal + card stagger + text stagger — the full cascade · 4 every glyph staggers; disabling JS leaves the page blank.

**22. Cursor Light Beam / Spotlight** — *w 1.5*
Detect: `radial-gradient` following `--mouse-x/--mouse-y` on hero/grid; pointer-reactive glow cards; custom cursor dot.
Anchors: 0 none · 1 hero only · 2 beam across the grid · 3 beam is the hero's whole idea · 4 beams run in every section and a custom cursor dot follows site-wide.

**23. Hover Animations** — *w 0.5*
Detect: uniform `hover:-translate-y-1 hover:scale-105 hover:shadow-xl transition-all` on every interactive element, all with the same duration/easing.
Anchors: 0 considered states · 1 cards only · 2 buttons+cards+links · 3 identical lift/blur on literally everything · 4 the same transform + shadow fires even on static text and dividers.

## D. Copy & Content (24-31)

**24. Buzzword Copy** — *w 1.5*
Detect: count occurrences of — *supercharge, unlock, unleash, seamless, powerful, effortlessly, revolutionize, next-generation, cutting-edge, game-changer, elevate, robust, streamlined, one-stop, built for the modern…*
Anchors: 0 none · 1-2 in sub copy · 2 most section headlines · 3 the whole page is filler · 4 buzzwords appear in nav, buttons, and footer; no concrete claim exists anywhere.

**25. "It's not X, it's Y" Copy** — *w 1.5*
Detect: the rhetorical move verbatim — "Not just a tool. A partner." / "This isn't X, it's Y" / "Forget X. Embrace Y."
Anchors: 0 none · 1 one instance · 2 it structures the hero and 2 sections · 3 it is the voice · 4 every headline and CTA runs the pivot.

**26. Fake Product Screenshots / Mockups** — *w 1.0*
Detect: browser-chrome mockups showing data that cannot exist (perfect metrics, invented UI, lorem stats), device frames floating at 15°, glassy reflections; screenshot text unreadable or inconsistent with the real product.
Anchors: 0 real or honest · 1 one decorative mock · 2 mockups as primary proof · 3 mockups contradict the live app · 4 every visual is invented; the real product is never shown.

**27. Fake Testimonials** — *w 1.5*
Detect: generic names ("Sarah J.", "Alex T."), stock avatars, `i.pravatar.cc` / Unsplash faces, identical sentence lengths, no company/title, no links, praise that describes no specific feature.
Anchors: 0 none or verifiable · 1 one section, real names · 2 obviously generated · 3 generated + fake metrics ("10,000+ teams") · 4 fake quotes, fake logos, and a fake press row.

**28. Stock Team / Office Photography** — *w 1.0*
Detect: Unsplash "team in office", laptop-on-desk, handshake, laughing-coworkers; generic hero photography unrelated to the product.
Anchors: 0 none/owned · 1 one editorial shot · 2 stock carries the sections · 3 stock + fake product shots · 4 stock photography is the entire visual system, with images repeated across sections.

**29. Checkmark Bullets** — *w 0.5*
Detect: `✓`/`CheckIcon` lists in features, pricing, comparison tables; all green or all brand color.
Anchors: 0 other list treatment · 1 pricing only · 2 features + pricing · 3 checkmarks + colored check circles as the icon system · 4 every list item on the page, footnotes included, is a green check.

**30. FAQ Restating the Product** — *w 1.0*
Detect: accordion Qs that restate marketing copy instead of answering objections; "What is X?" / "Why X?" / "How is X different?" where the answer is the hero blurb; answers one sentence long.
Anchors: 0 substantive FAQ · 1 1-2 soft questions · 2 most questions self-referential · 3 accordion is padding · 4 every answer restates the hero blurb verbatim; pure SEO filler.

**31. Vague CTAs** — *w 1.0*
Detect: "Get Started", "Learn More", "Try for Free" with no value noun, repeated across every section; identical button label in hero, nav, mid-page, footer.
Anchors: 0 specific CTAs · 1 generic in nav · 2 generic everywhere · 3 generic + a vague secondary ("See how it works" → nothing) · 4 every interactive element says "Get Started" and links to the same place.

## E. Trust & Polish (32-36)

**32. Missing TOS / Privacy** — *w 0.5*
Detect: `/terms`, `/privacy` absent, 404, or footer links to `#`. **Absence-only** — max Mild unless another point in this section is ≥ Moderate.
Anchors: 0 terms and privacy live and dated · 1 live but thin or undated · 2 one missing or 404 · 3 both missing · 4 footer links point to `#` and the pages are placeholder stubs.

**33. Missing Skeleton / Loading States** — *w 0.5*
Detect: no loading affordance on lists/data; layout jumps on fetch; no `loading="lazy"`/skeleton on async content. Requires an interactive app to judge — if static marketing only, record **None** and note "not evaluable".
Anchors: 0 loading states match final geometry and space is reserved · 1 lazy-loading attributes only · 2 layout jumps on fetch · 3 no loading affordance anywhere · 4 every data view flashes blank to content.

**34. Inconsistent Spacing / Broken Flow** — *w 1.0*
Detect: vertical rhythm jumps between sections (96px / 64px / 128px with no rule), uneven card gutters, misaligned grid edges, one section's padding unrelated to the rest; layout shifting across breakpoints.
Anchors: 0 consistent scale · 1 one odd section · 2 several · 3 no discernible system · 4 spacing is random per section; no two sections match at any breakpoint.

**35. Dead Links / Placeholder Pages** — *w 1.0*
Detect: 404s, `#` hrefs, "Coming soon" pages, empty legal/blog/careers, `href=""`, untranslated `TODO`/lorem in output.
Anchors: 0 all live · 1 one placeholder · 2 footer/secondary dead · 3 primary nav dead · 4 whole sections are `#` stubs: legal, blog, and careers all empty.

**36. No Personality / Nothing Sticks** — *w 1.5*
Detect: after reading the whole page you could swap in a competitor's name and change nothing; no owned voice, no specific opinion, no artifact of a human who cares, no visual moment you'd remember tomorrow.
Anchors: 0 something clearly belongs to this team · 1 mostly generic with a few tells · 2 completely interchangeable · 3 no opinion, no story, no artifact · 4 a competitor's name could be dropped in with zero other edits.

---

## Roll-up discipline

- Score all 36 before computing. A blank is not a 0.
- Fill `{{CALC_ROWS}}` with one row per group — the template's columns are **Σ weight / Σ contribution / share of total** (its own total row and band are already rendered). Point counts (A 16, B 3, C 4, D 8, E 5) are for reference only; never print them as the weight column (Σw: 17.0 / 4.0 / 3.0 / 9.0 / 4.5).
- Re-check the anti-gaming table in `SKILL.md` §3 before publishing.
