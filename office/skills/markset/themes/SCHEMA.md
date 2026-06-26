# Theme Schema

The canonical reference for every key a theme YAML file can contain. Every
theme sits under a top-level `theme:` key. See
`themes/presets/default.yaml` for a complete working example.

## Mental model

A theme is two things side-by-side:

1. **Dials** — dimensionless factors and two base lengths (`type.base`,
   `rhythm.base`). Change a dial and everything proportional re-derives.
2. **Identity & absolutes** — colours, font families, layout enums, page
   margins, rule widths. These are chosen, not derived.

The Lua filter (`templates/apply-theme.lua`) reads the dials, computes a
**tokens tree** (individual heading sizes, heading-before spacings,
callout padding, etc.), applies any overrides, then emits LaTeX.

You rarely touch individual tokens. You turn dials. When you need a
specific token value anyway, use the `overrides:` block.

## Types

| Type | Shape | Examples |
|---|---|---|
| `length` | number + TeX unit | `4pt`, `20mm`, `1.5em` |
| `hex` | `#rrggbb` | `#ca9ee6` |
| `factor` | dimensionless decimal (× `base`) | `1.25`, `0.9`, `2.5` |
| `ratio` | standalone dimensionless decimal | `1.45` (arraystretch), `0.6` (image width) |
| `enum<…>` | one of listed values | see per-key |
| `bool` | `true` / `false` | |
| `string` | free text | `Inter`, `[i]`, `•` |
| `ref` | `{{path.to.hex}}` | `{{accent.primary}}` — palette only |

---

## Dials — `type`

Every role's size and leading is computed from data in the YAML. The Lua
filter walks three per-role tables: `size_exponents`, `size_factors`,
`leading`. No formula is hidden in code.

### Base dials

| Key | Type | Default | Effect |
|---|---|---|---|
| `type.base` | length | `10pt` | Body size — all type scales from here |
| `type.scale` | factor | `1.2` | Heading ratio — raised to an exponent per tier |

### Size — exponent form

For every role in `type.size_exponents`:
**`size = base × scale^exponent`**

| Role | Default | Result at base=10, scale=1.2 |
|---|---|---|
| `h1` | `2` | 14.4pt |
| `h2` | `1` | 12pt |
| `h3` | `0` | 10pt |
| `h4` | `0` | 10pt |

Change an exponent to reshape the hierarchy. Add roles (e.g. `h5: -1`) to
extend it. `cover_title` inherits `h1`; `toc_title` inherits `h2`.

### Size — factor form

For every role in `type.size_factors`:
**`size = base × factor`**

| Role | Default | Result at base=10 |
|---|---|---|
| `caption` | `0.9` | 9pt |
| `code` | `0.9` | 9pt |
| `inline_code` | `0.9` | 9pt |
| `header` | `0.8` | 8pt |
| `line_number` | `0.6` | 6pt |
| `cover_meta` | `0.9` | 9pt |
| `ascii_cover` | `1.4` | 14pt |
| `ascii_body` | `1.2` | 12pt |
| `toc_entry` | `1.0` | 10pt |

### Leading — per role

For every role in `type.leading`:
**`line_height = size × leading[role]`**

Roles missing from the `leading` table fall back to `leading.body`.

| Role | Default | Rationale |
|---|---|---|
| `body` | `1.5` | Readable body leading |
| `h1` / `h2` / `h3` | `1.2` | Tighter — headings are short |
| `h4` | `1.5` | Matches body — h4 reads like body-with-weight |
| `caption` | `1.4` | Smaller text, slightly tighter than body |
| `code` / `inline_code` | `1.4` | Tighter for code blocks |
| `header` / `line_number` | `1.4` | Tighter for supporting text |
| `cover_title` | `1.2` | Heading leading |
| `cover_meta` | `1.4` | Small text leading |
| `ascii_cover` / `ascii_body` | `1.4` | ASCII art needs modest extra air |
| `toc_title` | `1.2` | Heading leading |
| `toc_entry` | `1.4` | Body-ish leading |

