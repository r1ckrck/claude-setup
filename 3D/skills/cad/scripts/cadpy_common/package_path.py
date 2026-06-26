from __future__ import annotations

import sys
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
PACKAGES_DIR = SCRIPTS_DIR / "packages"
CADPY_SRC_DIR = PACKAGES_DIR / "cadpy" / "src"


def ensure_cadpy_package_path(*extra_paths: str | Path) -> None:
    paths = [str(Path(path)) for path in extra_paths]
    paths.extend([str(CADPY_SRC_DIR), str(PACKAGES_DIR)])
    for path in reversed(paths):
        while path in sys.path:
            sys.path.remove(path)
        sys.path.insert(0, path)
