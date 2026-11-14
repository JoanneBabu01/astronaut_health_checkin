# core/charts.py
# Owner: Role 2 (Latisha)
import pandas as pd
import plotly.graph_objects as go

#status
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

# Coloured bands per indicator: (low, high, status)
bands = {
    "systolic_bp":  [(60, 90, "amber"), (90, 120, "green"), (120, 140, "amber"), (140, 220, "red")],
    "diastolic_bp": [(30, 60, "amber"), (60, 80, "green"), (80, 90, "amber"), (90, 140, "red")],
    "heart_rate":   [(20, 40, "red"), (40, 50, "amber"), (50, 100, "green"), (100, 120, "amber"), (120, 200, "red")],
    "glucose":      [(30, 55, "red"), (55, 70, "amber"), (70, 100, "green"), (100, 126, "amber"), (126, 300, "red")],
    "body_temp":    [(33, 35.5, "red"), (35.5, 36.1, "amber"), (36.1, 37.3, "green"), (37.3, 38, "amber"), (38, 42, "red")],
    "sleep_hours":  [(0, 6, "red"), (6, 7, "amber"), (7, 9, "green"), (9, 14, "green")],
    "mood":         [(0, 2.5, "red"), (2.5, 3.5, "amber"), (3.5, 6, "green")],
}

indicator_names = {
    "systolic_bp": "Systolic blood pressure", "diastolic_bp": "Diastolic blood pressure",
    "heart_rate": "Resting heart rate", "glucose": "Blood glucose",
    "body_temp": "Body temperature", "sleep_hours": "Sleep", "mood": "Mood",
}