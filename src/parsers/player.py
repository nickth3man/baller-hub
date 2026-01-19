from src.utilities import str_to_float, str_to_int


class PlayerAdvancedSeasonTotalsParser:
    def __init__(self, position_abbreviation_parser, team_abbreviation_parser):
        self.position_abbreviation_parser = position_abbreviation_parser
        self.team_abbreviation_parser = team_abbreviation_parser

    def parse(self, totals):
        return [
            {
                "slug": str(total.slug),
                "name": str(total.name).rstrip("*"),
                "positions": self.position_abbreviation_parser.from_abbreviations(
                    total.position_abbreviations
                ),
                "age": str_to_int(total.age, default=None),
                "team": self.team_abbreviation_parser.from_abbreviation(
                    total.team_abbreviation
                ),
                "games_played": str_to_int(total.games_played),
                "minutes_played": str_to_int(total.minutes_played),
                "player_efficiency_rating": str_to_float(
                    total.player_efficiency_rating
                ),
                "true_shooting_percentage": str_to_float(
                    total.true_shooting_percentage
                ),
                "three_point_attempt_rate": str_to_float(
                    total.three_point_attempt_rate
                ),
                "free_throw_attempt_rate": str_to_float(total.free_throw_attempt_rate),
                "offensive_rebound_percentage": str_to_float(
                    total.offensive_rebound_percentage
                ),
                "defensive_rebound_percentage": str_to_float(
                    total.defensive_rebound_percentage
                ),
                "total_rebound_percentage": str_to_float(
                    total.total_rebound_percentage
                ),
                "assist_percentage": str_to_float(total.assist_percentage),
                "steal_percentage": str_to_float(total.steal_percentage),
                "block_percentage": str_to_float(total.block_percentage),
                "turnover_percentage": str_to_float(total.turnover_percentage),
                "usage_percentage": str_to_float(total.usage_percentage),
                "offensive_win_shares": str_to_float(total.offensive_win_shares),
                "defensive_win_shares": str_to_float(total.defensive_win_shares),
                "win_shares": str_to_float(total.win_shares),
                "win_shares_per_48_minutes": str_to_float(
                    total.win_shares_per_48_minutes
                ),
                "offensive_box_plus_minus": str_to_float(total.offensive_plus_minus),
                "defensive_box_plus_minus": str_to_float(total.defensive_plus_minus),
                "box_plus_minus": str_to_float(total.plus_minus),
                "value_over_replacement_player": str_to_float(
                    total.value_over_replacement_player
                ),
                "is_combined_totals": total.is_combined_totals,
            }
            for total in totals
        ]


class PlayerSeasonTotalsParser:
    def __init__(self, position_abbreviation_parser, team_abbreviation_parser):
        self.position_abbreviation_parser = position_abbreviation_parser
        self.team_abbreviation_parser = team_abbreviation_parser

    def parse(self, totals):
        return [
            {
                "slug": str(total.slug),
                "name": str(total.name).rstrip("*"),
                "positions": self.position_abbreviation_parser.from_abbreviations(
                    total.position_abbreviations
                ),
                "age": str_to_int(total.age, default=None),
                "team": self.team_abbreviation_parser.from_abbreviation(
                    total.team_abbreviation
                ),
                "games_played": str_to_int(total.games_played),
                "games_started": str_to_int(total.games_started),
                "minutes_played": str_to_int(total.minutes_played),
                "made_field_goals": str_to_int(total.made_field_goals),
                "attempted_field_goals": str_to_int(total.attempted_field_goals),
                "made_three_point_field_goals": str_to_int(
                    total.made_three_point_field_goals
                ),
                "attempted_three_point_field_goals": str_to_int(
                    total.attempted_three_point_field_goals
                ),
                "made_free_throws": str_to_int(total.made_free_throws),
                "attempted_free_throws": str_to_int(total.attempted_free_throws),
                "offensive_rebounds": str_to_int(total.offensive_rebounds),
                "defensive_rebounds": str_to_int(total.defensive_rebounds),
                "assists": str_to_int(total.assists),
                "steals": str_to_int(total.steals),
                "blocks": str_to_int(total.blocks),
                "turnovers": str_to_int(total.turnovers),
                "personal_fouls": str_to_int(total.personal_fouls),
                "points": str_to_int(total.points),
            }
            for total in totals
        ]
