export interface Season {
  season_id: number;
  year: number;
  season_name: string;
  is_active: boolean;
  champion?: string | null;
}

export interface SeasonDetail extends Season {
  start_date: string;
  end_date: string;
  all_star_date?: string | null;
  playoffs_start_date?: string | null;
  playoffs_end_date?: string | null;
  champion_team_name?: string | null;
  runner_up_team_name?: string | null;
}

export interface SeasonScheduleGame {
  game_id: number;
  date: string;
  time: string | null;
  home_team_abbrev: string;
  away_team_abbrev: string;
  home_score: number | null;
  away_score: number | null;
  season_type: string;
}

export interface SeasonSchedule {
  season_year: number;
  month?: number | null;
  games: SeasonScheduleGame[];
}

export interface SeasonLeaderEntry {
  rank: number;
  player_slug: string;
  player_name: string;
  team_abbrev: string;
  value: number;
  games_played: number;
}

export interface SeasonLeaders {
  season_year: number;
  category: string;
  per_game: boolean;
  leaders: SeasonLeaderEntry[];
}
