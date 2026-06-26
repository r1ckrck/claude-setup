---
name: osxphotos
description: Drive the osxphotos CLI to query, export, delete, import, modify, and audit photos in the user's Apple Photos library on macOS. Invoke whenever the user asks about their Photos app library, screenshots, photo metadata, photo exports, photo cleanup, photo deletion, or photo management. Also invoke for any task that involves reading from or writing to a Photos library — filtering by date/person/album/keyword, exporting originals to disk, deleting duplicates or unwanted photos, batch-editing metadata, fixing timestamps, importing new files, comparing libraries, or snapshot-based audit. Covers all 28 commands, the filename/path template DSL, iCloud "Optimize Mac Storage" download behavior, macOS TCC permission model (Full Disk Access, Photos, Automation), and the Terminal.app delegation mechanism required when mutating the library from VS Code or Claude Code.
---

# osxphotos

A macOS-only CLI for working with the Apple Photos library. Reads the Photos SQLite database directly for queries and uses PhotoKit + AppleScript for writes. Invoked as `osxphotos` (installed globally via pipx).

## Mental model

The tool has four jobs. Match the user's intent to the right job first, then pick the command.

| Job | Primary command | Reference |
|---|---|---|
| **Find** photos by any criteria | `osxphotos query …` | [query.md](references/query.md) |
| **Export / move** photos to disk | `osxphotos export DEST …` | [export.md](references/export.md) |
| **Delete** photos from the library | `osxphotos delete --uuid-from-file FILE` | [delete.md](references/delete.md) |
| **Audit** library state before/after changes | `osxphotos snap`, `osxphotos diff` | [audit.md](references/audit.md) |

Most Claude-driven workflows are a loop of **find → export → review → delete**, with optional audit snapshots around the destructive step. See [workflows.md](references/workflows.md) for recipes.

## All commands at a glance

28 registered commands. Columns: command | what it does | where to read more.

### Core (daily use)

| Command | Purpose | Detail |
|---|---|---|
| `query` | Filter the library by ~80 criteria; output list / count / JSON / templated fields | [query.md](references/query.md) |
| `export DEST` | Copy photos to a folder with templated paths; handles iCloud download; supports sidecars | [export.md](references/export.md) |
| `delete` | Move photos to Recently Deleted via PhotoKit (30-day grace, iCloud-synced) | [delete.md](references/delete.md) |
| `show UUID_OR_NAME` | Scroll Photos.app to a specific photo, album, or folder | [show.md](references/show.md) |
| `info` | Library stats: photo/album/person/keyword counts, storage, library version | [discovery.md](references/discovery.md) |

### Discovery (browse metadata)

| Command | Purpose |
|---|---|
| `albums` | List all albums with photo counts |
| `keywords` | List keywords with counts |
| `labels` | List ML classification labels (Photos 5+) |
| `persons` | List detected faces with counts |
| `places` | List reverse-geocoded place names with counts |
| `grep` | Raw SQL grep across the Photos DB |
| `list` (`list-libraries`) | Find all Photos libraries on disk |

All covered in [discovery.md](references/discovery.md).

### Audit (library state)

| Command | Purpose |
|---|---|
| `snap` | Save a timestamped snapshot of the Photos DB |
| `diff` | Compare current DB to a snapshot (needs `sqldiff`) |
| `compare` | Compare two Photos libraries |
| `orphans` | Find DB entries with no file on disk |
| `uuid` | Print UUIDs of currently-selected photos in Photos.app |
| `inspect` | Live inspector — metadata for whichever photo you select in Photos |

All covered in [audit.md](references/audit.md).

### Modify (write operations)

| Command | Purpose |
|---|---|
| `import` | Import files/folders into the library |
| `batch-edit` | Bulk set title/description/keyword/album/favorite/location |
| `timewarp` | Adjust date/time/timezone on photos |
| `push-exif` | Write Photos metadata back to original files via exiftool |
| `add-locations` | Reverse-geocode GPS coords into place names |
| `sync` | Sync metadata between two libraries |

