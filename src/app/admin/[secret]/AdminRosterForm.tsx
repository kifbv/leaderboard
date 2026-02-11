"use client";

import { useState } from "react";

type Player = {
  id: number;
  name: string;
  eloRating: number;
};

export default function AdminRosterForm({
  secret,
  initialPlayers,
}: {
  secret: string;
  initialPlayers: Player[];
}) {
  const [players, setPlayers] = useState<Player[]>(initialPlayers);
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function handleAddPlayer(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const res = await fetch(`/api/admin/${secret}/players`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error ?? "Something went wrong");
        return;
      }
      setPlayers((prev) =>
        [...prev, data as Player].sort((a, b) => a.name.localeCompare(b.name))
      );
      setName("");
      setSuccess(`${(data as Player).name} added successfully`);
    } catch {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Roster Management</h1>

      {/* Add player form */}
      <form onSubmit={handleAddPlayer} className="mb-8">
        <label
          htmlFor="player-name"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Add Player
        </label>
        <div className="flex gap-2">
          <input
            id="player-name"
            type="text"
            value={name}
            onChange={(e) => {
              setName(e.target.value);
              setError(null);
              setSuccess(null);
            }}
            placeholder="Player name"
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-base focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={loading || name.trim().length === 0}
            className="px-4 py-2 bg-blue-600 text-white font-medium rounded-lg text-base disabled:opacity-50 hover:bg-blue-700 active:bg-blue-800 transition-colors"
          >
            {loading ? "Adding…" : "Add Player"}
          </button>
        </div>

        {error && (
          <p className="mt-2 text-sm text-red-600">{error}</p>
        )}
        {success && (
          <p className="mt-2 text-sm text-green-600">{success}</p>
        )}
      </form>

      {/* Player list */}
      <h2 className="text-lg font-semibold mb-3">
        Players ({players.length})
      </h2>
      {players.length === 0 ? (
        <p className="text-gray-500 text-sm">No players yet.</p>
      ) : (
        <ul className="divide-y divide-gray-200 border border-gray-200 rounded-lg overflow-hidden">
          {players.map((player) => (
            <li
              key={player.id}
              className="flex items-center justify-between px-4 py-3 bg-white"
            >
              <span className="font-medium text-gray-900">{player.name}</span>
              <span className="text-sm text-gray-500">
                ELO {player.eloRating}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
