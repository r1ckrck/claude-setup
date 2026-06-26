# Audit commands

Tools for capturing, comparing, and inspecting library state. Best paired with any destructive operation (delete, batch-edit, timewarp, import) to verify only the intended changes happened.

## `snap`

Save a timestamped snapshot of the Photos SQLite database.

```bash
osxphotos snap
# → writes to /private/tmp/osxphotos_snapshots/<timestamp>-Photos.sqlite
```

Environment:
- `OSXPHOTOS_SNAPSHOT` — override snapshot directory

The snap is a copy of the SQLite DB files only (`Photos.sqlite`, `Photos.sqlite-shm`, `Photos.sqlite-wal`). Photos themselves are not copied. Snaps are cheap — a few MB to hundreds of MB depending on library size.

## `diff`

Compare current Photos DB to a snapshot, or two DBs explicitly.

```bash
osxphotos diff                          # current vs most recent snap
osxphotos diff /path/to/snap1.sqlite    # current vs a specific snap
osxphotos diff snap1.sqlite snap2.sqlite  # two snaps explicitly
```

Flags:
- `--raw-output` / `-r` — disable syntax highlighting
- `--style STYLE` / `-s STYLE` — pygments theme (default `monokai`)

**Requires `sqldiff`** — install with `brew install sqldiff` if missing.

Output: SQL-like diff showing exactly which rows were added/modified/deleted in which tables. Best for forensic review of a delete or batch-edit.

### Typical audit loop

```bash
osxphotos snap                                            # baseline
osxphotos delete --uuid-from-file approved.txt --yes     # destructive op
osxphotos diff                                            # what changed
```

## `compare`

Compare two complete Photos libraries (not just DBs).

```bash
osxphotos compare /path/to/libraryA.photoslibrary /path/to/libraryB.photoslibrary
```

Flags:
- `--csv`, `--tsv`, `--json` — output format
- `--output FILE` / `-o` — write to file instead of stdout
- `--check` / `-k` — exit 0 if identical, 1 if different (good for scripts)
- `--signature TEMPLATE` / `-s` — custom photo signature template (default uses filename + fingerprint)

Use cases: sync verification, backup validation, migration audit.

## `orphans`

Find photos referenced in the library DB but missing on disk.

```bash
osxphotos orphans                     # list orphans
osxphotos orphans --export ~/orphans  # copy the orphan files (if they exist elsewhere) out
osxphotos orphans --verbose
```

Useful for:
- Diagnosing iCloud download failures (orphans with no local original)
- Cleaning up after library corruption or bad imports

## `uuid`

Print UUIDs of photos currently selected in Photos.app.

```bash
osxphotos uuid                  # one UUID per line
osxphotos uuid --filename       # UUID + filename as "comment" lines
```

Flags:
- `--filename` / `-f` — add `# <filename>` comment lines for human-readable context

Typical use: manually select photos in Photos.app → capture UUIDs → pipe into `delete`, `export`, or `batch-edit`.

```bash
osxphotos uuid > to_delete.txt
osxphotos delete --uuid-from-file to_delete.txt --yes
```

## `inspect`

Interactive live inspector. Open Photos.app, run `inspect`, and as you click photos in Photos, their full metadata prints to the terminal.

```bash
osxphotos inspect
osxphotos inspect --detect-text     # also run OCR (slow; cached after first run)
osxphotos inspect --template "{created} | {place.name} | {keyword}"
```

Flags:
- `--detect-text` / `-t` — run Vision text detection per inspected photo
- `--template TEMPLATE` / `-T` — render a template instead of the full metadata dump. Repeatable
- `--theme dark|light|mono|plain` — output theme

Exit with `Ctrl+C`. Works best in a terminal with good image support (iTerm2, Kitty).

## Full audit workflow

```bash
# 1. Baseline
osxphotos snap

# 2. Destructive op
osxphotos delete --uuid-from-file cleanup.txt --yes

# 3. Diff for an exact change log
osxphotos diff > cleanup-$(date +%F).diff

# 4. If something unexpected shows up, restore from Recently Deleted in Photos.app
```

For large batches, consider:
- `compare` with `--check` in a CI-like pre-flight
- `orphans` after a failed `--download-missing` to find what didn't pull
- `inspect` during manual review before approving a big delete list
