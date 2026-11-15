# Owner: Role 3 (Rebecca)
import pandas as pd
import streamlit as st
from ui.bg_mars import background
from ui.sidebar import sidebar
from core.data import load_log

bg= background()
env= sidebar()
st.set_page_config(page_title="APP_NAME", page_icon="🚀", layout="wide")
st.title("APP NAME")
st.caption("Your personalised health monitoring buddy")

#replace w 'from core.assessment import assess' after merging
def assess(indicator, value):
    return "green"

INDICATORS = {
    "systolic_bp": ("Systolic BP", "mmHg"),
    "diastolic_bp": ("Diastolic BP", "mmHg"),
    "heart_rate": ("Heart rate", "bpm"),
    "blood_glucose": ("Blood glucose", "mg/dL"),
    "body_temp": ("Body temp", "°C"),
    "sleep_hours": ("Sleep", "h"),
    "mood": ("Mood", "/5"),
    "stress": ("Stress", "/5"),
}
LABELS = {"green": "🟢 OK", "amber": "🟠 Watch", "red": "🔴 Act"}

df= load_log()
latest, previous= df.iloc[-1], df.iloc[-2]

st.subheader(f"Latest check-in: {latest['timestamp']:%d %b, %H:%M} · {env}")

cols = st.columns(4)
for i, (col,(label, unit)) in enumerate(INDICATORS.items()):
    status= assess(col, latest[col])
    with cols[i%4]:
        st.metric(label, f"{latest[col]} {unit}",
                  delta=round(float(latest[col] - previous[col]), 1), delta_color="inverse")
        st.caption(LABELS[status])