import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

def train_player_aging_models(data_path="data/player_aging_dataset.csv", save_dir="models/player_aging"):
    # Load dataset
    df = pd.read_csv(data_path)

    stats = ["PTS_per_min", "REB_per_min", "OREB_per_min", "AST_per_min", "STL_per_min",
             "BLK_per_min", "TOV_per_min", "FG3M"]
    models = {}

    os.makedirs(save_dir, exist_ok=True)

    print(f"Training aging models for stats: {stats}")

    for stat in stats:
        X = df[[f"{stat}_last", "AGE_last"]]
        y = df[f"{stat}_next"]

        model = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
        model.fit(X, y)

        # Evaluation
        y_pred = model.predict(X)
        mse = mean_squared_error(y, y_pred)
        r2 = r2_score(y, y_pred)

        print(f"{stat} model trained: MSE = {mse:.4f}, R² = {r2:.4f}")

        # Save model
        model_path = os.path.join(save_dir, f"aging_model_{stat}.joblib")
        joblib.dump(model, model_path)
        print(f"Saved {stat} model to {model_path}")

        models[stat] = model

    print("All aging models trained and saved successfully.")
    return models

if __name__ == "__main__":
    train_player_aging_models()
