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

  if (type === "DOUBLES") {
    return handleDoubles(body as Record<string, unknown>);
  }

  return NextResponse.json({ error: "Unsupported match type. Use 'SINGLES' or 'DOUBLES'." }, { status: 400 });
}

async function handleDoubles(body: Record<string, unknown>) {
  const { winnerTeam, loserTeam } = body;

  if (
    !Array.isArray(winnerTeam) ||
    winnerTeam.length !== 2 ||
    !Array.isArray(loserTeam) ||
    loserTeam.length !== 2
  ) {
    return NextResponse.json(
      { error: "winnerTeam and loserTeam must each be arrays of exactly 2 player IDs" },
      { status: 400 }
    );
  }

  const allIds = [...winnerTeam, ...loserTeam] as unknown[];
  if (allIds.some((id) => typeof id !== "number")) {
    return NextResponse.json(
      { error: "All player IDs must be numbers" },
      { status: 400 }
    );
  }

  const ids = allIds as number[];
  const uniqueIds = new Set(ids);
  if (uniqueIds.size !== 4) {
    return NextResponse.json(
      { error: "All four player IDs must be distinct" },
      { status: 400 }
    );
  }

  const players = await prisma.player.findMany({ where: { id: { in: ids } } });
  if (players.length !== 4) {
    const foundIds = players.map((p) => p.id);
    const missing = ids.filter((id) => !foundIds.includes(id));
    return NextResponse.json(
      { error: `Player(s) not found: ${missing.join(", ")}` },
      { status: 400 }
    );
  }

  const getPlayer = (id: number) => players.find((p) => p.id === id)!;

  const [w1id, w2id] = winnerTeam as number[];
  const [l1id, l2id] = loserTeam as number[];
  const w1 = getPlayer(w1id);
  const w2 = getPlayer(w2id);
  const l1 = getPlayer(l1id);
  const l2 = getPlayer(l2id);

  const winnerAvg = Math.round((w1.eloRating + w2.eloRating) / 2);
  const loserAvg = Math.round((l1.eloRating + l2.eloRating) / 2);
  const { newWinnerRating: newWinnerAvg } = calculateElo(winnerAvg, loserAvg);
  const delta = newWinnerAvg - winnerAvg;

  const match = await prisma.$transaction(async (tx) => {
    const createdMatch = await tx.match.create({
      data: {
        type: "DOUBLES",
        matchPlayers: {
          create: [
            { playerId: w1id, role: "winner" },
            { playerId: w2id, role: "winner" },
            { playerId: l1id, role: "loser" },
            { playerId: l2id, role: "loser" },
          ],
        },
      },
      include: { matchPlayers: true },
    });

    for (const id of [w1id, w2id]) {
      await tx.player.update({
        where: { id },
        data: { eloRating: { increment: delta }, wins: { increment: 1 } },
      });
    }

    for (const id of [l1id, l2id]) {
      await tx.player.update({
        where: { id },
        data: { eloRating: { increment: -delta }, losses: { increment: 1 } },
      });
    }

    return createdMatch;
  });

  return NextResponse.json(
    {
      matchId: match.id,
      type: "DOUBLES",
      winnerTeam: [w1, w2].map((p) => ({
        id: p.id,
        name: p.name,
        oldRating: p.eloRating,
        newRating: p.eloRating + delta,
        delta,
      })),
      loserTeam: [l1, l2].map((p) => ({
        id: p.id,
        name: p.name,
        oldRating: p.eloRating,
        newRating: p.eloRating - delta,
        delta: -delta,
      })),
    },
    { status: 201 }
  );
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
