# Gotchas — known failure modes

Symptom → cause → fix.

## Export

### `Processed: N photo, exported: 0, missing: N`

**Cause:** iCloud "Optimize Mac Storage" is on; originals live in iCloud, not on disk.
**Fix:** Add `--download-missing` to the export command. Be aware it's slower and requires network.

### `--download-missing` hangs indefinitely

**Cause:** Photos.app is blocked — waiting for auth, offline, or iCloud throttled.
**Fix:** See [icloud.md](icloud.md) — "When it hangs" section — for full diagnosis and recovery steps.

### Export runs but filenames collide

**Cause:** Multi-valued template field (like `{album}`, `{keyword}`, `{person}`) produces duplicate outputs if the photo is in only one container.
**Fix:** Use `|join(_)` to collapse: `--filename "{keyword|sort|join(-)}_{original_name}"`.

### `{counter}` values vary across `--update` runs

**Cause:** Counter is session-scoped — resets to 0 each time.
**Fix:** Use `{id}` (stable DB primary key) instead: `--filename "{id:05d}_{original_name}"`.

### Nothing happens / "Command 'osxphotos' not found"

**Cause:** pipx shim not on PATH, or osxphotos uninstalled.
**Fix:** `pipx list` to confirm installation; `pipx ensurepath` to fix PATH; reopen terminal.

## Delete

### `PhotoKitAuthError: auth_status = 2`

**Cause:** Host app doesn't have Photos TCC. VS Code and Claude Code fall into this.
**Fix:** `delete` auto-delegates to Terminal.app — watch for "X wants to control Terminal" prompt, click Allow, then the macOS delete dialog. For other write commands (`batch-edit`, `import`, etc.), run from Terminal.app directly.

### Delete doesn't trigger the delegation

**Cause:** `osascript` or Terminal.app unavailable for some reason.
**Fix:** Run `osxphotos delete` from Terminal.app directly. Or check `tccutil reset AppleEvents <host-bundle-id>` to re-prompt for Automation permission.

### "Delete N photos?" dialog cancelled

**Cause:** User clicked Don't Allow.
**Fix:** Nothing was deleted. Re-run to get the dialog again.

### UUIDs listed as `not_found`

**Cause:** UUID doesn't exist in the library (already deleted, wrong library, typo).
**Fix:** Verify with `osxphotos query --uuid <UUID>` — if empty, the UUID is gone or wrong.

### Deleted photo affects a family member / partner

**Cause:** Photo was in the iCloud Shared Library; deletion propagates to all participants.
**Fix:** Restore from Recently Deleted in Photos.app. In future: pre-check with `--field shared "{shared_library?YES,no}"` before deleting.

## Show

### `Invalid photo id: <UUID>` on first call after Photos launches

**Cause:** AppleScript cold-start; Photos.app hasn't finished initializing.
**Fix:** Run `osxphotos show <UUID>` again. Second call usually works.

### Error persists after retry

**Cause:** Genuine problem — Automation permission missing, Photos library version < 5, or UUID is actually wrong.
**Fix:**
1. Verify UUID with `osxphotos query --uuid <UUID>` — confirms it exists
2. Check Automation permission: System Settings → Privacy & Security → Automation → your terminal → Photos must be toggled on
3. Ensure library is on a modern Photos version (`osxphotos info` shows it)

## Query

### Query returns 0 photos when you expected some

**Cause:** Combined filters are narrowing too aggressively (different flags AND).
**Fix:** Remove flags one by one to isolate which is excluding matches. Use `--count` for fast iteration.

### String filter misses expected matches

**Cause:** Case-sensitive by default; extra whitespace; unicode mismatch.
**Fix:** Add `--ignore-case`. For fuzzy needs use `--regex "pattern" "{title}"` or `--query-eval "'word' in (photo.title or '').lower()"`.

### `--album "Folder/Name"` doesn't match

**Cause:** Literal `/` in album name conflicts with folder separator.
**Fix:** Escape with double slash: `--album "Folder//Name"` for an album literally named "Folder/Name".

## Batch modifications

