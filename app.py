# Owner: Role 3 (Rebecca)
import streamlit as st
from ui import sidebar
st.title("APP NAME")
st.text("Your personalised health monitoring buddy")
env= sidebar()

hr= st.number_input("Heart rate (bpm)", min_value=30, max_value=200)
st.metric("Heart rate", f"{hr} bpm")