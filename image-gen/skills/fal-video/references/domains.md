# Domains — fal-video

The 6 video domains: how to detect them from a user request, and the vocabulary library to draw from when constructing the prompt for each. UI / Logo / Infographic are excluded because they don't translate meaningfully into motion.

---

## How domain detection works

The orchestrator reads the user's request, scans for **detection cues** (below), and picks the highest-confidence domain. If two or more domains tie above 60% confidence, it asks a single disambiguation MCQ. If no domain matches above 60%, it asks a disambiguation MCQ with the top candidates plus "something else."

Detection runs once per request, before any MCQs. Domain choice drives:
- Which preset gets loaded (`presets/<domain>.preset.md`)
- Which modifier library the brief-constructor draws from (this file's matching section)
- The default aspect ratio, fps, and motion register

---

## Domain index

| Domain | Type | Best for |
|---|---|---|
| **Cinema** | Photographic | Movie-still motion, narrative scenes, story-driven beats, atmosphere |
| **Product** | Photographic | Commercial product motion, packaging reveals, e-commerce hero clips |
| **Portrait** | Photographic | Single-subject motion portraits, character beats, breath-held stillness |
| **Editorial** | Photographic | Fashion / lifestyle motion, magazine register, layered styling |
| **Landscape** | Photographic | Environmental motion, time-lapse, drone reveals, atmospheric drift |
| **Abstract** | Atmospheric | Geometry, texture, color, generative motion, loop-friendly clips |

---

## Cinema

### Detection cues

**Strong signals** (high confidence):
- "cinematic clip", "movie scene", "film scene", "narrative shot"
- "scene from a film", "shot from a movie"
- Specific film/director references ("Wes Anderson style", "Blade Runner aesthetic")
- "story shot", "narrative motion"

**Medium signals**:
- Description of dramatic action with story implication ("a detective discovering a clue", "the moment before the door opens")
- Time-of-day specificity with mood ("late night neon", "blue hour stillness")
- Atmospheric / weather emphasis ("rain-slicked street", "fog rolling in")

**Weak signals**:
- "hero shot" without product context
- "dramatic" framing language with motion implication

### Modifier library

- **Camera bodies:** ARRI Alexa Mini LF · ARRI Alexa 65 · Sony Venice 2 · RED V-Raptor · Blackmagic URSA
- **Lenses:** Cooke S7/i · Zeiss Supreme Prime · Atlas Orion anamorphic · Master Prime · Leica Summilux-C
- **Film stocks:** Kodak Vision3 500T (tungsten) · Kodak Vision3 250D (daylight) · Fuji Eterna Vivid · Fuji Eterna 250D · Kodak Portra 400 (warm nostalgic)
- **Lighting setups:** three-point · chiaroscuro · Rembrandt · split lighting · butterfly · rim/backlight · motivated practical sources · single-source key
- **Shot types:** establishing wide · medium close-up · extreme close-up · Dutch angle · overhead · slow push-in · locked-off lockdown
- **Color grading:** teal-and-orange · desaturated cold · warm vintage · high-contrast noir · bleach bypass · cross-process · warm amber-magenta · cool steel-blue
- **Cinematographer / director references:** Roger Deakins · Emmanuel Lubezki · Christopher Doyle · Edward Lachman · classic 1970s thriller register · 1990s indie warmth · 2010s prestige drama
- **Camera moves:** slow push-in · slow pull-out · steadicam · handheld with breath · locked-off · locked-off + rack focus
- **Pacing:** slow burn · steady drift · accelerating · breath-held
- **Loop suitability:** rare — Cinema clips are typically narrative beats, not loops

---

## Product

### Detection cues

**Strong signals**:
- "product video", "product clip", "product motion"
- "hero clip for [a product]", "ad for [a product]", "product reveal"
- Named brand or product type ("AirPods", "headphones", "shoe", "bottle")
- "e-commerce video", "catalog motion"
- "advertising clip"

**Medium signals**:
- "commercial film"
- "studio motion"
- Description of an object as the central subject without a person
- "looping product clip" / "GIF of a product"

**Weak signals**:
- "hero clip" with website/landing-page context
- "marketing motion"

### Modifier library

- **Surfaces:** polished marble (Carrara, Calacatta) · brushed concrete · raw linen · acrylic riser · gradient sweep · matte black · weathered oak · pristine cream paper · brushed aluminum
- **Lighting:** softbox diffused (key) · hard key with white-card fill · rim separation · tent lighting · gradient backlight · single directional with negative fill
- **Angles:** 45-degree hero · flat lay · three-quarter · straight-on · slight low-angle hero · overhead
- **Style references:** Apple product film · Aesop minimal · Bang & Olufsen clean · luxury cosmetics editorial · Wallpaper* design feature · Bon Appétit food editorial · Kinfolk lifestyle
- **Reflections / shadows:** sharp drop-shadow falling away · soft penumbra · reflected highlight on rim · brushed metal catching specular highlight
- **Props policy spectrum:** product alone · contextual single prop · environmental (in use, hand holding, on counter)
- **Camera moves:** locked-off + rack focus · slow rotate (turntable) · arc orbit · slow drift · locked-off + rack zoom (sparingly)
- **Pacing:** gentle pace · steady drift · pulse-matched
- **Subject motion intensity defaults:** still or subtle (steam wisp, gentle drift on liquid surface, single hair fiber moving)
- **Loop suitability:** yes — Product clips loop well via drift-and-return or pulse-cycle, especially for web hero use

---

## Portrait

### Detection cues

**Strong signals**:
- "portrait video", "motion portrait", "video portrait"
- "video of [a person]" with no implied product or scene focus
- "character beat", "face-shot motion"

**Medium signals**:
- Single-person subject with detailed physical description and an implied still/contemplative beat
- Emphasis on facial features, expression, gaze, breath
- "studio portrait video", "natural-light portrait clip"

**Weak signals**:
- A scene with one named person and minimal environment
- "breath-held" or "contemplative" register cues

### Modifier library

- **Focal lengths:** 50mm (environmental portrait) · 85mm (classic portrait, mild compression) · 105mm (fashion portrait, strong compression) · 135mm (telephoto compression) · 200mm (heavy compression, beauty)
- **Apertures:** f/1.4 (dreamy bokeh, eyes-only sharp) · f/2.8 (subject-sharp, soft background) · f/4 (subject + immediate context sharp) · f/5.6 (environmental context retained)
- **Lighting styles:** Rembrandt · butterfly · split · loop (soft natural) · clamshell · single-source window light · soft directional natural with subtle fill
- **Pose language:** candid mid-gesture · direct-to-camera contemplative · profile silhouette · over-shoulder glance · contemplative downward gaze · hands engaged in activity
- **Skin / texture handling:** freckles visible · pores at macro distance · catch light in eyes · subsurface scattering at thin tissue · natural facial micro-texture · flyaway hairs · single bead of perspiration
- **Wardrobe register:** editorial styled · documentary natural · workwear authentic · period-specific costume · contemporary minimal · studio-neutral
- **Camera moves:** slow push-in · locked-off · handheld with breath
- **Pacing:** breath-held · slow burn · breath-cycle
- **Subject motion intensity defaults:** subtle (breath, micro-gestures, eye blinks)
- **Loop suitability:** sometimes — breath-cycle works well; full motion portraits are typically narrative beats, not loops

---

## Editorial

### Detection cues

**Strong signals**:
- "editorial video", "fashion video", "editorial motion"
- Specific publication referenced ("Vogue", "Harper's Bazaar", "GQ", "Kinfolk")
- "fashion shoot motion", "lifestyle clip"
- Layered styling implied

**Medium signals**:
- Person + clothing as joint focus (not just headshot, not just product)
- "story-driven", "narrative styling"
- Location described as part of the styling intent

**Weak signals**:
- Glossy/aspirational framing
- Multiple subjects with coordinated styling

### Modifier library

- **Publication references:** Vogue Italia · Harper's Bazaar · GQ · National Geographic · Kinfolk · The Gentlewoman · Apartamento · Wallpaper* · Vanity Fair · WIRED · i-D Magazine · AnOther Magazine · The New York Times Magazine
- **Styling notes:** layered textures · statement accessories · monochromatic palette · contrast patterns · period-specific styling · architectural silhouettes · texture-on-texture
- **Locations:** marble staircase · rooftop at golden hour · industrial loft · desert dunes · neon-lit alley · brutalist concrete · pristine modernist interior · weathered seaside · vintage diner · vacant theater
- **Pose language:** power stance · relaxed editorial lean · movement blur · fabric in wind · candid laughter · architectural pose
- **Crop styles:** full-bleed edge-to-edge · framed within negative space · asymmetric tight crop · classical centered · dynamic Dutch tilt
- **Era / styling decade:** late-90s grunge · early-2000s minimalism · 1970s warm · 1960s mod · 2010s normcore · contemporary streetwear · timeless classic
- **Camera moves:** slow drift · locked-off · gentle pan · steadicam follow
- **Pacing:** gentle pace · steady drift
- **Loop suitability:** rare — editorial motion is typically a narrative beat or a styled drift, not a loop

---

## Landscape

### Detection cues

**Strong signals**:
- "landscape video", "vista clip", "panorama motion"
- Named geographic location ("Yosemite", "Patagonia", "Scottish Highlands")
- "nature video", "outdoor clip", "wilderness motion"
- "mountain", "valley", "coast", "desert" as central subject
- "drone shot" / "aerial reveal"
- "time-lapse"

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
- **Camera moves:** drone aerial pull-up · drone reveal · drone aerial drift · slow pan · locked-off time-lapse · crane up
- **Pacing:** steady drift · floating · accelerating (for drone reveals) · slow burn (for time-lapse)
- **Subject motion intensity defaults:** still — environmental motion (clouds drifting, fog moving, light shifting) is the dominant motion
- **Loop suitability:** sometimes — drift loops and time-lapse cycles work; heroic reveals don't loop

---

## Abstract

### Detection cues

**Strong signals**:
- "abstract video", "abstract motion", "non-representational"
- "geometric pattern motion", "fractal animation", "generative motion"
- "texture study motion", "color field clip"
- "loop", "looping clip", "looping animation"

**Medium signals**:
- Description focused on shape, color, texture without a recognizable subject
- "mood piece", "atmosphere"
- "background motion", "wallpaper motion" (in the decorative sense)
- "particle flow", "fluid dynamics"

**Weak signals**:
- Avant-garde or experimental framing

### Modifier library

- **Geometry:** fractals · voronoi tessellation · spirals · fibonacci sequence · organic flow · crystalline structures · cellular automata · L-systems
- **Textures:** marble veining · fluid dynamics · smoke wisps · ink diffusion · watercolor bleed · paper grain · linen weave · brushed metal
- **Color palettes:** analogous harmony · complementary clash · monochromatic gradient · neon-on-black · earth tones · pastel chromatic · split-complementary
- **Style references:** generative motion (Casey Reas, Memo Akten, Ben Fry) · data visualization motion · glitch aesthetic · procedural · macro photography of materials in motion · Bauhaus geometric · op art (Bridget Riley) animated
- **Density / complexity spectrum:** sparse minimal · balanced · dense layered · maximalist
- **Movement / flow direction:** radial outward · linear cascade · centripetal · turbulent chaos · slow drift · explosive radial
- **Symmetry rule:** radial · bilateral · asymmetric balance · broken symmetry · perfect mirror
- **Motion treatment** *(Abstract-specific)*: generative drift · cellular automation step · particle flow · fluid simulation · radial pulse · linear cascade · chromatic shift · iterative growth
- **Camera moves:** locked-off · slow rotate · drift
- **Pacing:** pulse-matched · breath-cycle · floating
- **Subject motion intensity defaults:** the subject IS the motion — intensity describes the rate of pattern change (subtle for slow drift, active for rapid cascades)
- **Loop suitability:** yes — Abstract is the most loop-friendly domain (pulse-cycle, seamless wraparound, drift-and-return all natural)

---

## Fallback rule — when no domain matches

If domain confidence is below 60% for all 6 domains, OR two+ domains tie above 60%, the orchestrator asks **one disambiguation MCQ** before continuing:

```
Which register fits best?
   a) [top candidate domain] — [one-line rationale referencing what the user said]
   b) [second candidate domain] — [one-line rationale]
   c) [third candidate domain] — [one-line rationale]
   d) something different (describe)
```

Behavior:

- If user picks (a/b/c), use that domain. Proceed normally.
- If user picks (d) and writes free-text, set domain to **closest of the 6** (whichever the orchestrator judges nearest), inject the user's free-text as a **style override** in the brief-constructor's input, and flag the sidecar with `domain_inferred: true` in `params`.
- The disambiguation MCQ counts toward the 3-MCQ cap. After it, only 1–2 more MCQs allowed.

This keeps the 6-domain system intact while admitting the long tail (e.g., "logo animation reveal", "UI motion mockup", "infographic data-bar grow") without forcing the orchestrator to invent a new domain.

> **Note on dropped domains:** UI / Logo / Infographic don't have video presets in fal-video. If the user explicitly asks for one of these in motion (e.g., "animate this logo"), the orchestrator routes via the fallback rule — closest-of-6 (typically Abstract for logo motion, Product for UI mockup motion) plus user free-text injected as override.
