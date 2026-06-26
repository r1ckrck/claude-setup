# Capability 1 — Author Markdown

## 1. Read the Styleguide First

Before writing anything, read [`../templates/styleguide_md.md`](../templates/styleguide_md.md).
It is the single source of truth for all formatting rules.
Do not rely on memory — read the file every time.

---

## 2. Frontmatter

Every document requires these fields in the YAML block at the top of the file.
All fields are required — omitting any will cause a build failure.

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

`include-before` renders as cover art on the title page.
Design the ASCII art to fit the document's subject matter.
Hard limits: **60 characters wide**, **16 lines tall**.

---

## 3. File Placement

Save new markdown files to `docs/<filename>.md` relative to the project root, unless the user explicitly specifies a different location.

---

## 4. Writing Rules

The styleguide covers all rules authoritatively. Read it for the full details.
Summary of key areas:

- **Structure** — one sentence per line; consecutive sentences form paragraphs in the PDF
- **Headings** — max H4 depth; Title Case; auto-numbered (never add numbers manually)
- **Lists** — max 2 levels; no callouts or complex blocks inside a list
- **Tables** — caption is mandatory (`: Caption text` line immediately after the table, no blank line between); use dash count to control column width ratios
- **Callouts** — types: `note`, `tip`, `warning`, `important`; never inside lists or tables
- **Code blocks** — always specify language; aim for <80 chars per line
- **ASCII art** — use ` ```ascii ` class for inline diagrams; max 82 chars wide
- **Two-column layouts** — three ratios (`split-50-50`, `split-35-65`, `split-65-35`); each side accepts any block content (image, text, callout, list, code); both columns are atomic and won't break across pages

---

## 5. Common Mistakes

| Mistake | How to fix |
|---------|------------|
| Table missing caption | Add `: Caption text` on the line immediately after the closing row, no blank line |
| Callout inside a list | Move the callout outside the list |
| Raw LaTeX or HTML | Remove `\newpage`, `<div>`, etc. — the template handles layout |
| `include-before` missing | Add the full `\begin{lstlisting}[style=coverasciiart]` block to frontmatter |
| ASCII art too wide | Count characters — hard limit is 60 wide for cover art, 82 for inline |
: Common authoring mistakes
