import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from gen_sat_data import simulate_sat, FRONTDOOR_SEED

OUT_DIR = (
    Path(__file__).parent.parent.parent / "static/img/posts/do-calculus"
)

BLUE = "#2C4A7A"
RED = "#7A2A35"
GRAY = "#9E9E9E"
PT_BLUE = "#6B9BD2"
PT_RED = "#C47A85"
DARK_GRAY = "#333333"

PANEL_SIZE = (7.5, 4.8)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 12,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "none",
    "axes.facecolor": "none",
})

_SCATTER_KW = dict(s=14, alpha=0.3, edgecolors="none", rasterized=True)


def _style_spines(*axes):
    for ax in axes:
        for spine in ("bottom", "left"):
            if ax.spines[spine].get_visible():
                ax.spines[spine].set_color(GRAY)


def _downsample(arrays, n_plot=500, seed=99):
    rng = np.random.default_rng(seed)
    n = len(arrays[0])
    idx = rng.choice(n, size=min(n_plot, n), replace=False)
    return tuple(a[idx] for a in arrays)


def _save(fig, name):
    path = OUT_DIR / name
    fig.savefig(path, format="svg", bbox_inches="tight")
    print(f"Saved -> {path}")
    plt.close(fig)


def plot_step1(hours, prep):
    fig, ax = plt.subplots(figsize=PANEL_SIZE)

    h_ctrl = hours[prep == 0]
    h_treat = hours[prep == 1]

    parts = ax.violinplot([h_ctrl, h_treat], positions=[0, 1],
                          showmeans=False, showextrema=False, widths=0.5)
    colors = [PT_RED, PT_BLUE]
    edges = [RED, BLUE]
    for body, fc, ec in zip(parts["bodies"], colors, edges):
        body.set_facecolor(fc)
        body.set_edgecolor(ec)
        body.set_alpha(0.7)
        body.set_linewidth(1.3)

    for pos, d, ec in zip([0, 1], [h_ctrl, h_treat], edges):
        mean = np.mean(d)
        ax.plot(pos, mean, "o", color=ec, markersize=6, zorder=5)
        ax.hlines(mean, pos - 0.15, pos + 0.15, color=ec, lw=1.8, zorder=5)

    diff = h_treat.mean() - h_ctrl.mean()
    ax.text(0.5, 0.95, f"Prep adds ~{diff:.0f} hrs",
            transform=ax.transAxes, ha="center", va="top",
            fontsize=11, color=DARK_GRAY, fontweight="semibold",
            bbox=dict(boxstyle="round,pad=0.35", fc="white",
                      ec="#CCCCCC", alpha=0.9))

    ax.set_xticks([0, 1])
    ax.set_xticklabels(["No Prep", "Prep"])
    ax.set_ylabel("Hours Studied", labelpad=8)
    ax.set_title("Step 1: Prep → Hours", fontweight="semibold",
                 pad=12, color="#212121")
    ax.set_xlim(-0.6, 1.6)

    _style_spines(ax)
    fig.tight_layout()
    _save(fig, "frontdoor-step1.svg")


def plot_step2(hours, sat, prep):
    fig, ax = plt.subplots(figsize=PANEL_SIZE)

    control = prep == 0
    treated = prep == 1

    h_ds_c, s_ds_c = _downsample([hours[control], sat[control]])
    h_ds_t, s_ds_t = _downsample([hours[treated], sat[treated]])

    ax.scatter(h_ds_c, s_ds_c, color=PT_RED, label="No Prep", **_SCATTER_KW)
    ax.scatter(h_ds_t, s_ds_t, color=PT_BLUE, label="Prep", **_SCATTER_KW)

    for h_sub, s_sub, clr in [(hours[control], sat[control], RED),
                              (hours[treated], sat[treated], BLUE)]:
        coeffs = np.polyfit(h_sub, s_sub, 1)
        x_line = np.linspace(h_sub.min(), h_sub.max(), 50)
        ax.plot(x_line, np.polyval(coeffs, x_line), color=clr, lw=2.2)

    ax.set_xlabel("Hours Studied", labelpad=6)
    ax.set_ylabel("SAT Score", labelpad=8)
    ax.set_title("Step 2: Hours → SAT (by group)", fontweight="semibold",
                 pad=12, color="#212121")
    ax.legend(framealpha=0.85, edgecolor="#BDBDBD", loc="upper left")

    _style_spines(ax)
    fig.tight_layout()
    _save(fig, "frontdoor-step2.svg")


def _bootstrap_frontdoor(prep, hours, sat, n_boot=2000, seed=42):
    rng = np.random.default_rng(seed)
    n = len(prep)
    estimates = np.empty(n_boot)

    for i in range(n_boot):
        idx = rng.choice(n, size=n, replace=True)
        p_b, h_b, s_b = prep[idx], hours[idx], sat[idx]
        dh = h_b[p_b == 1].mean() - h_b[p_b == 0].mean()

        slopes = []
        for pval in (0, 1):
            mask = p_b == pval
            if mask.sum() > 10:
                c = np.polyfit(h_b[mask], s_b[mask], 1)
                slopes.append(c[0])
        avg_slope = float(np.mean(slopes)) if slopes else 0.0
        estimates[i] = dh * avg_slope

    return estimates


def plot_step3(prep, hours, sat):
    fig, ax = plt.subplots(figsize=PANEL_SIZE)

    fd = _bootstrap_frontdoor(prep, hours, sat)
    fd_mean = fd.mean()
    naive = sat[prep == 1].mean() - sat[prep == 0].mean()

    ax.hist(fd, bins=40, color=PT_BLUE, edgecolor=BLUE, alpha=0.7,
            density=True)
    ax.axvline(fd_mean, color=BLUE, lw=2.2,
               label=f"Front-door: {fd_mean:.0f}")
    ax.axvline(naive, color=RED, lw=2.2, linestyle="--",
               label=f"Naive: {naive:.0f}")

    ax.set_xlabel("Estimated Causal Effect (pts)", labelpad=6)
    ax.set_ylabel("Density", labelpad=8)
    ax.set_title("Step 3: Chained Estimate vs. Naive",
                 fontweight="semibold", pad=12, color="#212121")
    ax.legend(framealpha=0.85, edgecolor="#BDBDBD", loc="upper center")

    _style_spines(ax)
    fig.tight_layout()
    _save(fig, "frontdoor-step3.svg")


def main():
    data = simulate_sat(frontdoor=True, seed=FRONTDOOR_SEED)
    prep = data["prep_course"]
    hours = data["hours_studied"]
    sat = data["sat_score"]

    plot_step1(hours, prep)
    plot_step2(hours, sat, prep)
    plot_step3(prep, hours, sat)


if __name__ == "__main__":
    main()
