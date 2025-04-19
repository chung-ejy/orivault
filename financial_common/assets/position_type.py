from enum import Enum

class PositionType(Enum):
    LONG = ("long", 1.0)  # Represents a bullish position, expecting the asset to increase in value.
    SHORT = ("short", -1.0)  # Represents a bearish position, expecting the asset to decrease in value.

    def __init__(self, label, portfolio_effect):
        self.label = label
        self.portfolio_effect = portfolio_effect

    @classmethod
    def get_position_type(cls, position_label):
        """
        Retrieves the corresponding PositionType based on the provided label.

        Args:
            position_label (str): The label of the position type ("long" or "short").

        Returns:
            PositionType: The matching enum member if found, otherwise raises a ValueError.
        """
        mapping = {member.label: member for member in cls}
        if position_label not in mapping:
            raise ValueError(f"Unsupported position type: {position_label}")
        return mapping[position_label]
    
    def __str__(self):
        return self.label