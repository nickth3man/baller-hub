"""Game service - business logic for game operations."""

from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.game import BoxScore, Game, Location, PlayByPlay
from app.models.player import Player, PlayerBoxScore
from app.models.season import Season
from app.models.team import Team


class GameService:
    def __init__(self, session: Session):
        self.session = session

    def list_games(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        team_abbrev: str | None = None,
        season_year: int | None = None,
        season_type: str = "REGULAR",
        page: int = 1,
        per_page: int = 50,
    ) -> dict:
        """List games with filtering and pagination.

        Args:
            start_date: Filter games from this date.
            end_date: Filter games until this date.
            team_id: Filter by team (home or away).
            season_year: Filter by season.
            season_type: REGULAR, PLAYOFF, etc.
            page: Page number.
            per_page: Items per page.

        Returns:
            Dictionary with games and pagination info.
        """
        query = select(Game)

        if start_date:
            query = query.where(Game.game_date >= start_date)
        if end_date:
            query = query.where(Game.game_date <= end_date)
        if team_abbrev:
            team_query = select(Team.team_id).where(
                Team.abbreviation == team_abbrev.upper()
            )
            team_result = self.session.execute(team_query)
            team_id = team_result.scalar_one_or_none()
            if team_id:
                query = query.where(
                    (Game.home_team_id == team_id) | (Game.away_team_id == team_id)
                )
            else:
                query = query.where(Game.game_id == -1)
        if season_year:
            # Get season id for year
            season_subq = select(Season.season_id).where(Season.year == season_year)
            query = query.where(Game.season_id.in_(season_subq))
        if season_type:
            query = query.where(Game.season_type == season_type)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = (
            query.order_by(Game.game_date.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )

        result = self.session.execute(query)
        games = result.scalars().all()
        team_map = self._get_team_abbrev_map(
            {game.home_team_id for game in games}
            | {game.away_team_id for game in games}
        )

        return {
            "items": [self._game_to_dict(g, team_map) for g in games],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        }

    def get_todays_games(self, target_date: date | None = None) -> list[dict]:
        """Get all games for today (or specified date).

        Args:
            target_date: Date to get games for. Defaults to today.

        Returns:
            List of games.
        """
        if target_date is None:
            target_date = date.today()

        query = (
            select(Game).where(Game.game_date == target_date).order_by(Game.game_time)
        )

        result = self.session.execute(query)
        games = result.scalars().all()
        team_map = self._get_team_abbrev_map(
            {game.home_team_id for game in games}
            | {game.away_team_id for game in games}
        )

        return [self._game_to_dict(g, team_map) for g in games]

    def get_games_by_date(self, game_date: date) -> list[dict]:
        """Get games for a specific date."""
        query = select(Game).where(Game.game_date == game_date).order_by(Game.game_time)
        result = self.session.execute(query)
        games = result.scalars().all()
        team_map = self._get_team_abbrev_map(
            {game.home_team_id for game in games}
            | {game.away_team_id for game in games}
        )
        return [self._game_to_dict(game, team_map) for game in games]

    def get_games_by_date_range(self, start_date: date, end_date: date) -> list[dict]:
        """Get games within a date range.

        Args:
            start_date: Start of range.
            end_date: End of range.

        Returns:
            List of games.
        """
        query = (
            select(Game)
            .where(Game.game_date >= start_date)
            .where(Game.game_date <= end_date)
            .order_by(Game.game_date, Game.game_time)
        )

        result = self.session.execute(query)
        games = result.scalars().all()
        team_map = self._get_team_abbrev_map(
            {game.home_team_id for game in games}
            | {game.away_team_id for game in games}
        )

        return [self._game_to_dict(g, team_map) for g in games]

    def get_game_by_id(self, game_id: int) -> dict | None:
        """Get game details by ID.

        Args:
            game_id: Database game ID.

        Returns:
            Game details or None.
        """
        query = select(Game).where(Game.game_id == game_id)

        result = self.session.execute(query)
        game = result.scalar_one_or_none()

        if game is None:
            return None

        team_map = self._get_team_abbrev_map({game.home_team_id, game.away_team_id})
        return self._game_to_dict(game, team_map)

    def get_box_score(self, game_id: int) -> dict | None:
        """Get full box score for a game.

        Args:
            game_id: Database game ID.

        Returns:
            Box score with team and player stats.
        """
        # Get game
        game_query = select(Game).where(Game.game_id == game_id)
        game_result = self.session.execute(game_query)
        game = game_result.scalar_one_or_none()

        if game is None:
            return None

        team_info = self._get_team_info_map({game.home_team_id, game.away_team_id})
        team_abbrevs = {
            team_id: info.get("abbrev") for team_id, info in team_info.items()
        }

        # Get team box scores
        team_bs_query = select(BoxScore).where(BoxScore.game_id == game_id)
        team_bs_result = self.session.execute(team_bs_query)
        team_box_scores = team_bs_result.scalars().all()

        # Get player box scores
        player_bs_query = (
            select(PlayerBoxScore, Player)
            .join(Player, PlayerBoxScore.player_id == Player.player_id)
            .where(PlayerBoxScore.game_id == game_id)
            .order_by(PlayerBoxScore.is_starter.desc(), Player.last_name)
        )
        player_bs_result = self.session.execute(player_bs_query)
        player_box_scores = player_bs_result.all()

        # Organize by team
        home_players = []
        away_players = []

        for pbs, player in player_box_scores:
            player_data = self._player_box_score_to_dict(pbs, player)
            if pbs.team_id == game.home_team_id:
                home_players.append(player_data)
            else:
                away_players.append(player_data)

        return {
            "game": self._game_to_dict(game, team_abbrevs),
            "home_team": {
                "team_id": game.home_team_id,
                "team_abbrev": team_info.get(game.home_team_id, {}).get("abbrev"),
                "team_name": team_info.get(game.home_team_id, {}).get("name"),
                "score": game.home_score,
                "box_score": next(
                    (
                        self._team_box_score_to_dict(bs)
                        for bs in team_box_scores
                        if bs.location == Location.HOME
                    ),
                    None,
                ),
                "players": home_players,
            },
            "away_team": {
                "team_id": game.away_team_id,
                "team_abbrev": team_info.get(game.away_team_id, {}).get("abbrev"),
                "team_name": team_info.get(game.away_team_id, {}).get("name"),
                "score": game.away_score,
                "box_score": next(
                    (
                        self._team_box_score_to_dict(bs)
                        for bs in team_box_scores
                        if bs.location == Location.AWAY
                    ),
                    None,
                ),
                "players": away_players,
            },
        }

    def get_play_by_play(self, game_id: int, period: int | None = None) -> dict | None:
        """Get play-by-play data for a game."""
        game_query = select(Game).where(Game.game_id == game_id)
        game_result = self.session.execute(game_query)
        game = game_result.scalar_one_or_none()
        if game is None:
            return None

        query = select(PlayByPlay).where(PlayByPlay.game_id == game_id)
        if period is not None:
            query = query.where(PlayByPlay.period == period)
        query = query.order_by(PlayByPlay.period, PlayByPlay.seconds_remaining.desc())

        result = self.session.execute(query)
        plays = result.scalars().all()

        team_map = self._get_team_abbrev_map({game.home_team_id, game.away_team_id})
        return {
            "game_id": game.game_id,
            "home_team_abbrev": team_map.get(game.home_team_id, ""),
            "away_team_abbrev": team_map.get(game.away_team_id, ""),
            "plays": [self._play_to_dict(play, team_map) for play in plays],
            "period_filter": period,
        }

    def get_games_week(self, reference_date: date | None = None) -> dict:
        """Get games for a week around a reference date.

        Args:
            reference_date: Center date. Defaults to today.

        Returns:
            Dictionary with games grouped by date.
        """
        if reference_date is None:
            reference_date = date.today()

        # Get 3 days before and after
        start_date = reference_date - timedelta(days=3)
        end_date = reference_date + timedelta(days=3)

        games = self.get_games_by_date_range(start_date, end_date)

        # Group by date
        games_by_date: dict[str, list[dict]] = {}
        for game in games:
            game_date = game["date"]
            if game_date not in games_by_date:
                games_by_date[game_date] = []
            games_by_date[game_date].append(game)

        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "games_by_date": games_by_date,
        }

    def _get_team_abbrev_map(self, team_ids: set[int]) -> dict[int, str]:
        if not team_ids:
            return {}
        query = select(Team.team_id, Team.abbreviation).where(
            Team.team_id.in_(team_ids)
        )
        result = self.session.execute(query)
        return dict(result.all())

    def _get_team_info_map(self, team_ids: set[int]) -> dict[int, dict[str, str]]:
        if not team_ids:
            return {}
        query = select(Team.team_id, Team.abbreviation, Team.name).where(
            Team.team_id.in_(team_ids)
        )
        result = self.session.execute(query)
        return {
            team_id: {"abbrev": abbrev, "name": name}
            for team_id, abbrev, name in result.all()
        }

    # Helper methods
    def _game_to_dict(
        self, game: Game, team_abbrev_map: dict[int, str] | None = None
    ) -> dict:
        """Convert Game to basic dict."""
        home_abbrev = (
            team_abbrev_map.get(game.home_team_id) if team_abbrev_map else None
        )
        away_abbrev = (
            team_abbrev_map.get(game.away_team_id) if team_abbrev_map else None
        )
        return {
            "game_id": game.game_id,
            "date": game.game_date.isoformat(),
            "time": game.game_time.isoformat() if game.game_time else None,
            "home_team_id": game.home_team_id,
            "away_team_id": game.away_team_id,
            "home_team_abbrev": home_abbrev,
            "away_team_abbrev": away_abbrev,
            "home_score": game.home_score,
            "away_score": game.away_score,
            "season_type": game.season_type,
            "is_final": game.home_score is not None,
            "arena": game.arena,
            "attendance": game.attendance,
        }

    def _game_detail_to_dict(
        self, game: Game, team_abbrev_map: dict[int, str] | None = None
    ) -> dict:
        """Convert Game to detailed dict."""
        return {
            **self._game_to_dict(game, team_abbrev_map),
            "duration_minutes": game.duration_minutes,
            "officials": game.officials,
            "playoff_round": game.playoff_round,
            "playoff_game_number": game.playoff_game_number,
        }

    def _team_box_score_to_dict(self, bs: BoxScore) -> dict:
        """Convert team BoxScore to dict."""
        total_rebounds = (
            bs.total_rebounds
            if bs.total_rebounds is not None
            else bs.offensive_rebounds + bs.defensive_rebounds
        )
        return {
            "points": bs.points_scored,
            "fg_made": bs.made_fg,
            "fg_attempted": bs.attempted_fg,
            "fg_pct": float(bs.field_goal_percentage)
            if bs.field_goal_percentage
            else None,
            "fg3_made": bs.made_3pt,
            "fg3_attempted": bs.attempted_3pt,
            "fg3_pct": float(bs.three_point_percentage)
            if bs.three_point_percentage
            else None,
            "ft_made": bs.made_ft,
            "ft_attempted": bs.attempted_ft,
            "ft_pct": float(bs.free_throw_percentage)
            if bs.free_throw_percentage
            else None,
            "offensive_rebounds": bs.offensive_rebounds,
            "defensive_rebounds": bs.defensive_rebounds,
            "total_rebounds": total_rebounds,
            "assists": bs.assists,
            "steals": bs.steals,
            "blocks": bs.blocks,
            "turnovers": bs.turnovers,
            "personal_fouls": bs.personal_fouls,
            "quarter_scores": bs.quarter_scores,
        }

    def _player_box_score_to_dict(self, pbs: PlayerBoxScore, player: Player) -> dict:
        """Convert PlayerBoxScore to dict."""
        return {
            "player_id": player.player_id,
            "slug": player.slug,
            "name": player.full_name,
            "position": pbs.position.value if pbs.position else None,
            "is_starter": pbs.is_starter,
            "minutes": pbs.seconds_played,
            "points": pbs.points_scored,
            "rebounds": pbs.total_rebounds,
            "offensive_rebounds": pbs.offensive_rebounds,
            "defensive_rebounds": pbs.defensive_rebounds,
            "assists": pbs.assists,
            "steals": pbs.steals,
            "blocks": pbs.blocks,
            "turnovers": pbs.turnovers,
            "personal_fouls": pbs.personal_fouls,
            "fg_made": pbs.made_fg,
            "fg_attempted": pbs.attempted_fg,
            "fg3_made": pbs.made_3pt,
            "fg3_attempted": pbs.attempted_3pt,
            "ft_made": pbs.made_ft,
            "ft_attempted": pbs.attempted_ft,
            "plus_minus": pbs.plus_minus,
            "game_score": float(pbs.game_score) if pbs.game_score else None,
        }

    def _play_to_dict(self, play: PlayByPlay, team_abbrev_map: dict[int, str]) -> dict:
        """Convert PlayByPlay to dict."""
        minutes = play.seconds_remaining // 60
        seconds = play.seconds_remaining % 60

        return {
            "play_id": play.play_id,
            "period": play.period,
            "time": f"{minutes}:{seconds:02d}",
            "seconds_remaining": play.seconds_remaining,
            "home_score": play.home_score,
            "away_score": play.away_score,
            "team_abbrev": team_abbrev_map.get(play.team_id) if play.team_id else None,
            "play_type": play.play_type.value,
            "description": play.description,
            "player_id": play.player_involved_id,
            "points": play.points_scored,
        }
