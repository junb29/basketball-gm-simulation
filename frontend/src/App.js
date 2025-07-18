import React, { useState } from 'react';
import TeamSelector from './components/TeamSelector';
import MovesUI from './components/MovesUI';
import SimulationResult from './components/SimulationResult';

export default function App() {
  const [team, setTeam] = useState('');
  const [showSimulation, setShowSimulation] = useState(false);

  const TEAM_NAME_TO_ABBR = {
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

  const handleConfirm = (teamName) => {
    const abbr = TEAM_NAME_TO_ABBR[teamName];
    setTeam(abbr);
  };

  const handleSimulate = () => {
    setShowSimulation(true);
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      minHeight: '100vh'
    }}>
      {/* Main content */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        paddingTop: '40px'
      }}>
        <h1 style={{ marginBottom: '40px' }}>Basketball GM Assistant 🏀</h1>

        {!team ? (
          <TeamSelector onConfirm={handleConfirm} />
        ) : showSimulation ? (
          <SimulationResult 
            team={team}
            onSimulateAgain={() => setShowSimulation(true)}
            onStartOver={() => {
              setShowSimulation(false);
              setTeam('');
            }} 
          />
        ) : (
          <MovesUI
            team={team}
            onSimulate={handleSimulate}
          />
        )}
      </div>

      {/* Footer */}
      <footer style={{
        textAlign: 'center',
        fontSize: '0.9rem',
        padding: '20px',
        color: '#555'
      }}>
        <div>Enjoy!</div>
        <div>
          LinkedIn: <a href="https://www.linkedin.com/in/junbae03" target="_blank" rel="noopener noreferrer">
            www.linkedin.com/in/junbae03
          </a>
        </div>
        <div>
          Github Repo: <a href="https://github.com/junb29/basketball-gm-simulation.git" target="_blank" rel="noopener noreferrer">
            https://github.com/junb29/basketball-gm-simulation.git
          </a>
        </div>
      </footer>
    </div>
  );
}
