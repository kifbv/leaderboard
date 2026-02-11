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

type MatchResult = {
  matchId: number;
  type: "SINGLES";
  winner: EloResult;
  loser: EloResult;
};

export default function LogMatchForm({ players }: { players: Player[] }) {
  const [player1Id, setPlayer1Id] = useState<string>("");
  const [player2Id, setPlayer2Id] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MatchResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = player1Id !== "" && player2Id !== "" && player1Id !== player2Id;

  async function handleWinnerClick(winnerId: number, loserId: number) {
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

      setResult(data as MatchResult);
      setPlayer1Id("");
      setPlayer2Id("");
    } catch {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  const player1 = players.find((p) => p.id === Number(player1Id));
  const player2 = players.find((p) => p.id === Number(player2Id));

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Log Match</h1>

      {result && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="font-semibold text-green-800 mb-2">Match recorded!</p>
          <div className="text-sm text-green-700 space-y-1">
            <p>
              🏆 {result.winner.name}: {result.winner.oldRating} →{" "}
              {result.winner.newRating}{" "}
              <span className="font-medium">
                (+{result.winner.delta})
              </span>
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

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label
            htmlFor="player1"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Player 1
          </label>
          <select
            id="player1"
            value={player1Id}
            onChange={(e) => setPlayer1Id(e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-base bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select player…</option>
            {players.map((p) => (
              <option
                key={p.id}
                value={p.id}
                disabled={String(p.id) === player2Id}
              >
                {p.name} ({p.eloRating})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            htmlFor="player2"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Player 2
          </label>
          <select
            id="player2"
            value={player2Id}
            onChange={(e) => setPlayer2Id(e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-base bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select player…</option>
            {players.map((p) => (
              <option
                key={p.id}
                value={p.id}
                disabled={String(p.id) === player1Id}
              >
                {p.name} ({p.eloRating})
              </option>
            ))}
          </select>
        </div>

        {canSubmit && player1 && player2 ? (
          <div className="pt-2">
            <p className="text-sm font-medium text-gray-700 mb-3">
              Who won?
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => handleWinnerClick(player1.id, player2.id)}
                disabled={loading}
                className="flex-1 py-3 px-4 bg-blue-600 text-white font-semibold rounded-lg text-base disabled:opacity-50 hover:bg-blue-700 active:bg-blue-800 transition-colors"
              >
                {player1.name}
              </button>
              <button
                onClick={() => handleWinnerClick(player2.id, player1.id)}
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

      {loading && (
        <p className="mt-4 text-sm text-gray-500 text-center">
          Recording match…
        </p>
      )}
    </div>
  );
}
