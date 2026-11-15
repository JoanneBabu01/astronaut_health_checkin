# Owner: Role 3
import math
import pandas as pd
import streamlit as st
from ui.bg_blue import background
from ui.sidebar import sidebar
from ui.dashboard import inject_css, panel_title, pill
from core.thresholds import INDICATORS, THRESHOLDS

bg= background()
st.set_page_config(page_title="LEARN · Learn", page_icon="📚", layout="wide")
env = sidebar()
inject_css()

st.title("Learn")
st.caption("How to take each measurement, why it matters in space, and what the colours mean.")

HOW_TO = {
    "systolic_bp": ("🫀", "Blood pressure",
        ["Rest for 5 minutes first, without talking.",
         "Anchor yourself so you're still, with the cuff on your bare upper arm at heart level.",
         "Use the same arm each time. Take two readings a minute apart and log the second."],
        "Fluid shifts towards the head in microgravity, which changes blood pressure. "
        "Readings can also drop on return to gravity, causing dizziness."),
    "heart_rate": ("❤️", "Resting heart rate",
        ["Measure at rest, ideally just after waking or after the blood pressure reading.",
         "Count for a full 60 seconds, or read it from the monitor."],
        "The heart adapts to working without gravity. A steady rise over days can signal "
        "stress, poor sleep, illness or lost fitness."),
    "blood_glucose": ("🩸", "Blood glucose",
        ["Measure in the morning before eating.",
         "Clean the fingertip, use a fresh lancet, and apply the drop to the meter strip."],
        "Inactivity, stress and diet changes on long missions can push blood sugar out of range."),
    "body_temp": ("🌡️", "Body temperature",
        ["Use the same thermometer and method every time.",
         "Wait at least 30 minutes after exercise or hot drinks."],
        "The immune system changes in space, so a fever is worth catching early, "
        "especially in a closed cabin where germs spread easily."),
    "sleep_hours": ("🌙", "Sleep",
        ["Log the hours from falling asleep to waking, each morning."],
        "Light, noise and busy schedules make sleep in space harder. Short sleep affects "
        "mood, focus and safety."),
    "mood": ("🙂", "Mood and stress",
        ["Rate both honestly from 1 to 5, at the same time each day.",
         "There are no wrong answers; the trend over days matters most."],
        "Isolation and confinement are among the main hazards of long missions. "
        "Tracking mood helps spot problems before they grow."),
    "exercise_min": ("🦴", "Exercise",
        ["Log the total minutes of planned exercise today."],
        "Without gravity, bones and muscles weaken. Daily exercise is the main protection."),
}

HAZARDS = [
    ("☢️", "Space radiation", "Raises long-term risks to health. Watch for fatigue and signs of infection."),
    ("🔒", "Isolation and confinement", "Affects mood, stress, sleep and teamwork."),
    ("🌍", "Distance from Earth", "Help is far away. On Mars, a message can take up to about 20 minutes "
                                  "one way, so the crew must assess and act first."),
    ("🪐", "Gravity fields", "Bone and muscle loss, fluid shifts, and heart and blood pressure changes."),
    ("🏠", "Hostile or closed environments", "Temperature, noise, air quality and microbes all affect health."),
]

tab1, tab2, tab3 = st.tabs(["📏 How to measure", "🚀 Space hazards", "🚦 What the colours mean"])

with tab1:
    cols = st.columns(2, gap="medium")
    for i, (key, (icon, title, steps, why)) in enumerate(HOW_TO.items()):
        with cols[i % 2]:
            with st.container(key=f"panel_how_{key}"):
                panel_title(f"{icon} {title}")
                for n, step in enumerate(steps, 1):
                    st.write(f"{n}. {step}")
                st.caption(f"**Why it matters in space:** {why}")

with tab2:
    st.write("NASA's Human Research Program groups the risks of spaceflight into five hazards. "
             "Each one affects the health indicators this app tracks.")
    for icon, title, text in HAZARDS:
        with st.container(key=f"panel_hz_{title[:6].replace(' ', '_')}"):
            panel_title(f"{icon} {title}")
            st.write(text)
    st.caption("Source: [NASA Human Research Program, the five hazards of human spaceflight]"
               "(https://www.nasa.gov/hrp/hazards)")

with tab3:
    c1, c2, c3 = st.columns(3, gap="medium")
    c1.markdown(f"{pill('green')}<br>Keep going. Next check-in as scheduled.", unsafe_allow_html=True)
    c2.markdown(f"{pill('amber')}<br>Follow the self-care advice, recheck in a few hours, and note it.",
                unsafe_allow_html=True)
    c3.markdown(f"{pill('red')}<br>Tell the crew medical officer now, and contact the flight surgeon.",
                unsafe_allow_html=True)
    st.write("")

    def fmt(v):
        return "—" if v is None or (isinstance(v, float) and math.isinf(v)) else f"{v:g}"

    rows = []
    for ind in INDICATORS:
        t = THRESHOLDS[ind]
        g0, g1 = t["green"]
        a0, a1 = t["amber"]
        rows.append({"Indicator": t["label"], "Unit": t["unit"],
                     "🟢 Normal": f"{fmt(g0)} to {fmt(g1)}",
                     "🟠 Watch": f"{fmt(a0)} to {fmt(a1)}, outside normal",
                     "🔴 Act now": f"below {fmt(a0)} or {fmt(a1)} and above"})
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    st.caption("These ranges are for education and demonstration, not medical advice. "
               "Real flight medicine compares each astronaut with their own baseline.")