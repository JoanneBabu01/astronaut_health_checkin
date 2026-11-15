# Owner: Role 2 (Latisha) + Role 3 (Rebecca)
import streamlit as st
from ui.bg_aurora import background
from ui.sidebar import sidebar
from core.data import load_log
from core.charts import trend_chart

bg= background()
env= sidebar()
st.title("Trends")
df= load_log()
indicator = st.selectbox("Indicator", ["systolic_bp", "heart_rate", "blood_glucose", "body_temp", "sleep_hours", "mood", "stress"])
st.plotly_chart(trend_chart(df, indicator), use_container_width=True)