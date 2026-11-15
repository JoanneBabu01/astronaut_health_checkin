import streamlit as st
import streamlit.components.v1 as components

from core.calm_break import DEFAULT_PALETTE, calm_break_html

#   from core.theme import inject_theme
#   from core.cover import require_login
#   inject_theme()
#   astronaut = require_login()

st.title("Calm Break")
st.write("A quiet minute. Catch a few stars, or just follow the circle and breathe. "
         "There is no timer and no way to lose.")

st.caption("A relaxation break for education and demonstration, not medical advice.")

st.markdown(
    """<style>
    [data-testid="stMain"], [data-testid="stHeader"], .main, .block-container {
        background: __BG_TOP__ !important; }
    .block-container h1, .block-container p, .block-container [data-testid="stCaptionContainer"] {
        color: __TEXT__; }
    .block-container { max-width: none !important; padding: 0 !important; }
    .block-container [data-testid="stVerticalBlock"] { gap: 0 !important; }
    /* Keep the title and captions readable now that the page padding is gone. */
    .block-container h1,
    .block-container [data-testid="stMarkdownContainer"] p,
    .block-container [data-testid="stCaptionContainer"] { padding-left: 1.25rem; padding-right: 1.25rem; }
    .block-container h1 { padding-top: 4rem; }
    iframe[srcdoc] { display: block; width: 100% !important; height: 100vh !important;
                     min-height: 100vh; border: 0; }
    </style>""".replace("__BG_TOP__", DEFAULT_PALETTE["bg_top"])
    .replace("__TEXT__", DEFAULT_PALETTE["text"]),
    unsafe_allow_html=True,
)
components.html(calm_break_html(), height=700)
