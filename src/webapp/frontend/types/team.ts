export interface Team {
  team_id: number;
  name: string;
  abbreviation: string;
  city: string;
  is_active: boolean;
  founded_year?: number;
  arena?: string;
  arena_capacity?: number;
  franchise?: {
    name: string;
    founded_year: number;
  };
}

export interface TeamScheduleGame {
  game_id: number;
  date: string;
  opponent_abbrev: string;
  location: string;
  result?: string | null;
  team_score?: number | null;
  opponent_score?: number | null;
}

export interface TeamSeasonStats {
  games_played: number;
  wins: number;
  losses: number;
  points_per_game?: number | null;
  points_allowed_per_game?: number | null;
  offensive_rating?: number | null;
  defensive_rating?: number | null;
  net_rating?: number | null;
  pace?: number | null;
  playoff_seed?: number | null;
  made_playoffs?: boolean | null;
}

export interface TeamHistorySeason {
  year: number;
  wins: number;
  losses: number;
  win_pct: number;
  made_playoffs: boolean;
  playoff_round: string | null;
}
