"""
Multi-panel figure showing the front-door estimation.

Panel 1: Prep Course -> Hours Studied (clean relationship)
Panel 2: Hours Studied -> SAT Score (adjusted for Prep Course)
Panel 3: Combined causal effect estimate
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from gen_sat_data import simulate_sat, FRONTDOOR_SEED

OUT = (
    Path(__file__).parent.parent.parent
    / "static/img/posts/do-calculus/frontdoor-estimation.svg"
)

BLUE = "#2C4A7A"
RED = "#7A2A35"
GRAY = "#9E9E9E"
PT_BLUE = "#6B9BD2"
PT_RED = "#C47A85"
DARK_GRAY = "#333333"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "none",
    "axes.facecolor": "none",
})

_SCATTER_KW = dict(s=12, alpha=0.3, edgecolors="none", rasterized=True)


def _style_spines(*axes):
    for ax in axes:
        for spine in ("bottom", "left"):
            if ax.spines[spine].get_visible():
                ax.spines[spine].set_color(GRAY)


def _downsample(arrays, n_plot=400, seed=99):
    rng = np.random.default_rng(seed)
    n = len(arrays[0])
    idx = rng.choice(n, size=min(n_plot, n), replace=False)
    return tuple(a[idx] for a in arrays)


def main():
    data = simulate_sat(frontdoor=True, seed=FRONTDOOR_SEED)
    prep = data["prep_course"]
    hours = data["hours_studied"]
    sat = data["sat_score"]

    treated = prep == 1
    control = prep == 0

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4.5))

    # --- Panel 1: Prep -> Hours (no confounding on this link) ---
    h_ctrl, h_treat = hours[control], hours[treated]

    from matplotlib.patches import Patch
    parts1 = ax1.violinplot([h_ctrl, h_treat], positions=[0, 1],
                             showmeans=False, showextrema=False, widths=0.5)
    colors1 = [PT_RED, PT_BLUE]
    edges1 = [RED, BLUE]
    for body, fc, ec in zip(parts1["bodies"], colors1, edges1):
        body.set_facecolor(fc)
        body.set_edgecolor(ec)
        body.set_alpha(0.7)
        body.set_linewidth(1.3)

    for pos, d, ec in zip([0, 1], [h_ctrl, h_treat], edges1):
        mean = np.mean(d)
        ax1.plot(pos, mean, "o", color=ec, markersize=5, zorder=5)
        ax1.hlines(mean, pos - 0.15, pos + 0.15, color=ec, lw=1.6, zorder=5)

    diff_hours = h_treat.mean() - h_ctrl.mean()
    ax1.text(0.5, 0.95, f"Prep adds ~{diff_hours:.0f} hrs",
             transform=ax1.transAxes, ha="center", va="top",
             fontsize=10, color=DARK_GRAY, fontweight="semibold",
             bbox=dict(boxstyle="round,pad=0.3", fc="white",
                       ec="#CCCCCC", alpha=0.9))

    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(["No Prep", "Prep"], fontsize=10)
    ax1.set_ylabel("Hours Studied", labelpad=8)
    ax1.set_title("Step 1: Prep → Hours", fontsize=11,
                   fontweight="semibold", pad=10, color="#212121")
    ax1.set_xlim(-0.6, 1.6)

    # --- Panel 2: Hours -> SAT Score (within prep strata) ---
    # Show scatter with regression lines within each group
    h_ds_c, s_ds_c = _downsample([hours[control], sat[control]])
    h_ds_t, s_ds_t = _downsample([hours[treated], sat[treated]])

    ax2.scatter(h_ds_c, s_ds_c, color=PT_RED, label="No Prep", **_SCATTER_KW)
    ax2.scatter(h_ds_t, s_ds_t, color=PT_BLUE, label="Prep", **_SCATTER_KW)

    # Regression lines within strata
    for h_sub, s_sub, clr in [(hours[control], sat[control], RED),
                               (hours[treated], sat[treated], BLUE)]:
        coeffs = np.polyfit(h_sub, s_sub, 1)
        x_line = np.linspace(h_sub.min(), h_sub.max(), 50)
        ax2.plot(x_line, np.polyval(coeffs, x_line), color=clr, lw=2)

    ax2.set_xlabel("Hours Studied", labelpad=6)
    ax2.set_ylabel("SAT Score", labelpad=8)
    ax2.set_title("Step 2: Hours → SAT (by group)", fontsize=11,
                   fontweight="semibold", pad=10, color="#212121")
    ax2.legend(fontsize=9, framealpha=0.85, edgecolor="#BDBDBD",
               loc="upper left")

    # --- Panel 3: Combined effect ---
    # Bootstrap the front-door estimate
    rng = np.random.default_rng(42)
    n_boot = 2000
    fd_estimates = []
    n = len(prep)

    for _ in range(n_boot):
        idx = rng.choice(n, size=n, replace=True)
        p_b, h_b, s_b = prep[idx], hours[idx], sat[idx]

        # Step 1: E[Hours | Prep=1] - E[Hours | Prep=0]
        dh = h_b[p_b == 1].mean() - h_b[p_b == 0].mean()

        # Step 2: E[SAT | Hours, Prep] slope (pooled within-stratum)
        # Simple approach: average of within-group slopes
        slopes = []
        for pval in [0, 1]:
            mask = p_b == pval
            if mask.sum() > 10:
                c = np.polyfit(h_b[mask], s_b[mask], 1)
                slopes.append(c[0])
        avg_slope = np.mean(slopes) if slopes else 0

        # Chained effect
        fd_estimates.append(dh * avg_slope)

    fd_estimates = np.array(fd_estimates)
    fd_mean = fd_estimates.mean()
    fd_ci = np.percentile(fd_estimates, [2.5, 97.5])

    # Naive estimate for comparison
    naive = sat[treated].mean() - sat[control].mean()

    ax3.hist(fd_estimates, bins=40, color=PT_BLUE, edgecolor=BLUE,
             alpha=0.7, density=True)
    ax3.axvline(fd_mean, color=BLUE, lw=2, label=f"Front-door: {fd_mean:.0f}")
    ax3.axvline(naive, color=RED, lw=2, linestyle="--",
                label=f"Naive: {naive:.0f}")

    ax3.set_xlabel("Estimated Causal Effect (pts)", labelpad=6)
    ax3.set_ylabel("Density", labelpad=8)
    ax3.set_title("Step 3: Causal Estimate", fontsize=11,
                   fontweight="semibold", pad=10, color="#212121")
    ax3.legend(fontsize=9, framealpha=0.85, edgecolor="#BDBDBD",
               loc="upper right")

    _style_spines(ax1, ax2, ax3)

    plt.tight_layout(w_pad=1.5)
    fig.savefig(OUT, format="svg", bbox_inches="tight")
    print(f"Saved -> {OUT}")
    plt.close(fig)


if __name__ == "__main__":
    main()
