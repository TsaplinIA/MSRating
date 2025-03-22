import enum


class Team(str, enum.Enum):
    RED = "RED_TEAM"
    BLACK = "BLACK_TEAM"


class Role(str, enum.Enum):
    DON = "DON"
    SHERIFF = "SHERIFF"
    RED = "RED"
    BLACK = "BLACK"


