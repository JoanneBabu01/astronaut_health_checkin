# Owner: Role 3
import pandas as pd
import streamlit as st
from ui.bg_blue import background
from ui.sidebar import sidebar
from ui.dashboard import inject_css, panel_title, pill
from core.data import save_entry
from core.assessment import assess_row, overall_status
from content.guidance import get_guidance

bg= background()
env= sidebar()
st.set_page_config(page_title="LOG VITALS", page_icon="🧬", layout="wide")
st.title("Log vitals")
st.caption("Take your measurements, enter them below, and get instant feedback.")
inject_css()

# >>> paste your moon slider CSS st.markdown(...) block here <<<

NAMES = {"systolic_bp": ("Systolic BP", "mmHg"), "diastolic_bp": ("Diastolic BP", "mmHg"),
         "heart_rate": ("Heart rate", "bpm"), "blood_glucose": ("Blood glucose", "mg/dL"),
         "body_temp": ("Body temperature", "°C"), "sleep_hours": ("Sleep", "h"),
         "mood": ("Mood", "/5"), "stress": ("Stress", "/5"), "exercise_min": ("Exercise", "min")}
MOON = ["🌑", "🌒", "🌓", "🌔", "🌕"]


with st.container(key="panel_form"):
    panel_title("Today's check-in")
    with st.form("checkin", border=False):
        c1, c2 = st.columns(2, gap="large")
        systolic = c1.number_input("Systolic BP (mmHg)", 70, 220, 120, help="Sit still for 5 minutes first")
        diastolic = c1.number_input("Diastolic BP (mmHg)", 40, 140, 80)
        heart_rate = c1.number_input("Resting heart rate (bpm)", 30, 200, 65)
        exercise = c1.number_input("Exercise today (minutes)", 0, 300, 90)
        glucose = c2.number_input("Blood glucose (mg/dL)", 40, 400, 90)
        temp = c2.number_input("Body temperature (°C)", 34.0, 42.0, 36.7, step=0.1)
        sleep = c2.number_input("Sleep last night (hours)", 0.0, 14.0, 7.5, step=0.5)

        mood = st.select_slider("Mood", options=[1, 2, 3, 4, 5], value=4, key="mood",
                                format_func=lambda x: f"{MOON[x-1]} {['Very low','Low','Okay','Good','Great'][x-1]}")
        stress = st.select_slider("Stress", options=[1, 2, 3, 4, 5], value=2, key="stress",
                                  format_func=lambda x: f"{MOON[x-1]} {['Calm','Mild','Moderate','High','Overwhelmed'][x-1]}")
        submitted = st.form_submit_button("Save check-in", type="primary", use_container_width=True)

if submitted:
    reading = {"systolic_bp": systolic, "diastolic_bp": diastolic, "heart_rate": heart_rate,
               "blood_glucose": glucose, "body_temp": temp, "sleep_hours": sleep,
               "mood": mood, "stress": stress, "exercise_min": exercise}
    entry = {"timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
             "astronaut": st.session_state.astronaut, "environment": env, **reading}
    save_entry(entry)
    st.cache_data.clear()

    statuses = assess_row(reading)
    overall = overall_status(reading)
    problems = [k for k, s in statuses.items() if s != "green"]

    st.write("")
    if overall == "red":
        st.error(f"🔴 Check-in saved. {len(problems)} reading(s) need action now.")
    elif overall == "amber":
        st.warning(f"🟠 Check-in saved. {len(problems)} reading(s) to keep an eye on.")
    else:
        st.success("🟢 Check-in saved. All readings are in a healthy range.")

    with st.container(key="panel_results"):
        panel_title("Your results")
        for k in problems:
            name, unit = NAMES[k]
            g = get_guidance(k, statuses[k], env)
            st.markdown(f"{pill(statuses[k])} **{name}: {reading[k]} {unit}**", unsafe_allow_html=True)
            st.write(f"**What to do:** {g['action']}  \n**When to escalate:** {g['escalate']}")
        ok = [NAMES[k][0] for k in NAMES if k not in problems]
        if ok:
            st.markdown(f"{pill('green')} {', '.join(ok)}", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    c1.page_link("app.py", label="← Back to dashboard")
    c2.page_link("pages/2_Body_Map.py", label="Open body map →")