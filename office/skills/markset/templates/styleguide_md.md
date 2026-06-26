# Markdown Styleguide

## Frontmatter
Required fields — all must be present:
```yaml
---
title: "Document Title"
author: "Arnesh Mandal"
version: "1.0"
date: "2026-01-30"
include-before: |
  \begin{lstlisting}[style=coverasciiart]
  Your ASCII art here (max 60 chars wide, 16 lines tall)
  \end{lstlisting}
---
```

`include-before` must use the literal `lstlisting` wrapper shown — a bare string breaks the cover render.

Optional — theme customisation:
```yaml
theme_overrides:
  palette.accent.primary: "#ff6600"   # one-off accent colour
  rhythm.base: 5pt                     # bump the rhythm unit
  rhythm.h1_before: 36pt               # more air above H1
  layout.cover.style: title-top        # swap cover layout
```
Dot-path keys address any theme field — see `themes/SCHEMA.md` for the full map.

## Structure
- One sentence per line (source readability)
- Consecutive sentences combine into paragraphs in PDF
- Use bullets for separate points that should not combine into paragraphs
- Blank line between paragraphs or sections
- No indentation except for nested list items (2 spaces per level)

## Headings
- Max depth: H4
- Title Case: `# Getting Started With the API`
- Auto-numbered (never manual)
- One blank line before every heading; none after
- Multiple H1s per document are expected — the document title comes from frontmatter, not from `#`

Levels:
- `#` H1 — top-level section, a major division of the document
- `##` H2 — subsection within an H1
- `###` H3 — grouping inside an H2; use only when the section needs internal landmarks
- `####` H4 — rare; usually a signal to restructure

## Lists
- Max 2 levels nesting
- No callouts or complex blocks inside

```markdown
- Parent
  - Child
1. First
2. Second
```

## Tables
- Caption mandatory — `: Caption` line directly after the table, no blank line
- Column widths set by dash count in the header separator
- Distribute dashes by content length (short = fewer, long = more)
- Tables do not auto-shrink or scroll — keep content narrow enough to fit the column, or split into multiple tables

```markdown
| Col A | Col B |
|-------|-------|
| Data  | Data  |
: Table caption
```

## Code
- Inline: `` `code` ``
- Blocks: always specify language, aim <80 chars, no blank line before

````markdown
```python
def hello():
    print("world")
```
````

## ASCII Art
Two contexts — different limits:

- **Cover art** (in frontmatter `include-before`) — max 60 chars wide, 16 lines tall
- **Inline `ascii` block** — max 82 chars wide, no height limit; for diagrams in body

````markdown
```ascii
   +---------+
   |  Box    |
   +---------+
```
````

## Callouts
Four types — same syntax, different visual treatment. Never inside lists/tables or nested.

```markdown
::: note
Content here.
:::

::: tip
Content here.
:::

::: warning
Content here.
:::

::: important
Content here.
:::
```

## Images
Use only when necessary. Formats: PNG, JPG, PDF.

Two variants — pick based on role:

**Supporting image** (default, 60% column width — sits inside the reading column):
```markdown
![Caption](path.png)
```

**Full-bleed image** (100% column width — hero / diagram / feature shot):
```markdown
![Caption](path.png){width=100%}
```

Width override accepts `%` of column width (e.g. `{width=80%}`). Prefer the two variants above for consistency.

Placeholder (when the image is not yet available):
```markdown
::: image-placeholder
Figure: Title
Description: What it shows
Dimensions: supporting | full-bleed
:::
```

### Two-column layouts
Each column accepts any block content — image, text, callout, list, code. Any combination works: image + text, text + image, image + image, text + text.

| Class | Left | Right |
|---|---|---|
| `split-50-50` | 50% | 50% |
| `split-35-65` | 35% | 65% |
| `split-65-35` | 65% | 35% |

Syntax — outer div names the ratio, two `::: col` children carry the content:
```markdown
::: split-50-50
::: col
![Left caption](left.png)
:::
::: col
![Right caption](right.png)
:::
:::
```

Suggestions:
- `split-50-50` — equal pairs: comparison, two images, two notes
- `split-35-65` / `split-65-35` — the shorter side reads as a caption or sidebar to the longer side

Both columns are atomic and will not break across pages — keep each side roughly page-sized at most. Splits cannot nest — each `split-*` must contain exactly two `::: col` children, no further `split-*` inside.

## Links
`[descriptive text](url)` - never "click here" or raw URLs

## Other Elements
- **Block quotes**: `> text` (use sparingly)
- **Horizontal rules**: `---` (use sparingly)
- **Footnotes**: `text[^1]` + `[^1]: Note` at end (use sparingly)
- **Icons/Emojis**: Not used. For diagrams use ASCII art in an `ascii` code block

## Prohibited
No raw LaTeX (`\newpage`), HTML (`<div>`), or manual styling (fonts/colors/spacing).
Template handles all visual decisions.