> To change how h1 is leaded, edit `type.leading.h1`. To add a new role,
> add an entry to `size_factors` (or `size_exponents`) and optionally a
> matching entry in `leading`. No Lua changes needed.

## Dials — `rhythm`

Every rhythm value is `rhythm.base × factor`. Headings compound via
`heading.step`. Heading-after is `heading-before × content_proximity`.

| Key | Type | Default | Effect |
|---|---|---|---|
| `rhythm.base` | length | `4pt` | Spacing unit — all block rhythm scales from here |
| `rhythm.heading.space` | factor | `7` | H1 before-space = base × this |
| `rhythm.heading.step` | factor | `0.7` | Each level's before-space = previous × this |
| `rhythm.heading.content_proximity` | factor | `0.2` | Heading after-space = before × this. Smaller = tighter to content. |
| `rhythm.block.before` | factor | `2.5` | Before-space for callouts / code / tables |
| `rhythm.callout.after` | factor | `2.5` | Callout after-space (× base) |
| `rhythm.callout.pad_y` | factor | `2` | Callout vertical internal padding |
| `rhythm.callout.pad_x` | factor | `3` | Callout horizontal internal padding |
| `rhythm.code.after` | factor | `3.5` | Code block after-space |
| `rhythm.code.pad_x` | factor | `2.5` | Code block horizontal padding |
| `rhythm.table.after` | factor | `3.5` | Table after-space |
| `rhythm.table.col_sep` | factor | `2` | `\tabcolsep` — horizontal padding per cell |
| `rhythm.table.row_stretch` | ratio | `1.45` | `\arraystretch` — row height multiplier (absolute, not × base) |
| `rhythm.list.top_sep` | factor | `1.5` | Space before/after a list |
| `rhythm.list.item_sep` | factor | `1.25` | Space between items |
| `rhythm.image_placeholder.space` | factor | `2` | Before/after space for image-placeholder divs |
| `rhythm.split.gutter` | factor | `4` | Horizontal gap between columns in `split-*` divs |
| `rhythm.footnote.gap` | factor | `1` | Horizontal gap between footnote pills in the footer |

### Computed from the rhythm dials

These are what the template actually consumes. You rarely address them
directly — change a dial and they cascade. Override any of them in
`overrides:` if you need a specific value.

| Computed token | Formula | Default |
|---|---|---|
| `rhythm.unit` | `rhythm.base` | 4pt |
| `rhythm.xs / sm / md / lg / xl` | base × 0.5 / 1 / 2 / 3 / 5 | 2 / 4 / 8 / 12 / 20pt |
| `rhythm.h1_before` | base × heading.space | 28pt |
| `rhythm.h2_before` | h1_before × step | 20pt |
| `rhythm.h3_before` | h2_before × step | 14pt |
| `rhythm.h4_before` | h3_before × step | 10pt |
| `rhythm.h*_after` | h*_before × content_proximity | ≈ 6 / 4 / 3 / 2pt |
| `rhythm.callout_before` | base × block.before | 10pt |
| `rhythm.callout_after` | base × callout.after | 10pt |
| `rhythm.callout_pad_y` | base × callout.pad_y | 8pt |
| `rhythm.callout_pad_x` | base × callout.pad_x | 12pt |
| `rhythm.code_before` | base × block.before | 10pt |
| `rhythm.code_after` | base × code.after | 14pt |
| `rhythm.code_pad_x` | base × code.pad_x | 10pt |
| `rhythm.table_before` | base × block.before | 10pt |
| `rhythm.table_after` | base × table.after | 14pt |
| `rhythm.table_col_sep` | base × table.col_sep | 8pt |
| `rhythm.list_top_sep` | base × list.top_sep | 6pt |
| `rhythm.list_item_sep` | base × list.item_sep | 5pt |
| `rhythm.image_placeholder_before` | base × image_placeholder.space | 8pt |
| `rhythm.image_placeholder_after` | base × image_placeholder.space | 8pt |
| `rhythm.split_gutter` | base × split.gutter | 16pt |
| `rhythm.footnote_gap` | base × footnote.gap | 4pt |

