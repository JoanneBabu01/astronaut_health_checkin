import random
from datetime import datetime, timezone
from urllib.parse import quote

import pandas as pd
import streamlit as st

from core.charts import status_colours, theme

def _star_layer(seed, count, tile):
    rng = random.Random(seed)
    colours = ["#ffffff", "#c9a7ff", "#7aa2ff", "#e8e8ff"]
    dots = []
    for _ in range(count):
        x, y = rng.randint(0, tile), rng.randint(0, tile)
        size = rng.choice([1, 1, 1, 2])
        dots.append(f"radial-gradient({size}px {size}px at {x}px {y}px, {rng.choice(colours)}, transparent)")
    return ", ".join(dots)

def _constellation(points):
    lines = "".join(
        f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="rgb(201,167,255)" stroke-width="1.2" stroke-opacity="0.7"/>'
        for a, b in zip(points, points[1:])
    )
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="2.8" fill="white"/>' for x, y in points)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 130">{lines}{dots}</svg>'
    return "url(\"data:image/svg+xml," + quote(svg) + "\")"


BIG_DIPPER = _constellation([(12, 100), (52, 84), (92, 88), (126, 66), (158, 48), (192, 62), (222, 30)])
CASSIOPEIA = _constellation([(14, 40), (60, 90), (112, 52), (164, 96), (222, 44)])

