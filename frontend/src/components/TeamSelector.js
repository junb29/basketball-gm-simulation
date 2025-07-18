import React, { useState } from 'react';

const NBA_TEAMS = [
  'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets', 'Chicago Bulls', 
  'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets', 'Detroit Pistons', 'Golden State Warriors',
  'Houston Rockets', 'Indiana Pacers', 'Los Angeles Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies', 'Miami Heat', 'Milwaukee Bucks',
  'Minnesota Timberwolves', 'New Orleans Pelicans', 'New York Knicks',
  'Oklahoma City Thunder', 'Orlando Magic', 'Philadelphia 76ers', 'Pheonix Suns', 'Portland Trail Blazers', 'Sacramento Kings',
  'San Antonio Spurs', 'Tornoto Raptors', 'Utah Jazz', 'Washington Wizards'
];

export default function TeamSelector({ onConfirm }) {
  const [selectedTeam, setSelectedTeam] = useState('');

  const handleConfirm = () => {
    if (selectedTeam) {
      onConfirm(selectedTeam);
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center'
    }}>
      <h2>Select your team:</h2>
      <div style={{ marginTop: '10px' }}>
        <select
          value={selectedTeam}
          onChange={(e) => setSelectedTeam(e.target.value)}
        >
          <option value="">--Select--</option>
          {NBA_TEAMS.map((team) => (
            <option key={team} value={team}>{team}</option>
          ))}
        </select>
        <button onClick={handleConfirm} style={{ marginLeft: '8px' }}>Confirm</button>
      </div>
    </div>
  );
}