---

## Identity — `palette`

Colours grouped by role. Hex literals everywhere; `{{path}}` refs within
the palette are resolved before validation.

| Key | Type | Default | Purpose |
|---|---|---|---|
| `palette.page.bg` | hex | `#faf7f2` | Page background |
| `palette.page.fg` | hex | `#181826` | Default body text colour |
| `palette.surface.bg` | hex | `#f4f0e8` | Callouts, quote backgrounds |
| `palette.code.bg` | hex | `#f0ece4` | Code block / inline code background |
| `palette.placeholder.bg` | hex | `#ece8e0` | Image-placeholder fill |
| `palette.placeholder.border` | hex | `#c4c0b6` | Image-placeholder border |
| `palette.text.primary` | hex | `#181826` | Primary text |
| `palette.text.secondary` | hex | `#3d3d4d` | Secondary — metadata, captions |
| `palette.text.tertiary` | hex | `#5d5d6d` | Tertiary — header/footer, glyphs |
| `palette.accent.primary` | hex | `#ca9ee6` | Primary accent — tip borders, footnote marks |
| `palette.accent.muted` | hex | `#a080c0` | Muted accent — TOC numbers, links, important borders |
| `palette.rule.table` | hex | `#d4d0c6` | Table rules, quote border, footnote rule |
| `palette.callout.note.border` | hex | `#8d8d9d` | Note callout border |
| `palette.callout.note.glyph` | string | `[i]` | Note leading glyph |
| `palette.callout.tip.border` | hex/ref | `{{accent.primary}}` | Tip callout border |
| `palette.callout.tip.glyph` | string | `*` | Tip leading glyph |
| `palette.callout.warning.border` | hex | `#d4a574` | Warning callout border |
| `palette.callout.warning.glyph` | string | `[!]` | Warning leading glyph |
| `palette.callout.important.border` | hex/ref | `{{accent.muted}}` | Important callout border |
| `palette.callout.important.glyph` | string | `[*]` | Important leading glyph |
| `palette.syntax.string` | hex/ref | `{{accent.muted}}` | String literals in code |
| `palette.syntax.comment` | hex/ref | `{{text.tertiary}}` | Comments in code |
| `palette.syntax.number` | hex/ref | `{{text.secondary}}` | Numeric literals in code |

## Identity — `fonts`

| Key | Type | Default | Purpose |
|---|---|---|---|
| `fonts.main.family` | string | `Inter` | Main font family (must exist in `templates/fonts/`) |
| `fonts.main.weights.regular` | string | `-Regular` | Suffix for upright |
| `fonts.main.weights.bold` | string | `-SemiBold` | Suffix for bold |
| `fonts.main.weights.italic` | string | `-Italic` | Suffix for italic |
| `fonts.main.weights.bolditalic` | string | `-SemiBoldItalic` | Suffix for bold italic |
| `fonts.mono.family` | string | `JetBrainsMono` | Monospace font family |
| `fonts.mono.scale` | ratio | `0.9` | Mono font scale relative to body |
| `fonts.mono.weights.*` | string | `-Regular` / `-Bold` / `-Italic` / `-BoldItalic` | Weight suffixes |

> Swapping fonts requires TTFs in `templates/fonts/` with matching weight
> suffix naming.

---

## Absolutes

These sit outside the rhythm/type derivation.

### `page`

| Key | Type | Default | Effect |
|---|---|---|---|
| `page.margin.top` | length | `20mm` | |
| `page.margin.bottom` | length | `15mm` | |
| `page.margin.left` | length | `12.5mm` | |
| `page.margin.right` | length | `12.5mm` | |
| `page.header.height` | length | `12pt` | Running header box height |
| `page.header.sep` | length | `6pt` | Gap between header and body |
| `page.footer.skip` | length | `10pt` | Footer distance from body |

