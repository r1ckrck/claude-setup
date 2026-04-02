#!/usr/bin/env python3
"""
Diagram Autoresearch — Self-improving prompt optimization.

Karpathy autoresearch pattern applied to diagram generation:
1. Generate 10 diagrams with current prompt (Gemini image gen)
2. Evaluate each against 4 criteria via Claude vision → score out of 40
3. Compare against best score — keep winner
4. Mutate the winner prompt for next cycle
5. Repeat every 2 minutes

Usage:
    python3 diagram_autoresearch.py              # Continuous loop
    python3 diagram_autoresearch.py --once        # Single cycle
    python3 diagram_autoresearch.py --cycles 5    # Run N cycles
"""

import argparse
import base64
import json
import os
import random
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ─── Config ───────────────────────────────────────────────────────────────────

GEMINI_KEY = os.getenv("NANO_BANANA_API_KEY")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")

GEN_MODEL = "gemini-2.5-flash-image"
EVAL_MODEL = "claude-sonnet-4-6"
MUTATE_MODEL = "claude-sonnet-4-6"

BASE_DIR = Path(__file__).resolve().parent / "data"
PROMPT_FILE = BASE_DIR / "prompt.txt"
BEST_PROMPT_FILE = BASE_DIR / "best_prompt.txt"
STATE_FILE = BASE_DIR / "state.json"
RESULTS_FILE = BASE_DIR / "results.jsonl"
DIAGRAMS_DIR = BASE_DIR / "diagrams"

BATCH_SIZE = 10
CYCLE_SECONDS = 120
MAX_GEN_WORKERS = 3
MAX_EVAL_WORKERS = 5

# ─── Diagram Topics (diverse structures) ─────────────────────────────────────

TOPICS = [
    "CI/CD pipeline: code commit flows to build, then test, then deploy, then monitor",
    "Machine learning workflow: data collection to preprocessing to training to evaluation to deployment",
    "User authentication: login form to validation to JWT token to access granted",
    "Microservices: API gateway connecting to user service, payment service, and notification service",
    "ETL pipeline: extract from databases, transform with business rules, load into warehouse",
    "Email marketing funnel: capture lead to nurture sequence to segment to convert to retain",
    "Content creation pipeline: research to outline to draft to edit to publish",
    "Customer support flow: ticket submitted to triage to assign to resolve to follow up",
    "API request lifecycle: client request to load balancer to app server to database to response",
    "Git workflow: feature branch to pull request to code review to merge to deploy",
    "OAuth flow: user to app to authorization server to resource server",
    "Notification system: event trigger to queue to router splitting to email, push, and SMS channels",
    "Search engine pipeline: crawl pages to index to rank to serve results",
    "Video processing: upload to transcode to generate thumbnail to CDN to stream",
    "A/B testing: hypothesis to experiment design to traffic split to measure to analyze",
    "Payment processing: cart to checkout to payment gateway to bank to confirmation",
    "Recommendation engine: user activity to features to model to ranked results to display",
    "Monitoring stack: metrics collection to aggregation to alerting to dashboard",
    "Caching strategy: request to cache check then hit path or miss path to origin server",
    "Log aggregation: app logs to collector to parser to storage to visualization",
    "Message queue: producer to exchange to routing to queues to consumers",
    "Blue-green deploy: load balancer switching between blue and green environments",
    "SSO architecture: identity provider connecting to multiple service providers via tokens",
    "Data lake: raw ingestion to cataloging to processing to curated zone to analytics",
    "Serverless flow: API request to function trigger to compute to storage to response",
    "Container orchestration: registry to scheduler to node to pod to service mesh",
    "GraphQL architecture: client query to resolver to data sources to merged response",
    "Event sourcing: command to event store to projections to read models to query",
    "Feature flag system: config to evaluation engine to user targeting to rollout",
    "Rate limiting: request to counter check to allow or reject to update counter",
]

# ─── Eval Prompt ──────────────────────────────────────────────────────────────

