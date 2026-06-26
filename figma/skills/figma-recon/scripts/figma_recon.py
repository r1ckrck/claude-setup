#!/usr/bin/env python3
"""figma-recon REST engine.

Read-only Figma REST API client that caches a team's projects and files as
source-of-truth JSON under an output folder (default ./docs/figma), and renders
human-readable markdown from that cache.

Token: read from ~/.figma-token at call time, sent as the X-Figma-Token header.
The token is never printed, logged, or written to disk.

This script covers the REST "map" (breadth). Depth inside a file — structure,
variables/tokens, design-to-code — is the MCP's job and is added to the per-file
JSON by the calling agent, not here. Reading variables via REST is intentionally
absent: that endpoint is Enterprise-only.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_ROOT = "https://api.figma.com/v1"
TOKEN_PATH = Path.home() / ".figma-token"
MAX_RETRIES = 4
PACE_SECONDS = 0.4  # gentle spacing between calls to avoid bursts


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(name):
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"(^-+|-+$)", "", s) or "untitled"


def read_token():
    if not TOKEN_PATH.exists():
        sys.exit(
            f"No token at {TOKEN_PATH}. Create it (chmod 600) before running. "
            "See the skill pre-flight."
        )
    token = TOKEN_PATH.read_text().strip()
    if not token:
        sys.exit(f"Token file {TOKEN_PATH} is empty.")
    return token


def out_dir(args):
    base = args.out or os.environ.get("FIGMA_RECON_OUT") or "./docs/figma"
    p = Path(base)
    p.mkdir(parents=True, exist_ok=True)
    return p


def api_get(path, params=None):
    """GET a REST endpoint. Honors 429 + Retry-After. Returns parsed JSON.

    The token is injected only into the request header here. Error messages
    never include the header.
    """
    token = read_token()
    url = f"{API_ROOT}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    attempt = 0
    while True:
        req = urllib.request.Request(url, headers={"X-Figma-Token": token})
        try:
            with urllib.request.urlopen(req) as resp:
                time.sleep(PACE_SECONDS)
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < MAX_RETRIES:
                retry_after = e.headers.get("Retry-After")
                wait = int(retry_after) if retry_after and retry_after.isdigit() else 2 ** attempt
                sys.stderr.write(f"[429] rate limited on {path}; waiting {wait}s\n")
                time.sleep(wait)
                attempt += 1
                continue
            body = ""
            try:
                body = e.read().decode("utf-8")[:300]
            except Exception:
                pass
            sys.exit(f"HTTP {e.code} on {path}: {e.reason}. {body}")
        except urllib.error.URLError as e:
            sys.exit(f"Network error on {path}: {e.reason}")


def load_json(path):
    if Path(path).exists():
        return json.loads(Path(path).read_text())
    return None


def save_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def merge_file_json(path, rest_fields):
    """Top-level merge so MCP-sourced keys added by the agent survive a REST refresh."""
    existing = load_json(path) or {}
    existing.update(rest_fields)
    save_json(path, existing)
    return existing


def file_url(file_key, name):
    return f"https://www.figma.com/design/{file_key}/{urllib.parse.quote(name)}"


# ---- commands -------------------------------------------------------------

def cmd_list_projects(args):
    data = api_get(f"/teams/{args.team_id}/projects")
    out = out_dir(args)
    index = load_json(out / "index.json") or {}
    index["team_id"] = args.team_id
    index["team_name"] = data.get("name") or args.team_name or index.get("team_name", "")
    if args.team_name:
        index["team_name"] = args.team_name
    if args.handle:
        index["whoami"] = args.handle
    index["last_refreshed"] = now_iso()
    index["projects"] = [
        {
            "project_id": p["id"],
            "name": p["name"],
            "slug": slugify(p["name"]),
            "file_count": next(
                (op.get("file_count") for op in index.get("projects", []) if op["project_id"] == p["id"]),
                None,
            ),
            "last_project_refresh": next(
                (op.get("last_project_refresh") for op in index.get("projects", []) if op["project_id"] == p["id"]),
                None,
            ),
        }
        for p in data.get("projects", [])
    ]
    save_json(out / "index.json", index)
    print(json.dumps({"team_id": args.team_id, "team_name": index["team_name"],
                      "projects": [{"id": p["project_id"], "name": p["name"]} for p in index["projects"]]}, indent=2))


def cmd_list_files(args):
    data = api_get(f"/projects/{args.project_id}/files")
    out = out_dir(args)
    index = load_json(out / "index.json") or {}
    proj = next((p for p in index.get("projects", []) if p["project_id"] == args.project_id), None)
    pname = (proj or {}).get("name") or args.project_name or args.project_id
    slug = (proj or {}).get("slug") or slugify(str(pname))

    incoming = data.get("files", [])
    proj_path = out / slug / "project.json"
    existing = load_json(proj_path) or {"files": []}
    by_key = {f["file_key"]: f for f in existing.get("files", [])}

    unchanged, changed = 0, 0
    files = []
    for f in incoming:
        key = f["key"]
        prev = by_key.get(key, {})
        same = prev.get("last_modified") == f.get("last_modified") and prev.get("depth")
        if same:
            unchanged += 1
        else:
            changed += 1
        files.append({
            "file_key": key,
            "name": f.get("name"),
            "thumbnail_url": f.get("thumbnail_url"),
            "last_modified": f.get("last_modified"),
            "last_pulled": prev.get("last_pulled"),
            "depth": prev.get("depth", "map-only"),
        })
    save_json(proj_path, {
        "project_id": args.project_id,
        "name": pname,
        "slug": slug,
        "last_refreshed": now_iso(),
        "files": files,
    })
    # stamp count back into index
    for p in index.get("projects", []):
        if p["project_id"] == args.project_id:
            p["file_count"] = len(files)
            p["last_project_refresh"] = now_iso()
    save_json(out / "index.json", index)
    print(json.dumps({"project": pname, "files": len(files),
                      "changed": changed, "unchanged": unchanged}, indent=2))


def cmd_map(args):
    """Full breadth pass: projects, then files for each project."""
    cmd_list_projects(args)
    out = out_dir(args)
    index = load_json(out / "index.json")
    for p in index.get("projects", []):
        sub = argparse.Namespace(**vars(args))
        sub.project_id = p["project_id"]
        sub.project_name = p["name"]
        cmd_list_files(sub)
    print(json.dumps({"mapped_projects": len(index.get("projects", []))}, indent=2))


def _locate_file(out, file_key):
    for proj_json in out.glob("*/project.json"):
        pj = load_json(proj_json)
        for f in pj.get("files", []):
            if f["file_key"] == file_key:
                return pj["slug"], f
    return None, None


def cmd_file_meta(args):
    """Shallow file info (depth=1) — cheap. Tier 1, so used deliberately."""
    data = api_get(f"/files/{args.file_key}", {"depth": 1})
    out = out_dir(args)
    slug, listed = _locate_file(out, args.file_key)
    if not slug:
        sys.exit(f"File {args.file_key} not in cache. Run map/list-files first.")
    fpath = out / slug / "files" / f"{args.file_key}.json"
    name = data.get("name", (listed or {}).get("name", ""))
    rest = {
        "file_key": args.file_key,
        "name": name,
        "figma_url": file_url(args.file_key, name),
        "last_modified": data.get("lastModified"),
        "version": data.get("version"),
        "thumbnail_url": data.get("thumbnailUrl"),
        "last_pulled": now_iso(),
        "source": "rest",
        "depth": "metadata",
    }
    merge_file_json(fpath, rest)
    # stamp project listing
    pj = load_json(out / slug / "project.json")
    for f in pj.get("files", []):
        if f["file_key"] == args.file_key:
            f["last_pulled"] = rest["last_pulled"]
            f["depth"] = "metadata"
    save_json(out / slug / "project.json", pj)
    print(json.dumps({"file": name, "version": rest["version"],
                      "last_modified": rest["last_modified"]}, indent=2))


def _file_subresource(args, sub, key):
    data = api_get(f"/files/{args.file_key}/{sub}")
    out = out_dir(args)
    slug, listed = _locate_file(out, args.file_key)
    if not slug:
        sys.exit(f"File {args.file_key} not in cache. Run map/list-files first.")
    fpath = out / slug / "files" / f"{args.file_key}.json"
    payload = data.get("meta", data)
    merge_file_json(fpath, {key: payload, f"{key}_pulled": now_iso()})
    print(json.dumps({"file_key": args.file_key, key: "saved"}, indent=2))


def cmd_components(args):
    _file_subresource(args, "components", "components")


def cmd_styles(args):
    _file_subresource(args, "styles", "styles")


def cmd_component_sets(args):
    _file_subresource(args, "component_sets", "component_sets")


def cmd_versions(args):
    data = api_get(f"/files/{args.file_key}/versions")
    out = out_dir(args)
    slug, _ = _locate_file(out, args.file_key)
    if not slug:
        sys.exit(f"File {args.file_key} not in cache. Run map/list-files first.")
    fpath = out / slug / "files" / f"{args.file_key}.json"
    versions = [
        {"id": v.get("id"), "label": v.get("label"), "created_at": v.get("created_at"),
         "user": (v.get("user") or {}).get("handle")}
        for v in data.get("versions", [])
    ]
    merge_file_json(fpath, {"version_history": versions})
    print(json.dumps({"file_key": args.file_key, "versions": len(versions)}, indent=2))


def cmd_comments(args):
    data = api_get(f"/files/{args.file_key}/comments")
    out = out_dir(args)
    slug, _ = _locate_file(out, args.file_key)
    if not slug:
        sys.exit(f"File {args.file_key} not in cache. Run map/list-files first.")
    fpath = out / slug / "files" / f"{args.file_key}.json"
    merge_file_json(fpath, {"comments_count": len(data.get("comments", []))})
    print(json.dumps({"file_key": args.file_key, "comments": len(data.get("comments", []))}, indent=2))


def cmd_images(args):
    """Gated Tier-1 render. Off by default in the workflow; explicit only."""
    ids = args.node_ids
    data = api_get(f"/images/{args.file_key}", {"ids": ids, "format": args.format})
    print(json.dumps(data.get("images", {}), indent=2))


def cmd_parse_metadata(args):
    """Parse a saved MCP get_metadata output into the per-file structure.

    The MCP get_metadata response for a whole page can be large; the harness saves
    overflow to a tool-results file. Capturing the full output and parsing it here
    keeps detail high and context clean. Node tags ARE the type (canvas/section/
    frame/text/instance/...). Concatenated top-level elements are wrapped in a root.
    """
    import xml.etree.ElementTree as ET
    from collections import Counter
    raw = Path(args.saved_file).read_text()
    try:
        parts = json.loads(raw)
        text = "".join(p.get("text", "") for p in parts) if isinstance(parts, list) else raw
    except json.JSONDecodeError:
        text = raw
    root = ET.fromstring("<root>" + text + "</root>")
    type_counts = dict(Counter(el.tag for el in root.iter() if el.tag != "root"))
    pages = []
    for cv in (c for c in root if c.tag == "canvas"):
        pages.append({
            "id": cv.get("id"),
            "name": cv.get("name"),
            "node_count": sum(1 for _ in cv.iter()) - 1,
            "nodes": [{"id": c.get("id"), "name": c.get("name"), "type": c.tag} for c in list(cv)],
        })
    out = out_dir(args)
    slug, _ = _locate_file(out, args.file_key)
    if not slug:
        sys.exit(f"File {args.file_key} not in cache. Run map/list-files first.")
    fpath = out / slug / "files" / f"{args.file_key}.json"
    merge_file_json(fpath, {
        "structure": {"source": "mcp", "type_counts": type_counts, "pages": pages},
        "depth": "metadata",
        "last_pulled": now_iso(),
    })
    pj = load_json(out / slug / "project.json")
    for f in pj.get("files", []):
        if f["file_key"] == args.file_key:
            f["last_pulled"] = now_iso()
            f["depth"] = "metadata"
    save_json(out / slug / "project.json", pj)
    print(json.dumps({"file_key": args.file_key, "pages": [p["name"] for p in pages],
                      "node_count": sum(p["node_count"] for p in pages),
                      "type_counts": type_counts}, indent=2))


# ---- markdown rendering ---------------------------------------------------

def _stale(f):
    lm, lp = f.get("last_modified"), f.get("last_pulled")
    return bool(lm and lp and lm > lp)


def render_index(out):
    index = load_json(out / "index.json")
    if not index:
        return
    lines = [f"# Figma inventory — {index.get('team_name', '')}", ""]
    lines.append(f"Team ID `{index.get('team_id','')}` · last refreshed {index.get('last_refreshed','')}")
    if index.get("whoami"):
        lines.append(f"Authenticated as {index['whoami']}")
    lines += ["", "Generated by the figma-recon skill. Do not hand-edit.", "",
              "| Project | Files | Last refreshed |", "|---|---|---|"]
    for p in index.get("projects", []):
        lines.append(f"| [{p['name']}]({p['slug']}/project.md) | {p.get('file_count','?')} | {p.get('last_project_refresh') or '—'} |")
    (out / "index.md").write_text("\n".join(lines) + "\n")


def render_project(out, proj_json):
    pj = load_json(proj_json)
    slug = pj["slug"]
    lines = [f"# {pj['name']}", "",
             f"Project `{pj['project_id']}` · last refreshed {pj.get('last_refreshed','')}", "",
             "| File | Depth | Last modified | Last pulled | Stale |", "|---|---|---|---|---|"]
    for f in pj.get("files", []):
        link = f"files/{f['file_key']}.md"
        stale = "yes" if _stale(f) else ""
        lines.append(f"| [{f['name']}]({link}) | {f.get('depth','')} | {f.get('last_modified','')} | {f.get('last_pulled') or '—'} | {stale} |")
    (out / slug / "project.md").write_text("\n".join(lines) + "\n")


def render_file(out, file_json):
    fj = load_json(file_json)
    slug = file_json.parent.parent.name
    lines = [f"# {fj.get('name','')}", "",
             f"`{fj.get('file_key','')}` · [open in Figma]({fj.get('figma_url','')})", "",
             f"- Last modified: {fj.get('last_modified','')}",
             f"- Last pulled: {fj.get('last_pulled','')}  ·  source: {fj.get('source','')}  ·  depth: {fj.get('depth','')}",
             f"- Version: {fj.get('version','')}"]
    if "structure" in fj:
        lines += ["", "## Structure"]
        for page in fj["structure"].get("pages", []):
            lines.append(f"- **{page.get('name','')}** ({len(page.get('nodes', []))} top-level nodes)")
    for label, key in (("Components", "components"), ("Component sets", "component_sets"), ("Styles", "styles")):
        if key in fj and fj[key]:
            items = fj[key]
            count = len(items) if isinstance(items, list) else len(items.get(key, []) if isinstance(items, dict) else [])
            lines += ["", f"## {label} ({count})"]
    if "variables" in fj:
        v = fj["variables"]
        n = len(v.get("collections", [])) or len(v.get("samples", []))
        unit = "collection(s)" if v.get("collections") else "sampled node(s)"
        lines += ["", "## Variables / tokens", f"_source: MCP_  ·  {n} {unit}"]
    if "version_history" in fj:
        lines += ["", f"## Version history ({len(fj['version_history'])})"]
    (file_json.with_suffix(".md")).write_text("\n".join(lines) + "\n")


def cmd_render(args):
    out = out_dir(args)
    render_index(out)
    for proj_json in out.glob("*/project.json"):
        render_project(out, proj_json)
    for file_json in out.glob("*/files/*.json"):
        render_file(out, file_json)
    print(json.dumps({"rendered": "index + projects + files"}, indent=2))


# ---- cli ------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(description="figma-recon REST engine (read-only).")
    p.add_argument("--out", default=None, help="output folder (default ./docs/figma or $FIGMA_RECON_OUT)")
    sub = p.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--out", default=argparse.SUPPRESS,
                        help="output folder (overrides default ./docs/figma or $FIGMA_RECON_OUT)")

    sp = sub.add_parser("list-projects", parents=[common], help="list a team's projects")
    sp.add_argument("team_id")
    sp.add_argument("--team-name")
    sp.add_argument("--handle", help="authenticated handle from whoami, stored in index")
    sp.set_defaults(func=cmd_list_projects)

    sp = sub.add_parser("list-files", parents=[common], help="list a project's files")
    sp.add_argument("project_id")
    sp.add_argument("--project-name")
    sp.set_defaults(func=cmd_list_files)

    sp = sub.add_parser("map", parents=[common], help="full breadth pass: projects + files")
    sp.add_argument("team_id")
    sp.add_argument("--team-name")
    sp.add_argument("--handle")
    sp.set_defaults(func=cmd_map)

    sp = sub.add_parser("file-meta", parents=[common], help="shallow file info (depth=1)")
    sp.add_argument("file_key")
    sp.set_defaults(func=cmd_file_meta)

    for name, fn in (("components", cmd_components), ("styles", cmd_styles),
                     ("component-sets", cmd_component_sets), ("versions", cmd_versions),
                     ("comments", cmd_comments)):
        sp = sub.add_parser(name, parents=[common])
        sp.add_argument("file_key")
        sp.set_defaults(func=fn)

    sp = sub.add_parser("images", parents=[common], help="gated Tier-1 node render")
    sp.add_argument("file_key")
    sp.add_argument("node_ids", help="comma-separated node ids")
    sp.add_argument("--format", default="png", choices=["png", "svg", "pdf", "jpg"])
    sp.set_defaults(func=cmd_images)

    sp = sub.add_parser("parse-metadata", parents=[common], help="parse a saved MCP get_metadata file into per-file structure")
    sp.add_argument("saved_file", help="path to the saved get_metadata tool-results file")
    sp.add_argument("file_key")
    sp.set_defaults(func=cmd_parse_metadata)

    sp = sub.add_parser("render", parents=[common], help="regenerate markdown from cached JSON")
    sp.set_defaults(func=cmd_render)

    return p


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
