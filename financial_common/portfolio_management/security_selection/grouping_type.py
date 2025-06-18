from enum import Enum

class GroupingType(Enum):
    STANDARD_DEV = "standard_dev"  
    # AVERAGE_RETURN =  "average_return"
    # SIMPLE_MOVING_AVERAGE =  "simple_moving_average"
    # DRAWDOWN =  "drawdown"
    DISTANCE = "distance"
    # DIVIDEND = "dividend"
    # COOKED_RETURN = "cooked_return"
    @classmethod
    def get_grouping_type(cls, position_label):
        """
        Retrieves the corresponding PositionType based on the provided label.

        Args:
            position_label (str): The label of the position type ("long" or "short").

        Returns:
            PositionType: The matching enum member if found, otherwise raises a ValueError.
        """
        mapping = {member.value: member for member in cls}
        if position_label not in mapping:
            raise ValueError(f"Unsupported position type: {position_label}")
        return mapping[position_label]
    
    def __str__(self):
        return self.value