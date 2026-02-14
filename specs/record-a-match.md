# Record a Match

## Overview
Allow office workers to quickly log the result of a ping pong game — singles (1v1) or doubles (2v2) — directly from their phone. After submitting, ELO ratings update automatically for all involved players. This is the primary action in the app: the reason users open it after a game.

## Design Reference
- **Stitch Project:** Global Leaderboard (`projects/5408221919024409015`)
- **Screens:**
  - Log Match Result (`62b44798252d41208c099b5aa18db1df`, Mobile, 390x884)
- **Local HTML:** `designs/log-match-result.html`

### Design Details
- **Theme:** Dark mode, Lexend font, primary color `#135bec`, background `#101622`
- **Layout:** Modal-style full screen with close button (X) in header, "Log Match" title centered
- **"Who played?" section:** 2-column grid with Player 1 and Player 2 dropdowns, labels in primary color uppercase
- **Score section:** "Set Scores" with number inputs side-by-side per set, "Add Set" dashed button
- **Footer:** Full-width "Submit Result" primary button with send icon, subtitle text below
- **Dropdowns:** White/dark bg with rounded-xl, custom chevron, border styling

### Design vs. Spec Deviations
The design shows set-based scoring which is out of v1 scope. Adapt as follows:
- Use the overall layout, typography, and color scheme from the design
- Replace the set scores section with a winner selection (two tappable buttons or similar)
- Keep the modal-style presentation with close button
- Keep the 2-column player dropdown layout
- Keep the "Submit Result" footer button style

Do NOT implement:
- Set score inputs (v1 only records winner/loser, not scores)
- "Add Set" button

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
- [ ] A "Log Match" page accessible from the leaderboard FAB button, styled as modal-like screen per `designs/log-match-result.html`
- [ ] Header with close button (X) and centered "Log Match" title
- [ ] User selects match type (Singles selected by default)
- [ ] "Who played?" section with 2-column grid of Player 1 and Player 2 dropdowns (styled per design)
- [ ] A player cannot be selected for both slots simultaneously
- [ ] Winner selection via two clearly labeled tappable buttons (replacing the set scores from the design)
- [ ] Full-width "Submit Result" primary button in footer (styled per design)
- [ ] On success, a confirmation is shown with the ELO changes (e.g., "+18 / -18")
- [ ] Dark mode styling with Lexend font and primary color `#135bec`
- [ ] Mobile-first layout: comfortably usable on a 375px-wide screen
- [ ] UI matches design reference in `designs/log-match-result.html` (adapted for winner-only recording)
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
- UI matches design reference in `designs/log-match-result.html`
- Verify in browser
