# `osxphotos export`

Copy photos out of Photos.app to a folder on disk. Accepts every query flag (to filter what's exported) plus export-specific flags for destination, naming, metadata, and incremental update.

## Usage

```bash
osxphotos export DEST [OPTIONS]
```

`DEST` is the destination directory (required). If no query flags are provided, the entire library is exported.

## Examples

```bash
# Fresh export of all screenshots, pulling iCloud originals
osxphotos export ~/triage --screenshot --download-missing

# Organized by year/month, only photos from 2025
osxphotos export ~/Pictures/archive --year 2025 --download-missing \
  --directory "{created.year}/{created.mm}" \
  --filename "{original_name}"

# One-off export of a specific UUID
osxphotos export /tmp/test --uuid B62DE1BA-26BC-4DDD-A225-B128F55AFCB6

# Incremental: only copy what's changed since last export
osxphotos export ~/Pictures/archive --update

# Dry run — see what would happen, no files written
osxphotos export ~/Pictures/archive --screenshot --dry-run

# With JSON sidecar for each exported file
osxphotos export ~/triage --screenshot --sidecar json

# Write metadata directly into the exported files via exiftool
osxphotos export ~/triage --screenshot --exiftool
```

## Destination and naming

| Flag | Purpose |
|---|---|
| `DEST` (positional) | Base directory to export into |
| `--directory TEMPLATE` | Subdirectory structure under DEST. Templates allowed |
| `--filename TEMPLATE` | Exported filename. Default: original filename |
| `--edited-suffix SUFFIX` | Suffix on edited versions (default `_edited`) |
| `--jpeg-ext EXT` | Force a particular JPEG extension: `jpeg`, `jpg`, `JPEG`, `JPG` |
| `--original-name` | Use original camera filename |

See [templates.md](templates.md) for substitutions usable in `--directory` / `--filename`.

## iCloud handling

| Flag | Purpose |
|---|---|
| `--download-missing` | Tell Photos.app to download iCloud originals on demand (AppleScript bridge). **Required** if Optimize Mac Storage is on and you're exporting iCloud-only photos |
| `--use-photos-export` | Export through Photos.app (slower but more reliable for iCloud) |

> If export reports `missing: N` with N > 0, that's almost always iCloud photos without local originals. Add `--download-missing`.

## Update mode (incremental export)

| Flag | Purpose |
|---|---|
| `--update` | Only copy new or changed files. Uses `.osxphotos_export.db` for state |
| `--force-update` | Re-export if metadata changed, even if file bytes match |
| `--update-errors` | Re-export files that failed in a previous run |
| `--ignore-signature` | Skip size/date comparison when deciding if a file needs update |
| `--only-new` | Skip photos that were in the previous export, even if changed |
| `--retry N` | Retry each photo N times on failure |

The `.osxphotos_export.db` file is created at the root of DEST on first run. Delete it to force full re-export.

## Metadata and sidecars

| Flag | Purpose |
|---|---|
| `--exiftool` | Write metadata into exported files via the exiftool binary |
| `--exiftool-option OPT` | Pass a raw option to exiftool |
| `--sidecar FORMAT` | Emit a sidecar per photo. `FORMAT` ∈ {`json`, `xmp`, `exiftool`}. Repeatable |
| `--sidecar-drop-ext` | Name sidecars `photo.json` instead of `photo.jpg.json` |
| `--sidecar-template FORMAT TEMPLATE_FILE OUTPUT_TEMPLATE` | Custom sidecar via mako template |

### Which sidecar format to use

- **`json`** — machine-readable, most detailed. Best for piping to scripts, feeding to Claude, or archiving metadata cleanly alongside the original files
- **`xmp`** — Adobe / Lightroom / Bridge compatible. Use when the export is destined for a professional photo workflow
- **`exiftool`** — replayable JSON designed for `exiftool -json=file.json target.jpg`. Best for round-trip archival — later you can re-inject the metadata into the file with one exiftool command

## Filtering the export

All `query` flags work here. The most-used:

- `--uuid`, `--uuid-from-file`
- `--screenshot`, `--selfie`, `--live`, `--portrait`, `--panorama`
- `--album`, `--folder`, `--keyword`, `--person`
- `--from-date`, `--to-date`, `--year`
- `--favorite`, `--not-favorite`
- `--shared-library`, `--not-shared-library`
- `--edited`, `--not-edited`
- `--missing`, `--not-missing`

See [query.md](query.md) for the complete list.

## Skipping content

| Flag | Purpose |
|---|---|
| `--skip-edited` | Don't export edited versions |
| `--skip-original-if-edited` | Export only the edited version, not both |
| `--skip-bursts` | Don't export non-selected burst photos |
| `--skip-live` | Don't export the video component of Live Photos |
| `--skip-raw` | Don't export the RAW component of RAW+JPEG pairs |
| `--convert-to-jpeg` | Convert HEIC/PNG/etc. to JPEG (requires GPU) |
| `--jpeg-quality Q` | 0.0–1.0 quality when converting |

## Post-processing

| Flag | Purpose |
|---|---|
| `--post-command CATEGORY COMMAND` | Run a shell command after each photo. CATEGORY ∈ `exported`, `new`, `updated`, `skipped`, `missing`, `error`, `converted_to_jpeg`, `exif_updated`, `touched`, `removed` |
| `--post-function FILE.PY::FUNC` | Call a Python function after each photo |
| `--cleanup` | Delete files in DEST that weren't part of this export |
| `--keep PATTERN` | With `--cleanup`, preserve paths matching PATTERN (`.gitignore` syntax). Also read from `.osxphotos_keep` at the root of DEST |

Example: checksum every newly-exported file into a log.

```bash
osxphotos export ~/archive --screenshot --download-missing \
  --post-command exported "md5sum {filepath|shell_quote} >> /tmp/hashes.txt"
```

The template inside the COMMAND string uses the same template DSL as filename/directory — wrap paths in `{filepath|shell_quote}` to handle spaces correctly.

## Reporting

| Flag | Purpose |
|---|---|
| `--report FILE` | Write a CSV or SQLite report. Extension determines format (`.csv`, `.db`, `.sqlite`, `.json`) |
| `--append` | Append to existing report |
| `--dry-run` | Show what would be exported, don't write files |
| `--verbose` / `-V` | Verbose; repeatable |
| `--no-progress` | Hide progress bar |

## Album/folder preservation

| Flag | Purpose |
|---|---|
| `--album-keyword` | Treat albums as keywords in exported metadata |
| `--person-keyword` | Treat person names as keywords |
| `--keyword-template TEMPLATE` | Add a template-derived keyword to each photo |

## Path specifics

| Flag | Purpose |
|---|---|
| `--current-name` | Use the current (renamed) name from Photos instead of original |
| `--strip` | Strip whitespace from rendered templates |
| `--replace-keywords` | With `--keyword-template`, replace instead of append |

## Common patterns

### Year/month archive

```bash
osxphotos export ~/archive \
  --directory "{created.year}/{created.mm}" \
  --filename "{original_name}" \
  --download-missing --update
```

### Album-preserved export

```bash
osxphotos export ~/export \
  --directory "{folder_album}" \
  --filename "{original_name}" \
  --download-missing
```

### Export + sidecar JSON for metadata-heavy analysis

```bash
osxphotos export ~/triage --screenshot --download-missing \
  --sidecar json --sidecar-drop-ext
# Each photo.jpeg also gets photo.json with full metadata
```

See [workflows.md](workflows.md) for end-to-end recipes using these patterns.

## Output of `export`

Stdout:
- Per-photo lines as export proceeds (suppressable with `--no-progress`)
- Final summary: `Processed: N photo, exported: E, missing: M, error: X`

`missing: M` with M > 0 almost always means iCloud-only originals — add `--download-missing`.

`error: X` with X > 0 points at the specific photos that failed; use `--verbose` to see why.

## Notes

- `--download-missing` can hang if Photos.app is prompting for auth or offline — check Photos
- First-run `.osxphotos_export.db` creation doesn't hurt even if you never plan to use `--update`
- `{counter}` in filenames resets per run; use `{id}` for stable numbering with `--update`
- `--cleanup` is powerful — pair with `--dry-run` the first time to avoid surprise deletions
- All query flags filter what's exported — combine aggressively to scope the export small