EVAL_PROMPT = """You are evaluating a diagram image against 4 strict criteria. Examine the image carefully.

Criteria:
1. LEGIBLE_AND_GRAMMATICAL: ALL text in the diagram is clearly readable — no garbled, overlapping, blurry, or cut-off text. All words are real English words spelled correctly. Sentences/phrases are grammatically correct.

2. PASTEL_COLORS: The diagram uses ONLY soft pastel colors for fills (light purple, light blue, light green, light pink, light yellow, light teal, etc). No bright, saturated, neon, or dark-colored fills. White background counts as passing.

3. LINEAR_LAYOUT: The diagram flows in ONE clear linear direction — either strictly left-to-right OR strictly top-to-bottom. Not circular, radial, scattered, hub-and-spoke, or multi-directional.

4. NO_NUMBERS: The diagram contains ZERO numbers, step numbers, ordinals (1st, 2nd, 3rd), sequence indicators (Step 1, Phase 2), or any numerical ordering. Only text labels allowed.

Rate each criterion as PASS (true) or FAIL (false). Be strict.

Respond in this exact JSON format:
{"legible_and_grammatical": true, "pastel_colors": true, "linear_layout": true, "no_numbers": true, "failures": []}

If any criterion fails, set it to false and add a brief description to the failures array. Example:
{"legible_and_grammatical": false, "pastel_colors": true, "linear_layout": true, "no_numbers": false, "failures": ["Text 'Procssing' is misspelled", "Contains 'Step 1', 'Step 2' labels"]}"""

# ─── Mutation Prompt ──────────────────────────────────────────────────────────

MUTATION_TEMPLATE = """You are optimizing a text-to-image prompt for generating technical diagrams. The prompt is sent to Gemini's image generation model. Your goal: modify it so generated diagrams consistently pass ALL 4 evaluation criteria.

CURRENT PROMPT:
---
{current_prompt}
---

LAST BATCH RESULTS ({score}/40):
- Legible & grammatical: {leg_rate}/10
- Pastel colors: {col_rate}/10
- Linear layout: {lin_rate}/10
- No numbers/ordinals: {num_rate}/10

COMMON FAILURES:
{failures}

BEST SCORE SO FAR: {best_score}/40

RULES FOR YOUR MODIFICATION:
- Keep the core whiteboard/hand-drawn aesthetic
- For any criterion below 8/10, add VERY explicit constraints
- If numbers keep appearing: emphasize "ABSOLUTELY NO numbers, step numbers, ordinals, sequence indicators, or numerical labels of any kind"
- If layout isn't linear: specify "MUST flow in a single straight line from left to right" or "from top to bottom"
- If text is garbled: add "All text must be real, correctly spelled English words"
- If colors aren't pastel: list exact colors to use and explicitly ban dark/saturated fills
- Be specific and imperative — image models respond to direct commands
- Keep prompt under 400 words
- Return ONLY the new prompt text — no explanation, no markdown fences"""

# ─── Helpers ──────────────────────────────────────────────────────────────────


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"best_score": -1, "run_number": 0}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def load_prompt() -> str:
    return PROMPT_FILE.read_text().strip()


def save_prompt(prompt: str):
    PROMPT_FILE.write_text(prompt)


# ─── Generation (Gemini) ─────────────────────────────────────────────────────


def generate_one(gemini_client, prompt: str, topic: str, output_path: Path) -> bool:
    """Generate a single diagram via Gemini image generation."""
    from google.genai import types

    full_prompt = f"{prompt}\n\nDiagram to create: {topic}"
    try:
        response = gemini_client.models.generate_content(
            model=GEN_MODEL,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(part.inline_data.data)
                return True
        return False
    except Exception as e:
        print(f"    GEN ERROR: {e}")
        return False


# ─── Evaluation (Claude) ─────────────────────────────────────────────────────


def evaluate_one(anthropic_client, image_path: Path) -> dict | None:
    """Evaluate a single diagram against 4 criteria via Claude vision."""
    image_bytes = image_path.read_bytes()
    b64 = base64.b64encode(image_bytes).decode()

    try:
        response = anthropic_client.messages.create(
            model=EVAL_MODEL,
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": b64,
                            },
                        },
                        {"type": "text", "text": EVAL_PROMPT},
                    ],
                }
            ],
        )
        text = response.content[0].text.strip()
        # Extract JSON from response (handle markdown fences)
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        return json.loads(text)
    except Exception as e:
        print(f"    EVAL ERROR: {e}")
        return None


# ─── Mutation (Claude) ───────────────────────────────────────────────────────


