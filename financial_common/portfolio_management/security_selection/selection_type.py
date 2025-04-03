from enum import Enum
from financial_common.portfolio_management.security_selection.selection_methods import MixedSelection, TopSelection, BottomSelection
class SelectionType(Enum):
    
    MIXED = "mixed"
    TOP = "top"
    BOTTOM = "bottom"

    @classmethod    
    def selection_factory(cls,selection_type):
        if selection_type == SelectionType.MIXED.value:
            return MixedSelection()
        elif selection_type == SelectionType.TOP.value:
            return TopSelection()
        elif selection_type == SelectionType.BOTTOM.value:
            return BottomSelection()
        else:
            raise ValueError(f"Unsupported selection type: {selection_type}")