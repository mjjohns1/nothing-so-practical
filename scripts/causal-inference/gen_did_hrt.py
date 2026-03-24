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
    # Clean 2×2 diagram: four group × period means connected by lines,
    # with a dotted counterfactual and an effect arrow at the post-period
    # center.  No scatter — the focus is the estimation logic.
    rng = np.random.default_rng(42)
    years = np.arange(1985, 1999)
    treatment_year = 1992
    pre = years < treatment_year
    post = ~pre

    # Simulate underlying data (used only to derive the means)
    ctrl = 60 - 1.2 * (years - 1985) + rng.normal(0, 0.8, len(years))
    hrt_base = 50 - 1.2 * (years - 1985) + rng.normal(0, 0.8, len(years))
    treatment_effect = np.where(post, -2.5 * (years - treatment_year + 1), 0)
    hrt = hrt_base + treatment_effect

    # Group × period means
    ctrl_pre_mean  = ctrl[pre].mean()
    ctrl_post_mean = ctrl[post].mean()
    hrt_pre_mean   = hrt[pre].mean()
    hrt_post_mean  = hrt[post].mean()
    hrt_cf_mean    = hrt_pre_mean + (ctrl_post_mean - ctrl_pre_mean)

    # Symmetric x-positions: pre=1, post=2, boundary at 1.5
    x_pre, x_post, x_mid = 1, 2, 1.5

    fig, ax = plt.subplots(figsize=(9, 4.5))

    # Treatment period shading
    ax.axvspan(x_mid, x_post + 0.5, color="#E3F2FD", alpha=0.5, zorder=0)
    ax.axvline(x_mid, color=GRAY, ls="--", lw=1, alpha=0.6)
    ax.text(x_mid + 0.04, ctrl_pre_mean + 1.5, "HRT adoption",
            fontsize=9.5, color="#555555", style="italic", va="bottom")

    # Control group: pre-mean → post-mean
    ax.plot([x_pre, x_post], [ctrl_pre_mean, ctrl_post_mean],
            color=RED, lw=2.2, marker="o", markersize=7,
            label="Non-HRT users", zorder=4)

    # HRT observed: pre-mean → post-mean
    ax.plot([x_pre, x_post], [hrt_pre_mean, hrt_post_mean],
            color=BLUE, lw=2.2, marker="o", markersize=7,
            label="HRT users (observed)", zorder=4)

    # Counterfactual: pre-mean → cf post-mean
    ax.plot([x_pre, x_post], [hrt_pre_mean, hrt_cf_mean],
            color=BLUE, lw=1.8, ls=":", alpha=0.7,
            label="HRT users (counterfactual)", zorder=3)
    # Distinct marker at the counterfactual endpoint only
    ax.scatter([x_post], [hrt_cf_mean],
               color=BLUE, s=55, marker="D", alpha=0.7, zorder=5)

    # Effect arrow
    ax.annotate(
        "", xy=(x_post + 0.07, hrt_post_mean),
        xytext=(x_post + 0.07, hrt_cf_mean),
        arrowprops=dict(arrowstyle="<->", color="#444444", lw=1.5),
    )
    ax.text(x_post + 0.12, (hrt_post_mean + hrt_cf_mean) / 2,
            "Estimated\neffect",
            ha="left", va="center", fontsize=9.5,
            color="#444444", style="italic", fontweight="semibold")

    ax.set_xticks([x_pre, x_post])
    ax.set_xticklabels(["Pre-treatment", "Post-treatment"], fontsize=11)
    ax.set_xlim(x_pre - 0.5, x_post + 0.5)
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
