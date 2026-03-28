import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from scipy.stats import norm

# Paths
OUT_DIR = Path(__file__).parent.parent.parent / "static/img/posts/cuped"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_PATH = OUT_DIR / "cuped_vs_ancova.svg"
FIG_COV_PATH = OUT_DIR / "pre_post_covariation.svg"
FIG_VARRED_PATH = OUT_DIR / "variance_reduction.svg"
FIG_DIST_PATH = OUT_DIR / "tx_effect_distributions.svg"

# Colors
BLUE = "#2C4A7A"
RED = "#7A2A35"
PT_BLUE = "#6B9BD2"
PT_RED = "#C47A85"
GRAY = "#9E9E9E"
DARK_GRAY = "#333333"
MID_GRAY = "#666666"
INDIGO = "#3B3F6E"
PT_INDIGO = "#7A7FB5"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "none",
    "axes.facecolor": "none",
})


# Helpers
def _downsample(arrays, n_plot=750, seed=99):
    """Return downsampled views of arrays for plotting."""

    rng = np.random.default_rng(seed)
    n = len(arrays[0])
    idx = rng.choice(n, size=min(n_plot, n), replace=False)

    return tuple(a[idx] for a in arrays)


_SCATTER_KW = dict(s=16, alpha=0.4, edgecolors="none")
_LEGEND_KW = dict(fontsize=9, framealpha=0.85, edgecolor="#BDBDBD", loc="upper left")


def _style_spines(*axes):
    """Apply consistent spine colors to axes."""

    for ax in axes:
        for spine in ("bottom", "left"):
            if ax.spines[spine].get_visible():
                ax.spines[spine].set_color(GRAY)


def _save_figure(fig, path):
    """Save figure as SVG, print path, and close."""

    fig.savefig(path, format="svg", bbox_inches="tight")
    print(f"Saved figure → {path}")
    plt.close(fig)


# Simulation
def simulate(n=5000, tau=3.0, seed=42):
    """
    Simulate an AB test with a pre-experiment covariate.

    Parameters
    ----------
    n : int
        Users per group.
    tau : float
        True treatment effect (percentage points).
    seed : int
        Random seed.

    Returns
    -------
    dict with arrays: pre, post, treatment (0/1)
    """
    rng = np.random.default_rng(seed)

    # Pre-experiment search rate (%), drawn from a Beta → scaled to [0, 60]
    pre = 60 * rng.beta(2, 5, size=2 * n)

    # Treatment assignment (random)
    treatment = np.concatenate([np.zeros(n), np.ones(n)])
    rng.shuffle(treatment)

    # In-experiment search rate
    slope = 0.6
    intercept = 12.0
    noise = rng.normal(0, 6.0, size=2 * n)
    post = intercept + slope * pre + tau * treatment + noise

    return {"pre": pre, "post": post, "treatment": treatment,
            "true_tau": tau, "true_slope": slope}


# OLS via normal equations
def ols(X, y):
    """Return (coefficients, ss_res, R²) from OLS."""

    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    resid = y - X @ beta
    ss_res = resid @ resid
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot

    return beta, ss_res, r2


# CUPED adjustment
def cuped_adjust(pre, post):
    """
    Return CUPED-adjusted outcome and theta.

    adjusted_i = post_i - theta * (pre_i - mean(pre))
    where theta = cov(post, pre) / var(pre)
    """

    theta = np.cov(post, pre)[0, 1] / np.var(pre, ddof=1)
    adjusted = post - theta * (pre - pre.mean())

    return adjusted, theta


