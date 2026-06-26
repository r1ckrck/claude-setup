# Markset — Developer Reference

Markset converts Markdown to PDF via Pandoc + Tectonic. Binaries and fonts are bundled; no system installs.

## Directory layout

```
markset/
├── CLAUDE.md                  This file
├── SKILL.md                   Skill manifest (trigger description)
├── README.md                  End-user setup + troubleshooting
├── bin/                       Pandoc + Tectonic binaries (gitignored, per-arch)
├── cache/                     Tectonic LaTeX package cache (gitignored, ~300 MB)
├── build/                     Generated PDFs (gitignored)
├── docs/                      Markdown sources
│   ├── index.md               Showcase doc — exercises every template element
│   └── images/                Image assets (gitignored)
├── templates/
│   ├── template.tex           Structural LaTeX — consumes \ms* tokens only
│   ├── apply-theme.lua        Theme pipeline: validate → compute → emit tokens
│   ├── divs.lua               Div / code / table / FloatBarrier / split-* layouts
│   ├── styleguide_md.md       Markdown authoring rules
│   └── fonts/                 TTFs (Inter + JetBrains Mono, gitignored)
├── themes/
│   ├── README.md              Theme workflow
│   ├── SCHEMA.md              Full token reference
│   └── presets/
│       └── default.yaml       Bundled default theme
└── workflow/
    ├── build-pdf.sh           Build script — entry point
    ├── build-pdf.md           Step-by-step build instructions for Claude
    └── author-markdown.md     Step-by-step authoring instructions for Claude
```

## Architectural invariants

Break any of these and the build logic cracks open.

- **`templates/template.tex` is structural only.** It consumes `\ms*` tokens and `$if(...)$` layout flags; it must never define them. All numeric and colour decisions come from the theme.
- **`templates/apply-theme.lua` is the token source.** It reads the theme YAML, validates, computes derived values, and emits `\ms*` macros + `\definecolor` into `header-includes`. The only Lua that should touch theme data.
- **Filter order matters.** `apply-theme.lua` runs before `divs.lua` in the pandoc invocation. Never reorder. `divs.lua` handles `:::` divs, inline/block code, tables, and `\FloatBarrier` before H2/H3 — it must not touch theme state.
- **LaTeX command names cannot contain digits.** Heading tokens use `hone / htwo / hthree / hfour`, never `h1 / h2 / h3 / h4`. YAML keys stay `h1` / `h2`; Lua translates.
- **Overrides target output tokens, not input dials.** `theme_overrides: { type.h1: 22pt }` pins h1. `theme_overrides: { type.scale: 1.4 }` silently no-ops — to change a dial, edit it at the top level.
- **Skill stays self-contained.** No system dependencies. Binaries under `bin/`, fonts under `templates/fonts/`, cache under `cache/`.

## Build

```bash
./workflow/build-pdf.sh <input.md> [output.pdf]
./workflow/build-pdf.sh --theme <path> <input.md>
```

Theme resolution (highest wins): `--theme` flag → `./theme.yaml` next to input → `themes/presets/default.yaml`.

## Where things live

| Concern | File |
|---|---|
| Visual tokens (type, rhythm, palette, fonts, layout) | [`themes/presets/default.yaml`](./themes/presets/default.yaml) |
| Full token reference — every field, type, default, effect | [`themes/SCHEMA.md`](./themes/SCHEMA.md) |
| Theme workflow (presets, overrides, resolution) | [`themes/README.md`](./themes/README.md) |
| Markdown authoring grammar | [`templates/styleguide_md.md`](./templates/styleguide_md.md) |
| Build / author step-by-step | [`workflow/build-pdf.md`](./workflow/build-pdf.md), [`workflow/author-markdown.md`](./workflow/author-markdown.md) |
| Setup, binaries, troubleshooting, platform support | [`README.md`](./README.md) |

## Extending

| Task | Steps |
|---|---|
| Add a token | Add the dial in `default.yaml` → derive in `apply-theme.lua` `compute_defaults()` → emit via `emit_tokens()` → consume in `template.tex` → document in `SCHEMA.md` |
| Add a markdown construct | Handler in `divs.lua` → rule in `styleguide_md.md` → matching LaTeX env in `template.tex` if needed |
| Add a layout variant (cover / header / numbering) | Enum value in `default.yaml` `layout.*` → bool flag in `apply-theme.lua` → `$if(...)$` branch in `template.tex` → document in `SCHEMA.md` |
