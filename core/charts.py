# core/charts.py
# Owner: Role 2 (Latisha)
import pandas as pd
import plotly.graph_objects as go
from core.thresholds import THRESHOLDS, get_bands

status_colours = {"green": "#2ecc71", "amber": "#f5a623", "red": "#e74c3c"}
status_words = {"green": "OK", "amber": "Watch", "red": "Act"}

# theme
theme = {
    "bg": "#0b0b2a",      # page background
    "panel": "#15153f",   # chart background
    "grid": "#2c2c66",    # grid lines
    "text": "#e8e8ff",    # text
    "line": "#7aa2ff",    # daily readings
    "avg": "#c9a7ff",     # 7-day average
}

SCORE_INDICATORS = ("mood", "stress")



def _rgba(hex_color, alpha):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _add_bands(fig, indicator, ymin, ymax):
    """Draw the green/amber/red bands (from thresholds.py) behind the line, each with an OK / Watch / Act word."""
    for lo, hi, status in get_bands(indicator):
        lo2, hi2 = max(lo, ymin), min(hi, ymax)   # only draw the part we can see
        if lo2 >= hi2:
            continue
        fig.add_hrect(
            y0=lo2, y1=hi2, layer = "below", line_width=0,
            fillcolor=_rgba(status_colours[status], 0.18),
            annotation_text = status_words[status], annotation_position="top right",
            annotation_font=dict(color = status_colours[status], size=12),
        )
