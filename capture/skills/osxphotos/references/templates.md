# Template DSL

The template system substitutes photo metadata into strings. Used by `--directory`, `--filename`, `--field NAME TEMPLATE`, `--print`, `--title`, `--description`, `--keyword`, `--add-to-album`, `--regex`, and any other flag whose argument name ends in `TEMPLATE`.

Syntax: `{field}`, `{field.subfield}`, `{field|filter}`, `{field?true_value,false_value}`.

## 1. Selection / identity

Fields that identify a single photo — useful for stable filenames, audit logs, lookup tables.

| Template | Result | Notes |
|---|---|---|
| `{uuid}` | 36-char UUID | Unique per photo |
| `{id}` | Database sequential ID | Integer; stable across runs |
| `{original_name}` | Original filename + extension | e.g. `IMG_5451.HEIC` |
| `{name}` | Current filename | Renamed if the user changed it |
| `{title}` | Photo title | User-set; may be empty |
| `{descr}` | Description / caption | Alias: `{description}` |

## 2. Organizing output

Fields that shape directory trees, filenames, or groupings — the "where does this photo go?" fields.

### Date / time

All date fields accept sub-keys and strftime. Analogous forms exist for `{modified.*}` (modified date) and `{date_added.*}` (added-to-library date).

| Template | Result |
|---|---|
| `{created}` | `2025-06-12` (ISO date) |
| `{created.date}` | Same as `{created}` |
| `{created.year}` | `2025` |
| `{created.yy}` | `25` |
| `{created.mm}` | `06` |
| `{created.month}` | `June` |
| `{created.dd}` | `12` |
| `{created.dow}` | `Thursday` (day of week) |
| `{created.doy}` | `163` (day of year) |
| `{created.hour}` | `14` |
| `{created.minute}` | `05` |
| `{created.second}` | `30` |
| `{created.time}` | `14:05:30` |
| `{created.strftime,%Y-W%U}` | Custom format via strftime |

### Containers

| Template | Result | Notes |
|---|---|---|
| `{album}` | Album name(s) | Multi-valued: one output per album |
| `{folder_album}` | `Folder/Album` | Full hierarchy |
| `{album_seq}` | `1`, `2`, …  | Photo's position within the album |

### Counter / stable index

| Template | Result | Notes |
|---|---|---|
| `{counter}` | `0, 1, 2, …` | Session-scoped; resets each run |
| `{counter(1)}` | `1, 2, 3, …` | Start from 1 |
| `{counter(1,100,2)}` | `1, 3, 5, …, 99` | start, stop, step |
| `{counter:05d}` | `00000, 00001, …` | Zero-padded |
| `{id:05d}` | `00001, 00002, …` | DB primary key, padded — use when you need stable numbering across runs (e.g. with `--update`) |

## 3. Content and people

Fields that describe *what's in* the photo — faces, tags, places, media type, EXIF metadata, OCR text.

### People / keywords / labels / places

| Template | Result |
|---|---|
| `{person}` | Detected face name(s). Multi-valued |
| `{keyword}` | Keyword(s). Multi-valued |
| `{label}` | ML classification label(s). Multi-valued |
| `{place.name}` | Full rendered place name |
| `{place.name.city}` | City only |
| `{place.name.country}` | Country only |
| `{place.name.state_province}` | State or province |
| `{place.address}` | Full postal address |

### Media / format

| Template | Result |
|---|---|
| `{media_type}` | `photo`, `video`, `screenshot`, `selfie`, etc. |
| `{photo_or_video}` | `photo` or `video` |
| `{uti}` | Uniform type identifier |
| `{format_original}` | Original file extension |
| `{format_edited}` | Edited file extension |

### EXIF passthrough

| Template | Result | Notes |
|---|---|---|
| `{exif.camera_make}` | `Apple` | Common fields available directly |
| `{exif.camera_model}` | `iPhone 14 Pro` | |
| `{exif.focal_length}` | `7.6mm` | |
| `{exiftool:EXIF:Make}` | `Apple` | Raw exiftool tag. Requires exiftool installed |
| `{exiftool:XMP:Rating}` | User rating (1–5) if set | |

### OCR / detected content

| Template | Result | Notes |
|---|---|---|
| `{detected_text}` | Text extracted via Apple Vision | Slow first time; cached as extended attribute |
| `{detected_text:0.7}` | Confidence-filtered (0.0–1.0) | |

