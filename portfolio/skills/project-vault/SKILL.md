---
name: project-vault
description: >
  Index and store a person's projects pulled from many sources into one canonical vault.
  A project is logical (one record); its files are physical and scattered across local
  folders, GitHub repos, Figma projects, and live sites — so one project can have many
  sources. Use this whenever the user says "index my projects", "project vault", "catalog
  my work", "what projects do I have", "pull my projects from github/figma/local/my site",
  "add a project" or "add a source", "link these as the same project", "refresh the vault",
  or wants a single source of truth across scattered work — even if they don't say "skill".
  Discover items from each connector, propose matches against a ledger so the same project
  across sources collapses into one record, let the user confirm (never auto-merge), then
  enrich and render the index. Reference-only in v1 — store metadata + pointers, never copy
  source files, never store secrets.
allowed-tools: Bash(python3 .claude/skills/project-vault/scripts/vault.py:*), Bash(python3 .claude/skills/project-vault/scripts/populate.py:*), Bash(gh:*), Bash(python3 .claude/skills/figma-recon/scripts/figma_recon.py:*), Read, Write, Edit
user-invocable: true
---

# project-vault

Index and store projects from heterogeneous sources into one **vault**. The split mirrors
`figma-recon`: this skill is the *how* (workflow, connectors, rules); the `vault/` folder is
the *what* (the records). A **project** is the logical unit; it has many **sources**
(physical locations). The same project across GitHub + Figma + local + a live site is one
project with several sources.

Project-agnostic: no accounts, teams, or absolute paths live in the skill. The vault is one
global store (default `./vault`, override with `--vault` or `$PROJECT_VAULT`). JSON is the
source of truth; markdown is rendered. Stdlib-only Python.

Run the engine from the repo root with its full relative path. `--vault` may come before or
after the subcommand:
`python3 .claude/skills/project-vault/scripts/vault.py <command> [--vault <path>]`

To wrap it, use a shell function (with `"$@"`), never a bare variable — an unquoted variable
splits the path into separate words:
`pv(){ python3 .claude/skills/project-vault/scripts/vault.py "$@"; }`

## Pre-flight

1. **Resolve the vault.** If it has no `connectors.json`, run `init` — it scaffolds the
   vault and copies the example config. Then **ask the user to fill `connectors.json`**:
   which connectors to enable, their accounts (GitHub user, Figma team), local roots, site
   URLs. Nothing is discovered until a connector is `enabled`.
2. **Tokens.** Connectors that need auth read it from a path they own (e.g. figma-recon
   reads `~/.figma-token`; `gh` uses its own login). Never put tokens in `connectors.json`.

## Connectors (v1)

| Connector | Discovers | Reuses |
|---|---|---|
| `localfs` | child folders of configured roots | — |
| `github` | your repos | `gh` CLI |
| `figma` | your Figma projects | the `figma-recon` engine |
| `webfetch` | a live URL (e.g. a personal site) | stdlib urllib |

Contract + how to add one: `references/connectors.md`. Config shapes: `references/schema.md`.

## Workflow

1. **discover** — `vault.py discover` runs every enabled connector, caches items.
   `--connector <name>` runs just one (useful for a smoke test).
2. **propose** — `vault.py propose` classifies each item against the ledger: already
   **linked**, **suggested** (name-similar to an existing project), or **new**. Non-mutating.
3. **confirm** — present the proposals to the user. For each, run:
   - `vault.py link <uri> --project <id>` (attach to an existing project), or
   - `vault.py link <uri> --new --name "<Name>" --type <category>` (new project), or
   - `vault.py reject <uri>` (not a project).
   Never auto-merge — the user decides what is the same project.
   For initial or bulk population — and when the source-to-project mapping needs judgment
   (many sources → one product, or one broad source → many) — write a manifest and apply it
   with `populate.py` instead of linking one at a time. See `references/classification.md`.
4. **enrich** — `vault.py enrich` fetches metadata for every linked source and writes
   `project.json` + `sources.json` (policy `reference`).
5. **render** — `vault.py render` regenerates `index.json`, `index.md`, and per-project
   markdown.
6. **refresh** — `vault.py refresh` later: discover → enrich changed (by `last_modified`)
   → render. Unchanged sources are no-ops.

`vault.py status` prints counts and how many discovered items are still unlinked.

## Identity & the ledger

- Every project has a stable `id` (`p_` + 8 hex) plus a `slug` (folder name). Two projects
  with the same name get different ids and a disambiguated slug.
- `matches.json` maps `source-uri → project-id` and holds a reject list. It is the memory
  that stops the engine re-asking about a source you've already placed.

## Rules

**Always**
- Cache to the vault; treat the vault as the source of truth.
- Let the user confirm matches. Propose, don't merge.
- Stamp `last_modified` / `last_pulled`; refresh incrementally.

**Never**
- Store secrets — config references token paths only.
- Copy source files in v1 (reference policy; artifact capture comes later).
- Auto-merge two sources into one project without confirmation.
- Hand-edit generated files (`index.*`, per-project `.md`) — edit JSON and re-render.

## Out of scope

No artifact capture yet (no `artifacts/`). No writing back to any source. No multi-account
crawling beyond what `connectors.json` declares.
