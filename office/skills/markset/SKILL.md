---
name: markset
description: Use this skill for two separate jobs — (a) authoring markdown that follows the project's formatting rules, (b) building a PDF from an existing markdown file via Pandoc + Tectonic. Match the user's verb: "write/draft/create a report" → author only; "build/render/compile/produce a PDF" → build only; only do both when the user asks for both.
---

> This skill is at `.claude/skills/markset/` relative to the project root. Do not search for it.

# Markset

This skill gives you two capabilities:

1. **Author Markdown** — write documents that conform to the project's formatting rules
2. **Build PDF** — compile markdown files into PDFs using the Pandoc + Tectonic pipeline

The skill is fully self-contained. All templates, fonts, binaries, and scripts live inside this skill folder.

---

## Default behaviour

Match the scope of the user's request — do not bundle.

- Asked to **write / draft / author** markdown → produce the `.md` file and stop. Do not build a PDF.
- Asked to **build / render / compile** → run `build-pdf.sh` against the named file. Do not author new markdown.
- Asked for **both** (e.g. "write and build", "produce a PDF report") → author, then build.

When unsure, ask before building.

---

## Capability 1 — Author Markdown

Write markdown that the build pipeline can compile without errors.
The styleguide ([`./templates/styleguide_md.md`](./templates/styleguide_md.md)) is the single source of truth — read it before writing anything.
Full step-by-step instructions, including the required frontmatter block and common mistakes, are in [`./workflow/author-markdown.md`](./workflow/author-markdown.md).

---

## Capability 2 — Build PDF

Convert any markdown file to PDF using [`./workflow/build-pdf.sh`](./workflow/build-pdf.sh).
The script auto-detects architecture, uses skill-local fonts and binaries, and requires no system installs.
Full step-by-step instructions, including input/output paths, failure diagnosis, and architecture notes, are in [`./workflow/build-pdf.md`](./workflow/build-pdf.md).

---

## Theme customisation

Every visual decision — type scale, spacing rhythm, colour palette, layout variants — lives in a single YAML theme file at [`./themes/presets/default.yaml`](./themes/presets/default.yaml). Copy it, edit, and point the build script at the new theme with `--theme <path>`. Per-document tweaks via frontmatter `theme_overrides:`. Full token reference: [`./themes/SCHEMA.md`](./themes/SCHEMA.md).
