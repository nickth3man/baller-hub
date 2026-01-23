export interface StandingsTeam {
  team_id: number;
  name: string;
  abbreviation: string;
  wins: number;
  losses: number;
  win_pct: number;
  games_back: number;
  conference_rank: number | null;
  points_per_game?: number | null;
  points_allowed_per_game?: number | null;
  net_rating?: number | null;
}

export interface StandingsResponse {
  season_year: number;
  view: string;
  eastern?: StandingsTeam[];
  western?: StandingsTeam[];
  league?: StandingsTeam[];
}

export type StandingsView = "conference" | "division" | "league";
