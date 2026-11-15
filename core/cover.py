# core/cover.py

import math
import random
from urllib.parse import quote

import streamlit as st

PAINT_A = ("#020310", "#050820", "#0A051F")  # wide base paint
PAINT_B = ("#06102A", "#0B0826", "#100720")  # softer paint on top
GLOW = "#23407a"                              # faint glow along the middle of the trail
CHALK = "#ecebe4"                             # chalk white for the border pictures

W, H = 160, 90         
PAINT_SECONDS = 7      # how long the spaceship takes to paint the whole screen
ART_DELAY = 8           # border pictures start fading in
CARD_DELAY = 10.2       # name card starts fading in


# ---------- The route of the spaceship: a smooth wandering curve that covers the whole screen ----------
# These waypoints were chosen so the wide trail paints every corner. Change them for a different flight.
WAYPOINTS = [(-12, 38.8), (6, 39.7), (40.4, 27.6), (87.1, 46.7), (125.4, 37.5), (141.5, 69.6), (111.5, 81.1),
             (59.6, 74.0), (21.3, 70.3), (14.7, 13.0), (72.5, 11.8), (105.4, 12.1), (143.1, 12.8), (153.1, 39.6),
             (157.0, 75.6), (144.4, 89.3), (110.0, 64.4), (51.1, 55.8), (3.8, 80.0)]


def _smooth_path(points):
    """A smooth curve through all the points (Catmull-Rom turned into SVG curves)."""
    p = [points[0]] + list(points) + [points[-1]]
    d = f"M {points[0][0]} {points[0][1]}"
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C {c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]} {p2[1]}"
    return d


ROUTE = _smooth_path(WAYPOINTS)


# ---------- Layer 1: the paint trail, the stars and the spaceship (one animated picture) ----------
def _stars(animated, seed=11, count=75):
    rng = random.Random(seed)
    out = []
    for i in range(count):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        r = rng.choice([0.25, 0.3, 0.4, 0.55])
        colour = rng.choice(["#ffffff", "#d9ccff", "#aebcff"])
        twinkle = ""
        if animated and i % 3 == 0:
            twinkle = (f'<animate attributeName="opacity" values="0.25;1;0.25" dur="{rng.uniform(3, 7):.1f}s" '
                       f'begin="{rng.uniform(0, 3):.1f}s" repeatCount="indefinite"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{colour}" opacity="0.85">{twinkle}</circle>')
    return "".join(out)


SHIP = (
    '<g transform="scale(0.55)">'
    '<ellipse cx="-15" cy="0" rx="10" ry="2.8" fill="url(#eng)"/>'
    '<path d="M -12 -2 L -6 -7.5 L -3 -2.4 Z" fill="#8a92b4"/>'
    '<path d="M -12 2 L -6 7.5 L -3 2.4 Z" fill="#8a92b4"/>'
    '<path d="M -12 -2.7 L 5 -2.7 Q 16 0 5 2.7 L -12 2.7 Z" fill="#d5d9e8"/>'
    '<path d="M 2 -2.7 Q 9 -2.2 11 0 Q 9 2.2 2 2.7 Z" fill="#9aa5cf"/>'
    '</g>'
)


