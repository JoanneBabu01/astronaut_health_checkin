"""Dr. Call: a simulated call to the flight surgeon.

The logic (who needs attention, the report text, the suggested questions) is
plain Python and tested. Only dr_call_panel() uses Streamlit.

For education and demonstration, not medical advice. Nobody is really called.
"""
import inspect
from datetime import datetime

from core.environments import get_environment
from core.thresholds import INDICATORS, THRESHOLDS

try:
    from core.charts import status_words as STATUS_WORDS   # {"green": "OK", ...}
except ImportError:
    STATUS_WORDS = {"green": "OK", "amber": "Watch", "red": "Act"}

GLASS_CLASS = "drcall-card"
ALERT_CLASS = "drcall-alert"

_CSS = """
.drcall-card { background: rgba(20, 26, 60, 0.72); border: 1px solid rgba(150, 170, 255, 0.35);
  border-radius: 14px; padding: 12px 14px; margin-bottom: 8px; color: #e8ecff;
  backdrop-filter: blur(6px); }
.drcall-alert { border-color: rgba(255, 90, 90, 0.9); animation: drcall-pulse 2.4s ease-in-out infinite; }
@keyframes drcall-pulse { 0%, 100% { box-shadow: 0 0 6px rgba(255, 90, 90, 0.25); }
  50% { box-shadow: 0 0 18px rgba(255, 90, 90, 0.6); } }
@media (prefers-reduced-motion: reduce) { .drcall-alert { animation: none; } }
"""

NO_ADVICE = "No advice text is available for this reading yet."

DISCLAIMER = ("For education and demonstration, not medical advice. "
              "This is a simulated call: nobody is actually connected.")

_ORDER = {"red": 0, "amber": 1}


def _word(status):
    return STATUS_WORDS.get(status, status)


def _label(indicator):
    return THRESHOLDS[indicator]["label"]


def _reading_text(indicator, readings):
    value = (readings or {}).get(indicator)
    if value is None:
        return None
    unit = THRESHOLDS[indicator]["unit"]
    return f"{value:g} {unit}".strip() if isinstance(value, (int, float)) else f"{value} {unit}".strip()


def concerns(statuses):
    """Indicators that are amber or red, red first, in the order of the thresholds table."""
    found = [(i, statuses[i]) for i in INDICATORS if statuses.get(i) in _ORDER]
    return sorted(found, key=lambda pair: _ORDER[pair[1]])


def _call_guidance(get_guidance, indicator, status, environment, value):
    """Ask the advice function for text. Never raises.

    content/guidance.py takes an optional `value` so it can tell a too-low reading
    from a too-high one, so we pass it whenever the function accepts it. A missing
    entry gives {} instead of crashing the panel.
    """
    try:
        params = inspect.signature(get_guidance).parameters
        takes_value = "value" in params or any(
            p.kind is inspect.Parameter.VAR_KEYWORD for p in params.values())
    except (TypeError, ValueError):
        takes_value = False
    try:
        if takes_value and value is not None:
            return get_guidance(indicator, status, environment, value=value) or {}
        return get_guidance(indicator, status, environment) or {}
    except (KeyError, TypeError):
        return {}


def call_summary(statuses, environment, get_guidance, readings=None):
    """One dict per amber or red indicator with the advice text.

    get_guidance(indicator, status, environment, value=None) must return a dict
    with the keys meaning, action and escalate (see content/guidance.py).
    `readings` ({indicator: value}) lets it pick low-versus-high advice.
    """
    env = get_environment(environment)["name"]
    summary = []
    for indicator, status in concerns(statuses):
        advice = _call_guidance(get_guidance, indicator, status, env,
                                (readings or {}).get(indicator))
        if not any(advice.get(k) for k in ("meaning", "action", "escalate")):
            advice = {"meaning": NO_ADVICE}
        summary.append({
            "indicator": indicator,
            "label": _label(indicator),
            "status": status,
            "word": _word(status),
            "meaning": advice.get("meaning", ""),
            "action": advice.get("action", ""),
            "escalate": advice.get("escalate", ""),
        })
    return summary


def suggested_questions(statuses, readings=None):
    """Exactly three questions to ask the flight surgeon."""
    found = concerns(statuses)
    if found:
        worst, status = found[0]
        reading = _reading_text(worst, readings)
        if reading:
            first = (f"My {_label(worst).lower()} is {reading} ({_word(status)}). "
                     "Is that expected given my recent days, and what should I do first?")
        else:
            first = (f"My {_label(worst).lower()} is flagged '{_word(status)}'. "
                     "What should I do first?")
    else:
        first = "Everything looks fine today. Is there anything I should keep doing to stay on track?"

    second = ("How long should I wait before rechecking, and what result would mean "
              "I should call you straight back?")

    mind_body = {"sleep_hours", "stress", "mood"}
    if any(i in mind_body for i, _ in found):
        third = "Are my sleep, stress and mood connected here, and would you change my routine?"
    else:
        third = "Could this be linked to my exercise, food or sleep over the last few days?"
    return [first, second, third]


