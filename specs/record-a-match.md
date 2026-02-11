# Record a Match

## Overview
Allow office workers to quickly log the result of a ping pong game — singles (1v1) or doubles (2v2) — directly from their phone. After submitting, ELO ratings update automatically for all involved players. This is the primary action in the app: the reason users open it after a game.

## User Stories

### US-001: Create ELO calculation utility
**Description:** As a developer, I want a pure function that computes new ELO ratings for two opponents so that match results produce correct ranking changes.

**Acceptance Criteria:**
- [ ] Function accepts two current ratings and a result (who won) and returns both new ratings
- [ ] Uses standard ELO formula with K-factor of 32 and starting rating of 1000
- [ ] Unit tests cover: equal ratings, large rating gap (underdog wins), large rating gap (favorite wins)
- [ ] Ratings are rounded to the nearest integer
- [ ] `npx tsc --noEmit` passes

### US-002: Create match recording API endpoint for singles
**Description:** As a frontend consumer, I want a POST endpoint that records a 1v1 match result and updates both players' ELO ratings in a single transaction.

**Acceptance Criteria:**
- [ ] `POST /api/matches` accepts `{ type: "SINGLES", winnerId: number, loserId: number }`
- [ ] Endpoint validates that both player IDs exist and are different from each other
- [ ] Creates a Match record and updates both players' `eloRating`, `wins`, and `losses` in a single database transaction
- [ ] Returns the created match with the ELO changes (old and new ratings for each player)
- [ ] Returns 400 with a descriptive message for invalid input
- [ ] `npx tsc --noEmit` passes

### US-003: Create match recording API endpoint for doubles
**Description:** As a frontend consumer, I want the POST endpoint to also handle 2v2 match results, updating ELO ratings for all four players.

**Acceptance Criteria:**
- [ ] `POST /api/matches` accepts `{ type: "DOUBLES", winnerTeam: [id, id], loserTeam: [id, id] }`
- [ ] Endpoint validates all four player IDs exist and are all distinct
- [ ] For ELO calculation, uses the average rating of each team as the team's effective rating
- [ ] Each player on the winning team gains ELO; each player on the losing team loses ELO (same delta based on team averages)
- [ ] Creates a Match record and updates all four players in a single database transaction
- [ ] Returns 400 with a descriptive message for invalid input (duplicate players, missing players)
- [ ] `npx tsc --noEmit` passes

### US-004: Build singles match logging UI
**Description:** As an office worker, I want to pick two players and tap the winner to log a 1v1 match from my phone.

**Acceptance Criteria:**
- [ ] A "Log Match" page or modal is accessible from the main navigation
- [ ] User selects match type (Singles selected by default)
- [ ] Two player dropdowns allow selecting Player 1 and Player 2 from all registered players
- [ ] A player cannot be selected for both slots simultaneously
- [ ] User taps one of two clearly labeled buttons to indicate the winner (e.g., "Player A won" / "Player B won")
- [ ] On success, a confirmation is shown with the ELO changes (e.g., "+18 / -18")
- [ ] Mobile-first layout: comfortably usable on a 375px-wide screen
- [ ] `npx tsc --noEmit` passes

### US-005: Build doubles match logging UI
**Description:** As an office worker, I want to pick four players across two teams and tap the winning team to log a 2v2 match.

**Acceptance Criteria:**
- [ ] When "Doubles" match type is selected, the form shows Team 1 (two player selects) and Team 2 (two player selects)
- [ ] No player can appear in more than one slot
- [ ] User taps one of two buttons to indicate the winning team
- [ ] On success, a confirmation is shown with each player's ELO change
- [ ] Mobile-first layout: comfortably usable on a 375px-wide screen
- [ ] `npx tsc --noEmit` passes

## Functional Requirements
- FR-1: Match type defaults to Singles; user can toggle to Doubles.
- FR-2: ELO is calculated using the standard formula: `expectedScore = 1 / (1 + 10^((opponentRating - playerRating) / 400))`, `newRating = oldRating + K * (actualScore - expectedScore)` where K = 32.
- FR-3: For doubles, each team's effective rating is the average of its two players' ratings. All four players receive the same absolute ELO delta (positive for winners, negative for losers).
- FR-4: Match recording and ELO updates happen atomically in a single database transaction — no partial updates on failure.
- FR-5: The match log form resets after a successful submission so another match can be logged immediately.
- FR-6: Player dropdowns are sorted alphabetically by name.
- FR-7: The submit action is disabled until all required players are selected.

## Non-Goals
- Match scores (only winner/loser is recorded)
- Undo or edit a submitted match
- Match history list or recent matches feed
- Confirmation dialog before submission (one-tap submit is intentional for speed)
- Offline support or optimistic UI updates

## Technical Considerations
- The `Match` model schema is defined in the "See the standings" spec — this feature populates it.
- Doubles matches require relating 4 players to a single match. The schema should use a `MatchPlayer` join table or equivalent to support both singles and doubles cleanly.
- ELO calculation should be a standalone pure utility (`lib/elo.ts`) for easy unit testing.
- All database mutations must use Prisma transactions to ensure atomicity.
- Player list for the dropdowns can reuse the `/api/leaderboard` endpoint or a simpler `/api/players` endpoint.

## Quality Gates
- `npx tsc --noEmit` passes
- Unit tests pass for ELO calculation (at least 3 scenarios)
- `POST /api/matches` returns correct ELO deltas for a known input
- Singles and doubles forms are usable on a 375px-wide viewport (manual check)