def _paint_svg(animated=True):
    dash = 'stroke-dasharray="100 100" stroke-dashoffset="100"' if animated else ""

    def draw(width, stroke, opacity=1, blur=None):
        grow = (f'<animate attributeName="stroke-dashoffset" from="100" to="0" dur="{PAINT_SECONDS}s" '
                f'begin="0s" fill="freeze"/>') if animated else ""
        filt = f' filter="url(#{blur})"' if blur else ""
        return (f'<path d="{ROUTE}" pathLength="100" fill="none" stroke="{stroke}" stroke-width="{width}" '
                f'stroke-linecap="round" stroke-linejoin="round" opacity="{opacity}"{filt} {dash}>{grow}</path>')

    ship = ""
    if animated:
        ship = (
            '<g><animate attributeName="opacity" from="1" to="0" '
            f'begin="{PAINT_SECONDS}s" dur="0.8s" fill="freeze"/>'
            f'<g><animateMotion path="{ROUTE}" dur="{PAINT_SECONDS}s" begin="0s" rotate="auto" fill="freeze"/>'
            f'{SHIP}</g></g>'
        )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">'
        '<defs>'
        f'<linearGradient id="a" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="{H}">'
        f'<stop offset="0" stop-color="{PAINT_A[0]}"/><stop offset="0.55" stop-color="{PAINT_A[1]}"/><stop offset="1" stop-color="{PAINT_A[2]}"/>'
        '</linearGradient>'
        f'<linearGradient id="b" gradientUnits="userSpaceOnUse" x1="{W}" y1="0" x2="0" y2="{H}">'
        f'<stop offset="0" stop-color="{PAINT_B[0]}"/><stop offset="0.5" stop-color="{PAINT_B[1]}"/><stop offset="1" stop-color="{PAINT_B[2]}"/>'
        '</linearGradient>'
        '<radialGradient id="eng"><stop offset="0" stop-color="#cfe0ff" stop-opacity="0.9"/><stop offset="1" stop-color="#4a6fd0" stop-opacity="0"/></radialGradient>'
        '<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.4"/></filter>'
        '<filter id="softer" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="4"/></filter>'
        '</defs>'
        f'{draw(36, "url(#a)")}'
        f'{draw(25, "url(#b)", 0.9, "soft")}'
        f'{draw(11, GLOW, 0.3, "softer")}'
        f'{_stars(animated)}'
        f'{ship}'
        '</svg>'
    )
    return svg


# ---------- Layer 2: chalk-drawn border pictures (white outlines only, like chalk on a slate) ----------
def _sparkle(x, y, size=2.0):
    k = size
    return (f'<path d="M {x} {y - k} Q {x} {y} {x + k} {y} Q {x} {y} {x} {y + k} '
            f'Q {x} {y} {x - k} {y} Q {x} {y} {x} {y - k} Z"/>')


def _cross(x, y, size=1.1):
    return f'<path d="M {x - size} {y} L {x + size} {y} M {x} {y - size} L {x} {y + size}"/>'


def _sun(x, y, r):
    rays = []
    for i in range(14):
        ang = math.radians(i * 360 / 14)
        r1, r2 = r + 1.8, r + (4.8 if i % 2 == 0 else 3.4)
        rays.append(f"M {x + r1 * math.cos(ang):.1f} {y + r1 * math.sin(ang):.1f} "
                    f"L {x + r2 * math.cos(ang):.1f} {y + r2 * math.sin(ang):.1f}")
    return f'<circle cx="{x}" cy="{y}" r="{r}"/><circle cx="{x}" cy="{y}" r="{r * 0.62:.1f}" opacity="0.6"/><path d="{" ".join(rays)}"/>'


def _rocket(x, y, angle, scale):
    return (
        f'<g transform="translate({x} {y}) rotate({angle}) scale({scale})">'
        '<path d="M 0 -11 C 4.5 -7 4.5 3 3.4 8 L -3.4 8 C -4.5 3 -4.5 -7 0 -11 Z"/>'
        '<circle cx="0" cy="-2.5" r="1.9"/>'
        '<path d="M -3.6 3.5 L -7.5 9.5 L -3.4 8 M 3.6 3.5 L 7.5 9.5 L 3.4 8"/>'
        '<path d="M -2 9.5 Q 0 15 2 9.5 M -0.8 9.8 Q 0 12.5 0.8 9.8"/>'
        '</g>'
    )


