import os
from pathlib import Path

os.environ["PYTENSOR_FLAGS"] = "device=cpu,floatX=float64,cxx="

import causalpy as cp  # type: ignore[import]
import pandas as pd
from pymc_extras.prior import Prior  # type: ignore[import]

OUT_DIR = Path(__file__).resolve().parents[2] / "static" / "img" / "dread-risk"
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "fars" / "processed" / "monthly_national.csv"


def prepare_df():
    # PiecewiseITS needs the time variable as a column, not just the index.
    df = (
        pd.read_csv(DATA_PATH)
        .assign(date=lambda d: pd.to_datetime(d[["YEAR", "MONTH"]].assign(DAY=1)))
        .sort_values("date")
        .assign(
            t=lambda d: range(len(d)),
            month=lambda d: d["date"].dt.month,
            y=lambda d: d["fatal_crashes"],
        )
        .pipe(lambda d: d.assign(t=(d.t - d.t.mean()) / d.t.std()))
    )
    return df.set_index("date").assign(date=df["date"].values)


def main():
    df = prepare_df()

    # PiecewiseITS uses step() and ramp() transforms in the formula.
    # step(date, t0) = 1 if date >= t0 (level change at intervention)
    # ramp(date, t0) = 0 before t0, linearly increasing after (slope change)
    # Together they estimate both an immediate jump and a change in trajectory.
    result = cp.PiecewiseITS(
        df,
        formula="y ~ 1 + t + C(month) + step(date, '2001-10-01') + ramp(date, '2001-10-01')",
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
    print("PIECEWISE ITS EFFECT SUMMARY (Oct 2001 – Dec 2004)")
    print("=" * 60)
    summary = result.effect_summary(direction="two-sided", cumulative=True)
    print(summary)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig, _axes = result.plot(show=False)
    fig.suptitle(
        "Piecewise ITS: Post-9/11 Fatal Traffic Accidents (through 2004)",
        y=1.02,
    )
    fig.tight_layout()
    out_path = OUT_DIR / "its_piecewise.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nPlot saved to {out_path}")


if __name__ == "__main__":
    main()
