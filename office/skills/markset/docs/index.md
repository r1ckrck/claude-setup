---
title: "Markset Feature Showcase"
author: "Arnesh Mandal"
version: "2.0"
date: "2026-04-21"
include-before: |
  \begin{lstlisting}[style=coverasciiart]
   __  __            _            _
  |  \/  | __ _ _ __| | _____ ___| |_
  | |\/| |/ _` | '__| |/ / __|___| __|
  | |  | | (_| | |  |   <\__ \\\_| |_
  |_|  |_|\__,_|_|  |_|\_\___/ \_|\__|

  A self-contained Markdown to PDF skill
  \end{lstlisting}
---

# Introduction

Markset converts Markdown into polished PDFs with consistent typography, colour, and layout.
This document exercises every element the template supports so regressions are easy to spot.

The skill is self-contained — Pandoc and Tectonic binaries are bundled and fonts live inside the project.
A single YAML theme file drives every visual decision; see `themes/SCHEMA.md` for the full token map.

# Typography

## Paragraphs and Inline Styles

Body text is set in Inter at 10pt on 15pt leading.
Inline elements cover **bold emphasis**, *italic emphasis*, and ***bold italic*** for strong contrast.
Use `inline code` for identifiers, file names like `build-pdf.sh`, or short shell snippets.
Links appear in the muted accent colour — see the [Pandoc user manual](https://pandoc.org/MANUAL.html) for reference.

Consecutive sentences on separate source lines merge into a single paragraph.
This is the authoring convention documented in the styleguide.
It keeps diffs meaningful while producing proper paragraph flow in the PDF.

## Heading Hierarchy

### Third-Level Heading

H3 sits tight to its own content, with a clear step down in size from H2.

#### Fourth-Level Heading

H4 is the deepest level permitted and differentiates from body through weight and a small size bump.

# Lists

## Unordered

- First item in a single-level unordered list
- Second item with **bold** and *italic* content inline
- Third item that references `inline code`
  - Nested child one
  - Nested child two demonstrating the alternate glyph
- Fourth top-level item

## Ordered

1. Install Pandoc via Homebrew or drop a binary into `bin/`
2. Install Tectonic the same way
3. Run the build script with the default theme
   1. Inspect the PDF output
   2. Adjust the theme YAML
4. Repeat until satisfied

# Tables

A table uses dash-count to hint at column width ratios.
Captions are mandatory and appear directly after the closing row.

| Axis | Knob | Effect |
|------|------|--------|
| Rhythm | `rhythm.base` | All block spacing scales |
| Size | `type.body` | All type scales proportionally |
| Colour | `accent.primary` | Every accent reference shifts |
| Layout | `cover.style` | Cover page structure changes |
: Four axes of theme control

A second table with narrow columns distributed by dash count:

| Tier | Size | Leading |
|------|------|---------|
| H1 | 14pt | 17pt |
| H2 | 12pt | 14pt |
| H3 | 10pt | 12pt |
| H4 | 10pt | 14pt |
| Body | 10pt | 14pt |
: Default type scale — H1/H2 derived via `type.scale = 1.2`; H3/H4 match body size with bold weight differentiating

# Callouts

::: note
This is a note callout.
It carries an informational marker and the neutral grey border.
Use it for background context that doesn't change what the reader should do.
:::

::: tip
Tips share their border colour with the primary accent.
Use them to surface a non-obvious shortcut or a better way to do something.
:::

::: warning
Warnings use the warm amber border.
Reserve them for situations that will cause something to break if ignored.
:::

::: important
The important callout uses the muted accent.
Use it sparingly for the single most important thing on a given page.
:::

# Code

## Block with Language

```python
def build_pdf(markdown_path: str, theme_path: str) -> Path:
    """Convert Markdown to PDF via Pandoc + Tectonic."""
    output = OUT_DIR / f"{Path(markdown_path).stem}.pdf"
    subprocess.run([
        "pandoc", markdown_path,
        "--template", TEMPLATE,
        "--metadata-file", theme_path,
        "--pdf-engine=tectonic",
        "-o", str(output),
    ], check=True)
    return output
```

## Shell Snippet

```bash
./workflow/build-pdf.sh --theme themes/presets/default.yaml docs/index.md
./workflow/build-pdf.sh docs/index.md build/custom.pdf
```

## YAML Fragment

```yaml
palette:
  accent:
    primary: "#ca9ee6"
    muted:   "#a080c0"
  callout:
    tip:
      border: "{{accent.primary}}"
      glyph:  "*"
