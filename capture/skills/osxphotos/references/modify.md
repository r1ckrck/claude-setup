# Modify commands

Commands that change the Photos library. All are macOS-only and all need Photos library access (usually via Terminal.app's TCC identity — see [permissions.md](permissions.md)).

**Safety reminder:** snap before, diff after. See [audit.md](audit.md).

## `import`

Add files to the Photos library.

```bash
osxphotos import PATH [PATH ...] [OPTIONS]
```

Common flags:
- `--album ALBUM_TEMPLATE` / `-a` — add imported photos to this album. Template-supported. Repeatable
- `--title TITLE_TEMPLATE` / `-t` — set title
- `--description DESCRIPTION_TEMPLATE` / `-d` — set description (caption)
- `--keyword KEYWORD_TEMPLATE` / `-k` — add keyword. Repeatable
- `--skip-dups` — skip files already in the library (by filename + fingerprint)
- `--dup-albums` — add already-imported photos to the specified album(s) anyway
- `--split-folder` — create folder hierarchy matching filesystem
- `--relative-to PATH` — compute album templates relative to PATH
- `--walk` / `-w` — recurse into subdirectories
- `--glob PATTERN` / `-g` — only import files matching PATTERN
- `--timezone OFFSET` — adjust timezone on import (e.g. `-08:00`)
- `--resume` — resume interrupted import
- `--report FILE` — CSV/SQLite report
- `--dry-run` — preview
- `--verbose` / `-V`

### Edited photo handling

`import` preserves `.AAE` adjustment files from an `osxphotos export --export-aae`. Filename conventions:
- `IMG_1234.jpg` + `IMG_E1234.jpg` (Photos format)
- `IMG_1234.jpg` + `IMG_1234_edited.jpg` (osxphotos-exported)

See `osxphotos import --help` for RAW+JPEG pair conventions.

### Examples

```bash
# Import a folder
osxphotos import ~/Downloads/vacation

# Import into a specific album with keyword
osxphotos import ~/Screenshots \
  --album "Screenshots/{created.year}" \
  --keyword "screenshot"

# Mirror a folder tree as nested albums
osxphotos import ~/Pictures --walk --split-folder --album "{filepath.parent.name}"

# Skip duplicates, add to album
osxphotos import ~/Downloads --skip-dups --album "Downloads {created.date}"
```

## `batch-edit`

Bulk set metadata (title, description, keyword, album, favorite, location) on photos matched by query or Photos.app selection.

```bash
osxphotos batch-edit [OPTIONS]
```

Common flags:
- `--title TITLE_TEMPLATE` / `-t`
- `--description DESCRIPTION_TEMPLATE` / `-d` (also `--caption`)
- `--keyword KEYWORD_TEMPLATE` / `-k` — add. Repeatable
- `--replace-keywords` / `-K` — with `--keyword`, replace instead of append
- `--add-to-album ALBUM_TEMPLATE` / `-a` — add to album. Repeatable
- `--split-folder TEXT` / `-f` — with `--add-to-album`, auto-create folder hierarchy
- `--set-favorite` / `-F` — mark as favorite
- `--clear-favorite` / `-c` — unmark
- `--location LAT LON` / `-l` — set coordinates
- `--undo` — undo the last batch edit (in-tool history)
- `--verbose` / `-V`
- Query flags to select which photos to edit

If no query flags and no Photos.app selection, `batch-edit` acts on whatever is selected; with Photos showing an album and no selection, it acts on all photos in that album.

### Examples

```bash
# Set title template on all photos in an album
osxphotos batch-edit \
  --album "California 2023" \
  --title "California vacation {created.year}-{created.dd}-{created.mm} {counter:03d}" \
  --description "{place.name}" \
  --keyword "Family" --keyword "Travel"

# Favorite all 5-star EXIF photos
osxphotos batch-edit --exif "XMP:Rating" "5" --set-favorite

# Move a single photo into an album by UUID
osxphotos batch-edit --uuid UUID --add-to-album "Archive/2020"
```

**Test on a small set first.** Template errors can scramble many photos at once.

## `timewarp`

Shift or set date/time/timezone on photos.

```bash
osxphotos timewarp [OPTIONS]
```

Common flags:
- `--date DATE` / `-d` — set creation date. `YYYY-MM-DD`
- `--date-delta DELTA` / `-D` — shift date. `+1 day`, `-2 weeks`, etc.
- `--time TIME` / `-t` — set time. `HH:MM:SS` or `HH:MM`
- `--time-delta DELTA` / `-T` — shift time. `+1 hour`, `-30 minutes`, `+90 seconds`
- `--timezone TZ` / `-z` — set timezone. `+05:00`, `-0700`, or IANA name (`America/Los_Angeles`)
- `--timezone-delta OFFSET` — shift timezone
- `--match-time` — with `--timezone`, also shift clock time to match (so "apparent" time stays the same)
- `--date-added DATE` — set date-added (import date), doesn't touch photo's EXIF date
- `--push-exif` — after changing Photos metadata, write it back to the original file
- `--pull-exif` — pull date/time from the original file's EXIF into Photos
- `--inspect` — preview without changing
- `--plain` — disable color output
- `--force` — skip confirmation
- `--function FILE:FUNC` — custom transformation function
- Query flags to target photos

### Examples

```bash
# Shift all photos forward one day (camera clock was off)
osxphotos timewarp --date-delta "+1 day" --album "Event" --force

# Set timezone on photos from a trip
osxphotos timewarp --timezone "America/Los_Angeles" --match-time \
  --from-date 2023-06-01 --to-date 2023-06-15

# Preview changes on a selected photo set
osxphotos timewarp --date-delta "-2 hours" --selected --inspect

# Reset from EXIF (undo manual changes if originals have correct date)
osxphotos timewarp --pull-exif --uuid UUID
```

## `push-exif`

Write Photos metadata back to the original source files using exiftool. Useful for creating an "EXIF-authoritative" archive.

```bash
osxphotos push-exif FIELDS [OPTIONS]
```

`FIELDS` is a positional arg controlling which fields to push. Common patterns:
- `osxphotos push-exif all` — push everything supported
- `osxphotos push-exif keywords` — just keywords
- `osxphotos push-exif title,description,keywords` — several specific

Common flags:
- `--push-edited` — also push to the edited version if present
- `--compare` — show what would change without writing
- `--report FILE` — CSV/SQLite report
- Query flags to target photos

### Example

```bash
osxphotos push-exif all --album "Backup" --push-edited --report push.csv
```

**Caveat:** modifies the original files on disk. Use `--compare` first.

## `add-locations`

Reverse-geocode GPS coordinates into place names and write them back to photos. Useful when photos have GPS but no place metadata.

```bash
osxphotos add-locations [OPTIONS]
```

Common flags:
- Query flags to target photos (usually combine with `--location --no-place`)
- `--verbose`

### Example

```bash
# Fill in place names for GPS-tagged photos missing them
osxphotos add-locations --location --no-place
```

## `sync`

Sync metadata (title, description, keywords, albums) between two Photos libraries using an intermediate export file. Photos must have matching original filename + fingerprint in both libraries.

```bash
osxphotos sync [OPTIONS]
```

Common flags:
- `--export FILE` — export metadata from current library to FILE
- `--import FILE` — import metadata from FILE into current library
- `--set FIELDS` — fields to overwrite (comma-separated, or `all`)
- `--merge FIELDS` — fields to merge (additive — keywords, albums)
- `--unmatched-skip` — silently skip unmatched photos
- Query flags

### Example

```bash
# On library A: capture metadata
osxphotos sync --export metadata.osxphotos_sync --library /path/to/A

# On library B: apply merges
osxphotos sync --import metadata.osxphotos_sync --merge keywords,albums --library /path/to/B
```

Use case: manually importing from iPhone → Mac (no iCloud), want to preserve metadata edits.

## Safety practices for all modify commands

1. **Test on a small selection first** — use `--uuid UUID1 UUID2` or a small album before going wide
2. **Dry run / inspect** when available (`--dry-run`, `--inspect`, `--compare`)
3. **Check the report** after a batch (`--report`) to see per-photo outcomes
4. **Snapshot + diff** — see [audit.md](audit.md) for the canonical safety loop

If something goes wrong:
- `batch-edit --undo` reverts the most recent batch edit (in-tool history)
- Other commands have no undo — recovery via manual edits in Photos.app or restoring from Recently Deleted (for imports that created new assets)
