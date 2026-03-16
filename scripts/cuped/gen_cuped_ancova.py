import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
OUT_DIR = Path(__file__).parent.parent.parent / "static/img/posts/cuped"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_PATH = OUT_DIR / "cuped_vs_ancova.svg"
FIG_COV_PATH = OUT_DIR / "pre_post_covariation.svg"
FIG_VARRED_PATH = OUT_DIR / "variance_reduction.svg"
FIG_DIST_PATH = OUT_DIR / "tx_effect_distributions.svg"

# ── Colors ───────────────────────────────────────────────────────────────────
# Line / annotation colors
BLUE = "#2C4A7A"
RED = "#7A2A35"
# Lighter point colors for scatter (less visual density)
PT_BLUE = "#6B9BD2"
PT_RED = "#C47A85"
GRAY = "#9E9E9E"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "none",
    "axes.facecolor": "none",
})


# ── Simulation ───────────────────────────────────────────────────────────────
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
    # Beta(2, 5) gives a right-skewed distribution with values near zero.
    pre_raw = rng.beta(2, 5, size=2 * n)
    pre = 60 * pre_raw  # map to [0, 60] range

    # Treatment assignment (random)
    treatment = np.concatenate([np.zeros(n), np.ones(n)])
    rng.shuffle(treatment)

    # In-experiment search rate:
    #   post = intercept + slope * pre + tau * treatment + noise
    slope = 0.6
    intercept = 12.0
    noise = rng.normal(0, 6.0, size=2 * n)
    post = intercept + slope * pre + tau * treatment + noise

    return {"pre": pre, "post": post, "treatment": treatment,
            "true_tau": tau, "true_slope": slope}


# ── OLS via normal equations ─────────────────────────────────────────────────
def ols(X, y):
    """Return (coefficients, residuals, R²) from OLS."""
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    resid = y - X @ beta
    ss_res = resid @ resid
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot
    return beta, resid, r2


# ── CUPED adjustment ────────────────────────────────────────────────────────
def cuped_adjust(pre, post):
    """
    Return CUPED-adjusted outcome and theta.

    adjusted_i = post_i - theta * (pre_i - mean(pre))
    where theta = cov(post, pre) / var(pre)
    """
    theta = np.cov(post, pre)[0, 1] / np.var(pre, ddof=1)
    adjusted = post - theta * (pre - pre.mean())
    return adjusted, theta


# ── Print summary statistics ─────────────────────────────────────────────────
def print_stats(data):
    pre, post, treat = data["pre"], data["post"], data["treatment"]
    n = len(pre)

    print("=" * 60)
    print("SIMULATION SUMMARY")
    print("=" * 60)
    print(f"N total: {n}  (treatment: {int(treat.sum())}, "
          f"control: {int(n - treat.sum())})")
    print(f"True treatment effect: {data['true_tau']:.1f} pp")
    print()

    # Pre-experiment descriptives
    print(f"Pre-experiment SR:  mean = {pre.mean():.1f}%,  "
          f"sd = {pre.std():.1f}")
    print(f"In-experiment SR:   mean = {post.mean():.1f}%,  "
          f"sd = {post.std():.1f}")
    print()

    # Correlation
    rho = np.corrcoef(pre, post)[0, 1]
    print(f"Correlation(pre, post): {rho:.3f}")
    print(f"Variance reduction:     1 - rho^2 = {1 - rho**2:.3f}  "
          f"({(rho**2) * 100:.1f}% removed)")
    print()

    # ── Naive difference in means ────────────────────────────────────────
    diff_naive = post[treat == 1].mean() - post[treat == 0].mean()
    print(f"Naive difference in means: {diff_naive:.2f}")
    print()

    # ── CUPED ────────────────────────────────────────────────────────────
    adjusted, theta = cuped_adjust(pre, post)
    adj_treat = adjusted[treat == 1].mean()
    adj_ctrl = adjusted[treat == 0].mean()
    cuped_est = adj_treat - adj_ctrl
    print(f"CUPED theta:              {theta:.4f}")
    print(f"CUPED treatment estimate: {cuped_est:.2f}")
    print(f"  Var(observed):  {np.var(post, ddof=1):.2f}")
    print(f"  Var(adjusted):  {np.var(adjusted, ddof=1):.2f}")
    print()

    # ── ANCOVA (regression) ──────────────────────────────────────────────
    X = np.column_stack([np.ones(n), treat, pre])
    beta, resid, r2 = ols(X, post)
    print(f"ANCOVA regression:  post = {beta[0]:.2f} + "
          f"{beta[1]:.2f}*treat + {beta[2]:.4f}*pre")
    print(f"  Treatment effect (tau): {beta[1]:.2f}")
    print(f"  Pre-experiment coef:    {beta[2]:.4f}")
    print(f"  R²: {r2:.3f}")

    # Standard errors (OLS, homoscedastic)
    sigma2 = (resid @ resid) / (n - 3)
    var_beta = sigma2 * np.linalg.inv(X.T @ X)
    se_tau = np.sqrt(var_beta[1, 1])
    print(f"  SE(tau): {se_tau:.2f}")
    print()

    # ── Simple t-test (no covariate) ─────────────────────────────────────
    X_simple = np.column_stack([np.ones(n), treat])
    beta_s, resid_s, _ = ols(X_simple, post)
    sigma2_s = (resid_s @ resid_s) / (n - 2)
    var_beta_s = sigma2_s * np.linalg.inv(X_simple.T @ X_simple)
    se_simple = np.sqrt(var_beta_s[1, 1])
    print(f"Simple t-test estimate:  {beta_s[1]:.2f}  (SE = {se_simple:.2f})")
    print(f"SE reduction from ANCOVA: {(1 - se_tau / se_simple) * 100:.1f}%")
    print("=" * 60)

    return {
        "rho": rho, "theta": theta, "cuped_est": cuped_est,
        "ancova_beta": beta, "adjusted": adjusted,
        "se_tau": se_tau, "se_simple": se_simple,
    }


