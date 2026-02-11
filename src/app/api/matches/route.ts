import { NextRequest, NextResponse } from "next/server";
import { prisma } from "../../../lib/prisma";
import { calculateElo } from "../../../lib/elo";

export async function POST(req: NextRequest) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (typeof body !== "object" || body === null) {
    return NextResponse.json({ error: "Invalid request body" }, { status: 400 });
  }

  const { type } = body as Record<string, unknown>;

  if (type === "SINGLES") {
    return handleSingles(body as Record<string, unknown>);
  }

  return NextResponse.json({ error: "Unsupported match type. Use 'SINGLES'." }, { status: 400 });
}

async function handleSingles(body: Record<string, unknown>) {
  const { winnerId, loserId } = body;

  if (typeof winnerId !== "number" || typeof loserId !== "number") {
    return NextResponse.json(
      { error: "winnerId and loserId must be numbers" },
      { status: 400 }
    );
  }

  if (winnerId === loserId) {
    return NextResponse.json(
      { error: "winnerId and loserId must be different players" },
      { status: 400 }
    );
  }

  // Fetch both players in one query
  const players = await prisma.player.findMany({
    where: { id: { in: [winnerId, loserId] } },
  });

  if (players.length !== 2) {
    const foundIds = players.map((p) => p.id);
    const missing = [winnerId, loserId].filter((id) => !foundIds.includes(id));
    return NextResponse.json(
      { error: `Player(s) not found: ${missing.join(", ")}` },
      { status: 400 }
    );
  }

  const winner = players.find((p) => p.id === winnerId)!;
  const loser = players.find((p) => p.id === loserId)!;

  const { newWinnerRating, newLoserRating } = calculateElo(winner.eloRating, loser.eloRating);

  // Atomic transaction: create match + MatchPlayer records + update player stats
  const match = await prisma.$transaction(async (tx) => {
    const createdMatch = await tx.match.create({
      data: {
        type: "SINGLES",
        matchPlayers: {
          create: [
            { playerId: winnerId, role: "winner" },
            { playerId: loserId, role: "loser" },
          ],
        },
      },
      include: { matchPlayers: true },
    });

    await tx.player.update({
      where: { id: winnerId },
      data: {
        eloRating: newWinnerRating,
        wins: { increment: 1 },
      },
    });

    await tx.player.update({
      where: { id: loserId },
      data: {
        eloRating: newLoserRating,
        losses: { increment: 1 },
      },
    });

    return createdMatch;
  });

  return NextResponse.json(
    {
      matchId: match.id,
      type: "SINGLES",
      winner: {
        id: winnerId,
        name: winner.name,
        oldRating: winner.eloRating,
        newRating: newWinnerRating,
        delta: newWinnerRating - winner.eloRating,
      },
      loser: {
        id: loserId,
        name: loser.name,
        oldRating: loser.eloRating,
        newRating: newLoserRating,
        delta: newLoserRating - loser.eloRating,
      },
    },
    { status: 201 }
  );
}