### `batch-edit` affects photos you didn't expect

**Cause:** With no query flags and no Photos.app selection, batch-edit targets the current album view.
**Fix:** Always pass explicit query flags or `--uuid` when running non-interactively. Use `--dry-run` / `--inspect` equivalents first.

### `timewarp` looks wrong after running

**Cause:** Timezone vs clock-time confusion. `--timezone` alone changes the timezone label; `--timezone X --match-time` also shifts the clock.
**Fix:** `osxphotos timewarp --pull-exif --uuid <UUID>` to reset a photo from its EXIF data. Or re-run timewarp with reversed delta.

### `push-exif` doesn't find exiftool

**Cause:** `exiftool` binary not on PATH.
**Fix:** `brew install exiftool`. Or use `osxphotos exiftool` (bundled passthrough) to confirm availability.

## Audit

### `osxphotos diff` says "sqldiff not found"

**Cause:** `sqldiff` (SQLite's comparison tool) isn't installed.
**Fix:** `brew install sqldiff`.

### `diff` shows unexpected changes after delete

**Cause:** Might be iCloud sync updating unrelated metadata (analysis state, cache timestamps) in the background.
**Fix:** Normal — filter the diff to the `ZASSET` and `ZDETECTEDFACE` tables if you only care about delete-caused changes.

## Permissions

### "Terminal wants to control Terminal" prompt loops

**Cause:** Rare — happens when the delegation re-spawns within an already-delegated Terminal session.
**Fix:** Quit all Terminal windows, retry from fresh.

### App doesn't appear in System Settings → Photos

**Cause:** App hasn't requested Photos access, or its bundle doesn't declare `NSPhotoLibraryUsageDescription`.
**Fix:** Run a command that triggers a request; if still absent, the app simply can't request it. Use the `delete` delegation, or run from Terminal.app directly.

### Permissions reset after OS update

**Cause:** macOS major updates occasionally reset TCC state.
**Fix:** Re-grant Full Disk Access and Photos for your terminal(s). Re-run `osxphotos info` and `osxphotos show <UUID>` to re-trigger prompts.

## Shared Library

### Shared Library read returns empty or partial

**Cause:** macOS 26 has known regressions reading shared-album metadata in some configurations.
**Fix:** Query by direct album name if you know it; avoid relying on shared-album listings; export from the owner's library when possible.

### Deleting a shared photo didn't prompt differently

**Cause:** The CLI doesn't currently flag shared-library photos in the delete flow — the single OS dialog is the only indicator, and it doesn't distinguish.
**Fix:** Before delete, run: `osxphotos query --uuid-from-file X.txt --field uuid "{uuid}" --field shared "{shared_library?YES,no}"`. Rows showing `YES` will affect all Shared Library participants.

## General

### `FileNotFoundError: ... phototemplate.tx`

**Cause:** A required runtime grammar file is missing from the install.
**Fix:** `pipx reinstall osxphotos`. If it recurs, the install tree may be corrupted.

### `ValueError: Invalid photo id` from a non-show command

**Cause:** Usually a photoscript / AppleScript issue — same family as the show cold-start.
**Fix:** Retry. If persistent, verify the UUID exists, and check Automation permission.

### Photos command output contains ANSI control codes in logs

**Cause:** Default theme assumes a terminal.
**Fix:** Pass `--theme plain` to kill colors, or pipe through `sed 's/\x1b\[[0-9;]*m//g'` to strip.

### Very slow `query` or `export` startup

**Cause:** osxphotos copies the Photos SQLite DB to a temp dir on each invocation — cold disk caches make this slow.
**Fix:** Normal first time; subsequent calls are faster. For many sequential queries in a script, use `osxphotos repl` or `osxphotos run` so the DB loads once.

### Commands from a cron job or launchd fail silently

**Cause:** Headless environments (cron, launchd) don't have the TCC identity of the user's interactive session.
**Fix:** Add the launchd label or cron wrapper app to Full Disk Access (and Photos for write ops). Some macOS versions don't allow TCC from cron at all — use a launchd user agent instead.
