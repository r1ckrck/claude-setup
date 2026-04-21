# Show Claude Code Session State in VS Code Terminal Tabs

A tiny setup that makes each Claude Code session's terminal tab in VS Code dynamically display its current state — done, waiting, or working — so you can manage multiple sessions at a glance without OS notifications.

## What you'll get

Each Claude Code session running in a separate VS Code terminal will have its tab title in the right-side tab list reflect that session's state:

| Tab title | Meaning |
|---|---|
| `✓` | Claude finished its turn, your move |
| `⚠` | Claude needs permission or input |
| (Claude's own title, e.g. `✳ Claude`) | Actively working |

With multiple Claude sessions open, each tab updates independently. No popups, no toasts.

## How it works

Two pieces working together:

1. **VS Code** can use a special tab-title variable called `${sequence}` — it reflects whatever title the program inside the terminal has set via an OSC escape sequence.
2. **Claude Code hooks** (`Stop` and `Notification`) let you run a shell command at specific lifecycle moments. We use them to write OSC escape sequences directly to the terminal (`/dev/tty`), updating the title.

When Claude finishes a turn → `Stop` hook fires → writes `\033]2;✓\007` to the terminal → terminal updates its title → VS Code shows the new title in the tab list.

We use just an icon (not a longer label) because hooks **replace** the title — they can't append to it. A single character feels like a status prefix and stays out of the way.

## Setup

### 1. VS Code settings

Open `Cmd+Shift+P` → "Preferences: Open User Settings (JSON)" and add:

```json
"terminal.integrated.tabs.title": "${sequence}",
"terminal.integrated.tabs.description": "${process}${separator}${cwd}"
```

The `${sequence}` is the key — without it, VS Code uses its default title format and ignores escape-sequence titles.

### 2. Claude Code hooks

Edit `~/.claude/settings.json` (create the file if it doesn't exist) and add a `hooks` block:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "printf '\\033]2;✓\\007' > /dev/tty 2>/dev/null || true"
          }
        ]
      }
    ],
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "printf '\\033]2;⚠\\007' > /dev/tty 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

If you already have a `hooks` block, merge these entries into it — don't replace the whole thing.

The empty matcher (`""`) means the hook fires for all events of that type. The `2>/dev/null || true` ensures the hook never errors-out Claude if `/dev/tty` is unavailable.

### 3. Reload

- Reload VS Code: `Cmd+Shift+P` → "Developer: Reload Window".
- Restart any active Claude Code sessions so they pick up the new hooks.

## Testing

1. Open a new VS Code terminal.
2. Run `claude` and send any prompt.
3. Wait for the response.
4. Look at the **right-side terminal tab list** — that session's tab should now read `✓`.
5. Open another terminal, run another `claude` session, and confirm both tabs update independently.

## Customize the labels

The titles are arbitrary — change the text inside `printf '\\033]2;<TITLE>\\007'` to whatever you want:

- `✅` / `🔔`
- `[done]` / `[waiting]`
- `✓ Claude` / `⚠ Claude` (icon + short label if you want more context)

Skip emojis if your terminal font doesn't render them well. Keep titles short — long titles get truncated in the tab list.

## What about renaming tabs?

There are two kinds of rename and they behave differently:

**1. VS Code right-click → "Rename"**
This sets a manual override that beats `${sequence}`. Once you rename a tab this way, our hook still runs but VS Code ignores the new title. You won't see `✓` or `⚠` updates on that tab anymore. To restore auto-status, kill the terminal and start a new one.

**2. Claude Code's `/rename` slash command**
Claude writes a new title via escape sequence — it shows up immediately. But the next `Stop` or `Notification` hook overwrites it with `✓` or `⚠`. Net effect: `/rename` titles get clobbered after Claude's next turn. To make `/rename` titles stick, set `"terminalTitleFromRename": false` in `~/.claude/settings.json` — but that disables the rename → title behavior entirely.

**Rule of thumb:** can't have both a custom name AND auto status icons on the same tab. Pick one per terminal.

## Caveats

- **Claude Code overwrites the title when working** — it sets its own title (e.g. `✳ Claude`) at the start of each turn. Our `✓` only shows during the gap between turns. This is the desired behavior.
- **`/dev/tty` requires a controlling terminal**. In standard interactive Claude Code sessions this is always available. In headless setups (CI, SSH without a TTY) the hook silently no-ops.
- **VS Code-only.** This relies on VS Code's `${sequence}` tab variable. iTerm2 and other terminals show OSC titles in their own way — the hook still works, but the displayed location differs.

## Related VS Code settings worth enabling

For a fuller terminal experience that pairs well with this:

```json
"terminal.integrated.shellIntegration.enabled": true,
"terminal.integrated.shellIntegration.decorationsEnabled": "both",
"terminal.integrated.tabs.enabled": true,
"terminal.integrated.tabs.location": "right",
"terminal.integrated.enableVisualBell": true,
"terminal.integrated.stickyScroll.enabled": true,
"terminal.integrated.confirmOnKill": "always"
```

These give you success/fail dots in the gutter, a flash on the bell character (which Claude Code emits when it needs you), and protection against accidentally killing a running Claude session.

## Why not OS notifications?

Notifications are jarring and don't tell you *which* of several Claude sessions needs attention. The tab-title approach gives per-session visual state with zero interruption — you check it when you choose to.
