# CadQuery — parametric, code-first

How I work with Claude Code on **functional FDM parts authored in CadQuery (Python)**. Hobbyist desktop FDM, output is STL/3MF for a slicer. Code-first: every dimension is a parameter at the top of a `.py` script, geometry is rebuilt from scratch on every run.

This folder is documentation only — no project files. For a real project, copy `CLAUDE.md.template` into a new repo as `CLAUDE.md`.

## Files

| File | Purpose |
|---|---|
| `README.md` | This overview. |
| `CLAUDE.md.template` | Drop into a new CadQuery project repo as `CLAUDE.md`. |

## Why CadQuery over Blender / OpenSCAD / Fusion

| | CadQuery | OpenSCAD | Fusion 360 | Blender |
|---|---|---|---|---|
| Authoring | Python | Custom DSL | GUI + timeline | Mesh, GUI |
| Parametric | Yes, every run | Yes | Yes (history) | No |
| pip-installable | Yes | No (separate app) | No (cloud app) | No |
| Booleans on real solids | OpenCASCADE B-rep | CGAL | Parasolid | Mesh booleans (fragile) |
| Fits Claude's edit-loop | Excellent | Excellent | Poor (GUI) | Via MCP only |

CadQuery gives Claude a tight **edit a `.py` → run → inspect STL → re-edit** loop with no live application required. Source lives in git, every parameter is reviewable in a diff.

## Setup — one time per project

```bash
# CadQuery's docs say Python 3.10–3.12 (OCC kernel wheels).
# 3.13 works in practice via cadquery 2.7 — bump deliberately if the wheels regress.
python3.12 -m venv .venv && source .venv/bin/activate

pip install cadquery trimesh pyrender Pillow numpy
```

`cadquery` is the geometry kernel (OpenCASCADE under the hood). `trimesh` + `pyrender` + `Pillow` drive the headless preview-and-repair loop. No display server needed; pyrender renders offscreen.

If `cadquery` fails to install:

```bash
# Officially recommended fallback
conda install -c cadquery -c conda-forge cadquery

# Or pre-built wheels
pip install cadquery --find-links https://github.com/CadQuery/CadQuery/releases
```

## The skill — pre-built CadQuery toolkit for Claude

The community skill **`parametric-3d-printing`** (a.k.a. `cad-skill`) ships ready-made helpers Claude reuses across projects. Install once globally:

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/flowful-ai/cad-skill ~/.claude/skills/parametric-3d-printing
```

What it provides:

| File | What it does |
|---|---|
| `SKILL.md` | Workflow Claude follows: requirements → base shape → features → finish, with previews between phases. |
| `preview.py` | Headless STL → multi-view PNG renderer (trimesh + pyrender). `--strict` fails on non-watertight meshes. |
| `run_cadquery_model.py` | Subprocess wrapper: runs a `.py`, captures errors, optionally renders, emits JSON. Lets Claude self-correct in a loop. |
| `mesh_io.py` | STL loading + validation. |
| `stl_to_3mf.py` | STL → 3MF for Bambu Studio / PrusaSlicer. |
| `design-review.md` | Visual inspection + printability checklist. |

> **Don't duplicate these.** When a project's CLAUDE.md says "render a preview," it means *call `~/.claude/skills/parametric-3d-printing/preview.py`*, not write a new renderer.

## The build → render → compare loop

The whole workflow is structured around this:

1. **Edit** `<part>.py` (parametric CadQuery script).
2. **Run** it → exports `<part>.stl`. Always end the script with a **trimesh repair pass** (see below).
3. **Render** a preview PNG via `preview.py`.
4. **Compare** side-by-side with reference images / earlier renders / the visual target.
5. **Iterate.**

One-shot driver:

```bash
python3 ~/.claude/skills/parametric-3d-printing/run_cadquery_model.py path/to/part.py --preview --strict
```

Standalone preview when the STL already exists:

```bash
python3 ~/.claude/skills/parametric-3d-printing/preview.py path/to/part.stl out.png --views multi --strict
python3 ~/.claude/skills/parametric-3d-printing/preview.py path/to/part.stl out.png --views iso
```

## Watertight repair — the trimesh tail

CadQuery's per-face STL mesher leaves micro-gaps at face boundaries. These show up as **boundary edges** (1-face), not real holes. Slicers usually auto-repair, but you want the file watertight before handoff. Every script ends with:

```python
import cadquery as cq, trimesh