```

# ASCII Art in Body

ASCII-art blocks use the `ascii` class and avoid line breaking.

```ascii
         ┌──────────┐      ┌──────────┐      ┌──────────┐
  .md ──▶│  Pandoc  │─────▶│ Tectonic │─────▶│   .pdf   │
         └──────────┘      └──────────┘      └──────────┘
               │
               ▼
      apply-theme.lua
      (validate, derive, emit)
```

# Images

## Supporting Image

A supporting image sits inline at 60% column width — the reading-column variant.

![A neutral gradient serving as a test image at 60% width](images/sample.jpg)

## Full-Bleed Image

Using the `{width=100%}` modifier promotes an image to full column width — for diagrams or hero shots.

![The same image promoted to full width](images/sample.jpg){width=100%}

## Placeholder

When the final image isn't ready, use an image-placeholder div.

::: image-placeholder
Figure: System architecture
Description: Block diagram showing pandoc, lua filters, and tectonic.
Dimensions: full-bleed
:::

# Two-Column Layouts

Three ratios are available — `split-50-50`, `split-35-65`, `split-65-35`. The gutter between columns is theme-driven (`rhythm.split.gutter`). Each column accepts any block content; the variants below exercise the common combinations.

## 50-50 — Image and Text

::: split-50-50
::: col
![A neutral gradient at 50% width](images/sample.jpg)
:::
::: col
The 50-50 split is the workhorse — two images, two callouts, or a label / definition pair sit naturally side-by-side. Both columns share equal weight.
:::
:::

## 50-50 — Two Images

::: split-50-50
::: col
![Lake at sunrise](images/sample.jpg)
:::
::: col
![Same scene, second exposure](images/sample.jpg)
:::
:::

## 50-50 — Callout and Text

::: split-50-50
::: col
::: tip
The simplest pairing is a tip alongside the rule it supports — the callout reads as a quick prompt, the text carries the detail.
:::
:::
::: col
A callout in one column and explanatory text in the other works well for design rationale, decision logs, or short briefs. The callout sets the directive; the prose argues for it.
:::
:::

## 35-65 — Sidebar Label and Body

::: split-35-65
::: col
**Why split layouts?**

A narrow left column is great for labels, captions, or pull-style call-outs that frame a wider main panel.
:::
::: col
The 35-65 ratio puts the emphasis on the right side. Use it when the right column is the "content" and the left is supporting context — a quote next to its source, a label next to its definition, a small thumbnail next to descriptive text.
:::
:::

## 35-65 — Thumbnail and Description

::: split-35-65
::: col
![Reference photo](images/sample.jpg)
:::
::: col
A thumbnail-sized image on the left frames a longer descriptive block on the right. Useful for catalogue entries, photo essays, and reference cards where the image is the index, not the focus.
:::
:::

## 65-35 — Body and Sidebar Note

::: split-65-35
::: col
The 65-35 ratio inverts the previous one. The main reading column sits on the left where the eye lands first; supplementary material — a small image, a definition, a side note — sits to the right.
:::
::: col
**Side note**

Both columns are atomic; if a row is too tall to fit on the current page, the entire row jumps to the next.
:::
:::

## 65-35 — Body and Reference Image

::: split-65-35
::: col
The eye lands on the body column first because it carries weight. The right column then provides a referenced visual without competing for primary attention. Best for documentation paragraphs that cite a small diagram or screenshot inline.
:::
::: col
![Companion image](images/sample.jpg)
:::
:::

# Block Quotes

> Design is the art of gradually applying constraints until only one option remains.
> Tokens are constraints; a theme is a set of them chosen deliberately.

Block quotes use the callout visual vocabulary — a left rule plus a surface-tone background — but render in italics and secondary text colour to distinguish them from information boxes.

# Footnotes

Footnotes[^1] cite supporting material without breaking reading flow.
Use them sparingly — if a point needs a footnote every sentence, it belongs in the body.[^2]

[^1]: Footnote markers pick up the primary accent colour by default.
[^2]: Or in a separate section, under its own heading.

# Horizontal Rule

Use horizontal rules sparingly to separate thematic shifts within a single heading section.

---

The rule renders as a single thin line matching `rules.thin` in the theme.

# Closing

Everything above should render without manual styling.
If something looks off, the fix is in the theme YAML — not in the Markdown source.
