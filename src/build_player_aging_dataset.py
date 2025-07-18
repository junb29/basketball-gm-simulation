import pandas as pd

def build_player_aging_dataset():
    
    seasons = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]
    player_data = []

    for season in seasons:
        df = pd.read_csv(f"data/player_stats_{season}_cleaned.csv")
        df["SEASON"] = season
        player_data.append(df)

    all_players = pd.concat(player_data, ignore_index=True)
    all_players = all_players.sort_values(by=["PLAYER_ID", "SEASON"])

    records = []

    for player_id, group in all_players.groupby("PLAYER_ID"):
        group = group.sort_values("SEASON")
        seasons_list = group["SEASON"].tolist()
        
        if len(seasons_list) < 2:
            continue
        
        for i in range(len(seasons_list) -1):
            season_t = seasons_list[i]
            season_t1 = seasons_list[i+1]
            
            stats_t = group[group["SEASON"] == season_t].iloc[0]
            stats_t1 = group[group["SEASON"] == season_t1].iloc[0]
            
            stats_t = group[group["SEASON"] == season_t].iloc[0]
            stats_t1 = group[group["SEASON"] == season_t1].iloc[0]

            # Filter out players who didn’t play much either season
            if stats_t["MIN"] < 200 or stats_t1["MIN"] < 200:
                continue
            
            record = {
                "PLAYER_ID": player_id,
                "AGE_last": stats_t["AGE"],
                "SEASON_last": season_t,
                "SEASON_next": season_t1
            }
            
            # Compute per-minute stats for both years
            for stat in ["PTS", "REB", "OREB", "AST", "STL", "BLK", "TOV"]:
                per_min_last = stats_t[stat] / stats_t["MIN"] if stats_t["MIN"] > 0 else 0
                per_min_next = stats_t1[stat] / stats_t1["MIN"] if stats_t1["MIN"] > 0 else 0

                record[f"{stat}_per_min_last"] = round(per_min_last, 3)
                record[f"{stat}_per_min_next"] = round(per_min_next, 3)

            for stat in ["FG3M"]:
                record[f"{stat}_last"] = round(stats_t[stat] / stats_t["GP"], 1)
                record[f"{stat}_next"] = round(stats_t1[stat] / stats_t1["GP"], 1)

            records.append(record)

    history_df = pd.DataFrame(records)
    history_df.to_csv("data/player_aging_dataset.csv", index=False)
    print("Saved player aging dataset with per-minute stats")

if __name__ == "__main__":
    build_player_aging_dataset()