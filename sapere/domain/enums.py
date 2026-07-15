from enum import IntEnum


class ReviewScore(IntEnum):
    AGAIN = 1
    HARD = 2
    GOOD = 3
    EASY = 4


class BloomLevel(IntEnum):
    REMEMBER = 1
    UNDERSTAND = 2
    APPLY = 3
    ANALYZE = 4
    EVALUATE = 5
    CREATE = 6


class Difficulty(IntEnum):
    BEGINNER = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    EXPERT = 5


class EnergyLevel(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class SessionStatus(IntEnum):
    ACTIVE = 0
    COMPLETE = 1
    ABANDONED = 2


class ExerciseLevel(IntEnum):
    BASIC = 1
    MEDIUM = 2
    ADVANCED = 3
    EXAM = 4
