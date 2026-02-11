# Manage the Roster

## Overview
Allow an admin to add new players to the system via a secret URL, so that the leaderboard and match logging always have an up-to-date roster. The admin page is accessible through a hard-to-guess URL path — no password required, but not discoverable by casual users.

## User Stories

### US-001: Generate and store a secret admin path
**Description:** As a developer, I want the app to use a secret URL segment for the admin page so that only people who know the link can access roster management.

**Acceptance Criteria:**
- [ ] An environment variable `ADMIN_SECRET` holds the secret path segment (e.g., `abc123xyz`)
- [ ] A `.env.example` file documents this variable with a placeholder value
- [ ] The secret segment is at least 16 characters when set in `.env`
- [ ] If `ADMIN_SECRET` is not set, the admin routes return 404
- [ ] `npx tsc --noEmit` passes

### US-002: Create add-player API endpoint
**Description:** As an admin page consumer, I want a POST endpoint that creates a new player with a default ELO rating so that players can be added to the roster.

**Acceptance Criteria:**
- [ ] `POST /api/admin/[secret]/players` accepts `{ name: string }`
- [ ] Returns 201 with the created player object (id, name, eloRating, wins, losses)
- [ ] Player is created with eloRating 1000, wins 0, losses 0
- [ ] Returns 400 if name is empty or only whitespace
- [ ] Returns 409 if a player with that exact name already exists (case-insensitive check)
- [ ] Returns 404 if the secret segment does not match `ADMIN_SECRET`
- [ ] `npx tsc --noEmit` passes

### US-003: Create list-players admin API endpoint
**Description:** As an admin page consumer, I want a GET endpoint that returns all players so that the admin page can display the current roster.

**Acceptance Criteria:**
- [ ] `GET /api/admin/[secret]/players` returns JSON array of all players
- [ ] Players are sorted alphabetically by name
- [ ] Each player object includes: id, name, eloRating, wins, losses
- [ ] Returns 404 if the secret segment does not match `ADMIN_SECRET`
- [ ] `npx tsc --noEmit` passes

### US-004: Build admin roster management UI
**Description:** As an office admin, I want a page at the secret URL where I can see all players and add new ones so that I can manage who's on the leaderboard.

**Acceptance Criteria:**
- [ ] Page is accessible at `/admin/[secret]`
- [ ] Page displays a list of all current players (name and ELO rating)
- [ ] A text input and "Add Player" button allow adding a new player by name
- [ ] On success, the new player appears in the list without a full page reload
- [ ] On error (duplicate name, empty name), a clear error message is shown
- [ ] Visiting `/admin/wrong-secret` shows a 404 page
- [ ] Mobile-first layout: usable on a 375px-wide screen
- [ ] `npx tsc --noEmit` passes

## Functional Requirements
- FR-1: The admin page is only accessible via the secret URL path (`/admin/[ADMIN_SECRET]`).
- FR-2: Player names must be unique (case-insensitive). "Alice" and "alice" are considered the same name.
- FR-3: New players start with an ELO rating of 1000, 0 wins, and 0 losses.
- FR-4: The player list on the admin page is sorted alphabetically by name.
- FR-5: The admin API endpoints return 404 (not 403) for wrong secrets to avoid revealing that the path exists.

## Non-Goals
- Editing or deleting existing players
- Admin authentication beyond the secret URL
- Bulk import of players
- Player profile pictures or additional metadata
- Admin audit log

## Technical Considerations
- The `ADMIN_SECRET` environment variable must be configured in `.env` for local development and in the hosting environment for production.
- Use Next.js dynamic route segments (`[secret]`) for both the page and API routes.
- The admin API routes should validate the secret segment before processing any request.
- The `Player` model is already defined in the "See the standings" spec — this feature only creates player records.
- Consider trimming whitespace from player names before saving.

## Quality Gates
- `npx tsc --noEmit` passes
- `POST /api/admin/[secret]/players` creates a player and returns 201 for valid input
- `POST /api/admin/[secret]/players` returns 409 for a duplicate name
- Admin page returns 404 for an incorrect secret
- Admin page is usable on a 375px-wide viewport (manual check)
