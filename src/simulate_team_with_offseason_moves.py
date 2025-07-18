import torch
import pandas as pd
from .pytorch_model import MLPRegressor
from .predict_player_next_season_stats import predict_player_next_season

# Constants
SALARY_CAP = 187895000  # Luxury Tax Threshold
SECOND_APRON = 207824000
TOP_N_PLAYERS = 9

mlp_model = MLPRegressor(input_dim = 126)
mlp_model.load_state_dict(torch.load("models/win_predictor_mlp_simulation.pt", map_location = torch.device("cpu")))
mlp_model.eval()

class TeamRoster:
    def __init__(self, team_abbr, player_data, fa_list):
        self.team_abbr = team_abbr
        self.df = player_data.copy()
        self.fa_list = set(name.lower().strip() for name in fa_list)
        self.roster = self.build_initial_roster()

    def build_initial_roster(self):
        roster = self.df[self.df["TEAM_ABBREVIATION"] == self.team_abbr]
        roster = roster[~roster['PLAYER_NAME'].isin(self.fa_list)]
        return roster

    def get_salary(self):
        return self.roster['SALARY'].sum()

    def display_roster(self):
        print("\nCurrent Roster:")
        print(self.roster[['PLAYER_NAME', 'AGE', 'SALARY']])

    def add_player(self, player_row, salary=None):
        if salary:
            player_row['SALARY'] = salary
        self.roster = pd.concat([self.roster, pd.DataFrame([player_row])], ignore_index=True)

    def remove_player(self, player_name):
        self.roster = self.roster[self.roster['PLAYER_NAME'] != player_name]

def process_fa_signing(team_roster, player_name, offer_salary, df):
    
    messages = []
    
    player_name = player_name.lower().strip()
    current_salary = team_roster.get_salary()

    player_row = df[df['PLAYER_NAME'] == player_name].iloc[0]
    player_team = player_row['TEAM_ABBREVIATION']

    if player_team == team_roster.team_abbr:
        # Bird rights: re-sign freely
        team_roster.add_player(player_row, salary=offer_salary)
        msg1 = f"Signed {player_name} (re-sign) at ${offer_salary}M"
        #print(msg1)
        messages.append(msg1)
        
        if(player_row['SALARY'] > offer_salary * 2):
            msg2 = f"Wow! That's a lot of paycut for {player_name}"
            #print(msg2)
            messages.append(msg2)
        
    else:
        if current_salary < SALARY_CAP and current_salary + offer_salary <= SECOND_APRON:
            team_roster.add_player(player_row, salary=offer_salary)
            msg3 = f"Signed {player_name} as FA at ${offer_salary}M"
            #print(msg3)
            messages.append(msg3)
        
        else:
            msg4 = f"Cannot sign {player_name}: salary cap will be over second apron."
            #print(msg4)
            messages.append(msg4)
            
    return messages


def process_trade(team_roster, players_out, players_in, partner_abbr, df):
    
    messages = []
    
    players_out = [p.lower().strip() for p in players_out]
    players_in = [p.lower().strip() for p in players_in]

    outgoing = team_roster.roster[team_roster.roster['PLAYER_NAME'].isin(players_out)]
    incoming = df[(df['TEAM_ABBREVIATION'] == partner_abbr) & (df['PLAYER_NAME'].isin(players_in))]

    out_salary = outgoing['SALARY'].sum()
    in_salary = incoming['SALARY'].sum()

    user_salary = team_roster.get_salary()
    user_max_incoming = out_salary * (2 if user_salary < SALARY_CAP else 1.25)
    if in_salary > user_max_incoming:
        msg1 = f"Invalid trade: incoming salary too high for {team_roster.team_abbr}."
        #print(msg1)
        messages.append(msg1)
        return messages

    # Check partner team
    partner_roster = df[df['TEAM_ABBREVIATION'] == partner_abbr]
    partner_salary = partner_roster['SALARY'].sum()
    partner_out = incoming['SALARY'].sum()
    partner_in = outgoing['SALARY'].sum()

    partner_max_incoming = partner_out * (2 if partner_salary < SALARY_CAP else 1.25)
    if partner_in > partner_max_incoming:
        msg2 = f"Invalid trade for {partner_abbr}: incoming salary too high."
        #print(msg2)
        messages.append(msg2)
        return messages

    # PPG realism warning
    out_ppg = outgoing.apply(lambda r: r['PTS']/r['GP'] if r['GP'] > 0 else 0, axis=1).sum()
    in_ppg = incoming.apply(lambda r: r['PTS']/r['GP'] if r['GP'] > 0 else 0, axis=1).sum()
    if abs(out_ppg - in_ppg) > 10:
        msg3 = f"\nLooks like this trade might be unrealistic in real life"
        #print(msg3)
        messages.append(msg3)

    # Apply trade
    for name in players_out:
        team_roster.remove_player(name)
    for _, row in incoming.iterrows():
        team_roster.add_player(row)
        
    msg4 = f"\nTrade completed with {partner_abbr}."  
    #print(msg4)
    messages.append(msg4)
    
    return messages


