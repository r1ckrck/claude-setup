---
name: first-click-test
description: Test protocol loaded by the `facilitator` skill for a first-click test — defines the single-screen, one-click protocol, what to log, and the natural-done condition. Not invoked directly.
---

# First-click test

Where does the persona go *first* to reach a goal? The first click strongly predicts whether the task would succeed.

## Inputs

- One **screen** — a static image the user provides, or the first viewport of a URL.
- One **goal** stated as a natural intent ("where would you go to apply for a loan?").

## Protocol

Show the single screen. Let the persona decide where it would tap first to reach the goal, thinking aloud. Capture that first action and its reasoning, then **stop** — no further navigation, no second click. Ask only an open "why there?" Never hint at the right answer.

## What to log

- **Goal** — the natural intent given.
- **First click** — the element or region tapped first.
- **Optimal path** — correct / incorrect (was the first click on the route to the goal?).
- **Time-to-first-click** — turns taken before the first click.
- **Why there** — the persona's one-line reasoning, verbatim.

## Natural-done (Layer A)

First click + reasoning captured (inherently 1–2 turns).

## Report

Findings render via `report-first-click.md` (this skill folder). The facilitator owns the loop, probing, Layer-B stops, debrief, and report skeleton.
