# Vault schema

All machine state is JSON; markdown views are rendered from it. Files keyed by stable
`id` (project) and source `uri`.

## Layout

```
vault/
├── connectors.json     # config (which sources, accounts, paths) — gitignored
├── matches.json        # the ledger
├── index.json / index.md   # generated aggregate
├── .cache/             # discovered.json, proposals.json, figma/ (gitignored)
└── projects/<slug>/
    ├── project.json
    ├── sources.json
    └── project.md      # rendered
```

## connectors.json

`{ "connectors": { "<type>": { "enabled": bool, ...type-specific } } }`. See
`connectors.example.json`. Type-specific keys:

- **localfs**: `roots[]` (paths, `~` ok), `exclude[]`
- **github**: `user`, `limit`
- **figma**: `team_id`, `team_name`, `handle`, `recon_path` (path to figma-recon engine), `cache_dir` (null → `<vault>/.cache/figma`)
- **webfetch**: `urls[]`

No secrets here — connectors that need a token read it from a path the connector owns
(e.g. figma-recon reads `~/.figma-token`). This file is gitignored.

## matches.json — the ledger

```json
{ "links": { "<source_uri>": "<project_id>" }, "rejects": ["<source_uri>"] }
```

`links` maps each confirmed source location to its canonical project id. `rejects` are
URIs the user marked as not-a-project. The engine reads this before proposing, so confirmed
decisions never get re-asked.

## project.json

```json
{
  "id": "p_ab12cd34", "slug": "maanak", "name": "Maanak",
  "category": "tooling", "status": "", "tags": [], "summary": "",
  "created": "2026-...Z", "updated": "2026-...Z"
}
```

`id` is the stable key (`p_` + 8 hex), generated once. `slug` is the folder name; on name
collision it gets a `-2`/`-3` suffix while the `id` stays unique.

## sources.json

```json
{
  "project_id": "p_ab12cd34",
  "sources": [
    {
      "type": "github", "role": "code", "uri": "https://github.com/u/maanak",
      "visibility": "public", "last_modified": "2026-...Z", "last_pulled": "2026-...Z",
      "policy": "reference", "meta": { "language": "TypeScript", "...": "..." }
    }
  ]
}
```

`role` ∈ code / design / docs / deck / data / live. `policy` is `reference` in v1
(metadata only; nothing copied). `meta` holds connector-specific fields.

## index.json (generated)

```json
{ "generated": "...", "project_count": N,
  "projects": [ { "id", "slug", "name", "category", "status", "summary",
                  "source_count", "sources": [{"type","role","uri"}], "updated" } ] }
```

Refresh is a diff: a source whose `last_modified` is unchanged is a no-op.
