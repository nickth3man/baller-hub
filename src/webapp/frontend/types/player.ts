export interface Player {
  player_id: number;
  slug: string;
  first_name: string;
  last_name: string;
  full_name: string;
  position: string | null;
  is_active: boolean;
  birth_date: string | null;
  birth_place_city: string | null;
  birth_place_country: string | null;
  height_inches: number | null;
  weight_lbs: number | null;
  college: string | null;
  high_school: string | null;
  draft_year: number | null;
  draft_pick: number | null;
  debut_year: number | null;
  final_year: number | null;
  current_team?: string;
}

export interface PlayerSeasonStats {
  season_id: number;
  season_year: number;
  season_type: string;
  team_id: number | null;
  team_abbrev?: string | null;
  games_played: number;
  games_started: number;
  minutes_played: number;
  points: number;
  ppg: number;
  rebounds: number;
  assists: number;
  steals: number;
  blocks: number;
  turnovers: number;
  fg_made: number;
  fg_attempted: number;
  fg3_made: number;
  fg3_attempted: number;
  ft_made: number;
  ft_attempted: number;
}

export interface PlayerGameLogGame {
  game_id: number;
  game_date: string;
  opponent_abbrev: string;
  location: string;
  outcome: string;
  seconds_played: number;
  points: number;
  rebounds: number;
  assists: number;
  steals: number;
  blocks: number;
  turnovers: number;
  made_fg: number;
  attempted_fg: number;
  made_3pt: number;
  attempted_3pt: number;
  made_ft: number;
  attempted_ft: number;
  plus_minus: number | null;
}

export interface PlayerGameLogTotals {
  games_played: number;
  seconds_played: number;
  points: number;
  rebounds: number;
  assists: number;
  steals: number;
  blocks: number;
  turnovers: number;
  made_fg: number;
  attempted_fg: number;
  made_3pt: number;
  attempted_3pt: number;
  made_ft: number;
  attempted_ft: number;
}

export interface PlayerGameLog {
  player_slug: string;
  player_name: string;
  season_year: number;
  season_type: string;
  games: PlayerGameLogGame[];
  totals: PlayerGameLogTotals;
}

export interface RosterPlayer {
  player_id: number;
  slug: string;
  name: string;
  position: string | null;
  games_played: number;
  games_started: number;
  ppg: number;
}
