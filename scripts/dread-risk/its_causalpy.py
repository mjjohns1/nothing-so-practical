import os
os.environ["PYTENSOR_FLAGS"] = "device=cpu,floatX=float64,cxx="

from pathlib import Path

import causalpy as cp  # type: ignore[import]
import pandas as pd
from pymc_extras.prior import Prior  # type: ignore[import]

OUT_DIR = Path(__file__).resolve().parents[2] / "static" / "img" / "dread-risk"
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "fars" / "processed" / "monthly_national.csv"


def prepare_df(end_date="2001-12-01"):
    return (
        pd.read_csv(DATA_PATH)
        .assign(date=lambda d: pd.to_datetime(d[["YEAR", "MONTH"]].assign(DAY=1)))
        .set_index("date")
        .sort_index()
        .assign(
            t=lambda d: range(len(d)),
            month=lambda d: d.index.month,
            y=lambda d: d["fatal_crashes"],
        )
        .loc[:end_date]
        .pipe(lambda d: d.assign(t=(d.t - d.t.mean()) / d.t.std()))
    )


def main():
    df = prepare_df()
    treatment_time = pd.Timestamp("2001-10-01")

    result = cp.InterruptedTimeSeries(
        df,
        treatment_time,
        formula="y ~ 1 + t + C(month)",
        model=cp.pymc_models.LinearRegression(
            priors={
                "beta": Prior("Normal", mu=0, sigma=500, dims=["treated_units", "coeffs"]),
                "y_hat": Prior(
                    "Normal",
                    sigma=Prior("HalfNormal", sigma=200, dims=["treated_units"]),
                    dims=["obs_ind", "treated_units"],
                ),
            },
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
    summary = result.effect_summary(direction="two-sided", cumulative=True)
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
