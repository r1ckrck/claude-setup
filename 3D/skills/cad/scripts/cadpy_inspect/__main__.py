from __future__ import annotations

from pathlib import Path
import sys

TOOL_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = TOOL_DIR.parent
scripts_path = str(SCRIPTS_DIR)
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from cadpy_inspect.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
