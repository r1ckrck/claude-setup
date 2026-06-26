# Scripting commands

Escape hatches when the CLI flags aren't enough. All run with the library already loaded.

## `repl`

Interactive Python shell (ptpython) with the Photos library pre-loaded.

```bash
osxphotos repl                       # default library
osxphotos repl --library /path       # specific library
osxphotos repl --album "Vacation"    # pre-filtered `photos` variable
osxphotos repl --emacs               # emacs keybindings (default: vi)
```

### Variables available in the REPL

| Name | Type | Description |
|---|---|---|
| `photosdb` | `PhotosDB` | The loaded database object |
| `photos` | `list[PhotoInfo]` | Matches the CLI query flags you passed (or all photos) |
| `all_photos` | `list[PhotoInfo]` | Everything including Recently Deleted |
| `selected` | callable / live list | Current Photos.app selection. Re-evaluate after changing selection |
| `get_photo(uuid)` | callable | Fetch by UUID |
| `show(photo)` | callable | Open in default viewer |
| `spotlight(photo)` | callable | Scroll Photos.app to it |
| `inspect(obj)` | callable | Pretty-print object attributes |
| `explore(obj)` | callable | Interactive object tree explorer |

All `osxphotos` classes are in scope: `PhotosDB`, `PhotoInfo`, `AlbumInfo`, `PersonInfo`, `PlaceInfo`, `ExifInfo`, etc.

### Typical REPL session

```python
>>> len(photos)
820
>>> favorites = [p for p in photos if p.favorite]
>>> len(favorites)
12
>>> p = photos[0]
>>> p.uuid
'B62DE1BA-26BC-4DDD-A225-B128F55AFCB6'
>>> p.keywords
['vacation', 'beach']
>>> show(p)       # open in default viewer
>>> spotlight(p)  # scroll Photos.app to it
>>> quit()
```

## `run`

Execute a Python script with the osxphotos environment loaded and args forwarded to the script.

```bash
osxphotos run SCRIPT [SCRIPT_ARGS...]
```

Inside the script, `import osxphotos` works and all the classes are available.

Example script:

```python
#!/usr/bin/env python3
"""find_big_screenshots.py — list screenshots over N megabytes"""
import sys
import osxphotos

min_mb = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0
db = osxphotos.PhotosDB()
for p in db.photos(screenshot=True):
    if p.path and p.original_filesize / 1024 / 1024 > min_mb:
        print(f"{p.uuid}  {p.original_filename}  {p.original_filesize / 1024 / 1024:.1f} MB")
```

Run it:

```bash
osxphotos run find_big_screenshots.py 10
```

The script can also be a URL — `osxphotos run https://example.com/script.py` fetches and executes it.

Note: `run` strips `sys.argv[0]` and everything up to the `run` keyword, so your script sees a clean `sys.argv`.

## `exiftool`

Passthrough to the bundled exiftool binary. Useful when working with files already exported.

```bash
osxphotos exiftool [exiftool args...]
```

Examples:

```bash
osxphotos exiftool -Make -Model ~/triage/IMG_1234.jpg
osxphotos exiftool -EXIF:DateTimeOriginal=2023:01:01 ~/triage/*.jpg
```

This is a thin wrapper — identical to having exiftool on PATH and running it directly. Included for convenience when exiftool isn't installed system-wide.

## `version`

```bash
osxphotos version    # prints "1.0.0"
osxphotos --version  # also shows Python and macOS details
```

`version` is the CLI subcommand (just the number). `--version` is the global flag (number + environment info).

## When to use which

| Task | Use |
|---|---|
| Quick exploratory analysis | `repl` |
| Reusable automation | write a script, run with `run` |
| Read metadata from exported files | `exiftool` |
| Check what's installed | `version` |
| Complex filters the CLI query flags can't express | `repl` with a list comprehension |
| Long-running batch processing | `run` with a script (easier to log, checkpoint, resume) |

## Python API outline

When writing a script or in the REPL, the main classes are:

```python
import osxphotos

db = osxphotos.PhotosDB()                  # load default library
db = osxphotos.PhotosDB(dbfile="/path")    # explicit

photos = db.photos()                        # all photos
photos = db.photos(screenshot=True)         # filter at load time
photos = db.photos(keywords=["vacation"], persons=["Mom"])

p = photos[0]
p.uuid, p.original_filename, p.date, p.path
p.keywords, p.persons, p.albums, p.favorite
p.exif_info.camera_make, p.exif_info.camera_model
p.place.name.city, p.place.name.country
p.export(dest="/tmp/out")                   # export this one photo
```

Full API docs would normally come from source — for quick exploration, use `inspect(p)` in the REPL.
