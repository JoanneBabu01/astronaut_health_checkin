# Owner: Role 3
import pandas as pd
import plotly.express as px
import streamlit as st
from ui.sidebar import sidebar
from ui.bg_mars import background
from ui.dashboard import (inject_css, hero, attention_bar, stat_card, panel_title, glass, score_ring, pill, vitals_row)
from core.data import load_log
from core.assessment import assess_row, overall_status, health_score, trend_flags  # check file names
from core.charts import trend_chart
from content.guidance import get_guidance
# from <Person A's file> import dr_call_panel

st.set_page_config(page_title="APP NAME", page_icon="🚀", layout="wide")
bg= background()
env = sidebar()
inject_css()
NO_BAR = {"displayModeBar": False}

df = load_log(st.session_state.astronaut).sort_values("timestamp")
latest = df.iloc[-1]
INDICATORS = ["systolic_bp", "diastolic_bp", "heart_rate", "blood_glucose",
              "body_temp", "sleep_hours", "mood", "stress", "exercise_min"]
reading = {k: latest[k] for k in INDICATORS}
statuses = assess_row(reading)
overall = overall_status(reading)
score = health_score(statuses)
problems = [k for k, s in statuses.items() if s!= "green"]
ORDER = ["green", "amber", "red"]
worst = lambda *ks: max((statuses[k] for k in ks), key=ORDER.index)

# 1. Greeting banner
hour = pd.Timestamp.now().hour
greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
hours_since = (pd.Timestamp.now() - latest["timestamp"]).total_seconds() / 3600
due = "⏰ Check-in overdue" if hours_since > 24 else f"Next check-in in {24 - hours_since:.0f} h"
hero(f"{greeting}, {latest['astronaut']}",
     f"{env} · Last check-in {latest['timestamp']:%d %b, %H:%M} · {due}")

# 2. Attention bar, linking to the section at the bottom
attention_bar(overall, len(problems))

# 3. Health score (left) | heart rate + blood pressure, body map bar underneath (right)
vitals_row(score, overall,
           latest["heart_rate"], statuses["heart_rate"],
           f"{latest['systolic_bp']}/{latest['diastolic_bp']}", worst("systolic_bp", "diastolic_bp"))

PANEL_H = 380   # height of the chart rows: change this one number

# 4. Blood glucose + blood pressure chart
c1, c2 = st.columns([1, 2], gap="medium")
with c1:
    stat_card("🩸", "Blood glucose", latest["blood_glucose"], "mg/dL",
              statuses["blood_glucose"], tall=True, height=PANEL_H)
with c2:
    with st.container(key="panel_bp", height=PANEL_H):
        panel_title("Systolic blood pressure (mmHg), last 30 days")
        st.plotly_chart(glass(trend_chart(df.tail(30), "systolic_bp"), height=PANEL_H - 80),
                        use_container_width=True, config=NO_BAR)

st.write("")

# 5. Sleep chart + body temperature
c1, c2 = st.columns([2, 1], gap="medium")
with c1:
    with st.container(key="panel_sleep", height=PANEL_H):
        panel_title("Sleep (hours), last 7 nights")
        last7 = df.tail(7)
        fig = px.bar(last7, x="sleep_hours", y=last7["timestamp"].dt.strftime("%a"),
                     orientation="h")
        fig.update_traces(marker_color="#60a5fa")
        fig.add_vline(x=7, line_dash="dash", line_color="#34d399")
        st.plotly_chart(glass(fig, height=PANEL_H - 80), use_container_width=True, config=NO_BAR)
with c2:
    stat_card("🌡️", "Body temperature", latest["body_temp"], "°C",
              statuses["body_temp"], tall=True, height=PANEL_H)

# 6. Sleep, mood, stress
c1, c2, c3 = st.columns(3, gap="medium")
with c1:
    stat_card("🌙", "Sleep", latest["sleep_hours"], "h", statuses["sleep_hours"])
with c2:
    stat_card("🙂", "Mood", latest["mood"], "/5", statuses["mood"])
with c3:
    stat_card("🧠", "Stress", latest["stress"], "/5", statuses["stress"])

st.write("")

# 7. Needs attention (the attention bar links here)
st.markdown('<div id="needs-attention"></div>', unsafe_allow_html=True)
with st.container(key="panel_attention"):
    panel_title("⚠️ Needs attention")
    flags = trend_flags(df)
    active = [f for f in flags if f["active"]]
    past = [f for f in flags if not f["active"]]

    for f in active:
        box = st.error if f["status"] == "red" else st.warning
        box(f"**{f['label']}:** {f['message']}", icon="📈")

    if past:
        with st.expander(f"Earlier patterns ({len(past)})"):
            for f in sorted(past, key=lambda f: f["end"], reverse=True):
                st.markdown(
                    f"{pill(f['status'])} **{f['label']}**: {f['message']} "
                    f"<span style='color:#9aa8d6'>({f['start']:%d %b} – {f['end']:%d %b})</span>",
                    unsafe_allow_html=True,
                )
    if not problems:
        st.write("Nothing to act on. Keep up the routine. 🚀")
    for k in problems:
        g = get_guidance(k, statuses[k], env)
        st.markdown(f"{pill(statuses[k])} **{k.replace('_', ' ').title()}: {reading[k]}**",
                    unsafe_allow_html=True)
        st.write(f"{g['action']} *Escalate:* {g['escalate']}")
    if statuses["mood"] != "green" or statuses["stress"] != "green":
        st.page_link("pages/6_Calm_Break.py", label="🧘 Take a calm break")
    # if overall == "red":
    #     dr_call_panel(statuses, env, reading, st.session_state.astronaut)