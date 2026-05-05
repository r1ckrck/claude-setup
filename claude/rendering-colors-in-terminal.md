# Rendering colors in the terminal (for Claude Code chat)

A self-reference for future Claude Code sessions. When the user asks to see colors / swatches / palettes in chat, this is how to do it reliably.

---

## The thing I keep getting wrong

When I run a Bash command that emits ANSI escape codes, the **tool result view** I see in my context shows the escape sequences as visible text — like `[48;2;242;238;227m`. That looks like the codes got stripped.

**They didn't.** That's just how Claude Code's tool-result display escapes raw ESC bytes for safe display in my context window. The user's actual terminal renders the colors correctly.

> **Rule:** Never conclude that ANSI didn't render based on my tool-result view. Trust that `printf` with `\033[...]` works. If I'm unsure, ask the user.

---

## The mechanism

ANSI escape codes are sequences a terminal interprets as commands (color, formatting, cursor movement, etc.). The sequence starts with the **ESC byte** (0x1B, octal `\033`, hex `\x1B`).

To send actual ESC bytes through Bash, use `printf` with `\033`. The `printf` command interprets the escape, sending real ESC bytes to stdout. The terminal then interprets those bytes as color/format commands.

`echo` does **not** interpret `\033` by default. Use `printf` or `echo -e`.

---

## The truecolor (24-bit) format

Modern terminals (including Claude Code's) support 24-bit color. The format is:

| Purpose | Sequence | Example |
|---|---|---|
| Set background to RGB | `\033[48;2;R;G;Bm` | `\033[48;2;242;238;227m` (warm off-white) |
| Set foreground to RGB | `\033[38;2;R;G;Bm` | `\033[38;2;17;17;17m` (near-black) |
| Reset everything | `\033[0m` | always end with this to avoid bleeding |
| Bold | `\033[1m` | for emphasis in text labels |

R, G, B are 0–255 decimals. **Always** terminate with `\033[0m` or color leaks into the next output.

---

## Hex → RGB conversion

If the user gives a hex code, convert each pair to decimal:

| Hex | RGB |
|---|---|
| `#F2EEE3` | 242, 238, 227 |
| `#111111` | 17, 17, 17 |
| `#7A7569` | 122, 117, 105 |
| `#B8842A` | 184, 132, 42 |

Mental math: `0x = 16 × first hex digit + second hex digit`. Or just use `printf '%d' 0xF2`.

---

## Patterns that work

### Single color swatch with label

```bash
printf '\033[48;2;242;238;227m              \033[0m  #F2EEE3  Background\n'
```

A row of spaces with the bg color set acts as a swatch. ~14 spaces is a reasonable width.

### Foreground on background (text preview)

```bash
printf '\033[48;2;242;238;227m\033[38;2;17;17;17m   Aa Bb Cc — sample text   \033[0m\n'
```

Layer fg on bg by chaining the codes. Inner spaces around the text give the swatch breathing room.

### Block-on-block (one color framed by another)

```bash
printf '\033[48;2;242;238;227m   \033[0m\033[48;2;184;132;42m       \033[0m\033[48;2;242;238;227m   \033[0m  Accent against background\n'
```

Reset between segments so each block holds its color.

### Bold label headers

```bash
printf '\n\033[1mPalette\033[0m\n\n'
```

`\033[1m` for bold, reset at end.

### Multi-line palette: chain printf calls

Use a single Bash block with multiple `printf` calls. Each call emits one row. Add `\n` at the end of each format string.

---

## Opacity (there's no real opacity in ANSI)

Terminal ANSI doesn't support alpha. To represent a color "at X% opacity on background Y," **pre-blend the color** mathematically:

```
visible = bg × (1 - α) + fg × α
```

Example: `#1F1F1F at 30% on #F2EEE3`:
- R: `242 × 0.7 + 31 × 0.3 = 169.4 + 9.3 = 178.7 → 179`
- G: `238 × 0.7 + 31 × 0.3 = 166.6 + 9.3 = 175.9 → 176`
- B: `227 × 0.7 + 31 × 0.3 = 158.9 + 9.3 = 168.2 → 168`

Result: `#B3B0A8`. Render that as the swatch.

---

## A complete example

Tested-working block that renders palette + accent options for a design system. Save as a template.

```bash
printf '\n\033[1mPalette\033[0m\n\n'
printf '\033[48;2;242;238;227m              \033[0m  #F2EEE3  Background\n'
printf '\033[48;2;17;17;17m              \033[0m  #111111  Foreground\n'
printf '\033[48;2;122;117;105m              \033[0m  #7A7569  Mute\n'

printf '\n\033[1mPairings on background\033[0m\n\n'
printf '\033[48;2;242;238;227m\033[38;2;17;17;17m   Aa Bb Cc — sample   \033[0m  Foreground on bg\n'
printf '\033[48;2;242;238;227m\033[38;2;122;117;105m   Aa Bb Cc — sample   \033[0m  Mute on bg\n'

printf '\n\033[1mAccent options\033[0m\n\n'
printf '\033[48;2;184;132;42m              \033[0m  #B8842A  A. Archival ochre\n'
printf '\033[48;2;156;31;31m              \033[0m  #9C1F1F  B. Ink red\n'
printf '\033[48;2;31;63;140m              \033[0m  #1F3F8C  C. Studio blue\n'
printf '\n'
```

---

## Gotchas

| Gotcha | Fix |
|---|---|
| `echo` doesn't interpret `\033` | Use `printf` or `echo -e` |
| Forgot the reset `\033[0m` | Always end every colored segment with reset |
| Tried to render in a markdown code block | Code blocks display escape codes as text. Render via Bash command output, not markdown. |
| Used `[` without preceding ESC | The `[` alone does nothing; the ESC byte (`\033`) before it is what triggers interpretation |
| Concluded "it didn't render" from my tool view | My tool-result view always shows escape codes as text. Ask the user if I'm unsure. |

---

## When NOT to use ANSI

- **Saving to a file the user will open later** → use HTML or generate a PNG instead. ANSI only renders live in a terminal.
- **Putting colors inside chat markdown** → won't render. Use Bash output.
- **More than 8 colors at once with intricate layouts** → consider generating an image via fal-image or rendering an HTML preview.

For most "show me what these colors look like" requests, ANSI via `printf` is the right tool.
