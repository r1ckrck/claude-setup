# Supported exports

Read this file when the user requests STL, 3MF, or native GLB output from CAD geometry. Read `dxf.md` for DXF output, because DXF uses a separate `gen_dxf()` source contract.

## Policy

STL and 3MF are mesh sidecars, not substitutes for STEP. Generate and validate STEP first; the mesh exports come from the same `scripts/step` run. Do not treat sidecar renders as CAD validation; inspect the STEP, verify the primary STEP/STP with CAD `scripts/snapshot` when snapshot review applies, and return `$cad-viewer` viewer links for every generated or modified supported artifact.

**Auto-export (default on).** Every `scripts/step` run writes mesh artifacts for **all** parts:

- **combined STL** — whole model merged.
- **per-part STLs** — one per leaf part, into the meshes directory.
- **flat multi-part 3MF** — one mesh object per unique part plus one build item per occurrence; slicers open each part separately.

Suppress any with `--no-stl` / `--no-meshes` / `--no-3mf`. Native GLB stays opt-in via `--glb`.

Native GLB sidecars are ordinary glTF 2.0 binary files for external tools: Y-up, meter-scaled, and free of the CAD Viewer `STEP_topology` extension. Do not confuse them with the hidden `.<name>.step.glb` CAD Viewer topology artifact.

## Tool

Use `scripts/step` with a generated Python source. With no flags, the combined STL and flat 3MF land beside the STEP and per-part STLs in `meshes/` beside the STEP:

```bash
python scripts/step path/to/model.py
```

Override any output location (paths are relative, resolved against the STEP output dir; `..` allowed to reach sibling folders such as `exports/`):

```bash
python scripts/step models/src/model.py=models/model.step \
  --stl ../exports/model.stl \
  --3mf ../exports/model.3mf \
  --meshes-dir meshes \
  --glb meshes/model.glb
```

Use direct STEP/STP targets (with `--kind`) only when the generator is unavailable or the user explicitly identifies that file as the target.

## Mesh tolerance

The default mesh density is `0.02` linear deflection and `0.05` angular deflection.

Use these flags when the default mesh density is wrong for the part:

```bash
--mesh-tolerance FLOAT
--mesh-angular-tolerance FLOAT
```

Use tighter tolerances for small curved parts or visual fidelity. Use looser tolerances for large simple geometry when file size matters.

## Workflow

1. Generate STEP from `gen_step()`; combined STL, per-part STLs, and the flat 3MF write automatically. Add `--no-stl`/`--no-meshes`/`--no-3mf` to suppress, or path flags to redirect.
2. Run facts/planes/positioning inspection on the STEP.
3. Return the STEP, requested sidecar files, and `$cad-viewer` viewer links for every generated or modified supported artifact when available.

Example:

```bash
python scripts/step models/bracket.py \
  --stl meshes/bracket.stl \
  --glb meshes/bracket.glb \
  --mesh-tolerance 0.2 \
  --mesh-angular-tolerance 0.2

python scripts/inspect refs models/bracket.step --facts --planes --positioning
```

## Reporting

```text
Files:
- STEP: /absolute/project/models/bracket.step
- STL: /absolute/project/models/meshes/bracket.stl
- GLB: /absolute/project/models/meshes/bracket.glb

CAD Viewer:
- STEP: http://127.0.0.1:4178/?dir=/absolute/project/models&file=bracket.step
- STL: http://127.0.0.1:4178/?dir=/absolute/project/models&file=meshes/bracket.stl
- GLB: http://127.0.0.1:4178/?dir=/absolute/project/models&file=meshes/bracket.glb

Validation:
- STEP geometry validated; STL/3MF/native GLB generated as requested sidecars.
- Primary STEP/STP snapshot packet run/skipped and why.
```
