# Prompt Engineering — fal-image

The construction system used by `fal-image` to turn a user request into a production prompt for fal.ai image models. Read this before constructing any prompt.

---

## The 5-component formula

Every prompt is built from five components woven into narrative prose:

> **Subject → Action → Location/Context → Composition → Style (lighting included)**

| # | Component | What it captures | Example fragment |
|---|---|---|---|
| 1 | **Subject** | Who or what — physical specifics (age, build, material, species, expression). Never just "a person" or "a product." | "a weathered Japanese ceramicist in his seventies, sun-etched wrinkles, calloused hands" |
| 2 | **Action** | What the subject is doing — strong present-tense verb or visible state. If no action, describe pose or arrangement. | "leaning forward in concentration, smoothing the rim with a wet thumb" |
| 3 | **Location / Context** | Where + when + atmosphere. Include environmental details, time of day, weather, mood. | "inside a wood-fired anagama kiln workshop, late afternoon light through rice paper screens" |
| 4 | **Composition** | Camera perspective, framing, spatial relationship, focal length, aperture. | "intimate close-up from slightly below eye level, shot on Hasselblad H6D-100c with 80mm lens at f/2.8, shallow depth of field" |
| 5 | **Style (with lighting)** | Visual register, medium, lighting setup, real-world references (cameras, film stock, photographers, publications, art movements). | "warm directional Rembrandt lighting, Magnum Photos documentary register, Dorothea Lange editorial restraint" |

### Weight distribution

| Component | Weight | Includes |
|---|---:|---|
| Subject | 30% | Age, ethnicity, build, hair, eyes, expression, material, species |
| Action | 10% | Movement, pose, gesture, interaction, state |
| Context | 15% | Location + time + weather + atmosphere |
| Composition | 10% | Shot type, angle, framing, focal length, aperture |
| Lighting | 10% | Quality, direction, color temperature, shadows, motivated sources |
| Style | 25% | Medium, brand/camera names, textures, publications, art movements, color grading |

Lighting is technically inside Style but gets its own row because it's the single highest-leverage detail — bad lighting language tanks any prompt regardless of subject quality.

---

## Hard rules

These are non-negotiable. Violating any of them degrades output quality on every fal image model tested.

1. **Narrative prose, never keyword lists.** Write paragraphs, not comma-separated tags. The model reads natural language better than tag soup.

2. **100–200 words standard.** 20–60 for quick drafts, 200–300 for complex professional briefs. Validate per fal model — FLUX prefers shorter, Imagen accepts longer. Don't pad just to hit the count.

3. **Critical specifics in the first third.** The model attends most to the opening. Bury "MUST contain exactly three figures" at the end and the model will ignore it. Lead with the must-haves.

4. **Real-world anchors over generic descriptors.** Name real cameras (Sony A7R IV, Canon EOS R5, Hasselblad H6D), real lenses with apertures (85mm f/1.4, 24mm f/1.4 Sigma Art), real brands (Tom Ford suit, Aesop bottle, B&O speaker), real publications (Vanity Fair, National Geographic, Wallpaper*). These are training-data clusters the model has strong representations of.

5. **ALL CAPS for hard constraints.** When something MUST be true, write it in caps: "MUST contain exactly three figures" · "NEVER include any text" · "ENGLISH only on the sign". Lowercase versions get ignored.

6. **Reframe negatives as positives.** No fal model handles "no X" reliably. Rewrite as the inverse:
   - "no blur" → "tack-sharp, in-focus, crisp detail"
   - "no people" → "uninhabited, deserted, empty"
   - "not dark" → "brightly lit, high-key, bright daylight"
   - "no logos" → "clean, unbranded, no commercial markings"

7. **Write the scene, not the concept.** Anti-pattern: *"A dark-themed Instagram ad showing modern professionalism for a SaaS company."* That describes the *intent*, not the *image*. The image renders nothing because there's nothing visual to render. Rewrite as scene: *"A solo founder at 11pm, blue laptop glow on tired face, single desk lamp pooling on a worn leather notebook, minimalist studio loft, raindrops on industrial windows, shot on Sony A7R IV at 50mm f/1.8, deep teal shadows with warm amber highlights, WIRED feature register."*

8. **Micro-details over adjectives.** "sweat droplets on collarbones" beats "sweaty." "baby hairs stuck to the neck" beats "messy hair." "subsurface scattering at the earlobe" beats "realistic skin." Specificity is the most underused lever in image prompting.

---

## Anchor language over generic quality words

Generic quality terms ("8K", "masterpiece", "ultra-detailed", "photorealistic", "trending on artstation", "best quality", "award winning") carry weak training-data signal. They pull toward stock-photo aesthetics. Replace them with concrete real-world anchors — camera bodies, lenses, film stocks, photographers, publications, art movements — which carry strong, distinct representations the model can render.

