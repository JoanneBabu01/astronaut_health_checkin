"""Settings for each mission environment: gravity and Earth communication delay.

Plain Python, no Streamlit. Used by the Dr. Call panel and by the advice text.
The delays are ILLUSTRATIVE values for a demo, not mission specifications.
"""

DEFAULT_ENVIRONMENT = "ISS"

# Keys match the `environment` column in data/sample_crew_log.csv.
ENVIRONMENT_SETTINGS = {
    "ISS": {
        "label": "Space station (ISS)",
        "gravity_g": 0.0,
        "gravity_text": "microgravity",
        "one_way_delay_s": 1.0,
        "screen_wait_s": 1.0,
        "delay_note": "Near real-time contact with the ground, with short gaps.",
    },
    "Transit": {
        "label": "Transit spacecraft",
        "gravity_g": 0.0,
        "gravity_text": "microgravity",
        "one_way_delay_s": 300.0,
        "screen_wait_s": 3.0,
        "delay_note": ("The delay grows with distance from Earth. About 5 minutes one way "
                       "is used here for mid-journey; it can reach about 22 minutes."),
    },
    "Lunar base": {
        "label": "Lunar base",
        "gravity_g": 0.166,
        "gravity_text": "about one sixth of Earth gravity",
        "one_way_delay_s": 1.3,
        "screen_wait_s": 1.5,
        "delay_note": "Radio signals take about 1.3 seconds one way.",
    },
    "Mars base": {
        "label": "Mars base",
        "gravity_g": 0.38,
        "gravity_text": "about 38% of Earth gravity",
        "one_way_delay_s": 720.0,
        "screen_wait_s": 5.5,
        "delay_note": ("Signals take between about 3 and 22 minutes one way, depending on "
                       "where Earth and Mars are. 12 minutes is used here."),
    },
}


def format_duration(seconds):
    """1 -> '1 second', 1.3 -> '1.3 seconds', 720 -> '12 minutes'."""
    if seconds < 60:
        if seconds == int(seconds):
            n = int(seconds)
            return f"{n} second" + ("" if n == 1 else "s")
        return f"{seconds:g} seconds"
    minutes = seconds / 60
    if minutes == int(minutes):
        n = int(minutes)
        return f"{n} minute" + ("" if n == 1 else "s")
    return f"{minutes:.1f} minutes"


def get_environment(name):
    """Settings for an environment, matched ignoring case. Unknown names give the ISS."""
    wanted = str(name or "").strip().casefold()
    key = next((k for k in ENVIRONMENT_SETTINGS if k.casefold() == wanted), DEFAULT_ENVIRONMENT)
    settings = dict(ENVIRONMENT_SETTINGS[key])
    settings["name"] = key
    settings["one_way_text"] = format_duration(settings["one_way_delay_s"])
    settings["round_trip_text"] = format_duration(settings["one_way_delay_s"] * 2)
    return settings
