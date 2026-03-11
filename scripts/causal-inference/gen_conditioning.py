import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

OUT = (
    Path(__file__).parent.parent.parent
    / "static/img/posts/causal-inference/conditioning-on-z.svg"
)

BLUE = "#2C4A7A"
RED = "#7A2A35"
GRAY = "#9E9E9E"
LIGHT_BLUE = "#A8C4E0"
LIGHT_RED = "#D4A0A8"

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
                          widths=0.5)
    for body, fc, ec in zip(parts["bodies"], colors, edge_colors):
        body.set_facecolor(fc)
        body.set_edgecolor(ec)
        body.set_alpha(0.7)
        body.set_linewidth(1.3)

    # Mean markers
    for pos, data, ec in zip(positions, datasets, edge_colors):
        mean = np.mean(data)
        ax.plot(pos, mean, "o", color=ec, markersize=6, zorder=5)
        ax.hlines(mean, pos - 0.18, pos + 0.18, color=ec,
                  lw=1.8, zorder=5)


def main():
    rng = np.random.default_rng(42)

    # Confounded data: Z drives both treatment choice and outcome.
    # High-Z women are healthier AND more likely to take HRT.
    n = 400
    z = rng.binomial(1, 0.5, n)

    # Treatment assignment: correlated with Z
    treat_prob = np.where(z == 1, 0.7, 0.3)
    treated = rng.binomial(1, treat_prob)

    # Outcome: depends on Z only, not treatment
    y = rng.normal(loc=3.0 - 2.0 * z, scale=0.7, size=n)

    y_treat = y[treated == 1]
    y_ctrl = y[treated == 0]

    # Within Z strata
    y_z0_treat = y[(z == 0) & (treated == 1)]
    y_z0_ctrl = y[(z == 0) & (treated == 0)]
    y_z1_treat = y[(z == 1) & (treated == 1)]
    y_z1_ctrl = y[(z == 1) & (treated == 0)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 4),
                                   sharey=True,
                                   gridspec_kw={"width_ratios": [1, 1.5]})

    # Left panel: naive comparison
    make_violin(ax1, [0, 1],
                [y_ctrl, y_treat],
                [LIGHT_RED, LIGHT_BLUE],
                [RED, BLUE])

    # Arrow showing naive difference
    mean_ctrl = np.mean(y_ctrl)
    mean_treat = np.mean(y_treat)
    ax1.annotate(
        "", xy=(1.35, mean_treat), xytext=(1.35, mean_ctrl),
        arrowprops=dict(arrowstyle="<->", color="#444444", lw=1.6),
    )
    ax1.text(1.48, (mean_ctrl + mean_treat) / 2, "Treatment\ncontrast",
             ha="left", va="center", fontsize=10,
             color="#444444", style="italic", fontweight="semibold")

    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(["Control\n(X=0)", "Treated\n(X=1)"],
                        fontsize=10)
    ax1.set_ylabel("Outcome  (Y)", labelpad=8)
    ax1.set_title("Naive ATE", fontsize=12,
                  fontweight="semibold", pad=10, color="#212121")
    ax1.set_xlim(-0.6, 1.9)
    ax1.spines["bottom"].set_color(GRAY)
    ax1.spines["left"].set_color(GRAY)

    # Right panel: conditioned on Z
    positions = [0, 0.6, 1.6, 2.2]
    datasets = [y_z0_ctrl, y_z0_treat, y_z1_ctrl, y_z1_treat]
    colors = [LIGHT_RED, LIGHT_BLUE, LIGHT_RED, LIGHT_BLUE]
    edge_colors = [RED, BLUE, RED, BLUE]

    make_violin(ax2, positions, datasets, colors, edge_colors)

    ax2.set_xticks(positions)
    ax2.set_xticklabels(["Ctrl", "Treat", "Ctrl", "Treat"],
                        fontsize=9)
    ax2.set_title("ATE Conditioned on Z", fontsize=12,
                  fontweight="semibold", pad=10, color="#212121")
    ax2.set_xlim(-0.6, 2.8)

    # Group labels below tick labels via curly braces / text
    trans = ax2.get_xaxis_transform()
    for cx, label in [(0.3, "Z = low"), (1.9, "Z = high")]:
        ax2.annotate(
            label, xy=(cx, -0.14), xycoords=trans,
            ha="center", va="top", fontsize=9.5,
            color="#555555", fontweight="semibold",
        )
        # Bracket line
        ax2.annotate(
            "", xy=(cx - 0.32, -0.08), xytext=(cx + 0.32, -0.08),
            xycoords=trans, textcoords=trans,
            arrowprops=dict(arrowstyle="-", color="#AAAAAA", lw=1),
        )
    ax2.spines["bottom"].set_color(GRAY)
    ax2.spines["left"].set_color(GRAY)

    # Legend (shared)
    from matplotlib.patches import Patch
    legend_handles = [
        Patch(facecolor=LIGHT_RED, edgecolor=RED, label="Control (X=0)"),
        Patch(facecolor=LIGHT_BLUE, edgecolor=BLUE, label="Treated (X=1)"),
    ]
    ax2.legend(handles=legend_handles, fontsize=9, framealpha=0.85,
               edgecolor="#BDBDBD", loc="upper right")

    plt.tight_layout()
    fig.savefig(OUT, format="svg", bbox_inches="tight")
    print(f"Saved → {OUT}")
    plt.close(fig)


if __name__ == "__main__":
    main()
