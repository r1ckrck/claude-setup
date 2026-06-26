---
name: testing
description: Apply whenever the user wants to know if code works — "test this", "does it work", "write tests", "verify" — OR when something is broken — "debug this", "why is this failing", "it's throwing", "it's broken". Two modes. Verify writes tests for the paths the user can't eyeball (empty, null, invalid, error cases), runs the project's real test runner, and reports in plain language what passes and what's still untested, so "all green" never hides a blind spot. Debug runs a disciplined loop — reproduce the bug with a failing test, rank the likely causes, change one thing at a time, then lock the fix with a regression test. Detects the runner or offers to set one up (Vitest for JS/TS, pytest for Python) when none exists. Pairs with coding-standards and the /code-review + /verify + /run chain — tests prove the logic is right, /verify proves it actually runs.
---

# testing

This skill is the verification layer for someone who can't reliably eyeball whether code is correct. It proves the logic works by running tests, and then says so in **plain language** — so the user learns the code is right without reading a single test. A green checkmark they can't interpret is worth nothing; a sentence they can act on is the whole point.

It runs in **two modes**:

- **Verify** — *"I built this, is it right?"* Write tests, run them, report what holds and what's untested.
- **Debug** — *"It's broken, why?"* Run a disciplined loop to find the cause instead of guessing at a fix.

A test is the tool in both. In verify mode you write tests to prove good code right; in debug mode you write a *failing* test to corner a bug, then make it pass. Same muscle, pointed at a new thing versus a broken one.

## What this skill does

| Does | Doesn't |
|---|---|
| Writes tests for the behavior that matters | Find bugs by reading code — that's `/code-review` |
| Runs the project's real test runner | Run the actual app — that's `/verify` / `/run` |
| Reports a plain-language verdict + the gaps | Replace either of those — tests are one part of the proof |
| Debugs a known failure by reproducing it, then fixing | Hunt for unknown bugs in working code — that's `/code-review` |

## What deserves a test

- **Test behavior, not implementation** — assert what the function promises (output for input), not how it's wired inside. *Why:* a test tied to internals breaks on every refactor and proves nothing about correctness.
- **Concentrate on the paths the user can't eyeball** — empty input, `null`/missing, zero/negative, invalid or malformed data, the boundary, the error case. *Why:* the happy path is the one a designer often *can* picture; the silent bugs live in the cases they can't.
- **One baseline for the happy path** — confirm the normal case works, then spend the rest on edges. *Why:* you need the baseline, but it's the cheapest case — don't over-invest there.
- **Skip the trivial** — don't test the language, the framework, or a plain getter. *Why:* a test with no real failure mode is noise that slows the suite and lengthens the report.
- If you're unsure what could break, that uncertainty *is* the test list.

## The runner — use it or set it up

1. **Find the real runner first** — the nearest `package.json` with a `test` script, or a `vitest` / `jest` / `playwright` config, or `pytest.ini` / `pyproject.toml` for Python. If one exists, **use it as-is** — don't introduce a second framework.
2. **Match its conventions** — file names (`*.test.ts`, `tests/test_*.py`) and folder layout.
3. **If there is no runner, say so plainly and offer to set up a minimal standard one** — **Vitest** for JS/TS, **pytest** for Python — naming the one dependency it adds and the one `test` script it creates.
4. **Wait for the user's ok before installing anything.** Adding tooling silently is exactly the unrequested change `coding-standards` forbids.
5. **Don't co-opt the `slides` Playwright QA** (`slides/qa/qa.js`) — that's visual-regression for decks, a sibling verification tool, not a unit-test harness. Point there for visual/deck work; don't bolt unit tests onto it.

## Writing the tests

- **One concept per test** — each test checks a single behavior, and its name says which. *Why:* when it fails, the name alone tells the user what broke — no test-reading required. This is what makes the plain-language report possible.
- **Arrange–act–check shape** — set up the input, run the thing, check the result, in that order. *Why:* a test the user *could* read tells them what the code promises; it doubles as documentation.
- **Names are full sentences about behavior** — `rejects an email with no @`, not `test3`. *Why:* the test names become the report almost verbatim.
- **F.I.R.S.T., lightly** — Fast and Independent matter most (cheap to run every loop; any order, no shared state); Repeatable (no clock/network/random flake); Self-validating (passes or fails, never "go check the output yourself"). *Why:* a slow or flaky suite is one the user stops running, which kills the safety net.
- **No test-first mandate, no coverage target.** Tests are proof checked right after you write the code — not a ritual you perform before it.

## Report back in plain language

This is the point of the skill. Never hand the user raw runner output as the answer — translate it. Lead with the verdict; name what passed in plain words; **always name the gaps, even when everything's green**; point to the next step.

