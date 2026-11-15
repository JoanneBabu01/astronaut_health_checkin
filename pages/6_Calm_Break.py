import streamlit as st
import streamlit.components.v1 as components

from core.calm_break import calm_break_html

# Rebecca adds the shared lines at the top, as on every other page:
#   from core.theme import inject_theme
#   from core.cover import require_login
#   inject_theme()
#   astronaut = require_login()

st.title("Calm Break")
st.write("A quiet minute. Catch a few stars, or just follow the circle and breathe. "
         "There is no timer and no way to lose.")

st.caption("A relaxation break for education and demonstration, not medical advice.")

# Make the game fill the space under the title (the sidebar and header stay visible).
st.markdown(
    """<style>
    .block-container { max-width: none; padding-top: 3rem; }
    iframe[srcdoc] { height: calc(100vh - 250px) !important; min-height: 620px; }
    </style>""",
    unsafe_allow_html=True,
)
components.html(calm_break_html(), height=700)
