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


def main():
    # Stylized diff-in-diff illustration for HRT example.
    # Pre-treatment: both groups trend downward (improving) in parallel.
    # Post-treatment: HRT group diverges from the parallel-trend
    # counterfactual.
    years = np.arange(1985, 1999)
    treatment_year = 1992
    pre = years < treatment_year
    post = ~pre

    # Baseline cardiovascular risk (per 1000 women, stylized)
    # Control group: steady decline
    ctrl = 60 - 1.2 * (years - 1985) + np.array(
        [0.3, -0.4, 0.2, -0.1, 0.5, -0.3, 0.1, -0.2,
         0.4, -0.3, 0.2, -0.1, 0.3, -0.4]
    )

    # HRT group: lower baseline (health-conscious), parallel pre-trend,
    # then a visible drop post-treatment
    hrt_base = 50 - 1.2 * (years - 1985) + np.array(
        [-0.2, 0.3, -0.1, 0.4, -0.3, 0.1, -0.4, 0.2,
         -0.1, 0.3, -0.2, 0.1, -0.3, 0.2]
    )
    # Post-treatment: additional decrease (the apparent treatment effect)
    treatment_effect = np.where(post, -2.5 * (years - treatment_year + 1), 0)
    hrt = hrt_base + treatment_effect

    # Counterfactual: what HRT group would have looked like without treatment
    counterfactual = hrt_base

    fig, ax = plt.subplots(figsize=(9, 4.5))

    # Shading for treatment period
    ax.axvspan(treatment_year - 0.5, years[-1] + 0.5,
               color="#E3F2FD", alpha=0.5, zorder=0)
    ax.axvline(treatment_year - 0.5, color=GRAY, ls="--", lw=1, alpha=0.6)
    ax.text(treatment_year + 0.1, max(ctrl) + 1.5, "HRT adoption",
            fontsize=9.5, color="#555555", style="italic", va="bottom")

    # Control group
    ax.plot(years, ctrl, color=RED, linewidth=2.2, marker="o",
            markersize=4, alpha=0.85, label="Non-HRT users", zorder=3)

    # HRT group (observed)
    ax.plot(years, hrt, color=BLUE, linewidth=2.2, marker="o",
            markersize=4, alpha=0.85, label="HRT users (observed)", zorder=3)

    # Counterfactual (parallel trend)
    ax.plot(years[post], counterfactual[post], color=BLUE, linewidth=1.8,
            linestyle=":", alpha=0.55, label="HRT users (counterfactual)",
            zorder=2)

    # Annotate the treatment effect
    last_idx = len(years) - 1
    y_obs = hrt[last_idx]
    y_cf = counterfactual[last_idx]
    ax.annotate(
        "", xy=(years[last_idx] + 0.3, y_obs),
        xytext=(years[last_idx] + 0.3, y_cf),
        arrowprops=dict(arrowstyle="<->", color="#444444", lw=1.5),
    )
    ax.text(years[last_idx] + 0.55, (y_obs + y_cf) / 2,
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