| Generic phrase | Concrete anchor |
|---|---|
| "photorealistic" | "shot on Sony A7R IV with 85mm f/1.4" |
| "8K, ultra-detailed" | a single named publication ("Vanity Fair editorial portrait") |
| "masterpiece, award-winning" | a named award or publication ("World Press Photo documentary", "Pulitzer cover") |
| "highly detailed" | one specific micro-detail ("subsurface scattering at the earlobe") |
| "trending on artstation" | a named art movement or studio ("Bauhaus poster", "Pentagram editorial") |

---

## Prestigious context anchors

Replace generic quality words with **specific publication or award references**. These are training-data clusters the model has strong, distinct representations of.

> Pulitzer Prize-winning cover photograph · Vanity Fair editorial portrait · National Geographic cover story · WIRED magazine feature spread · Architectural Digest interior · Magnum Photos documentary · Wallpaper* design editorial · Bon Appétit feature spread · Kinfolk magazine register · The Gentlewoman portrait · Vogue Italia fashion editorial · Harper's Bazaar fashion shoot · GQ portraiture · World Press Photo documentary · IPA International Photography Award

Rule of thumb: pick the anchor that matches the *register* you want. Vogue Italia is fashion-editorial. Magnum is documentary. Architectural Digest is interior/lifestyle. Wallpaper* is design/product.

---

## Text-in-image rules

Text rendering is the most fragile part of any image model. Follow these rules tightly.

| Rule | Detail |
|---|---|
| **≤25 characters per text element** | Past 25, character-level errors compound. For longer text, generate the visual without text and composite later (or use multiple short labels). |
| **Quote the exact text** | Always wrap target text in quotation marks: `with the text "OPEN DAILY"` not `with text saying open daily`. |
| **Describe font characteristics, not names** | "bold condensed sans-serif" works. "Helvetica Bold" does not — model has no font library. Use: `bold geometric sans-serif`, `elegant serif with small terminals`, `condensed all-caps headline`, `humanist italic`. |
| **Specify placement** | "centered at the bottom third" · "upper left corner" · "across the middle horizontal axis" · "tucked into the lower-right margin." Without placement, text floats randomly. |
| **High contrast** | Light text on dark, dark on light. Specify: `cream serif text on charcoal background`. |
| **Limit to 2–3 distinct phrases** | More than 3 separate text elements and the model starts hallucinating extra text. |
| **Text-first hack** | If text is critical, mention it conversationally before the visual ask: *"A poster reading 'OPEN 24 HOURS' in bold red typography. The poster is mounted on the door of a vintage diner..."* — anchoring the text early gives it priority. |

---

## Anti-patterns to avoid

| Anti-pattern | Example | Why it fails | Fix |
|---|---|---|---|
| **Writing the concept** | "A dark-themed Instagram ad about productivity." | Describes intent, not image. Nothing to render. | Write the literal scene that conveys the concept. |
| **Vague adjective stacks** | "Modern, clean, professional, sleek, minimal." | Adjectives without nouns produce nothing. | Replace with specific objects, materials, lighting, composition. |
| **Describing viewer feelings** | "An image that makes you feel nostalgic." | Model can't render emotion directly — it renders objects that evoke emotion. | Describe the *objects* that produce the feeling: warm tungsten light, faded film grain, late-afternoon shadows. |
| **Keyword stuffing** | "Beautiful, gorgeous, stunning, breathtaking, amazing, masterpiece, 8K, ultra-detailed." | Stack of redundant quality words. | One specific publication anchor. |
| **Tag-list format** | "woman, red dress, beach, sunset, beautiful, cinematic" | Comma-separated lists are MidJourney-era. fal models prefer prose. | Rewrite as narrative paragraph. |
| **Burying critical details** | "[200 words of fluff]... and she must be holding a cat." | Last-third details get deprioritized. | Move critical specs to first third. |
| **Mixing register mid-prompt** | "Cinematic editorial fashion shot, also looks like a children's book illustration." | Conflicting style anchors confuse the model. | Pick one register and commit. |

---

## Proven prompt templates

Five starting-point patterns. Each is a *skeleton* — fill the bracketed slots with specifics. Real prompts deviate from the skeleton; these are scaffolding.

### Template 1 — Photorealistic / editorial portrait

```
[Subject: age + ethnicity + build + features], [wearing description with brand/material],
[present-tense action verb] in [specific location + time of day]. [Micro-detail: skin/hair/sweat/texture].
Captured with [camera body + lens + aperture], [lighting description with direction and quality].
[Publication anchor: "Vanity Fair editorial" / "Magnum documentary" / "Pulitzer cover photograph"].
```

