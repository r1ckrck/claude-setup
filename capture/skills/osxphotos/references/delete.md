# `osxphotos delete`

Remove photos from the Photos library by UUID. Photos move to **Recently Deleted** (30-day grace window); iCloud propagates the deletion (and the recovery) across all connected devices.

## Usage

```bash
osxphotos delete [OPTIONS]
```

All options:

| Flag | Purpose |
|---|---|
| `--uuid UUID` | UUID of a photo to delete. Repeatable |
| `--uuid-from-file FILE` | Read UUIDs from a file. One per line; `#` comments and blank lines ignored |
| `--yes` / `-y` | Skip the tool's own confirmation prompt. The macOS system dialog still fires |
| `--dry-run` | Show what would be deleted without deleting |
| `--help` / `-h` | Help |

Explicit UUIDs only. Query-style filters (`--screenshot`, `--from-date`, etc.) are **not** supported on `delete` — by design, to prevent accidental broad deletions. Use `query` to produce a UUID list first, then `delete`.

## Examples

```bash
# Single photo, interactive
osxphotos delete --uuid B62DE1BA-26BC-4DDD-A225-B128F55AFCB6

# Several photos, skip the tool prompt (OS dialog still appears)
osxphotos delete --uuid UUID1 --uuid UUID2 --uuid UUID3 --yes

# From a file (preferred for batches of any size)
osxphotos delete --uuid-from-file deletions.txt --yes

# Preview only
osxphotos delete --uuid-from-file deletions.txt --dry-run
```

## UUID file format

```
# Duplicates flagged on 2026-04-22
778CB2E1-6778-4BE7-82D9-86B99AA9BAAC
A3F4E2D1-1234-5678-90AB-CDEF01234567

# Old screenshots
B62DE1BA-26BC-4DDD-A225-B128F55AFCB6
```

Rules:
- One UUID per line
- Blank lines ignored
- Lines starting with `#` are comments
- UUIDs are 36-char hyphenated (as emitted by `osxphotos query --print "{uuid}"`)
- Duplicate UUIDs de-duped automatically

## What happens when you run it

The CLI de-dupes UUIDs, prompts the user unless `--yes`, calls PhotoKit's `PHAssetChangeRequest.deleteAssets_` in a single batch, waits for the macOS system confirmation dialog, and on confirmation prints deleted UUIDs to stdout. Cancel or auth failure raises and exits non-zero; no photos are affected.

## The macOS system dialog

Apple enforces this dialog for any third-party app writing to the Photos library. It **cannot be suppressed** via any flag. What you can control is how often it fires:

- **Once per `delete` call**, regardless of how many UUIDs are in the call
- A 500-UUID batch file = one dialog, one click
- 500 separate `delete --uuid X` commands = 500 dialogs

**Always batch** by passing many UUIDs in one invocation (either repeated `--uuid` or a file).

## TCC delegation — critical for VS Code / Claude Code

PhotoKit write operations require the **Photos library access** TCC permission, distinct from Full Disk Access. macOS only grants this to apps that declare `NSPhotoLibraryUsageDescription` in their `Info.plist`:

- **Terminal.app** declares it → can request + receive Photos access
- **iTerm** generally does → usually works
- **VS Code** does not → silently denied
- **Claude Code** (the desktop app or CLI) does not → silently denied

When `delete` detects a denied PhotoKit auth from a host that can't request it, it **auto-delegates**: the CLI spawns `osascript -e 'tell application "Terminal" to do script "osxphotos delete --uuid ... --yes; exit"'`. Terminal.app runs the command with its own TCC identity, prompts the user via the macOS dialog, and deletes on approval.

What the user sees the first time a delegate fires:
1. **"VS Code wants to control Terminal"** prompt → click Allow (Automation permission; persistent)
2. **"Delete N photos?"** system dialog → click Delete
3. Photos move to Recently Deleted

Subsequent calls: the Automation prompt is gone. Only the Photos delete dialog appears.

The Terminal window may not come to the foreground — the command still runs; no action required from the user after the dialogs.