def mutate_prompt(
    anthropic_client,
    current_prompt: str,
    eval_results: list[dict],
    best_score: int,
) -> str:
    """Use Claude to improve the prompt based on failure analysis."""
    n = len(eval_results)
    leg = sum(1 for r in eval_results if r.get("legible_and_grammatical"))
    col = sum(1 for r in eval_results if r.get("pastel_colors"))
    lin = sum(1 for r in eval_results if r.get("linear_layout"))
    num = sum(1 for r in eval_results if r.get("no_numbers"))
    score = leg + col + lin + num

    all_failures = []
    for r in eval_results:
        for f in r.get("failures", []):
            all_failures.append(f)

    # Deduplicate and limit
    unique_failures = list(dict.fromkeys(all_failures))[:20]
    failures_text = "\n".join(f"- {f}" for f in unique_failures) if unique_failures else "- None"

    mutation_prompt = MUTATION_TEMPLATE.format(
        current_prompt=current_prompt,
        score=score,
        leg_rate=leg,
        col_rate=col,
        lin_rate=lin,
        num_rate=num,
        best_score=best_score,
        failures=failures_text,
    )

    response = anthropic_client.messages.create(
        model=MUTATE_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": mutation_prompt}],
    )
    return response.content[0].text.strip()


# ─── Main Cycle ──────────────────────────────────────────────────────────────


