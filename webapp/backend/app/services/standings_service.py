"""Standings service - business logic for standings operations."""

from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.game import Game
from app.models.season import Conference, Division, Season
from app.models.team import Team, TeamSeason


class StandingsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_standings(self, season_year: int, view: str = "conference"):
        season_id = await self._get_season_id(season_year)
        if season_id is None:
            return {"season_year": season_year, "view": view}

        query = (
            select(TeamSeason, Team, Conference.conference_type)
            .join(Team, TeamSeason.team_id == Team.team_id)
            .join(Division, Team.division_id == Division.division_id)
            .join(Conference, Division.conference_id == Conference.conference_id)
            .where(TeamSeason.season_id == season_id)
            .where(TeamSeason.season_type == "REGULAR")
        )
        result = await self.session.execute(query)
        rows = result.all()

        standings = [self._row_to_team_dict(ts, team) for ts, team, _ in rows]
        conference_map = {}
        for (_ts, _team, conference_type), entry in zip(rows, standings, strict=True):
            key = (
                conference_type.value
                if hasattr(conference_type, "value")
                else conference_type
            )
            conference_map.setdefault(key, []).append(entry)

        if view == "league":
            league = self._apply_rank_and_games_back(standings)
            return {"season_year": season_year, "view": view, "league": league}

        eastern = self._apply_rank_and_games_back(
            conference_map.get("EASTERN", [])
        )
        western = self._apply_rank_and_games_back(
            conference_map.get("WESTERN", [])
        )
        return {
            "season_year": season_year,
            "view": view,
            "eastern": eastern,
            "western": western,
        }

    async def get_standings_as_of_date(
        self, season_year: int, as_of_date: str, view: str = "conference"
    ):
        season_id = await self._get_season_id(season_year)
        if season_id is None:
            return {"season_year": season_year, "view": view}

        cutoff = date.fromisoformat(as_of_date)
        game_query = (
            select(Game)
            .where(Game.season_id == season_id)
            .where(Game.season_type == "REGULAR")
            .where(Game.game_date <= cutoff)
            .where(Game.home_score.isnot(None))
            .where(Game.away_score.isnot(None))
        )
        result = await self.session.execute(game_query)
        games = result.scalars().all()

        records: dict[int, dict[str, int]] = {}
        for game in games:
            home_id = game.home_team_id
            away_id = game.away_team_id
            if home_id not in records:
                records[home_id] = {"wins": 0, "losses": 0}
            if away_id not in records:
                records[away_id] = {"wins": 0, "losses": 0}

            if game.home_score > game.away_score:
                records[home_id]["wins"] += 1
                records[away_id]["losses"] += 1
            else:
                records[away_id]["wins"] += 1
                records[home_id]["losses"] += 1

        team_query = (
            select(Team, Conference.conference_type)
            .join(TeamSeason, TeamSeason.team_id == Team.team_id)
            .join(Division, Team.division_id == Division.division_id)
            .join(Conference, Division.conference_id == Conference.conference_id)
            .where(TeamSeason.season_id == season_id)
            .where(TeamSeason.season_type == "REGULAR")
        )
        team_result = await self.session.execute(team_query)
        team_rows = team_result.all()

        standings = []
        conference_map: dict[str, list[dict]] = {}
        for team, conference_type in team_rows:
            key = (
                conference_type.value
                if hasattr(conference_type, "value")
                else conference_type
            )
            record = records.get(team.team_id, {"wins": 0, "losses": 0})
            entry = {
                "team_id": team.team_id,
                "name": team.name,
                "abbreviation": team.abbreviation,
                "wins": record["wins"],
                "losses": record["losses"],
                "win_pct": self._win_pct(record["wins"], record["losses"]),
                "games_back": 0.0,
                "conference_rank": None,
                "points_per_game": None,
                "points_allowed_per_game": None,
                "net_rating": None,
            }
            standings.append(entry)
            conference_map.setdefault(key, []).append(entry)

        if view == "league":
            league = self._apply_rank_and_games_back(standings)
            return {"season_year": season_year, "view": view, "league": league}

        eastern = self._apply_rank_and_games_back(
            conference_map.get("EASTERN", [])
        )
        western = self._apply_rank_and_games_back(
            conference_map.get("WESTERN", [])
        )
        return {
            "season_year": season_year,
            "view": view,
            "eastern": eastern,
            "western": western,
        }

    async def get_expanded_standings(self, season_year: int):
        return await self.get_standings(season_year, view="league")

    async def get_playoff_bracket(self, season_year: int):
        return {
            "season_year": season_year,
            "eastern_conference": [],
            "western_conference": [],
            "finals": None,
            "champion_abbrev": None,
        }

    async def _get_season_id(self, season_year: int) -> int | None:
        query = select(Season.season_id).where(Season.year == season_year)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    def _row_to_team_dict(self, ts: TeamSeason, team: Team) -> dict:
        return {
            "team_id": team.team_id,
            "name": team.name,
            "abbreviation": team.abbreviation,
            "wins": ts.wins,
            "losses": ts.losses,
            "win_pct": self._win_pct(ts.wins, ts.losses),
            "games_back": 0.0,
            "conference_rank": None,
            "points_per_game": float(ts.points_per_game)
            if ts.points_per_game
            else None,
            "points_allowed_per_game": float(ts.points_allowed_per_game)
            if ts.points_allowed_per_game
            else None,
            "net_rating": float(ts.net_rating) if ts.net_rating else None,
        }

    def _win_pct(self, wins: int, losses: int) -> float:
        total = wins + losses
        return round(wins / total, 3) if total else 0.0

    def _apply_rank_and_games_back(self, teams: list[dict]) -> list[dict]:
        if not teams:
            return []
        sorted_teams = sorted(
            teams, key=lambda t: (-t["wins"], t["losses"], t["name"])
        )
        leader = sorted_teams[0]
        leader_wins = leader["wins"]
        leader_losses = leader["losses"]

        for idx, team in enumerate(sorted_teams, start=1):
            games_back = (
                (leader_wins - team["wins"]) + (team["losses"] - leader_losses)
            ) / 2
            team["games_back"] = round(games_back, 1)
            team["conference_rank"] = idx

        return sorted_teams
