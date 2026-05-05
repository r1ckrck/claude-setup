# VS Code Terminal Keybindings

Custom keybindings for working comfortably inside VS Code's integrated terminal — built around juggling multiple Claude Code sessions across tabs and splits.

Config lives at: `~/Library/Application Support/Code/User/keybindings.json`

## Design principle

**One modifier family for all terminal navigation: `⌥⌘` (Option + Cmd).**

- **`⌥⌘` + arrows** = navigate. Up/Down = tabs. Left/Right = panes.
- **`⌥⌘` + key** = act. N = New, W = Close, `\` = Split.

No brackets, no mixed modifiers, no memorizing exceptions.

## Custom bindings

| Action | Shortcut | VS Code command |
|---|---|---|
| New terminal tab | `⌥⌘N` | `workbench.action.terminal.new` |
| Close active terminal | `⌥⌘W` | `workbench.action.terminal.kill` |
| Split terminal | `⌥⌘\` | `workbench.action.terminal.split` |
| Next terminal tab | `⌥⌘↓` | `workbench.action.terminal.focusNext` |
| Previous terminal tab | `⌥⌘↑` | `workbench.action.terminal.focusPrevious` |
| Focus left pane | `⌥⌘←` | `workbench.action.terminal.focusPreviousPane` |
| Focus right pane | `⌥⌘→` | `workbench.action.terminal.focusNextPane` |

All custom bindings are scoped with `"when": "terminalFocus"` so they don't hijack editor shortcuts outside the terminal.

## Defaults kept as-is

| Action | Shortcut | Notes |
|---|---|---|
| Toggle bottom panel | `⌘J` | Used to focus/unfocus terminal |
| Copy / Paste | `⌘C` / `⌘V` | System default |
| Select all | `⌘A` | System default |
| Cursor to start of line | `⌃A` | Unix default |
| Cursor to end of line | `⌃E` | Unix default |
| Delete word backward | `⌥⌫` | macOS default |
| Previous shell command | `↑` | Shell history |
| Next shell command | `↓` | Shell history |

## Why `⌘W` needed rebinding

`⌘W` is VS Code's global "close" — in a terminal context it closes the entire panel, killing all terminal tabs. The dedicated `workbench.action.terminal.kill` command closes only the focused terminal but has no default binding. `⌥⌘W` fills that gap.

## Preserved: `shift+enter` → ESC + CR

The existing Claude Code binding for `shift+enter` (sends `\r` to insert a newline in the Claude prompt without submitting) is untouched.

## Reset / troubleshoot

- **Reload after editing:** VS Code usually picks up changes immediately. If not: command palette → `Developer: Reload Window`.
- **Check what's bound:** command palette → `Preferences: Open Keyboard Shortcuts` → search for "terminal".
- **Conflicts:** if a shortcut doesn't fire, another binding is winning. Open the Keyboard Shortcuts UI, search the key combo, and look for competing entries.
