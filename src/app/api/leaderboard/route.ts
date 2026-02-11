import { NextResponse } from "next/server";
import { prisma } from "../../../lib/prisma";

export async function GET() {
  const players = await prisma.player.findMany({
    orderBy: { eloRating: "desc" },
  });

  let rank = 1;
  const result = players.map((player, index) => {
    // Ties share the same rank; advance rank by 1 for each player regardless
    if (index > 0 && players[index - 1].eloRating !== player.eloRating) {
      rank = index + 1;
    }
    const totalMatches = player.wins + player.losses;
    const winRate = totalMatches === 0 ? 0 : Math.round((player.wins / totalMatches) * 100);
    return {
      id: player.id,
      name: player.name,
      eloRating: player.eloRating,
      wins: player.wins,
      losses: player.losses,
      winRate,
      rank,
    };
  });

  return NextResponse.json(result);
}
