import { PrismaClient } from "../src/generated/prisma/client";
import { PrismaBetterSqlite3 } from "@prisma/adapter-better-sqlite3";

const adapter = new PrismaBetterSqlite3({
  url: process.env.DATABASE_URL ?? "file:./dev.db",
});
const prisma = new PrismaClient({ adapter });

const players = [
  { name: "Alice", eloRating: 1320, wins: 18, losses: 5 },
  { name: "Bob", eloRating: 1185, wins: 10, losses: 9 },
  { name: "Carol", eloRating: 1142, wins: 7, losses: 8 },
  { name: "Dave", eloRating: 1076, wins: 4, losses: 11 },
  { name: "Eve", eloRating: 998, wins: 3, losses: 12 },
  { name: "Frank", eloRating: 1250, wins: 14, losses: 6 },
];

async function main() {
  for (const player of players) {
    await prisma.player.upsert({
      where: { name: player.name },
      update: {
        eloRating: player.eloRating,
        wins: player.wins,
        losses: player.losses,
      },
      create: player,
    });
  }
  console.log(`Seeded ${players.length} players.`);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
