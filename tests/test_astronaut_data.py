import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.data import COLUMNS, MAX_NAME_LENGTH, load_log, save_entry  # noqa: E402

GOOD = {
    "systolic_bp": 118, "diastolic_bp": 76, "heart_rate": 64,
    "blood_glucose": 92, "body_temp": 36.8, "sleep_hours": 7.5,
    "mood": 4, "stress": 2, "exercise_min": 120,
}


@pytest.fixture
def log(tmp_path):
    path = tmp_path / "log.csv"
    save_entry({**GOOD, "astronaut": "Commander A", "timestamp": "2026-11-13 08:00"}, path)
    save_entry({**GOOD, "astronaut": "Commander A", "heart_rate": 70, "timestamp": "2026-11-14 08:00"}, path)
    save_entry({**GOOD, "astronaut": "Nova", "heart_rate": 80, "timestamp": "2026-11-14 09:00"}, path)
    return path


def test_only_that_astronauts_rows(log):
    df = load_log("Commander A", path=log)
    assert len(df) == 2 and set(df["astronaut"]) == {"Commander A"}
    assert list(df["heart_rate"]) == [64, 70]


def test_two_astronauts_never_see_each_other(log):
    nova = load_log("Nova", path=log)
    assert len(nova) == 1 and nova.loc[0, "heart_rate"] == 80


def test_name_match_ignores_case_and_edge_spaces(log):
    assert len(load_log("  commander a ", path=log)) == 2


def test_new_name_gives_empty_table_with_the_same_columns(log):
    df = load_log("Brand New", path=log)
    assert df.empty and list(df.columns) == COLUMNS


def test_blank_name_does_not_show_everyone_elses_data(log):
    assert load_log("   ", path=log).empty


def test_no_name_still_returns_everything_for_old_callers(log):
    assert len(load_log(path=log)) == 3


def test_old_call_style_with_a_path_still_works(log):
    assert len(load_log(log)) == 3


def test_missing_file_for_a_name_is_empty_not_an_error(tmp_path):
    df = load_log("Nova", path=tmp_path / "nope.csv")
    assert df.empty and list(df.columns) == COLUMNS


def test_saved_row_carries_the_trimmed_name_and_is_found_again(tmp_path):
    path = tmp_path / "log.csv"
    row = save_entry({**GOOD, "astronaut": "  Orion  "}, path)
    assert row["astronaut"] == "Orion"
    assert len(load_log("orion", path=path)) == 1


def test_missing_name_falls_back_to_the_demo_crew_member(tmp_path):
    path = tmp_path / "log.csv"
    assert save_entry(GOOD, path)["astronaut"] == "Commander A"


@pytest.mark.parametrize("bad", ["x" * (MAX_NAME_LENGTH + 1), "two\nlines"])
def test_unreasonable_names_are_rejected_and_nothing_is_written(tmp_path, bad):
    path = tmp_path / "log.csv"
    with pytest.raises(ValueError, match="name"):
        save_entry({**GOOD, "astronaut": bad}, path)
    assert not path.exists()


def test_name_with_a_comma_survives_the_csv(tmp_path):
    path = tmp_path / "log.csv"
    save_entry({**GOOD, "astronaut": "Doe, Jane"}, path)
    assert len(load_log("Doe, Jane", path=path)) == 1
