# Workflows

End-to-end recipes for common Claude-driven tasks. Each is a minimal, copy-pasteable sequence.

## 1. Triage screenshots (the canonical Claude loop)

Export screenshots → Claude reviews them → write a deletions file → delete approved ones → audit.

```bash
# 1. Export candidates with UUID-prefixed filenames so Claude can map back
osxphotos export ~/triage --screenshot --download-missing \
  --filename "{uuid}_{original_name}"

# 2. (Claude reads files in ~/triage, decides which to delete,
#     writes UUIDs to ~/triage/deletions.txt — one per line, # comments OK)

# 3. Sanity-check before destructive action
osxphotos delete --uuid-from-file ~/triage/deletions.txt --dry-run

# 4. Audit baseline
osxphotos snap

# 5. Execute
osxphotos delete --uuid-from-file ~/triage/deletions.txt --yes
# → macOS dialog: "Delete N photos?" → user clicks Delete
# → photos go to Recently Deleted

# 6. Diff to confirm only the intended UUIDs were removed
osxphotos diff > triage-$(date +%F).diff

# 7. Clean up exported files
rm -rf ~/triage
```

Filename prefix `{uuid}_{original_name}` ensures Claude can parse the UUID from any review note back into the deletions file.

## 2. Find duplicates

```bash
# List possible duplicates by fingerprint
osxphotos query --duplicate \
  --field uuid "{uuid}" \
  --field name "{original_name}" \
  --field size "{exif.file_size or unknown}" \
  --field created "{created}"

# Dump duplicates' UUIDs for review
osxphotos query --duplicate --print "{uuid}" --quiet > duplicates.txt

# After Claude (or you) pick which to delete:
osxphotos delete --uuid-from-file duplicates-approved.txt --yes
```

`--duplicate` uses photo signature (visual fingerprint + size). It won't catch semantic duplicates (same photo edited differently); for those, export + Claude vision review.

## 3. Archive by year/month

```bash
osxphotos export ~/Pictures/archive \
  --directory "{created.year}/{created.mm}" \
  --filename "{original_name}" \
  --download-missing \
  --update

# Incremental run tomorrow — only new/changed photos copy
osxphotos export ~/Pictures/archive \
  --directory "{created.year}/{created.mm}" \
  --filename "{original_name}" \
  --download-missing \
  --update
```

`--update` uses `.osxphotos_export.db` in the destination to track state.

## 4. Export a single album

```bash
osxphotos export ~/export --album "Italy 2025" --download-missing
```

For nested albums: `--album "Travel/2025/Italy"`. Escape literal `/` in names as `//`.

## 5. Bulk keyword tagging

```bash
# Add "travel" to every photo in specific albums
osxphotos batch-edit \
  --album "Italy 2025" --album "France 2025" \
  --keyword "travel"

# Replace keywords instead of adding
osxphotos batch-edit \
  --album "WIP Album" \
  --keyword "work-in-progress" \
  --replace-keywords
```

## 6. Fix dates on a batch

```bash
# Camera clock was 1 day behind for a trip
osxphotos timewarp --date-delta "+1 day" \
  --album "Trip" \
  --inspect      # preview first

# Apply after confirming
osxphotos timewarp --date-delta "+1 day" --album "Trip" --force
```

```bash
# Set timezone for photos from a different region
osxphotos timewarp \
  --timezone "America/Los_Angeles" --match-time \
  --from-date 2023-06-01 --to-date 2023-06-15
```

## 7. Metadata archive (sidecar JSON per photo)

```bash
# For cross-tool analysis (e.g. share with tools that don't read Photos DB)
osxphotos export ~/backup \
  --download-missing \
  --sidecar json --sidecar-drop-ext \
  --update
```

Each `photo.jpeg` gets a sibling `photo.json` with full PhotoInfo metadata.

## 8. Import a folder of new files

```bash
osxphotos import ~/Downloads/new-photos \
  --album "Imports/{created.date}" \
  --keyword "imported" \
  --skip-dups \
  --walk
```

`--walk` recurses subdirectories. `--skip-dups` avoids re-importing photos already in the library (by filename + fingerprint).

## 9. Scripted ad-hoc analysis

```python
# find_large_screenshots.py
import osxphotos
db = osxphotos.PhotosDB()
for p in db.photos(screenshot=True):
    if p.original_filesize and p.original_filesize > 10 * 1024 * 1024:
        print(f"{p.uuid}\t{p.original_filesize // (1024*1024)}MB\t{p.original_filename}")
```

```bash
osxphotos run find_large_screenshots.py > large_screenshots.tsv
```

## 10. Pre-flight safety for a big destructive op

```bash
osxphotos snap
osxphotos batch-edit --album "Old Vacations" --keyword "archive-2020" --favorite
osxphotos diff
```

See [audit.md](audit.md) for what diff output means and how to recover from unintended changes.

## 11. Capture UUIDs from Photos.app selection

```bash
# User has photos selected in Photos.app
osxphotos uuid > selected.txt
osxphotos delete --uuid-from-file selected.txt --yes
```

Or pipe directly:

```bash
osxphotos uuid | xargs -I {} osxphotos delete --uuid {} --yes
# (but this makes N separate delete calls = N OS dialogs; prefer a file)
```

## 12. Find photos missing expected metadata

```bash
# Screenshots without a keyword or title
osxphotos query --screenshot --no-keyword --no-title \
  --field uuid "{uuid}" --field name "{original_name}"

# GPS-tagged photos without a place name (fix with add-locations)
osxphotos query --location --no-place --count
osxphotos add-locations --location --no-place
```

## 13. Audit iCloud sync state

```bash
# Photos that are cloud-managed but not yet synced
osxphotos query --cloudasset --not-incloud --count

# Photos with local originals (not iCloud-only)
osxphotos query --not-missing --count

# By media type, how many are iCloud-only
osxphotos query --screenshot --missing --count
osxphotos query --portrait --missing --count
```

## 14. Multi-library comparison

```bash
# Do two libraries have the same photos?
osxphotos compare /path/to/A /path/to/B --json --check
echo $?   # 0 = same, 1 = different

# Full diff report
osxphotos compare /path/to/A /path/to/B --csv -o comparison.csv
```

## 15. Roll back an export

```bash
# Cleanup mode: delete files in export tree that weren't part of the current export
osxphotos export ~/archive --album "2025" --update --cleanup --dry-run
# Inspect, then remove --dry-run to execute
```

`--keep PATTERN` with `--cleanup` preserves non-export files (`.DS_Store`, `.osxphotos_keep`, etc.)

## Tips

- Batch behavior and safety layers: see [delete.md](delete.md)
- Filename / path templates for export: see [templates.md](templates.md)
- Snapshot + diff for pre-flight safety: see [audit.md](audit.md)
