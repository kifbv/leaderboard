import { prisma } from "../lib/prisma";

export const dynamic = "force-dynamic";

export default async function LeaderboardPage() {
  const players = await prisma.player.findMany({
    orderBy: { eloRating: "desc" },
  });

  // Compute rank (ties share rank) and winRate using reduce to avoid mutation
  type Row = (typeof players)[0] & { rank: number; winRate: number };
  const rankedRows = players.reduce<Row[]>((acc, player, index) => {
    const prevRank = acc[index - 1]?.rank ?? 0;
    const prevElo = players[index - 1]?.eloRating;
    const rank =
      index === 0 || prevElo !== player.eloRating ? index + 1 : prevRank;
    const totalMatches = player.wins + player.losses;
    const winRate =
      totalMatches === 0 ? 0 : Math.round((player.wins / totalMatches) * 100);
    return [...acc, { ...player, rank, winRate }];
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Standings</h1>
      {rankedRows.length === 0 ? (
        <p className="text-gray-500 text-center py-12">No players yet</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="text-left text-gray-500 border-b border-gray-200">
                <th className="py-2 pr-3 font-medium w-8">#</th>
                <th className="py-2 pr-3 font-medium">Name</th>
                <th className="py-2 pr-3 font-medium text-right">ELO</th>
                <th className="py-2 pr-3 font-medium text-right">W</th>
                <th className="py-2 pr-3 font-medium text-right">L</th>
                <th className="py-2 font-medium text-right">Win%</th>
              </tr>
            </thead>
            <tbody>
              {rankedRows.map((player) => (
                <tr
                  key={player.id}
                  className="border-b border-gray-100 last:border-0"
                >
                  <td className="py-3 pr-3 text-gray-400 font-medium">
                    {player.rank}
                  </td>
                  <td className="py-3 pr-3 font-medium">{player.name}</td>
                  <td className="py-3 pr-3 text-right tabular-nums">
                    {player.eloRating}
                  </td>
                  <td className="py-3 pr-3 text-right tabular-nums text-green-600">
                    {player.wins}
                  </td>
                  <td className="py-3 pr-3 text-right tabular-nums text-red-500">
                    {player.losses}
                  </td>
                  <td className="py-3 text-right tabular-nums">
                    {player.winRate}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
