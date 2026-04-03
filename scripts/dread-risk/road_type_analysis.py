from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT_DIR = Path(__file__).resolve().parents[2] / "static" / "img" / "dread-risk"
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "fars" / "processed" / "monthly_by_road_type.csv"

ROAD_LABELS = {1: "Interstate", 0: "Non-Interstate"}
MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_NAMES = {10: "Oct", 11: "Nov", 12: "Dec"}


def compute_baseline_and_2001(df, road_type):
    rd = df[df.road_type == road_type]
    baseline = rd[rd.YEAR.between(1996, 2000)].groupby("MONTH").agg(
        mean=("fatal_crashes", "mean"),
        min=("fatal_crashes", "min"),
        max=("fatal_crashes", "max"),
    )
    y2001 = rd[rd.YEAR == 2001].set_index("MONTH")["fatal_crashes"]
    return baseline, y2001


def print_q4_table(baseline, y2001, road_type):
    print(f"\n{'=' * 50}")
    print(road_type)
    print(f"{'=' * 50}")
    print(f"{'Month':>5} | {'Baseline':>8} | {'2001':>6} | {'Excess':>6}")
    print("-" * 40)
    for m in range(10, 13):
        bl = baseline.loc[m, "mean"]
        val = y2001.loc[m]
        print(f"{MONTH_NAMES[m]:>5} | {bl:>8.0f} | {val:>6.0f} | {val - bl:>+6.0f}")

    bl_q4 = baseline.loc[10:12, "mean"].sum()
    val_q4 = y2001.loc[10:12].sum()
    pct = ((val_q4 - bl_q4) / bl_q4) * 100
    print(f"{'Total':>5} | {bl_q4:>8.0f} | {val_q4:>6.0f} | {val_q4 - bl_q4:>+6.0f}  ({pct:+.1f}%)")


def main():
    df = pd.read_csv(DATA_PATH)
    df["road_type"] = df["is_interstate"].map(ROAD_LABELS)

    road_types = ["Interstate", "Non-Interstate"]
    stats = {rt: compute_baseline_and_2001(df, rt) for rt in road_types}

    for rt in road_types:
        print_q4_table(*stats[rt], rt)

    # Plot
    months = np.arange(1, 13)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=False)

    for ax, rt in zip(axes, road_types):
        baseline, y2001 = stats[rt]

        ax.vlines(months, baseline["min"], baseline["max"],
                  color="black", linewidth=1.5, zorder=2)
        ax.plot(months, baseline["mean"], color="gray", marker="o",
                markersize=6, linewidth=2, label="1996–2000 mean", zorder=3)
        ax.plot(months, y2001.values, color="black", marker="s",
                markersize=7, linewidth=0, label="2001", zorder=4)
        ax.axvline(9, color="red", linestyle="--", alpha=0.5, linewidth=1)

        ax.set_xticks(months)
        ax.set_xticklabels(MONTH_LABELS, fontsize=8)
        ax.set_ylabel("Fatal Crashes")
        ax.set_title(rt)
        ax.legend(loc="lower right", fontsize=9)

    fig.suptitle("Fatal Crashes by Road Type: 1996–2000 vs. 2001", fontsize=13)
    fig.tight_layout()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "road_type.png", dpi=150)
    print(f"\nPlot saved to {OUT_DIR / 'road_type.png'}")


if __name__ == "__main__":
    main()
