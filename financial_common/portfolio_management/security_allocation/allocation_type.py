from enum import Enum
import numpy as np

class AllocationType(Enum):
    EQUAL = ("equal", lambda: EqualAllocation())
    RISK = ("risk",lambda:RiskAllocation())
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
        trades["date_key"] = ["".join(x.split("_")[:-1]) for x in trades["major_key"]]
        trades["weight"] = 1 / (trades.groupby(["date_key"]).cumcount()+1).max()
        trades.drop("date_key",axis=1,inplace=True)
        return trades

class RiskAllocation:
    @staticmethod
    def allocate(trades):
        """allocate a symmetric subset of rows from the trades based on percentage."""
        trades["date_key"] = ["".join(x.split("_")[:-1]) for x in trades["major_key"]]
        trades["reversed_risk"] = 1/trades["risk"]
        trades["weight"] = trades["reversed_risk"] / trades.groupby(["date_key"])["reversed_risk"].transform("sum")
        trades.drop(["date_key","reversed_risk"],axis=1,inplace=True)
        return trades