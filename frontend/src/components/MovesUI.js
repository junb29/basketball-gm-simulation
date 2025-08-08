import React, { useState, useEffect } from 'react';
import axios from 'axios';

const SALARY_CAP = 187.895;  // Salary cap in millions
const BACKEND_URL = 'https://basketball-gm-simulation.onrender.com';

export default function MovesUI({ team, onSimulate, setSessionId, sessionId }) {
    const [myRoster, setMyRoster] = useState([]);
    const [faList, setFaList] = useState([]);
    const [selectedFa, setSelectedFa] = useState('');
    const [offerSalary, setOfferSalary] = useState('');
    const [moves, setMoves] = useState([]);
    const [teams, setTeams] = useState([]);
    const [selectedTradeTeam, setSelectedTradeTeam] = useState('');
    const [tradeTeamRoster, setTradeTeamRoster] = useState([]);
    const [selectedMyPlayers, setSelectedMyPlayers] = useState([]);
    const [selectedTheirPlayers, setSelectedTheirPlayers] = useState([]);

    useEffect(() => {
        // Fetch FA list
        axios.get(`${BACKEND_URL}/fa_list`)
            .then(res => setFaList(res.data))
            .catch(error => console.error('Error fetching FA players:', error));
        // Fetch teams list
        axios.get(`${BACKEND_URL}/teams`)
            .then(res => setTeams(res.data))
            .catch(error => console.error('Error fetching teams:', error));
    }, []);

    useEffect(() => {
        if (team) { // reset session_id and get original roster
            axios.post(`${BACKEND_URL}/get_team_info`, { team })
                .then(res => {
                    setSessionId(res.data.session_id);
                    setMyRoster(res.data.roster);
                    setFaList(res.data.fa_list);
                    setMoves([]);
                })
                .catch(err => {
                    console.error('Error initializing session:', err);
                    alert('Could not initialize session for team.');
                });
        }
    }, [team, setSessionId]);

    const handleAddFa = async () => {
        if (selectedFa && offerSalary) {
            try {
            const res = await axios.post(`${BACKEND_URL}/sign_fa`, {
                my_team: team,
                player: selectedFa,
                salary: offerSalary,
                session_id: sessionId
            });

            // Show backend messages to user
            if (res.data.messages && res.data.messages.length > 0) {
                alert(res.data.messages.join("\n"));
            }

            // Update myRoster from backend
            setMyRoster(res.data.roster);

            // Track in moves for simulation
            setMoves([...moves, { type: 'fa', player: selectedFa, salary: offerSalary }]);

            // Sync faList if returned by backend:
            if (res.data.fa_list) {
                setFaList(res.data.fa_list);
            } else {
                setFaList(faList.filter(p => p !== selectedFa));
            }

            // Reset input UI:
            setSelectedFa('');
            setOfferSalary('');

            } catch (error) {
            console.error("FA signing failed:", error.response ? error.response.data : error.message);
            alert("Could not sign FA player due to backend error.");
            }
        }
    };

    const handleSelectTradeTeam = (team) => {
        setSelectedTradeTeam(team);
        axios.get(`${BACKEND_URL}/roster/${team}`, { params: { session_id: sessionId } })
            .then(response => setTradeTeamRoster(response.data))
            .catch(error => console.error('Error fetching team roster:', error));
    };

    const handleAddTrade = async () => {

        if (!selectedTradeTeam || selectedTheirPlayers.length === 0 || selectedMyPlayers.length === 0) {
            alert("Select trade partner and at least one player from both rosters.");
            return;
        }

        try {
            const response = await axios.post(`${BACKEND_URL}/trade`, {
                my_team: team,
                trade_partner: selectedTradeTeam,
                players_out: selectedMyPlayers,
                players_in: selectedTheirPlayers,
                session_id: sessionId
            });

            axios.get(`${BACKEND_URL}/roster/${selectedTradeTeam}?session_id=${sessionId}`)
                .then(res => setTradeTeamRoster(res.data))
                .catch(err => console.error('Error refreshing partner roster:', err));

            // Use response data to update state immediately:
            setMyRoster(response.data.roster);

            setMoves([...moves, {
                type: 'trade',
                tradePartner: selectedTradeTeam,
                playersOut: selectedMyPlayers,
                playersIn: selectedTheirPlayers
            }]);

            alert(response.data.messages.join("\n"));

            // Optionally reset selections
            setSelectedMyPlayers([]);
            setSelectedTheirPlayers([]);

        } catch (error) {
            console.error("Trade failed:", error.response ? error.response.data : error.message);
            alert("Trade could not be completed. Check console for details.");
        }
    };

    const handleResetAllMoves = async () => {
        try {
            // Clear moves state
            setMoves([]);

            // Reset backend state for user team by re-calling /get_team_info:
            const res = await axios.post(`${BACKEND_URL}/get_team_info`, { team });
            setSessionId(res.data.session_id);

            // Set roster to clean state
            setMyRoster(res.data.roster);

            // Refresh FA list as well (optional):
            const faRes = await axios.get(`${BACKEND_URL}/fa_list`);
            setFaList(faRes.data);

            // Reset selected trade state:
            setSelectedTradeTeam('');
            setTradeTeamRoster([]);
            setSelectedMyPlayers([]);
            setSelectedTheirPlayers([]);

            alert("All moves reset and roster restored!");

        } catch (err) {
            console.error("Failed to reset state:", err);
            alert("Could not reset state properly.");
        }
    };

    const currentSalary = myRoster.reduce((sum, player) => sum + player.SALARY, 0);
    const salaryCapRemaining = SALARY_CAP - currentSalary;

    return (
    <div style={{ display: 'flex', alignItems: 'flex-start' }}>
        {/* LEFT SIDE: all interaction UI */}
        <div style={{ width: '60%', paddingRight: '50px' }}>
        <h3>Propose Free Agent Signings:</h3>
        <select value={selectedFa} onChange={e => setSelectedFa(e.target.value)}>
            <option value="">--Select FA--</option>
            {faList.map(player => <option key={player} value={player}>{player}</option>)}
        </select>
        <input
            type="number"
            step="0.1"
            min="0"
            placeholder="Offer Salary (in M)"
            value={offerSalary}
            onChange={e => setOfferSalary(e.target.value)}
        />
        <button onClick={handleAddFa}>Add FA signing</button>

        <h2>Propose Trade:</h2>
        <select
            value={selectedTradeTeam}
            onChange={(e) => handleSelectTradeTeam(e.target.value)}
        >
            <option value="">--Select Trade Partner--</option>
            {teams.map(team => (
            <option key={team} value={team}>{team}</option>
            ))}
        </select>

        {selectedTradeTeam && tradeTeamRoster.length > 0 && (
            <div style={{ width: '70%', marginTop: '20px' }}>
            <h3>{selectedTradeTeam} Roster</h3>
            <table border="1" cellPadding="5">
                <thead>
                <tr>
                    <th></th>
                    <th>Player</th>
                    <th>Age</th>
                    <th>PTS</th>
                    <th>REB</th>
                    <th>AST</th>
                    <th>GP</th>
                    <th>MIN</th>
                    <th>SALARY</th>
                </tr>
                </thead>
                <tbody>
                {tradeTeamRoster.map(player => (
                <tr key={player.PLAYER_ID}>
                    <td>
                    <input
                        type="checkbox"
                        checked={selectedTheirPlayers.includes(player.PLAYER_NAME)}
                        onChange={(e) => {
                        if (e.target.checked) {
                            setSelectedTheirPlayers([...selectedTheirPlayers, player.PLAYER_NAME]);
                        } else {
                            setSelectedTheirPlayers(selectedTheirPlayers.filter(p => p !== player.PLAYER_NAME));
                        }
                        }}
                    />
                    </td>
                    {/*}
                    <td style={{ display: 'flex', alignItems: 'center' }}>
                    <img
                        src={`https://cdn.nba.com/headshots/nba/latest/1040x760/${player.PLAYER_ID}.png`}
                        alt={player.PLAYER_NAME}
                        style={{ width: '30px', height: '30px', borderRadius: '50%', objectFit: 'cover', marginRight: '6px' }}
                        onError={(e) => { e.target.src = '/default-headshot.png'; }}
                    />
                        {player.PLAYER_NAME}
                    </td>
                    */}
                    <td>{player.PLAYER_NAME}</td>
                    <td>{player.AGE}</td>
                    <td>{(player.PTS/player.GP).toFixed(1)}</td>
                    <td>{(player.REB/player.GP).toFixed(1)}</td>
                    <td>{(player.AST/player.GP).toFixed(1)}</td>
                    <td>{player.GP}</td>
                    <td>{player.MIN}</td>
                    <td>${player.SALARY.toFixed(1)}M</td>
                </tr>
                ))}
                </tbody>
            </table>
            </div>
        )}
        
        <button onClick={handleAddTrade}>Add Trade</button>

        <h3>Current Moves:</h3>
        <ul>
            {moves.map((move, idx) => (
            <li key={idx}>
                {move.type === 'fa' ? `FA: ${move.player} at $${move.salary}M` :
                `Trade: with ${move.tradePartner}, Out: ${move.playersOut}, In: ${move.playersIn}`}
            </li>
            ))}
            <button onClick={() => handleResetAllMoves()}>Remove</button>
        </ul>

        <button onClick={onSimulate}>Simulate Next Season</button>

        </div>

        {/* RIGHT SIDE: always show My Roster */}
        <div style={{
        width: '80%',
        border: '1px solid #ccc',
        padding: '10px',
        overflowX: 'auto',
        boxSizing: 'border-box',
        marginLeft: 'auto'
        }}>
        <h3>My Team Roster ({team})</h3>
        <p>Salary Cap Remaining: ${salaryCapRemaining.toFixed(1)}M</p>
        <table border="1" cellPadding="5">
            <thead>
            <tr>
                <th></th>
                <th>Player</th>
                <th>Age</th>
                <th>PTS</th>
                <th>REB</th>
                <th>AST</th>
                <th>SALARY</th>
            </tr>
            </thead>
            <tbody>
            {myRoster.map(player => (
                <tr key={player.PLAYER_ID}>
                    <td>
                    <input
                        type="checkbox"
                        checked={selectedMyPlayers.includes(player.PLAYER_NAME)}
                        onChange={(e) => {
                        if (e.target.checked) {
                            setSelectedMyPlayers([...selectedMyPlayers, player.PLAYER_NAME]);
                        } else {
                            setSelectedMyPlayers(selectedMyPlayers.filter(p => p !== player.PLAYER_NAME));
                        }
                        }}
                    />
                    </td>
                    {/*}
                    <td style={{ display: 'flex', alignItems: 'center' }}>
                    <img
                        src={`https://cdn.nba.com/headshots/nba/latest/1040x760/${player.PLAYER_ID}.png`}
                        alt={player.PLAYER_NAME}
                        style={{ width: '30px', height: '30px', borderRadius: '50%', objectFit: 'cover', marginRight: '6px' }}
                        onError={(e) => { e.target.src = '/default-headshot.png'; }}
                    />
                    {player.PLAYER_NAME}
                    </td>
                    */}
                    <td>{player.PLAYER_NAME}</td>
                    <td>{player.AGE}</td>
                    <td>{(player.PTS/player.GP).toFixed(1)}</td>
                    <td>{(player.REB/player.GP).toFixed(1)}</td>
                    <td>{(player.AST/player.GP).toFixed(1)}</td>
                    <td>${player.SALARY.toFixed(1)}M</td>
                </tr>
                ))}
            </tbody>
        </table>
        </div>
    </div>
    );

}
