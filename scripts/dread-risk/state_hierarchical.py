import os

os.environ["PYTENSOR_FLAGS"] = "device=cpu,floatX=float64,cxx="

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd
import pymc as pm  # type: ignore[import]

OUT_DIR = Path(__file__).resolve().parents[2] / "static" / "img" / "dread-risk"
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "fars" / "processed" / "monthly_by_state.csv"

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
HIGH_AIR_TRAVEL = {
    "CA", "TX", "FL", "IL", "GA", "NY", "PA", "AZ", "NV", "MO",
    "CO", "NC", "MI", "VA", "MN",
}


def prepare_data():
    """
    State-level change scores with pre-period noise estimates.

    For each state:
      - pre_mean: average Oct-Dec monthly crashes, 1996-2000 (15 observations)
      - pre_se:   standard error of that mean (sd / sqrt(n)), used as likelihood weight
      - post_mean: average Oct-Dec monthly crashes, 2001 (3 observations)
      - delta:    post_mean - pre_mean (absolute change)
      - pct_change: delta / pre_mean
    """
    df = (
        pd.read_csv(DATA_PATH)
        .assign(state_abbr=lambda d: d["STATE"].map(FIPS_TO_STATE))
        .dropna(subset=["state_abbr"])
        .query("10 <= MONTH <= 12")
    )

    pre = (
        df.query("1996 <= YEAR <= 2000")
        .groupby("state_abbr")["fatal_crashes"]
        .agg(pre_mean="mean", pre_sd="std", pre_n="count")
    )

    post = (
        df.query("YEAR == 2001")
        .groupby("state_abbr")["fatal_crashes"]
        .agg(post_mean="mean", post_sd="std", post_n="count")
    )

    return (
        pd.concat([pre, post], axis=1)
        .dropna()
        .assign(
            delta=lambda d: d["post_mean"] - d["pre_mean"],
            pct_change=lambda d: d["delta"] / d["pre_mean"] * 100,
            high_air_travel=lambda d: d.index.isin(HIGH_AIR_TRAVEL),
            # SE of the change score: sqrt(Var(pre_mean) + Var(post_mean))
            # Post period has only 3 obs so we pool SD from pre for stability
            delta_se=lambda d: np.sqrt(
                d["pre_sd"] ** 2 / d["pre_n"] + d["pre_sd"] ** 2 / d["post_n"]
            ),
        )
    )


def run_model(state_df):
    """
    Weighted comparison of state-level change scores.

      delta[s] ~ Normal(mu[group[s]], se[s])
      mu[0], mu[1] ~ Normal(0, 200)
      DiD = mu[1] - mu[0]

    The pre-period SE acts as a precision weight: noisy small states
    contribute less to the group mean estimates.
    """
    group = state_df["high_air_travel"].astype(int).values
    delta = state_df["delta"].values
    se = state_df["delta_se"].values

    with pm.Model() as model:
        mu = pm.Normal("mu", mu=0, sigma=200, shape=2)
        pm.Normal("obs", mu=mu[group], sigma=se, observed=delta)
        pm.Deterministic("DiD", mu[1] - mu[0])

    print(model.debug())

    with model:
        idata = pm.sample(
            draws=2000,
            tune=1000,
            random_seed=42,
            progressbar=True,
        )

    return idata


def summarize_and_plot(idata, state_df):
    divergences = int(idata.sample_stats["diverging"].values.sum())
    print(f"Divergences: {divergences}")

    # ── Group means and DiD ──
    post = idata.posterior
    mu_low = post["mu"].sel(mu_dim_0=0).values.ravel()
    mu_high = post["mu"].sel(mu_dim_0=1).values.ravel()
    did = post["DiD"].values.ravel()

    print("\n" + "=" * 60)
    print("BAYESIAN WEIGHTED DiD (Oct-Dec 2001 vs. 1996-2000)")
    print("=" * 60)

    for label, samples in [("Low air travel", mu_low), ("High air travel", mu_high), ("DiD (high − low)", did)]:
        lo, hi = np.percentile(samples, [2.5, 97.5])
        print(f"  {label:22s}: {samples.mean():+6.1f}  [95% HDI: {lo:+.1f}, {hi:+.1f}]")

    print(f"  P(DiD > 0): {(did > 0).mean():.3f}")

    # ── Convert to % using group baseline averages ──
    high_baseline = state_df.loc[state_df["high_air_travel"], "pre_mean"].mean()
    low_baseline = state_df.loc[~state_df["high_air_travel"], "pre_mean"].mean()
    did_pct = (mu_high / high_baseline - mu_low / low_baseline) * 100
    print(f"\n  DiD in % terms (approx): {did_pct.mean():+.1f}pp  "
          f"[{np.percentile(did_pct, 2.5):.1f}, {np.percentile(did_pct, 97.5):.1f}]")

    # ── Raw descriptive summary ──
    print("\n" + "=" * 60)
    print("DESCRIPTIVE SUMMARY (unweighted)")
    print("=" * 60)
    for flag, label in [(True, "High air travel"), (False, "Other")]:
        g = state_df[state_df["high_air_travel"] == flag]
        print(f"  {label} (n={len(g)}): avg change {g['delta'].mean():+.1f} crashes/mo  "
              f"({g['pct_change'].mean():+.1f}%)")

    # ── Figure ──
    fig, axes = plt.subplots(1, 2, figsize=(13, 8))

    # Left: state-level change scores (dot plot), sized by baseline volume
    ax = axes[0]
    state_df_sorted = state_df.sort_values("delta")
    colors = ["#d62728" if h else "#1f77b4" for h in state_df_sorted["high_air_travel"]]
    sizes = (state_df_sorted["pre_mean"] / state_df_sorted["pre_mean"].max() * 200).clip(lower=10)
    y_pos = np.arange(len(state_df_sorted))

    ax.scatter(state_df_sorted["delta"], y_pos, c=colors, s=sizes, alpha=0.8, zorder=3)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(state_df_sorted.index, fontsize=7)
    ax.set_xlabel("Change in Avg Monthly Fatal Crashes (Oct–Dec 2001 vs. 1996–2000)")
    ax.set_title("State-Level Change Scores\n(dot size ∝ baseline volume)")
    ax.legend(
        handles=[
            Patch(color="#d62728", label="High air travel"),
            Patch(color="#1f77b4", label="Other"),
        ],
        loc="lower right",
    )

    # Right: DiD posterior
    ax = axes[1]
    ax.hist(did, bins=60, color="steelblue", alpha=0.8, density=True)
    ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
    ax.axvline(float(did.mean()), color="steelblue", linewidth=1.5)
    lo95, hi95 = np.percentile(did, [2.5, 97.5])
    ax.axvspan(lo95, hi95, alpha=0.15, color="steelblue")
    ax.set_xlabel("Avg Change: High − Low Air Travel (crashes/month)")
    ax.set_title("Posterior: Group Difference in Avg Change")

    fig.tight_layout()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "state_hierarchical.png"
    fig.savefig(out_path, dpi=150)
    print(f"\nPlot saved to {out_path}")


def main():
    state_df = prepare_data()
    print(f"States: {len(state_df)}  |  High air travel: {state_df['high_air_travel'].sum()}")

    idata = run_model(state_df)
    summarize_and_plot(idata, state_df)


if __name__ == "__main__":
    main()
