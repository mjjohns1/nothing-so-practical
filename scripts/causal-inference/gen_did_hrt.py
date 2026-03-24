import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

OUT = (
    Path(__file__).parent.parent.parent
    / "static/img/posts/causal-inference/did-hrt.svg"
)

BLUE = "#2C4A7A"
RED = "#7A2A35"
GRAY = "#9E9E9E"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "none",
    "axes.facecolor": "none",
})


def ols_line(x, y):
    """Fit a degree-1 OLS line; return (fitted_y, coefficients)."""
    coeffs = np.polyfit(x, y, 1)
    return np.polyval(coeffs, x), coeffs


def main():
    # Stylized diff-in-diff illustration for HRT example.
    # Noisy observations are shown as scatter; OLS lines are fit
    # separately for each group × period.  The HRT pre-treatment fit
    # is extended into the post period as the counterfactual.
    rng = np.random.default_rng(42)
    years = np.arange(1985, 1999)
    treatment_year = 1992
    pre = years < treatment_year
    post = ~pre

    # Control group: steady decline with small noise
    ctrl = 60 - 1.2 * (years - 1985) + rng.normal(0, 0.8, len(years))

    # HRT group: lower baseline (health-conscious), parallel pre-trend,
    # then a visible post-treatment drop
    hrt_base = 50 - 1.2 * (years - 1985) + rng.normal(0, 0.8, len(years))
    treatment_effect = np.where(post, -2.5 * (years - treatment_year + 1), 0)
    hrt = hrt_base + treatment_effect

    # OLS fits: one line per group per period
    ctrl_pre_fit, _ = ols_line(years[pre], ctrl[pre])
    ctrl_post_fit, _ = ols_line(years[post], ctrl[post])
    hrt_pre_fit, hrt_pre_coeffs = ols_line(years[pre], hrt[pre])
    hrt_post_fit, _ = ols_line(years[post], hrt[post])

    # Counterfactual: extend HRT pre-trend into the post period
    hrt_cf = np.polyval(hrt_pre_coeffs, years[post])

    fig, ax = plt.subplots(figsize=(9, 4.5))

    # Shading for treatment period
    ax.axvspan(treatment_year - 0.5, years[-1] + 0.5,
               color="#E3F2FD", alpha=0.5, zorder=0)
    ax.axvline(treatment_year - 0.5, color=GRAY, ls="--", lw=1, alpha=0.6)
    ax.text(treatment_year + 0.1, max(ctrl) + 1.5, "HRT adoption",
            fontsize=9.5, color="#555555", style="italic", va="bottom")

    # Scatter: observed data points (both groups, both periods)
    ax.scatter(years[pre], ctrl[pre], color=RED, s=18, alpha=0.45, zorder=3)
    ax.scatter(years[post], ctrl[post], color=RED, s=18, alpha=0.45, zorder=3)
    ax.scatter(years[pre], hrt[pre], color=BLUE, s=18, alpha=0.45, zorder=3)
    ax.scatter(years[post], hrt[post], color=BLUE, s=18, alpha=0.45, zorder=3)

    # Fitted lines — control group (label only on one segment for legend)
    ax.plot(years[pre], ctrl_pre_fit, color=RED, lw=2.2, alpha=0.9, zorder=4)
    ax.plot(years[post], ctrl_post_fit, color=RED, lw=2.2, alpha=0.9,
            label="Non-HRT users", zorder=4)

    # Fitted lines — HRT observed
    ax.plot(years[pre], hrt_pre_fit, color=BLUE, lw=2.2, alpha=0.9, zorder=4)
    ax.plot(years[post], hrt_post_fit, color=BLUE, lw=2.2, alpha=0.9,
            label="HRT users (observed)", zorder=4)

    # Counterfactual (parallel trend extended from pre-period fit)
    ax.plot(years[post], hrt_cf, color=BLUE, lw=1.8, ls=":", alpha=0.6,
            label="HRT users (counterfactual)", zorder=2)

    # Annotate the treatment effect at the last observed year
    y_obs = hrt_post_fit[-1]
    y_cf = hrt_cf[-1]
    ax.annotate(
        "", xy=(years[-1] + 0.3, y_obs),
        xytext=(years[-1] + 0.3, y_cf),
        arrowprops=dict(arrowstyle="<->", color="#444444", lw=1.5),
    )
    ax.text(years[-1] + 0.55, (y_obs + y_cf) / 2,
            "Estimated\neffect",
            ha="left", va="center", fontsize=9.5,
            color="#444444", style="italic", fontweight="semibold")

    ax.set_xlabel("Year", labelpad=8)
    ax.set_ylabel("CV events per 1,000 women", labelpad=8)
    ax.set_title("Difference-in-Differences Design",
                 fontsize=13, fontweight="semibold", pad=12,
                 color="#212121")

    ax.legend(loc="upper right", framealpha=0.85, edgecolor="#BDBDBD",
              fontsize=10)

    ax.spines["bottom"].set_color(GRAY)
    ax.spines["left"].set_color(GRAY)

    plt.tight_layout()
    fig.savefig(OUT, format="svg", bbox_inches="tight")
    print(f"Saved → {OUT}")
    plt.close(fig)


if __name__ == "__main__":
    main()
