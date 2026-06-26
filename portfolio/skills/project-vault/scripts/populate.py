#!/usr/bin/env python3
"""Bulk-create projects and link their sources from a confirmed manifest.

The manifest carries the grouping judgment — which sources belong to which project —
authored and reviewed before running. That review is the confirmation, so the
"propose, don't auto-merge" rule still holds: nothing here decides what is the same
project; it executes a decision already made.

Manifest shape:

    {
      "projects": [
        { "name": "FD Post-Payment", "category": "product", "status": "",
          "summary": "...", "tags": [],
          "sources": ["figma:project/123", "https://github.com/u/repo", "/abs/path"] }
      ]
    }

For each project: create the record, set its summary/status/tags, then point every
listed source at it in the ledger. A source already linked to another project is
skipped (never silently re-pointed). This step does not enrich or render — run
`vault.py enrich` then `vault.py render` afterwards to pull metadata and rebuild
the index.

    python3 .claude/skills/project-vault/scripts/populate.py <manifest.json> [--vault <path>] [--dry-run]
"""

import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import vault  # noqa: E402


def load_manifest(path):
    if not os.path.exists(path):
        sys.exit(f"manifest not found: {path}")
    try:
        data = json.loads(open(path).read())
    except json.JSONDecodeError as e:
        sys.exit(f"manifest is not valid JSON: {e}")
    projects = data.get("projects")
    if not isinstance(projects, list):
        sys.exit('manifest must have a "projects" list')
    for i, p in enumerate(projects):
        if not p.get("name"):
            sys.exit(f"project at index {i} has no name")
    return projects


def main():
    ap = argparse.ArgumentParser(description="bulk-create projects + link sources from a manifest")
    ap.add_argument("manifest", help="path to the manifest JSON")
    ap.add_argument("--vault", help="vault path (default ./vault or $PROJECT_VAULT)")
    ap.add_argument("--dry-run", action="store_true", help="print the plan; write nothing")
    args = ap.parse_args()

    v = vault.vault_dir(args)
    projects = load_manifest(args.manifest)
    matches = vault.load_matches(v)

    created, skipped = [], []
    linked = 0

    for spec in projects:
        name = spec["name"]
        category = spec.get("category", "")
        sources = spec.get("sources", []) or []

        if args.dry_run:
            pid, slug = "(dry-run)", vault.slugify(name)
        else:
            pid = vault.create_project(v, name, category)
            proj = vault.find_project_by_id(v, pid)
            slug = proj["slug"]
            proj["summary"] = spec.get("summary", "")
            proj["status"] = spec.get("status", "")
            proj["tags"] = spec.get("tags", []) or []
            proj["updated"] = vault.now_iso()
            vault.save_json(v / "projects" / slug / "project.json", proj)

        created.append({"name": name, "id": pid, "slug": slug, "sources": len(sources)})

        for uri in sources:
            existing = matches["links"].get(uri)
            if existing and existing != pid:
                skipped.append({"uri": uri, "reason": f"already linked to {existing}"})
                continue
            if not args.dry_run:
                matches["links"][uri] = pid
                if uri in matches["rejects"]:
                    matches["rejects"].remove(uri)
            linked += 1

    if not args.dry_run:
        vault.save_matches(v, matches)

    for s in skipped:
        sys.stderr.write(f"skip {s['uri']}: {s['reason']}\n")

    print(json.dumps({
        "dry_run": args.dry_run,
        "projects_created": len(created),
        "sources_linked": linked,
        "sources_skipped": len(skipped),
        "next": "run `vault.py enrich` then `vault.py render`",
        "created": created,
        "skipped": skipped,
    }, indent=2))


if __name__ == "__main__":
    main()
