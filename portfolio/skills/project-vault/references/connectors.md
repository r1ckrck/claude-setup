# Connectors

A connector is a Python module under `scripts/connectors/` registered in
`scripts/connectors/__init__.py` (`REGISTRY`). The engine is source-agnostic: it only
knows the contract.

## Contract

Each connector implements two functions:

```python
def discover(config) -> list[dict]:
    # config is the connector's block from connectors.json, plus an injected "_vault" path.
    # returns items: {"uri": str, "type": str, "role": str, "name": str, "meta": dict}

def fetch_meta(uri, config) -> dict:
    # returns: {"name", "last_modified", "visibility", ...type-specific}
```

- `uri` is the stable identity of a source location. It must be reproducible across runs
  (a path, a repo URL, a `figma:project/<id>`, a site URL) so the ledger stays valid.
- `discover` is cheap breadth. `fetch_meta` is per-source detail.
- `last_modified` drives incremental refresh — return the source's real value when possible.
- Never read or emit secrets. If a source needs a token, read it from a path the connector
  owns; never put a token in `connectors.json` or in returned data.

## v1 connectors

| Connector | `discover` returns | `fetch_meta` returns | Notes |
|---|---|---|---|
| **localfs** | one item per immediate child dir of each `root` | top file-type counts, total size, latest mtime | excludes node_modules/.git/etc. |
| **github** | `gh repo list` → one item per repo | name, pushed_at, visibility, language, description | uses `gh` auth; no token handling |
| **figma** | shells out to figma-recon `map`, then one item per Figma **project** | file_count, sample file names, newest file mtime | reuses figma-recon; cache in `<vault>/.cache/figma` |
| **webfetch** | one item per configured URL | page title, description, h1/h2 headings, link count | stdlib urllib + html.parser |

## Adding a connector

1. Write `scripts/connectors/<name>.py` with `discover` + `fetch_meta`.
2. Register it in `__init__.py`'s `REGISTRY`.
3. Add a config block to `connectors.example.json` and document it in `schema.md`.
4. The engine's `discover`/`enrich`/`infer_type` pick it up automatically by type name.

`infer_type` in `vault.py` maps a bare uri back to a connector when the discovered cache
isn't present (figma: → figma, github.com → github, http → webfetch, else localfs). If a
new connector's URIs aren't distinguishable, extend `infer_type`.
