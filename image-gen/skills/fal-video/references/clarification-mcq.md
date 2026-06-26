# Clarification MCQ — fal-video

How the orchestrator decides whether to ask MCQ questions, what to ask, and how to render them. Read by the orchestrator (SKILL.md), not by the brief-constructor subagent.

---

## When to ask

**Heuristic:** can the orchestrator fill **every slot** of the 6-component formula for the detected domain from the user's message + the resolved preset?

- **Yes → skip MCQs.** Generate directly. Show the constructed prompt to the user after.
- **No → ask MCQs to close the gaps.**

### Slot-by-slot gap evaluation

For each of the 6 formula slots, the slot is **filled** if either:
- The user's message provides it, OR
- The resolved preset provides a non-empty value, OR
- The slot is one the brief-constructor can reliably infer from domain + subject

The slot is a **gap** if both message and preset are empty/`—` AND the brief-constructor cannot infer reliably.

| Slot | Filled by user message... | Filled by preset... | Inference allowed? |
|---|---|---|---|
| **Subject** | the object / person / thing being asked for | rarely | No — must come from message |
| **Action** | a verb or implied state | rarely | Sometimes (default: still for products, breath/contemplative for portraits) |
| **Location/Context** | a place / setting | partially via `cultural / regional context` | Sometimes |
| **Composition** | framing / angle / aspect | yes — `default aspect ratio`, `focal length`, `angle preference` | Yes for photographic domains |
| **Motion** | camera move language ("slowly push in") or "animate this" | partially — preset has `camera-move preference`, `pacing` | **Sometimes — only if preset is rich; otherwise gap. Motion is high-leverage; treat as gap if even slightly underspecified.** |
| **Style + Lighting** | style words, lighting, mood | yes — heavily, via `lighting setup`, `color grading`, `mood`, `film stock` | Yes if preset has values |

### Gap count → MCQ count

| Gap count | MCQs to ask |
|---:|---|
| 0 | none — proceed straight to pre-flight |
| 1 | 1 content MCQ |
| 2 | 2 content MCQs |
| 3+ | 2 content MCQs (highest-impact slots). Remaining gaps filled by brief-constructor inference. |

**Cap: 2 content MCQs per request.** The orchestrator picks the model itself from the roster — no model MCQ. The pre-flight summary surfaces the chosen model with its cost and reason, and the user can override there.

**Priority order for picking the 2 MCQs when 3+ gaps:**

1. **Motion** — highest video-specific impact; bad motion language tanks the clip
2. **Style + Lighting** — second highest visual impact
3. **Action** — defines what's happening
4. **Subject** — only if extremely vague ("make me something nice")
5. **Location/Context** — often inferable from subject
6. **Composition** — preset usually covers it

---

## Skip MCQs entirely when

Skip content MCQs if **any** of these are true:

