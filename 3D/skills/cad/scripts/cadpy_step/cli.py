from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
import sys

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from cadpy_common.package_path import ensure_cadpy_package_path

ensure_cadpy_package_path()

from cadpy.catalog import StepImportOptions
from cadpy.generation import generate_step_targets, targets_include_output_pairs
from cadpy.metadata import normalize_mesh_numeric


def _normalize_cli_numeric(value: object, *, field_name: str, parser: argparse.ArgumentParser) -> float | None:
    try:
        return normalize_mesh_numeric(value, field_name=field_name)
    except ValueError as exc:
        parser.error(str(exc))
    return None


def _add_step_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "targets",
        nargs="+",
        help="Explicit Python generator, STEP/STP file path, or SOURCE.py=OUTPUT.step pair to generate.",
    )
    parser.add_argument(
        "--kind",
        choices=("part", "assembly"),
        help="Required for direct STEP/STP targets. Generated Python targets infer kind from gen_step().",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="PATH",
        help="Write the generated STEP file to this path. Valid only with one plain generated Python target.",
    )
    parser.add_argument(
        "--stl",
        metavar="OUTPUT",
        help="Override the combined STL output location (relative .stl path). On by default beside the STEP.",
    )
    parser.add_argument(
        "--3mf",
        dest="three_mf",
        metavar="OUTPUT",
        help="Override the flat multi-part 3MF output location (relative .3mf path). On by default beside the STEP.",
    )
    parser.add_argument(
        "--meshes-dir",
        dest="meshes_dir",
        metavar="DIR",
        help="Override the per-part STL output directory (relative path). On by default at meshes/ beside the STEP.",
    )
    parser.add_argument(
        "--no-stl",
        action="store_true",
        help="Suppress the combined STL export.",
    )
    parser.add_argument(
        "--no-meshes",
        action="store_true",
        help="Suppress the per-part STL exports.",
    )
    parser.add_argument(
        "--no-3mf",
        action="store_true",
        help="Suppress the flat multi-part 3MF export.",
    )
    parser.add_argument(
        "--glb",
        metavar="OUTPUT",
        help="Export a native Y-up GLB sidecar to this relative .glb path.",
    )
    parser.add_argument(
        "--skip-step-write",
        action="store_true",
        help="For Python gen_step() targets, generate the hidden GLB/topology artifact without writing STEP.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate STEP and hidden CAD Viewer GLB/topology outputs even when current artifacts match.",
    )
    parser.add_argument(
        "--mesh-tolerance",
        type=float,
        help="Positive shared mesh linear deflection for GLB/topology, native GLB, STL, and 3MF artifacts.",
    )
    parser.add_argument(
        "--mesh-angular-tolerance",
        type=float,
        help="Positive shared mesh angular deflection for GLB/topology, native GLB, STL, and 3MF artifacts.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed progress and timing information.",
    )


def _step_import_options_from_args(args: argparse.Namespace, *, parser: argparse.ArgumentParser) -> StepImportOptions:
    return StepImportOptions(
        stl=args.stl,
        three_mf=args.three_mf,
        glb=args.glb,
        meshes_dir=args.meshes_dir,
        no_stl=args.no_stl,
        no_meshes=args.no_meshes,
        no_3mf=args.no_3mf,
        mesh_tolerance=_normalize_cli_numeric(
            args.mesh_tolerance,
            field_name="mesh_tolerance",
            parser=parser,
        ),
        mesh_angular_tolerance=_normalize_cli_numeric(
            args.mesh_angular_tolerance,
            field_name="mesh_angular_tolerance",
            parser=parser,
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scripts/step",
        description="Generate explicit CAD STEP targets and their CAD Viewer artifacts.",
    )
    _add_step_arguments(parser)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.output is not None:
        if targets_include_output_pairs(args.targets):
            parser.error("--output cannot be combined with SOURCE=OUTPUT targets")
        if len(args.targets) != 1:
            parser.error("--output can only be used with exactly one target")
    return generate_step_targets(
        args.targets,
        direct_step_kind=args.kind,
        step_options=_step_import_options_from_args(args, parser=parser),
        output=args.output,
        skip_step_write=bool(args.skip_step_write),
        force=bool(args.force),
        verbose=bool(args.verbose),
    )


if __name__ == "__main__":
    raise SystemExit(main())
