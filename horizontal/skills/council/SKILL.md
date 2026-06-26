---
name: council
description: Run a decision through six adversarial advisors instead of getting a single agreeable answer. Use whenever the user says "ask the council:" or "council this:" followed by a question or decision — and reach for it any time the user is weighing a build/no-build, which-approach, or is-this-worth-it call and wants a real verdict rather than encouragement. Six subagents each attack from a fixed conflicting angle, then a chairman returns one verdict and one next move.
allowed-tools: Task, Read
---

# Council

Breaks the yes-man reflex. Ask if an idea is good and you get five reasons it's brilliant; ask if it's bad and five reasons to kill it — same idea, opposite framing, both useless. The council forces the issue: six advisors, each with a fixed attack vector and a built-in refusal, so none can just agree with you. A chairman then weighs them into a single call.

The advisors run as parallel subagents. Their personas live in `advisors/` and load only inside each subagent — this file stays lean.

## When to use

| Trigger | Action |
|---|---|
| Message contains `ask the council:` or `council this:` | Run the workflow below on the text after the colon |
| User is weighing a build/approach/worth-it decision and wants a hard verdict | Offer the council, or just run it |

Append `--deep` (or say "deep council") to run the heavier peer-review round — see step 6.

## The six advisors

| File | Advisor | Attacks from |
|---|---|---|
| `advisors/01-killer.md` | Killer | the fatal flaw — why it fails |
| `advisors/02-first-principles.md` | First Principles | the real problem under the question |
| `advisors/03-expansionist.md` | Expansionist | the bigger version you're avoiding |
| `advisors/04-craftsman.md` | Craftsman | the taste / restraint bar |
| `advisors/05-outsider.md` | Outsider | the dumb question you stopped asking |
| `advisors/06-gatekeeper.md` | Gatekeeper | what saying yes steals from your other loops |

**Skill root.** Every path below is relative to this skill's own folder — the directory that contains this `SKILL.md`. Resolve that directory's absolute path once and call it `{SKILL_DIR}`; build the advisor and chairman paths under it. Don't hardcode a machine path — this lets the skill run from any location or device.

## Workflow

1. **Extract the question.** Take everything after `ask the council:` / `council this:` **verbatim** — don't clean it up, rephrase it, or fill in gaps. The Outsider advisor judges the raw phrasing; rewriting it defeats the point. (Strip a trailing `--deep` flag if present and note it for step 6.)

2. **Fan out all six advisors in ONE turn.** Issue six `Task` calls together (`subagent_type: general-purpose`) so they run in parallel. Use this wrapper for each — the only thing that changes is the file:

   > Read `{SKILL_DIR}/advisors/01-killer.md` and follow it exactly. The question before the council:
   > ```
   > <verbatim question>
   > ```
   > Return ONLY your formatted verdict block — no preamble, no markdown fence, nothing after.

   Repeat for `02-first-principles.md` through `06-gatekeeper.md`. The persona, rules, and output format are NOT in this prompt — the subagent reads them from its file. That's what keeps every spawn cheap.

3. **Collect the six verdicts.** If a reply has leading chatter before its `… VERDICT:` line, drop the chatter. If an advisor returns empty or malformed, note "(advisor failed)" and proceed with the rest — the chairman works with the survivors.

4. **Run the chairman.** One more `Task` call:

   > Read `{SKILL_DIR}/chairman.md` and follow it exactly. The advisors' verdicts:
   > ```
   > <all six verdict blocks, in order>
   > ```
   > The original question:
   > ```
   > <verbatim question>
   > ```
   > Return ONLY the CHAIRMAN VERDICT block.

5. **Output.** Print, in this order:
   - **The roster** — one line per advisor: its `VERDICT:` line only. This shows the disagreement at a glance without a wall of text.
   - **The chairman block** in full.

   Keep the full advisor reasoning in reserve — show it only if the user asks to see a given advisor.

6. **`--deep` (optional, between steps 3 and 4).** Only when the user asked for it. Run a second six-`Task` round: hand each advisor all six verdicts and ask for a 1-2 sentence critique of the others, in its own voice. Then pass the six verdicts **and** the six critiques to the chairman in step 4. The chairman format is unchanged — it just has more signal to discount a weak voice. Default runs skip this entirely.

## Notes

- The council answers in chat. It writes nothing to disk.
- Don't summarize or soften the advisors before the chairman sees them — conflict is the input the chairman needs.
- If the question is genuinely empty (nothing after the colon), ask what to put before the council rather than running it on air.
