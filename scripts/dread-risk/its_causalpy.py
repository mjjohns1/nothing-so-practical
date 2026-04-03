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

    # Add a linear trend variable (months since start)
    df["t"] = range(len(df))

    # Add month column for seasonality
    df["month"] = df.index.month

    # Outcome variable
    df["y"] = df["fatal_crashes"]

    # Truncate to end of 2001 to match paper's analysis window
    df = df[:"2001-12-01"]

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

    # Print summary
    print("\n" + "=" * 60)
    print("EFFECT SUMMARY")
    print("=" * 60)
    summary = result.effect_summary(direction="increase", cumulative=True)
    print(summary)

    # Save the built-in CausalPy plot
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig, _axes = result.plot(show=False)
    fig.suptitle("Interrupted Time Series: Post-9/11 Fatal Traffic Accidents", y=1.02)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "its_causalpy.png", dpi=150, bbox_inches="tight")
    print(f"\nPlot saved to {OUT_DIR / 'its_causalpy.png'}")


if __name__ == "__main__":
    main()
