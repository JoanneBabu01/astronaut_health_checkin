# core/theme.py
# Owner: Role 2 (Latisha)
# The space look: starfield, shooting star, fading constellations, header twinkle,
# glass cards, red-alert glow and a mission clock.
# Everyone else just calls inject_theme() once at the top of every page.
import random
from datetime import datetime, timezone
from urllib.parse import quote

import pandas as pd
import streamlit as st

from core.charts import status_colours, theme


# ---------- Stars: little dots scattered at fixed random places ----------
def _star_layer(seed, count, tile):
    rng = random.Random(seed)
    colours = ["#ffffff", "#c9a7ff", "#7aa2ff", "#e8e8ff"]
    dots = []
    for _ in range(count):
        x, y = rng.randint(0, tile), rng.randint(0, tile)
        size = rng.choice([1, 1, 1, 2])
        dots.append(f"radial-gradient({size}px {size}px at {x}px {y}px, {rng.choice(colours)}, transparent)")
    return ", ".join(dots)


# ---------- Constellations: a little web that GROWS, while its starting point fades away ----------
# Drawn as a tiny animated SVG used as a background image.
CYCLE = 26     # seconds for one full grow-and-fade loop
STEP = 2.4     # seconds each line takes to draw


def _constellation(points, edges, phase=0):
    # depth = how many lines away from the first star (it decides when a star lights up)
    depth = {0: 0}
    for _ in edges:
        for a, b in edges:
            if a in depth and b not in depth:
                depth[b] = depth[a] + 1
    css = (
        f"line{{stroke:rgb(201,167,255);stroke-width:1.4;stroke-linecap:round;"
        f"stroke-dasharray:100 100;stroke-dashoffset:100;animation:seg {CYCLE}s linear infinite}}"
        f"circle{{fill:white;opacity:0;animation:node {CYCLE}s linear infinite}}"
        "@keyframes seg{0%{stroke-dashoffset:100}9.2%{stroke-dashoffset:0}30.8%{stroke-dashoffset:0}"
        "40%{stroke-dashoffset:-100}100%{stroke-dashoffset:-100}}"
        "@keyframes node{0%{opacity:0}3%{opacity:1}31%{opacity:1}40%{opacity:0}100%{opacity:0}}"
    )
    lines = "".join(
        f'<line pathLength="100" x1="{points[a][0]}" y1="{points[a][1]}" x2="{points[b][0]}" y2="{points[b][1]}" '
        f'style="animation-delay:{depth[a] * STEP - phase:.1f}s"/>'
        for a, b in edges
    )
    dots = "".join(
        f'<circle cx="{points[i][0]}" cy="{points[i][1]}" r="2.8" style="animation-delay:{depth[i] * STEP - phase:.1f}s"/>'
        for i in depth
    )
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 130"><style>{css}</style>{lines}{dots}</svg>'
    return "url(\"data:image/svg+xml," + quote(svg) + "\")"


# star positions, and which stars are joined by a line (first star = starting point)
BIG_DIPPER = _constellation(
    [(12, 100), (52, 84), (92, 88), (126, 66), (158, 48), (192, 62), (222, 30), (98, 122), (150, 8)],
    [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (2, 7), (4, 8)],
)
CASSIOPEIA = _constellation(
    [(14, 40), (60, 90), (112, 52), (164, 96), (222, 44), (108, 8), (170, 126)],
    [(0, 1), (1, 2), (2, 3), (3, 4), (2, 5), (3, 6)],
    phase=13,
)


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&display=swap');

/* ---------- Page background ---------- */
.stApp {
    background: radial-gradient(ellipse at 20% 10%, #1b1b55 0%, __BG__ 55%, #05051a 100%) !important;
    color: __TEXT__;
    isolation: isolate;
}
[data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
    background: transparent !important;
}
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] {
    background: rgba(11, 11, 42, 0.85) !important;
    border-right: 1px solid rgba(201, 167, 255, 0.2);
}

/* ---------- Twinkling stars (two layers, different speeds) ---------- */
.stApp::before, .stApp::after {
    content: "";
    position: fixed;
    inset: 0;
    z-index: -1;
    pointer-events: none;
}
.stApp::before {
    background-image: __STARS_A__;
    background-size: 300px 300px;
    animation: twinkle 5s ease-in-out infinite;
}
.stApp::after {
    background-image: __STARS_B__;
    background-size: 430px 430px;
    animation: twinkle 7s ease-in-out infinite 2s;
}
@keyframes twinkle {
    0%, 100% { opacity: 0.35; }
    50% { opacity: 1; }
}

