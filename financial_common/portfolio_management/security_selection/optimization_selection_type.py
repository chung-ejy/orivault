from enum import Enum
import numpy as np

class OptimizationSelectionType(Enum):
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
        trades["selection"] = (abs(trades["rank_percentile"] - 0.5) >= (0.5 - percentage))
        
        # Filter trades based on mask and reset index
        filtered = trades[trades["selection"]==True].reset_index(drop=True)
        # Assign position type within grouping phase, avoiding post-processing
        filtered["position_type"] = position_type.portfolio_effect
        return filtered
    
class LongShortSelection:
    @staticmethod
    def select(trades, percentage, position_type):
        # Compute selection mask
        trades["selection"] = abs(trades["rank_percentile"] - 0.5) >= (0.5 - percentage)
        
        # Filter trades based on selection mask
        filtered = trades[trades["selection"]].copy()  # Use .copy() to avoid SettingWithCopyWarning
        filtered.reset_index(drop=True, inplace=True)

        # Assign position type based on percentile
        filtered["position_type"] = np.where(
            filtered["rank_percentile"] < 0.5, 
            position_type.portfolio_effect, 
            -position_type.portfolio_effect
        )

        return filtered

class TopSelection:
    @staticmethod
    def select(trades, percentage, position_type):
        """Select the top subset of rows from the group based on percentage."""
        trades["selection"] = (trades["rank_percentile"] <= percentage)
        
        # Filter trades based on mask and reset index
        filtered = trades[trades["selection"]==True].reset_index(drop=True)
        filtered["position_type"] = position_type.portfolio_effect
        return filtered

class BottomSelection:
    @staticmethod
    def select(trades, percentage, position_type):
        """Select the top subset of rows from the group based on percentage."""
        trades["selection"] = (trades["rank_percentile"] >= (1 - percentage))
        
        # Filter trades based on mask and reset index
        filtered = trades[trades["selection"]==True].reset_index(drop=True)
        filtered["position_type"] = position_type.portfolio_effect
        return filtered