Example:
> A 70-year-old Japanese ceramicist with deep sun-etched wrinkles and calloused hands, wearing an indigo cotton noragi over a worn linen apron, leaning forward in deep concentration as he smooths the rim of a tea bowl with a wet thumb, inside a traditional wood-fired anagama kiln workshop with late afternoon light streaming through rice paper screens. Visible clay dust on his forearms, single bead of sweat at the temple, ash-stained fingernails. Shot on Hasselblad H6D-100c with 80mm Zeiss lens at f/2.8, intimate close-up from slightly below eye level, shallow depth of field with the kiln glowing softly out of focus behind him, warm directional Rembrandt lighting from a single window, Magnum Photos documentary register.

### Template 2 — Product / commercial

```
[Product with brand name] [dynamic visual element: condensation, splash, glow, particles],
[product detail: "logo prominently displayed"], on [surface description] with [supporting prop].
[Lighting setup with direction and quality]. [Reflection or shadow detail].
Commercial photography for [publication or campaign register].
```

Example:
> A polished black B&O Beoplay H95 over-ear headphone resting at a forty-five-degree hero angle on a slab of Carrara marble veined with grey, single coil of brushed aluminum reflecting the rim light, Earcup leather catching a soft directional key from camera-right with a hard fill bouncing off a white card, shallow drop-shadow falling away to the lower-left. Commercial photography for a Wallpaper* design feature, true-to-life color, no Instagram filtering.

### Template 3 — Illustrated / stylized

```
A [art style: flat vector / isometric 3D / line art / watercolor] [format: illustration / poster / spot art]
of [subject with character detail], featuring [distinctive characteristic] with [color palette].
[Line style] and [shading technique]. Background is [description].
[Mood / atmospheric note].
```

Example:
> A flat vector illustration of a coffee shop interior at golden hour, featuring three baristas in cream aprons working a brass espresso machine with a copper steam wand, color palette restricted to deep navy, cream, brass, and a single accent of brick red. Bold outlines with selective highlights, no gradients, geometric shapes with rounded corners. Background is a warm wood-paneled wall with a single hanging plant and a chalkboard menu. Cozy, deliberate, Kinfolk magazine register translated to vector.

### Template 4 — Text-heavy asset

```
A [asset type: poster / sign / book cover / packaging] with the text "[exact text under 25 chars]"
in [descriptive font characteristic], [placement and sizing within the frame].
[Layout structure description]. [Color scheme with hex or descriptive palette].
[Surrounding visual context that supports the text].
```

Example:
> A movie-poster-style image with the text "MIDNIGHT RUN" in bold condensed serif, all-caps, set across the lower third of the frame in cream against a deep crimson backdrop. Layout follows a 70/30 split — top two-thirds image, bottom third text. The image above the text shows a lone figure walking down a rain-slicked alley at 2am, neon signs in the distance reflecting in puddles, single headlight cutting through fog. Color palette: deep crimson, cream, neon teal, asphalt black. Cinematic 1970s thriller poster register.

### Template 5 — Infographic

```
A [layout style: modular bento grid / vertical flow / timeline] infographic about [topic],
with [N] data points displayed as [data viz type]. Hierarchy: [hierarchy description].
The text "[heading text under 25 chars]" reads at the top in [font characteristic].
[Color palette: max 4 colors with hex if known]. [Iconography style].
Background is [description].
```