def simulate_next_season(team_roster):
    
    predicted_players = []

    for _, player in team_roster.roster.iterrows():
        stats = predict_player_next_season(player)
        stats['PLAYER_NAME'] = player['PLAYER_NAME']
        stats['PLAYER_ID'] = player['PLAYER_ID']
        stats['SALARY'] = player['SALARY']
        predicted_players.append(stats)

    pred_df = pd.DataFrame(predicted_players)

    # Select top 8 players by predicted MIN
    top_players = pred_df.sort_values('PTS', ascending=False).head(TOP_N_PLAYERS)
    
    # Normalize minutes to 240 total
    if (top_players['MIN'].sum() > 240):
        top_players['MIN'] = round(top_players['MIN'] / top_players['MIN'].sum() * 240, 1)

    # Build feature vectors for win prediction
    feature_vector = {}
    for i in range(TOP_N_PLAYERS):
        player = top_players.iloc[i]
        feature_vector.update({
            f'P{i+1}_PTS': player['PTS'],
            f'P{i+1}_REB': player['REB'],
            f'P{i+1}_OREB': player['OREB'],
            f'P{i+1}_AST': player['AST'],
            f'P{i+1}_STL': player['STL'],
            f'P{i+1}_BLK': player['BLK'],
            f'P{i+1}_TOV': player['TOV'],
            f'P{i+1}_FG_PCT': player['FG_PCT'],
            f'P{i+1}_FG3_PCT': player['FG3_PCT'],
            f'P{i+1}_FG3M': player['FG3M'],
            f'P{i+1}_FT_PCT': player['FT_PCT'],
            #f'P{i+1}_PLUS_MINUS': player['PLUS_MINUS'],
            f'P{i+1}_AGE': player['AGE'],
            f'P{i+1}_MIN': player['MIN'],
            f'P{i+1}_GP': player['GP'],
        })

    X = pd.DataFrame([feature_vector])
    feature_cols = [
        'P1_PTS', 'P1_REB', 'P1_OREB', 'P1_AST', 'P1_STL', 'P1_BLK', 'P1_TOV', 'P1_FG_PCT', 'P1_FG3_PCT', 'P1_FG3M', 'P1_FT_PCT', 'P1_AGE', 'P1_MIN', 'P1_GP',
        'P2_PTS', 'P2_REB', 'P2_OREB', 'P2_AST', 'P2_STL', 'P2_BLK', 'P2_TOV', 'P2_FG_PCT', 'P2_FG3_PCT', 'P2_FG3M', 'P2_FT_PCT', 'P2_AGE', 'P2_MIN', 'P2_GP',
        'P3_PTS', 'P3_REB', 'P3_OREB', 'P3_AST', 'P3_STL', 'P3_BLK', 'P3_TOV', 'P3_FG_PCT', 'P3_FG3_PCT', 'P3_FG3M', 'P3_FT_PCT', 'P3_AGE', 'P3_MIN', 'P3_GP',
        'P4_PTS', 'P4_REB', 'P4_OREB', 'P4_AST', 'P4_STL', 'P4_BLK', 'P4_TOV', 'P4_FG_PCT', 'P4_FG3_PCT', 'P4_FG3M', 'P4_FT_PCT', 'P4_AGE', 'P4_MIN', 'P4_GP',
        'P5_PTS', 'P5_REB', 'P5_OREB', 'P5_AST', 'P5_STL', 'P5_BLK', 'P5_TOV', 'P5_FG_PCT', 'P5_FG3_PCT', 'P5_FG3M', 'P5_FT_PCT', 'P5_AGE', 'P5_MIN', 'P5_GP',
        'P6_PTS', 'P6_REB', 'P6_OREB', 'P6_AST', 'P6_STL', 'P6_BLK', 'P6_TOV', 'P6_FG_PCT', 'P6_FG3_PCT', 'P6_FG3M', 'P6_FT_PCT', 'P6_AGE', 'P6_MIN', 'P6_GP',
        'P7_PTS', 'P7_REB', 'P7_OREB', 'P7_AST', 'P7_STL', 'P7_BLK', 'P7_TOV', 'P7_FG_PCT', 'P7_FG3_PCT', 'P7_FG3M', 'P7_FT_PCT', 'P7_AGE', 'P7_MIN', 'P7_GP',
        'P8_PTS', 'P8_REB', 'P8_OREB', 'P8_AST', 'P8_STL', 'P8_BLK', 'P8_TOV', 'P8_FG_PCT', 'P8_FG3_PCT', 'P8_FG3M', 'P8_FT_PCT', 'P8_AGE', 'P8_MIN', 'P8_GP',
        'P9_PTS', 'P9_REB', 'P9_OREB', 'P9_AST', 'P9_STL', 'P9_BLK', 'P9_TOV', 'P9_FG_PCT', 'P9_FG3_PCT', 'P9_FG3M', 'P9_FT_PCT', 'P9_AGE', 'P9_MIN', 'P9_GP'
    ]
    X = X[feature_cols]
    X_tensor = torch.tensor(X.values, dtype=torch.float32)

    with torch.no_grad():
        predicted_wins = mlp_model(X_tensor).item()

    '''
    print(f"\nPredicted Wins: {int(predicted_wins)}\tPredicted Losses: {82-int(predicted_wins)}")
    print("\nTop 9 Predicted Players:")
    with pd.option_context('display.max_columns', None):
        print(top_players[['PLAYER_NAME', 'PTS', 'REB', 'AST', 'MIN', 'GP', 'AGE', 'SALARY']])
    '''

    return predicted_wins, top_players

# Example Usage
if __name__ == "__main__":
    
    player_data = pd.read_csv("data/player_stats_2024-25_with_salaries.csv")
    fa_df = pd.read_csv("data/fa_player.csv")
    fa_list = fa_df['PLAYER_NAME'].tolist()

    team = TeamRoster("HOU", player_data, fa_list)
    team.display_roster()

    # Example sequence of moves
    process_fa_signing(team, "fred vanvleet", 20000000, player_data)
    process_fa_signing(team, "dorian finney-smith", 12000000, player_data)
    process_trade(team, ["Jalen Green", "Dillon Brooks"], ["Kevin Durant"], "PHX", player_data)
    team.display_roster()

    # Simulate next season
    simulate_next_season(team)