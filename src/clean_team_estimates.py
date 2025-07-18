import pandas as pd
import os

SEASONS = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]

KEEP_COLS = [
    "TEAM_NAME", "GP", "W", "L", "W_PCT",
    "E_OFF_RATING", "E_DEF_RATING", "E_NET_RATING",
    "E_PACE", "E_AST_RATIO", "E_OREB_PCT", "E_DREB_PCT", "E_REB_PCT", "E_TM_TOV_PCT"
]

def clean_team_estimates(season):
    path = f"data/team_estimates_{season}.csv"
    df = pd.read_csv(path)
    df_cleaned = df[KEEP_COLS]
    df_cleaned.to_csv(f"data/team_estimates_{season}_cleaned.csv", index=False)
    print(f"Cleaned {season} saved.")

def clean_all_team_estimates():
    for season in SEASONS:
        clean_team_estimates(season)

if __name__ == "__main__":
    clean_all_team_estimates()
