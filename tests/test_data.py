import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from prepare_data import INDICATORS, N_DAYS, generate, validate  # noqa: E402


def test_columns_and_size():
    df = generate()
    assert list(df.columns) == ["date", "indicator", "value", "unit", "source", "source_ref"]
    assert len(df) == N_DAYS * len(INDICATORS)


def test_same_seed_same_data():
    assert generate(seed=1).equals(generate(seed=1))


def test_no_missing_and_in_range():
    validate(generate())


def test_everything_labelled_simulated():
    assert (generate()["source"] == "simulated").all()


def test_story_is_visible():
    df = generate()
    sleep = df[df.indicator == "sleep_hours"].reset_index(drop=True)
    assert sleep.loc[19:23, "value"].mean() < sleep.loc[:18, "value"].mean() - 1
    sbp = df[df.indicator == "systolic_bp"].reset_index(drop=True)
    assert sbp.loc[45:, "value"].mean() > sbp.loc[:19, "value"].mean() + 10


def test_validate_rejects_impossible_value():
    df = generate()
    df.loc[df.indicator == "heart_rate", "value"] = 0
    with pytest.raises(ValueError):
        validate(df)
