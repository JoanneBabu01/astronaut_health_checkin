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
