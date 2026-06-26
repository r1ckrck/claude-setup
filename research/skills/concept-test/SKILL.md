---
name: concept-test
description: Test protocol loaded by the `facilitator` skill for a concept test — defines how to probe a concept, what to log, and the natural-done condition. Not invoked directly.
---

# Concept test

Does the idea make sense and matter to the persona? Reacts to a concept, not a working flow.

## Inputs

- A **concept frame** — a static image or a short description of the idea (not a clickable flow).

## Protocol

Present the concept. Probe in order: **comprehension** ("what is this, what's it for?"), **relevance** ("does this fit your life?"), **desirability** (the reaction, in the persona's own words), **objections** ("what concerns you, what's missing, would you use it?"). Resist the politeness trap — do not accept "looks nice"; dig for a reason or a concrete use, and treat hedging as soft-negative.

## What to log

- **Comprehension** — how the persona described it back.
- **Relevance** — whether it maps to a real need, grounded in the persona.
- **Desirability** — the reaction plus 3–5 emotional words in the persona's own words.
- **Objections** — concerns, missing pieces, conditions.

## Natural-done (Layer A)

The concept prompts answered (comprehension, relevance, desirability, objections).

## Report

Findings render via `report-concept.md` (this skill folder, which adds the validate / iterate / kill verdict). The facilitator owns the loop, probing, Layer-B stops, debrief, and report skeleton.