## 4. Conditionals (state flags)

Syntax: `{field?true_value,false_value}`. Both values may be empty.

| Template | Result |
|---|---|
| `{favorite?y,n}` | `y` if favorite, `n` otherwise |
| `{hidden?hidden,}` | `hidden` or empty |
| `{edited?_edited,}` | `_edited` suffix if photo was edited, empty otherwise |
| `{burst?_burst,}` | Similar |

Literal commas inside conditional values require `{comma}`:

```
{favorite?{comma}yes{comma},}
→ ",yes," if favorite, empty otherwise
```

## 5. Styling — filters and literals

### Filters (pipe-separated, applied left to right)

| Filter | Effect |
|---|---|
| `|lower` | lowercase |
| `|upper` | UPPERCASE |
| `|capitalize` | First Word Only |
| `|titlecase` | Title Case Everything |
| `|strip` | Trim whitespace |
| `|braces`, `|parens`, `|brackets` | Wrap in `{}` / `()` / `[]` |
| `|shell_quote` | Quote for shell safety |
| `|split(x)` | Split by delimiter, returns list |
| `|autosplit` | Split on commas/semicolons/spaces |
| `|sort`, `|rsort`, `|reverse` | Order a list |
| `|join(x)` | Join list with x |
| `|slice(start:stop:step)` | Python slice on list |
| `|chop(n)`, `|chomp(n)` | Remove n chars from end / start |
| `|prepend(x)`, `|append(x)` | Add x to each list item |
| `|remove(x)`, `|filter(x)` | Remove items equal to x / keep items containing x |
| `|parse_date(FMT)`, `|parse_datetime(FMT)` | Parse list items as dates |
| `|function:FILE.PY:FUNC` | Custom Python function |

Chain example: `{keyword|sort|join(_)}` — sort keywords alphabetically, join with underscore.

### Literals

Use these when a literal conflicts with template syntax:

| Template | Result |
|---|---|
| `{comma}` | `,` |
| `{semicolon}` | `;` |
| `{pipe}` | `\|` |
| `{tab}` | tab character |
| `{newline}` | newline |
| `{openbrace}` | `{` |
| `{closebrace}` | `}` |
| `{percent}` | `%` |

## Common patterns

```
{created.year}/{created.mm}/{original_name}
→ 2025/06/IMG_5451.HEIC

{folder_album}/{created.date}_{original_name}
→ Travel/Italy/2025-06-12_IMG_5451.HEIC

{person|sort|join(_)}_{original_name}
→ Dad_Mom_IMG_5451.HEIC  (for a photo with people Dad and Mom)

{created.year}/{keyword|autosplit|sort|join(-)}_{id:05d}
→ 2025/beach-vacation_00042.HEIC

{favorite?⭐,}{original_name}
→ ⭐IMG_5451.HEIC (if favorite) or IMG_5451.HEIC

{exiftool:XMP:Rating}-star/{original_name}
→ 5-star/IMG_5451.HEIC (export grouped by user rating)
```

## Multi-valued field behavior

Multi-valued fields (`{album}`, `{keyword}`, `{person}`, `{label}`) produce one output per value by default. `--filename "{keyword}_{original_name}"` for a photo with 3 keywords produces 3 exported files.

Collapse into one output by piping through `|join(x)`:

```
--filename "{keyword|sort|join(-)}_{original_name}"
→ one file with all keywords in the name
```

## Counters and update mode

`{counter}` values reset to zero on each `export` invocation. If you're using `--update` and expect filenames to remain stable across runs, use `{id}` (a database primary key that never changes) instead.

## Where templates are accepted

| Command | Flag | Template rendered |
|---|---|---|
| `query` | `--field NAME TEMPLATE` | Per-photo field value |
| `query`, `export` | `--print TEMPLATE` | Per-photo log line |
| `query` | `--regex REGEX TEMPLATE` | Template matched against regex |
| `export` | `--directory TEMPLATE` | Directory tree under DEST |
| `export` | `--filename TEMPLATE` | Filename per exported photo |
| `export` | `--keyword-template TEMPLATE` | Add template-derived keyword |
| `batch-edit` | `--title`, `--description`, `--keyword`, `--add-to-album` | Template per photo |
| `import` | `--title`, `--description`, `--keyword`, `--album` | Same |

If a flag's argument name ends in `TEMPLATE`, the template system applies.
