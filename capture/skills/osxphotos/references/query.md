# `osxphotos query`

Filter the Photos library and emit results. The widest and most-used command.

## Usage

```bash
osxphotos query [OPTIONS]
```

No query options → returns every photo. Different options AND together. Same option repeated ORs.

Example of AND + OR together:
```bash
osxphotos query --person "John Doe" --person "Jane Doe" --keyword "vacation"
# photos where (person is John OR Jane) AND (keyword is vacation)
```

## Output modes

| Flag | Effect |
|---|---|
| *(default)* | Human-readable list of photo filenames |
| `--count` | Just the integer count. No listing |
| `--json` | Every matching photo as JSON array, full metadata |
| `--field NAME TEMPLATE` | Emit custom fields per photo, CSV-like. Repeatable |
| `--print TEMPLATE` | Render a template string per photo |
| `--quiet` | Suppress results (use with `--print`, `--add-to-album`) |
| `--mute` | Suppress status/progress, keep results |
| `--newest-first` | Sort newest first (default: oldest) |
| `--ignore-case` | Case-insensitive string matching |

### `--field` and `--print` examples

```bash
# CSV-like: uuid, filename, date
osxphotos query --screenshot \
  --field uuid "{uuid}" --field name "{original_name}" --field date "{created.date}"

# Free-form template per photo
osxphotos query --favorite --print "{created.date} | {title or original_name}"
```

## Filter categories

### Identity / selection

| Flag | Notes |
|---|---|
| `--uuid UUID` | Match specific UUID. Repeatable |
| `--uuid-from-file FILE` | Load UUIDs from file. One per line, `#` comments + blank lines ignored |
| `--selected` | Only photos currently selected in Photos.app (macOS) |
| `--name FILENAME` | Match original filename (no path) |

### Date / time

| Flag | Notes |
|---|---|
| `--from-date DATE` | ISO 8601, e.g. `2023-01-12` or `2023-01-12T12:00:00` |
| `--to-date DATE` | Exclusive upper bound |
| `--year YEAR` | Repeatable for multiple years |
| `--added-in-last DELTA` | e.g. `"7 days"`, `"2 weeks"`, `"1 month"` |
| `--from-time TIME` / `--to-time TIME` | Time-of-day filter, e.g. `"06:00"` / `"18:00"` |

### Media type

All binary — pass the positive or the `--not-X` variant.

| Positive | Negative | Matches |
|---|---|---|
| `--screenshot` | `--not-screenshot` | Screenshots |
| `--screen-recording` | `--not-screen-recording` | Screen recordings |
| `--selfie` | `--not-selfie` | Front-facing-camera photos |
| `--live` | `--not-live` | Live Photos |
| `--portrait` | `--not-portrait` | Portrait-mode photos |
| `--panorama` | `--not-panorama` | Panoramas |
| `--hdr` | `--not-hdr` | HDR photos |
| `--slow-mo` | `--not-slow-mo` | Slow-mo videos |
| `--time-lapse` | `--not-time-lapse` | Time lapses |
| `--burst` | `--not-burst` | Burst photos |
| `--only-photos` | — | Exclude videos |
| `--only-movies` | — | Videos only |
| `--has-raw` | — | RAW+JPEG pairs |

### Metadata

| Flag | Notes |
|---|---|
| `--title TEXT` / `--no-title` | Photo title. Substring match |
| `--description TEXT` / `--no-description` | Description (also called caption) |
| `--keyword KEYWORD` / `--no-keyword` | Repeatable. OR across multiple `--keyword` |
| `--label LABEL` | ML classification label (Photos 5+). Repeatable |
| `--favorite` / `--not-favorite` | Favorite flag |
| `--hidden` / `--not-hidden` | Hidden flag |
| `--edited` / `--not-edited` | Has adjustments |
| `--external-edit` | Edited by external app |
| `--is-reference` / `--not-reference` | Referenced-file (not managed) |

### People / places

| Flag | Notes |
|---|---|
| `--person PERSON` | Repeatable. Detected face name. OR across multiple |
| `--no-person` | Photos with no detected faces |
| `--place PLACE` / `--no-place` | Reverse-geocoded place name. Substring match |
| `--location` / `--no-location` | Has GPS coordinates |

### Containers

