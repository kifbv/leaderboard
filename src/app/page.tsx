import { prisma } from "../lib/prisma";

export const dynamic = "force-dynamic";

// Deterministic avatar background color from player name
const AVATAR_COLORS = [
  "bg-violet-600",
  "bg-blue-600",
  "bg-emerald-600",
  "bg-rose-600",
  "bg-amber-600",
  "bg-cyan-600",
  "bg-fuchsia-600",
  "bg-lime-600",
];

function avatarColor(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = (hash * 31 + name.charCodeAt(i)) & 0xffffffff;
  }
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length];
}

export default async function LeaderboardPage() {
  const players = await prisma.player.findMany({
    orderBy: { eloRating: "desc" },
  });

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

  const top3 = rankedRows.slice(0, 3);
  const rest = rankedRows.slice(3);
  const showPodium = top3.length >= 2;

  // Podium order: 2nd (left), 1st (center), 3rd (right)
  const podiumOrder =
    top3.length === 3
      ? [top3[1], top3[0], top3[2]]
      : top3.length === 2
        ? [top3[1], top3[0]]
        : [];

  return (
    <div className="relative flex min-h-screen flex-col overflow-x-hidden">
      {/* Sticky Header */}
      <header className="sticky top-0 z-30 bg-background-dark/80 backdrop-blur-lg px-6 pt-10 pb-4">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-primary text-4xl font-bold">
            sports_tennis
          </span>
          <h1 className="text-2xl font-bold tracking-tight">
            TGSB Leaderboard
          </h1>
        </div>
      </header>

      {/* Podium — top 3 */}
      {showPodium && (
        <section className="px-6 py-4">
          <div className="flex items-end justify-center gap-4 py-4">
            {podiumOrder.map((player) => {
              const isFirst = player.rank === 1;
              const isSecond = player.rank === 2;
              const isThird = player.rank === 3;
              const initial = player.name.charAt(0).toUpperCase();
              const colorClass = avatarColor(player.name);

              return (
                <div
                  key={player.id}
                  className={`flex flex-col items-center gap-3 flex-1${isFirst ? " -mt-4" : ""}`}
                >
                  <div className="relative">
                    <div
                      className={`rounded-full flex items-center justify-center font-bold text-white ${colorClass} ${
                        isFirst
                          ? "w-20 h-20 text-xl border-4 border-primary shadow-[0_0_20px_rgba(19,91,236,0.3)]"
                          : isSecond
                            ? "w-16 h-16 text-lg border-2 border-slate-700"
                            : "w-16 h-16 text-lg border-2 border-[#b87333]/50"
                      }`}
                    >
                      {initial}
                    </div>
                    <div
                      className={`absolute -bottom-2 left-1/2 -translate-x-1/2 text-white font-bold rounded-full ${
                        isFirst
                          ? "bg-primary text-xs px-3 py-1 shadow-lg"
                          : isSecond
                            ? "bg-slate-600 text-[10px] px-2 py-0.5"
                            : "bg-[#b87333]/80 text-[10px] px-2 py-0.5"
                      }`}
                    >
                      {isFirst ? "1st" : isSecond ? "2nd" : "3rd"}
                    </div>
                  </div>
                  <div className="text-center">
                    <p
                      className={`font-bold truncate ${isFirst ? "text-sm max-w-[100px]" : "text-xs max-w-[80px]"}`}
                    >
                      {player.name}
                    </p>
                    <p
                      className={`font-semibold text-primary ${isFirst ? "text-lg font-bold" : "text-sm"}`}
                    >
                      {player.eloRating}
                    </p>
                    <p className="text-[9px] text-slate-500 uppercase tracking-tighter">
                      {player.wins}W - {player.losses}L
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Card rows — 4th and below (or all players if podium hidden) */}
      <main className="flex-1 px-6 pb-40">
        {rankedRows.length === 0 ? (
          <p className="text-slate-500 text-center py-12">No players yet</p>
        ) : (
          <div className="space-y-3 mt-6">
            {(showPodium ? rest : rankedRows).map((player) => {
              const initial = player.name.charAt(0).toUpperCase();
              const colorClass = avatarColor(player.name);
              return (
                <div
                  key={player.id}
                  className="flex items-center gap-4 bg-card-dark p-4 rounded-2xl hover:bg-slate-800/40 transition-all"
                >
                  <span className="w-4 text-sm font-bold text-slate-400">
                    {player.rank}
                  </span>
                  <div
                    className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-white shrink-0 ${colorClass}`}
                  >
                    {initial}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-bold truncate">{player.name}</p>
                    <p className="text-[10px] text-slate-500 font-medium uppercase tracking-tight">
                      {player.wins}W - {player.losses}L · {player.winRate}% Win
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-primary tracking-tight">
                      {player.eloRating}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>

      {/* Floating Action Button */}
      <a
        href="/log-match"
        className="fixed bottom-8 right-6 px-8 py-4 bg-primary text-white rounded-full shadow-[0_8px_30px_rgb(19,91,236,0.4)] flex items-center justify-center hover:scale-105 active:scale-95 transition-transform z-40"
      >
        <span className="text-sm font-bold tracking-wide">Log Match</span>
      </a>
    </div>
  );
}
