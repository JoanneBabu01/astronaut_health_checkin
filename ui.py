import streamlit as st

STARS_CSS = """
<style>
[data-testid="stApp"] { background: #05070f; }

/* Two layers of stars that fade in and out at different speeds */
[data-testid="stApp"]::before,
[data-testid="stApp"]::after {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    background-image:
        radial-gradient(1.5px 1.5px at 20px 30px, #ffffff, transparent),
        radial-gradient(1px 1px at 90px 140px, #cfe0ff, transparent),
        radial-gradient(2px 2px at 160px 60px, #9ec5ff, transparent),
        radial-gradient(1.5px 1.5px at 230px 200px, #ffffff, transparent),
        radial-gradient(1px 1px at 300px 90px, #ffe9c4, transparent),
        radial-gradient(2px 2px at 360px 250px, #ffd2a1, transparent),
        radial-gradient(1.5px 1.5px at 60px 260px, #d9c8ff, transparent),
        radial-gradient(1px 1px at 330px 170px, #ffffff, transparent);
    background-size: 400px 300px;
    animation: twinkle 7s ease-in-out infinite alternate;
}
[data-testid="stApp"] {
    background:
        radial-gradient(ellipse at 15% 20%, rgba(80, 60, 160, 0.25), transparent 50%),
        radial-gradient(ellipse at 85% 75%, rgba(30, 90, 160, 0.20), transparent 55%),
        /* linear-gradient(180deg, #02030a 0%, #0a1030 55%, #1a1446 100%) !important; */
        /* linear-gradient(180deg, #020611 0%, #06213f 60%, #0b3a66 100%); */
        /* linear-gradient(180deg, #05060d 0%, #1b0f1f 55%, #3a1a14 100%); */
        linear-gradient(160deg, #02040c 0%, #0a1a2e 50%, #0f3b3a 100%);
    background-attachment: fixed !important;
}
@keyframes twinkle {
    from { opacity: 0.25; }
    to   { opacity: 0.9; }
}

/* Keep the app's content above the stars */
[data-testid="stAppViewContainer"],
[data-testid="stHeader"] {
    background: transparent;
    position: relative;
    z-index: 1;
}
</style>
"""

def background():
    st.markdown(STARS_CSS, unsafe_allow_html=True)

ENVIRONMENTS = ["ISS", "Transit", "Lunar base", "Mars base"]

def sidebar():
    if "env" not in st.session_state:
        st.session_state.env = ENVIRONMENTS[0]
    st.session_state.env = st.sidebar.selectbox(
        "Environment", ENVIRONMENTS,
        index=ENVIRONMENTS.index(st.session_state.env),
    )
    return st.session_state.env