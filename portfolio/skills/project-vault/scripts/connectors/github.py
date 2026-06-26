"""github connector — wraps the `gh` CLI (uses gh's own auth; no token handling here)."""

import json
import subprocess

FIELDS = "name,description,visibility,isFork,isArchived,primaryLanguage,pushedAt,url"


def _run(args):
    return subprocess.run(args, capture_output=True, text=True)


def discover(config):
    limit = str(config.get("limit", 300))
    r = _run(["gh", "repo", "list", "--limit", limit, "--json", FIELDS])
    if r.returncode != 0:
        raise RuntimeError("gh repo list failed: " + r.stderr.strip())
    items = []
    for repo in json.loads(r.stdout):
        items.append({
            "uri": repo["url"], "type": "github", "role": "code", "name": repo["name"],
            "meta": {
                "visibility": (repo.get("visibility") or "").lower(),
                "fork": repo.get("isFork"), "archived": repo.get("isArchived"),
                "language": (repo.get("primaryLanguage") or {}).get("name"),
                "pushed_at": repo.get("pushedAt"), "description": repo.get("description"),
            },
        })
    return items


def fetch_meta(uri, config):
    slug = "/".join(uri.rstrip("/").split("/")[-2:])
    r = _run(["gh", "repo", "view", slug, "--json", "name,visibility,primaryLanguage,pushedAt,description"])
    if r.returncode != 0:
        raise RuntimeError("gh repo view failed: " + r.stderr.strip())
    d = json.loads(r.stdout)
    return {
        "name": d.get("name"),
        "last_modified": d.get("pushedAt"),
        "visibility": (d.get("visibility") or "").lower(),
        "language": (d.get("primaryLanguage") or {}).get("name"),
        "description": d.get("description"),
    }
