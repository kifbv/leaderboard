"use client";

import { useState } from "react";

type Player = {
  id: number;
  name: string;
  eloRating: number;
};

type EloResult = {
  id: number;
  name: string;
  oldRating: number;
  newRating: number;
  delta: number;
};

type SinglesResult = {
  matchId: number;
  type: "SINGLES";
  winner: EloResult;
  loser: EloResult;
};

type DoublesResult = {
  matchId: number;
  type: "DOUBLES";
  winnerTeam: EloResult[];
  loserTeam: EloResult[];
};

type MatchResult = SinglesResult | DoublesResult;

type MatchType = "SINGLES" | "DOUBLES";

function PlayerSelect({
  id,
  label,
  value,
  onChange,
  players,
  disabledIds,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (val: string) => void;
  players: Player[];
  disabledIds: string[];
}) {
  return (
    <div className="flex flex-col gap-2">
      <label
        htmlFor={id}
        className="text-[10px] font-bold uppercase tracking-widest text-primary ml-1"
      >
        {label}
      </label>
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-slate-900 border border-slate-800 rounded-xl py-3 px-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all cursor-pointer appearance-none"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2364748b'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E")`,
          backgroundPosition: "right 0.75rem center",
          backgroundRepeat: "no-repeat",
          backgroundSize: "1.25em 1.25em",
        }}
      >
        <option value="">Select player…</option>
        {players.map((p) => (
          <option
            key={p.id}
            value={p.id}
            disabled={disabledIds.includes(String(p.id))}
          >
            {p.name} ({p.eloRating})
          </option>
        ))}
      </select>
    </div>
  );
}

export default function LogMatchForm({ players }: { players: Player[] }) {
  const [matchType, setMatchType] = useState<MatchType>("SINGLES");

  // Singles state
  const [player1Id, setPlayer1Id] = useState<string>("");
  const [player2Id, setPlayer2Id] = useState<string>("");

  // Doubles state
  const [team1p1Id, setTeam1p1Id] = useState<string>("");
  const [team1p2Id, setTeam1p2Id] = useState<string>("");
  const [team2p1Id, setTeam2p1Id] = useState<string>("");
  const [team2p2Id, setTeam2p2Id] = useState<string>("");

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MatchResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const singlesReady =
    player1Id !== "" && player2Id !== "" && player1Id !== player2Id;

  const doublesIds = [team1p1Id, team1p2Id, team2p1Id, team2p2Id];
  const doublesAllFilled = doublesIds.every((id) => id !== "");
  const doublesAllDistinct =
    new Set(doublesIds.filter(Boolean)).size === doublesIds.length;
  const doublesReady = doublesAllFilled && doublesAllDistinct;

  function resetForm() {
    setPlayer1Id("");
    setPlayer2Id("");
    setTeam1p1Id("");
    setTeam1p2Id("");
    setTeam2p1Id("");
    setTeam2p2Id("");
  }

  function handleTypeChange(type: MatchType) {
    setMatchType(type);
    setResult(null);
    setError(null);
    resetForm();
  }

  async function handleSinglesWinner(winnerId: number, loserId: number) {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch("/api/matches", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type: "SINGLES", winnerId, loserId }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error ?? "Something went wrong");
        return;
      }
      setResult(data as SinglesResult);
      resetForm();
    } catch {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function handleDoublesWinner(
    winnerTeam: number[],
    loserTeam: number[]
  ) {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch("/api/matches", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type: "DOUBLES", winnerTeam, loserTeam }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error ?? "Something went wrong");
        return;
      }
      setResult(data as DoublesResult);
      resetForm();
    } catch {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  const player1 = players.find((p) => p.id === Number(player1Id));
  const player2 = players.find((p) => p.id === Number(player2Id));

  const team1 = [
    players.find((p) => p.id === Number(team1p1Id)),
    players.find((p) => p.id === Number(team1p2Id)),
  ];
  const team2 = [
    players.find((p) => p.id === Number(team2p1Id)),
    players.find((p) => p.id === Number(team2p2Id)),
  ];

  return (
    <div className="min-h-screen bg-background-dark flex flex-col">
      {/* Modal-style sticky header */}
      <header className="sticky top-0 z-10 bg-background-dark/80 backdrop-blur-md px-4 py-4 flex items-center justify-between border-b border-slate-800">
        <a
          href="/"
          className="w-10 h-10 flex items-center justify-start text-slate-500 hover:text-primary transition-colors"
        >
          <span className="material-symbols-outlined text-2xl">close</span>
        </a>
        <h1 className="text-lg font-semibold tracking-tight">Log Match</h1>
        <div className="w-10" />
      </header>

      <main className="flex-1 px-6 py-8 flex flex-col gap-8">
        {/* Match type toggle */}
        <div className="flex gap-2 p-1 bg-slate-800/50 rounded-xl">
          <button
            onClick={() => handleTypeChange("SINGLES")}
            className={`flex-1 py-2 px-4 rounded-lg font-medium text-sm transition-colors ${
              matchType === "SINGLES"
                ? "bg-primary text-white"
                : "bg-transparent text-slate-400"
            }`}
          >
            Singles
          </button>
          <button
            onClick={() => handleTypeChange("DOUBLES")}
            className={`flex-1 py-2 px-4 rounded-lg font-medium text-sm transition-colors ${
              matchType === "DOUBLES"
                ? "bg-primary text-white"
                : "bg-transparent text-slate-400"
            }`}
          >
            Doubles
          </button>
        </div>

        {/* Success result */}
        {result && result.type === "SINGLES" && (
          <div className="p-4 bg-green-900/30 border border-green-800 rounded-xl">
            <p className="font-semibold text-green-400 mb-2">Match recorded!</p>
            <div className="text-sm text-green-400 space-y-1">
              <p>
                🏆 {result.winner.name}: {result.winner.oldRating} →{" "}
                {result.winner.newRating}{" "}
                <span className="font-medium">(+{result.winner.delta})</span>
              </p>
              <p>
                {result.loser.name}: {result.loser.oldRating} →{" "}
                {result.loser.newRating}{" "}
                <span className="font-medium">({result.loser.delta})</span>
              </p>
            </div>
          </div>
        )}

        {result && result.type === "DOUBLES" && (
          <div className="p-4 bg-green-900/30 border border-green-800 rounded-xl">
            <p className="font-semibold text-green-400 mb-2">Match recorded!</p>
            <div className="text-sm text-green-400 space-y-2">
              <div>
                <p className="font-medium mb-1">🏆 Winners</p>
                {result.winnerTeam.map((p) => (
                  <p key={p.id}>
                    {p.name}: {p.oldRating} → {p.newRating}{" "}
                    <span className="font-medium">(+{p.delta})</span>
                  </p>
                ))}
              </div>
              <div>
                <p className="font-medium mb-1">Losers</p>
                {result.loserTeam.map((p) => (
                  <p key={p.id}>
                    {p.name}: {p.oldRating} → {p.newRating}{" "}
                    <span className="font-medium">({p.delta})</span>
                  </p>
                ))}
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="p-4 bg-red-900/30 border border-red-800 rounded-xl">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {/* Who played? heading */}
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-1">Who played?</h2>
          <p className="text-slate-500 text-sm">
            Select the match participants.
          </p>
        </div>

        {/* Singles form */}
        {matchType === "SINGLES" && (
          <div className="flex flex-col gap-6">
            <div className="grid grid-cols-2 gap-4">
              <PlayerSelect
                id="player1"
                label="Player 1"
                value={player1Id}
                onChange={setPlayer1Id}
                players={players}
                disabledIds={[player2Id]}
              />
              <PlayerSelect
                id="player2"
                label="Player 2"
                value={player2Id}
                onChange={setPlayer2Id}
                players={players}
                disabledIds={[player1Id]}
              />
            </div>

            {singlesReady && player1 && player2 ? (
              <div className="flex flex-col gap-3">
                <p className="text-sm font-medium text-slate-400">Who won?</p>
                <div className="flex gap-3">
                  <button
                    onClick={() => handleSinglesWinner(player1.id, player2.id)}
                    disabled={loading}
                    className="flex-1 py-4 bg-primary hover:bg-primary/90 text-white font-bold rounded-2xl shadow-lg shadow-primary/20 disabled:bg-slate-800 disabled:text-slate-500 disabled:cursor-not-allowed transition-colors"
                  >
                    {player1.name}
                  </button>
                  <button
                    onClick={() => handleSinglesWinner(player2.id, player1.id)}
                    disabled={loading}
                    className="flex-1 py-4 bg-primary hover:bg-primary/90 text-white font-bold rounded-2xl shadow-lg shadow-primary/20 disabled:bg-slate-800 disabled:text-slate-500 disabled:cursor-not-allowed transition-colors"
                  >
                    {player2.name}
                  </button>
                </div>
              </div>
            ) : (
              <button
                disabled
                className="w-full py-4 bg-slate-800 text-slate-500 font-bold rounded-2xl cursor-not-allowed"
              >
                Select both players to continue
              </button>
            )}
          </div>
        )}

        {/* Doubles form */}
        {matchType === "DOUBLES" && (
          <div className="flex flex-col gap-6">
            <div>
              <p className="text-sm font-bold text-slate-400 mb-3 uppercase tracking-widest">
                Team 1
              </p>
              <div className="grid grid-cols-2 gap-4">
                <PlayerSelect
                  id="team1p1"
                  label="Player 1"
                  value={team1p1Id}
                  onChange={setTeam1p1Id}
                  players={players}
                  disabledIds={[team1p2Id, team2p1Id, team2p2Id]}
                />
                <PlayerSelect
                  id="team1p2"
                  label="Player 2"
                  value={team1p2Id}
                  onChange={setTeam1p2Id}
                  players={players}
                  disabledIds={[team1p1Id, team2p1Id, team2p2Id]}
                />
              </div>
            </div>

            <div>
              <p className="text-sm font-bold text-slate-400 mb-3 uppercase tracking-widest">
                Team 2
              </p>
              <div className="grid grid-cols-2 gap-4">
                <PlayerSelect
                  id="team2p1"
                  label="Player 1"
                  value={team2p1Id}
                  onChange={setTeam2p1Id}
                  players={players}
                  disabledIds={[team1p1Id, team1p2Id, team2p2Id]}
                />
                <PlayerSelect
                  id="team2p2"
                  label="Player 2"
                  value={team2p2Id}
                  onChange={setTeam2p2Id}
                  players={players}
                  disabledIds={[team1p1Id, team1p2Id, team2p1Id]}
                />
              </div>
            </div>

            {doublesReady && team1[0] && team1[1] && team2[0] && team2[1] ? (
              <div className="flex flex-col gap-3">
                <p className="text-sm font-medium text-slate-400">
                  Which team won?
                </p>
                <div className="flex gap-3">
                  <button
                    onClick={() =>
                      handleDoublesWinner(
                        [Number(team1p1Id), Number(team1p2Id)],
                        [Number(team2p1Id), Number(team2p2Id)]
                      )
                    }
                    disabled={loading}
                    className="flex-1 py-4 bg-primary hover:bg-primary/90 text-white font-bold rounded-2xl shadow-lg shadow-primary/20 disabled:bg-slate-800 disabled:text-slate-500 disabled:cursor-not-allowed transition-colors"
                  >
                    Team 1
                    <span className="block text-xs font-normal opacity-80">
                      {team1[0].name} & {team1[1].name}
                    </span>
                  </button>
                  <button
                    onClick={() =>
                      handleDoublesWinner(
                        [Number(team2p1Id), Number(team2p2Id)],
                        [Number(team1p1Id), Number(team1p2Id)]
                      )
                    }
                    disabled={loading}
                    className="flex-1 py-4 bg-primary hover:bg-primary/90 text-white font-bold rounded-2xl shadow-lg shadow-primary/20 disabled:bg-slate-800 disabled:text-slate-500 disabled:cursor-not-allowed transition-colors"
                  >
                    Team 2
                    <span className="block text-xs font-normal opacity-80">
                      {team2[0].name} & {team2[1].name}
                    </span>
                  </button>
                </div>
              </div>
            ) : (
              <button
                disabled
                className="w-full py-4 bg-slate-800 text-slate-500 font-bold rounded-2xl cursor-not-allowed"
              >
                Select all four players to continue
              </button>
            )}
          </div>
        )}

        {loading && (
          <p className="text-sm text-slate-400 text-center">
            Recording match…
          </p>
        )}
      </main>
    </div>
  );
}
