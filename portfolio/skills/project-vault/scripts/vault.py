#!/usr/bin/env python3
"""project-vault engine.

Indexes and stores projects pulled from heterogeneous sources. A project is a
logical record; each project has many sources (local folder, GitHub repo, Figma
project, live URL). Connectors discover items from each source; a match ledger
links source URIs to canonical projects; the index aggregates everything.

JSON is the source of truth; markdown is rendered for reading. Python stdlib only.
Secrets are never stored — connector configs reference token paths, nothing more.
"""

import argparse
import difflib
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from connectors import REGISTRY  # noqa: E402

EXAMPLE_CONFIG = os.path.join(SCRIPT_DIR, "..", "references", "connectors.example.json")


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", (name or "").strip().lower())
    return re.sub(r"(^-+|-+$)", "", s) or "untitled"


def load_json(path):
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else None


def save_json(path, data):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


# ---- vault paths & state --------------------------------------------------

def vault_dir(args):
    base = args.vault or os.environ.get("PROJECT_VAULT") or "./vault"
    return Path(base)


def load_connectors(v):
    cfg = load_json(v / "connectors.json") or {}
    return cfg.get("connectors", cfg)


def conn_config(cfg, name, v):
    c = dict(cfg.get(name, {}))
    c["_vault"] = str(v)
    return c


def load_matches(v):
    m = load_json(v / "matches.json") or {}
    m.setdefault("links", {})
    m.setdefault("rejects", [])
    return m


def save_matches(v, m):
    save_json(v / "matches.json", m)


def load_projects(v):
    out = []
    pdir = v / "projects"
    if pdir.exists():
        for d in sorted(pdir.iterdir()):
            pj = d / "project.json"
            if pj.exists():
                out.append(load_json(pj))
    return out


def find_project_by_id(v, pid):
    for p in load_projects(v):
        if p.get("id") == pid:
            return p
    return None


def unique_slug(v, base):
    existing = {p["slug"] for p in load_projects(v)}
    if base not in existing:
        return base
    i = 2
    while f"{base}-{i}" in existing:
        i += 1
    return f"{base}-{i}"


def create_project(v, name, category):
    pid = "p_" + uuid.uuid4().hex[:8]
    slug = unique_slug(v, slugify(name))
    proj = {
        "id": pid, "slug": slug, "name": name, "category": category or "",
        "status": "", "tags": [], "summary": "", "created": now_iso(), "updated": now_iso(),
    }
    save_json(v / "projects" / slug / "project.json", proj)
    save_json(v / "projects" / slug / "sources.json", {"project_id": pid, "sources": []})
    sys.stderr.write(f"created project {pid} ({slug})\n")
    return pid


def infer_type(uri, by_uri):
    if uri in by_uri:
        return by_uri[uri].get("type")
    if uri.startswith("figma:"):
        return "figma"
    if "github.com" in uri:
        return "github"
    if uri.startswith("http"):
        return "webfetch"
    return "localfs"


# ---- commands -------------------------------------------------------------

def cmd_init(args):
    v = vault_dir(args)
    (v / "projects").mkdir(parents=True, exist_ok=True)
    (v / ".cache").mkdir(parents=True, exist_ok=True)
    if not (v / "connectors.json").exists():
        example = load_json(EXAMPLE_CONFIG) or {"connectors": {}}
        save_json(v / "connectors.json", example)
    if not (v / "matches.json").exists():
        save_matches(v, {"links": {}, "rejects": []})
    if not (v / "index.json").exists():
        save_json(v / "index.json", {"generated": now_iso(), "project_count": 0, "projects": []})
    gi = v / ".gitignore"
    if not gi.exists():
        gi.write_text(".cache/\nconnectors.json\n")
    print(json.dumps({"vault": str(v), "status": "ready"}, indent=2))


def cmd_discover(args):
    v = vault_dir(args)
    cfg = load_connectors(v)
    only = args.connector
    items = []
    for name, conn in REGISTRY.items():
        c = cfg.get(name, {})
        run = (only == name) or (only is None and c.get("enabled"))
        if not run:
            continue
        try:
            got = conn.discover(conn_config(cfg, name, v))
            for it in got:
                it.setdefault("role", "")
            items += got
            print(f"[{name}] discovered {len(got)}")
        except Exception as e:
            sys.stderr.write(f"[{name}] ERROR: {e}\n")
    save_json(v / ".cache" / "discovered.json", {"discovered_at": now_iso(), "items": items})
    print(json.dumps({"total": len(items)}))


