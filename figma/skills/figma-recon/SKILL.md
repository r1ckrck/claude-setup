---
name: figma-recon
description: >
  Build and maintain a detailed, cached source-of-truth inventory of a Figma
  team's work, using the Figma REST API for breadth (the map) and the Figma MCP
  for depth (the lens). Use this whenever the user says "recon my figma", "figma
  inventory", "index figma", "catalog figma", "pull my figma", "refresh figma",
  "what's in my figma", "list my figma files/projects", asks which design files
  exist for a team, or shares a figma.com URL to catalog — even if they don't say
  the word "skill". Always pull in full detail (never shallow-scrape), cache every
  fetch to a working folder, treat the cache as source of truth, and refresh
  incrementally by comparing last_modified so nothing is re-fetched needlessly.
  Use cheap REST listing to narrow candidates, then spend scarce MCP calls only
  on the files that matter. Read variables and design tokens through the MCP only —
  never via REST (that endpoint is Enterprise-only). Respect rate limits.
allowed-tools: Bash(python3 .claude/skills/figma-recon/scripts/figma_recon.py:*), Read, Write, Edit, mcp__figma__whoami, mcp__figma__get_metadata, mcp__figma__get_variable_defs, mcp__figma__get_design_context, mcp__figma__get_screenshot, mcp__figma__get_libraries
user-invocable: true
---

# figma-recon

Catalog a Figma team into a cached, source-of-truth inventory. The REST API is the
**map** — breadth across a team's projects and files, read-only, no file URL needed
(it needs a `team_id`). The MCP is the **lens** — depth inside one file at a time,
which needs a file URL. Spend the scarce MCP budget only on files the cheap REST
listing already narrowed.

This skill is project-agnostic. It hardcodes no team, no project, no absolute path.
It writes to `./docs/figma/` relative to the current working directory and reads the
token from `~/.figma-token`. Move it or share it freely.

## Pre-flight

1. **Resolve the team.** Run `mcp__figma__whoami` (exempt from the MCP budget) to
   confirm identity and list the teams. If the in-scope team isn't already known
   from the project's `CLAUDE.md`, **stop and ask the user which one** — only one
   team is in scope per run. Grab its `team_id` (the digits after `team::`).
2. **Confirm the token.** Check `~/.figma-token` exists and is mode `600`. Never
   print, echo, or paste its contents. If missing, tell the user to create it
   (`printf '%s' '<token>' > ~/.figma-token && chmod 600 ~/.figma-token`) and stop.
3. **Output folder.** Outputs go to `./docs/figma/` (created on first write).

## Decision rule — which tool for what

| Need | Tool | Why |
|---|---|---|
| List a team's projects | REST `list-projects` (Tier 3) | breadth, generous limit |
| List a project's files (key, name, thumbnail_url, last_modified) | REST `list-files` (Tier 3) | breadth; drives the refresh diff |
| Shallow file info (version, last_modified) | REST `file-meta` (Tier 1) | cheap with `depth=1`, use deliberately |
| Components / styles / component sets | REST `components`/`styles`/`component-sets` (Tier 3) | design-system breadth |
| Version history, comments | REST `versions`/`comments` (Tier 2/3) | provenance |
| Render node images / thumbnails | REST `images` (Tier 1) | **gated** — skip unless explicitly asked |
| File structure / pages / node tree | MCP `get_metadata` | depth, needs file URL |
| Design-to-code context | MCP `get_design_context` | depth |
| Screenshot of a node | MCP `get_screenshot` | depth |
| **Variables / design tokens** | **MCP `get_variable_defs` ONLY** | REST variables are Enterprise-only; on Pro/Student it returns 403. Never attempt REST variables. |
| Library enumeration | MCP `get_libraries` | depth |

## Workflow

Run the engine from the project root with its full relative path. `--out` may come before or
after the subcommand:
`python3 .claude/skills/figma-recon/scripts/figma_recon.py [--out <dir>] <command> [args]`

To wrap it, use a shell function (with `"$@"`), never a bare variable — an unquoted variable
splits the path into separate words:
`fr(){ python3 .claude/skills/figma-recon/scripts/figma_recon.py "$@"; }`

