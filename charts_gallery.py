# charts_gallery.py: builds ONE web page with every chart, for checking and screenshots.
# Local helper only (don't commit it).
import pandas as pd
from core.charts import (trend_chart, bp_chart, status_gauge, health_radar,
                         body_map_figure, body_regions)
from core.thresholds import INDICATORS

df = pd.read_csv("data/sample_crew_log.csv")
last = df.iloc[-1]

figs = [("Trend charts", [trend_chart(df, i) for i in INDICATORS]),
        ("Blood pressure", [bp_chart(df)]),
        ("Status dials (latest reading)", [status_gauge(i, float(last[i])) for i in INDICATORS]),
        ("Health snapshot", [health_radar(last)]),
        ("Body map", [body_map_figure({"brain": "amber", "heart": "red"})])]

parts = ["<html><body style='background:#0b0b2a;color:#e8e8ff;font-family:sans-serif;padding:20px'>"]
first = True
for title, group in figs:
    parts.append(f"<h2>{title}</h2>")
    for f in group:
        parts.append(f.to_html(full_html=False, include_plotlyjs="cdn" if first else False))
        first = False
parts.append("</body></html>")

with open("charts_gallery.html", "w", encoding="utf-8") as fh:
    fh.write("\n".join(parts))
print("Open charts_gallery.html in your browser")