```
Verdict: <N pass / M fail> — <plain summary of what's proven>.
Passing: <behaviors in plain words, taken from the test names>
Failing: <what broke, in plain words> — <what it means for the user>
Gaps:    <what is NOT tested yet> — so green doesn't mean complete
Next:    <run /verify or /run to confirm it runs, or write the missing test>
```

Worked example:

```
Verdict: 3 pass, 0 fail — the email check works on the cases I tested.
Passing: accepts a normal valid email
         rejects a blank string
         rejects an address with no @
Gaps:    very long addresses and ones with a missing domain aren't covered.
         Green here means "these three hold," not "all email rules are correct."
Next:    want me to add the missing-domain test, or run /verify to confirm it
         works inside the real app?
```

A failure is reported as what it *means* ("blank input slips through — it should be rejected"), not "assertion failed, line 12." Raw stack traces are secondary; the verdict leads. (Debug mode has its own short report — see the loop below.)

## When something's broken — the debug loop

Verify mode assumes the code is meant to work. Debug mode is for when it doesn't. Don't read the code and guess a fix — run this loop. The whole thing rests on step 1.

1. **Build a yes/no signal first** — before touching the fix, make a fast, automatic check that answers "is the bug present?" Usually a **failing test**; otherwise **run it and watch** (a curl / CLI call or a quick browser script), or **replay a saved input** through the broken path. *Why:* once you can check for the bug on demand, finding the cause is mechanical — without that signal you're just staring at code.
2. **Reproduce the user's actual bug** — confirm the signal shows the symptom the user described, not a nearby one, and capture the exact symptom (message, wrong output). *Why:* the wrong bug gets the wrong fix.
3. **Rank 3–5 likely causes** — list several guesses, best first, each with the prediction that would confirm or kill it. On a **hard bug, show the list and wait** — the user often re-ranks it instantly ("I just changed that"). On a **small bug, proceed** and report the reasoning after. *Why:* settling on one guess anchors on the first plausible idea; ranking several beats it.
4. **Test one thing at a time** — probe one guess per change, never shotgun. Tag any temporary logging `[DEBUG-xxxx]` so cleanup is a single search. *Why:* changing two things hides which one mattered, and tagged logs never get left behind (no silent slop).
5. **Lock the fix with a regression test** — turn the reproduction into a failing test, apply the fix, watch it go red→green. If there's no honest place for a test that catches the *real* bug, say so plainly rather than fake a passing one. *Why:* the test is what stops the bug returning; a test that doesn't exercise the real path is false comfort.
6. **One-line post-mortem** — say what caused it, in a sentence. If the root cause is structural (no test seam, tangled code), flag it — a signal for a later cleanup, not this fix.

Debug report — plain language, same spirit as the verify report:

```
Bug:    <the symptom, in plain words>
Cause:  <the guess that proved right>
Fix:    <what changed, one line>
Guard:  <the regression test now covering it — or "no honest test seam: <why>">
```

(Perf problems are the one exception — for "it's slow," measure with a timing baseline first, since logs mislead there. Rare here; expand only if it comes up.)

## Where the textbook is wrong for us

| Textbook says | We do instead | Why |
|---|---|---|
| Write the test first (TDD), always | Write tests right after the code, while it's fresh | Test-first is a discipline for trained engineers; here it adds ceremony without the payoff |
| Chase 100% coverage | Cover what matters + the can't-eyeball paths | A coverage number is gamed easily and proves nothing; tested *behavior* does |
| A passing suite means it's done | Tests prove the logic; `/verify` proves it runs | Green logic in an app that won't start is still broken |
| Debug by reading code / logging everything | Build a yes/no signal first, then change one thing at a time | Log-and-grep is guessing; a repeatable signal makes the cause findable |

## Where this fits — the verify chain

| Tool | Answers | Boundary |
|---|---|---|
| `coding-standards` | is the code clean as written | Parent skill; `testing` is its "Tests & verification" bucket, expanded |
| **`testing`** (this) | does the logic do what it should | Owns writing/running tests + the plain-language verdict |
| `/code-review` | are there bugs in the diff | Finds bugs by reading; `testing` proves behavior by running — complementary |
| `/verify` + `/run` | does it actually run in the real app | The final gate; a green suite is not a substitute |
| `code-simplifier` | is it tidy | Runs earlier in the chain; unrelated to test logic |

`testing` produces the "tests pass" proof inside `coding-standards`' after-coding chain (`code-simplifier` → `/code-review` → tests pass → `/verify` + `/run`). It runs the real runner; it never reimplements `/code-review`'s bug-finding or `/run`'s app-launching. **Tests answer "does the logic do what it should"; `/verify` answers "does it actually run." Both, not either.**
