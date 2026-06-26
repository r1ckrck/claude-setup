# Permissions (macOS TCC)

osxphotos touches three separate macOS privacy permissions. They're independent — granting one does not grant another. macOS only prompts for a permission the first time an eligible app requests it, so if a user ever dismissed a prompt, the app gets silently denied thereafter until the user grants it manually in System Settings.

## Quick mental map

| Permission | For what | When needed |
|---|---|---|
| **Full Disk Access** | Reading `Photos.sqlite` | Every osxphotos command that reads the library (almost all) |
| **Photos** (PHAccessLevelReadWrite) | PhotoKit operations | Writes: `delete`, and any future write path via PhotoKit |
| **Automation** (Apple Events) | Driving other apps via AppleScript | `show`, the delete TCC delegation, `uuid` via photoscript |

## Full Disk Access

**Panel:** System Settings → Privacy & Security → Full Disk Access.

Needed by whatever app is running `osxphotos` — Terminal.app, iTerm, Warp, VS Code, Claude Code. The app itself (not its shells) shows up in this list.

Without FDA:
```
OSError: Error copying /Users/.../Photos Library.photoslibrary/database/Photos.sqlite to /var/folders/...
```

Grant:
1. System Settings → Privacy & Security → Full Disk Access
2. Toggle the terminal/app on
3. **Quit and relaunch the terminal** — permission applies to fresh processes only

## Photos library access

**Panel:** System Settings → Privacy & Security → Photos.

Only populated with apps that declare `NSPhotoLibraryUsageDescription` in their Info.plist. This means:
- **Terminal.app** can request and receive Photos access ✓
- **iTerm2** typically can ✓
- **VS Code** does **not** declare it → silently denied ✗
- **Claude Code** does **not** declare it → silently denied ✗
- **Warp, Alacritty, Kitty** — varies; check Privacy panel

Without Photos access:
```
PhotoKitAuthError: Could not get authorizaton to use Photos: auth_status = 2
```

Status codes: `0` = not determined, `1` = restricted, `2` = denied, `3` = authorized, `4` = limited.

### How to grant it

If the app is listed in System Settings → Privacy & Security → Photos (even toggled off), just toggle on. Quit and relaunch.

If the app is **not listed at all**, it means the app hasn't (yet) or can't request access. The `+` button rarely works for CLI parent apps. Two recovery paths:

1. **Trigger a fresh request from an app that can declare it**: `tccutil reset Photos <BUNDLE_ID>` (e.g. `com.microsoft.VSCode`), then re-run the osxphotos write command. If the bundle declares `NSPhotoLibraryUsageDescription`, a system prompt appears.

2. **Run the command from Terminal.app instead**: Terminal reliably prompts. This is the basis of the `delete` auto-delegation — see below.

## Automation (Apple Events)

**Panel:** System Settings → Privacy & Security → Automation.

Lists apps and, underneath each, the other apps they may control. osxphotos commands that talk to Photos.app via AppleScript (`show`, `uuid`, `import`'s edited-file handling) need the parent app → Photos.app Automation edge granted. The `delete` TCC delegation needs parent app → Terminal.app granted.

Granted on first attempt via a macOS prompt ("X wants to control Y"). Persistent after allow.

## The delete auto-delegation mechanism

This is the most important thing to understand.

### Problem

VS Code and Claude Code can't receive Photos TCC. Running `osxphotos delete` from their terminal fails with `PhotoKitAuthError`.

### Solution in `cli/delete.py`

When `PhotoKitAuthError` is caught, the CLI spawns Terminal.app via:

```bash
osascript -e 'tell application "Terminal" to do script "osxphotos delete --uuid ... --yes; echo Done; exit"'
```

Terminal has Photos TCC (or will prompt for it on first write attempt). The `delete` runs there, shows the macOS "Delete N photos?" dialog, moves the photos to Recently Deleted.

### What the user sees

**First time ever** (from any non-Terminal host):
1. macOS prompt: "Visual Studio Code wants to control Terminal" (or "Claude Code wants to…") → click Allow. Grants Automation permission, persistent.
2. macOS Photos delete dialog: "Delete N photos?" → click Delete.

**Subsequent runs:**
1. Just the Photos delete dialog.

The Terminal window may or may not come to the foreground — it runs either way. If it does surface, it closes itself after the command finishes (`exit` is appended).

### Detection in the tool

Claude Code can observe this in the CLI's stdout:

```
Requested deletion of 1 photo(s):
  778CB2E1-6778-4BE7-82D9-86B99AA9BAAC
This terminal doesn't have Photos access. Opening Terminal.app (which does) to run the delete there — watch for a new Terminal window and the macOS confirmation dialog.
```

That message means delegation fired. Claude should wait for the user to confirm the OS dialog, then verify the delete via `osxphotos query --uuid <UUID>` — the photo is gone from the library's active set if the user clicked Delete.

## Other write paths (not delegated)

Currently only `delete` has the Terminal fallback. Other write-capable commands (`import`, `batch-edit`, `timewarp`, `add-locations`, `push-exif`, `sync`) rely on photoscript / AppleScript, which routes through Automation permission, not Photos TCC. These should work from any terminal as long as Automation → Photos.app is granted.

If one of these unexpectedly fails with a TCC-flavored error, run it from Terminal.app directly.

## Resetting permissions

If a permission gets stuck (denied silently and System Settings won't let you re-enable), reset with `tccutil reset <scope> <bundle-id>`. Example for VS Code's Photos access: `tccutil reset Photos com.microsoft.VSCode`. Scopes: `Photos`, `AppleEvents` (Automation), `All` (every scope for that bundle). Drop the bundle-id for the nuclear all-apps reset. Re-run the osxphotos command afterward — the OS will prompt fresh if the app is able to request the permission.

## Quick diagnostic checklist

1. `osxphotos info` works? → Full Disk Access is fine.
2. `osxphotos show <UUID>` works? → Automation → Photos.app is fine.
3. `osxphotos delete --uuid <UUID> --yes` from your terminal works? → Photos TCC is fine (or delegation is succeeding — check for "Opening Terminal.app…" message).

If any of these fail with a TCC-flavored error, the fix is always the same shape: grant the right permission via System Settings, quit/relaunch the app, retry.
