"""Season service - business logic for season operations."""

from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models.game import Game
from app.models.player import (
    Player,
    PlayerSeason,
    PlayerSeasonAdvanced,
    Position,
    SeasonType,
)
from app.models.season import League, Season
from app.models.team import Team


class SeasonService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_seasons(self, league: str = "NBA", limit: int = 20):
        champion = aliased(Team)
        query = (
            select(Season, champion.name, League.league_type)
            .join(League, Season.league_id == League.league_id)
            .outerjoin(champion, Season.champion_team_id == champion.team_id)
            .order_by(Season.year.desc())
            .limit(limit)
        )
        if league:
            query = query.where(League.league_type == league)

        result = await self.session.execute(query)
        rows = result.all()
        return [
            self._season_to_dict(season, champion_name)
            for season, champion_name, _ in rows
        ]

    async def get_current_season(self):
        champion = aliased(Team)
        runner_up = aliased(Team)
        query = (
            select(Season, champion.name, runner_up.name)
            .outerjoin(champion, Season.champion_team_id == champion.team_id)
            .outerjoin(runner_up, Season.runner_up_team_id == runner_up.team_id)
            .where(Season.is_active)
        )
        result = await self.session.execute(query)
        row = result.first()
        if row is None:
            return None
        season, champion_name, runner_up_name = row
        return self._season_detail_to_dict(season, champion_name, runner_up_name)

    async def get_season_by_year(self, year: int):
        champion = aliased(Team)
        runner_up = aliased(Team)
        query = (
            select(Season, champion.name, runner_up.name)
            .outerjoin(champion, Season.champion_team_id == champion.team_id)
            .outerjoin(runner_up, Season.runner_up_team_id == runner_up.team_id)
            .where(Season.year == year)
        )
        result = await self.session.execute(query)
        row = result.first()
        if row is None:
            return None
        season, champion_name, runner_up_name = row
        return self._season_detail_to_dict(season, champion_name, runner_up_name)

    async def get_season_schedule(self, season_year: int, month: int | None = None):
        season_id = await self._get_season_id(season_year)
        if season_id is None:
            return {"season_year": season_year, "month": month, "games": []}

        home_team = aliased(Team)
        away_team = aliased(Team)
        query = (
            select(Game, home_team.abbreviation, away_team.abbreviation)
            .join(home_team, Game.home_team_id == home_team.team_id)
            .join(away_team, Game.away_team_id == away_team.team_id)
            .where(Game.season_id == season_id)
            .order_by(Game.game_date, Game.game_time)
        )
        if month is not None:
            query = query.where(func.extract("month", Game.game_date) == month)

        result = await self.session.execute(query)
        games = []
        for game, home_abbrev, away_abbrev in result.all():
            games.append(
                {
                    "game_id": game.game_id,
                    "date": game.game_date.isoformat(),
                    "time": game.game_time.isoformat() if game.game_time else None,
                    "home_team_abbrev": home_abbrev,
                    "away_team_abbrev": away_abbrev,
                    "home_score": game.home_score,
                    "away_score": game.away_score,
                    "season_type": game.season_type,
                }
            )

        return {"season_year": season_year, "month": month, "games": games}

    async def get_season_leaders(
        self,
        season_year: int,
        category: str = "points",
        per_game: bool = True,
        limit: int = 10,
    ):
        season_id = await self._get_season_id(season_year)
        if season_id is None:
            return {
                "season_year": season_year,
                "category": category,
                "per_game": per_game,
                "leaders": [],
            }

        query = (
            select(PlayerSeason, Player, Team.abbreviation)
            .join(Player, PlayerSeason.player_id == Player.player_id)
            .outerjoin(Team, PlayerSeason.team_id == Team.team_id)
            .where(PlayerSeason.season_id == season_id)
            .where(PlayerSeason.season_type == SeasonType.REGULAR)
        )
        result = await self.session.execute(query)
        rows = result.all()

        selected = self._select_combined_rows(
            [(ps, player, team_abbrev) for ps, player, team_abbrev in rows]
        )

        stat_key = self._leader_stat_key(category)
        leaders = []
        for ps, player, team_abbrev in selected:
            stat_value = getattr(ps, stat_key)
            games_played = max(ps.games_played, 1)
            value = stat_value / games_played if per_game else stat_value
            leaders.append(
                {
                    "player_slug": player.slug,
                    "player_name": player.full_name,
                    "team_abbrev": "TOT" if ps.is_combined_totals else team_abbrev,
                    "value": float(value),
                    "games_played": ps.games_played,
                }
            )

        leaders.sort(key=lambda item: item["value"], reverse=True)
        leaders = leaders[:limit]
        for idx, leader in enumerate(leaders, start=1):
            leader["rank"] = idx

        return {
            "season_year": season_year,
            "category": category,
            "per_game": per_game,
            "leaders": leaders,
        }

    async def get_season_player_stats(
        self,
        season_year: int,
        stat_type: str = "totals",
        position: str | None = None,
        min_games: int = 0,
        page: int = 1,
        per_page: int = 50,
        sort_by: str = "points",
        sort_order: str = "desc",
    ):
        season_id = await self._get_season_id(season_year)
        if season_id is None:
            return {
                "items": [],
                "total": 0,
                "page": page,
                "per_page": per_page,
                "pages": 0,
            }

        if stat_type == "advanced":
            items = await self._season_advanced_stats(season_id, position, min_games)
        else:
            items = await self._season_basic_stats(season_id, position, min_games)
            if stat_type in {"per_game", "per_36", "per_100"}:
                items = [
                    self._apply_rate_transform(stat_type, item) for item in items
                ]

        if items and sort_by not in items[0]:
            sort_by = "per" if stat_type == "advanced" else "points"
        items = self._sort_items(items, sort_by, sort_order)

        total = len(items)
        start = (page - 1) * per_page
        end = start + per_page
        paged_items = items[start:end]

        return {
            "items": paged_items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        }

    async def _get_season_id(self, season_year: int) -> int | None:
        query = select(Season.season_id).where(Season.year == season_year)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    def _season_to_dict(self, season: Season, champion_name: str | None) -> dict:
        return {
            "season_id": season.season_id,
            "year": season.year,
            "season_name": self._format_season_name(season.year, season.season_name),
            "is_active": season.is_active,
            "champion": champion_name,
        }

    def _season_detail_to_dict(
        self,
        season: Season,
        champion_name: str | None,
        runner_up_name: str | None,
    ) -> dict:
        return {
            **self._season_to_dict(season, champion_name),
            "start_date": season.start_date,
            "end_date": season.end_date,
            "all_star_date": season.all_star_date,
            "playoffs_start_date": season.playoffs_start_date,
            "playoffs_end_date": season.playoffs_end_date,
            "champion_team_name": champion_name,
            "runner_up_team_name": runner_up_name,
        }

    def _format_season_name(self, year: int, season_name: str | None) -> str:
        if season_name:
            return season_name
        return f"{year - 1}-{str(year)[-2:]}"

    def _leader_stat_key(self, category: str) -> str:
        return {
            "points": "points_scored",
            "rebounds": "total_rebounds",
            "assists": "assists",
            "steals": "steals",
            "blocks": "blocks",
        }.get(category, "points_scored")

    def _select_combined_rows(
        self, rows: Iterable[tuple[PlayerSeason, Player, str | None]]
    ) -> list[tuple[PlayerSeason, Player, str | None]]:
        selected: dict[int, tuple[PlayerSeason, Player, str | None]] = {}
        for ps, player, team_abbrev in rows:
            existing = selected.get(player.player_id)
            if existing is None or (ps.is_combined_totals and not existing[0].is_combined_totals):
                selected[player.player_id] = (ps, player, team_abbrev)
        return list(selected.values())

    async def _season_basic_stats(
        self, season_id: int, position: str | None, min_games: int
    ) -> list[dict]:
        query = (
            select(PlayerSeason, Player, Team.abbreviation)
            .join(Player, PlayerSeason.player_id == Player.player_id)
            .outerjoin(Team, PlayerSeason.team_id == Team.team_id)
            .where(PlayerSeason.season_id == season_id)
            .where(PlayerSeason.season_type == SeasonType.REGULAR)
            .where(PlayerSeason.games_played >= min_games)
        )
        position_enum = self._parse_position(position)
        if position_enum is not None:
            query = query.where(PlayerSeason.position == position_enum)

        result = await self.session.execute(query)
        rows = result.all()
        selected = self._select_combined_rows(
            [(ps, player, team_abbrev) for ps, player, team_abbrev in rows]
        )

        items = []
        for ps, player, team_abbrev in selected:
            items.append(
                {
                    "player_id": player.player_id,
                    "player_slug": player.slug,
                    "player_name": player.full_name,
                    "team_abbrev": "TOT" if ps.is_combined_totals else team_abbrev,
                    "games_played": ps.games_played,
                    "minutes_played": ps.minutes_played,
                    "points": ps.points_scored,
                    "rebounds": ps.total_rebounds,
                    "assists": ps.assists,
                    "steals": ps.steals,
                    "blocks": ps.blocks,
                    "turnovers": ps.turnovers,
                    "fg_made": ps.made_fg,
                    "fg_attempted": ps.attempted_fg,
                    "fg3_made": ps.made_3pt,
                    "fg3_attempted": ps.attempted_3pt,
                    "ft_made": ps.made_ft,
                    "ft_attempted": ps.attempted_ft,
                }
            )
        return items

    async def _season_advanced_stats(
        self, season_id: int, position: str | None, min_games: int
    ) -> list[dict]:
        query = (
            select(PlayerSeasonAdvanced, Player, Team.abbreviation)
            .join(Player, PlayerSeasonAdvanced.player_id == Player.player_id)
            .outerjoin(Team, PlayerSeasonAdvanced.team_id == Team.team_id)
            .where(PlayerSeasonAdvanced.season_id == season_id)
            .where(PlayerSeasonAdvanced.season_type == SeasonType.REGULAR)
            .where(PlayerSeasonAdvanced.games_played >= min_games)
        )
        position_enum = self._parse_position(position)
        if position_enum is not None:
            query = query.where(Player.position == position_enum)

        result = await self.session.execute(query)
        rows = result.all()
        selected: dict[int, tuple[PlayerSeasonAdvanced, Player, str | None]] = {}
        for ps, player, team_abbrev in rows:
            existing = selected.get(player.player_id)
            if existing is None or (ps.is_combined_totals and not existing[0].is_combined_totals):
                selected[player.player_id] = (ps, player, team_abbrev)

        items = []
        for ps, player, team_abbrev in selected.values():
            items.append(
                {
                    "player_id": player.player_id,
                    "player_slug": player.slug,
                    "player_name": player.full_name,
                    "team_abbrev": "TOT" if ps.is_combined_totals else team_abbrev,
                    "games_played": ps.games_played,
                    "minutes_played": ps.minutes_played,
                    "per": self._to_float(ps.player_efficiency_rating),
                    "ts_pct": self._to_float(ps.true_shooting_percentage),
                    "efg_pct": self._to_float(ps.effective_fg_percentage),
                    "usage_pct": self._to_float(ps.usage_percentage),
                    "win_shares": self._to_float(ps.win_shares),
                    "bpm": self._to_float(ps.box_plus_minus),
                    "vorp": self._to_float(ps.value_over_replacement_player),
                }
            )
        return items

    def _parse_position(self, position: str | None) -> Position | None:
        if not position:
            return None
        normalized = position.upper()
        shorthand = {"G": Position.GUARD, "F": Position.FORWARD, "C": Position.CENTER}
        if normalized in shorthand:
            return shorthand[normalized]
        try:
            return Position[normalized]
        except KeyError:
            return None

    def _apply_rate_transform(self, stat_type: str, item: dict) -> dict:
        games_played = max(item.get("games_played", 0), 1)
        minutes_played = item.get("minutes_played", 0) or 0
        if stat_type == "per_game":
            factor = games_played
        elif stat_type == "per_36":
            factor = minutes_played / 36 if minutes_played else 0
        else:  # per_100
            factor = minutes_played / 100 if minutes_played else 0

        if factor == 0:
            return item

        return {
            **item,
            "points": item["points"] / factor,
            "rebounds": item["rebounds"] / factor,
            "assists": item["assists"] / factor,
            "steals": item["steals"] / factor,
            "blocks": item["blocks"] / factor,
            "turnovers": item["turnovers"] / factor,
            "fg_made": item["fg_made"] / factor,
            "fg_attempted": item["fg_attempted"] / factor,
            "fg3_made": item["fg3_made"] / factor,
            "fg3_attempted": item["fg3_attempted"] / factor,
            "ft_made": item["ft_made"] / factor,
            "ft_attempted": item["ft_attempted"] / factor,
        }

    def _sort_items(
        self, items: list[dict], sort_by: str, sort_order: str
    ) -> list[dict]:
        reverse = sort_order.lower() == "desc"
        return sorted(items, key=lambda item: item.get(sort_by, 0), reverse=reverse)

    def _to_float(self, value) -> float | None:
        return float(value) if value is not None else None
