import { notFound } from "next/navigation";
import { getAdminSecret } from "../../../lib/adminSecret";
import { prisma } from "../../../lib/prisma";
import AdminRosterForm from "./AdminRosterForm";

export const dynamic = "force-dynamic";

export default async function AdminPage({
  params,
}: {
  params: Promise<{ secret: string }>;
}) {
  const { secret } = await params;
  const adminSecret = getAdminSecret();
  if (!adminSecret || secret !== adminSecret) {
    notFound();
  }

  const players = await prisma.player.findMany({
    orderBy: { name: "asc" },
    select: { id: true, name: true, eloRating: true },
  });

  return <AdminRosterForm secret={secret} initialPlayers={players} />;
}
