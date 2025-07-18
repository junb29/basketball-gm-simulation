from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from .routes import router
from pydantic import BaseModel
from typing import List, Union
import pandas as pd
import os
from src.simulate_team_with_offseason_moves import (
    TeamRoster,
    process_fa_signing,
    process_trade,
    simulate_next_season
)

# uvicorn backend.app.main:app --reload --port 8001
app = FastAPI()

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],  # adjust port as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

session_state = {}

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
player_data = pd.read_csv(os.path.join(project_root, "data", "player_stats_2024-25_with_salaries.csv"))
player_data["SALARY"] = round(player_data["SALARY"] / 1000000, 1)
fa_df = pd.read_csv(os.path.join(project_root, "data", "fa_player.csv"))
fa_list = fa_df['PLAYER_NAME'].tolist()

class TeamSelect(BaseModel):
    team: str

class FAMove(BaseModel):
    my_team : str
    player: str
    salary: int

class TradeMove(BaseModel):
    my_team: str
    trade_partner: str
    players_out: List[str]
    players_in: List[str]
    
class SimulateRequest(BaseModel):
    team: str

@app.post("/get_team_info")
def get_team_info(req: TeamSelect):
    
    session_state.clear()
    
    team_roster = TeamRoster(req.team, player_data, fa_list)
    session_state['team_roster'] = team_roster

    roster = team_roster.roster.to_dict(orient="records")
    salary = team_roster.get_salary()

    return {
        "team": req.team,
        "roster": roster,
        "salary": salary,
        "fa_list": fa_list
    }

@app.post("/sign_fa")
def sign_fa(move: FAMove):
    team_roster = session_state.get(f'team_roster_{move.my_team}')
    if team_roster is None:
        team_roster = TeamRoster(move.my_team, player_data, fa_list)
        session_state[f'team_roster_{move.my_team}'] = team_roster
    messages = process_fa_signing(team_roster, move.player, move.salary, player_data)
    
    if move.player in fa_list:
        fa_list.remove(move.player)
    
    salary = team_roster.get_salary()
    roster = team_roster.roster.to_dict(orient="records")
    return {"status": "signed", "salary": salary, "roster": roster, "fa_list" : fa_list, "messages": messages}

@app.post("/trade")
def trade(move: TradeMove):
    print(f"Received trade request: {move}")
    my_team_abbr = move.my_team
    partner_abbr = move.trade_partner
    players_out = move.players_out
    players_in = move.players_in

    team_roster = session_state.get(f'team_roster_{my_team_abbr}')
    if team_roster is None:
        team_roster = TeamRoster(my_team_abbr, player_data, fa_list)
        session_state[f'team_roster_{my_team_abbr}'] = team_roster
        
    partner_roster = session_state.get(f'team_roster_{partner_abbr}')
    if partner_roster is None:
        partner_roster = TeamRoster(partner_abbr, player_data, fa_list)
        session_state[f'team_roster_{partner_abbr}'] = partner_roster    

    messages = process_trade(team_roster, players_out, players_in, partner_abbr, player_data)
    process_trade(partner_roster, players_in, players_out, my_team_abbr, player_data)
   
    session_state[f'team_roster_{my_team_abbr}'] = team_roster
    session_state[f'team_roster_{partner_abbr}'] = partner_roster

    salary = team_roster.get_salary()
    roster = team_roster.roster.to_dict(orient="records")
    return {"status": "trade_completed", "salary": salary, "roster": roster, "messages": messages}


@app.get("/roster/{team}")
def get_team_roster(team: str):
    team_roster = session_state.get(f'team_roster_{team}')
    if team_roster:
        team_roster.roster = team_roster.roster[~team_roster.roster['PLAYER_NAME'].isin(fa_df['PLAYER_NAME'])]
        return team_roster.roster.to_dict(orient='records')
    else:
        team_roster = TeamRoster(team, player_data, fa_list)
        return team_roster.roster.to_dict(orient='records')


@app.post("/simulate")
def simulate(request: SimulateRequest):
    team_abbr = request.team
    team_roster = session_state.get(f'team_roster_{team_abbr}')
    if not team_roster:
        team_roster = TeamRoster(team_abbr, player_data, fa_list)

    wins, players = simulate_next_season(team_roster)
    return {
        "wins": round(wins),
        "losses": 82 - round(wins),
        "top_players": players.to_dict(orient="records")
    }