def run_cycle(gemini_client, anthropic_client, state: dict) -> dict:
    """Run one autoresearch optimization cycle."""
    run_num = state["run_number"] + 1
    state["run_number"] = run_num
    run_dir = DIAGRAMS_DIR / f"run_{run_num:03d}"
    run_dir.mkdir(parents=True, exist_ok=True)

    prompt = load_prompt()
    topics = random.sample(TOPICS, min(BATCH_SIZE, len(TOPICS)))

    print(f"\n{'='*60}")
    print(f"RUN {run_num} | {datetime.now().strftime('%H:%M:%S')} | Best: {state['best_score']}/40")
    print(f"{'='*60}")

    # ── Generate ──────────────────────────────────────────────────
    print(f"\n  Generating {BATCH_SIZE} diagrams...")
    generated: list[tuple[int, str, Path]] = []

    with ThreadPoolExecutor(max_workers=MAX_GEN_WORKERS) as pool:
        futures = {}
        for i, topic in enumerate(topics):
            out = run_dir / f"diagram_{i:02d}.png"
            f = pool.submit(generate_one, gemini_client, prompt, topic, out)
            futures[f] = (i, topic, out)

        for f in as_completed(futures):
            i, topic, out = futures[f]
            try:
                ok = f.result()
            except Exception as e:
                ok = False
                print(f"    [{i+1}/{BATCH_SIZE}] ERROR: {e}")
            if ok:
                generated.append((i, topic, out))
                print(f"    [{i+1}/{BATCH_SIZE}] generated: {topic[:50]}")
            else:
                print(f"    [{i+1}/{BATCH_SIZE}] FAILED: {topic[:50]}")

    if not generated:
        print("  ERROR: No diagrams generated. Skipping cycle.")
        save_state(state)
        return state

    # ── Evaluate ──────────────────────────────────────────────────
    print(f"\n  Evaluating {len(generated)} diagrams via Claude...")
    eval_results: list[dict] = []

    with ThreadPoolExecutor(max_workers=MAX_EVAL_WORKERS) as pool:
        futures = {}
        for i, topic, path in generated:
            f = pool.submit(evaluate_one, anthropic_client, path)
            futures[f] = (i, topic, path)

        for f in as_completed(futures):
            i, topic, path = futures[f]
            try:
                result = f.result()
            except Exception as e:
                result = None
                print(f"    [{i+1}] EVAL ERROR: {e}")

            if result:
                eval_results.append(result)
                criteria_pass = sum([
                    result.get("legible_and_grammatical", False),
                    result.get("pastel_colors", False),
                    result.get("linear_layout", False),
                    result.get("no_numbers", False),
                ])
                fails = result.get("failures", [])
                print(f"    [{i+1}] {criteria_pass}/4 | {'; '.join(fails) if fails else 'all pass'}")
            else:
                eval_results.append({
                    "legible_and_grammatical": False,
                    "pastel_colors": False,
                    "linear_layout": False,
                    "no_numbers": False,
                    "failures": ["eval_error"],
                })
                print(f"    [{i+1}] 0/4 | eval failed")

    # ── Score ─────────────────────────────────────────────────────
    leg = sum(1 for r in eval_results if r.get("legible_and_grammatical"))
    col = sum(1 for r in eval_results if r.get("pastel_colors"))
    lin = sum(1 for r in eval_results if r.get("linear_layout"))
    num = sum(1 for r in eval_results if r.get("no_numbers"))
    score = leg + col + lin + num

    print(f"\n  SCORE: {score}/40")
    print(f"    Legible:    {leg}/10")
    print(f"    Pastel:     {col}/10")
    print(f"    Linear:     {lin}/10")
    print(f"    No numbers: {num}/10")

    # ── Log ───────────────────────────────────────────────────────
    log_entry = {
        "run": run_num,
        "timestamp": datetime.now().isoformat(),
        "score": score,
        "max": 40,
        "criteria": {"legible": leg, "pastel": col, "linear": lin, "no_numbers": num},
        "prompt_len": len(prompt),
        "generated": len(generated),
    }
    with open(RESULTS_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    # ── Keep or discard ───────────────────────────────────────────
    if score > state["best_score"]:
        state["best_score"] = score
        BEST_PROMPT_FILE.write_text(prompt)
        print(f"\n  NEW BEST! {score}/40 (was {state.get('best_score', -1)})")
        print(f"  Saved to: {BEST_PROMPT_FILE}")
    else:
        print(f"\n  No improvement ({score} vs best {state['best_score']})")
        # Revert to best prompt as mutation base
        if BEST_PROMPT_FILE.exists():
            print("  Reverting to best prompt for next mutation")

    # ── Mutate ────────────────────────────────────────────────────
    if score < 40:
        print("\n  Mutating prompt...")
        # Always mutate from the best known prompt
        base_prompt = BEST_PROMPT_FILE.read_text().strip() if BEST_PROMPT_FILE.exists() else prompt
        new_prompt = mutate_prompt(anthropic_client, base_prompt, eval_results, state["best_score"])
        save_prompt(new_prompt)
        print(f"  New prompt ({len(new_prompt)} chars):")
        # Print first 200 chars
        preview = new_prompt[:200].replace("\n", " ")
        print(f"    {preview}...")
    else:
        print("\n  PERFECT 40/40! Prompt fully optimized.")

    save_state(state)
    return state


# ─── Entry Point ──────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Diagram autoresearch loop")
    parser.add_argument("--once", action="store_true", help="Run a single cycle")
    parser.add_argument("--cycles", type=int, default=0, help="Run N cycles (0=infinite)")
    args = parser.parse_args()

    if not GEMINI_KEY:
        print("ERROR: NANO_BANANA_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    if not ANTHROPIC_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    # Lazy imports
    from google import genai
    import anthropic

    BASE_DIR.mkdir(parents=True, exist_ok=True)
    DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)

    gemini_client = genai.Client(api_key=GEMINI_KEY)
    anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    state = load_state()

    print("Diagram Autoresearch")
    print(f"  Gen model:    {GEN_MODEL}")
    print(f"  Eval model:   {EVAL_MODEL}")
    print(f"  Mutate model: {MUTATE_MODEL}")
    print(f"  Batch size:   {BATCH_SIZE}")
    print(f"  Cycle:        {CYCLE_SECONDS}s")
    print(f"  State:        run {state['run_number']}, best {state['best_score']}/40")

    if args.once:
        run_cycle(gemini_client, anthropic_client, state)
        return

    max_cycles = args.cycles or float("inf")
    i = 0
    while i < max_cycles:
        start = time.time()
        try:
            state = run_cycle(gemini_client, anthropic_client, state)
        except Exception as e:
            print(f"\n  CYCLE ERROR: {e}")
            traceback.print_exc()
        elapsed = time.time() - start
        i += 1

        if i < max_cycles:
            wait = max(0, CYCLE_SECONDS - elapsed)
            if wait > 0:
                print(f"\n  Waiting {wait:.0f}s until next cycle...")
                time.sleep(wait)
            else:
                print(f"\n  Cycle took {elapsed:.0f}s (>{CYCLE_SECONDS}s budget)")

    print(f"\nDone. Best score: {state['best_score']}/40")
    if BEST_PROMPT_FILE.exists():
        print(f"Best prompt: {BEST_PROMPT_FILE}")


if __name__ == "__main__":
    main()
