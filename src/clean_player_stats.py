import pandas as pd
import unicodedata

def clean_player_stats(input_path, output_path):
    keep_stats = [
        'PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'AGE', 'GP', 'MIN',
        'PTS', 'REB', 'OREB', 'AST', 'STL', 'BLK', 'TOV',
        'FG_PCT', 'FG3M', 'FG3_PCT', 'FT_PCT', 'PLUS_MINUS'
    ]
    
    df = pd.read_csv(input_path)
    df_cleaned = df[keep_stats]
    df_cleaned['MIN'] = df_cleaned['MIN'].astype(int)
    df_cleaned['AGE'] = df_cleaned['AGE'].astype(int)
    df_cleaned['PLAYER_NAME'] = df["PLAYER_NAME"].apply(normalize_name)
    df_cleaned.to_csv(output_path, index=False)

    print(f"Cleaned player stats saved to {output_path}")

def normalize_name(name):
    return unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8').strip().lower()

if __name__ == "__main__":
    for season in ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]:
        clean_player_stats(
            input_path=f"data/player_stats_{season}.csv",
            output_path=f"data/player_stats_{season}_cleaned.csv"
        )