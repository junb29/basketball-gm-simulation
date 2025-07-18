import pandas as pd

df = pd.read_csv("data/player_stats_2024-25_with_salaries.csv")
df = df[df["SALARY"] == 0]
print(len(df))