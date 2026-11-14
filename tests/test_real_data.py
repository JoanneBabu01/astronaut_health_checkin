"""Tests use small MOCK files that copy the column layout of the real OSDR files."""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from prepare_real_data import OUT_COLUMNS, combine, parse_timepoint, tidy_cbc, tidy_cmp  # noqa: E402


def mock_cbc():
    rows = []
    for crew in ("C001", "C002"):
        for tp in ("L-92", "R+1"):
            rows.append(["WHITE BLOOD CELL COUNT", 5.4, 3.8, 10.8, "Thousand/uL", "CBC", crew, "M", tp])
            rows.append(["HEMOGLOBIN", 14.1, 13.2, 17.1, "g/dL", "CBC", crew, "F", tp])
    rows.append(["MCV", "<0.1", 80.0, 100.0, "fL", "CBC", "C001", "M", "L-92"])  # not a number
    return pd.DataFrame(rows, columns=[
        "ANALYTE", "VALUE", "RANGE_MIN", "RANGE_MAX", "UNITS", "TEST_TYPE",
        "SUBJECT_ID", "SEX", "TEST_DATE"])


def mock_cmp():
    return pd.DataFrame({
        "Sample Name": ["C001_serum_L-3", "C001_serum_R+1", "C002_serum_L-3", "C002_serum_R+1"],
        "albumin_value_gram_per_deciliter": [4.5, 4.2, 4.4, 4.1],
        "albumin_range_min_gram_per_deciliter": [3.6] * 4,
        "albumin_range_max_gram_per_deciliter": [5.1] * 4,
        "albumin_to_globulin_ratio_value": [1.8, 1.7, 1.6, 1.5],
        "albumin_to_globulin_ratio_range_min": [1.0] * 4,
        "albumin_to_globulin_ratio_range_max": [2.5] * 4,
        "alt_value_units_per_liter": [20, 25, 30, 150],
        "alt_range_min_units_per_liter": [9] * 4,
        "alt_max_units_per_liter": [46] * 4,          # real file has no "range" here
        "glucose_value_milligram_per_deciliter": [88, 95, 70, 130],
        "glucose_range_min_milligram_per_deciliter": [65] * 4,
        "glucose_range_max_milligram_per_deciliter": [99] * 4,
        "egfr_african_american_value_milliliter_per_minute_per_1.73_meter_squared": [90] * 4,
        "egfr_african_american_range_min_milliliter_per_minute_per_1.73_meter_squared": [60] * 4,
        "egfr_african_american_range_max_milliliter_per_minute_per_1.73_meter_squared": [200] * 4,
    })


def build():
    return combine([tidy_cbc(mock_cbc()), tidy_cmp(mock_cmp())])


def test_parse_timepoint():
    assert parse_timepoint("L-3") == ("pre-flight", -3)
    assert parse_timepoint("R+194") == ("post-flight", 194)
    with pytest.raises(ValueError):
        parse_timepoint("day 5")


def test_output_columns_and_no_sex_column():
    out, _ = build()
    assert list(out.columns) == OUT_COLUMNS
    assert "SEX" not in out.columns and "sex" not in out.columns


def test_non_numeric_values_skipped_and_counted():
    out, dropped = build()
    assert dropped == 1
    assert "mcv" not in set(out["analyte"])


def test_cmp_wide_columns_are_unpivoted_with_units_and_ranges():
    out, _ = build()
    glucose = out[(out.analyte == "glucose") & (out.crew == "C002") & (out.timepoint == "R+1")].iloc[0]
    assert glucose["value"] == 130 and glucose["unit"] == "mg/dL"
    assert glucose["ref_min"] == 65 and glucose["ref_max"] == 99
    ratio = out[out.analyte == "albumin_to_globulin_ratio"].iloc[0]
    assert ratio["unit"] == ""
    alt = out[out.analyte == "alt"].iloc[0]
    assert alt["ref_max"] == 46     # picked up from the "alt_max_" column name


def test_excluded_analyte_is_left_out():
    out, _ = build()
    assert not out["analyte"].str.startswith("egfr_african").any()


def test_status_uses_the_labs_own_reference_range():
    out, _ = build()
    row = lambda a, c, t: out[(out.analyte == a) & (out.crew == c) & (out.timepoint == t)].iloc[0]
    assert row("glucose", "C001", "L-3")["status"] == "in range"
    assert row("glucose", "C002", "R+1")["status"] == "high"
    assert row("alt", "C002", "R+1")["status"] == "high"


def test_timepoint_order_pre_flight_before_post_flight():
    out, _ = build()
    pre = out[out.phase == "pre-flight"]["timepoint_order"].max()
    post = out[out.phase == "post-flight"]["timepoint_order"].min()
    assert pre < post
    first = out[out.timepoint == "L-92"]["timepoint_order"].iloc[0]
    assert first == 1


def test_every_row_has_a_source():
    out, _ = build()
    assert out["source"].str.startswith("NASA OSDR").all()
