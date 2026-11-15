# Owner: Role 3
import streamlit as st
from ui.bg_dark import background
from ui.sidebar import sidebar
from ui.dashboard import inject_css, panel_title, glass, pill
from core.data import load_log
from core.assessment import assess_row
from core.charts import body_map_figure, trend_chart
from content.guidance import get_guidance

bg= background()
st.set_page_config(page_title="BODY MAP", page_icon="🩻", layout="wide")
env= sidebar()
inject_css()
NO_BAR = {"displayModeBar": False}

SYSTEMS = {
    "brain": ("🧠", "Brain and mind", ["mood", "stress", "sleep_hours"],
              "Mood, stress and sleep. Isolation, confinement and busy schedules affect all three."),
    "heart": ("🫀", "Heart and circulation", ["heart_rate", "systolic_bp", "diastolic_bp"],
              "Pumps blood around the body. Fluid shifts in microgravity change heart rate and blood pressure."),
    "blood": ("🩸", "Blood sugar", ["blood_glucose"],
              "Fuel for the brain and muscles. Diet, stress and inactivity can push it out of range."),
    "core": ("🌡️", "Core temperature", ["body_temp"],
             "A rise can signal infection, which matters because the immune system changes in space."),
    "musculoskeletal": ("🦴", "Bones and muscles", ["exercise_min"],
                        "Without gravity, bone and muscle weaken quickly. Daily exercise is the main protection."),
}
NAMES = {"mood": ("Mood", "/5"), "stress": ("Stress", "/5"), "sleep_hours": ("Sleep", "h"),
         "heart_rate": ("Heart rate", "bpm"), "systolic_bp": ("Systolic BP", "mmHg"),
         "diastolic_bp": ("Diastolic BP", "mmHg"), "blood_glucose": ("Blood glucose", "mg/dL"),
         "body_temp": ("Body temperature", "°C"), "exercise_min": ("Exercise", "min")}
ORDER = ["green", "amber", "red"]

st.title("Body map")
st.caption("Tap a body system to see how it's doing and what to do.")

df = load_log(st.session_state.astronaut).sort_values("timestamp")
if df.empty:
    st.info("No check-ins yet. Log your first one to see the body map.")
    st.stop()

latest = df.iloc[-1]
reading = {k: latest[k] for k in NAMES}
statuses = assess_row(reading)
system_status = {s: max((statuses[k] for k in inds), key=ORDER.index)
                 for s, (_, _, inds, _) in SYSTEMS.items()}

if "system" not in st.session_state:
    # open on the worst system, so problems are the first thing you see
    st.session_state.system = max(system_status, key=lambda s: ORDER.index(system_status[s]))

left, right = st.columns([1, 1], gap="medium")

with left:
    with st.container(key="panel_figure"):
        panel_title("Body systems")
        fig = body_map_figure(system_status)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        event = st.plotly_chart(fig, on_select="rerun", selection_mode="points",
                                key="body", use_container_width=True, config=NO_BAR)
        points = event["selection"]["points"] if event else []
        if points:
            clicked = points[0].get("customdata")
            if isinstance(clicked, (list, tuple)):
                clicked = clicked[0]
            if clicked in SYSTEMS:
                st.session_state.system = clicked

        # Backup buttons, in case a click on the figure doesn't register
        cols = st.columns(len(SYSTEMS))
        for col, (key, (icon, title, _, _)) in zip(cols, SYSTEMS.items()):
            if col.button(icon, key=f"btn_{key}", help=title, use_container_width=True):
                st.session_state.system = key

with right:
    key = st.session_state.system
    icon, title, indicators, about = SYSTEMS[key]
    with st.container(key="panel_detail"):
        st.markdown(f"### {icon} {title} &nbsp; {pill(system_status[key])}", unsafe_allow_html=True)
        st.write(about)

        for ind in indicators:
            s = statuses[ind]
            name, unit = NAMES[ind]
            with st.expander(f"{name}: {reading[ind]} {unit}", expanded=(s != "green")):
                st.markdown(pill(s), unsafe_allow_html=True)
                g = get_guidance(ind, s, env)
                st.write(f"**What it means:** {g['meaning']}")
                st.write(f"**What to do:** {g['action']}")
                st.write(f"**When to escalate:** {g['escalate']}")
                st.plotly_chart(glass(trend_chart(df.tail(30), ind), height=220),
                                use_container_width=True, config=NO_BAR, key=f"trend_{ind}")