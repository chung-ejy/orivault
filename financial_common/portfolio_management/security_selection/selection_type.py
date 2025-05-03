from enum import Enum
import numpy as np
import pandas as pd

class SelectionType(Enum):
    MIXED = ("mixed", lambda: MixedSelection())
    TOP = ("top", lambda: TopSelection())
    BOTTOM = ("bottom", lambda: BottomSelection())
    LONGSHORT = ("long_short", lambda: LongShortSelection())  # Placeholder for long/short selection

    def __init__(self, label, selection_method):
        self.label = label
        self.selection_method = selection_method

    def select(self, trades, percentage, position_type):
        """Invoke the associated selection method."""
        # Get max index within each group and broadcast it for each row
        return self.selection_method().select(trades, percentage, position_type)
    
    @classmethod
    def selection_type_factory(cls, selection_type):
        mapping = {member.label: member for member in cls}
        return mapping.get(selection_type, None)
    
    def __str__(self):
        return self.label

class MixedSelection:
    @staticmethod
    def select(trades, percentage, position_type):
        # Compute indices within each group
        filtered = pd.concat([trades.groupby("major_key").first(),trades.groupby("major_key").last()])
        # Assign position type within grouping phase, avoiding post-processing
        filtered["position_type"] = position_type.portfolio_effect
        return filtered
    
class LongShortSelection:
    @staticmethod
    def select(trades, percentage, position_type):
        # Compute indices within each group
        top = trades.groupby("major_key").first()
        top["position_type"] = position_type.portfolio_effect
        bottom = trades.groupby("major_key").last()
        bottom["position_type"] = -position_type.portfolio_effect
        filtered = pd.concat([top,bottom])
        return filtered

class TopSelection:
    @staticmethod
    def select(trades, percentage, position_type):
        top = trades.groupby("major_key").first()
        top["position_type"] = position_type.portfolio_effect
        return top

class BottomSelection:
    @staticmethod
    def select(trades, percentage, position_type):
        bottom = trades.groupby("major_key").last()
        bottom["position_type"] = position_type.portfolio_effect
        return bottom