import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os

def train_baseline_model(data_path="data/team_player_features.csv", save_path="models/win_predictor_baseline_simulation.pkl"):
    # Load dataset
    df = pd.read_csv(data_path)
    
    # Define features and target
    feature_cols = [col for col in df.columns if col not in ["TEAM_ABBREVIATION", "W", "SEASON", "PLUS_MINUS"]]
    # Exclude +/- stats to make model focus more on other stats
    # This leads to higher MAE and lower r2 score but makes the simulation more realistic and entertainable
    feature_cols = [col for col in feature_cols if col not in ["P1_PLUS_MINUS", "P2_PLUS_MINUS", "P3_PLUS_MINUS", "P4_PLUS_MINUS", "P5_PLUS_MINUS", "P6_PLUS_MINUS", "P7_PLUS_MINUS", "P8_PLUS_MINUS", "P9_PLUS_MINUS"]]
    X = df[feature_cols]
    y = df["W"]
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)
    
    # Model
    model = RandomForestRegressor(n_estimators = 100, random_state = 42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Baseline Model trained")
    print(f"MAE: {mae:.2f} wins")
    print(f"R² Score: {r2:.2f}")

    # Ensure models directory exists
    os.makedirs("models", exist_ok=True)

    # Save model
    joblib.dump(model, save_path)
    print(f"Model saved at {save_path}")
    
if __name__ == "__main__":
    train_baseline_model()

