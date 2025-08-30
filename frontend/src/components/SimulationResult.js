import React, { useEffect, useState } from 'react';
import axios from 'axios';
import '../App.css';

const BACKEND_URL = 'https://basketball-gm-simulation.onrender.com';

export default function SimulationResult({ team, sessionId, onSimulateAgain, onStartOver }) {
  const [result, setResult] = useState(null);


  useEffect(() => {
    const fetchSimulation = async () => {
      try {
        const res = await axios.post(`${BACKEND_URL}/simulate`, { team, session_id: sessionId });
        setResult(res.data);
      } catch (err) {
        console.error('Simulation failed:', err);
        alert('Simulation could not be completed.');
      }
    };

    if (sessionId) {
      fetchSimulation();
    }
  }, [team, sessionId]);


  if (!result) {
    return <div style={{color: 'white'}}>Loading simulation...</div>;
  }

  return (
  <div style={{textAlign: 'center',
               paddingTop: '40px',
               backgroundColor: '1e1e1e',
               backdropFilter: 'blur(8px)',
               padding: '20px',
               borderRadius: '12px',
               color: 'white',
               boxShadow: '0 4px 12px rgba(0,0,0,0.4)', }}>
    <h2>Simulation Results</h2>
    <p>Wins: {result.wins} / Losses: {result.losses}</p>

    <h3>Top 9 Players</h3>
    <table border="1" cellPadding="5" style={{ margin: '0 auto' }}>
      <thead>
        <tr>
          <th>Player</th>
          <th>PTS</th>
          <th>REB</th>
          <th>AST</th>
          <th>STL</th>
          <th>BLK</th>
          <th>TOV</th>
          <th>FG_PCT</th>
          <th>FG3M</th>
          <th>FG3_PCT</th>
          <th>FT_PCT</th>
          <th>GP</th>
          <th>MIN</th>
          <th>AGE</th>
        </tr>
      </thead>
      <tbody>
      {result && result.top_players && result.top_players.map((p, index) => (
        <tr key={index}>
          {/*
          <td style={{ display: 'flex', alignItems: 'center' }}>
            <img 
              src={`https://cdn.nba.com/headshots/nba/latest/1040x760/${p.PLAYER_ID}.png`} 
              alt={p.PLAYER_NAME} 
              style={{ width: '30px', height: '30px', borderRadius: '50%', marginRight: '8px' }}
            />
            {p.PLAYER_NAME}
          </td>
          */}
          <td>{p.PLAYER_NAME}</td>
          <td>{p.PTS}</td>
          <td>{p.REB}</td>
          <td>{p.AST}</td>
          <td>{p.STL}</td>
          <td>{p.BLK}</td>
          <td>{p.TOV}</td>
          <td>{p.FG_PCT}</td>
          <td>{p.FG3M}</td>
          <td>{p.FG3_PCT}</td>
          <td>{p.FT_PCT}</td>
          <td>{p.GP}</td>
          <td>{p.MIN}</td>
          <td>{p.AGE}</td>
        </tr>
      ))}
    </tbody>

    </table>

    <div style={{ marginTop: '20px' }}>
      <button onClick={async () => {
        try {
          const res = await axios.post(`${BACKEND_URL}/simulate`, { team, session_id: sessionId });
          setResult(res.data);
        } catch (err) {
          console.error("Simulation failed:", err);
          alert("Simulation could not be completed. Check console.");
        }
      }}>
        Simulate Again
      </button>
      <button onClick={onStartOver}>
        Start Over
      </button>
    </div>
  </div>
);

}