| Flag | Notes |
|---|---|
| `--album ALBUM` | Repeatable. OR. Use `'Folder/Album'` for nested; escape `/` as `//` |
| `--folder FOLDER` | Repeatable. Matches any album inside the folder |
| `--in-album` / `--not-in-album` | Any album at all |

### iCloud / shared

| Flag | Notes |
|---|---|
| `--cloudasset` / `--not-cloudasset` | Is an iCloud-managed asset |
| `--incloud` / `--not-incloud` | Currently synced to iCloud |
| `--shared-library` / `--not-shared-library` | Part of iCloud Shared Library |
| `--shared-moment` / `--not-shared-moment` | Part of a shared moment |
| `--syndicated` / `--not-syndicated` | Shared via "Shared with You" |
| `--saved-to-library` / `--not-saved-to-library` | Syndicated + saved locally |
| `--has-comment` / `--no-comment` | Has comments (shared photos) |
| `--has-likes` / `--no-likes` | Has likes (shared photos) |

### Files

| Flag | Notes |
|---|---|
| `--missing` / `--not-missing` | Original not present on disk (typically iCloud-only) |
| `--min-size SIZE` / `--max-size SIZE` | e.g. `1MB`, `500KB` |
| `--duplicate` | Possible duplicates (by signature) |
| `--deleted` | Include photos in Recently Deleted |
| `--deleted-only` | Only Recently Deleted |

### Advanced

| Flag | Notes |
|---|---|
| `--regex REGEX TEMPLATE` | Match a template's rendered value against a regex. Repeatable |
| `--exif TAG VALUE` | Match EXIF tag via exiftool. Repeatable |
| `--query-eval CRITERIA` | Python expression; `photo` is the PhotoInfo |
| `--query-function FILE.PY::FUNC` | Call a Python function that returns bool |

### Side effects from query

| Flag | Notes |
|---|---|
| `--add-to-album ALBUM` | Add matching photos to an album (macOS). Creates album if missing |

## Sort

| Flag | Effect |
|---|---|
| `--newest-first` | Sort newest first (default: oldest first) |
| `--oldest-first` | Explicit oldest first |

## Examples

```bash
# Count screenshots
osxphotos query --screenshot --count

# All screenshots this year as JSON
osxphotos query --screenshot --from-date 2026-01-01 --json

# Find photos of a specific person, newest first
osxphotos query --person "Mom" --newest-first --print "{created.date}: {original_name}"

# Photos in a specific album, in a subfolder
osxphotos query --album "Travel/2025/Italy"

# Duplicates — two-column output
osxphotos query --duplicate \
  --field uuid "{uuid}" --field name "{original_name}"

# Read UUIDs from file (matches `delete --uuid-from-file` format)
osxphotos query --uuid-from-file to_review.txt --field uuid "{uuid}" --field name "{original_name}"

# Favorite photos with no keywords
osxphotos query --favorite --no-keyword --count

# Photos added in the last week
osxphotos query --added-in-last "7 days" --newest-first

# Pass result UUIDs straight into a delete file
osxphotos query --screenshot --from-date 2020-01-01 --to-date 2021-01-01 \
  --print "{uuid}" --quiet > old_screenshots.txt
```

## Global flags that also apply

- `--library PATH` / `--db PATH`
- `--json`
- `--verbose` / `-V`
- `--help` / `-h`

## Notes

- `query --json` emits the full PhotoInfo dict per matching photo — heavy but useful for scripting
- `--field` is the lightest structured output; pair with `--print "{uuid}" --quiet` for UUID-only streams
- Regex and `--query-eval` are rarely needed — prefer structured flags first
- See [templates.md](templates.md) for everything you can put inside `--field`, `--print`, `--regex`'s template argument

## Quick lookup

Flat flag catalog for when you just need "what flag does X?" without surrounding commentary.

### Identity

| Flag | Value | Notes |
|---|---|---|
| `--uuid UUID` | string | Repeatable |
| `--uuid-from-file FILE` | path | One UUID per line, `#` comments |
| `--selected` | flag | Currently selected in Photos.app |
| `--name FILENAME` | string | Match against original filename |

### Date / time

