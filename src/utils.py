import random
import pandas as pd
import numpy as np

def adjust_shooting_percentage(current_pct, age):
    """
    Predict next-season shooting percentage for a player based on simple age-aware heuristics.
    """
    adjustment = 0
    rand_val = random.uniform(0, 1)

    if age < 25:
        if rand_val < 0.3:
            adjustment = 0.02
        elif rand_val < 0.6:
            adjustment = 0.01
        elif rand_val < 0.9:
            adjustment = 0
        else:
            adjustment = -0.01

    elif 25 <= age <= 30:
        if rand_val < 0.1:
            adjustment = 0.02
        elif rand_val < 0.4:
            adjustment - 0.01
        elif rand_val < 0.8:
            adjustment = 0.00
        else:
            adjustment = -0.01

    elif 31 <= age <= 34:
        if rand_val < 0.1:
            adjustment = 0.01
        elif rand_val < 0.6:
            adjustment = 0.00
        else:
            adjustment = -0.01

    else:  # age >= 35
        if rand_val < 0.3:
            adjustment = 0
        elif rand_val < 0.65:
            adjustment = -0.01
        elif rand_val < 0.9:
            adjustment = -0.02
        else:
            adjustment = 0.01

    new_pct = current_pct + adjustment
    new_pct = min(max(new_pct, 0), 1)
    return round(new_pct, 2)

def predict_minutes(minutes_last, age, pts_per_min_last):
    """
    Predict next-season minutes for a player based on simple age-aware heuristics.
    """
    rand_val = random.uniform(0, 1)

    if age < 25:
        # Define a young breakout threshold
        if pts_per_min_last >= 0.5 and minutes_last < 28:
            # Breakout candidate: boost minutes aggressively
            if rand_val < 0.2:
                predicted = min(minutes_last + 10, 36)  # Major leap
            elif rand_val < 0.5:
                predicted = min(minutes_last + 6, 36)   # Moderate leap
            else:
                predicted = min(minutes_last + 3, 36)   # Conservative increase
        else:
            # Normal young player: mild changes
            if rand_val < 0.3:
                predicted = minutes_last + 2
            elif rand_val < 0.6:
                predicted = minutes_last + 1
            elif rand_val < 0.8:
                predicted = minutes_last
            else:
                predicted = minutes_last - 1

    elif 25 <= age <= 30:
        # Slight decline pattern
        if rand_val < 0.3:
            predicted = minutes_last
        elif rand_val < 0.6:
            predicted = minutes_last + 1
        elif rand_val < 0.9:
            predicted = minutes_last - 1
        else:
            predicted = minutes_last - 2

    elif 31 <= age <= 34:
        # Moderate decline
        if rand_val < 0.4:
            predicted = minutes_last - 1
        elif rand_val < 0.8:
            predicted = minutes_last - 2
        else:
            predicted = minutes_last

    else:  # age >= 35
        # Steeper decline
        if rand_val < 0.6:
            predicted = minutes_last - 3
        elif rand_val < 0.9:
            predicted = minutes_last - 2
        else:
            predicted = minutes_last - 1

    # Clamp to valid NBA range
    predicted = max(min(predicted, 38), 0)

    return round(predicted, 1)


def add_stat_variance(predicted_stat, variance=0.1):
    scale = max(variance * abs(predicted_stat), 0.01)
    noise = np.random.normal(0, scale)
    return predicted_stat + noise


# Load historical player stats just once at module level
all_years_df = pd.concat([
    pd.read_csv(f"data/player_stats_{season}_cleaned.csv")
    for season in ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]
])

all_years_df['PLAYER_NAME'] = all_years_df['PLAYER_NAME'].str.lower().str.strip()

def predict_gp(player_row):
    name = player_row["PLAYER_NAME"].lower().strip()
    history = all_years_df[all_years_df["PLAYER_NAME"] == name]
    
    # Filter to seasons where GP >= 30
    history = history[history["GP"] >= 30]

    if len(history) == 0:
        # Fallback if player never played 30+ games
        return min(round(all_years_df["GP"].mean(), 0), 82)

    gp_mean = history["GP"].mean()
    return min(round(gp_mean, 0), 82)

def predict_plus_minus(player_row):
    name = player_row["PLAYER_NAME"].lower().strip()
    history = all_years_df[all_years_df["PLAYER_NAME"] == name]
    
    if len(history) < 2:
        return round(player_row["PLUS_MINUS"], 1)
    
    pm_last = history.iloc[-1]["PLUS_MINUS"]
    pm_prev = history.iloc[-2]["PLUS_MINUS"]
    delta = pm_last - pm_prev
    predicted_pm = pm_last + (0.5 * delta) 
    return round(predicted_pm, 1)
