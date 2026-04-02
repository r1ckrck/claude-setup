---
name: autoresearch-diagrams
description: Self-improving diagram prompt optimization using the Karpathy autoresearch pattern. Generates batches of diagrams, evaluates via Claude vision, mutates the prompt, keeps winners. Includes a live web dashboard.
allowed-tools: Read, Bash, Glob, Grep
---

# Autoresearch Diagrams — Self-Improving Prompt Optimization

## What It Does
Applies the Karpathy autoresearch pattern to diagram generation prompts. Every 2 minutes:
1. Generates 10 diagrams with the current prompt (Gemini image gen)
2. Evaluates each against 4 criteria via Claude Sonnet vision (score out of 40)
3. Keeps the prompt if it beats the best score, discards otherwise
4. Mutates the best prompt to try to improve further
5. Logs everything to JSONL for tracking

## Eval Criteria (4 per image, 40 max per batch)
1. **Legible & grammatical** — all text readable, correctly spelled
2. **Pastel colors** — soft pastel fills only, no saturated/dark colors
3. **Linear layout** — strictly left-to-right or top-to-bottom
4. **No numbers** — zero digits, ordinals, or step numbers

## Quick Start

```bash
# Run continuous loop (every 2 min)
python3 .claude/skills/autoresearch-diagrams/autoresearch.py

# Single cycle (test)
python3 .claude/skills/autoresearch-diagrams/autoresearch.py --once

# Run N cycles
python3 .claude/skills/autoresearch-diagrams/autoresearch.py --cycles 10

# Start the live dashboard
python3 .claude/skills/autoresearch-diagrams/dashboard.py --port 8501
# Then open http://localhost:8501
```

## Environment
Requires in `.env`:
```
NANO_BANANA_API_KEY=your_gemini_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

Dependencies: `google-genai`, `anthropic`, `python-dotenv`

## File Structure

```
.claude/skills/autoresearch-diagrams/
  SKILL.md              # This file
  autoresearch.py       # Main generate -> eval -> mutate loop
  dashboard.py          # Live web dashboard (Chart.js)
  data/
    prompt.txt          # Current prompt being optimized
    best_prompt.txt     # Best prompt found so far
    state.json          # Loop state (run number, best score)
    results.jsonl       # Append-only experiment log
    diagrams/
      run_001/          # 10 diagrams per run
      run_002/
      ...
```

## Models
- **Generation**: `gemini-2.5-flash-image` (Gemini native image gen)
- **Evaluation**: `claude-sonnet-4-6` (vision + structured JSON output)
- **Mutation**: `claude-sonnet-4-6` (prompt rewriting based on failure analysis)

## Dashboard
Serves at `http://localhost:8501` with:
- 4 stat cards (current best, baseline, improvement %, runs/kept)
- Score-over-time chart with keep/discard dot coloring
- Per-criterion breakdown charts (legible, pastel, linear, no numbers)
- Run history table
- Current best prompt display
- Auto-refreshes every 15s

## Cost
- ~$0.03-0.05 per diagram generation (Gemini Flash)
- ~$0.01 per eval (Sonnet vision, small image + short response)
- ~$0.01 per mutation (Sonnet text)
- **Total: ~$0.40-0.60 per cycle (10 diagrams)**
- At 2-min intervals: ~$12-18/hour
