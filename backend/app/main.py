from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from .routes import router
from pydantic import BaseModel
from typing import List
import uuid
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

TEAM_NAME_TO_ABBR = {
    "Atlanta Hawks": "ATL",
    "Boston Celtics": "BOS",
    "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA",
    "Chicago Bulls": "CHI",
    "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL",
    "Denver Nuggets": "DEN",
    "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW",
    "Houston Rockets": "HOU",
    "Indiana Pacers": "IND",
    "Los Angeles Clippers": "LAC",
    "Los Angeles Lakers": "LAL",
    "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA",
    "Milwaukee Bucks": "MIL",
    "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP",
    "New York Knicks": "NYK",
    "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL",
    "Philadelphia 76ers": "PHI",
    "Pheonix Suns": "PHX",
    "Portland Trail Blazers": "POR",
    "Sacramento Kings": "SAC",
    "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR",
    "Utah Jazz": "UTA",
    "Washington Wizards": "WAS"
};

class TeamSelect(BaseModel):
    team: str

class FAMove(BaseModel):
    my_team : str
    player: str
    salary: float

class TradeMove(BaseModel):
    my_team: str
    trade_partner: str
    players_out: List[str]
    players_in: List[str]
    
class SimulateRequest(BaseModel):
    team: str

@app.post("/get_team_info")
def get_team_info(req: TeamSelect):
    
    session_id = str(uuid.uuid4())
    
    session_state[session_id] = {
        'team_roster': {},  
        'fa_list': fa_list.copy()
    }
    
    for abbr in TEAM_NAME_TO_ABBR.values():
        session_state[session_id]['team_roster'][abbr] = TeamRoster(abbr, player_data, fa_list)
    session_state[session_id]['fa_list'] = fa_list.copy()

    team_roster = session_state[session_id]['team_roster'][req.team]
    session_fa_list = session_state[session_id]['fa_list']
    
    roster = team_roster.roster.to_dict(orient="records")
    salary = team_roster.get_salary()

    return {
        "session_id": session_id,
        "team": req.team,
        "roster": roster,
        "salary": salary,
        "fa_list": session_fa_list
    }

@app.post("/sign_fa")
def sign_fa(move: FAMove, session_id: str):
    
    state = session_state.get(session_id)
    if state is None:
        return {"error": "Invalid session_id"}
    
    team_roster = state['team_roster'][move.my_team]
    session_fa_list = state['fa_list']
        
    messages = process_fa_signing(team_roster, move.player, move.salary, player_data)
    
    if move.player in session_fa_list:
        session_fa_list.remove(move.player)
    
    salary = team_roster.get_salary()
    roster = team_roster.roster.to_dict(orient="records")
    return {"status": "signed", "salary": salary, "roster": roster, "fa_list" : session_fa_list, "messages": messages}

@app.post("/trade")
def trade(move: TradeMove, session_id: str):
    
    state = session_state.get(session_id)
    if state is None:
        return {"error": "Invalid session_id"}

    my_team_abbr = move.my_team
    partner_abbr = move.trade_partner
    players_out = move.players_out
    players_in = move.players_in
    
    fa_list = state['fa_list']

    team_roster = state['team_roster'][my_team_abbr]
    if team_roster is None:
        team_roster = TeamRoster(my_team_abbr, player_data, fa_list)
        state['team_roster'][my_team_abbr] = team_roster
        
    partner_roster = state['team_roster'][partner_abbr]
    if partner_roster is None:
        partner_roster = TeamRoster(partner_abbr, player_data, fa_list)
        state['team_roster'][partner_abbr] = partner_roster    

    messages = process_trade(team_roster, players_out, players_in, partner_abbr, player_data)
    process_trade(partner_roster, players_in, players_out, my_team_abbr, player_data)
   
    # Save rosters after trade
    state['team_roster'][my_team_abbr] = team_roster
    state['team_roster'][partner_abbr] = partner_roster

    salary = team_roster.get_salary()
    roster = team_roster.roster.to_dict(orient="records")
    return {"status": "trade_completed", "salary": salary, "roster": roster, "messages": messages}


@app.get("/roster/{team}")
def get_team_roster(team: str, session_id: str):
    
    state = session_state.get(session_id)
    if state is None:
        return {"error": "Invalid session_id"}
    
    team_roster = state['team_roster'][team]
    fa_list = state['fa_list']
    
    if team_roster:
        team_roster.roster = team_roster.roster[~team_roster.roster['PLAYER_NAME'].isin(fa_df['PLAYER_NAME'])]
        return team_roster.roster.to_dict(orient='records')
    else:
        team_roster = TeamRoster(team, player_data, fa_list)
        return team_roster.roster.to_dict(orient='records')


@app.post("/simulate")
def simulate(request: SimulateRequest, session_id: str):
    
    state = session_state.get(session_id)
    if state is None:
        return {"error": "Invalid session_id"}
    
    team_roster = state['team_roster'][request.team]
    if not team_roster:
        team_roster = TeamRoster(request.team, player_data, fa_list)

    wins, players = simulate_next_season(team_roster)
    return {
        "wins": round(wins),
        "losses": 82 - round(wins),
        "top_players": players.to_dict(orient="records")
    }



# Deploy FastAPI + React

REACT_BUILD_DIR = os.path.join(os.path.dirname(__file__), "../../frontend/build")

app.mount("/static", StaticFiles(directory=os.path.join(REACT_BUILD_DIR, "static")), name="static")

@app.get("/")
def serve_react_app():
    index_path = os.path.join(REACT_BUILD_DIR, "index.html")
    return FileResponse(index_path)

@app.get("/{path_name:path}")
async def serve_spa(path_name: str):
    return FileResponse(os.path.join(REACT_BUILD_DIR, "index.html"))