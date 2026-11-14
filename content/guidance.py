# content/guidance.py
# Owner: Role 4 (Joanne)
# Advice text for each indicator and status.
# Write for a tired astronaut, not a doctor. Keep each sentence short.
#
# Green is one text. For indicators that can go wrong in both directions,
# amber and red have a "low" text and a "high" text.
# One-sided indicators (mood, stress, exercise_min) have one text per colour.
# For educational use. Decision support, not a diagnosis.

from core.thresholds import THRESHOLDS

GUIDANCE = {
    # ---------------------------------------------------------------- blood pressure
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
    # ---------------------------------------------------------------- heart rate
    "heart_rate": {
        "green": {
            "meaning": "Your resting heart rate is in the healthy range.",
            "action": "Keep up your exercise and rest routine.",
            "escalate": "No need to report.",
        },
        "amber": {
            "high": {
                "meaning": "Your resting heart rate is a little high.",
                "action": "Sit quietly, drink water, and measure again in 30 minutes.",
                "escalate": "Tell the crew doctor if it stays high for 3 days.",
            },
            "low": {
                "meaning": "Your resting heart rate is a little low.",
                "action": "Sit down and stand up slowly. Measure again later today.",
                "escalate": "Tell the crew doctor if you feel dizzy or it stays low for 3 days.",
            },
        },
        "red": {
            "high": {
                "meaning": "Your resting heart rate is very high.",
                "action": "Sit down, breathe slowly, and rest for 10 minutes. Then measure again.",
                "escalate": "Tell the crew doctor today. Get help right away if you have chest pain or trouble breathing.",
            },
            "low": {
                "meaning": "Your resting heart rate is very low.",
                "action": "Sit or lie down. Do not stand up fast.",
                "escalate": "Tell the crew doctor today. Get help right away if you feel faint or have chest pain.",
            },
        },
    },
    # ---------------------------------------------------------------- blood glucose
    "blood_glucose": {
        "green": {
            "meaning": "Your fasting blood sugar is in the healthy range.",
            "action": "Keep eating regular, balanced meals.",
            "escalate": "No need to report.",
        },
        "amber": {
            "high": {
                "meaning": "Your fasting blood sugar is a little high.",
                "action": "Drink water, avoid sugary food, and measure again tomorrow before eating.",
                "escalate": "Tell the crew doctor if it stays high for 3 days.",
            },
            "low": {
                "meaning": "Your fasting blood sugar is a little low.",
                "action": "Eat a small snack and measure again in 15 minutes.",
                "escalate": "Tell the crew doctor if it stays low or you feel shaky.",
            },
        },
        "red": {
            "high": {
                "meaning": "Your fasting blood sugar is high.",
                "action": "Drink water, avoid sugary food, and measure again.",
                "escalate": "Tell the crew doctor today.",
            },
            "low": {
                "meaning": "Your fasting blood sugar is very low.",
                "action": "Eat or drink something sugary now. Measure again in 15 minutes.",
                "escalate": "Tell the crew doctor right away.",
            },
        },
    },
    # ---------------------------------------------------------------- body temperature
    "body_temp": {
        "green": {
            "meaning": "Your body temperature is normal.",
            "action": "Nothing to do. Keep drinking water.",
            "escalate": "No need to report.",
        },
        "amber": {
            "high": {
                "meaning": "Your temperature is a little high.",
                "action": "Rest, drink water, and measure again in an hour.",
                "escalate": "Tell the crew doctor if it stays up for a day.",
            },
            "low": {
                "meaning": "Your temperature is a little low.",
                "action": "Warm up with an extra layer and a warm drink. Measure again in an hour.",
                "escalate": "Tell the crew doctor if it stays low for a day.",
            },
        },
        "red": {
            "high": {
                "meaning": "You may have a fever.",
                "action": "Rest, drink water, and measure again in an hour.",
                "escalate": "Tell the crew doctor today. Get help right away if you feel confused or short of breath.",
            },
            "low": {
                "meaning": "Your temperature is low.",
                "action": "Warm up now with extra layers and warm drinks. Measure again in 30 minutes.",
                "escalate": "Tell the crew doctor today.",
            },
        },
    },
    # ---------------------------------------------------------------- sleep
    "sleep_hours": {
        "green": {
            "meaning": "You slept a healthy amount.",
            "action": "Keep your bedtime and wake-up time regular.",
            "escalate": "No need to report.",
        },
        "amber": {
            "high": {
                "meaning": "You slept more than usual.",
                "action": "Keep a regular schedule. Get some light and exercise today.",
                "escalate": "Tell the crew doctor if this lasts 3 days.",
            },
            "low": {
                "meaning": "You slept a bit less than you need.",
                "action": "Go to bed earlier tonight. Keep lights dim and screens off before sleep.",
                "escalate": "Tell the crew doctor if you sleep under 7 hours for 3 nights in a row.",
            },
        },
        "red": {
            "high": {
                "meaning": "You slept much longer than normal.",
                "action": "Keep a regular schedule, drink water, eat well, and move around.",
                "escalate": "Tell the crew doctor today, especially if you feel unwell or very tired.",
            },
            "low": {
                "meaning": "You slept far too little.",
                "action": "Protect your sleep tonight. Skip hard tasks and avoid caffeine late in the day.",
                "escalate": "Tell the crew doctor today. Do not take sleep medicine without their advice.",
            },
        },
    },
    # ---------------------------------------------------------------- mood (low is bad)
    "mood": {
        "green": {
            "meaning": "Your mood is good.",
            "action": "Keep up your routines: sleep, exercise, and time with the crew.",
            "escalate": "No need to report.",
        },
        "amber": {
            "meaning": "Your mood is lower than usual.",
            "action": "Take a short break, exercise, or call someone you trust.",
            "escalate": "Tell the crew doctor if your mood stays low for a week.",
        },
        "red": {
            "meaning": "Your mood is very low.",
            "action": "Talk to someone you trust today and take a break from work.",
            "escalate": "Tell the crew doctor today. If you have thoughts of harming yourself, get help right away.",
        },
    },
    # ---------------------------------------------------------------- stress (high is bad)
    "stress": {
        "green": {
            "meaning": "Your stress is low.",
            "action": "Keep up what is working for you.",
            "escalate": "No need to report.",
        },
        "amber": {
            "meaning": "Your stress is moderate.",
            "action": "Take a short break, breathe slowly, and do something relaxing.",
            "escalate": "Tell the crew doctor if it stays this way for a week.",
        },
        "red": {
            "meaning": "Your stress is very high.",
            "action": "Pause what you can, breathe slowly, and talk to someone you trust.",
            "escalate": "Tell the crew doctor today.",
        },
    },
    # ---------------------------------------------------------------- exercise (low is bad)
    "exercise_min": {
        "green": {
            "meaning": "You are getting enough exercise.",
            "action": "Keep it up. Exercise protects your bones, muscles and heart.",
            "escalate": "No need to report.",
        },
        "amber": {
            "meaning": "You exercised less than your target.",
            "action": "Add a short session today. Exercise protects your bones, muscles and heart.",
            "escalate": "Tell the crew doctor if you cannot exercise for several days.",
        },
        "red": {
            "meaning": "You got very little exercise.",
            "action": "Fit in a workout today, even a short one.",
            "escalate": "Tell the crew doctor if you skip exercise for 3 days or cannot exercise.",
        },
    },
}

