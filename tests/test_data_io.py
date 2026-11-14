import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import prepare_data  # noqa: E402
from core.assessment import overall_status  # noqa: E402
from core.data import COLUMNS, load_log, save_entry  # noqa: E402

GOOD = {
    "systolic_bp": 118, "diastolic_bp": 76, "heart_rate": 64,
    "blood_glucose": 92, "body_temp": 36.8, "sleep_hours": 7.5,
    "mood": 4, "stress": 2, "exercise_min": 120,
}


def test_columns_match_the_data_generator():
    assert COLUMNS == prepare_data.COLUMNS


def test_missing_file_gives_empty_frame_with_columns(tmp_path):
    df = load_log(tmp_path / "nope.csv")
    assert df.empty and list(df.columns) == COLUMNS


def test_save_then_load_round_trip(tmp_path):
    path = tmp_path / "log.csv"
    row = save_entry({**GOOD, "timestamp": "2026-11-14 08:00"}, path)
    assert row["astronaut"] == "Commander A" and row["environment"] == "ISS"
    df = load_log(path)
    assert len(df) == 1 and df.loc[0, "heart_rate"] == 64
    assert df.loc[0, "timestamp"].hour == 8


def test_save_appends_and_keeps_old_rows(tmp_path):
    path = tmp_path / "log.csv"
    save_entry({**GOOD, "timestamp": "2026-11-14 08:00"}, path)
    save_entry({**GOOD, "heart_rate": 70, "timestamp": "2026-11-15 08:00"}, path)
    df = load_log(path)
    assert list(df["heart_rate"]) == [64, 70]


def test_appends_to_real_sample_file_without_breaking_it(tmp_path):
    sample = Path(__file__).resolve().parents[1] / "data" / "sample_crew_log.csv"
    if not sample.exists():
        pytest.skip("sample_crew_log.csv not generated yet")
    copy = tmp_path / "copy.csv"
    copy.write_bytes(sample.read_bytes().rstrip(b"\r\n"))   # no trailing newline
    before = len(load_log(copy))
    save_entry({**GOOD, "timestamp": "2099-01-01 08:00"}, copy)
    assert len(load_log(copy)) == before + 1


def test_file_resaved_by_excel_then_appended_still_loads(tmp_path):
    """Excel can rewrite dates as dd-mm-yyyy; our rows are ISO. Both must load."""
    path = tmp_path / "excel.csv"
    path.write_text(
        ",".join(COLUMNS) + "\n"
        "13-11-2026 08:00,Commander A,ISS,111,71,61,87,36.8,7.6,5,2,113\n"
        "14-11-2026 08:00,Commander A,ISS,107,72,65,83,36.9,7.8,4,2,117\n",
        encoding="utf-8",
    )
    save_entry({**GOOD, "timestamp": "2026-11-15 08:00"}, path)
    df = load_log(path)
    assert len(df) == 3
    assert df["timestamp"].iloc[0].month == 11 and df["timestamp"].iloc[0].day == 13
    assert df["timestamp"].iloc[2].day == 15


def test_garbage_timestamp_gives_clear_error(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text(",".join(COLUMNS) + "\nnot-a-date,A,ISS,111,71,61,87,36.8,7.6,5,2,113\n")
    with pytest.raises(ValueError, match="timestamp"):
        load_log(path)


@pytest.mark.parametrize("field,bad", [
    ("heart_rate", 0), ("body_temp", 50), ("mood", 6), ("stress", 0),
    ("sleep_hours", 30), ("systolic_bp", 400), ("exercise_min", -5),
    ("heart_rate", "abc"), ("mood", 3.5),
])
def test_impossible_values_rejected_and_nothing_written(tmp_path, field, bad):
    path = tmp_path / "log.csv"
    with pytest.raises(ValueError):
        save_entry({**GOOD, field: bad}, path)
    assert not path.exists()


def test_missing_reading_rejected(tmp_path):
    entry = dict(GOOD)
    del entry["mood"]
    with pytest.raises(ValueError, match="mood"):
        save_entry(entry, tmp_path / "log.csv")


def test_unknown_environment_rejected(tmp_path):
    with pytest.raises(ValueError):
        save_entry({**GOOD, "environment": "Jupiter"}, tmp_path / "log.csv")


def test_dangerous_but_possible_readings_can_be_logged_and_flagged(tmp_path):
    path = tmp_path / "log.csv"
    row = save_entry({**GOOD, "systolic_bp": 150, "heart_rate": 130}, path)
    assert overall_status(row) == "red"
