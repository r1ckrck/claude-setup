"""Slice a CAD model along an axis and plot the cross-section in world coordinates.

3D iso renders foreshorten, so small geometry changes (gaps, wall thickness,
feature placement) are easy to miss. Slicing the model along an axis at an
exact coordinate and plotting the cross-section in world mm makes those features
unambiguous: hover-free, you read positions straight off the labeled axes.

Input is a STEP/STP file (tessellated via build123d) or any trimesh-loadable
mesh (STL/GLB/3MF/OBJ). Output is a PNG with one panel per requested slice.

Convention (matches the workspace's coordinate-anchored language):
  --axis x  -> plane normal +X, panel plots world Y (horizontal) vs Z (vertical)
  --axis y  -> plane normal +Y, panel plots world X (horizontal) vs Z (vertical)
  --axis z  -> plane normal +Z, panel plots world X (horizontal) vs Y (vertical)
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh

# For each slice-normal axis: (index, horizontal-axis, vertical-axis)
_PLANE = {
    "x": (0, ("y", 1), ("z", 2)),
    "y": (1, ("x", 0), ("z", 2)),
    "z": (2, ("x", 0), ("y", 1)),
}


def load_mesh(path: Path) -> trimesh.Trimesh:
    """Load a STEP/STP via build123d tessellation, or any mesh via trimesh."""
    suffix = path.suffix.lower()
    if suffix in (".step", ".stp"):
        from build123d import import_step

        shape = import_step(str(path))
        verts, faces = shape.tessellate(tolerance=0.05)
        mesh = trimesh.Trimesh(
            vertices=[(v.X, v.Y, v.Z) for v in verts], faces=faces
        )
    else:
        mesh = trimesh.load(path, force="mesh")
    if mesh.vertices is None or len(mesh.vertices) == 0:
        raise ValueError(f"No geometry loaded from {path}")
    return mesh


def draw_slice(ax, mesh: trimesh.Trimesh, axis: str, at: float, grid: float) -> None:
    idx, (h_name, h_i), (v_name, v_i) = _PLANE[axis]
    normal = [0.0, 0.0, 0.0]
    normal[idx] = 1.0
    origin = [0.0, 0.0, 0.0]
    origin[idx] = at

    section = mesh.section(plane_origin=origin, plane_normal=normal)
    title = f"{axis.upper()} = {at:.2f} mm   ({h_name.upper()}-{v_name.upper()} section)"

    if section is None:
        ax.text(
            0.5, 0.5, "no intersection", ha="center", va="center",
            transform=ax.transAxes, color="#b00", fontsize=11,
        )
        ax.set_title(title, fontsize=10)
        return

    verts = section.vertices  # world-coordinate 3D points
    for entity in section.entities:
        pts = verts[entity.points]
        ax.plot(pts[:, h_i], pts[:, v_i], color="#1a1a1a", linewidth=1.4)

    # World-coordinate framing with a labeled grid every `grid` mm.
    hv = verts[:, h_i]
    vv = verts[:, v_i]
    pad = grid * 0.5
    ax.set_xlim(_round_down(hv.min(), grid) - pad, _round_up(hv.max(), grid) + pad)
    ax.set_ylim(_round_down(vv.min(), grid) - pad, _round_up(vv.max(), grid) + pad)
    ax.set_xticks(_ticks(ax.get_xlim(), grid))
    ax.set_yticks(_ticks(ax.get_ylim(), grid))
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, color="#cccccc", linewidth=0.6)
    ax.axhline(0, color="#999999", linewidth=0.8)
    ax.axvline(0, color="#999999", linewidth=0.8)
    ax.set_xlabel(f"{h_name.upper()} (mm)", fontsize=9)
    ax.set_ylabel(f"{v_name.upper()} (mm)", fontsize=9)
    ax.set_title(title, fontsize=10)


def _round_down(v: float, step: float) -> float:
    return float(np.floor(v / step) * step)


def _round_up(v: float, step: float) -> float:
    return float(np.ceil(v / step) * step)


def _ticks(limits, step: float):
    lo, hi = limits
    return np.arange(_round_down(lo, step), _round_up(hi, step) + step, step)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Slice a CAD model and plot world-coordinate cross-sections."
    )
    parser.add_argument("input", help="STEP/STP file or mesh (STL/GLB/3MF/OBJ)")
    parser.add_argument(
        "--axis", choices=["x", "y", "z"], required=True,
        help="Slice-plane normal axis",
    )
    parser.add_argument(
        "--at", type=float, nargs="+",
        help="World coordinate(s) on the axis to slice at (mm). "
             "Default: center of the bounding box on that axis.",
    )
    parser.add_argument("-o", "--output", required=True, help="Output PNG path")
    parser.add_argument(
        "--grid", type=float, default=10.0,
        help="Grid + tick spacing in mm (default 10)",
    )
    args = parser.parse_args()

    mesh = load_mesh(Path(args.input))

    idx = _PLANE[args.axis][0]
    if args.at is None:
        center = float(mesh.bounds[:, idx].mean())
        ats = [center]
    else:
        ats = args.at

    n = len(ats)
    fig, axes = plt.subplots(1, n, figsize=(5.2 * n, 5.2), squeeze=False)
    for ax, at in zip(axes[0], ats):
        draw_slice(ax, mesh, args.axis, at, args.grid)

    fig.tight_layout()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=130)
    plt.close(fig)
    print(f"saved slice: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