- User said **"just generate"** / **"go ahead"** / **"no questions"** / **"surprise me"**
- User pasted a **fully-specified brief** (≥30 words covering subject + scene + motion + style)
- This is a **batch follow-up** (subsequent calls in a batch series inherit the first call's answers)

If user said "just generate", the orchestrator infers all gaps via brief-constructor and proceeds to the pre-flight summary.

---

## Domain disambiguation MCQ

When two or more domains tie above 60% confidence, OR no domain matches above 60%, the orchestrator asks a **disambiguation MCQ first**, before any content MCQs. This counts toward the 3-MCQ cap.

### Format

```
Which register fits best?
   a) [Domain A] — [one-line rationale referencing what the user said]
   b) [Domain B] — [one-line rationale]
   c) [Domain C] — [one-line rationale, only if a third candidate exists]
   d) something different (describe)
```

### Worked example

User: *"make me a moody video portrait of a chef"*

Detected domains tied: Portrait (matches "portrait"), Cinema (matches "moody"), with Editorial as a candidate.

```
Which register fits best?
   a) Portrait — telephoto compression, slow push-in, breath-held register
   b) Cinema — narrative beat, dramatic lighting, slow burn pacing
   c) Editorial — fashion register, layered styling, gentle drift
   d) something different (describe)
```

If user picks (d) with custom text → set domain to closest match + inject text as style override + flag `domain_inferred: true` in sidecar.

---

## Content MCQ patterns per slot

When the orchestrator decides to ask a content MCQ, it picks the appropriate slot pattern. These are templates, not scripts — fill in domain-specific options each time.

### Motion MCQ (NEW — top priority for video)

Used when motion is a gap and not inferable from preset alone.

```
What kind of camera motion?
   a) Locked-off — fixed frame, subject motion only
   b) Slow push-in — camera drifts gently toward the subject
   c) Pan or arc — camera moves laterally or orbits the subject
   d) Handheld — natural breath, subtle organic shake
   e) something else (describe)
```

(Five options for Motion — it has more distinct buckets than Style.)

**Variation for landscape / atmospheric:**

```
What kind of camera motion?
   a) Locked-off time-lapse — fixed frame, environmental motion (clouds, light, fog)
   b) Drone reveal / pull-up — aerial reveal of the scene
   c) Drone drift — slow lateral drift over the landscape
   d) Slow pan — horizontal sweep across the vista
   e) something else (describe)
```

**Variation for product / abstract loops:**

```
What kind of camera motion?
   a) Locked-off + rack focus — fixed frame, focus shifts between elements
   b) Slow rotate — camera or subject rotates on a vertical axis
   c) Locked-off with pulse loop — frame fixed, subject pulses on a cycle
   d) Drift-and-return — camera or subject drifts then returns (loop-friendly)
   e) something else (describe)
```

### Subject MCQ (rare — only for very vague requests)

Used when user said something like "make me a video" with no subject specified.

```
What's the subject?
   a) [domain-typical subject A]
   b) [domain-typical subject B]
   c) [domain-typical subject C]
   d) something else (describe)
```

### Action / state MCQ

Used when subject is clear but action/state is not.

```
What's [the subject] doing?
   a) [action A — e.g., "still, just resting / standing"]
   b) [action B — e.g., "mid-action, captured in motion"]
   c) [action C — e.g., "interacting with [related object]"]
   d) something else (describe)
```

Example for a product video:
```
How is the headphone displayed?
   a) Resting at 45° hero angle, single steam wisp drifting
   b) Slowly rotating on a turntable, single key light traveling across the surface
   c) Hand reaching in, picking it up from a desk
   d) something else (describe)
```

### Style / mood MCQ

Used when style and lighting are gaps.

```
What's the mood?
   a) [Mood A with cinematographer or publication anchor — e.g., "Warm, contemplative, Roger Deakins steady prestige drama"]
   b) [Mood B — e.g., "Bold, contemporary, Wallpaper* design feature"]
   c) [Mood C — e.g., "Moody, cinematic noir, single-source dramatic"]
   d) something else (describe)
```

### Location / context MCQ

Used when context is a gap.

```
Where's the scene?
   a) [Context A — e.g., "Studio with seamless backdrop"]
   b) [Context B — e.g., "Real-world environment that contextualizes the subject"]
   c) [Context C — e.g., "Outdoor / natural setting"]
   d) something else (describe)
```

---

## Rendering rule

MCQs are rendered as **plain markdown in the chat**, NOT via the AskUserQuestion tool. The orchestrator outputs the question + options, the user replies in freeform.

### Why plain markdown

- AskUserQuestion is meant for structured forms; over-formal for this conversational flow
- Plain markdown lets the user reply with `(a)`, `a`, "the first one", "let's go with the recommended", or freeform like "actually let's do something even moodier" — all parseable
- "No second-round MCQs" rule: if the user gives custom text in (d), the orchestrator works with it; doesn't ask follow-up MCQs

### Parsing user replies

The orchestrator looks for, in priority order:

1. **Letter selection** — `a`, `b`, `c`, `d`, `e`, `(a)`, `option a`, `the a one`
2. **Position selection** — "first", "second", "third", "fourth", "fifth"
3. **Recommended fallback** — "recommended", "default", "your pick", "you choose" → option (b) or marked-recommended
4. **Custom freeform** — anything else is treated as user-provided text for option (d) or (e)

If parsing fails, the orchestrator asks once for clarification: *"Just to confirm — are you going with (a), (b), (c), (d), or do you want to describe something else?"* — but does not start a new MCQ flow.

---

## Worked example — full MCQ flow

User: *"make me a video portrait of a chef in a kitchen"*

Domain detection: **Portrait** (high confidence).

Slot evaluation:
- Subject: filled (a chef)
- Action: gap (no verb specified)
- Location: filled (in a kitchen)
- Composition: filled by preset (200mm, f/1.4, 4:3)
- Motion: gap (preset has `slow push-in or locked-off` but two options — count as a soft gap; also user gave no motion cue)
- Style+Lighting: gap (no style cues, preset's lighting is default but mood/grading empty)

Gap count: 3. Plan: 2 content MCQs. Priority pick: **Motion (1st)**, Style+Lighting (2nd).

### Question 1 (Motion):

```
What kind of camera motion?
   a) Locked-off — chef stands still, only breath and subtle gestures
   b) Slow push-in — camera drifts gently toward the chef over the clip
   c) Handheld with breath — natural organic register, documentary feel
   d) Pan or steadicam follow — camera moves with the chef as they work
   e) something else (describe)
```

### Question 2 (Style):

```
What's the mood?
   a) Warm, intimate, Kinfolk-like — soft natural light through windows, contemplative
   b) Bold, editorial, GQ register — directional studio light, confident
   c) Moody, cinematic — single-source dramatic lighting, low-key, Roger Deakins prestige drama
   d) something else (describe)
```

User replies: *"b, c"* → orchestrator interprets as: slow push-in motion + moody cinematic style.

brief-constructor receives:
- User request: "video portrait of a chef in a kitchen"
- Domain: Portrait
- Preset path: `<project>/.claude/skills/fal-video/presets/portrait.preset.md`
- Mode: generate
- Target model: veo-3.1 (orchestrator's pick from the roster, surfaced in the pre-flight summary)
- Audio enabled: false
- MCQ answers: `{ motion: "slow push-in", style: "moody cinematic Roger Deakins prestige drama" }`

→ proceeds to construct the prompt with all 6 slots filled.
