import pandas as pd
from core.charts import bp_chart, status_gauge

df = pd.read_csv("data/sample_crew_log.csv")
bp_chart(df).show()
status_gauge("heart_rate", 72).show()