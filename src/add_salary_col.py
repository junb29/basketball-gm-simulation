import pandas as pd

def merge_salaries(input_path, salaries_path, output_path):
    
    stats_df = pd.read_csv(input_path)
    salary_df = pd.read_csv(salaries_path)
    
    stats_df['PLAYER_NAME'] = stats_df['PLAYER_NAME'].str.lower().str.strip()
    salary_df['PLAYER_NAME'] = salary_df['PLAYER_NAME'].str.lower().str.strip()

    merged_df = stats_df.merge(salary_df, on="PLAYER_NAME", how="left")
    merged_df['SALARY'] = merged_df['SALARY'].fillna(0).astype(int)
    
    merged_df.to_csv(output_path, index=False)
    print(f"Merged salaries into player stats and saved to {output_path}")

if __name__ == "__main__":
    merge_salaries(
        input_path="data/player_stats_2024-25_cleaned.csv",
        salaries_path="data/player_salaries.csv",
        output_path="data/player_stats_2024-25_with_salaries.csv"
    )