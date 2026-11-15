import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.data import ENVIRONMENTS  # noqa: E402
from core.environments import ENVIRONMENT_SETTINGS, format_duration, get_environment  # noqa: E402


def test_every_environment_the_data_layer_accepts_has_settings():
    assert set(ENVIRONMENTS) == set(ENVIRONMENT_SETTINGS)


@pytest.mark.parametrize("seconds,text", [
    (1, "1 second"), (1.3, "1.3 seconds"), (3, "3 seconds"),
    (60, "1 minute"), (300, "5 minutes"), (720, "12 minutes"), (90, "1.5 minutes"),
])
def test_format_duration(seconds, text):
    assert format_duration(seconds) == text


def test_moon_is_about_one_point_three_seconds_one_way():
    moon = get_environment("Lunar base")
    assert moon["one_way_delay_s"] == 1.3 and moon["one_way_text"] == "1.3 seconds"


def test_mars_delay_is_in_the_real_3_to_22_minute_range_and_shown_as_5_or_6_seconds():
    mars = get_environment("Mars base")
    assert 3 * 60 <= mars["one_way_delay_s"] <= 22 * 60
    assert 5 <= mars["screen_wait_s"] <= 6
    assert mars["round_trip_text"] == "24 minutes"


def test_delays_grow_with_distance():
    d = {n: ENVIRONMENT_SETTINGS[n]["one_way_delay_s"] for n in ENVIRONMENT_SETTINGS}
    assert d["ISS"] <= d["Lunar base"] < d["Transit"] < d["Mars base"]


def test_on_screen_waits_stay_short_for_a_demo():
    assert all(s["screen_wait_s"] <= 6 for s in ENVIRONMENT_SETTINGS.values())


def test_lookup_ignores_case_and_unknown_names_fall_back_to_the_iss():
    assert get_environment("mars base")["name"] == "Mars base"
    assert get_environment("Jupiter")["name"] == "ISS"
    assert get_environment(None)["name"] == "ISS"


def test_gravity_values():
    assert get_environment("ISS")["gravity_g"] == 0
    assert get_environment("Lunar base")["gravity_g"] == pytest.approx(0.166, abs=0.01)
    assert get_environment("Mars base")["gravity_g"] == pytest.approx(0.38, abs=0.01)


def test_lookup_returns_a_copy():
    get_environment("ISS")["one_way_delay_s"] = 999
    assert ENVIRONMENT_SETTINGS["ISS"]["one_way_delay_s"] == 1.0