# Compute statistics
def compute_stats(data):
    """Compute all summary statistics from simulated data."""
    pre, post, treat = data["pre"], data["post"], data["treatment"]
    n = len(pre)

    rho = np.corrcoef(pre, post)[0, 1]

    # CUPED
    adjusted, theta = cuped_adjust(pre, post)
    cuped_est = adjusted[treat == 1].mean() - adjusted[treat == 0].mean()

    # ANCOVA
    X = np.column_stack([np.ones(n), treat, pre])
    ancova_beta, ss_res, r2 = ols(X, post)
    sigma2 = ss_res / (n - 3)
    var_beta = sigma2 * np.linalg.inv(X.T @ X)
    se_tau = np.sqrt(var_beta[1, 1])

    # Simple t-test (no covariate)
    X_simple = np.column_stack([np.ones(n), treat])
    beta_s, ss_res_s, _ = ols(X_simple, post)
    sigma2_s = ss_res_s / (n - 2)
    XtX_inv_diag1_s = np.linalg.solve(X_simple.T @ X_simple, np.eye(2))[:, 1]
    se_simple = np.sqrt(sigma2_s * XtX_inv_diag1_s[1])

    return {
        "rho": rho,
        "theta": theta,
        "cuped_est": cuped_est,
        "ancova_beta": ancova_beta,
        "ancova_r2": r2,
        "adjusted": adjusted,
        "se_tau": se_tau,
        "se_simple": se_simple,
        "naive_est": beta_s[1],
    }


def print_stats(data, stats):
    """Print a formatted summary of simulation results."""

    pre, post, treat = data["pre"], data["post"], data["treatment"]
    n = len(pre)
    beta = stats["ancova_beta"]

    print("=" * 60)
    print("SIMULATION SUMMARY")
    print("=" * 60)
    print(f"N total: {n}  (treatment: {int(treat.sum())}, "
          f"control: {int(n - treat.sum())})")
    print(f"True treatment effect: {data['true_tau']:.1f} pp")
    print()

    print(f"Pre-experiment SR:  mean = {pre.mean():.1f}%,  "
          f"sd = {pre.std():.1f}")
    print(f"In-experiment SR:   mean = {post.mean():.1f}%,  "
          f"sd = {post.std():.1f}")
    print()

    rho = stats["rho"]
    print(f"Correlation(pre, post): {rho:.3f}")
    print(f"Variance reduction:     1 - rho^2 = {1 - rho**2:.3f}  "
          f"({rho**2 * 100:.1f}% removed)")
    print()

    print(f"Naive difference in means: {stats['naive_est']:.2f}")
    print()

    print(f"CUPED theta:              {stats['theta']:.4f}")
    print(f"CUPED treatment estimate: {stats['cuped_est']:.2f}")
    print(f"  Var(observed):  {np.var(post, ddof=1):.2f}")
    print(f"  Var(adjusted):  {np.var(stats['adjusted'], ddof=1):.2f}")
    print()

    print(f"ANCOVA regression:  post = {beta[0]:.2f} + "
          f"{beta[1]:.2f}*treat + {beta[2]:.4f}*pre")
    print(f"  Treatment effect (tau): {beta[1]:.2f}")
    print(f"  Pre-experiment coef:    {beta[2]:.4f}")
    print(f"  R²: {stats['ancova_r2']:.3f}")
    print(f"  SE(tau): {stats['se_tau']:.2f}")
    print()

    print(f"Simple t-test estimate:  {stats['naive_est']:.2f}  "
          f"(SE = {stats['se_simple']:.2f})")
    print(f"SE reduction from ANCOVA: "
          f"{(1 - stats['se_tau'] / stats['se_simple']) * 100:.1f}%")
    print("=" * 60)