def cmd_propose(args):
    v = vault_dir(args)
    disc = load_json(v / ".cache" / "discovered.json") or {"items": []}
    matches = load_matches(v)
    projects = load_projects(v)
    res = {"linked": [], "rejected": [], "suggested": [], "new": []}
    for it in disc["items"]:
        uri = it["uri"]
        if uri in matches["links"]:
            res["linked"].append({"uri": uri, "project": matches["links"][uri]})
        elif uri in matches["rejects"]:
            res["rejected"].append({"uri": uri})
        else:
            best, br = None, 0.0
            for p in projects:
                r = difflib.SequenceMatcher(None, it["name"].lower(), p["name"].lower()).ratio()
                if r > br:
                    br, best = r, p
            if best and br >= 0.6:
                res["suggested"].append({"uri": uri, "name": it["name"], "suggest": best["id"],
                                         "suggest_name": best["name"], "score": round(br, 2)})
            else:
                res["new"].append({"uri": uri, "name": it["name"], "type": it["type"]})
    save_json(v / ".cache" / "proposals.json", res)
    print(json.dumps({k: len(val) for k, val in res.items()}, indent=2))


def cmd_link(args):
    v = vault_dir(args)
    matches = load_matches(v)
    if args.new:
        if not args.name:
            sys.exit("--new requires --name")
        pid = create_project(v, args.name, args.type)
    else:
        if not args.project:
            sys.exit("provide --project <id> or --new --name <name>")
        pid = args.project
        if not find_project_by_id(v, pid):
            sys.exit(f"no project with id {pid}")
    matches["links"][args.uri] = pid
    if args.uri in matches["rejects"]:
        matches["rejects"].remove(args.uri)
    save_matches(v, matches)
    print(json.dumps({"linked": args.uri, "project": pid}))


def cmd_reject(args):
    v = vault_dir(args)
    matches = load_matches(v)
    if args.uri not in matches["rejects"]:
        matches["rejects"].append(args.uri)
    matches["links"].pop(args.uri, None)
    save_matches(v, matches)
    print(json.dumps({"rejected": args.uri}))


def cmd_enrich(args):
    v = vault_dir(args)
    cfg = load_connectors(v)
    matches = load_matches(v)
    disc = load_json(v / ".cache" / "discovered.json") or {"items": []}
    by_uri = {it["uri"]: it for it in disc["items"]}
    changed = unchanged = 0
    for uri, pid in matches["links"].items():
        typ = infer_type(uri, by_uri)
        if args.connector and typ != args.connector:
            continue
        conn = REGISTRY.get(typ)
        if not conn:
            sys.stderr.write(f"no connector for {uri}\n")
            continue
        try:
            meta = conn.fetch_meta(uri, conn_config(cfg, typ, v))
        except Exception as e:
            sys.stderr.write(f"[{typ}] fetch_meta {uri}: {e}\n")
            continue
        proj = find_project_by_id(v, pid)
        if not proj:
            continue
        spath = v / "projects" / proj["slug"] / "sources.json"
        sj = load_json(spath) or {"project_id": pid, "sources": []}
        existing = next((s for s in sj["sources"] if s["uri"] == uri), None)
        new_lm = meta.get("last_modified")
        if existing and existing.get("last_modified") == new_lm and existing.get("last_pulled"):
            unchanged += 1
            continue
        role = (by_uri.get(uri, {}) or {}).get("role") or (existing or {}).get("role", "")
        entry = {
            "type": typ, "role": role, "uri": uri,
            "visibility": meta.get("visibility"),
            "last_modified": new_lm, "last_pulled": now_iso(), "policy": "reference",
            "meta": {k: val for k, val in meta.items() if k not in ("name", "last_modified", "visibility")},
        }
        if existing:
            sj["sources"] = [entry if s["uri"] == uri else s for s in sj["sources"]]
        else:
            sj["sources"].append(entry)
        save_json(spath, sj)
        if not proj.get("name") and meta.get("name"):
            proj["name"] = meta["name"]
        proj["updated"] = now_iso()
        save_json(v / "projects" / proj["slug"] / "project.json", proj)
        changed += 1
    print(json.dumps({"changed": changed, "unchanged": unchanged}))