# ── Figure ───────────────────────────────────────────────────────────────────
def make_figure(data, stats, n_plot=750):
    pre, post, treat = data["pre"], data["post"], data["treatment"]
    adjusted = stats["adjusted"]
    beta = stats["ancova_beta"]

    # Downsample for plotting (use all data for stats, fewer points for clarity)
    rng = np.random.default_rng(99)
    idx = rng.choice(len(pre), size=min(n_plot, len(pre)), replace=False)
    pre_p, post_p, treat_p, adj_p = pre[idx], post[idx], treat[idx], adjusted[idx]

    ctrl_p = treat_p == 0
    tx_p = treat_p == 1

    # Full-data masks (for mean lines)
    ctrl = treat == 0
    tx = treat == 1

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5),
                                    sharey=True,
                                    gridspec_kw={"wspace": 0.15})

    # ── Left panel: ANCOVA ───────────────────────────────────────────────
    ax1.scatter(pre_p[ctrl_p], post_p[ctrl_p], s=16, alpha=0.4,
                color=PT_RED, edgecolors="none", label="Control")
    ax1.scatter(pre_p[tx_p], post_p[tx_p], s=16, alpha=0.4,
                color=PT_BLUE, edgecolors="none", label="Treatment")

    # Grand mean vertical line
    xbar = pre.mean()
    ax1.axvline(xbar, color=GRAY, ls="--", lw=1.0, alpha=0.85)
    ax1.text(xbar + 0.8, ax1.get_ylim()[0] + 1, f"Grand mean\n({xbar:.0f}%)",
             fontsize=8, color="#666666", va="bottom")

    # Regression lines (extend to y-axis)
    x_range = np.array([0, pre.max() + 1])
    y_ctrl_line = beta[0] + beta[2] * x_range
    y_tx_line = beta[0] + beta[1] + beta[2] * x_range
    ax1.plot(x_range, y_ctrl_line, color=RED, lw=1.8, alpha=0.8)
    ax1.plot(x_range, y_tx_line, color=BLUE, lw=1.8, alpha=0.8)

    # Annotate treatment effect (vertical gap, right of grand mean)
    y_mid_ctrl = beta[0] + beta[2] * xbar
    y_mid_tx = y_mid_ctrl + beta[1]
    ax1.annotate(
        "", xy=(xbar + 4, y_mid_tx), xytext=(xbar + 4, y_mid_ctrl),
        arrowprops=dict(arrowstyle="<->", color="#333333", lw=1.5),
    )
    ax1.text(xbar + 5, (y_mid_ctrl + y_mid_tx) / 2,
             f"$\\hat{{\\tau}}$ = {beta[1]:.1f}",
             ha="left", va="center", fontsize=10, fontweight="semibold",
             color="#333333")

    ax1.set_xlabel("Pre-experiment SR (%)")
    ax1.set_ylabel("Adjusted Search Rate (%)")
    ax1.set_title("ANCOVA", fontsize=13, fontweight="semibold", pad=10)
    ax1.legend(fontsize=9, framealpha=0.85, edgecolor="#BDBDBD",
               loc="upper left")

    # Subtitle
    ax1.text(0.5, -0.15,
             "Parallel regression lines. The treatment\n"
             "effect is the constant vertical gap.",
             transform=ax1.transAxes, ha="center", va="top",
             fontsize=8.5, color="#666666", style="italic")

    # ── Right panel: CUPED ───────────────────────────────────────────────
    ax2.scatter(pre_p[ctrl_p], adj_p[ctrl_p], s=16, alpha=0.4,
                color=PT_RED, edgecolors="none", label="Control (adj.)")
    ax2.scatter(pre_p[tx_p], adj_p[tx_p], s=16, alpha=0.4,
                color=PT_BLUE, edgecolors="none", label="Treatment (adj.)")

    # Flat group means
    mean_adj_ctrl = adjusted[ctrl].mean()
    mean_adj_tx = adjusted[tx].mean()
    ax2.axhline(mean_adj_ctrl, color=RED, lw=1.8, alpha=0.8)
    ax2.axhline(mean_adj_tx, color=BLUE, lw=1.8, alpha=0.8)

    # Annotate treatment effect
    x_ann = pre.max() - 2
    ax2.annotate(
        "", xy=(x_ann, mean_adj_tx), xytext=(x_ann, mean_adj_ctrl),
        arrowprops=dict(arrowstyle="<->", color="#333333", lw=1.5),
    )
    ax2.text(x_ann + 1.5, (mean_adj_ctrl + mean_adj_tx) / 2,
             f"$\\hat{{\\tau}}$ = {mean_adj_tx - mean_adj_ctrl:.1f}",
             ha="left", va="center", fontsize=10, fontweight="semibold",
             color="#333333")

    ax2.set_xlabel("Pre-experiment SR (%)")
    ax2.set_title("CUPED", fontsize=13, fontweight="semibold", pad=10)
    ax2.legend(fontsize=9, framealpha=0.85, edgecolor="#BDBDBD",
               loc="upper left")

    # Subtitle
    ax2.text(0.5, -0.15,
             "After subtracting $\\theta \\times (X_i - \\bar{X})$, the slope\n"
             "disappears. The treatment effect is the gap\nbetween the "
             "two flat means.",
             transform=ax2.transAxes, ha="center", va="top",
             fontsize=8.5, color="#666666", style="italic")

    for ax in (ax1, ax2):
        ax.spines["bottom"].set_color(GRAY)
        ax.spines["left"].set_color(GRAY)

    fig.savefig(FIG_PATH, format="svg", bbox_inches="tight")
    print(f"\nSaved figure → {FIG_PATH}")
    plt.close(fig)


