# `osxphotos show`

Open Photos.app and scroll to a specific photo, album, or folder. Useful for visual verification before destructive operations like `delete`.

## Usage

```bash
osxphotos show UUID_OR_NAME [OPTIONS]
```

The positional argument can be:
- A 36-char UUID: `osxphotos show B62DE1BA-26BC-4DDD-A225-B128F55AFCB6`
- An album name: `osxphotos show "My Album"`
- A folder path: `osxphotos show "Travel/2025"`
- A filename: `osxphotos show IMG_1234.JPG`
- A path to an exported file (looks up the UUID via the export DB): `osxphotos show /path/to/exported/photo.jpg`

Only flag:
- `--library PATH` / `--db PATH` — specify Photos library

## What it does

Uses AppleScript (via photoscript) to tell Photos.app to spotlight the given item. Photos.app must be running or launchable.

## Requirements

- macOS only
- Photos library version 5 or higher (every modern Photos version)
- Automation permission (granted on first use via a system prompt)
- Photos.app running (or launchable)

## Known behaviors

- **First call after Photos.app starts can time out** (`-1712` or a spurious "Invalid photo id"). Retry once.
- **Subfolders aren't directly addressable.** `show "Travel/2025"` only works if `2025` is an album inside a folder `Travel`. Check album names with `osxphotos albums`.
- **Exported-file lookup** uses `.osxphotos_export.db` in the file's enclosing directory. If that DB is missing or the file moved, the lookup fails.

See [gotchas.md](gotchas.md) for full troubleshooting.

## Examples

```bash
# Verify a UUID before deleting
osxphotos show $UUID

# Open an album directly
osxphotos show "Screenshots"

# Reverse-lookup a photo in an export folder
osxphotos show ~/triage/B62DE1BA-26BC-4DDD-A225-B128F55AFCB6_IMG_5451.jpeg
```

## Pre-delete verification pattern

```bash
# Show each candidate, one by one, giving the user a chance to veto
while read uuid; do
  [[ -z "$uuid" || "$uuid" == \#* ]] && continue
  osxphotos show "$uuid"
  read -p "Delete $uuid? [y/N] " yn
  [[ "$yn" == "y" ]] && osxphotos delete --uuid "$uuid" --yes
done < deletions.txt
```

For pure Claude-driven workflows, skip this — `delete` already has a dry-run and prompt. But for human eyes-on review, `show` is the fastest way to see candidates.

