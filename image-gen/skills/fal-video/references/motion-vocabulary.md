# Motion Vocabulary — fal-video

The motion vocabulary library used by `fal-video`. Drawn from cinematography practice; model-agnostic. Read this together with `prompt-engineering.md` whenever the Motion slot of the 6-component formula needs to be filled.

> Motion is the new high-leverage slot for video. Bad motion language tanks any clip regardless of subject quality. This file enumerates the moves, the pacing words, the subject-motion bands, and the cross-domain "when to use" guidance so the brief-constructor can fill the slot with intention, not generics.

---

## Camera moves

The camera-move taxonomy. One dominant move per shot — combinations are documented at the end.

### Static / stabilized moves

| Move | What it does | When to use |
|---|---|---|
| **Locked-off (lockdown)** | Tripod, no movement. Frame is fixed. | Product reveals · talking-head portraits · time-lapse · architectural · loop-friendly clips · whenever motion should come from the subject, not the camera |
| **Locked-off + rack focus** | Frame fixed; focus shifts from foreground to background or vice versa. | Product hero · narrative reveal · two-character beat without moving |
| **Locked-off + rack zoom (dolly zoom)** | Frame fixed in subject size; perspective compresses or expands. The Hitchcock effect. Use sparingly — easily becomes cliché. | Vertigo / disorientation moments only |

### Push / pull moves

| Move | What it does | When to use |
|---|---|---|
| **Slow push-in (dolly-in)** | Camera moves forward toward the subject. Increases intimacy and tension. | Portraits · cinematic narrative · revealing emotional weight · contemplative beats |
| **Slow pull-out (dolly-out)** | Camera moves backward away from the subject. Reveals scale or context. | Establishing shots · scale reveals · ending a beat · transitioning out |
| **Brisk push** | Faster forward dolly. More urgency. | Action beats · escalating tension |
| **Snap zoom** | Rapid optical zoom-in. Often handheld. | Reaction beats · 1970s thriller register · documentary register |

### Lateral / orbital moves

| Move | What it does | When to use |
|---|---|---|
| **Pan left / pan right** | Camera rotates horizontally on a fixed axis. | Following lateral motion · scanning a wide scene · landscape sweeps |
| **Whip-pan** | Rapid pan, frame blurs through the move. Often used for transitions. | Music videos · 1990s indie · Christopher Doyle register · transition implication |
| **Truck (lateral track)** | Camera moves laterally with the subject (no rotation). | Walking-and-talking · following along a counter · parallax foreground / background separation |
| **Crab dolly** | Diagonal lateral track. | More dynamic than straight truck; reveals depth |
| **Arc orbit** | Camera circles the subject on a curved path. | Product 360 reveals · key moment of a portrait · architectural orbit |
| **Tilt up / tilt down** | Camera rotates vertically on a fixed axis. | Reveal a tall subject · architectural · scale beat |

### Aerial / vertical moves

| Move | What it does | When to use |
|---|---|---|
| **Crane up / crane down** | Camera rises or descends on a vertical axis. | Establishing shot endings · revealing scale from a single figure to a wide environment |
| **Jib** | Pivoting crane. Camera arcs from one elevation to another. | Stylized reveal · ceremonial beats |
| **Drone aerial pull-up** | Drone rises and pulls back. Quintessential reveal. | Landscape reveals · architectural reveals · "from one figure to vast environment" |
| **Drone reveal** | Drone moves laterally or pushes through an opening. | Geographic establishing shots · scale reveals |
| **Drone aerial drift** | Slow drone drift over a static landscape. | Landscape time-lapse alternative · contemplative atmospheric beats |

### Handheld / human moves

| Move | What it does | When to use |
|---|---|---|
| **Handheld with breath** | Slight, organic micro-movement. Natural human breath in the frame. | Documentary register · Lubezki-style natural-light · intimate portraits |
| **Handheld with shake** | More pronounced human movement. | 1990s indie · documentary · grit register |
| **Steadicam** | Smooth gimbal-style flow following the subject. | Following walking subjects · long-take reveals · prestige drama register |
| **Gimbal** | Modern stabilized smooth follow. Less organic than steadicam. | Contemporary commercial · YouTube creator register |

### Specialty moves

| Move | What it does | When to use |
|---|---|---|
| **Slow rotate (turntable)** | Camera or subject rotates on a vertical axis at a slow, even pace. | Product reveals · sculptural objects · 360 product views |
| **Match-cut implication** | Frame composition designed to imply a cut to a related shot. Used in single-clip context as a structural choice. | Sophisticated single-take · transitional setup |
| **Single continuous take** | Explicit declaration of no internal cuts. | Long-take cinematography · prestige drama · live-action register |

