// Player interface
export interface Player {
  player_id: string;
  username: string;
  email: string;
  site_id: string;
  elo_score: number;
  profile?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

// Game interface
export interface Game {
  game_id: string;
  site_id: string;
  player_ids: string[];
  scores: number[];
  date: string;
  created_at: string;
}

// Tournament interface
export interface Tournament {
  tournament_id: string;
  site_id: string;
  name: string;
  start_date: string;
  end_date: string;
  status: 'upcoming' | 'active' | 'completed';
  players: string[];
  created_at: string;
}

// Site interface
export interface Site {
  site_id: string;
  name: string;
  address?: string;
  created_at: string;
}

// User auth state interface
export interface AuthUser {
  username: string;
  email: string;
  isAdmin: boolean;
  attributes?: Record<string, any>;
}

// API response interface
export interface ApiResponse<T> {
  statusCode: number;
  body: T;
}