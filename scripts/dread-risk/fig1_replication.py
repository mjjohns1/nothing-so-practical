from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT_DIR = Path(__file__).resolve().parents[2] / "static" / "img" / "dread-risk"
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "fars" / "processed" / "monthly_national.csv"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def main():
    df = pd.read_csv(DATA_PATH)

    # Baseline: 1996-2000
    baseline = df[df.YEAR.between(1996, 2000)]
    baseline_stats = baseline.groupby("MONTH").agg(
        mean=("fatal_crashes", "mean"),
        min=("fatal_crashes", "min"),
        max=("fatal_crashes", "max"),
    )

    # 2001 values
    y2001 = df[df.YEAR == 2001].set_index("MONTH")["fatal_crashes"]

    fig, ax = plt.subplots(figsize=(10, 6))

    months = np.arange(1, 13)

    # Baseline range (min-max bars)
    ax.vlines(
        months, baseline_stats["min"], baseline_stats["max"],
        color="black", linewidth=1.5, zorder=2,
    )

    # Baseline mean line
    ax.plot(
        months, baseline_stats["mean"],
        color="gray", marker="o", markersize=7, linewidth=2,
        label="1996–2000 mean", zorder=3,
    )

    # 2001 values
    ax.plot(
        months, y2001.values,
        color="black", marker="s", markersize=8, linewidth=0,
        label="2001", zorder=4,
    )

    # September 11 reference line
    ax.axvline(9, color="red", linestyle="--", alpha=0.5, linewidth=1)
    ax.text(9.15, ax.get_ylim()[0] + 50, "Sep 11", color="red", fontsize=9, alpha=0.7)

    ax.set_xticks(months)
    ax.set_xticklabels(MONTHS)
    ax.set_ylabel("Number of Fatal Traffic Accidents")
    ax.set_title("Fatal Traffic Accidents: 1996–2000 vs. 2001")
    ax.legend(loc="lower right")
    ax.set_ylim(2200, 3700)

    fig.tight_layout()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "fig1_replication.png"
    fig.savefig(out_path, dpi=150)
    print(f"Saved to {out_path}")

    # Print the numbers for reference
    print("\nMonth | 96-00 Mean | 96-00 Range      | 2001")
    print("-" * 50)
    for m in months:
        mean = baseline_stats.loc[m, "mean"]
        lo = baseline_stats.loc[m, "min"]
        hi = baseline_stats.loc[m, "max"]
        val = y2001.loc[m]
        diff = val - mean
        print(f"  {MONTHS[m-1]:>3}   {mean:7.0f}    {lo:5.0f} – {hi:5.0f}    {val:5.0f}  ({diff:+.0f})")


if __name__ == "__main__":
    main()
