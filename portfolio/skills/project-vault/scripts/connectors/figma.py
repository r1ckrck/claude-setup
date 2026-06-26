"""figma connector — reuses the figma-recon engine (does not duplicate it). Emits one
item per Figma project (not per file) to keep discovery readable."""

import json
import os
import subprocess


def _cache_dir(config):
    cd = config.get("cache_dir")
    if cd:
        return os.path.expanduser(cd)
    return os.path.join(config.get("_vault", "."), ".cache", "figma")


def _run_map(config, cache):
    path = os.path.expanduser(config["recon_path"])
    args = ["python3", path, "--out", cache, "map", str(config["team_id"])]
    if config.get("team_name"):
        args += ["--team-name", config["team_name"]]
    if config.get("handle"):
        args += ["--handle", config["handle"]]
    return subprocess.run(args, capture_output=True, text=True)


def _projects(cache):
    idx = os.path.join(cache, "index.json")
    if not os.path.exists(idx):
        return []
    return json.load(open(idx)).get("projects", [])


def discover(config):
    cache = _cache_dir(config)
    r = _run_map(config, cache)
    if r.returncode != 0:
        raise RuntimeError("figma-recon map failed: " + r.stderr.strip()[:300])
    items = []
    for p in _projects(cache):
        slug = p.get("slug")
        files = []
        pj = os.path.join(cache, slug, "project.json") if slug else None
        if pj and os.path.exists(pj):
            files = [f.get("name") for f in json.load(open(pj)).get("files", [])][:5]
        items.append({
            "uri": "figma:project/" + str(p["project_id"]),
            "type": "figma", "role": "design", "name": p["name"],
            "meta": {"file_count": p.get("file_count"), "sample_files": files},
        })
    return items


def fetch_meta(uri, config):
    cache = _cache_dir(config)
    pid = uri.split("/")[-1]
    name, fc, slug = uri, None, None
    for p in _projects(cache):
        if str(p["project_id"]) == pid:
            name, fc, slug = p["name"], p.get("file_count"), p.get("slug")
            break
    files, lm = [], None
    if slug:
        pj = os.path.join(cache, slug, "project.json")
        if os.path.exists(pj):
            d = json.load(open(pj))
            files = [{"name": f.get("name"), "key": f.get("file_key"),
                      "last_modified": f.get("last_modified")} for f in d.get("files", [])]
            lms = [f.get("last_modified") for f in d.get("files", []) if f.get("last_modified")]
            lm = max(lms) if lms else None
    return {"name": name, "last_modified": lm, "visibility": "team", "file_count": fc, "files": files}
