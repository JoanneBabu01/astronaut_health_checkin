import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.drcall import (  # noqa: E402
    DISCLAIMER, NO_ADVICE, build_report, call_summary, concerns, suggested_questions,
)
from core.thresholds import INDICATORS  # noqa: E402


def fake_guidance(indicator, status, environment):
    return {
        "meaning": f"{indicator} is {status}",
        "action": f"act on {indicator} in {environment}",
        "escalate": f"escalate {indicator}",
    }


MIXED = {"heart_rate": "green", "sleep_hours": "amber", "systolic_bp": "red",
         "mood": "green", "stress": "amber"}
READINGS = {"heart_rate": 64, "sleep_hours": 6.4, "systolic_bp": 142, "mood": 4, "stress": 3}


def test_concerns_lists_only_amber_and_red_with_red_first():
    found = concerns(MIXED)
    assert [s for _, s in found] == ["red", "amber", "amber"]
    assert found[0][0] == "systolic_bp"
    # amber ones keep the order of the thresholds table
    assert [i for i, s in found if s == "amber"] == [i for i in INDICATORS if MIXED.get(i) == "amber"]


def test_all_green_has_no_concerns():
    assert concerns({i: "green" for i in INDICATORS}) == []


def test_call_summary_uses_the_guidance_function_and_the_environment():
    summary = call_summary(MIXED, "Mars base", fake_guidance)
    assert [s["indicator"] for s in summary][0] == "systolic_bp"
    assert summary[0]["action"] == "act on systolic_bp in Mars base"
    assert summary[0]["word"] == "Act" and summary[1]["word"] == "Watch"


def test_call_summary_survives_empty_guidance():
    summary = call_summary({"mood": "red"}, "ISS", lambda *a: None)
    assert summary[0]["meaning"] == NO_ADVICE and summary[0]["label"] == "Mood"


def test_always_exactly_three_questions():
    for statuses in (MIXED, {i: "green" for i in INDICATORS}, {}, {"mood": "red"}):
        assert len(suggested_questions(statuses, READINGS)) == 3


def test_first_question_names_the_worst_reading():
    first = suggested_questions(MIXED, READINGS)[0]
    assert "systolic blood pressure" in first and "142" in first and "Act" in first


def test_mind_and_body_concerns_change_the_third_question():
    mind = suggested_questions({"stress": "red"}, {})[2]
    body = suggested_questions({"heart_rate": "red"}, {})[2]
    assert "stress" in mind.lower() and mind != body


def test_report_contents():
    now = datetime(2026, 11, 15, 9, 30)
    report = build_report("Commander A", "Mars base", READINGS, MIXED, fake_guidance, now=now)
    assert "Astronaut: Commander A" in report and "Environment: Mars base" in report
    assert "2026-11-15 09:30" in report
    assert "about 12 minutes one way" in report and "24 minutes round trip" in report
    assert "Systolic blood pressure: 142 mmHg  [Act]" in report
    assert "act on systolic_bp in Mars base" in report
    assert report.count("\n1. ") == 1 and "3. " in report
    assert DISCLAIMER in report


def test_report_without_guidance_or_readings_still_works():
    report = build_report(None, "ISS", None, {}, None)
    assert "Astronaut: unknown" in report and "No readings supplied" in report
    assert "every indicator is green" in report.lower()


def test_report_is_plain_text_you_can_send():
    report = build_report("A", "ISS", READINGS, MIXED, fake_guidance)
    assert "<" not in report and isinstance(report, str)


# ---- the real content/guidance.py takes an optional `value` (low versus high advice) ----

_GUIDE = {
    "heart_rate": {"red": {"low": {"meaning": "pulse too low", "action": "sit down", "escalate": "call now"},
                           "high": {"meaning": "pulse too high", "action": "rest", "escalate": "call soon"}}},
    "mood": {"amber": {"meaning": "mood dip", "action": "take a break", "escalate": "if it lasts"}},
}


def joanne_style(indicator, status, environment="ISS", value=None):
    entry = _GUIDE[indicator][status]
    if "meaning" in entry:
        return entry
    direction = "low" if value is not None and value < 60 else "high"
    return entry[direction]


def test_value_is_passed_so_a_low_reading_gets_the_low_advice():
    low = call_summary({"heart_rate": "red"}, "ISS", joanne_style, {"heart_rate": 35})
    high = call_summary({"heart_rate": "red"}, "ISS", joanne_style, {"heart_rate": 130})
    assert low[0]["meaning"] == "pulse too low" and high[0]["meaning"] == "pulse too high"


def test_report_also_uses_the_direction_specific_advice():
    report = build_report("A", "ISS", {"heart_rate": 35}, {"heart_rate": "red"}, joanne_style)
    assert "pulse too low" in report and "pulse too high" not in report


def test_guidance_functions_without_a_value_parameter_still_work():
    summary = call_summary({"mood": "amber"}, "ISS", fake_guidance, {"mood": 3})
    assert summary[0]["action"] == "act on mood in ISS"


def test_a_missing_guidance_entry_does_not_crash_the_panel_logic():
    summary = call_summary({"stress": "red"}, "ISS", joanne_style, {"stress": 5})   # not in _GUIDE
    assert summary[0]["meaning"] == NO_ADVICE
    report = build_report("A", "ISS", {"stress": 5}, {"stress": "red"}, joanne_style)
    assert NO_ADVICE in report


# ---- the Streamlit panel itself ------------------------------------------------

st_testing = pytest.importorskip("streamlit.testing.v1")


def _panel_app():
    from core.drcall import dr_call_panel
    guidance = lambda i, s, e: {"meaning": "M-" + i, "action": "A-" + i, "escalate": "E-" + i}  # noqa: E731
    dr_call_panel({"heart_rate": "red", "mood": "amber", "sleep_hours": "green"}, "ISS",
                  readings={"heart_rate": 130, "mood": 3, "sleep_hours": 7.5},
                  astronaut="Commander A", guidance_fn=guidance)


def test_panel_shows_only_the_call_button_before_connecting():
    at = st_testing.AppTest.from_function(_panel_app).run(timeout=30)
    assert not at.exception
    assert [b.label for b in at.button] == ["Call flight surgeon"]
    assert len(at.success) == 0


def test_panel_connects_and_shows_advice_questions_and_report():
    at = st_testing.AppTest.from_function(_panel_app).run(timeout=30)
    at.button(key="drcall_button").click().run(timeout=30)
    assert not at.exception
    assert len(at.success) == 1
    text = " ".join(m.value for m in at.markdown)
    assert "Resting heart rate: Act" in text and "Mood: Watch" in text
    assert "What to do: A-heart_rate" in text and "When to escalate: E-mood" in text
    assert "A-sleep_hours" not in text                      # green indicators are not listed
    assert len(at.get("download_button")) == 1
    assert "End call" in [b.label for b in at.button]


def test_end_call_returns_to_the_start():
    at = st_testing.AppTest.from_function(_panel_app).run(timeout=30)
    at.button(key="drcall_button").click().run(timeout=30)
    at.button(key="drcall_end").click().run(timeout=30)
    assert not at.exception and len(at.success) == 0


def test_panel_brings_its_own_styles_and_pulses_red_when_something_is_red():
    at = st_testing.AppTest.from_function(_panel_app).run(timeout=30)
    markup = " ".join(m.value for m in at.markdown)
    assert "<style>" in markup and ".drcall-card" in markup
    assert 'class="drcall-card drcall-alert"' in markup
    assert "prefers-reduced-motion" in markup
