export interface SearchPlayer {
  player_id: number;
  slug: string;
  full_name: string;
  position: string | null;
  is_active: boolean;
}

export interface SearchTeam {
  team_id: number;
  name: string;
  city: string | null;
  abbreviation: string;
  is_active: boolean;
}

export interface SearchGame {
  game_id: number;
  game_date: string;
  matchup: string;
  score: string | null;
}

export interface SearchResults {
  query?: string;
  players: SearchPlayer[];
  teams: SearchTeam[];
  games: SearchGame[];
  total_results?: number;
}
