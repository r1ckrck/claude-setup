---
name: interview
description: Test protocol loaded by the `facilitator` skill for an open interview — defines the questioning approach, what to log, and the natural-done condition. Not invoked directly.
---

# Interview

Open-ended voice-of-customer. No interface — the value is themes, stories, and motivations.

## Inputs

- A **topic guide** — the themes to cover. No stimulus.

## Protocol

Run the facilitator's moderated conversation. Use the **funnel** (broad → specific): open with **grand-tour** questions ("tell me about the last time you…"), then probe. **Ladder** from behavior to motivation ("why does that matter?"). Chase **stories of past behavior** over opinions — a remembered action beats a stated preference. Cover the topic guide; follow strong threads where they appear.

## What to log

- **Themes** — grouped patterns in what the persona said.
- **Quotes** — verbatim, with a turn reference, for each theme.
- **Motivations** — what drives the behavior, laddered from what was said.
- **Pain points** — concrete frustrations, each with its quote.
- **Topic coverage** — which parts of the guide were covered; flag anything thin.

## Natural-done (Layer A)

Topic guide exhausted — stop at diminishing returns, when new questions stop yielding new themes.

## Report

Findings render via `report-interview.md` (this skill folder). The facilitator owns the loop, probing, Layer-B stops, debrief, and report skeleton.