1. **Map pass (REST, cheap).** `map <team_id> --team-name "<name>" --handle "<handle>"`
   pulls projects, then files for each. Writes `index.json` + per-project
   `project.json`. This is breadth to narrow candidates.
2. **Diff.** `list-files` reports `changed` vs `unchanged` by comparing each file's
   incoming `last_modified` to the cached `last_pulled`. Unchanged files are no-ops —
   don't re-pull them.
3. **Narrow.** Present the candidate files (new or changed). Let the user or the task
   pick which deserve a lens pass. Don't open files just to look.
4. **Lens pass (MCP, scarce).** For chosen files only: `get_metadata` for structure,
   then `get_variable_defs` for tokens. Reserve `get_design_context` / `get_screenshot`
   for files the user explicitly selects (budget-heavy). Pace under 15/min; stop near
   200/day and report remaining headroom. See MCP caveats below.
5. **Write detail.** For structure, run `parse-metadata <saved-file> <file-key>` (the
   engine parses the captured `get_metadata` output into the per-file JSON). Add
   `get_variable_defs` and `get_libraries` results under `variables` / `libraries`
   (annotate `source: mcp`). REST sub-resources are merged by the engine. All writers
   top-level-merge, so none clobbers the others.
6. **Render + stamp.** `render` regenerates all markdown from the JSON. Update
   `last_pulled` / freshness. Markdown is derived — never hand-edit it.

## MCP caveats (verified)

The remote Figma MCP works **headlessly** — the desktop app does not need to be open.
`whoami`, `get_metadata`, and `get_variable_defs` all return data on their own.

- **`get_metadata` for a whole page is large, and that's the point.** Call it with no
  `nodeId` first to list pages, then pass a page id to pull the full subtree. When the
  response overflows context the harness saves it to a tool-results file — capture that
  full output and parse it with the engine: `parse-metadata <saved-file> <file_key>`.
  This stores the complete structure (type counts, node count, top-level nodes) into the
  per-file JSON deterministically. Capturing-full-then-script-parsing is the intended
  detailed-pull path — don't shallow-skim.
- **`get_variable_defs` needs a concrete node id that actually binds variables.** The page
  root (`0:1`) returns a misleading "nothing selected"; a node with no bindings returns
  `{}`; a frame/instance that uses tokens returns the definitions (colors, fonts, etc.).
  Drill to a real bound node — get ids from the parsed structure. Variables stay MCP-only
  (never REST).

## Rate limits & smart usage

REST is a per-minute leaky bucket by endpoint tier. On HTTP `429`, honor the
`Retry-After` header (the engine does this automatically). Tier 1 (file GET, image
render) is tightest (~10–20/min) — treat renders as expensive. Tier 3 (projects,
files, components) is generous (~50–150/min) — safe for breadth. The MCP budget on a
Pro Full seat is **200 calls/day, 15/min**; `whoami` is exempt.

Five laws:

1. Fetch once, cache, treat the cache as truth.
2. Refresh incrementally via `last_modified` — never re-fetch an unchanged file.
3. Skip thumbnails / image renders unless asked (Tier 1).
4. Use cheap Tier-3 listing to narrow; spend MCP only on chosen files.
5. Pace, never burst.

Full detail: `references/rate-limits.md`. Endpoint reference: `references/rest-endpoints.md`.
Working-folder schema: `references/schema.md`.

## Documentation discipline

**Always**
- Pull in full detail — every field the schema lists for that level. Never shallow-scrape.
- Cache to `docs/figma/` before using the data.
- Stamp `last_refreshed` / `last_pulled`.
- Keep both the JSON snapshot (source of truth) and the derived markdown at each level.

**Never**
- Re-fetch a file whose `last_modified` is unchanged.
- Hit REST for variables/tokens — that's the MCP's job.
- Print, echo, or write the token anywhere.
- Catalog more than the one in-scope team in a run.
- Hand-edit generated files (re-run the engine) or add history / meta-comments —
  outputs carry current state only.

## Out of scope

No writing or generating in Figma (this skill reads and catalogs only — use the
Figma write tools for that). No multi-team crawl. No token provisioning. No
design or strategy decisions — those live in the project's own docs.
