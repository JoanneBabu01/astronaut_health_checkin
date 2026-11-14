import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from prepare_data import COLUMNS, N_DAYS, generate, validate  # noqa: E402

END = "2026-11-13"


def make(**kw):
    return generate(end_date=END, **kw)


def test_contract_columns_and_rows():
    df = make()
    assert list(df.columns) == COLUMNS
    assert len(df) == N_DAYS


def test_same_seed_same_data():
    assert make(seed=1).equals(make(seed=1))


def test_no_missing_and_in_range():
    validate(make())


def test_ends_on_given_date():
    assert make()["timestamp"].iloc[-1].startswith(END)


def test_planted_problems_reach_red():
    df = make()
    assert df["sleep_hours"].min() < 6          # red sleep
    assert df["mood"].min() <= 2                # red mood
    assert df["blood_glucose"].max() >= 126     # red glucose
    assert df["systolic_bp"].iloc[-1] >= 140    # red blood pressure at the end
    assert 37.3 <= df["body_temp"].max() < 38   # amber temperature


def test_first_three_weeks_are_normal():
    early = make().iloc[:18]
    assert early["sleep_hours"].min() >= 6.9
    assert early["systolic_bp"].max() < 120
    assert early["blood_glucose"].max() <= 99


def test_validate_rejects_impossible_value():
    df = make()
    df["heart_rate"] = 0
    with pytest.raises(ValueError):
        validate(df)


def test_validate_rejects_wrong_columns():
    with pytest.raises(ValueError):
        validate(make().rename(columns={"blood_glucose": "glucose"}))
