# Owner: Role 3
import pandas as pd
import streamlit as st
from ui.bg_aurora import background
from ui.sidebar import sidebar
from ui.dashboard import inject_css, panel_title, glass, card_html, pill
from core.data import load_log
from core.assessment import assess
from core.charts import trend_chart

bg= background()
st.set_page_config(page_title="TRENDS", page_icon="📈", layout="wide")
env= sidebar()
inject_css()
NO_BAR = {"displayModeBar": False}

INDICATORS = {
    "systolic_bp": ("Systolic BP", "mmHg"), "diastolic_bp": ("Diastolic BP", "mmHg"),
    "heart_rate": ("Heart rate", "bpm"), "blood_glucose": ("Blood glucose", "mg/dL"),
    "body_temp": ("Body temperature", "°C"), "sleep_hours": ("Sleep", "h"),
    "mood": ("Mood", "/5"), "stress": ("Stress", "/5"), "exercise_min": ("Exercise", "min"),
}

st.title("Trends")
st.caption("See how each health indicator has changed over time.")

df = load_log(st.session_state.astronaut).sort_values("timestamp")
if df.empty:
    st.info("No check-ins yet. Log your first one to see trends.")
    st.stop()

c1, c2 = st.columns([2, 1], gap="medium")
with c1:
    ind = st.selectbox("Indicator", list(INDICATORS), format_func=lambda k: INDICATORS[k][0])
with c2:
    days = st.radio("Period", [7, 30, 90], index=1, horizontal=True,
                    format_func=lambda d: f"{d} days")

label, unit = INDICATORS[ind]
data = df[df["timestamp"] >= df["timestamp"].max() - pd.Timedelta(days=days)]

# Summary cards: latest, average, days out of range
latest = data[ind].iloc[-1]
avg = round(float(data[ind].mean()), 1)
off = sum(assess(ind, v) != "green" for v in data[ind])
cols = st.columns(3, gap="medium")
cards = [
    card_html("📍", "Latest", latest, unit, assess(ind, latest)),
    card_html("➗", f"{days}-day average", avg, unit, assess(ind, avg)),
    card_html("⚠️", "Days out of range", off, f"of {len(data)}", "green" if off == 0 else "amber"),
]
for col, html in zip(cols, cards):
    col.markdown(html, unsafe_allow_html=True)

st.write("")

with st.container(key="panel_trend"):
    panel_title(f"{label} ({unit}), last {days} days")
    st.plotly_chart(glass(trend_chart(data, ind), height=420), use_container_width=True,
                    config=NO_BAR)
    st.caption("Shaded bands: green = OK, amber = Watch, red = Act. "
               "Dashed line = 7-day average.")