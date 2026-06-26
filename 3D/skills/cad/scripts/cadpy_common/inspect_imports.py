from __future__ import annotations

import sys
from pathlib import Path


def ensure_inspect_import_path() -> None:
    scripts_dir = Path(__file__).resolve().parents[1]
    scripts_path = str(scripts_dir)
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
