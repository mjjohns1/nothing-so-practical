import os
from pathlib import Path
os.environ["PYTENSOR_FLAGS"] = "device=cpu,floatX=float64,cxx="

import causalpy as cp  # type: ignore[import]
import pandas as pd
from pymc_extras.prior import Prior  # type: ignore[import]

OUT_DIR = Path(__file__).resolve().parents[2] / "static" / "img" / "dread-risk"
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "fars" / "processed" / "monthly_national.csv"


def prepare_df():
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
        .pipe(lambda d: d.assign(t=(d.t - d.t.mean()) / d.t.std()))
    )


def quarterly_breakdown(result, treatment_time):
    return (
        result.get_plot_data()
        .loc[lambda d: d.index >= treatment_time]
        .assign(
            effect=lambda d: d["y"] - d["prediction"],
            quarter=lambda d: d.index.to_period("Q"),
        )
        .groupby("quarter")
        .agg(
            avg_monthly_effect=("effect", "mean"),
            total_effect=("effect", "sum"),
            months=("effect", "count"),
        )
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

    print("\n" + "=" * 60)
    print("FULL POST-PERIOD EFFECT (Oct 2001 – Dec 2004)")
    print("=" * 60)
    print(result.effect_summary(direction="two-sided", cumulative=True))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig, _axes = result.plot(show=False)
    fig.suptitle(
        "Interrupted Time Series: Post-9/11 Fatal Traffic Accidents (through 2004)",
        y=1.02,
    )
    fig.tight_layout()
    fig.savefig(OUT_DIR / "its_extended.png", dpi=150, bbox_inches="tight")
    print(f"\nPlot saved to {OUT_DIR / 'its_extended.png'}")

    quarterly = quarterly_breakdown(result, treatment_time)
    print("\n" + "=" * 60)
    print("QUARTERLY BREAKDOWN OF EXCESS FATAL CRASHES")
    print("=" * 60)
    print(quarterly.to_string(float_format="{:.0f}".format))


if __name__ == "__main__":
    main()
