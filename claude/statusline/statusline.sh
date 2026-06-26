#!/bin/bash
# Native Claude Code statusline.
# Line 1 (identity): [Model pill] [CWD pill] [Git arrow segment]
# Line 2 (metrics):  cache · ctx · 5h · 7d · api · cost  (thin │ separators)
# Uses ANSI 16 so the VS Code terminal palette applies.
set -u
export LC_ALL=en_US.UTF-8

input=$(cat)

IFS=$'\x1f' read -r model model_id cwd cost api_ms p5h r5h p7d r7d ctx_pct cu_in cu_cr cu_cc effort <<<"$(printf '%s' "$input" | jq -r '[
  (.model.display_name // .model.id // "?"),
  (.model.id // ""),
  (.workspace.current_dir // .cwd // "."),
  ((.cost.total_cost_usd // 0) | tostring),
  ((.cost.total_api_duration_ms // 0) | tostring),
  ((.rate_limits.five_hour.used_percentage // "") | tostring),
  ((.rate_limits.five_hour.resets_at // "") | tostring),
  ((.rate_limits.seven_day.used_percentage // "") | tostring),
  ((.rate_limits.seven_day.resets_at // "") | tostring),
  ((.context_window.used_percentage // "") | tostring),
  ((.context_window.current_usage.input_tokens // 0) | tostring),
  ((.context_window.current_usage.cache_read_input_tokens // 0) | tostring),
  ((.context_window.current_usage.cache_creation_input_tokens // 0) | tostring),
  (.effort.level // "")
] | join("\u001f")')"

# Context % — straight from the payload (authoritative); strip any fraction.
ctx_pct=${ctx_pct%.*}

# Cache hit rate — share of the last turn's input tokens served from cache.
cache_pct=""
total=$((cu_in + cu_cr + cu_cc))
if [ "$total" -gt 0 ]; then
  cache_pct=$((cu_cr * 100 / total))
fi

# Git info.
branch=""; dirty=""; ahead=0; behind=0; age=""
if git -C "$cwd" rev-parse --git-dir >/dev/null 2>&1; then
  branch=$(git -C "$cwd" symbolic-ref --short HEAD 2>/dev/null || git -C "$cwd" rev-parse --short HEAD 2>/dev/null)
  if ! git -C "$cwd" diff --quiet --ignore-submodules 2>/dev/null \
     || ! git -C "$cwd" diff --cached --quiet --ignore-submodules 2>/dev/null; then
    dirty="1"
  fi
  if ab=$(git -C "$cwd" rev-list --left-right --count '@{u}'...HEAD 2>/dev/null); then
    behind=$(printf '%s' "$ab" | awk '{print $1}')
    ahead=$(printf '%s' "$ab" | awk '{print $2}')
  fi
  age=$(git -C "$cwd" log -1 --format=%cr 2>/dev/null)
fi

short_cwd="${cwd/#$HOME/~}"

# Effort level — from the payload; fall back to settings.json if absent.
if [ -z "$effort" ]; then
  settings_path="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/settings.json"
  if [ -f "$settings_path" ]; then
    effort=$(jq -r '.effortLevel // empty' "$settings_path" 2>/dev/null)
  fi
fi

# ── Helpers ─────────────────────────────────────────────────
fmt_dur() {
  local ms=${1:-0}; local s=$((ms / 1000))
  if   [ "$s" -lt 60 ];   then printf '%ds' "$s"
  elif [ "$s" -lt 3600 ]; then printf '%dm %ds' $((s/60)) $((s%60))
  else                         printf '%dh %dm' $((s/3600)) $(((s%3600)/60))
  fi
}
fmt_left() {
  local s=${1:-0}
  [ "$s" -le 0 ] && return 1
  if   [ "$s" -lt 3600 ];  then printf '%dm' $((s/60))
  elif [ "$s" -lt 86400 ]; then printf '%dh %dm' $((s/3600)) $(((s%3600)/60))
  else                          printf '%dd %dh' $((s/86400)) $(((s%86400)/3600))
  fi
}
bar() {
  local pct=${1%.*}; local width=10
  [ -z "$pct" ] && pct=0
  [ "$pct" -gt 100 ] && pct=100
  [ "$pct" -lt 0 ] && pct=0
  local filled=$((pct * width / 100)) empty
  empty=$((width - filled))
  local b="" i
  for ((i=0; i<filled; i++)); do b+="█"; done
  b+=$'\033[90m'
  for ((i=0; i<empty;  i++)); do b+="░"; done
  printf '%s' "$b"
}
pct_fg() {
  local p=${1%.*}
  [ -z "$p" ] && p=0
  if   [ "$p" -lt 50 ]; then printf '32'
  elif [ "$p" -lt 75 ]; then printf '33'
  elif [ "$p" -lt 90 ]; then printf '91'
  else                       printf '1;31'
  fi
}

# Cache hit rate uses reversed polarity — higher = better.
cache_fg() {
  local p=${1%.*}
  [ -z "$p" ] && p=0
  if   [ "$p" -lt 40 ]; then printf '91'    # bright red — bad
  elif [ "$p" -lt 70 ]; then printf '33'    # yellow — mediocre
  else                       printf '32'    # green — good
  fi
}

# Powerline glyphs (raw UTF-8).
PL_ARROW=$(printf '\xee\x82\xb0')   #  right-solid
PL_LHC=$(printf '\xee\x82\xb6')     #  left half circle solid
PL_RHC=$(printf '\xee\x82\xb4')     #  right half circle solid

# Nerd Font icons (raw UTF-8).
ICO_MODEL=$(printf '\xf3\xb0\x9a\xa9')     # nf-md-robot U+F06A9
ICO_FOLDER=$(printf '\xef\x81\xbb')        # nf-fa-folder
ICO_BRANCH=$(printf '\xef\x84\xa6')        # nf-fa-code_fork
ICO_BOLT=$(printf '\xef\x83\xa7')          # nf-fa-bolt
ICO_BRAIN=$(printf '\xf3\xb0\x9a\x8b')     # nf-md-brain U+F068B
ICO_STOPWATCH=$(printf '\xef\x8b\xb2')     # nf-fa-stopwatch
ICO_CAL=$(printf '\xef\x81\xb3')           # nf-fa-calendar
ICO_HOURGLASS=$(printf '\xef\x89\x92')     # nf-fa-hourglass

# Color helpers.
C()   { printf '\033[%sm' "$1"; }
R()   { printf '\033[0m'; }
DIM=90
FG=37

# Pill: rounded end-caps on both sides, solid bg between.
#   $1 bg code (40-47 or 100-107)   $2 fg code   $3 text
pill() {
  local bg=$1 fg=$2 text=$3
  local cap=$((bg - 10))
  printf '\033[%sm%s' "$cap" "$PL_LHC"
  printf '\033[%sm\033[%sm %s \033[0m' "$bg" "$fg" "$text"
  printf '\033[%sm%s\033[0m' "$cap" "$PL_RHC"
}

# Open a pill that will be chained into another (rounded left, flat right).
pill_open() {
  local bg=$1 fg=$2 text=$3
  local cap=$((bg - 10))
  printf '\033[%sm%s' "$cap" "$PL_LHC"
  printf '\033[%sm\033[%sm %s ' "$bg" "$fg" "$text"
}
# Join into the next pill.
pill_join() {
  local prev_bg=$1 next_bg=$2 next_fg=$3 text=$4
  printf '\033[%sm \033[%sm\033[%sm %s ' "$prev_bg" "$next_bg" "$next_fg" "$text"
}
# Close a chained pill (rounded right cap).
pill_close() {
  local bg=$1
  local cap=$((bg - 10))
  printf '\033[%sm\033[%sm%s\033[0m' "$bg" "$cap" "$PL_RHC"
}

# Arrow segment: square left edge, right-arrow tip. For git "state flag".
#   $1 bg   $2 fg (may be "1;97" etc.)   $3 text
arrow_seg() {
  local bg=$1 fg=$2 text=$3
  local tip=$((bg - 10))
  printf '\033[%sm\033[%sm %s \033[0m' "$bg" "$fg" "$text"
  printf '\033[%sm%s\033[0m' "$tip" "$PL_ARROW"
}

# Open a chained arrow segment (no trailing tip — for chaining into the next).
seg_open()  {
  local bg=$1 fg=$2 text=$3
  printf '\033[%sm\033[%sm %s ' "$bg" "$fg" "$text"
}
# Transition arrow between two chained segments: previous bg → next bg.
seg_join()  {
  local from_bg=$1 to_bg=$2
  local from_fg=$((from_bg - 10))
  printf '\033[%sm\033[%sm%s' "$to_bg" "$from_fg" "$PL_ARROW"
}
# Final arrow tip on default bg after a chained segment.
seg_close() {
  local from_bg=$1
  local from_fg=$((from_bg - 10))
  printf '\033[0m\033[%sm%s\033[0m' "$from_fg" "$PL_ARROW"
}

# ── Line 1 — identity band ──────────────────────────────────
out=""
# Model pill bg color by family (pastel ANSI, respects theme palette).
model_lc=$(printf '%s' "$model_id$model" | tr '[:upper:]' '[:lower:]')
case "$model_lc" in
  *opus*)   model_bg=45 ;;   # magenta (violet pastel) #b0a0d4
  *sonnet*) model_bg=44 ;;   # blue pastel             #8fadcc
  *haiku*)  model_bg=42 ;;   # green pastel            #a3bf8f
  *)        model_bg=45 ;;   # fallback: violet
esac
# Effort pill colors.
effort_bg=""; effort_fg=""; effort_label=""
case "$effort" in
  low)    effort_bg=100; effort_fg=37;     effort_label="low"    ;;  # grey / dim white
  medium) effort_bg=46;  effort_fg="1;97"; effort_label="medium" ;;  # cyan / bright white
  high)   effort_bg=43;  effort_fg="1;30"; effort_label="high"   ;;  # yellow / bold black
  xhigh)  effort_bg=103; effort_fg="1;30"; effort_label="xhigh"  ;;  # bright yellow / bold black
  max)    effort_bg=41;  effort_fg="1;97"; effort_label="✦ max"  ;;  # red / bold white + marker
esac

if [ -n "$effort_label" ]; then
  out+=$(pill_open "$model_bg" "1;97" "$ICO_MODEL $model")
  out+=$(pill_join "$model_bg" "$effort_bg" "$effort_fg" "$effort_label")
  out+=$(pill_close "$effort_bg")
else
  out+=$(pill "$model_bg" "1;97" "$ICO_MODEL $model")
fi
out+=" "

# CWD + Git form a single arrow chain (blue family — same hue, different shades).
CWD_BG=44    # blue #8fadcc
out+=$(seg_open "$CWD_BG" 97 "$ICO_FOLDER $short_cwd")

if [ -n "$branch" ]; then
  if [ -n "$dirty" ]; then
    git_bg=41;  git_fg="1;97"            # red alert
  else
    git_bg=104; git_fg=97                # bright blue #a3c0db — lighter shade
  fi
  git_text="$ICO_BRANCH $branch"
  [ "$ahead"  -gt 0 ] && git_text+=" ↑$ahead"
  [ "$behind" -gt 0 ] && git_text+=" ↓$behind"
  [ -n "$age" ]       && git_text+=" · $age"
  out+=$(seg_join "$CWD_BG" "$git_bg")
  out+=$(seg_open "$git_bg" "$git_fg" "$git_text")
  out+=$(seg_close "$git_bg")
else
  out+=$(seg_close "$CWD_BG")
fi
printf '%s\n\xc2\xa0\n' "$out"

# ── Line 2 — metrics band ───────────────────────────────────
SEP=" $(C $DIM)│$(R) "
out=""; first=1
add() { [ -z "$first" ] && out+="$SEP"; out+="$1"; first=""; }

if [ -n "$cache_pct" ]; then
  add "$(C $DIM)$ICO_BOLT cache$(R) $(C "$(cache_fg "$cache_pct")")${cache_pct}%$(R)"
fi
if [ -n "$ctx_pct" ]; then
  col=$(pct_fg "$ctx_pct")
  add "$(C $DIM)$ICO_BRAIN ctx$(R) $(C "$col")$(bar "$ctx_pct")$(R) $(C "$col")${ctx_pct}%$(R)"
fi
if [ -n "$p5h" ]; then
  p=${p5h%.*}; col=$(pct_fg "$p")
  seg="$(C $DIM)$ICO_STOPWATCH 5h$(R) $(C "$col")$(bar "$p")$(R) $(C "$col")${p}%$(R)"
  if [ -n "$r5h" ] && [ "$r5h" != "0" ]; then
    left=$(($(printf '%s' "$r5h" | awk '{printf "%d", $1}') - $(date +%s)))
    if left_fmt=$(fmt_left "$left"); then
      seg+=" $(C $DIM)↻ ${left_fmt}$(R)"
    fi
  fi
  add "$seg"
fi
if [ -n "$p7d" ]; then
  p=${p7d%.*}; col=$(pct_fg "$p")
  seg="$(C $DIM)$ICO_CAL 7d$(R) $(C "$col")${p}%$(R)"
  if [ -n "$r7d" ] && [ "$r7d" != "0" ]; then
    left=$(($(printf '%s' "$r7d" | awk '{printf "%d", $1}') - $(date +%s)))
    if left_fmt=$(fmt_left "$left"); then
      seg+=" $(C $DIM)↻ ${left_fmt}$(R)"
    fi
  fi
  add "$seg"
fi
if [ "${api_ms:-0}" -gt 0 ]; then
  add "$(C $DIM)$ICO_HOURGLASS api$(R) $(C $FG)$(fmt_dur "$api_ms")$(R)"
fi
cost_fmt=$(printf '%.2f' "$cost" 2>/dev/null || printf '%s' "$cost")
add "$(C $DIM)\$$(R) $(C $FG)$cost_fmt$(R)"

printf '%s' "$out"
