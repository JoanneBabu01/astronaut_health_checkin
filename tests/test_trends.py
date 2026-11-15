import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.assessment import (  # noqa: E402
    AMBER_PENALTY, RED_PENALTY, assess_row, health_score, trend_flags,
)
from core.data import load_log  # noqa: E402

NORMAL = {"sleep_hours": 7.5, "mood": 4, "stress": 2,
          "systolic_bp": 110, "diastolic_bp": 70, "heart_rate": 62}


def make_log(days, start="2026-11-01", **overrides):
    """A daily log with normal values; overrides are lists (padded with the normal value)."""
    rows = []
    for i in range(days):
        row = {"timestamp": pd.Timestamp(start) + pd.Timedelta(days=i, hours=8)}
        for name, normal in NORMAL.items():
            values = overrides.get(name)
            row[name] = values[i] if values is not None and i < len(values) else normal
        rows.append(row)
    return pd.DataFrame(rows)


def ids(flags):
    return [f["id"] for f in flags]


def by_id(flags, flag_id):
    return next(f for f in flags if f["id"] == flag_id)


# ---------------------------------------------------------------- health score

def test_all_green_is_100():
    assert health_score({"heart_rate": "green", "mood": "green"}) == 100
    assert health_score({}) == 100


def test_each_amber_and_red_subtracts():
    assert health_score({"a": "amber"}) == 100 - AMBER_PENALTY
    assert health_score({"a": "red"}) == 100 - RED_PENALTY
    assert health_score({"a": "amber", "b": "red", "c": "green"}) == 100 - AMBER_PENALTY - RED_PENALTY


def test_score_never_goes_below_zero_and_ignores_unknown_words():
    assert health_score({str(i): "red" for i in range(20)}) == 0
    assert health_score({"a": "unknown"}) == 100


def test_score_works_on_real_assessments():
    row = {"heart_rate": 64, "sleep_hours": 5.0, "mood": 3}      # green, red, amber
    assert health_score(assess_row(row)) == 100 - RED_PENALTY - AMBER_PENALTY


# ---------------------------------------------------------------- streak flags

def test_three_short_nights_in_a_row_is_a_red_active_flag():
    flags = trend_flags(make_log(6, sleep_hours=[7.5, 7.5, 7.5, 5.5, 5.0, 5.8]))
    flag = by_id(flags, "sleep_short")
    assert flag["status"] == "red" and flag["active"] is True
    assert "under 6 hours" in flag["message"] and flag["label"] == "Sleep"
    assert flag["start"] == pd.Timestamp("2026-11-04") and flag["end"] == pd.Timestamp("2026-11-06")


def test_two_short_nights_is_not_enough():
    flags = trend_flags(make_log(5, sleep_hours=[7.5, 7.5, 7.5, 5.5, 5.0]))
    assert "sleep_short" not in ids(flags) and "sleep_low" not in ids(flags)


def test_a_missed_day_breaks_the_streak():
    log = make_log(6, sleep_hours=[7.5, 7.5, 7.5, 5.5, 5.0, 5.8])
    log = log[log["timestamp"].dt.day != 5].reset_index(drop=True)      # no check-in on the 5th
    assert "sleep_short" not in ids(trend_flags(log))


def test_a_finished_streak_stays_as_history_but_is_not_active():
    flags = trend_flags(make_log(8, sleep_hours=[5.5, 5.0, 5.8]))
    flag = by_id(flags, "sleep_short")
    assert flag["active"] is False and flag["end"] == pd.Timestamp("2026-11-03")


def test_red_wins_over_amber_for_the_same_indicator_and_day():
    flags = trend_flags(make_log(3, sleep_hours=[5.5, 5.0, 5.8]))
    assert ids(flags).count("sleep_short") == 1 and "sleep_low" not in ids(flags)


def test_milder_streak_is_amber():
    flags = trend_flags(make_log(4, sleep_hours=[6.5, 6.4, 6.8, 6.6]))
    assert by_id(flags, "sleep_low")["status"] == "amber"
    assert "sleep_short" not in ids(flags)


