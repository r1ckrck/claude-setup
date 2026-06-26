# Prompt Engineering — fal-video

The construction system used by `fal-video` to turn a user request into a production prompt for fal.ai video models. Read this before constructing any prompt. Six components, with **Motion** as a first-class slot and rules tightened around motion language.

---

## The 6-component formula

Every prompt is built from six components woven into narrative prose:

> **Subject → Action → Location/Context → Composition → Motion → Style (lighting included)**

| # | Component | What it captures | Example fragment |
|---|---|---|---|
| 1 | **Subject** | Who or what — physical specifics (age, build, material, species, expression). Never "a person." | "a weathered Japanese ceramicist in his seventies, sun-etched wrinkles, calloused hands" |
| 2 | **Action** | What the subject is doing — present-tense verb or visible state. | "leaning forward in concentration, smoothing the rim with a wet thumb" |
| 3 | **Location / Context** | Where + when + atmosphere. Time of day, weather, mood. | "inside a wood-fired anagama kiln workshop, late afternoon light through rice paper screens" |
| 4 | **Composition** | Camera perspective, framing, focal length, aperture. | "intimate close-up at slight low angle, shot on ARRI Alexa Mini LF with 50mm Cooke S7/i at T2.0" |
| 5 | **Motion** | Camera move + pacing + subject motion intensity. The new high-leverage slot for video. | "slow handheld push-in over five seconds, gentle parallax, breath-cycle pacing, subject motion subtle" |
| 6 | **Style (with lighting)** | Visual register, lighting setup, real-world references (cinematographers, film stock, publications). | "warm directional Rembrandt key from a single window, late-analog 1990s film register, Roger Deakins cinematography" |

### Weight distribution

| Component | Weight | Includes |
|---|---:|---|
| Subject | 25% | Age, ethnicity, build, expression, material, species |
| Action | 10% | Movement, pose, gesture, interaction |
| Context | 15% | Location + time + weather + atmosphere |
| Composition | 10% | Shot type, angle, framing, focal length, aperture |
| **Motion** | **15%** | Camera move + pacing + subject motion intensity |
| Style + Lighting | 25% | Medium, brand/camera names, textures, publications, art movements, color grading |

