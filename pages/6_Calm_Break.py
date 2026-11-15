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

components.html(calm_break_html(), height=700)

st.caption("A relaxation break for education and demonstration, not medical advice.")
