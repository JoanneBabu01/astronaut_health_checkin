import pandas as pd
from core.charts import health_radar

df = pd.read_csv("data/sample_crew_log.csv")
health_radar(df.iloc[-1]).show()
