export interface DraftPick {
  pick_id: number;
  draft_id: number;
  overall_pick: number;
  round_number: number;
  round_pick: number;
  team_id: number;
  player_id: number | null;
  original_team_id: number | null;
  trade_notes: string | null;
  college: string | null;
  height_in: number | null;
  weight_lbs: number | null;
  position: string | null;
  player_name?: string | null;
  team_abbrev?: string | null;
}

export interface Draft {
  draft_id: number;
  season_id: number;
  year: number;
  draft_date: string | null;
  round_count: number;
  pick_count: number;
  picks?: DraftPick[];
}
