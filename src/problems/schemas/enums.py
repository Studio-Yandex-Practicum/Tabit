from enum import Enum, unique


@unique
class MeetingStatus(Enum):
    NEW = 'NEW'
    PASSED = 'PASSED'
    SUSPENDED = 'SUSPENDED'


@unique
class MeetingResult(Enum):
    GREAT = 'GREAT'
    GOOD = 'GOOD'
    BAD = 'BAD'


@unique
class MeetingProblemSolution(Enum):
    YES = True
    NO = False


@unique
class MeetingParticipiantEngagement(Enum):
    YES = True
    NO = False
