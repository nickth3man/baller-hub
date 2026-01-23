export interface AwardRecipient {
  award_id: number;
  season_id: number;
  player_id: number | null;
  team_id: number | null;
  vote_rank: number | null;
  vote_count: number | null;
  vote_percentage: number | null;
  first_place_votes: number | null;
  recipient_type: "PLAYER" | "TEAM" | "COACH";
  notes: string | null;
  player_name?: string | null;
  team_abbrev?: string | null;
  award_name?: string | null;
  season_year?: number | null;
}

export interface Award {
  award_id: number;
  name: string;
  category: string;
  description: string | null;
  first_awarded_year: number | null;
  last_awarded_year: number | null;
  is_active: boolean;
  recipients?: AwardRecipient[];
}
