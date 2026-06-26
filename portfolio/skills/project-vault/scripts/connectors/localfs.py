"""localfs connector — scans configured local directories. Each immediate child
directory of a root is a candidate project."""

import os
from datetime import datetime, timezone

DEFAULT_EXCLUDE = {"node_modules", ".git", ".expo", "dist", "build", "__pycache__", ".venv", ".next", "ios", "android"}


def discover(config):
    items = []
    exclude = set(config.get("exclude", [])) | DEFAULT_EXCLUDE
    for root in config.get("roots", []):
        root = os.path.expanduser(root)
        if not os.path.isdir(root):
            continue
        for name in sorted(os.listdir(root)):
            if name.startswith(".") or name in exclude:
                continue
            path = os.path.join(root, name)
            if os.path.isdir(path):
                items.append({"uri": path, "type": "localfs", "role": "code", "name": name, "meta": {}})
    return items


def fetch_meta(uri, config):
    exclude = set(config.get("exclude", [])) | DEFAULT_EXCLUDE
    types, total, latest = {}, 0, 0.0
    for dirpath, dirs, files in os.walk(uri):
        dirs[:] = [d for d in dirs if d not in exclude and not d.startswith(".")]
        for f in files:
            ext = os.path.splitext(f)[1].lower().lstrip(".")
            if ext:
                types[ext] = types.get(ext, 0) + 1
            try:
                st = os.stat(os.path.join(dirpath, f))
                total += st.st_size
                latest = max(latest, st.st_mtime)
            except OSError:
                pass
    top = sorted(types.items(), key=lambda x: -x[1])[:8]
    lm = datetime.fromtimestamp(latest, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if latest else None
    return {
        "name": os.path.basename(uri.rstrip("/")),
        "last_modified": lm,
        "visibility": "local",
        "file_types": ["." + e for e, _ in top],
        "size_bytes": total,
    }
