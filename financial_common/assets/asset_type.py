from enum import Enum

class AssetType(Enum):
    LONG = ("long", 1.0)
    SHORT = ("short", -1.0)

    def __init__(self, label, portfolio_effect):
        self.label = label
        self.portfolio_effect = portfolio_effect

    @classmethod
    def asset_factory(cls, asset_type):
        if asset_type == cls.LONG.label:
            return cls.LONG  # Adjust as needed for LONG behavior
        elif asset_type == cls.SHORT.label:
            return cls.SHORT  # Adjust as needed for SHORT behavior
        else:
            raise ValueError(f"Unsupported asset type: {asset_type}")