import { Player } from "./player";

export interface Game {
  game_id: number;
  date: string;
  time: string | null;
  home_team_id: number;
  away_team_id: number;
  home_team_abbrev?: string | null;
  away_team_abbrev?: string | null;
  home_score: number | null;
  away_score: number | null;
  season_type: string;
  is_final: boolean;
  arena?: string;
  attendance?: number;
}

export interface PlayerBoxScore {
  player_id: number;
  slug: string;
  name: string;
  position: string | null;
  is_starter: boolean;
  minutes: number;
  points: number;
  rebounds: number;
  offensive_rebounds: number;
  defensive_rebounds: number;
  assists: number;
  steals: number;
  blocks: number;
  turnovers: number;
  personal_fouls: number;
  fg_made: number;
  fg_attempted: number;
  fg3_made: number;
  fg3_attempted: number;
  ft_made: number;
  ft_attempted: number;
  plus_minus: number | null;
  game_score: number | null;
}

export interface TeamBoxScore {
  points: number;
  fg_made: number;
  fg_attempted: number;
  fg_pct: number | null;
  fg3_made: number;
  fg3_attempted: number;
  fg3_pct: number | null;
  ft_made: number;
  ft_attempted: number;
  ft_pct: number | null;
  offensive_rebounds: number;
  defensive_rebounds: number;
  total_rebounds: number;
  assists: number;
  steals: number;
  blocks: number;
  turnovers: number;
  personal_fouls: number;
  quarter_scores: Record<string, number> | null;
}

export interface BoxScoreResponse {
  game: Game;
  home_team: {
    team_id: number;
    team_abbrev?: string | null;
    team_name?: string | null;
    score: number | null;
    box_score: TeamBoxScore | null;
    players: PlayerBoxScore[];
  };
  away_team: {
    team_id: number;
    team_abbrev?: string | null;
    team_name?: string | null;
    score: number | null;
    box_score: TeamBoxScore | null;
    players: PlayerBoxScore[];
  };
}
