"""Player service - business logic for player operations."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.player import Player, PlayerBoxScore, PlayerSeason, PlayerSeasonAdvanced


class PlayerService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_players(
        self,
        page: int = 1,
        per_page: int = 50,
        is_active: bool | None = None,
        position: str | None = None,
        search: str | None = None,
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
            query = query.where(Player.position == position)
        if search:
            # Search both first and last name
            search_pattern = f"%{search}%"
            query = query.where(
                (Player.first_name.ilike(search_pattern))
                | (Player.last_name.ilike(search_pattern))
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = (
            query.order_by(Player.last_name, Player.first_name)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )

        result = await self.session.execute(query)
        players = result.scalars().all()

        return {
            "items": [self._player_to_dict(p) for p in players],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        }

    async def get_player_by_slug(self, slug: str) -> dict | None:
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
        result = await self.session.execute(query)
        player = result.scalar_one_or_none()

        if player is None:
            return None

        return self._player_detail_to_dict(player)

    async def get_player_game_log(
        self,
        player_slug: str,
        season_year: int,
        season_type: str = "REGULAR",
    ) -> list[dict]:
        """Get a player's game log for a season.

        Args:
            player_slug: Player's unique slug.
            season_year: Season end year (e.g., 2024 for 2023-24).
            season_type: REGULAR, PLAYOFF, etc.

        Returns:
            List of game log entries.
        """
        from app.models.game import Game
        from app.models.season import Season

        # Get player
        player_query = select(Player.player_id).where(Player.slug == player_slug)
        player_result = await self.session.execute(player_query)
        player_id = player_result.scalar_one_or_none()

        if player_id is None:
            return []

        # Get season
        season_query = select(Season.season_id).where(Season.year == season_year)
        season_result = await self.session.execute(season_query)
        season_id = season_result.scalar_one_or_none()

        if season_id is None:
            return []

        # Get box scores for the player in that season
        query = (
            select(PlayerBoxScore)
            .join(Game, PlayerBoxScore.game_id == Game.game_id)
            .where(PlayerBoxScore.player_id == player_id)
            .where(Game.season_id == season_id)
            .where(Game.season_type == season_type)
            .order_by(Game.game_date)
        )

        result = await self.session.execute(query)
        box_scores = result.scalars().all()

        return [self._box_score_to_dict(bs) for bs in box_scores]

    async def get_player_career_stats(self, player_slug: str) -> list[dict]:
        """Get player's career statistics by season.

        Args:
            player_slug: Player's unique slug.

        Returns:
            List of season statistics.
        """
        query = (
            select(PlayerSeason)
            .join(Player)
            .where(Player.slug == player_slug)
            .order_by(PlayerSeason.season_id.desc())
        )
        result = await self.session.execute(query)
        seasons = result.scalars().all()

        return [self._season_stats_to_dict(s) for s in seasons]

    async def get_player_advanced_stats(self, player_slug: str) -> list[dict]:
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
        result = await self.session.execute(query)
        seasons = result.scalars().all()

        return [self._advanced_stats_to_dict(s) for s in seasons]

    async def get_player_splits(self, player_slug: str, season_year: int) -> dict:
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
        player_result = await self.session.execute(player_query)
        player_id = player_result.scalar_one_or_none()

        if player_id is None:
            return {}

        # Get season
        season_query = select(Season.season_id).where(Season.year == season_year)
        season_result = await self.session.execute(season_query)
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

        result = await self.session.execute(query)
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

    async def search_players(self, query: str, limit: int = 10) -> list[dict]:
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

        result = await self.session.execute(search_query)
        players = result.scalars().all()

        return [self._player_to_dict(p) for p in players]

    # Helper methods for serialization
    def _player_to_dict(self, player: Player) -> dict:
        """Convert Player to basic dict."""
        return {
            "player_id": player.player_id,
            "slug": player.slug,
            "first_name": player.first_name,
            "last_name": player.last_name,
            "full_name": player.full_name,
            "position": player.position.value if player.position else None,
            "is_active": player.is_active,
        }

    def _player_detail_to_dict(self, player: Player) -> dict:
        """Convert Player to detailed dict."""
        return {
            **self._player_to_dict(player),
            "middle_name": player.middle_name,
            "birth_date": player.birth_date.isoformat() if player.birth_date else None,
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

    def _season_stats_to_dict(self, ps: PlayerSeason) -> dict:
        """Convert PlayerSeason to dict."""
        return {
            "season_id": ps.season_id,
            "season_type": ps.season_type.value,
            "team_id": ps.team_id,
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
