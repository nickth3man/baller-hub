"""Team service - business logic for team operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.game import Game
from app.models.player import Player, PlayerSeason
from app.models.season import Conference, Division, Season
from app.models.team import Franchise, Team, TeamSeason


class TeamService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_teams(
        self,
        is_active: bool = True,
        conference: str | None = None,
        division: str | None = None,
    ) -> list[dict]:
        """List all teams with optional filtering.

        Args:
            is_active: Filter by active status.
            conference: Filter by conference (EASTERN, WESTERN).

        Returns:
            List of team dictionaries.
        """
        query = select(Team).options(selectinload(Team.franchise))

        if is_active is not None:
            query = query.where(Team.is_active == is_active)

        if conference or division:
            query = query.join(Division, Team.division_id == Division.division_id)
            if conference:
                query = query.join(
                    Conference, Division.conference_id == Conference.conference_id
                ).where(Conference.conference_type == conference.upper())
            if division:
                query = query.where(Division.division_type == division.upper())

        query = query.order_by(Team.name)
        result = await self.session.execute(query)
        teams = result.scalars().all()

        return [self._team_to_dict(t) for t in teams]

    async def get_team_by_abbreviation(self, abbreviation: str) -> dict | None:
        """Get team details by abbreviation.

        Args:
            abbreviation: Team abbreviation (e.g., "BOS", "LAL").

        Returns:
            Team details dictionary or None.
        """
        query = (
            select(Team)
            .options(selectinload(Team.franchise), selectinload(Team.seasons))
            .where(Team.abbreviation == abbreviation.upper())
        )
        result = await self.session.execute(query)
        team = result.scalar_one_or_none()

        if team is None:
            return None

        return self._team_detail_to_dict(team)

    async def get_team_roster(self, abbreviation: str, season_year: int) -> list[dict]:
        """Get team roster for a specific season.

        Args:
            abbreviation: Team abbreviation.
            season_year: Season end year.

        Returns:
            List of player dictionaries.
        """
        # Get team
        team_query = select(Team.team_id).where(
            Team.abbreviation == abbreviation.upper()
        )
        team_result = await self.session.execute(team_query)
        team_id = team_result.scalar_one_or_none()

        if team_id is None:
            return []

        # Get season
        season_query = select(Season.season_id).where(Season.year == season_year)
        season_result = await self.session.execute(season_query)
        season_id = season_result.scalar_one_or_none()

        if season_id is None:
            return []

        # Get players who played for this team in this season
        query = (
            select(Player, PlayerSeason)
            .join(PlayerSeason, Player.player_id == PlayerSeason.player_id)
            .where(PlayerSeason.team_id == team_id)
            .where(PlayerSeason.season_id == season_id)
            .order_by(Player.last_name)
        )

        result = await self.session.execute(query)
        rows = result.all()

        return [
            {
                **self._player_to_dict(player),
                "games_played": ps.games_played,
                "games_started": ps.games_started,
                "ppg": ps.points_per_game,
            }
            for player, ps in rows
        ]

    async def get_team_schedule(
        self, abbreviation: str, season_year: int
    ) -> list[dict]:
        """Get team's schedule for a season.

        Args:
            abbreviation: Team abbreviation.
            season_year: Season end year.

        Returns:
            List of game dictionaries.
        """
        # Get team
        team_query = select(Team.team_id).where(
            Team.abbreviation == abbreviation.upper()
        )
        team_result = await self.session.execute(team_query)
        team_id = team_result.scalar_one_or_none()

        if team_id is None:
            return []

        # Get season
        season_query = select(Season.season_id).where(Season.year == season_year)
        season_result = await self.session.execute(season_query)
        season_id = season_result.scalar_one_or_none()

        if season_id is None:
            return []

        # Get games where team is home or away
        query = (
            select(Game)
            .where(Game.season_id == season_id)
            .where((Game.home_team_id == team_id) | (Game.away_team_id == team_id))
            .order_by(Game.game_date)
        )

        result = await self.session.execute(query)
        games = result.scalars().all()
        team_map = await self._get_team_abbrev_map(
            {game.home_team_id for game in games}
            | {game.away_team_id for game in games}
        )

        return [self._game_to_dict(g, team_id, team_map) for g in games]

    async def get_team_season_stats(
        self, abbreviation: str, season_year: int
    ) -> dict | None:
        """Get team's aggregated stats for a season.

        Args:
            abbreviation: Team abbreviation.
            season_year: Season end year.

        Returns:
            Team season statistics.
        """
        # Get team
        team_query = select(Team.team_id).where(
            Team.abbreviation == abbreviation.upper()
        )
        team_result = await self.session.execute(team_query)
        team_id = team_result.scalar_one_or_none()

        if team_id is None:
            return None

        # Get season
        season_query = select(Season.season_id).where(Season.year == season_year)
        season_result = await self.session.execute(season_query)
        season_id = season_result.scalar_one_or_none()

        if season_id is None:
            return None

        # Get team season
        query = select(TeamSeason).where(
            TeamSeason.team_id == team_id,
            TeamSeason.season_id == season_id,
        )
        result = await self.session.execute(query)
        team_season = result.scalar_one_or_none()

        if team_season is None:
            return None

        return self._team_season_to_dict(team_season)

    async def get_team_history(self, abbreviation: str) -> list[dict]:
        """Get team's historical season-by-season records.

        Args:
            abbreviation: Team abbreviation.

        Returns:
            List of season records.
        """
        # Get team
        team_query = select(Team.team_id).where(
            Team.abbreviation == abbreviation.upper()
        )
        team_result = await self.session.execute(team_query)
        team_id = team_result.scalar_one_or_none()

        if team_id is None:
            return []

        # Get all seasons for this team
        query = (
            select(TeamSeason, Season)
            .join(Season, TeamSeason.season_id == Season.season_id)
            .where(TeamSeason.team_id == team_id)
            .order_by(Season.year.desc())
        )

        result = await self.session.execute(query)
        rows = result.all()

        return [
            {
                "year": season.year,
                "wins": ts.wins,
                "losses": ts.losses,
                "win_pct": ts.win_percentage,
                "made_playoffs": ts.made_playoffs,
                "playoff_round": ts.playoff_round_reached,
            }
            for ts, season in rows
        ]

    async def get_franchise_history(self, abbreviation: str) -> dict | None:
        """Get full franchise history including relocations.

        Args:
            abbreviation: Current team abbreviation.

        Returns:
            Franchise history dictionary.
        """
        # Get team and franchise
        query = (
            select(Team)
            .options(selectinload(Team.franchise).selectinload(Franchise.teams))
            .where(Team.abbreviation == abbreviation.upper())
        )
        result = await self.session.execute(query)
        team = result.scalar_one_or_none()

        if team is None or team.franchise is None:
            return None

        return {
            "franchise_id": team.franchise.franchise_id,
            "name": team.franchise.name,
            "founded_year": team.franchise.founded_year,
            "current_team": self._team_to_dict(team),
            "all_teams": [self._team_to_dict(t) for t in team.franchise.teams],
        }

    # Helper methods
    def _team_to_dict(self, team: Team) -> dict:
        """Convert Team to basic dict."""
        return {
            "team_id": team.team_id,
            "name": team.name,
            "abbreviation": team.abbreviation,
            "city": team.city,
            "is_active": team.is_active,
            "founded_year": team.founded_year,
            "arena": team.arena,
            "arena_capacity": team.arena_capacity,
        }

    def _team_detail_to_dict(self, team: Team) -> dict:
        """Convert Team to detailed dict."""
        return {
            **self._team_to_dict(team),
            "franchise": {
                "name": team.franchise.name,
                "founded_year": team.franchise.founded_year,
            }
            if team.franchise
            else None,
        }

    def _player_to_dict(self, player: Player) -> dict:
        """Convert Player to basic dict."""
        return {
            "player_id": player.player_id,
            "slug": player.slug,
            "name": player.full_name,
            "position": player.position.value if player.position else None,
        }

    async def _get_team_abbrev_map(self, team_ids: set[int]) -> dict[int, str]:
        if not team_ids:
            return {}
        query = select(Team.team_id, Team.abbreviation).where(
            Team.team_id.in_(team_ids)
        )
        result = await self.session.execute(query)
        return {team_id: abbrev for team_id, abbrev in result.all()}

    def _game_to_dict(
        self, game: Game, team_id: int, team_abbrev_map: dict[int, str]
    ) -> dict:
        """Convert Game to dict relative to a team."""
        is_home = game.home_team_id == team_id
        opponent_id = game.away_team_id if is_home else game.home_team_id
        return {
            "game_id": game.game_id,
            "date": game.game_date.isoformat(),
            "opponent_abbrev": team_abbrev_map.get(opponent_id, ""),
            "location": "HOME" if is_home else "AWAY",
            "team_score": game.home_score if is_home else game.away_score,
            "opponent_score": game.away_score if is_home else game.home_score,
            "result": self._get_result(game, team_id),
        }

    def _get_result(self, game: Game, team_id: int) -> str | None:
        """Determine W/L for a team in a game."""
        if game.home_score is None or game.away_score is None:
            return None
        is_home = game.home_team_id == team_id
        if is_home:
            return "W" if game.home_score > game.away_score else "L"
        return "W" if game.away_score > game.home_score else "L"

    def _team_season_to_dict(self, ts: TeamSeason) -> dict:
        """Convert TeamSeason to dict."""
        return {
            "games_played": ts.games_played,
            "wins": ts.wins,
            "losses": ts.losses,
            "points_per_game": float(ts.points_per_game)
            if ts.points_per_game
            else None,
            "points_allowed_per_game": float(ts.points_allowed_per_game)
            if ts.points_allowed_per_game
            else None,
            "pace": float(ts.pace) if ts.pace else None,
            "offensive_rating": float(ts.offensive_rating)
            if ts.offensive_rating
            else None,
            "defensive_rating": float(ts.defensive_rating)
            if ts.defensive_rating
            else None,
            "net_rating": float(ts.net_rating) if ts.net_rating else None,
            "playoff_seed": ts.playoff_seed,
            "made_playoffs": ts.made_playoffs,
        }