cq.exporters.export(result, "part.stl",
                    tolerance=0.005, angularTolerance=0.05)

m = trimesh.load("part.stl")
m.merge_vertices(digits_vertex=4)
m.fill_holes()
m.fix_normals()
m.export("part.stl")
print("watertight:", m.is_watertight, "open edges:", len(m.edges_unique) - len(m.edges_sorted)//2)
```

`tolerance=0.005, angularTolerance=0.05` give consistent tessellation across runs. The defaults produce variable file sizes and over-tessellated text. With this combo + `merge_vertices(4) → fill_holes → fix_normals` you typically reach ≤6 open edges — well within slicer auto-repair.

> **"Watertight: False" usually means boundary edges, not real holes.** Before assuming a leak, count and locate them — often they're degenerate seams from a coplanar boolean, fixed by an epsilon, not by patching the mesh.

## Coordinate convention — pick once per project, write it down

CadQuery defaults to centered geometry on each plane. Pin a convention in CLAUDE.md and stick to it. Typical:

- **X** = width (left/right). Body symmetric about X=0.
- **Y** = depth. Pick a sign for "front" and "back" once, never flip.
- **Z** = up. Z=0 = bottom of body (use `centered=(True, True, False)` on `.box()`).

> **Gotcha:** `cq.Workplane("XZ")` extrudes in **−Y** direction, not +Y. Text/wordmark debossing uses an explicit `cq.Plane(..., normal=(0,-1,0))` plus `.mirror("YZ")` to land glyphs readable from the front face.

## Reusable patterns

```python
import cadquery as cq
from cadquery.occ_impl.geom import Location, Vector

def rounded_rect_sketch(w, d, r):
    return cq.Sketch().rect(w, d).vertices().fillet(r)

def section_extrude(z0, z1, w, d, r):
    return (cq.Workplane("XY", origin=(0, 0, z0))
            .placeSketch(rounded_rect_sketch(w, d, r))
            .extrude(z1 - z0))

def transition_loft(z0, w0, d0, r0, z1, w1, d1, r1):
    sketches = [
        rounded_rect_sketch(w0, d0, r0).moved(Location(Vector(0, 0, z0))),
        rounded_rect_sketch(w1, d1, r1).moved(Location(Vector(0, 0, z1))),
    ]
    return cq.Workplane("XY").placeSketch(*sketches).loft(combine=True, ruled=False)
```

Selective fillets (e.g., top fillet on front + sides only, leaving the back sharp) use `cq.selectors.BoxSelector` with a thin Z-slab to isolate the edges.

## Pitfalls — fix the cause, not the symptom

- **Hollowing: prefer boolean subtraction over `.shell()`.** `.shell()` fails on tapered bodies, lofted shapes, multi-primitive unions, anything heavily filleted. The reliable pattern is `outer.cut(inner)` with `inner` constructed at `offset=floor_t` and shrunk by `2 * wall`.
- **Fillet → cut, never cut → fillet.** Filleting after a `.cut()` often raises `BRep_API: command not done`. Apply largest-radius fillets first, while the body is still a clean primitive.
- **Don't wrap fillets in try/except to silently shrink the radius.** A fillet failure means the radius or the geometry is wrong (radius > wall thickness, adjacent faces would degenerate). Find and fix that.
- **Vertical edge fillet radius `R` must be ≤ min(W, D)/2.** Body's R doesn't have to match feature R — features narrower than the body cap their own fillet.
- **Loft fails between dimensionally identical adjacent profiles.** Adjacent loft profiles must differ slightly in W or D.
- **Loft is fragile in general.** Prefer `.extrude(taper=angle)` for shape → scaled-shape transitions. Use `.loft()` only for genuinely different profiles (circle → rectangle).
- **Taper sign:** in `.extrude(taper=angle)`, **positive** narrows (draft inward), **negative** flares. Opposite to most intuition.
- **Bottom fillet < half body Y depth.** A fillet that meets exactly at Y=0 creates a degenerate zero-width seam. Knock 0.5 mm off the radius.
- **Zero-thickness booleans.** When a cut is meant to pass *just* through a surface, add a 0.01 mm epsilon. Coplanar faces in a boolean produce non-manifold output.
- **`.hole()` cuts through the entire part by default.** Use `.cboreHole()` / `.cskHole()` for counterbore / countersink, or `.cutBlind(depth)` for a stop.

## Diagnostics — slice first, render second

3D iso renders foreshorten. Small geometry changes — a 0.5 mm wall, a 1 mm step — are easy to miss. The fastest way to confirm a feature is the same one you're picturing is to slice the mesh in world coordinates:

```python
import trimesh
m = trimesh.load("part.stl")

# Side view (YZ at given X)
sec = m.section(plane_origin=[X, 0, 0], plane_normal=[1, 0, 0])

# Top-down (XY at given Z)
sec = m.section(plane_origin=[0, 0, Z], plane_normal=[0, 0, 1])

# Constant-Y front-wall sweep
sec = m.section(plane_origin=[0, Y, 0], plane_normal=[0, 1, 0])
```

Plot the resulting 2D path with axes in mm. Sweep across X, Y, or Z to see how a feature evolves. Keep these as small `*_diag_*.py` scripts checked into the repo — when you hit the same class of bug six months later, the diagnostic is already there.

## Iteration discipline

- **One atomic change → rebuild → confirm → next.** Don't bundle a fix with a refactor.
- **Predict before editing.** Write what the change will do (which params, expected geometry shift, expected volume delta) *before* editing. If the user disagrees with the prediction, they catch the misread before code lands.
- **When the user says "no X," stop reaching for X-shaped solutions.** Even a different-looking variant is still X. Re-diagnose.
- **"Find the gap" means stop and diagnose**, not "find then fix in the same turn." Pause at diagnosis, get confirmation, then propose the fix.

## Coordinate-anchored language

Words like *back, front, end, lip, gap, plateau, shelf* are ambiguous. Pin spatial discussion to **(X, Y, Z) in mm**. Lead descriptions with coordinates: *"the strip at Z=32–35, Y=7.5–8.5"* not *"the strip near the lip."*

If your STL viewer shows live cursor coordinates (the VS Code STL extension can be patched to show X/Y/Z under the cursor + grey numeric labels every 10 mm along axes), use them — ask the user to hover and read off coords rather than describing visually.

## Pre-export checklist (CadQuery → STL/3MF)

1. **Export tolerance pinned**: `tolerance=0.005, angularTolerance=0.05`.
2. **trimesh repair tail** ran (`merge_vertices` → `fill_holes` → `fix_normals`).
3. **Watertight ≥ near-watertight**: `is_watertight=True`, or open-edge count ≤ 6 (slicer-repairable).
4. **Bounding box** matches the parameters at the top of the script.
5. **Print orientation** noted in the script's header comment.
6. **Prefer 3MF over STL** when the slicer supports it — 3MF carries units, STL is unitless. Convert via `stl_to_3mf.py`.

## When CadQuery is the wrong tool

> CadQuery is parametric B-rep, not mesh sculpting. Right for **precise mating dimensions, bolt patterns, parametric assemblies, snap-fits dialed by clearance numbers**. Wrong for **organic surfaces, sculpted grips, decorative reliefs, anything you'd rather feel out by eye**.

For organic / sculpted work, switch to the [Blender flow](../Blender/) — author the organic part in Blender, export STL, optionally union with the parametric chassis as a final step.

## Project folder layout

Each CadQuery project gets its own repo:

```
<project-name>/
├── CLAUDE.md         ← copy from CLAUDE.md.template, customize
├── README.md         ← what the project is, dimensions, design decisions, slicer settings
├── .venv/            ← project-local Python 3.12 venv (gitignored)
├── requirements.txt  ← pinned cadquery + trimesh + pyrender + Pillow
├── src/              ← .py scripts, one per part (or per family)
│   └── <part>_v<N>.py    ← version in the filename; old versions archived, not modified
├── exports/          ← STL / 3MF outputs for the slicer
└── references/       ← reference STLs / target images for visual comparison
```

Versioned filenames (`<part>_v1.py`, `<part>_v2.py`, ...) document iteration decisions. **Never modify an old version** — its existence is the audit trail.
