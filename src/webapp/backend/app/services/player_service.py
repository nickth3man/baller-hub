"""Player service - business logic for player operations."""

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session, selectinload

from app.models.player import (
    Player,
    PlayerBoxScore,
    PlayerSeason,
    PlayerSeasonAdvanced,
    Position,
    SeasonType,
)
from app.models.season import Season
from app.models.team import Team


class PlayerService:
    def __init__(self, session: Session):
        self.session = session

    def list_players(
        self,
        page: int = 1,
        per_page: int = 50,
        is_active: bool | None = None,
        position: str | None = None,
        search: str | None = None,
        season_year: int | None = None,
        team_abbrev: str | None = None,
    ) -> dict:
        """List players with pagination and filtering.

        Args:
            page: Page number (1-indexed).
            per_page: Items per page.
            is_active: Filter by active status.
            position: Filter by position (e.g., "POINT_GUARD").
            search: Search by name (partial match).

        Returns:
            Dictionary with items, total, page info.
        """
        # Build base query
        query = select(Player)

        if is_active is not None:
            query = query.where(Player.is_active == is_active)
        if position:
            positions = self._parse_positions(position)
            if positions:
                query = query.where(Player.position.in_(positions))
        if search:
            # Search both first and last name
            search_pattern = f"%{search}%"
            query = query.where(
                (Player.first_name.ilike(search_pattern))
                | (Player.last_name.ilike(search_pattern))
            )

        if season_year or team_abbrev:
            season_player_query = (
                select(PlayerSeason.player_id)
                .join(Season, PlayerSeason.season_id == Season.season_id)
                .where(PlayerSeason.season_type == SeasonType.REGULAR)
                .where(PlayerSeason.team_id.isnot(None))
            )
            if season_year:
                season_player_query = season_player_query.where(
                    Season.year == season_year
                )
            if team_abbrev:
                season_player_query = season_player_query.join(
                    Team, PlayerSeason.team_id == Team.team_id
                ).where(Team.abbreviation == team_abbrev.upper())

            query = query.where(Player.player_id.in_(season_player_query.distinct()))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = (
            query.order_by(Player.last_name, Player.first_name)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )

        result = self.session.execute(query)
        players = result.scalars().all()
        current_teams = self._get_current_teams(
            [player.player_id for player in players]
        )

        return {
            "items": [
                self._player_to_dict(p, current_teams.get(p.player_id)) for p in players
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        }

    def get_player_by_slug(self, slug: str) -> dict | None:
        """Get player details by slug.

        Args:
            slug: Player's unique slug (e.g., "jamesle01").

        Returns:
            Player details dictionary or None.
        """
        query = (
            select(Player)
            .options(
                selectinload(Player.seasons), selectinload(Player.seasons_advanced)
            )
            .where(Player.slug == slug)
        )
        result = self.session.execute(query)
        player = result.scalar_one_or_none()

        if player is None:
            return None

        current_team = (self._get_current_teams([player.player_id])).get(
            player.player_id
        )
        return self._player_detail_to_dict(player, current_team)

    def get_player_game_log(
        self,
        player_slug: str,
        season_year: int,
        season_type: str = "REGULAR",
    ) -> dict | None:
        """Get a player's game log for a season.

        Args:
            player_slug: Player's unique slug.
            season_year: Season end year (e.g., 2024 for 2023-24).
            season_type: REGULAR, PLAYOFF, etc.

        Returns:
            List of game log entries.
        """
        from app.models.game import BoxScore, Game

        # Get player
        player_query = select(Player).where(Player.slug == player_slug)
        player_result = self.session.execute(player_query)
        player = player_result.scalar_one_or_none()

        if player is None:
            return None

        # Get season
        season_query = select(Season.season_id).where(Season.year == season_year)
        season_result = self.session.execute(season_query)
        season_id = season_result.scalar_one_or_none()

        if season_id is None:
            return None

        # Get box scores for the player in that season
        query = (
            select(
                PlayerBoxScore,
                Game.game_date,
                BoxScore.location,
                BoxScore.outcome,
                Team.abbreviation,
            )
            .join(Game, PlayerBoxScore.game_id == Game.game_id)
            .join(BoxScore, PlayerBoxScore.box_id == BoxScore.box_id)
            .join(Team, BoxScore.opponent_team_id == Team.team_id)
            .where(PlayerBoxScore.player_id == player.player_id)
            .where(Game.season_id == season_id)
            .where(Game.season_type == season_type)
            .order_by(Game.game_date)
        )

        result = self.session.execute(query)
        rows = result.all()

        games = []
        totals = {
            "games_played": 0,
            "seconds_played": 0,
            "points": 0,
            "rebounds": 0,
            "assists": 0,
            "steals": 0,
            "blocks": 0,
            "turnovers": 0,
            "made_fg": 0,
            "attempted_fg": 0,
            "made_3pt": 0,
            "attempted_3pt": 0,
            "made_ft": 0,
            "attempted_ft": 0,
        }

        for pbs, game_date, location, outcome, opponent_abbrev in rows:
            games.append(
                {
                    "game_id": pbs.game_id,
                    "game_date": game_date,
                    "opponent_abbrev": opponent_abbrev,
                    "location": location.value,
                    "outcome": outcome.value,
                    "seconds_played": pbs.seconds_played,
                    "points": pbs.points_scored,
                    "rebounds": pbs.total_rebounds,
                    "assists": pbs.assists,
                    "steals": pbs.steals,
                    "blocks": pbs.blocks,
                    "turnovers": pbs.turnovers,
                    "made_fg": pbs.made_fg,
                    "attempted_fg": pbs.attempted_fg,
                    "made_3pt": pbs.made_3pt,
                    "attempted_3pt": pbs.attempted_3pt,
                    "made_ft": pbs.made_ft,
                    "attempted_ft": pbs.attempted_ft,
                    "plus_minus": pbs.plus_minus,
                }
            )

            totals["games_played"] += 1
            totals["seconds_played"] += pbs.seconds_played
            totals["points"] += pbs.points_scored
            totals["rebounds"] += pbs.total_rebounds
            totals["assists"] += pbs.assists
            totals["steals"] += pbs.steals
            totals["blocks"] += pbs.blocks
            totals["turnovers"] += pbs.turnovers
            totals["made_fg"] += pbs.made_fg
            totals["attempted_fg"] += pbs.attempted_fg
            totals["made_3pt"] += pbs.made_3pt
            totals["attempted_3pt"] += pbs.attempted_3pt
            totals["made_ft"] += pbs.made_ft
            totals["attempted_ft"] += pbs.attempted_ft

        return {
            "player_slug": player.slug,
            "player_name": player.full_name,
            "season_year": season_year,
            "season_type": season_type,
            "games": games,
            "totals": totals,
        }

    def get_player_career_stats(self, player_slug: str) -> list[dict]:
        """Get player's career statistics by season.

        Args:
            player_slug: Player's unique slug.

        Returns:
            List of season statistics.
        """
        query = (
            select(PlayerSeason, Season.year, Team.abbreviation)
            .join(Player)
            .join(Season, PlayerSeason.season_id == Season.season_id)
            .outerjoin(Team, PlayerSeason.team_id == Team.team_id)
            .where(Player.slug == player_slug)
            .order_by(Season.year.desc())
        )
        result = self.session.execute(query)
        rows = result.all()

        selected: dict[
            tuple[int, SeasonType], tuple[PlayerSeason, int, str | None]
        ] = {}
        for player_season, season_year, team_abbrev in rows:
            key = (player_season.season_id, player_season.season_type)
            if key not in selected:
                selected[key] = (player_season, season_year, team_abbrev)
                continue
            if (
                player_season.is_combined_totals
                and not selected[key][0].is_combined_totals
            ):
                selected[key] = (player_season, season_year, team_abbrev)

        seasons = sorted(selected.values(), key=lambda item: item[1], reverse=True)
        return [
            self._season_stats_to_dict(ps, season_year, team_abbrev)
            for ps, season_year, team_abbrev in seasons
        ]

    def get_player_career(self, player_slug: str) -> dict | None:
        """Get aggregated career totals from the materialized view."""
        query = text(
            """
            SELECT
                player_id,
                slug,
                first_name,
                last_name,
                games_played,
                career_points,
                career_assists,
                career_rebounds,
                ppg,
                apg,
                rpg
            FROM player_career_stats
            WHERE slug = :slug
            """
        )
        result = self.session.execute(query, {"slug": player_slug})
        row = result.mappings().first()
        if not row:
            return None

        return {
            "player_id": row["player_id"],
            "slug": row["slug"],
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "games_played": row["games_played"] or 0,
            "career_points": row["career_points"] or 0,
            "career_assists": row["career_assists"] or 0,
            "career_rebounds": row["career_rebounds"] or 0,
            "ppg": float(row["ppg"]) if row["ppg"] is not None else 0.0,
            "apg": float(row["apg"]) if row["apg"] is not None else 0.0,
            "rpg": float(row["rpg"]) if row["rpg"] is not None else 0.0,
        }

    def get_player_advanced_stats(self, player_slug: str) -> list[dict]:
        """Get player's advanced career statistics.

        Args:
            player_slug: Player's unique slug.

        Returns:
            List of advanced season statistics.
        """
        query = (
            select(PlayerSeasonAdvanced)
            .join(Player)
            .where(Player.slug == player_slug)
            .order_by(PlayerSeasonAdvanced.season_id.desc())
        )
        result = self.session.execute(query)
        seasons = result.scalars().all()

        return [self._advanced_stats_to_dict(s) for s in seasons]

    def get_player_splits(self, player_slug: str, season_year: int) -> dict:
        """Calculate player splits for a season.

        Args:
            player_slug: Player's unique slug.
            season_year: Season end year.

        Returns:
            Dictionary with home/away, win/loss splits etc.
        """
        from app.models.game import BoxScore, Game, Location, Outcome
        from app.models.season import Season

        # Get player
        player_query = select(Player.player_id).where(Player.slug == player_slug)
        player_result = self.session.execute(player_query)
        player_id = player_result.scalar_one_or_none()

        if player_id is None:
            return {}

        # Get season
        season_query = select(Season.season_id).where(Season.year == season_year)
        season_result = self.session.execute(season_query)
        season_id = season_result.scalar_one_or_none()

        if season_id is None:
            return {}

        # Get all box scores with game info
        query = (
            select(PlayerBoxScore, BoxScore)
            .join(BoxScore, PlayerBoxScore.box_id == BoxScore.box_id)
            .join(Game, PlayerBoxScore.game_id == Game.game_id)
            .where(PlayerBoxScore.player_id == player_id)
            .where(Game.season_id == season_id)
        )

        result = self.session.execute(query)
        rows = result.all()

        # Calculate splits
        home_stats = {"games": 0, "points": 0, "rebounds": 0, "assists": 0}
        away_stats = {"games": 0, "points": 0, "rebounds": 0, "assists": 0}
        win_stats = {"games": 0, "points": 0, "rebounds": 0, "assists": 0}
        loss_stats = {"games": 0, "points": 0, "rebounds": 0, "assists": 0}

        for pbs, bs in rows:
            stats = home_stats if bs.location == Location.HOME else away_stats
            stats["games"] += 1
            stats["points"] += pbs.points_scored
            stats["rebounds"] += pbs.offensive_rebounds + pbs.defensive_rebounds
            stats["assists"] += pbs.assists

            outcome_stats = win_stats if bs.outcome == Outcome.WIN else loss_stats
            outcome_stats["games"] += 1
            outcome_stats["points"] += pbs.points_scored
            outcome_stats["rebounds"] += pbs.offensive_rebounds + pbs.defensive_rebounds
            outcome_stats["assists"] += pbs.assists

        def avg(total: int, games: int) -> float:
            return round(total / games, 1) if games > 0 else 0.0

        return {
            "home": {
                "games": home_stats["games"],
                "ppg": avg(home_stats["points"], home_stats["games"]),
                "rpg": avg(home_stats["rebounds"], home_stats["games"]),
                "apg": avg(home_stats["assists"], home_stats["games"]),
            },
            "away": {
                "games": away_stats["games"],
                "ppg": avg(away_stats["points"], away_stats["games"]),
                "rpg": avg(away_stats["rebounds"], away_stats["games"]),
                "apg": avg(away_stats["assists"], away_stats["games"]),
            },
            "wins": {
                "games": win_stats["games"],
                "ppg": avg(win_stats["points"], win_stats["games"]),
                "rpg": avg(win_stats["rebounds"], win_stats["games"]),
                "apg": avg(win_stats["assists"], win_stats["games"]),
            },
            "losses": {
                "games": loss_stats["games"],
                "ppg": avg(loss_stats["points"], loss_stats["games"]),
                "rpg": avg(loss_stats["rebounds"], loss_stats["games"]),
                "apg": avg(loss_stats["assists"], loss_stats["games"]),
            },
        }

    def search_players(self, query: str, limit: int = 10) -> list[dict]:
        """Search players by name.

        Args:
            query: Search term.
            limit: Maximum results.

        Returns:
            List of matching players.
        """
        search_pattern = f"%{query}%"
        search_query = (
            select(Player)
            .where(
                (Player.first_name.ilike(search_pattern))
                | (Player.last_name.ilike(search_pattern))
            )
            .order_by(Player.last_name)
            .limit(limit)
        )

        result = self.session.execute(search_query)
        players = result.scalars().all()

        current_teams = self._get_current_teams(
            [player.player_id for player in players]
        )
        return [
            self._player_to_dict(player, current_teams.get(player.player_id))
            for player in players
        ]

    # Helper methods for serialization
    def _get_current_teams(self, player_ids: list[int]) -> dict[int, str]:
        """Get the most recent team abbreviation for a list of players."""
        if not player_ids:
            return {}

        query = (
            select(PlayerSeason.player_id, Season.year, Team.abbreviation)
            .join(Season, PlayerSeason.season_id == Season.season_id)
            .join(Team, PlayerSeason.team_id == Team.team_id)
            .where(PlayerSeason.player_id.in_(player_ids))
            .where(PlayerSeason.team_id.isnot(None))
            .where(PlayerSeason.season_type == SeasonType.REGULAR)
        )
        result = self.session.execute(query)
        latest: dict[int, tuple[int, str]] = {}

        for player_id, season_year, abbrev in result.all():
            current = latest.get(player_id)
            if current is None or season_year > current[0]:
                latest[player_id] = (season_year, abbrev)

        return {player_id: abbrev for player_id, (_, abbrev) in latest.items()}

    def _parse_positions(self, position: str) -> list[Position]:
        normalized = position.upper()
        if normalized in {"G", "GUARD"}:
            return [
                Position.GUARD,
                Position.POINT_GUARD,
                Position.SHOOTING_GUARD,
            ]
        if normalized in {"F", "FORWARD"}:
            return [
                Position.FORWARD,
                Position.SMALL_FORWARD,
                Position.POWER_FORWARD,
            ]
        if normalized in {"C", "CENTER"}:
            return [Position.CENTER]
        if normalized in {"G-F", "F-G"}:
            return [
                Position.GUARD,
                Position.FORWARD,
                Position.POINT_GUARD,
                Position.SHOOTING_GUARD,
                Position.SMALL_FORWARD,
                Position.POWER_FORWARD,
            ]
        if normalized in {"F-C", "C-F"}:
            return [
                Position.FORWARD,
                Position.CENTER,
                Position.SMALL_FORWARD,
                Position.POWER_FORWARD,
            ]
        try:
            return [Position[normalized]]
        except KeyError:
            return []

    def _player_to_dict(self, player: Player, current_team: str | None = None) -> dict:
        """Convert Player to basic dict."""
        return {
            "player_id": player.player_id,
            "slug": player.slug,
            "first_name": player.first_name,
            "last_name": player.last_name,
            "full_name": player.full_name,
            "position": player.position.value if player.position else None,
            "is_active": player.is_active,
            "birth_date": player.birth_date,
            "birth_place_city": player.birth_place_city,
            "birth_place_country": player.birth_place_country,
            "height_inches": float(player.height_inches)
            if player.height_inches
            else None,
            "weight_lbs": player.weight_lbs,
            "college": player.college,
            "high_school": player.high_school,
            "draft_year": player.draft_year,
            "draft_pick": player.draft_pick,
            "debut_year": player.debut_year,
            "final_year": player.final_year,
            "current_team": current_team,
        }

    def _player_detail_to_dict(
        self, player: Player, current_team: str | None = None
    ) -> dict:
        """Convert Player to detailed dict."""
        return {
            **self._player_to_dict(player, current_team),
            "middle_name": player.middle_name,
        }

    def _box_score_to_dict(self, bs: PlayerBoxScore) -> dict:
        """Convert PlayerBoxScore to dict."""
        return {
            "game_id": bs.game_id,
            "points": bs.points_scored,
            "rebounds": bs.offensive_rebounds + bs.defensive_rebounds,
            "offensive_rebounds": bs.offensive_rebounds,
            "defensive_rebounds": bs.defensive_rebounds,
            "assists": bs.assists,
            "steals": bs.steals,
            "blocks": bs.blocks,
            "turnovers": bs.turnovers,
            "minutes": bs.minutes_played,
            "fg_made": bs.made_fg,
            "fg_attempted": bs.attempted_fg,
            "fg3_made": bs.made_3pt,
            "fg3_attempted": bs.attempted_3pt,
            "ft_made": bs.made_ft,
            "ft_attempted": bs.attempted_ft,
            "plus_minus": bs.plus_minus,
            "game_score": float(bs.game_score) if bs.game_score else None,
        }

    def _season_stats_to_dict(
        self,
        ps: PlayerSeason,
        season_year: int,
        team_abbrev: str | None,
    ) -> dict:
        """Convert PlayerSeason to dict."""
        resolved_team = "TOT" if ps.is_combined_totals else team_abbrev
        return {
            "season_id": ps.season_id,
            "season_year": season_year,
            "season_type": ps.season_type.value,
            "team_id": ps.team_id,
            "team_abbrev": resolved_team,
            "games_played": ps.games_played,
            "games_started": ps.games_started,
            "minutes_played": ps.minutes_played,
            "points": ps.points_scored,
            "ppg": ps.points_per_game,
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

    def _advanced_stats_to_dict(self, ps: PlayerSeasonAdvanced) -> dict:
        """Convert PlayerSeasonAdvanced to dict."""
        return {
            "season_id": ps.season_id,
            "season_type": ps.season_type.value,
            "games_played": ps.games_played,
            "minutes_played": ps.minutes_played,
            "per": float(ps.player_efficiency_rating)
            if ps.player_efficiency_rating
            else None,
            "ts_pct": float(ps.true_shooting_percentage)
            if ps.true_shooting_percentage
            else None,
            "efg_pct": float(ps.effective_fg_percentage)
            if ps.effective_fg_percentage
            else None,
            "usage_pct": float(ps.usage_percentage) if ps.usage_percentage else None,
            "bpm": float(ps.box_plus_minus) if ps.box_plus_minus else None,
            "vorp": float(ps.value_over_replacement_player)
            if ps.value_over_replacement_player
            else None,
            "win_shares": float(ps.win_shares) if ps.win_shares else None,
            "ws_per_48": float(ps.win_shares_per_48) if ps.win_shares_per_48 else None,
        }
