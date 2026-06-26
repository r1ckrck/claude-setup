# Discovery commands

Read-only commands for browsing Photos library metadata.

## `info`

Library-wide stats: total photos, album/keyword/person counts, library version, storage info.

```bash
osxphotos info
osxphotos info --json     # structured output
```

Useful as a first look at any library. Numbers that matter:
- Total photos (photos + videos combined)
- Named persons, detected faces
- Albums, shared albums, folders
- Screenshots, selfies, panoramas (media subtypes)
- AI analysis counts (photos that have been analyzed vs not)

## `albums`

Every album with its photo count.

```bash
osxphotos albums                # YAML-like, alphabetical
osxphotos albums --json         # structured
osxphotos albums --sort-size    # by photo count, highest first
```

Shared albums are marked. Folder-nested albums show their full path.

## `keywords`

Every keyword and how many photos carry it.

```bash
osxphotos keywords
osxphotos keywords --json
```

Tip: compare this to `query --no-keyword --count` to find photos with no keywords at all.

## `labels`

ML-generated classification labels (Photos 5+). Things like "Tree", "Beach", "Dog". Not user-set — derived by Apple's on-device vision.

```bash
osxphotos labels
osxphotos labels --json
```

Query by label: `osxphotos query --label "Dog"`.

## `persons`

Detected faces with photo counts. Named persons plus an "_UNKNOWN_" bucket for unnamed faces.

```bash
osxphotos persons
osxphotos persons --sort-size    # most photographed first
osxphotos persons --json
```

Query by person: `osxphotos query --person "Name"`.

## `places`

Reverse-geocoded place names from GPS coordinates.

```bash
osxphotos places
osxphotos places --json
```

Query by place: `osxphotos query --place "San Francisco"`.

## `grep`

Raw text search across the Photos SQLite database. Hidden command (show with `OSXPHOTOS_SHOW_HIDDEN=1 osxphotos --help`).

```bash
osxphotos grep "vacation"
osxphotos grep --ignore-case "VACATION"
osxphotos grep --print-filename "trip"
```

Use when the structured commands don't find something — e.g. searching for a string that appears in the DB but not in any typed field (EXIF blobs, edit history, etc.).

## `list` (`list-libraries`)

Find all Photos libraries on the system.

```bash
osxphotos list
osxphotos list --json
```

Output marks:
- `(*)` the system library
- `(#)` the last-opened library
- Paths unmarked are other libraries present on disk

Use this if the user has multiple libraries and you need to know the path to pass via `--library`.

## Shared output properties

Every command in this file:

- Accepts `--library PATH` / `--db PATH` to target a non-default library
- Supports `--json` for structured output
- Is purely read-only (no side effects, no permissions beyond Full Disk Access)
- Works on any Photos library version ≥ 4 (most work ≥ 2)

## Quick patterns

```bash
osxphotos info                      # library scale overview
osxphotos albums --sort-size        # albums ranked by photo count
osxphotos persons --sort-size       # people ranked by photo count
osxphotos labels --json             # ML labels (pipe through your preferred JSON parser)
```

For structured processing, add `--json` and pipe to `jq`, a Python script, or the osxphotos Python API (see [scripting.md](scripting.md)).
