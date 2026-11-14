"""Turn the two NASA OSDR Inspiration4 lab files into one tidy table.

Inputs (download them yourself from osdr.nasa.gov; do NOT commit the raw files):
  --cbc  the complete blood count CSV   (OSD-569, "..._CBC.upload_SUBMITTED.csv")
  --cmp  the comprehensive metabolic panel CSV (OSD-575, "CMP_TRANSFORMED.csv")

Output: data/real_inspiration4_labs.csv  (one row per crew member, timepoint, analyte)

Example (from the repo root):
  python scripts/prepare_real_data.py --cbc "C:\\OSDR\\LSDS-7_Complete_Blood_Count_CBC.upload_SUBMITTED.csv" --cmp "C:\\OSDR\\LSDS-8_Comprehensive_Metabolic_Panel_\\CMP_TRANSFORMED.csv"

Timepoints: L-n = n days before launch, R+n = n days after return.
The SEX column in the CBC file is deliberately left out; we do not need it.
"""
import argparse
import re
from pathlib import Path

import pandas as pd

OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "real_inspiration4_labs.csv"

SOURCES = {
    "CBC": "NASA OSDR OSD-569 (Inspiration4 complete blood count)",
    "CMP": "NASA OSDR OSD-575 (Inspiration4 comprehensive metabolic panel)",
}
OUT_COLUMNS = [
    "crew", "timepoint", "phase", "timepoint_order", "test", "analyte",
    "value", "unit", "ref_min", "ref_max", "status", "source",
]
# Race-adjusted eGFR is not useful for this app, so it is left out.
EXCLUDE_ANALYTES = {"egfr_african_american"}

UNIT_NAMES = {
    "gram_per_deciliter": "g/dL",
    "milligram_per_deciliter": "mg/dL",
    "units_per_liter": "U/L",
    "millimol_per_liter": "mmol/L",
    "milliliter_per_minute_per_1.73_meter_squared": "mL/min/1.73m2",
}


def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", str(text).strip().lower()).strip("_")


def parse_timepoint(timepoint):
    """'L-3' -> ('pre-flight', -3); 'R+194' -> ('post-flight', 194)."""
    m = re.fullmatch(r"([LR])([+-])(\d+)", str(timepoint).strip())
    if not m:
        raise ValueError(f"Unrecognised timepoint {timepoint!r} (expected like L-3 or R+1)")
    days = int(m.group(3))
    if m.group(1) == "L":
        return "pre-flight", -days
    return "post-flight", days


def tidy_cbc(df):
    df = df.rename(columns=lambda c: str(c).strip())
    needed = {"ANALYTE", "VALUE", "RANGE_MIN", "RANGE_MAX", "UNITS", "SUBJECT_ID", "TEST_DATE"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"CBC file is missing columns: {sorted(missing)}")
    return pd.DataFrame({
        "crew": df["SUBJECT_ID"].astype(str).str.strip(),
        "timepoint": df["TEST_DATE"].astype(str).str.strip(),
        "test": "CBC",
        "analyte": df["ANALYTE"].map(slug),
        "value": pd.to_numeric(df["VALUE"], errors="coerce"),
        "unit": df["UNITS"].astype(str).str.strip(),
        "ref_min": pd.to_numeric(df["RANGE_MIN"], errors="coerce"),
        "ref_max": pd.to_numeric(df["RANGE_MAX"], errors="coerce"),
    })


def tidy_cmp(df):
    """The CMP file is wide: <analyte>_value_<unit>, <analyte>_range_min_<unit>, ..."""
    df = df.rename(columns=lambda c: str(c).strip())
    if "Sample Name" not in df.columns:
        raise ValueError("CMP file has no 'Sample Name' column")
    parts = df["Sample Name"].astype(str).str.split("_")
    crew, timepoint = parts.str[0], parts.str[-1]

    frames = []
    for col in df.columns:
        m = re.match(r"^(?P<name>.+?)_value(?:_(?P<unit>.+))?$", col)
        if not m:
            continue
        name, unit = m.group("name"), m.group("unit")
        suffix = f"_{unit}" if unit else ""
        min_col = f"{name}_range_min{suffix}"
        max_col = next((c for c in (f"{name}_range_max{suffix}", f"{name}_max{suffix}")
                        if c in df.columns), None)
        frames.append(pd.DataFrame({
            "crew": crew,
            "timepoint": timepoint,
            "test": "CMP",
            "analyte": slug(name),
            "value": pd.to_numeric(df[col], errors="coerce"),
            "unit": UNIT_NAMES.get(unit, (unit or "").replace("_", " ")),
            "ref_min": pd.to_numeric(df[min_col], errors="coerce") if min_col in df.columns else float("nan"),
            "ref_max": pd.to_numeric(df[max_col], errors="coerce") if max_col else float("nan"),
        }))
    if not frames:
        raise ValueError("No '<analyte>_value_<unit>' columns found in the CMP file")
    return pd.concat(frames, ignore_index=True)


def combine(frames):
    df = pd.concat(frames, ignore_index=True)
    df = df[~df["analyte"].isin(EXCLUDE_ANALYTES)]
    dropped = int(df["value"].isna().sum())
    df = df.dropna(subset=["value"]).copy()

    parsed = df["timepoint"].map(parse_timepoint)
    df["phase"] = parsed.str[0]
    df["_days"] = parsed.str[1]
    # pre-flight (all negative) sorts before post-flight (all positive) by day offset
    order = sorted(df["_days"].unique())
    df["timepoint_order"] = df["_days"].map({d: i + 1 for i, d in enumerate(order)})

    df["status"] = "in range"
    df.loc[df["value"] < df["ref_min"], "status"] = "low"
    df.loc[df["value"] > df["ref_max"], "status"] = "high"
    df.loc[df["ref_min"].isna() & df["ref_max"].isna(), "status"] = "no range"

    df["source"] = df["test"].map(SOURCES)
    df = df.sort_values(["crew", "timepoint_order", "test", "analyte"]).reset_index(drop=True)
    return df[OUT_COLUMNS], dropped


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cbc", type=Path, help="complete blood count CSV (OSD-569)")
    parser.add_argument("--cmp", type=Path, help="comprehensive metabolic panel CSV (OSD-575)")
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    args = parser.parse_args()
    if not (args.cbc or args.cmp):
        parser.error("give at least one of --cbc / --cmp")

    frames = []
    if args.cbc:
        frames.append(tidy_cbc(pd.read_csv(args.cbc)))
    if args.cmp:
        frames.append(tidy_cmp(pd.read_csv(args.cmp)))
    out, dropped = combine(frames)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)
    print(f"Wrote {len(out)} rows to {args.out}")
    print(f"  crew: {out['crew'].nunique()}  timepoints: {out['timepoint'].nunique()}  analytes: {out['analyte'].nunique()}")
    print(f"  rows skipped because the value was not a number: {dropped}")


if __name__ == "__main__":
    main()
