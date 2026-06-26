"""
Bajaj DCX research-agents — chart style.

Single source of truth for chart palette + matplotlib rcparams. Every chart
function in charts.py calls apply() before plotting so the output matches the
markset PDF visual language.

Palette: neutral grays + one accent (#ff6600, matching markset default).
Discipline: no gridlines unless data demands them, no 3D, no shadows.
"""

import matplotlib as mpl

ACCENT = "#ff6600"  # matches markset themes/presets/default.yaml palette.accent.primary
TEXT   = "#1a1a1a"
MUTED  = "#6b6b6b"
FAINT  = "#d0d0d0"
BG     = "#ffffff"

# Used by multi-category pies/bars; accent kept for emphasis on the most-important value
NEUTRAL_SEQ = [TEXT, MUTED, FAINT]


def apply():
    """Apply the project chart style to matplotlib globally."""
    mpl.rcParams.update({
        "figure.facecolor": BG,
        "axes.facecolor":   BG,
        "savefig.facecolor":BG,

        "font.family":      "sans-serif",
        "font.sans-serif":  ["Inter", "Helvetica", "Arial", "DejaVu Sans"],
        "font.size":        10,
        "axes.titlesize":   12,
        "axes.titleweight": "bold",
        "axes.labelsize":   10,
        "axes.titlepad":    14,

        "axes.edgecolor":   MUTED,
        "axes.linewidth":   0.5,
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "axes.grid":         False,

        "xtick.color":      TEXT,
        "ytick.color":      TEXT,
        "xtick.major.size": 0,
        "ytick.major.size": 0,

        "text.color":       TEXT,
        "patch.edgecolor":  "none",

        "figure.dpi":  100,
        "savefig.dpi": 200,
    })
