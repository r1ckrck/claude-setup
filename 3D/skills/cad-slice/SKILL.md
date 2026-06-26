---
name: cad-slice
description: Slice a CAD model along an X/Y/Z axis and plot the cross-section in world-coordinate millimeters. Use to verify internal geometry, wall thickness, gaps, clearances, and exact feature placement that a 3D iso render foreshortens or hides. Complements the cad skill's snapshot (3D vision) and inspect (numeric facts) — this is the precision visual channel. Triggers: "slice the model", "cross-section at X/Y/Z=...", "check the wall thickness at...", "is there a gap at...", "section view", "what does the inside look like at...".
---

# CAD slicing — world-coordinate cross-sections

## Purpose

3D iso renders foreshorten. Small but critical geometry — a 0.5 mm gap, a wall that thinned, a feature that landed 1 mm off — is easy to miss in a perspective render. Slicing the model along an axis at an exact coordinate and plotting the cross-section in world millimeters makes those features unambiguous: positions are read straight off the labeled axes.

This is the **primary precision-verification channel**. Pair it with the `cad` skill's `snapshot` (overall shape, vision) and `inspect` (numeric facts, no vision). Use slices whenever the question is about an interior, a thickness, a clearance, or whether two features meet at a specific coordinate.

## When to use

- Confirming wall thickness at a specific coordinate.
- Detecting a gap, overlap, or non-contact between features.
- Checking that a feature (hole, lip, pocket, boss) lands at the intended world coordinate.
- Inspecting internal geometry that the outer surface hides.
- Any spatial claim the workspace expresses in coordinate-anchored language (e.g. "the strip at Z=32–35, Y=7.5–8.5").

Prefer `snapshot` instead when the question is "does the overall shape look right?". Prefer `inspect` when a single number answers it.

## Tool

```bash
python .claude/skills/cad-slice/scripts/slice.py <input> --axis <x|y|z> [--at <mm> ...] -o <out.png> [--grid <mm>]
```

- `<input>` — a STEP/STP file (tessellated via build123d) or any trimesh-loadable mesh (STL/GLB/3MF/OBJ). Prefer the primary `.step` artifact.
- `--axis` — the slice-plane normal:
  - `x` → plots world **Y vs Z** (side view)
  - `y` → plots world **X vs Z** (front view)
  - `z` → plots world **X vs Y** (top-down)
- `--at` — one or more world coordinates on that axis (mm). Omit to slice at the bounding-box center. Multiple values produce side-by-side panels — sweep across an axis to see how a feature evolves.
- `--grid` — tick + grid spacing in mm (default 10), matching the workspace's 10 mm axis-label convention.

Use the project venv interpreter (`.venv/bin/python`), not bare `python`.

## Examples

```bash
# Side view at X=0 (the YZ midplane)
python .claude/skills/cad-slice/scripts/slice.py part.step --axis x --at 0 -o slices/x0.png

# Sweep three top-down sections up the Z axis
python .claude/skills/cad-slice/scripts/slice.py part.step --axis z --at 2 16 32 -o slices/z_sweep.png

# Front-wall thickness through Z at Y=8
python .claude/skills/cad-slice/scripts/slice.py part.step --axis y --at 8 -o slices/y8.png
```

## Reading the output

Each panel is a true world-coordinate plot: equal aspect, a grid every `--grid` mm, and the world origin drawn as faint cross-hairs. Read feature positions and thicknesses directly off the labeled axes. A panel labelled "no intersection" means the slice plane missed all geometry at that coordinate — move `--at` into the model's bounds.