Example:
> A modular bento-grid infographic about Q4 revenue by region, with 5 data points displayed as horizontal bar charts of varying lengths. Hierarchy: large heading at top, secondary subheading, then 5 data rows with bars right-aligned. The text "Q4 BY REGION" reads at the top in bold geometric sans-serif. Color palette restricted to deep navy (#0F1A2E), cream (#F4EFE6), brass (#B8853E), and accent magenta (#D14D72). Geometric line-art icons, single-stroke. Background is a clean cream surface with a faint hairline grid. Editorial register, Pentagram studio aesthetic.

---

## Common mistakes (10-item checklist)

Before sending any prompt, verify it does NOT have any of these:

- [ ] **1. Keyword stuffing** — comma-separated quality adjectives ("beautiful, stunning, masterpiece, 8K")
- [ ] **2. Tag-list format** — Midjourney-era comma lists with no prose connective tissue
- [ ] **3. Missing lighting** — every prompt should specify lighting direction, quality, color temperature
- [ ] **4. No composition direction** — angle, framing, focal length, aperture should be spelled out
- [ ] **5. Vague style** — "modern" / "clean" / "professional" without anchors. Use a publication name.
- [ ] **6. Aspect ratio mismatch** — prompt describes a wide cinematic shot but request asks for a square. Either reword or change ratio.
- [ ] **7. Overlong prompts** — past ~250 words, returns diminish. Cut filler.
- [ ] **8. Text >25 chars** — break into multiple short text elements or composite later.
- [ ] **9. Burying key details** — critical specs after the first third get deprioritized.
- [ ] **10. Not iterating** — the first generation is rarely the final. Plan to iterate, refine, regenerate.

---

## Adapting prompts from other ecosystems

When users paste prompts copied from Midjourney, Stable Diffusion, or DALL-E databases:

| Source convention | Convert to |
|---|---|
| `--ar 16:9 --v 6 --style raw --chaos 30` | Strip flags. Move aspect ratio to the API parameter. |
| `(masterpiece:1.5), (best quality:1.4)` | Strip weighted-prompt syntax. Use prose. |
| `(woman:1.3), (red dress:1.2), beach, sunset` | Rewrite as narrative paragraph. |
| `8K, masterpiece, ultra-detailed` | Replace with a publication anchor and a specific camera/lens spec. |
| `shot on Hasselblad, 85mm f/1.4` | **Keep this** — real camera/lens specs are universal and work everywhere. |

---

## Character consistency (multi-image work)

When generating multiple images of the same character/subject across a session:

- **Repeat 2–3 anchor identifiers verbatim** across every prompt. ("a 35-year-old woman with shoulder-length auburn hair, freckles across the nose bridge, and a single dimple on her left cheek.")
- **Use named references** — "Maya" or "the engineer" — and pin those names in subsequent prompts.
- **Hold the camera/lens specs constant** across the series unless deliberately changing perspective.
- **Hold the lighting register constant** for visual continuity. Changing only what should change minimizes drift.
- **Pass a character reference image** when the model supports it (Nano Banana Pro, Flux 2 [flex], Flux Kontext). Reference-image conditioning beats prose every time for identity lock — text alone cannot reliably reproduce a face across rolls.

---

## Per-model prompt-style notes

Different models reward different opening orders and lengths. Adapt the construction to the target_model the orchestrator passes you.

| Model | Opening | Length sweet spot | Notes |
|---|---|---|---|
| **Nano Banana Pro** | Subject + scene context, conversational | 80–200 words | World-aware — can name films, designers, magazines. Up to 14 reference images. |
| **Flux 2 [pro]** | Subject-first, front-loaded | 80–200 words | HEX colors directly in prose. `(weight:1.5)` syntax ignored. |
| **Flux Kontext [pro]** | Imperative edit instruction | ≤512 tokens | Name subjects, never use pronouns. Quote any literal text edits. |
| **Recraft V4 Pro** | Describe the artifact itself | short, direct | Vector-friendly: "flat", "geometric", "two-color", "scalable". |
| **Ideogram V3** | One-line scene summary, then quoted text | ~150 words | Describe typeface ("bold sans-serif"), never name fonts. Quote the literal text. |

Across all models: paragraph prose only, never JSON, no negative prompts, no `(word:1.5)` weighting. Aspect ratio is always a parameter, not prose.

---

## Putting it all together — full example walkthrough

User request: *"hero image for my coffee shop website"*

Detected domain: **Product** (commercial register, hero composition implied).

Preset values to fold in (image/product preset):
- Default aspect ratio: 4:3
- Surface / background: contextual minimal — material complements the product, never competes
- Lighting setup: studio quality — softbox key, hard fill, rim separation
- Angle preference: 45° hero
- Focal length: 85mm
- Color treatment: true-to-life

5-component construction:

| Slot | Filled with |
|---|---|
| **Subject** | A weathered ceramic mug of single-origin espresso, slight chip on the rim, the espresso showing a marbled crema |
| **Action** | Resting on a worn oak counter, single rising wisp of steam |
| **Location/Context** | Inside a small-batch roastery at mid-morning, warm soft daylight streaming from tall industrial windows |
| **Composition** | Forty-five-degree hero angle, intimate close-up, shot on Hasselblad H6D-100c with 80mm lens at f/2.8, shallow depth of field with the roastery softly out of focus |
| **Style** | Warm directional natural light with subtle window fill, true-to-life color, Kinfolk magazine editorial register |

Final prompt (~140 words):

> A weathered ceramic espresso mug with a slight chip at the rim, single shot of single-origin espresso showing a marbled tiger-stripe crema, resting on a worn oak counter inside a small-batch roastery at mid-morning. Single wisp of steam rising vertically before drifting toward camera-left. Tall industrial windows behind cast soft warm daylight across the counter, the roastery's brass espresso machine and copper kettle softly out of focus in the background. Shot at a forty-five-degree hero angle, intimate close-up framing on Hasselblad H6D-100c with 80mm Zeiss lens at f/2.8, shallow depth of field. Warm directional natural light from camera-right with a subtle white-card fill, brass highlights catching on the rim, true-to-life color with no Instagram filtering. Kinfolk magazine editorial register.

This is a generation-ready prompt. It has all 5 slots filled, real camera/lens specs, narrative prose, micro-details (chipped rim, marbled crema, single wisp, tiger-stripe), and a publication anchor.
