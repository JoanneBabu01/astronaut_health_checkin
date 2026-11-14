# Data: what is real, what is simulated, and the limits

> **Decision support, not diagnosis.** Everything in this folder is for education and demonstration. It is not medical advice.

## The short version

| File | What it is | Real or simulated |
| --- | --- | --- |
| `sample_crew_log.csv` | 50 days of daily check-ins for one pretend astronaut ("Commander A") | **Simulated** |
| `real_inspiration4_labs.csv` | Blood-test results from the four Inspiration4 crew members, at 7 timepoints | **Real** (NASA OSDR) |

Rows added to `sample_crew_log.csv` later through the app's Log Vitals form are entered by whoever uses the app. They are not simulated, and the file has no column that marks them, so treat any row after the generated 50 as user-entered.

## What is real

`real_inspiration4_labs.csv` comes from NASA's [Open Science Data Repository (OSDR)](https://osdr.nasa.gov/), from the Inspiration4 mission (four civilians, a short flight of about three days):

- **Complete blood count (CBC)**, study OSD-569: for example white blood cell count, red blood cells, hemoglobin.
- **Comprehensive metabolic panel (CMP)**, study OSD-575: for example glucose, calcium, sodium, potassium, kidney and liver markers.

It has **4 crew members** (anonymised as C001 to C004), **41 analytes** and **7 timepoints**: 92, 44 and 3 days before launch (`L-92`, `L-44`, `L-3`) and 1, 45, 82 and 194 days after return (`R+1`, `R+45`, `R+82`, `R+194`). That is 1,034 measurements.

**Credit:** Data from the NASA Open Science Data Repository, Inspiration4 studies OSD-569 and OSD-575.

`scripts/prepare_real_data.py` converts the two downloaded files into one tidy table. The raw files are not stored in this repo; download them from OSDR and run:

```
python scripts/prepare_real_data.py --cbc <path to the CBC csv> --cmp <path to the CMP csv>
```

What the converter changes:

- Rows whose value was not a plain number (for example `<0.1`) are skipped (23 rows).
- The sex column and the race-adjusted eGFR values are left out.
- `status` (in range / low / high) is judged against **the lab's own reference range** for each analyte, not against the thresholds in `core/thresholds.py`.

| Column | Meaning |
| --- | --- |
| `crew` | Anonymised crew member (C001-C004) |
| `timepoint` | `L-n` = n days before launch, `R+n` = n days after return |
| `phase` | pre-flight or post-flight |
| `timepoint_order` | 1-7, in time order (handy for chart axes) |
| `test` | CBC or CMP |
| `analyte` | The measurement, for example `white_blood_cell_count` |
| `value`, `unit` | The result and its unit |
| `ref_min`, `ref_max` | The lab's reference range |
| `status` | in range, low, high, or no range |
| `source` | Which OSDR study it came from |

## What is simulated

`scripts/prepare_data.py` generates `sample_crew_log.csv`. It is reproducible: the random seed is fixed (`42`), so the same code gives the same values. The 50 days **end on the day before the script is run**, so the app's "next check-in due" reminder is not months overdue.

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

### Columns of `sample_crew_log.csv`

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
- `scripts/prepare_real_data.py` is tested on small mock files that copy the column layout of the real OSDR files (`tests/test_real_data.py`).

## Limits

- **The simulated data is one pretend person.** Nothing in `sample_crew_log.csv` shows how real astronauts behave.
- **Daily readings only** in the simulated file, with no hourly or continuous data.
- **Simulated indicators are independent random noise.** Apart from the planted story, poor sleep does not cause low mood or high heart rate, as it might in a real person.
- **The real data is only four people** on a short flight, measured about seven times. It cannot show trends or what happens on a long mission. Over these timepoints, the white blood cell counts we checked stayed within the lab's normal range. Do not read more into it than that.
- **The real and simulated files measure different things.** The real file is blood tests; the simulated file is daily vitals, mood and sleep. They are not combined.
- **Thresholds are common adult reference ranges** (see `core/thresholds.py`), not spaceflight limits. Real flight medicine compares each astronaut with their own baseline, which this version does not do.
- **Not clinically validated.** Do not use any of it to make health decisions.

## Regenerate and test

From the repo root:

```
python scripts/prepare_data.py     # rewrites data/sample_crew_log.csv
python -m pytest -q tests          # runs all tests
```

Regenerating the simulated file on a different day shifts every date by that many days, so only do it when you mean to.
