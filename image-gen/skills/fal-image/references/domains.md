# Domains — fal-image

The 9 image domains: how to detect them from a user request, and the vocabulary library to draw from when constructing the prompt for each. Modifier libraries adopted verbatim from banana-claude (model-agnostic vocabulary).

---

## How domain detection works

The orchestrator reads the user's request, scans for **detection cues** (below), and picks the highest-confidence domain. If two or more domains tie above 60% confidence, it asks a single disambiguation MCQ. If no domain matches above 60%, it asks a disambiguation MCQ with the top-3 candidates plus "something else."

Detection runs once per request, before any MCQs. Domain choice drives:
- Which preset gets loaded (`presets/<domain>.preset.md`)
- Which modifier library the brief-constructor draws from (this file's matching section)
- The default aspect ratio and styling register

---

## Domain index

| Domain | Type | Best for |
|---|---|---|
| **Cinema** | Photographic | Movie stills, narrative scenes, story-driven imagery, atmosphere |
| **Product** | Photographic | Commercial product shots, packaging, e-commerce, hero imagery |
| **Portrait** | Photographic | Headshots, character studies, single-subject people imagery |
| **Editorial** | Photographic | Fashion, lifestyle, magazine spreads, layered styling |
| **UI / Web** | Structural | Interface mockups, app screens, component design |
| **Logo** | Structural | Brand marks, lettermarks, monograms, logotype |
| **Landscape** | Photographic | Environmental scenes, nature, vistas, atmospheric depth |
| **Abstract** | Atmospheric | Geometry, texture, color as primary language, non-representational |
| **Infographic** | Structural | Data visualization, hierarchy, structured information |

---

## Cinema

### Detection cues

**Strong signals** (high confidence):
- "movie still", "film still", "cinematic", "cinema", "cinematography"
- "scene from a film", "shot from a movie"
- Specific film/director references ("Wes Anderson style", "Blade Runner aesthetic")
- "narrative shot", "story shot"

**Medium signals**:
- Description of dramatic action with story implication ("a detective discovering a clue", "the moment before the door opens")
- Time-of-day specificity with mood ("late night neon", "blue hour stillness")
- Atmospheric / weather emphasis ("rain-slicked street", "fog rolling in")

**Weak signals**:
- "hero shot" without product context
- "epic" / "dramatic" framing language

### Modifier library

- **Camera bodies:** RED V-Raptor · ARRI Alexa 65 · Sony Venice 2 · Blackmagic URSA · ARRI Alexa Mini LF
- **Lenses:** Cooke S7/i · Zeiss Supreme Prime · Atlas Orion anamorphic · Master Prime · Leica Summilux-C
- **Film stocks:** Kodak Vision3 500T (tungsten) · Kodak Vision3 250D (daylight) · Fuji Eterna Vivid · Fuji Eterna 250D · Kodak Portra 400 (warm nostalgic)
- **Lighting setups:** three-point · chiaroscuro · Rembrandt · split lighting · butterfly · rim/backlight · motivated practical sources · single-source key
- **Shot types:** establishing wide · medium close-up · extreme close-up · Dutch angle · overhead crane · Steadicam tracking · locked-off lockdown · slow push-in
- **Color grading:** teal-and-orange · desaturated cold · warm vintage · high-contrast noir · bleach bypass · cross-process · warm amber-magenta · cool steel-blue
- **Director / film references:** Roger Deakins cinematography · Emmanuel Lubezki natural-light · Christopher Doyle handheld · Edward Lachman late-analog · classic 1970s thriller register · 1990s indie warmth · 2010s prestige drama

---

## Product

### Detection cues

**Strong signals**:
- "product shot", "product photography", "packshot"
- "hero image for [a product]", "ad for [a product]"
- Named brand or product type ("AirPods", "headphones", "shoe", "bottle")
- "e-commerce", "catalog", "merchandise"
- "advertising campaign"

**Medium signals**:
- "commercial photography"
- "studio shot"
- Description of an object as the central subject without a person

**Weak signals**:
- "hero image" with website/landing-page context
- "marketing visual"

### Modifier library

- **Surfaces:** polished marble (Carrara, Calacatta) · brushed concrete · raw linen · acrylic riser · gradient sweep · matte black · weathered oak · pristine cream paper · brushed aluminum
- **Lighting:** softbox diffused (key) · hard key with white-card fill · rim separation · tent lighting · light painting · gradient backlight · single directional with negative fill
- **Angles:** 45-degree hero · flat lay · three-quarter · straight-on · worm's-eye · overhead · slight low-angle hero
- **Style references:** Apple product photography · Aesop minimal · Bang & Olufsen clean · luxury cosmetics editorial · Wallpaper* design feature · Bon Appétit food editorial · Kinfolk lifestyle · Apartamento interior register
- **Reflections / shadows:** sharp drop-shadow falling away · soft penumbra · reflected highlight on rim · subsurface glow on translucent material · brushed metal catching specular highlight
- **Props policy spectrum:** product alone (zero props) · contextual single prop (ingredient, accessory) · environmental (in use, hand holding, on counter) · styled scene (multiple props, full lifestyle)

---

## Portrait

### Detection cues

**Strong signals**:
- "portrait", "headshot", "self-portrait"
- "portrait of [a person]", "headshot of [a person]"
- Person named or described as the subject with no implied product or scene focus
- "character study", "face shot"

**Medium signals**:
- Single-person subject with detailed physical description
- Emphasis on facial features, expression, gaze
- "studio portrait", "natural-light portrait"

**Weak signals**:
- A scene with one named person and minimal environment

### Modifier library

- **Focal lengths:** 50mm (environmental portrait) · 85mm (classic portrait, mild compression) · 105mm (fashion portrait, strong compression) · 135mm (telephoto compression) · 200mm (heavy compression, beauty)
- **Apertures:** f/1.4 (dreamy bokeh, eyes-only sharp) · f/2.8 (subject-sharp, soft background) · f/4 (subject + immediate context sharp) · f/5.6 (environmental context retained)
- **Lighting styles:** Rembrandt (triangular cheek light) · butterfly (Hollywood beauty) · split (dramatic 50/50) · loop (soft natural) · clamshell (beauty fashion) · single-source window light · soft directional natural with subtle fill
- **Pose language:** candid mid-gesture · direct-to-camera confrontational · profile silhouette · over-shoulder glance · contemplative downward gaze · hands engaged in activity · environmental engagement
- **Skin / texture handling:** freckles visible · pores at macro distance · catch light in eyes · subsurface scattering at thin tissue (earlobes, nose tip) · natural facial micro-texture · flyaway hairs · single bead of perspiration
- **Wardrobe register:** editorial styled · documentary natural · workwear authentic · period-specific costume · contemporary minimal · studio-neutral

---

## Editorial

### Detection cues

**Strong signals**:
- "editorial", "magazine", "fashion editorial"
- Specific publication referenced ("Vogue", "Harper's Bazaar", "GQ", "Kinfolk")
- "fashion shoot", "lifestyle shoot"
- "spread", "feature spread"
- Layered styling implied ("dressed in layers", "head-to-toe styling")

**Medium signals**:
- Person + clothing as joint focus (not just headshot, not just product)
- "story-driven", "narrative styling"
- Location described as part of the styling intent

**Weak signals**:
- Glossy/aspirational framing
- Multiple subjects with coordinated styling

### Modifier library

- **Publication references:** Vogue Italia · Harper's Bazaar · GQ · National Geographic · Kinfolk · The Gentlewoman · Apartamento · Wallpaper* · Vanity Fair · WIRED · i-D Magazine · AnOther Magazine · The New York Times Magazine
- **Styling notes:** layered textures · statement accessories · monochromatic palette · contrast patterns · period-specific styling · deliberate disheveled · architectural silhouettes · texture-on-texture
- **Locations:** marble staircase · rooftop at golden hour · industrial loft · desert dunes · neon-lit alley · brutalist concrete · pristine modernist interior · weathered seaside · vintage diner · vacant theater
- **Pose language:** power stance · relaxed editorial lean · movement blur · fabric in wind · candid laughter · group-staged tableau · architectural pose (figure echoing the building lines)
- **Crop styles:** full-bleed edge-to-edge · framed within negative space · asymmetric tight crop · classical centered composition · dynamic Dutch tilt
- **Era / styling decade:** late-90s grunge · early-2000s minimalism · 1970s warm · 1960s mod · 2010s normcore · contemporary streetwear · timeless classic

---

## UI / Web

### Detection cues

**Strong signals**:
- "UI mockup", "interface design", "app screen", "dashboard"
- "landing page", "homepage", "web design"
- "mobile app screen", "iPhone screenshot", "Android UI"
- "wireframe", "component", "design system"

**Medium signals**:
- Description of interface elements (buttons, cards, navigation)
- Reference to design styles (flat, glassmorphic, neumorphic)
- "for a SaaS product", "for an app"

**Weak signals**:
- Reference to specific apps or design tools

### Modifier library

- **Styles:** flat vector · isometric 3D · line art · glassmorphism · neumorphism · material design · skeuomorphism · brutalism · neo-brutalism · soft 3D · clay illustration
- **Color systems:** specify exact hex (e.g., "deep navy #0F1A2E to indigo #1E1B4B gradient") · descriptive palette ("cool blues", "warm cream tones") · brand-color anchored
- **Sizing:** 2x retina target · exact pixel dimensions ("1440 × 900 desktop frame") · responsive breakpoint specified ("mobile 375 × 812", "desktop 1920 × 1080")
- **Backgrounds:** transparent (request solid white, post-process to alpha) · solid color · gradient · subtle texture (paper, noise) · environmental (in-use shot of a screen)
- **Component vocabulary:** card with elevation · sticky top navigation · floating action button · modal overlay · data table · sidebar navigation · toast notification · skeleton loader · progressive disclosure
- **State coverage:** default · hover · focus · active · disabled · loading · error · empty
- **Iconography style:** outlined single-stroke · filled solid · duotone · 3D extruded · hand-drawn · geometric

---

## Logo

### Detection cues

**Strong signals**:
- "logo", "logomark", "wordmark", "lettermark", "monogram", "brand mark"
- "logo for [name]", "design a logo"
- "brand identity"

**Medium signals**:
- Description of a name or short phrase needing visual identity
- "icon for a brand", "symbol for a company"

**Weak signals**:
- "minimal mark", "simple symbol"

### Modifier library

- **Construction styles:** geometric primitives · golden-ratio grid · orthogonal grid · negative-space construction · letter-mashup · symmetric reflection · asymmetric balance
- **Typography styles:** bold sans-serif · elegant serif · custom lettermark · modern geometric · humanist · slab serif · script flourish · monospaced technical
- **Color rules:** max 2-3 colors · works in monochrome · high contrast · single accent color · complementary pair · analogous trio
- **Backgrounds:** transparent (always specify) · solid white (then post-process to alpha) · solid black for monochrome viability test
- **Shape primitives:** circle · square · rounded square · hexagon · triangle · organic blob · letterform interlock · negative-space arrow
- **Reference brands:** Pentagram-designed · Saul Bass-era simplicity · contemporary tech logo (Stripe, Linear) · luxury heritage (Hermès, Chanel) · indie boutique
- **Output requirement:** must work in monochrome at 16px favicon size — if the design fails this test, simplify

---

## Landscape

### Detection cues

**Strong signals**:
- "landscape", "vista", "panorama", "scenery"
- Named geographic location ("Yosemite", "Patagonia", "Scottish Highlands")
- "nature photography", "outdoor", "wilderness"
- "mountain", "valley", "coast", "desert" as central subject

**Medium signals**:
- Time of day with environmental focus ("sunrise over the lake", "golden hour in the canyon")
- Weather as primary atmospheric driver
- Wide horizon implied

**Weak signals**:
- Outdoor scene with no human subject focus

### Modifier library

- **Depth-layer composition:** foreground interest · midground subject · background atmosphere · three-layer depth · single-plane silhouette
- **Atmospherics:** fog · mist · haze · volumetric light rays · dust particles · drifting smoke · low cloud · alpenglow · heat shimmer
- **Time of day:** blue hour (pre-dawn / post-sunset) · golden hour · magic hour · midnight blue · midday harsh · twilight transition
- **Weather:** dramatic storm clouds · clearing after rain · snow-covered · sun-dappled · windswept · still glassy water · breaking wave · drifting fog
- **Camera bodies / lenses:** Sony A7R IV with 24-70mm GM · Hasselblad H6D for landscape · Phase One IQ4 · 14mm ultra-wide · 70-200mm compression for distant peaks · 24mm tilt-shift
- **Composition styles:** rule of thirds · leading lines · symmetrical reflection · centered subject · diagonal flow · framing through foreground element
- **Color palette / grading:** natural unsaturated · slightly warm enhancement · cool blue dominance · earthy ochres · monochrome conversion · split-tone (cool shadows, warm highlights)
- **Season:** late autumn (gold and rust) · winter sparse · spring fresh · summer lush · transitional

---

## Abstract

### Detection cues

**Strong signals**:
- "abstract", "non-representational"
- "geometric pattern", "fractal", "generative art"
- "texture study", "color field"

**Medium signals**:
- Description focused on shape, color, texture without a recognizable subject
- "mood piece", "atmosphere"
- "background art", "wallpaper" (in the decorative sense)

**Weak signals**:
- Avant-garde or experimental framing

### Modifier library

- **Geometry:** fractals · voronoi tessellation · spirals · fibonacci sequence · organic flow · crystalline structures · cellular automata · L-systems
- **Textures:** marble veining · fluid dynamics · smoke wisps · ink diffusion · watercolor bleed · paper grain · linen weave · brushed metal
- **Color palettes:** analogous harmony · complementary clash · monochromatic gradient · neon-on-black · earth tones · pastel chromatic · split-complementary
- **Style references:** generative art (Casey Reas, Ben Fry) · data visualization art · glitch aesthetic · procedural · macro photography of materials · Bauhaus geometric · suprematism · op art (Bridget Riley)
- **Density / complexity spectrum:** sparse minimal · balanced · dense layered · maximalist
- **Movement / flow direction:** radial outward · linear cascade · centripetal · turbulent chaos · slow drift · explosive radial
- **Symmetry rule:** radial · bilateral · asymmetric balance · broken symmetry · perfect mirror

---

## Infographic

### Detection cues

**Strong signals**:
- "infographic", "data visualization", "diagram"
- "chart", "graph", "comparison"
- "explainer graphic", "informational graphic"
- "timeline", "flowchart"

**Medium signals**:
- Mention of specific data points or quantities
- "show how X works", "visualize the process"
- Reference to dashboards or reports

**Weak signals**:
- Educational or instructional framing

### Modifier library

- **Layout styles:** modular sections · clear visual hierarchy · bento grid · vertical flow top-to-bottom · horizontal timeline · radial / hub-and-spoke · matrix grid
- **Hierarchy:** large hero number / heading · secondary subhead · body data labels · footnote attribution
- **Text rendering:** quote exact text · descriptive font characteristic ("bold geometric sans-serif") · specify size ratio (heading 4× body)
- **Data viz primitives:** bar charts (horizontal / vertical) · pie charts · flow diagrams · timelines · comparison tables · sankey flows · scatter plots · line charts · stacked area
- **Color palette:** high-contrast accessible · 4-color max · brand-anchored · sequential gradient (single hue) · diverging diverging gradient (two hues from neutral midpoint)
- **Iconography:** geometric line-art (single-stroke) · filled solid · duotone · isometric 3D
- **Density spectrum:** sparse focused (1-3 data points) · balanced (4-7) · dense reference card (8+)
- **Annotation style:** call-out arrows · numbered markers · dotted-line connectors · inline labels · footnote indices

---

## Fallback rule — when no domain matches

If domain confidence is below 60% for all 9 domains, OR two+ domains tie above 60%, the orchestrator asks **one disambiguation MCQ** before continuing:

```
Which register fits best?
   a) [top candidate domain] — [one-line rationale]
   b) [second candidate domain] — [one-line rationale]
   c) [third candidate domain] — [one-line rationale]
   d) something different (describe)
```

Behavior:

- If user picks (a/b/c), use that domain. Proceed normally.
- If user picks (d) and writes free-text, set domain to **closest of the 9** (whichever the orchestrator judges nearest), inject the user's free-text as a **style override** in the brief-constructor's input, and flag the sidecar with `domain_inferred: true` in `params`.
- The disambiguation MCQ counts toward the 2–3 MCQ cap. After it, only 1–2 more MCQs allowed.

This keeps the 9-domain system intact while admitting the long tail (e.g., "comic book panel", "anime keyframe", "stained glass window") without forcing the orchestrator to invent a new domain.
