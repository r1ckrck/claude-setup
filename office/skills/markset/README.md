# markset

A Claude Code skill that turns Markdown into polished PDFs — authored by AI, rendered with a fixed design grammar.

AI writes great structured content. The problem is markdown carries no design. markset solves this: define the design once in a LaTeX template, let Claude write to that grammar. Every document looks consistent and intentional — no manual formatting.

## How it works

```
Markdown  →  Pandoc  →  Tectonic (XeLaTeX)  →  PDF
               ↑               ↑
         Lua filter       LaTeX template
         (callouts)       (fonts, layout, colors)
```

Ships its own Pandoc and Tectonic binaries. No system tools required beyond bash.

## Features

- **Cover page** — ASCII art + title block + table of contents on page one
- **Clickable TOC** — hyperlinked, depth-2, auto-generated
- **Auto-numbered sections** — H2/H3/H4 numbered automatically, H1 unnumbered
- **Syntax-highlighted code** — language-aware, monospaced, styled background
- **Inline code** — highlighted background, styled to match
- **ASCII art blocks** — rendered in monospace, no line-breaking
- **Callouts** — `note`, `tip`, `warning`, `important` with left-border accents
- **Image placeholders** — dashed box with label for images to be added later
- **Tables** — styled with captions, left-aligned, no manual formatting needed
- **Clickable links** — colored, no underline
- **Block quotes** — styled with left-border
- **Footnotes** — numbered, styled
- **Running header** — title + version on every page
- **Page numbers** — bottom-right on every page

---

## Setup

### 1. Clone into your Claude skills folder

```bash
git clone https://github.com/r1ckrck/markset.git ~/.claude/skills/markset
```

### 2. Add binaries

Binaries are not included in the repo. Detect your architecture first:

```bash
uname -m   # arm64 = Apple Silicon · x86_64 = Intel/Linux
```

**Pandoc** — [github.com/jgm/pandoc/releases/latest](https://github.com/jgm/pandoc/releases/latest)
Download the standalone binary, then:
```bash
cp pandoc-*/bin/pandoc ~/.claude/skills/markset/bin/pandoc-arm64
chmod +x ~/.claude/skills/markset/bin/pandoc-arm64
```

**Tectonic** — [github.com/tectonic-typesetting/tectonic/releases/latest](https://github.com/tectonic-typesetting/tectonic/releases/latest)
Download the single binary, then:
```bash
cp tectonic ~/.claude/skills/markset/bin/tectonic-arm64
chmod +x ~/.claude/skills/markset/bin/tectonic-arm64
```

> Replace `arm64` with `x86_64` if that's your architecture.

### 3. (macOS only) Clear quarantine if binaries are blocked

```bash
xattr -d com.apple.quarantine ~/.claude/skills/markset/bin/pandoc-arm64
xattr -d com.apple.quarantine ~/.claude/skills/markset/bin/tectonic-arm64
```

---

## Usage

Ask Claude to write a document and build it to PDF — Claude handles both steps once the skill is loaded.

To build manually:
```bash
~/.claude/skills/markset/workflow/build-pdf.sh <input.md> [output.pdf]
```

If no output path is given, the PDF is saved to `build/<filename>.pdf` relative to the input file's parent directory. The folder is created automatically.

> **First build:** Tectonic downloads ~300 MB of LaTeX packages into `cache/`. Subsequent builds are fast.

---

## Compatibility

| Platform | Architecture | Status |
|----------|-------------|--------|
| macOS Apple Silicon | arm64 | Supported |
| macOS Intel | x86_64 | Supported |
| Linux | x86_64 | Supported |
| Windows | any | Not supported |
: Platform support

---

## Customisation

All visual decisions live in a single YAML theme file. Copy `themes/presets/default.yaml`, edit, point the build script at it.

| What you want to change | Where to edit |
|-------------------------|---------------|
| Body size, heading scale, line-height, per-role leading | `themes/presets/default.yaml` → `type.*` |
| Spacing rhythm, heading air, callout / code / table padding | `themes/presets/default.yaml` → `rhythm.*` |
| Colour palette, callout glyphs | `themes/presets/default.yaml` → `palette.*` |
| Fonts, page margins, rule widths, cover style, TOC, numbering | `themes/presets/default.yaml` → `fonts.*`, `page.*`, `layout.*`, `rules.*` |
| Per-document tweak (one-off) | frontmatter `theme_overrides:` |
| Markdown grammar Claude follows | `templates/styleguide_md.md` |
| Structural changes (new block types, cover layout variants) | `templates/template.tex` |
: Customisation reference

**Three knobs do most of the work:** `type.base` (body size), `rhythm.base` (spacing unit), `palette.accent.primary` (accent colour). Change one of those and everything proportional cascades.

Full token map with every field, type, default, and effect: `themes/SCHEMA.md`.

### Multiple themes

Create named presets in `themes/presets/`:

```bash
cp themes/presets/default.yaml themes/presets/minimal.yaml
# …edit minimal.yaml…
./workflow/build-pdf.sh --theme themes/presets/minimal.yaml docs/report.md
```

Resolution order (highest wins): `--theme` flag → `./theme.yaml` next to the markdown file → `themes/presets/default.yaml`.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Binary blocked by Gatekeeper | `xattr -d com.apple.quarantine bin/<binary>` |
| Binary not executable | `chmod +x bin/<binary>` |
| Fonts missing | Ensure all 8 TTFs are in `templates/fonts/` |
| Slow first build | Expected — Tectonic fetches LaTeX packages once |
: Common issues
