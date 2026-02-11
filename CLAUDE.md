# Leaderboard

## Build & Run

```bash
npm install
npx prisma migrate dev   # run migrations
npx prisma generate      # generate Prisma client (output: src/generated/prisma)
npm run dev              # start dev server on http://localhost:3000
```

## Validation

Run these after implementing to get feedback:

- Typecheck: `npx tsc --noEmit`
- Lint: `npm run lint`
- Build: `npm run build`

## Operational Notes

**Stack:** Next.js 16 (App Router) + Prisma 7 + SQLite (via better-sqlite3 driver adapter)

**Prisma 7 quirks:**
- Uses new `prisma-client` generator (not `prisma-client-js`) — output in `src/generated/prisma/`
- Requires driver adapter: `PrismaBetterSqlite3` from `@prisma/adapter-better-sqlite3`
- `PrismaClient` constructor signature: `new PrismaClient({ adapter })`
- Import path: `../generated/prisma/client` (no index.ts in generated dir)
- Schema has no `url` in datasource — URL provided via `prisma.config.ts` for CLI and via adapter at runtime
- DATABASE_URL format: `file:./dev.db` (relative to project root; db file is at root)

**Path aliases:** `@/*` maps to root `./*` (not `src/`). Use relative imports inside `src/`.

**Seed:** `npx prisma db seed` (configured in package.json `prisma.seed`)