# ── Covariation figure ───────────────────────────────────────────────────────
def make_covariation_figure(data, stats, n_plot=750):
    pre, post, treat = data["pre"], data["post"], data["treatment"]
    rho = stats["rho"]

    # Downsample for plotting
    rng = np.random.default_rng(99)
    idx = rng.choice(len(pre), size=min(n_plot, len(pre)), replace=False)
    pre_p, post_p = pre[idx], post[idx]

    # Simple regression line (ignoring treatment for this plot)
    slope, intercept = np.polyfit(pre, post, 1)

    fig, ax = plt.subplots(figsize=(5.5, 4.5))

    ax.scatter(pre_p, post_p, s=16, alpha=0.4,
               color="#7A7FB5", edgecolors="none")

    x_range = np.array([0, pre.max() + 1])
    ax.plot(x_range, intercept + slope * x_range,
            color="#3B3F6E", lw=2, alpha=0.85)

    # Annotate correlation
    ax.text(0.95, 0.08, f"$\\rho$ = {rho:.2f}",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=12, fontweight="semibold", color="#3B3F6E")

    ax.set_xlabel("Pre-experiment SR (%)")
    ax.set_ylabel("In-experiment SR (%)")
    ax.spines["bottom"].set_color(GRAY)
    ax.spines["left"].set_color(GRAY)

    fig.savefig(FIG_COV_PATH, format="svg", bbox_inches="tight")
    print(f"Saved figure → {FIG_COV_PATH}")
    plt.close(fig)


