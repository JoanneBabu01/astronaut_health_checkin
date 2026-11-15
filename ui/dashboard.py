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

.rb-card.tall { min-height: 300px; display: flex; flex-direction: column; justify-content: center; }
.rb-alert {
  border-radius: 14px; padding: 12px 18px; margin: -6px 0 18px;
  display: flex; justify-content: space-between; align-items: center; font-weight: 600;
}
.rb-alert a { color: inherit; text-decoration: underline; }

div[class*="st-key-panel_bodymap"] { margin-top: 16px; }

.rb-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  grid-template-rows: 1fr auto;
  gap: 16px;
  margin-bottom: 18px;
}
.rb-grid .score   { grid-column: 1; grid-row: 1 / 3; }
.rb-grid .hr      { grid-column: 2; grid-row: 1; }
.rb-grid .bp      { grid-column: 3; grid-row: 1; }
.rb-grid .bodymap { grid-column: 2 / 4; grid-row: 2; }
.rb-grid .rb-card { min-height: 0; height: 100%; box-sizing: border-box; }

/* Donut ring drawn in pure CSS */
.rb-ring-wrap { position: relative; width: min(200px, 80%); aspect-ratio: 1; margin: 14px auto 0; }
.rb-ring {
  position: absolute; inset: 0; border-radius: 50%;
  background: conic-gradient(var(--c) calc(var(--p) * 1%), rgba(255,255,255,0.08) 0);
  -webkit-mask: radial-gradient(farthest-side, transparent 76%, #000 77%);
          mask: radial-gradient(farthest-side, transparent 76%, #000 77%);
}
.rb-ring-text { position: absolute; inset: 0; display: grid; place-items: center;
                color: #fff; font-size: 1.6rem; font-weight: 700; }
.rb-ring-text span { font-size: 1rem; color: #9aa8d6; font-weight: 500; }

.rb-bodymap { display: flex; justify-content: space-between; align-items: center; gap: 12px; color: #e6ecff; }
.rb-bodymap a { color: #8fb3ff; font-weight: 600; text-decoration: none; white-space: nowrap; }

/* On narrow screens, stack everything */
@media (max-width: 900px) {
  .rb-grid { grid-template-columns: 1fr; grid-template-rows: auto; }
  .rb-grid .score, .rb-grid .hr, .rb-grid .bp, .rb-grid .bodymap { grid-column: 1; grid-row: auto; }
}

.rb-stack { display: flex; flex-direction: column; gap: 16px; box-sizing: border-box; }
.rb-stack .rb-card {
  flex: 1; min-height: 0; box-sizing: border-box;
  display: flex; flex-direction: column; justify-content: center;
}

/* Centre the contents of every metric card */
.rb-card { text-align: center; }

/* Flex cards: centre horizontally as well */
.rb-stack .rb-card,
.rb-card.tall { align-items: center; }

/* Heart rate and blood pressure in the top grid: centre both ways */
.rb-grid .hr,
.rb-grid .bp {
  display: flex; flex-direction: column;
  justify-content: center; align-items: center;
}

/* Keep the body map bar laid out left-to-right */
.rb-grid .bodymap { text-align: left; }

</style>
"""

def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)

def pill(status):
    c= PILL[status]
    return (f'<span class="rb-pill" style="background:{c}22;color:{c};'
            f'border:1px solid {c}66">{WORD[status]}</span>')

def hero(greeting, subtitle):
    html = (f'<div class="rb-hero"><div><h1>{greeting}</h1><p>{subtitle}</p></div></div>')
    st.markdown(html, unsafe_allow_html=True)

def attention_bar(overall, count):
    c = PILL[overall]
    if overall == "green":
        text, link = "🟢 All readings are in a healthy range", ""
    else:
        icon = "🔴 Act now" if overall == "red" else "🟠 Keep an eye on things"
        text = f"{icon}: {count} reading{'s' if count != 1 else ''} need attention"
        link = '<a href="#needs-attention" target="_self">See what needs attention ↓</a>'
    html = (f'<div class="rb-alert" style="background:{c}1f;border:1px solid {c}66;color:{c}">'
            f'<span>{text}</span>{link}</div>')
    st.markdown(html, unsafe_allow_html=True)

def card_html(icon, label, value, unit, status):
    return (f'<div class="rb-card"><div class="rb-label">{icon} {label}</div>'
            f'<div class="rb-value">{value}<span class="rb-unit">{unit}</span></div>'
            f'<div>{pill(status)}</div></div>')

def stat_card(icon, label, value, unit, status, tall=False, height=None):
    html = card_html(icon, label, value, unit, status)
    if tall:
        html = html.replace('class="rb-card"', 'class="rb-card tall"', 1)
    if height:
        html = html.replace('class="rb-card', f'style="height:{height}px;box-sizing:border-box" class="rb-card', 1)
    st.markdown(html, unsafe_allow_html=True)

def stat_stack(cards, height):
    """Stack several cards so that together, with the gaps, they are exactly `height` px."""
    html = f'<div class="rb-stack" style="height:{height}px">' + "".join(cards) + "</div>"
    st.markdown(html, unsafe_allow_html=True)

def score_ring(score, status, height=180):
    fig = go.Figure(go.Pie(values=[score, 100 - score], hole=0.78, sort=False,
                           marker=dict(colors=[PILL[status], "rgba(255,255,255,0.08)"]),
                           textinfo="none", hoverinfo="skip"))
    fig.add_annotation(text=f"<b>{score}</b>/100", showarrow=False,
                       font=dict(size=22, color="#ffffff"))
    return glass(fig, height=height)

def panel_title(text):
    st.markdown(f'<div class="rb-panel-title">{text}</div>', unsafe_allow_html=True)

def glass(fig, height=260, clean=True):
    """Make any Plotly figure blend into the dark panels."""
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      height=height, margin=dict(l=10, r=10, t=10, b=10),
                      font=dict(color="#c9d4f5"), showlegend=False)
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.06)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.06)")
    if clean:
        fig.update_layout(title_text="")
        fig.update_xaxes(title_text="")
        fig.update_yaxes(title_text="")
    return fig

def vitals_row(score, overall, hr, hr_status, bp_text, bp_status):
    c = PILL[overall]
    html = (
        '<div class="rb-grid">'
        f'<div class="rb-card score"><div class="rb-label">Overall health score</div>'
        f'<div class="rb-ring-wrap"><div class="rb-ring" style="--p:{score};--c:{c}"></div>'
        f'<div class="rb-ring-text"><div>{score}<span>/100</span></div></div></div></div>'
        f'<div class="rb-card hr"><div class="rb-label">❤️ Heart rate</div>'
        f'<div class="rb-value">{hr}<span class="rb-unit">bpm</span></div>{pill(hr_status)}</div>'
        f'<div class="rb-card bp"><div class="rb-label">🫀 Blood pressure</div>'
        f'<div class="rb-value">{bp_text}<span class="rb-unit">mmHg</span></div>{pill(bp_status)}</div>'
        '<div class="rb-card bodymap"><div class="rb-bodymap">'
        "<span>🧍 <b>Body map</b> · See each body system's status at a glance</span>"
        '<a href="Body_Map" target="_self">Open body map →</a></div></div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)