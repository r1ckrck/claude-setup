from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    tool_dir = Path(__file__).resolve().parent
    scripts_dir = tool_dir.parent
    sys.path.insert(0, str(scripts_dir))
else:
    tool_dir = Path(__file__).resolve().parent

from cadpy_common.package_path import ensure_cadpy_package_path

ensure_cadpy_package_path()

from cadpy_inspect.inspect_refs.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
