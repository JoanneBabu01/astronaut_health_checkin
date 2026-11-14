# content/guidance.py
# Owner: Role 4 (Joanne)
# Advice text for each indicator and status.
# Write for a tired astronaut, not a doctor. Keep each sentence short.
#
# Green is one text. Amber and red have "low" and "high" texts for
# indicators that can go wrong in both directions.

from core.thresholds import THRESHOLDS

GUIDANCE = {
    "systolic_bp": {
        "green": {
            "meaning": "Your top blood pressure number is in the healthy range.",
            "action": "Keep exercising and drinking water as usual.",
            "escalate": "No need to report. Check again tomorrow.",
        },
        "amber": {
            "high": {
                "meaning": "Your top number is a little high.",
                "action": "Rest, drink water, and measure again in an hour.",
                "escalate": "Tell the crew doctor if it stays high for 3 days.",
            },
            "low": {
                "meaning": "Your top number is a little low.",
                "action": "Sit down, drink water, and stand up slowly.",
                "escalate": "Tell the crew doctor if you feel dizzy or it stays low for 3 days.",
            },
        },
        "red": {
            "high": {
                "meaning": "Your top number is high.",
                "action": "Sit and rest for 5 minutes, then measure again.",
                "escalate": "Tell the crew doctor today. If it is above 180, get medical help right away.",
            },
            "low": {
                "meaning": "Your top number is very low.",
                "action": "Sit or lie down and drink water. Do not stand up fast.",
                "escalate": "Tell the crew doctor today. Get help right away if you feel faint.",
            },
        },
    },
    "diastolic_bp": {
        "green": {
            "meaning": "Your bottom blood pressure number is in the healthy range.",
            "action": "Keep exercising and drinking water as usual.",
            "escalate": "No need to report. Check again tomorrow.",
        },
        "amber": {
            "high": {
                "meaning": "Your bottom number is a little high.",
                "action": "Rest, drink water, and measure again in an hour.",
                "escalate": "Tell the crew doctor if it stays high for 3 days.",
            },
            "low": {
                "meaning": "Your bottom number is a little low.",
                "action": "Sit down, drink water, and stand up slowly.",
                "escalate": "Tell the crew doctor if you feel dizzy or it stays low for 3 days.",
            },
        },
        "red": {
            "high": {
                "meaning": "Your bottom number is high.",
                "action": "Sit and rest for 5 minutes, then measure again.",
                "escalate": "Tell the crew doctor today. If it is above 120, get medical help right away.",
            },
            "low": {
                "meaning": "Your bottom number is very low.",
                "action": "Sit or lie down and drink water. Do not stand up fast.",
                "escalate": "Tell the crew doctor today. Get help right away if you feel faint.",
            },
        },
    },
    "sleep_hours": {
        "green": {"meaning": "TODO", "action": "TODO", "escalate": "TODO"},
        "amber": {
            "high": {"meaning": "TODO", "action": "TODO", "escalate": "TODO"},
            "low": {"meaning": "TODO", "action": "TODO", "escalate": "TODO"},
        },
        "red": {
            "high": {"meaning": "TODO", "action": "TODO", "escalate": "TODO"},
            "low": {"meaning": "TODO", "action": "TODO", "escalate": "TODO"},
        },
    },
}

HOW_TO_MEASURE = {
    "systolic_bp": "Sit still for 5 minutes. Use the same arm each time. Keep the cuff at heart level. Take two readings, one minute apart.",
    "diastolic_bp": "Sit still for 5 minutes. Use the same arm each time. Keep the cuff at heart level. Take two readings, one minute apart.",
    "sleep_hours": "TODO",
}


def get_direction(indicator, value):
    """Return "low" if the value is below the green range, else "high"."""
    green_low, _ = THRESHOLDS[indicator]["green"]
    return "low" if value < green_low else "high"


def get_guidance(indicator, status, environment="ISS", value=None):
    
    entry = GUIDANCE[indicator][status]
    if "meaning" in entry:  
        return entry
    direction = get_direction(indicator, value) if value is not None else "high"
    return entry[direction]