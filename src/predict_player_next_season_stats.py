import pandas as pd
from joblib import load
from .utils import predict_minutes, adjust_shooting_percentage, add_stat_variance, predict_gp, predict_plus_minus, all_years_df

# Load trained aging models (done once at script startup)
aging_models = {
    "PTS_per_min": load("models/player_aging/aging_model_PTS_per_min.joblib"),
    "REB_per_min": load("models/player_aging/aging_model_REB_per_min.joblib"),
    "OREB_per_min": load("models/player_aging/aging_model_OREB_per_min.joblib"),
    "AST_per_min": load("models/player_aging/aging_model_AST_per_min.joblib"),
    "BLK_per_min": load("models/player_aging/aging_model_BLK_per_min.joblib"),
    "STL_per_min": load("models/player_aging/aging_model_STL_per_min.joblib"),
    "TOV_per_min": load("models/player_aging/aging_model_TOV_per_min.joblib"),
    "FG3M": load("models/player_aging/aging_model_FG3M.joblib")
}

# Load 2024-25 player stats once
player_df = pd.read_csv("data/player_stats_2024-25_cleaned.csv")

def predict_player_next_season(player_row):
    # Age adjustment
    age_next = player_row["AGE"] + 1
    minutes_last = round(player_row["MIN"] / player_row["GP"], 1)

    # Predict minutes
    pts_per_min_last = player_row["PTS"] / player_row["MIN"] if player_row["MIN"] > 0 else 0
    predicted_minutes = predict_minutes(minutes_last, age_next, pts_per_min_last)

    # Predict per-minute stats
    predicted_stats = {}

    for stat in ["PTS", "REB", "OREB", "AST", "STL", "BLK", "TOV"]:
        stat_per_min_last = player_row[stat] / player_row["MIN"] if player_row["MIN"] > 0 else 0
        model = aging_models[f"{stat}_per_min"]
        X_pred = pd.DataFrame(
            [[stat_per_min_last, player_row["AGE"]]],
            columns=[f"{stat}_per_min_last", "AGE_last"]
        )
        predicted_per_min = model.predict(X_pred)[0]
        predicted_total = predicted_per_min * predicted_minutes
        predicted_total = add_stat_variance(predicted_total)
        predicted_stats[stat] = round(predicted_total, 1)

    # Predict FG3M, GP, PLUS_MINUS
    predicted_stats["GP"] = min(82, round(add_stat_variance(predict_gp(player_row))))
    model = aging_models["FG3M"]
    X_pred = pd.DataFrame([[player_row["FG3M"], player_row["AGE"]]], columns=["FG3M_last", "AGE_last"])
    predicted_fg3m = model.predict(X_pred)[0]
    predicted_stats["FG3M"] = round(add_stat_variance(predicted_fg3m / predicted_stats["GP"]), 1)
    predicted_stats["PLUS_MINUS"] = round(add_stat_variance(predict_plus_minus(player_row) / predicted_stats["GP"]), 1)

    # Predict shooting percentages
    predicted_stats["FG_PCT"] = adjust_shooting_percentage(player_row["FG_PCT"], age_next)
    predicted_stats["FG3_PCT"] = adjust_shooting_percentage(player_row["FG3_PCT"], age_next)
    predicted_stats["FT_PCT"] = adjust_shooting_percentage(player_row["FT_PCT"], age_next)

    # Predict minutes and age
    predicted_stats["MIN"] = predicted_minutes
    predicted_stats["AGE"] = age_next

    return predicted_stats

def predict_by_name_or_id(player_identifier):
    """
    Look up player by PLAYER_NAME or PLAYER_ID from 2024-25 dataset
    and predict next season's stat line.
    """
    # PLAYER_ID (numeric search)
    if isinstance(player_identifier, int):
        player_row = player_df[player_df["PLAYER_ID"] == player_identifier]
    else:
        # PLAYER_NAME string search
        player_row = player_df[player_df["PLAYER_NAME"].str.lower() == player_identifier.lower()]

    if player_row.empty:
        print(f"Player '{player_identifier}' not found in 2024-25 dataset.")
        return None

    # Get the single row as dict
    player_row = player_row.iloc[0]

    # Predict next season stats
    prediction = predict_player_next_season(player_row)
    return prediction

# Example usage:
if __name__ == "__main__":
    # Simulate user input (example)
    user_input = "jayson tatum"  # or could be player_id like 1629029
    result = predict_by_name_or_id(user_input)

    if result:
        print(f"Predicted 2025-26 stats for {user_input}:")
        for k, v in result.items():
            print(f"{k}: {v}")