---
name: usability-test
description: Test protocol loaded by the `facilitator` skill for a usability test — defines the task, what to log, and the natural-done condition. Not invoked directly.
---

# Usability test

Can the persona complete a real task on the interface? Surfaces where it stalls, detours, or fails.

## Inputs

- A **task** expressed as a natural goal for the persona ("you want a personal loan — here's the app"), never as "complete this task."
- A **live URL** (real site or coded/published prototype) — the facilitator drives it per its interaction model.

## Protocol

Run the facilitator's moderated loop. The persona pursues the goal on its own, thinking aloud; you relay its actions and probe at hesitations. Apply graduated assistance only when it is genuinely stuck. Never reveal that this is a test, and never name a UI element the persona hasn't mentioned.

## What to log

- **Task outcome** — success / success-with-assist / fail; turns used; assists (with level).
- **Path taken** — the route step by step; mark the optimal path and any detours or dead-ends.
- **Hesitation points** — where it paused, re-read, or doubted (even if it recovered).
- **What worked** — elements that performed well.

## Natural-done (Layer A)

Task goal reached, **or** the persona explicitly abandons the task.

## Report

Findings render via `report-usability.md` (this skill folder). The facilitator owns the loop, probing, graduated assistance, Layer-B stops, debrief, and report skeleton.
