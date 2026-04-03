import os
from pathlib import Path

import causalpy as cp  # type: ignore[import]
import pandas as pd

OUT_DIR = Path(__file__).resolve().parents[2] / "static" / "img" / "dread-risk"
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "fars" / "processed" / "monthly_national.csv"

os.environ["PYTENSOR_FLAGS"] = "device=cpu,floatX=float64,cxx="


def main():
    df = pd.read_csv(DATA_PATH)

    # Build a proper date index (first of each month)
    df["date"] = pd.to_datetime(df[["YEAR", "MONTH"]].assign(DAY=1))
    df = df.set_index("date").sort_index()

    # Add a linear trend variable and month for seasonality
    df["t"] = range(len(df))
    df["month"] = df.index.month
    df["y"] = df["fatal_crashes"]

    treatment_time = pd.Timestamp("2001-10-01")

    result = cp.InterruptedTimeSeries(
        df,
        treatment_time,
        formula="y ~ 1 + t + C(month)",
        model=cp.pymc_models.LinearRegression(
            sample_kwargs={
                "draws": 2000,
                "tune": 2000,
                "random_seed": 42,
                "progressbar": True,
            }
        ),
    )

    # Print overall summary
    print("\n" + "=" * 60)
    print("FULL POST-PERIOD EFFECT (Oct 2001 – Dec 2004)")
    print("=" * 60)
    summary = result.effect_summary(direction="increase", cumulative=True)
    print(summary)

    # Save the default CausalPy plot
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig, _axes = result.plot(show=False)
    fig.suptitle(
        "Interrupted Time Series: Post-9/11 Fatal Traffic Accidents (through 2004)",
        y=1.02,
    )
    fig.tight_layout()
    fig.savefig(OUT_DIR / "its_extended.png", dpi=150, bbox_inches="tight")
    print(f"\nPlot saved to {OUT_DIR / 'its_extended.png'}")

    # ── Rolling effect by quarter ──
    plot_data = result.get_plot_data()
    post = plot_data.loc[plot_data.index >= treatment_time].copy()
    effect_df = pd.DataFrame({
        "observed": post["y"].values,
        "counterfactual": post["prediction"].values,
    }, index=post.index)
    effect_df["effect"] = effect_df["observed"] - effect_df["counterfactual"]

    effect_df["quarter"] = effect_df.index.to_period("Q")
    quarterly = effect_df.groupby("quarter").agg(
        avg_monthly_effect=("effect", "mean"),
        total_effect=("effect", "sum"),
        months=("effect", "count"),
    )

    print("\n" + "=" * 60)
    print("QUARTERLY BREAKDOWN OF EXCESS FATAL CRASHES")
    print("=" * 60)
    print(quarterly.to_string(float_format="{:.0f}".format))


if __name__ == "__main__":
    main()
