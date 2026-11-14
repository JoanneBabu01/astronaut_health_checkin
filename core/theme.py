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