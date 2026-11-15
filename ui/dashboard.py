# Owner: Role 3
import streamlit as st
import plotly.graph_objects as go

PILL= {"green": "#34d399", "amber": "#fbbf24", "red": "#f87171"}
WORD= {"green": "Normal", "amber": "Watch", "red": "Act now"}

CSS = """
<style>
.rb-hero {
  background: linear-gradient(135deg, rgba(59,130,246,0.35), rgba(139,92,246,0.25));
  border: 1px solid rgba(140,170,255,0.25); border-radius: 22px;
  padding: 26px 30px; display: flex; justify-content: space-between;
  align-items: center; margin-bottom: 18px;
}
.rb-hero h1 { color: #fff; font-size: 2rem; margin: 0; padding: 0; }
.rb-hero p { color: #b9c7f0; margin: 6px 0 0; }
.rb-hero-right { text-align: right; }
.rb-score { color: #fff; font-size: 2.4rem; font-weight: 700; line-height: 1; }
.rb-score span { font-size: 1rem; color: #9aa8d6; }

.rb-card {
  background: rgba(18,28,68,0.55); border: 1px solid rgba(120,150,255,0.18);
  border-radius: 18px; padding: 18px 20px; min-height: 150px;
  backdrop-filter: blur(6px);
}
.rb-label { color: #8fb3ff; font-size: 0.9rem; font-weight: 600; }
.rb-value { color: #fff; font-size: 2.2rem; font-weight: 700; line-height: 1.1; margin: 10px 0 12px; }
.rb-unit { font-size: 0.95rem; color: #9aa8d6; margin-left: 6px; font-weight: 500; }
.rb-pill { font-size: 0.78rem; padding: 3px 12px; border-radius: 999px; font-weight: 600; }

div[class*="st-key-panel_"] {
  background: rgba(18,28,68,0.55); border: 1px solid rgba(120,150,255,0.18) !important;
  border-radius: 18px; padding: 14px 16px; backdrop-filter: blur(6px);
}
.rb-panel-title { color: #8fb3ff; font-weight: 600; font-size: 0.95rem; margin-bottom: 4px; }
</style>
"""

def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)

def pill(status):
    c= PILL[status]
    return (f'<span class="rb-pill" style="background:{c}22;color:{c};'
            f'border:1px solid {c}66">{WORD[status]}</span>')

def hero(greeting, subtitle, overall, score):
    html= (f'<div class="rb-hero"><div><h1>{greeting}</h1><p>{subtitle}</p></div>'
            f'<div class="rb-hero-right"><div class="rb-score">{score}<span>/100</span></div>'
            f'<div style="margin-top:8px">{pill(overall)}</div></div></div>')
    st.markdown(html, unsafe_allow_html=True)

def stat_card(icon, label, value, unit, status):
    html = (f'<div class="rb-card"><div class="rb-label">{icon} {label}</div>'
            f'<div class="rb-value">{value}<span class="rb-unit">{unit}</span></div>'
            f'{pill(status)}</div>')
    st.markdown(html, unsafe_allow_html=True)

def panel_title(text):
    st.markdown(f'<div class="rb-panel-title">{text}</div>', unsafe_allow_html=True)

def glass(fig, height=260):
    """Make any Plotly figure blend into the dark panels."""
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      height=height, margin=dict(l=10, r=10, t=10, b=10),
                      font=dict(color="#c9d4f5"), showlegend=False)
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.06)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.06)")
    return fig

def score_ring(score, status):
    fig = go.Figure(go.Pie(values=[score, 100 - score], hole=0.78, sort=False,
                           marker=dict(colors=[PILL[status], "rgba(255,255,255,0.08)"]),
                           textinfo="none", hoverinfo="skip"))
    fig.add_annotation(text=f"<b>{score}</b>/100", showarrow=False,
                       font=dict(size=22, color="#ffffff"))
    return glass(fig, height=180)