import { NextRequest, NextResponse } from "next/server";
import { prisma } from "../../../../../lib/prisma";
import { validateAdminSecret } from "../../../../../lib/adminSecret";

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ secret: string }> }
) {
  const { secret } = await params;
  const authError = validateAdminSecret(secret);
  if (authError) return authError;

  const players = await prisma.player.findMany({
    select: { id: true, name: true, eloRating: true, wins: true, losses: true },
    orderBy: { name: "asc" },
  });

  return NextResponse.json(players);
}

export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ secret: string }> }
) {
  const { secret } = await params;
  const authError = validateAdminSecret(secret);
  if (authError) return authError;

  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (typeof body !== "object" || body === null) {
    return NextResponse.json({ error: "Invalid request body" }, { status: 400 });
  }

  const { name } = body as Record<string, unknown>;

  if (typeof name !== "string" || name.trim().length === 0) {
    return NextResponse.json({ error: "name is required and must not be empty" }, { status: 400 });
  }

  const trimmedName = name.trim();

  // Case-insensitive duplicate check (SQLite doesn't support mode: "insensitive")
  const players = await prisma.player.findMany({ select: { name: true } });
  const existing = players.find(
    (p) => p.name.toLowerCase() === trimmedName.toLowerCase()
  );

  if (existing) {
    return NextResponse.json(
      { error: `A player named "${existing.name}" already exists` },
      { status: 409 }
    );
  }

  const player = await prisma.player.create({
    data: { name: trimmedName },
    select: { id: true, name: true, eloRating: true, wins: true, losses: true },
  });

  return NextResponse.json(player, { status: 201 });
}
