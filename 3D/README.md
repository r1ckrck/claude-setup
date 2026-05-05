# 3D — Claude Code workflows for 3D-printable parts

Two ways I drive 3D modeling with Claude Code. Same end goal — STL/3MF for a slicer, hobbyist desktop FDM. They differ in **how the geometry is authored**.

| Approach | Authoring style | Claude talks to | Use when |
|---|---|---|---|
| **[Blender](./Blender/)** | Mesh-based, interactive in a live Blender session | The **Blender Lab MCP** server (live `bpy` calls into the running app) | Organic, sculpted, decorative, hard-surface stylized parts. Anything where the form is felt out by eye. |
| **[CadQuery](./CadQuery/)** | Parametric, code-first Python scripts → STL on disk | The **filesystem** (edits `.py` files, runs them, reads back STL + rendered PNG) | Functional parts with precise mating dimensions, parametric history, snap-fits, bolt patterns, enclosures over a known PCB. |

Each subfolder is a self-contained kit: `README.md` explaining the approach, plus a `CLAUDE.md.template` (and any `.mcp.json` / config) to drop into a new project repo.

## Picking between them

> **Mesh vs parametric is the real fork.** Blender edits a mesh you can see live; CadQuery rebuilds a tree from parameters every run. Get this wrong and you'll fight the tool for the whole project.

- **Need to dial a wall thickness, hole pattern, or PCB clearance to a number?** CadQuery. Parameters at the top of the script, edit and rebuild.
- **Need to feel out a curve, sculpt a grip, or iterate on visual proportion?** Blender. Direct mesh manipulation in a live session.
- **Mixing both** is fine — model the parametric chassis in CadQuery, export STL, import into Blender for organic accents. Going the other way (Blender → CadQuery) does not work; mesh has no parametric history to recover.

## Common ground (applies to both)

The FDM design rules don't care which tool authored the geometry. Both folders restate the same constraints because each is meant to stand alone, but the substance is identical:

- Orientation is the load path. Decide it before modeling. Z-strength is ~4–5× weaker than XY.
- Fillets on top, chamfers on bottom. 1–2 mm bottom chamfer, never a fillet (elephant's foot).
- Walls in clean multiples of line width: 0.8 / 1.2 / 1.6 / 2.0 mm. Default 1.6 mm (4 perimeters at 0.4 mm nozzle).
- Tolerance starting points (PLA, 0.4 mm nozzle): holes ≤5 mm oversize +0.2–0.4; press fit 0.05–0.10 mm gap; snug friction 0.15–0.20 mm; free running 0.25–0.35 mm.
- Always run a tolerance test print before committing to a multi-part assembly.

## Folder layout for a real project

Whichever approach you pick, a project repo ends up with:

```
<project-name>/
├── CLAUDE.md      ← copied from the chosen approach's template, customized
├── .mcp.json      ← only for the Blender flow
├── README.md      ← what the project is, dimensions, design decisions
├── parts/  or  src/  ← .blend files (Blender) or .py scripts (CadQuery)
└── exports/       ← STL / 3MF outputs
```

This `3D/` folder is documentation only. No project files belong here.
