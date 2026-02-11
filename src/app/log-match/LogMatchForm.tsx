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
    <div>
      <label
        htmlFor={id}
        className="block text-sm font-medium text-gray-700 mb-1"
      >
        {label}
      </label>
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-base bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
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
    <div>
      <h1 className="text-2xl font-bold mb-6">Log Match</h1>

      {/* Match type toggle */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => handleTypeChange("SINGLES")}
          className={`flex-1 py-2 px-4 rounded-lg font-medium text-base border transition-colors ${
            matchType === "SINGLES"
              ? "bg-blue-600 text-white border-blue-600"
              : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
          }`}
        >
          Singles
        </button>
        <button
          onClick={() => handleTypeChange("DOUBLES")}
          className={`flex-1 py-2 px-4 rounded-lg font-medium text-base border transition-colors ${
            matchType === "DOUBLES"
              ? "bg-blue-600 text-white border-blue-600"
              : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
          }`}
        >
          Doubles
        </button>
      </div>

      {/* Success result */}
      {result && result.type === "SINGLES" && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="font-semibold text-green-800 mb-2">Match recorded!</p>
          <div className="text-sm text-green-700 space-y-1">
            <p>
              🏆 {result.winner.name}: {result.winner.oldRating} →{" "}
              {result.winner.newRating}{" "}
              <span className="font-medium">(+{result.winner.delta})</span>
            </p>
            <p>
              {result.loser.name}: {result.loser.oldRating} →{" "}
              {result.loser.newRating}{" "}
              <span className="font-medium text-red-600">
                ({result.loser.delta})
              </span>
            </p>
          </div>
        </div>
      )}

      {result && result.type === "DOUBLES" && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="font-semibold text-green-800 mb-2">Match recorded!</p>
          <div className="text-sm text-green-700 space-y-2">
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
                  <span className="font-medium text-red-600">({p.delta})</span>
                </p>
              ))}
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Singles form */}
      {matchType === "SINGLES" && (
        <div className="space-y-4">
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

          {singlesReady && player1 && player2 ? (
            <div className="pt-2">
              <p className="text-sm font-medium text-gray-700 mb-3">
                Who won?
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => handleSinglesWinner(player1.id, player2.id)}
                  disabled={loading}
                  className="flex-1 py-3 px-4 bg-blue-600 text-white font-semibold rounded-lg text-base disabled:opacity-50 hover:bg-blue-700 active:bg-blue-800 transition-colors"
                >
                  {player1.name}
                </button>
                <button
                  onClick={() => handleSinglesWinner(player2.id, player1.id)}
                  disabled={loading}
                  className="flex-1 py-3 px-4 bg-blue-600 text-white font-semibold rounded-lg text-base disabled:opacity-50 hover:bg-blue-700 active:bg-blue-800 transition-colors"
                >
                  {player2.name}
                </button>
              </div>
            </div>
          ) : (
            <div className="pt-2">
              <button
                disabled
                className="w-full py-3 px-4 bg-gray-300 text-gray-500 font-semibold rounded-lg text-base cursor-not-allowed"
              >
                Select both players to continue
              </button>
            </div>
          )}
        </div>
      )}

      {/* Doubles form */}
      {matchType === "DOUBLES" && (
        <div className="space-y-5">
          <div>
            <p className="text-sm font-semibold text-gray-800 mb-3">Team 1</p>
            <div className="space-y-3">
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
            <p className="text-sm font-semibold text-gray-800 mb-3">Team 2</p>
            <div className="space-y-3">
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

          {doublesReady &&
          team1[0] &&
          team1[1] &&
          team2[0] &&
          team2[1] ? (
            <div className="pt-2">
              <p className="text-sm font-medium text-gray-700 mb-3">
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
                  className="flex-1 py-3 px-4 bg-blue-600 text-white font-semibold rounded-lg text-base disabled:opacity-50 hover:bg-blue-700 active:bg-blue-800 transition-colors"
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
                  className="flex-1 py-3 px-4 bg-blue-600 text-white font-semibold rounded-lg text-base disabled:opacity-50 hover:bg-blue-700 active:bg-blue-800 transition-colors"
                >
                  Team 2
                  <span className="block text-xs font-normal opacity-80">
                    {team2[0].name} & {team2[1].name}
                  </span>
                </button>
              </div>
            </div>
          ) : (
            <div className="pt-2">
              <button
                disabled
                className="w-full py-3 px-4 bg-gray-300 text-gray-500 font-semibold rounded-lg text-base cursor-not-allowed"
              >
                Select all four players to continue
              </button>
            </div>
          )}
        </div>
      )}

      {loading && (
        <p className="mt-4 text-sm text-gray-500 text-center">
          Recording match…
        </p>
      )}
    </div>
  );
}
