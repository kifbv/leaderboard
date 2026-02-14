# See the Standings

## Overview
Display the current ELO rankings for all players so that anyone in the office can quickly check who's on top. This is the landing page of the app — the first thing users see when they open it on their phone.

## Design Reference
- **Stitch Project:** Global Leaderboard (`projects/5408221919024409015`)
- **Screens:**
  - Global Leaderboard (`742aab4a3acb405b8f593bed517eaf8a`, Mobile, 390x967)
- **Local HTML:** `designs/global-leaderboard.html`

### Design Details
- **Theme:** Dark mode, Lexend font, primary color `#135bec`, background `#0b121e`, card `#0d1625`
- **Layout:** Top-3 podium (1st centered/larger with glow, 2nd left, 3rd right) with avatar circles and rank badges, followed by a card list for 4th place onwards
- **Each card row:** rank number, avatar circle, player name, "XW - YL · Z% Win" subtitle, ELO rating right-aligned in primary color
- **Header:** Sticky with blur backdrop, app title "TGSB Leaderboard" with `sports_tennis` icon, search input below
- **FAB:** Floating "Log Match" button (primary color, bottom-right, rounded-full with shadow)
- **Bottom nav:** 4 tabs (Leaderboard, Matches, Leagues, Profile) — only Leaderboard is in v1 scope

### Design vs. Spec Deviations
The design includes elements beyond v1 scope. Implement these from the design:
- Top-3 podium layout with rank badges
- Card-style rows for 4th+ players
- Floating "Log Match" FAB button (links to match logging)
- Dark mode styling, Lexend font, primary color scheme
- Sticky header with app title and icon

Do NOT implement these (out of v1 scope):
- Search bar (design shows it, spec excludes filtering/searching)
- Avatar images (no user uploads in v1 — use initials or colored circles)
- Bottom navigation bar (Matches, Leagues, Profile tabs are out of scope)

## User Stories

### US-001: Set up project foundation with database schema
**Description:** As a developer, I want the Next.js project initialized with Prisma and SQLite so that all subsequent features have a working data layer.

**Acceptance Criteria:**
- [ ] Next.js app created with TypeScript enabled
- [ ] Prisma configured with SQLite provider
- [ ] `Player` model exists with fields: `id`, `name`, `eloRating` (default 1000), `wins` (default 0), `losses` (default 0), `createdAt`
- [ ] `Match` model exists with fields: `id`, `type` (SINGLES/DOUBLES), `createdAt`, and relations to players (winner/loser for singles; team members and winning team for doubles)
- [ ] `npx prisma migrate dev` runs without errors
- [ ] `npx tsc --noEmit` passes

### US-002: Create leaderboard API endpoint
**Description:** As a frontend consumer, I want a GET endpoint that returns all players sorted by ELO rating so that the leaderboard can be rendered.

**Acceptance Criteria:**
- [ ] `GET /api/leaderboard` returns JSON array of players
- [ ] Players are sorted by `eloRating` descending
- [ ] Each player object includes: `id`, `name`, `eloRating`, `wins`, `losses`, `winRate` (calculated percentage)
- [ ] Response includes a `rank` field (1-indexed position)
- [ ] Players with zero matches are included (winRate = 0)
- [ ] `npx tsc --noEmit` passes

### US-003: Build leaderboard UI
**Description:** As an office worker, I want to see a ranked list of players with their stats on my phone so that I can check the standings at a glance.

**Acceptance Criteria:**
- [ ] Landing page (`/`) displays a leaderboard matching the design in `designs/global-leaderboard.html`
- [ ] Top-3 players shown in a podium layout (1st centered/larger, 2nd left, 3rd right) with rank badges
- [ ] Players 4th and below shown in card-style rows: rank, initials avatar, name, W-L + win%, ELO
- [ ] List is sorted by ELO rating (highest first)
- [ ] Dark mode styling with Lexend font and primary color `#135bec`
- [ ] Sticky header with app title and sports icon
- [ ] Floating "Log Match" button (FAB) linking to match logging page
- [ ] Mobile-first layout: readable without horizontal scrolling on a 375px-wide screen
- [ ] Empty state shown when no players exist ("No players yet")
- [ ] UI matches design reference in `designs/global-leaderboard.html`
- [ ] `npx tsc --noEmit` passes

### US-004: Seed database with test players
**Description:** As a developer, I want a seed script that populates the database with sample players so that the leaderboard can be visually verified during development.

**Acceptance Criteria:**
- [ ] `npx prisma db seed` creates at least 5 players with varying ELO ratings, wins, and losses
- [ ] Seed script is idempotent (can be run multiple times without duplicating data)
- [ ] Seeded data produces a visually representative leaderboard
- [ ] `npx tsc --noEmit` passes

## Functional Requirements
- FR-1: The leaderboard page is the app's root route (`/`).
- FR-2: Players are ranked by ELO rating in descending order.
- FR-3: Win rate is displayed as a whole-number percentage (e.g., "67%"). Players with zero matches show "0%".
- FR-4: The leaderboard refreshes data on each page load (no caching needed for v1).
- FR-5: Rank numbers are sequential starting at 1. Ties in ELO share the same rank.

## Non-Goals
- Real-time live updates (WebSocket/SSE) — page refresh is sufficient
- Pagination — v1 expects fewer than 50 players
- Filtering, searching, or sorting by other columns
- Player profile pages or click-through from leaderboard rows
- Match history display

## Technical Considerations
- ELO rating is stored as an integer on the `Player` model (standard starting value: 1000)
- Win rate is computed at query time, not stored
- The `Match` model is defined here but populated by the "Record a match" feature
- Doubles match schema needs a junction/relation to support 4 players per match — design for this upfront even though doubles logging comes later
- Use Next.js App Router with server components for the leaderboard page

## Quality Gates
- `npx tsc --noEmit` passes
- `npx prisma migrate dev` runs cleanly
- `npx prisma db seed` populates test data
- Leaderboard renders correctly on a 375px-wide viewport (manual check)
- UI matches design reference in `designs/global-leaderboard.html`
- Verify in browser