Motion claims 15% by reducing Subject from 30% (image's value) to 25% and Style from a combined 35% to 25%. Bad motion language tanks any video prompt — it's the single biggest delta from image.

---

## Hard rules

These are non-negotiable. Violating any of them degrades output quality on every fal video model tested.

1. **Narrative prose, never keyword lists.** Write paragraphs, not comma-separated tags.
2. **100–200 words standard.** 50–120 for image-to-video (the source image already locks most slots). 200–280 for complex briefs. Validate per fal model.
3. **Critical specifics in the first third.** The model attends most to the opening. Lead with must-haves.
4. **Real-world anchors over generic descriptors.** Real cameras (ARRI Alexa Mini LF, Sony Venice 2), real lenses with apertures (50mm Cooke S7/i at T2.0), real publications (National Geographic, Magnum), real cinematographers (Roger Deakins, Emmanuel Lubezki).
5. **ALL CAPS for hard constraints.** "MUST loop seamlessly" · "NEVER include cuts" · "ENGLISH only on the sign."
6. **Reframe negatives as positives.**
   - "no shake" → "locked-off, rock-steady frame"
   - "no people" → "uninhabited, deserted"
   - "no cuts" → "single continuous take"
   - "no audio" → no language needed; audio param controls this, not the prompt
7. **Write the scene, not the concept.** Describe what's literally on screen, not the intended feeling. Anti-pattern: *"A dynamic motion clip showing modern productivity."* — nothing visual to render.
8. **Micro-details over adjectives.** "single bead of sweat traveling down the temple" beats "intense." Specificity is the most underused lever.
9. **Motion language is mandatory.** Every prompt must specify a camera move (or "locked-off") AND pacing language (slow burn, breath-held, gentle drift, brisk, etc.). "A scene of X" with no motion description produces inert clips.
10. **Pacing word in the first half.** Bury "slow push-in" at the end and the model deprioritizes it. Lead with motion intent.
11. **No contradictory motion.** Don't combine "locked-off" with "rapid handheld," or "drone aerial reveal" with "tight intimate handheld." Pick one dominant move.
12. **State subject motion intensity explicitly.** One of: still / subtle / moderate / active / vigorous. Without this, models default to over-animation.

---

## Anchor language over generic quality words

Generic quality terms ("8K", "masterpiece", "ultra-detailed", "photorealistic", "cinematic", "epic", "dynamic motion", "smooth animation") carry weak training-data signal. They pull toward stock-video aesthetics. Replace them with concrete real-world anchors — cinematographers, camera bodies, lenses, film registers, publications — which carry strong, distinct representations the model can render.

| Generic phrase | Concrete anchor |
|---|---|
| "cinematic" | a named cinematographer + camera-move family ("Roger Deakins handheld", "Lubezki natural-light drift") |
| "epic" | concrete scope ("drone aerial reveal pulling out from a single figure to a 200-meter granite cliff face") |
| "dynamic motion" | the literal motion ("rapid handheld whip-pan from foreground to background over 1.5 seconds") |
| "smooth animation" | explicit pacing ("locked-off, breath-held push-in", "slow gentle drift") |
| "8K, ultra-detailed" | a specific publication ("Vanity Fair video portrait", "National Geographic time-lapse") |
| "photorealistic" | "shot on ARRI Alexa Mini LF with 50mm Cooke S7/i at T2.0" |

---

## Prestigious context anchors

Replace generic quality words with **specific publication, cinematographer, or film-register references**. These are training-data clusters with strong distinct representations.

**Image-side anchors that carry over:**
> Pulitzer Prize-winning cover photograph · Vanity Fair editorial portrait · National Geographic cover story · WIRED magazine feature spread · Magnum Photos documentary · Wallpaper* design editorial · Architectural Digest interior · Bon Appétit feature spread

**Video-specific anchors:**
> Roger Deakins cinematography · Emmanuel Lubezki natural-light handheld · Christopher Doyle handheld register · Edward Lachman late-analog · classic 1970s thriller register · 1990s indie warmth · 2010s prestige drama series cinematography · National Geographic time-lapse · drone aerial reveal register · single-take long shot register

Pick the anchor matching the *register* you want. Roger Deakins is steady prestige drama. Lubezki is natural-light handheld. Doyle is restless intimate handheld. Don't mix.

---

## Text-in-video rules

Text rendering in motion is even more fragile than in stills. Follow these rules tightly.

| Rule | Detail |
|---|---|
| **Avoid text when possible** | If the GIF / video doesn't need text, leave it out. fal video models corrupt text more often than not. |
| **Lock to a static plate** | If text must appear, anchor it to a non-animated plate (a sign, a poster, a screen). Don't ask for animated text. |
| **≤15 characters** | Even more conservative than image's ≤25. Longer text in motion compounds character-level errors frame-to-frame. |
| **Quote the exact text** | `with the text "OPEN"` not `with text saying open`. |
| **Describe font characteristics, not names** | "bold geometric sans-serif" works. "Helvetica Bold" doesn't. |
| **Single placement** | One text element per clip. Multiple text elements multiply the corruption risk. |
| **High contrast** | Light on dark or dark on light. Always specify. |

---

## Anti-patterns to avoid

| Anti-pattern | Example | Why it fails | Fix |
|---|---|---|---|
| **Writing the concept** | "A dynamic motion clip about productivity." | Describes intent, not image. Nothing to render. | Write the literal scene + motion that conveys it. |
| **Vague adjective stacks** | "Modern, clean, professional, dynamic." | Adjectives without nouns produce nothing. | Replace with specific objects, materials, lighting, camera move. |
| **Describing emotion of motion** | "Tense pacing, urgent feel." | Doesn't tell the model what to do. | Name the actual move: "rapid handheld whip-pan, accelerating pacing." |
| **Keyword stuffing** | "Beautiful, gorgeous, cinematic, epic, dynamic, smooth, masterpiece." | Stack of redundant quality words. | One specific cinematographer or film register. |
| **Tag-list format** | "woman, walking, beach, sunset, cinematic" | Comma lists are MidJourney-era. fal models prefer prose. | Rewrite as narrative paragraph. |
| **Burying critical motion details** | "[180 words]... and the camera should slowly push in." | Last-third details get deprioritized. | Move motion specs to the first third. |
| **Mixing register mid-prompt** | "Roger Deakins handheld also looks like a music video whip-pan montage." | Conflicting style anchors. | Pick one register and commit. |
| **Combining contradictory moves** | "Locked-off camera with rapid handheld shake." | Mutually exclusive. | One dominant move per shot. |

---

## Proven prompt templates

Five starting-point patterns. Each is a *skeleton* — fill the bracketed slots with specifics. Real prompts deviate from the skeleton.

### Template 1 — Cinematic narrative shot

```
[Subject: age + ethnicity + build + features], [wearing description with brand/material],
[present-tense action verb] in [specific location + time of day]. [Micro-detail: skin/hair/sweat/texture].
Captured with [camera body + lens + aperture]. [Camera move + pacing + duration cue].
[Subject motion intensity]. [Lighting description with direction and quality].
[Cinematographer or film register anchor].
```

Example:
> A 70-year-old Japanese ceramicist with deep sun-etched wrinkles and calloused hands, wearing an indigo cotton noragi over a worn linen apron, leaning forward in deep concentration as he smooths the rim of a tea bowl with a wet thumb, inside a traditional wood-fired anagama kiln workshop with late afternoon light through rice paper screens. Visible clay dust on his forearms, single bead of sweat at the temple. Captured with ARRI Alexa Mini LF and 50mm Cooke S7/i at T2.0. Slow handheld push-in over five seconds, breath-held pacing, subject motion subtle — only the thumb moves and the chest rises softly. Warm directional Rembrandt lighting from a single window. Roger Deakins cinematography, late-analog 1990s film register.

### Template 2 — Product reveal

```
[Product with brand name] [resting state or arranged state],
on [surface description] with [supporting prop]. [Lighting setup with direction].
[Camera move: slow rotate or locked-off + rack focus + duration]. [Pacing word].
Subject is [still / subtle motion]. [Reflection or shadow detail].
Commercial film for [publication or campaign register].
```

Example:
> A polished black B&O Beoplay H95 over-ear headphone resting at a forty-five-degree hero angle on a slab of Carrara marble veined with grey, single coil of brushed aluminum reflecting the rim light. Earcup leather catching a soft directional key from camera-right with a hard fill bouncing off a white card. Locked-off frame with a slow rack focus over four seconds, gentle drift pacing, subject is still — only the catchlight on the brushed metal subtly travels as the focus shifts from the headband to the earcup. Sharp drop-shadow falling away to the lower-left. Wallpaper* design feature register.

### Template 3 — Motion portrait

```
[Subject: detailed physical description],
[present-tense action: contemplative, breath, micro-gesture],
in [location] with [lighting source and quality].
[Camera: focal length and aperture]. [Camera move: slow push-in or locked-off + duration].
[Subject motion intensity: subtle, breath, micro-gestures].
[Cinematographer or publication register anchor].
```

Example:
> A 35-year-old woman with shoulder-length auburn hair and freckles across the nose bridge, contemplating the room in front of her, sitting at a worn oak counter in a small-batch roastery at golden hour, soft diffused window light entering from camera-left. Captured at 200mm f/1.4. Slow gentle push-in over six seconds, breath-cycle pacing, subject motion subtle — single eye blink and the chest rising gently with breath. Vanity Fair video portrait register, Edward Lachman late-analog warmth.

### Template 4 — Landscape time-lapse / drift

```
A [landscape: geographic anchor + time of day + atmospheric layer],
[depth-layer description: foreground / midground / background].
[Camera: focal length, lens, position]. [Camera move: slow pan or drone drift or locked-off time-lapse + duration].
[Subject motion: still or environmental — clouds drifting, light shifting].
[Color palette / grading]. [Publication or register anchor].
```

Example:
> A volcanic ridgeline in southern Iceland at blue hour, low fog drifting across the foreground basalt fields, the midground ridge silhouetted against a band of magenta sky, distant glacier visible beyond. Shot on Sony A7R IV with 24-70mm GM at f/8. Locked-off twenty-second time-lapse, gentle drift pacing as fog moves left to right and sky color shifts from magenta to indigo. Earthy ochres in the foreground, cool blue dominance overhead. National Geographic time-lapse register.

### Template 5 — Abstract motion study

```
[Geometric or textural subject: shape primitives, materials, color palette],
[arrangement and density]. [Movement direction + flow + symmetry rule].
[Camera: locked-off or slow drift + duration]. [Pacing: pulse-cycle, breath-cycle, slow burn].
[Loop seam: start frame ≈ end frame, seamless wraparound].
[Reference art movement or generative practitioner].
```

Example:
> A field of small voronoi tessellations in deep navy and brass, dense layered arrangement filling the frame, arranged in radial outward bilateral symmetry. The cells pulse outward from the center on a four-second pulse-cycle, then return to rest, creating a seamless loop where start frame equals end frame. Locked-off frame, breath-cycle pacing. Generative motion register evoking Casey Reas and Memo Akten, op-art bilateral symmetry.

---

## Common mistakes (10-item checklist)

Before sending any prompt, verify it does NOT have any of these:

- [ ] **1. Keyword stuffing** — comma-separated quality adjectives
- [ ] **2. Tag-list format** — Midjourney-era comma lists with no prose
- [ ] **3. Missing motion** — every prompt should specify a camera move (or "locked-off") AND pacing
- [ ] **4. Missing motion intensity** — every prompt should state subject motion (still / subtle / moderate / active / vigorous)
- [ ] **5. Missing lighting** — direction, quality, color temperature
- [ ] **6. No composition** — angle, framing, focal length, aperture spelled out
- [ ] **7. Vague style** — "modern" / "cinematic" without anchors. Use a cinematographer or publication.
- [ ] **8. Aspect-ratio mismatch** — prompt describes a wide cinematic shot but request asks for a square. Reword or change ratio.
- [ ] **9. Overlong prompts** — past ~280 words, returns diminish. Cut filler.
- [ ] **10. Burying motion details** — motion specs must be in the first third.

---

## Adapting prompts from other ecosystems

| Source convention | Convert to |
|---|---|
| `--ar 16:9 --fps 24 --motion 5` (Midjourney video) | Strip flags. Move aspect ratio + fps to API parameters. |
| `(masterpiece:1.5), (best quality:1.4)` | Strip weighted-prompt syntax. Use prose. |
| `(woman:1.3), walking, beach, cinematic` | Rewrite as narrative paragraph with a real motion clause. |
| `8K, masterpiece, ultra-detailed` | Replace with a cinematographer / publication anchor and a real camera/lens spec. |
| `shot on ARRI Alexa, 50mm` | **Keep this** — real camera/lens specs are universal. |
| `slow motion, time-lapse, hyperlapse` | Use sparingly; specify the speed effect explicitly (overcrank, undercrank, ramp). |

---

## Character consistency (multi-clip work)

When generating multiple clips of the same character/subject across a session:

- **Repeat 2–3 anchor identifiers verbatim** across every prompt
- **Use named references** — "Maya" or "the engineer" — and pin those names in subsequent prompts
- **Hold the camera/lens specs constant** across the series
- **Hold the lighting register constant** for visual continuity
- **Hold the motion register constant** — same camera-move family, same pacing — unless deliberately changing for a different beat
- **Pass a character reference image** when the model supports it (Veo 3.1 Ingredients to Video, Kling I2V). Reference-image conditioning beats prose for identity lock — text alone cannot reliably reproduce a face across clips.

Changing only what should change minimizes drift across clips.

---

## Per-model prompt-style notes

Different models reward different opening orders and audio handling. Adapt the construction to the target_model the orchestrator passes you.

| Model | Opening | Length sweet spot | Audio | Notes |
|---|---|---|---|---|
| **Veo 3.1** | **Cinematography-first** — shot type, camera move, lens, aperture before subject | flexible (long detailed paragraphs OK) | Native audio. When `audio_enabled` is true, weave the audio brief into prose ("ambient roastery hum, espresso machine hiss at three seconds, no music"). | Reference images supported as Ingredients to Video, up to 3 |
| **Kling 2.5 Turbo Pro** | **Subject-first** + explicit motion verb in same sentence, director's voice | 50–150 words | None — don't mention audio | Strong physics; explicit motion language ("dolly in slowly") works well |

Across all models: paragraph prose only, never JSON, no negative prompts, no `(word:1.5)` weighting. Aspect ratio, fps, and duration are always API parameters, not prose.

---

## Putting it all together — full example walkthrough

User request: *"hero video for my coffee shop website"*

Detected domain: **Product** (commercial register, hero composition implied).

Preset values to fold in (video/product preset):
- Default aspect ratio: 4:3
- Surface / background: contextual minimal — material complements the product, never competes
- Lighting setup: studio quality — softbox key, hard fill, rim separation
- Angle preference: 45° hero
- Focal length: 85mm
- Color treatment: true-to-life
- Default fps: 30
- Camera-move preference: slow rotate or locked-off + rack focus
- Loopability: yes
- Subject motion intensity: still or subtle
- Audio rules: off

6-component construction:

| Slot | Filled with |
|---|---|
| **Subject** | A weathered ceramic mug of single-origin espresso, slight chip on the rim, marbled tiger-stripe crema |
| **Action** | Resting on a worn oak counter, single rising wisp of steam |
| **Location/Context** | Inside a small-batch roastery at mid-morning, warm soft daylight from tall industrial windows |
| **Composition** | 45° hero angle, intimate close-up, shot on Sony Venice 2 with 85mm Zeiss at T2.8, shallow depth of field |
| **Motion** | Locked-off frame with a slow rack focus over four seconds, gentle drift pacing, subject still — only the steam wisp drifts upward and curls toward camera-left |
| **Style + Lighting** | Warm directional natural light from camera-right with a subtle white-card fill, true-to-life color, Wallpaper* design feature register |

Final prompt (~165 words):

> A weathered ceramic espresso mug with a hairline chip at the rim, single shot of single-origin espresso showing a marbled tiger-stripe crema, resting on a worn oak counter inside a small-batch roastery at mid-morning. Single wisp of steam rising vertically and curling slowly toward camera-left. Tall industrial windows behind cast soft warm daylight across the counter, the brass espresso machine and copper kettle softly out of focus in the background. Shot on Sony Venice 2 with 85mm Zeiss at T2.8, intimate 45-degree hero framing, shallow depth of field. Locked-off frame with a slow rack focus over four seconds, gentle drift pacing — the focus shifts from the chipped rim to the marbled crema, the rest of the frame stays still, only the steam wisp drifts upward. Subject motion subtle. Warm directional natural light from camera-right with a subtle white-card fill, true-to-life color, Wallpaper* design feature register.

This is a generation-ready prompt. It has all 6 slots filled, real camera/lens specs, narrative prose, micro-details (chipped rim, marbled crema, single wisp), an explicit camera move (locked-off + rack focus) with a duration (four seconds) and pacing (gentle drift), an explicit subject motion intensity (subtle), and a publication anchor.