### `rules`

| Key | Type | Default | Effect |
|---|---|---|---|
| `rules.thin` | length | `0.5pt` | Light table rules, H1 rule, footnote rule |
| `rules.thick` | length | `0.75pt` | Heavy table rules (booktabs `\heavyrulewidth`) |
| `rules.callout_border` | length | `3pt` | Left border of callout / quote boxes |

### `list`

| Key | Type | Default | Effect |
|---|---|---|---|
| `list.indent` | length | `14pt` | Left indent of top-level lists |
| `list.sub_indent` | length | `16pt` | Left indent of nested lists |
| `list.marker_l1` | string | `•` | Level-1 bullet glyph |
| `list.marker_l2` | string | `◦` | Level-2 bullet glyph |

### `image`

| Key | Type | Default | Effect |
|---|---|---|---|
| `image.default_width` | ratio | `0.6` | Default image width as fraction of linewidth |
| `image.placeholder_height` | length | `60pt` | Image-placeholder box height |

### `layout`

Named variants — change structure, not just values.

| Key | Type | Values | Default |
|---|---|---|---|
| `layout.cover.style` | enum | `centered-ascii`, `title-top`, `none` | `centered-ascii` |
| `layout.header.content` | enum | `title-version`, `title-only`, `section`, `none` | `title-version` |
| `layout.toc.include` | bool | `true` / `false` | `true` |
| `layout.toc.depth` | integer | 1–4 | `3` |
| `layout.numbering.scheme` | enum | `arabic`, `roman`, `none` | `arabic` |
| `layout.numbering.h1_numbered` | bool | `true` / `false` | `false` |
| `layout.tables.break_threshold` | integer | row count above which a table is allowed to break across pages; at or below it stays on one page | `12` |

---

## Overrides

Both theme-level (`overrides:` block in the YAML) and per-document
(`theme_overrides:` in frontmatter) use dot-path keys. Paths route by
first segment:

| First segment | Writes to | Example |
|---|---|---|
| `type.*` | tokens tree (post-compute) | `type.h1: 22pt` |
| `rhythm.*` | tokens tree (post-compute) | `rhythm.callout_pad_x: 16pt` |
| `palette.*` | theme palette | `palette.accent.primary: "#ff6600"` |
| `fonts.*` | theme fonts | `fonts.main.family: "Helvetica"` |
| `layout.*` | theme layout | `layout.cover.style: title-top` |
| `page.*` | theme page | `page.margin.top: 25mm` |
| `rules.*` | theme rules | `rules.thin: 0.75pt` |
| `list.*` | theme list | `list.marker_l1: "▸"` |
| `image.*` | theme image | `image.default_width: 0.8` |

> **Type/rhythm overrides target output tokens, not input dials.**
> To change `type.scale` or `rhythm.heading.space`, edit the top-level
> theme value directly — don't put it in `overrides:`. That way a scale
> change cascades; a specific override pins one output value only.

Example frontmatter:

```yaml
---
title: "…"
author: "…"
version: "…"
date: "…"
theme_overrides:
  palette.accent.primary: "#ff6600"
  type.h1: 24pt
  rhythm.h1_before: 36pt
  layout.cover.style: title-top
---
```

---

## Locked (not tokens)

These are structural decisions baked into `templates/template.tex`. To
change any of them, edit the template.

- Widow / orphan penalties (`\widowpenalty=10000`, `\clubpenalty=10000`)
- `\parindent = 0pt`
- Pandoc `\tightlist` behaviour
- TOC hang / indent widths within a tier (`\cftsubsubsecindent` etc.)
- Section-penalty value (`\@secpenalty`)
- Callout `breakable` / `frame hidden` structural choices
- tcolorbox `enhanced` engine
- `\floatplacement{figure}{H}` — figures don't float
