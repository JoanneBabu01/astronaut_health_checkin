import streamlit as st
from core.theme import inject_theme, card, mission_clock

st.set_page_config(page_title="Theme test", layout="wide")
inject_theme()

st.title("Theme test")
mission_clock("2026-09-25")
st.header("Hover over this heading")
st.subheader("And this one")
card("<b>Normal glass card</b><br>Used for panels and speech bubbles.")
card("<b>Heart rate: Act</b><br>A red card pulses gently.", status="red")
st.metric("Heart rate", "72 bpm")
with st.expander("An expander"):
    st.write("Hello from space")
st.button("A button")