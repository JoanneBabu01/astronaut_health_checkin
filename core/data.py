"""Load and save the crew health log. Plain Python, no Streamlit.

The CSV follows the team's data contract: one row per check-in.
"""
import csv
from datetime import datetime
from pathlib import Path

import pandas as pd

CSV_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_crew_log.csv"

COLUMNS = [
    "timestamp", "astronaut", "environment", "systolic_bp", "diastolic_bp",
    "heart_rate", "blood_glucose", "body_temp", "sleep_hours", "mood",
    "stress", "exercise_min",
]
ENVIRONMENTS = ["ISS", "Transit", "Lunar base", "Mars base"]
DEFAULT_ASTRONAUT = "Commander A"
MAX_NAME_LENGTH = 40
DEFAULT_ENVIRONMENT = "ISS"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M"

LIMITS = {
    "systolic_bp":   (int, 50, 260),
    "diastolic_bp":  (int, 30, 160),
    "heart_rate":    (int, 20, 250),
    "blood_glucose": (int, 20, 600),
    "body_temp":     (float, 30.0, 43.0),
    "sleep_hours":   (float, 0.0, 24.0),
    "mood":          (int, 1, 5),
    "stress":        (int, 1, 5),
    "exercise_min":  (int, 0, 1440),
}


_DAY_FIRST_FORMATS = (
    "%d-%m-%Y %H:%M", "%d-%m-%Y %H:%M:%S", "%d/%m/%Y %H:%M",
    "%d/%m/%Y %H:%M:%S", "%d-%m-%Y", "%d/%m/%Y",
)


def _parse_timestamps(values):
    """Parse timestamps even if the file mixes formats.

    Our own rows are ISO (2026-11-14 08:00). If someone opens the CSV in Excel
    and saves it, Windows may rewrite dates as 14-11-2026 08:00. Both are read
    correctly here (day first for the Excel style), so one re-save cannot crash
    the app.
    """
    values = values.astype(str).str.strip()
    parsed = pd.to_datetime(values, format="ISO8601", errors="coerce")
    for fmt in _DAY_FIRST_FORMATS:
        missing = parsed.isna()
        if not missing.any():
            break
        parsed[missing] = pd.to_datetime(values[missing], format=fmt, errors="coerce")
    if parsed.isna().any():
        bad = values[parsed.isna()].iloc[0]
        raise ValueError(f"Cannot read timestamp {bad!r} in the log file")
    return parsed


def load_log(astronaut=None, path=CSV_PATH):
    """Return the log as a DataFrame, oldest first.

    astronaut: if given, only that astronaut's rows. Names match ignoring upper
    or lower case and spaces at the ends, so "commander a " finds "Commander A".

    A missing or empty file, or a name with no rows, gives an empty DataFrame
    with the right columns, so pages can show a friendly "no data yet" message
    instead of crashing.
    """
    if isinstance(astronaut, Path):     
        astronaut, path = None, astronaut
    path = Path(path)
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame(columns=COLUMNS)
    df = pd.read_csv(path)
    if df.empty:
        return pd.DataFrame(columns=COLUMNS)
    df["timestamp"] = _parse_timestamps(df["timestamp"])
    if astronaut is not None:
        wanted = str(astronaut).strip().casefold()
        df = df[df["astronaut"].astype(str).str.strip().str.casefold() == wanted]
    return df.sort_values("timestamp").reset_index(drop=True)


def validate_entry(entry):
    """Return a cleaned copy of `entry` or raise ValueError saying what is wrong."""
    clean = {}
    problems = []

    missing = [c for c in LIMITS if entry.get(c) is None]
    if missing:
        raise ValueError("Missing readings: " + ", ".join(missing))

    for column, (kind, low, high) in LIMITS.items():
        raw = entry[column]
        try:
            value = float(raw)
        except (TypeError, ValueError):
            problems.append(f"{column} must be a number (got {raw!r})")
            continue
        if kind is int:
            if value != int(value):
                problems.append(f"{column} must be a whole number (got {raw!r})")
                continue
            value = int(value)
        if not low <= value <= high:
            problems.append(f"{column} {value} is not possible (allowed {low} to {high})")
            continue
        clean[column] = value

    environment = entry.get("environment") or DEFAULT_ENVIRONMENT
    if environment not in ENVIRONMENTS:
        problems.append(f"environment must be one of {ENVIRONMENTS}")
    clean["environment"] = environment
    name = str(entry.get("astronaut") or "").strip() or DEFAULT_ASTRONAUT
    if len(name) > MAX_NAME_LENGTH or any(ord(ch) < 32 for ch in name):
        problems.append(f"astronaut name must be at most {MAX_NAME_LENGTH} characters, on one line")
    clean["astronaut"] = name

    stamp = entry.get("timestamp") or datetime.now()
    try:
        clean["timestamp"] = pd.Timestamp(stamp).strftime(TIMESTAMP_FORMAT)
    except (ValueError, TypeError):
        problems.append(f"timestamp not understood: {stamp!r}")

    if problems:
        raise ValueError("; ".join(problems))
    return {c: clean[c] for c in COLUMNS}


def save_entry(entry, path=CSV_PATH):
    """Validate one check-in and append it to the CSV. Returns the saved row.

    Raises ValueError (nothing is written) if a reading is missing or
    impossible. If Streamlit's cache_data wraps load_log, clear it after saving.
    """
    row = validate_entry(entry)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    needs_header = not path.exists() or path.stat().st_size == 0
    needs_newline = False
    if not needs_header:
        with open(path, "rb") as f:
            f.seek(-1, 2)
            needs_newline = f.read(1) not in (b"\n", b"\r")

    with open(path, "a", newline="", encoding="utf-8") as f:
        if needs_newline:
            f.write("\n")
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if needs_header:
            writer.writeheader()
        writer.writerow(row)
    return row
