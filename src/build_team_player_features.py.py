import pandas as pd

SEASONS = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]
TOP_N_PLAYERS = 9

PLAYER_FEATURES = ['PTS', 'REB', 'OREB', 'AST', 'STL', 'BLK', 'TOV', 'FG_PCT', 'FG3_PCT', 'FG3M', 'FT_PCT', 'PLUS_MINUS', 'AGE', 'MIN', 'GP']

PER_GAME_STATS = ['PTS', 'REB', 'OREB', 'AST', 'STL', 'BLK', 'TOV']

TEAM_NAME_TO_ABBR = {
    "Atlanta Hawks": "ATL",
    "Boston Celtics": "BOS",
    "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA",
    "Chicago Bulls": "CHI",
    "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL",
    "Denver Nuggets": "DEN",
    "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW",
    "Houston Rockets": "HOU",
    "Indiana Pacers": "IND",
    "LA Clippers": "LAC",
    "Los Angeles Lakers": "LAL",
    "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA",
    "Milwaukee Bucks": "MIL",
    "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP",
    "New York Knicks": "NYK",
    "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL",
    "Philadelphia 76ers": "PHI",
    "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR",
    "Sacramento Kings": "SAC",
    "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR",
    "Utah Jazz": "UTA",
    "Washington Wizards": "WAS"
}

def build_team_row(team_df, team_abbr, season):
    
    team_players = team_df[team_df["TEAM_ABBREVIATION"] == team_abbr]

    # Filter players who played 20+ games 
    team_players = team_players[team_players["GP"] >= 20]

    # Compute per-game stats for selected stats
    for stat in PER_GAME_STATS:
        team_players[stat] = team_players.apply(
            lambda row: round(row[stat] / row["GP"], 1),
            axis=1
        )
    
    # Sort by points per game descending
    team_players = team_players.sort_values("PTS", ascending=False)

    row = {'TEAM_ABBREVIATION': team_abbr, 'SEASON': season}
    
    for i in range(TOP_N_PLAYERS):
        if i < len(team_players):
            player = team_players.iloc[i]
            for feat in PLAYER_FEATURES:
                row[f'P{i+1}_{feat}'] = player[feat]
        else:
            # Pad with zeros
            for feat in PLAYER_FEATURES:
                row[f'P{i+1}_{feat}'] = 0
    return row

def build_full_dataset():
    dataset_rows = []
    for season in SEASONS:
        
        player_path = f"data/player_stats_{season}_cleaned.csv"
        players = pd.read_csv(player_path)
        
        for stat in ["FG3M", "MIN", "PLUS_MINUS"]:
            players[stat] = round(players[stat] / players["GP"], 1)
        
        team_path = f"data/team_estimates_{season}_cleaned.csv"
        teams = pd.read_csv(team_path)
        
        # Map team names
        for team_abbr in players["TEAM_ABBREVIATION"].unique():
            row = build_team_row(players, team_abbr, season)
            wins = teams.loc[teams["TEAM_NAME"].map(TEAM_NAME_TO_ABBR) == team_abbr, "W"].values
            if len(wins) > 0:
                row['W'] = wins[0]
                dataset_rows.append(row)

    df = pd.DataFrame(dataset_rows)
    df.to_csv("data/team_player_features.csv", index=False)
    print("Saved team_player_features.csv with player-level representation")
    return df

if __name__ == "__main__":
    build_full_dataset()
