import streamlit as st

ENVIRONMENTS = ["ISS", "Transit", "Lunar base", "Mars base"]

def sidebar():
    if "env" not in st.session_state:
        st.session_state.env = ENVIRONMENTS[0]
    st.session_state.env = st.sidebar.selectbox(
        "Environment", ENVIRONMENTS,
        index=ENVIRONMENTS.index(st.session_state.env),
    )
    return st.session_state.env