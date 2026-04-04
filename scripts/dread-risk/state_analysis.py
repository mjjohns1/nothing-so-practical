from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

OUT_DIR = Path(__file__).resolve().parents[2] / "static" / "img" / "dread-risk"
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "fars" / "processed" / "monthly_by_state.csv"

# FARS state FIPS codes to state abbreviations (50 states + DC)
FIPS_TO_STATE = {
    1: "AL", 2: "AK", 4: "AZ", 5: "AR", 6: "CA", 8: "CO", 9: "CT", 10: "DE",
    11: "DC", 12: "FL", 13: "GA", 15: "HI", 16: "ID", 17: "IL", 18: "IN",
    19: "IA", 20: "KS", 21: "KY", 22: "LA", 23: "ME", 24: "MD", 25: "MA",
    26: "MI", 27: "MN", 28: "MS", 29: "MO", 30: "MT", 31: "NE", 32: "NV",
    33: "NH", 34: "NJ", 35: "NM", 36: "NY", 37: "NC", 38: "ND", 39: "OH",
    40: "OK", 41: "OR", 42: "PA", 43: "PR", 44: "RI", 45: "SC", 46: "SD",
    47: "TN", 48: "TX", 49: "UT", 50: "VT", 51: "VA", 52: "VI", 53: "WA",
    54: "WV", 55: "WI", 56: "WY",
}

# Top 15 states by passenger enplanements in 2001 (FAA ACAIS CY2001 data)
# These states contain the busiest airports and account for the bulk of air travel
HIGH_AIR_TRAVEL = {
    "CA", "TX", "FL", "IL", "GA", "NY", "PA", "AZ", "NV", "MO",
    "CO", "NC", "MI", "VA", "MN",
}


def prepare_state_df():
    df = (
        pd.read_csv(DATA_PATH)
        .assign(state_abbr=lambda d: d["STATE"].map(FIPS_TO_STATE))
        .dropna(subset=["state_abbr"])
    )

    baseline_avg = (
        df.query("1996 <= YEAR <= 2000 and 10 <= MONTH <= 12")
        .groupby("state_abbr")["fatal_crashes"]
        .mean()
        .rename("baseline_monthly_avg")
    )

    post_avg = (
        df.query("YEAR == 2001 and 10 <= MONTH <= 12")
        .groupby("state_abbr")["fatal_crashes"]
        .mean()
        .rename("post_monthly_avg")
    )

    return (
        pd.concat([baseline_avg, post_avg], axis=1)
        .dropna()
        .assign(
            excess=lambda d: d["post_monthly_avg"] - d["baseline_monthly_avg"],
            pct_change=lambda d: (d["excess"] / d["baseline_monthly_avg"]) * 100,
            high_air_travel=lambda d: d.index.isin(HIGH_AIR_TRAVEL),
        )
    )


def permutation_test(state_df, n_permutations=10000, seed=42):
    """Permutation test for the weighted % difference between high and low air travel states."""
    rng = np.random.default_rng(seed)
    n_high = int(state_df["high_air_travel"].sum())

    def weighted_diff(df, high_mask):
        high = df[high_mask]
        low = df[~high_mask]
        pct_high = (high["excess"].sum() / high["baseline_monthly_avg"].sum()) * 100
        pct_low = (low["excess"].sum() / low["baseline_monthly_avg"].sum()) * 100
        return pct_high - pct_low

    observed = weighted_diff(state_df, state_df["high_air_travel"])
    indices = np.arange(len(state_df))
    diffs = []
    for _ in range(n_permutations):
        perm_high = rng.choice(indices, size=n_high, replace=False)
        mask = np.zeros(len(state_df), dtype=bool)
        mask[perm_high] = True
        diffs.append(weighted_diff(state_df, mask))

    p_value = float(np.mean(np.array(diffs) >= observed))
    return observed, p_value, np.array(diffs)


def main():
    state_df = prepare_state_df()

    # ── Summary by air travel group ──
    print("=" * 60)
    print("EXCESS FATAL CRASHES (Oct-Dec 2001 vs 1996-2000 baseline)")
    print("=" * 60)

    for group, label in [(True, "High air travel states"), (False, "Other states")]:
        g = state_df[state_df.high_air_travel == group]
        total_excess = g["excess"].sum() * 3  # 3 months
        avg_pct = (g["excess"].sum() / g["baseline_monthly_avg"].sum()) * 100
        print(f"\n{label} (n={len(g)}):")
        print(f"  Total excess crashes (Oct-Dec): {total_excess:.0f}")
        print(f"  Average % change: {avg_pct:.1f}%")

    # ── Bar chart: % change by state, colored by air travel group ──
    state_df = state_df.sort_values("pct_change", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 12))
    colors = ["#d62728" if h else "#1f77b4" for h in state_df["high_air_travel"]]
    ax.barh(range(len(state_df)), state_df["pct_change"], color=colors)
    ax.set_yticks(range(len(state_df)))
    ax.set_yticklabels(state_df.index, fontsize=8)
    ax.set_xlabel("% Change in Fatal Crashes (Oct–Dec 2001 vs. 1996–2000 avg)")
    ax.set_title("Post-9/11 Excess Fatal Crashes by State")
    ax.axvline(0, color="black", linewidth=0.8)

    ax.legend(
        handles=[
            Patch(color="#d62728", label="High air travel"),
            Patch(color="#1f77b4", label="Other"),
        ],
        loc="lower right",
    )

    fig.tight_layout()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "state_excess.png", dpi=150)
    print(f"\nPlot saved to {OUT_DIR / 'state_excess.png'}")

    # ── Permutation test ──
    observed_diff, p_value, perm_diffs = permutation_test(state_df)
    print(f"\n{'=' * 60}")
    print("PERMUTATION TEST (high vs. other, 10,000 permutations)")
    print(f"{'=' * 60}")
    print(f"  Observed difference: {observed_diff:.1f}pp")
    print(f"  p-value (one-sided, H1: high > other): {p_value:.4f}")

    # ── Print top/bottom states ──
    print("\n" + "=" * 60)
    print("TOP 10 STATES BY % INCREASE")
    print("=" * 60)
    top = state_df.sort_values("pct_change", ascending=False).head(10)
    for st, row in top.iterrows():
        air = " *" if row["high_air_travel"] else ""
        print(f"  {st:>2}: {row['pct_change']:+.1f}%  (baseline avg: {row['baseline_monthly_avg']:.0f}/mo){air}")


if __name__ == "__main__":
    main()
