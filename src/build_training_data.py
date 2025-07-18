import pandas as pd

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

SEASONS = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]

def merge_features_and_labels(season):
    features = pd.read_csv(f"data/team_features_{season}.csv")
    estimates = pd.read_csv(f"data/team_estimates_{season}_cleaned.csv")
    estimates["TEAM_ABBREVIATION"] = estimates["TEAM_NAME"].map(TEAM_NAME_TO_ABBR)

    merged = pd.merge(
    features,
    estimates[["TEAM_ABBREVIATION", "W", "E_NET_RATING"]],
    on="TEAM_ABBREVIATION",
    how="inner"
    )

    merged["SEASON"] = season
    return merged

def build_training_data():
    all_seasons = [merge_features_and_labels(season) for season in SEASONS]
    df = pd.concat(all_seasons, ignore_index=True)
    df.to_csv("data/team_training_data.csv", index=False)
    print("Saved full training dataset to data/team_training_data.csv")
    return df

if __name__ == "__main__":
    build_training_data()
