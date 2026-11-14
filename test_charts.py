import pandas as pd
from core.charts import trend_chart

df = pd.read_csv("data/sample_crew_log.csv")
trend_chart(df, "heart_rate").show()