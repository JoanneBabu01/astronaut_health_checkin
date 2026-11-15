# Owner: Role 2 (Latisha) + Role 3 (Rebecca)
import streamlit as st
from ui.bg_dark import background
from ui.sidebar import sidebar
from core.data import load_log
from core.assessment import assess_row
from core.charts import body_map_figure, trend_chart
from content.guidance import get_guidance

bg= background()
env= sidebar()
st.title("Body map")
st.caption("Tap a body system to see how it's doing and what to do.")

# Which indicators belong to which body system
SYSTEMS = {
    "brain": ("Brain and mind", ["mood", "stress", "sleep_hours"],
              "Mood, stress and sleep. Isolation, confinement and busy schedules affect all three."),
    "heart": ("Heart and circulation", ["heart_rate", "systolic_bp", "diastolic_bp"],
              "Pumps blood around the body. Fluid shifts in microgravity change heart rate and blood pressure."),
    "blood": ("Blood sugar", ["blood_glucose"],
              "Fuel for the brain and muscles. Diet, stress and inactivity can push it out of range."),
    "core": ("Core temperature", ["body_temp"],
             "A rise can signal infection, which matters because the immune system changes in space."),
    "musculoskeletal": ("Bones and muscles", ["exercise_min"],
                        "Without gravity, bone and muscle weaken quickly. Daily exercise is the main protection."),
}
NAMES = {"mood": "Mood", "stress": "Stress", "sleep_hours": "Sleep", "heart_rate": "Heart rate",
         "systolic_bp": "Systolic BP", "diastolic_bp": "Diastolic BP", "blood_glucose": "Blood glucose",
         "body_temp": "Body temperature", "exercise_min": "Exercise"}
LABELS = {"green": "🟢 OK", "amber": "🟠 Watch", "red": "🔴 Act"}
ORDER = ["green", "amber", "red"]

# Latest reading and its statuses
df= load_log().sort_values("timestamp")
latest= df.iloc[-1]
reading= {k: latest[k] for k in NAMES}
statuses= assess_row(reading)

# Each system takes the worst status of its indicators
system_status= {s: max((statuses[k] for k in inds), key=ORDER.index)
                 for s, (_, inds, _) in SYSTEMS.items()}

if "system" not in st.session_state:
    st.session_state.system = "heart"

left, right= st.columns([3, 2])

with left:
    fig= body_map_figure(system_status)
    event= st.plotly_chart(fig, on_select="rerun", selection_mode="points",
                            key="body", config={"displayModeBar": False})
    points= event["selection"]["points"] if event else []
    if points:
        clicked= points[0].get("customdata")
        if isinstance(clicked, (list, tuple)):
            clicked= clicked[0]
        if clicked in SYSTEMS:
            st.session_state.system= clicked

    # Backup buttons, in case a click on the figure doesn't register
    cols= st.columns(len(SYSTEMS))
    for col, (key, (title, _, _)) in zip(cols, SYSTEMS.items()):
        if col.button(f"{LABELS[system_status[key]].split()[0]} {title}", key=f"btn_{key}",
                      use_container_width=True):
            st.session_state.system = key

with right:
    key = st.session_state.system
    title, indicators, about = SYSTEMS[key]
    st.subheader(f"{LABELS[system_status[key]]}  {title}")
    st.write(about)

    for ind in indicators:
        s = statuses[ind]
        with st.expander(f"{LABELS[s]}  {NAMES[ind]}: {reading[ind]}", expanded=(s != "green")):
            g = get_guidance(ind, s, env)
            st.write(f"**What it means:** {g['meaning']}")
            st.write(f"**What to do:** {g['action']}")
            st.write(f"**When to escalate:** {g['escalate']}")
            st.plotly_chart(trend_chart(df, ind), use_container_width=True, key=f"trend_{ind}")
