from __future__ import annotations

import re
from pathlib import Path

from OCP.StlAPI import StlAPI_Writer

from cadpy.render import REPO_ROOT, part_stl_path
from cadpy.step_scene import (
    LoadedStepScene,
    scene_export_shape,
    scene_leaf_occurrences,
    scene_occurrence_shape,
)


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def export_part_stl_from_scene(step_path: Path, scene: LoadedStepScene, *, target_path: Path | None = None) -> Path:
    target_path = target_path or part_stl_path(step_path)
    export_shape_stl(scene_export_shape(scene), target_path)
    return target_path

def export_shape_stl(shape: object, target_path: Path) -> Path:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    writer = StlAPI_Writer()
    writer.ASCIIMode = False
    if not writer.Write(shape, str(target_path)):
        raise RuntimeError(f"Failed to write STL output: {_display_path(target_path)}")
    return target_path


def _safe_label(name: str | None, fallback: str) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", (name or "").strip()).strip("_")
    return text or fallback


def export_per_part_stls(scene: LoadedStepScene, output_dir: Path) -> list[Path]:
    """Write one STL per leaf part into output_dir, named by its label.

    Each occurrence is exported as its own located shape. Colliding labels get a numeric
    suffix so no part overwrites another.
    """
    leaves = scene_leaf_occurrences(scene)
    if not leaves:
        raise RuntimeError(f"No CAD geometry available for per-part STL export: {scene.step_path}")
    output_dir.mkdir(parents=True, exist_ok=True)
    used: dict[str, int] = {}
    paths: list[Path] = []
    for index, node in enumerate(leaves):
        raw = node.source_name or scene.prototype_names.get(node.prototype_key) or node.name
        label = _safe_label(raw, f"part-{index + 1}")
        seen = used.get(label, 0)
        used[label] = seen + 1
        filename = label if seen == 0 else f"{label}_{seen + 1}"
        target = export_shape_stl(scene_occurrence_shape(scene, node), output_dir / f"{filename}.stl")
        paths.append(target)
    return paths
