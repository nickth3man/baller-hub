"""Award models."""

from enum import Enum

from sqlmodel import Field, Relationship, SQLModel


class AwardCategory(str, Enum):
    """Enum representing the category of an award.

    Attributes:
        MOST_VALUABLE_PLAYER: MVP award.
        CHAMPIONSHIP: NBA Championship.
        FINALS_MVP: Bill Russell NBA Finals MVP.
        DEFENSIVE_PLAYER_OF_THE_YEAR: Defensive Player of the Year.
        ROOKIE_OF_THE_YEAR: Rookie of the Year.
        COACH_OF_THE_YEAR: Coach of the Year.
        SIXTH_MAN: Sixth Man of the Year.
        MOST_IMPROVED: Most Improved Player.
        ALL_NBA_FIRST_TEAM: All-NBA First Team.
        ALL_NBA_SECOND_TEAM: All-NBA Second Team.
        ALL_NBA_THIRD_TEAM: All-NBA Third Team.
        ALL_DEFENSIVE_FIRST_TEAM: NBA All-Defensive First Team.
        ALL_DEFENSIVE_SECOND_TEAM: NBA All-Defensive Second Team.
        ALL_ROOKIE_FIRST_TEAM: NBA All-Rookie First Team.
        ALL_ROOKIE_SECOND_TEAM: NBA All-Rookie Second Team.
        ALL_STAR: NBA All-Star selection.
    """

    MOST_VALUABLE_PLAYER = "MOST_VALUABLE_PLAYER"
    CHAMPIONSHIP = "CHAMPIONSHIP"
    FINALS_MVP = "FINALS_MVP"
    DEFENSIVE_PLAYER_OF_THE_YEAR = "DEFENSIVE_PLAYER_OF_THE_YEAR"
    ROOKIE_OF_THE_YEAR = "ROOKIE_OF_THE_YEAR"
    COACH_OF_THE_YEAR = "COACH_OF_THE_YEAR"
    SIXTH_MAN = "SIXTH_MAN"
    MOST_IMPROVED = "MOST_IMPROVED"
    ALL_NBA_FIRST_TEAM = "ALL_NBA_FIRST_TEAM"
    ALL_NBA_SECOND_TEAM = "ALL_NBA_SECOND_TEAM"
    ALL_NBA_THIRD_TEAM = "ALL_NBA_THIRD_TEAM"
    ALL_DEFENSIVE_FIRST_TEAM = "ALL_DEFENSIVE_FIRST_TEAM"
    ALL_DEFENSIVE_SECOND_TEAM = "ALL_DEFENSIVE_SECOND_TEAM"
    ALL_ROOKIE_FIRST_TEAM = "ALL_ROOKIE_FIRST_TEAM"
    ALL_ROOKIE_SECOND_TEAM = "ALL_ROOKIE_SECOND_TEAM"
    ALL_STAR = "ALL_STAR"


class RecipientType(str, Enum):
    """Enum representing the type of award recipient.

    Attributes:
        PLAYER: Awarded to a player.
        TEAM: Awarded to a team.
        COACH: Awarded to a coach.
    """

    PLAYER = "PLAYER"
    TEAM = "TEAM"
    COACH = "COACH"


class Award(SQLModel, table=True):
    """Represents an NBA award or honor.

    Attributes:
        award_id: Unique identifier for the award.
        name: Name of the award.
        category: Category of the award.
        description: Description of the award.
        first_awarded_year: Year the award was first presented.
        last_awarded_year: Year the award was last presented.
        is_active: Whether the award is currently active.
        recipients: List of recipients for this award.
    """

    __tablename__ = "award"

    award_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    category: AwardCategory
    description: str | None = None
    first_awarded_year: int | None = None
    last_awarded_year: int | None = None
    is_active: bool = Field(default=True)

    recipients: list["AwardRecipient"] = Relationship(back_populates="award")


class AwardRecipient(SQLModel, table=True):
    """Represents a recipient of an award for a specific season.

    Attributes:
        award_id: Foreign key to the award.
        season_id: Foreign key to the season.
        player_id: Foreign key to the player (if applicable).
        team_id: Foreign key to the team (if applicable).
        vote_rank: Rank in voting (if applicable).
        vote_count: Number of votes received.
        vote_percentage: Percentage of votes received.
        first_place_votes: Number of first-place votes.
        recipient_type: Type of recipient (player, team, coach).
        notes: Additional notes about the award.
        award: The award being received.
    """

    __tablename__ = "award_recipient"

    award_id: int = Field(foreign_key="award.award_id", primary_key=True)
    season_id: int = Field(foreign_key="season.season_id", primary_key=True)
    player_id: int | None = Field(default=None, foreign_key="player.player_id")
    team_id: int | None = Field(default=None, foreign_key="team.team_id")

    vote_rank: int | None = None
    vote_count: int | None = None
    vote_percentage: float | None = None
    first_place_votes: int | None = None
    recipient_type: RecipientType | None = None
    notes: str | None = None

    award: Award = Relationship(back_populates="recipients")