# Figures
def make_figure(data, stats, n_plot=750):
    pre, post, treat = data["pre"], data["post"], data["treatment"]
    adjusted = stats["adjusted"]
    beta = stats["ancova_beta"]

    pre_p, post_p, treat_p, adj_p = _downsample(
        [pre, post, treat, adjusted], n_plot,
    )

    ctrl_p = treat_p == 0
    tx_p = treat_p == 1
    ctrl = treat == 0
    tx = treat == 1

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(10, 4.5),
        sharey=True, gridspec_kw={"wspace": 0.15},
    )

    # Left panel: ANCOVA
    ax1.scatter(pre_p[ctrl_p], post_p[ctrl_p], color=PT_RED,
                label="Control", **_SCATTER_KW)
    ax1.scatter(pre_p[tx_p], post_p[tx_p], color=PT_BLUE,
                label="Treatment", **_SCATTER_KW)

    # Grand mean vertical line
    xbar = pre.mean()
    ax1.axvline(xbar, color=GRAY, ls="--", lw=1.0, alpha=0.85)
    ax1.text(xbar + 0.8, ax1.get_ylim()[0] + 1, f"Grand mean\n({xbar:.0f}%)",
             fontsize=8, color=MID_GRAY, va="bottom")

    # Regression lines
    x_range = np.array([0, pre.max() + 1])
    ax1.plot(x_range, beta[0] + beta[2] * x_range,
             color=RED, lw=1.8, alpha=0.8)
    ax1.plot(x_range, beta[0] + beta[1] + beta[2] * x_range,
             color=BLUE, lw=1.8, alpha=0.8)

    # Annotate treatment effect
    y_mid_ctrl = beta[0] + beta[2] * xbar
    y_mid_tx = y_mid_ctrl + beta[1]
    ax1.annotate(
        "", xy=(xbar, y_mid_tx), xytext=(xbar, y_mid_ctrl),
        arrowprops=dict(arrowstyle="|-|", color=DARK_GRAY, lw=1.5),
    )
    ax1.text(xbar + 8, (y_mid_ctrl + y_mid_tx) / 2,
             f"$\\tau$ = {beta[1]:.1f}",
             ha="left", va="center", fontsize=10, fontweight="semibold",
             color=DARK_GRAY)

    ax1.set_xlabel("Pre-experiment SR (%)")
    ax1.set_ylabel("Adjusted Search Rate (%)")
    ax1.set_title("ANCOVA", fontsize=13, fontweight="semibold", pad=10)
    ax1.legend(**_LEGEND_KW)

    # Right panel: CUPED
    ax2.scatter(pre_p[ctrl_p], adj_p[ctrl_p], color=PT_RED,
                label="Control", **_SCATTER_KW)
    ax2.scatter(pre_p[tx_p], adj_p[tx_p], color=PT_BLUE,
                label="Treatment", **_SCATTER_KW)

    # Flat group means
    mean_adj_ctrl = adjusted[ctrl].mean()
    mean_adj_tx = adjusted[tx].mean()
    ax2.axhline(mean_adj_ctrl, color=RED, lw=1.8, alpha=0.8)
    ax2.axhline(mean_adj_tx, color=BLUE, lw=1.8, alpha=0.8)

    # Annotate treatment effect
    x_ann = pre.max() - 2
    ax2.annotate(
        "", xy=(x_ann, mean_adj_tx), xytext=(x_ann, mean_adj_ctrl),
        arrowprops=dict(arrowstyle="<->", color=DARK_GRAY, lw=1.5),
    )
    ax2.text(x_ann + 1.5, (mean_adj_ctrl + mean_adj_tx) / 2,
             f"$\\tau$ = {mean_adj_tx - mean_adj_ctrl:.1f}",
             ha="left", va="center", fontsize=10, fontweight="semibold",
             color=DARK_GRAY)

    ax2.set_xlabel("Pre-experiment SR (%)")
    ax2.set_title("CUPED", fontsize=13, fontweight="semibold", pad=10)
    ax2.legend(**_LEGEND_KW)

    _style_spines(ax1, ax2)
    _save_figure(fig, FIG_PATH)


# Covariation figure
def make_covariation_figure(data, stats, n_plot=750):
    pre, post = data["pre"], data["post"]
    rho = stats["rho"]

    pre_p, post_p = _downsample([pre, post], n_plot)

    slope, intercept = np.polyfit(pre, post, 1)

    fig, ax = plt.subplots(figsize=(5.5, 4.5))

    ax.scatter(pre_p, post_p, color=PT_INDIGO, **_SCATTER_KW)

    x_range = np.array([0, pre.max() + 1])
    ax.plot(x_range, intercept + slope * x_range,
            color=INDIGO, lw=2, alpha=0.85)

    ax.text(0.95, 0.08, f"$\\rho$ = {rho:.2f}",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=12, fontweight="semibold", color=INDIGO)

    ax.set_xlabel("Pre-experiment SR (%)")
    ax.set_ylabel("Experiment SR (%)")
    _style_spines(ax)
    _save_figure(fig, FIG_COV_PATH)


