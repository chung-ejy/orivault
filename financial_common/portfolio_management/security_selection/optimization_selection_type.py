from enum import Enum
import numpy as np

class OptimizationSelectionType(Enum):
    MIXED = ("mixed", lambda: MixedSelection())
    TOP = ("top", lambda: TopSelection())
    BOTTOM = ("bottom", lambda: BottomSelection())
    LONGSHORT = ("longshort", lambda: LongShortSelection())  # Placeholder for long/short selection

    def __init__(self, label, selection_method):
        self.label = label
        self.selection_method = selection_method

    def select(self, trades, percentage, position_type):
        """Invoke the associated selection method."""
        # Get max index within each group and broadcast it for each row
        
        # # Compute group index efficiently
        trades["group_idx"] = trades.groupby("major_key").cumcount() + 1

        # Compute max index per group **without repeating groupby()**
        group_max_idx = trades.groupby("major_key", as_index=False)["group_idx"].max().rename(columns={"group_idx": "group_idx_max"})
        trades = trades.merge(group_max_idx, on="major_key", how="left")

        # Ensure safe float division
        trades["group_idx_max"] = trades["group_idx_max"].astype(float)

        # Compute percentiles using safer rounding
        trades["group_percentile"] = round(trades["group_idx"] / trades["group_idx_max"] * 1000) / 1000
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
        trades["selection"] = (abs(trades["group_percentile"] - 0.5) > (0.5 - percentage))
        
        # Filter trades based on mask and reset index
        filtered = trades[trades["selection"]==True].reset_index(drop=True)
        # Assign position type within grouping phase, avoiding post-processing
        filtered["position_type"] = position_type.portfolio_effect
        return filtered
    
class LongShortSelection:
    @staticmethod
    def select(trades, percentage, position_type):
        # Compute indices within each group
        trades["selection"] = (abs(trades["group_percentile"] - 0.5) > (0.5 - percentage))
        
        # Filter trades based on mask and reset index
        filtered = trades[trades["selection"]==True].reset_index(drop=True)
        # Assign position type within grouping phase, avoiding post-processing
        filtered["position_type"] = [position_type.portfolio_effect if x < percentage else -position_type.portfolio_effect for x in trades["group_percentile"]]
        return filtered

class TopSelection:
    @staticmethod
    def select(trades, percentage, position_type):
        """Select the top subset of rows from the group based on percentage."""
        trades["selection"] = (trades["group_percentile"] < percentage)
        
        # Filter trades based on mask and reset index
        filtered = trades[trades["selection"]==True].reset_index(drop=True)
        filtered["position_type"] = position_type.portfolio_effect
        return filtered

class BottomSelection:
    @staticmethod
    def select(trades, percentage, position_type):
        """Select the top subset of rows from the group based on percentage."""
        trades["selection"] = (trades["group_percentile"] > (1 - percentage))
        
        # Filter trades based on mask and reset index
        filtered = trades[trades["selection"]==True].reset_index(drop=True)
        filtered["position_type"] = position_type.portfolio_effect
        return filtered