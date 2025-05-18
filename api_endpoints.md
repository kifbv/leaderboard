# Leaderboard API Endpoints

## Player Endpoints
- `GET /api/players` - List top players or players by site
  - Query params: `site_id` (optional), `limit` (optional, default 10)
  - Returns: Array of player objects with rankings
  - Auth: User authentication required

- `GET /api/players/{id}` - Get player profile
  - Path params: `id` (player ID)
  - Returns: Player profile with details, ELO, recent games
  - Auth: User authentication required

- `POST /api/players` - Create a new player
  - Body: Player details (username, email, site_id)
  - Returns: Created player object
  - Auth: User authentication required
  - Note: This is primarily used during signup process

## Game Endpoints
- `GET /api/games` - List recent games
  - Query params: `site_id` (optional), `player_id` (optional), `limit` (optional, default 20)
  - Returns: Array of game objects with details
  - Auth: User authentication required

- `POST /api/games` - Record a new game
  - Body: Game details (players, score, site_id, date)
  - Returns: Created game object with updated ELO scores
  - Auth: User authentication required

## Tournament Endpoints
- `GET /api/tournaments` - List recent tournaments
  - Query params: `site_id` (optional), `limit` (optional, default 5)
  - Returns: Array of tournament objects
  - Auth: User authentication required

- `POST /api/tournaments` - Create a new tournament
  - Body: Tournament details (name, site_id, players, format)
  - Returns: Created tournament object
  - Auth: Admin authorization required

## Site Endpoints
- `GET /api/sites` - List all sites
  - Returns: Array of site objects
  - Auth: User authentication required

- `POST /api/sites` - Create a new site
  - Body: Site details (name, location)
  - Returns: Created site object
  - Auth: Admin authorization required

## Admin Endpoints
- `GET /api/admin` - Admin dashboard data
  - Returns: Administrative statistics and controls
  - Auth: Admin authorization required

## Authentication
All endpoints require user authentication through AWS Cognito (Google OAuth)
Admin endpoints have additional authorization through the custom Admin Authorizer