# Variance reduction figure
def make_variance_reduction_figure(stats):
    rho_data = stats["rho"]

    rho = np.linspace(0, 0.99, 200)
    var_remaining = 1 - rho ** 2

    fig, ax = plt.subplots(figsize=(6, 4))

    ax.plot(rho, var_remaining, color=INDIGO, lw=2.5)
    ax.fill_between(rho, var_remaining, alpha=0.08, color=INDIGO)

    # Mark our data point
    our_y = 1 - rho_data ** 2
    ax.plot(rho_data, our_y, "o", color=BLUE, markersize=8, zorder=5)
    ax.annotate(
        f"Our data\n$\\rho$ = {rho_data:.2f}",
        xy=(rho_data, our_y),
        xytext=(rho_data + 0.12, our_y + 0.08),
        fontsize=9, color=BLUE,
        fontweight="semibold",
        arrowprops=dict(arrowstyle="-", color=BLUE, lw=1.2),
    )

    # Reference points
    for rho_ref, label_offset in [(0.5, (0.58, 0.85)), (0.9, (0.94, 0.23))]:
        ref_y = 1 - rho_ref ** 2
        ax.plot(rho_ref, ref_y, "o", color=GRAY, markersize=6, zorder=5)
        ax.annotate(
            f"$\\rho$ = {rho_ref}",
            xy=(rho_ref, ref_y),
            xytext=label_offset,
            fontsize=8.5, color=MID_GRAY,
            arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.8),
        )

    ax.set_xlabel("Correlation ($\\rho$)")
    ax.set_ylabel("Fraction of variance remaining")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    _style_spines(ax)
    _save_figure(fig, FIG_VARRED_PATH)


# Treatment effect distribution figure
def make_tx_distribution_figure(stats):
    tau = stats["cuped_est"]
    se_naive = stats["se_simple"]
    se_adj = stats["se_tau"]

    x = np.linspace(tau - 4 * se_naive, tau + 4 * se_naive, 300)
    y_naive = norm.pdf(x, tau, se_naive)
    y_adj = norm.pdf(x, tau, se_adj)

    fig, ax = plt.subplots(figsize=(6.5, 4))

    # Naive (wider)
    ax.plot(x, y_naive, color=RED, lw=2, label="Unadjusted")
    ax.fill_between(x, y_naive, alpha=0.12, color=RED)

    # Adjusted (narrower)
    ax.plot(x, y_adj, color=BLUE, lw=2.2, label="With CUPED")
    ax.fill_between(x, y_adj, alpha=0.15, color=BLUE)

    # Treatment effect line
    ax.axvline(tau, color=DARK_GRAY, ls="--", lw=0.9, alpha=0.5)

    # SE annotations — arrows from outside pointing inward, touching the curve
    for se, color, side in [(se_naive, RED, 1), (se_adj, BLUE, -1)]:
        curve_x = tau + side * se
        h = norm.pdf(curve_x, tau, se)
        start_x = curve_x + side * se  # one SE further out
        ax.annotate(
            "", xy=(curve_x, h), xytext=(start_x, h),
            arrowprops=dict(arrowstyle="->", color=color, lw=1.3),
        )
        ax.text(start_x + side * 0.01, h,
                f"SE = {se:.2f}",
                ha="left" if side == 1 else "right", va="center",
                fontsize=9, color=color, fontweight="semibold")

    ax.set_xlabel("Treatment effect (percentage points)")
    ax.set_ylabel("Density")
    ax.set_yticks([])
    ax.legend(**_LEGEND_KW)
    ax.spines["left"].set_visible(False)
    _style_spines(ax)
    _save_figure(fig, FIG_DIST_PATH)


def main():
    data = simulate()
    stats = compute_stats(data)
    print_stats(data, stats)
    make_covariation_figure(data, stats)
    make_variance_reduction_figure(stats)
    make_tx_distribution_figure(stats)
    make_figure(data, stats)


if __name__ == "__main__":
    main()
