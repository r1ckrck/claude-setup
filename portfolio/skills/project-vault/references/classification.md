# Bulk classification

The one-by-one `link` flow and the name-similarity `propose` step handle the easy cases: a
source whose name matches an existing project, or a single new project to add. They fall
short when the mapping between sources and projects isn't one-to-one:

- **Many sources → one product.** Several Figma files of one journey, a GitHub repo, a local
  folder, and a live URL are all the same project. Name similarity won't always connect them.
- **One broad source → many products.** A single Figma team (or a catch-all repo) holds files
  spanning many distinct products that should each become their own project.

Both need judgment — which files belong together — that no string match can supply. Capture
that judgment in a **manifest**, then apply it in bulk with `populate.py`.

## Recipe

1. **discover** — `vault.py discover` caches candidates to `.cache/discovered.json`.
2. **group** — read `.cache/discovered.json` and decide the projects: which source URIs belong
   to each, splitting broad sources and merging scattered ones as needed.
3. **manifest** — write those decisions as a manifest (schema below). The manifest is the
   confirmation: it records a decision already made, so "propose, don't auto-merge" holds.
4. **populate** — `populate.py <manifest.json>` creates each project and points its sources at
   it in the ledger. A source already linked to another project is skipped, never re-pointed.
5. **enrich → render** — `vault.py enrich` pulls metadata for the new links; `vault.py render`
   rebuilds the index.

```
python3 .claude/skills/project-vault/scripts/populate.py <manifest.json> [--vault <path>] [--dry-run]
```

Run `--dry-run` first to print the create/link plan without writing.

## Manifest schema

```json
{
  "projects": [
    {
      "name": "FD Post-Payment",
      "category": "product",
      "status": "",
      "summary": "one-line description",
      "tags": [],
      "sources": [
        "figma:project/123",
        "https://github.com/u/repo",
        "/abs/local/path",
        "https://live.url"
      ]
    }
  ]
}
```

Only `name` is required. `category`, `status`, `summary`, `tags` land in `project.json`;
each `sources` URI becomes a ledger link. `populate.py` does not enrich or render — those
stay separate steps.

## When to use which

- **`populate.py`** — initial or bulk population, and any time the source-to-project mapping
  needs judgment (grouping or splitting).
- **`link` / `reject`** — adding or placing a single source later, once the vault exists.
