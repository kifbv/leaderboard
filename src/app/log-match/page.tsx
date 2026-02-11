import { prisma } from "../../lib/prisma";
import LogMatchForm from "./LogMatchForm";

export const dynamic = "force-dynamic";

export default async function LogMatchPage() {
  const players = await prisma.player.findMany({
    orderBy: { name: "asc" },
    select: { id: true, name: true, eloRating: true },
  });

  return <LogMatchForm players={players} />;
}