def render_project_md(v, proj, sj):
    lines = [f"# {proj['name']}", ""]
    if proj.get("summary"):
        lines += [proj["summary"], ""]
    meta = []
    if proj.get("category"):
        meta.append(f"**Category:** {proj['category']}")
    if proj.get("status"):
        meta.append(f"**Status:** {proj['status']}")
    if meta:
        lines += ["  ·  ".join(meta), ""]
    lines += [f"`{proj['id']}` · updated {proj.get('updated', '')}", "",
              "## Sources", "", "| Type | Role | Location | Last modified |", "|---|---|---|---|"]
    for s in sj.get("sources", []):
        lines.append(f"| {s['type']} | {s.get('role') or ''} | {s['uri']} | {s.get('last_modified') or ''} |")
    (v / "projects" / proj["slug"] / "project.md").write_text("\n".join(lines) + "\n")


def cmd_render(args):
    v = vault_dir(args)
    projects = load_projects(v)
    index = []
    for proj in projects:
        sj = load_json(v / "projects" / proj["slug"] / "sources.json") or {"sources": []}
        srcs = [{"type": s["type"], "role": s.get("role"), "uri": s["uri"]} for s in sj["sources"]]
        index.append({
            "id": proj["id"], "slug": proj["slug"], "name": proj["name"],
            "category": proj.get("category"), "status": proj.get("status"),
            "summary": proj.get("summary"), "source_count": len(srcs),
            "sources": srcs, "updated": proj.get("updated"),
        })
        render_project_md(v, proj, sj)
    save_json(v / "index.json", {"generated": now_iso(), "project_count": len(index), "projects": index})
    lines = ["# Project vault index", "",
             f"{len(index)} projects · generated {now_iso()}", "",
             "Generated from project records. Do not hand-edit; re-run the project-vault skill.", "",
             "| Project | Category | Status | Description | Sources |", "|---|---|---|---|---|"]
    for p in index:
        s = " ".join(x["type"] for x in p["sources"]) or "—"
        desc = (p.get("summary") or "").replace("|", "/").replace("\n", " ")
        lines.append(f"| [{p['name']}](projects/{p['slug']}/project.md) | {p.get('category') or ''} | {p.get('status') or ''} | {desc} | {s} |")
    (v / "index.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"projects": len(index)}))


def cmd_refresh(args):
    cmd_discover(args)
    cmd_enrich(args)
    cmd_render(args)


def cmd_status(args):
    v = vault_dir(args)
    projects = load_projects(v)
    matches = load_matches(v)
    disc = load_json(v / ".cache" / "discovered.json") or {"items": []}
    by_type = {}
    for proj in projects:
        sj = load_json(v / "projects" / proj["slug"] / "sources.json") or {"sources": []}
        for s in sj["sources"]:
            by_type[s["type"]] = by_type.get(s["type"], 0) + 1
    linked = set(matches["links"])
    unlinked = [it["uri"] for it in disc["items"] if it["uri"] not in linked and it["uri"] not in matches["rejects"]]
    print(json.dumps({
        "projects": len(projects), "sources_by_type": by_type,
        "links": len(matches["links"]), "rejects": len(matches["rejects"]),
        "discovered": len(disc["items"]), "unlinked": len(unlinked),
    }, indent=2))


# ---- cli ------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(description="project-vault engine.")
    p.add_argument("--vault", help="vault path (default ./vault or $PROJECT_VAULT)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="scaffold the vault").set_defaults(func=cmd_init)

    sp = sub.add_parser("discover", help="run connectors, cache discovered items")
    sp.add_argument("--connector", help="run only this connector")
    sp.set_defaults(func=cmd_discover)

    sub.add_parser("propose", help="classify discovered items vs the ledger (non-mutating)").set_defaults(func=cmd_propose)

    sp = sub.add_parser("link", help="link a source uri to a project")
    sp.add_argument("uri")
    sp.add_argument("--project", help="existing project id")
    sp.add_argument("--new", action="store_true", help="create a new project")
    sp.add_argument("--name", help="name for --new")
    sp.add_argument("--type", help="category for --new")
    sp.set_defaults(func=cmd_link)

    sp = sub.add_parser("reject", help="mark a source uri as not-a-project")
    sp.add_argument("uri")
    sp.set_defaults(func=cmd_reject)

    sp = sub.add_parser("enrich", help="fetch metadata for linked sources")
    sp.add_argument("--connector", help="enrich only this connector's sources")
    sp.set_defaults(func=cmd_enrich)

    sub.add_parser("render", help="regenerate index + per-project markdown").set_defaults(func=cmd_render)

    sp = sub.add_parser("refresh", help="discover + enrich changed + render")
    sp.add_argument("--connector")
    sp.set_defaults(func=cmd_refresh)

    sub.add_parser("status", help="vault summary").set_defaults(func=cmd_status)
    return p


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