def build_report(astronaut, environment, readings, statuses, get_guidance=None, now=None):
    """Plain-text report the astronaut can download and send."""
    env = get_environment(environment)
    now = now or datetime.now()
    lines = [
        "REPORT FOR THE FLIGHT SURGEON (simulated, for education and demonstration)",
        "",
        f"Astronaut: {astronaut or 'unknown'}",
        f"Environment: {env['label']}",
        f"Generated: {now.strftime('%Y-%m-%d %H:%M')}",
        f"Signal delay: about {env['one_way_text']} one way "
        f"(about {env['round_trip_text']} round trip)",
        "",
        "LATEST READINGS",
    ]
    shown = 0
    for indicator in INDICATORS:
        reading = _reading_text(indicator, readings)
        if reading is None:
            continue
        status = statuses.get(indicator)
        tag = f"  [{_word(status)}]" if status else ""
        lines.append(f"- {_label(indicator)}: {reading}{tag}")
        shown += 1
    if not shown:
        lines.append("- No readings supplied")

    lines += ["", "NEEDS ATTENTION"]
    found = concerns(statuses)
    if not found:
        lines.append("- Nothing: every indicator is green.")
    for indicator, status in found:
        lines.append(f"- {_label(indicator)} ({_word(status)})")
        if get_guidance:
            advice = _call_guidance(get_guidance, indicator, status, env["name"],
                                    (readings or {}).get(indicator))
            if not any(advice.get(k) for k in ("meaning", "action", "escalate")):
                advice = {"meaning": NO_ADVICE}
            for key, title in (("meaning", "What it means"), ("action", "What to do"),
                               ("escalate", "When to escalate")):
                if advice.get(key):
                    lines.append(f"    {title}: {advice[key]}")

    lines += ["", "SUGGESTED QUESTIONS"]
    lines += [f"{n}. {q}" for n, q in enumerate(suggested_questions(statuses, readings), 1)]
    lines += ["", DISCLAIMER]
    return "\n".join(lines)


# ---------------------------------------------------------------- Streamlit part

def _simulate_connection(st, time, env):
    wait = env["screen_wait_s"]
    bar = st.progress(0, text="Connecting to the flight surgeon...")
    steps = 20
    for step in range(steps):
        time.sleep(wait / steps)
        bar.progress((step + 1) / steps,
                     text=(f"Signal delay: about {env['one_way_text']} one way "
                           f"(shown here as {wait:g} seconds)"))
    bar.empty()


def dr_call_panel(statuses, environment, readings=None, astronaut=None, guidance_fn=None):
    """Draw the Dr. Call panel (put it in the sidebar or on the Home page).

    statuses:    {indicator: "green"|"amber"|"red"}  (use assess_row)
    environment: "ISS", "Transit", "Lunar base" or "Mars base"
    readings:    optional {indicator: value} for the latest check-in, used in the report
    astronaut:   optional name for the report
    """
    import html
    import time

    import streamlit as st

    if guidance_fn is None:
        from content.guidance import get_guidance as guidance_fn

    env = get_environment(environment)
    state_key = "drcall_connected_to"
    any_red = any(s == "red" for s in statuses.values())

    css = GLASS_CLASS + (" " + ALERT_CLASS if any_red else "")
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="{css}"><strong>Dr. Call</strong><br>'
        f'{html.escape(env["label"])}: signal delay about {html.escape(env["one_way_text"])} one way.'
        f'</div>',
        unsafe_allow_html=True,
    )

    if st.button("Call flight surgeon", key="drcall_button"):
        _simulate_connection(st, time, env)
        st.session_state[state_key] = env["name"]

    if st.session_state.get(state_key) != env["name"]:
        st.caption(DISCLAIMER)
        return

    st.success("Connected to the flight surgeon (simulated)")
    st.caption(env["delay_note"])
    for item in call_summary(statuses, env["name"], guidance_fn, readings):
        st.markdown(f"**{item['label']}: {item['word']}**")
        for key, title in (("meaning", "What it means"), ("action", "What to do"),
                           ("escalate", "When to escalate")):
            if item[key]:
                st.write(f"{title}: {item[key]}")
    if not concerns(statuses):
        st.write("Every indicator is green. Nothing needs the flight surgeon right now.")

    st.markdown("**Questions you could ask**")
    for question in suggested_questions(statuses, readings):
        st.write(f"- {question}")

    report = build_report(astronaut, env["name"], readings, statuses, guidance_fn)
    st.download_button("Report for the flight surgeon", data=report,
                       file_name="flight_surgeon_report.txt", mime="text/plain",
                       key="drcall_download")
    if st.button("End call", key="drcall_end"):
        st.session_state.pop(state_key, None)
        st.rerun()
    st.caption(DISCLAIMER)
