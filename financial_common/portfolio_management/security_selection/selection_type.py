from enum import Enum
import numpy as np

class SelectionType(Enum):
    MIXED = ("mixed", lambda: MixedSelection())
    TOP = ("top", lambda: TopSelection())
    BOTTOM = ("bottom", lambda: BottomSelection())

    def __init__(self, label, selection_method):
        self.label = label
        self.selection_method = selection_method

    def select(self, group, percentage, position_type):
        """Invoke the associated selection method."""
        return self.selection_method().select(group, percentage, position_type)
    
    @classmethod
    def selection_type_factory(cls, selection_type):
        mapping = {member.label: member for member in cls}
        return mapping.get(selection_type, None)
    
    def __str__(self):
        return self.label

class MixedSelection:
    @staticmethod
    def select(group, percentage, position_type):
        """Select a symmetric subset of rows from the group based on percentage."""
        def mixed_allocation_percentage(n, percentage):
            k = max(1, int(n * percentage))  # Total rows to select
            if k >= n:
                return np.arange(n)  # Take all if percentage >= 1
            mid = k // 2
            arr = np.arange(-mid, mid + 1) if k % 2 == 1 else np.delete(np.arange(-mid, mid + 1), mid)
            return arr
        
        idx = mixed_allocation_percentage(len(group), percentage)
        selected_indices = group.index[idx % len(group)]  # Handle negative indexing safely
        group = group.loc[selected_indices].reset_index(drop=True)
        group["position_type"] = group.index < int(group.index.size / 2)
        group["position_type"] = group["position_type"].map(lambda x: position_type.portfolio_effect if x else position_type.portfolio_effect * -1)
        return group 


class TopSelection:
    @staticmethod
    def select(group, percentage, position_type):
        """Select the top subset of rows from the group based on percentage."""
        n_rows = max(1, int(len(group) * percentage))
        trades = group.head(n_rows).reset_index(drop=True)
        trades["position_type"] = position_type.portfolio_effect
        return trades


class BottomSelection:
    @staticmethod
    def select(group, percentage, position_type):
        """Select the bottom subset of rows from the group based on percentage."""
        n_rows = max(1, int(len(group) * percentage))
        trades = group.tail(n_rows).reset_index(drop=True)
        trades["position_type"] = position_type.portfolio_effect
        return trades