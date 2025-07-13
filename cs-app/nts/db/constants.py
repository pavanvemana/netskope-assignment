from enum import StrEnum, Enum

class TicketStates(StrEnum):
    OPEN = 'OPEN'
    IN_PROGRESS = 'IN_PROGRESS'
    AWAITING_CUSTOMER = 'AWAITING_CUSTOMER'
    RESOLVED = 'RESOLVED'

class EscalationLevels(Enum):
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3

class SLAStates(StrEnum):
    ACTIVE = 'ACTIVE'
    NON_BUSINESS_HOURS = 'NON_BUSINESS_HOURS'
    AT_RISK = 'AT_RISK'
    BREACHED = 'BREACHED'
    PAUSED = 'PAUSED'
    STOPPED = 'STOPPED'

class SLAClock(StrEnum):
    RESPONSE = 'RESPONSE'
    RESOLUTION = 'RESOLUTION'