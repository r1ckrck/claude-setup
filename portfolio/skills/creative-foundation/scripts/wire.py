#!/usr/bin/env python3
"""creative-foundation wiring helper.

Two jobs, both idempotent and stdlib-only:

  scaffold  create the foundation/ folder and its numbered document skeletons
            (heading-only stubs). Never overwrites a file that already exists, so
            authored content is safe across re-runs.

  wire      regenerate one delimited block in CLAUDE.md that links every
            foundation document, so the router always points at the current set.
            Content outside the markers is left untouched; if CLAUDE.md is absent
            a minimal router is created. Running it twice yields an identical file.

    python3 .claude/skills/creative-foundation/scripts/wire.py scaffold [--foundation <dir>]
    python3 .claude/skills/creative-foundation/scripts/wire.py wire [--foundation <dir>] [--claude <path>]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

MARK_START = "<!-- creative-foundation:start -->"
MARK_END = "<!-- creative-foundation:end -->"
DEFERRED_RE = re.compile(r"^\s*>\s*Deferred\b\s*[—:-]?\s*(.*)$")

# filename -> (H1 title, [section headings])
DOCS = [
    ("00-brief.md", "Brief",
     ["Audience", "Intent", "Goals", "Success criteria", "Scope", "Constraints", "Vision"]),
    ("01-positioning.md", "Positioning",
     ["Statement", "Best-fit audience", "Competitive alternatives", "Differentiators",
      "Value & proof", "Frame of reference", "Anti-positioning"]),
    ("02-narrative.md", "Narrative",
     ["Hook", "Throughline", "Arc", "Stakes", "Proof beats", "Ordering"]),
    ("03-content-plan.md", "Content plan",
     ["Information architecture", "Voice", "Project-display rules"]),
    ("04-brand.md", "Brand",
     ["Brand statement", "Attributes", "Personality & archetype", "Art direction",
      "What to avoid"]),
    ("05-concept.md", "Concept",
     ["Direction", "How it works", "Why it fits", "What it gates", "Status"]),
    ("06-design-principles.md", "Design principles",
     ["Principles", "Using them"]),
    ("07-design-system.md", "Design system",
     ["Typography", "Color", "Motion", "Components", "Layout & spacing"]),
    ("08-tech-stack.md", "Tech stack",
     ["Constraints", "Rendering", "Framework", "Language", "Content", "Backend",
      "Hosting", "Styling", "Components", "Motion"]),
]


def read_text(path):
    p = Path(path)
    return p.read_text() if p.exists() else None


def write_text(path, data):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(data)


def foundation_dir(args):
    base = args.foundation or os.environ.get("CREATIVE_FOUNDATION") or "./foundation"
    return Path(base)


def stub(title, sections):
    body = "\n\n".join("## " + s for s in sections)
    return "# " + title + "\n\n" + body + "\n"


def cmd_scaffold(args):
    fdir = foundation_dir(args)
    created, skipped = [], []
    for name, title, sections in DOCS:
        path = fdir / name
        if path.exists():
            skipped.append(name)
            continue
        write_text(path, stub(title, sections))
        created.append(name)
    print(json.dumps({"foundation": str(fdir), "created": created, "skipped": skipped}, indent=2))


def doc_title(text, fallback):
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def doc_description(text):
    seen_h1 = False
    para = []
    for line in text.splitlines():
        s = line.strip()
        if not seen_h1:
            if s.startswith("# "):
                seen_h1 = True
            continue
        if DEFERRED_RE.match(line):
            continue
        if not para:
            if not s or s.startswith("#"):
                continue
            para.append(s)
        elif not s or s.startswith("#"):
            break
        else:
            para.append(s)
    return " ".join(para)


def doc_deferrals(text):
    out = []
    for line in text.splitlines():
        m = DEFERRED_RE.match(line)
        if m:
            out.append(m.group(1).strip())
    return out


def build_block(fdir):
    rows, threads = [], []
    if fdir.exists():
        for path in sorted(fdir.glob("*.md")):
            text = path.read_text()
            title = doc_title(text, path.stem)
            rel = os.path.join(fdir.name, path.name)
            rows.append("| [{}]({}) | {} |".format(title, rel, doc_description(text)))
            for reason in doc_deferrals(text):
                threads.append("- **{}** — {}".format(title, reason) if reason else "- **{}**".format(title))
    table = "| Document | What it defines |\n|---|---|\n" + "\n".join(rows) if rows else \
            "_No foundation documents yet. Run the creative-foundation skill._"
    block = ("## Foundation\n\n"
             "The portfolio's foundation. Re-run the creative-foundation skill to refresh this list.\n\n"
             + table)
    if threads:
        block += "\n\n### Open threads\n\n" + "\n".join(threads)
    return block


def cmd_wire(args):
    fdir = foundation_dir(args)
    claude = Path(args.claude or "./CLAUDE.md")
    block = build_block(fdir)
    region = MARK_START + "\n" + block + "\n" + MARK_END

    text = read_text(claude)
    if text is None:
        title = "# " + (claude.resolve().parent.name or "Project")
        result = title + "\n\n" + region + "\n"
    elif MARK_START in text and MARK_END in text:
        pre = text[:text.index(MARK_START)]
        post = text[text.index(MARK_END) + len(MARK_END):]
        result = pre + region + post
    else:
        result = text.rstrip() + "\n\n" + region + "\n"

    write_text(claude, result)
    print(json.dumps({"claude": str(claude), "documents": len(sorted(fdir.glob('*.md')) if fdir.exists() else [])}, indent=2))


def build_parser():
    p = argparse.ArgumentParser(description="creative-foundation wiring helper.")
    p.add_argument("--foundation", default=None,
                   help="foundation folder (default ./foundation or $CREATIVE_FOUNDATION)")
    sub = p.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--foundation", default=argparse.SUPPRESS,
                        help="foundation folder (default ./foundation or $CREATIVE_FOUNDATION)")

    sp = sub.add_parser("scaffold", parents=[common],
                        help="create the foundation folder and document skeletons")
    sp.set_defaults(func=cmd_scaffold)

    sp = sub.add_parser("wire", parents=[common], help="sync the foundation block in CLAUDE.md")
    sp.add_argument("--claude", help="path to CLAUDE.md (default ./CLAUDE.md)")
    sp.set_defaults(func=cmd_wire)

    return p


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
