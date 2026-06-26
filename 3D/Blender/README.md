# 3D — Blender + Claude Code

How I work with Claude Code on **functional 3D-print parts** in Blender. Hobbyist desktop FDM, output is STL/3MF for a slicer. Not animation, render, or visualization.

This folder is documentation only — no project files. For a real project, copy `CLAUDE.md.template` and `mcp.json.example` into a new repo.

## Files

| File | Purpose |
|---|---|
| `README.md` | This overview. |
| `CLAUDE.md.template` | Drop into a new 3D project repo as `CLAUDE.md`. |
| `mcp.json.example` | Drop into a new 3D project repo as `.mcp.json`. |

## MCP — Blender Lab

Claude talks to a live Blender session through the **Blender Lab MCP server**. Blender must be running with the MCP add-on enabled and connected before any tool call lands.

### Install (one-time)

The server lives at `~/blender_mcp/mcp` and is run via `uv`. The Blender add-on is installed inside Blender (Edit → Preferences → Add-ons → install from the same repo) and enabled per session.

### Wire it into a project

Drop `mcp.json.example` into the project root as `.mcp.json`:

```json
{
  "mcpServers": {
    "blender": {
      "command": "uv",
      "args": ["--directory", "/Users/YOUR_USER/blender_mcp/mcp", "run", "blender-mcp"]
    }
  }
}
```

Claude Code picks it up on launch.

### Tools that matter

| Tool | When to use |
|---|---|
| `get_objects_summary` | Always run first — see what's in the scene before mutating. |
| `get_object_detail_summary` | Inspect one object's modifiers, materials, transforms. |
| `execute_blender_code` | Run `bpy` Python in the live session. **Last resort** — prefer dedicated tools. |
| `get_screenshot_of_window_as_image` | Verify visual results after changes. |
| `render_viewport_to_path` | Save a viewport snapshot for the README. |
| `get_blendfile_summary_*` | Datablocks, missing files, linked libs, path info. |
| `search_api_docs` / `search_manual_docs` | Look up `bpy` operators/properties before guessing. |

### Working rules

> **Inspect before mutating.** Never assume scene state. Run `get_objects_summary` first.

- Keep `execute_blender_code` blocks **small and idempotent**.
- Many `bpy.ops` operators depend on **mode** (Object/Edit) and **active+selected** objects — set both explicitly.
- Update the dependency graph after changes before reading computed properties.
- In Edit mode, use **bmesh**, not the regular mesh data API. Flush bmesh changes back.
- Hide cutter objects after Boolean: `cutter.hide_viewport = True`.

## Skills

Claude Code skills (`.claude/skills/`) provide deep Blender domain knowledge. For 3D printing, **only these are useful** — the rest are noise:

| Skill | Use |
|---|---|
| `blender-modeling-modifiers` | **Primary.** Modifiers, bmesh, mesh editing. |
| `blender-scene-rendering` | Export only — STL/3MF/glTF, units, view layers. |
| `blender-geometry-nodes` | Procedural patterns (vents, lattice, scatter). |
| `blender-python-scripting` | Automation, batch processing, custom operators. |

**Ignore** for FDM work: `shader-nodes`, `animation-rigging`, `compositing-nodes`, `physics-simulation`.

The skills aren't copied here — they ship as part of the Blender skill pack and are referenced from the project's `.claude/skills/` directory.

## Blender setup — verify at session start

| Setting | Value |
|---|---|
| Units > System | Metric |
| Units > Length | Millimeters |
| Units > Unit Scale | **0.001** (1 BU = 1 mm) |
| Add-ons | **3D Print Toolbox** + **3MF format** enabled |

> Wrong scale exports a 1000× oversize STL. Fix this before modeling.

## FDM design rules — the mental flip

> FDM is constrained by **gravity during the build** and **anisotropy after**. Orientation is the load path — decide it before modeling. Z-strength is ~4–5× weaker than XY.

What flips from injection-molding / CNC intuition: draft angles **irrelevant**; uniform walls **less critical**; undercuts **free**; cycle time = hours, so print time is a design constraint.

### Apply while modeling

1. **Orient first.** Pick the bed face before geometry. Load path runs along XY.
2. **No supports.** Redesign instead:
   - Bottom overhangs → **chamfer ≥ 45°**, not fillet
   - Horizontal holes Ø > 8 mm → **teardrop** (90° peak)
   - Holes through bridges → **sacrificial 1-layer floor**, drilled out post-print
   - Steep flat overhang → split + glue, or rotate
3. **Mantra: fillets on top, chamfers on bottom.**
4. **Bottom edges → 1–2 mm chamfer.** Never fillet (= elephant's foot).
5. **Walls > infill.** 4 perimeters = 1.6 mm wall = functional default. Wall thickness must be a clean multiple of line width (0.8, 1.2, 1.6, 2.0 mm).
6. **Internal corners → fillet** ≥ wall thickness. Blend into a region, don't end at one critical layer.
7. **Threads → heat-set brass inserts** for any cycled fastener. Captured nut pocket (with sacrificial bridge) also fine. Tapped PLA = prototype only.
8. **Print-in-place gaps:** PLA 0.2–0.3 mm, PETG 0.3–0.4 mm. Joint/hinge axes must be horizontal (XY).
9. **Living hinges:** PLA fatigues — use PETG/TPU/PP, or a discrete pin.

## Tolerance cheat sheet — PLA, 0.4 mm nozzle

| Feature | Compensate |
|---|---|
| Hole Ø ≤ 5 mm | Oversize **+0.2 to +0.4 mm** |
| Hole Ø 5–20 mm | Oversize +0.1 mm |
| Hole Ø > 20 mm | Nominal |
| External XY | Subtract 0.1 mm if critical |
| Press fit | 0.05–0.10 mm gap |
| **Snug friction** | **0.15–0.20 mm gap** |
| Free running | 0.25–0.35 mm gap |

Always print a tolerance test before committing to a multi-part assembly.

## Pre-export checklist (Blender → STL/3MF)

1. **Apply all modifiers** (Subsurf, Mirror, Solidify, Bevel — STL ignores live modifiers unless `apply_modifiers=True`)
2. **Apply scale** (Ctrl-A → Scale)
3. **Recalculate normals** (Edit Mode → Shift-N)
4. **Manifold check** (3D Print Toolbox → Check All → Make Manifold)
5. **Prefer 3MF over STL** when slicer supports it — 3MF carries units, STL is unitless

## Boolean — common failure pattern

Booleans need clean, manifold operands with no coplanar faces.

- Apply **Solidify** and **Bevel** *before* Boolean, never after.
- Use the **Exact** solver for anything load-bearing — Blender 5.1 made it fast, no reason to use Fast.
- Hide cutters: `cutter.hide_viewport = True`.

## When Blender is the wrong tool

> Blender is mesh-based, not parametric. Right for **organic, sculpted, decorative, hard-surface stylized**. Wrong for **precise mating dimensions, bolt patterns, gear meshes, threads-to-spec, parametric assemblies**.

If a part needs precise mating dimensions or parametric history, use **Plasticity / Fusion 360 / OnShape** instead. Don't silently struggle in Blender.

## Project folder layout

Each 3D-printing project gets its own repo with this layout:

```
<project-name>/
├── CLAUDE.md     ← copy from CLAUDE.md.template, customize
├── .mcp.json     ← copy from mcp.json.example
├── README.md     ← what the project is, math/dimensions, design decisions, slicer settings
├── parts/        ← .blend sources, one file per part (or per family)
└── exports/      ← STL / 3MF outputs for the slicer
```

`parts/` and `exports/` belong inside a project folder, never at a repo root that holds multiple projects.