def test_mood_streaks():
    low = trend_flags(make_log(4, mood=[4, 2, 1, 2]))
    assert by_id(low, "mood_low")["status"] == "red"
    dip = trend_flags(make_log(4, mood=[4, 3, 3, 3]))
    assert by_id(dip, "mood_dip")["status"] == "amber" and "mood_low" not in ids(dip)


def test_stress_streaks():
    high = trend_flags(make_log(3, stress=[4, 5, 4]))
    assert by_id(high, "stress_high")["status"] == "red"
    up = trend_flags(make_log(3, stress=[3, 3, 3]))
    assert by_id(up, "stress_up")["status"] == "amber"


def test_normal_days_give_no_flags():
    assert trend_flags(make_log(20)) == []


# ---------------------------------------------------------------- rising averages

def test_systolic_average_rising_is_flagged_with_the_size_of_the_rise():
    flags = trend_flags(make_log(14, systolic_bp=[110] * 7 + [122] * 7))
    flag = by_id(flags, "systolic_rising")
    assert flag["status"] == "amber" and flag["active"] is True
    assert "12 mmHg" in flag["message"]


def test_small_rise_and_too_little_history_are_not_flagged():
    assert trend_flags(make_log(14, systolic_bp=[110] * 7 + [114] * 7)) == []
    assert trend_flags(make_log(10, systolic_bp=[110] * 5 + [130] * 5)) == []


def test_rise_that_already_happened_is_history():
    flags = trend_flags(make_log(24, systolic_bp=[110] * 7 + [122] * 17))
    flag = by_id(flags, "systolic_rising")
    assert flag["active"] is False


# ---------------------------------------------------------------- input handling

def test_empty_none_and_odd_frames_give_no_flags():
    assert trend_flags(None) == []
    assert trend_flags(make_log(0)) == []
    assert trend_flags(pd.DataFrame({"x": [1]})) == []


def test_missing_indicator_columns_are_skipped():
    log = make_log(5, sleep_hours=[5, 5, 5, 5, 5])[["timestamp", "sleep_hours"]]
    assert ids(trend_flags(log)) == ["sleep_short"]


def test_unsorted_rows_and_two_readings_in_a_day():
    log = make_log(4, sleep_hours=[5.5, 5.0, 5.8, 5.2])
    extra = log.iloc[[1]].copy()
    extra["timestamp"] = extra["timestamp"] - pd.Timedelta(hours=4)      
    extra["sleep_hours"] = 9.0                                           
    shuffled = pd.concat([log, extra]).sample(frac=1, random_state=1)
    assert "sleep_short" in ids(trend_flags(shuffled))


def test_timestamps_given_as_text_still_work():
    log = make_log(4, sleep_hours=[5.5, 5.0, 5.8, 5.2])
    log["timestamp"] = log["timestamp"].dt.strftime("%d-%m-%Y %H:%M")    
    assert "sleep_short" in ids(trend_flags(log))


def test_order_is_active_first_then_red_then_newest():
    sleep = [5.5, 5.0, 5.8] + [7.5] * 7                                  
    systolic = [110] * 10 + [122] * 7                                     
    stress = [3, 3, 3] + [2] * 14                                         
    flags = trend_flags(make_log(17, sleep_hours=sleep, systolic_bp=systolic, stress=stress))
    assert flags[0]["id"] == "systolic_rising" and flags[0]["active"]
    past = [f for f in flags if not f["active"]]
    assert past[0]["status"] == "red"
    assert all(a["active"] >= b["active"] for a, b in zip(flags, flags[1:]))


# ---------------------------------------------------------------- the demo data

def test_demo_data_tells_its_story():
    path = Path(__file__).resolve().parents[1] / "data" / "sample_crew_log.csv"
    if not path.exists():
        pytest.skip("sample_crew_log.csv not generated yet")
    flags = trend_flags(load_log("Commander A", path=path))
    assert {"sleep_short", "stress_high", "mood_dip"} <= set(ids(flags))     
    assert by_id(flags, "systolic_rising")["active"]                           
    assert flags[0]["active"]
