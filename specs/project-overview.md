# Ping Pong Leaderboard

## Problem Statement
Office workers playing ping pong have no way to record match results or track rankings, limiting the competitive and social potential of the game. This app makes it easy to log matches and see who's on top.

## Target Users
Anyone at the office with a mobile phone. Non-technical, casual users who just want to quickly log a game or check the standings. The app must be immediately obvious to use with no onboarding.

## Jobs to Be Done
1. **See the standings** - View the current ELO rankings for all players - Status: spec created
2. **Record a match** - Log the result of a singles or doubles game - Status: needs spec
3. **Manage the roster** - Add new players to the system - Status: needs spec

## v1 Scope

### In Scope
- Leaderboard showing: rank, player name, ELO rating, wins, losses, win rate %
- Log a singles match (1v1): pick two players, pick the winner
- Log a doubles match (2v2): pick two fixed teams of two, pick the winning team
- ELO ratings update automatically after each match (standard ELO, K=32, starting rating 1000)
- Secret admin URL to add new players (hard-to-guess path, no password required)
- Mobile-first responsive design

### Out of Scope (v1)
- User authentication or accounts
- Match scores (only winner/loser recorded)
- Personal stats page / match history per player
- Admin password or full auth for roster management
- Notifications, social features, or sharing
- Tournament brackets

### Non-Negotiables
- Works well on mobile (primary use case)
- ELO updates correctly after every match
- Trust-based: no login required to log a match (pick your name from a list)
- Admin URL must not be guessable (sufficiently random path segment)

## Technical Constraints
- **Platform:** Mobile-first web app (responsive, no native app)
- **Stack:** Next.js (React + API routes) + SQLite via Prisma
- **Hosting:** Railway (recommended - handles HTTPS, git-based deploys, persistent storage)
- **Auth:** None
- **External dependencies:** None

## Quality Gates
- Unit tests for ELO calculation logic
- Manual verification of match logging and leaderboard update on mobile

## Success Criteria
- A user can open the app on their phone, log a match result, and immediately see updated ELO rankings
- The app is stable enough for daily office use
