from enum import Enum
import numpy as np

class OptimizationAllocationType(Enum):
    EQUAL = ("equal", lambda: EqualAllocation())
    RISK = ("risk",lambda: RiskAllocation())

    def __init__(self, label, allocation_method):
        self.label = label
        self.allocation_method = allocation_method

    def allocate(self, trades):
        """Invoke the associated allocation method."""
        return self.allocation_method().allocate(trades)
    
    @classmethod
    def allocation_type_factory(cls, allocation_type):
        mapping = {member.label: member for member in cls}
        return mapping.get(allocation_type, None)
    
    def __str__(self):
        return self.label

class EqualAllocation:
    @staticmethod
    def allocate(trades):
        """allocate a symmetric subset of rows from the trades based on percentage."""
        trades["weight"] = 1
        return trades
    
class RiskAllocation:
    @staticmethod
    def allocate(trades):
        trades["date_key"] = ["".join(x.split("_")) for x in trades["major_key"]]
        trades["group_risk"] = trades.groupby("date_key")["risk"].transform("sum")
        trades["weight"] = trades["risk"] / trades["group_risk"] 
        return trades