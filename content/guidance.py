GUIDANCE = {
    "sleep_hours": {
        "green": {
            "meaning": "TODO",
            "action": "TODO",
            "escalate": "TODO",
        },
        "amber": {
            "meaning": "TODO",
            "action": "TODO",
            "escalate": "TODO",
        },
        "red": {
            "meaning": "TODO",
            "action": "TODO",
            "escalate": "TODO",
        },
    },
}

HOW_TO_MEASURE = {
    "sleep_hours": "TODO",
}


def get_guidance(indicator, status, environment="ISS"):
    """Return meaning, action and escalation text for one reading."""
    return GUIDANCE[indicator][status]