All covered in [modify.md](references/modify.md).

### Scripting

| Command | Purpose |
|---|---|
| `repl` | Interactive Python shell with library pre-loaded |
| `run SCRIPT` | Execute a Python file with osxphotos API available |
| `exiftool` | Passthrough to the bundled exiftool binary |
| `version` | Print version |

All covered in [scripting.md](references/scripting.md).

## Cross-cutting concerns

These apply to many commands — keep them in mind when choosing flags.

### Template DSL

Fields like `--directory`, `--filename`, `--field NAME TEMPLATE`, `--print`, `--title`, `--description`, `--keyword`, `--album` (in batch-edit and import) accept template strings: `{uuid}`, `{created.year}/{created.mm}`, `{album}/{original_name}`, etc. Full substitution list and filter syntax in [templates.md](references/templates.md).

### iCloud "Optimize Mac Storage"

Most photos in a typical library are iCloud-only — thumbnails local, originals in the cloud. Exports need `--download-missing` for iCloud-only files to pull them on demand. Query flags `--cloudasset`, `--incloud`, `--missing`, `--not-missing` filter by cloud state. Full detail in [icloud.md](references/icloud.md).

### Permissions and TCC delegation

Three separate macOS permissions matter:
- **Full Disk Access** — required for any read; grant to Terminal / iTerm / VS Code / Claude Code
- **Photos library access** — required for writes (delete, etc.); only apps declaring `NSPhotoLibraryUsageDescription` can request it (Terminal yes, VS Code/Claude Code no)
- **Automation** — required for `show` and for the delete auto-delegation

When `delete` is called from a host without Photos access, it transparently re-invokes itself via `osascript → Terminal.app`, which has the right TCC identity. First run triggers a one-time "X wants to control Terminal" prompt. Full detail in [permissions.md](references/permissions.md).

### Output formats

Most read commands support:
- **Default**: human-readable YAML (for `albums`, `keywords`, etc.) or list (for `query`)
- **`--json`**: machine-readable JSON
- **`--count`**: just the number (query only)
- **`--field NAME TEMPLATE`**: custom CSV-like columns via templates (query)
- **`--print TEMPLATE`**: render a template per photo (query, export)
- **`--report FILE`**: CSV or SQLite report (export, push-exif, etc.)

## Top gotchas (full catalog in [gotchas.md](references/gotchas.md))

1. **"missing: N" in export** — iCloud Optimize Storage is on. Add `--download-missing`.
2. **`PhotoKitAuthError auth_status=2`** — caller app lacks Photos TCC. `delete` auto-delegates to Terminal; other write paths don't. Run those from Terminal.app directly.
3. **`show UUID` fails once** — Photos.app cold-start AppleScript timeout. Retry.
4. **OS delete dialog can't be skipped** — Apple enforces one confirmation per `delete` call. Always batch UUIDs into a single file to make it one click for many photos.
5. **Shared Library deletions propagate to all participants** — no in-tool warning yet. Check `--shared-library` before deleting.
6. **`{counter}` is not stable across runs** — use `{id}` for stable identifiers with `--update`.

## Global flags (most commands)

- `--library PATH` / `--db PATH` — specify Photos library (defaults to last-opened, then system library, then `~/Pictures/Photos Library.photoslibrary`)
- `--json` — JSON output (where supported)
- `--verbose` / `-V` — verbose; repeatable for more detail
- `--timestamp` — add timestamps to verbose output
- `--theme dark|light|mono|plain` — output color theme
- `--help` / `-h` — show command help

## Quickest path to useful output

When the user first engages with the library, these three commands orient Claude fast:

```bash
osxphotos info                           # library scale + structure
osxphotos query --count                  # total photo count
osxphotos query --screenshot --count     # screenshots specifically
```

From there, branch into the specific task and the reference file that matches it.