---

## Pacing

How fast the motion unfolds. Independent of the camera move itself.

| Pacing | Description | Pairs well with |
|---|---|---|
| **Locked / breath-held** | No tempo at all; stillness with subtle subject motion. | Locked-off + still or subtle subject |
| **Slow burn** | Tempo accumulates over the clip. Tension builds. | Slow push-in · dolly-out · Roger Deakins register |
| **Steady drift** | Constant, even tempo throughout. | Drone drift · time-lapse · gentle pan |
| **Gentle pace** | Slightly faster than steady drift; conversational. | Steadicam follow · walking-and-talking |
| **Brisk** | Conversational-fast; energetic but not urgent. | Truck · crab dolly · gimbal follow |
| **Rapid** | Urgent, escalating. | Whip-pan · brisk push · documentary register |
| **Staccato** | Sharp, punctuated motion. Often implies multiple sub-beats inside a clip. | Music-video register; use sparingly in fal video as it implies cuts |
| **Accelerating** | Tempo speeds up across the clip. | Push-in that intensifies · drone pull-up that takes off |
| **Decelerating** | Tempo slows across the clip. | Pull-out that ends contemplative · dolly-out into stillness |
| **Pulse-matched** | Tempo cycles like a heartbeat or breath. | Loop-friendly clips · abstract motion |
| **Floating** | Untethered, drifting, no destination. | Abstract motion · contemplative landscape |

> Every prompt must contain a pacing word. Even "static, breath-held, locked-off" qualifies — that's the pacing of stillness.

---

## Subject motion intensity

How much the subject moves, independent of the camera. Always state explicitly. Without this, models default to over-animation (everything wiggles).

| Intensity | What's moving | Examples |
|---|---|---|
| **Still** | Nothing. Subject is fixed. | Product on a table · sleeping figure · architectural element |
| **Subtle** | Micro-gestures, breath, fabric flutter, eye blinks, single hair tendril. | Contemplative portrait · drinking-in-the-moment beat · breath-held tension |
| **Moderate** | Clear gestures at conversational pace. Reaching, turning, glancing. | Conversation beats · everyday activity · chef stirring · barista pulling espresso |
| **Active** | Mid-action with larger gestures. Walking, picking up, working with hands. | Documentary work register · craft scenes · sport sub-action |
| **Vigorous** | Running, dancing, dynamic full-body motion. | Sport · dance · action sequences |

**Rule of thumb:** match camera move to subject motion. Locked-off + still = static frame. Locked-off + subtle = product breath. Slow push-in + moderate = portrait beat. Handheld + active = documentary register. Avoid mismatches like "locked-off frame, vigorous subject motion" unless deliberate (e.g., the camera observing).

---

## Action verbs (video-specific)

Strong, specific verbs that translate well into video model output. Prefer these over generic verbs.

| Verb | When to use |
|---|---|
| **drifts** | Slow lateral motion · clouds · steam · mist |
| **rises** | Vertical motion · steam · smoke · dust · subject standing |
| **falls** | Vertical descent · leaves · fabric draping · drops of liquid |
| **pulses** | Cyclical motion · breath · heartbeat · light flickering · abstract patterns |
| **ripples** | Wave-like motion · water · fabric in wind · sand |
| **settles** | End-of-motion · dust settling · figure relaxing into pose · liquid coming to rest |
| **awakens** | Beginning-of-motion · light dawning · subject opening eyes · scene activating |
| **turns** | Rotational subject motion · head turn · object spinning · doorway opening |
| **glances** | Subtle gaze shift · key portrait micro-action |
| **reaches** | Subject extending hand or limb |
| **embraces** | Two-figure interaction · hug · hand on shoulder |
| **steps forward** | Subject advancing toward camera |
| **pivots** | Rotational subject motion on the heel |
| **breathes** | Visible chest rise / fall · breath in cold air |
| **sighs** | Visible exhale · shoulders dropping |

These verbs are the verbs of the **Action** slot, not the Motion slot. Motion describes the camera; Action describes the subject.

---

## Transitions and edits within a single shot

fal video models produce a single continuous clip — there are no internal cuts. But you can imply transitions through composition and motion.

