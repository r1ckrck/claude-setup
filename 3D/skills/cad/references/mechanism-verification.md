# Mechanism verification — does the geometry realize the motion

Read this file when an assembly has parts that **move relative to each other** (a hinge, slider, swivel, axle, gear, linkage — anything with a degree of freedom). It catches one specific failure: a declared joint with no physical feature realizing it. A single part, or an assembly where every contact is fixed or fastened, is out of scope — the check is a no-op there.

## Contents

- Why it exists
- Interface table (the artifact)
- The gate
- Confirm with existing tools
- Optional joint reconciliation
- Report

## Why it exists

Static renders, slices, and dimension checks confirm geometry and fit, not mechanism. Two parts whose faces merely touch look identical to a real journaled joint in any still view, and a posable URDF will rotate a joint whether or not the geometry supports it. So a "swivel" can ship as a post butting against a flat plate — coincident faces, nothing connecting or retaining them. This gate makes each degree of freedom explicit and checkable.

## Interface table (the artifact)

For an assembly with relative motion, keep a small interface table in the **project's** own notes (its `CLAUDE.md` or a design doc — not in this skill). One row per place two parts meet:

| Interface | Parts (A–B) | Contact | Detail | Realizing feature | Verified |
|---|---|---|---|---|---|
| hinge | door–frame | moving | rotate about Y | knuckle bore + pin + end caps | slice Y@0 |
| slide | drawer–case | moving | translate along X | rail in groove + end stop | inspect measure |
| seam | case–lid | fastened | M3×4 | 4× Ø3.4 thru + bosses | inspect refs |
| body | wall–wall | fixed | printed as one | — | — |

- **Contact** is one of `fixed` (one rigid body / printed together), `fastened` (screws/bolts — name them), or `moving` (a degree of freedom — name the axis).
- **Realizing feature** is REQUIRED for every `moving` row.

## The gate

Every `moving` row must name three things that are actually present in the STEP:

1. **Journal** — a bore, sleeve, groove, or race the motion runs in. A flat face-to-face butt is NOT a journal.
2. **Member** — the pin / kingpin / shaft / axle / rail that occupies the journal.
3. **Retention** — what stops the parts separating: a head, shoulder, nut, clip, end cap, or captured race.

A `moving` row with any of the three blank — or a "journal" that is really two flat faces touching — is the bug. Fix the geometry, not the table.

## Confirm with existing tools

No new tooling. Confirm each `moving` row's realizing feature is real:

- `inspect refs --positioning` — locate the bore/groove and the member on the joint axis.
- `inspect measure` across the journal — expect a running clearance between member and bore, not 0 mm of solid butt; measure member-end to retainer to confirm axial capture.
- `$cad-slice` along the joint axis — the decisive check. A real joint shows a bored (or grooved) member with a clearance gap; a fake one shows two solids meeting on a flat line.

## Optional joint reconciliation

WHEN the project also has a URDF or build123d source joints, the table's `moving` rows should reconcile 1:1 with the non-fixed joints (`continuous`/`revolute`/`prismatic`, or `RevoluteJoint`/`LinearJoint`/`CylindricalJoint`/`BallJoint`). A non-fixed joint with no matching realizing feature is the same bug seen from the kinematic side. This is corroboration only — the gate runs on the table alone and never requires a URDF to exist.

## Report

Add the result to the validation report (see `inspection-and-validation.md`):
`Mechanism: <N moving interfaces, all realized | which row failed | n/a — static>`.
