# Transcripts scaffold

Companion to the processed report. Verbatim conversations + debriefs, no analysis. Read by auditors who want to verify a claim in the main report.

## File header

```markdown
# Transcripts — <Test type>, <descriptor>

**Test:** <test-type>
**Stimulus:** <path or "—" for interviews>
**Date:** YYYY-MM-DD
**Personas (locked order):** Arsheen → Danish → Mohammed → Seema → Akeela → Himanshu → Salman → Sonal
**Protocol:** Parallel + lockstep, adaptive multi-turn
**Run verdict for all 8:** valid / mixed / etc.
```

## Per-persona block

One block per persona in **locked order**:

```markdown
## N. <Name> — <segment>, <age>, <city>

**Natural goal given:** *"<the framing the moderator gave>"*

**In-character transcript:**

​```
[Turn 1 — open]
<persona reply>

[Round 2: <topic of probe>]
<persona reply>

[...more rounds...]
​```

**[DEBRIEF]:**

​```
<persona's out-of-character debrief>
​```

**Run verdict:** valid / give-up / blocked / invalid
```

Eight blocks total, separated by `---`.

## File location + naming

```
reports/<run>/<stem>_transcripts.md
```

Lives at the run-folder root (not in `artifacts/`) — this file is a primary consumer artifact, not a build input.
