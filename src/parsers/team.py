from src.data import Outcome
from src.utilities import str_to_int


class TeamTotalsParser:
    def __init__(self, team_abbreviation_parser):
        self.team_abbreviation_parser = team_abbreviation_parser

    def parse(self, first_team_totals, second_team_totals):
        return [
            self.parse_totals(
                team_totals=first_team_totals,
                opposing_team_totals=second_team_totals,
            ),
            self.parse_totals(
                team_totals=second_team_totals,
                opposing_team_totals=first_team_totals,
            ),
        ]

    def parse_totals(self, team_totals, opposing_team_totals):
        current_team = self.team_abbreviation_parser.from_abbreviation(
            team_totals.team_abbreviation
        )

        if str_to_int(team_totals.points) > str_to_int(opposing_team_totals.points):
            outcome = Outcome.WIN
        elif str_to_int(team_totals.points) < str_to_int(opposing_team_totals.points):
            outcome = Outcome.LOSS
        else:
            outcome = None

        return {
            "team": current_team,
            "outcome": outcome,
            "minutes_played": str_to_int(team_totals.minutes_played),
            "made_field_goals": str_to_int(team_totals.made_field_goals),
            "attempted_field_goals": str_to_int(team_totals.attempted_field_goals),
            "made_three_point_field_goals": str_to_int(
                team_totals.made_three_point_field_goals
            ),
            "attempted_three_point_field_goals": str_to_int(
                team_totals.attempted_three_point_field_goals
            ),
            "made_free_throws": str_to_int(team_totals.made_free_throws),
            "attempted_free_throws": str_to_int(team_totals.attempted_free_throws),
            "offensive_rebounds": str_to_int(team_totals.offensive_rebounds),
            "defensive_rebounds": str_to_int(team_totals.defensive_rebounds),
            "assists": str_to_int(team_totals.assists),
            "steals": str_to_int(team_totals.steals),
            "blocks": str_to_int(team_totals.blocks),
            "turnovers": str_to_int(team_totals.turnovers),
            "personal_fouls": str_to_int(team_totals.personal_fouls),
            "points": str_to_int(team_totals.points),
        }