HOW_TO_MEASURE = {
    "systolic_bp": "Sit still for 5 minutes. Use the same arm each time. Keep the cuff at heart level. Take two readings, one minute apart.",
    "diastolic_bp": "Sit still for 5 minutes. Use the same arm each time. Keep the cuff at heart level. Take two readings, one minute apart.",
    "heart_rate": "Sit quietly for 5 minutes. Read your monitor, or count your pulse at the wrist for 30 seconds and double it.",
    "blood_glucose": "Measure before eating, after at least 8 hours without food. Wash and dry your hands. Use a fresh test strip and follow your device instructions.",
    "body_temp": "Use the same thermometer each time, at the same time each morning. Wait 15 minutes after exercise or a hot drink.",
    "sleep_hours": "Note when you fall asleep and when you wake up. Count only the time you were actually asleep. Record it each morning.",
    "mood": "Each morning, rate how you feel from 1 (very low) to 5 (great). Go with your first feeling.",
    "stress": "Rate your stress from 1 (calm) to 5 (overwhelmed). Go with your first feeling.",
    "exercise_min": "Add up all your exercise minutes for the day: treadmill, bike and resistance training.",
}


def get_direction(indicator, value):
    """Return "low" if the value is below the green range, else "high"."""
    green_low, _ = THRESHOLDS[indicator]["green"]
    return "low" if value < green_low else "high"


def get_guidance(indicator, status, environment="ISS", value=None):
    """Return meaning, action and escalation text for one reading.

    Pass `value` so we can tell too-low from too-high.
    """
    entry = GUIDANCE[indicator][status]
    if "meaning" in entry:  # one text for everything (green, one-sided)
        return entry
    direction = get_direction(indicator, value) if value is not None else "high"
    return entry[direction]