def _astronaut(x, y, angle):
    return (
        f'<g transform="translate({x} {y}) rotate({angle})">'
        '<rect x="-8" y="7.5" width="3.4" height="10" rx="1.3"/>'                    # backpack
        '<rect x="-5" y="6" width="10" height="13" rx="3.4"/>'                        # body
        '<rect x="-2.4" y="9" width="4.8" height="3.2" rx="1"/>'                      # chest panel
        '<circle cx="0" cy="0" r="6.4"/>'                                             # helmet
        '<ellipse cx="0.9" cy="0.5" rx="4.2" ry="3.4"/>'                              # visor
        '<path d="M -1.2 -0.8 Q 0 -1.8 1.6 -1.4" opacity="0.7"/>'                     # shine
        '<g transform="translate(5 8) rotate(-135)"><rect x="-1.9" y="0" width="3.8" height="10.5" rx="1.9"/></g>'
        '<g transform="translate(-5 8) rotate(28)"><rect x="-1.9" y="0" width="3.8" height="10.5" rx="1.9"/></g>'
        '<g transform="translate(-2.4 18.5) rotate(10)"><rect x="-2" y="0" width="4" height="11" rx="2"/></g>'
        '<g transform="translate(2.4 18.5) rotate(-22)"><rect x="-2" y="0" width="4" height="11" rx="2"/></g>'
        '<path d="M -7 17 C -22 24 -4 36 -16 48" opacity="0.8"/>'                     # tether
        '</g>'
    )


def _constellation_chalk(points):
    parts = []
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        length = math.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / length, (by - ay) / length
        parts.append(f"M {ax + ux * 1.7:.1f} {ay + uy * 1.7:.1f} L {bx - ux * 1.7:.1f} {by - uy * 1.7:.1f}")
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="1"/>' for x, y in points)
    return f'<path d="{" ".join(parts)}"/>{dots}'


def _satellite(x, y, angle):
    return (
        f'<g transform="translate({x} {y}) rotate({angle})">'
        '<rect x="-2" y="-2" width="4" height="4" rx="0.6"/>'
        '<rect x="-10" y="-1.8" width="7" height="3.6"/><rect x="3" y="-1.8" width="7" height="3.6"/>'
        '<path d="M -6.5 -1.8 L -6.5 1.8 M 6.5 -1.8 L 6.5 1.8 M 0 -2 L 0 -5 M -1.6 -5.6 Q 0 -3.6 1.6 -5.6"/>'
        '</g>'
    )


_ART_SHAPES = (
    # sun, top left
    _sun(15, 15, 4.6)
    # ringed planet, top right
    + '<g transform="translate(141 18) rotate(-18)">'
      '<circle r="8"/><path d="M -7.6 -2.6 Q 0 -5 7.6 -2.6 M -8 1.6 Q 0 -0.6 8 1.6" opacity="0.7"/>'
      '<path d="M -16 0 A 16 4.2 0 0 1 16 0" mask="url(#behind)"/><path d="M -16 0 A 16 4.2 0 0 0 16 0"/>'
      '</g>'
    # big cratered planet, bottom right (partly off screen)
    + '<circle cx="152" cy="93" r="19"/><circle cx="145" cy="82" r="3"/><circle cx="157" cy="86" r="1.8"/>'
      '<circle cx="141" cy="90" r="1.5"/><path d="M 134 79 Q 142 74 152 75" opacity="0.6"/>'
      '<path d="M 124 70 A 36 14 0 0 1 160 62" stroke-dasharray="1.4 1.8" opacity="0.7"/><circle cx="127" cy="68" r="1.9"/>'
    # crescent moon + craters, bottom left
    + '<path d="M 18 69.3 A 7 7 0 1 0 18 82.7 A 7.5 7.5 0 0 1 18 69.3 Z"/>'
      '<circle cx="11.6" cy="75" r="1.1"/><circle cx="13.2" cy="79.4" r="0.8"/>'
    # astronaut, left
    + _astronaut(17, 33, -14)
    # rockets
    + _rocket(40, 16, 32, 0.8) + _rocket(121, 79, -28, 0.7) + _rocket(151, 52, -64, 0.55)
    # satellite
    + _satellite(86, 80, -12)
    # comet
    + '<circle cx="148" cy="38" r="1.5"/><path d="M 149.5 37 L 160 31 M 149 36 L 158 28 M 150.2 38 L 160 36" opacity="0.8"/>'
    # constellations
    + _constellation_chalk([(54, 8), (62, 13), (70, 10), (77, 16), (86, 11), (92, 17)])
    + _constellation_chalk([(50, 62), (56, 68), (64, 66), (69, 73)])
    # stars and little crosses
    + _sparkle(28, 7, 2.2) + _sparkle(99, 7, 1.6) + _sparkle(131, 8, 1.8) + _sparkle(6, 54, 1.6) + _sparkle(34, 40, 1.4)
    + _sparkle(104, 72, 1.8) + _sparkle(70, 84, 1.8) + _sparkle(52, 80, 1.3) + _sparkle(156, 24, 1.5) + _sparkle(8, 5, 1.4)
    + _cross(24, 30, 1.0) + _cross(60, 24, 1.0) + _cross(133, 30, 1.1) + _cross(94, 62, 0.9) + _cross(150, 66, 1.0)
    + _cross(4, 70, 1.0) + _cross(78, 6, 0.9) + _cross(40, 84, 1.0) + _cross(158, 12, 0.9) + _cross(118, 6, 0.9)
)