| Flag | Value | Notes |
|---|---|---|
| `--from-date DATE` | ISO 8601 | Inclusive lower bound |
| `--to-date DATE` | ISO 8601 | Exclusive upper bound |
| `--year YEAR` | int | Repeatable |
| `--added-in-last TIME_DELTA` | e.g. `"7 days"` | Library-add date |
| `--from-time TIME` | `HH:MM` | Time of day, regardless of date |
| `--to-time TIME` | `HH:MM` | Time of day |

### Media type

| Positive | Negative |
|---|---|
| `--screenshot` | `--not-screenshot` |
| `--screen-recording` | `--not-screen-recording` |
| `--selfie` | `--not-selfie` |
| `--live` | `--not-live` |
| `--portrait` | `--not-portrait` |
| `--panorama` | `--not-panorama` |
| `--hdr` | `--not-hdr` |
| `--slow-mo` | `--not-slow-mo` |
| `--time-lapse` | `--not-time-lapse` |
| `--burst` | `--not-burst` |
| `--only-photos` | — |
| `--only-movies` | — |
| `--has-raw` | — |

### Metadata

| Flag | Value | Notes |
|---|---|---|
| `--title TEXT` / `--no-title` | string | Substring match |
| `--description TEXT` / `--no-description` | string | Substring match |
| `--keyword KEYWORD` / `--no-keyword` | string | Repeatable OR |
| `--label LABEL` | string | ML label, repeatable |
| `--favorite` / `--not-favorite` | flag | — |
| `--hidden` / `--not-hidden` | flag | — |
| `--edited` / `--not-edited` | flag | Has adjustments |
| `--external-edit` | flag | Edited in external app |
| `--is-reference` / `--not-reference` | flag | Referenced-file (not managed) |

### People / places

| Flag | Value | Notes |
|---|---|---|
| `--person PERSON` / `--no-person` | string | Repeatable OR |
| `--place PLACE` / `--no-place` | string | Substring |
| `--location` / `--no-location` | flag | Has GPS |

### Containers

| Flag | Value | Notes |
|---|---|---|
| `--album ALBUM` | string | Repeatable. `Folder/Album` for nested; `//` to escape literal `/` |
| `--folder FOLDER` | string | Any album in the folder |
| `--in-album` / `--not-in-album` | flag | — |

### iCloud / shared

| Flag | Meaning |
|---|---|
| `--cloudasset` / `--not-cloudasset` | iCloud-managed |
| `--incloud` / `--not-incloud` | Currently synced |
| `--shared-library` / `--not-shared-library` | In iCloud Shared Library |
| `--shared-moment` / `--not-shared-moment` | In shared moment |
| `--syndicated` / `--not-syndicated` | Shared with You |
| `--saved-to-library` / `--not-saved-to-library` | Syndicated + saved |
| `--has-comment` / `--no-comment` | — |
| `--has-likes` / `--no-likes` | — |

### Files / storage

| Flag | Value | Notes |
|---|---|---|
| `--missing` / `--not-missing` | flag | Original on disk? |
| `--min-size SIZE` / `--max-size SIZE` | e.g. `1MB` | File size |
| `--duplicate` | flag | Possible duplicates |
| `--deleted` / `--deleted-only` | flag | Include / only Recently Deleted |

### Advanced

| Flag | Value | Notes |
|---|---|---|
| `--regex REGEX TEMPLATE` | regex + template | Repeatable |
| `--exif TAG VALUE` | string + string | Needs exiftool |
| `--query-eval CRITERIA` | Python expr | `photo` is PhotoInfo |
| `--query-function FILE.PY::FUNC` | Python callable | Returns bool |
| `--ignore-case` | flag | Case-insensitive strings |

### Output

| Flag | Meaning |
|---|---|
| `--count` | Just the count |
| `--json` | Full JSON per photo |
| `--field NAME TEMPLATE` | CSV-like custom field, repeatable |
| `--print TEMPLATE` | Render per photo |
| `--quiet` | Suppress results |
| `--mute` | Suppress progress |
| `--newest-first` / `--oldest-first` | Sort direction |

### Side effects

| Flag | Meaning |
|---|---|
| `--add-to-album ALBUM` | Add matches to album; creates if missing |

### Global

| Flag | Meaning |
|---|---|
| `--library PATH` / `--db PATH` | Specify Photos library |
| `--verbose` / `-V` | Repeatable |
| `--timestamp` | Prefix verbose output |
| `--theme THEME` | `dark`, `light`, `mono`, `plain` |
| `--help` / `-h` | Help |
