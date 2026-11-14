import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.assessment import assess, assess_row, overall_status  # noqa: E402
from core.thresholds import INDICATORS, THRESHOLDS, get_bands  # noqa: E402

# (indicator, value, expected) taken from the plan's threshold table
CASES = [
    # blood pressure
    ("systolic_bp", 119, "green"), ("systolic_bp", 120, "amber"),
    ("systolic_bp", 139, "amber"), ("systolic_bp", 140, "red"),
    ("systolic_bp", 89, "amber"), ("systolic_bp", 60, "red"),
    ("diastolic_bp", 79, "green"), ("diastolic_bp", 80, "amber"),
    ("diastolic_bp", 89, "amber"), ("diastolic_bp", 90, "red"),
    ("diastolic_bp", 59, "amber"),
    # heart rate: exactly 100 bpm is green
    ("heart_rate", 100, "green"), ("heart_rate", 101, "amber"),
    ("heart_rate", 120, "amber"), ("heart_rate", 121, "red"),
    ("heart_rate", 50, "green"), ("heart_rate", 49, "amber"),
    ("heart_rate", 40, "amber"), ("heart_rate", 39, "red"),
    # glucose
    ("blood_glucose", 99, "green"), ("blood_glucose", 100, "amber"),
    ("blood_glucose", 125, "amber"), ("blood_glucose", 126, "red"),
    ("blood_glucose", 70, "green"), ("blood_glucose", 69, "amber"),
    ("blood_glucose", 55, "amber"), ("blood_glucose", 54, "red"),
    # temperature
    ("body_temp", 36.1, "green"), ("body_temp", 37.2, "green"),
    ("body_temp", 37.3, "amber"), ("body_temp", 37.9, "amber"),
    ("body_temp", 38.0, "red"), ("body_temp", 36.0, "amber"),
    ("body_temp", 35.5, "amber"), ("body_temp", 35.4, "red"),
    # sleep
    ("sleep_hours", 7.0, "green"), ("sleep_hours", 9.0, "green"),
    ("sleep_hours", 6.9, "amber"), ("sleep_hours", 6.0, "amber"),
    ("sleep_hours", 5.9, "red"),
    # mood and stress
    ("mood", 5, "green"), ("mood", 4, "green"), ("mood", 3, "amber"),
    ("mood", 2, "red"), ("mood", 1, "red"),
    ("stress", 1, "green"), ("stress", 2, "green"), ("stress", 3, "amber"),
    ("stress", 4, "red"), ("stress", 5, "red"),
    # exercise
    ("exercise_min", 90, "green"), ("exercise_min", 89, "amber"),
    ("exercise_min", 30, "amber"), ("exercise_min", 29, "red"),
]


@pytest.mark.parametrize("indicator,value,expected", CASES)
def test_assess(indicator, value, expected):
    assert assess(indicator, value) == expected


def test_unknown_indicator_and_missing_value():
    with pytest.raises(ValueError):
        assess("shoe_size", 9)
    with pytest.raises(ValueError):
        assess("heart_rate", float("nan"))


def test_overall_is_worst_single_status():
    ok = {"heart_rate": 64, "sleep_hours": 7.5, "mood": 4}
    assert overall_status(ok) == "green"
    assert overall_status({**ok, "mood": 3}) == "amber"
    assert overall_status({**ok, "systolic_bp": 145}) == "red"
    assert overall_status({"heart_rate": 64, "sleep_hours": 6.5, "mood": 2}) == "red"


def test_overall_with_nothing_to_assess():
    assert overall_status({}) == "unknown"


def test_assess_row_accepts_pandas_series_and_skips_nan():
    row = pd.Series({"heart_rate": 64, "sleep_hours": float("nan"), "mood": 2})
    assert assess_row(row) == {"heart_rate": "green", "mood": "red"}


def test_bands_cover_plot_range_without_gaps():
    for name in INDICATORS:
        bands = get_bands(name)
        lo, hi = THRESHOLDS[name]["plot_range"]
        assert bands[0][0] == lo and bands[-1][1] == hi
        for (_, b1, _), (a2, _, _) in zip(bands, bands[1:]):
            assert b1 == a2


def test_sample_data_first_weeks_green_and_story_goes_red():
    path = Path(__file__).resolve().parents[1] / "data" / "sample_crew_log.csv"
    if not path.exists():
        pytest.skip("sample_crew_log.csv not generated yet")
    df = pd.read_csv(path)
    assert overall_status(df.iloc[0]) == "green"
    statuses = {overall_status(r) for _, r in df.iterrows()}
    assert {"green", "amber", "red"} <= statuses
