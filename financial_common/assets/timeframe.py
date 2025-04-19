from enum import Enum

class Timeframe(Enum):
    QUARTER = "quarter"
    MONTH ="month"
    WEEK = "week"

    @classmethod
    def timeframe_factory(cls, timeframe):
        mapping = {member.value: member for member in cls}
        return mapping.get(timeframe, None)