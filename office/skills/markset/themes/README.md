# Themes

A **theme** is a YAML file that controls every visual aspect of a Markset PDF:
spacing, typography, colours, layout variants.

## Using a theme

Pick one of three ways — listed in precedence order, highest wins.

1. **CLI flag**: pass `--theme path/to/theme.yaml` to the build script
2. **Project theme**: drop a file called `theme.yaml` next to your markdown file
3. **Default**: if neither is present, `themes/presets/default.yaml` is used

```bash
./workflow/build-pdf.sh docs/report.md
./workflow/build-pdf.sh --theme themes/presets/minimal.yaml docs/report.md
./workflow/build-pdf.sh docs/report.md --theme ~/my-brand/theme.yaml
```

## Customising

Copy a preset and edit — never edit the bundled presets directly:

```bash
cp themes/presets/default.yaml themes/my-theme.yaml
# …edit my-theme.yaml…
./workflow/build-pdf.sh --theme themes/my-theme.yaml docs/report.md
```

The full list of keys, types, defaults, and what they control is in `SCHEMA.md`.

## Per-document overrides

Override individual tokens in a document's frontmatter without touching the
theme file:

```yaml
---
title: "Launch Report"
author: "Jane Doe"
version: "1.0"
date: "2026-04-21"
theme_overrides:
  palette.accent.primary: "#ff6600"
  rhythm.base: 5pt
  rhythm.h1_before: 36pt
---
```

Dot-paths address any field in the theme tree. The override wins over the
theme file for this document only.

## What's in a theme

Four axes, loosely independent:

| Axis | Governed by | Example change |
|---|---|---|
| Rhythm | `rhythm.base` | `4pt → 5pt` scales all block spacing |
| Size | `type.body`, `type.scale_ratio` | `10pt → 11pt` body scales every text size |
| Colour | `palette.*` | Replace one hex → palette-wide shift |
| Layout | `layout.*` | Switch cover style or header content |

Most tokens fall cleanly on one axis. Where a token is an absolute value that
sits outside the derivation system (page margins, rule widths, specific
padding), it's documented as independent in `SCHEMA.md`.

## Adding a preset

Presets live in `themes/presets/`. To add one, copy `default.yaml`, rename,
edit. Reference it via `--theme themes/presets/<name>.yaml`.