# ── Variance reduction figure ────────────────────────────────────────────────
def make_variance_reduction_figure(stats):
    rho_data = stats["rho"]

    rho = np.linspace(0, 0.99, 200)
    var_remaining = 1 - rho ** 2

    fig, ax = plt.subplots(figsize=(6, 4))

    # Curve
    ax.plot(rho, var_remaining, color="#3B3F6E", lw=2.5)

    # Fill under curve
    ax.fill_between(rho, var_remaining, alpha=0.08, color="#3B3F6E")

    # Mark our data point
    our_y = 1 - rho_data ** 2
    ax.plot(rho_data, our_y, "o", color="#2C4A7A", markersize=8, zorder=5)
    ax.annotate(
        f"Our data\n$\\rho$ = {rho_data:.2f}",
        xy=(rho_data, our_y),
        xytext=(rho_data + 0.12, our_y + 0.08),
        fontsize=9, color="#2C4A7A", fontweight="semibold",
        arrowprops=dict(arrowstyle="-", color="#2C4A7A", lw=1.2),
    )

    # Mark ρ = 0.5
    r05_y = 1 - 0.5 ** 2
    ax.plot(0.5, r05_y, "o", color=GRAY, markersize=6, zorder=5)
    ax.annotate(
        "$\\rho$ = 0.5",
        xy=(0.5, r05_y),
        xytext=(0.58, 0.85),
        fontsize=8.5, color="#666666",
        arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.8),
    )

    # Mark ρ = 0.9
    r09_y = 1 - 0.9 ** 2
    ax.plot(0.9, r09_y, "o", color=GRAY, markersize=6, zorder=5)
    ax.annotate(
        "$\\rho$ = 0.9",
        xy=(0.9, r09_y),
        xytext=(0.75, 0.42),
        fontsize=8.5, color="#666666",
        arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.8),
    )

    ax.set_xlabel("Correlation ($\\rho$)")
    ax.set_ylabel("Fraction of variance remaining")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.spines["bottom"].set_color(GRAY)
    ax.spines["left"].set_color(GRAY)

    fig.savefig(FIG_VARRED_PATH, format="svg", bbox_inches="tight")
    print(f"Saved figure → {FIG_VARRED_PATH}")
    plt.close(fig)


# ── Treatment effect distribution figure ─────────────────────────────────────
def make_tx_distribution_figure(stats):
    from scipy.stats import norm

    tau = stats["cuped_est"]
    se_naive = stats["se_simple"]
    se_adj = stats["se_tau"]

    x = np.linspace(tau - 4 * se_naive, tau + 4 * se_naive, 300)
    y_naive = norm.pdf(x, tau, se_naive)
    y_adj = norm.pdf(x, tau, se_adj)

    fig, ax = plt.subplots(figsize=(6.5, 4))

    # Naive (wider)
    ax.plot(x, y_naive, color=RED, lw=2, label="Without adjustment")
    ax.fill_between(x, y_naive, alpha=0.12, color=RED)

    # Adjusted (narrower)
    ax.plot(x, y_adj, color="#2C4A7A", lw=2.2, label="With CUPED / ANCOVA")
    ax.fill_between(x, y_adj, alpha=0.15, color="#2C4A7A")

    # Treatment effect line
    ax.axvline(tau, color="#333333", ls="--", lw=0.9, alpha=0.5)
    ax.text(tau, max(y_adj) * 1.05,
            f"$\\hat{{\\tau}}$ = {tau:.1f}",
            ha="center", va="bottom", fontsize=10,
            fontweight="semibold", color="#333333")

    # SE annotations — arrows from center, labels outside right tail
    # Naive
    h_naive = norm.pdf(tau + se_naive, tau, se_naive)
    ax.annotate(
        "", xy=(tau + se_naive, h_naive), xytext=(tau, h_naive),
        arrowprops=dict(arrowstyle="<->", color=RED, lw=1.3),
    )
    ax.text(tau + se_naive + 0.02, h_naive,
            f"SE = {se_naive:.2f}",
            ha="left", va="center", fontsize=9, color=RED,
            fontweight="semibold")

    # Adjusted — place bracket higher so it visually spans the distribution
    h_adj = norm.pdf(tau + se_adj * 0.8, tau, se_adj)
    ax.annotate(
        "", xy=(tau + se_adj, h_adj), xytext=(tau, h_adj),
        arrowprops=dict(arrowstyle="<->", color="#2C4A7A", lw=1.3),
    )
    ax.text(tau + se_adj + 0.02, h_adj,
            f"SE = {se_adj:.2f}",
            ha="left", va="center", fontsize=9, color="#2C4A7A",
            fontweight="semibold")

    ax.set_xlabel("Treatment effect (percentage points)")
    ax.set_ylabel("Density")
    ax.set_yticks([])
    ax.legend(fontsize=9, framealpha=0.85, edgecolor="#BDBDBD",
              loc="upper left")
    ax.spines["bottom"].set_color(GRAY)
    ax.spines["left"].set_visible(False)

    fig.savefig(FIG_DIST_PATH, format="svg", bbox_inches="tight")
    print(f"Saved figure → {FIG_DIST_PATH}")
    plt.close(fig)


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    data = simulate()
    stats = print_stats(data)
    make_covariation_figure(data, stats)
    make_variance_reduction_figure(stats)
    make_tx_distribution_figure(stats)
    make_figure(data, stats)


if __name__ == "__main__":
    main()
