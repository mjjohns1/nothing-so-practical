"""
Two-panel figure: confounded vs. adjusted SAT score comparison.

Left panel:  Naive comparison (prep vs. no prep) — big gap, confounded.
Right panel: Adjusted comparison (stratified by income tercile) — smaller,
             real effect visible.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
from pathlib import Path

from gen_sat_data import simulate_sat

OUT = (
    Path(__file__).parent.parent.parent
    / "static/img/posts/do-calculus/confounded-vs-adjusted.svg"
)

BLUE = "#2C4A7A"
RED = "#7A2A35"
GRAY = "#9E9E9E"
LIGHT_BLUE = "#A8C4E0"
LIGHT_RED = "#D4A0A8"
DARK_GRAY = "#333333"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "none",
    "axes.facecolor": "none",
})


def make_violin(ax, positions, datasets, colors, edge_colors):
    parts = ax.violinplot(datasets, positions=positions,
                          showmeans=False, showextrema=False,
                          widths=0.45)
    for body, fc, ec in zip(parts["bodies"], colors, edge_colors):
        body.set_facecolor(fc)
        body.set_edgecolor(ec)
        body.set_alpha(0.7)
        body.set_linewidth(1.3)

    for pos, data, ec in zip(positions, datasets, edge_colors):
        mean = np.mean(data)
        ax.plot(pos, mean, "o", color=ec, markersize=5, zorder=5)
        ax.hlines(mean, pos - 0.15, pos + 0.15, color=ec, lw=1.6, zorder=5)


def main():
    data = simulate_sat()
    sat = data["sat_score"]
    prep = data["prep_course"]
    income = data["family_income"]

    treated = prep == 1
    control = prep == 0

    # --- Figure ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2),
                                    sharey=True,
                                    gridspec_kw={"width_ratios": [1, 1.8]})

    # Left panel: naive comparison
    make_violin(ax1, [0, 1],
                [sat[control], sat[treated]],
                [LIGHT_RED, LIGHT_BLUE],
                [RED, BLUE])

    naive_diff = sat[treated].mean() - sat[control].mean()
    mean_c = sat[control].mean()
    mean_t = sat[treated].mean()

    ax1.annotate("", xy=(1.38, mean_t), xytext=(1.38, mean_c),
                 arrowprops=dict(arrowstyle="<->", color=DARK_GRAY, lw=1.5))
    ax1.text(1.50, (mean_c + mean_t) / 2, f"+{naive_diff:.0f}\npts",
             ha="left", va="center", fontsize=10,
             color=DARK_GRAY, fontweight="semibold")

    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(["No Prep", "Prep"], fontsize=10)
    ax1.set_ylabel("SAT Score", labelpad=8)
    ax1.set_title("Naive Comparison", fontsize=12,
                   fontweight="semibold", pad=10, color="#212121")
    ax1.set_xlim(-0.6, 1.9)
    ax1.spines["bottom"].set_color(GRAY)
    ax1.spines["left"].set_color(GRAY)

    # Right panel: stratified by income tercile
    inc_terciles = np.percentile(income, [33.3, 66.7])
    inc_labels = ["Low\nIncome", "Mid\nIncome", "High\nIncome"]
    inc_groups = np.digitize(income, inc_terciles)

    positions = []
    datasets = []
    colors = []
    edge_colors = []
    strata_diffs = []

    for g in range(3):
        mask = inc_groups == g
        y_ctrl = sat[mask & control]
        y_treat = sat[mask & treated]

        base = g * 1.3
        positions.extend([base, base + 0.55])
        datasets.extend([y_ctrl, y_treat])
        colors.extend([LIGHT_RED, LIGHT_BLUE])
        edge_colors.extend([RED, BLUE])

        if len(y_ctrl) > 0 and len(y_treat) > 0:
            strata_diffs.append(y_treat.mean() - y_ctrl.mean())

    make_violin(ax2, positions, datasets, colors, edge_colors)

    # Group labels
    trans = ax2.get_xaxis_transform()
    for g in range(3):
        base = g * 1.3
        cx = base + 0.275
        ax2.annotate(inc_labels[g], xy=(cx, -0.08), xycoords=trans,
                     ha="center", va="top", fontsize=9.5,
                     color="#555555", fontweight="semibold")
        ax2.annotate("", xy=(base - 0.15, -0.03),
                     xytext=(base + 0.70, -0.03),
                     xycoords=trans, textcoords=trans,
                     arrowprops=dict(arrowstyle="-", color="#AAAAAA", lw=1))

    adj_diff = np.mean(strata_diffs)
    ax2.text(0.98, 0.95,
             f"Avg. within-stratum\ndifference: +{adj_diff:.0f} pts",
             transform=ax2.transAxes, ha="right", va="top",
             fontsize=10, color=DARK_GRAY, fontweight="semibold",
             bbox=dict(boxstyle="round,pad=0.4", fc="white",
                       ec="#CCCCCC", alpha=0.9))

    ax2.set_xticks(positions)
    ax2.set_xticklabels(["No\nPrep", "Prep"] * 3, fontsize=8.5)
    ax2.set_title("Adjusted for Income", fontsize=12,
                   fontweight="semibold", pad=10, color="#212121")
    ax2.set_xlim(-0.5, 3.5)
    ax2.spines["bottom"].set_color(GRAY)
    ax2.spines["left"].set_color(GRAY)

    # Legend
    legend_handles = [
        Patch(facecolor=LIGHT_RED, edgecolor=RED, label="No Prep Course"),
        Patch(facecolor=LIGHT_BLUE, edgecolor=BLUE, label="Prep Course"),
    ]
    ax2.legend(handles=legend_handles, fontsize=9, framealpha=0.85,
               edgecolor="#BDBDBD", loc="upper left")

    plt.tight_layout()
    fig.savefig(OUT, format="svg", bbox_inches="tight")
    print(f"Saved -> {OUT}")
    plt.close(fig)


if __name__ == "__main__":
    main()
