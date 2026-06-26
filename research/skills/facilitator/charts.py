"""
charts.py — render report charts from a stats.json file.

Invocation:
    .venv/bin/python charts.py --stats <stats.json> --out <charts_dir> --test concept

One function per chart type. Each function takes the relevant slice of the
stats dict + an output path stem, and writes both a PDF (vector archive) and
a PNG (for HTML <img> embedding).

Chart inventory by test type lives in CHART_FUNCTIONS at the bottom. To add a
chart for a new test type, write the function and register it there.

would_use_counts and top_affect_words are intentionally NOT charted.
would_use is the same shape as verdict (redundant); affect_words are
preserved as snapshot quotes in prose, not aggregated.
"""

import argparse
import json
import os
import sys
from collections import Counter

import matplotlib.pyplot as plt

from chartstyle import apply, ACCENT, MUTED, FAINT, TEXT

apply()

PNG_DPI = 200


def _save(fig, out_stem):
    """Write <stem>.pdf and <stem>.png from the same figure."""
    fig.savefig(f"{out_stem}.pdf", format="pdf", bbox_inches="tight")
    fig.savefig(f"{out_stem}.png", format="png", bbox_inches="tight", dpi=PNG_DPI)
    plt.close(fig)


# ---------- chart functions ----------------------------------------------------

def verdict_pie(counts, out_stem):
    """3-slice pie: validate / iterate / kill. Accent on the largest slice."""
    labels = ["Validate", "Iterate", "Kill"]
    values = [counts.get("validate", 0), counts.get("iterate", 0), counts.get("kill", 0)]
    base_colors = [FAINT, MUTED, TEXT]
    max_idx = max(range(3), key=lambda i: values[i])
    colors = list(base_colors)
    colors[max_idx] = ACCENT

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.pie(
        values,
        labels=[f"{l}\n{v}" for l, v in zip(labels, values)],
        colors=colors,
        startangle=90,
        textprops={"color": TEXT, "fontsize": 10},
    )
    fig.tight_layout()
    _save(fig, out_stem)


def comprehension_dist(counts, out_stem):
    """Horizontal bar of comprehension levels."""
    labels = ["Correct", "Partial", "Missed"]
    values = [counts.get("correct", 0), counts.get("partial", 0), counts.get("missed", 0)]
    max_val = max(values) if values else 1
    colors = [ACCENT if v == max_val and v > 0 else (MUTED if v > 0 else FAINT) for v in values]

    fig, ax = plt.subplots(figsize=(6, 2.5))
    bars = ax.barh(labels, values, color=colors)
    ax.set_xlim(0, max_val + 1.5)
    ax.invert_yaxis()
    for bar, val in zip(bars, values):
        ax.text(val + 0.15, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", color=TEXT)
    fig.tight_layout()
    _save(fig, out_stem)


def binding_constraints_bar(constraints, out_stem):
    """Aggregate binding constraints by category, horizontal bar."""
    cats = Counter(c["category"] for c in constraints)
    items = sorted(cats.items(), key=lambda x: -x[1])
    labels = [k for k, _ in items]
    values = [v for _, v in items]
    max_val = max(values) if values else 1
    colors = [ACCENT if v == max_val else MUTED for v in values]

    fig, ax = plt.subplots(figsize=(7, 3.5))
    bars = ax.barh(labels, values, color=colors)
    ax.set_xlim(0, max_val + 1.5)
    ax.invert_yaxis()
    for bar, val in zip(bars, values):
        ax.text(val + 0.15, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", color=TEXT)
    fig.tight_layout()
    _save(fig, out_stem)


# ---------- chart inventory per test type -------------------------------------

CHART_FUNCTIONS = {
    "concept": {
        "verdict_pie":             (verdict_pie,             lambda s: s["verdict_counts"]),
        "comprehension_dist":      (comprehension_dist,      lambda s: s["comprehension_counts"]),
        "binding_constraints_bar": (binding_constraints_bar, lambda s: s["binding_constraints"]),
    },
    # first-click, usability, interview: register here as those tests get built
}


# ---------- CLI ---------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Render report charts from stats.json.")
    parser.add_argument("--stats", required=True, help="Path to stats.json")
    parser.add_argument("--out",   required=True, help="Output directory for chart PDFs")
    parser.add_argument("--test",  default=None,
                        help="Test type: concept | first-click | usability | interview "
                             "(defaults to stats.json's test_type)")
    args = parser.parse_args()

    with open(args.stats) as f:
        stats = json.load(f)

    test_type = args.test or stats.get("test_type")
    if not test_type:
        sys.exit("--test required (or set test_type in stats.json)")

    inventory = CHART_FUNCTIONS.get(test_type)
    if inventory is None:
        sys.exit(f"No chart inventory for test type: {test_type}")

    os.makedirs(args.out, exist_ok=True)
    for name, (fn, picker) in inventory.items():
        out_stem = os.path.join(args.out, name)
        fn(picker(stats), out_stem)
        print(f"wrote {out_stem}.pdf + .png")


if __name__ == "__main__":
    main()