## Safety layers (all active)

1. **Dry-run** — pass `--dry-run` to see target list without deleting
2. **Tool prompt** — default interactive `y/N` confirmation (skip with `--yes`)
3. **macOS system dialog** — Apple-enforced; always fires on real delete
4. **Recently Deleted album** — all deletions go here first, recoverable for 30 days
5. **iCloud sync** — deletion + recovery both propagate; nothing is immediately permanent

## Recovery

Deletions are reversible within 30 days:

1. Open Photos.app
2. Sidebar → **Recently Deleted**
3. Select the photos to restore
4. Click **Recover**

They reappear in their original album context. iCloud syncs the recovery across devices.

## Permanent deletion

This CLI does **not** permanently delete photos (no "empty trash" command). To permanently delete:

1. Photos.app → Recently Deleted → select → **Delete** (confirm dialog)
2. Or wait 30 days for automatic purge

## Output

On success:
```
Requested deletion of 3 photo(s):
  778CB2E1-6778-4BE7-82D9-86B99AA9BAAC
  A3F4E2D1-1234-5678-90AB-CDEF01234567
  B62DE1BA-26BC-4DDD-A225-B128F55AFCB6
Deleted 3 photo(s) (moved to Recently Deleted).
778CB2E1-6778-4BE7-82D9-86B99AA9BAAC
A3F4E2D1-1234-5678-90AB-CDEF01234567
B62DE1BA-26BC-4DDD-A225-B128F55AFCB6
```

The final block of plain UUIDs is pipeable — `osxphotos delete --uuid-from-file x.txt --yes | tee deleted_$(date +%F).log` preserves an audit trail.

Exit codes:
- `0` — all requested UUIDs deleted
- `1` — error (user cancelled, auth failure, etc.)
- `2` — some UUIDs not found in the library (partial success)

## Recommended Claude workflow

1. Use `query` with relevant filters to identify candidate photos
2. Export them with a `{uuid}_`-prefixed filename so Claude can map files back to UUIDs
3. Claude reviews the exports and writes `deletions.txt` with approved UUIDs
4. Run `osxphotos delete --uuid-from-file deletions.txt --dry-run` first to confirm
5. Run without `--dry-run` (add `--yes` for batch) to execute
6. Optionally `osxphotos snap` before, `osxphotos diff` after for an audit diff

See [workflows.md](workflows.md) for fuller recipes.

## Gotchas specific to delete

- **Auth not auto-delegated for other commands.** Only `delete` has the Terminal fallback. If `import` or other write paths fail with `PhotoKitAuthError`, run them from Terminal.app directly.
- **Shared Library photos affect all participants.** Deleting a UUID in an iCloud Shared Library removes it from everyone's view. There's no in-tool warning for this — before batch-deleting, run `osxphotos query --uuid-from-file deletions.txt --field uuid "{uuid}" --field shared "{shared_library?YES,no}"` to check.
- **UUID not found in library.** If a UUID in your file has already been deleted (or doesn't exist), the CLI skips it and reports it in `not_found`. Exit code 2.
- **Terminal window closes immediately after delegated delete.** Intentional — the spawned command appends `exit` to return your Terminal to a prompt.
- **First delegated run asks for Automation permission.** If the user denies, the whole flow breaks. Re-run to re-prompt (macOS remembers the "denied" state, so may need `tccutil reset AppleEvents com.microsoft.VSCode` or similar).

## Under the hood (for debugging)

- Apple bridge: `osxphotos/photokit.py :: PhotoLibrary.delete_assets(uuid_list)` → `PHAssetChangeRequest.deleteAssets_(...)` inside `performChangesAndWait_error_`
- Operation: `osxphotos/photodeleter.py :: delete_uuids(uuid_list, dry_run=False)` returns `DeleteResult(requested, deleted, not_found, error)`
- CLI: `osxphotos/cli/delete.py` — handles prompts, de-dupe, delegation

Only useful if a delete is misbehaving and you need to follow the call chain.
