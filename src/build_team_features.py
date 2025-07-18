import pandas as pd

SEASONS = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]

# Define which columns to sum vs. mean
SUM_COLS = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'MIN', 'GP', 'FG3M', 'PLUS_MINUS']
MEAN_COLS = ['FG_PCT', 'FG3_PCT', 'FT_PCT', 'AGE']

def build_team_features(season):
    input_path = f"data/player_stats_{season}_cleaned.csv"
    output_path = f"data/team_features_{season}.csv"

    df = pd.read_csv(input_path)

    grouped_sum = df.groupby("TEAM_ABBREVIATION")[SUM_COLS].sum()
    grouped_mean = df.groupby("TEAM_ABBREVIATION")[MEAN_COLS].mean().round(2)

    team_features = pd.concat([grouped_sum, grouped_mean], axis=1).reset_index()
    team_features.to_csv(output_path, index=False)
    print(f"Saved team features for {season} to {output_path}")

def build_all_team_features():
    for season in SEASONS:
        build_team_features(season)

if __name__ == "__main__":
    build_all_team_features()
