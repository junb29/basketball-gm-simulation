import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import os

# Dataset Class
class TeamDataset(Dataset):
    def __init__(self, dataframe, feature_cols, target_col):
        self.X = dataframe[feature_cols].values
        self.y = dataframe[target_col].values
    
    def __len__(self):
        return len(self.y)
    
    def __getitem__(self, idx):
        return torch.tensor(self.X[idx], dtype = torch.float32), torch.tensor(self.y[idx], dtype = torch.float32)
    
# MLP Model   
class MLPRegressor(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, 512)
        self.bn1 = nn.BatchNorm1d(512)
        self.fc2 = nn.Linear(512, 256)
        self.bn2 = nn.BatchNorm1d(256)
        self.fc3 = nn.Linear(256, 128)
        self.bn3 = nn.BatchNorm1d(128)
        self.out = nn.Linear(128, 1)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)

    def forward(self, x):
        x1 = self.relu(self.bn1(self.fc1(x)))
        x2 = self.relu(self.bn2(self.fc2(self.dropout(x1))))
        x3 = self.relu(self.bn3(self.fc3(self.dropout(x2))))
        return self.out(self.dropout(x3))

# Training function
def train_mlp(data_path="data/team_player_features.csv", save_path="models/win_predictor_mlp_simulation.pt", epochs=200, batch_size=8, lr=0.001):
    df = pd.read_csv(data_path)
    feature_cols = [col for col in df.columns if col not in ["TEAM_ABBREVIATION", "W", "SEASON"]]
    # Exclude +/- stats to make model focus more on other stats
    # This leads to higher MAE and lower r2 score but makes the simulation more realistic and entertainable
    feature_cols = [col for col in feature_cols if col not in ["P1_PLUS_MINUS", "P2_PLUS_MINUS", "P3_PLUS_MINUS", "P4_PLUS_MINUS", "P5_PLUS_MINUS", "P6_PLUS_MINUS", "P7_PLUS_MINUS", "P8_PLUS_MINUS", "P9_PLUS_MINUS"]]
    print(f"feature cols: {len(feature_cols)}")
    target_col = "W"

    X_train, X_test, y_train, y_test = train_test_split(df[feature_cols], df[target_col], test_size=0.2, random_state=42)

    train_df = pd.concat([X_train, y_train], axis=1)
    test_df = pd.concat([X_test, y_test], axis=1)

    train_dataset = TeamDataset(train_df, feature_cols, target_col)
    test_dataset = TeamDataset(test_df, feature_cols, target_col)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = MLPRegressor(input_dim=len(feature_cols)).to(device)

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay = 1e-4)

    for epoch in range(epochs):
        model.train()
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device).unsqueeze(1)
            optimizer.zero_grad()
            preds = model(X_batch)
            loss = criterion(preds, y_batch)
            loss.backward()
            optimizer.step()

        if (epoch+1) % 50 == 0:
            print(f"Epoch {epoch+1}/{epochs} - Loss: {loss.item():.4f}")

    # Evaluate
    model.eval()
    with torch.no_grad():
        X_test_tensor = torch.tensor(X_test.values, dtype=torch.float32).to(device)
        preds = model(X_test_tensor).cpu().numpy().flatten()
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)

    print(f"PyTorch MLP Model trained")
    print(f"MAE: {mae:.2f} wins")
    print(f"R² Score: {r2:.2f}")

    os.makedirs("models", exist_ok=True)
    torch.save(model.state_dict(), save_path)
    print(f"Model saved at {save_path}")

if __name__ == "__main__":
    train_mlp()