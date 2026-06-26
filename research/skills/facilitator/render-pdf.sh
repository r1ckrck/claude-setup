#!/usr/bin/env bash
# render-pdf.sh — print the processed report HTML to PDF via headless Chrome.
#
# Usage:
#   .claude/skills/facilitator/render-pdf.sh <run-folder> <stem>
#
# Example:
#   .claude/skills/facilitator/render-pdf.sh \
#     reports/2026-06-01_concept_terranova-ask-ai \
#     2026-06-01_concept_terranova-ask-ai
#
# Behaviour:
#   1. Copies facilitator/report-style.css → <run>/artifacts/report-style.css
#      (so the run folder stays self-contained even if the skill changes).
#   2. Starts python3 -m http.server on a free port, serving <run>/artifacts/.
#   3. Drives playwright-cli: open the HTML, print to PDF at
#      <run>/<stem>_report.pdf, close the page.
#   4. Tears the server down on exit (incl. errors / Ctrl-C).
#
# Requirements:
#   - playwright-cli on PATH (we use the `open`, `pdf`, `close` verbs)
#   - python3 on PATH
#   - <run>/artifacts/<stem>_report.html must already exist

set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <run-folder> <stem>" >&2
  exit 2
fi

RUN="$1"
STEM="$2"

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ART="$RUN/artifacts"
HTML="$ART/${STEM}_report.html"
PDF="$RUN/${STEM}_report.pdf"
CSS_SRC="$SKILL_DIR/report-style.css"
CSS_DST="$ART/report-style.css"

if [[ ! -f "$HTML" ]]; then
  echo "error: HTML not found: $HTML" >&2
  exit 1
fi
if [[ ! -f "$CSS_SRC" ]]; then
  echo "error: CSS not found: $CSS_SRC" >&2
  exit 1
fi

# 1. Pin a copy of the canonical CSS into the run.
cp "$CSS_SRC" "$CSS_DST"

# 2. Find a free port; start http.server in background serving the run's artifacts/.
PORT="$(python3 -c 'import socket;s=socket.socket();s.bind(("",0));print(s.getsockname()[1]);s.close()')"
python3 -m http.server "$PORT" --directory "$ART" >/dev/null 2>&1 &
SERVER_PID=$!

cleanup() {
  if kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  playwright-cli close >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Give the server a moment to bind.
for _ in 1 2 3 4 5; do
  if curl -sf "http://localhost:$PORT/${STEM}_report.html" -o /dev/null; then break; fi
  sleep 0.2
done

# 3. Drive Chrome: open → pdf → close.
playwright-cli open "http://localhost:$PORT/${STEM}_report.html"
playwright-cli pdf --filename="$PDF"
playwright-cli close

echo "wrote $PDF"
