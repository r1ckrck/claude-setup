# REST endpoints

Base URL: `https://api.figma.com/v1`. Auth header: `X-Figma-Token: <personal access token>`
(personal tokens use this header; OAuth apps use `Authorization: Bearer`). All endpoints
below are read-only `GET`. The engine cannot enumerate teams — a `team_id` must be supplied
(get it from `mcp__figma__whoami`, the digits after `team::`).

## Endpoint table

| Endpoint | Purpose | Key returned fields | Tier / caveats |
|---|---|---|---|
| `/teams/:team_id/projects` | List a team's projects | `name` (team), `projects[]`: `id`, `name` | Tier 3 (generous) |
| `/projects/:project_id/files` | List a project's files | `files[]`: `key`, `name`, `thumbnail_url`, `last_modified` | Tier 3 |
| `/files/:key` | File document | `name`, `lastModified`, `version`, `thumbnailUrl`, `document` tree | Tier 1 (tight). Use `depth=1` for a shallow, cheap read; omit for full tree (large). |
| `/files/:key/nodes?ids=` | Specific nodes only | per-node `document`, `components`, `styles` | Tier 1. Cheaper than full file when you know the node ids. |
| `/files/:key/versions` | Version history | `versions[]`: `id`, `label`, `created_at`, `user.handle` | Tier 2/3 |
| `/files/:key/comments` | Comments | `comments[]`: `id`, `message`, `user`, `created_at` | Tier 2 |
| `/files/:key/components` | Components in a file | `meta.components[]`: `key`, `name`, `description`, `containing_frame` | Tier 3 |
| `/files/:key/component_sets` | Component sets in a file | `meta.component_sets[]` | Tier 3 |
| `/files/:key/styles` | Styles in a file | `meta.styles[]`: `key`, `name`, `style_type` | Tier 3 |
| `/teams/:team_id/components` | Published components, team-wide | `meta.components[]` + `meta.cursor` | Tier 3, **cursor-paginated** |
| `/teams/:team_id/component_sets` | Published component sets | `meta.component_sets[]` + cursor | Tier 3, paginated |
| `/teams/:team_id/styles` | Published styles, team-wide | `meta.styles[]` + cursor | Tier 3, paginated |
| `/images/:key?ids=&format=` | Render nodes to PNG/SVG/PDF/JPG | `images{ nodeId: url }` | Tier 1 (tightest). **Gated** — only on explicit request. |
| `/files/:key/images` | Image-fill URLs | `meta.images{ ref: url }` | Tier 1 |

## Variables — not available here

`GET /files/:key/variables/local` and `/variables/published` exist, but Figma restricts them:

> "This API is available to full members of Enterprise orgs."

Personal/Pro/Student accounts get `403`. **Read variables and tokens through the MCP**
(`mcp__figma__get_variable_defs`) instead. The engine deliberately ships no variables
command so it cannot be misused.

## Pagination

Project and file lists are not paginated — one call returns everything. Team-level
`components` / `component_sets` / `styles` are cursor-paginated: the response carries
`meta.cursor.after`; pass it back as the `after` query param until it's absent.

## Building a shareable URL from a file key

```
https://www.figma.com/design/<file_key>/<url-encoded-name>
```

The path segment differs by file kind: `/design/` for design files, `/board/` for FigJam,
`/slides/` for Slides. The REST file/project endpoints return design files; FigJam and
Slides have limited REST coverage and are best inspected via the MCP screenshot tool.
