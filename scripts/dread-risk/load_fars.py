import zipfile
from pathlib import Path

import pandas as pd

FARS_DIR = Path(__file__).resolve().parents[2] / "data" / "fars"
OUT_DIR = FARS_DIR / "processed"

YEARS = range(1996, 2005)

KEEP_COLS = {"STATE", "MONTH", "DAY", "YEAR", "FATALS", "ROAD_FNC"}

# ROAD_FNC codes (FARS Analytical Reference Guide)
# Rural: 1=Interstate, 2=Principal Arterial, 3=Minor Arterial,
#        4=Major Collector, 5=Minor Collector, 6=Local
# Urban: 11=Interstate, 12=Freeways/Expressways, 13=Principal Arterial,
#        14=Minor Arterial, 15=Collector, 16=Local
INTERSTATE_CODES = {1, 11}


def load_accident_tables() -> pd.DataFrame:
    """Load and concatenate ACCIDENT.CSV from all year ZIPs."""
    frames = []
    for year in YEARS:
        zip_path = FARS_DIR / f"FARS{year}NationalCSV.zip"
        with zipfile.ZipFile(zip_path) as zf:
            with zf.open("ACCIDENT.CSV") as f:
                df = pd.read_csv(f, usecols=lambda c: c in KEEP_COLS, encoding="latin-1")
        # Some early years encode YEAR as 2-digit (e.g. 96); normalize to 4-digit
        if "YEAR" not in df.columns:
            df["YEAR"] = year
        elif df["YEAR"].max() < 100:
            df["YEAR"] = df["YEAR"] + 1900
        frames.append(df)
        print(f"  {year}: {len(df):,} crashes")
    return pd.concat(frames, ignore_index=True)


def build_monthly_national(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly fatal crashes and fatalities, national level."""
    return (
        df.groupby(["YEAR", "MONTH"])
        .agg(fatal_crashes=("FATALS", "size"), fatalities=("FATALS", "sum"))
        .reset_index()
        .sort_values(["YEAR", "MONTH"])
    )


def build_monthly_by_state(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly fatal crashes and fatalities by state."""
    return (
        df.groupby(["YEAR", "MONTH", "STATE"])
        .agg(fatal_crashes=("FATALS", "size"), fatalities=("FATALS", "sum"))
        .reset_index()
        .sort_values(["YEAR", "MONTH", "STATE"])
    )


def build_monthly_by_road_type(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly fatal crashes and fatalities by road functional class."""
    df = df.copy()
    df["is_interstate"] = df["ROAD_FNC"].isin(INTERSTATE_CODES).astype(int)
    return (
        df.groupby(["YEAR", "MONTH", "is_interstate"])
        .agg(fatal_crashes=("FATALS", "size"), fatalities=("FATALS", "sum"))
        .reset_index()
        .sort_values(["YEAR", "MONTH", "is_interstate"])
    )


def main():
    print("Loading FARS ACCIDENT tables (1996-2004)...")
    df = load_accident_tables()
    print(f"\nTotal records: {len(df):,}")
    print(f"Year range: {df['YEAR'].min()}-{df['YEAR'].max()}")
    print(f"Total fatalities: {df['FATALS'].sum():,}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\nBuilding monthly aggregates...")
    national = build_monthly_national(df)
    national.to_csv(OUT_DIR / "monthly_national.csv", index=False)
    print(f"  National: {len(national)} rows -> monthly_national.csv")

    by_state = build_monthly_by_state(df)
    by_state.to_csv(OUT_DIR / "monthly_by_state.csv", index=False)
    print(f"  By state: {len(by_state)} rows -> monthly_by_state.csv")

    by_road = build_monthly_by_road_type(df)
    by_road.to_csv(OUT_DIR / "monthly_by_road_type.csv", index=False)
    print(f"  By road type: {len(by_road)} rows -> monthly_by_road_type.csv")

    print("\nDone! Files saved to", OUT_DIR)


if __name__ == "__main__":
    main()
