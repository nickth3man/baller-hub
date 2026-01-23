from enum import Enum


class Position(str, Enum):
    POINT_GUARD = "POINT_GUARD"
    SHOOTING_GUARD = "SHOOTING_GUARD"
    SMALL_FORWARD = "SMALL_FORWARD"
    POWER_FORWARD = "POWER_FORWARD"
    CENTER = "CENTER"
    GUARD = "GUARD"
    FORWARD = "FORWARD"


class SeasonType(str, Enum):
    REGULAR = "REGULAR"
    PLAYOFF = "PLAYOFF"
    ALL_STAR = "ALL_STAR"
    PRESEASON = "PRESEASON"
