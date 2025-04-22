from enum import Enum
import numpy as np

class AllocationType(Enum):
    EQUAL = ("equal", lambda: EqualAllocation())
    MARKET_CAP = ("market_cap", lambda: MarketCapAllocation())
    RISK = ("risk",lambda: RiskAllocation())

    def __init__(self, label, allocation_method):
        self.label = label
        self.allocation_method = allocation_method

    def allocate(self, group):
        """Invoke the associated allocation method."""
        return self.allocation_method().allocate(group)
    
    @classmethod
    def allocation_type_factory(cls, allocation_type):
        mapping = {member.label: member for member in cls}
        return mapping.get(allocation_type, None)
    
    def __str__(self):
        return self.label

class EqualAllocation:
    @staticmethod
    def allocate(group):
        """allocate a symmetric subset of rows from the group based on percentage."""
        group["weight"] = 1
        return group

class MarketCapAllocation:
    @staticmethod
    def allocate(group):
        total_market_cap = group["market_cap"].sum()
        group["weight"] = group["market_cap"] / total_market_cap
        return group
    
class RiskAllocation:
    @staticmethod
    def allocate(group):
        total_beta = group["risk"].sum()
        weights = list((group["risk"] / total_beta).values)
        weights.reverse()
        group["weight"] = weights
        return group