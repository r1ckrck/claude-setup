# Interaction Model

How the AI perceives and acts on a test stimulus **the way a human does** — sees a screen, decides, taps, scrolls. The contract that keeps a simulated user from "reading the code" instead of looking at the screen.

## Who reads this

- **The Facilitator reads and runs this.** It operates the tooling.
- **The persona never sees this file, the page structure, element refs, or DOM** — only screenshots. The persona decides; it never touches the plumbing.

## Stimulus types

| Stimulus | Tool | Action |
|---|---|---|
| Live URL — a real site, or a coded / published prototype | `playwright-cli` | Full relay loop (below) |
| Static image — a path the user provides | Vision (Read the image) | Look only; no navigation |
| No interface — an interview | — | Not applicable |

Raw Figma `proto/` links are **not** drivable (canvas-rendered). A clickable prototype must be supplied as a real URL.

## The facilitator-relay loop (live URL)

The persona is handed a phone; the facilitator is its hand and camera — nothing more.

1. Drive the browser with the **`playwright-cli` skill** — invoke that skill (it carries the command reference), do not call Playwright directly. Open at a **mobile viewport**: `resize 360 800` (budget-Android default; desktop only if explicitly asked).
2. Wait for the page to settle, then `screenshot` and save to a file.
3. Show the persona **only that screenshot** (it Reads the image). Ask what it does, or let it think aloud.
4. The persona answers in human terms — "scroll down", "tap the Apply button", "type my name".
5. The facilitator finds the element the persona meant in the snapshot and executes it **verbatim** (`click <ref>`, `fill <ref> "…"`, `mousewheel`, `go-back`).
6. Re-screenshot. Repeat.

The persona never sees the snapshot, the refs, or the DOM — only the screenshots.

## Anti-withholding guard

The facilitator is a **transparent hand + camera**. It:

- Executes the persona's stated intent **verbatim** — never substitutes a different target.
- Shows the **full current-viewport screenshot every turn** — never crops, skips, or rations.
- **Never decides** where to go, what to look at, or when to scroll. The persona decides; the facilitator only moves.

Reading the page structure is permitted **only** to locate the element the persona named — never to choose or to feed the persona content.

## Perception discipline

- The persona perceives **pixels only**.
- A screenshot shows the **current viewport**, not the full page. To see more, the persona must choose to scroll.
- Screenshot only **after the page settles**, so the persona reacts to a stable screen, not a half-loaded one.

## Action vocabulary

The persona speaks intent; the facilitator runs the command.

| Persona says | Facilitator runs |
|---|---|
| tap / click X | `click <ref for X>` (coordinate click as fallback if no ref) |
| scroll down / up | `mousewheel 0 100` / `mousewheel 0 -100` |
| type "…" into a field | `fill <ref> "…"` |
| go back | `go-back` |

## Dead-tap honesty

If the persona's described target isn't in the snapshot, the facilitator does **not** guess a different element. It re-screenshots unchanged — a real dead tap. Misses are findings, not problems to paper over.

## Scope fences

A new tab, an external domain, or anything that leaves the test target → **stop and flag the boundary**. Do not wander off-site.

## Sensitive data

- **Never enter real PII.** Use test credentials if provided.
- Login / OTP / payment with no test path → treat as a **wall**, record it as a blocker. Never fabricate an OTP or card detail.

## Static image path

For a user-provided image path: the image is viewed via vision (Read) — one screen, no navigation. For a first-click test, the persona describes where it would tap; the facilitator records the spot. Nothing is clicked.

## Limits

- Canvas-rendered apps (raw Figma prototypes) can't be driven — out of scope.
- Vision misreads small or low-contrast text; the coordinate fallback is approximate. These are accepted costs of seeing like a human.

Depends on: `playwright-cli` (`~/.claude/skills/playwright-cli`).