/* ---------- Shooting star + fading constellations ---------- */
.space-fx { position: fixed; inset: 0; pointer-events: none; z-index: 0; }
.space-fx .shoot {
    position: absolute; top: 12%; left: 70%; width: 140px; height: 2px;
    background: linear-gradient(to right, #ffffff, rgba(255, 255, 255, 0));
    opacity: 0;
    animation: shoot 12s linear infinite;
}
@keyframes shoot {
    0% { transform: translate(0, 0) rotate(-30deg); opacity: 0; }
    2% { opacity: 1; }
    8% { transform: translate(-520px, 300px) rotate(-30deg); opacity: 0; }
    100% { transform: translate(-520px, 300px) rotate(-30deg); opacity: 0; }
}
.space-fx .const {
    position: absolute; width: 240px; height: 130px;
    background-repeat: no-repeat; background-size: contain;
    opacity: 0.9;
}
.space-fx .c1 { top: 9%; right: 4%; background-image: __BIG_DIPPER__; }
.space-fx .c2 { bottom: 8%; left: 24%; background-image: __CASSIOPEIA__; }

/* ---------- Headings: space font, sparkle on hover ---------- */
.stApp h1, .stApp h2, .stApp h3 {
    font-family: 'Orbitron', 'Segoe UI', sans-serif !important;
    letter-spacing: 0.03em;
    transition: text-shadow 0.3s ease;
}
.stApp h1:hover, .stApp h2:hover, .stApp h3:hover {
    text-shadow: 0 0 10px __AVG__, 0 0 22px __LINE__;
}
.stApp h1:hover::after, .stApp h2:hover::after, .stApp h3:hover::after {
    content: "  \\2726 \\2727 \\2726";
    color: __AVG__;
    font-size: 0.6em;
    animation: twinkle 0.9s ease-in-out infinite;
}

/* ---------- Glass cards ---------- */
.glass,
[data-testid="stMetric"],
[data-testid="stExpander"],
[data-testid="stForm"] {
    background: rgba(21, 21, 63, 0.55) !important;
    border: 1px solid rgba(201, 167, 255, 0.28) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}
.glass { padding: 14px 18px; margin: 6px 0 12px 0; }
[data-testid="stMetric"] { padding: 12px 16px; }

/* ---------- Red alert: gentle pulsing glow ---------- */
.alert-red {
    border-color: __RED__ !important;
    animation: pulse-red 2.2s ease-in-out infinite;
}
@keyframes pulse-red {
    0%, 100% { box-shadow: 0 0 4px rgba(231, 76, 60, 0.35); }
    50% { box-shadow: 0 0 22px rgba(231, 76, 60, 0.85); }
}

/* ---------- Buttons ---------- */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
    background: linear-gradient(90deg, #3b4cca, #7b4fd6) !important;
    color: white !important;
    border: 1px solid rgba(201, 167, 255, 0.5) !important;
    border-radius: 999px !important;
    transition: box-shadow 0.25s ease, transform 0.25s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {
    box-shadow: 0 0 16px __LINE__;
    transform: translateY(-1px);
}

/* ---------- Mission clock banner ---------- */
.mission-clock {
    display: flex; justify-content: space-between; align-items: center;
    font-family: 'Orbitron', 'Segoe UI', sans-serif;
}
.mission-clock .day { font-size: 1.1rem; color: __LINE__; }
.mission-clock .time { font-size: 0.95rem; color: __AVG__; }

/* ---------- Reduced motion: switch every animation off ---------- */
@media (prefers-reduced-motion: reduce) {
    .stApp::before, .stApp::after, .space-fx .shoot,
    .alert-red, .stApp h1:hover::after, .stApp h2:hover::after, .stApp h3:hover::after {
        animation: none !important;
    }
    .space-fx .shoot { display: none; }
    .space-fx .const { display: none; }
}
</style>
<div class="space-fx"><div class="shoot"></div><div class="const c1"></div><div class="const c2"></div></div>
"""


def _build_css():
    return (_CSS
            .replace("__BG__", theme["bg"])
            .replace("__TEXT__", theme["text"])
            .replace("__LINE__", theme["line"])
            .replace("__AVG__", theme["avg"])
            .replace("__RED__", status_colours["red"])
            .replace("__STARS_A__", _star_layer(7, 22, 300))
            .replace("__STARS_B__", _star_layer(21, 16, 430))
            .replace("__BIG_DIPPER__", BIG_DIPPER)
            .replace("__CASSIOPEIA__", CASSIOPEIA))


def inject_theme():
    """Call once at the top of every page. Adds the whole space look."""
    st.markdown(_build_css(), unsafe_allow_html=True)


def card(html, status=None):
    """A glass card. Pass status="red" to make it pulse red. 'html' can be any HTML text."""
    cls = "glass alert-red" if status == "red" else "glass"
    st.markdown(f'<div class="{cls}">{html}</div>', unsafe_allow_html=True)


def mission_clock(start_date, now=None):
    """A small 'Mission Day N' banner. start_date: the first day of the mission, e.g. "2026-09-25".
    now: optional, e.g. the latest check-in time; by default the current time."""
    start = pd.to_datetime(start_date).date()
    current = pd.to_datetime(now) if now is not None else datetime.now(timezone.utc)
    day = (current.date() - start).days + 1
    card(
        f'<div class="mission-clock"><span class="day">Mission Day {day}</span>'
        f'<span class="time">{current:%d %b %Y, %H:%M} UTC</span></div>'
    )