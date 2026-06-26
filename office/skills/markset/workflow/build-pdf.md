# Capability 2 — Build PDF

## 1. Run the Script

Use [`../workflow/build-pdf.sh`](../workflow/build-pdf.sh) directly. No other build tool is needed.

```bash
.claude/skills/markset/workflow/build-pdf.sh <input.md> [output.pdf]
```

The skill is always at `.claude/skills/markset/` relative to the project root. Use this relative path — do not use absolute paths and do not search for the skill folder.

---

## 2. Input / Output Paths

- **Input**: any `.md` file from anywhere; pass it as the first argument
- **Output**: optional second argument
  - If provided, the PDF is written to that path
  - If omitted, the PDF is written to `build/<filename>.pdf` relative to the input file's parent directory

If the user specifies a different output location, use that path as the second argument.

---

## 3. What the Script Does

The script (`../workflow/build-pdf.sh`) performs these steps automatically:

1. Detects architecture via `uname -m` (`arm64` or `x86_64`)
2. Selects `bin/pandoc-<arch>` and `bin/tectonic-<arch>` accordingly
3. Sets `OSFONTDIR` to `templates/fonts/` — no system font install required
4. Sets `TECTONIC_CACHE_DIR` to `cache/` — first build downloads ~300 MB of LaTeX packages; subsequent builds are fast
5. Runs Pandoc with the custom LaTeX template, Lua filter, TOC, section numbering, and listings support

---

## 4. Verify the Build

After running:

1. Confirm the PDF exists at the expected output path
2. If the script printed errors, surface them to the user verbatim
3. Do not silently retry — diagnose the error first

---

## 5. Diagnose Failures

| Symptom | Likely cause |
|---------|-------------|
| LaTeX error about missing frontmatter | `title`, `author`, `version`, `date`, or `include-before` missing from YAML |
| Binary not found | `bin/pandoc-<arch>` or `bin/tectonic-<arch>` not present — see README.md |
| Font not found | TTF files missing from `templates/fonts/` — see README.md |
| Template not found | `templates/template.tex` missing — skill folder may be incomplete |
| Callout render error | Callout is inside a list or table (prohibited) |
| Table render error | Table is missing its caption (`: Caption text` line) |
| Raw LaTeX/HTML error | Document contains `\newpage`, `<div>`, or other prohibited elements |
: Common build failure causes

---

## 6. Architecture Note

The skill ships two binary slots per tool:

- `bin/pandoc-arm64` + `bin/tectonic-arm64` → Apple Silicon Macs
- `bin/pandoc-x86_64` + `bin/tectonic-x86_64` → Intel Macs / Linux x86_64

The build script selects the correct binary automatically via `uname -m`.
If a binary is missing, direct the user to README.md.
