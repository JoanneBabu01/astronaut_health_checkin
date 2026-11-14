# Owner: Role 3 (Rebecca)
from core.assessment import assess, overall_status 
from content.guidance import get_guidance
import streamlit as st
from ui import sidebar

env= sidebar()
st.title("Log vitals")

with st.form("checkin"):
    c1, c2= st.columns(2)
    systolic= c1.number_input("Systolic BP (mmHg)", 70, 220, 120, help="Sit still 5 minutes first")
    diastolic= c2.number_input("Diastolic BP (mmHg)", 40, 140, 80)
    heart_rate= c1.number_input("Resting heart rate (bpm)", 30, 200, 65)
    glucose= c2.number_input("Blood glucose (mg/dL)", 40, 400, 90)
    temp= c1.number_input("Body temperature (°C)", 34.0, 42.0, 36.7, step=0.1)
    sleep= c2.number_input("Sleep last night (hours)", 0.0, 14.0, 7.5, step=0.5)
    exercise= c1.number_input("Exercise today (minutes)", 0, 300, 90)
    mood= st.select_slider("Mood", options=[1, 2, 3, 4, 5], value=4,
                            format_func=lambda x: ["Very low", "Low", "Okay", "Good", "Great"][x - 1])
    stress= st.select_slider("Stress", options=[1, 2, 3, 4, 5], value=2,
                              format_func=lambda x: ["Calm", "Mild", "Moderate", "High", "Overwhelmed"][x - 1])
    submitted= st.form_submit_button("Save check-in")

    if submitted:
        entry = {"environment": env, 
                 "systolic_bp": systolic, 
                 "diastolic_bp": diastolic,
                 "heart_rate": heart_rate, 
                 "blood_glucose": glucose, 
                 "body_temp": temp,
                 "sleep_hours": sleep, 
                 "mood": mood, 
                 "stress": stress, 
                 "exercise_min": exercise}
        st.success("Check-in saved")   # later: save_entry(entry) and show each status + advice
        st.write(entry)

        st.title("Current Health Summary")
        labels= {"green": "🟢 OK", "amber": "🟠 Watch", "red": "🔴 Act"}
        names= {"systolic_bp": "Systolic BP", 
                "diastolic_bp": "Diastolic BP", 
                "heart_rate": "Heart rate",
                "blood_glucose": "Blood glucose", 
                "body_temp": "Body temperature",
                "sleep_hours": "Sleep", 
                "mood": "Mood", 
                "stress": "Stress", 
                "exercise_min": "Exercise"}

        statuses= {x:assess(x, entry[x])for x in names}
        overall= overall_status(statuses)

        if overall == "red":
            st.error("One or more readings need action now.")
        elif overall == "amber":
            st.warning("Some readings need watching.")
        else:
            st.success("All readings are in a healthy range.")

        problems = []
        for k, s in statuses.items():
            if s != "green":
                problems.append(k)

        for k in problems:
            g = get_guidance(k, statuses[k], env)
        with st.expander(f"{labels[statuses[k]]}  {names[k]}: {entry[k]}", expanded=True):
            st.write(f"**What it means:** {g['meaning']}")
            st.write(f"**What to do:** {g['action']}")
            st.write(f"**When to escalate:** {g['escalate']}")

        ok = [names[k] for k in NAMES if k not in problems]
        if ok:
            st.caption("🟢 Normal: " + ", ".join(ok))
        
        st.page_link("app.py", label="Back to dashboard")