def _art_svg():
    group = f'fill="none" stroke="{CHALK}" stroke-width="0.55" stroke-linecap="round" stroke-linejoin="round"'
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" '
        'preserveAspectRatio="xMidYMid slice">'
        '<defs>'
        '<mask id="behind" maskUnits="userSpaceOnUse" x="-30" y="-30" width="60" height="60">'
        '<rect x="-30" y="-30" width="60" height="60" fill="white"/><circle r="8.2" fill="black"/></mask>'
        '<filter id="chalk" x="-2%" y="-2%" width="104%" height="104%">'
        '<feTurbulence type="fractalNoise" baseFrequency="0.07" numOctaves="2" seed="5" result="warp"/>'
        '<feDisplacementMap in="SourceGraphic" in2="warp" scale="1.3" xChannelSelector="R" yChannelSelector="G" result="wobbly"/>'
        '<feTurbulence type="fractalNoise" baseFrequency="1.9" numOctaves="1" seed="12" result="grain"/>'
        '<feColorMatrix in="grain" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.4 2.25" result="holes"/>'
        '<feComposite in="wobbly" in2="holes" operator="in"/>'
        '</filter>'
        f'<g id="art" {group}>{_ART_SHAPES}</g>'
        '</defs>'
        '<g filter="url(#chalk)">'
        '<use xlink:href="#art" href="#art" transform="translate(0.32 0.26)" opacity="0.5"/>'
        '<use xlink:href="#art" href="#art" opacity="0.92"/>'
        '</g>'
        '</svg>'
    )


def _uri(svg):
    return 'url("data:image/svg+xml,' + quote(svg) + '")'


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&display=swap');

