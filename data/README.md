# Data: what is real, what is simulated, and the limits

> **Decision support, not diagnosis.** Everything in this folder is for education and demonstration. It is not medical advice.

## The short version

- `sample_crew_log.csv` holds **50 days of simulated check-ins for one pretend astronaut ("Commander A")**.
- **No real astronaut data is used in this version.**
- Rows added later through the app's Log Vitals form are entered by whoever uses the app. They are not simulated, and the file has no column that marks them, so treat any row after the generated 50 as user-entered.

## What is real

Nothing in the current dataset. NASA's [Open Science Data Repository (OSDR)](https://osdr.nasa.gov/) holds real blood-test data from the Inspiration4 crew, but according to [the paper describing it](https://www.nature.com/articles/s41526-024-00393-5), public access covers processed data only, and individual-level data needs an approved application. We did not use it.

## What is simulated

`scripts/prepare_data.py` generates the file. It is reproducible: the random seed is fixed (`42`), so the same code gives the same values. The 50 days **end on the day before the script is run**, so the app's "next check-in due" reminder is not months overdue.

Each indicator is a baseline plus random noise (a normal distribution, so values wobble a little from day to day), with a deliberate **story** added so the charts show green, amber and red:

| Days | What happens |
| --- | --- |
| 1-19 | Normal: indicators sit in the green range, apart from the odd noisy reading |
| 20-24 | A stressful week: sleep drops to about 5.8 h, stress rises, exercise falls |
| 22-30 | Mood dips (red at the lowest point) and then recovers |
| 25-50 | Blood pressure and resting heart rate climb slowly; blood pressure ends in the red range |
| 33 | One high blood glucose reading |
| 40-42 | A mild rise in body temperature (amber) |

**Baselines and drift sizes are illustrative.** Baselines were chosen so normal days land in the green range of our starting thresholds. The size of each drift has not been checked against published spaceflight values.

## Columns

One row per check-in. Names match `core/data.py` and must not be renamed without telling the team.

| Column | Meaning | Unit / range |
| --- | --- | --- |
| `timestamp` | When the check-in was taken | `YYYY-MM-DD HH:MM` |
| `astronaut` | Who | text |
| `environment` | Where | ISS, Transit, Lunar base, Mars base |
| `systolic_bp` | Blood pressure, top number | mmHg |
| `diastolic_bp` | Blood pressure, bottom number | mmHg |
| `heart_rate` | Resting heart rate | bpm |
| `blood_glucose` | Fasting blood sugar | mg/dL |
| `body_temp` | Body temperature | °C |
| `sleep_hours` | Sleep the previous night | hours |
| `mood` | 1 = very low, 5 = great | 1-5 |
| `stress` | 1 = calm, 5 = overwhelmed | 1-5 |
| `exercise_min` | Exercise that day | minutes |

## Validation

- `scripts/prepare_data.py` checks its output (right columns, no missing values, nothing impossible) before writing the file.
- `core/data.py` `save_entry()` refuses impossible values (for example a heart rate of 0 or a temperature of 50) and writes nothing when it does. Dangerous but possible readings, such as a systolic pressure of 150, can still be logged so the app can flag them red.
- `load_log()` reads both ISO dates (`2026-11-14 08:00`) and day-first dates (`14-11-2026 08:00`), which is what Excel writes if the CSV is re-saved there. Avoid editing the CSV in Excel.

## Limits

- **One pretend person.** Nothing here shows how real astronauts behave.
- **Daily readings only,** with no hourly or continuous data.
- **Indicators are independent random noise.** Apart from the planted story, poor sleep does not cause low mood or high heart rate, as it might in a real person.
- **Thresholds are common adult reference ranges** (see `core/thresholds.py`), not spaceflight limits. Real flight medicine compares each astronaut with their own baseline, which this version does not do.
- **Not clinically validated.** Do not use it to make health decisions.

## Regenerate and test

From the repo root:

```
python scripts/prepare_data.py     # rewrites data/sample_crew_log.csv
python -m pytest -q tests          # runs all tests
```

Regenerating on a different day shifts every date by that many days, so only do it when you mean to.
