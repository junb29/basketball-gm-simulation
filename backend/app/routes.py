from fastapi import APIRouter
from fastapi.responses import JSONResponse
import pandas as pd
import os

router = APIRouter()

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))

player_df = pd.read_csv(os.path.join(project_root,"data","player_stats_2024-25_with_salaries.csv"))
for stat in ["PTS", "REB", "AST", "MIN"]:
    player_df[stat] = round(player_df[stat] / player_df["GP"], 1)
player_df["SALARY"] = round(player_df["SALARY"] / 1000000, 1)
fa_df = pd.read_csv(os.path.join(project_root, "data", "fa_player.csv"))

@router.get("/fa_list")
async def get_fa_list():
    fa_players = fa_df['PLAYER_NAME'].tolist()
    return JSONResponse(content=fa_players)

@router.get("/teams")
async def get_teams():
    teams = player_df['TEAM_ABBREVIATION'].unique().tolist()
    return teams
'''
@router.get("/roster/{team}")
async def get_team_roster(team: str):
    team_roster = session_state.get(f'team_roster_{team}')
    if team_roster:
        return team_roster.roster.to_dict(orient='records')
    else:
        team_roster = TeamRoster(team, player_data, fa_list)
        return team_roster.roster.to_dict(orient='records')
'''

@router.get("/fa_player/{player_name}")
async def get_fa_player(player_name: str):
    player_row = player_df[player_df['PLAYER_NAME'] == player_name]
    if player_row.empty:
        return {}
    player_dict = player_row.iloc[0].to_dict()
    player_dict['SALARY'] = round(player_dict['SALARY'] / 1000000, 1)  # ensure salary units match frontend
    return player_dict