/* ---------- very dark blue page ---------- */
.stApp {
    background: radial-gradient(ellipse at 50% 40%, #0b0d2e 0%, #060616 70%, #04040f 100%) !important;
    isolation: isolate;
}
[data-testid="stAppViewContainer"], [data-testid="stMain"], .main { background: transparent !important; }
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"], #MainMenu, footer { display: none !important; }

/* ---------- layer 1: the ship paints the screen ---------- */
.stApp::before {
    content: ""; position: fixed; inset: 0; z-index: -1; pointer-events: none;
    background: __PAINT__ center / cover no-repeat;
}
/* ---------- layer 2: border pictures fade in ---------- */
.stApp::after {
    content: ""; position: fixed; inset: 0; z-index: -1; pointer-events: none;
    background: __ART__ center / cover no-repeat;
    opacity: 0;
    animation: cover-fade 2.6s ease __ART_DELAY__s forwards;
}
@keyframes cover-fade { from { opacity: 0; } to { opacity: 1; } }

/* ---------- name card in the middle, fades in after the ship finishes ---------- */
.block-container, [data-testid="stMainBlockContainer"] {
    max-width: 520px !important;
    padding-top: 22vh !important;
    opacity: 0;
    animation: cover-fade 1.8s ease __CARD_DELAY__s forwards;
}
.cover-title {
    font-family: 'Orbitron', 'Segoe UI', sans-serif; font-weight: 700;
    font-size: 1.7rem; letter-spacing: 0.1em; white-space: nowrap; text-align: center; color: #e8e8ff;
    text-shadow: 0 0 18px rgba(122, 162, 255, 0.55);
}
.cover-sub { text-align: center; color: #b6b0ee; margin: 4px 0 18px 0; letter-spacing: 0.08em; }
.cover-hint { text-align: center; color: #9a95d6; font-size: 0.9rem; margin-top: 10px; }

[data-testid="stForm"] {
    background: rgba(10, 12, 44, 0.72) !important;
    border: 1px solid rgba(155, 140, 255, 0.35) !important;
    border-radius: 20px !important;
    padding: 22px 24px !important;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    box-shadow: 0 0 40px rgba(30, 30, 110, 0.35);
}
[data-testid="stForm"] label p { color: #cfc9ff !important; }
[data-testid="stForm"] input::placeholder { color: #8f8ac8 !important; opacity: 1 !important; }
[data-testid="stForm"] input {
    background: rgba(6, 8, 34, 0.9) !important; color: #e8e8ff !important;
    border: 1px solid rgba(155, 140, 255, 0.4) !important; border-radius: 12px !important;
}
.stFormSubmitButton, [data-testid="stFormSubmitButton"] { width: 100%; }
[data-testid="stFormSubmitButton"] > button { width: 100% !important; }
.stFormSubmitButton > button {
    background: linear-gradient(90deg, #1b2468, #3d2a7a) !important;
    color: #ffffff !important; border: 1px solid rgba(190, 175, 255, 0.5) !important;
    border-radius: 999px !important; width: 100% !important;
    transition: box-shadow 0.25s ease, transform 0.25s ease;
}
.stFormSubmitButton > button:hover { box-shadow: 0 0 18px rgba(122, 162, 255, 0.8); transform: translateY(-1px); }

/* ---------- reduced motion: show the finished picture straight away, no animation ---------- */
@media (prefers-reduced-motion: reduce) {
    .stApp::before { background-image: __PAINT_STATIC__; }
    .stApp::after, .block-container, [data-testid="stMainBlockContainer"] { animation: none !important; opacity: 1; }
}
</style>
"""


def _css():
    return (_CSS
            .replace("__PAINT_STATIC__", _uri(_paint_svg(animated=False)))
            .replace("__PAINT__", _uri(_paint_svg(animated=True)))
            .replace("__ART__", _uri(_art_svg()))
            .replace("__ART_DELAY__", str(ART_DELAY))
            .replace("__CARD_DELAY__", str(CARD_DELAY)))


def show_cover():
    """Draw the cover page. When the astronaut presses Launch, the name is saved and the app opens."""
    st.markdown(_css(), unsafe_allow_html=True)
    st.markdown('<div class="cover-title">MISSION CONTROL</div>'
                '<div class="cover-sub">Astronaut Health Check-in</div>', unsafe_allow_html=True)

    with st.form("cover_form"):
        name = st.text_input("Enter astronaut name", placeholder="e.g. Commander A")
        launch = st.form_submit_button("Launch \U0001F680")
        demo = st.form_submit_button("Use demo crew member")
    st.markdown('<div class="cover-hint">Demo crew member: Commander A</div>', unsafe_allow_html=True)

    if launch or demo:
        chosen = "Commander A" if demo else name.strip()
        if chosen:
            st.session_state["astronaut"] = chosen
            st.rerun()
        else:
            st.warning("Please enter a name to launch.")


def require_login():
    """Put at the top of app.py and of every page. Returns the astronaut's name,
    or shows the cover page and stops the page until a name is entered."""
    name = st.session_state.get("astronaut")
    if name:
        return name
    show_cover()
    st.stop()


def switch_astronaut():
    """Sign out and go back to the cover page (e.g. call this from a sidebar button)."""
    st.session_state.pop("astronaut", None)
    st.rerun()