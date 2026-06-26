# Clarification MCQ — fal-image

How the orchestrator decides whether to ask MCQ questions, what to ask, and how to render them. Read by the orchestrator (SKILL.md), not by the brief-constructor subagent.

---

## When to ask

**Heuristic:** can the orchestrator fill **every slot** of the 5-component formula for the detected domain from the user's message + the resolved preset?

- **Yes → skip MCQs.** Generate directly. Show the constructed prompt to the user after.
- **No → ask MCQs to close the gaps.**

### Slot-by-slot gap evaluation

For each of the 5 formula slots, the slot is **filled** if either:
- The user's message provides it, OR
- The resolved preset provides a non-empty value, OR
- The slot is one the brief-constructor can reliably infer from domain + subject (Composition for photographic domains is usually inferable from preset)

The slot is a **gap** if both message and preset are empty/`—` AND the brief-constructor cannot infer reliably.

| Slot | Filled by user message... | Filled by preset... | Inference allowed? |
|---|---|---|---|
| **Subject** | the object / person / thing being asked for | rarely | No — must come from message |
| **Action** | a verb or implied state ("running", "resting", "displayed") | rarely | Sometimes (default: static for products, candid for people) |
| **Location/Context** | a place / setting | partially via `cultural / regional context` | Sometimes |
| **Composition** | framing / angle / aspect | yes — `default aspect ratio`, `focal length`, `angle preference` | Yes for photographic domains |
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

1. Style + Lighting (highest visual impact)
2. Action (defines what's happening)
3. Subject (only if extremely vague, e.g., "make me something nice")
4. Location/Context (often inferable from subject)
5. Composition (preset usually covers it)

---

## Skip MCQs entirely when

Skip content MCQs if **any** of these are true:

- User said **"just generate"** / **"go ahead"** / **"no questions"** / **"surprise me"**
- User pasted a **fully-specified brief** (≥30 words covering subject + scene + style)
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

User: *"make me a product portrait of a watch"*

Detected domains tied: Product (matches "product"), Portrait (matches "portrait"), with Editorial as a candidate.

```
Which register fits best?
   a) Product — studio shot, 45° hero, the watch is the subject (recommended for e-commerce / hero imagery)
   b) Portrait — telephoto compression, shallow DoF, treating the watch like a face (artistic / editorial)
   c) Editorial — fashion register, watch on wrist or styled with accessories
   d) something different (describe)
```

If user picks (d) with custom text → set domain to closest match + inject text as style override + flag `domain_inferred: true` in sidecar.

---

## Content MCQ patterns per slot

When the orchestrator decides to ask a content MCQ, it picks the appropriate slot pattern. These are templates, not scripts — fill in domain-specific options each time.

### Subject MCQ (rare — only for very vague requests)

Used when user said something like "make me an image" with no subject specified.

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
   a) [action A — e.g., "displayed at rest, no motion"]
   b) [action B — e.g., "mid-action, captured in motion"]
   c) [action C — e.g., "interacting with [related object]"]
   d) something else (describe)
```

Example for a product request:
```
How is the headphone displayed?
   a) Resting at 45° hero angle on a neutral surface
   b) Worn by a model (head not visible, just the product on the head)
   c) Mid-action, hand picking it up from a desk
   d) something else (describe)
```

### Style / mood MCQ

Used when style and lighting are gaps.

```
What's the mood?
   a) [Mood A with publication anchor — e.g., "Warm, nostalgic, Kinfolk-like"]
   b) [Mood B — e.g., "Bold, contemporary, Wallpaper* design"]
   c) [Mood C — e.g., "Moody, cinematic, dramatic"]
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

1. **Letter selection** — `a`, `b`, `c`, `d`, `(a)`, `option a`, `the a one`
2. **Position selection** — "first", "second", "third", "fourth"
3. **Recommended fallback** — "recommended", "default", "your pick", "you choose" → option (b) or marked-recommended
4. **Custom freeform** — anything else is treated as user-provided text for option (d)

If parsing fails, the orchestrator asks once for clarification: *"Just to confirm — are you going with (a), (b), (c), or do you want to describe something else?"* — but does not start a new MCQ flow.

---

## Worked example — full MCQ flow

User: *"make me a portrait of a chef in a kitchen"*

Domain detection: **Portrait** (high confidence).

Slot evaluation:
- Subject: filled (a chef)
- Action: gap (no verb specified)
- Location: filled (in a kitchen)
- Composition: filled by preset (200mm, f/1.4, 4:3)
- Style+Lighting: gap (no style cues, preset's lighting is default but mood/grading empty)

Gap count: 2. Plan: 2 content MCQs.

Priority order picks: Style+Lighting (1st), Action (2nd).

### Question 1 (Style):

```
What's the mood?
   a) Warm, intimate, Kinfolk-like — soft natural light through windows, contemplative
   b) Bold, editorial, GQ register — directional studio light, confident
   c) Moody, cinematic — single-source dramatic lighting, low-key
   d) something else (describe)
```

### Question 2 (Action):

```
What's the chef doing?
   a) Mid-action — plating, pouring, slicing — captured in motion
   b) Pausing — hands on counter, looking out at the kitchen, contemplative
   c) Direct-to-camera — confident posture, knife in hand or apron straightened
   d) something else (describe)
```

User replies: *"a, c"* → orchestrator interprets as: warm/intimate mood + direct-to-camera action.

brief-constructor receives:
- User request: "portrait of a chef in a kitchen"
- Domain: Portrait
- Preset path: ~/.claude/skills/fal-image/presets/portrait.preset.md
- Mode: generate
- Target model: nano-banana-pro (orchestrator's pick from the roster, surfaced in the pre-flight summary)
- MCQ answers: `{ style: "warm intimate Kinfolk-like", action: "direct-to-camera confident" }`

→ proceeds to construct the prompt.
