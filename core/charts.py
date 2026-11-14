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


def trend_chart(df, indicator):
    
    fig = go.Figure()
    if indicator not in THRESHOLDS or df is None or df.empty or indicator not in df.columns:
        fig.update_layout(template="plotly_dark", title=f"{indicator}: no data yet")
        return fig

    t = THRESHOLDS[indicator]
    name, unit = t["label"], t["unit"]
    hover_unit = "" if unit == "1-5" else unit    

    d = df[["timestamp", indicator]].dropna().copy()
    d["timestamp"] = pd.to_datetime(d["timestamp"])
    d = d.sort_values("timestamp")
    d["value"] = d[indicator]
    d["avg7"] = d["value"].rolling(7, min_periods=1).mean()

    # visible y-range: mood and stress use thresholds.py plot_range, others zoom to the data
    if indicator in SCORE_INDICATORS:
        ymin, ymax = t["plot_range"]
    else:
        span = max(d["value"].max() - d["value"].min(), 1e-6)
        pad = span * 0.15
        ymin, ymax = d["value"].min() - pad, d["value"].max() + pad

    _add_bands(fig, indicator, ymin, ymax)

    fig.add_trace(go.Scatter(
        x=d["timestamp"], y=d["value"], mode="lines+markers", name="Daily reading",
        line=dict(color=theme["line"], width=2), marker=dict(size=6), cliponaxis=False,
        hovertemplate="%{x|%d %b}: %{y} " + hover_unit + "<extra>Daily</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=d["timestamp"], y=d["avg7"], mode="lines", name="7-day average",
        line=dict(color=theme["avg"], width=2, dash="dash"), cliponaxis=False,
        hovertemplate="%{x|%d %b}: %{y:.1f} " + hover_unit + "<extra>7-day avg</extra>",
    ))

    yaxis = dict(range=[ymin, ymax], gridcolor=theme["grid"])
    if indicator in SCORE_INDICATORS:
        yaxis.update(tickmode="array", tickvals=[1, 2, 3, 4, 5])   

    fig.update_layout(
        template="plotly_dark",
        title=f"{name} over time",
        xaxis_title="Date", yaxis_title=f"{name} ({unit})",
        paper_bgcolor=theme["bg"], plot_bgcolor=theme["panel"],
        font=dict(color=theme["text"]),
        xaxis=dict(gridcolor=theme["grid"]),
        yaxis=yaxis,
        legend=dict(orientation="h", y=-0.2),
        height=420, margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig



def bp_chart(df):
    
    fig = go.Figure()
    if df is None or df.empty or "systolic_bp" not in df.columns or "diastolic_bp" not in df.columns:
        fig.update_layout(template="plotly_dark", title="Blood pressure: no data yet")
        return fig

    d = df[["timestamp", "systolic_bp", "diastolic_bp"]].dropna().copy()
    d["timestamp"] = pd.to_datetime(d["timestamp"])
    d = d.sort_values("timestamp")

    fig.add_trace(go.Scatter(
        x=d["timestamp"], y=d["systolic_bp"], mode="lines+markers", name="Systolic (top number)",
        line=dict(color=theme["line"], width=2), marker=dict(size=6),
        hovertemplate="%{x|%d %b}: %{y} mmHg<extra>Systolic</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=d["timestamp"], y=d["diastolic_bp"], mode="lines+markers", name="Diastolic (bottom number)",
        line=dict(color=theme["avg"], width=2), marker=dict(size=6),
        hovertemplate="%{x|%d %b}: %{y} mmHg<extra>Diastolic</extra>",
    ))

    # dotted limit lines, taken from thresholds.py: top of green = Watch, top of amber = Act
    for col, short in [("systolic_bp", "Systolic"), ("diastolic_bp", "Diastolic")]:
        t = THRESHOLDS[col]
        for limit, status, word in [(t["green"][1], "amber", "Watch above"), (t["amber"][1], "red", "Act at")]:
            fig.add_hline(
                y=limit, line_dash="dot", line_color= status_colours[status], line_width=1,
                annotation_text=f"{short}: {word} {limit:g}", annotation_position="top left",
                annotation_font=dict(color= status_colours[status], size=11),
            )

    fig.update_layout(
        template="plotly_dark",
        title="Blood pressure over time",
        xaxis_title="Date", yaxis_title="Blood pressure (mmHg)",
        paper_bgcolor=theme["bg"], plot_bgcolor=theme["panel"],
        font=dict(color=theme["text"]),
        xaxis=dict(gridcolor=theme["grid"]),
        yaxis=dict(gridcolor=theme["grid"]),
        legend=dict(orientation="h", y=-0.2),
        height=420, margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig

    

def _status_from_bands(indicator, value):
    bands = get_bands(indicator)
    if value < bands[0][0]:
        return bands[0][2]
    for lo, hi, status in bands:
        if lo <= value < hi:
            return status
    return bands[-1][2]


def status_gauge(indicator, value):
    t = THRESHOLDS[indicator]
    status = _status_from_bands(indicator, value)
    unit = "" if t["unit"] == "1-5" else " " + t["unit"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number=dict(suffix=unit, font=dict(color=theme["text"])),
        title=dict(
            text=f"{t['label']}<br><span style='color:{status_colours[status]}'>{status_words[status]}</span>",
            font=dict(color=theme["text"], size=16),
        ),
        gauge=dict(
            axis=dict(range=list(t["plot_range"]), tickcolor=theme["text"]),
            bar=dict(color=theme["line"], thickness=0.3),
            bgcolor=theme["panel"],
            borderwidth=0,
            steps=[dict(range=[lo, hi], color=_rgba(status_colours[s], 0.45)) for lo, hi, s in get_bands(indicator)],
        ),
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=theme["bg"], font=dict(color=theme["text"]),
        height=280, margin=dict(l=30, r=30, t=80, b=20),
    )
    return fig