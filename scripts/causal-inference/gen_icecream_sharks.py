import numpy as np
import matplotlib.pyplot as plt
# import matplotlib.lines as mlinesd
from pathlib import Path

OUT = Path(__file__).parent.parent.parent / "static/img/posts/causal-inference/icecream-sharks.svg"  # noqa

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# US ice cream retail sales, $M (approximate real-world seasonal shape)
ice_cream = np.array([480, 510, 620, 810, 1100, 1520,
                      1780, 1690, 1280, 870, 600, 520], dtype=float)

# US unprovoked shark attacks by month (approximate, sums to ~46)
sharks = np.array([1, 1, 2, 3, 4, 7,
                   9, 8, 6, 3, 1, 1], dtype=float)

x = np.arange(len(MONTHS))

BLUE = "#2C4A7A"  # dark navy, slightly desaturated
RED = "#7A2A35"  # dark burgundy/wine
GRAY = "#9E9E9E"

plt.rcParams.update({
    "font.family":      "sans-serif",
    "font.size":        11,
    "axes.spines.top":  False,
    "figure.facecolor": "none",
    "axes.facecolor":   "none",
})

fig, ax1 = plt.subplots(figsize=(9, 4.2))

# Left axis — ice cream
l1, = ax1.plot(x, ice_cream, color=BLUE, linewidth=2.2, marker="o",
               markersize=4, alpha=0.82, label="Ice cream sales ($M)")
ax1.set_ylabel("Ice cream sales ($M)", color=BLUE, labelpad=8)
ax1.tick_params(axis="y", labelcolor=BLUE)
ax1.set_ylim(0, 2100)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v:,.0f}"))
ax1.spines["left"].set_color(BLUE)
ax1.spines["bottom"].set_color(GRAY)
ax1.spines["right"].set_visible(False)

# Right axis — shark attacks
ax2 = ax1.twinx()
l2, = ax2.plot(x, sharks, color=RED, linewidth=2.2, linestyle=":",
               marker="s", markersize=4, alpha=0.82, label="Shark attacks")
ax2.set_ylabel("Shark attacks", color=RED, labelpad=8)
ax2.tick_params(axis="y", labelcolor=RED)
ax2.set_ylim(0, 14)
ax2.spines["right"].set_color(RED)
ax2.spines["top"].set_visible(False)

# X axis
ax1.set_xticks(x)
ax1.set_xticklabels(MONTHS, color="#424242")
ax1.set_xlim(-0.5, 11.5)

# Shade summer months (Jun–Sep: indices 5–8)
ax1.axvspan(4.5, 8.5, color="#FFF9C4", alpha=0.6, zorder=0)
ax1.text(6.5, 1980, "Summer", ha="center", va="top",
         fontsize=9, color="#9E6C00", style="italic")

# Single combined legend
ax1.legend(handles=[l1, l2], loc="upper left",
           framealpha=0.85, edgecolor="#BDBDBD", fontsize=10)

ax1.set_title("Ice Cream Sales and Shark Attacks Rise and Fall Together",
              fontsize=13, fontweight="semibold", pad=12, color="#212121")

plt.tight_layout()
fig.savefig(OUT, format="svg", bbox_inches="tight")
print(f"Saved → {OUT}")