| Technique | Description | When to use |
|---|---|---|
| **Cross-dissolve in** | Clip starts on a soft fade-in from black or white. | Polished commercial · contemplative opener |
| **Fade up from black** | Clip opens from full black to full image. | Cinematic register · narrative implication |
| **Fade out to white** | Clip ends fading to white. | Commercial register · uplifting beats |
| **Fade out to black** | Clip ends fading to black. | Cinematic ending · dramatic register |
| **Match-cut implication** | Frame composition designed so a cut to a related shot would feel seamless. | Sophisticated single-take · structural composition |
| **Single continuous take** | Explicit declaration of no transition at all. | Prestige drama · long-take register |

> Internal cuts don't exist in fal video output. Don't write "cut to," "and then," or "later." Describe one continuous shot.

---

## Loop and seam

Loop-friendly clips share start and end frames so they can repeat seamlessly.

| Technique | Description | When to use |
|---|---|---|
| **Start frame ≈ end frame** | The first and last frame are visually identical (or near-identical). | Loop-friendly clips · downstream GIF source material |
| **Seamless wraparound** | Motion direction at end matches motion direction at start. | Drift loops · particle flow · abstract patterns |
| **Drift-and-return** | Motion drifts in one direction, then returns to origin. | Subtle product loops · breathing portraits |
| **Pulse-cycle** | Motion expands and contracts on a fixed cycle (like a heartbeat). | Abstract motion · UI / micro-animation feel |
| **Breath-cycle** | Motion follows a breath rhythm — inhale (expand), exhale (contract). | Portraits · contemplative beats · meditation register |

Loops work best when subject motion intensity is **still** or **subtle**. Active or vigorous subject motion is hard to loop.

---

## Speed effects (use sparingly)

| Effect | Description | Cost / risk |
|---|---|---|
| **Slow-motion (overcrank)** | Action plays slower than real time. Captured at higher frame rate, played back at standard rate. | Eats fal model budget if model interprets as longer source duration. Use specific cue: "captured at 120fps, played at 24fps." |
| **Time-lapse (undercrank)** | Action plays faster than real time. | Best on landscape / environmental subjects. State explicitly: "twenty-second time-lapse compressed into a five-second clip." |
| **Ramp** | Speed transitions from one rate to another within the clip. | Hard for current fal models to honor reliably. Use sparingly. |
| **Normal-time (no manipulation)** | Action plays at real-time speed. | The default. Don't bother stating unless contrasting with another clip. |

> Don't reach for slow-motion or time-lapse unless the brief calls for it. Real-time motion is more reliable across all fal video models.

---

## Cross-reference table — when to use which camera move per domain

| Domain | Typical camera moves | Typical pacing | Loop suitability |
|---|---|---|---|
| **Cinema** | Slow push-in · slow pull-out · steadicam · handheld with breath · locked-off | Slow burn · steady drift · accelerating | Rare |
| **Product** | Locked-off + rack focus · slow rotate · arc orbit | Gentle pace · steady drift · pulse-matched | Yes (drift-and-return, pulse-cycle) |
| **Portrait** | Slow push-in · locked-off · handheld with breath | Breath-held · slow burn · breath-cycle | Sometimes (breath-cycle) |
| **Editorial** | Slow drift · locked-off · gentle pan | Gentle pace · steady drift | Rare |
| **Landscape** | Drone aerial pull-up · drone drift · slow pan · locked-off time-lapse | Steady drift · floating · accelerating | Sometimes (drift loops) |
| **Abstract** | Locked-off · slow rotate · drift | Pulse-matched · breath-cycle · floating | Yes (pulse-cycle, seamless wraparound) |

This table is a **starting point**, not a constraint. User intent overrides — a "frantic handheld product reveal" overrides Product's locked-off default.

---

## Hard rules — motion

These are non-negotiable for the Motion slot.

1. **One dominant camera move per shot.** Don't chain "pan + zoom + truck." Pick the dominant move, mention it explicitly, and let any secondary motion be implied.

2. **Match move to subject motion.** Locked-off + still subject = static frame, fine. Locked-off + vigorous subject = camera observes, be explicit. Mismatches read as model errors unless you call them out.

3. **Pacing word always present.** Even "static, breath-held, locked-off" satisfies — that's the pacing of stillness. Without a pacing word, the model picks a default that's almost always wrong.

4. **No contradictory moves.** Locked-off + rapid handheld is mutually exclusive. Pick one. If you want the camera observing rapid subject motion, write "locked-off frame, subject moves rapidly across the frame."

5. **Lead with motion intent.** If the camera move is the point of the clip (a slow push-in, a drone reveal), state it in the first sentence. Buried-at-the-end motion gets ignored.
