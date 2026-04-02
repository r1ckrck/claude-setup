# claude-setup

A public repository of Claude Code skills, MCP configurations, and automation setups organized by domain. Meant for others to quickly adopt what they need, and as a personal reference.

## Purpose

Each top-level folder is a domain (see `Domains` section). Each folder contains skills, MCP setup, tech stack and supporting references for that domain. Some cross-cutting utilities live at the root.

## Structure

```
claude-setup/
├── .claude/                      # Claude Code setup for this repo
├── WIP/                          # Work in progress skills
├── <domain>/
│   ├── skills/
│   │   └── <skill-name>/
│   │       ├── SKILL.md          # Skill definition (frontmatter + instructions)
│   │       ├── scripts/          # Skill scripts
│   │       └── references/       # Supporting docs, type defs, reference files
│   ├── settings.json             # MCP config + allowed commands (no API keys)
│   └── README.md                 # Domain overview; which skills/MCPs to use and when
├── horizontal/                   # Cross-cutting skills and configs
├── CLAUDE.md                     # Claude Code setup for this repo
└── READEME.md                    # Root-level README
```

## Domains

| Domain | Description |
|---|---|
| `claude` | Claude Code setup, skills, hooks, and configuration |
| `code` | General coding skills and tools |
| `figma` | Figma design, plugin API, design systems |
| `office` | Office document processing (PDF, DOCX, XLSX, PPTX) |
| `image-gen` | AI image generation workflows |
| `research` | Research, summarization, and knowledge extraction |
| `web-design` | Web design skills and tools |
| `horizontal` | Cross-cutting skills and tools |