# iCloud behaviors

Most users have iCloud Photos enabled and many have **Optimize Mac Storage** on. Both affect what photos are physically on disk and what the CLI sees as "missing."

## Key concepts

- **iCloud-managed asset** (`cloudasset` = true): the photo is part of the iCloud library. Doesn't mean it's downloaded locally.
- **In the cloud** (`incloud` = true): currently synced to iCloud. A photo can be both `cloudasset` and `incloud`.
- **Missing** (`missing` = true): the original file isn't on this Mac's disk. Usually because of Optimize Storage.
- **Referenced** vs **managed**: managed photos live inside the library; referenced photos live elsewhere and the library just points at them. Referenced photos can show as `missing` if the source file moved.

## Optimize Mac Storage

When enabled (Photos app → Settings → iCloud → Optimize Mac Storage), macOS keeps thumbnails locally and originals in iCloud. Typical result:
- `osxphotos query --screenshot --count` → 819
- `osxphotos query --screenshot --not-missing --count` → 3

That's not a bug; that's Optimize Storage in action. Most originals are in the cloud.

## Query flags for cloud state

| Flag | Meaning |
|---|---|
| `--cloudasset` | iCloud-managed asset |
| `--not-cloudasset` | Local-only (not in iCloud) |
| `--incloud` | Currently synced up |
| `--not-incloud` | Not yet synced (pending upload) |
| `--missing` | Original not on disk |
| `--not-missing` | Original present on disk |

Combinations:
- `--cloudasset --missing` — iCloud-only with no local copy (typical Optimize-Storage state)
- `--not-cloudasset` — local-only, never uploaded
- `--cloudasset --not-incloud` — upload in progress or failed

## Export and `--download-missing`

Export reads from disk. If the original isn't there, it's reported as "missing" and skipped. Without `--download-missing`, a screenshot-heavy library with Optimize Storage on might report:

```
Processed: 819 photo, exported: 3, missing: 816, error: 0
```

Adding `--download-missing` tells Photos.app (via AppleScript) to pull the original from iCloud on demand before each copy:

```bash
osxphotos export ~/triage --screenshot --download-missing
```

Behavior:
- Slower — each missing file requires a cloud round-trip
- Can **hang** if Photos.app is prompting for authentication, offline, or iCloud is throttling
- Uses network bandwidth proportional to library size

### When it hangs

If export stalls, check:
1. **Photos.app state** — is it open and responsive? An auth prompt or dialog there will block AppleScript
2. **Network** — iCloud sync requires internet
3. **iCloud availability** — `icloud.com` or System Settings → Apple ID → iCloud for status
4. **Kill and resume** — Ctrl+C; `export --update --download-missing` will resume from the export DB (skips already-done files)

## iCloud Shared Library

Distinct from **Shared Albums** (see below). Shared Library is an asset-level share — every participant has equal rights to add, edit, delete photos.

Query flags:
- `--shared-library` — photos that are part of the Shared Library
- `--not-shared-library` — personal-library only

**Deletion of a Shared Library photo affects all participants.** This CLI does not currently flag shared-library photos in delete output — always pre-check:

```bash
osxphotos query --uuid-from-file deletions.txt \
  --field uuid "{uuid}" \
  --field name "{original_name}" \
  --field shared "{shared_library?YES_SHARED,personal}"
```

Any row with `YES_SHARED` means deleting will propagate to all Shared Library participants.

## Shared Albums

The older per-album sharing feature. Read-only for non-owners, separate from the Shared Library.

- Query: `--album "Shared Album Name"` (the album name appears in `osxphotos albums` output marked as shared)
- On macOS 26: reading shared-album metadata is known broken. Queries may return empty or incomplete results for photos in shared albums. Work around by querying the owner's library directly, or by exporting before metadata read-back.

## Shared moments and syndication ("Shared with You")

Photos others have shared with you via Messages etc.

| Flag | Meaning |
|---|---|
| `--syndicated` | Photo came via Shared with You |
| `--not-syndicated` | — |
| `--saved-to-library` | Syndicated AND saved to your library |
| `--not-saved-to-library` | Syndicated but not saved |
| `--shared-moment` | Part of a shared moment |
| `--not-shared-moment` | — |
| `--has-comment` / `--no-comment` | Comments on shared content |
| `--has-likes` / `--no-likes` | Likes on shared content |

## Deletion and iCloud sync

- Deletions propagate within seconds to all iCloud-connected devices
- Deleted photos go to Recently Deleted — also synced — recoverable from any device
- Restoring a photo from Recently Deleted on one device restores it everywhere
- Permanent deletion (emptying Recently Deleted or waiting 30 days) is also synced

The `osxphotos delete` command doesn't bypass any of this. It uses PhotoKit's standard delete path, which is the same API Photos.app uses internally.

## Practical patterns

```bash
# See the mix of cloud vs local
osxphotos info

# All iCloud-only screenshots (largest cleanup target in most libraries)
osxphotos query --screenshot --cloudasset --missing --count

# Pre-export check: how many will actually download?
osxphotos query --screenshot --missing --count

# Safer export: only what's already local
osxphotos export ~/triage --screenshot --not-missing

# Download-missing with rate-limit awareness
osxphotos export ~/triage --screenshot --download-missing --retry 3 --verbose

# Find photos stuck in "not yet synced" state
osxphotos query --cloudasset --not-incloud
```

## When iCloud is paused / offline

- Reads (`query`, `info`, `albums`, etc.) still work — they hit the local SQLite DB which has the full library catalog
- Exports of `--not-missing` photos work fine
- Exports of `--missing` photos fail; `--download-missing` will error or hang
- Delete operations queue the delete intent — it syncs when iCloud reconnects
