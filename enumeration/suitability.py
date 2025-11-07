from enum import Enum

class SuitabilityEnum(str, Enum):
    UNDER_5 = 'under_5'
    UNDER_10 = 'under_10'
    UNDER_13 = 'under_13'
    UNDER_16 = 'under_16'
    UNDER_18 = 'under_18'
    ADULT = 'adult'
