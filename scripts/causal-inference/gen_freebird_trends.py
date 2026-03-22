import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

OUT = (
    Path(__file__).parent.parent.parent
    / "static/img/posts/causal-inference/freebird-trends.svg"
)

DATA = Path(__file__).parent / "googl_trends_twitter_search_202205_202212.csv"

BLUE = "#2C4A7A"
RED = "#7A2A35"
GRAY = "#9E9E9E"
LIGHT_GRAY = "#CCCCCC"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "none",
    "axes.facecolor": "none",
})


def main():
    df = pd.read_csv(DATA, parse_dates=["Time"])

    fig, ax = plt.subplots(figsize=(9.5, 4.5))

    # Plot control series (LinkedIn, TikTok, Instagram) in light gray
    for col in ["LinkedIn", "TikTok", "Instagram"]:
        ax.plot(df["Time"], df[col], color=LIGHT_GRAY, linewidth=1.4,
                alpha=0.7, zorder=1)

    # Label controls once (at the last data point, stacked)
    last = df.iloc[-1]
    controls = [("Instagram", last["Instagram"]),
                ("TikTok", last["TikTok"]),
                ("LinkedIn", last["LinkedIn"])]
    for name, y in controls:
        ax.text(last["Time"] + pd.Timedelta(days=3), y, name,
                fontsize=8.5, color="#999999", va="center")

    # Plot Twitter in blue
    ax.plot(df["Time"], df["Twitter"], color=BLUE, linewidth=2.2,
            marker="o", markersize=3.5, alpha=0.85, zorder=3,
            label="Twitter")
    ax.text(last["Time"] + pd.Timedelta(days=3), last["Twitter"],
            "Twitter", fontsize=9, color=BLUE, va="center",
            fontweight="semibold")

    # Mark the acquisition week (Oct 23 week contains Oct 27 close + Oct 28 tweet)
    acq_date = pd.Timestamp("2022-10-23")
    ax.axvline(acq_date, color=RED, ls="--", lw=1.5, alpha=0.7, zorder=2)
    ax.text(acq_date - pd.Timedelta(days=3), 102,
            "Acquisition closes Oct 27\n\"The bird is freed\" Oct 28",
            fontsize=9, color=RED, ha="right", va="bottom",
            fontweight="semibold")

    ax.set_ylabel("Relative search interest", labelpad=8)
    ax.set_ylim(0, 115)
    ax.set_title('Google Trends: Weekly Search Interest (US)',
                 fontsize=12.5, fontweight="semibold", pad=12,
                 color="#212121")

    ax.spines["bottom"].set_color(GRAY)
    ax.spines["left"].set_color(GRAY)

    # Rotate x labels for readability
    fig.autofmt_xdate(rotation=30, ha="right")

    plt.tight_layout()
    fig.savefig(OUT, format="svg", bbox_inches="tight")
    print(f"Saved → {OUT}")
    plt.close(fig)


if __name__ == "__main__":
    main()
