import os
from nba_api.stats.endpoints import teamestimatedmetrics, leaguedashplayerstats

DATA_DIR = "data"

def get_team_estimates(seasons=["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"], save=True):
    
    for season in seasons:
        metrics = teamestimatedmetrics.TeamEstimatedMetrics(season=season)
        df = metrics.get_data_frames()[0]
        
        if save:
            os.makedirs(DATA_DIR, exist_ok=True)
            df.to_csv(f"{DATA_DIR}/team_estimates_{season}.csv", index=False)
            print(f"{season} season team data saved")
        

def get_player_stats(seasons=["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"], per_mode="Totals", save=True):
    
    for season in seasons:
        stats = leaguedashplayerstats.LeagueDashPlayerStats(
            season=season,
            per_mode_detailed=per_mode
        )
        df = stats.get_data_frames()[0]

        if save:
            os.makedirs(DATA_DIR, exist_ok=True)
            df.to_csv(f"{DATA_DIR}/player_stats_{season}.csv", index=False)
            print(f"{season} season player data saved")

if __name__ == "__main__":
    team_df = get_team_estimates()
    player_df = get_player_stats()
