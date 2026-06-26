#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Markset — PDF Build Script
# Converts Markdown to PDF using Pandoc + Tectonic with custom template.
# All paths are relative to the skill folder — no system installs required.
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Detect architecture
ARCH=$(uname -m)

# Resolve binaries: prefer system install on PATH, fall back to skill-local bin/<tool>-<arch>.
resolve_bin() {
  local tool="$1"
  if command -v "$tool" >/dev/null 2>&1; then
    command -v "$tool"
  elif [ -x "$SKILL_DIR/bin/${tool}-${ARCH}" ]; then
    echo "$SKILL_DIR/bin/${tool}-${ARCH}"
  else
    echo ""
  fi
}

PANDOC="$(resolve_bin pandoc)"
TECTONIC="$(resolve_bin tectonic)"

# Template + filter paths
TEMPLATE="$SKILL_DIR/templates/template.tex"
THEME_FILTER="$SKILL_DIR/templates/apply-theme.lua"
DIVS_FILTER="$SKILL_DIR/templates/divs.lua"
DEFAULT_THEME="$SKILL_DIR/themes/presets/default.yaml"

# Font dir (always skill-local)
export OSFONTDIR="$SKILL_DIR/templates/fonts/"

# Cache: use skill-local cache/ only if it exists; otherwise let Tectonic use its default user cache.
if [ -d "$SKILL_DIR/cache" ]; then
  export TECTONIC_CACHE_DIR="$SKILL_DIR/cache/"
fi

# =============================================================================
# Arguments
# =============================================================================

# Parse args: support --theme <path> anywhere, otherwise positional [input] [output].
THEME=""
POSITIONAL=()
while [ $# -gt 0 ]; do
  case "$1" in
    --theme)
      if [ -z "${2:-}" ]; then
        echo "Error: --theme requires a path argument." >&2
        exit 1
      fi
      THEME="$2"
      shift 2
      ;;
    --theme=*)
      THEME="${1#--theme=}"
      shift
      ;;
    -h|--help)
      cat <<EOF
Usage: build-pdf.sh [--theme <path>] <input.md> [output.pdf]

  --theme <path>   Theme YAML. Default search order:
                     1. --theme flag
                     2. ./theme.yaml next to the input file
                     3. themes/presets/default.yaml (bundled)
EOF
      exit 0
      ;;
    *)
      POSITIONAL+=("$1")
      shift
      ;;
  esac
done
set -- "${POSITIONAL[@]}"

if [ $# -lt 1 ]; then
  echo "Usage: build-pdf.sh [--theme <path>] <input.md> [output.pdf]" >&2
  exit 1
fi

INPUT="$1"

if [ -n "${2:-}" ]; then
  OUTPUT="$2"
else
  BASENAME="$(basename "$INPUT" .md)"
  OUTPUT="$(dirname "$INPUT")/../build/${BASENAME}.pdf"
fi

# Theme resolution: --theme > ./theme.yaml next to input > bundled default.
if [ -z "$THEME" ]; then
  CANDIDATE="$(dirname "$INPUT")/theme.yaml"
  if [ -f "$CANDIDATE" ]; then
    THEME="$CANDIDATE"
  else
    THEME="$DEFAULT_THEME"
  fi
fi

# =============================================================================
# Validation
# =============================================================================

if [ -z "$PANDOC" ] || [ ! -x "$PANDOC" ]; then
  echo "Error: pandoc not found. Install via 'brew install pandoc' or drop bin/pandoc-${ARCH} in the skill folder."
  exit 1
fi

if [ -z "$TECTONIC" ] || [ ! -x "$TECTONIC" ]; then
  echo "Error: tectonic not found. Install via 'brew install tectonic' or drop bin/tectonic-${ARCH} in the skill folder."
  exit 1
fi

if [ ! -f "$TEMPLATE" ]; then
  echo "Error: LaTeX template not found at $TEMPLATE"
  exit 1
fi

if [ ! -f "$THEME_FILTER" ]; then
  echo "Error: Theme filter not found at $THEME_FILTER" >&2
  exit 1
fi

if [ ! -f "$DIVS_FILTER" ]; then
  echo "Error: Divs filter not found at $DIVS_FILTER" >&2
  exit 1
fi

if [ ! -f "$THEME" ]; then
  echo "Error: Theme file not found at $THEME" >&2
  exit 1
fi

if [ ! -f "$INPUT" ]; then
  echo "Error: Input file not found at $INPUT" >&2
  exit 1
fi

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT")"

# Pandoc 3.x requires --pdf-engine to be an engine name, not a path.
# Expose the arch-specific tectonic binary as 'tectonic' on PATH.
TMPBIN="$(mktemp -d)"
trap 'rm -rf "$TMPBIN"' EXIT
ln -s "$TECTONIC" "$TMPBIN/tectonic"
export PATH="$TMPBIN:$PATH"

# =============================================================================
# Build
# =============================================================================

"$PANDOC" "$INPUT" \
  -o "$OUTPUT" \
  --pdf-engine=tectonic \
  --template="$TEMPLATE" \
  --metadata-file="$THEME" \
  --lua-filter="$THEME_FILTER" \
  --lua-filter="$DIVS_FILTER" \
  -V fontdir="$SKILL_DIR/templates/fonts" \
  --resource-path="$(dirname "$INPUT"):." \
  --toc \
  --toc-depth=3 \
  --number-sections \
  --listings \
  -V colorlinks=true

echo "PDF generated → $OUTPUT  (theme: $(basename "$THEME"))"
