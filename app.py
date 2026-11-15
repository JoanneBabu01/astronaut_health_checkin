# Owner: Role 3
import pandas as pd
import plotly.express as px
import streamlit as st
from ui.bg_mars import background
from ui.sidebar import sidebar
from ui.dashboard import inject_css, hero, stat_card, panel_title, glass, score_ring, pill
from core.data import load_log
from core.assessment import assess_row, overall_status
from core.charts import trend_chart
from content.guidance import get_guidance

bg= background()
st.set_page_config(page_title="REBECCA", page_icon="🚀", layout="wide")
env = sidebar()
inject_css()

df = load_log().sort_values("timestamp")
latest = df.iloc[-1]
INDICATORS = ["systolic_bp", "diastolic_bp", "heart_rate", "blood_glucose",
              "body_temp", "sleep_hours", "mood", "stress", "exercise_min"]
reading = {k: latest[k] for k in INDICATORS}
statuses = assess_row(reading)
overall = overall_status(reading)
ORDER = ["green", "amber", "red"]
worst = lambda *ks: max((statuses[k] for k in ks), key=ORDER.index)

# Health score: swap for Person 1's function if they made one
n_amber = sum(s == "amber" for s in statuses.values())
n_red = sum(s == "red" for s in statuses.values())
score = max(0, 100 - 8 * n_amber - 20 * n_red)

# ---- Banner ----
hour = pd.Timestamp.now().hour
greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
hours_since = (pd.Timestamp.now() - latest["timestamp"]).total_seconds() / 3600
due = "⏰ Check-in overdue" if hours_since > 24 else f"Next check-in in {24 - hours_since:.0f} h"
hero(f"{greeting}, {latest['astronaut']}",
     f"{env} · Last check-in {latest['timestamp']:%d %b, %H:%M} · {due}", overall, score)

# ---- Row 1: score ring + key vitals ----
c1, c2, c3, c4 = st.columns(4, gap="medium")
with c1:
    with st.container(key="panel_score"):
        panel_title("Overall health score")
        st.plotly_chart(score_ring(score, overall), use_container_width=True,
                        config={"displayModeBar": False})
with c2:
    stat_card("❤️", "Heart rate", latest["heart_rate"], "bpm", statuses["heart_rate"])
with c3:
    stat_card("🫀", "Blood pressure", f"{latest['systolic_bp']}/{latest['diastolic_bp']}", "mmHg",
              worst("systolic_bp", "diastolic_bp"))
with c4:
    stat_card("🩸", "Blood glucose", latest["blood_glucose"], "mg/dL", statuses["blood_glucose"])

st.write("")
c1, c2, c3, c4 = st.columns(4, gap="medium")
with c1:
    stat_card("🌡️", "Body temperature", latest["body_temp"], "°C", statuses["body_temp"])
with c2:
    stat_card("🌙", "Sleep", latest["sleep_hours"], "h", statuses["sleep_hours"])
with c3:
    stat_card("🙂", "Mood", latest["mood"], "/5", statuses["mood"])
with c4:
    stat_card("🧠", "Stress", latest["stress"], "/5", statuses["stress"])

# ---- Row 2: trends ----
st.write("")
left, right = st.columns([2, 1], gap="medium")
with left:
    with st.container(key="panel_bp"):
        panel_title("Blood pressure, last 30 days")
        st.plotly_chart(glass(trend_chart(df.tail(30), "systolic_bp")),
                        use_container_width=True, config={"displayModeBar": False})
with right:
    with st.container(key="panel_sleep"):
        panel_title("Sleep, last 7 nights")
        last7 = df.tail(7)
        fig = px.bar(last7, x="sleep_hours", y=last7["timestamp"].dt.strftime("%a"),
                     orientation="h")
        fig.update_traces(marker_color="#60a5fa")
        fig.add_vline(x=7, line_dash="dash", line_color="#34d399")
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        st.plotly_chart(glass(fig), use_container_width=True, config={"displayModeBar": False})

# ---- Row 3: needs attention ----
st.write("")
with st.container(key="panel_attention"):
    panel_title("Needs attention")
    problems = [k for k, s in statuses.items() if s != "green"]
    if not problems:
        st.write("Nothing to act on. Keep up the routine. 🚀")
    for k in problems:
        g = get_guidance(k, statuses[k], env)
        st.markdown(f"{pill(statuses[k])} **{k.replace('_', ' ').title()}: {reading[k]}**",
                    unsafe_allow_html=True)
        st.write(f"{g['action']} *Escalate:* {g['escalate']}")