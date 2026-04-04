import os

os.environ["PYTENSOR_FLAGS"] = "device=cpu,floatX=float64,cxx="

from pathlib import Path

import causalpy as cp  # type: ignore[import]
import matplotlib.pyplot as plt
import pandas as pd
from pymc_extras.prior import Prior

OUT_DIR = Path(__file__).resolve().parents[2] / "static" / "img" / "dread-risk"
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "fars" / "processed" / "monthly_national.csv"

PLACEBO_YEARS = [1997, 1998, 1999, 2000]
ACTUAL_YEAR = 2001
FORMULA = "y ~ 1 + t + C(month) + C(year)"


def prepare_df():
    return (
        pd.read_csv(DATA_PATH)
        .assign(date=lambda d: pd.to_datetime(d[["YEAR", "MONTH"]].assign(DAY=1)))
        .set_index("date")
        .sort_index()
        .assign(
            t=lambda d: range(len(d)),
            month=lambda d: d.index.month,
            year=lambda d: d["YEAR"],
            y=lambda d: d["fatal_crashes"],
        )
        .pipe(lambda d: d.assign(t=(d.t - d.t.mean()) / d.t.std()))
    )


def run_its(df, treatment_year, formula):
    subset = df[:f"{treatment_year}-12-01"].copy()
    treatment_time = pd.Timestamp(f"{treatment_year}-10-01")

    result = cp.InterruptedTimeSeries(
        subset,
        treatment_time,
        formula=formula,
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
                "progressbar": False,
            }
        ),
    )
    summary = result.effect_summary(direction="increase", cumulative=True)
    return result, summary


def run_and_collect(df, formula, label):
    results = {}
    all_years = PLACEBO_YEARS + [ACTUAL_YEAR]

    for year in all_years:
        kind = "actual" if year == ACTUAL_YEAR else "placebo"
        print(f"\n[{label}] Running ITS for {year} ({kind})...")
        result, summary = run_its(df, year, formula)
        results[year] = summary

        avg = summary.table.loc["average"]
        print(f"  Avg monthly effect: {avg['mean']:.1f} [{avg['hdi_lower']:.1f}, {avg['hdi_upper']:.1f}]")

    return results


def results_to_df(results, all_years):
    return (
        pd.DataFrame({
            year: results[year].table.loc["average"]
            for year in all_years
        })
        .T
        .rename_axis("year")
        .assign(
            is_actual=lambda d: d.index == ACTUAL_YEAR,
            color=lambda d: d["is_actual"].map({True: "#d62728", False: "#1f77b4"}),
        )
    )


def plot_comparison(results_old, results_new, all_years):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

    for ax, results, title in zip(
        axes,
        [results_old, results_new],
        ["Without Year Fixed Effects", "With Year Fixed Effects"],
    ):
        plot_df = results_to_df(results, all_years)
        ax.bar(plot_df.index.astype(str), plot_df["mean"], color=plot_df["color"], width=0.6)
        ax.errorbar(
            plot_df.index.astype(str), plot_df["mean"],
            yerr=[plot_df["mean"] - plot_df["hdi_lower"], plot_df["hdi_upper"] - plot_df["mean"]],
            fmt="none", color="black", capsize=5,
        )
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_ylabel("Avg Monthly Excess Fatal Crashes")
        ax.set_xlabel("Treatment Year (Oct–Dec)")
        ax.set_title(title)

    fig.suptitle("Placebo Tests: Effect of Adding Year Fixed Effects", fontsize=13)
    fig.tight_layout()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "placebo_comparison.png", dpi=150)
    print(f"\nPlot saved to {OUT_DIR / 'placebo_comparison.png'}")


def main():
    df = prepare_df()
    all_years = PLACEBO_YEARS + [ACTUAL_YEAR]

    print("=" * 60)
    print("WITHOUT YEAR FIXED EFFECTS: y ~ 1 + t + C(month)")
    print("=" * 60)
    results_old = run_and_collect(df, "y ~ 1 + t + C(month)", "no year FE")

    print("\n" + "=" * 60)
    print("WITH YEAR FIXED EFFECTS: y ~ 1 + t + C(month) + C(year)")
    print("=" * 60)
    results_new = run_and_collect(df, FORMULA, "year FE")

    plot_comparison(results_old, results_new, all_years)


if __name__ == "__main__":
    main()
